"""FastAPI gateway for the desktop client and service-mode workers."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.auth.firebase_admin_setup import FirebaseAdminClient
from backend.auth.shell_tokens import ShellTokenService
from backend.api_gateway.routes import (
    build_admin_router,
    build_auth_router,
    build_concept_videos_router,
    build_evaluation_router,
    build_execution_router,
    build_lessons_router,
    build_quiz_router,
    build_study_buddy_router,
    build_telemetry_router,
    build_visualization_router,
    build_workspace_router,
)
from backend.persistence import Database
from backend.services.alei_export_service import ALEIExportService
from backend.services.authored_lesson_service import AuthoredLessonService
from backend.services.lesson_registry_service import LessonRegistryService
from backend.services.auth_service import AuthService
from backend.services.evaluation_session_service import EvaluationSessionService
from backend.services.prediction_probe_service import PredictionProbeService
from backend.services.study_session_survey_service import StudySessionSurveyService
from backend.services.execution_service import ExecutionService as LocalExecutionService
from backend.services.firebase_progress_service import FirebaseProgressService
from backend.services.local_eval_progress_service import LocalEvalProgressService
from backend.services.learning_analytics_export_service import LearningAnalyticsExportService
from backend.services.lesson_catalog_service import LessonCatalogService
from backend.services.metrics_export_service import MetricsExportService
from backend.services.quiz_service import QuizService
from backend.services.remote_execution_service import RemoteExecutionService
from backend.services.remote_user_evaluation_service import RemoteUserEvaluationService
from backend.services.remote_workspace_service import RemoteWorkspaceService
from backend.services.security_audit_service import SecurityAuditService
from backend.services.study_buddy_service import StudyBuddyService
from backend.services.telemetry_service import TelemetryService
from backend.services.user_evaluation_service import UserEvaluationService
from backend.settings import GatewaySettings, require_configured_secret

_LOCAL_DEV_CORS_ORIGIN_REGEX = (
    r"^https?://("
    r"localhost|"
    r"127\.0\.0\.1|"
    r"0\.0\.0\.0|"
    r"([a-zA-Z0-9-]+\.local)|"
    r"(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|"
    r"(192\.168\.\d{1,3}\.\d{1,3})|"
    r"(172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})"
    r")(:\d+)?$"
)


@dataclass(frozen=True)
class ServiceContainer:
    lesson_catalog: LessonCatalogService
    user_evaluation: UserEvaluationService | RemoteUserEvaluationService
    auth: AuthService
    execution: LocalExecutionService | RemoteExecutionService
    workspace: RemoteWorkspaceService | None
    metrics_export: MetricsExportService
    learning_analytics_export: Any | None = None
    telemetry: Any | None = None
    study_buddy: Any | None = None
    audit: SecurityAuditService | None = None
    shell_tokens: ShellTokenService | None = None
    evaluation_session: EvaluationSessionService | None = None
    prediction_probe: PredictionProbeService | None = None
    study_session_survey: StudySessionSurveyService | None = None
    alei_export: ALEIExportService | None = None
    authored_lessons: AuthoredLessonService | None = None
    lesson_registry: LessonRegistryService | None = None


def _build_services() -> ServiceContainer:
    settings = GatewaySettings.from_env()
    if settings.execution_mode == "remote" or settings.user_service_mode == "remote":
        require_configured_secret(
            "RL_IDE_INTERNAL_TOKEN",
            "gateway-to-service authentication in remote mode",
        )
    database = Database()
    telemetry = TelemetryService(database=database)
    study_buddy = StudyBuddyService(
        telemetry_service=telemetry,
        database=telemetry.database,
    )
    user_evaluation, local_progress_service = _build_user_evaluation(settings)
    firebase_client = _build_firebase_admin_client(settings)

    import os as _os
    if _os.environ.get("RL_IDE_ALLOW_LOCAL_PASSWORD_AUTH", "0").strip() == "1":
        # Evaluation harness: use local SQLite auth so @example.test accounts
        # can sign in without Firebase. Never used in production.
        progress_for_auth: Any = LocalEvalProgressService()
    else:
        progress_for_auth = local_progress_service or FirebaseProgressService(
            credentials_path=settings.firebase_credentials_path,
            app_name=settings.firebase_app_name,
        )
    audit = SecurityAuditService(database=database)
    auth_service = AuthService(
        database=database,
        progress_service=progress_for_auth,
        token_secret=settings.auth_token_secret,
        token_ttl_seconds=settings.auth_token_ttl_seconds,
        firebase_client=firebase_client,
        audit_service=audit,
        open_provisioning=settings.open_provisioning,
        allow_legacy_password_sign_in=settings.allow_legacy_password_sign_in,
    )
    auth_service.bootstrap_admin(
        firebase_uid=settings.bootstrap_admin_firebase_uid,
        display_name=settings.bootstrap_admin_display_name,
    )
    shell_tokens = ShellTokenService(settings.shell_token_secret)
    evaluation_session_svc = EvaluationSessionService(database=database)
    prediction_probe_svc = PredictionProbeService(database=database)
    study_session_survey_svc = StudySessionSurveyService(database=database)
    alei_export_svc = ALEIExportService(database=database)
    authored_lesson_svc = AuthoredLessonService(database=database)
    lesson_registry_svc = LessonRegistryService(database=database)

    import backend.lesson_registry as _lr
    _lr.set_registry(lesson_registry_svc)

    execution, workspace = _build_execution_services(
        settings,
        local_progress_service,
        telemetry,
    )

    return ServiceContainer(
        lesson_catalog=LessonCatalogService(registry=lesson_registry_svc),
        user_evaluation=user_evaluation,
        auth=auth_service,
        execution=execution,
        workspace=workspace,
        metrics_export=MetricsExportService(),
        learning_analytics_export=LearningAnalyticsExportService(
            database=telemetry.database,
        ),
        telemetry=telemetry,
        study_buddy=study_buddy,
        audit=audit,
        shell_tokens=shell_tokens,
        evaluation_session=evaluation_session_svc,
        prediction_probe=prediction_probe_svc,
        study_session_survey=study_session_survey_svc,
        alei_export=alei_export_svc,
        authored_lessons=authored_lesson_svc,
        lesson_registry=lesson_registry_svc,
    )


def _build_firebase_admin_client(settings: GatewaySettings) -> FirebaseAdminClient | None:
    should_initialize = bool(
        settings.firebase_credentials_path
        or settings.bootstrap_admin_firebase_uid
        or not settings.allow_legacy_password_sign_in
    )
    if not should_initialize:
        return None
    try:
        return FirebaseAdminClient(
            credentials_path=settings.firebase_credentials_path,
            app_name=settings.firebase_app_name,
        )
    except Exception:
        return None


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
    telemetry: TelemetryService | None,
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

    return (
        LocalExecutionService(
            progress_service=local_progress_service,
            telemetry_service=telemetry,
        ),
        None,
    )


def _close_if_present(service: Any) -> None:
    close = getattr(service, "close", None)
    if callable(close):
        close()


def create_app(services: ServiceContainer | None = None) -> FastAPI:
    svc = services or _build_services()
    settings = GatewaySettings.from_env()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            yield
        finally:
            _close_if_present(svc.workspace)
            _close_if_present(svc.execution)
            _close_if_present(svc.telemetry)
            _close_if_present(svc.user_evaluation)

    app = FastAPI(
        title="RL IDE Backend Gateway",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_origin_regex=_LOCAL_DEV_CORS_ORIGIN_REGEX if settings.cors_allow_local_regex else None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def read_root():
        return {"status": "Backend is running"}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready")
    def ready():
        return {"status": "ready"}

    app.include_router(build_lessons_router(svc))
    app.include_router(build_concept_videos_router())
    app.include_router(build_workspace_router(svc))
    app.include_router(build_visualization_router(svc))
    app.include_router(build_auth_router(svc))
    app.include_router(build_quiz_router(svc))
    app.include_router(build_execution_router(svc))
    if svc.telemetry is not None:
        app.include_router(build_telemetry_router(svc))
    if svc.study_buddy is not None:
        app.include_router(build_study_buddy_router(svc))
    app.include_router(build_admin_router(svc))
    app.include_router(build_evaluation_router(svc))
    return app
