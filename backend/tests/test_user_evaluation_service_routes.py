from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

from fastapi.testclient import TestClient

from backend.user_evaluation_service.base import ServiceContainer, create_app


@dataclass
class _FakeUserEvaluationService:
    sign_in_error: str | None = None

    def sign_in(
        self,
        display_name: str,
        password: str,
        firebase_id_token: str | None = None,
    ) -> dict[str, Any]:
        del password, firebase_id_token
        if self.sign_in_error:
            raise ValueError(self.sign_in_error)
        return {
            "student": {
                "id": "student-1",
                "display_name": display_name or "Maya",
            },
            "progress": {
                "completed_lesson_ids": [],
                "successful_runs": 0,
                "latest_lesson_id": None,
                "pretest_score": None,
                "posttest_score": None,
                "n_gain": None,
                "quiz_attempts": {"pretest": 0, "posttest": 0},
            },
        }

    def get_dashboard(self, student_id: str) -> dict[str, Any] | None:
        if student_id == "missing":
            return None
        return {
            "student": {"id": student_id, "display_name": "Maya"},
            "progress": {
                "completed_lesson_ids": ["dp_policy_eval"],
                "successful_runs": 1,
                "latest_lesson_id": "dp_policy_eval",
                "pretest_score": 50.0,
                "posttest_score": None,
                "n_gain": None,
                "quiz_attempts": {"pretest": 1, "posttest": 0},
            },
        }

    def ensure_student_record(self, *, student_id: str, display_name: str) -> dict[str, Any]:
        return {
            "student": {"id": student_id, "display_name": display_name},
            "progress": {
                "completed_lesson_ids": [],
                "successful_runs": 0,
                "latest_lesson_id": None,
                "pretest_score": None,
                "posttest_score": None,
                "n_gain": None,
                "quiz_attempts": {"pretest": 0, "posttest": 0},
            },
        }

    def start_quiz(self, student_id: str, phase: str) -> dict[str, Any]:
        if student_id == "missing":
            raise ValueError("Unknown student_id.")
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

    def quiz_catalog(self) -> dict[str, Any]:
        return {
            "assessment_phases": [],
            "category_quizzes": [],
            "quiz_families": [{"id": "dp_policy_eval"}],
        }

    def submit_quiz(
        self,
        student_id: str,
        session_id: str,
        answers: list[dict[str, int]],
    ) -> dict[str, Any]:
        del session_id, answers
        if student_id == "missing":
            raise ValueError("Unknown student_id.")
        return {
            "phase": "pretest",
            "score": 1,
            "total_questions": 1,
            "percentage": 100.0,
            "n_gain": None,
            "progress": self.get_dashboard(student_id)["progress"],
        }

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


def _make_client(service: _FakeUserEvaluationService | None = None) -> TestClient:
    previous_token = os.environ.get("RL_IDE_INTERNAL_TOKEN")
    os.environ["RL_IDE_INTERNAL_TOKEN"] = "test-internal-token"
    try:
        app = create_app(
            services=ServiceContainer(
                user_evaluation=service or _FakeUserEvaluationService(),
            )
        )
    finally:
        if previous_token is None:
            os.environ.pop("RL_IDE_INTERNAL_TOKEN", None)
        else:
            os.environ["RL_IDE_INTERNAL_TOKEN"] = previous_token
    return TestClient(app)


def _internal_headers() -> dict[str, str]:
    return {"X-Internal-Token": "test-internal-token"}


def test_internal_sign_in_returns_dashboard_payload():
    client = _make_client()
    response = client.post(
        "/internal/auth/sign-in",
        json={
            "display_name": "Maya",
            "password": "SecurePass123!",
            "firebase_id_token": "firebase-token",
        },
        headers=_internal_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["student"]["display_name"] == "Maya"


def test_internal_sign_in_maps_validation_error_to_400():
    client = _make_client(_FakeUserEvaluationService(sign_in_error="Invalid Firebase token."))
    response = client.post(
        "/internal/auth/sign-in",
        json={
            "display_name": "Maya",
            "password": "SecurePass123!",
            "firebase_id_token": "bad-token",
        },
        headers=_internal_headers(),
    )

    assert response.status_code == 400


def test_internal_dashboard_returns_404_for_missing_student():
    client = _make_client()
    response = client.get(
        "/internal/students/missing/dashboard",
        headers=_internal_headers(),
    )

    assert response.status_code == 404


def test_internal_student_ensure_returns_seeded_dashboard():
    client = _make_client()
    response = client.post(
        "/internal/students/ensure",
        json={"student_id": "new-student", "display_name": "New Student"},
        headers=_internal_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["student"]["id"] == "new-student"
    assert payload["student"]["display_name"] == "New Student"


def test_internal_quiz_start_omits_answer_key():
    client = _make_client()
    response = client.post(
        "/internal/quiz/start",
        json={"student_id": "student-1", "phase": "pretest"},
        headers=_internal_headers(),
    )

    assert response.status_code == 200
    question = response.json()["questions"][0]
    assert "correct_index" not in question


def test_internal_quiz_catalog_requires_internal_token():
    client = _make_client()

    response = client.get("/internal/quiz/catalog")

    assert response.status_code == 401


def test_internal_quiz_catalog_returns_catalog():
    client = _make_client()

    response = client.get(
        "/internal/quiz/catalog",
        headers=_internal_headers(),
    )

    assert response.status_code == 200
    assert response.json()["quiz_families"] == [{"id": "dp_policy_eval"}]


def test_internal_quiz_submit_returns_score_payload():
    client = _make_client()
    response = client.post(
        "/internal/quiz/submit",
        json={
            "student_id": "student-1",
            "session_id": "session-1",
            "answers": [{"question_id": "q1", "selected_index": 0}],
        },
        headers=_internal_headers(),
    )

    assert response.status_code == 200
    assert response.json()["percentage"] == 100.0


def test_internal_n_gain_metrics_returns_export_rows():
    client = _make_client()
    response = client.get(
        "/internal/metrics/n-gain",
        headers=_internal_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["rows"][0]["student_id"] == "student-1"
