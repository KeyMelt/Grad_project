from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class StudentProgressRecord(SQLModel, table=True):
    __tablename__ = "student_progress"

    id: str = Field(primary_key=True)
    display_name: str = Field(index=True)
    normalized_name: str = Field(index=True, unique=True)
    password_hash: str = Field(default="")
    password_salt: str = Field(default="")

    completed_lesson_ids_json: str = Field(default="[]")
    successful_runs: int = Field(default=0)
    latest_lesson_id: Optional[str] = Field(default=None)

    pretest_score: Optional[float] = Field(default=None)
    posttest_score: Optional[float] = Field(default=None)
    n_gain: Optional[float] = Field(default=None)

    quiz_attempts_pretest: int = Field(default=0)
    quiz_attempts_posttest: int = Field(default=0)
    question_history_json: str = Field(default="[]")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
