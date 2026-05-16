from __future__ import annotations

import concurrent.futures
from pathlib import Path
import os
import time
from typing import Any, Literal

from pydantic import BaseModel, Field

from backend.config import trigger_config
from backend.services.env_loader import load_local_env
from backend.services.pedagogical_context_assembler import PedagogicalPromptContext

SolutionLeakageRisk = Literal["low", "medium", "high"]


class PedagogicalIntervention(BaseModel):
    intervention_type: str
    title: str
    message: str
    diagnostic_question: str
    choices: list[str] = Field(default_factory=list)
    checkpoint: str | None = None
    next_step: str
    concept_ids: list[str] = Field(default_factory=list)
    solution_leakage_risk: SolutionLeakageRisk = "low"


class PedagogicalChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class PedagogicalChatContext(BaseModel):
    student_id: str
    lesson_id: str
    session_id: str
    lesson_title: str
    lesson_description: str
    concept_prompts: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    unresolved_blanks: list[str] = Field(default_factory=list)
    failure_kind: str | None = None
    latest_feedback: dict[str, Any] = Field(default_factory=dict)
    current_code_excerpt: str | None = None
    recent_failures: list[dict[str, Any]] = Field(default_factory=list)
    recent_interventions: list[dict[str, Any]] = Field(default_factory=list)
    history: list[PedagogicalChatMessage] = Field(default_factory=list)
    message: str = Field(min_length=1, max_length=4000)


class PedagogicalChatReply(BaseModel):
    reply: str = Field(min_length=1, max_length=4000)
    suggested_next_step: str | None = Field(default=None, max_length=500)
    concept_ids: list[str] = Field(default_factory=list)
    solution_leakage_risk: SolutionLeakageRisk = "low"


