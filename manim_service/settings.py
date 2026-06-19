"""manim_service configuration."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENVIRONMENT: str = os.environ.get("RL_IDE_ENV", "development").lower()
IS_PRODUCTION: bool = ENVIRONMENT in {"prod", "production"}

# Path to the manim venv python binary
MANIM_PYTHON: str = os.environ.get("MANIM_PYTHON", sys.executable)


def resolve_executable(command: str) -> str | None:
    """Return an executable path for an absolute path or PATH command."""
    command_path = Path(command)
    if command_path.exists():
        return str(command_path)
    return shutil.which(command)


# Shared media output directory (backend reads from same path)
SHARED_MEDIA_DIR: Path = Path(
    os.environ.get("SHARED_MEDIA_DIR", str(PROJECT_ROOT / "backend" / "media"))
)
CONCEPT_VIDEO_MEDIA_DIR_CONFIGURED: bool = "CONCEPT_VIDEO_MEDIA_DIR" in os.environ
CONCEPT_VIDEO_MEDIA_DIR: Path = Path(
    os.environ.get(
        "CONCEPT_VIDEO_MEDIA_DIR",
        str(SHARED_MEDIA_DIR / "concept_videos"),
    )
)
TRACE_MEDIA_DIR_CONFIGURED: bool = "TRACE_MEDIA_DIR" in os.environ
TRACE_MEDIA_DIR: Path = Path(
    os.environ.get(
        "TRACE_MEDIA_DIR",
        str(SHARED_MEDIA_DIR / "traces"),
    )
)

# Scratch/output trees for local Manim authoring. These default to repo-local
# paths, but can be redirected to an off-repo support directory.
MANIM_MEDIA_DIR: Path = Path(
    os.environ.get(
        "MANIM_MEDIA_DIR",
        str(PROJECT_ROOT / "manim_service" / "_manim_media"),
    )
)
TRACE_MANIM_MEDIA_DIR: Path = Path(
    os.environ.get(
        "TRACE_MANIM_MEDIA_DIR",
        str(PROJECT_ROOT / "manim_service" / "_manim_media"),
    )
)
MANIM_WORKSPACES_DIR: Path = Path(
    os.environ.get(
        "MANIM_WORKSPACES_DIR",
        str(PROJECT_ROOT / "manim_service" / "workspaces"),
    )
)

# Media publishing. The default keeps local development file-system based.
MEDIA_STORAGE_BACKEND: str = os.environ.get("RL_IDE_MEDIA_STORAGE_BACKEND", "local").lower()
DO_SPACES_REGION: str = os.environ.get("DO_SPACES_REGION", "fra1")
DO_SPACES_BUCKET: str = os.environ.get("DO_SPACES_BUCKET", "")
DO_SPACES_ENDPOINT: str = os.environ.get(
    "DO_SPACES_ENDPOINT",
    f"https://{DO_SPACES_REGION}.digitaloceanspaces.com",
)
DO_SPACES_CDN_URL: str = os.environ.get("DO_SPACES_CDN_URL", "").rstrip("/")
DO_SPACES_ACCESS_KEY: str = os.environ.get("DO_SPACES_ACCESS_KEY", "")
DO_SPACES_SECRET_KEY: str = os.environ.get("DO_SPACES_SECRET_KEY", "")

# Render quality: "l" (480p15 dev), "m" (720p30 final)
RENDER_QUALITY: str = os.environ.get("RENDER_QUALITY", "l")

# Hard cap for one trace clip render. Keeps worker subprocesses bounded.
TRACE_RENDER_TIMEOUT_SECONDS: int = int(os.environ.get("TRACE_RENDER_TIMEOUT_SECONDS", "180"))

# Queue backend: "memory" for MVP, "redis" for production
QUEUE_BACKEND: str = os.environ.get("QUEUE_BACKEND", "memory")
REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Audio / TTS configuration --------------------------------------------------

# Kokoro-onnx model + voices files (downloaded once to ~/.cache/kokoro/).
# These are user-level caches, not committed to the repo.
KOKORO_MODEL_PATH: Path = Path(
    os.environ.get(
        "KOKORO_MODEL_PATH",
        str(Path.home() / ".cache" / "kokoro" / "kokoro-v1.0.onnx"),
    )
)
KOKORO_VOICES_PATH: Path = Path(
    os.environ.get(
        "KOKORO_VOICES_PATH",
        str(Path.home() / ".cache" / "kokoro" / "voices-v1.0.bin"),
    )
)

# Default narrator voice for the concept-video series. Single voice across
# the whole library — measured, professorial American male tone.
DEFAULT_NARRATOR_VOICE: str = os.environ.get("DEFAULT_NARRATOR_VOICE", "am_michael")

# Default synthesis speed (1.0 = natural; <1.0 slower, >1.0 faster).
DEFAULT_NARRATOR_SPEED: float = float(os.environ.get("DEFAULT_NARRATOR_SPEED", "1.0"))

# ffmpeg binary used for mixing/muxing audio with rendered MP4.
FFMPEG_BIN: str = os.environ.get("FFMPEG_BIN", "ffmpeg")


def render_runtime_status() -> dict[str, str | None]:
    """Report external executables needed by Manim trace rendering."""
    return {
        "manim_python": resolve_executable(MANIM_PYTHON),
        "ffmpeg": resolve_executable(FFMPEG_BIN),
        "latex": resolve_executable("latex"),
        "dvisvgm": resolve_executable("dvisvgm"),
    }


# Scratch directory for per-render synthesised audio segments. Safe to nuke
# between runs; cache is per-render, not per-line.
AUDIO_CACHE_DIR: Path = Path(
    os.environ.get(
        "AUDIO_CACHE_DIR",
        str(Path(__file__).resolve().parent / "_audio_cache"),
    )
)
