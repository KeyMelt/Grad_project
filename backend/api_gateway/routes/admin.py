from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.auth.dependencies import build_current_principal_dependency, require_roles
from backend.auth.roles import PlatformRole, Principal
from backend.lessons import get_lesson_definition


class AuthoredLessonUpsertRequest(BaseModel):
    lesson: dict[str, Any] = Field(default_factory=dict)


def build_admin_router(services: Any) -> APIRouter:
    router = APIRouter()
    current_principal = build_current_principal_dependency(
        auth_service=services.auth,
        audit_service=getattr(services, "audit", None),
    )
    admin_principal = require_roles(current_principal, PlatformRole.ADMIN)
    authoring_principal = require_roles(
        current_principal,
        PlatformRole.INSTRUCTOR,
        PlatformRole.ADMIN,
    )

    @router.get("/admin/metrics/n-gain/export")
    def export_n_gain_metrics(principal: Principal = Depends(admin_principal)):
        audit = getattr(services, "audit", None)
        if audit is not None:
            audit.record(
                actor_user_id=principal.id,
                action="metrics_export",
                resource_type="n_gain",
                outcome="success",
            )
        rows = services.user_evaluation.list_n_gain_metrics()
        filename, content = services.metrics_export.build_n_gain_export(rows)
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            iter([content]),
            media_type=("application/vnd.openxmlformats-officedocument." "spreadsheetml.sheet"),
            headers=headers,
        )

    @router.get("/admin/metrics/learning-analytics/export")
    def export_learning_analytics(principal: Principal = Depends(admin_principal)):
        audit = getattr(services, "audit", None)
        if audit is not None:
            audit.record(
                actor_user_id=principal.id,
                action="metrics_export",
                resource_type="learning_analytics",
                outcome="success",
            )
        export_service = getattr(services, "learning_analytics_export", None)
        if export_service is None:
            raise HTTPException(
                status_code=503,
                detail="Learning analytics export is unavailable.",
            )
        filename, content = export_service.build_export()
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            iter([content]),
            media_type=("application/vnd.openxmlformats-officedocument." "spreadsheetml.sheet"),
            headers=headers,
        )

    @router.get("/admin/lessons/authored")
    def list_authored_lessons(principal: Principal = Depends(authoring_principal)):
        del principal
        service = getattr(services, "authored_lessons", None)
        if service is None:
            raise HTTPException(status_code=503, detail="Lesson authoring is unavailable.")
        return {"lessons": service.list_lessons()}

    @router.put("/admin/lessons/authored/{lesson_id}")
    def upsert_authored_lesson(
        lesson_id: str,
        request: AuthoredLessonUpsertRequest,
        principal: Principal = Depends(authoring_principal),
    ):
        if get_lesson_definition(lesson_id) is not None:
            raise HTTPException(
                status_code=409,
                detail="Core lessons cannot be overwritten by the authoring studio.",
            )
        service = getattr(services, "authored_lessons", None)
        if service is None:
            raise HTTPException(status_code=503, detail="Lesson authoring is unavailable.")
        try:
            lesson = service.upsert_lesson(
                lesson_id=lesson_id,
                payload=request.lesson,
                actor_user_id=principal.id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"lesson": lesson}

    @router.delete("/admin/lessons/authored/{lesson_id}", status_code=204)
    def delete_authored_lesson(
        lesson_id: str,
        principal: Principal = Depends(authoring_principal),
    ):
        del principal
        if get_lesson_definition(lesson_id) is not None:
            raise HTTPException(
                status_code=409,
                detail="Core lessons cannot be deleted by the authoring studio.",
            )
        service = getattr(services, "authored_lessons", None)
        if service is None:
            raise HTTPException(status_code=503, detail="Lesson authoring is unavailable.")
        deleted = service.delete_lesson(lesson_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Authored lesson not found.")
        return None

    return router
