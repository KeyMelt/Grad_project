from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from sqlmodel import select

from backend.models.prediction_probe_attempt import PredictionProbeAttempt
from backend.persistence import Database


class PredictionProbeService:
    """Persists and queries prediction probe attempts."""

    def __init__(self, *, database: Database) -> None:
        self._lock = Lock()
        self._database = database
        self._database.create_schema()

    def submit_attempt(
        self,
        *,
        study_session_id: str,
        student_id: str,
        lesson_id: str,
        concept_id: str,
        probe_id: str,
        actual_value: float,
        predicted_value: float,
        tolerance: float,
    ) -> PredictionProbeAttempt:
        """
        Persists a probe attempt.
        - Computes absolute_error = abs(predicted_value - actual_value).
        - Computes is_within_tolerance = absolute_error <= tolerance.
        - Computes attempt_index by counting prior attempts for the same
          (study_session_id, probe_id) and adding 1.
        Returns the persisted record.
        """
        for name, value in (
            ("study_session_id", study_session_id),
            ("student_id", student_id),
            ("lesson_id", lesson_id),
            ("concept_id", concept_id),
            ("probe_id", probe_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        if tolerance < 0.0:
            raise ValueError("tolerance must be >= 0.0")

        absolute_error = abs(predicted_value - actual_value)
        is_within_tolerance = absolute_error <= tolerance

        with self._lock:
            with self._database.session() as session:
                prior_count_stmt = (
                    select(PredictionProbeAttempt)
                    .where(PredictionProbeAttempt.study_session_id == study_session_id)
                    .where(PredictionProbeAttempt.probe_id == probe_id)
                )
                prior_attempts = session.exec(prior_count_stmt).all()
                attempt_index = len(prior_attempts) + 1

                record = PredictionProbeAttempt(
                    study_session_id=study_session_id,
                    student_id=student_id,
                    lesson_id=lesson_id,
                    concept_id=concept_id,
                    probe_id=probe_id,
                    attempt_index=attempt_index,
                    actual_value=actual_value,
                    predicted_value=predicted_value,
                    absolute_error=absolute_error,
                    tolerance=tolerance,
                    is_within_tolerance=is_within_tolerance,
                    occurred_at_utc=datetime.now(timezone.utc),
                )
                session.add(record)
                session.commit()
                session.refresh(record)
                session.expunge(record)
                return record

    def list_attempts(
        self,
        *,
        study_session_id: str | None = None,
        student_id: str | None = None,
        lesson_id: str | None = None,
    ) -> list[PredictionProbeAttempt]:
        """Lists attempts matching the supplied filters, ordered by occurred_at_utc."""
        with self._lock:
            with self._database.session() as session:
                statement = select(PredictionProbeAttempt)
                if study_session_id is not None:
                    statement = statement.where(
                        PredictionProbeAttempt.study_session_id == study_session_id
                    )
                if student_id is not None:
                    statement = statement.where(
                        PredictionProbeAttempt.student_id == student_id
                    )
                if lesson_id is not None:
                    statement = statement.where(
                        PredictionProbeAttempt.lesson_id == lesson_id
                    )
                statement = statement.order_by(PredictionProbeAttempt.occurred_at_utc)
                records = session.exec(statement).all()
                for record in records:
                    session.expunge(record)
                return list(records)

    def mean_error_by_lesson(
        self,
        *,
        study_session_id: str,
    ) -> dict[str, float]:
        """
        Returns a dict mapping lesson_id -> mean absolute_error
        for all attempts in the given study_session_id.
        """
        attempts = self.list_attempts(study_session_id=study_session_id)
        errors_by_lesson: dict[str, list[float]] = {}
        for attempt in attempts:
            errors_by_lesson.setdefault(attempt.lesson_id, []).append(attempt.absolute_error)
        return {
            lesson_id: sum(errors) / len(errors)
            for lesson_id, errors in errors_by_lesson.items()
        }
