"""Lesson cache — single manifest every agent (Claude + Codex) reads.

The pipeline's "shared filesystem" approach to cross-vendor alignment:
- Orchestrator builds `cache/{lesson_id}/manifest.json` once per lesson.
- Every agent receives only the manifest path in its prompt.
- Each agent reads what it needs from the manifest's artifact paths.

This kills the inline-content-pasting tax. Both Claude (via Read) and
Codex (via filesystem) get identical context with zero prompt-token waste.

Usage:
    from manim_service.pipeline.lesson_cache import (
        build_manifest, read_manifest, manifest_path, record_stage_result,
    )

    # Orchestrator side (Step 2):
    build_manifest(
        lesson_id="policies_values_bellman",
        phase_count=26,
        render_target_seconds=1290,
    )

    # Agent brief side:
    path = manifest_path("policies_values_bellman")
    # The brief tells the agent: "Read this manifest.json and follow its paths"

    # End-of-stage side:
    record_stage_result("policies_values_bellman", stage="g1_rl_expert",
                        result_path="path/to/report.md", verdict="APPROVED")
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_ROOT   = PROJECT_ROOT / "manim_service" / "pipeline" / "cache"


# ---------------------------------------------------------------------------
# Default artifact path layout (per lesson)
# ---------------------------------------------------------------------------

def _default_artifact_paths(lesson_id: str) -> dict[str, str]:
    """Map of artifact key -> repo-relative path. Stable across all lessons."""
    cv = "manim_service/concept_videos"
    return {
        "specs":               f"{cv}/{lesson_id}_specs.md",
        "plan":                f"{cv}/{lesson_id}_plan.md",
        "choreo":              f"{cv}/{lesson_id}_choreo.md",
        "tv_canonical":        f"{cv}/{lesson_id}_tv_canonical.md",
        "scene":               f"{cv}/{lesson_id}_concept.py",
        "narration_script":    f"{cv}/{lesson_id}_narration_script.md",
        "audio_brief":         f"{cv}/{lesson_id}_audio_brief.md",
        "captions_srt":        f"{cv}/{lesson_id}_captions.srt",
        "captions_vtt":        f"{cv}/{lesson_id}_captions.vtt",
        "silent_mp4":          f"media/videos/{lesson_id}_concept/480p15/PoliciesValuesBellmanConcept.mp4",  # template
        "phase_timestamps":    f"media/videos/{lesson_id}_concept/480p15/phase_timestamps.json",
        "narrated_mp4":        f"backend/media/concept_videos/{lesson_id}_concept_narrated.mp4",
        "audio_report":        f"backend/media/concept_videos/{lesson_id}_concept_narrated.audio_report.json",
        # Cross-lesson canon
        "style_bible":         f"{cv}/docs/STYLE_BIBLE.md",
        "common_defects":      f"{cv}/docs/COMMON_DEFECTS.md",
        "rl_knowledge_base":   f"{cv}/docs/rl_knowledge_base.md",
        "session_log":         "manim_service/SESSION_LOG.md",
        "codex_handoff":       f"{cv}/docs/CODEX_HANDOFF.md",
    }


# ---------------------------------------------------------------------------
# Manifest data structure
# ---------------------------------------------------------------------------

@dataclass
class StageResult:
    stage: str
    result_path: str
    verdict: str
    timestamp: str


@dataclass
class Manifest:
    lesson_id: str
    phase_count: int | None = None
    render_target_seconds: float | None = None
    artifacts: dict[str, str] = field(default_factory=dict)
    stage_results: list[StageResult] = field(default_factory=list)
    notes: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def manifest_dir(lesson_id: str) -> Path:
    """Per-lesson cache directory; created on demand."""
    d = CACHE_ROOT / lesson_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def manifest_path(lesson_id: str) -> Path:
    return manifest_dir(lesson_id) / "manifest.json"


def build_manifest(
    lesson_id: str,
    *,
    phase_count: int | None = None,
    render_target_seconds: float | None = None,
    extra_artifacts: dict[str, str] | None = None,
    notes: dict[str, Any] | None = None,
) -> Path:
    """Create or overwrite the lesson manifest. Returns the manifest path."""
    artifacts = _default_artifact_paths(lesson_id)
    if extra_artifacts:
        artifacts.update(extra_artifacts)
    m = Manifest(
        lesson_id=lesson_id,
        phase_count=phase_count,
        render_target_seconds=render_target_seconds,
        artifacts=artifacts,
        notes=notes or {},
    )
    p = manifest_path(lesson_id)
    p.write_text(json.dumps(asdict(m), indent=2))
    return p


def read_manifest(lesson_id: str) -> Manifest:
    p = manifest_path(lesson_id)
    if not p.exists():
        raise FileNotFoundError(f"No manifest for lesson_id={lesson_id!r}; "
                                f"orchestrator must call build_manifest() first.")
    data = json.loads(p.read_text())
    sr = [StageResult(**s) for s in data.pop("stage_results", [])]
    m = Manifest(**data)
    m.stage_results = sr
    return m


def record_stage_result(
    lesson_id: str,
    *,
    stage: str,
    result_path: str,
    verdict: str,
) -> None:
    """Append a stage result to the manifest. The orchestrator calls this
    after each gate so downstream agents can see prior verdicts via the
    manifest alone."""
    from datetime import datetime
    m = read_manifest(lesson_id)
    m.stage_results.append(StageResult(
        stage=stage,
        result_path=result_path,
        verdict=verdict,
        timestamp=datetime.utcnow().isoformat() + "Z",
    ))
    manifest_path(lesson_id).write_text(json.dumps(asdict(m), indent=2))


def absolute(lesson_id: str, artifact_key: str) -> Path:
    """Resolve an artifact key to an absolute path. Raises KeyError if the
    key is not in the manifest."""
    m = read_manifest(lesson_id)
    rel = m.artifacts[artifact_key]
    return PROJECT_ROOT / rel


# ---------------------------------------------------------------------------
# CLI for ad-hoc inspection
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m manim_service.pipeline.lesson_cache <lesson_id> [build|show]")
        sys.exit(2)
    lesson = sys.argv[1]
    cmd = sys.argv[2] if len(sys.argv) > 2 else "show"
    if cmd == "build":
        path = build_manifest(lesson)
        print(f"Wrote manifest: {path}")
    elif cmd == "show":
        m = read_manifest(lesson)
        print(json.dumps(asdict(m), indent=2))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(2)
