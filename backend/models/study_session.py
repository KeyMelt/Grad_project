from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class StudySession(SQLModel, table=True):
    __tablename__ = "study_sessions"
    __table_args__ = (
        Index(
            "ix_study_sessions_student_condition_started",
            "student_id",
            "condition",
            "started_at_utc",
        ),
    )

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    student_id: str = Field(index=True)
    condition: str = Field(index=True)
    lesson_ids_json: str = Field(default="[]")
    started_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    pre_test_completed_at_utc: Optional[datetime] = Field(default=None)
    post_test_completed_at_utc: Optional[datetime] = Field(default=None)
    survey_completed_at_utc: Optional[datetime] = Field(default=None)
    ended_at_utc: Optional[datetime] = Field(default=None)
    source_version: str = Field(default="study_buddy_v1")
