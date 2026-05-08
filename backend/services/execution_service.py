import threading
from typing import Optional
from typing import Any

from backend.execution_runtime import ExecutionPipelineError, run_submission_with_timeout
from backend.job_store import ExecutionJobStore
from backend.artifact_store_sqlite import SqliteArtifactStore
from backend.services.student_progress_service import StudentProgressService


class ExecutionService:
    """Service boundary for async job submission, tracking, and execution."""

    def __init__(
        self,
        job_store: Optional[ExecutionJobStore] = None,
        artifact_store: Optional[SqliteArtifactStore] = None,
        progress_service: Optional[StudentProgressService] = None,
    ):
        self.job_store = job_store or ExecutionJobStore()
        self.artifact_store = artifact_store
        self.progress_service = progress_service

    def submit(self, submission_payload: dict[str, Any]) -> dict[str, str]:
        job = self.job_store.create()
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
        if self.artifact_store is not None:
            artifacts = self.artifact_store.list_for_task(task_id)
            if artifacts:
                snapshot["artifacts"] = artifacts
        return snapshot

    def execute_sync(self, submission_payload: dict[str, Any]) -> dict[str, Any]:
        try:
            result = run_submission_with_timeout(submission_payload)
        except ExecutionPipelineError as error:
            self._record_submission_outcome(
                submission_payload,
                passed=False,
                failure_kind=(
                    error.detail.get("failure_kind") if isinstance(error.detail, dict) else None
                ),
            )
            raise

        self._record_submission_outcome(submission_payload, passed=True)
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

    def close(self) -> None:
        if self.progress_service is None:
            return
        close = getattr(self.progress_service, "close", None)
        if callable(close):
            close()
