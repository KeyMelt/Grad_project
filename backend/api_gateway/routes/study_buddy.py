from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.api_gateway.schemas import (
    StudyBuddyChatRequest,
    StudyBuddyInterventionResponseRequest,
)
from backend.auth.dependencies import build_current_principal_dependency, require_roles
from backend.auth.roles import PlatformRole, Principal
from backend.services.pedagogical_llm_service import PedagogicalLLMUnavailableError


def build_study_buddy_router(services: Any) -> APIRouter:
    router = APIRouter()
    current_principal = build_current_principal_dependency(
        auth_service=services.auth,
        audit_service=getattr(services, "audit", None),
    )
    student_or_admin = require_roles(
        current_principal,
        PlatformRole.STUDENT,
        PlatformRole.INSTRUCTOR,
        PlatformRole.ADMIN,
    )
    admin_principal = require_roles(current_principal, PlatformRole.ADMIN)

    @router.get("/study-buddy/interventions/{session_id}/pending")
    def pending_intervention(
        session_id: str,
        principal: Principal = Depends(student_or_admin),
    ):
        intervention = services.study_buddy.pending_intervention(session_id)
        if intervention is not None and principal.role != PlatformRole.ADMIN:
            if intervention.get("student_id") != principal.id:
                intervention = None
        return {"intervention": intervention}

    @router.get("/me/learning-timeline")
    def my_learning_timeline(
        principal: Principal = Depends(student_or_admin),
        limit: int = Query(default=100, ge=1, le=250),
    ):
        return services.study_buddy.learning_timeline(principal.id, limit=limit)

    @router.get("/me/study-buddy/summary")
    def my_study_buddy_summary(principal: Principal = Depends(student_or_admin)):
        return services.study_buddy.summary(principal.id)

    @router.post("/me/study-buddy/chat")
    def study_buddy_chat(
        request: StudyBuddyChatRequest,
        principal: Principal = Depends(student_or_admin),
    ):
        try:
            return services.study_buddy.chat(
                student_id=principal.id,
                lesson_id=request.lesson_id,
                session_id=request.session_id,
                message=request.message,
                history=[message.model_dump(mode="json") for message in request.history],
                current_code=request.current_code,
                unresolved_blanks=request.unresolved_blanks,
                failure_kind=request.failure_kind,
                latest_feedback=request.latest_feedback,
            )
        except PedagogicalLLMUnavailableError as error:
            raise HTTPException(
                status_code=503,
                detail=error.public_message,
            ) from error

    @router.get("/admin/students/{student_id}/learning-timeline")
    def admin_learning_timeline(
        student_id: str,
        limit: int = Query(default=100, ge=1, le=250),
        _principal: Principal = Depends(admin_principal),
    ):
        return services.study_buddy.learning_timeline(student_id, limit=limit)

    @router.get("/admin/students/{student_id}/study-buddy/summary")
    def admin_study_buddy_summary(
        student_id: str,
        _principal: Principal = Depends(admin_principal),
    ):
        return services.study_buddy.summary(student_id)

    @router.post("/study-buddy/interventions/{intervention_id}/respond")
    def respond_to_intervention(
        intervention_id: str,
        request: StudyBuddyInterventionResponseRequest,
        principal: Principal = Depends(student_or_admin),
    ):
        intervention = services.study_buddy.get_intervention(intervention_id)
        if intervention is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown intervention_id '{intervention_id}'.",
            )
        if principal.role != PlatformRole.ADMIN and intervention.get("student_id") != principal.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this intervention.",
            )

        updated = services.study_buddy.respond_to_intervention(
            intervention_id,
            response=request.response,
        )
        if updated is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown intervention_id '{intervention_id}'.",
            )
        return {"intervention": updated}

    return router
