from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class QuizQuestion(SQLModel, table=True):
    """Persisted quiz question.

    The options array and the correct answer are stored as JSON so the schema
    remains stable when questions are added or options are reordered.
    """

    id: str = Field(primary_key=True)
    concept: str = Field(index=True)
    prompt: str
    options_json: str
    correct_index: int
    created_by_user_id: str = Field(default="system")
    created_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
