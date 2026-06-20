from __future__ import annotations

import os
from typing import Any, Callable
from urllib.parse import urlparse

import requests

from backend.replay_contract import normalize_replay_state


def manim_service_base_url() -> str:
    return os.environ.get("RL_IDE_MANIM_SERVICE_URL", "http://localhost:8200").rstrip("/")


def manim_service_netloc() -> str:
    raw = manim_service_base_url()
    parsed = urlparse(raw)
    return parsed.netloc or parsed.path


def get_manim_job(
    job_id: str,
    *,
    base_url: str | None = None,
    timeout_seconds: float | None = None,
    http_get: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    client = http_get or requests.get
    response = client(
        f"{(base_url or manim_service_base_url()).rstrip('/')}/jobs/{job_id}",
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return response.json()


def replay_status_payload(
    job_data: dict[str, Any],
    *,
    job_id: str,
    base_url: str | None = None,
) -> dict[str, Any]:
    resolved_base_url = (base_url or manim_service_base_url()).rstrip("/")
    video_url = job_data.get("video_url") or ""
    video_path = ""
    if isinstance(video_url, str) and video_url:
        video_path = (
            f"{resolved_base_url}{video_url}"
            if video_url.startswith("/")
            else video_url
        )
    raw_status = str(job_data.get("status") or "unknown")
    error = job_data.get("error")
    return {
        "job_id": str(job_data.get("job_id") or job_id),
        "status": raw_status,
        "replay_state": normalize_replay_state(
            raw_status,
            video_path=video_path,
            error=error,
        ),
        "video_path": video_path,
        "video_url": video_path,
        "error": error,
    }


def enrich_snapshot_with_replay(
    snapshot: dict[str, Any],
    *,
    base_url: str | None = None,
    timeout_seconds: float | None = None,
    http_get: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    result = snapshot.get("result")
    if not isinstance(result, dict):
        return snapshot

    replay_render_job_id = str(result.get("replay_render_job_id") or "").strip()
    if not replay_render_job_id:
        return snapshot

    try:
        job_data = get_manim_job(
            replay_render_job_id,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            http_get=http_get,
        )
    except requests.RequestException:
        return snapshot

    replay = replay_status_payload(
        job_data,
        job_id=replay_render_job_id,
        base_url=base_url,
    )
    updated_snapshot = dict(snapshot)
    updated_result = dict(result)
    resolved_video_path = str(replay["video_path"] or updated_result.get("video_path") or "")
    updated_result["replay_render_status"] = replay["status"]
    updated_result["replay_state"] = normalize_replay_state(
        replay["status"],
        video_path=resolved_video_path,
        error=replay["error"],
    )
    updated_result["video_path"] = resolved_video_path
    updated_result["visualization_ready"] = updated_result["replay_state"] == "ready"
    updated_snapshot["result"] = updated_result
    return updated_snapshot
