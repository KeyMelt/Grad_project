"""Rendered-video storage layout.

All MP4s live under `settings.SHARED_MEDIA_DIR` in two subdirectories:

    {SHARED_MEDIA_DIR}/concept_videos/{lesson_id}_concept.mp4
    {SHARED_MEDIA_DIR}/traces/{job_id}.mp4

The naming convention preserves the legacy `backend/concept_videos/render.py`
output filename (`{lesson_id}_concept.mp4`) so existing backend code that reads
from the shared directory keeps working unchanged.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from manim_service import settings
from manim_service.storage import spaces

CONCEPT_VIDEOS_SUBDIR = "concept_videos"
TRACES_SUBDIR = "traces"


def _concept_video_media_dir() -> Path:
    if settings.CONCEPT_VIDEO_MEDIA_DIR_CONFIGURED:
        return settings.CONCEPT_VIDEO_MEDIA_DIR
    return settings.SHARED_MEDIA_DIR / CONCEPT_VIDEOS_SUBDIR


def _trace_media_dir() -> Path:
    if settings.TRACE_MEDIA_DIR_CONFIGURED:
        return settings.TRACE_MEDIA_DIR
    return settings.SHARED_MEDIA_DIR / TRACES_SUBDIR


def ensure_subdirs() -> None:
    """Make sure both output subdirectories exist."""
    _concept_video_media_dir().mkdir(parents=True, exist_ok=True)
    _trace_media_dir().mkdir(parents=True, exist_ok=True)


def concept_video_path(lesson_id: str) -> Path:
    """Canonical output path for a concept video."""
    return _concept_video_media_dir() / f"{lesson_id}_concept.mp4"


def trace_video_path(job_id: str) -> Path:
    """Canonical output path for a trace video."""
    return _trace_media_dir() / f"{job_id}.mp4"


def store_rendered_video(src: Path, dest: Path) -> Path:
    """Copy a freshly rendered MP4 into its canonical location."""
    if not src.is_file():
        raise FileNotFoundError(f"Render output not found: {src}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    publish_media_file(dest)
    return dest


def media_object_key(path: Path) -> str:
    """Return the Spaces object key for a file inside SHARED_MEDIA_DIR."""
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(_concept_video_media_dir().resolve()).as_posix()
        return f"{CONCEPT_VIDEOS_SUBDIR}/{relative}"
    except ValueError:
        pass
    try:
        relative = resolved.relative_to(_trace_media_dir().resolve()).as_posix()
        return f"{TRACES_SUBDIR}/{relative}"
    except ValueError:
        pass
    return resolved.relative_to(settings.SHARED_MEDIA_DIR.resolve()).as_posix()


def publish_media_file(path: Path) -> str | None:
    """Publish a media file to the configured remote backend, if enabled."""
    return spaces.upload_public_file(path, media_object_key(path))


def public_url_for_media_path(path: Path) -> str | None:
    """Return the CDN URL for a local media path when Spaces is configured."""
    try:
        return spaces.public_url(media_object_key(path))
    except ValueError:
        return None


def resolve_safe_video_path(filename: str) -> Path | None:
    """Resolve a filename for serving via `GET /videos/{filename}`.

    Returns `None` if the file is missing or the request attempts to escape
    the configured media root (path traversal guard).
    """
    safe_name = Path(filename).name  # strip any directory components
    if not safe_name or safe_name != filename:
        return None
    search_roots = (
        _concept_video_media_dir().resolve(),
        _trace_media_dir().resolve(),
    )
    for root in search_roots:
        candidate = (root / safe_name).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    return None
