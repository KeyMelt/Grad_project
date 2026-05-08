from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from websockets.asyncio.client import connect as websocket_connect

from backend.api_gateway.editor_shell import build_editor_shell_html
from backend.api_gateway.schemas import WorkspaceFileUpdateRequest, WorkspaceSessionCreateRequest
from backend.services.remote_workspace_service import RemoteWorkspaceService
from backend.services.workspace_service import WorkspaceRuntimeError
from backend.settings import GatewaySettings


def build_workspace_router(services: Any) -> APIRouter:
    router = APIRouter()

    def _workspace_service() -> RemoteWorkspaceService:
        if services.workspace is None:
            raise HTTPException(
                status_code=503,
                detail="Workspace runtime requires remote execution mode.",
            )
        return services.workspace

    @router.get("/workspace/editor-shell")
    def workspace_editor_shell():
        return HTMLResponse(build_editor_shell_html())

    @router.get("/workspace/health")
    def workspace_health():
        if services.workspace is None:
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
            health = services.workspace.health()
        except WorkspaceRuntimeError as error:
            detail = (
                error.detail if isinstance(error.detail, dict) else {"message": str(error.detail)}
            )
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

    @router.post("/workspace/sessions")
    def create_workspace_session(request: WorkspaceSessionCreateRequest):
        try:
            return _workspace_service().create_session(request.lesson_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.get("/workspace/sessions/{session_id}")
    def get_workspace_session(session_id: str):
        try:
            return _workspace_service().get_session(session_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.get("/workspace/sessions/{session_id}/files/{path:path}")
    def get_workspace_file(session_id: str, path: str):
        try:
            return _workspace_service().get_file(session_id, path)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.put("/workspace/sessions/{session_id}/files/{path:path}")
    def update_workspace_file(
        session_id: str,
        path: str,
        request: WorkspaceFileUpdateRequest,
    ):
        try:
            return _workspace_service().update_file(session_id, path, request.content)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.post("/workspace/sessions/{session_id}/run")
    def run_workspace_script(session_id: str):
        try:
            return _workspace_service().run_script(session_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.get("/workspace/sessions/{session_id}/runs/{run_id}")
    def get_workspace_run(session_id: str, run_id: str):
        try:
            return _workspace_service().get_run(session_id, run_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.websocket("/workspace/sessions/{session_id}/console")
    async def workspace_console(websocket: WebSocket, session_id: str):
        if services.workspace is None:
            await websocket.close(code=1013)
            return

        worker_ws_url, headers = _workspace_console_upstream(session_id)

        await websocket.accept()
        try:
            async with websocket_connect(
                worker_ws_url,
                additional_headers=headers or None,
            ) as upstream:
                await _proxy_console_messages(websocket, upstream)
        except WebSocketDisconnect:
            return
        except Exception:
            await websocket.close(code=1011)

    return router


def _workspace_console_upstream(session_id: str) -> tuple[str, dict[str, str]]:
    settings = GatewaySettings.from_env()
    worker_base_url = settings.execution_worker_url.rstrip("/")
    worker_ws_url = (
        worker_base_url.replace("http://", "ws://").replace(
            "https://",
            "wss://",
        )
        + f"/internal/workspace/sessions/{session_id}/console"
    )

    headers = {}
    if settings.internal_token:
        headers["X-Internal-Token"] = settings.internal_token
    return worker_ws_url, headers


async def _proxy_console_messages(websocket: WebSocket, upstream: Any) -> None:
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
