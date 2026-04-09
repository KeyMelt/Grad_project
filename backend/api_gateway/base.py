from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from websockets.asyncio.client import connect as websocket_connect

from backend.api_gateway.editor_shell import build_editor_shell_html
from backend.execution_runtime import ExecutionPipelineError
from backend.services.execution_service import ExecutionService as LocalExecutionService
from backend.services.firebase_progress_service import FirebaseProgressService
from backend.services.lesson_catalog_service import LessonCatalogService
from backend.services.metrics_export_service import MetricsExportService
from backend.services.quiz_service import QuizService
from backend.services.remote_execution_service import RemoteExecutionService
from backend.services.remote_workspace_service import RemoteWorkspaceService
from backend.services.student_progress_service import StudentProgressService
from backend.services.workspace_service import WorkspaceRuntimeError


@dataclass(frozen=True)
class ServiceContainer:
    lesson_catalog: LessonCatalogService
    progress: Any
    quiz: QuizService
    execution: LocalExecutionService | RemoteExecutionService
    workspace: RemoteWorkspaceService | None
    metrics_export: MetricsExportService


def _build_services() -> ServiceContainer:
    progress_backend = os.getenv("RL_IDE_PROGRESS_BACKEND", "sql").strip().lower()
    progress: Any
    if progress_backend == "firebase":
        try:
            progress = FirebaseProgressService(
                credentials_path=os.getenv("RL_IDE_FIREBASE_CREDENTIALS_PATH") or None,
                app_name=os.getenv("RL_IDE_FIREBASE_APP_NAME", "rl-ide-backend"),
            )
        except RuntimeError:
            progress = StudentProgressService()
    else:
        progress = StudentProgressService()
    execution_mode = os.getenv("RL_IDE_EXECUTION_MODE", "local").strip().lower()
    if execution_mode == "remote":
        worker_base_url = os.getenv(
            "RL_IDE_EXECUTION_WORKER_URL",
            "http://127.0.0.1:8100",
        )
        execution = RemoteExecutionService(
            worker_base_url=worker_base_url,
            internal_token=os.getenv("RL_IDE_INTERNAL_TOKEN"),
            timeout_seconds=float(os.getenv("RL_IDE_WORKER_TIMEOUT_SECONDS", "10")),
        )
        workspace = RemoteWorkspaceService(
            worker_base_url=worker_base_url,
            internal_token=os.getenv("RL_IDE_INTERNAL_TOKEN"),
            timeout_seconds=float(os.getenv("RL_IDE_WORKER_TIMEOUT_SECONDS", "10")),
        )
    else:
        execution = LocalExecutionService(progress_service=progress)
        workspace = None

    return ServiceContainer(
        lesson_catalog=LessonCatalogService(),
        progress=progress,
        quiz=QuizService(progress),
        execution=execution,
        workspace=workspace,
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
    display_name: str = Field(default="", max_length=80)
    password: str = Field(default="", max_length=128)
    firebase_id_token: Optional[str] = None


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


class WorkspaceSessionCreateRequest(BaseModel):
    lesson_id: str


class WorkspaceFileUpdateRequest(BaseModel):
    content: str


def _close_if_present(service: Any) -> None:
    close = getattr(service, "close", None)
    if callable(close):
        close()


def create_app(services: Optional[ServiceContainer] = None) -> FastAPI:
    svc = services or _build_services()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            yield
        finally:
            _close_if_present(svc.workspace)
            _close_if_present(svc.execution)
            _close_if_present(svc.quiz)
            _close_if_present(svc.progress)

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

    @app.get("/lessons")
    def get_lessons():
        return {"lessons": svc.lesson_catalog.list_lessons()}

    @app.get("/workspace/editor-shell")
    def workspace_editor_shell():
        return HTMLResponse(build_editor_shell_html())

    @app.get("/workspace/health")
    def workspace_health():
        if svc.workspace is None:
            return {
                "ready": False,
                "runtime_mode": "docker",
                "worker_reachable": False,
                "docker_cli_available": False,
                "docker_daemon_reachable": False,
                "message": "Workspace runtime requires remote execution mode.",
                "issues": ["Set RL_IDE_EXECUTION_MODE=remote and start the worker."],
            }
        try:
            health = svc.workspace.health()
        except WorkspaceRuntimeError as error:
            detail = error.detail if isinstance(error.detail, dict) else {"message": str(error.detail)}
            message = detail.get("message", "Workspace worker unavailable.")
            issues = detail.get("issues", [message])
            return {
                "ready": False,
                "runtime_mode": "docker",
                "worker_reachable": False,
                "docker_cli_available": False,
                "docker_daemon_reachable": False,
                "message": message,
                "issues": issues,
            }

        return {
            "worker_reachable": True,
            **health,
        }

    @app.post("/auth/sign-in")
    def sign_in(request: StudentSignInRequest):
        try:
            return svc.progress.sign_in(
                request.display_name,
                request.password,
                request.firebase_id_token,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=500, detail=str(error)) from error

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

    def _workspace_service() -> RemoteWorkspaceService:
        if svc.workspace is None:
            raise HTTPException(
                status_code=503,
                detail="Workspace runtime requires remote execution mode.",
            )
        return svc.workspace

    @app.post("/workspace/sessions")
    def create_workspace_session(request: WorkspaceSessionCreateRequest):
        try:
            return _workspace_service().create_session(request.lesson_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.get("/workspace/sessions/{session_id}")
    def get_workspace_session(session_id: str):
        try:
            return _workspace_service().get_session(session_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.get("/workspace/sessions/{session_id}/files/{path:path}")
    def get_workspace_file(session_id: str, path: str):
        try:
            return _workspace_service().get_file(session_id, path)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.put("/workspace/sessions/{session_id}/files/{path:path}")
    def update_workspace_file(
        session_id: str,
        path: str,
        request: WorkspaceFileUpdateRequest,
    ):
        try:
            return _workspace_service().update_file(session_id, path, request.content)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.post("/workspace/sessions/{session_id}/run")
    def run_workspace_script(session_id: str):
        try:
            return _workspace_service().run_script(session_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.get("/workspace/sessions/{session_id}/runs/{run_id}")
    def get_workspace_run(session_id: str, run_id: str):
        try:
            return _workspace_service().get_run(session_id, run_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.websocket("/workspace/sessions/{session_id}/console")
    async def workspace_console(websocket: WebSocket, session_id: str):
        if svc.workspace is None:
            await websocket.close(code=1013)
            return

        worker_base_url = os.getenv(
            "RL_IDE_EXECUTION_WORKER_URL",
            "http://127.0.0.1:8100",
        ).rstrip("/")
        worker_ws_url = worker_base_url.replace("http://", "ws://").replace(
            "https://",
            "wss://",
        ) + f"/internal/workspace/sessions/{session_id}/console"

        headers = {}
        internal_token = os.getenv("RL_IDE_INTERNAL_TOKEN")
        if internal_token:
            headers["X-Internal-Token"] = internal_token

        await websocket.accept()
        try:
            async with websocket_connect(worker_ws_url, additional_headers=headers or None) as upstream:
                async def _forward_client_messages() -> None:
                    while True:
                        message = await websocket.receive_text()
                        await upstream.send(message)

                async def _forward_worker_messages() -> None:
                    async for message in upstream:
                        await websocket.send_text(message)

                forward_client = asyncio.create_task(_forward_client_messages())
                forward_worker = asyncio.create_task(_forward_worker_messages())
                done, pending = await asyncio.wait(
                    {forward_client, forward_worker},
                    return_when=asyncio.FIRST_EXCEPTION,
                )
                for task in pending:
                    task.cancel()
                for task in done:
                    task.result()
        except WebSocketDisconnect:
            return
        except Exception:
            await websocket.close(code=1011)

    return app
