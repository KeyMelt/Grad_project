from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class PredictionProbeAttempt(SQLModel, table=True):
    __tablename__ = "prediction_probe_attempts"
    __table_args__ = (
        Index(
            "ix_prediction_probe_attempts_session_probe_attempt",
            "study_session_id",
            "probe_id",
            "attempt_index",
        ),
        Index(
            "ix_prediction_probe_attempts_student_lesson_occurred",
            "student_id",
            "lesson_id",
            "occurred_at_utc",
        ),
    )

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    study_session_id: str = Field(index=True)
    student_id: str = Field(index=True)
    lesson_id: str = Field(index=True)
    concept_id: str = Field(index=True)
    probe_id: str
    attempt_index: int
    actual_value: float
    predicted_value: float
    absolute_error: float
    tolerance: float
    is_within_tolerance: bool
    occurred_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    source_version: str = Field(default="study_buddy_v1")