class PedagogicalLLMService:
    def __init__(
        self,
        *,
        enabled: bool | None = None,
        api_key: str | None = None,
        model: str | None = None,
        prompt_version: str = "pedagogical_intervention_v1",
        timeout_seconds: float | None = None,
    ) -> None:
        load_local_env()
        self.enabled = (
            enabled
            if enabled is not None
            else os.getenv("RL_IDE_STUDY_BUDDY_AI_ENABLED", "1").strip().lower()
            not in {"0", "false", "no"}
        )
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model = model or os.getenv("RL_IDE_GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.prompt_version = prompt_version
        self.timeout_seconds = timeout_seconds or float(
            os.getenv(
                "RL_IDE_STUDY_BUDDY_LLM_TIMEOUT_SECONDS",
                str(trigger_config.LLM_TIMEOUT_SECONDS),
            )
        )

    def generate(
        self,
        context: PedagogicalPromptContext,
    ) -> tuple[PedagogicalIntervention, dict]:
        fallback = self.fallback_intervention(context)
        if not self.enabled or not self.api_key:
            return fallback, {
                "model": None,
                "prompt_version": "deterministic_v1",
                "latency_ms": 0,
                "used_fallback": True,
            }

        prompt = self._build_prompt(context)
        started = time.perf_counter()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._call_gemini, prompt)
                raw_text = future.result(timeout=self.timeout_seconds)
            intervention = PedagogicalIntervention.model_validate_json(raw_text)
            return intervention, {
                "model": self.model,
                "prompt_version": self.prompt_version,
                "latency_ms": int((time.perf_counter() - started) * 1000),
                "used_fallback": False,
            }
        except Exception as error:
            return fallback, {
                "model": self.model,
                "prompt_version": self.prompt_version,
                "latency_ms": int((time.perf_counter() - started) * 1000),
                "used_fallback": True,
                "error": type(error).__name__,
            }

    def generate_chat(
        self,
        context: PedagogicalChatContext,
    ) -> tuple[PedagogicalChatReply, dict]:
        fallback = self.fallback_chat_reply(context)
        if not self.enabled or not self.api_key:
            return fallback, {
                "model": None,
                "prompt_version": "deterministic_chat_v1",
                "latency_ms": 0,
                "used_fallback": True,
            }

        prompt = self._build_chat_prompt(context)
        started = time.perf_counter()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self._call_gemini_for_schema,
                    prompt,
                    PedagogicalChatReply,
                )
                raw_text = future.result(timeout=self.timeout_seconds)
            reply = PedagogicalChatReply.model_validate_json(raw_text)
            return reply, {
                "model": self.model,
                "prompt_version": "pedagogical_chat_v1",
                "latency_ms": int((time.perf_counter() - started) * 1000),
                "used_fallback": False,
            }
        except Exception as error:
            return fallback, {
                "model": self.model,
                "prompt_version": "pedagogical_chat_v1",
                "latency_ms": int((time.perf_counter() - started) * 1000),
                "used_fallback": True,
                "error": type(error).__name__,
            }

    def fallback_chat_reply(
        self,
        context: PedagogicalChatContext,
    ) -> PedagogicalChatReply:
        next_step = (
            context.success_criteria[0]
            if context.success_criteria
            else "Run one small check after you make the next code change."
        )
        blocker = (
            f" The current blocker appears related to `{context.failure_kind}`."
            if context.failure_kind
            else ""
        )
        blank_note = (
            f" Focus first on `{context.unresolved_blanks[0]}`."
            if context.unresolved_blanks
            else ""
        )
        return PedagogicalChatReply(
            reply=(
                f"Use the lesson goal as the anchor: {context.lesson_description}"
                f"{blocker}{blank_note} I can help you reason through the next "
                "step, but I will keep it at the checkpoint level so you still "
                "write the solution yourself."
            ),
            suggested_next_step=next_step,
            concept_ids=[context.lesson_id],
            solution_leakage_risk="low",
        )

    def fallback_intervention(
        self,
        context: PedagogicalPromptContext,
    ) -> PedagogicalIntervention:
        title = {
            "submission_failure_streak": "Check the failing pattern",
            "video_loop_confusion": "Pause on the core idea",
            "editor_stall": "Take one small next step",
            "quiz_gap": "Review before moving on",
        }.get(context.trigger_type, "Study Buddy checkpoint")
        question = {
            "submission_failure_streak": "Which part is failing right now?",
            "video_loop_confusion": "Which part of the concept feels least clear?",
            "editor_stall": "What is the smallest code change you can test next?",
            "quiz_gap": "Which answer choice were you least confident about?",
        }.get(context.trigger_type, "What would help most right now?")
        next_step = (
            context.success_criteria[0]
            if context.success_criteria
            else "Try one small check, then run the lesson again."
        )
        return PedagogicalIntervention(
            intervention_type=context.intervention_type,
            title=title,
            message=(
                "I noticed a struggle signal for this lesson. Focus on the concept "
                "rather than the full solution: compare the goal, the evidence from "
                "your last attempt, and one small next action."
            ),
            diagnostic_question=question,
            choices=[
                "I need the concept restated",
                "I need a smaller checkpoint",
                "I want to try again",
            ],
            checkpoint="State the update goal in one sentence before changing code.",
            next_step=next_step,
            concept_ids=[context.concept_id or context.lesson_id],
            solution_leakage_risk="low",
        )

    def _call_gemini(self, prompt: str) -> str:
        return self._call_gemini_for_schema(prompt, PedagogicalIntervention)

    def _call_gemini_for_schema(self, prompt: str, schema_model: type[BaseModel]) -> str:
        from google import genai

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": schema_model.model_json_schema(),
            },
        )
        return response.text

    def _build_prompt(self, context: PedagogicalPromptContext) -> str:
        template = self._load_prompt_template()
        return f"""
{template}

Context JSON:
{context.model_dump_json(indent=2)}
""".strip()

    def _build_chat_prompt(self, context: PedagogicalChatContext) -> str:
        return f"""
You are Study Buddy, a concise reinforcement-learning tutor embedded inside a coding workspace.

Respond to the learner's latest message using the provided lesson and workspace context.

Rules:
- Do not provide a full completed solution or paste replacement code.
- Keep the reply short enough for a side panel.
- Ground the answer in the lesson objective, current exercise, recent feedback, and current code excerpt when available.
- Prefer one diagnostic question or one concrete next checkpoint over broad explanation.
- If the learner asks for the direct answer, give a hint and a checkpoint instead.

Return JSON matching the supplied schema.

Context JSON:
{context.model_dump_json(indent=2)}
""".strip()

    def _load_prompt_template(self) -> str:
        prompt_path = Path(__file__).resolve().parents[1] / "prompts" / f"{self.prompt_version}.txt"
        return prompt_path.read_text()
