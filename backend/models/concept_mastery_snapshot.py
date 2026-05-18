from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class ConceptMasterySnapshot(SQLModel, table=True):
    __tablename__ = "concept_mastery_snapshots"
    __table_args__ = (
        Index(
            "ix_concept_mastery_student_concept_recorded",
            "student_id",
            "concept_id",
            "recorded_at_utc",
        ),
    )

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    student_id: str = Field(index=True)
    lesson_id: str = Field(index=True)
    concept_id: str = Field(index=True)
    mastery_score: float = Field(default=0.50)
    support_need_score: float = Field(default=0.0)
    confidence_score: float = Field(default=0.10)
    staleness_days: int = Field(default=0)
    evidence_summary_json: str = Field(default="{}")
    recorded_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    source_version: str = Field(default="study_buddy_v1")
