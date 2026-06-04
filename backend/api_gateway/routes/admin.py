from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field

from backend.auth.dependencies import build_current_principal_dependency, require_roles
from backend.auth.roles import PlatformRole, Principal
class LessonUpsertRequest(BaseModel):
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

    def _registry():
        svc = getattr(services, "lesson_registry", None)
        if svc is None:
            raise HTTPException(status_code=503, detail="Lesson registry is unavailable.")
        return svc

    # ------------------------------------------------------------------
    # Metrics exports
    # ------------------------------------------------------------------

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
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
            raise HTTPException(status_code=503, detail="Learning analytics export is unavailable.")
        filename, content = export_service.build_export()
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            iter([content]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers,
        )

    # ------------------------------------------------------------------
    # Lesson CRUD
    # ------------------------------------------------------------------

    @router.get("/admin/lessons")
    def list_lessons(principal: Principal = Depends(authoring_principal)):
        del principal
        return {"lessons": _registry().list_lesson_payloads()}

    @router.put("/admin/lessons/{lesson_id}")
    def upsert_lesson(
        lesson_id: str,
        request: LessonUpsertRequest,
        principal: Principal = Depends(authoring_principal),
    ):
        try:
            lesson = _registry().upsert_lesson(
                lesson_id=lesson_id,
                payload=request.lesson,
                actor_user_id=principal.id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"lesson": lesson}

    @router.delete("/admin/lessons/{lesson_id}", status_code=204)
    def delete_lesson(
        lesson_id: str,
        principal: Principal = Depends(authoring_principal),
    ):
        del principal
        deleted = _registry().delete_lesson(lesson_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Lesson not found.")
        return None

    # ------------------------------------------------------------------
    # Lecture notes stored on the lesson payload
    # ------------------------------------------------------------------

    @router.get(
        "/admin/lessons/{lesson_id}/lecture-notes",
        response_class=PlainTextResponse,
    )
    def get_lecture_notes(
        lesson_id: str,
        principal: Principal = Depends(authoring_principal),
    ):
        del principal
        payload = _registry().get_lesson_payload(lesson_id)
        if payload is None:
            raise HTTPException(status_code=404, detail="Lesson not found.")
        content = str((payload.get("concept_video") or {}).get("lecture_notes") or "")
        if not content:
            raise HTTPException(status_code=404, detail="No lecture notes found for this lesson.")
        return content

    @router.put("/admin/lessons/{lesson_id}/lecture-notes", status_code=200)
    async def upload_lecture_notes(
        lesson_id: str,
        file: UploadFile = File(...),
        principal: Principal = Depends(authoring_principal),
    ):
        if not file.filename or not file.filename.endswith(".md"):
            raise HTTPException(status_code=422, detail="Only .md files are accepted.")
        content_bytes = await file.read()
        if not content_bytes:
            raise HTTPException(status_code=422, detail="Uploaded file is empty.")
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=422, detail="Lecture notes must be UTF-8 text.") from exc
        try:
            _registry().set_lecture_notes(
                lesson_id=lesson_id,
                markdown=content,
                actor_user_id=principal.id,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Lesson not found.") from exc
        return {"lesson_id": lesson_id, "bytes_written": len(content_bytes)}

    @router.delete("/admin/lessons/{lesson_id}/lecture-notes", status_code=204)
    def delete_lecture_notes(
        lesson_id: str,
        principal: Principal = Depends(authoring_principal),
    ):
        deleted = _registry().delete_lecture_notes(
            lesson_id=lesson_id,
            actor_user_id=principal.id,
        )
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="No lecture notes found for this lesson.",
            )
        return None

    return router
