from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

from fastapi.testclient import TestClient

from backend.api_gateway.base import ServiceContainer, create_app
from backend.execution_runtime import ExecutionPipelineError


@dataclass
class _FakeLessonCatalogService:
    def list_lesson_sections(self) -> list[dict[str, Any]]:
        lesson = {
            "id": "dp_policy_eval",
            "title": "Policy Evaluation",
            "category": "Dynamic Programming",
            "description": "Evaluate a fixed policy.",
            "starter_code": "def policy_evaluation(): pass",
            "backend_enabled": True,
            "concept_video": {
                "stream_path": "/media/concept-videos/dp_policy_eval_concept.mp4",
                "duration_label": "03:30",
                "summary": "Bellman expectation backup walkthrough.",
                "highlights": ["Policy weighting"],
            },
            "exercise": {
                "title": "Implement iterative policy evaluation",
                "overview": "Complete the Bellman update.",
                "tasks": ["Fill the backup loop."],
                "template_blanks": [],
                "success_criteria": ["The function returns values."],
                "code_tip": "Tune DISCOUNT_FACTOR in code.",
            },
        }
        return [{"title": "Dynamic Programming", "lessons": [lesson]}]


class _FakeUserEvaluationService:
    def __init__(self) -> None:
        self._dashboards = {
            "student-1": {
                "student": {"id": "student-1", "display_name": "Maya"},
                "progress": {
                    "completed_lesson_ids": [],
                    "successful_runs": 0,
                    "latest_lesson_id": None,
                    "pretest_score": None,
                    "posttest_score": None,
                    "n_gain": None,
                    "quiz_attempts": {"pretest": 0, "posttest": 0},
                },
            },
        }

    def sign_in(self, display_name: str, password: str, firebase_id_token: str | None = None):
        del firebase_id_token
        if password == "bad":
            raise ValueError("Invalid display name or password.")
        return self._dashboards["student-1"]

    def get_dashboard(self, student_id: str):
        return self._dashboards.get(student_id)

    def list_n_gain_metrics(self) -> list[dict[str, Any]]:
        return [
            {
                "student_id": "student-1",
                "display_name": "Maya",
                "pretest_score": 50.0,
                "posttest_score": 80.0,
                "n_gain": 0.6,
                "successful_runs": 2,
                "lessons_completed": 1,
                "quiz_attempts_pretest": 1,
                "quiz_attempts_posttest": 1,
                "last_updated_utc": "2026-01-01T00:00:00+00:00",
            }
        ]

    def start_quiz(self, student_id: str, phase: str):
        if self.get_dashboard(student_id) is None:
            raise ValueError("Unknown student_id.")
        if phase not in {"pretest", "posttest"}:
            raise ValueError(f"Unsupported quiz phase '{phase}'.")
        return {
            "session_id": "session-1",
            "phase": phase,
            "question_count": 1,
            "questions": [
                {
                    "id": "q1",
                    "concept": "Core RL",
                    "prompt": "What does gamma control?",
                    "options": ["Future rewards", "Nothing"],
                }
            ],
        }

    def submit_quiz(self, student_id: str, session_id: str, answers: list[dict[str, int]]):
        del session_id, answers
        if self.get_dashboard(student_id) is None:
            raise ValueError("Unknown student_id.")
        return {
            "phase": "pretest",
            "score": 1,
            "total_questions": 1,
            "percentage": 100.0,
            "n_gain": None,
            "progress": self.get_dashboard(student_id)["progress"],
        }


class _FakeExecutionService:
    def submit(self, submission_payload: dict[str, Any]) -> dict[str, str]:
        del submission_payload
        return {"task_id": "task-1", "status": "queued"}

    def snapshot(self, task_id: str) -> dict[str, Any] | None:
        if task_id != "task-1":
            return None
        return {
            "task_id": "task-1",
            "status": "succeeded",
            "result": {
                "status": "success",
                "message": "Execution pipeline completed.",
                "lesson": {"id": "dp_policy_eval", "title": "Policy Evaluation"},
                "video_path": "/tmp/demo.mp4",
                "visualization_ready": True,
                "test_results": [],
                "step_trace": [],
                "metrics": {
                    "episodes_completed": 2,
                    "steps_recorded": 8,
                    "total_reward": 1.0,
                    "average_reward": 0.5,
                    "best_episode_reward": 1.0,
                },
            },
        }

    def execute_sync(self, submission_payload: dict[str, Any]) -> dict[str, Any]:
        if submission_payload.get("lesson_id") == "bad-lesson":
            raise ExecutionPipelineError(
                status_code=404,
                detail="Unknown lesson 'bad-lesson'.",
            )
        if submission_payload.get("lesson_id") == "invalid-code":
            raise ExecutionPipelineError(
                status_code=400,
                detail={
                    "message": "Code validation failed.",
                    "issues": ["q_learning_update not found"],
                    "failure_kind": "validation_error",
                    "student_feedback": {
                        "status": "validation_error",
                        "summary": "The required function body is incomplete.",
                        "likely_issue": "The update rule is still missing.",
                        "affected_blank_ids": [],
                        "next_steps": ["Keep the required function signature."],
                        "hint_level": "light",
                    },
                },
            )
        return {
            "status": "success",
            "message": "Execution pipeline completed.",
            "lesson": {"id": "dp_policy_eval", "title": "Policy Evaluation"},
            "video_path": "/tmp/demo.mp4",
            "visualization_ready": True,
            "test_results": [],
            "step_trace": [],
            "metrics": {
                "episodes_completed": 2,
                "steps_recorded": 8,
                "total_reward": 1.0,
                "average_reward": 0.5,
                "best_episode_reward": 1.0,
            },
        }


