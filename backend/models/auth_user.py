from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class AuthUser(SQLModel, table=True):
    __tablename__ = "auth_users"

    id: str = Field(primary_key=True)
    firebase_uid: str | None = Field(default=None, index=True, unique=True)
    display_name: str = Field(default="Student", index=True)
    normalized_display_name: str = Field(default="", index=True)
    role: str = Field(default="student", index=True)
    status: str = Field(default="active", index=True)
    revocation_time: datetime | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
