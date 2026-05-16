from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fastapi.testclient import TestClient
from sqlmodel import select

from backend.api_gateway.base import ServiceContainer, create_app
from backend.auth.roles import AccountStatus, PlatformRole, Principal
from backend.models.study_buddy_intervention_record import StudyBuddyInterventionRecord
from backend.persistence import Database
from backend.services.learning_analytics_export_service import LearningAnalyticsExportService
from backend.services.metrics_export_service import MetricsExportService
from backend.services.pedagogical_context_assembler import PedagogicalPromptContext
from backend.services.pedagogical_llm_service import (
    PedagogicalChatContext,
    PedagogicalChatReply,
    PedagogicalIntervention,
)
from backend.services.student_progress_service import StudentProgressService
from backend.services.study_buddy_service import StudyBuddyService
from backend.services.telemetry_service import TelemetryService
from backend.services.user_evaluation_service import UserEvaluationService


class _FakeAuthService:
    def __init__(self, student_id: str = "student-1") -> None:
        self._token_map = {
            "student-token": Principal(
                id=student_id,
                role=PlatformRole.STUDENT,
                status=AccountStatus.ACTIVE,
            ),
            "admin-token": Principal(
                id="admin-1",
                role=PlatformRole.ADMIN,
                status=AccountStatus.ACTIVE,
            ),
        }

    def authenticate_token(self, token: str) -> Principal:
        principal = self._token_map.get(token)
        if principal is None:
            raise ValueError("Invalid token")
        return principal


def _auth_headers(token: str = "student-token") -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _event(
    event_type: str,
    payload: dict[str, Any],
    *,
    session_id: str = "study-session-1",
) -> dict[str, Any]:
    return {
        "student_id": "student-1",
        "lesson_id": "dp_policy_eval",
        "concept_id": "dp_policy_eval",
        "session_id": session_id,
        "event_type": event_type,
        "occurred_at_utc": datetime.now(timezone.utc),
        "payload_json": payload,
        "source_version": "study_buddy_v1_test",
    }


@dataclass
class _FakeLLMService:
    prompt_version: str = "test_prompt_v1"

    def generate(
        self,
        context: PedagogicalPromptContext,
    ) -> tuple[PedagogicalIntervention, dict]:
        return self.fallback_intervention(context), {
            "model": "fake-model",
            "prompt_version": self.prompt_version,
            "latency_ms": 1,
            "used_fallback": False,
        }

    def fallback_intervention(
        self,
        context: PedagogicalPromptContext,
    ) -> PedagogicalIntervention:
        return PedagogicalIntervention(
            intervention_type=context.intervention_type,
            title="Study Buddy test prompt",
            message="Focus on one concept checkpoint.",
            diagnostic_question="What feels unclear?",
            choices=["Concept", "Checkpoint", "Try again"],
            checkpoint="Name the update target.",
            next_step="Run one small check.",
            concept_ids=[context.concept_id or context.lesson_id],
            solution_leakage_risk="low",
        )

    def generate_chat(
        self,
        context: PedagogicalChatContext,
    ) -> tuple[PedagogicalChatReply, dict]:
        return PedagogicalChatReply(
            reply=(
                f"For {context.lesson_title}, start by naming the Bellman update "
                "target before editing code."
            ),
            suggested_next_step="Run one small check.",
            concept_ids=[context.lesson_id],
            solution_leakage_risk="low",
        ), {
            "model": "fake-chat-model",
            "prompt_version": "test_chat_prompt_v1",
            "latency_ms": 1,
            "used_fallback": False,
        }


def _service() -> StudyBuddyService:
    database = Database("sqlite://")
    telemetry = TelemetryService(database=database)
    return StudyBuddyService(
        telemetry_service=telemetry,
        database=database,
        llm_service=_FakeLLMService(),
    )


def test_submission_failure_streak_creates_pending_intervention():
    service = _service()

    service.ingest_events(
        [
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
        ]
    )

    pending = service.pending_intervention("study-session-1")
    assert pending is not None
    assert pending["trigger_type"] == "submission_failure_streak"
    assert pending["intervention_type"] == "mini_example"
    assert pending["response"]["title"] == "Study Buddy test prompt"


def test_coordinator_suppresses_duplicate_ready_trigger_in_cooldown():
    service = _service()

    service.ingest_events(
        [
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
        ]
    )

    with service._database.session() as session:
        interventions = session.exec(select(StudyBuddyInterventionRecord)).all()
    assert len(interventions) == 1


def test_respond_to_intervention_marks_record_completed():
    service = _service()
    service.ingest_events(
        [
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
        ]
    )
    pending = service.pending_intervention("study-session-1")

    updated = service.respond_to_intervention(
        pending["id"],
        response="completed",
    )

    assert updated is not None
    assert updated["status"] == "completed"
    assert updated["resolved_at_utc"] is not None
    assert service.pending_intervention("study-session-1") is None


def test_summary_and_timeline_include_mastery_evidence():
    service = _service()
    service.ingest_events(
        [
            _event("code_run_result", {"passed": True}),
            _event("concept_video_session", {"replay_count": 3, "seek_back_count": 5}),
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
        ]
    )

    summary = service.summary("student-1")
    snapshots = summary["mastery_snapshots"]
    assert snapshots
    assert snapshots[0]["concept_id"] == "dp_policy_eval"
    assert snapshots[0]["evidence_summary"]["direct_evidence_count"] >= 3
    assert snapshots[0]["confidence_score"] > 0.10
    assert summary["recent_interventions"]

    timeline = service.learning_timeline("student-1")
    item_types = {item["item_type"] for item in timeline["items"]}
    assert {"event", "intervention", "mastery_snapshot"}.issubset(item_types)


