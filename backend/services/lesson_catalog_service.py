"""Lesson catalog service — presents lessons to the Flutter client.

All lesson data now lives in the DB via LessonRegistryService.
Lecture notes are resolved from two locations (first match wins):
  1. backend/media/lesson_notes/<lesson_id>_lecture_notes.md  (admin-uploaded)
  2. manim_service/concept_videos/<lesson_id>_lecture_notes.md (built-in generated)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import os

if TYPE_CHECKING:
    from backend.services.lesson_registry_service import LessonRegistryService

# Primary upload dir (persistent volume in production, gitignored content)
NOTES_UPLOAD_DIR = Path(__file__).resolve().parents[2] / "backend" / "media" / "lesson_notes"
# Fallback dir (built-in manim-generated notes, committed to repo)
NOTES_BUILTIN_DIR = Path(__file__).resolve().parents[2] / "manim_service" / "concept_videos"

CONCEPT_VIDEO_ROUTE_PREFIX = os.environ.get(
    "RL_IDE_CONCEPT_VIDEO_ROUTE_PREFIX", "/media/concept-videos"
).rstrip("/")

_DEFAULT_SECTION_ORDER = (
    "Dynamic Programming",
    "Monte Carlo Methods",
    "Temporal Difference",
)


def _load_section_order() -> tuple[str, ...]:
    raw = os.environ.get("RL_IDE_LESSON_SECTION_ORDER", "").strip()
    if raw:
        return tuple(part.strip() for part in raw.split(",") if part.strip())
    return _DEFAULT_SECTION_ORDER


LESSON_SECTION_ORDER = _load_section_order()


def load_lecture_notes(lesson_id: str) -> str:
    """Load lecture notes for a lesson. Admin-uploaded file takes priority over built-in."""
    NOTES_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for directory in (NOTES_UPLOAD_DIR, NOTES_BUILTIN_DIR):
        path = directory / f"{lesson_id}_lecture_notes.md"
        if path.is_file():
            try:
                return path.read_text(encoding="utf-8")
            except OSError:
                pass
    return ""


def _with_backend_video_path(concept_video: dict, lesson_id: str) -> dict:
    updated = dict(concept_video)
    stream_path = str(updated.get("stream_path") or "")
    if stream_path:
        filename = stream_path.rstrip("/").rsplit("/", maxsplit=1)[-1]
    else:
        filename = f"{lesson_id}_concept.mp4"
    updated["stream_path"] = f"{CONCEPT_VIDEO_ROUTE_PREFIX}/{filename}"
    updated["caption_path"] = f"{CONCEPT_VIDEO_ROUTE_PREFIX}/{lesson_id}_captions.vtt"
    return updated


def _serialize_payload_for_client(payload: dict[str, Any]) -> dict[str, Any]:
    lesson_id = payload["id"]

    concept_video = dict(payload.get("concept_video") or {})
    concept_video = _with_backend_video_path(concept_video, lesson_id)
    concept_video["lecture_notes"] = load_lecture_notes(lesson_id)

    exercise = dict(payload.get("exercise") or {})
    exercise["template_blanks"] = [
        {
            "blank_id": b["blank_id"],
            "kind": b["kind"],
            "prompt": b["prompt"],
            "expected_concept": b["expected_concept"],
            "approx_line_anchor": b["approx_line_anchor"],
        }
        for b in payload.get("template_blanks", [])
    ]
    exercise["success_criteria"] = payload.get("success_criteria", [])

    return {
        "id": lesson_id,
        "title": payload.get("title", ""),
        "description": payload.get("description", ""),
        "category": payload.get("category", ""),
        "starter_code": payload.get("starter_code", ""),
        "backend_enabled": bool(payload.get("backend_enabled", True)),
        "concept_video": concept_video,
        "exercise": exercise,
    }


class LessonCatalogService:
    """Presents lessons to the Flutter client from the unified DB registry."""

    def __init__(self, registry: "LessonRegistryService") -> None:
        self._registry = registry

    def list_lessons(self) -> list[dict]:
        return [
            _serialize_payload_for_client(p)
            for p in self._registry.list_lesson_payloads()
        ]

    def list_lesson_sections(self) -> list[dict]:
        lessons_by_category: dict[str, list[dict]] = {
            cat: [] for cat in LESSON_SECTION_ORDER
        }
        for lesson in self.list_lessons():
            lessons_by_category.setdefault(lesson["category"], []).append(lesson)
        return [
            {"title": category, "lessons": lessons}
            for category, lessons in lessons_by_category.items()
            if lessons
        ]

    def get_lesson(self, lesson_id: str) -> dict | None:
        payload = self._registry.get_lesson_payload(lesson_id)
        return None if payload is None else _serialize_payload_for_client(payload)
