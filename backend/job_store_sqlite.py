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

    def create(self) -> ExecutionJob:
        with self._lock, self._connection() as conn:
            task_id = uuid4().hex
            conn.execute(
                """
                INSERT INTO execution_jobs (task_id, status, result_json, error_json)
                VALUES (?, ?, NULL, NULL)
                """,
                (task_id, "queued"),
            )
            conn.commit()
        return ExecutionJob(task_id=task_id, status="queued")

    def get(self, task_id: str) -> Optional[ExecutionJob]:
        with self._lock, self._connection() as conn:
            row = conn.execute(
                """
                SELECT task_id, status, result_json, error_json
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
            result=json.loads(row[2]) if row[2] else None,
            error=json.loads(row[3]) if row[3] else None,
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
        payload: dict[str, Any] = {"task_id": job.task_id, "status": job.status}
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
                    result_json TEXT NULL,
                    error_json TEXT NULL,
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
