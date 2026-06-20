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


class TestTupleStateNormalisation:
    """Blackjack states are tuples; _to_json_safe must convert them to lists."""

    def test_tuple_state_becomes_list(self):
        step = {
            "state": (16, 10, False),
            "action": 1,
            "reward": 0.0,
            "next_state": (18, 10, False),
        }
        result = VisualizationController._normalize_step(step)
        assert result["state"] == [16, 10, False]
        assert result["next_state"] == [18, 10, False]

    def test_nested_tuple_inside_mc_details(self):
        step = {
            "state": (16, 10, False),
            "action": 0,
            "reward": -1.0,
            "next_state": (16, 10, False),
            "equation_update": {
                "kind": "mc_sampling",
                "mc_details": {"observation": {"player_sum": 16, "dealer_card": 10}},
            },
        }
        result = VisualizationController._normalize_step(step)
        assert isinstance(result["state"], list)
        assert result["equation_update"]["kind"] == "mc_sampling"

    def test_enqueue_replay_render_with_tuple_states_posts_list_state(self, monkeypatch):
        """End-to-end: tuple states in log_data must not cause a 422 when POSTed."""
        import json as _json

        captured_bodies: list[dict] = []

        class _CapturingHttp:
            def post(self, url, *, json, timeout):
                captured_bodies.append(json)
                return _StubResponse(payload={"job_id": "xyz789", "status": "queued"})

        monkeypatch.setenv("RL_IDE_MANIM_TIMEOUT_SECONDS", "10")
        controller = VisualizationController(
            base_url="http://manim:8200",
            http_client=_CapturingHttp(),
        )

        mc_log_data = [
            [
                {
                    "state": (16, 10, False),
                    "action": 1,
                    "reward": 0.0,
                    "next_state": (18, 10, False),
                    "equation_update": {
                        "kind": "mc_sampling",
                        "mc_details": {
                            "observation": {"player_sum": 16, "dealer_card": 10,
                                            "usable_ace": False},
                            "action_label": "Hit",
                            "reward": 0.0,
                            "terminated": False,
                        },
                    },
                }
            ]
        ]

        result = controller.enqueue_replay_render(mc_log_data, "mc_first_visit")

        assert result["replay_render_job_id"] == "xyz789"
        assert result["replay_render_status"] == "queued"
        body = captured_bodies[0]
        # state must be serialisable list, not a tuple (which json.dumps can't re-load as tuple)
        posted_state = body["episodes"][0]["steps"][0]["state"]
        assert isinstance(posted_state, list)
        assert posted_state == [16, 10, False]
        # Verify the body is fully JSON-serialisable (no remaining tuples)
        _json.dumps(body)

    def test_enqueue_replay_render_accepts_curated_trace_episodes(self, monkeypatch):
        captured_bodies: list[dict] = []

        class _CapturingHttp:
            def post(self, url, *, json, timeout):
                captured_bodies.append(json)
                return _StubResponse(payload={"job_id": "dp123", "status": "queued"})

        monkeypatch.setenv("RL_IDE_MANIM_TIMEOUT_SECONDS", "10")
        controller = VisualizationController(
            base_url="http://manim:8200",
            http_client=_CapturingHttp(),
        )

        trace_episodes = [
            {
                "episode_index": 7,
                "steps": [
                    {
                        "state": 0,
                        "action": -1,
                        "reward": 0.0,
                        "next_state": 0,
                        "equation_update": {"kind": "policy_evaluation"},
                    }
                ],
            }
        ]

        result = controller.enqueue_replay_render(trace_episodes, "dp_policy_eval")

        assert result["replay_render_job_id"] == "dp123"
        assert result["replay_render_status"] == "queued"
        assert result["replay_episode_indices"] == [7]
        body = captured_bodies[0]
        assert body["episodes"][0]["episode_index"] == 7
        assert body["episodes"][0]["steps"][0]["equation_update"]["kind"] == (
            "policy_evaluation"
        )

    def test_enqueue_replay_render_with_staged_td_payload_posts_episodes(self, monkeypatch):
        captured_bodies: list[dict] = []

        class _CapturingHttp:
            def post(self, url, *, json, timeout):
                captured_bodies.append(json)
                return _StubResponse(payload={"job_id": "stage123", "status": "queued"})

        monkeypatch.setenv("RL_IDE_MANIM_TIMEOUT_SECONDS", "10")
        controller = VisualizationController(
            base_url="http://manim:8200",
            http_client=_CapturingHttp(),
        )

        staged_log_data = [
            {
                "stage": "untrained",
                "stage_label": "① Untrained · episode 1",
                "episode_index": 0,
                "steps": [
                    {
                        "state": 1,
                        "action": 0,
                        "reward": -1.0,
                        "next_state": 2,
                    }
                ],
            },
            {
                "stage": "converged",
                "stage_label": "③ Converged · solved in 2 steps",
                "episode_index": 500,
                "steps": [
                    {
                        "state": 12,
                        "action": 2,
                        "reward": -1.0,
                        "next_state": 13,
                    },
                    {
                        "state": 13,
                        "action": 4,
                        "reward": 20.0,
                        "next_state": 14,
                    },
                ],
            },
        ]

        result = controller.enqueue_replay_render(staged_log_data, "td_q_learning")

        assert result["replay_render_job_id"] == "stage123"
        assert result["replay_render_status"] == "queued"
        assert result["replay_episode_indices"] == [0, 500]
        body = captured_bodies[0]
        # Staged payloads now route through the episodes path for parallel rendering.
        assert "episodes" in body
        assert [ep["role"] for ep in body["episodes"]] == ["untrained", "converged"]
        assert body["episodes"][0]["episode_index"] == 0
        assert body["episodes"][1]["episode_index"] == 500
        assert body["episodes"][0]["steps"][0]["state"] == 1
        # episode_trace.steps carries the last stage's steps as a legacy fallback.
        assert body["episode_trace"]["steps"][0]["state"] == 12
