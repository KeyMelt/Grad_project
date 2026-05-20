"""Worker loop that consumes the queue and dispatches Manim renders.

Concept videos are rendered by invoking the Manim CLI as a subprocess in the
dedicated Manim venv (`settings.MANIM_PYTHON`), then the resulting MP4 is
copied into the shared media directory under its canonical name.

Trace rendering is not yet implemented — the trace pipeline is the subject of
a separate plan. Trace jobs fail cleanly with a descriptive error so the API
contract is honoured today even though the renderer is not.
"""
from __future__ import annotations

import logging
import os
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from manim_service import settings
from manim_service.jobs.queue import Job, JobKind, JobQueue, get_queue
from manim_service.storage import output as storage

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]

KNOWN_LESSON_IDS = frozenset(
    {
        "dp_policy_eval",
        "dp_policy_improvement",
        "dp_value_iteration",
        "mc_first_visit",
        "td_sarsa",
        "td_q_learning",
    }
)


@dataclass(frozen=True)
class SceneRef:
    scene_file: Path
    scene_class: str


# Lesson → scene registry. New entries are added as scenes are authored.
# Empty after the 2026-05-20 supersession — all six concept scenes will be
# (re)authored by the upcoming pipeline run and registered here by Step 13.
CONCEPT_VIDEO_SCENES: dict[str, SceneRef] = {
    "dp_policy_eval": SceneRef(
        scene_file=ROOT / "manim_service" / "concept_videos" / "dp_policy_eval_concept.py",
        scene_class="PolicyEvaluationConcept",
    ),
}

QUALITY_TO_DIR = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}


class RenderError(RuntimeError):
    pass


def has_scene(lesson_id: str) -> bool:
    return lesson_id in CONCEPT_VIDEO_SCENES


def process_job(job: Job) -> str:
    """Render `job` and return the final video path. Raises `RenderError` on failure."""
    if job.kind == JobKind.CONCEPT_VIDEO:
        lesson_id = job.payload["lesson_id"]
        force = bool(job.payload.get("force", False))
        return str(_render_concept_video(lesson_id=lesson_id, force=force))
    if job.kind == JobKind.TRACE:
        raise RenderError(
            "Trace rendering is not yet implemented in manim_service. "
            "The trace pipeline is deferred to a separate plan."
        )
    raise RenderError(f"Unknown job kind: {job.kind!r}")


def _render_concept_video(*, lesson_id: str, force: bool) -> Path:
    if lesson_id not in CONCEPT_VIDEO_SCENES:
        raise RenderError(
            f"No concept-video scene registered for lesson_id={lesson_id!r}. "
            f"Available: {sorted(CONCEPT_VIDEO_SCENES)}"
        )
    scene = CONCEPT_VIDEO_SCENES[lesson_id]
    output_path = storage.concept_video_path(lesson_id)

    if output_path.is_file() and not force:
        logger.info("Concept video already exists; skipping render: %s", output_path)
        return output_path

    rendered = _invoke_manim(scene.scene_file, scene.scene_class)
    silent_path = storage.store_rendered_video(rendered, output_path)

    # Mux narration if the Voice & BGM agent has already delivered the script.
    # This is best-effort: if the narration script is missing, we leave the
    # silent MP4 in place and the Voice & BGM agent will fill it in later.
    narrated = _maybe_mux_narration(lesson_id=lesson_id, silent_mp4=silent_path)
    return narrated or silent_path


