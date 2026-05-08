from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, HTTPException

from backend.artifact_store_sqlite import SqliteArtifactStore
from backend.execution_worker.routes import (
    build_health_router,
    build_jobs_router,
    build_workspace_router,
)
from backend.job_store_sqlite import SqliteExecutionJobStore
from backend.services.execution_service import ExecutionService
from backend.services.student_progress_service import StudentProgressService
from backend.services.workspace_service import WorkspaceSessionService
from backend.settings import WorkerSettings, env_bool
from backend.workspace_store_sqlite import SqliteWorkspaceStore


@dataclass(frozen=True)
class WorkerServiceContainer:
    execution: ExecutionService
    workspace: WorkspaceSessionService


def _build_services() -> WorkerServiceContainer:
    settings = WorkerSettings.from_env()
    progress_service: StudentProgressService | None = None
    if env_bool("RL_IDE_WORKER_RECORD_PROGRESS"):
        progress_service = StudentProgressService()

    return WorkerServiceContainer(
        execution=ExecutionService(
            job_store=SqliteExecutionJobStore(str(settings.job_store_path)),
            artifact_store=SqliteArtifactStore(str(settings.artifact_store_path)),
            progress_service=progress_service,
        ),
        workspace=WorkspaceSessionService(
            base_dir=settings.workspace_base_dir,
            sandbox_image=settings.workspace_image,
            use_docker=settings.workspace_use_docker,
            store=SqliteWorkspaceStore(str(settings.workspace_store_path)),
        ),
    )


def _close_if_present(service: Any) -> None:
    close = getattr(service, "close", None)
    if callable(close):
        close()


def create_app(services: WorkerServiceContainer | None = None) -> FastAPI:
    svc = services or _build_services()
    required_token = WorkerSettings.from_env().internal_token or ""

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        svc.workspace.start_runtime_prepare()
        try:
            yield
        finally:
            _close_if_present(svc.workspace)
            _close_if_present(svc.execution)

    app = FastAPI(
        title="RL IDE Execution Worker",
        lifespan=lifespan,
    )

    def _assert_internal_access(x_internal_token: str | None) -> None:
        if not required_token:
            return
        if x_internal_token != required_token:
            raise HTTPException(status_code=401, detail="Unauthorized worker call.")

    app.include_router(build_health_router(svc, _assert_internal_access))
    app.include_router(build_jobs_router(svc, _assert_internal_access))
    app.include_router(build_workspace_router(svc, _assert_internal_access))
    return app
