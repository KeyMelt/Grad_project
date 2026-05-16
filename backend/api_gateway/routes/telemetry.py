from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse

from backend.api_gateway.schemas import TelemetryBatchRequest
from backend.auth.dependencies import build_current_principal_dependency, require_roles
from backend.auth.roles import PlatformRole, Principal


def build_telemetry_router(services: Any) -> APIRouter:
    router = APIRouter()
    current_principal = build_current_principal_dependency(
        auth_service=services.auth,
        audit_service=getattr(services, "audit", None),
    )
    telemetry_principal = require_roles(
        current_principal,
        PlatformRole.STUDENT,
        PlatformRole.INSTRUCTOR,
        PlatformRole.ADMIN,
    )

    @router.post("/telemetry/events", status_code=202)
    def submit_telemetry_events(
        request: TelemetryBatchRequest,
        background_tasks: BackgroundTasks,
        principal: Principal = Depends(telemetry_principal),
    ):
        payload = []
        for event in request.events:
            item = event.model_dump()
            item["student_id"] = principal.id
            payload.append(item)
        ingest_events = getattr(services.study_buddy, "ingest_events", None)
        if callable(ingest_events):
            background_tasks.add_task(ingest_events, payload)
        else:
            background_tasks.add_task(services.telemetry.record_events, payload)
        return JSONResponse(
            status_code=202,
            content={"accepted": len(payload)},
        )

    return router
