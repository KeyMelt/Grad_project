from __future__ import annotations

from pathlib import Path

from backend.job_store_sqlite import SqliteExecutionJobStore


def test_sqlite_job_store_round_trip(tmp_path: Path):
    store = SqliteExecutionJobStore(str(tmp_path / "jobs.db"))
    job = store.create()
    assert job.status == "queued"

    store.mark_running(job.task_id)
    assert store.snapshot(job.task_id)["status"] == "running"

    store.mark_succeeded(job.task_id, {"status": "success", "metrics": {"episodes_completed": 1}})
    snapshot = store.snapshot(job.task_id)
    assert snapshot["status"] == "succeeded"
    assert snapshot["result"]["status"] == "success"


def test_sqlite_job_store_failure_path(tmp_path: Path):
    store = SqliteExecutionJobStore(str(tmp_path / "jobs.db"))
    job = store.create()
    store.mark_failed(job.task_id, {"message": "execution failed"})

    snapshot = store.snapshot(job.task_id)
    assert snapshot["status"] == "failed"
    assert snapshot["error"]["message"] == "execution failed"
