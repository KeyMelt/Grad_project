from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from backend.job_store_sqlite import SqliteExecutionJobStore
from backend.execution_runtime import ExecutionPipelineError
from backend.services.execution_service import ExecutionService
from backend.services.student_progress_service import StudentProgressService
from backend.services.workspace_service import WorkspaceRuntimeError, WorkspaceSessionService


@dataclass(frozen=True)
class WorkerServiceContainer:
    execution: ExecutionService
    workspace: WorkspaceSessionService


def _build_services() -> WorkerServiceContainer:
    job_store_path = os.getenv(
        "RL_IDE_JOB_STORE_PATH",
        "backend/data/execution_jobs.db",
    )
    progress_service: Optional[StudentProgressService] = None
    if _truthy_env("RL_IDE_WORKER_RECORD_PROGRESS"):
        progress_service = StudentProgressService()

    return WorkerServiceContainer(
        execution=ExecutionService(
            job_store=SqliteExecutionJobStore(job_store_path),
            progress_service=progress_service,
        ),
        workspace=WorkspaceSessionService(
            base_dir=os.getenv("RL_IDE_WORKSPACE_BASE_DIR"),
            sandbox_image=os.getenv("RL_IDE_WORKSPACE_IMAGE", "python:3.11-slim"),
            use_docker=True,
        ),
    )


class CodeSubmission(BaseModel):
    lesson_id: str
    code: str
    learning_rate: Optional[float] = Field(default=None, gt=0, le=1)
    discount_factor: Optional[float] = Field(default=None, gt=0, le=1)
    exploration_rate: Optional[float] = Field(default=None, ge=0, le=1)
    episode_count: Optional[int] = Field(default=None, ge=1, le=500)
    student_id: Optional[str] = None


class WorkspaceSessionCreateRequest(BaseModel):
    lesson_id: str


class WorkspaceFileUpdateRequest(BaseModel):
    content: str


def _close_if_present(service: Any) -> None:
    close = getattr(service, "close", None)
    if callable(close):
        close()


def create_app(services: Optional[WorkerServiceContainer] = None) -> FastAPI:
    svc = services or _build_services()
    required_token = os.getenv("RL_IDE_INTERNAL_TOKEN", "").strip()

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

    @app.get("/")
    def read_root():
        return {"status": "Execution worker running"}

    @app.get("/internal/workspace/health")
    def workspace_health(
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        return svc.workspace.health_snapshot()

    @app.post("/internal/jobs")
    def submit(
        submission: CodeSubmission,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        return svc.execution.submit(submission.model_dump())

    @app.get("/internal/jobs/{task_id}")
    def snapshot(
        task_id: str,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        result = svc.execution.snapshot(task_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Unknown task_id '{task_id}'.")
        return result

    @app.post("/internal/execute")
    def execute_sync(
        submission: CodeSubmission,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return svc.execution.execute_sync(submission.model_dump())
        except ExecutionPipelineError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.post("/internal/workspace/sessions")
    async def create_workspace_session(
        request: WorkspaceSessionCreateRequest,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return await svc.workspace.create_session(request.lesson_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.get("/internal/workspace/sessions/{session_id}")
    async def get_workspace_session(
        session_id: str,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return await svc.workspace.get_session(session_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.get("/internal/workspace/sessions/{session_id}/files/{path:path}")
    async def get_workspace_file(
        session_id: str,
        path: str,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return await svc.workspace.read_file(session_id, path)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.put("/internal/workspace/sessions/{session_id}/files/{path:path}")
    async def update_workspace_file(
        session_id: str,
        path: str,
        request: WorkspaceFileUpdateRequest,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return await svc.workspace.write_file(session_id, path, request.content)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.post("/internal/workspace/sessions/{session_id}/run")
    async def run_workspace_script(
        session_id: str,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return await svc.workspace.run_script(session_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.get("/internal/workspace/sessions/{session_id}/runs/{run_id}")
    async def get_workspace_run(
        session_id: str,
        run_id: str,
        x_internal_token: str | None = Header(default=None),
    ):
        _assert_internal_access(x_internal_token)
        try:
            return await svc.workspace.get_run(session_id, run_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @app.websocket("/internal/workspace/sessions/{session_id}/console")
    async def workspace_console(
        websocket: WebSocket,
        session_id: str,
    ):
        token = websocket.headers.get("x-internal-token")
        try:
            _assert_internal_access(token)
        except HTTPException:
            await websocket.close(code=4401)
            return

        await websocket.accept()
        try:
            queue = await svc.workspace.subscribe(session_id)
        except WorkspaceRuntimeError:
            await websocket.close(code=4404)
            return

        async def _sender() -> None:
            while True:
                event = await queue.get()
                await websocket.send_json(event)

        async def _receiver() -> None:
            while True:
                message = await websocket.receive_text()
                await svc.workspace.handle_console_message(session_id, message)

        sender_task = asyncio.create_task(_sender())
        receiver_task = asyncio.create_task(_receiver())
        try:
            await asyncio.wait(
                {sender_task, receiver_task},
                return_when=asyncio.FIRST_EXCEPTION,
            )
        except WebSocketDisconnect:
            pass
        finally:
            sender_task.cancel()
            receiver_task.cancel()
            await svc.workspace.unsubscribe(session_id, queue)

    return app


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}
