from __future__ import annotations

from typing import Any

import pytest

from backend.visualization.controller import VisualizationController


class _StubResponse:
    def __init__(self, status_code: int = 200, payload: dict[str, Any] | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise AssertionError(f"unexpected status {self.status_code}")

    def json(self) -> dict[str, Any]:
        return self._payload


class _StubHttp:
    """Records calls and replays a scripted sequence of responses."""

    def __init__(self, responses: list[_StubResponse]):
        self.calls: list[tuple[str, str, dict[str, Any]]] = []
        self._responses = list(responses)

    def post(self, url: str, *, json: dict[str, Any], timeout: int):
        self.calls.append(("POST", url, json))
        return self._responses.pop(0)

    def get(self, url: str, *, timeout: int):
        self.calls.append(("GET", url, {}))
        return self._responses.pop(0)


@pytest.fixture
def log_data() -> list:
    return [[{"state": 0, "action": 1, "reward": 0, "next_state": 1}]]


def test_returns_video_url_when_job_completes(monkeypatch, log_data):
    monkeypatch.setenv("RL_IDE_MANIM_TIMEOUT_SECONDS", "10")
    http = _StubHttp(
        [
            _StubResponse(payload={"job_id": "abc123", "status": "queued"}),
            _StubResponse(payload={"job_id": "abc123", "status": "rendering"}),
            _StubResponse(
                payload={
                    "job_id": "abc123",
                    "status": "complete",
                    "video_url": "/videos/td_q_learning.mp4",
                }
            ),
        ]
    )
    controller = VisualizationController(
        base_url="http://manim:8200",
        poll_interval_seconds=0,
        http_client=http,
    )

    url = controller.generate_animation(log_data, "td_q_learning")

    assert url == "http://manim:8200/videos/td_q_learning.mp4"
    assert http.calls[0][0] == "POST"
    assert http.calls[0][1] == "http://manim:8200/render/trace"
    assert http.calls[0][2]["lesson_id"] == "td_q_learning"
    assert http.calls[0][2]["episode_trace"]["steps"][0]["done"] is False


def test_returns_empty_string_when_job_fails(monkeypatch, log_data):
    monkeypatch.setenv("RL_IDE_MANIM_TIMEOUT_SECONDS", "10")
    http = _StubHttp(
        [
            _StubResponse(payload={"job_id": "abc123", "status": "queued"}),
            _StubResponse(
                payload={"job_id": "abc123", "status": "failed", "error": "render error"}
            ),
        ]
    )
    controller = VisualizationController(
        base_url="http://manim:8200",
        poll_interval_seconds=0,
        http_client=http,
    )

    url = controller.generate_animation(log_data, "td_q_learning")

    assert url == ""


def test_returns_empty_string_on_empty_log_data():
    controller = VisualizationController(base_url="http://manim:8200")
    assert controller.generate_animation([], "td_q_learning") == ""
    assert controller.generate_animation([[]], "td_q_learning") == ""
