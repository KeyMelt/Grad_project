from __future__ import annotations

from threading import Lock

from sqlmodel import select

from backend.models.study_session_survey import StudySessionSurvey
from backend.persistence import Database

_VALID_CONDITIONS = frozenset({"adaptive", "control"})


class StudySessionSurveyService:
    """Persists and queries SUS + Raw NASA-TLX survey responses."""

    def __init__(self, *, database: Database) -> None:
        self._lock = Lock()
        self._database = database
        self._database.create_schema()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_sus(
        q1: int,
        q2: int,
        q3: int,
        q4: int,
        q5: int,
        q6: int,
        q7: int,
        q8: int,
        q9: int,
        q10: int,
    ) -> float:
        """Brooke 1996 SUS formula.

        Odd items (positive phrasing): contribution = raw - 1
        Even items (negative phrasing): contribution = 5 - raw
        sus_score = sum_of_all_contributions * 2.5  (range 0–100)
        """
        odd_sum = (q1 - 1) + (q3 - 1) + (q5 - 1) + (q7 - 1) + (q9 - 1)
        even_sum = (5 - q2) + (5 - q4) + (5 - q6) + (5 - q8) + (5 - q10)
        return (odd_sum + even_sum) * 2.5

    @staticmethod
    def _compute_tlx_overall(
        mental_demand: int,
        physical_demand: int,
        temporal_demand: int,
        performance: int,
        effort: int,
        frustration: int,
    ) -> float:
        """Raw NASA-TLX overall score: arithmetic mean of the 6 subscales."""
        return (
            mental_demand
            + physical_demand
            + temporal_demand
            + performance
            + effort
            + frustration
        ) / 6.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit_survey(
        self,
        *,
        study_session_id: str,
        student_id: str,
        condition: str,
        sus_q1: int,
        sus_q2: int,
        sus_q3: int,
        sus_q4: int,
        sus_q5: int,
        sus_q6: int,
        sus_q7: int,
        sus_q8: int,
        sus_q9: int,
        sus_q10: int,
        tlx_mental_demand: int,
        tlx_physical_demand: int,
        tlx_temporal_demand: int,
        tlx_performance: int,
        tlx_effort: int,
        tlx_frustration: int,
        feedback_helpful: str | None = None,
        feedback_confusing: str | None = None,
        feedback_improvement: str | None = None,
    ) -> StudySessionSurvey:
        """Compute sus_score and tlx_overall, validate, and persist the survey.

        Raises ValueError if any SUS item is outside 1–5.
        Raises ValueError if any TLX subscale is outside 0–100.
        Raises ValueError if condition is not 'adaptive' or 'control'.
        Returns the persisted record.
        """
        if condition not in _VALID_CONDITIONS:
            raise ValueError(
                f"condition must be one of {sorted(_VALID_CONDITIONS)!r}, got {condition!r}"
            )

        sus_items = {
            "sus_q1": sus_q1,
            "sus_q2": sus_q2,
            "sus_q3": sus_q3,
            "sus_q4": sus_q4,
            "sus_q5": sus_q5,
            "sus_q6": sus_q6,
            "sus_q7": sus_q7,
            "sus_q8": sus_q8,
            "sus_q9": sus_q9,
            "sus_q10": sus_q10,
        }
        for name, value in sus_items.items():
            if not (1 <= value <= 5):
                raise ValueError(
                    f"{name} must be between 1 and 5 inclusive, got {value}"
                )

        tlx_items = {
            "tlx_mental_demand": tlx_mental_demand,
            "tlx_physical_demand": tlx_physical_demand,
            "tlx_temporal_demand": tlx_temporal_demand,
            "tlx_performance": tlx_performance,
            "tlx_effort": tlx_effort,
            "tlx_frustration": tlx_frustration,
        }
        for name, value in tlx_items.items():
            if not (0 <= value <= 100):
                raise ValueError(
                    f"{name} must be between 0 and 100 inclusive, got {value}"
                )

        sus_score = self._compute_sus(
            sus_q1, sus_q2, sus_q3, sus_q4, sus_q5,
            sus_q6, sus_q7, sus_q8, sus_q9, sus_q10,
        )
        tlx_overall = self._compute_tlx_overall(
            tlx_mental_demand,
            tlx_physical_demand,
            tlx_temporal_demand,
            tlx_performance,
            tlx_effort,
            tlx_frustration,
        )

        record = StudySessionSurvey(
            study_session_id=study_session_id,
            student_id=student_id,
            condition=condition,
            sus_q1=sus_q1,
            sus_q2=sus_q2,
            sus_q3=sus_q3,
            sus_q4=sus_q4,
            sus_q5=sus_q5,
            sus_q6=sus_q6,
            sus_q7=sus_q7,
            sus_q8=sus_q8,
            sus_q9=sus_q9,
            sus_q10=sus_q10,
            sus_score=sus_score,
            tlx_mental_demand=tlx_mental_demand,
            tlx_physical_demand=tlx_physical_demand,
            tlx_temporal_demand=tlx_temporal_demand,
            tlx_performance=tlx_performance,
            tlx_effort=tlx_effort,
            tlx_frustration=tlx_frustration,
            tlx_overall=tlx_overall,
            feedback_helpful=feedback_helpful,
            feedback_confusing=feedback_confusing,
            feedback_improvement=feedback_improvement,
        )

        with self._lock:
            with self._database.session() as session:
                session.add(record)
                session.commit()
                session.refresh(record)
                session.expunge(record)

        return record

    def get_survey(self, study_session_id: str) -> StudySessionSurvey | None:
        """Return the survey for the given session, or None if not found."""
        with self._lock:
            with self._database.session() as session:
                statement = select(StudySessionSurvey).where(
                    StudySessionSurvey.study_session_id == study_session_id
                )
                record = session.exec(statement).first()
                if record is not None:
                    session.expunge(record)
                return record

    def list_surveys(
        self,
        *,
        student_id: str | None = None,
        condition: str | None = None,
    ) -> list[StudySessionSurvey]:
        """List surveys, optionally filtered by student_id and/or condition,
        ordered by submitted_at_utc ascending.
        """
        with self._lock:
            with self._database.session() as session:
                statement = select(StudySessionSurvey)
                if student_id is not None:
                    statement = statement.where(
                        StudySessionSurvey.student_id == student_id
                    )
                if condition is not None:
                    statement = statement.where(
                        StudySessionSurvey.condition == condition
                    )
                statement = statement.order_by(StudySessionSurvey.submitted_at_utc)
                records = session.exec(statement).all()
                for record in records:
                    session.expunge(record)
                return list(records)
