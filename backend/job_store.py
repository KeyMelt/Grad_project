from dataclasses import dataclass
from threading import Lock
from typing import Any, Optional
from uuid import uuid4


@dataclass
class ExecutionJob:
    task_id: str
    status: str
    result: Optional[dict[str, Any]] = None
    error: Any = None


class ExecutionJobStore:
    """Thread-safe in-memory store for asynchronous execution jobs."""

    def __init__(self):
        self._jobs: dict[str, ExecutionJob] = {}
        self._lock = Lock()

    def create(self) -> ExecutionJob:
        with self._lock:
            job = ExecutionJob(task_id=uuid4().hex, status="queued")
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
