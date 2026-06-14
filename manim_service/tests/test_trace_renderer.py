"""Tests for manim_service.jobs.trace_renderer."""
from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from manim_service import settings as manim_settings
from manim_service.jobs.queue import Job, JobKind, JobStatus, MemoryJobQueue
from manim_service.jobs.trace_renderer import (
    RenderError,
    _canonical_cache_path,
    _compute_trace_hash,
    render_trace,
)
from manim_service.storage import output as storage
from manim_service.trace_scenes.trace_replay_scene import _parse_updated_values


def _make_trace_job(lesson_id: str = "td_q_learning", steps: list | None = None) -> Job:
    """Build a minimal TRACE job without using the global queue singleton."""
    if steps is None:
        steps = [
            {
                "state": 0,
                "action": 1,
                "reward": 0.0,
                "next_state": 4,
                "done": False,
                "math_equation": r"Q(s,a) \leftarrow ...",
                "agent_caption": "Moving down",
            }
        ]
    # Use MemoryJobQueue.enqueue to generate a real job_id, then retrieve the Job
    q = MemoryJobQueue()
    job_id = q.enqueue(
        JobKind.TRACE,
        {
            "lesson_id": lesson_id,
            "episode_trace": {"steps": steps},
        },
    )
    return q.get(job_id)


class TestComputeTraceHash:
    def test_deterministic(self):
        steps = [{"state": 0, "action": 1, "reward": 0.5, "next_state": 1}]
        h1 = _compute_trace_hash("td_q_learning", steps)
        h2 = _compute_trace_hash("td_q_learning", steps)
        assert h1 == h2

    def test_different_lesson_ids(self):
        steps = [{"state": 0, "action": 1, "reward": 0.5, "next_state": 1}]
        h1 = _compute_trace_hash("td_q_learning", steps)
        h2 = _compute_trace_hash("td_sarsa", steps)
        assert h1 != h2

    def test_different_steps(self):
        steps_a = [{"state": 0, "action": 1, "reward": 0.5, "next_state": 1}]
        steps_b = [{"state": 0, "action": 2, "reward": 0.5, "next_state": 1}]
        assert _compute_trace_hash("td_q_learning", steps_a) != _compute_trace_hash(
            "td_q_learning", steps_b
        )

    def test_different_render_quality(self, monkeypatch):
        steps = [{"state": 0, "action": 1, "reward": 0.5, "next_state": 1}]
        monkeypatch.setattr(manim_settings, "RENDER_QUALITY", "l")
        low_hash = _compute_trace_hash("td_q_learning", steps)
        monkeypatch.setattr(manim_settings, "RENDER_QUALITY", "m")
        medium_hash = _compute_trace_hash("td_q_learning", steps)
        assert low_hash != medium_hash

    def test_returns_16_hex_chars(self):
        h = _compute_trace_hash("dp_policy_eval", [])
        assert len(h) == 16
        assert all(c in "0123456789abcdef" for c in h)


def test_trace_scene_parses_q_table_updated_values_as_source_state():
    parsed = _parse_updated_values({"Q(3, 1)": 0.42, "Q(7,2)": -0.5, "V(9)": 1.0})

    assert parsed == {3: 0.42, 7: -0.5, 9: 1.0}


LESSON_ID = "td_q_learning"
STEPS = [
    {
        "state": 0,
        "action": 1,
        "reward": 0.0,
        "next_state": 4,
        "done": False,
        "math_equation": r"Q(s,a) \leftarrow ...",
        "agent_caption": "Moving down",
    }
]


