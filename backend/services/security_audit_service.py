from __future__ import annotations

from datetime import datetime, timezone
import json
from threading import Lock
from typing import Any

from backend.models.security_audit_log import SecurityAuditLog
from backend.persistence import Database


class SecurityAuditService:
    def __init__(self, *, database: Database) -> None:
        self._database = database
        self._lock = Lock()
        self._database.create_schema()

    def record(
        self,
        *,
        actor_user_id: str,
        action: str,
        resource_type: str,
        outcome: str,
        target_user_id: str | None = None,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        with self._lock:
            with self._database.session() as session:
                session.add(
                    SecurityAuditLog(
                        actor_user_id=actor_user_id,
                        target_user_id=target_user_id,
                        action=action,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        outcome=outcome,
                        metadata_json=json.dumps(
                            metadata or {},
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                        occurred_at_utc=datetime.now(timezone.utc),
                    )
                )
                session.commit()
