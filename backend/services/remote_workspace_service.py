from __future__ import annotations

from typing import Any

import requests

from backend.services.workspace_service import WorkspaceRuntimeError


class RemoteWorkspaceService:
    """Gateway-side adapter for worker-owned workspace APIs."""

    def __init__(
        self,
        *,
        worker_base_url: str,
        internal_token: str | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._worker_base_url = worker_base_url.rstrip("/")
        self._internal_token = internal_token
        self._timeout_seconds = timeout_seconds

    def create_session(
        self,
        lesson_id: str,
        *,
        owner_user_id: str,
        owner_role: str,
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/internal/workspace/sessions",
            json={
                "lesson_id": lesson_id,
                "owner_user_id": owner_user_id,
                "owner_role": owner_role,
            },
        )
        return response.json()

    def health(self) -> dict[str, Any]:
        response = self._request(
            "GET",
            "/internal/workspace/health",
        )
        return response.json()

    def get_session(self, session_id: str) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/internal/workspace/sessions/{session_id}",
        )
        return response.json()

    def get_file(self, session_id: str, path: str) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/internal/workspace/sessions/{session_id}/files/{path}",
        )
        return response.json()

    def update_file(self, session_id: str, path: str, content: str) -> dict[str, Any]:
        response = self._request(
            "PUT",
            f"/internal/workspace/sessions/{session_id}/files/{path}",
            json={"content": content},
        )
        return response.json()

    def run_script(self, session_id: str) -> dict[str, Any]:
        response = self._request(
            "POST",
            f"/internal/workspace/sessions/{session_id}/run",
        )
        return response.json()

    def get_run(self, session_id: str, run_id: str) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/internal/workspace/sessions/{session_id}/runs/{run_id}",
        )
        return response.json()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> requests.Response:
        headers: dict[str, str] = {}
        if self._internal_token:
            headers["X-Internal-Token"] = self._internal_token

        try:
            response = requests.request(
                method=method,
                url=f"{self._worker_base_url}{path}",
                json=json,
                headers=headers,
                timeout=self._timeout_seconds,
            )
        except requests.RequestException as error:
            raise WorkspaceRuntimeError(
                status_code=503,
                detail={
                    "message": "Workspace worker unavailable.",
                    "issues": [str(error)],
                },
            ) from error

        if response.status_code >= 400:
            detail: Any
            try:
                payload = response.json()
                detail = payload.get("detail", payload)
            except ValueError:
                detail = response.text or "Workspace worker request failed."
            raise WorkspaceRuntimeError(status_code=response.status_code, detail=detail)

        return response
