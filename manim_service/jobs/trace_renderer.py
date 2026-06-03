"""Trace render pipeline with content-hash caching.

Usage::

    from manim_service.jobs.trace_renderer import render_trace
    output_path = render_trace(job)

``render_trace`` returns a ``Path`` to the finished MP4 and is safe to call
from the worker thread.  It de-duplicates identical renders via a sha256
content hash so that repeated replays of the same lesson + steps skip the
Manim subprocess entirely.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from manim_service import settings
from manim_service.jobs.queue import Job
from manim_service.storage import output as storage

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
TRACE_SCENE_FILE = ROOT / "manim_service" / "trace_scenes" / "trace_replay_scene.py"
TRACE_SCENE_CLASS = "TraceReplayScene"
TRACE_VISUAL_HELPERS = (ROOT / "manim_service" / "scenes" / "rl_visuals.py",)

QUALITY_TO_DIR: dict[str, str] = {
    "l": "480p15",
    "m": "720p30",
    "h": "1080p60",
    "k": "2160p60",
}


# ---------------------------------------------------------------------------
# Local RenderError (avoids circular import from worker)
# ---------------------------------------------------------------------------

class RenderError(RuntimeError):
    """Raised when the Manim subprocess fails or the render payload is invalid."""


# ---------------------------------------------------------------------------
# Content-hash helpers
# ---------------------------------------------------------------------------

def _source_signature() -> str:
    h = hashlib.sha256()
    h.update(settings.RENDER_QUALITY.encode())
    for path in (TRACE_SCENE_FILE, *TRACE_VISUAL_HELPERS):
        h.update(str(path).encode())
        try:
            h.update(path.read_bytes())
        except OSError:
            h.update(b"<missing>")
    return h.hexdigest()


def _compute_trace_hash(lesson_id: str, steps: list) -> str:
    """Stable sha256 hash of (lesson_id, steps).

    The hash is deterministic: the steps list is serialised with sorted keys
    so that dict insertion order never affects the result.

    Args:
        lesson_id: identifier for the lesson (e.g. ``"td_q_learning"``).
        steps: list of step dicts as produced by the trace-log pipeline.

    Returns:
        First 16 hex characters of the sha256 digest (64 bits of collision
        resistance — sufficient for a local file-system cache).
    """
    payload = (
        lesson_id
        + _source_signature()
        + json.dumps(steps, sort_keys=True, default=str)
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _canonical_cache_path(lesson_id: str, trace_hash: str) -> Path:
    """Path of the canonical (content-addressed) cache entry."""
    return settings.SHARED_MEDIA_DIR / storage.TRACES_SUBDIR / f"{lesson_id}_{trace_hash}.mp4"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def render_trace(job: Job) -> Path:
    """Render a TRACE job and return the path to the finished MP4.

    Pipeline:
        1. Validate the payload.
        2. Compute a sha256 content hash of (lesson_id, steps).
        3. Cache hit  → copy the canonical file to the job-specific path,
           return immediately (no Manim invocation).
        4. Cache miss → write steps to a temp JSON file, invoke Manim,
           store the result at the job-specific path, and copy to the
           canonical cache entry for future reuse.

    Args:
        job: a ``Job`` with ``kind == JobKind.TRACE`` and a payload
             containing at least ``lesson_id`` (str) and ``steps`` (list).

    Returns:
        ``Path`` to the final MP4 (always the job-specific path).

    Raises:
        RenderError: if the payload is invalid, steps is empty, the scene
                     file is missing, or the Manim subprocess fails.
    """
    # ------------------------------------------------------------------
    # 1. Extract and validate payload
    # ------------------------------------------------------------------
    lesson_id: str = job.payload.get("lesson_id", "")
    episode_trace: dict = job.payload.get("episode_trace", {})
    steps: list = episode_trace.get("steps", [])
    job_id: str = job.job_id

    if not lesson_id:
        raise RenderError("Trace job payload is missing 'lesson_id'.")
    if not steps:
        raise RenderError("Trace job has empty steps list — nothing to render.")

    storage.ensure_subdirs()

    # ------------------------------------------------------------------
    # 2. Content hash
    # ------------------------------------------------------------------
    trace_hash = _compute_trace_hash(lesson_id, steps)
    canonical = _canonical_cache_path(lesson_id, trace_hash)
    job_path = storage.trace_video_path(job_id)

    # ------------------------------------------------------------------
    # 3. Cache hit
    # ------------------------------------------------------------------
    if canonical.is_file():
        logger.info(
            "Trace cache hit for %s (hash=%s); copying to %s",
            lesson_id,
            trace_hash,
            job_path,
        )
        shutil.copy2(canonical, job_path)
        storage.publish_media_file(job_path)
        return job_path

    # ------------------------------------------------------------------
    # 4. Cache miss — render via Manim
    # ------------------------------------------------------------------
    logger.info(
        "Trace cache miss for %s (hash=%s); invoking Manim.",
        lesson_id,
        trace_hash,
    )

    with tempfile.TemporaryDirectory(prefix="trace_render_") as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Write the steps to a temp JSON file that the scene will read
        data_json = tmp_path / "trace_data.json"
        data_json.write_text(json.dumps(steps, default=str), encoding="utf-8")

        # Invoke Manim
        rendered = _invoke_trace_manim(data_json)

        # Copy to job-specific destination
        job_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(rendered, job_path)
        storage.publish_media_file(job_path)

    # Cache the result for future reuse
    try:
        canonical.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(job_path, canonical)
        logger.info("Cached trace render at %s", canonical)
    except Exception:  # noqa: BLE001
        logger.warning(
            "Could not write trace to canonical cache path %s; "
            "render still succeeded.",
            canonical,
            exc_info=True,
        )

    return job_path


# ---------------------------------------------------------------------------
# Manim invocation (mirrors _invoke_manim in worker.py)
# ---------------------------------------------------------------------------

def _invoke_trace_manim(data_json: Path) -> Path:
    """Run the Manim CLI for TraceReplayScene and return the rendered MP4 path.

    Args:
        data_json: absolute path to the JSON file containing the steps list.

    Returns:
        Path to the MP4 file that Manim wrote.

    Raises:
        RenderError: on any subprocess or file-system failure.
    """
    if not TRACE_SCENE_FILE.is_file():
        raise RenderError(f"Trace scene file not found: {TRACE_SCENE_FILE}")

    manim_python = settings.MANIM_PYTHON
    if not Path(manim_python).exists():
        raise RenderError(
            f"Manim python interpreter not found: {manim_python}"
        )

    quality = settings.RENDER_QUALITY
    quality_dir = QUALITY_TO_DIR.get(quality)
    if quality_dir is None:
        raise RenderError(
            f"Unknown RENDER_QUALITY={quality!r}; "
            f"expected one of {sorted(QUALITY_TO_DIR)}"
        )

    quality_flag = f"-q{quality}"
    media_dir = ROOT / "manim_service" / "_manim_media"
    media_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        manim_python,
        "-m",
        "manim",
        quality_flag,
        "--media_dir",
        str(media_dir),
        str(TRACE_SCENE_FILE),
        TRACE_SCENE_CLASS,
    ]

    env = dict(os.environ)
    env["PYTHONPATH"] = (
        f"{ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    )
    # Pass the data file path to the scene via environment variable
    env["TRACE_DATA_PATH"] = str(data_json)

    logger.info("Invoking Manim for trace render: %s", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True, cwd=str(ROOT), env=env)
    except subprocess.CalledProcessError as error:
        raise RenderError(
            f"Manim trace render failed (exit code {error.returncode}) for "
            f"{TRACE_SCENE_FILE.name}:{TRACE_SCENE_CLASS}"
        ) from error

    rendered = (
        media_dir
        / "videos"
        / TRACE_SCENE_FILE.stem
        / quality_dir
        / f"{TRACE_SCENE_CLASS}.mp4"
    )
    if not rendered.is_file():
        raise RenderError(
            f"Expected trace render output not found: {rendered}"
        )
    return rendered
