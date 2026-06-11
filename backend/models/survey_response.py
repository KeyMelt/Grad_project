from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class SurveyResponse(SQLModel, table=True):
    __tablename__ = "survey_responses"
    __table_args__ = (
        Index(
            "ix_survey_responses_session_template",
            "study_session_id",
            "survey_template_id",
        ),
        Index(
            "ix_survey_responses_student_condition",
            "student_id",
            "condition",
        ),
    )

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    survey_template_id: str = Field(index=True)
    survey_version: int
    study_session_id: str = Field(index=True)
    student_id: str = Field(index=True)
    condition: str
    submitted_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    source_version: str = Field(default="study_buddy_v1")


class SurveyItemResponse(SQLModel, table=True):
    __tablename__ = "survey_item_responses"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    survey_response_id: str = Field(index=True)
    item_id: str = Field(index=True)
    likert_value: Optional[int] = Field(default=None)
    text_value: Optional[str] = Field(default=None)
