from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Iterator, Optional
from uuid import uuid4

from backend.job_store import ExecutionJob


@dataclass
class SqliteExecutionJobStore:
    """Durable sqlite-backed store for execution jobs."""

    database_path: str

    def __post_init__(self) -> None:
        self._lock = Lock()
        db_path = Path(self.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._database_path = str(db_path)
        self._init_schema()

    def create(
        self,
        *,
        owner_user_id: str,
        owner_role: str,
    ) -> ExecutionJob:
        with self._lock, self._connection() as conn:
            task_id = uuid4().hex
            created_at_utc = _utc_now()
            conn.execute(
                """
                INSERT INTO execution_jobs (
                    task_id,
                    status,
                    owner_user_id,
                    owner_role,
                    created_at_utc,
                    result_json,
                    error_json
                )
                VALUES (?, ?, ?, ?, ?, NULL, NULL)
                """,
                (task_id, "queued", owner_user_id, owner_role, created_at_utc),
            )
            conn.commit()
        return ExecutionJob(
            task_id=task_id,
            status="queued",
            owner_user_id=owner_user_id,
            owner_role=owner_role,
            created_at_utc=created_at_utc,
        )

    def get(self, task_id: str) -> Optional[ExecutionJob]:
        with self._lock, self._connection() as conn:
            row = conn.execute(
                """
                SELECT task_id, status, owner_user_id, owner_role, created_at_utc, result_json, error_json
                FROM execution_jobs
                WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
        if row is None:
            return None
        return ExecutionJob(
            task_id=row[0],
            status=row[1],
            owner_user_id=row[2],
            owner_role=row[3],
            created_at_utc=row[4],
            result=json.loads(row[5]) if row[5] else None,
            error=json.loads(row[6]) if row[6] else None,
        )

    def mark_running(self, task_id: str) -> None:
        self._update(task_id, status="running")

    def mark_succeeded(self, task_id: str, result: dict[str, Any]) -> None:
        self._update(task_id, status="succeeded", result=result, error=None)

    def mark_failed(self, task_id: str, error: Any) -> None:
        self._update(task_id, status="failed", result=None, error=error)

    def snapshot(self, task_id: str) -> Optional[dict[str, Any]]:
        job = self.get(task_id)
        if job is None:
            return None
        payload: dict[str, Any] = {
            "task_id": job.task_id,
            "status": job.status,
            "owner_user_id": job.owner_user_id,
            "owner_role": job.owner_role,
            "created_at_utc": job.created_at_utc,
        }
        if job.result is not None:
            payload["result"] = job.result
        if job.error is not None:
            payload["error"] = job.error
        return payload

    def _update(
        self,
        task_id: str,
        *,
        status: str,
        result: Any = None,
        error: Any = None,
    ) -> None:
        with self._lock, self._connection() as conn:
            updated = conn.execute(
                """
                UPDATE execution_jobs
                SET status = ?, result_json = ?, error_json = ?
                WHERE task_id = ?
                """,
                (
                    status,
                    json.dumps(result) if result is not None else None,
                    json.dumps(error) if error is not None else None,
                    task_id,
                ),
            ).rowcount
            conn.commit()
        if updated == 0:
            raise KeyError(f"Unknown task_id '{task_id}'.")

    def _init_schema(self) -> None:
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS execution_jobs (
                    task_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    owner_user_id TEXT NOT NULL DEFAULT '',
                    owner_role TEXT NOT NULL DEFAULT 'student',
                    created_at_utc TEXT NOT NULL DEFAULT (datetime('now')),
                    result_json TEXT NULL,
                    error_json TEXT NULL
                )
                """)
            column_rows = conn.execute("PRAGMA table_info(execution_jobs)").fetchall()
            existing_columns = {row[1] for row in column_rows}
            if "owner_user_id" not in existing_columns:
                conn.execute(
                    "ALTER TABLE execution_jobs ADD COLUMN owner_user_id TEXT NOT NULL DEFAULT ''"
                )
            if "owner_role" not in existing_columns:
                conn.execute(
                    "ALTER TABLE execution_jobs ADD COLUMN owner_role TEXT NOT NULL DEFAULT 'student'"
                )
            if "created_at_utc" not in existing_columns:
                conn.execute(
                    "ALTER TABLE execution_jobs ADD COLUMN created_at_utc TEXT NOT NULL DEFAULT (datetime('now'))"
                )
            conn.commit()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._database_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()
