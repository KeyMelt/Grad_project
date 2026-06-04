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
    return [[{"state": 0, "action": 1, "reward": 0, "next_state": 1, "done": False}]]


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


def test_enqueue_replay_render_posts_first_middle_last_clips(monkeypatch):
    monkeypatch.setenv("RL_IDE_MANIM_TIMEOUT_SECONDS", "10")
    http = _StubHttp([_StubResponse(payload={"job_id": "render123", "status": "queued"})])
    controller = VisualizationController(
        base_url="http://manim:8200",
        poll_interval_seconds=0,
        http_client=http,
    )
    log_data = [
        [{"state": 0, "action": 1, "reward": 0, "next_state": 1}],
        [{"state": 1, "action": 1, "reward": 0, "next_state": 2}],
        [{"state": 2, "action": 1, "reward": 0, "next_state": 3}],
        [{"state": 3, "action": 1, "reward": 1, "next_state": 4}],
        [{"state": 4, "action": 1, "reward": 2, "next_state": 5}],
    ]

    result = controller.enqueue_replay_render(log_data, "td_q_learning")

    assert result == {
        "replay_render_job_id": "render123",
        "replay_render_status": "queued",
        "replay_episode_indices": [0, 2, 4],
    }
    payload = http.calls[0][2]
    assert [episode["role"] for episode in payload["episodes"]] == ["first", "middle", "last"]
    assert [episode["episode_index"] for episode in payload["episodes"]] == [0, 2, 4]
    assert payload["episode_trace"]["steps"] == payload["episodes"][-1]["steps"]


def test_clip_episode_steps_is_bounded_and_deduplicated():
    steps = [
        {"state": index, "action": 1, "reward": 0, "next_state": index + 1}
        for index in range(10)
    ]
    steps[2]["updated_values"] = {"V(2)": 0.1}
    steps[5]["updated_values"] = {"V(5)": 2.0}
    steps[9]["terminated"] = True

    clipped = VisualizationController._clip_episode_steps(steps)

    assert len(clipped) <= 5
    assert clipped[0]["state"] == 0
    assert clipped[-1]["state"] == 9
    assert len({step["state"] for step in clipped}) == len(clipped)
    assert any(step["state"] == 5 for step in clipped)


def test_selected_episode_indices_handles_small_counts():
    assert VisualizationController._selected_episode_indices([[1]]) == [0]
    assert VisualizationController._selected_episode_indices([[1], [2]]) == [0, 1]
    assert VisualizationController._selected_episode_indices([[1], [2], [3]]) == [0, 1, 2]


class TestNormalizeStepRichFields:
    """_normalize_step must preserve all rich fields and convert numpy types."""

    def test_preserves_all_rich_fields(self):
        step = {
            "state": 3,
            "action": 1,
            "reward": 0.5,
            "next_state": 4,
            "done": False,
            "agent_caption": "Agent moves right",
            "code_lines": ["q[s,a] += alpha * td_error"],
            "math_equation": r"Q(s,a) \leftarrow Q(s,a) + \alpha \delta",
            "math_lines": ["td_error = 0.1"],
            "updated_values": {"Q(3,1)": 0.42},
            "equation_update": {"reward": 0.5, "gamma": 0.99, "lhs": "Q(3,1)"},
        }
        result = VisualizationController._normalize_step(step)
        assert result["agent_caption"] == "Agent moves right"
        assert result["code_lines"] == ["q[s,a] += alpha * td_error"]
        assert result["math_equation"] == r"Q(s,a) \leftarrow Q(s,a) + \alpha \delta"
        assert result["updated_values"] == {"Q(3,1)": 0.42}
        assert result["equation_update"]["reward"] == 0.5

    def test_converts_numpy_int(self):
        try:
            import numpy as np
        except ImportError:
            pytest.skip("numpy not installed")
        step = {"state": np.int64(5), "action": np.int32(2), "reward": np.float32(1.0),
                "next_state": np.int64(6), "done": False,
                "equation_update": {"reward": np.float64(1.0), "gamma": np.float32(0.9)}}
        result = VisualizationController._normalize_step(step)
        assert type(result["state"]) is int
        assert type(result["action"]) is int
        assert type(result["reward"]) is float
        assert type(result["equation_update"]["reward"]) is float
        assert type(result["equation_update"]["gamma"]) is float

    def test_numpy_in_list_field(self):
        try:
            import numpy as np
        except ImportError:
            pytest.skip("numpy not installed")
        step = {"state": 0, "action": 0, "reward": 0.0, "next_state": 1,
                "math_lines": [np.str_("hello"), "world"]}
        result = VisualizationController._normalize_step(step)
        # list must survive; non-numpy elements pass through unchanged
        assert result["math_lines"][1] == "world"
