from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Flashcard(SQLModel, table=True):
    """Vocabulary flashcard served to the Flutter client.

    Content is seeded from the built-in catalog on first startup.
    Admin-created cards use a different created_by_user_id so they survive
    across restarts without being overwritten.
    """

    id: str = Field(primary_key=True)
    term: str
    category: str = Field(index=True)
    explanation: str
    sort_order: int = Field(default=0, index=True)
    created_by_user_id: str = Field(default="system")
    created_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
