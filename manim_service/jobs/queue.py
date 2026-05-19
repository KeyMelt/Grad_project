"""Job queue for render requests.

Two implementations live behind a single Protocol so the API contract does not
change between dev (in-process, MVP) and production (Redis-backed, scalable).

MVP scope:
- `MemoryJobQueue` — thread-safe in-process queue
- Redis backend deferred; selecting it raises until implemented
"""
from __future__ import annotations

import queue as _queue
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from manim_service import settings


class JobKind(str, Enum):
    CONCEPT_VIDEO = "concept_video"
    TRACE = "trace"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RENDERING = "rendering"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Job:
    job_id: str
    kind: JobKind
    payload: dict[str, Any]
    status: JobStatus = JobStatus.QUEUED
    video_path: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "job_id": self.job_id,
            "kind": self.kind.value,
            "status": self.status.value,
        }
        if self.video_path is not None:
            result["video_path"] = self.video_path
        if self.error is not None:
            result["error"] = self.error
        return result


class JobQueue(Protocol):
    """Queue contract — same shape for memory and Redis backends."""

    def enqueue(self, kind: JobKind, payload: dict[str, Any]) -> str: ...

    def pop(self, timeout: float | None = None) -> Job | None: ...

    def get(self, job_id: str) -> Job | None: ...

    def mark_rendering(self, job_id: str) -> None: ...

    def mark_complete(self, job_id: str, video_path: str) -> None: ...

    def mark_failed(self, job_id: str, error: str) -> None: ...

    def shutdown(self) -> None: ...


class MemoryJobQueue:
    """In-process job queue backed by `queue.Queue` + a dict for status lookup."""

    def __init__(self) -> None:
        self._queue: _queue.Queue[str] = _queue.Queue()
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._stopped = False

    def enqueue(self, kind: JobKind, payload: dict[str, Any]) -> str:
        job_id = uuid.uuid4().hex
        job = Job(job_id=job_id, kind=kind, payload=dict(payload))
        with self._lock:
            self._jobs[job_id] = job
        self._queue.put(job_id)
        return job_id

    def pop(self, timeout: float | None = None) -> Job | None:
        try:
            job_id = self._queue.get(timeout=timeout)
        except _queue.Empty:
            return None
        if job_id == _SHUTDOWN_SENTINEL:
            return None
        with self._lock:
            return self._jobs.get(job_id)

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            return Job(
                job_id=job.job_id,
                kind=job.kind,
                payload=dict(job.payload),
                status=job.status,
                video_path=job.video_path,
                error=job.error,
            )

    def mark_rendering(self, job_id: str) -> None:
        self._update(job_id, status=JobStatus.RENDERING)

    def mark_complete(self, job_id: str, video_path: str) -> None:
        self._update(job_id, status=JobStatus.COMPLETE, video_path=video_path)

    def mark_failed(self, job_id: str, error: str) -> None:
        self._update(job_id, status=JobStatus.FAILED, error=error)

    def shutdown(self) -> None:
        with self._lock:
            if self._stopped:
                return
            self._stopped = True
        self._queue.put(_SHUTDOWN_SENTINEL)

    def _update(self, job_id: str, **fields: Any) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            for key, value in fields.items():
                setattr(job, key, value)


_SHUTDOWN_SENTINEL = "__shutdown__"


_default_queue: JobQueue | None = None
_default_queue_lock = threading.Lock()


def get_queue() -> JobQueue:
    """Process-wide default queue, selected by `settings.QUEUE_BACKEND`."""
    global _default_queue
    if _default_queue is not None:
        return _default_queue
    with _default_queue_lock:
        if _default_queue is None:
            _default_queue = _build_queue(settings.QUEUE_BACKEND)
    return _default_queue


def reset_queue_for_tests(replacement: JobQueue | None = None) -> None:
    """Test helper — clears the cached default queue or installs a replacement."""
    global _default_queue
    with _default_queue_lock:
        _default_queue = replacement


def _build_queue(backend: str) -> JobQueue:
    if backend == "memory":
        return MemoryJobQueue()
    if backend == "redis":
        raise NotImplementedError(
            "Redis queue backend is not yet implemented. "
            "Set QUEUE_BACKEND=memory or implement RedisJobQueue."
        )
    raise ValueError(f"Unknown QUEUE_BACKEND: {backend!r}")
