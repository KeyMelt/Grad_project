from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from typing import Any

from sqlmodel import select

from backend.config.trigger_config import TELEMETRY_SOURCE_VERSION
from backend.models.concept_mastery_snapshot import ConceptMasterySnapshot
from backend.models.learning_interaction_event import LearningInteractionEvent
from backend.models.study_buddy_intervention_record import StudyBuddyInterventionRecord
from backend.persistence import Database


@dataclass(frozen=True)
class MasteryEvidenceUpdate:
    direct_delta: float = 0.0
    support_delta: float = 0.0
    direct_correct: bool | None = None
    passive_signal: bool = False
    intervention_type: str | None = None
    occurred_at_utc: datetime | None = None


class MasteryTrackingService:
    """Maintains transparent concept-level learner-state snapshots."""

    def __init__(self, *, database: Database) -> None:
        self._database = database

    def record_event_evidence(
        self,
        session: Any,
        event: LearningInteractionEvent,
    ) -> ConceptMasterySnapshot | None:
        if event.concept_id is None:
            return None
        update = self._event_update(event)
        if update is None:
            return None
        return self._add_snapshot(
            session,
            student_id=event.student_id,
            lesson_id=event.lesson_id,
            concept_id=event.concept_id,
            update=update,
        )

    def record_intervention_evidence(
        self,
        session: Any,
        record: StudyBuddyInterventionRecord,
    ) -> ConceptMasterySnapshot | None:
        if record.concept_id is None:
            return None
        return self._add_snapshot(
            session,
            student_id=record.student_id,
            lesson_id=record.lesson_id,
            concept_id=record.concept_id,
            update=MasteryEvidenceUpdate(
                support_delta=0.05,
                passive_signal=True,
                intervention_type=record.intervention_type,
                occurred_at_utc=record.created_at_utc,
            ),
        )

    def record_intervention_response(
        self,
        session: Any,
        record: StudyBuddyInterventionRecord,
        *,
        response: str,
    ) -> ConceptMasterySnapshot | None:
        if record.concept_id is None:
            return None
        support_delta = -0.08 if response == "completed" else 0.02
        return self._add_snapshot(
            session,
            student_id=record.student_id,
            lesson_id=record.lesson_id,
            concept_id=record.concept_id,
            update=MasteryEvidenceUpdate(
                support_delta=support_delta,
                intervention_type=record.intervention_type,
                occurred_at_utc=record.resolved_at_utc,
            ),
        )

    def record_quiz_result(
        self,
        *,
        student_id: str,
        session_id: str,
        result: dict[str, Any],
    ) -> None:
        concept_results = result.get("concept_results")
        if not isinstance(concept_results, list):
            return

        with self._database.session() as session:
            for item in concept_results:
                if not isinstance(item, dict):
                    continue
                concept = str(item.get("concept") or "").strip()
                if not concept:
                    continue
                correct = bool(item.get("correct"))
                concept_id = self._concept_to_id(concept)
                occurred_at_utc = datetime.now(timezone.utc)
                session.add(
                    LearningInteractionEvent(
                        student_id=student_id,
                        lesson_id=str(item.get("lesson_id") or concept_id),
                        concept_id=concept_id,
                        session_id=session_id,
                        event_type="quiz_result",
                        occurred_at_utc=occurred_at_utc,
                        payload_json=json.dumps(
                            {
                                "phase": result.get("phase"),
                                "question_id": item.get("question_id"),
                                "concept": concept,
                                "correct": correct,
                            },
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                        source_version=TELEMETRY_SOURCE_VERSION,
                    )
                )
                self._add_snapshot(
                    session,
                    student_id=student_id,
                    lesson_id=concept_id,
                    concept_id=concept_id,
                    update=MasteryEvidenceUpdate(
                        direct_delta=0.14 if correct else -0.12,
                        support_delta=-0.06 if correct else 0.08,
                        direct_correct=correct,
                        occurred_at_utc=occurred_at_utc,
                    ),
                )
            session.commit()

    def latest_snapshots(self, student_id: str) -> list[dict[str, Any]]:
        with self._database.session() as session:
            return self.latest_snapshots_from_session(session, student_id)

    def latest_snapshots_from_session(
        self,
        session: Any,
        student_id: str,
    ) -> list[dict[str, Any]]:
        statement = (
            select(ConceptMasterySnapshot)
            .where(ConceptMasterySnapshot.student_id == student_id)
            .order_by(
                ConceptMasterySnapshot.concept_id, ConceptMasterySnapshot.recorded_at_utc.desc()
            )
        )
        latest_by_concept: dict[str, ConceptMasterySnapshot] = {}
        for snapshot in session.exec(statement).all():
            if snapshot.concept_id not in latest_by_concept:
                latest_by_concept[snapshot.concept_id] = snapshot

        return [
            self.serialize_snapshot(snapshot)
            for snapshot in sorted(
                latest_by_concept.values(),
                key=lambda item: item.concept_id,
            )
        ]

    def learning_timeline(self, student_id: str, *, limit: int = 100) -> list[dict[str, Any]]:
        with self._database.session() as session:
            event_rows = session.exec(
                select(LearningInteractionEvent)
                .where(LearningInteractionEvent.student_id == student_id)
                .order_by(LearningInteractionEvent.occurred_at_utc.desc())
                .limit(limit)
            ).all()
            intervention_rows = session.exec(
                select(StudyBuddyInterventionRecord)
                .where(StudyBuddyInterventionRecord.student_id == student_id)
                .order_by(StudyBuddyInterventionRecord.created_at_utc.desc())
                .limit(limit)
            ).all()
            mastery_rows = session.exec(
                select(ConceptMasterySnapshot)
                .where(ConceptMasterySnapshot.student_id == student_id)
                .order_by(ConceptMasterySnapshot.recorded_at_utc.desc())
                .limit(limit)
            ).all()

            items: list[dict[str, Any]] = []
            items.extend(self._serialize_event(event) for event in event_rows)
            items.extend(self._serialize_intervention(record) for record in intervention_rows)
            items.extend(
                self._serialize_mastery_timeline_item(snapshot) for snapshot in mastery_rows
            )
            items.sort(key=lambda item: item["occurred_at_utc"], reverse=True)
            return items[:limit]

    def recent_interventions(self, student_id: str, *, limit: int = 5) -> list[dict[str, Any]]:
        with self._database.session() as session:
            rows = session.exec(
                select(StudyBuddyInterventionRecord)
                .where(StudyBuddyInterventionRecord.student_id == student_id)
                .order_by(StudyBuddyInterventionRecord.created_at_utc.desc())
                .limit(limit)
            ).all()
            return [self._serialize_intervention(record) for record in rows]

    def serialize_snapshot(self, snapshot: ConceptMasterySnapshot) -> dict[str, Any]:
        return {
            "id": snapshot.id,
            "student_id": snapshot.student_id,
            "lesson_id": snapshot.lesson_id,
            "concept_id": snapshot.concept_id,
            "mastery_score": snapshot.mastery_score,
            "support_need_score": snapshot.support_need_score,
            "confidence_score": snapshot.confidence_score,
            "staleness_days": snapshot.staleness_days,
            "evidence_summary": self._decode_summary(snapshot.evidence_summary_json),
            "recorded_at_utc": snapshot.recorded_at_utc.isoformat(),
            "source_version": snapshot.source_version,
        }

    def _add_snapshot(
        self,
        session: Any,
        *,
        student_id: str,
        lesson_id: str,
        concept_id: str,
        update: MasteryEvidenceUpdate,
    ) -> ConceptMasterySnapshot:
        previous = self._latest_snapshot(session, student_id, concept_id)
        summary = self._decode_summary(
            previous.evidence_summary_json if previous is not None else "{}"
        )
        occurred_at_utc = update.occurred_at_utc or datetime.now(timezone.utc)

        if update.direct_correct is not None:
            summary["direct_evidence_count"] += 1
            summary["last_direct_evidence_at_utc"] = occurred_at_utc.isoformat()
            if update.direct_correct:
                summary["correct_checks"] += 1
            else:
                summary["incorrect_checks"] += 1
        if update.passive_signal:
            summary["passive_signal_count"] += 1
        if update.intervention_type is not None:
            summary["intervention_count"] += 1
            summary["last_intervention_type"] = update.intervention_type

        mastery_score = self._clamp(
            (previous.mastery_score if previous is not None else 0.50) + update.direct_delta
        )
        support_need_score = self._clamp(
            (previous.support_need_score if previous is not None else 0.00) + update.support_delta
        )
        confidence_score = self._clamp(0.10 + (summary["direct_evidence_count"] * 0.12))
        staleness_days = self._staleness_days(summary.get("last_direct_evidence_at_utc"))

        snapshot = ConceptMasterySnapshot(
            student_id=student_id,
            lesson_id=lesson_id,
            concept_id=concept_id,
            mastery_score=round(mastery_score, 3),
            support_need_score=round(support_need_score, 3),
            confidence_score=round(confidence_score, 3),
            staleness_days=staleness_days,
            evidence_summary_json=json.dumps(
                summary,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        session.add(snapshot)
        return snapshot

    def _event_update(
        self,
        event: LearningInteractionEvent,
    ) -> MasteryEvidenceUpdate | None:
        payload = self._decode_json(event.payload_json)
        if event.event_type == "submission_result":
            passed = bool(payload.get("passed"))
            return MasteryEvidenceUpdate(
                direct_delta=0.12 if passed else -0.10,
                support_delta=-0.10 if passed else 0.12,
                direct_correct=passed,
                occurred_at_utc=event.occurred_at_utc,
            )
        if event.event_type == "code_run_result":
            passed = bool(payload.get("passed"))
            return MasteryEvidenceUpdate(
                direct_delta=0.06 if passed else -0.04,
                support_delta=-0.04 if passed else 0.06,
                direct_correct=passed,
                occurred_at_utc=event.occurred_at_utc,
            )
        if event.event_type == "micro_checkpoint_result":
            correct = bool(payload.get("correct") or payload.get("passed"))
            return MasteryEvidenceUpdate(
                direct_delta=0.14 if correct else -0.12,
                support_delta=-0.08 if correct else 0.10,
                direct_correct=correct,
                occurred_at_utc=event.occurred_at_utc,
            )
        if event.event_type == "quiz_result":
            correct = bool(payload.get("correct"))
            return MasteryEvidenceUpdate(
                direct_delta=0.14 if correct else -0.12,
                support_delta=-0.06 if correct else 0.08,
                direct_correct=correct,
                occurred_at_utc=event.occurred_at_utc,
            )
        if event.event_type == "concept_video_session":
            replay_count = int(payload.get("replay_count") or 0)
            seek_back_count = int(payload.get("seek_back_count") or 0)
            completion_ratio = float(payload.get("completion_ratio") or 0)
            if replay_count >= 2 or seek_back_count >= 3 or completion_ratio < 0.35:
                return MasteryEvidenceUpdate(
                    support_delta=0.08,
                    passive_signal=True,
                    occurred_at_utc=event.occurred_at_utc,
                )
        if event.event_type == "workspace_focus_session":
            duration_seconds = float(payload.get("duration_seconds") or 0)
            if duration_seconds >= 300:
                return MasteryEvidenceUpdate(
                    support_delta=0.05,
                    passive_signal=True,
                    occurred_at_utc=event.occurred_at_utc,
                )
        if event.event_type == "study_buddy_intervention_response":
            completed = payload.get("response") == "completed"
            return MasteryEvidenceUpdate(
                support_delta=-0.08 if completed else 0.02,
                occurred_at_utc=event.occurred_at_utc,
            )
        return None

    def _latest_snapshot(
        self,
        session: Any,
        student_id: str,
        concept_id: str,
    ) -> ConceptMasterySnapshot | None:
        return session.exec(
            select(ConceptMasterySnapshot)
            .where(ConceptMasterySnapshot.student_id == student_id)
            .where(ConceptMasterySnapshot.concept_id == concept_id)
            .order_by(ConceptMasterySnapshot.recorded_at_utc.desc())
        ).first()

    def _serialize_event(self, event: LearningInteractionEvent) -> dict[str, Any]:
        return {
            "item_type": "event",
            "id": event.id,
            "student_id": event.student_id,
            "lesson_id": event.lesson_id,
            "concept_id": event.concept_id,
            "session_id": event.session_id,
            "event_type": event.event_type,
            "payload": self._decode_json(event.payload_json),
            "occurred_at_utc": event.occurred_at_utc.isoformat(),
            "source_version": event.source_version,
        }

    def _serialize_intervention(
        self,
        record: StudyBuddyInterventionRecord,
    ) -> dict[str, Any]:
        return {
            "item_type": "intervention",
            "id": record.id,
            "student_id": record.student_id,
            "lesson_id": record.lesson_id,
            "concept_id": record.concept_id,
            "session_id": record.session_id,
            "trigger_type": record.trigger_type,
            "intervention_type": record.intervention_type,
            "status": record.status,
            "prompt_version": record.prompt_version,
            "reflection_pass_result": record.reflection_pass_result,
            "occurred_at_utc": record.created_at_utc.isoformat(),
            "resolved_at_utc": (
                record.resolved_at_utc.isoformat() if record.resolved_at_utc is not None else None
            ),
        }

    def _serialize_mastery_timeline_item(
        self,
        snapshot: ConceptMasterySnapshot,
    ) -> dict[str, Any]:
        return {
            "item_type": "mastery_snapshot",
            "id": snapshot.id,
            "student_id": snapshot.student_id,
            "lesson_id": snapshot.lesson_id,
            "concept_id": snapshot.concept_id,
            "mastery_score": snapshot.mastery_score,
            "support_need_score": snapshot.support_need_score,
            "confidence_score": snapshot.confidence_score,
            "staleness_days": snapshot.staleness_days,
            "occurred_at_utc": snapshot.recorded_at_utc.isoformat(),
            "source_version": snapshot.source_version,
        }

    def _decode_summary(self, raw_value: str) -> dict[str, Any]:
        summary = {
            "direct_evidence_count": 0,
            "last_direct_evidence_at_utc": None,
            "correct_checks": 0,
            "incorrect_checks": 0,
            "intervention_count": 0,
            "last_intervention_type": None,
            "passive_signal_count": 0,
        }
        decoded = self._decode_json(raw_value)
        for key in summary:
            if key in decoded:
                summary[key] = decoded[key]
        return summary

    def _decode_json(self, raw_value: str) -> dict[str, Any]:
        try:
            decoded = json.loads(raw_value or "{}")
        except json.JSONDecodeError:
            return {}
        return decoded if isinstance(decoded, dict) else {}

    def _staleness_days(self, raw_timestamp: str | None) -> int:
        if not raw_timestamp:
            return 0
        try:
            last_direct = datetime.fromisoformat(raw_timestamp)
        except ValueError:
            return 0
        if last_direct.tzinfo is None:
            last_direct = last_direct.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - last_direct.astimezone(timezone.utc)
        return max(delta.days, 0)

    def _concept_to_id(self, concept: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", concept.casefold()).strip("_")
        return slug or "unknown_concept"

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))
