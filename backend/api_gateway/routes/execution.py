from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.auth.dependencies import (
    assert_owner_or_admin,
    build_current_principal_dependency,
    require_roles,
)
from backend.auth.roles import PlatformRole, Principal
from backend.api_gateway.schemas import CodeSubmission
from backend.execution_runtime import ExecutionPipelineError


def build_execution_router(services: Any) -> APIRouter:
    router = APIRouter()
    current_principal = build_current_principal_dependency(
        auth_service=services.auth,
        audit_service=getattr(services, "audit", None),
    )
    submit_principal = require_roles(
        current_principal,
        PlatformRole.STUDENT,
        PlatformRole.INSTRUCTOR,
        PlatformRole.ADMIN,
    )
    admin_principal = require_roles(current_principal, PlatformRole.ADMIN)

    @router.post("/submit")
    def submit_code(
        submission: CodeSubmission,
        principal: Principal = Depends(submit_principal),
    ):
        payload = submission.model_dump()
        payload["student_id"] = principal.id
        payload["owner_user_id"] = principal.id
        payload["owner_role"] = principal.role.value
        return services.execution.submit(payload)

    @router.get("/tasks/{task_id}")
    def get_task_status(
        task_id: str,
        principal: Principal = Depends(current_principal),
    ):
        snapshot = services.execution.snapshot(task_id)
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown task_id '{task_id}'.",
            )
        owner_user_id = str(snapshot.get("owner_user_id") or "")
        assert_owner_or_admin(principal=principal, owner_user_id=owner_user_id)
        return snapshot

    @router.post("/execute")
    def execute_code(
        submission: CodeSubmission,
        principal: Principal = Depends(admin_principal),
    ):
        try:
            payload = submission.model_dump()
            payload["student_id"] = principal.id
            payload["owner_user_id"] = principal.id
            payload["owner_role"] = principal.role.value
            return services.execution.execute_sync(payload)
        except ExecutionPipelineError as error:
            raise HTTPException(
                status_code=error.status_code,
                detail=error.detail,
            ) from error

    return router
