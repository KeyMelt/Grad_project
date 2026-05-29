"""Module-level shim so existing callers need only change their import path.

All callers that previously imported from ``backend.lessons`` should now
import from here.  The actual registry is backed by the DB via
:class:`~backend.services.lesson_registry_service.LessonRegistryService`,
which is initialised once by the application and registered here at
startup via :func:`set_registry`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.models.lesson import LessonDefinition, TemplateBlank, serialize_lesson  # noqa: F401

if TYPE_CHECKING:
    from backend.services.lesson_registry_service import LessonRegistryService

_registry: "LessonRegistryService | None" = None


def set_registry(registry: "LessonRegistryService") -> None:
    """Called once at application startup to wire the DB-backed registry."""
    global _registry
    _registry = registry


def get_lesson_definition(lesson_id: str) -> LessonDefinition | None:
    if _registry is None:
        raise RuntimeError(
            "Lesson registry has not been initialised. "
            "Call lesson_registry.set_registry() during app startup."
        )
    return _registry.get_lesson(lesson_id)


def list_lesson_definitions() -> list[LessonDefinition]:
    if _registry is None:
        raise RuntimeError(
            "Lesson registry has not been initialised. "
            "Call lesson_registry.set_registry() during app startup."
        )
    return _registry.list_lessons()
