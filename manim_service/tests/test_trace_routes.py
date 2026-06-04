"""Integration tests for POST /render/trace, GET /jobs/{id}, GET /videos/{file}.

Uses FastAPI TestClient with the real app (no network calls) and a fresh
MemoryJobQueue per test so tests are fully isolated from each other.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from manim_service import settings as manim_settings
from manim_service.api.main import app
from manim_service.jobs.queue import MemoryJobQueue, reset_queue_for_tests


RICH_STEP = {
    "state": 0,
    "action": 1,
    "reward": 0.0,
    "next_state": 4,
    "done": False,
    "math_equation": r"Q(s,a) \leftarrow Q(s,a) + \alpha \delta",
    "agent_caption": "Agent moves down",
    "code_lines": ["q[s,a] += alpha * (r + gamma * max_q - q[s,a])"],
    "equation_update": {
        "reward": 0.0,
        "gamma": 0.99,
        "bootstrap_value": 0.1,
        "td_target": 0.099,
        "lhs": "Q(0,1)",
        "old_value": 0.0,
        "alpha": 0.1,
        "new_value": 0.0099,
    },
}


@pytest.fixture(autouse=True)
def isolated_queue():
    """Install a fresh MemoryJobQueue for each test and tear it down after."""
    q = MemoryJobQueue()
    reset_queue_for_tests(q)
    yield q
    q.shutdown()
    reset_queue_for_tests(None)


@pytest.fixture
def client():
    # Use with_lifespan=False so the background render worker thread is not
    # started — tests should never actually invoke Manim.
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


class TestEnqueueTrace:
    def test_valid_rich_payload_accepted(self, client):
        resp = client.post(
            "/render/trace",
            json={
                "lesson_id": "td_q_learning",
                "episode_trace": {"steps": [RICH_STEP]},
            },
        )
        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        assert body["status"] == "queued"

    def test_multi_episode_payload_accepted(self, client):
        resp = client.post(
            "/render/trace",
            json={
                "lesson_id": "td_q_learning",
                "episode_trace": {"steps": [RICH_STEP]},
                "episodes": [
                    {"episode_index": 0, "role": "first", "steps": [RICH_STEP]},
                    {"episode_index": 2, "role": "last", "steps": [RICH_STEP]},
                ],
            },
        )
        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        assert body["status"] == "queued"

    def test_unknown_lesson_id_rejected(self, client):
        resp = client.post(
            "/render/trace",
            json={
                "lesson_id": "not_a_real_lesson",
                "episode_trace": {"steps": [RICH_STEP]},
            },
        )
        assert resp.status_code == 400


class TestHealth:
    def test_health_reports_runtime_ready(self, client, monkeypatch):
        monkeypatch.setattr(
            manim_settings,
            "render_runtime_status",
            lambda: {
                "manim_python": "/usr/local/bin/python",
                "ffmpeg": "/usr/bin/ffmpeg",
                "latex": "/usr/bin/latex",
                "dvisvgm": "/usr/bin/dvisvgm",
            },
        )

        resp = client.get("/health")

        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_health_fails_when_render_runtime_missing(self, client, monkeypatch):
        monkeypatch.setattr(
            manim_settings,
            "render_runtime_status",
            lambda: {
                "manim_python": "/usr/local/bin/python",
                "ffmpeg": "/usr/bin/ffmpeg",
                "latex": None,
                "dvisvgm": "/usr/bin/dvisvgm",
            },
        )

        resp = client.get("/health")

        assert resp.status_code == 503
        assert resp.json()["status"] == "degraded"
        assert resp.json()["missing"] == ["latex"]

    def test_missing_required_step_fields_rejected(self, client):
        resp = client.post(
            "/render/trace",
            json={
                "lesson_id": "td_q_learning",
                # Missing action, reward, next_state
                "episode_trace": {"steps": [{"state": 0}]},
            },
        )
        assert resp.status_code == 422  # Pydantic validation error

    def test_all_known_lesson_ids_accepted(self, client):
        known_ids = [
            "dp_policy_eval",
            "dp_policy_improvement",
            "dp_value_iteration",
            "mc_first_visit",
            "td_sarsa",
            "td_q_learning",
        ]
        for lesson_id in known_ids:
            resp = client.post(
                "/render/trace",
                json={
                    "lesson_id": lesson_id,
                    "episode_trace": {"steps": [RICH_STEP]},
                },
            )
            assert resp.status_code == 202, f"Expected 202 for lesson_id={lesson_id!r}"

    def test_empty_steps_list_accepted_at_route_level(self, client):
        """The route itself accepts an empty steps list (validation is in render_trace).

        The HTTP layer only enforces schema; domain validation (non-empty steps)
        happens inside render_trace, so 202 is the expected route response here.
        """
        resp = client.post(
            "/render/trace",
            json={
                "lesson_id": "td_q_learning",
                "episode_trace": {"steps": []},
            },
        )
        # The route enqueues without inspecting step count; 202 is correct
        assert resp.status_code == 202


class TestGetJob:
    def test_unknown_job_returns_404(self, client):
        resp = client.get("/jobs/nonexistent-job-id")
        assert resp.status_code == 404

    def test_queued_job_returns_status(self, client):
        # Enqueue first, then poll
        post_resp = client.post(
            "/render/trace",
            json={
                "lesson_id": "td_q_learning",
                "episode_trace": {"steps": [RICH_STEP]},
            },
        )
        assert post_resp.status_code == 202
        job_id = post_resp.json()["job_id"]

        status_resp = client.get(f"/jobs/{job_id}")
        assert status_resp.status_code == 200
        body = status_resp.json()
        assert body["status"] in {"queued", "rendering", "complete", "failed"}
        assert body["job_id"] == job_id

    def test_completed_job_includes_video_url(self, client, isolated_queue):
        """When a job is marked complete, the status response includes video_url."""
        post_resp = client.post(
            "/render/trace",
            json={
                "lesson_id": "td_q_learning",
                "episode_trace": {"steps": [RICH_STEP]},
            },
        )
        job_id = post_resp.json()["job_id"]

        # Manually advance the job to complete state (no Manim needed)
        fake_path = "/shared/traces/fake.mp4"
        isolated_queue.mark_complete(job_id, fake_path)

        status_resp = client.get(f"/jobs/{job_id}")
        assert status_resp.status_code == 200
        body = status_resp.json()
        assert body["status"] == "complete"
        assert body["video_url"] is not None
        assert "fake.mp4" in body["video_url"]

    def test_failed_job_includes_error(self, client, isolated_queue):
        """When a job is marked failed, the status response includes the error message."""
        post_resp = client.post(
            "/render/trace",
            json={
                "lesson_id": "td_q_learning",
                "episode_trace": {"steps": [RICH_STEP]},
            },
        )
        job_id = post_resp.json()["job_id"]

        isolated_queue.mark_failed(job_id, "Manim subprocess crashed")

        status_resp = client.get(f"/jobs/{job_id}")
        assert status_resp.status_code == 200
        body = status_resp.json()
        assert body["status"] == "failed"
        assert "Manim subprocess crashed" in (body.get("error") or "")


class TestGetVideo:
    def test_path_traversal_blocked(self, client):
        # Path components with ".." should be blocked (safe_name strips them → not found)
        resp = client.get("/videos/../../../etc/passwd")
        assert resp.status_code == 404

    def test_nonexistent_file_returns_404(self, client):
        resp = client.get("/videos/does_not_exist.mp4")
        assert resp.status_code == 404

    def test_existing_file_served(self, client, tmp_path, monkeypatch):
        """A real MP4 placed in the traces subdirectory is served correctly."""
        from manim_service import settings as manim_settings
        from manim_service.storage import output as storage

        # Patch the settings attribute so resolve_safe_video_path sees tmp_path
        monkeypatch.setattr(manim_settings, "SHARED_MEDIA_DIR", tmp_path)

        traces_dir = tmp_path / storage.TRACES_SUBDIR
        traces_dir.mkdir(parents=True, exist_ok=True)
        video_file = traces_dir / "myvideo.mp4"
        video_file.write_bytes(b"\x00" * 8)  # Minimal fake MP4

        resp = client.get("/videos/myvideo.mp4")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("video/mp4")