def test_chat_returns_grounded_reply_and_records_telemetry():
    service = _service()
    service.ingest_events(
        [
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
            _event("submission_result", {"passed": False, "failure_kind": "test_failure"}),
        ]
    )

    response = service.chat(
        student_id="student-1",
        lesson_id="dp_policy_eval",
        session_id="study-session-1",
        message="Why is my Bellman expectation still failing?",
        history=[{"role": "assistant", "content": "Start with the update target."}],
        current_code="raise NotImplementedError('TODO')",
        unresolved_blanks=["policy_eval_expectation"],
        failure_kind="test_failure",
        latest_feedback={"summary": "Expected every transition branch."},
    )

    assert response["message"]["role"] == "assistant"
    assert "Bellman update target" in response["reply"]
    assert response["used_fallback"] is False
    assert response["observability"]["prompt_version"] == "test_chat_prompt_v1"

    events = service.telemetry_service.list_events(session_id="study-session-1")
    chat_event_types = [event.event_type for event in events]
    assert "study_buddy_chat_message" in chat_event_types
    assert "study_buddy_chat_reply" in chat_event_types


def test_study_buddy_routes_poll_and_respond():
    service = _service()
    auth = _FakeAuthService()
    app = create_app(
        services=ServiceContainer(
            lesson_catalog=None,
            user_evaluation=None,
            auth=auth,
            execution=None,
            workspace=None,
            metrics_export=MetricsExportService(),
            learning_analytics_export=LearningAnalyticsExportService(
                database=service._database,
            ),
            telemetry=service.telemetry_service,
            study_buddy=service,
        )
    )
    client = TestClient(app)

    client.post(
        "/telemetry/events",
        json={
            "events": [
                {
                    **_event(
                        "submission_result",
                        {"passed": False, "failure_kind": "test_failure"},
                    ),
                    "occurred_at_utc": "2026-05-13T10:00:00Z",
                },
                {
                    **_event(
                        "submission_result",
                        {"passed": False, "failure_kind": "test_failure"},
                    ),
                    "occurred_at_utc": "2026-05-13T10:01:00Z",
                },
            ]
        },
        headers=_auth_headers(),
    )

    pending_response = client.get(
        "/study-buddy/interventions/study-session-1/pending",
        headers=_auth_headers(),
    )
    pending = pending_response.json()["intervention"]
    assert pending["trigger_type"] == "submission_failure_streak"

    respond_response = client.post(
        f"/study-buddy/interventions/{pending['id']}/respond",
        json={"response": "dismissed"},
        headers=_auth_headers(),
    )
    assert respond_response.status_code == 200
    assert respond_response.json()["intervention"]["status"] == "dismissed"

    summary_response = client.get("/me/study-buddy/summary", headers=_auth_headers())
    assert summary_response.status_code == 200
    assert summary_response.json()["mastery_snapshots"]

    chat_response = client.post(
        "/me/study-buddy/chat",
        json={
            "lesson_id": "dp_policy_eval",
            "session_id": "study-session-1",
            "message": "What should I inspect next?",
            "current_code": "raise NotImplementedError('TODO')",
            "unresolved_blanks": ["policy_eval_expectation"],
            "failure_kind": "test_failure",
            "latest_feedback": {"summary": "Expected every transition branch."},
            "history": [
                {
                    "role": "assistant",
                    "content": "Start with the update target.",
                }
            ],
        },
        headers=_auth_headers(),
    )
    assert chat_response.status_code == 200
    assert chat_response.json()["message"]["role"] == "assistant"
    assert chat_response.json()["observability"]["model"] == "fake-chat-model"

    timeline_response = client.get("/me/learning-timeline", headers=_auth_headers())
    assert timeline_response.status_code == 200
    assert timeline_response.json()["items"]

    export_response = client.get(
        "/admin/metrics/learning-analytics/export",
        headers=_auth_headers("admin-token"),
    )
    assert export_response.status_code == 200
    assert export_response.content


def test_quiz_submit_route_records_mastery_evidence():
    database = Database("sqlite://")
    telemetry = TelemetryService(database=database)
    service = StudyBuddyService(
        telemetry_service=telemetry,
        database=database,
        llm_service=_FakeLLMService(),
    )
    progress = StudentProgressService(database=database)
    user_evaluation = UserEvaluationService(progress_service=progress)
    dashboard = user_evaluation.sign_in("Maya", "Password123!")
    auth = _FakeAuthService(student_id=dashboard["student"]["id"])
    app = create_app(
        services=ServiceContainer(
            lesson_catalog=None,
            user_evaluation=user_evaluation,
            auth=auth,
            execution=None,
            workspace=None,
            metrics_export=MetricsExportService(),
            learning_analytics_export=LearningAnalyticsExportService(
                database=database,
            ),
            telemetry=telemetry,
            study_buddy=service,
        )
    )
    client = TestClient(app)

    start = client.post(
        "/quiz/start",
        json={"phase": "pretest"},
        headers=_auth_headers(),
    )
    assert start.status_code == 200
    quiz = start.json()
    session_state = user_evaluation._quiz_service._sessions[quiz["session_id"]]
    answers = [
        {
            "question_id": question["id"],
            "selected_index": session_state.correct_indices[question["id"]],
        }
        for question in quiz["questions"]
    ]

    submit = client.post(
        "/quiz/submit",
        json={
            "session_id": quiz["session_id"],
            "answers": answers,
        },
        headers=_auth_headers(),
    )

    assert submit.status_code == 200
    summary = service.summary(dashboard["student"]["id"])
    assert summary["mastery_snapshots"]
    assert any(
        snapshot["evidence_summary"]["direct_evidence_count"] >= 1
        for snapshot in summary["mastery_snapshots"]
    )
