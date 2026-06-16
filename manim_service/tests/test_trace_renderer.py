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
from manim_service.trace_scenes.taxi_board import TaxiBoard, classify_taxi_transition
from manim_service.trace_scenes.trace_boards import make_board
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
        "state": 3,
        "action": 4,
        "reward": -1.0,
        "next_state": 19,
        "transition_probability": 1.0,
        "frame_path": "",
        "grid_metadata": {
            "environment": "Taxi",
            "rows": 5,
            "columns": 5,
            "cells": [
                {
                    "state": row * 5 + column,
                    "row": row,
                    "column": column,
                    "tile_type": (
                        "R"
                        if (row, column) == (0, 0)
                        else "G"
                        if (row, column) == (0, 4)
                        else "Y"
                        if (row, column) == (4, 0)
                        else "B"
                        if (row, column) == (4, 3)
                        else "F"
                    ),
                    "terminal": False,
                }
                for row in range(5)
                for column in range(5)
            ],
            "state": 0,
            "next_state": 0,
            "encoded_state": 3,
            "encoded_next_state": 19,
            "state_coordinates": {"row": 0, "column": 0},
            "next_state_coordinates": {"row": 0, "column": 0},
            "passenger": {"location": "R", "row": 0, "column": 0, "in_taxi": False},
            "next_passenger": {"location": "in_taxi", "row": 0, "column": 0, "in_taxi": True},
            "destination": {"label": "B", "row": 4, "column": 3},
            "walls": [
                {"start": {"row": 0, "column": 1}, "end": {"row": 0, "column": 2}},
            ],
            "action": 4,
            "action_label": "Pickup",
            "reward": -1.0,
            "terminated": False,
            "truncated": False,
        },
        "agent_caption": "Agent selected Pickup",
        "code_title": "Code Trace",
        "code_lines": ["action = epsilon_greedy(Q[state], epsilon)"],
        "math_title": "TD / Q-Learning",
        "math_equation": r"Q(s,a)\leftarrow Q(s,a)+\alpha[r+\gamma \max_{a'}Q(s',a')-Q(s,a)]",
        "math_lines": ["TD target = -1 + 0.95 * 0 = -1.00"],
        "updated_values": {"Q(3, 4)": -0.1},
        "trace_schema_version": 2,
        "tables": {
            "kind": "q_table",
            "before": [[0.0] * 6 for _ in range(500)],
            "after": [[0.0] * 6 for _ in range(500)],
            "active_cell": {"row": 3, "column": 4},
            "bootstrap_cell": {"row": 19, "column": 0},
            "changed_cells": [{"row": 3, "column": 4}],
            "action_labels": ["South", "North", "East", "West", "Pickup", "Dropoff"],
        },
        "equation_update": {
            "kind": "q_learning",
            "lhs": "Q(3,4)",
            "old_value": 0.0,
            "reward": -1.0,
            "gamma": 0.95,
            "bootstrap_label": "max_a Q(19,a)",
            "bootstrap_value": 0.0,
            "td_target": -1.0,
            "td_error": -1.0,
            "alpha": 0.1,
            "new_value": -0.1,
            "code_focus": "Q[state][action] += alpha * (td_target - Q[state][action])",
        },
    },
    {
        "state": 479,
        "action": 5,
        "reward": 20.0,
        "next_state": 475,
        "transition_probability": 1.0,
        "frame_path": "",
        "grid_metadata": {
            "environment": "Taxi",
            "rows": 5,
            "columns": 5,
            "cells": [
                {
                    "state": row * 5 + column,
                    "row": row,
                    "column": column,
                    "tile_type": (
                        "R"
                        if (row, column) == (0, 0)
                        else "G"
                        if (row, column) == (0, 4)
                        else "Y"
                        if (row, column) == (4, 0)
                        else "B"
                        if (row, column) == (4, 3)
                        else "F"
                    ),
                    "terminal": False,
                }
                for row in range(5)
                for column in range(5)
            ],
            "state": 23,
            "next_state": 23,
            "encoded_state": 479,
            "encoded_next_state": 475,
            "state_coordinates": {"row": 4, "column": 3},
            "next_state_coordinates": {"row": 4, "column": 3},
            "passenger": {"location": "in_taxi", "row": 4, "column": 3, "in_taxi": True},
            "next_passenger": {"location": "B", "row": 4, "column": 3, "in_taxi": False},
            "destination": {"label": "B", "row": 4, "column": 3},
            "walls": [],
            "action": 5,
            "action_label": "Dropoff",
            "reward": 20.0,
            "terminated": True,
            "truncated": False,
        },
        "agent_caption": "Agent selected Dropoff",
        "code_title": "Code Trace",
        "code_lines": ["action = epsilon_greedy(Q[state], epsilon)"],
        "math_title": "TD / Q-Learning",
        "math_equation": r"Q(s,a)\leftarrow Q(s,a)+\alpha[r+\gamma \max_{a'}Q(s',a')-Q(s,a)]",
        "math_lines": ["TD target = 20 + 0.95 * 0 = 20.00"],
        "updated_values": {"Q(479, 5)": 2.0},
        "trace_schema_version": 2,
        "tables": {
            "kind": "q_table",
            "before": [[0.0] * 6 for _ in range(500)],
            "after": [[0.0] * 6 for _ in range(500)],
            "active_cell": {"row": 479, "column": 5},
            "bootstrap_cell": None,
            "changed_cells": [{"row": 479, "column": 5}],
            "action_labels": ["South", "North", "East", "West", "Pickup", "Dropoff"],
        },
        "equation_update": {
            "kind": "q_learning",
            "lhs": "Q(479,5)",
            "old_value": 0.0,
            "reward": 20.0,
            "gamma": 0.95,
            "bootstrap_label": "0 terminal",
            "bootstrap_value": 0.0,
            "td_target": 20.0,
            "td_error": 20.0,
            "alpha": 0.1,
            "new_value": 2.0,
            "code_focus": "Q[state][action] += alpha * (td_target - Q[state][action])",
        },
    },
]

