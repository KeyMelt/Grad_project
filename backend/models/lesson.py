"""Shared lesson domain types used by the execution pipeline and registry."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class TemplateBlank:
    blank_id: str
    kind: str
    prompt: str
    expected_concept: str
    approx_line_anchor: int


@dataclass(frozen=True)
class LessonDefinition:
    id: str
    title: str
    description: str
    category: str
    required_function: str
    environment_name: str
    starter_code: str
    template_kind: str = "guided_fill_in"
    template_blanks: list[TemplateBlank] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)


def serialize_lesson(lesson: LessonDefinition) -> dict:
    return asdict(lesson)
