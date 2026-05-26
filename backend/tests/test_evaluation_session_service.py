from __future__ import annotations

import json

import pytest

from backend.persistence import Database
from backend.services.evaluation_session_service import EvaluationSessionService


def _make_service() -> EvaluationSessionService:
    return EvaluationSessionService(database=Database("sqlite://"))


# ---------------------------------------------------------------------------
# create_session
# ---------------------------------------------------------------------------


def test_create_session_persists_record_with_correct_fields():
    service = _make_service()

    session = service.create_session(
        student_id="student-1",
        condition="adaptive",
        lesson_ids=["rl_intro", "mdp_foundations"],
    )

    assert session.id
    assert session.student_id == "student-1"
    assert session.condition == "adaptive"
    assert json.loads(session.lesson_ids_json) == ["rl_intro", "mdp_foundations"]
    assert session.started_at_utc is not None
    assert session.pre_test_completed_at_utc is None
    assert session.post_test_completed_at_utc is None
    assert session.survey_completed_at_utc is None
    assert session.ended_at_utc is None
    assert session.source_version == "study_buddy_v1"


def test_create_session_raises_for_invalid_condition():
    service = _make_service()

    with pytest.raises(ValueError, match="Invalid condition"):
        service.create_session(
            student_id="student-1",
            condition="invalid_condition",
            lesson_ids=["rl_intro"],
        )


def test_create_session_raises_for_empty_lesson_ids():
    service = _make_service()

    with pytest.raises(ValueError, match="lesson_ids"):
        service.create_session(
            student_id="student-1",
            condition="control",
            lesson_ids=[],
        )


# ---------------------------------------------------------------------------
# get_session
# ---------------------------------------------------------------------------


def test_get_session_returns_none_for_unknown_id():
    service = _make_service()

    result = service.get_session("nonexistent-id")

    assert result is None


def test_get_session_returns_existing_session():
    service = _make_service()

    created = service.create_session(
        student_id="student-2",
        condition="control",
        lesson_ids=["rl_intro"],
    )

    fetched = service.get_session(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.student_id == "student-2"


# ---------------------------------------------------------------------------
# mark_pre_test_complete
# ---------------------------------------------------------------------------


def test_mark_pre_test_complete_sets_timestamp():
    service = _make_service()

    session = service.create_session(
        student_id="student-3",
        condition="adaptive",
        lesson_ids=["rl_intro"],
    )
    assert session.pre_test_completed_at_utc is None

    service.mark_pre_test_complete(session.id)

    updated = service.get_session(session.id)
    assert updated is not None
    assert updated.pre_test_completed_at_utc is not None


# ---------------------------------------------------------------------------
# mark_post_test_complete
# ---------------------------------------------------------------------------


def test_mark_post_test_complete_sets_both_timestamps():
    service = _make_service()

    session = service.create_session(
        student_id="student-4",
        condition="control",
        lesson_ids=["rl_intro"],
    )

    service.mark_post_test_complete(session.id)

    updated = service.get_session(session.id)
    assert updated is not None
    assert updated.post_test_completed_at_utc is not None
    assert updated.ended_at_utc is not None


# ---------------------------------------------------------------------------
# list_sessions
# ---------------------------------------------------------------------------


def test_list_sessions_filters_by_student_id():
    service = _make_service()

    service.create_session(
        student_id="student-a",
        condition="adaptive",
        lesson_ids=["rl_intro"],
    )
    service.create_session(
        student_id="student-b",
        condition="control",
        lesson_ids=["mdp_foundations"],
    )
    service.create_session(
        student_id="student-a",
        condition="control",
        lesson_ids=["policy_eval"],
    )

    results = service.list_sessions(student_id="student-a")

    assert len(results) == 2
    assert all(r.student_id == "student-a" for r in results)


def test_list_sessions_returns_all_when_no_filter():
    service = _make_service()

    service.create_session(
        student_id="student-x",
        condition="adaptive",
        lesson_ids=["rl_intro"],
    )
    service.create_session(
        student_id="student-y",
        condition="control",
        lesson_ids=["mdp_foundations"],
    )

    results = service.list_sessions()

    assert len(results) == 2


def test_list_sessions_ordered_by_started_at_utc():
    service = _make_service()

    service.create_session(
        student_id="student-z",
        condition="adaptive",
        lesson_ids=["rl_intro"],
    )
    service.create_session(
        student_id="student-z",
        condition="control",
        lesson_ids=["mdp_foundations"],
    )

    results = service.list_sessions(student_id="student-z")

    assert len(results) == 2
    assert results[0].started_at_utc <= results[1].started_at_utc
