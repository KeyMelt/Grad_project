from __future__ import annotations

from typing import Any, Optional

import requests

from backend.execution_runtime import ExecutionPipelineError
from backend.services.replay_status_service import enrich_snapshot_with_replay


class RemoteExecutionService:
    """Gateway-side adapter that proxies execution jobs to a worker service."""

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

    def submit(self, submission_payload: dict[str, Any]) -> dict[str, str]:
        response = self._request(
            "POST",
            "/internal/jobs",
            json=submission_payload,
            expect_error=False,
        )
        return response.json()

    def snapshot(self, task_id: str) -> Optional[dict[str, Any]]:
        response = self._request(
            "GET",
            f"/internal/jobs/{task_id}",
            expect_error=False,
        )
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            self._raise_pipeline_error(response)
        return enrich_snapshot_with_replay(
            response.json(),
            timeout_seconds=self._timeout_seconds,
        )

    def execute_sync(self, submission_payload: dict[str, Any]) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/internal/execute",
            json=submission_payload,
            expect_error=False,
        )
        if response.status_code >= 400:
            self._raise_pipeline_error(response)
        return response.json()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        expect_error: bool = False,
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
            raise ExecutionPipelineError(
                status_code=503,
                detail={
                    "message": "Execution worker unavailable.",
                    "issues": [str(error)],
                },
            ) from error

        if not expect_error and response.status_code >= 500:
            self._raise_pipeline_error(response)
        return response

    def _raise_pipeline_error(self, response: requests.Response) -> None:
        detail: Any
        try:
            payload = response.json()
            detail = payload.get("detail", payload)
        except ValueError:
            detail = response.text or "Worker request failed."

        raise ExecutionPipelineError(
            status_code=response.status_code,
            detail=detail,
        )
