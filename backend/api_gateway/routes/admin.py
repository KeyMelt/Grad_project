from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from backend.auth.dependencies import build_current_principal_dependency, require_roles
from backend.auth.roles import PlatformRole, Principal


def build_admin_router(services: Any) -> APIRouter:
    router = APIRouter()
    current_principal = build_current_principal_dependency(
        auth_service=services.auth,
        audit_service=getattr(services, "audit", None),
    )
    admin_principal = require_roles(current_principal, PlatformRole.ADMIN)

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

    return router
