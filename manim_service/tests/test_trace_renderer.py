"""Tests for manim_service.jobs.trace_renderer."""
from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from manim_service import settings as manim_settings
import manim_service.jobs.trace_renderer as trace_renderer
from manim_service.jobs.queue import Job, JobKind, JobStatus, MemoryJobQueue
from manim_service.jobs.trace_renderer import (
    RenderError,
    _canonical_cache_path,
    _canonical_clip_cache_path,
    _compute_clip_hash,
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


def test_trace_manim_accepts_interpreter_from_path(monkeypatch, tmp_path):
    data_json = tmp_path / "trace.json"
    data_json.write_text("[]")
    scene_file = tmp_path / "trace_replay_scene.py"
    scene_file.write_text("class TraceReplayScene: pass")
    rendered = (
        tmp_path
        / "manim_service"
        / "_manim_media"
        / "videos"
        / "trace_replay_scene"
        / "480p15"
        / "TraceReplayScene.mp4"
    )
    rendered.parent.mkdir(parents=True)
    rendered.write_bytes(b"mp4")

    monkeypatch.setattr(trace_renderer, "ROOT", tmp_path)
    monkeypatch.setattr(trace_renderer, "TRACE_SCENE_FILE", scene_file)
    monkeypatch.setattr(manim_settings, "MANIM_PYTHON", "python3")
    monkeypatch.setattr(manim_settings, "RENDER_QUALITY", "l")
    monkeypatch.setattr(manim_settings, "resolve_executable", lambda command: f"/bin/{command}")

    with patch("manim_service.jobs.trace_renderer.subprocess.run") as mock_run:
        result = trace_renderer._invoke_trace_manim(data_json)

    assert result == rendered
    assert mock_run.call_args.args[0][0] == "/bin/python3"


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

    def test_episode_clip_cache_reuses_hit_and_concats_ordered_clips(self, tmp_path):
        storage.ensure_subdirs()
        episode_hit = {
            "episode_index": 0,
            "role": "first",
            "steps": STEPS,
        }
        episode_miss = {
            "episode_index": 2,
            "role": "last",
            "steps": [
                {
                    "state": 2,
                    "action": 1,
                    "reward": 1.0,
                    "next_state": 3,
                }
            ],
        }
        hit_hash = _compute_clip_hash(LESSON_ID, episode_hit)
        hit_path = _canonical_clip_cache_path(LESSON_ID, "first", 0, hit_hash)
        hit_path.parent.mkdir(parents=True, exist_ok=True)
        hit_path.write_bytes(b"cached")

        fake_render = tmp_path / "fake_clip.mp4"
        fake_render.write_bytes(b"rendered")
        job = _make_trace_job(lesson_id=LESSON_ID, steps=STEPS)
        job.payload["episodes"] = [episode_hit, episode_miss]

        with patch(
            "manim_service.jobs.trace_renderer._invoke_trace_manim",
            return_value=fake_render,
        ) as mock_manim, patch(
            "manim_service.jobs.trace_renderer._concat_clips",
        ) as mock_concat:
            result = render_trace(job)

        mock_manim.assert_called_once()
        mock_concat.assert_called_once()
        ordered_paths = mock_concat.call_args.args[0]
        assert ordered_paths[0] == hit_path
        assert ordered_paths[1].is_file()
        assert result.name == f"{job.job_id}.mp4"
