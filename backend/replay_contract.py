from __future__ import annotations

from typing import Any

_NORMALIZED_REPLAY_STATES = {
    "queued",
    "rendering",
    "ready",
    "failed",
    "timeout",
    "unavailable",
}


def normalize_replay_state(
    raw_status: str | None,
    *,
    video_path: str | None = None,
    error: Any = None,
) -> str:
    normalized_path = str(video_path or "").strip()
    normalized_status = str(raw_status or "").strip().lower()

    if normalized_path:
        return "ready"
    if normalized_status == "idle":
        return "idle"
    if normalized_status == "ready":
        return "unavailable"
    if normalized_status in _NORMALIZED_REPLAY_STATES:
        return normalized_status
    if normalized_status == "complete":
        return "unavailable"
    if error:
        return "failed"
    return "unavailable"
