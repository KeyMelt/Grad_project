from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEO_DIR = Path(
    os.getenv("RL_IDE_CONCEPT_VIDEO_DIR", str(ROOT / "backend" / "media" / "concept_videos"))
).expanduser()
TMP_MEDIA_DIR = ROOT / "backend" / "concept_videos" / "_manim_media"
MANIM_PYTHON = Path(os.getenv("RL_IDE_MANIM_PYTHON", "/Users/ultramarine/.venvs/manim/bin/python3"))

def render_concept_video(
    scene_file: Path,
    *,
    lesson_id: str,
    scene_name: str | None = None,
    force: bool = False,
) -> Path:
    """Render a single concept-video Manim scene into the backend concept-video directory.

    Output filename matches backend metadata: `{lesson_id}_concept.mp4`.

    By default, this is idempotent: if the output file already exists, no render is performed.
    """
    scene_file = _resolve_scene_file(scene_file)
    _validate_lesson_id(lesson_id)

    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    TMP_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    output_name = f"{lesson_id}_concept.mp4"
    output_path = (VIDEO_DIR / output_name).resolve()
    if output_path.exists() and not force:
        print(f"Concept video already exists; skipping render: {output_path}")
        return output_path

    resolved_scene_name = scene_name or _detect_scene_name(scene_file)
    rendered_path = _render_scene(scene_file, resolved_scene_name)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(rendered_path, output_path)
    print(f"Wrote concept video: {output_path}")
    return output_path


def _resolve_scene_file(scene_file: Path) -> Path:
    candidate = scene_file.expanduser()
    if not candidate.is_absolute():
        candidate = (ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()
    if candidate.suffix.lower() != ".py":
        raise SystemExit(f"Scene file must be a .py script: {candidate}")
    if not candidate.exists() or not candidate.is_file():
        raise SystemExit(f"Scene file not found: {candidate}")
    return candidate


def _validate_lesson_id(lesson_id: str) -> None:
    if not lesson_id or not lesson_id.strip():
        raise SystemExit("--lesson-id is required.")
    value = lesson_id.strip()
    if any(ch.isspace() for ch in value):
        raise SystemExit(f"Invalid lesson id (contains whitespace): {value!r}")
    if not all(ch.isalnum() or ch in {"_", "-"} for ch in value):
        raise SystemExit(f"Invalid lesson id (only [A-Za-z0-9_-] allowed): {value!r}")


def _detect_scene_name(scene_file: Path) -> str:
    """Detect a scene class defined by `scene_file` using the configured Manim interpreter."""
    probe = r"""
import importlib.util
import inspect
import json
import sys
from pathlib import Path

scene_path = Path(sys.argv[1]).resolve()
module_name = f"concept_video_probe_{scene_path.stem}"
spec = importlib.util.spec_from_file_location(module_name, scene_path)
if spec is None or spec.loader is None:
    raise SystemExit(f"Unable to load scene module: {scene_path}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

from manim import Scene  # noqa: E402

scenes = []
for name, obj in vars(module).items():
    if not inspect.isclass(obj):
        continue
    if obj is Scene:
        continue
    try:
        is_scene = issubclass(obj, Scene)
    except Exception:
        continue
    if not is_scene:
        continue
    if getattr(obj, "__module__", None) != module_name:
        continue
    scenes.append(name)

print(json.dumps(sorted(scenes)))
"""

    env = dict(os.environ)
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    try:
        result = subprocess.run(
            [str(MANIM_PYTHON), "-c", probe, str(scene_file)],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        raise SystemExit(
            "Failed while importing scene file to detect Manim Scene classes.\n"
            f"scene_file: {scene_file}\n"
            f"stdout:\n{error.stdout}\n"
            f"stderr:\n{error.stderr}"
        ) from error
    try:
        names = json.loads(result.stdout.strip() or "[]")
    except json.JSONDecodeError as error:
        raise SystemExit(
            f"Failed to parse scene detection output.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        ) from error

    if not names:
        raise SystemExit(f"No Manim Scene subclasses detected in {scene_file}.")
    if len(names) == 1:
        return str(names[0])

    concept_like = [name for name in names if str(name).endswith("Concept")]
    if len(concept_like) == 1:
        return str(concept_like[0])

    raise SystemExit(
        "Multiple scenes detected; pass --scene-name to disambiguate. "
        f"Detected: {', '.join(map(str, names))}"
    )


def _render_scene(scene_file: Path, scene_name: str) -> Path:
    cmd = [
        str(MANIM_PYTHON),
        "-m",
        "manim",
        "-ql",
        "--media_dir",
        str(TMP_MEDIA_DIR),
        str(scene_file),
        scene_name,
    ]
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    subprocess.run(cmd, check=True, cwd=str(ROOT), env=env)

    rendered = TMP_MEDIA_DIR / "videos" / scene_file.stem / "480p15" / f"{scene_name}.mp4"
    if not rendered.exists() or not rendered.is_file():
        raise FileNotFoundError(f"Expected render output not found: {rendered}")
    return rendered


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python -m backend.concept_videos.render",
        description=(
            "Render a single pre-generated Manim concept video and store it in the backend media directory."
        ),
    )
    parser.add_argument(
        "scene_file",
        help="Path to the Manim scene script (absolute path recommended).",
    )
    parser.add_argument(
        "--lesson-id",
        required=True,
        help="Lesson id used to name the output file as {lesson_id}_concept.mp4.",
    )
    parser.add_argument(
        "--scene-name",
        help="Optional Manim Scene class name. If omitted, render.py will try to auto-detect it.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing {lesson_id}_concept.mp4 by re-rendering.",
    )
    args = parser.parse_args()

    render_concept_video(
        Path(args.scene_file),
        lesson_id=args.lesson_id,
        scene_name=args.scene_name,
        force=bool(args.force),
    )