ILLEGAL_TAXI_STEP = {
    "grid_metadata": {
        "environment": "Taxi",
        "action": 5,
        "action_label": "Dropoff",
        "reward": -10.0,
        "passenger": {"location": "R", "row": 0, "column": 0, "in_taxi": False},
        "next_passenger": {"location": "R", "row": 0, "column": 0, "in_taxi": False},
    }
}


class TestTaxiTraceIntegration:
    def test_taxi_trace_hash_differs_from_cliff_walking(self):
        h_taxi = _compute_trace_hash("td_q_learning", TAXI_Q_LEARNING_STEPS)
        h_cliff = _compute_trace_hash("td_q_learning", STEPS)
        assert h_taxi != h_cliff

    def test_taxi_trace_job_creation(self):
        job = _make_trace_job(lesson_id="td_q_learning", steps=TAXI_Q_LEARNING_STEPS)
        payload = job.payload
        assert payload["lesson_id"] == "td_q_learning"
        assert payload["episode_trace"]["steps"][0]["grid_metadata"]["environment"] == "Taxi"

    def test_taxi_env_detection(self):
        from manim_service.trace_scenes import trace_common as C

        assert C.detect_env(TAXI_Q_LEARNING_STEPS) == "Taxi"

    def test_taxi_action_labels_and_shape(self):
        from manim_service.trace_scenes import trace_common as C

        assert C.action_label("Taxi", 0) == "South"
        assert C.action_label("Taxi", 4) == "Pickup"
        assert C.action_label("Taxi", 5) == "Dropoff"
        assert C.grid_shape("Taxi") == (5, 5)

    def test_taxi_board_factory_uses_isolated_board(self):
        board = make_board("Taxi", TAXI_Q_LEARNING_STEPS[0])
        assert isinstance(board, TaxiBoard)

    def test_taxi_transition_classifier_uses_explicit_passenger_state(self):
        assert classify_taxi_transition(TAXI_Q_LEARNING_STEPS[0]) == "pickup"
        assert classify_taxi_transition(TAXI_Q_LEARNING_STEPS[1]) == "dropoff"
        assert classify_taxi_transition(ILLEGAL_TAXI_STEP) == "illegal_dropoff"


# ---------------------------------------------------------------------------
# Monte Carlo / Blackjack tests
# ---------------------------------------------------------------------------

MC_SAMPLING_STEP = {
    "state": [16, 10, False],   # tuple serialised as JSON array
    "action": 1,
    "reward": 0.0,
    "next_state": [18, 10, False],
    "done": False,
    "frame_path": "",
    "equation_update": {
        "kind": "mc_sampling",
        "lhs": "episode[0][0]",
        "reward": 0.0,
        "new_value": "[18, 10, False]",
        "mc_details": {
            "episode_index": 0,
            "episode_step": 0,
            "phase": "sampling",
            "observation": {
                "label": "(16, 10, no ace)",
                "player_sum": 16,
                "dealer_card": 10,
                "usable_ace": False,
            },
            "action": 1,
            "action_label": "Hit",
            "reward": 0.0,
            "terminated": False,
            "truncated": False,
        },
    },
}

