from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Header, HTTPException

from backend.execution_runtime import ExecutionPipelineError
from backend.execution_worker.schemas import CodeSubmission


def build_jobs_router(
    services: Any,
    assert_internal_access: Callable[[str | None], None],
) -> APIRouter:
    router = APIRouter()

    @router.post("/internal/jobs")
    def submit(
        submission: CodeSubmission,
        x_internal_token: str | None = Header(default=None),
    ):
        assert_internal_access(x_internal_token)
        return services.execution.submit(submission.model_dump())

    @router.get("/internal/jobs/{task_id}")
    def snapshot(
        task_id: str,
        x_internal_token: str | None = Header(default=None),
    ):
        assert_internal_access(x_internal_token)
        result = services.execution.snapshot(task_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Unknown task_id '{task_id}'.")
        return result

    @router.post("/internal/execute")
    def execute_sync(
        submission: CodeSubmission,
        x_internal_token: str | None = Header(default=None),
    ):
        assert_internal_access(x_internal_token)
        try:
            return services.execution.execute_sync(submission.model_dump())
        except ExecutionPipelineError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    return router
