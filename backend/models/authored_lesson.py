from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class AuthoredLesson(SQLModel, table=True):
    """Persisted instructor-authored lesson metadata.

    These records make lesson studio edits deployable without changing the
    source-code lesson registry.
    """

    id: str = Field(primary_key=True)
    title: str
    category: str = Field(index=True)
    description: str
    payload_json: str
    created_by_user_id: str = Field(index=True)
    updated_by_user_id: str = Field(index=True)
    created_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