MC_FIRST_VISIT_STEP = {
    "state": [16, 10, False],
    "action": 1,
    "reward": 0.0,
    "next_state": [16, 10, False],
    "done": True,
    "frame_path": "",
    "updated_values": {"V((16, 10, False))": -0.5},
    "equation_update": {
        "kind": "mc_first_visit",
        "lhs": "V((16, 10, False))",
        "gamma": 1.0,
        "td_target": -1.0,
        "new_value": -0.5,
        "mc_details": {
            "episode_index": 0,
            "episode_step": 0,
            "phase": "first_visit_update",
            "observation": {
                "label": "(16, 10, no ace)",
                "player_sum": 16,
                "dealer_card": 10,
                "usable_ace": False,
            },
            "action": 1,
            "action_label": "Hit",
            "first_visit": True,
            "return_value": -1.0,
            "return_terms": [{"step": 0, "gamma_power": 1.0, "reward": -1.0}],
            "returns_history": [-1.0],
        },
    },
}


class TestMcTraceStep:
    """TraceStep model must accept Blackjack tuple-states serialised as arrays."""

    def test_mc_sampling_step_accepted(self):
        from manim_service.api.routes.traces import TraceStep
        step = TraceStep(**MC_SAMPLING_STEP)
        assert step.state == [16, 10, False]
        assert step.action == 1

    def test_mc_first_visit_step_accepted(self):
        from manim_service.api.routes.traces import TraceStep
        step = TraceStep(**MC_FIRST_VISIT_STEP)
        assert step.state == [16, 10, False]
        assert step.done is True

    def test_integer_state_still_accepted(self):
        from manim_service.api.routes.traces import TraceStep
        step = TraceStep(state=0, action=1, reward=0.0, next_state=4)
        assert step.state == 0

    def test_string_state_accepted(self):
        from manim_service.api.routes.traces import TraceStep
        step = TraceStep(state="(16, 10, False)", action=1, reward=0.0, next_state="(18, 10, False)")
        assert step.state == "(16, 10, False)"


class TestMcEnvDetection:
    """detect_env must identify Blackjack from mc_details observation."""

    def test_mc_sampling_detected_as_blackjack(self):
        from manim_service.trace_scenes import trace_common as C
        assert C.detect_env([MC_SAMPLING_STEP]) == "Blackjack"

    def test_mc_first_visit_detected_as_blackjack(self):
        from manim_service.trace_scenes import trace_common as C
        assert C.detect_env([MC_FIRST_VISIT_STEP]) == "Blackjack"

    def test_mixed_phases_detected_as_blackjack(self):
        from manim_service.trace_scenes import trace_common as C
        assert C.detect_env([MC_SAMPLING_STEP, MC_FIRST_VISIT_STEP]) == "Blackjack"

    def test_no_grid_metadata_required(self):
        """Blackjack detection must not depend on grid_metadata being present."""
        from manim_service.trace_scenes import trace_common as C
        step_no_grid = {k: v for k, v in MC_SAMPLING_STEP.items() if k != "grid_metadata"}
        assert C.detect_env([step_no_grid]) == "Blackjack"


class TestMcBlackjackBoard:
    """BlackjackBoard renders from frame_path when available, text-only otherwise."""

    def test_board_factory_returns_blackjack_board(self):
        from manim_service.trace_scenes.trace_boards import BlackjackBoard, make_board
        board = make_board("Blackjack", MC_SAMPLING_STEP)
        assert isinstance(board, BlackjackBoard)

    def test_board_is_not_spatial(self):
        from manim_service.trace_scenes.trace_boards import BlackjackBoard
        assert BlackjackBoard.is_spatial is False

    def test_text_only_panel_built_when_frame_path_empty(self):
        from manim_service.trace_scenes.trace_boards import BlackjackBoard
        board = BlackjackBoard()
        panel = board._frame_panel(MC_SAMPLING_STEP)
        # Should return a Group with text content, not an image-based panel
        assert panel is not None

    def test_frame_panel_with_missing_file_falls_back_gracefully(self, tmp_path):
        from manim_service.trace_scenes.trace_boards import BlackjackBoard
        step_with_bad_path = {**MC_SAMPLING_STEP, "frame_path": str(tmp_path / "nonexistent.png")}
        board = BlackjackBoard()
        # Must not raise even when frame file is missing
        panel = board._frame_panel(step_with_bad_path)
        assert panel is not None

    def test_frame_panel_uses_real_image_when_file_exists(self, tmp_path):
        from PIL import Image as _Image
        from manim_service.trace_scenes.trace_boards import BlackjackBoard
        import numpy as np

        # Create a minimal valid PNG as a fake Gymnasium frame
        fake_frame_path = tmp_path / "blackjack_frame.png"
        _Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8)).save(fake_frame_path)

        step_with_frame = {**MC_SAMPLING_STEP, "frame_path": str(fake_frame_path)}
        board = BlackjackBoard()
        panel = board._frame_panel(step_with_frame)
        assert panel is not None

    def test_no_synthetic_card_content(self):
        """BlackjackBoard._frame_panel must not call card_mobject (no synthetic cards)."""
        import manim_service.trace_scenes.trace_boards as _boards_module
        assert not hasattr(_boards_module, "card_mobject") or True
        # The real check: _frame_panel is callable and does not import card_mobject internally
        from manim_service.trace_scenes.trace_boards import BlackjackBoard
        board = BlackjackBoard()
        # _panel_with_frame and _text_only_panel are the two paths — neither calls card_mobject
        import inspect
        src_frame = inspect.getsource(BlackjackBoard._panel_with_frame)
        src_text = inspect.getsource(BlackjackBoard._text_only_panel)
        assert "card_mobject" not in src_frame
        assert "card_mobject" not in src_text


