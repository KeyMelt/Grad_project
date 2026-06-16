from datetime import datetime, timezone
import threading
from typing import Any, Optional
from uuid import uuid4

from backend.config.trigger_config import TELEMETRY_SOURCE_VERSION
from backend.execution_runtime import ExecutionPipelineError, run_submission_with_timeout
from backend.job_store import ExecutionJobStore
from backend.artifact_store_sqlite import SqliteArtifactStore
from backend.services.firebase_progress_service import FirebaseProgressService
from backend.services.replay_status_service import enrich_snapshot_with_replay
from backend.services.telemetry_service import TelemetryService


class ExecutionService:
    """Service boundary for async job submission, tracking, and execution."""

    def __init__(
        self,
        job_store: ExecutionJobStore | None = None,
        artifact_store: SqliteArtifactStore | None = None,
        progress_service: FirebaseProgressService | None = None,
        telemetry_service: TelemetryService | None = None,
    ):
        self.job_store = job_store or ExecutionJobStore()
        self.artifact_store = artifact_store
        self.progress_service = progress_service
        self.telemetry_service = telemetry_service

    def submit(self, submission_payload: dict[str, Any]) -> dict[str, str]:
        owner_user_id = str(submission_payload.get("owner_user_id") or "anonymous")
        owner_role = str(submission_payload.get("owner_role") or "student")
        job = self.job_store.create(
            owner_user_id=owner_user_id,
            owner_role=owner_role,
        )
        thread = threading.Thread(
            target=self._execute_async_job,
            args=(job.task_id, submission_payload),
            daemon=True,
        )
        thread.start()
        return {"task_id": job.task_id, "status": job.status}

    def snapshot(self, task_id: str) -> Optional[dict[str, Any]]:
        snapshot = self.job_store.snapshot(task_id)
        if snapshot is None:
            return None
        snapshot = enrich_snapshot_with_replay(snapshot)
        if self.artifact_store is not None:
            artifacts = self.artifact_store.list_for_task(task_id)
            if artifacts:
                snapshot["artifacts"] = artifacts
        return snapshot

    def execute_sync(self, submission_payload: dict[str, Any]) -> dict[str, Any]:
        try:
            result = run_submission_with_timeout(submission_payload)
        except ExecutionPipelineError as error:
            failure_kind = (
                error.detail.get("failure_kind") if isinstance(error.detail, dict) else None
            )
            self._record_submission_outcome(
                submission_payload,
                passed=False,
                failure_kind=failure_kind,
            )
            self._record_submission_telemetry(
                submission_payload,
                passed=False,
                failure_kind=failure_kind,
            )
            raise

        self._record_submission_outcome(submission_payload, passed=True)
        self._record_submission_telemetry(submission_payload, passed=True)
        self._record_success(submission_payload)
        return result

    def _execute_async_job(self, task_id: str, submission_payload: dict[str, Any]) -> None:
        self.job_store.mark_running(task_id)
        try:
            result = self.execute_sync(submission_payload)
            self.job_store.mark_succeeded(task_id, result)
            self._record_artifacts(task_id, result)
        except ExecutionPipelineError as error:
            self.job_store.mark_failed(task_id, error.detail)
        except Exception as error:  # pragma: no cover - fallback guard
            self.job_store.mark_failed(
                task_id,
                {
                    "message": "Unhandled execution failure.",
                    "issues": [str(error)],
                },
            )

    def _record_artifacts(self, task_id: str, result: dict[str, Any]) -> None:
        if self.artifact_store is None:
            return

        video_path = result.get("video_path")
        if video_path:
            self.artifact_store.record(
                task_id=task_id,
                artifact_kind="replay_video",
                artifact_path=str(video_path),
            )

    def _record_success(self, submission_payload: dict[str, Any]) -> None:
        if self.progress_service is None:
            return

        student_id = submission_payload.get("student_id")
        lesson_id = submission_payload.get("lesson_id")
        if not student_id or not lesson_id:
            return

        self.progress_service.record_lesson_completion(student_id, lesson_id)

    def _record_submission_outcome(
        self,
        submission_payload: dict[str, Any],
        *,
        passed: bool,
        failure_kind: str | None = None,
    ) -> None:
        if self.progress_service is None:
            return

        student_id = submission_payload.get("student_id")
        if not student_id:
            return

        record_submission_outcome = getattr(
            self.progress_service,
            "record_submission_outcome",
            None,
        )
        if callable(record_submission_outcome):
            record_submission_outcome(
                student_id,
                passed=passed,
                failure_kind=failure_kind,
            )

    def _record_submission_telemetry(
        self,
        submission_payload: dict[str, Any],
        *,
        passed: bool,
        failure_kind: str | None = None,
    ) -> None:
        if self.telemetry_service is None:
            return

        student_id = submission_payload.get("student_id")
        lesson_id = submission_payload.get("lesson_id")
        if not student_id or not lesson_id:
            return

        session_id = (
            submission_payload.get("session_id")
            or submission_payload.get("workspace_session_id")
            or f"submission-{uuid4().hex}"
        )
        self.telemetry_service.record_events(
            [
                {
                    "student_id": student_id,
                    "lesson_id": lesson_id,
                    "concept_id": submission_payload.get("concept_id") or lesson_id,
                    "session_id": session_id,
                    "event_type": "submission_result",
                    "occurred_at_utc": datetime.now(timezone.utc),
                    "payload_json": {
                        "passed": passed,
                        "failure_kind": failure_kind,
                        "origin": "backend_execution_service",
                    },
                    "source_version": TELEMETRY_SOURCE_VERSION,
                }
            ]
        )

    def close(self) -> None:
        if self.progress_service is None:
            return
        close = getattr(self.progress_service, "close", None)
        if callable(close):
            close()
