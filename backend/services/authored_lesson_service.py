from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from threading import Lock
from typing import Any

from sqlmodel import select

from backend.models.authored_lesson import AuthoredLesson
from backend.persistence import Database


class AuthoredLessonService:
    """Stores instructor-authored lesson content outside the code registry."""

    def __init__(self, *, database: Database) -> None:
        self._database = database
        self._lock = Lock()

    def list_lessons(self) -> list[dict[str, Any]]:
        with self._lock:
            with self._database.session() as session:
                rows = session.exec(
                    select(AuthoredLesson).order_by(
                        AuthoredLesson.category,
                        AuthoredLesson.title,
                    )
                ).all()
                return [self._decode_payload(row.payload_json) for row in rows]

    def upsert_lesson(
        self,
        *,
        lesson_id: str,
        payload: Mapping[str, Any],
        actor_user_id: str,
    ) -> dict[str, Any]:
        normalized = self._normalize_payload(lesson_id, payload)
        now = datetime.now(timezone.utc)
        with self._lock:
            with self._database.session() as session:
                row = session.get(AuthoredLesson, lesson_id)
                if row is None:
                    row = AuthoredLesson(
                        id=lesson_id,
                        title=normalized["title"],
                        category=normalized["category"],
                        description=normalized["description"],
                        payload_json=json.dumps(normalized, sort_keys=True),
                        created_by_user_id=actor_user_id,
                        updated_by_user_id=actor_user_id,
                        created_at_utc=now,
                        updated_at_utc=now,
                    )
                else:
                    row.title = normalized["title"]
                    row.category = normalized["category"]
                    row.description = normalized["description"]
                    row.payload_json = json.dumps(normalized, sort_keys=True)
                    row.updated_by_user_id = actor_user_id
                    row.updated_at_utc = now
                session.add(row)
                session.commit()
        return normalized

    def delete_lesson(self, lesson_id: str) -> bool:
        with self._lock:
            with self._database.session() as session:
                row = session.get(AuthoredLesson, lesson_id)
                if row is None:
                    return False
                session.delete(row)
                session.commit()
                return True

    def _normalize_payload(
        self,
        lesson_id: str,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        normalized = dict(payload)
        normalized["id"] = lesson_id
        normalized["backend_enabled"] = bool(normalized.get("backend_enabled", False))
        for key in ("title", "category", "description", "starter_code"):
            value = str(normalized.get(key) or "").strip()
            if not value:
                raise ValueError(f"Authored lesson requires '{key}'.")
            normalized[key] = value
        normalized.setdefault("concept_video", {})
        normalized.setdefault("exercise", {})
        if not isinstance(normalized["concept_video"], dict):
            raise ValueError("Authored lesson concept_video must be an object.")
        if not isinstance(normalized["exercise"], dict):
            raise ValueError("Authored lesson exercise must be an object.")
        return normalized

    def _decode_payload(self, raw_value: str) -> dict[str, Any]:
        try:
            decoded = json.loads(raw_value)
        except json.JSONDecodeError:
            return {}
        return decoded if isinstance(decoded, dict) else {}
