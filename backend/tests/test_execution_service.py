from __future__ import annotations

import time

from backend.artifact_store_sqlite import SqliteArtifactStore
from backend.execution_runtime import ExecutionPipelineError
from backend.services.execution_service import ExecutionService


def _wait_for_terminal_state(
    service: ExecutionService,
    task_id: str,
    timeout_seconds: float = 2.0,
) -> dict:
    started = time.time()
    while time.time() - started <= timeout_seconds:
        snapshot = service.snapshot(task_id)
        if snapshot is None:
            raise AssertionError("Expected snapshot to exist.")
        if snapshot["status"] in {"succeeded", "failed"}:
            return snapshot
        time.sleep(0.02)
    raise AssertionError(f"Task {task_id} did not reach terminal state in time.")


def test_submit_transitions_to_succeeded(monkeypatch):
    service = ExecutionService()

    def _fake_execute_sync(payload):
        del payload
        return {"status": "success", "metrics": {"episodes_completed": 1}}

    monkeypatch.setattr(service, "execute_sync", _fake_execute_sync)

    submission = service.submit({"lesson_id": "dp_policy_eval", "code": "print('x')"})
    assert submission["status"] in {"queued", "running", "succeeded"}

    snapshot = _wait_for_terminal_state(service, submission["task_id"])
    assert snapshot["status"] == "succeeded"
    assert snapshot["result"]["status"] == "success"


def test_submit_transitions_to_failed_on_pipeline_error(monkeypatch):
    service = ExecutionService()

    def _fake_execute_sync(payload):
        del payload
        raise ExecutionPipelineError(
            status_code=400,
            detail={"message": "Code validation failed.", "issues": ["missing function"]},
        )

    monkeypatch.setattr(service, "execute_sync", _fake_execute_sync)

    submission = service.submit({"lesson_id": "td_q_learning", "code": "def helper(): pass"})
    snapshot = _wait_for_terminal_state(service, submission["task_id"])
    assert snapshot["status"] == "failed"
    assert snapshot["error"]["message"] == "Code validation failed."


def test_submit_transitions_to_failed_on_unhandled_error(monkeypatch):
    service = ExecutionService()

    def _fake_execute_sync(payload):
        del payload
        raise RuntimeError("unexpected crash")

    monkeypatch.setattr(service, "execute_sync", _fake_execute_sync)

    submission = service.submit({"lesson_id": "dp_policy_eval", "code": "print('x')"})
    snapshot = _wait_for_terminal_state(service, submission["task_id"])
    assert snapshot["status"] == "failed"
    assert snapshot["error"]["message"] == "Unhandled execution failure."


def test_successful_jobs_record_replay_artifact_reference(tmp_path, monkeypatch):
    service = ExecutionService(
        artifact_store=SqliteArtifactStore(str(tmp_path / "execution_artifacts.db"))
    )

    def _fake_execute_sync(payload):
        del payload
        return {
            "status": "success",
            "video_path": "/tmp/replay.mp4",
            "metrics": {"episodes_completed": 1},
        }

    monkeypatch.setattr(service, "execute_sync", _fake_execute_sync)

    submission = service.submit({"lesson_id": "dp_policy_eval", "code": "print('x')"})
    snapshot = _wait_for_terminal_state(service, submission["task_id"])

    assert snapshot["status"] == "succeeded"
    assert snapshot["artifacts"][0]["artifact_kind"] == "replay_video"
    assert snapshot["artifacts"][0]["artifact_path"] == "/tmp/replay.mp4"


def test_snapshot_refreshes_live_replay_status(monkeypatch):
    service = ExecutionService()
    service.job_store.create(owner_user_id="student-1", owner_role="student")
    task_id = next(iter(service.job_store._jobs))
    service.job_store.mark_succeeded(
        task_id,
        {
            "status": "success",
            "replay_render_job_id": "job-1",
            "replay_render_status": "queued",
            "replay_state": "queued",
            "video_path": "",
            "visualization_ready": False,
        },
    )

    monkeypatch.setattr(
        "backend.services.execution_service.enrich_snapshot_with_replay",
        lambda snapshot: {
            **snapshot,
            "result": {
                **snapshot["result"],
                "replay_render_status": "complete",
                "replay_state": "ready",
                "video_path": "http://manim-service:8300/videos/job-1.mp4",
                "visualization_ready": True,
            },
        },
    )

    snapshot = service.snapshot(task_id)

    assert snapshot is not None
    assert snapshot["result"]["replay_render_status"] == "complete"
    assert snapshot["result"]["replay_state"] == "ready"
    assert snapshot["result"]["visualization_ready"] is True


def test_execute_sync_records_submission_outcomes(monkeypatch):
    class _FakeProgressService:
        def __init__(self) -> None:
            self.calls: list[tuple[str, bool, str | None]] = []

        def record_submission_outcome(
            self,
            student_id: str,
            *,
            passed: bool,
            failure_kind: str | None = None,
        ) -> None:
            self.calls.append((student_id, passed, failure_kind))

        def record_lesson_completion(self, student_id: str, lesson_id: str) -> None:
            self.calls.append((student_id, True, lesson_id))

    progress_service = _FakeProgressService()
    service = ExecutionService(progress_service=progress_service)

    def _fake_run_submission_with_timeout(payload):
        del payload
        return {"status": "success", "metrics": {"episodes_completed": 1}}

    monkeypatch.setattr(
        "backend.services.execution_service.run_submission_with_timeout",
        _fake_run_submission_with_timeout,
    )

    service.execute_sync(
        {
            "lesson_id": "dp_policy_eval",
            "student_id": "student-1",
            "code": "def policy_evaluation(*args): return []",
        }
    )

    assert progress_service.calls[0] == ("student-1", True, None)


def test_execute_sync_records_failed_submission_outcome(monkeypatch):
    class _FakeProgressService:
        def __init__(self) -> None:
            self.calls: list[tuple[str, bool, str | None]] = []

        def record_submission_outcome(
            self,
            student_id: str,
            *,
            passed: bool,
            failure_kind: str | None = None,
        ) -> None:
            self.calls.append((student_id, passed, failure_kind))

    progress_service = _FakeProgressService()
    service = ExecutionService(progress_service=progress_service)

    def _fake_run_submission_with_timeout(payload):
        del payload
        raise ExecutionPipelineError(
            status_code=400,
            detail={"message": "Code validation failed.", "failure_kind": "test_failure"},
        )

    monkeypatch.setattr(
        "backend.services.execution_service.run_submission_with_timeout",
        _fake_run_submission_with_timeout,
    )

    try:
        service.execute_sync(
            {
                "lesson_id": "dp_policy_eval",
                "student_id": "student-1",
                "code": "def policy_evaluation(*args): return []",
            }
        )
    except ExecutionPipelineError:
        pass
    else:
        raise AssertionError("Expected execute_sync to propagate the pipeline failure.")

    assert progress_service.calls[0] == ("student-1", False, "test_failure")
