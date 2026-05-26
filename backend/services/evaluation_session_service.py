from __future__ import annotations

import json
from datetime import datetime, timezone
from threading import Lock

from sqlmodel import select

from backend.models.study_session import StudySession
from backend.persistence import Database

_VALID_CONDITIONS = {"adaptive", "control"}


class EvaluationSessionService:
    """Creates and manages StudySession records for the evaluation framework."""

    def __init__(self, *, database: Database) -> None:
        self._lock = Lock()
        self._database = database
        self._database.create_schema()

    def create_session(
        self,
        *,
        student_id: str,
        condition: str,
        lesson_ids: list[str],
    ) -> StudySession:
        """Creates and persists a new StudySession. Returns the new record."""
        if condition not in _VALID_CONDITIONS:
            raise ValueError(
                f"Invalid condition {condition!r}. Must be one of: {sorted(_VALID_CONDITIONS)}"
            )
        if not lesson_ids:
            raise ValueError("lesson_ids must be a non-empty list.")

        record = StudySession(
            student_id=student_id,
            condition=condition,
            lesson_ids_json=json.dumps(lesson_ids),
            started_at_utc=datetime.now(timezone.utc),
        )

        with self._lock:
            with self._database.session() as session:
                session.add(record)
                session.commit()
                session.refresh(record)
                session.expunge(record)

        return record

    def get_session(self, session_id: str) -> StudySession | None:
        """Returns the StudySession by id, or None if not found."""
        with self._lock:
            with self._database.session() as session:
                record = session.get(StudySession, session_id)
                if record is not None:
                    session.expunge(record)
                return record

    def mark_pre_test_complete(self, session_id: str) -> None:
        """Sets pre_test_completed_at_utc = now."""
        with self._lock:
            with self._database.session() as session:
                record = session.get(StudySession, session_id)
                if record is not None:
                    record.pre_test_completed_at_utc = datetime.now(timezone.utc)
                    session.add(record)
                    session.commit()

    def mark_post_test_complete(self, session_id: str) -> None:
        """Sets post_test_completed_at_utc = now. Also sets ended_at_utc = now."""
        now = datetime.now(timezone.utc)
        with self._lock:
            with self._database.session() as session:
                record = session.get(StudySession, session_id)
                if record is not None:
                    record.post_test_completed_at_utc = now
                    record.ended_at_utc = now
                    session.add(record)
                    session.commit()

    def mark_survey_complete(self, session_id: str) -> None:
        """Sets survey_completed_at_utc = now."""
        with self._lock:
            with self._database.session() as session:
                record = session.get(StudySession, session_id)
                if record is not None:
                    record.survey_completed_at_utc = datetime.now(timezone.utc)
                    session.add(record)
                    session.commit()

    def list_sessions(
        self, *, student_id: str | None = None
    ) -> list[StudySession]:
        """Lists sessions, optionally filtered by student_id, ordered by started_at_utc."""
        with self._lock:
            with self._database.session() as session:
                statement = select(StudySession)
                if student_id is not None:
                    statement = statement.where(StudySession.student_id == student_id)
                statement = statement.order_by(StudySession.started_at_utc)
                records = session.exec(statement).all()
                for record in records:
                    session.expunge(record)
                return list(records)
