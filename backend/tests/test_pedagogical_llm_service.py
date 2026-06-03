from __future__ import annotations

from backend.services.pedagogical_context_assembler import PedagogicalPromptContext
from backend.services.pedagogical_llm_service import (
    PedagogicalChatContext,
    PedagogicalLLMService,
)


def _context() -> PedagogicalPromptContext:
    return PedagogicalPromptContext(
        student_id="student-1",
        lesson_id="dp_policy_eval",
        concept_id="dp_policy_eval",
        lesson_title="Policy Evaluation",
        lesson_description="Evaluate a policy on FrozenLake.",
        concept_prompts=["Bellman expectation: Complete one backup."],
        success_criteria=["Run one small check."],
        trigger_type="submission_failure_streak",
        trigger_score=1.0,
        intervention_type="mini_example",
        escalated=False,
    )


def _chat_context(message: str) -> PedagogicalChatContext:
    return PedagogicalChatContext(
        student_id="student-1",
        lesson_id="dp_policy_eval",
        session_id="session-1",
        lesson_title="Policy Evaluation",
        lesson_description="Evaluate a fixed policy over FrozenLake.",
        concept_prompts=["Bellman expectation: Complete one backup."],
        success_criteria=["Run one small check."],
        unresolved_blanks=["policy_eval_expectation"],
        failure_kind="runtime_error",
        latest_feedback={"summary": "Execution timed out."},
        message=message,
    )


def test_llm_service_uses_fallback_without_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    service = PedagogicalLLMService(enabled=True)

    intervention, metadata = service.generate(_context())

    assert intervention.title == "Check the failing pattern"
    assert intervention.solution_leakage_risk == "low"
    assert metadata["used_fallback"] is True
    assert metadata["prompt_version"] == "deterministic_v1"


def test_chat_fallback_responds_to_latest_message(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    service = PedagogicalLLMService(enabled=True)

    greeting, greeting_metadata = service.generate_chat(_chat_context("hello"))
    blocker, blocker_metadata = service.generate_chat(
        _chat_context("why is this timing out?")
    )
    recap, _ = service.generate_chat(_chat_context("Give me a quick recap"))

    assert "Hi." in greeting.reply
    assert "blocker" in blocker.reply
    assert "Quick recap" in recap.reply
    assert greeting.reply != blocker.reply
    assert greeting_metadata["used_fallback"] is True
    assert blocker_metadata["prompt_version"] == "deterministic_chat_v1"


def test_llm_service_accepts_mocked_gemini_json(monkeypatch):
    service = PedagogicalLLMService(
        enabled=True,
        api_key="test-key",
        model="gemini-test",
        timeout_seconds=2,
    )
    monkeypatch.setattr(
        service,
        "_call_gemini",
        lambda _prompt: """
        {
          "intervention_type": "mini_example",
          "title": "Compare the target",
          "message": "Focus on the expected return target without filling the exercise.",
          "diagnostic_question": "Which term changes after the transition?",
          "choices": ["Reward", "Discounted future value", "Policy weight"],
          "checkpoint": "State the target in words.",
          "next_step": "Run one small check.",
          "concept_ids": ["dp_policy_eval"],
          "solution_leakage_risk": "low"
        }
        """,
    )

    intervention, metadata = service.generate(_context())

    assert intervention.title == "Compare the target"
    assert intervention.intervention_type == "mini_example"
    assert metadata["model"] == "gemini-test"
    assert metadata["prompt_version"] == "pedagogical_intervention_v1"
    assert metadata["used_fallback"] is False


def test_llm_service_falls_back_on_invalid_model_output(monkeypatch):
    service = PedagogicalLLMService(
        enabled=True,
        api_key="test-key",
        model="gemini-test",
        timeout_seconds=2,
    )
    monkeypatch.setattr(service, "_call_gemini", lambda _prompt: "not json")

    intervention, metadata = service.generate(_context())

    assert intervention.title == "Check the failing pattern"
    assert metadata["used_fallback"] is True
    assert metadata["error"]
