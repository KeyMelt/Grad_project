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

# Real REFERENCE SOLUTIONS for the demo. The product templates under
# backend/rl_engine/templates/ are starter STUBS shown to students (q_learning /
# mc are `pass`), so running them never learns. We must not turn those into
# answer keys; the demo supplies correct solutions here instead. dp_value_iteration
# ships a real solution already, so we read it.
_Q_LEARNING_SOLUTION = (
    "LEARNING_RATE = 0.5\n"
    "DISCOUNT_FACTOR = 0.99\n"
    "EXPLORATION_RATE = 0.20\n"
    # EPISODE_COUNT is the (capped) per-submission count; the staged-capture
    # training budget is the engine's own 2000-4000 for Taxi, independent of this.
    "EPISODE_COUNT = 200\n\n"
    "def q_learning_update(Q, state, action, reward, next_state,\n"
    "                      alpha=LEARNING_RATE, gamma=DISCOUNT_FACTOR):\n"
    "    best_next = max(Q[next_state])\n"
    "    Q[state][action] += alpha * (reward + gamma * best_next - Q[state][action])\n"
    "    return Q\n"
)
_MC_SOLUTION = (
    "def mc_first_visit_prediction(episode, V, returns, gamma=1.0):\n"
    "    visited = [s for (s, a, r) in episode]\n"
    "    G = 0.0\n"
    "    for t in range(len(episode) - 1, -1, -1):\n"
    "        state, action, reward = episode[t]\n"
    "        G = gamma * G + reward\n"
    "        if state not in visited[:t]:\n"
    "            if state not in returns:\n"
    "                returns[state] = []\n"
    "            returns[state].append(G)\n"
    "            V[state] = sum(returns[state]) / len(returns[state])\n"
    "    return V\n"
)


def _solution_code(lesson_id: str) -> str:
    if lesson_id == "td_q_learning":
        return _Q_LEARNING_SOLUTION
    if lesson_id == "mc_first_visit":
        return _MC_SOLUTION
    return (TEMPLATES / f"{lesson_id}.py").read_text(encoding="utf-8")


# (lesson_id, output stem).
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
        code = _solution_code(lesson_id)
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
