from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Any, Iterator


class SqliteArtifactStore:
    """Durable sqlite-backed store for execution artifact references."""

    def __init__(self, database_path: str) -> None:
        self._lock = Lock()
        db_path = Path(database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._database_path = str(db_path)
        self._init_schema()

    def record(
        self,
        *,
        task_id: str,
        artifact_kind: str,
        artifact_path: str,
    ) -> None:
        with self._lock, self._connection() as conn:
            conn.execute(
                """
                INSERT INTO execution_artifacts (task_id, artifact_kind, artifact_path)
                VALUES (?, ?, ?)
                """,
                (task_id, artifact_kind, artifact_path),
            )
            conn.commit()

    def list_for_task(self, task_id: str) -> list[dict[str, Any]]:
        with self._lock, self._connection() as conn:
            rows = conn.execute(
                """
                SELECT task_id, artifact_kind, artifact_path, created_at_utc
                FROM execution_artifacts
                WHERE task_id = ?
                ORDER BY created_at_utc ASC
                """,
                (task_id,),
            ).fetchall()
        return [
            {
                "task_id": row["task_id"],
                "artifact_kind": row["artifact_kind"],
                "artifact_path": row["artifact_path"],
                "created_at_utc": row["created_at_utc"],
            }
            for row in rows
        ]

    def _init_schema(self) -> None:
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS execution_artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
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
