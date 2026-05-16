from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class LearningInteractionEvent(SQLModel, table=True):
    __tablename__ = "learning_interaction_events"
    __table_args__ = (
        Index(
            "ix_learning_events_student_concept_time",
            "student_id",
            "concept_id",
            "occurred_at_utc",
        ),
        Index(
            "ix_learning_events_session_type",
            "session_id",
            "event_type",
        ),
    )

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    student_id: str = Field(index=True)
    lesson_id: str = Field(index=True)
    concept_id: Optional[str] = Field(default=None, index=True)
    session_id: str = Field(index=True)
    event_type: str = Field(index=True)
    payload_json: str = Field(default="{}")
    occurred_at_utc: datetime = Field(nullable=False)
    created_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    source_version: str = Field(default="study_buddy_v1")
