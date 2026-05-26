"""Thin HTTP client for `manim_service`.

Replaces the previous in-process subprocess controller (which has been moved
into `manim_service`). The backend now only knows *what* should be rendered;
the manim service owns *how* and *where* it is rendered.

Public API is preserved so existing callers continue to work unchanged:

    controller = VisualizationController()
    url = controller.generate_animation(log_data, lesson_id)

`url` is the manim_service `/videos/{filename}` path on success, or `""` on
failure (transport error, render failure, or poll timeout).
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

try:
    import numpy as np
except ImportError:
    np = None

from backend.settings import VisualizationSettings

logger = logging.getLogger(__name__)


class VisualizationController:
    """HTTP client that submits trace renders to manim_service and polls for completion."""

    DEFAULT_BASE_URL = "http://localhost:8200"

    def __init__(
        self,
        output_dir: str | None = None,
        manim_python_path: str | None = None,
        *,
        base_url: str | None = None,
        poll_interval_seconds: float = 1.0,
        http_client: requests.Session | None = None,
    ):
        settings = VisualizationSettings.from_env()
        # output_dir and manim_python_path are retained for API compatibility
        # but no longer used here; manim_service owns those concerns.
        del output_dir
        del manim_python_path
        self.manim_timeout_seconds = settings.manim_timeout_seconds
        self.base_url = (
            base_url
            or os.environ.get("RL_IDE_MANIM_SERVICE_URL", self.DEFAULT_BASE_URL)
        ).rstrip("/")
        self.poll_interval_seconds = poll_interval_seconds
        self._http = http_client or requests

    def generate_animation(self, log_data: list, lesson_id: str) -> str:
        if not log_data or not log_data[0]:
            logger.warning("No log data provided for Manim visualization.")
            return ""

        latest_episode = log_data[-1]
        payload = {
            "lesson_id": lesson_id,
            "episode_trace": {
                "steps": [self._normalize_step(step) for step in latest_episode],
            },
        }

        try:
            job = self._post_json(f"{self.base_url}/render/trace", payload)
        except requests.RequestException as error:
            logger.error("manim_service trace enqueue failed: %s", error)
            return ""

        job_id = job.get("job_id")
        if not job_id:
            logger.error("manim_service did not return a job_id: %s", job)
            return ""

        return self._poll_until_complete(job_id)

    def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._http.post(url, json=payload, timeout=self.manim_timeout_seconds)
        response.raise_for_status()
        return response.json()

    def _poll_until_complete(self, job_id: str) -> str:
        deadline = time.monotonic() + self.manim_timeout_seconds
        url = f"{self.base_url}/jobs/{job_id}"
        while time.monotonic() < deadline:
            try:
                response = self._http.get(url, timeout=self.manim_timeout_seconds)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as error:
                logger.error("manim_service poll failed for job %s: %s", job_id, error)
                return ""

            status = data.get("status")
            if status == "complete":
                video_url = data.get("video_url") or ""
                if not video_url:
                    logger.error("Job %s complete but no video_url returned", job_id)
                    return ""
                return f"{self.base_url}{video_url}" if video_url.startswith("/") else video_url
            if status == "failed":
                logger.error("manim_service job %s failed: %s", job_id, data.get("error"))
                return ""
            time.sleep(self.poll_interval_seconds)

        logger.error("manim_service job %s did not complete within %ss", job_id, self.manim_timeout_seconds)
        return ""

    @staticmethod
    def _to_json_safe(value: Any) -> Any:
        if np is not None:
            if isinstance(value, np.integer):
                return int(value)
            if isinstance(value, np.floating):
                return float(value)
        if isinstance(value, dict):
            return {k: VisualizationController._to_json_safe(v) for k, v in value.items()}
        if isinstance(value, list):
            return [VisualizationController._to_json_safe(item) for item in value]
        return value

    @staticmethod
    def _normalize_step(step: dict[str, Any]) -> dict[str, Any]:
        return {
            k: VisualizationController._to_json_safe(v)
            for k, v in step.items()
        }
