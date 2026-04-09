from typing import Optional

from backend.lessons import (
    get_lesson_definition,
    list_lesson_definitions,
    serialize_lesson,
)


class LessonCatalogService:
    """Service boundary for lesson metadata and starter templates."""

    def list_lessons(self) -> list[dict]:
        return [serialize_lesson(lesson) for lesson in list_lesson_definitions()]

    def get_lesson(self, lesson_id: str) -> Optional[dict]:
        lesson = get_lesson_definition(lesson_id)
        return None if lesson is None else serialize_lesson(lesson)
