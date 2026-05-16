from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
import json
from threading import Lock
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator
from sqlmodel import select

from backend.config.trigger_config import TELEMETRY_SOURCE_VERSION
from backend.models.concept_mastery_snapshot import ConceptMasterySnapshot
from backend.models.learning_interaction_event import LearningInteractionEvent
from backend.models.study_buddy_intervention_record import StudyBuddyInterventionRecord
from backend.persistence import Database

_SCHEMA_MODELS = (
    ConceptMasterySnapshot,
    LearningInteractionEvent,
    StudyBuddyInterventionRecord,
)


class LearningInteractionEventCreate(BaseModel):
    student_id: str = Field(min_length=1)
    lesson_id: str = Field(min_length=1)
    concept_id: Optional[str] = None
    session_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    occurred_at_utc: datetime
    payload_json: dict[str, Any] = Field(default_factory=dict)
    source_version: str = Field(
        default=TELEMETRY_SOURCE_VERSION,
        min_length=1,
    )

    @field_validator(
        "student_id",
        "lesson_id",
        "concept_id",
        "session_id",
        "event_type",
        "source_version",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value: Any) -> Any:
        if value is None:
            return value
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @field_validator("occurred_at_utc")
    @classmethod
    def _normalize_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class MasteryEvidenceSummary(BaseModel):
    direct_evidence_count: int = Field(default=0, ge=0)
    last_direct_evidence_at_utc: str | None = None
    correct_checks: int = Field(default=0, ge=0)
    incorrect_checks: int = Field(default=0, ge=0)
    intervention_count: int = Field(default=0, ge=0)
    last_intervention_type: str | None = None
    passive_signal_count: int = Field(default=0, ge=0)


class TelemetryService:
    """Validates and persists append-only learning telemetry events."""

    def __init__(
        self,
        *,
        database: Optional[Database] = None,
        database_url: Optional[str] = None,
    ) -> None:
        self._lock = Lock()
        self._database = database or Database(database_url)
        self._database.create_schema()

    @property
    def database(self) -> Database:
        return self._database

    def record_events(self, events: Sequence[Mapping[str, Any]]) -> list[str]:
        validated = [LearningInteractionEventCreate.model_validate(dict(event)) for event in events]
        if not validated:
            return []

        with self._lock:
            with self._database.session() as session:
                records = [
                    LearningInteractionEvent(
                        student_id=event.student_id,
                        lesson_id=event.lesson_id,
                        concept_id=event.concept_id,
                        session_id=event.session_id,
                        event_type=event.event_type,
                        occurred_at_utc=event.occurred_at_utc,
                        payload_json=json.dumps(
                            event.payload_json,
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                        source_version=event.source_version,
                    )
                    for event in validated
                ]
                session.add_all(records)
                session.commit()
                return [record.id for record in records]

    def list_events(
        self,
        *,
        student_id: str | None = None,
        session_id: str | None = None,
    ) -> list[LearningInteractionEvent]:
        with self._lock:
            with self._database.session() as session:
                statement = select(LearningInteractionEvent)
                if student_id is not None:
                    statement = statement.where(LearningInteractionEvent.student_id == student_id)
                if session_id is not None:
                    statement = statement.where(LearningInteractionEvent.session_id == session_id)
                statement = statement.order_by(LearningInteractionEvent.occurred_at_utc)
                records = session.exec(statement).all()
                for record in records:
                    session.expunge(record)
                return list(records)

    def close(self) -> None:
        self._database.close()
