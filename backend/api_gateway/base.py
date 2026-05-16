"""FastAPI gateway for the desktop client and service-mode workers."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api_gateway.routes import (
    build_admin_router,
    build_auth_router,
    build_concept_videos_router,
    build_execution_router,
    build_lessons_router,
    build_quiz_router,
    build_visualization_router,
    build_workspace_router,
)
from backend.services.execution_service import ExecutionService as LocalExecutionService
from backend.services.firebase_progress_service import FirebaseProgressService
from backend.services.lesson_catalog_service import LessonCatalogService
from backend.services.metrics_export_service import MetricsExportService
from backend.services.quiz_service import QuizService
from backend.services.remote_execution_service import RemoteExecutionService
from backend.services.remote_user_evaluation_service import RemoteUserEvaluationService
from backend.services.remote_workspace_service import RemoteWorkspaceService
from backend.services.user_evaluation_service import UserEvaluationService
from backend.settings import GatewaySettings


@dataclass(frozen=True)
class ServiceContainer:
    lesson_catalog: LessonCatalogService
    user_evaluation: UserEvaluationService | RemoteUserEvaluationService
    execution: LocalExecutionService | RemoteExecutionService
    workspace: RemoteWorkspaceService | None
    metrics_export: MetricsExportService


def _build_services() -> ServiceContainer:
    settings = GatewaySettings.from_env()
    user_evaluation, local_progress_service = _build_user_evaluation(settings)
    execution, workspace = _build_execution_services(settings, local_progress_service)

    return ServiceContainer(
        lesson_catalog=LessonCatalogService(),
        user_evaluation=user_evaluation,
        execution=execution,
        workspace=workspace,
        metrics_export=MetricsExportService(),
    )


def _build_user_evaluation(
    settings: GatewaySettings,
) -> tuple[UserEvaluationService | RemoteUserEvaluationService, FirebaseProgressService | None]:
    if settings.user_service_mode == "remote":
        return (
            RemoteUserEvaluationService(
                user_service_base_url=settings.user_service_url,
                internal_token=settings.internal_token,
                timeout_seconds=settings.user_service_timeout_seconds,
            ),
            None,
        )

    progress = FirebaseProgressService(
        credentials_path=settings.firebase_credentials_path,
        app_name=settings.firebase_app_name,
    )

    return (
        UserEvaluationService(
            progress_service=progress,
            quiz_service=QuizService(progress),
        ),
        progress,
    )


def _build_execution_services(
    settings: GatewaySettings,
    local_progress_service: FirebaseProgressService | None,
) -> tuple[LocalExecutionService | RemoteExecutionService, RemoteWorkspaceService | None]:
    if settings.execution_mode == "remote":
        execution = RemoteExecutionService(
            worker_base_url=settings.execution_worker_url,
            internal_token=settings.internal_token,
            timeout_seconds=settings.worker_timeout_seconds,
        )
        workspace = RemoteWorkspaceService(
            worker_base_url=settings.execution_worker_url,
            internal_token=settings.internal_token,
            timeout_seconds=settings.worker_timeout_seconds,
        )
        return execution, workspace

    return LocalExecutionService(progress_service=local_progress_service), None


def _close_if_present(service: Any) -> None:
    close = getattr(service, "close", None)
    if callable(close):
        close()


def create_app(services: ServiceContainer | None = None) -> FastAPI:
    svc = services or _build_services()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            yield
        finally:
            _close_if_present(svc.workspace)
            _close_if_present(svc.execution)
            _close_if_present(svc.user_evaluation)

    app = FastAPI(
        title="RL IDE Backend Gateway",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def read_root():
        return {"status": "Backend is running"}

    app.include_router(build_lessons_router(svc))
    app.include_router(build_concept_videos_router())
    app.include_router(build_workspace_router(svc))
    app.include_router(build_visualization_router())
    app.include_router(build_auth_router(svc))
    app.include_router(build_quiz_router(svc))
    app.include_router(build_execution_router(svc))
    app.include_router(build_admin_router(svc))
    return app
