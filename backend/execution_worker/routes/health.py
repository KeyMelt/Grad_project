from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Header


def build_health_router(
    services: Any,
    assert_internal_access: Callable[[str | None], None],
) -> APIRouter:
    router = APIRouter()

    @router.get("/")
    def read_root():
        return {"status": "Execution worker running"}

    @router.get("/internal/workspace/health")
    def workspace_health(
        x_internal_token: str | None = Header(default=None),
    ):
        assert_internal_access(x_internal_token)
        return services.workspace.health_snapshot()

    return router
