from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Any, Iterator


class SqliteWorkspaceStore:
    """Durable sqlite-backed store for workspace sessions, runs, and artifacts."""

    def __init__(self, database_path: str) -> None:
        self._lock = Lock()
        db_path = Path(database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._database_path = str(db_path)
        self._init_schema()

    def upsert_session(
        self,
        *,
        session_id: str,
        lesson_id: str,
        workspace_dir: str,
        visible_files: list[str],
        file_versions: dict[str, int],
        runtime_mode: str,
        console_ready: bool,
    ) -> None:
        with self._lock, self._connection() as conn:
            conn.execute(
                """
                INSERT INTO workspace_sessions (
                    session_id,
                    lesson_id,
                    workspace_dir,
                    visible_files_json,
                    file_versions_json,
                    runtime_mode,
                    console_ready
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    lesson_id = excluded.lesson_id,
                    workspace_dir = excluded.workspace_dir,
                    visible_files_json = excluded.visible_files_json,
                    file_versions_json = excluded.file_versions_json,
                    runtime_mode = excluded.runtime_mode,
                    console_ready = excluded.console_ready,
                    updated_at_utc = datetime('now')
                """,
                (
                    session_id,
                    lesson_id,
                    workspace_dir,
                    json.dumps(visible_files),
                    json.dumps(file_versions),
                    runtime_mode,
                    1 if console_ready else 0,
                ),
            )
            conn.commit()

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        with self._lock, self._connection() as conn:
            row = conn.execute(
                """
                SELECT session_id, lesson_id, workspace_dir, visible_files_json,
                       file_versions_json, runtime_mode, console_ready
                FROM workspace_sessions
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "session_id": row["session_id"],
            "lesson_id": row["lesson_id"],
            "workspace_dir": row["workspace_dir"],
            "visible_files": json.loads(row["visible_files_json"]),
            "file_versions": json.loads(row["file_versions_json"]),
            "runtime_mode": row["runtime_mode"],
            "console_ready": bool(row["console_ready"]),
        }

    def upsert_run(
        self,
        *,
        session_id: str,
        run_id: str,
        status: str,
        exit_code: int | None,
        started_at: str,
        finished_at: str | None,
    ) -> None:
        with self._lock, self._connection() as conn:
            conn.execute(
                """
                INSERT INTO workspace_runs (
                    session_id,
                    run_id,
                    status,
                    exit_code,
                    started_at_utc,
                    finished_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id, run_id) DO UPDATE SET
                    status = excluded.status,
                    exit_code = excluded.exit_code,
                    started_at_utc = excluded.started_at_utc,
                    finished_at_utc = excluded.finished_at_utc
                """,
                (session_id, run_id, status, exit_code, started_at, finished_at),
            )
            conn.commit()

    def get_run(self, session_id: str, run_id: str) -> dict[str, Any] | None:
        with self._lock, self._connection() as conn:
            row = conn.execute(
                """
                SELECT session_id, run_id, status, exit_code, started_at_utc, finished_at_utc
                FROM workspace_runs
                WHERE session_id = ? AND run_id = ?
                """,
                (session_id, run_id),
            ).fetchone()
        if row is None:
            return None
        return {
            "session_id": row["session_id"],
            "run_id": row["run_id"],
            "status": row["status"],
            "exit_code": row["exit_code"],
            "started_at": row["started_at_utc"],
            "finished_at": row["finished_at_utc"],
        }

    def record_artifact(
        self,
        *,
        owner_kind: str,
        owner_id: str,
        artifact_kind: str,
        artifact_path: str,
    ) -> None:
        with self._lock, self._connection() as conn:
            conn.execute(
                """
                INSERT INTO workspace_artifacts (
                    owner_kind,
                    owner_id,
                    artifact_kind,
                    artifact_path
                ) VALUES (?, ?, ?, ?)
                """,
                (owner_kind, owner_id, artifact_kind, artifact_path),
            )
            conn.commit()

    def list_artifacts(self, owner_kind: str, owner_id: str) -> list[dict[str, Any]]:
        with self._lock, self._connection() as conn:
            rows = conn.execute(
                """
                SELECT owner_kind, owner_id, artifact_kind, artifact_path, created_at_utc
                FROM workspace_artifacts
                WHERE owner_kind = ? AND owner_id = ?
                ORDER BY created_at_utc ASC
                """,
                (owner_kind, owner_id),
            ).fetchall()
        return [
            {
                "owner_kind": row["owner_kind"],
                "owner_id": row["owner_id"],
                "artifact_kind": row["artifact_kind"],
                "artifact_path": row["artifact_path"],
                "created_at_utc": row["created_at_utc"],
            }
            for row in rows
        ]

    def _init_schema(self) -> None:
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workspace_sessions (
                    session_id TEXT PRIMARY KEY,
                    lesson_id TEXT NOT NULL,
                    workspace_dir TEXT NOT NULL,
                    visible_files_json TEXT NOT NULL,
                    file_versions_json TEXT NOT NULL,
                    runtime_mode TEXT NOT NULL,
                    console_ready INTEGER NOT NULL,
                    created_at_utc TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at_utc TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workspace_runs (
                    session_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    exit_code INTEGER NULL,
                    started_at_utc TEXT NOT NULL,
                    finished_at_utc TEXT NULL,
                    PRIMARY KEY (session_id, run_id)
                )
                """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workspace_artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_kind TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    artifact_kind TEXT NOT NULL,
                    artifact_path TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """)
            conn.commit()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._database_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()
