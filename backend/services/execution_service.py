import threading
from typing import Optional
from typing import Any

from backend.execution_runtime import ExecutionPipelineError, run_submission_with_timeout
from backend.job_store import ExecutionJobStore
from backend.services.student_progress_service import StudentProgressService


class ExecutionService:
    """Service boundary for async job submission, tracking, and execution."""

    def __init__(
        self,
        job_store: Optional[ExecutionJobStore] = None,
        progress_service: Optional[StudentProgressService] = None,
    ):
        self.job_store = job_store or ExecutionJobStore()
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
        return self.job_store.snapshot(task_id)

    def execute_sync(self, submission_payload: dict[str, Any]) -> dict[str, Any]:
        result = run_submission_with_timeout(submission_payload)
        self._record_success(submission_payload)
        return result

    def _execute_async_job(self, task_id: str, submission_payload: dict[str, Any]) -> None:
        self.job_store.mark_running(task_id)
        try:
            result = self.execute_sync(submission_payload)
            self.job_store.mark_succeeded(task_id, result)
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

    def _record_success(self, submission_payload: dict[str, Any]) -> None:
        if self.progress_service is None:
            return

        student_id = submission_payload.get("student_id")
        lesson_id = submission_payload.get("lesson_id")
        if not student_id or not lesson_id:
            return

        self.progress_service.record_lesson_completion(student_id, lesson_id)

    def close(self) -> None:
        if self.progress_service is None:
            return
        close = getattr(self.progress_service, "close", None)
        if callable(close):
            close()