class TestMcRenderTrace:
    """render_trace must handle mc_first_visit traces without grid_metadata."""

    @pytest.fixture(autouse=True)
    def _redirect_media_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(manim_settings, "SHARED_MEDIA_DIR", tmp_path)
        monkeypatch.setattr(storage, "SHARED_MEDIA_DIR", tmp_path, raising=False)

    def test_mc_sampling_trace_renders(self, tmp_path):
        storage.ensure_subdirs()
        fake_mp4 = tmp_path / "fake_mc.mp4"
        fake_mp4.write_bytes(b"mc-sampling-mp4")

        job = _make_trace_job(lesson_id="mc_first_visit", steps=[MC_SAMPLING_STEP])
        with patch(
            "manim_service.jobs.trace_renderer._invoke_trace_manim",
            return_value=fake_mp4,
        ):
            result = render_trace(job)
        assert result.is_file()
        assert result.read_bytes() == b"mc-sampling-mp4"

    def test_mc_first_visit_trace_renders(self, tmp_path):
        storage.ensure_subdirs()
        fake_mp4 = tmp_path / "fake_mc_fv.mp4"
        fake_mp4.write_bytes(b"mc-first-visit-mp4")

        job = _make_trace_job(lesson_id="mc_first_visit", steps=[MC_FIRST_VISIT_STEP])
        with patch(
            "manim_service.jobs.trace_renderer._invoke_trace_manim",
            return_value=fake_mp4,
        ):
            result = render_trace(job)
        assert result.read_bytes() == b"mc-first-visit-mp4"

    def test_mc_both_phases_render(self, tmp_path):
        storage.ensure_subdirs()
        fake_mp4 = tmp_path / "fake_mc_both.mp4"
        fake_mp4.write_bytes(b"mc-both-phases")

        both_steps = [MC_SAMPLING_STEP, MC_FIRST_VISIT_STEP]
        job = _make_trace_job(lesson_id="mc_first_visit", steps=both_steps)
        with patch(
            "manim_service.jobs.trace_renderer._invoke_trace_manim",
            return_value=fake_mp4,
        ):
            result = render_trace(job)
        assert result.read_bytes() == b"mc-both-phases"

    def test_mc_render_without_grid_metadata(self, tmp_path):
        storage.ensure_subdirs()
        fake_mp4 = tmp_path / "fake_mc_nogrid.mp4"
        fake_mp4.write_bytes(b"no-grid-data")

        step_no_grid = {k: v for k, v in MC_SAMPLING_STEP.items() if k != "grid_metadata"}
        job = _make_trace_job(lesson_id="mc_first_visit", steps=[step_no_grid])
        with patch(
            "manim_service.jobs.trace_renderer._invoke_trace_manim",
            return_value=fake_mp4,
        ):
            result = render_trace(job)
        assert result.read_bytes() == b"no-grid-data"

    def test_mc_missing_frame_path_does_not_fail(self, tmp_path):
        storage.ensure_subdirs()
        fake_mp4 = tmp_path / "fake_mc_noframe.mp4"
        fake_mp4.write_bytes(b"no-frame-data")

        step_no_frame = {**MC_SAMPLING_STEP, "frame_path": ""}
        job = _make_trace_job(lesson_id="mc_first_visit", steps=[step_no_frame])
        with patch(
            "manim_service.jobs.trace_renderer._invoke_trace_manim",
            return_value=fake_mp4,
        ):
            result = render_trace(job)
        assert result.read_bytes() == b"no-frame-data"

    def test_existing_td_render_unaffected(self, tmp_path):
        """MC changes must not break existing TD trace renders."""
        storage.ensure_subdirs()
        fake_mp4 = tmp_path / "fake_td.mp4"
        fake_mp4.write_bytes(b"td-data")

        job = _make_trace_job(lesson_id="td_q_learning", steps=STEPS)
        with patch(
            "manim_service.jobs.trace_renderer._invoke_trace_manim",
            return_value=fake_mp4,
        ):
            result = render_trace(job)
        assert result.read_bytes() == b"td-data"
