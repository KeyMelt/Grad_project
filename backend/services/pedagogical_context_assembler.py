from __future__ import annotations

from datetime import datetime
import hashlib
import json
from typing import Any

from pydantic import BaseModel, Field
from sqlmodel import Session, select

from backend.lessons import get_lesson_definition
from backend.models.concept_mastery_snapshot import ConceptMasterySnapshot
from backend.models.learning_interaction_event import LearningInteractionEvent
from backend.models.study_buddy_intervention_record import StudyBuddyInterventionRecord
from backend.services.intervention_coordinator import InterventionDecision


class RecentFailurePattern(BaseModel):
    event_type: str
    failure_kind: str | None = None
    passed: bool | None = None
    occurred_at_utc: str


class LearnerStateContext(BaseModel):
    mastery_score: float = 0.50
    support_need_score: float = 0.0
    confidence_score: float = 0.10
    staleness_days: int = 0


class SessionInterventionContext(BaseModel):
    intervention_type: str
    status: str
    created_at_utc: str


class PedagogicalPromptContext(BaseModel):
    student_id: str
    lesson_id: str
    concept_id: str | None
    lesson_title: str
    lesson_description: str
    concept_prompts: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    recent_failures: list[RecentFailurePattern] = Field(default_factory=list)
    learner_state: LearnerStateContext = Field(default_factory=LearnerStateContext)
    session_interventions: list[SessionInterventionContext] = Field(default_factory=list)
    trigger_type: str
    trigger_score: float
    intervention_type: str
    escalated: bool

    def stable_hash(self) -> str:
        raw = json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class PedagogicalContextAssembler:
    def assemble(
        self,
        session: Session,
        decision: InterventionDecision,
    ) -> PedagogicalPromptContext:
        trigger = decision.trigger
        lesson = get_lesson_definition(trigger.lesson_id)
        concept_prompts: list[str] = []
        success_criteria: list[str] = []
        title = trigger.lesson_id
        description = ""
        if lesson is not None:
            title = lesson.title
            description = lesson.description
            concept_prompts = [
                f"{blank.expected_concept}: {blank.prompt}" for blank in lesson.template_blanks
            ]
            success_criteria = list(lesson.success_criteria)

        return PedagogicalPromptContext(
            student_id=trigger.student_id,
            lesson_id=trigger.lesson_id,
            concept_id=trigger.concept_id,
            lesson_title=title,
            lesson_description=description,
            concept_prompts=concept_prompts,
            success_criteria=success_criteria,
            recent_failures=self._recent_failures(session, trigger),
            learner_state=self._learner_state(session, trigger),
            session_interventions=self._session_interventions(session, trigger),
            trigger_type=trigger.trigger_type,
            trigger_score=trigger.trigger_score,
            intervention_type=decision.intervention_type,
            escalated=decision.escalated,
        )

    def _recent_failures(
        self,
        session: Session,
        trigger: Any,
    ) -> list[RecentFailurePattern]:
        statement = (
            select(LearningInteractionEvent)
            .where(LearningInteractionEvent.student_id == trigger.student_id)
            .where(LearningInteractionEvent.lesson_id == trigger.lesson_id)
            .where(
                LearningInteractionEvent.event_type.in_(["submission_result", "code_run_result"])
            )
            .order_by(LearningInteractionEvent.occurred_at_utc.desc())
            .limit(6)
        )
        events = []
        for event in session.exec(statement).all():
            payload = _decode_payload(event.payload_json)
            if payload.get("passed") is True:
                continue
            events.append(
                RecentFailurePattern(
                    event_type=event.event_type,
                    failure_kind=payload.get("failure_kind"),
                    passed=payload.get("passed"),
                    occurred_at_utc=_iso(event.occurred_at_utc),
                )
            )
        return events

    def _learner_state(
        self,
        session: Session,
        trigger: Any,
    ) -> LearnerStateContext:
        if trigger.concept_id is None:
            return LearnerStateContext()
        statement = (
            select(ConceptMasterySnapshot)
            .where(ConceptMasterySnapshot.student_id == trigger.student_id)
            .where(ConceptMasterySnapshot.concept_id == trigger.concept_id)
            .order_by(ConceptMasterySnapshot.recorded_at_utc.desc())
        )
        snapshot = session.exec(statement).first()
        if snapshot is None:
            return LearnerStateContext()
        return LearnerStateContext(
            mastery_score=snapshot.mastery_score,
            support_need_score=snapshot.support_need_score,
            confidence_score=snapshot.confidence_score,
            staleness_days=snapshot.staleness_days,
        )

    def _session_interventions(
        self,
        session: Session,
        trigger: Any,
    ) -> list[SessionInterventionContext]:
        statement = (
            select(StudyBuddyInterventionRecord)
            .where(StudyBuddyInterventionRecord.session_id == trigger.session_id)
            .order_by(StudyBuddyInterventionRecord.created_at_utc)
        )
        return [
            SessionInterventionContext(
                intervention_type=record.intervention_type,
                status=record.status,
                created_at_utc=_iso(record.created_at_utc),
            )
            for record in session.exec(statement).all()
        ]


def _decode_payload(raw_payload: str) -> dict:
    try:
        decoded = json.loads(raw_payload or "{}")
    except json.JSONDecodeError:
        return {}
    return decoded if isinstance(decoded, dict) else {}


def _iso(value: datetime) -> str:
    return value.isoformat()
