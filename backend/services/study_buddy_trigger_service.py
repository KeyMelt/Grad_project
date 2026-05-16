from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json

from sqlmodel import Session, select

from backend.config import trigger_config
from backend.models.learning_interaction_event import LearningInteractionEvent


@dataclass(frozen=True)
class StudyBuddyTrigger:
    trigger_type: str
    trigger_score: float
    student_id: str
    lesson_id: str
    concept_id: str | None
    session_id: str
    source_event_type: str


class StudyBuddyTriggerService:
    """Deterministic struggle trigger rules backed by bounded event windows."""

    def evaluate_event(
        self,
        session: Session,
        event: LearningInteractionEvent,
    ) -> list[StudyBuddyTrigger]:
        payload = _decode_payload(event.payload_json)
        triggers: list[StudyBuddyTrigger] = []

        if event.event_type == "concept_video_session":
            trigger = self._evaluate_video_loop(session, event, payload)
            if trigger is not None:
                triggers.append(trigger)

        if event.event_type == "submission_result":
            trigger = self._evaluate_submission_failure_streak(session, event)
            if trigger is not None:
                triggers.append(trigger)

        if event.event_type == "workspace_focus_session":
            trigger = self._evaluate_editor_stall(session, event, payload)
            if trigger is not None:
                triggers.append(trigger)

        if event.event_type in {"quiz_result", "micro_checkpoint_result"}:
            trigger = self._evaluate_quiz_gap(session, event)
            if trigger is not None:
                triggers.append(trigger)

        return triggers

    def _evaluate_video_loop(
        self,
        session: Session,
        event: LearningInteractionEvent,
        payload: dict,
    ) -> StudyBuddyTrigger | None:
        replay_count = int(payload.get("replay_count") or 0)
        seek_back_count = int(payload.get("seek_back_count") or 0)
        if (
            replay_count < trigger_config.VIDEO_LOOP_REPLAY_THRESHOLD
            and seek_back_count < trigger_config.VIDEO_LOOP_SEEK_BACK_THRESHOLD
        ):
            return None

        if self._has_recent_success(
            session,
            event,
            window_seconds=trigger_config.VIDEO_LOOP_WINDOW_SECONDS,
        ):
            return None

        replay_score = replay_count / trigger_config.VIDEO_LOOP_REPLAY_THRESHOLD
        seek_score = seek_back_count / trigger_config.VIDEO_LOOP_SEEK_BACK_THRESHOLD
        return _trigger(
            event,
            "video_loop_confusion",
            min(max(replay_score, seek_score), 2.0),
        )

    def _evaluate_submission_failure_streak(
        self,
        session: Session,
        event: LearningInteractionEvent,
    ) -> StudyBuddyTrigger | None:
        failures = [
            candidate
            for candidate in self._window_events(
                session,
                event,
                event_types={"submission_result"},
                window_seconds=trigger_config.SUBMISSION_FAILURE_WINDOW_SECONDS,
            )
            if _decode_payload(candidate.payload_json).get("passed") is False
        ]
        if len(failures) < trigger_config.SUBMISSION_FAILURE_THRESHOLD:
            return None
        return _trigger(
            event,
            "submission_failure_streak",
            len(failures) / trigger_config.SUBMISSION_FAILURE_THRESHOLD,
        )

    def _evaluate_editor_stall(
        self,
        session: Session,
        event: LearningInteractionEvent,
        payload: dict,
    ) -> StudyBuddyTrigger | None:
        if payload.get("view_id") != "code":
            return None
        duration_seconds = float(payload.get("duration_seconds") or 0)
        if duration_seconds < trigger_config.EDITOR_STALL_WINDOW_SECONDS:
            return None
        if self._has_recent_success(
            session,
            event,
            window_seconds=trigger_config.EDITOR_STALL_WINDOW_SECONDS,
        ):
            return None
        return _trigger(
            event,
            "editor_stall",
            min(duration_seconds / trigger_config.EDITOR_STALL_WINDOW_SECONDS, 2.0),
        )

    def _evaluate_quiz_gap(
        self,
        session: Session,
        event: LearningInteractionEvent,
    ) -> StudyBuddyTrigger | None:
        checks = self._window_events(
            session,
            event,
            event_types={"quiz_result", "micro_checkpoint_result"},
            window_seconds=24 * 60 * 60,
        )
        direct = [
            _decode_payload(candidate.payload_json)
            for candidate in checks
            if "correct" in _decode_payload(candidate.payload_json)
        ]
        if len(direct) < trigger_config.QUIZ_GAP_MIN_DIRECT_CHECKS:
            return None
        correct = sum(1 for payload in direct if payload.get("correct") is True)
        accuracy = correct / len(direct)
        if accuracy >= trigger_config.QUIZ_GAP_ACCURACY_THRESHOLD:
            return None
        return _trigger(event, "quiz_gap", 1.0 - accuracy)

    def _has_recent_success(
        self,
        session: Session,
        event: LearningInteractionEvent,
        *,
        window_seconds: int,
    ) -> bool:
        return any(
            _decode_payload(candidate.payload_json).get("passed") is True
            for candidate in self._window_events(
                session,
                event,
                event_types={"code_run_result", "submission_result"},
                window_seconds=window_seconds,
            )
        )

    def _window_events(
        self,
        session: Session,
        event: LearningInteractionEvent,
        *,
        event_types: set[str],
        window_seconds: int,
    ) -> list[LearningInteractionEvent]:
        occurred_at = _as_utc(event.occurred_at_utc)
        lower_bound = occurred_at - timedelta(seconds=window_seconds)
        statement = (
            select(LearningInteractionEvent)
            .where(LearningInteractionEvent.student_id == event.student_id)
            .where(LearningInteractionEvent.lesson_id == event.lesson_id)
            .where(LearningInteractionEvent.occurred_at_utc >= lower_bound)
            .where(LearningInteractionEvent.occurred_at_utc <= occurred_at)
            .where(LearningInteractionEvent.event_type.in_(event_types))
        )
        if event.concept_id is not None:
            statement = statement.where(LearningInteractionEvent.concept_id == event.concept_id)
        return list(session.exec(statement).all())


def _trigger(
    event: LearningInteractionEvent,
    trigger_type: str,
    score: float,
) -> StudyBuddyTrigger:
    return StudyBuddyTrigger(
        trigger_type=trigger_type,
        trigger_score=round(score, 3),
        student_id=event.student_id,
        lesson_id=event.lesson_id,
        concept_id=event.concept_id,
        session_id=event.session_id,
        source_event_type=event.event_type,
    )


def _decode_payload(raw_payload: str) -> dict:
    try:
        decoded = json.loads(raw_payload or "{}")
    except json.JSONDecodeError:
        return {}
    return decoded if isinstance(decoded, dict) else {}


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
