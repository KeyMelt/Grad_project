from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from backend.auth.dependencies import build_current_principal_dependency, require_roles
from backend.auth.roles import PlatformRole, Principal


class StartSessionRequest(BaseModel):
    condition: str
    lesson_ids: list[str]


class ProbeSubmitRequest(BaseModel):
    study_session_id: str
    lesson_id: str
    concept_id: str
    probe_id: str
    actual_value: float
    predicted_value: float
    tolerance: float


class SurveySubmitRequest(BaseModel):
    study_session_id: str
    condition: str
    sus_q1: int = Field(ge=1, le=5)
    sus_q2: int = Field(ge=1, le=5)
    sus_q3: int = Field(ge=1, le=5)
    sus_q4: int = Field(ge=1, le=5)
    sus_q5: int = Field(ge=1, le=5)
    sus_q6: int = Field(ge=1, le=5)
    sus_q7: int = Field(ge=1, le=5)
    sus_q8: int = Field(ge=1, le=5)
    sus_q9: int = Field(ge=1, le=5)
    sus_q10: int = Field(ge=1, le=5)
    tlx_mental_demand: int = Field(ge=0, le=100)
    tlx_physical_demand: int = Field(ge=0, le=100)
    tlx_temporal_demand: int = Field(ge=0, le=100)
    tlx_performance: int = Field(ge=0, le=100)
    tlx_effort: int = Field(ge=0, le=100)
    tlx_frustration: int = Field(ge=0, le=100)
    feedback_helpful: Optional[str] = None
    feedback_confusing: Optional[str] = None
    feedback_improvement: Optional[str] = None


def build_evaluation_router(services: Any) -> APIRouter:
    router = APIRouter()
    current_principal = build_current_principal_dependency(
        auth_service=services.auth,
        audit_service=getattr(services, "audit", None),
    )
    student_principal = require_roles(
        current_principal,
        PlatformRole.STUDENT,
        PlatformRole.INSTRUCTOR,
        PlatformRole.ADMIN,
    )
    admin_principal = require_roles(
        current_principal,
        PlatformRole.ADMIN,
    )

    @router.post("/evaluation/session/start", status_code=201)
    def start_session(
        request: StartSessionRequest,
        principal: Principal = Depends(student_principal),
    ):
        try:
            record = services.evaluation_session.create_session(
                student_id=principal.id,
                condition=request.condition,
                lesson_ids=request.lesson_ids,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        return {"study_session_id": record.id}

    @router.post("/evaluation/probe/submit", status_code=200)
    def submit_probe(
        request: ProbeSubmitRequest,
        principal: Principal = Depends(student_principal),
    ):
        try:
            record = services.prediction_probe.submit_attempt(
                student_id=principal.id,
                study_session_id=request.study_session_id,
                lesson_id=request.lesson_id,
                concept_id=request.concept_id,
                probe_id=request.probe_id,
                actual_value=request.actual_value,
                predicted_value=request.predicted_value,
                tolerance=request.tolerance,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        return {
            "absolute_error": record.absolute_error,
            "is_within_tolerance": record.is_within_tolerance,
            "attempt_index": record.attempt_index,
        }

    @router.post("/evaluation/survey/submit", status_code=201)
    def submit_survey(
        request: SurveySubmitRequest,
        principal: Principal = Depends(student_principal),
    ):
        try:
            record = services.study_session_survey.submit_survey(
                student_id=principal.id,
                study_session_id=request.study_session_id,
                condition=request.condition,
                sus_q1=request.sus_q1,
                sus_q2=request.sus_q2,
                sus_q3=request.sus_q3,
                sus_q4=request.sus_q4,
                sus_q5=request.sus_q5,
                sus_q6=request.sus_q6,
                sus_q7=request.sus_q7,
                sus_q8=request.sus_q8,
                sus_q9=request.sus_q9,
                sus_q10=request.sus_q10,
                tlx_mental_demand=request.tlx_mental_demand,
                tlx_physical_demand=request.tlx_physical_demand,
                tlx_temporal_demand=request.tlx_temporal_demand,
                tlx_performance=request.tlx_performance,
                tlx_effort=request.tlx_effort,
                tlx_frustration=request.tlx_frustration,
                feedback_helpful=request.feedback_helpful,
                feedback_confusing=request.feedback_confusing,
                feedback_improvement=request.feedback_improvement,
            )
            services.evaluation_session.mark_survey_complete(
                request.study_session_id
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        return {"sus_score": record.sus_score, "tlx_overall": record.tlx_overall}

    @router.get("/evaluation/export/alei-components")
    def export_alei_components(
        principal: Principal = Depends(admin_principal),
    ):
        try:
            filename, content = services.alei_export.build_export()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    return router