class _FakeMetricsExportService:
    def build_n_gain_export(self, rows: list[dict[str, Any]]):
        del rows
        return "n_gain.xlsx", b"fake-xlsx-content"


class _FakeWorkspaceService:
    def __init__(self) -> None:
        self.content = "print('hello from workspace')\n"
        self.version = 1

    def create_session(self, lesson_id: str):
        return {
            "session_id": "workspace-1",
            "lesson_id": lesson_id,
            "visible_files": ["script.py"],
            "console_ready": True,
        }

    def health(self):
        return {
            "ready": True,
            "runtime_mode": "docker",
            "docker_cli_available": True,
            "docker_daemon_reachable": True,
            "message": "Workspace runtime is ready.",
            "issues": [],
        }

    def get_session(self, session_id: str):
        return {
            "session_id": session_id,
            "lesson_id": "dp_policy_eval",
            "visible_files": ["script.py"],
            "console_ready": True,
        }

    def get_file(self, session_id: str, path: str):
        del session_id
        return {
            "path": path,
            "content": self.content,
            "version": self.version,
            "diagnostics": [],
        }

    def update_file(self, session_id: str, path: str, content: str):
        del session_id, path
        self.content = content
        self.version += 1
        return {
            "path": "script.py",
            "content": self.content,
            "version": self.version,
            "diagnostics": [],
        }

    def run_script(self, session_id: str):
        del session_id
        return {
            "run_id": "run-1",
            "status": "running",
            "exit_code": None,
            "started_at": "2026-01-01T00:00:00+00:00",
            "finished_at": None,
        }

    def get_run(self, session_id: str, run_id: str):
        del session_id
        return {
            "run_id": run_id,
            "status": "completed",
            "exit_code": 0,
            "started_at": "2026-01-01T00:00:00+00:00",
            "finished_at": "2026-01-01T00:00:02+00:00",
        }


def _make_client() -> TestClient:
    user_evaluation = _FakeUserEvaluationService()
    services = ServiceContainer(
        lesson_catalog=_FakeLessonCatalogService(),
        user_evaluation=user_evaluation,
        execution=_FakeExecutionService(),
        workspace=_FakeWorkspaceService(),
        metrics_export=_FakeMetricsExportService(),
    )
    app = create_app(services=services)
    return TestClient(app)


def test_lessons_returns_grouped_frontend_catalog():
    client = _make_client()
    response = client.get("/lessons")

    assert response.status_code == 200
    body = response.json()
    lesson = body["sections"][0]["lessons"][0]
    assert body["sections"][0]["title"] == "Dynamic Programming"
    assert body["lessons"][0]["id"] == "dp_policy_eval"
    assert lesson["starter_code"]
    assert lesson["backend_enabled"] is True
    assert lesson["concept_video"]["stream_path"].endswith(".mp4")
    assert lesson["exercise"]["template_blanks"] == []
    assert lesson["exercise"]["success_criteria"]


def test_concept_video_serves_backend_media(tmp_path, monkeypatch):
    monkeypatch.setenv("RL_IDE_CONCEPT_VIDEO_DIR", str(tmp_path))
    video_path = tmp_path / "dp_policy_eval_concept.mp4"
    video_path.write_bytes(b"mp4-data")
    client = _make_client()

    response = client.get("/media/concept-videos/dp_policy_eval_concept.mp4")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("video/mp4")
    assert response.content == b"mp4-data"

    range_response = client.get(
        "/media/concept-videos/dp_policy_eval_concept.mp4",
        headers={"Range": "bytes=0-2"},
    )
    assert range_response.status_code == 206
    assert range_response.content == b"mp4"


