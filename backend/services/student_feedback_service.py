from __future__ import annotations

import concurrent.futures
import os
from typing import Literal

from pydantic import BaseModel, Field

from backend.models.lesson import LessonDefinition
from backend.services.env_loader import load_local_env

FailureKind = Literal[
    "incomplete_template",
    "validation_error",
    "runtime_error",
    "test_failure",
]


class StudentFeedback(BaseModel):
    status: FailureKind
    summary: str
    likely_issue: str
    affected_blank_ids: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    hint_level: Literal["light"] = "light"


class StudentFeedbackService:
    def __init__(
        self,
        *,
        enabled: bool | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        load_local_env()
        self.enabled = (
            enabled
            if enabled is not None
            else os.getenv("RL_IDE_GEMINI_ENABLED", "1").strip().lower() not in {"0", "false", "no"}
        )
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model = model or os.getenv("RL_IDE_GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.timeout_seconds = timeout_seconds or float(
            os.getenv("RL_IDE_GEMINI_TIMEOUT_SECONDS", "5")
        )

    def build_feedback(
        self,
        *,
        lesson: LessonDefinition,
        submitted_code: str,
        failure_kind: FailureKind,
        issues: list[str],
        unresolved_blanks: list[str],
        test_results: list[dict] | None = None,
    ) -> dict:
        fallback = self._fallback_feedback(
            lesson=lesson,
            failure_kind=failure_kind,
            issues=issues,
            unresolved_blanks=unresolved_blanks,
            test_results=test_results or [],
        )
        if not self.enabled or not self.api_key:
            return fallback.model_dump()

        try:
            return self._generate_feedback(
                lesson=lesson,
                submitted_code=submitted_code,
                failure_kind=failure_kind,
                issues=issues,
                unresolved_blanks=unresolved_blanks,
                test_results=test_results or [],
                fallback=fallback,
            ).model_dump()
        except Exception:
            return fallback.model_dump()

    def _generate_feedback(
        self,
        *,
        lesson: LessonDefinition,
        submitted_code: str,
        failure_kind: FailureKind,
        issues: list[str],
        unresolved_blanks: list[str],
        test_results: list[dict],
        fallback: StudentFeedback,
    ) -> StudentFeedback:
        prompt = self._build_prompt(
            lesson=lesson,
            submitted_code=submitted_code,
            failure_kind=failure_kind,
            issues=issues,
            unresolved_blanks=unresolved_blanks,
            test_results=test_results,
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._call_gemini, prompt)
            response_text = future.result(timeout=self.timeout_seconds)

        feedback = StudentFeedback.model_validate_json(response_text)
        return self._sanitize_feedback(feedback, fallback)

    def _call_gemini(self, prompt: str) -> str:
        from google import genai

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": StudentFeedback.model_json_schema(),
            },
        )
        return response.text

    def _sanitize_feedback(
        self,
        feedback: StudentFeedback,
        fallback: StudentFeedback,
    ) -> StudentFeedback:
        cleaned = StudentFeedback(
            status=feedback.status,
            summary=self._strip_solution_language(feedback.summary, fallback.summary),
            likely_issue=self._strip_solution_language(
                feedback.likely_issue,
                fallback.likely_issue,
            ),
            affected_blank_ids=feedback.affected_blank_ids or fallback.affected_blank_ids,
            next_steps=[
                self._strip_solution_language(step, "")
                for step in feedback.next_steps[:4]
                if self._strip_solution_language(step, "").strip()
            ]
            or fallback.next_steps,
            hint_level="light",
        )
        return cleaned

    def _fallback_feedback(
        self,
        *,
        lesson: LessonDefinition,
        failure_kind: FailureKind,
        issues: list[str],
        unresolved_blanks: list[str],
        test_results: list[dict],
    ) -> StudentFeedback:
        blank_map = {blank.blank_id: blank for blank in lesson.template_blanks}
        if failure_kind == "incomplete_template":
            next_steps = [
                blank_map[blank_id].prompt
                for blank_id in unresolved_blanks
                if blank_id in blank_map
            ][:4]
            if not next_steps:
                next_steps = [
                    "Replace every TODO block and __BLANK marker before submitting.",
                ]
            return StudentFeedback(
                status="incomplete_template",
                summary="The submission still contains guided blanks.",
                likely_issue="One or more placeholder sections were left unchanged in the template.",
                affected_blank_ids=unresolved_blanks,
                next_steps=next_steps,
            )

        if failure_kind == "test_failure":
            failed_names = [
                result.get("name", "sample_test")
                for result in test_results
                if not result.get("passed", False)
            ]
            return StudentFeedback(
                status="test_failure",
                summary="The code ran, but at least one lesson check still failed.",
                likely_issue=(
                    issues[0]
                    if issues
                    else "The implemented update rule does not match the lesson contract yet."
                ),
                affected_blank_ids=unresolved_blanks,
                next_steps=[
                    (
                        f"Recheck the logic behind {failed_names[0]}."
                        if failed_names
                        else "Recheck the failed lesson condition."
                    ),
                    (
                        lesson.success_criteria[0]
                        if lesson.success_criteria
                        else "Match the required update rule exactly."
                    ),
                    "Use Run to inspect intermediate values before submitting again.",
                ],
            )

        if failure_kind == "runtime_error":
            return StudentFeedback(
                status="runtime_error",
                summary="The submission raised an error while the lesson code was running.",
                likely_issue=(
                    issues[0] if issues else "A runtime exception interrupted the lesson execution."
                ),
                affected_blank_ids=unresolved_blanks,
                next_steps=[
                    "Check the traceback or error text in the submit result.",
                    "Verify names, indexes, and terminal-state branches in the updated code.",
                    "Use Run to isolate the failure before submitting again.",
                ],
            )

        return StudentFeedback(
            status="validation_error",
            summary="The submission does not satisfy the lesson interface yet.",
            likely_issue=(
                issues[0]
                if issues
                else "The required function or update expression is still incorrect."
            ),
            affected_blank_ids=unresolved_blanks,
            next_steps=[
                f"Keep the required function name: {lesson.required_function}.",
                (
                    lesson.success_criteria[0]
                    if lesson.success_criteria
                    else "Align the implementation with the lesson contract."
                ),
                "Submit again after the function body matches the requested update step.",
            ],
        )

    def _build_prompt(
        self,
        *,
        lesson: LessonDefinition,
        submitted_code: str,
        failure_kind: FailureKind,
        issues: list[str],
        unresolved_blanks: list[str],
        test_results: list[dict],
    ) -> str:
        blank_lines = "\n".join(
            [
                f"- {blank.blank_id}: {blank.prompt} | concept={blank.expected_concept} | line={blank.approx_line_anchor}"
                for blank in lesson.template_blanks
            ]
        )
        failed_tests = "\n".join(
            [
                f"- {result.get('name', 'sample_test')}: {result.get('message', '')}"
                for result in test_results
                if not result.get("passed", False)
            ]
        )
        issues_block = "\n".join(f"- {issue}" for issue in issues) or "- none"
        unresolved_block = "\n".join(f"- {blank_id}" for blank_id in unresolved_blanks) or "- none"
        success_block = "\n".join(f"- {item}" for item in lesson.success_criteria) or "- none"

        return f"""
You are generating brief diagnostic feedback for a reinforcement-learning coding exercise.

Do not provide a full solution.
Do not rewrite the student's code.
Do not output complete replacement code.
Keep the hint level light and diagnostic only.

Lesson:
- id: {lesson.id}
- title: {lesson.title}
- required function: {lesson.required_function}

Template blanks:
{blank_lines}

Failure kind:
- {failure_kind}

Reported issues:
{issues_block}

Unresolved blanks:
{unresolved_block}

Failed tests:
{failed_tests or "- none"}

Success criteria:
{success_block}

Student submission:
```python
{submitted_code}
```
""".strip()

    def _strip_solution_language(self, value: str, fallback: str) -> str:
        lowered = value.lower()
        banned_fragments = (
            "here is the code",
            "replace the function with",
            "use this code",
            "full solution",
            "complete implementation",
        )
        if any(fragment in lowered for fragment in banned_fragments):
            return fallback
        return value
