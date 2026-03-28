from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.execution_runtime import ExecutionPipelineError
from backend.services.execution_service import ExecutionService
from backend.services.lesson_catalog_service import LessonCatalogService
from backend.services.metrics_export_service import MetricsExportService
from backend.services.quiz_service import QuizService
from backend.services.student_progress_service import StudentProgressService


@dataclass(frozen=True)
class ServiceContainer:
    lesson_catalog: LessonCatalogService
    progress: StudentProgressService
    quiz: QuizService
    execution: ExecutionService
    metrics_export: MetricsExportService


def _build_services() -> ServiceContainer:
    progress = StudentProgressService()
    return ServiceContainer(
        lesson_catalog=LessonCatalogService(),
        progress=progress,
        quiz=QuizService(progress),
        execution=ExecutionService(progress_service=progress),
        metrics_export=MetricsExportService(),
    )


class CodeSubmission(BaseModel):
    lesson_id: str
    code: str
    learning_rate: Optional[float] = Field(default=None, gt=0, le=1)
    discount_factor: Optional[float] = Field(default=None, gt=0, le=1)
    exploration_rate: Optional[float] = Field(default=None, ge=0, le=1)
    episode_count: Optional[int] = Field(default=None, ge=1, le=500)
    student_id: Optional[str] = None


class StudentSignInRequest(BaseModel):
    display_name: str = Field(min_length=2, max_length=80)


class QuizStartRequest(BaseModel):
    student_id: str
    phase: str


class QuizAnswer(BaseModel):
    question_id: str
    selected_index: int = Field(ge=0)


class QuizSubmissionRequest(BaseModel):
    student_id: str
    session_id: str
    answers: list[QuizAnswer]


def create_app(services: Optional[ServiceContainer] = None) -> FastAPI:
    app = FastAPI(title="RL IDE Backend Gateway")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    svc = services or _build_services()

    @app.get("/")
    def read_root():
        return {"status": "Backend is running"}

    @app.get("/lessons")
    def get_lessons():
        return {"lessons": svc.lesson_catalog.list_lessons()}

    @app.post("/auth/sign-in")
    def sign_in(request: StudentSignInRequest):
        try:
            return svc.progress.sign_in(request.display_name)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.get("/students/{student_id}/dashboard")
    def get_student_dashboard(student_id: str):
        dashboard = svc.progress.get_dashboard(student_id)
        if dashboard is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown student_id '{student_id}'.",
            )
        return dashboard

    @app.post("/quiz/start")
    def start_quiz(request: QuizStartRequest):
        try:
            return svc.quiz.start_session(
                student_id=request.student_id,
                phase=request.phase,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.post("/quiz/submit")
    def submit_quiz(request: QuizSubmissionRequest):
        try:
            return svc.quiz.submit_session(
                student_id=request.student_id,
                session_id=request.session_id,
                answers=[answer.model_dump() for answer in request.answers],
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.post("/submit")
    def submit_code(submission: CodeSubmission):
        return svc.execution.submit(submission.model_dump())

    @app.get("/tasks/{task_id}")
    def get_task_status(task_id: str):
        snapshot = svc.execution.snapshot(task_id)
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown task_id '{task_id}'.",
            )
        return snapshot

    @app.get("/admin/metrics/n-gain/export")
    def export_n_gain_metrics():
        rows = svc.progress.list_n_gain_metrics()
        filename, content = svc.metrics_export.build_n_gain_export(rows)
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            iter([content]),
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers=headers,
        )

    @app.post("/execute")
    def execute_code(submission: CodeSubmission):
        try:
            return svc.execution.execute_sync(submission.model_dump())
        except ExecutionPipelineError as error:
            raise HTTPException(
                status_code=error.status_code,
                detail=error.detail,
            ) from error

    return app


app = create_app()

