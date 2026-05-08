from __future__ import annotations

from backend.lessons import get_lesson_definition
from backend.services.student_feedback_service import StudentFeedbackService


def test_feedback_service_uses_fallback_when_disabled():
    lesson = get_lesson_definition("td_q_learning")
    assert lesson is not None
    service = StudentFeedbackService(enabled=False, api_key="")

    feedback = service.build_feedback(
        lesson=lesson,
        submitted_code=lesson.starter_code,
        failure_kind="incomplete_template",
        issues=["Complete every guided blank before submitting."],
        unresolved_blanks=["q_learning_best_next"],
        test_results=[],
    )

    assert feedback["status"] == "incomplete_template"
    assert feedback["affected_blank_ids"] == ["q_learning_best_next"]


def test_feedback_service_parses_structured_gemini_response(monkeypatch):
    lesson = get_lesson_definition("td_q_learning")
    assert lesson is not None
    service = StudentFeedbackService(enabled=True, api_key="test-key")

    monkeypatch.setattr(
        service,
        "_call_gemini",
        lambda prompt: (
            '{"status":"validation_error","summary":"The required function body is incomplete.","likely_issue":"The TD update step is still missing.","affected_blank_ids":["q_learning_update_rule"],"next_steps":["Finish the incremental TD update.","Keep the existing function signature."],"hint_level":"light"}'
        ),
    )

    feedback = service.build_feedback(
        lesson=lesson,
        submitted_code=lesson.starter_code,
        failure_kind="validation_error",
        issues=["NameError: q_learning_update not found"],
        unresolved_blanks=["q_learning_update_rule"],
        test_results=[],
    )

    assert feedback["status"] == "validation_error"
    assert feedback["affected_blank_ids"] == ["q_learning_update_rule"]
    assert "full solution" not in feedback["summary"].lower()


def test_feedback_service_falls_back_on_malformed_gemini_response(monkeypatch):
    lesson = get_lesson_definition("td_q_learning")
    assert lesson is not None
    service = StudentFeedbackService(enabled=True, api_key="test-key")

    monkeypatch.setattr(service, "_call_gemini", lambda prompt: "not-json")

    feedback = service.build_feedback(
        lesson=lesson,
        submitted_code=lesson.starter_code,
        failure_kind="runtime_error",
        issues=["ZeroDivisionError: division by zero"],
        unresolved_blanks=[],
        test_results=[],
    )

    assert feedback["status"] == "runtime_error"
    assert feedback["summary"] == (
        "The submission raised an error while the lesson code was running."
    )


def test_feedback_service_falls_back_on_timeout(monkeypatch):
    lesson = get_lesson_definition("td_q_learning")
    assert lesson is not None
    service = StudentFeedbackService(enabled=True, api_key="test-key", timeout_seconds=0.01)

    def _raise_timeout(prompt: str) -> str:
        raise TimeoutError("timed out")

    monkeypatch.setattr(service, "_call_gemini", _raise_timeout)

    feedback = service.build_feedback(
        lesson=lesson,
        submitted_code=lesson.starter_code,
        failure_kind="test_failure",
        issues=["1 lesson sample test(s) failed."],
        unresolved_blanks=[],
        test_results=[
            {
                "name": "q_learning_update_target",
                "passed": False,
                "message": "Expected max-next bootstrap.",
            }
        ],
    )

    assert feedback["status"] == "test_failure"
    assert "q_learning_update_target" in " ".join(feedback["next_steps"])