def test_execute_success():
    client = _make_client()
    response = client.post(
        "/execute",
        json={
            "lesson_id": "dp_policy_eval",
            "code": "def policy_evaluation(*args):\n    return []\n",
            "episode_count": 5,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["visualization_ready"] is True


def test_execute_returns_pipeline_error_status():
    client = _make_client()
    response = client.post(
        "/execute",
        json={
            "lesson_id": "bad-lesson",
            "code": "def policy_evaluation(*args):\n    return []\n",
            "episode_count": 5,
        },
    )

    assert response.status_code == 404
    assert "Unknown lesson" in response.json()["detail"]


def test_execute_rejects_invalid_payload_with_422():
    client = _make_client()
    response = client.post(
        "/execute",
        json={
            "lesson_id": "dp_policy_eval",
            "code": "print('hi')",
            "episode_count": 9999,
        },
    )

    assert response.status_code == 422


def test_execute_returns_validation_400():
    client = _make_client()
    response = client.post(
        "/execute",
        json={
            "lesson_id": "invalid-code",
            "code": "def helper():\n    return 1\n",
            "episode_count": 5,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "Code validation failed."
    assert response.json()["detail"]["failure_kind"] == "validation_error"
    assert response.json()["detail"]["student_feedback"]["hint_level"] == "light"


def test_submit_and_task_snapshot_flow():
    client = _make_client()
    submit = client.post(
        "/submit",
        json={
            "lesson_id": "dp_policy_eval",
            "code": "def policy_evaluation(*args):\n    return []\n",
        },
    )
    assert submit.status_code == 200
    payload = submit.json()
    assert payload["task_id"] == "task-1"
    assert payload["status"] == "queued"

    snapshot = client.get("/tasks/task-1")
    assert snapshot.status_code == 200


def test_workspace_session_flow():
    client = _make_client()

    session = client.post("/workspace/sessions", json={"lesson_id": "dp_policy_eval"})
    assert session.status_code == 200
    assert session.json()["session_id"] == "workspace-1"

    script = client.get("/workspace/sessions/workspace-1/files/script.py")
    assert script.status_code == 200
    assert "hello from workspace" in script.json()["content"]

    updated = client.put(
        "/workspace/sessions/workspace-1/files/script.py",
        json={"content": "print('updated')\n"},
    )
    assert updated.status_code == 200
    assert updated.json()["version"] == 2

    run = client.post("/workspace/sessions/workspace-1/run")
    assert run.status_code == 200
    assert run.json()["status"] == "running"

    snapshot = client.get("/workspace/sessions/workspace-1/runs/run-1")
    assert snapshot.status_code == 200
    assert snapshot.json()["status"] == "completed"

    unknown = client.get("/tasks/unknown")
    assert unknown.status_code == 404


def test_workspace_health_reports_ready():
    client = _make_client()
    response = client.get("/workspace/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ready"] is True
    assert payload["worker_reachable"] is True


def test_visualization_frame_serves_png_under_output_root(tmp_path, monkeypatch):
    frame_dir = tmp_path / "captures"
    frame_dir.mkdir()
    frame_path = frame_dir / "frame.png"
    frame_path.write_bytes(b"png-data")
    monkeypatch.setenv("RL_IDE_VISUALIZATION_OUTPUT_DIR", str(tmp_path))

    client = _make_client()
    response = client.get(
        "/visualization/frame",
        params={"path": str(frame_path)},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == b"png-data"


def test_visualization_frame_rejects_paths_outside_output_root(tmp_path, monkeypatch):
    outside_path = tmp_path.parent / "outside.png"
    outside_path.write_bytes(b"png-data")
    monkeypatch.setenv("RL_IDE_VISUALIZATION_OUTPUT_DIR", str(tmp_path))

    client = _make_client()
    response = client.get(
        "/visualization/frame",
        params={"path": str(outside_path)},
    )

    assert response.status_code == 403
    os.remove(outside_path)


def test_visualization_video_serves_mp4_under_output_root(tmp_path, monkeypatch):
    video_dir = tmp_path / "videos"
    video_dir.mkdir()
    video_path = video_dir / "replay.mp4"
    video_path.write_bytes(b"mp4-data")
    monkeypatch.setenv("RL_IDE_VISUALIZATION_OUTPUT_DIR", str(tmp_path))

    client = _make_client()
    response = client.get(
        "/visualization/video",
        params={"path": str(video_path)},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "video/mp4"
    assert response.content == b"mp4-data"


def test_visualization_video_rejects_paths_outside_output_root(tmp_path, monkeypatch):
    outside_path = tmp_path.parent / "outside.mp4"
    outside_path.write_bytes(b"mp4-data")
    monkeypatch.setenv("RL_IDE_VISUALIZATION_OUTPUT_DIR", str(tmp_path))

    client = _make_client()
    response = client.get(
        "/visualization/video",
        params={"path": str(outside_path)},
    )

    assert response.status_code == 403
    os.remove(outside_path)


def test_sign_in_error_maps_to_http_400():
    client = _make_client()
    response = client.post(
        "/auth/sign-in",
        json={"display_name": "Maya", "password": "bad"},
    )
    assert response.status_code == 400


def test_quiz_start_requires_known_student():
    client = _make_client()
    response = client.post(
        "/quiz/start",
        json={"student_id": "missing", "phase": "pretest"},
    )
    assert response.status_code == 400