def _maybe_mux_narration(*, lesson_id: str, silent_mp4: Path) -> Path | None:
    """Run the audio pipeline if the narration script is ready.

    Returns the path to the narrated MP4 on success, or None if the
    narration script is missing or the synthesis subprocess fails (in
    which case the caller falls back to the silent MP4).
    """
    narration_script = (
        ROOT
        / "manim_service"
        / "concept_videos"
        / f"{lesson_id}_narration_script.md"
    )
    if not narration_script.is_file():
        logger.info(
            "No narration script at %s — leaving silent MP4 in place.",
            narration_script,
        )
        return None

    narrated_output = silent_mp4.with_name(silent_mp4.stem + "_narrated.mp4")
    cmd = [
        settings.MANIM_PYTHON,
        "-m",
        "manim_service.audio.synthesize",
        "--narration",
        str(narration_script),
        "--silent-mp4",
        str(silent_mp4),
        "--output",
        str(narrated_output),
        "--lesson-id",
        lesson_id,
    ]
    # If the Manim Expert emitted phase_timestamps.json, pass it in.
    phase_sidecar = silent_mp4.with_name("phase_timestamps.json")
    if not phase_sidecar.exists():
        # Fall back to the location next to the original render
        rendered_dir = (
            ROOT
            / "manim_service"
            / "_manim_media"
            / "videos"
            / silent_mp4.stem.replace(f"_concept", "_concept")  # no-op, future-proofs naming
        )
        for candidate in rendered_dir.rglob("phase_timestamps.json"):
            phase_sidecar = candidate
            break
    if phase_sidecar.exists():
        cmd.extend(["--phase-timestamps", str(phase_sidecar)])

    env = dict(os.environ)
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    logger.info("Invoking narration synthesis: %s", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True, cwd=str(ROOT), env=env)
    except subprocess.CalledProcessError as exc:
        logger.warning(
            "Narration synthesis failed (exit %d) — keeping silent MP4. "
            "QA gate D28 will flag this and route back to Voice & BGM.",
            exc.returncode,
        )
        return None

    if not narrated_output.is_file():
        logger.warning(
            "Synthesis subprocess succeeded but %s was not created.",
            narrated_output,
        )
        return None

    logger.info("Narrated MP4 ready: %s", narrated_output)
    return narrated_output


def _invoke_manim(scene_file: Path, scene_class: str) -> Path:
    if not scene_file.is_file():
        raise RenderError(f"Scene file not found: {scene_file}")
    if not Path(settings.MANIM_PYTHON).exists():
        raise RenderError(f"Manim python interpreter not found: {settings.MANIM_PYTHON}")

    quality_flag = f"-q{settings.RENDER_QUALITY}"
    quality_dir = QUALITY_TO_DIR.get(settings.RENDER_QUALITY)
    if quality_dir is None:
        raise RenderError(
            f"Unknown RENDER_QUALITY={settings.RENDER_QUALITY!r}; "
            f"expected one of {sorted(QUALITY_TO_DIR)}"
        )

    media_dir = ROOT / "manim_service" / "_manim_media"
    media_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        settings.MANIM_PYTHON,
        "-m",
        "manim",
        quality_flag,
        "--media_dir",
        str(media_dir),
        str(scene_file),
        scene_class,
    ]

    env = dict(os.environ)
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)

    logger.info("Invoking Manim: %s", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True, cwd=str(ROOT), env=env)
    except subprocess.CalledProcessError as error:
        raise RenderError(
            f"Manim render failed (exit code {error.returncode}) for "
            f"{scene_file.name}:{scene_class}"
        ) from error

    rendered = media_dir / "videos" / scene_file.stem / quality_dir / f"{scene_class}.mp4"
    if not rendered.is_file():
        raise RenderError(f"Expected render output not found: {rendered}")
    return rendered


def run_worker_loop(
    queue: JobQueue | None = None,
    *,
    stop_event: threading.Event | None = None,
    poll_timeout: float = 1.0,
    on_job: Callable[[Job], None] | None = None,
) -> None:
    """Pop jobs and process them until `stop_event` is set."""
    q = queue or get_queue()
    storage.ensure_subdirs()
    stop_event = stop_event or threading.Event()
    while not stop_event.is_set():
        job = q.pop(timeout=poll_timeout)
        if job is None:
            continue
        try:
            q.mark_rendering(job.job_id)
            video_path = process_job(job)
            q.mark_complete(job.job_id, video_path=video_path)
            logger.info("Job %s complete: %s", job.job_id, video_path)
        except Exception as error:  # noqa: BLE001 — surface any render failure as job error
            q.mark_failed(job.job_id, error=str(error))
            logger.exception("Job %s failed", job.job_id)
        finally:
            if on_job is not None:
                on_job(job)


def start_background_worker(queue: JobQueue | None = None) -> tuple[threading.Thread, threading.Event]:
    """Start `run_worker_loop` on a daemon thread. Returns (thread, stop_event)."""
    stop_event = threading.Event()
    thread = threading.Thread(
        target=run_worker_loop,
        kwargs={"queue": queue, "stop_event": stop_event},
        name="manim-render-worker",
        daemon=True,
    )
    thread.start()
    return thread, stop_event
