from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.api_gateway.base import ServiceContainer, create_app
from backend.auth.roles import AccountStatus, PlatformRole, Principal
from backend.persistence import Database
from backend.services.alei_export_service import ALEIExportService
from backend.services.authored_lesson_service import AuthoredLessonService
from backend.services.evaluation_session_service import EvaluationSessionService
from backend.services.lesson_registry_service import LessonRegistryService
from backend.services.prediction_probe_service import PredictionProbeService
from backend.services.study_session_survey_service import StudySessionSurveyService


# ── Fake auth ────────────────────────────────────────────────────────────────

class _FakeAuthService:
    def authenticate_token(self, token: str) -> Principal:
        if token == "student-token":
            return Principal(
                id="student-1",
                role=PlatformRole.STUDENT,
                status=AccountStatus.ACTIVE,
            )
        if token == "admin-token":
            return Principal(
                id="admin-1",
                role=PlatformRole.ADMIN,
                status=AccountStatus.ACTIVE,
            )
        raise ValueError("Invalid token")


def _student_headers() -> dict[str, str]:
    return {"Authorization": "Bearer student-token"}


def _admin_headers() -> dict[str, str]:
    return {"Authorization": "Bearer admin-token"}


# ── Shared fixture ────────────────────────────────────────────────────────────

@pytest.fixture()
def client(tmp_path):
    db = Database(f"sqlite:///{tmp_path}/test.db")
    db.create_schema()
    registry = LessonRegistryService(database=db)

    import backend.lesson_registry as _lr
    _lr.set_registry(registry)

    svc = ServiceContainer(
        lesson_catalog=None,
        user_evaluation=None,
        auth=_FakeAuthService(),
        execution=None,
        workspace=None,
        metrics_export=None,
        evaluation_session=EvaluationSessionService(database=db),
        prediction_probe=PredictionProbeService(database=db),
        study_session_survey=StudySessionSurveyService(database=db),
        alei_export=ALEIExportService(database=db),
        authored_lessons=AuthoredLessonService(database=db),
        lesson_registry=registry,
    )
    app = create_app(services=svc)
    yield TestClient(app)
    _lr.set_registry(None)  # type: ignore[arg-type]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _valid_survey_payload(study_session_id: str, condition: str = "adaptive") -> dict:
    return {
        "study_session_id": study_session_id,
        "condition": condition,
        "sus_q1": 4,
        "sus_q2": 2,
        "sus_q3": 4,
        "sus_q4": 2,
        "sus_q5": 4,
        "sus_q6": 2,
        "sus_q7": 4,
        "sus_q8": 2,
        "sus_q9": 4,
        "sus_q10": 2,
        "tlx_mental_demand": 30,
        "tlx_physical_demand": 10,
        "tlx_temporal_demand": 20,
        "tlx_performance": 50,
        "tlx_effort": 40,
        "tlx_frustration": 20,
    }


# ── Tests: POST /evaluation/session/start ─────────────────────────────────────

def test_start_session_returns_201_with_id(client):
    response = client.post(
        "/evaluation/session/start",
        json={"condition": "adaptive", "lesson_ids": ["rl_intro"]},
        headers=_student_headers(),
    )
    assert response.status_code == 201
    body = response.json()
    assert "study_session_id" in body
    assert isinstance(body["study_session_id"], str)
    assert len(body["study_session_id"]) > 0


def test_start_session_invalid_condition_returns_422(client):
    response = client.post(
        "/evaluation/session/start",
        json={"condition": "bogus", "lesson_ids": ["rl_intro"]},
        headers=_student_headers(),
    )
    assert response.status_code == 422


# ── Tests: POST /evaluation/probe/submit ─────────────────────────────────────

