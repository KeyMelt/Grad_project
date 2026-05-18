from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.auth.dependencies import build_current_principal_dependency, require_roles
from backend.auth.roles import PlatformRole, Principal
from backend.api_gateway.schemas import (
    AuthRoleUpdateRequest,
    AuthStatusUpdateRequest,
    StudentSignInRequest,
)


def _empty_progress_payload() -> dict[str, Any]:
    return {
        "completed_lesson_ids": [],
        "successful_runs": 0,
        "latest_lesson_id": None,
        "pretest_score": None,
        "posttest_score": None,
        "n_gain": None,
        "quiz_attempts": {"pretest": 0, "posttest": 0},
        "total_submission_attempts": 0,
        "passed_submission_attempts": 0,
        "validation_failures": 0,
        "runtime_failures": 0,
        "test_failures": 0,
    }


def build_auth_router(services: Any) -> APIRouter:
    router = APIRouter()
    current_principal = build_current_principal_dependency(
        auth_service=services.auth,
        audit_service=getattr(services, "audit", None),
    )
    admin_principal = require_roles(current_principal, PlatformRole.ADMIN)
    staff_principal = require_roles(
        current_principal,
        PlatformRole.INSTRUCTOR,
        PlatformRole.ADMIN,
    )

    @router.post("/auth/sign-in")
    def sign_in(request: StudentSignInRequest):
        try:
            principal, access_token = services.auth.sign_in(
                display_name=request.display_name,
                password=request.password,
                firebase_id_token=request.firebase_id_token,
            )
            dashboard = services.user_evaluation.get_dashboard(principal.id)
            if dashboard is None and request.firebase_id_token:
                dashboard = services.user_evaluation.sign_in(
                    request.display_name,
                    request.password,
                    request.firebase_id_token,
                )
            if dashboard is None:
                dashboard = {
                    "student": {
                        "id": principal.id,
                        "display_name": request.display_name or "User",
                    },
                    "progress": _empty_progress_payload(),
                }
            dashboard["student"]["role"] = principal.role.value
            dashboard["access_token"] = access_token
            return dashboard
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except Exception as error:  # noqa: BLE001
            if hasattr(error, "status_code") and hasattr(error, "detail"):
                raise HTTPException(status_code=error.status_code, detail=error.detail) from error
            raise HTTPException(status_code=500, detail=str(error)) from error

    @router.post("/auth/sign-out")
    def sign_out(principal: Principal = Depends(current_principal)):
        services.auth.sign_out(principal)
        return {"status": "signed_out"}

    @router.get("/me/dashboard")
    def get_my_dashboard(principal: Principal = Depends(current_principal)):
        dashboard = services.user_evaluation.get_dashboard(principal.id)
        if dashboard is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown student_id '{principal.id}'.",
            )
        dashboard["student"]["role"] = principal.role.value
        return dashboard

    @router.get("/admin/students/{student_id}/dashboard")
    def get_student_dashboard(
        student_id: str,
        _principal: Principal = Depends(admin_principal),
    ):
        dashboard = services.user_evaluation.get_dashboard(student_id)
        if dashboard is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown student_id '{student_id}'.",
            )
        return dashboard

    @router.get("/staff/students")
    def list_staff_students(_principal: Principal = Depends(staff_principal)):
        students = [
            {
                "id": user["id"],
                "display_name": user["display_name"],
                "role": user["role"],
                "status": user["status"],
            }
            for user in services.auth.list_users()
            if user.get("role") == PlatformRole.STUDENT.value
        ]
        students.sort(key=lambda user: (str(user.get("display_name") or "").casefold(), user["id"]))
        return {"students": students}

    @router.get("/staff/students/{student_id}/dashboard")
    def get_staff_student_dashboard(
        student_id: str,
        _principal: Principal = Depends(staff_principal),
    ):
        dashboard = services.user_evaluation.get_dashboard(student_id)
        if dashboard is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown student_id '{student_id}'.",
            )
        return dashboard

    @router.get("/admin/users")
    def list_users(_principal: Principal = Depends(admin_principal)):
        return {"users": services.auth.list_users()}

    @router.patch("/admin/users/{user_id}/role")
    def update_user_role(
        user_id: str,
        request: AuthRoleUpdateRequest,
        principal: Principal = Depends(admin_principal),
    ):
        try:
            user = services.auth.update_user_role(
                actor=principal,
                target_user_id=user_id,
                role=request.role,
            )
            return {"user": user}
        except Exception as error:  # noqa: BLE001
            if hasattr(error, "status_code") and hasattr(error, "detail"):
                raise HTTPException(status_code=error.status_code, detail=error.detail) from error
            raise HTTPException(status_code=500, detail=str(error)) from error

    @router.patch("/admin/users/{user_id}/status")
    def update_user_status(
        user_id: str,
        request: AuthStatusUpdateRequest,
        principal: Principal = Depends(admin_principal),
    ):
        try:
            user = services.auth.update_user_status(
                actor=principal,
                target_user_id=user_id,
                status=request.status,
            )
            return {"user": user}
        except Exception as error:  # noqa: BLE001
            if hasattr(error, "status_code") and hasattr(error, "detail"):
                raise HTTPException(status_code=error.status_code, detail=error.detail) from error
            raise HTTPException(status_code=500, detail=str(error)) from error

    return router
