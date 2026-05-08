from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.api_gateway.schemas import CodeSubmission
from backend.execution_runtime import ExecutionPipelineError


def build_execution_router(services: Any) -> APIRouter:
    router = APIRouter()

    @router.post("/submit")
    def submit_code(submission: CodeSubmission):
        return services.execution.submit(submission.model_dump())

    @router.get("/tasks/{task_id}")
    def get_task_status(task_id: str):
        snapshot = services.execution.snapshot(task_id)
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown task_id '{task_id}'.",
            )
        return snapshot

    @router.post("/execute")
    def execute_code(submission: CodeSubmission):
        try:
            return services.execution.execute_sync(submission.model_dump())
        except ExecutionPipelineError as error:
            raise HTTPException(
                status_code=error.status_code,
                detail=error.detail,
            ) from error

    return router
