from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Field, SQLModel


class SecurityAuditLog(SQLModel, table=True):
    __tablename__ = "security_audit_logs"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    actor_user_id: str = Field(index=True)
    target_user_id: str | None = Field(default=None, index=True)
    action: str = Field(index=True)
    resource_type: str = Field(index=True)
    resource_id: str | None = Field(default=None, index=True)
    outcome: str = Field(index=True)
    metadata_json: str = Field(default="{}")
    occurred_at_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
