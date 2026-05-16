from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Optional
from uuid import uuid4


@dataclass
class ExecutionJob:
    task_id: str
    status: str
    owner_user_id: str
    owner_role: str
    created_at_utc: str
    result: Optional[dict[str, Any]] = None
    error: Any = None


class ExecutionJobStore:
    """Thread-safe in-memory store for asynchronous execution jobs."""

    def __init__(self):
        self._jobs: dict[str, ExecutionJob] = {}
        self._lock = Lock()

    def create(
        self,
        *,
        owner_user_id: str,
        owner_role: str,
    ) -> ExecutionJob:
        with self._lock:
            job = ExecutionJob(
                task_id=uuid4().hex,
                status="queued",
                owner_user_id=owner_user_id,
                owner_role=owner_role,
                created_at_utc=datetime.now(timezone.utc).isoformat(),
            )
            self._jobs[job.task_id] = job
            return job

    def get(self, task_id: str) -> Optional[ExecutionJob]:
        with self._lock:
            return self._jobs.get(task_id)

    def mark_running(self, task_id: str) -> None:
        self._update(task_id, status="running")

    def mark_succeeded(self, task_id: str, result: dict[str, Any]) -> None:
        self._update(task_id, status="succeeded", result=result, error=None)

    def mark_failed(self, task_id: str, error: Any) -> None:
        self._update(task_id, status="failed", error=error, result=None)

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

    def _update(self, task_id: str, **changes: Any) -> None:
        with self._lock:
            job = self._jobs.get(task_id)
            if job is None:
                raise KeyError(f"Unknown task_id '{task_id}'.")

            for key, value in changes.items():
                setattr(job, key, value)