class TestRenderTrace:
    def test_empty_steps_raises(self):
        job = _make_trace_job(steps=[])
        with pytest.raises(RenderError, match="empty steps"):
            render_trace(job)

    def test_missing_lesson_id_raises(self):
        job = _make_trace_job(lesson_id="")
        with pytest.raises(RenderError, match="lesson_id"):
            render_trace(job)

    @pytest.fixture(autouse=True)
    def _redirect_media_dir(self, tmp_path, monkeypatch):
        """Redirect SHARED_MEDIA_DIR for all TestRenderTrace tests.

        ``storage.output`` reads ``settings.SHARED_MEDIA_DIR`` at call time for
        most helpers, but ``_canonical_cache_path`` in ``trace_renderer`` also
        reads ``storage.SHARED_MEDIA_DIR`` directly (which is an alias added by
        the module for convenience).  We patch both entry points so that every
        path that render_trace constructs lands under ``tmp_path``.
        """
        monkeypatch.setattr(manim_settings, "SHARED_MEDIA_DIR", tmp_path)
        # ``storage.SHARED_MEDIA_DIR`` is referenced by ``_canonical_cache_path``
        # in trace_renderer; add the attribute if absent, patch if present.
        monkeypatch.setattr(storage, "SHARED_MEDIA_DIR", tmp_path, raising=False)

    def test_cache_hit_skips_manim(self, tmp_path):
        """If the canonical cache file exists, Manim is never invoked."""
        storage.ensure_subdirs()

        job = _make_trace_job(lesson_id=LESSON_ID, steps=STEPS)
        trace_hash = _compute_trace_hash(LESSON_ID, STEPS)

        # Place a pre-existing canonical cache file
        canonical = tmp_path / storage.TRACES_SUBDIR / f"{LESSON_ID}_{trace_hash}.mp4"
        canonical.parent.mkdir(parents=True, exist_ok=True)
        canonical.write_bytes(b"fake-mp4-data")

        with patch("manim_service.jobs.trace_renderer._invoke_trace_manim") as mock_manim:
            result = render_trace(job)
            mock_manim.assert_not_called()

        assert result.read_bytes() == b"fake-mp4-data"

    def test_cache_miss_invokes_manim_once(self, tmp_path):
        """On cache miss, Manim is invoked once and result is cached."""
        storage.ensure_subdirs()

        # The fake "rendered" file that _invoke_trace_manim would produce
        fake_mp4 = tmp_path / "fake_rendered.mp4"
        fake_mp4.write_bytes(b"rendered-mp4")

        job = _make_trace_job(lesson_id=LESSON_ID, steps=STEPS)

        with patch(
            "manim_service.jobs.trace_renderer._invoke_trace_manim",
            return_value=fake_mp4,
        ) as mock_manim:
            result = render_trace(job)
            mock_manim.assert_called_once()

        assert result.is_file()
        assert result.read_bytes() == b"rendered-mp4"

        # Canonical cache entry must also exist after the first render
        trace_hash = _compute_trace_hash(LESSON_ID, STEPS)
        canonical = tmp_path / storage.TRACES_SUBDIR / f"{LESSON_ID}_{trace_hash}.mp4"
        assert canonical.is_file()
        assert canonical.read_bytes() == b"rendered-mp4"

    def test_second_call_uses_cache(self, tmp_path):
        """A second render of the identical (lesson_id, steps) uses the cache."""
        storage.ensure_subdirs()

        fake_mp4 = tmp_path / "fake_rendered.mp4"
        fake_mp4.write_bytes(b"rendered-once")

        job_first = _make_trace_job(lesson_id=LESSON_ID, steps=STEPS)
        job_second = _make_trace_job(lesson_id=LESSON_ID, steps=STEPS)

        with patch(
            "manim_service.jobs.trace_renderer._invoke_trace_manim",
            return_value=fake_mp4,
        ) as mock_manim:
            render_trace(job_first)
            render_trace(job_second)
            # Manim should only have been called for the first render
            assert mock_manim.call_count == 1

    def test_result_is_job_specific_path(self, tmp_path):
        """render_trace returns the job-specific path, not the canonical cache path."""
        storage.ensure_subdirs()

        fake_mp4 = tmp_path / "fake_rendered.mp4"
        fake_mp4.write_bytes(b"data")

        job = _make_trace_job(lesson_id=LESSON_ID, steps=STEPS)

        with patch(
            "manim_service.jobs.trace_renderer._invoke_trace_manim",
            return_value=fake_mp4,
        ):
            result = render_trace(job)

        # Job-specific path contains the job_id, not the hash
        assert job.job_id in result.name


