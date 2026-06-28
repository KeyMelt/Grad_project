"""Generate REAL trace logs by running the engine on each lesson's reference
solution — the same code path the platform uses, minus the render enqueue.

For each lesson it runs the reference template, pulls the real per-step log
(equation_update / dp_details / grid_metadata straight from the run), and writes
the featured episode as a flat step list the trace scene can render directly.

Usage:
    /Users/ultramarine/.venvs/manim/bin/python scripts/gen_demo_traces.py
Outputs: /tmp/demo_traces/<name>.json  (+ keeps capture dirs for Blackjack frames)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from backend.execution_runtime import (
    _build_trace_payload,
    _create_environment_adapter,
    _ensure_process_lesson_registry,
    _run_lesson_engine,
)
from backend.lesson_registry import get_lesson_definition
from backend.logger.event_logger import EventLogger, NpEncoder
from backend.services.student_feedback_service import StudentFeedbackService
from backend.settings import ExecutionSettings

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "backend" / "rl_engine" / "templates"
OUT = Path("/tmp/demo_traces")
OUT.mkdir(parents=True, exist_ok=True)

# (lesson_id, output stem). Templates are the reference solutions.
LESSONS = [
    ("dp_value_iteration", "frozenlake_value_iteration"),
    ("td_q_learning", "taxi_q_learning"),
    ("mc_first_visit", "blackjack_mc"),
]


def _featured_episode(log_data: list[list[dict]]) -> list[dict]:
    """Pick the most informative episode: the longest non-empty one."""
    episodes = [ep for ep in log_data if ep]
    if not episodes:
        return []
    return max(episodes, key=len)


def _diagnose(steps: list[dict]) -> str:
    if not steps:
        return "EMPTY"
    s0 = steps[0]
    eu = s0.get("equation_update") or {}
    gm = s0.get("grid_metadata") or {}
    dp = eu.get("dp_details") or {}
    backups = dp.get("action_backups") or []
    terms = (backups[0].get("transition_terms") if backups else None) or []
    return (f"steps={len(steps)} kind={eu.get('kind')!r} env={gm.get('environment')!r} "
            f"action_backups={len(backups)} terms[0]={len(terms)} "
            f"has_reward={'reward' in s0}")


def main() -> int:
    _ensure_process_lesson_registry()
    settings = ExecutionSettings.from_env()
    viz_dir = os.path.abspath(settings.visualization_output_dir)
    feedback = StudentFeedbackService()

    for lesson_id, stem in LESSONS:
        lesson = get_lesson_definition(lesson_id)
        code = (TEMPLATES / f"{lesson_id}.py").read_text(encoding="utf-8")
        payload = {"lesson_id": lesson_id, "code": code}
        logger = EventLogger(log_dir=settings.logger_dir)
        adapter = _create_environment_adapter(
            lesson=lesson, lesson_id=lesson_id, visualization_output_dir=viz_dir)
        meta = _run_lesson_engine(
            adapter=adapter, logger=logger, feedback_service=feedback,
            lesson=lesson, submission_payload=payload)
        log_data = logger.get_logs()
        episode_rewards = [sum(st.get("reward", 0) for st in ep) for ep in log_data]

        steps = _featured_episode(log_data)
        out_path = OUT / f"{stem}.json"
        out_path.write_text(json.dumps(steps, cls=NpEncoder), encoding="utf-8")
        print(f"[{lesson_id}] -> {out_path}  ({_diagnose(steps)})")

        # Also dump the platform's curated/staged payload for reference.
        try:
            tp = _build_trace_payload(lesson_id, log_data, episode_rewards,
                                      execution_metadata=meta)
            (OUT / f"{stem}.curated.json").write_text(
                json.dumps(tp.get("trace_episodes", []), cls=NpEncoder), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            print(f"    (curated payload skipped: {exc})")

    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