def test_submit_probe_returns_200_with_correct_fields(client):
    # Create a session first
    sess_resp = client.post(
        "/evaluation/session/start",
        json={"condition": "control", "lesson_ids": ["mdp_foundations"]},
        headers=_student_headers(),
    )
    assert sess_resp.status_code == 201
    session_id = sess_resp.json()["study_session_id"]

    response = client.post(
        "/evaluation/probe/submit",
        json={
            "study_session_id": session_id,
            "lesson_id": "mdp_foundations",
            "concept_id": "bellman",
            "probe_id": "probe-1",
            "actual_value": 1.0,
            "predicted_value": 0.8,
            "tolerance": 0.5,
        },
        headers=_student_headers(),
    )
    assert response.status_code == 200
    body = response.json()
    assert "absolute_error" in body
    assert "is_within_tolerance" in body
    assert "attempt_index" in body
    assert abs(body["absolute_error"] - 0.2) < 1e-9
    assert body["is_within_tolerance"] is True
    assert body["attempt_index"] == 1


# ── Tests: POST /evaluation/survey/submit ─────────────────────────────────────

def test_submit_survey_returns_201_with_scores(client):
    # Create a session first
    sess_resp = client.post(
        "/evaluation/session/start",
        json={"condition": "adaptive", "lesson_ids": ["rl_intro"]},
        headers=_student_headers(),
    )
    session_id = sess_resp.json()["study_session_id"]

    response = client.post(
        "/evaluation/survey/submit",
        json=_valid_survey_payload(session_id),
        headers=_student_headers(),
    )
    assert response.status_code == 201
    body = response.json()
    assert "sus_score" in body
    assert "tlx_overall" in body
    assert isinstance(body["sus_score"], float)
    assert isinstance(body["tlx_overall"], float)


def test_submit_survey_out_of_range_sus_returns_422(client):
    sess_resp = client.post(
        "/evaluation/session/start",
        json={"condition": "adaptive", "lesson_ids": ["rl_intro"]},
        headers=_student_headers(),
    )
    session_id = sess_resp.json()["study_session_id"]

    payload = _valid_survey_payload(session_id)
    payload["sus_q1"] = 0  # out of range (must be 1-5)

    response = client.post(
        "/evaluation/survey/submit",
        json=payload,
        headers=_student_headers(),
    )
    assert response.status_code == 422


# ── Tests: GET /evaluation/export/alei-components ─────────────────────────────

def test_export_alei_returns_403_for_student(client):
    response = client.get(
        "/evaluation/export/alei-components",
        headers=_student_headers(),
    )
    assert response.status_code == 403


def test_export_alei_returns_xlsx_for_admin(client):
    response = client.get(
        "/evaluation/export/alei-components",
        headers=_admin_headers(),
    )
    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "content-disposition" in response.headers
    assert response.headers["content-disposition"].startswith('attachment; filename="alei_components_')
    # Verify it's a valid xlsx (PK zip magic bytes)
    assert response.content[:2] == b"PK"


def test_admin_can_persist_and_delete_authored_lesson(client):
    lesson = {
        "id": "draft_cloud_lesson",
        "title": "Cloud Draft",
        "category": "Studio Drafts",
        "description": "A deployable authored lesson.",
        "starter_code": "def lesson_function():\n    return None\n",
        "backend_enabled": False,
        "concept_video": {
            "stream_path": "/media/concept-videos/draft.mp4",
            "duration_label": "00:45",
            "summary": "Draft video.",
            "highlights": ["One key idea"],
        },
        "exercise": {
            "title": "Draft exercise",
            "overview": "Complete the draft.",
            "tasks": ["Write the update."],
            "success_criteria": ["The goal is clear."],
            "code_tip": "Edit constants in code.",
        },
    }

    save_response = client.put(
        "/admin/lessons/draft_cloud_lesson",
        json={"lesson": lesson},
        headers=_admin_headers(),
    )
    assert save_response.status_code == 200
    assert save_response.json()["lesson"]["title"] == "Cloud Draft"

    list_response = client.get(
        "/admin/lessons",
        headers=_admin_headers(),
    )
    assert list_response.status_code == 200
    lesson_ids = [l["id"] for l in list_response.json()["lessons"]]
    assert "draft_cloud_lesson" in lesson_ids

    delete_response = client.delete(
        "/admin/lessons/draft_cloud_lesson",
        headers=_admin_headers(),
    )
    assert delete_response.status_code == 204

    list_after = client.get("/admin/lessons", headers=_admin_headers())
    lesson_ids_after = [l["id"] for l in list_after.json()["lessons"]]
    assert "draft_cloud_lesson" not in lesson_ids_after
