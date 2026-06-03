"""Quality gate — Gate-5 orchestrator for deterministic visual QA.

Runs the cheap, token-free gates in order and emits ONE compact verdict an
agent can read in a few lines:

    Tier-1  static lint     (scene_inspector)   — advisory, pre-render
    Tier-0  layout audit    (layout_audit.json) — BLOCKING, post-render
    -> if BLOCKING-clean: extract a minimal frame set (default 5) for an
       optional single LLM "polish" pass on an already-clean video.

The point is to spend zero vision tokens on gross defects (crowding,
off-canvas, dim-entry) and hand the LLM only a handful of frames from a video
that already passed the deterministic gates — instead of 26 frames × 3 rounds.

    python -m manim_service.pipeline.quality_gate --lesson-id policies_values_bellman

Exit codes:  0 PASS (deterministic-clean)   1 BLOCK (hard defect)   2 CANNOT-RUN (no render yet)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from manim_service.pipeline import scene_inspector

REPO = Path(__file__).resolve().parents[2]
CV_DIR = REPO / "manim_service" / "concept_videos"
RENDER_DIR = REPO / "media" / "videos"
NARRATED_DIR = REPO / "backend" / "media" / "concept_videos"


def _find_audit(lesson: str) -> Path | None:
    base = RENDER_DIR / f"{lesson}_concept"
    if not base.exists():
        return None
    cands = sorted(base.rglob("layout_audit.json"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


def _find_video(lesson: str) -> Path | None:
    for name in (f"{lesson}_concept_narrated.mp4", f"{lesson}_concept.mp4"):
        p = NARRATED_DIR / name
        if p.exists():
            return p
    base = RENDER_DIR / f"{lesson}_concept"
    if base.exists():
        cands = sorted(base.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if cands:
            return cands[0]
    return None


def _duration(video: Path) -> float | None:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nk=1:nw=1", str(video)],
            capture_output=True, text=True, check=True,
        )
        return float(out.stdout.strip())
    except Exception:
        return None


def _extract_frames(video: Path, fracs: list[float], out_dir: Path) -> list[Path]:
    dur = _duration(video)
    if not dur:
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i, f in enumerate(fracs):
        t = round(dur * f, 1)
        p = out_dir / f"review_{i:02d}_{t:.0f}s.png"
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-ss", str(t), "-i", str(video),
                 "-frames:v", "1", str(p)],
                capture_output=True, check=True,
            )
            if p.exists():
                paths.append(p)
        except Exception:
            pass
    return paths


def run_gate(lesson: str, *, scene: Path | None, audit: Path | None,
             video: Path | None, n_frames: int, frames_out: Path) -> int:
    print(f"QUALITY-GATE  {lesson}")

    # --- Tier-1: static lint (advisory) ---
    scene = scene or (CV_DIR / f"{lesson}_concept.py")
    static = scene_inspector.inspect_file(scene) if scene.exists() else []
    print(f"  G2 static  : {len(static)} advisory finding(s)"
          + ("" if scene.exists() else "  [scene file not found]"))
    for f in static[:8]:
        print(f"      - {f['rule']} L{f['line']}: {f['detail']}")
    if len(static) > 8:
        print(f"      … +{len(static) - 8} more")

    # --- Tier-0: layout audit (blocking) ---
    audit = audit or _find_audit(lesson)
    if not audit or not audit.exists():
        print("  G1 layout  : MISSING layout_audit.json — render the scene first")
        print("VERDICT: CANNOT-RUN")
        return 2
    data = json.loads(audit.read_text())
    phases = data.get("phases", [])
    fails = [p for p in phases if p.get("hard_fail")]
    crowd_phases = [p for p in phases if p.get("crowd")]
    n_crowd = sum(len(p.get("crowd", [])) for p in phases)
    print(f"  G1 layout  : {len(fails)} hard (OFF-CANVAS) / {len(phases)} phases; "
          f"{n_crowd} crowd advisor{'y' if n_crowd == 1 else 'ies'}")
    for p in fails:
        for oc in p["off_canvas"]:
            edges = ", ".join(f"{k}+{v}" for k, v in oc["edges"].items())
            print(f"      FAIL P{p['phase']} {p['name']}: OFF-CANVAS {oc['kind']} [{edges}]")
    for p in crowd_phases[:6]:
        for c in p["crowd"][:2]:
            print(f"      warn P{p['phase']} {p['name']}: crowd/{c['severity']} "
                  f"{c['a_kind']}↔{c['b_kind']} ({c['overlap_frac']:.0%})")
    space_phases = [p for p in phases
                    if any("under-uses" in w for w in p.get("warnings", []))]
    if space_phases:
        print(f"  space      : {len(space_phases)} phase(s) under-use the canvas (wasted space)")
        for p in space_phases[:6]:
            for w in p["warnings"]:
                if "under-uses" in w:
                    print(f"      warn P{p['phase']} {p['name']}: {w}")

    if fails:
        print("VERDICT: BLOCK  (fix hard defects, re-render, re-run gate)")
        return 1

    # --- deterministic-clean: prepare minimal LLM polish set ---
    video = video or _find_video(lesson)
    if video and video.exists() and n_frames > 0:
        fracs = [round((i + 1) / (n_frames + 1), 3) for i in range(n_frames)]
        frames = _extract_frames(video, fracs, frames_out)
        print(f"  polish set : {len(frames)} frame(s) -> {frames_out}")
        for fp in frames:
            print(f"      {fp.name}")
    else:
        print("  polish set : (no video found; skipped frame extraction)")

    print("VERDICT: PASS  (deterministic-clean; optional ≤"
          f"{n_frames}-frame LLM polish only)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic Gate-5 visual QA")
    ap.add_argument("--lesson-id", required=True)
    ap.add_argument("--scene", type=Path, default=None)
    ap.add_argument("--audit", type=Path, default=None)
    ap.add_argument("--video", type=Path, default=None)
    ap.add_argument("--review-frames", type=int, default=5)
    ap.add_argument("--frames-out", type=Path, default=None)
    args = ap.parse_args(argv)

    frames_out = args.frames_out or Path(f"/tmp/qa_review_{args.lesson_id}")
    return run_gate(
        args.lesson_id, scene=args.scene, audit=args.audit, video=args.video,
        n_frames=args.review_frames, frames_out=frames_out,
    )


if __name__ == "__main__":
    sys.exit(main())
