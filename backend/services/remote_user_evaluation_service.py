from __future__ import annotations

from typing import Any

import requests


class RemoteUserEvaluationService:
    """Gateway-side adapter for user/auth/quiz/evaluation service APIs."""

    def __init__(
        self,
        *,
        user_service_base_url: str,
        internal_token: str | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._user_service_base_url = user_service_base_url.rstrip("/")
        self._internal_token = internal_token
        self._timeout_seconds = timeout_seconds

    def sign_in(
        self,
        display_name: str,
        password: str,
        firebase_id_token: str | None = None,
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/internal/auth/sign-in",
            json={
                "display_name": display_name,
                "password": password,
                "firebase_id_token": firebase_id_token,
            },
        )
        return response.json()

    def get_dashboard(self, student_id: str) -> dict[str, Any] | None:
        response = self._request(
            "GET",
            f"/internal/students/{student_id}/dashboard",
            allow_not_found=True,
        )
        if response.status_code == 404:
            return None
        return response.json()

    def start_quiz(self, student_id: str, phase: str) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/internal/quiz/start",
            json={"student_id": student_id, "phase": phase},
        )
        return response.json()

    def submit_quiz(
        self,
        student_id: str,
        session_id: str,
        answers: list[dict[str, int]],
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/internal/quiz/submit",
            json={
                "student_id": student_id,
                "session_id": session_id,
                "answers": answers,
            },
        )
        return response.json()

    def list_n_gain_metrics(self) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "/internal/metrics/n-gain",
        )
        return list(response.json().get("rows", []))

    def close(self) -> None:
        return None

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        allow_not_found: bool = False,
    ) -> requests.Response:
        headers: dict[str, str] = {}
        if self._internal_token:
            headers["X-Internal-Token"] = self._internal_token

        try:
            response = requests.request(
                method=method,
                url=f"{self._user_service_base_url}{path}",
                json=json,
                headers=headers,
                timeout=self._timeout_seconds,
            )
        except requests.RequestException as error:
            raise RuntimeError(f"User service unavailable: {error}") from error

        if response.status_code == 404 and allow_not_found:
            return response
        if response.status_code >= 400:
            try:
                payload = response.json()
                detail = payload.get("detail", payload)
            except ValueError:
                detail = response.text or "User service request failed."
            raise ValueError(str(detail))

        return response
