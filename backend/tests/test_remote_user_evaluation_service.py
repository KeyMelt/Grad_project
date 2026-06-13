from __future__ import annotations

from typing import Any

import pytest
import requests

from backend.services.remote_user_evaluation_service import RemoteUserEvaluationService


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, Any] | None = None, text: str = ""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self) -> dict[str, Any]:
        if self._payload is None:
            raise ValueError("No JSON payload")
        return self._payload


def test_sign_in_proxies_to_user_service(monkeypatch):
    def _fake_request(**kwargs):
        assert kwargs["url"].endswith("/internal/auth/sign-in")
        assert kwargs["json"]["firebase_id_token"] == "token"
        return _FakeResponse(
            200,
            {
                "student": {"id": "student-1", "display_name": "Maya"},
                "progress": {"completed_lesson_ids": []},
            },
        )

    monkeypatch.setattr(requests, "request", _fake_request)
    service = RemoteUserEvaluationService(user_service_base_url="http://127.0.0.1:8200")

    payload = service.sign_in("Maya", "ignored", "token")

    assert payload["student"]["id"] == "student-1"


def test_get_dashboard_returns_none_on_404(monkeypatch):
    monkeypatch.setattr(
        requests,
        "request",
        lambda **kwargs: _FakeResponse(404, {"detail": "not found"}),
    )
    service = RemoteUserEvaluationService(user_service_base_url="http://127.0.0.1:8200")

    assert service.get_dashboard("missing") is None


def test_ensure_student_record_posts_to_internal_service(monkeypatch):
    def _fake_request(**kwargs):
        assert kwargs["method"] == "POST"
        assert kwargs["url"].endswith("/internal/students/ensure")
        assert kwargs["json"] == {
            "student_id": "new-student",
            "display_name": "New Student",
        }
        return _FakeResponse(
            200,
            {
                "student": {"id": "new-student", "display_name": "New Student"},
                "progress": {"completed_lesson_ids": []},
            },
        )

    monkeypatch.setattr(requests, "request", _fake_request)
    service = RemoteUserEvaluationService(user_service_base_url="http://127.0.0.1:8200")

    payload = service.ensure_student_record(
        student_id="new-student",
        display_name="New Student",
    )

    assert payload["student"]["id"] == "new-student"


def test_quiz_start_raises_value_error_on_bad_request(monkeypatch):
    monkeypatch.setattr(
        requests,
        "request",
        lambda **kwargs: _FakeResponse(400, {"detail": "Unknown student_id."}),
    )
    service = RemoteUserEvaluationService(user_service_base_url="http://127.0.0.1:8200")

    with pytest.raises(ValueError):
        service.start_quiz("missing", "pretest")


def test_quiz_catalog_proxies_to_user_service(monkeypatch):
    def _fake_request(**kwargs):
        assert kwargs["method"] == "GET"
        assert kwargs["url"].endswith("/internal/quiz/catalog")
        return _FakeResponse(
            200,
            {
                "assessment_phases": [],
                "category_quizzes": [],
                "quiz_families": [{"id": "dp_policy_eval"}],
            },
        )

    monkeypatch.setattr(requests, "request", _fake_request)
    service = RemoteUserEvaluationService(user_service_base_url="http://127.0.0.1:8200")

    payload = service.quiz_catalog()

    assert payload["quiz_families"] == [{"id": "dp_policy_eval"}]


def test_metrics_rows_are_unwrapped(monkeypatch):
    monkeypatch.setattr(
        requests,
        "request",
        lambda **kwargs: _FakeResponse(200, {"rows": [{"student_id": "student-1"}]}),
    )
    service = RemoteUserEvaluationService(user_service_base_url="http://127.0.0.1:8200")

    rows = service.list_n_gain_metrics()

    assert rows == [{"student_id": "student-1"}]
