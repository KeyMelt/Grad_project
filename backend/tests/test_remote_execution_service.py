from __future__ import annotations

from typing import Any

import pytest
import requests

from backend.execution_runtime import ExecutionPipelineError
from backend.services.remote_execution_service import RemoteExecutionService


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, Any] | None = None, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self) -> dict[str, Any]:
        if self._payload is None:
            raise ValueError("No JSON payload")
        return self._payload


def test_submit_proxies_to_worker(monkeypatch):
    def _fake_request(**kwargs):
        assert kwargs["url"].endswith("/internal/jobs")
        return _FakeResponse(200, {"task_id": "task-1", "status": "queued"})

    monkeypatch.setattr(requests, "request", _fake_request)
    service = RemoteExecutionService(worker_base_url="http://127.0.0.1:8100")
    payload = service.submit({"lesson_id": "dp_policy_eval", "code": "print('x')"})
    assert payload["task_id"] == "task-1"


def test_snapshot_returns_none_on_404(monkeypatch):
    monkeypatch.setattr(
        requests,
        "request",
        lambda **kwargs: _FakeResponse(404, {"detail": "not found"}),
    )
    service = RemoteExecutionService(worker_base_url="http://127.0.0.1:8100")
    assert service.snapshot("missing") is None


def test_execute_sync_raises_pipeline_error_on_worker_error(monkeypatch):
    monkeypatch.setattr(
        requests,
        "request",
        lambda **kwargs: _FakeResponse(400, {"detail": {"message": "validation failed"}}),
    )
    service = RemoteExecutionService(worker_base_url="http://127.0.0.1:8100")
    with pytest.raises(ExecutionPipelineError) as error:
        service.execute_sync({"lesson_id": "x", "code": "print('x')"})
    assert error.value.status_code == 400


def test_snapshot_refreshes_live_replay_status(monkeypatch):
    monkeypatch.setattr(
        requests,
        "request",
        lambda **kwargs: _FakeResponse(
            200,
            {
                "task_id": "task-1",
                "status": "succeeded",
                "owner_user_id": "student-1",
                "owner_role": "student",
                "created_at_utc": "2026-01-01T00:00:00+00:00",
                "result": {
                    "replay_render_job_id": "job-1",
                    "replay_render_status": "queued",
                    "replay_state": "queued",
                    "video_path": "",
                    "visualization_ready": False,
                },
            },
        ),
    )
    monkeypatch.setattr(
        "backend.services.remote_execution_service.enrich_snapshot_with_replay",
        lambda snapshot, timeout_seconds: {
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

    service = RemoteExecutionService(worker_base_url="http://127.0.0.1:8100")
    snapshot = service.snapshot("task-1")

    assert snapshot is not None
    assert snapshot["result"]["replay_state"] == "ready"
    assert snapshot["result"]["video_path"].endswith("/videos/job-1.mp4")


def test_network_failure_maps_to_503(monkeypatch):
    def _raise_request_exception(**kwargs):
        raise requests.RequestException("connection failed")

    monkeypatch.setattr(requests, "request", _raise_request_exception)
    service = RemoteExecutionService(worker_base_url="http://127.0.0.1:8100")
    with pytest.raises(ExecutionPipelineError) as error:
        service.submit({"lesson_id": "x", "code": "print('x')"})
    assert error.value.status_code == 503
