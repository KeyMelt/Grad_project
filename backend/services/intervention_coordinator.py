from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from backend.config import trigger_config
from backend.models.concept_mastery_snapshot import ConceptMasterySnapshot
from backend.models.study_buddy_intervention_record import StudyBuddyInterventionRecord
from backend.services.study_buddy_trigger_service import StudyBuddyTrigger


@dataclass(frozen=True)
class InterventionDecision:
    trigger: StudyBuddyTrigger
    intervention_type: str
    escalated: bool = False


class InterventionCoordinator:
    priority_order = {
        "submission_failure_streak": 4,
        "quiz_gap": 3,
        "video_loop_confusion": 2,
        "editor_stall": 1,
    }

    def select(
        self,
        session: Session,
        triggers: list[StudyBuddyTrigger],
    ) -> InterventionDecision | None:
        for trigger in sorted(
            triggers,
            key=lambda item: (
                self.priority_order.get(item.trigger_type, 0),
                item.trigger_score,
            ),
            reverse=True,
        ):
            decision = self._decision_for_trigger(session, trigger)
            if decision is not None:
                return decision
        return None

    def _decision_for_trigger(
        self,
        session: Session,
        trigger: StudyBuddyTrigger,
    ) -> InterventionDecision | None:
        if self._has_cooldown_match(session, trigger):
            return None

        confidence = self._latest_confidence(session, trigger)
        base_type = self._base_intervention_type(trigger.trigger_type)
        if confidence < 0.30:
            base_type = self._checkpoint_type(trigger.trigger_type)

        session_types = self._session_intervention_types(session, trigger)
        escalated_type = self._escalate(base_type, session_types)
        return InterventionDecision(
            trigger=trigger,
            intervention_type=escalated_type,
            escalated=escalated_type != base_type,
        )

    def _has_cooldown_match(
        self,
        session: Session,
        trigger: StudyBuddyTrigger,
    ) -> bool:
        lower_bound = datetime.now(timezone.utc) - timedelta(
            seconds=self._cooldown_seconds(trigger.trigger_type)
        )
        statement = (
            select(StudyBuddyInterventionRecord)
            .where(StudyBuddyInterventionRecord.student_id == trigger.student_id)
            .where(StudyBuddyInterventionRecord.lesson_id == trigger.lesson_id)
            .where(StudyBuddyInterventionRecord.trigger_type == trigger.trigger_type)
            .where(StudyBuddyInterventionRecord.created_at_utc >= lower_bound)
            .where(StudyBuddyInterventionRecord.status.in_(["pending", "ready"]))
        )
        if trigger.concept_id is not None:
            statement = statement.where(
                StudyBuddyInterventionRecord.concept_id == trigger.concept_id
            )
        return session.exec(statement).first() is not None

    def _cooldown_seconds(self, trigger_type: str) -> int:
        if trigger_type == "submission_failure_streak":
            return trigger_config.SUBMISSION_FAILURE_INTERVENTION_COOLDOWN_SECONDS
        return trigger_config.INTERVENTION_COOLDOWN_SECONDS

    def _latest_confidence(
        self,
        session: Session,
        trigger: StudyBuddyTrigger,
    ) -> float:
        if trigger.concept_id is None:
            return 0.10
        statement = (
            select(ConceptMasterySnapshot)
            .where(ConceptMasterySnapshot.student_id == trigger.student_id)
            .where(ConceptMasterySnapshot.concept_id == trigger.concept_id)
            .order_by(ConceptMasterySnapshot.recorded_at_utc.desc())
        )
        snapshot = session.exec(statement).first()
        return snapshot.confidence_score if snapshot is not None else 0.10

    def _session_intervention_types(
        self,
        session: Session,
        trigger: StudyBuddyTrigger,
    ) -> list[str]:
        statement = (
            select(StudyBuddyInterventionRecord)
            .where(StudyBuddyInterventionRecord.session_id == trigger.session_id)
            .order_by(StudyBuddyInterventionRecord.created_at_utc)
        )
        if trigger.concept_id is not None:
            statement = statement.where(
                StudyBuddyInterventionRecord.concept_id == trigger.concept_id
            )
        return [record.intervention_type for record in session.exec(statement).all()]

    def _base_intervention_type(self, trigger_type: str) -> str:
        return {
            "video_loop_confusion": "clarify_concept",
            "submission_failure_streak": "mini_example",
            "editor_stall": "next_step_prompt",
            "quiz_gap": "replay_recommendation",
        }.get(trigger_type, "clarify_concept")

    def _checkpoint_type(self, trigger_type: str) -> str:
        if trigger_type in {"submission_failure_streak", "editor_stall"}:
            return "code_completion_checkpoint"
        return "mcq_checkpoint"

    def _escalate(self, base_type: str, session_types: list[str]) -> str:
        if base_type == "clarify_concept" and "clarify_concept" in session_types:
            return "mini_example"
        if base_type == "mini_example" and "mini_example" in session_types:
            return "mcq_checkpoint"
        if (
            "clarify_concept" in session_types
            and "mini_example" in session_types
            and base_type in {"clarify_concept", "mini_example"}
        ):
            return "code_completion_checkpoint"
        return base_type