TAXI_Q_LEARNING_STEPS = [
    {
        "state": 328,
        "action": 0,
        "reward": -1.0,
        "next_state": 428,
        "transition_probability": 1.0,
        "frame_path": "",
        "grid_metadata": {
            "environment": "Taxi",
            "rows": 5,
            "columns": 5,
            "cells": [
                {"state": r * 5 + c, "row": r, "column": c, "tile_type": "F", "terminal": False}
                for r in range(5)
                for c in range(5)
            ],
            "state": 13,
            "next_state": 18,
            "encoded_state": 328,
            "encoded_next_state": 428,
            "state_coordinates": {"row": 2, "column": 3},
            "next_state_coordinates": {"row": 3, "column": 3},
            "passenger": {"location": "R", "row": 0, "column": 0, "in_taxi": False},
            "destination": {"label": "B", "row": 4, "column": 3},
            "action": 0,
            "action_label": "South",
            "reward": -1.0,
            "terminated": False,
            "truncated": False,
        },
        "agent_caption": "Agent selected South",
        "code_title": "Code Trace",
        "code_lines": ["action = epsilon_greedy(Q[state], epsilon)"],
        "math_title": "TD / Q-Learning",
        "math_equation": r"Q(s,a)\leftarrow Q(s,a)+\alpha[r+\gamma \max_{a'}Q(s',a')-Q(s,a)]",
        "math_lines": ["TD target = -1 + 0.95 * 0 = -0.95"],
        "updated_values": {"Q(328, 0)": -0.095},
        "trace_schema_version": 2,
        "tables": {
            "kind": "q_table",
            "before": [[0.0] * 6 for _ in range(500)],
            "after": [[0.0] * 6 for _ in range(500)],
            "active_cell": {"row": 328, "column": 0},
            "bootstrap_cell": {"row": 428, "column": 0},
            "changed_cells": [{"row": 328, "column": 0}],
            "action_labels": ["South", "North", "East", "West", "Pickup", "Dropoff"],
        },
        "equation_update": {
            "kind": "q_learning",
            "lhs": "Q(328,0)",
            "old_value": 0.0,
            "reward": -1.0,
            "gamma": 0.95,
            "bootstrap_label": "max_a Q(428,a)",
            "bootstrap_value": 0.0,
            "td_target": -1.0,
            "td_error": -1.0,
            "alpha": 0.1,
            "new_value": -0.1,
            "code_focus": "Q[state][action] += alpha * (td_target - Q[state][action])",
        },
    },
    {
        "state": 428,
        "action": 5,
        "reward": -10.0,
        "next_state": 428,
        "transition_probability": 1.0,
        "frame_path": "",
        "grid_metadata": {
            "environment": "Taxi",
            "rows": 5,
            "columns": 5,
            "cells": [
                {"state": r * 5 + c, "row": r, "column": c, "tile_type": "F", "terminal": False}
                for r in range(5)
                for c in range(5)
            ],
            "state": 18,
            "next_state": 18,
            "encoded_state": 428,
            "encoded_next_state": 428,
            "state_coordinates": {"row": 3, "column": 3},
            "next_state_coordinates": {"row": 3, "column": 3},
            "passenger": {"location": "R", "row": 0, "column": 0, "in_taxi": False},
            "destination": {"label": "B", "row": 4, "column": 3},
            "action": 5,
            "action_label": "Dropoff",
            "reward": -10.0,
            "terminated": False,
            "truncated": False,
        },
        "agent_caption": "Agent selected Dropoff (illegal)",
        "code_title": "Code Trace",
        "code_lines": ["action = epsilon_greedy(Q[state], epsilon)"],
        "math_title": "TD / Q-Learning",
        "math_equation": r"Q(s,a)\leftarrow Q(s,a)+\alpha[r+\gamma \max_{a'}Q(s',a')-Q(s,a)]",
        "math_lines": ["TD target = -10 + 0.95 * 0 = -9.50"],
        "updated_values": {"Q(428, 5)": -0.95},
        "trace_schema_version": 2,
        "tables": {
            "kind": "q_table",
            "before": [[0.0] * 6 for _ in range(500)],
            "after": [[0.0] * 6 for _ in range(500)],
            "active_cell": {"row": 428, "column": 5},
            "bootstrap_cell": {"row": 428, "column": 0},
            "changed_cells": [{"row": 428, "column": 5}],
            "action_labels": ["South", "North", "East", "West", "Pickup", "Dropoff"],
        },
        "equation_update": {
            "kind": "q_learning",
            "lhs": "Q(428,5)",
            "old_value": 0.0,
            "reward": -10.0,
            "gamma": 0.95,
            "bootstrap_label": "max_a Q(428,a)",
            "bootstrap_value": 0.0,
            "td_target": -10.0,
            "td_error": -10.0,
            "alpha": 0.1,
            "new_value": -1.0,
            "code_focus": "Q[state][action] += alpha * (td_target - Q[state][action])",
        },
    },
]


class TestTaxiTraceIntegration:
    def test_taxi_trace_hash_differs_from_cliff_walking(self):
        h_taxi = _compute_trace_hash("td_q_learning", TAXI_Q_LEARNING_STEPS)
        h_cliff = _compute_trace_hash("td_q_learning", STEPS)
        assert h_taxi != h_cliff

    def test_taxi_trace_job_creation(self):
        job = _make_trace_job(lesson_id="td_q_learning", steps=TAXI_Q_LEARNING_STEPS)
        payload = job.payload
        assert payload["lesson_id"] == "td_q_learning"
        steps = payload["episode_trace"]["steps"]
        assert len(steps) == 2
        assert steps[0]["grid_metadata"]["environment"] == "Taxi"
        assert steps[0]["equation_update"]["kind"] == "q_learning"
        assert steps[1]["grid_metadata"]["passenger"]["in_taxi"] is False
        assert steps[1]["equation_update"]["reward"] == -10.0

    def test_taxi_env_detection(self):
        from manim_service.trace_scenes import trace_common as C
        env = C.detect_env(TAXI_Q_LEARNING_STEPS)
        assert env == "Taxi"

    def test_taxi_td_pieces_extraction(self):
        from manim_service.trace_scenes import trace_common as C
        pieces = C.td_pieces(TAXI_Q_LEARNING_STEPS[0])
        assert pieces is not None
        assert pieces["kind"] == "q_learning"
        assert pieces["reward"] == -1.0
        assert pieces["bootstrap_value"] == 0.0
        assert pieces["on_policy"] is False

    def test_taxi_action_labels(self):
        from manim_service.trace_scenes import trace_common as C
        assert C.action_label("Taxi", 0) == "South"
        assert C.action_label("Taxi", 4) == "Pickup"
        assert C.action_label("Taxi", 5) == "Dropoff"

    def test_taxi_grid_shape(self):
        from manim_service.trace_scenes import trace_common as C
        assert C.grid_shape("Taxi") == (5, 5)
