"""Shared pytest fixtures for the backend test suite."""

from __future__ import annotations

import pytest

import backend.lesson_registry as _lr
from backend.persistence import Database
from backend.services.lesson_registry_service import LessonRegistryService


@pytest.fixture(autouse=True)
def _lesson_registry(tmp_path):
    """Seed an in-memory lesson registry for every test that needs it.

    Tests that don't call get_lesson_definition() are unaffected — the
    fixture just ensures the module-level singleton is always initialised
    so no test can fail with 'registry has not been initialised'.
    """
    db = Database(database_url=f"sqlite:///{tmp_path / 'test_registry.db'}")
    db.create_schema()
    registry = LessonRegistryService(database=db)
    _lr.set_registry(registry)
    yield
    _lr.set_registry(None)  # type: ignore[arg-type]
