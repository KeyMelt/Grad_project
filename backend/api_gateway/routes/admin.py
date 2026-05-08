from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse


def build_admin_router(services: Any) -> APIRouter:
    router = APIRouter()

    @router.get("/admin/metrics/n-gain/export")
    def export_n_gain_metrics():
        rows = services.user_evaluation.list_n_gain_metrics()
        filename, content = services.metrics_export.build_n_gain_export(rows)
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            iter([content]),
            media_type=("application/vnd.openxmlformats-officedocument." "spreadsheetml.sheet"),
            headers=headers,
        )

    return router
