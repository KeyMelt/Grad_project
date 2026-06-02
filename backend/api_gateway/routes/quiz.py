from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.auth.dependencies import build_current_principal_dependency, require_roles
from backend.auth.roles import PlatformRole, Principal
from backend.api_gateway.schemas import QuizStartRequest, QuizSubmissionRequest


def build_quiz_router(services: Any) -> APIRouter:
    router = APIRouter()
    current_principal = build_current_principal_dependency(
        auth_service=services.auth,
        audit_service=getattr(services, "audit", None),
    )
    quiz_principal = require_roles(
        current_principal,
        PlatformRole.STUDENT,
        PlatformRole.ADMIN,
    )

    @router.post("/quiz/start")
    def start_quiz(
        request: QuizStartRequest,
        principal: Principal = Depends(quiz_principal),
    ):
        try:
            _ensure_student_record(services, principal)
            return services.user_evaluation.start_quiz(
                student_id=principal.id,
                phase=request.phase,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @router.post("/quiz/submit")
    def submit_quiz(
        request: QuizSubmissionRequest,
        principal: Principal = Depends(quiz_principal),
    ):
        try:
            _ensure_student_record(services, principal)
            result = services.user_evaluation.submit_quiz(
                student_id=principal.id,
                session_id=request.session_id,
                answers=[answer.model_dump() for answer in request.answers],
            )
            record_quiz_result = getattr(
                getattr(services, "study_buddy", None),
                "record_quiz_result",
                None,
            )
            if callable(record_quiz_result):
                record_quiz_result(
                    student_id=principal.id,
                    session_id=request.session_id,
                    result=result,
                )
            return result
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    return router


def _ensure_student_record(services: Any, principal: Principal) -> None:
    ensure_record = getattr(services.user_evaluation, "ensure_student_record", None)
    if callable(ensure_record):
        ensure_record(
            student_id=principal.id,
            display_name=principal.id,
        )
