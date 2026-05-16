from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.api_gateway.base import ServiceContainer, create_app
from backend.auth.roles import AccountStatus, PlatformRole, Principal
from backend.execution_runtime import ExecutionPipelineError
from backend.persistence import Database
from backend.services.execution_service import ExecutionService
from backend.services.telemetry_service import TelemetryService


class _FakeAuthService:
    def authenticate_token(self, token: str) -> Principal:
        if token != "student-token":
            raise ValueError("Invalid token")
        return Principal(
            id="student-1",
            role=PlatformRole.STUDENT,
            status=AccountStatus.ACTIVE,
        )


def _auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer student-token"}


def _event_payload(**overrides: Any) -> dict[str, Any]:
    payload = {
        "student_id": "student-1",
        "lesson_id": "dp_policy_eval",
        "concept_id": "bellman_expectation",
        "session_id": "study-session-1",
        "event_type": "concept_video_session",
        "occurred_at_utc": datetime.now(timezone.utc),
        "payload_json": {
            "watch_duration_seconds": 42,
            "completion_ratio": 0.8,
        },
        "source_version": "study_buddy_v1_test",
    }
    payload.update(overrides)
    return payload


def test_telemetry_service_validates_and_persists_events():
    service = TelemetryService(database=Database("sqlite://"))

    event_ids = service.record_events([_event_payload()])

    assert len(event_ids) == 1
    records = service.list_events(student_id="student-1")
    assert len(records) == 1
    assert records[0].event_type == "concept_video_session"
    assert json.loads(records[0].payload_json)["completion_ratio"] == 0.8
    assert records[0].source_version == "study_buddy_v1_test"

    service.close()


def test_telemetry_service_rejects_invalid_events():
    service = TelemetryService(database=Database("sqlite://"))

    with pytest.raises(ValidationError):
        service.record_events([_event_payload(student_id="")])

    assert service.list_events() == []
    service.close()


def test_telemetry_route_accepts_batch_in_background_task():
    class _FakeTelemetryService:
        def __init__(self) -> None:
            self.events: list[dict[str, Any]] = []

        def record_events(self, events: list[dict[str, Any]]) -> list[str]:
            self.events.extend(events)
            return ["event-1"]

    telemetry = _FakeTelemetryService()
    app = create_app(
        services=ServiceContainer(
            lesson_catalog=None,
            user_evaluation=None,
            auth=_FakeAuthService(),
            execution=None,
            workspace=None,
            metrics_export=None,
            telemetry=telemetry,
        )
    )
    client = TestClient(app)

    response = client.post(
        "/telemetry/events",
        json={
            "events": [
                {
                    **_event_payload(),
                    "occurred_at_utc": "2026-05-13T10:00:00Z",
                }
            ]
        },
        headers=_auth_headers(),
    )

    assert response.status_code == 202
    assert response.json() == {"accepted": 1}
    assert telemetry.events[0]["event_type"] == "concept_video_session"


def test_execution_service_records_backend_submission_telemetry(monkeypatch):
    telemetry = TelemetryService(database=Database("sqlite://"))
    service = ExecutionService(telemetry_service=telemetry)

    def _fake_run_submission_with_timeout(payload: dict[str, Any]) -> dict[str, Any]:
        del payload
        return {"status": "success", "metrics": {"episodes_completed": 1}}

    monkeypatch.setattr(
        "backend.services.execution_service.run_submission_with_timeout",
        _fake_run_submission_with_timeout,
    )

    service.execute_sync(
        {
            "student_id": "student-1",
            "lesson_id": "dp_policy_eval",
            "session_id": "study-session-1",
            "code": "print('ok')",
        }
    )

    records = telemetry.list_events(session_id="study-session-1")
    assert len(records) == 1
    assert records[0].event_type == "submission_result"
    assert json.loads(records[0].payload_json)["passed"] is True
    telemetry.close()


def test_execution_service_records_failed_submission_telemetry(monkeypatch):
    telemetry = TelemetryService(database=Database("sqlite://"))
    service = ExecutionService(telemetry_service=telemetry)

    def _fake_run_submission_with_timeout(payload: dict[str, Any]) -> dict[str, Any]:
        del payload
        raise ExecutionPipelineError(
            status_code=400,
            detail={"message": "Failed.", "failure_kind": "test_failure"},
        )

    monkeypatch.setattr(
        "backend.services.execution_service.run_submission_with_timeout",
        _fake_run_submission_with_timeout,
    )

    with pytest.raises(ExecutionPipelineError):
        service.execute_sync(
            {
                "student_id": "student-1",
                "lesson_id": "dp_policy_eval",
                "session_id": "study-session-1",
                "code": "print('bad')",
            }
        )

    records = telemetry.list_events(session_id="study-session-1")
    payload = json.loads(records[0].payload_json)
    assert payload["passed"] is False
    assert payload["failure_kind"] == "test_failure"
    telemetry.close()
