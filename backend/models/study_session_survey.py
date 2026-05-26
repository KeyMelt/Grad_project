from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class StudySessionSurvey(SQLModel, table=True):
    __tablename__ = "study_session_surveys"
    __table_args__ = (
        Index(
            "ix_study_session_surveys_session_id",
            "study_session_id",
            unique=True,
        ),
        Index(
            "ix_study_session_surveys_student_condition",
            "student_id",
            "condition",
        ),
    )

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    study_session_id: str = Field(index=True)
    student_id: str = Field(index=True)
    condition: str  # "adaptive" or "control"

    # SUS items (1–5 scale)
    # Odd items (positive): contribution = raw - 1
    # Even items (negative): contribution = 5 - raw
    sus_q1: int  # "I think that I would like to use this system frequently"
    sus_q2: int  # "I found the system unnecessarily complex"
    sus_q3: int  # "I thought the system was easy to use"
    sus_q4: int  # "I think I would need support of a technical person to use this system"
    sus_q5: int  # "I found the various functions in this system were well integrated"
    sus_q6: int  # "I thought there was too much inconsistency in this system"
    sus_q7: int  # "I would imagine most people would learn to use this system very quickly"
    sus_q8: int  # "I found the system very cumbersome to use"
    sus_q9: int  # "I felt very confident using the system"
    sus_q10: int  # "I needed to learn a lot of things before I could get going with this system"
    sus_score: float  # Brooke 1996: sum_of_contributions * 2.5, range 0–100

    # Raw NASA-TLX subscales (0–100)
    tlx_mental_demand: int   # Mental Demand
    tlx_physical_demand: int  # Physical Demand
    tlx_temporal_demand: int  # Temporal Demand
    tlx_performance: int      # Performance (how successful were you?)
    tlx_effort: int           # Effort
    tlx_frustration: int      # Frustration
    tlx_overall: float        # Mean of the 6 subscales

    # Open-ended feedback
    feedback_helpful: Optional[str] = Field(default=None)
    feedback_confusing: Optional[str] = Field(default=None)
    feedback_improvement: Optional[str] = Field(default=None)

    submitted_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    source_version: str = Field(default="study_buddy_v1")
