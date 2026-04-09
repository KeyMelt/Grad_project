from __future__ import annotations

import time

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
