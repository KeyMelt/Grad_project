"""manim_service configuration."""
from __future__ import annotations

import os
from pathlib import Path

# Path to the manim venv python binary
MANIM_PYTHON: str = os.environ.get(
    "MANIM_PYTHON", "/Users/ultramarine/.venvs/manim/bin/python"
)

# Shared media output directory (backend reads from same path)
SHARED_MEDIA_DIR: Path = Path(
    os.environ.get("SHARED_MEDIA_DIR", "/Users/ultramarine/Desktop/grad_project/backend/media")
)

# Render quality: "l" (480p15 dev), "m" (720p30 final)
RENDER_QUALITY: str = os.environ.get("RENDER_QUALITY", "l")

# Queue backend: "memory" for MVP, "redis" for production
QUEUE_BACKEND: str = os.environ.get("QUEUE_BACKEND", "memory")
REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
