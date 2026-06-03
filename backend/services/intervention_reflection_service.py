from __future__ import annotations

from dataclasses import dataclass
import re

from backend.lesson_registry import get_lesson_definition
from backend.services.pedagogical_llm_service import PedagogicalIntervention


@dataclass(frozen=True)
class ReflectionResult:
    intervention: PedagogicalIntervention | None
    pass_result: str
    note: str = ""


class InterventionReflectionService:
    max_code_block_lines = 3

    def reflect(
        self,
        *,
        intervention: PedagogicalIntervention,
        lesson_id: str,
    ) -> ReflectionResult:
        if intervention.solution_leakage_risk == "high":
            return ReflectionResult(
                intervention=None,
                pass_result="blocked",
                note="llm_reported_high_leakage_risk",
            )

        text = "\n".join(
            [
                intervention.message,
                intervention.diagnostic_question,
                intervention.checkpoint or "",
                intervention.next_step,
            ]
        )
        if self._has_large_code_block(text):
            return ReflectionResult(
                intervention=None,
                pass_result="blocked",
                note="large_code_block",
            )

        leaked_blank = self._leaks_template_blank(text, lesson_id)
        if leaked_blank:
            return ReflectionResult(
                intervention=None,
                pass_result="blocked",
                note=f"template_blank_leak:{leaked_blank}",
            )

        return ReflectionResult(intervention=intervention, pass_result="passed")

    def _has_large_code_block(self, text: str) -> bool:
        for match in re.finditer(r"```(?:\w+)?\n(.*?)```", text, flags=re.DOTALL):
            lines = [line for line in match.group(1).splitlines() if line.strip()]
            if len(lines) > self.max_code_block_lines:
                return True
        return False

    def _leaks_template_blank(self, text: str, lesson_id: str) -> str | None:
        lesson = get_lesson_definition(lesson_id)
        if lesson is None:
            return None
        lowered = text.lower()
        for blank in lesson.template_blanks:
            if blank.blank_id.lower() in lowered:
                return blank.blank_id
        return None
