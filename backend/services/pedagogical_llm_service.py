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


class PedagogicalLLMUnavailableError(RuntimeError):
    def __init__(
        self,
        public_message: str,
        *,
        error_type: str,
        model: str | None = None,
    ) -> None:
        super().__init__(public_message)
        self.public_message = public_message
        self.error_type = error_type
        self.model = model


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
        if not self.enabled:
            raise PedagogicalLLMUnavailableError(
                "Study Buddy AI is disabled.",
                error_type="ai_disabled",
                model=None,
            )
        if not self.api_key:
            raise PedagogicalLLMUnavailableError(
                "Study Buddy AI is not configured.",
                error_type="missing_api_key",
                model=None,
            )

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
            raise PedagogicalLLMUnavailableError(
                "Study Buddy AI could not create an intervention right now.",
                error_type=type(error).__name__,
                model=self.model,
            ) from error

    def generate_chat(
        self,
        context: PedagogicalChatContext,
    ) -> tuple[PedagogicalChatReply, dict]:
        if not self.enabled:
            raise PedagogicalLLMUnavailableError(
                "Study Buddy AI is disabled.",
                error_type="ai_disabled",
                model=None,
            )
        if not self.api_key:
            raise PedagogicalLLMUnavailableError(
                "Study Buddy AI is not configured.",
                error_type="missing_api_key",
                model=None,
            )

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
            raise PedagogicalLLMUnavailableError(
                "Study Buddy AI could not reply right now.",
                error_type=type(error).__name__,
                model=self.model,
            ) from error

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
