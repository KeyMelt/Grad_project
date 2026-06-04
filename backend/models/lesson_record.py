from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class LessonRecord(SQLModel, table=True):
    """Persisted lesson metadata for every lesson in the platform."""

    __tablename__ = "authoredlesson"

    id: str = Field(primary_key=True)
    title: str
    category: str = Field(index=True)
    description: str
    payload_json: str
    created_by_user_id: str = Field(index=True)
    updated_by_user_id: str = Field(index=True)
    created_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
