from __future__ import annotations

from typing import Any

from fastapi import APIRouter


def build_lessons_router(services: Any) -> APIRouter:
    router = APIRouter()

    @router.get("/lessons")
    def get_lessons():
        sections = services.lesson_catalog.list_lesson_sections()
        return {
            "sections": sections,
            "lessons": [lesson for section in sections for lesson in section.get("lessons", [])],
        }

    return router
