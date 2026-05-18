from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class StudyBuddyInterventionRecord(SQLModel, table=True):
    __tablename__ = "study_buddy_interventions"
    __table_args__ = (
        Index(
            "ix_study_buddy_interventions_student_concept_created",
            "student_id",
            "concept_id",
            "created_at_utc",
        ),
        Index(
            "ix_study_buddy_interventions_session_status",
            "session_id",
            "status",
        ),
    )

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    student_id: str = Field(index=True)
    lesson_id: str = Field(index=True)
    concept_id: Optional[str] = Field(default=None, index=True)
    session_id: str = Field(index=True)
    trigger_type: str = Field(index=True)
    trigger_score: float = Field(default=0.0)
    intervention_type: str = Field(index=True)
    status: str = Field(default="pending", index=True)
    llm_model: Optional[str] = Field(default=None)
    prompt_version: str = Field(default="deterministic_v1")
    context_hash: str = Field(default="")
    response_json: str = Field(default="{}")
    reflection_pass_result: str = Field(default="fallback_substituted")
    created_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at_utc: Optional[datetime] = Field(default=None)
    source_version: str = Field(default="study_buddy_v1")
