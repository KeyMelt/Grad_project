from __future__ import annotations

import asyncio
from urllib.parse import urlencode
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from websockets.asyncio.client import connect as websocket_connect

from backend.api_gateway.editor_shell import build_editor_shell_html
from backend.api_gateway.schemas import WorkspaceFileUpdateRequest, WorkspaceSessionCreateRequest
from backend.auth.dependencies import (
    assert_owner_or_admin,
    build_current_principal_dependency,
    build_optional_principal_dependency,
    require_roles,
)
from backend.auth.roles import AccountStatus, PlatformRole, Principal
from backend.services.remote_workspace_service import RemoteWorkspaceService
from backend.services.workspace_service import WorkspaceRuntimeError
from backend.settings import GatewaySettings


def build_workspace_router(services: Any) -> APIRouter:
    router = APIRouter()
    current_principal = build_current_principal_dependency(
        auth_service=services.auth,
        audit_service=getattr(services, "audit", None),
    )
    optional_principal = build_optional_principal_dependency(auth_service=services.auth)
    workspace_principal = require_roles(
        current_principal,
        PlatformRole.STUDENT,
        PlatformRole.INSTRUCTOR,
        PlatformRole.ADMIN,
    )

    def _workspace_service() -> RemoteWorkspaceService:
        if services.workspace is None:
            raise HTTPException(
                status_code=503,
                detail="Workspace runtime requires remote execution mode.",
            )
        return services.workspace

    def _workspace_session(session_id: str) -> dict[str, Any]:
        try:
            return _workspace_service().get_session(session_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    def _authorize_with_launch_token(session_id: str, launch_token: str | None) -> Principal | None:
        if not launch_token:
            return None
        token_service = getattr(services, "shell_tokens", None)
        if token_service is None:
            raise HTTPException(status_code=503, detail="Shell token service unavailable.")
        try:
            token_payload = token_service.verify_launch(launch_token)
        except Exception as error:  # noqa: BLE001
            raise HTTPException(status_code=401, detail=str(error)) from error

        if token_payload["session_id"] != session_id:
            raise HTTPException(status_code=403, detail="Shell token session mismatch.")

        return Principal(
            id=token_payload["user_id"],
            role=PlatformRole(token_payload["role"]),
            status=AccountStatus.ACTIVE,
            firebase_uid=None,
        )

    def _authorize_with_shell_token(session_id: str, shell_token: str | None) -> Principal | None:
        if not shell_token:
            return None
        token_service = getattr(services, "shell_tokens", None)
        if token_service is None:
            raise HTTPException(status_code=503, detail="Shell token service unavailable.")
        try:
            token_payload = token_service.verify(shell_token)
        except Exception as error:  # noqa: BLE001
            raise HTTPException(status_code=401, detail=str(error)) from error

        if token_payload["session_id"] != session_id:
            raise HTTPException(status_code=403, detail="Shell token session mismatch.")

        return Principal(
            id=token_payload["user_id"],
            role=PlatformRole(token_payload["role"]),
            status=AccountStatus.ACTIVE,
            firebase_uid=None,
        )

    def _authorize_workspace_access(
        *,
        session_id: str,
        principal: Principal | None,
        shell_token: str | None,
    ) -> Principal:
        shell_principal = _authorize_with_shell_token(session_id, shell_token)
        effective = shell_principal or principal
        if effective is None:
            raise HTTPException(status_code=401, detail="Authentication required.")
        session = _workspace_session(session_id)
        owner_user_id = str(session.get("owner_user_id") or "")
        assert_owner_or_admin(principal=effective, owner_user_id=owner_user_id)
        return effective

    @router.get("/workspace/editor-shell")
    def workspace_editor_shell(
        session_id: str = Query(..., min_length=1),
        launch_token: str | None = Query(default=None),
        principal: Principal | None = Depends(optional_principal),
    ):
        effective_principal = _authorize_with_launch_token(session_id, launch_token) or principal
        if effective_principal is None:
            raise HTTPException(status_code=401, detail="Authentication required.")
        if effective_principal.role not in {
            PlatformRole.STUDENT,
            PlatformRole.INSTRUCTOR,
            PlatformRole.ADMIN,
        }:
            raise HTTPException(status_code=403, detail="Insufficient role for workspace shell.")
        session = _workspace_session(session_id)
        assert_owner_or_admin(
            principal=effective_principal,
            owner_user_id=str(session.get("owner_user_id") or ""),
        )
        token_service = getattr(services, "shell_tokens", None)
        if token_service is None:
            raise HTTPException(status_code=503, detail="Shell token service unavailable.")
        shell_token = token_service.issue(
            user_id=effective_principal.id,
            role=effective_principal.role.value,
            session_id=session_id,
            ttl_seconds=300,
        )
        return HTMLResponse(
            build_editor_shell_html(
                session_id=session_id,
                shell_token=shell_token,
            )
        )

    @router.get("/workspace/sessions/{session_id}/editor-shell")
    def get_workspace_editor_shell_url(
        session_id: str,
        principal: Principal = Depends(workspace_principal),
    ):
        session = _workspace_session(session_id)
        assert_owner_or_admin(
            principal=principal,
            owner_user_id=str(session.get("owner_user_id") or ""),
        )
        token_service = getattr(services, "shell_tokens", None)
        if token_service is None:
            raise HTTPException(status_code=503, detail="Shell token service unavailable.")
        launch_token = token_service.issue_launch(
            user_id=principal.id,
            role=principal.role.value,
            session_id=session_id,
            ttl_seconds=300,
        )
        query = urlencode(
            {
                "session_id": session_id,
                "launch_token": launch_token,
            }
        )
        return {"editor_shell_url": f"/workspace/editor-shell?{query}"}

    @router.get("/workspace/health")
    def workspace_health(_principal: Principal = Depends(workspace_principal)):
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
    def create_workspace_session(
        request: WorkspaceSessionCreateRequest,
        principal: Principal = Depends(workspace_principal),
    ):
        try:
            return _workspace_service().create_session(
                request.lesson_id,
                owner_user_id=principal.id,
                owner_role=principal.role.value,
            )
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.get("/workspace/sessions/{session_id}")
    def get_workspace_session(
        session_id: str,
        shell_token: str | None = Query(default=None),
        principal: Principal | None = Depends(optional_principal),
    ):
        _authorize_workspace_access(
            session_id=session_id,
            principal=principal,
            shell_token=shell_token,
        )
        return _workspace_session(session_id)

    @router.get("/workspace/sessions/{session_id}/files/{path:path}")
    def get_workspace_file(
        session_id: str,
        path: str,
        shell_token: str | None = Query(default=None),
        principal: Principal | None = Depends(optional_principal),
    ):
        _authorize_workspace_access(
            session_id=session_id,
            principal=principal,
            shell_token=shell_token,
        )
        try:
            return _workspace_service().get_file(session_id, path)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.put("/workspace/sessions/{session_id}/files/{path:path}")
    def update_workspace_file(
        session_id: str,
        path: str,
        request: WorkspaceFileUpdateRequest,
        shell_token: str | None = Query(default=None),
        principal: Principal | None = Depends(optional_principal),
    ):
        _authorize_workspace_access(
            session_id=session_id,
            principal=principal,
            shell_token=shell_token,
        )
        try:
            return _workspace_service().update_file(session_id, path, request.content)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.post("/workspace/sessions/{session_id}/run")
    def run_workspace_script(
        session_id: str,
        shell_token: str | None = Query(default=None),
        principal: Principal | None = Depends(optional_principal),
    ):
        _authorize_workspace_access(
            session_id=session_id,
            principal=principal,
            shell_token=shell_token,
        )
        try:
            return _workspace_service().run_script(session_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.get("/workspace/sessions/{session_id}/runs/{run_id}")
    def get_workspace_run(
        session_id: str,
        run_id: str,
        shell_token: str | None = Query(default=None),
        principal: Principal | None = Depends(optional_principal),
    ):
        _authorize_workspace_access(
            session_id=session_id,
            principal=principal,
            shell_token=shell_token,
        )
        try:
            return _workspace_service().get_run(session_id, run_id)
        except WorkspaceRuntimeError as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    @router.websocket("/workspace/sessions/{session_id}/console")
    async def workspace_console(websocket: WebSocket, session_id: str):
        if services.workspace is None:
            await websocket.close(code=1013)
            return

        shell_token = websocket.query_params.get("shell_token")
        try:
            _authorize_with_shell_token(session_id, shell_token)
        except HTTPException:
            await websocket.close(code=4401)
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
