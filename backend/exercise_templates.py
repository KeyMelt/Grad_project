from __future__ import annotations

import re
from typing import Any

from backend.lessons import LessonDefinition, TemplateBlank

EXPRESSION_PLACEHOLDER_PATTERN = re.compile(r"__BLANK_([A-Za-z0-9_]+)__")
BLOCK_PLACEHOLDER_PATTERN = re.compile(r'raise\s+NotImplementedError\("TODO:\s*([A-Za-z0-9_]+)"\)')


def find_unresolved_blanks(
    submitted_code: str,
    lesson: LessonDefinition,
) -> list[str]:
    expression_ids = set(EXPRESSION_PLACEHOLDER_PATTERN.findall(submitted_code))
    block_ids = set(BLOCK_PLACEHOLDER_PATTERN.findall(submitted_code))
    unresolved = expression_ids | block_ids
    ordered_blank_ids = [blank.blank_id for blank in lesson.template_blanks]
    ordered_matches = [blank_id for blank_id in ordered_blank_ids if blank_id in unresolved]
    extra_matches = sorted(unresolved - set(ordered_matches))
    return ordered_matches + extra_matches


def build_blank_diagnostics(
    submitted_code: str,
    lesson: LessonDefinition,
) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    blank_map = {blank.blank_id: blank for blank in lesson.template_blanks}
    lines = submitted_code.splitlines()

    for blank_id in find_unresolved_blanks(submitted_code, lesson):
        blank = blank_map.get(blank_id)
        line_number, column = _find_blank_location(lines, blank_id)
        message = _blank_message(blank_id, blank)
        diagnostics.append(
            {
                "message": message,
                "line": line_number,
                "column": column,
                "severity": "error",
            }
        )
    return diagnostics


def _find_blank_location(lines: list[str], blank_id: str) -> tuple[int, int]:
    expression_marker = f"__BLANK_{blank_id}__"
    block_marker = f"TODO: {blank_id}"
    for index, line in enumerate(lines, start=1):
        expression_column = line.find(expression_marker)
        if expression_column >= 0:
            return index, expression_column + 1
        block_column = line.find(block_marker)
        if block_column >= 0:
            return index, block_column + 1
    return 1, 1


def _blank_message(blank_id: str, blank: TemplateBlank | None) -> str:
    if blank is None:
        return f"Complete the guided blank '{blank_id}' before submitting."
    return f"{blank.prompt} ({blank.expected_concept})"
