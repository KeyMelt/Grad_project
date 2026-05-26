from __future__ import annotations

import pytest

from backend.persistence import Database
from backend.services.prediction_probe_service import PredictionProbeService


def _make_service() -> PredictionProbeService:
    return PredictionProbeService(database=Database("sqlite://"))


def test_submit_attempt_within_tolerance():
    service = _make_service()

    record = service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="qlearn_td_target_1",
        actual_value=10.0,
        predicted_value=10.3,
        tolerance=0.5,
    )

    assert abs(record.absolute_error - 0.3) < 1e-9
    assert record.is_within_tolerance is True


def test_submit_attempt_outside_tolerance():
    service = _make_service()

    record = service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="qlearn_td_target_1",
        actual_value=10.0,
        predicted_value=11.0,
        tolerance=0.5,
    )

    assert abs(record.absolute_error - 1.0) < 1e-9
    assert record.is_within_tolerance is False


def test_submit_attempt_increments_attempt_index():
    service = _make_service()

    r1 = service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="qlearn_td_target_1",
        actual_value=10.0,
        predicted_value=9.0,
        tolerance=1.0,
    )
    r2 = service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="qlearn_td_target_1",
        actual_value=10.0,
        predicted_value=10.5,
        tolerance=1.0,
    )
    r3 = service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="qlearn_td_target_1",
        actual_value=10.0,
        predicted_value=10.1,
        tolerance=1.0,
    )

    assert r1.attempt_index == 1
    assert r2.attempt_index == 2
    assert r3.attempt_index == 3


def test_submit_attempt_different_probes_index_independently():
    service = _make_service()

    r_a1 = service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="probe_a",
        actual_value=1.0,
        predicted_value=1.0,
        tolerance=0.1,
    )
    r_b1 = service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="probe_b",
        actual_value=2.0,
        predicted_value=2.0,
        tolerance=0.1,
    )
    r_a2 = service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="probe_a",
        actual_value=1.0,
        predicted_value=1.5,
        tolerance=0.1,
    )

    assert r_a1.attempt_index == 1
    assert r_b1.attempt_index == 1
    assert r_a2.attempt_index == 2


def test_submit_attempt_raises_for_negative_tolerance():
    service = _make_service()

    with pytest.raises(ValueError, match="tolerance"):
        service.submit_attempt(
            study_session_id="session-1",
            student_id="student-1",
            lesson_id="rl_intro",
            concept_id="td_update",
            probe_id="probe_a",
            actual_value=1.0,
            predicted_value=1.0,
            tolerance=-0.1,
        )


def test_submit_attempt_raises_for_empty_string_fields():
    service = _make_service()

    with pytest.raises(ValueError):
        service.submit_attempt(
            study_session_id="",
            student_id="student-1",
            lesson_id="rl_intro",
            concept_id="td_update",
            probe_id="probe_a",
            actual_value=1.0,
            predicted_value=1.0,
            tolerance=0.1,
        )

    with pytest.raises(ValueError):
        service.submit_attempt(
            study_session_id="session-1",
            student_id="",
            lesson_id="rl_intro",
            concept_id="td_update",
            probe_id="probe_a",
            actual_value=1.0,
            predicted_value=1.0,
            tolerance=0.1,
        )


def test_list_attempts_filter_by_study_session_id():
    service = _make_service()

    service.submit_attempt(
        study_session_id="session-A",
        student_id="student-1",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="probe_1",
        actual_value=1.0,
        predicted_value=1.0,
        tolerance=0.1,
    )
    service.submit_attempt(
        study_session_id="session-B",
        student_id="student-1",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="probe_1",
        actual_value=2.0,
        predicted_value=2.0,
        tolerance=0.1,
    )

    results = service.list_attempts(study_session_id="session-A")
    assert len(results) == 1
    assert results[0].study_session_id == "session-A"


def test_list_attempts_filter_by_student_id():
    service = _make_service()

    service.submit_attempt(
        study_session_id="session-1",
        student_id="alice",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="probe_1",
        actual_value=1.0,
        predicted_value=1.0,
        tolerance=0.1,
    )
    service.submit_attempt(
        study_session_id="session-2",
        student_id="bob",
        lesson_id="rl_intro",
        concept_id="td_update",
        probe_id="probe_1",
        actual_value=1.0,
        predicted_value=1.0,
        tolerance=0.1,
    )

    results = service.list_attempts(student_id="alice")
    assert len(results) == 1
    assert results[0].student_id == "alice"


def test_list_attempts_no_filters_returns_all():
    service = _make_service()

    for i in range(3):
        service.submit_attempt(
            study_session_id=f"session-{i}",
            student_id="student-1",
            lesson_id="rl_intro",
            concept_id="td_update",
            probe_id="probe_1",
            actual_value=float(i),
            predicted_value=float(i) + 0.1,
            tolerance=0.5,
        )

    results = service.list_attempts()
    assert len(results) == 3


def test_mean_error_by_lesson_returns_correct_means():
    service = _make_service()

    # lesson A: errors 0.0 and 2.0 -> mean 1.0
    service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="lesson_a",
        concept_id="concept_x",
        probe_id="probe_1",
        actual_value=5.0,
        predicted_value=5.0,
        tolerance=0.5,
    )
    service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="lesson_a",
        concept_id="concept_x",
        probe_id="probe_2",
        actual_value=5.0,
        predicted_value=7.0,
        tolerance=0.5,
    )
    # lesson B: error 1.0 -> mean 1.0
    service.submit_attempt(
        study_session_id="session-1",
        student_id="student-1",
        lesson_id="lesson_b",
        concept_id="concept_y",
        probe_id="probe_3",
        actual_value=10.0,
        predicted_value=11.0,
        tolerance=0.5,
    )
    # different session — should NOT appear
    service.submit_attempt(
        study_session_id="session-2",
        student_id="student-1",
        lesson_id="lesson_a",
        concept_id="concept_x",
        probe_id="probe_1",
        actual_value=5.0,
        predicted_value=0.0,
        tolerance=0.5,
    )

    means = service.mean_error_by_lesson(study_session_id="session-1")

    assert set(means.keys()) == {"lesson_a", "lesson_b"}
    assert abs(means["lesson_a"] - 1.0) < 1e-9
    assert abs(means["lesson_b"] - 1.0) < 1e-9


def test_mean_error_by_lesson_empty_session_returns_empty_dict():
    service = _make_service()

    means = service.mean_error_by_lesson(study_session_id="nonexistent-session")

    assert means == {}
