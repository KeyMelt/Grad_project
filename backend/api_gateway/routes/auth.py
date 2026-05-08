from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.api_gateway.schemas import StudentSignInRequest


def build_auth_router(services: Any) -> APIRouter:
    router = APIRouter()

    @router.post("/auth/sign-in")
    def sign_in(request: StudentSignInRequest):
        try:
            return services.user_evaluation.sign_in(
                request.display_name,
                request.password,
                request.firebase_id_token,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=500, detail=str(error)) from error

    @router.get("/students/{student_id}/dashboard")
    def get_student_dashboard(student_id: str):
        dashboard = services.user_evaluation.get_dashboard(student_id)
        if dashboard is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown student_id '{student_id}'.",
            )
        return dashboard

    return router
