from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Sequence

from sqlmodel import select

from backend.lessons import get_lesson_definition
from backend.models.learning_interaction_event import LearningInteractionEvent
from backend.models.study_buddy_intervention_record import StudyBuddyInterventionRecord
from backend.persistence import Database
from backend.services.intervention_coordinator import InterventionCoordinator
from backend.services.intervention_reflection_service import InterventionReflectionService
from backend.services.mastery_tracking_service import MasteryTrackingService
from backend.services.pedagogical_context_assembler import PedagogicalContextAssembler
from backend.services.pedagogical_llm_service import (
    PedagogicalChatContext,
    PedagogicalChatMessage,
    PedagogicalLLMService,
)
from backend.services.spaced_review_scheduler import SpacedReviewScheduler
from backend.services.study_buddy_trigger_service import StudyBuddyTriggerService
from backend.services.telemetry_service import TelemetryService


class StudyBuddyService:
    def __init__(
        self,
        *,
        telemetry_service: TelemetryService,
        database: Database,
        trigger_service: StudyBuddyTriggerService | None = None,
        coordinator: InterventionCoordinator | None = None,
        context_assembler: PedagogicalContextAssembler | None = None,
        llm_service: PedagogicalLLMService | None = None,
        reflection_service: InterventionReflectionService | None = None,
        mastery_service: MasteryTrackingService | None = None,
        review_scheduler: SpacedReviewScheduler | None = None,
    ) -> None:
        self.telemetry_service = telemetry_service
        self._database = database
        self.trigger_service = trigger_service or StudyBuddyTriggerService()
        self.coordinator = coordinator or InterventionCoordinator()
        self.context_assembler = context_assembler or PedagogicalContextAssembler()
        self.llm_service = llm_service or PedagogicalLLMService()
        self.reflection_service = reflection_service or InterventionReflectionService()
        self.mastery_service = mastery_service or MasteryTrackingService(database=database)
        self.review_scheduler = review_scheduler or SpacedReviewScheduler()
        self._database.create_schema()

    def ingest_events(self, events: Sequence[dict[str, Any]]) -> list[str]:
        event_ids = self.telemetry_service.record_events(events)
        if not event_ids:
            return []

        with self._database.session() as session:
            records = [
                record
                for record in (
                    session.get(LearningInteractionEvent, event_id) for event_id in event_ids
                )
                if record is not None
            ]
            for record in records:
                self._process_single_event(session, record)
            session.commit()
        return event_ids

    def _process_single_event(self, session: Any, record: LearningInteractionEvent) -> None:
        self.mastery_service.record_event_evidence(session, record)
        triggers = self.trigger_service.evaluate_event(session, record)
        decision = self.coordinator.select(session, triggers)
        if decision is None:
            return
        intervention_record = self._generate_intervention(session, decision)
        session.add(intervention_record)
        self.mastery_service.record_intervention_evidence(session, intervention_record)

    def _generate_intervention(self, session: Any, decision: Any) -> StudyBuddyInterventionRecord:
        context = self.context_assembler.assemble(session, decision)
        raw_intervention, metadata = self.llm_service.generate(context)
        fallback = self.llm_service.fallback_intervention(context)
        reflection = self.reflection_service.reflect(
            intervention=raw_intervention,
            fallback=fallback,
            lesson_id=decision.trigger.lesson_id,
        )
        response_payload = reflection.intervention.model_dump(mode="json")
        response_payload["observability"] = {
            **metadata,
            "reflection_note": reflection.note,
        }
        return StudyBuddyInterventionRecord(
            student_id=decision.trigger.student_id,
            lesson_id=decision.trigger.lesson_id,
            concept_id=decision.trigger.concept_id,
            session_id=decision.trigger.session_id,
            trigger_type=decision.trigger.trigger_type,
            trigger_score=decision.trigger.trigger_score,
            intervention_type=reflection.intervention.intervention_type,
            status="ready",
            llm_model=metadata.get("model"),
            prompt_version=metadata.get("prompt_version", "deterministic_v1"),
            context_hash=context.stable_hash(),
            response_json=json.dumps(
                response_payload,
                sort_keys=True,
                separators=(",", ":"),
            ),
            reflection_pass_result=reflection.pass_result,
        )

    def pending_intervention(self, session_id: str) -> dict | None:
        with self._database.session() as session:
            statement = (
                select(StudyBuddyInterventionRecord)
                .where(StudyBuddyInterventionRecord.session_id == session_id)
                .where(StudyBuddyInterventionRecord.status == "ready")
                .order_by(StudyBuddyInterventionRecord.created_at_utc)
            )
            record = session.exec(statement).first()
            if record is None:
                return None
            return self._serialize_intervention(record)

    def get_intervention(self, intervention_id: str) -> dict | None:
        with self._database.session() as session:
            record = session.get(StudyBuddyInterventionRecord, intervention_id)
            if record is None:
                return None
            return self._serialize_intervention(record)

    def respond_to_intervention(
        self,
        intervention_id: str,
        *,
        response: str,
    ) -> dict | None:
        with self._database.session() as session:
            record = session.get(StudyBuddyInterventionRecord, intervention_id)
            if record is None:
                return None
            record.status = response if response in {"completed", "dismissed"} else "completed"
            record.resolved_at_utc = datetime.now(timezone.utc)
            session.add(record)
            self.mastery_service.record_intervention_response(
                session,
                record,
                response=record.status,
            )
            session.commit()
            session.refresh(record)
            return self._serialize_intervention(record)

    def chat(
        self,
        *,
        student_id: str,
        lesson_id: str,
        session_id: str,
        message: str,
        history: Sequence[dict[str, Any]] = (),
        current_code: str | None = None,
        unresolved_blanks: Sequence[str] = (),
        failure_kind: str | None = None,
        latest_feedback: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_message = message.strip()
        if not normalized_message:
            raise ValueError("Study Buddy chat message cannot be empty.")

        with self._database.session() as session:
            context = self._assemble_chat_context(
                session,
                student_id=student_id,
                lesson_id=lesson_id,
                session_id=session_id,
                message=normalized_message,
                history=history,
                current_code=current_code,
                unresolved_blanks=unresolved_blanks,
                failure_kind=failure_kind,
                latest_feedback=latest_feedback or {},
            )

        reply, metadata = self.llm_service.generate_chat(context)
        self._record_chat_telemetry(
            student_id=student_id,
            lesson_id=lesson_id,
            session_id=session_id,
            message=normalized_message,
            reply=reply.reply,
            metadata=metadata,
        )

        safe_metadata = {
            key: value
            for key, value in metadata.items()
            if key in {"model", "prompt_version", "latency_ms", "used_fallback", "error"}
        }
        return {
            "message": {
                "role": "assistant",
                "content": reply.reply,
            },
            "reply": reply.reply,
            "suggested_next_step": reply.suggested_next_step,
            "concept_ids": reply.concept_ids,
            "solution_leakage_risk": reply.solution_leakage_risk,
            "used_fallback": bool(metadata.get("used_fallback", False)),
            "observability": safe_metadata,
        }

    def record_quiz_result(
        self,
        *,
        student_id: str,
        session_id: str,
        result: dict[str, Any],
    ) -> None:
        self.mastery_service.record_quiz_result(
            student_id=student_id,
            session_id=session_id,
            result=result,
        )

    def learning_timeline(self, student_id: str, *, limit: int = 100) -> dict:
        bounded_limit = max(1, min(limit, 250))
        return {
            "student_id": student_id,
            "items": self.mastery_service.learning_timeline(
                student_id,
                limit=bounded_limit,
            ),
        }

    def summary(self, student_id: str) -> dict:
        snapshots = self.mastery_service.latest_snapshots(student_id)
        return {
            "student_id": student_id,
            "mastery_snapshots": snapshots,
            "review_recommendation": self.review_scheduler.select(snapshots),
            "recent_interventions": self.mastery_service.recent_interventions(
                student_id,
                limit=5,
            ),
        }

    def _serialize_intervention(self, record: StudyBuddyInterventionRecord) -> dict:
        return {
            "id": record.id,
            "student_id": record.student_id,
            "lesson_id": record.lesson_id,
            "concept_id": record.concept_id,
            "session_id": record.session_id,
            "trigger_type": record.trigger_type,
            "trigger_score": record.trigger_score,
            "intervention_type": record.intervention_type,
            "status": record.status,
            "prompt_version": record.prompt_version,
            "reflection_pass_result": record.reflection_pass_result,
            "created_at_utc": record.created_at_utc.isoformat(),
            "resolved_at_utc": (
                record.resolved_at_utc.isoformat() if record.resolved_at_utc is not None else None
            ),
            "response": json.loads(record.response_json or "{}"),
        }

    def _assemble_chat_context(
        self,
        session: Any,
        *,
        student_id: str,
        lesson_id: str,
        session_id: str,
        message: str,
        history: Sequence[dict[str, Any]],
        current_code: str | None,
        unresolved_blanks: Sequence[str],
        failure_kind: str | None,
        latest_feedback: dict[str, Any],
    ) -> PedagogicalChatContext:
        lesson = get_lesson_definition(lesson_id)
        lesson_title = lesson_id
        lesson_description = ""
        concept_prompts: list[str] = []
        success_criteria: list[str] = []
        if lesson is not None:
            lesson_title = lesson.title
            lesson_description = lesson.description
            concept_prompts = [
                f"{blank.expected_concept}: {blank.prompt}" for blank in lesson.template_blanks
            ]
            success_criteria = list(lesson.success_criteria)

        return PedagogicalChatContext(
            student_id=student_id,
            lesson_id=lesson_id,
            session_id=session_id,
            lesson_title=lesson_title,
            lesson_description=lesson_description,
            concept_prompts=concept_prompts,
            success_criteria=success_criteria,
            unresolved_blanks=list(unresolved_blanks)[:20],
            failure_kind=failure_kind,
            latest_feedback=latest_feedback,
            current_code_excerpt=_code_excerpt(current_code),
            recent_failures=self._recent_chat_failures(
                session,
                student_id=student_id,
                lesson_id=lesson_id,
            ),
            recent_interventions=self._recent_chat_interventions(
                session,
                student_id=student_id,
                session_id=session_id,
            ),
            history=[
                PedagogicalChatMessage.model_validate(item)
                for item in list(history)[-12:]
                if item.get("content")
            ],
            message=message,
        )

    def _recent_chat_failures(
        self,
        session: Any,
        *,
        student_id: str,
        lesson_id: str,
    ) -> list[dict[str, Any]]:
        statement = (
            select(LearningInteractionEvent)
            .where(LearningInteractionEvent.student_id == student_id)
            .where(LearningInteractionEvent.lesson_id == lesson_id)
            .where(
                LearningInteractionEvent.event_type.in_(["submission_result", "code_run_result"])
            )
            .order_by(LearningInteractionEvent.occurred_at_utc.desc())
            .limit(5)
        )
        failures: list[dict[str, Any]] = []
        for event in session.exec(statement).all():
            payload = _decode_payload(event.payload_json)
            if payload.get("passed") is True:
                continue
            failures.append(
                {
                    "event_type": event.event_type,
                    "failure_kind": payload.get("failure_kind"),
                    "message": payload.get("message"),
                    "occurred_at_utc": event.occurred_at_utc.isoformat(),
                }
            )
        return failures

    def _recent_chat_interventions(
        self,
        session: Any,
        *,
        student_id: str,
        session_id: str,
    ) -> list[dict[str, Any]]:
        statement = (
            select(StudyBuddyInterventionRecord)
            .where(StudyBuddyInterventionRecord.student_id == student_id)
            .where(StudyBuddyInterventionRecord.session_id == session_id)
            .order_by(StudyBuddyInterventionRecord.created_at_utc.desc())
            .limit(3)
        )
        return [
            {
                "intervention_type": record.intervention_type,
                "trigger_type": record.trigger_type,
                "status": record.status,
                "created_at_utc": record.created_at_utc.isoformat(),
            }
            for record in session.exec(statement).all()
        ]

    def _record_chat_telemetry(
        self,
        *,
        student_id: str,
        lesson_id: str,
        session_id: str,
        message: str,
        reply: str,
        metadata: dict[str, Any],
    ) -> None:
        now = datetime.now(timezone.utc)
        self.telemetry_service.record_events(
            [
                {
                    "student_id": student_id,
                    "lesson_id": lesson_id,
                    "concept_id": lesson_id,
                    "session_id": session_id,
                    "event_type": "study_buddy_chat_message",
                    "occurred_at_utc": now,
                    "payload_json": {
                        "role": "user",
                        "message_length": len(message),
                    },
                    "source_version": "study_buddy_chat_v1",
                },
                {
                    "student_id": student_id,
                    "lesson_id": lesson_id,
                    "concept_id": lesson_id,
                    "session_id": session_id,
                    "event_type": "study_buddy_chat_reply",
                    "occurred_at_utc": now,
                    "payload_json": {
                        "reply_length": len(reply),
                        "used_fallback": bool(metadata.get("used_fallback", False)),
                        "prompt_version": metadata.get("prompt_version"),
                        "model": metadata.get("model"),
                        "error": metadata.get("error"),
                    },
                    "source_version": "study_buddy_chat_v1",
                },
            ]
        )


def _decode_payload(raw_payload: str) -> dict[str, Any]:
    try:
        decoded = json.loads(raw_payload or "{}")
    except json.JSONDecodeError:
        return {}
    return decoded if isinstance(decoded, dict) else {}


def _code_excerpt(current_code: str | None, *, max_chars: int = 6000) -> str | None:
    if current_code is None:
        return None
    stripped = current_code.strip()
    if not stripped:
        return None
    if len(stripped) <= max_chars:
        return stripped
    return stripped[-max_chars:]
