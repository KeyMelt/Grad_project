from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

import os

from backend.services.firebase_progress_service import FirebaseProgressService
from backend.services.local_eval_progress_service import LocalEvalProgressService
from backend.services.quiz_service import QuizService
from backend.services.user_evaluation_service import UserEvaluationService
from backend.settings import UserEvaluationSettings, require_configured_secret


@dataclass(frozen=True)
class ServiceContainer:
    user_evaluation: Any


class StudentSignInRequest(BaseModel):
    display_name: str = Field(default="", max_length=80)
    password: str = Field(default="", max_length=128)
    firebase_id_token: str | None = None


class QuizStartRequest(BaseModel):
    student_id: str
    phase: str


class StudentEnsureRequest(BaseModel):
    student_id: str
    display_name: str = Field(default="", max_length=120)


class QuizAnswer(BaseModel):
    question_id: str
    selected_index: int = Field(ge=0)


class QuizSubmissionRequest(BaseModel):
    student_id: str
    session_id: str
    answers: list[QuizAnswer]


def _close_if_present(service: Any) -> None:
    close = getattr(service, "close", None)
    if callable(close):
        close()


def _build_services() -> ServiceContainer:
    settings = UserEvaluationSettings.from_env()

    # When RL_IDE_ALLOW_LOCAL_PASSWORD_AUTH=1 the evaluation harness uses a
    # local SQLite-backed service instead of Firebase. This mode is intended
    # ONLY for the AI-agent evaluation harness - never for production.
    if os.environ.get("RL_IDE_ALLOW_LOCAL_PASSWORD_AUTH", "0").strip() == "1":
        progress = LocalEvalProgressService()
    else:
        progress = FirebaseProgressService(
            credentials_path=settings.firebase_credentials_path,
            app_name=settings.firebase_app_name,
        )

    return ServiceContainer(
        user_evaluation=UserEvaluationService(
            progress_service=progress,
            quiz_service=QuizService(progress),
        )
    )


def create_app(services: ServiceContainer | None = None) -> FastAPI:
    required_token = require_configured_secret(
        "RL_IDE_INTERNAL_TOKEN",
        "user evaluation internal API authentication",
    )
    svc = services or _build_services()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            yield
        finally:
            _close_if_present(svc.user_evaluation)

    app = FastAPI(
        title="RL IDE User Evaluation Service",
        lifespan=lifespan,
    )

    def _assert_internal_access(x_internal_token: str | None) -> None:
        if x_internal_token != required_token:
            raise HTTPException(status_code=401, detail="Unauthorized internal call.")

    @app.get("/")
    def read_root():
        return {"status": "User evaluation service is running"}

    @app.post("/internal/auth/sign-in")
    def sign_in(
        request: StudentSignInRequest,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return svc.user_evaluation.sign_in(
                request.display_name,
                request.password,
                request.firebase_id_token,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=500, detail=str(error)) from error

    @app.get("/internal/students/{student_id}/dashboard")
    def get_student_dashboard(
        student_id: str,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        dashboard = svc.user_evaluation.get_dashboard(student_id)
        if dashboard is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown student_id '{student_id}'.",
            )
        return dashboard

    @app.post("/internal/students/ensure")
    def ensure_student_record(
        request: StudentEnsureRequest,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return svc.user_evaluation.ensure_student_record(
                student_id=request.student_id,
                display_name=request.display_name or request.student_id,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.post("/internal/quiz/start")
    def start_quiz(
        request: QuizStartRequest,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return svc.user_evaluation.start_quiz(
                student_id=request.student_id,
                phase=request.phase,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.get("/internal/quiz/catalog")
    def quiz_catalog(x_internal_token: str | None = Header(default=None)):
        _assert_internal_access(x_internal_token)
        return svc.user_evaluation.quiz_catalog()

    @app.post("/internal/quiz/submit")
    def submit_quiz(
        request: QuizSubmissionRequest,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return svc.user_evaluation.submit_quiz(
                student_id=request.student_id,
                session_id=request.session_id,
                answers=[answer.model_dump() for answer in request.answers],
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.get("/internal/metrics/n-gain")
    def list_n_gain_metrics(x_internal_token: str | None = Header(default=None)):
        _assert_internal_access(x_internal_token)
        return {"rows": svc.user_evaluation.list_n_gain_metrics()}

    return app
