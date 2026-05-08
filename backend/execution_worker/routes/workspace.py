from __future__ import annotations

import asyncio
from typing import Any, Callable

from fastapi import APIRouter, Header, HTTPException, WebSocket, WebSocketDisconnect

from backend.execution_worker.schemas import (
    WorkspaceFileUpdateRequest,
    WorkspaceSessionCreateRequest,
)
from backend.services.workspace_service import WorkspaceRuntimeError


def build_workspace_router(
    services: Any,
    assert_internal_access: Callable[[str | None], None],
) -> APIRouter:
    router = APIRouter()

    @router.post("/internal/workspace/sessions")
    async def create_workspace_session(
        request: WorkspaceSessionCreateRequest,
        x_internal_token: str | None = Header(default=None),
    ):
        assert_internal_access(x_internal_token)
        try:
            return await services.workspace.create_session(request.lesson_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.get("/internal/workspace/sessions/{session_id}")
    async def get_workspace_session(
        session_id: str,
        x_internal_token: str | None = Header(default=None),
    ):
        assert_internal_access(x_internal_token)
        try:
            return await services.workspace.get_session(session_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.get("/internal/workspace/sessions/{session_id}/files/{path:path}")
    async def get_workspace_file(
        session_id: str,
        path: str,
        x_internal_token: str | None = Header(default=None),
    ):
        assert_internal_access(x_internal_token)
        try:
            return await services.workspace.read_file(session_id, path)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.put("/internal/workspace/sessions/{session_id}/files/{path:path}")
    async def update_workspace_file(
        session_id: str,
        path: str,
        request: WorkspaceFileUpdateRequest,
        x_internal_token: str | None = Header(default=None),
    ):
        assert_internal_access(x_internal_token)
        try:
            return await services.workspace.write_file(session_id, path, request.content)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.post("/internal/workspace/sessions/{session_id}/run")
    async def run_workspace_script(
        session_id: str,
        x_internal_token: str | None = Header(default=None),
    ):
        assert_internal_access(x_internal_token)
        try:
            return await services.workspace.run_script(session_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.get("/internal/workspace/sessions/{session_id}/runs/{run_id}")
    async def get_workspace_run(
        session_id: str,
        run_id: str,
        x_internal_token: str | None = Header(default=None),
    ):
        assert_internal_access(x_internal_token)
        try:
            return await services.workspace.get_run(session_id, run_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.websocket("/internal/workspace/sessions/{session_id}/console")
    async def workspace_console(
        websocket: WebSocket,
        session_id: str,
    ):
        token = websocket.headers.get("x-internal-token")
        try:
            assert_internal_access(token)
        except HTTPException:
            await websocket.close(code=4401)
            return

        await websocket.accept()
        try:
            queue = await services.workspace.subscribe(session_id)
        except WorkspaceRuntimeError:
            await websocket.close(code=4404)
            return

        await _bridge_console(websocket, services.workspace, session_id, queue)

    return router


async def _bridge_console(
    websocket: WebSocket,
    workspace: Any,
    session_id: str,
    queue: asyncio.Queue[dict[str, Any]],
) -> None:
    async def _sender() -> None:
        while True:
            event = await queue.get()
            await websocket.send_json(event)

    async def _receiver() -> None:
        while True:
            message = await websocket.receive_text()
            await workspace.handle_console_message(session_id, message)

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
        await workspace.unsubscribe(session_id, queue)
