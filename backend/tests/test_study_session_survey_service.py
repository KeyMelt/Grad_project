from __future__ import annotations

import pytest

from backend.persistence import Database
from backend.services.study_session_survey_service import StudySessionSurveyService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_service() -> StudySessionSurveyService:
    return StudySessionSurveyService(database=Database("sqlite://"))


def _default_kwargs(**overrides) -> dict:
    base = {
        "study_session_id": "session-1",
        "student_id": "student-1",
        "condition": "adaptive",
        "sus_q1": 3,
        "sus_q2": 3,
        "sus_q3": 3,
        "sus_q4": 3,
        "sus_q5": 3,
        "sus_q6": 3,
        "sus_q7": 3,
        "sus_q8": 3,
        "sus_q9": 3,
        "sus_q10": 3,
        "tlx_mental_demand": 50,
        "tlx_physical_demand": 50,
        "tlx_temporal_demand": 50,
        "tlx_performance": 50,
        "tlx_effort": 50,
        "tlx_frustration": 50,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# SUS score computation
# ---------------------------------------------------------------------------

def test_sus_score_all_threes_gives_50():
    """All items rated 3 → SUS = 50.0 (Brooke 1996 verification)."""
    service = _make_service()
    record = service.submit_survey(**_default_kwargs())
    assert record.sus_score == pytest.approx(50.0)


def test_sus_score_max_score():
    """Odd items = 5, even items = 1 → SUS = 100.0."""
    service = _make_service()
    kwargs = _default_kwargs(
        sus_q1=5, sus_q3=5, sus_q5=5, sus_q7=5, sus_q9=5,
        sus_q2=1, sus_q4=1, sus_q6=1, sus_q8=1, sus_q10=1,
    )
    record = service.submit_survey(**kwargs)
    assert record.sus_score == pytest.approx(100.0)


def test_sus_score_min_score():
    """Odd items = 1, even items = 5 → SUS = 0.0."""
    service = _make_service()
    kwargs = _default_kwargs(
        sus_q1=1, sus_q3=1, sus_q5=1, sus_q7=1, sus_q9=1,
        sus_q2=5, sus_q4=5, sus_q6=5, sus_q8=5, sus_q10=5,
    )
    record = service.submit_survey(**kwargs)
    assert record.sus_score == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# TLX overall computation
# ---------------------------------------------------------------------------

def test_tlx_overall_is_mean_of_six_subscales():
    service = _make_service()
    record = service.submit_survey(**_default_kwargs(
        tlx_mental_demand=10,
        tlx_physical_demand=20,
        tlx_temporal_demand=30,
        tlx_performance=40,
        tlx_effort=50,
        tlx_frustration=60,
    ))
    expected = (10 + 20 + 30 + 40 + 50 + 60) / 6.0
    assert record.tlx_overall == pytest.approx(expected)


def test_tlx_overall_all_same():
    service = _make_service()
    record = service.submit_survey(**_default_kwargs(
        tlx_mental_demand=75,
        tlx_physical_demand=75,
        tlx_temporal_demand=75,
        tlx_performance=75,
        tlx_effort=75,
        tlx_frustration=75,
    ))
    assert record.tlx_overall == pytest.approx(75.0)


# ---------------------------------------------------------------------------
# SUS item range validation
# ---------------------------------------------------------------------------

def test_sus_item_below_range_raises():
    service = _make_service()
    with pytest.raises(ValueError, match="sus_q3"):
        service.submit_survey(**_default_kwargs(sus_q3=0))


def test_sus_item_above_range_raises():
    service = _make_service()
    with pytest.raises(ValueError, match="sus_q7"):
        service.submit_survey(**_default_kwargs(sus_q7=6))


# ---------------------------------------------------------------------------
# TLX subscale range validation
# ---------------------------------------------------------------------------

def test_tlx_subscale_below_range_raises():
    service = _make_service()
    with pytest.raises(ValueError, match="tlx_effort"):
        service.submit_survey(**_default_kwargs(tlx_effort=-1))


def test_tlx_subscale_above_range_raises():
    service = _make_service()
    with pytest.raises(ValueError, match="tlx_frustration"):
        service.submit_survey(**_default_kwargs(tlx_frustration=101))


# ---------------------------------------------------------------------------
# Condition validation
# ---------------------------------------------------------------------------

def test_invalid_condition_raises():
    service = _make_service()
    with pytest.raises(ValueError, match="condition"):
        service.submit_survey(**_default_kwargs(condition="experimental"))


# ---------------------------------------------------------------------------
# get_survey
# ---------------------------------------------------------------------------

def test_get_survey_returns_none_for_unknown_session():
    service = _make_service()
    result = service.get_survey("nonexistent-session-id")
    assert result is None


def test_get_survey_returns_record_after_submit():
    service = _make_service()
    service.submit_survey(**_default_kwargs(study_session_id="sess-abc"))
    result = service.get_survey("sess-abc")
    assert result is not None
    assert result.study_session_id == "sess-abc"
    assert result.sus_score == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# list_surveys
# ---------------------------------------------------------------------------

def test_list_surveys_filters_by_condition():
    service = _make_service()

    service.submit_survey(**_default_kwargs(
        study_session_id="sess-1",
        student_id="student-1",
        condition="adaptive",
    ))
    service.submit_survey(**_default_kwargs(
        study_session_id="sess-2",
        student_id="student-2",
        condition="control",
    ))
    service.submit_survey(**_default_kwargs(
        study_session_id="sess-3",
        student_id="student-3",
        condition="adaptive",
    ))

    adaptive = service.list_surveys(condition="adaptive")
    assert len(adaptive) == 2
    assert all(r.condition == "adaptive" for r in adaptive)

    control = service.list_surveys(condition="control")
    assert len(control) == 1
    assert control[0].condition == "control"


def test_list_surveys_filters_by_student_id():
    service = _make_service()

    service.submit_survey(**_default_kwargs(
        study_session_id="sess-1",
        student_id="alice",
        condition="adaptive",
    ))
    service.submit_survey(**_default_kwargs(
        study_session_id="sess-2",
        student_id="bob",
        condition="control",
    ))

    results = service.list_surveys(student_id="alice")
    assert len(results) == 1
    assert results[0].student_id == "alice"


def test_list_surveys_no_filter_returns_all():
    service = _make_service()

    service.submit_survey(**_default_kwargs(
        study_session_id="sess-1",
        student_id="s1",
        condition="adaptive",
    ))
    service.submit_survey(**_default_kwargs(
        study_session_id="sess-2",
        student_id="s2",
        condition="control",
    ))

    results = service.list_surveys()
    assert len(results) == 2


def test_list_surveys_empty_returns_empty_list():
    service = _make_service()
    assert service.list_surveys() == []
