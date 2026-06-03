"""Per-segment render + concat with content-hash caching.

Why: a one-line edit to a 21-minute video should not re-render 21 minutes.
A video is authored as a *workspace* of independently-renderable segment scene
files. Editing one segment re-renders only that segment; every other segment is
reused from cache. Segments are concatenated into the final silent MP4.
Narration is applied ONCE to the final approved concat (never per segment, never
redone unless the concat itself changes).

Workspace layout::

    manim_service/workspaces/<lesson_id>/
        manifest.json            # ordered segments + render config
        segments/
            s01_intro.py         # exactly one Scene subclass per file
            s02_policy.py
            ...
        cache/                   # rendered segment MP4s keyed by content hash
        <lesson_id>_silent.mp4   # concatenated output (the render product)

manifest.json::

    {
      "lesson_id": "policies_values_bellman",
      "quality": "-ql",
      "segments": [
        {"id": "s01_intro",  "file": "segments/s01_intro.py",  "scene": "S01Intro"},
        {"id": "s02_policy", "file": "segments/s02_policy.py", "scene": "S02Policy"}
      ]
    }

Caching key per segment = sha256(segment source + shared-module hash + quality).
A change to a shared module (manim_service/scenes/*.py) busts every segment
(correct — it can affect them all); a change to one segment file busts only
that segment.

Usage::

    python -m manim_service.pipeline.segment_render --lesson-id <id>
    python -m manim_service.pipeline.segment_render --lesson-id <id> --segment s02_policy
    python -m manim_service.pipeline.segment_render --lesson-id <id> --force

Authoring rule (so segments concatenate seamlessly): each segment Scene must
start from and end on a clean, known state (fade in from / out to the dark
background). No mobject or camera state is carried across segment files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORKSPACES = REPO / "manim_service" / "workspaces"
SHARED_GLOB = REPO / "manim_service" / "scenes"
PYBIN = sys.executable


def _shared_hash() -> str:
    h = hashlib.sha256()
    for p in sorted(SHARED_GLOB.glob("*.py")):
        h.update(p.read_bytes())
    return h.hexdigest()


def _segment_hash(seg_file: Path, shared: str, quality: str) -> str:
    h = hashlib.sha256()
    h.update(seg_file.read_bytes())
    h.update(shared.encode())
    h.update(quality.encode())
    return h.hexdigest()[:16]


def _render_segment(seg_file: Path, scene: str, quality: str) -> Path:
    """Render one segment with manim; return the path to the produced MP4."""
    subprocess.run(
        [PYBIN, "-m", "manim", quality, "--disable_caching", str(seg_file), scene],
        cwd=str(REPO), check=True, capture_output=True, text=True,
    )
    stem = seg_file.stem
    candidates = sorted((REPO / "media" / "videos" / stem).rglob(f"{scene}.mp4"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError(f"render produced no MP4 for {scene} in {seg_file}")
    return candidates[0]


def _concat(segment_mp4s: list[Path], out: Path) -> None:
    listing = out.with_suffix(".concat.txt")
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in segment_mp4s))
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
             "-c", "copy", str(out)],
            check=True, capture_output=True, text=True,
        )
    finally:
        listing.unlink(missing_ok=True)


def build(lesson_id: str, only: str | None, force: bool, quality: str | None = None) -> int:
    ws = WORKSPACES / lesson_id
    manifest_path = ws / "manifest.json"
    if not manifest_path.exists():
        print(f"SEGMENT-RENDER: no workspace at {manifest_path}")
        return 2
    manifest = json.loads(manifest_path.read_text())
    quality = quality or manifest.get("quality", "-ql")
    cache = ws / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    shared = _shared_hash()
    # Include the workspace's shared base modules (e.g. *_base.py) in the shared
    # hash: they live outside manim_service/scenes but every segment imports them,
    # so editing a base must bust every segment in the workspace.
    base_h = hashlib.sha256()
    for bp in sorted((ws / "segments").glob("*_base.py")):
        base_h.update(bp.read_bytes())
    shared = shared + base_h.hexdigest()

    rendered, reused, ordered_mp4s = [], [], []
    for seg in manifest["segments"]:
        seg_file = ws / seg["file"]
        seg_hash = _segment_hash(seg_file, shared, quality)
        cached = cache / f"{seg['id']}__{seg_hash}.mp4"
        is_target = (only is None) or (only == seg["id"])

        if cached.exists() and not (force and is_target):
            reused.append(seg["id"])
        elif is_target:
            print(f"  render {seg['id']} …")
            produced = _render_segment(seg_file, seg["scene"], quality)
            # prune stale cache entries for this segment id, then store
            for old in cache.glob(f"{seg['id']}__*.mp4"):
                old.unlink()
            shutil.copy2(produced, cached)
            rendered.append(seg["id"])
        else:
            # not the targeted segment and no cache — cannot concat
            print(f"  MISSING cache for {seg['id']} (run without --segment first)")
            return 1
        ordered_mp4s.append(cached)

    out = ws / f"{lesson_id}_silent.mp4"
    _concat(ordered_mp4s, out)
    print(f"SEGMENT-RENDER {lesson_id}: rendered={rendered or '-'} "
          f"reused={reused or '-'}")
    print(f"  -> {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Per-segment render + concat with caching")
    ap.add_argument("--lesson-id", required=True)
    ap.add_argument("--segment", default=None, help="render only this segment id")
    ap.add_argument("--force", action="store_true", help="ignore cache for the target")
    ap.add_argument("--quality", default=None, help="override manifest quality flag, e.g. -qm")
    args = ap.parse_args(argv)
    return build(args.lesson_id, args.segment, args.force, args.quality)


if __name__ == "__main__":
    sys.exit(main())
