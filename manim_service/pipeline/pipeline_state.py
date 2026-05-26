"""Per-lesson pipeline state checkpoint.

A small, dependency-free helper so either runtime (Claude Code orchestrator or
Codex execution agent) can read and update the convergence-gate state of a
video production run without parsing the 56 KB SESSION_LOG.md.

State lives at:
    manim_service/concept_videos/{lesson_id}_pipeline_state.json

SESSION_LOG.md remains the human-readable audit trail. This file is the
machine-readable resume point.

CLI:
    python -m manim_service.pipeline.pipeline_state init  <lesson_id>
    python -m manim_service.pipeline.pipeline_state get   <lesson_id>
    python -m manim_service.pipeline.pipeline_state set-owner    <lesson_id> <claude|codex>
    python -m manim_service.pipeline.pipeline_state set-gate     <lesson_id> <gate_key> <status>
    python -m manim_service.pipeline.pipeline_state set-handoff  <lesson_id> --stage S --status ST [--brief P] [--result P]
    python -m manim_service.pipeline.pipeline_state set-artifact <lesson_id> <key> <path>

Gate keys:   g1_rl_expert_plan g2_tech_validator g3_voice_bgm g4_transcript
             g5_qa g6_series_continuity g7_rl_expert_final g8_producer
Gate status: pending | pass | fail
Owner:       claude | codex
Handoff stage:  full_pipeline | scene_render | narrate_mux | none
              (full_pipeline = plan.md + choreo.md + Gate1 + Gate2 + scene_render in one session)
Handoff status: awaiting_codex | codex_running | codex_done | codex_failed | none
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path

GATE_KEYS = (
    "g1_rl_expert_plan",
    "g2_tech_validator",
    "g3_voice_bgm",
    "g4_transcript",
    "g5_qa",
    "g6_series_continuity",
    "g7_rl_expert_final",
    "g8_producer",
)
GATE_STATUSES = ("pending", "pass", "fail")
OWNERS = ("claude", "codex")

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STATE_DIR = _REPO_ROOT / "manim_service" / "concept_videos"


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def state_path(lesson_id: str) -> Path:
    return _STATE_DIR / f"{lesson_id}_pipeline_state.json"


def _empty_state(lesson_id: str) -> dict:
    return {
        "lesson_id": lesson_id,
        "updated_at": _now(),
        "current_owner": "claude",
        "gates": {key: "pending" for key in GATE_KEYS},
        "handoff": {
            "stage": "none",
            "status": "none",
            "brief_path": "",
            "result_path": "",
        },
        "artifacts": {},
    }


def load(lesson_id: str) -> dict:
    path = state_path(lesson_id)
    if not path.exists():
        return _empty_state(lesson_id)
    return json.loads(path.read_text())


def save(state: dict) -> Path:
    state["updated_at"] = _now()
    path = state_path(state["lesson_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n")
    return path


def init(lesson_id: str) -> dict:
    """Create a fresh state file only if one does not already exist."""
    path = state_path(lesson_id)
    if path.exists():
        return load(lesson_id)
    state = _empty_state(lesson_id)
    save(state)
    return state


def set_owner(lesson_id: str, owner: str) -> dict:
    if owner not in OWNERS:
        raise ValueError(f"owner must be one of {OWNERS}, got {owner!r}")
    state = load(lesson_id)
    state["current_owner"] = owner
    save(state)
    return state


def set_gate(lesson_id: str, gate_key: str, status: str) -> dict:
    if gate_key not in GATE_KEYS:
        raise ValueError(f"gate_key must be one of {GATE_KEYS}, got {gate_key!r}")
    if status not in GATE_STATUSES:
        raise ValueError(f"status must be one of {GATE_STATUSES}, got {status!r}")
    state = load(lesson_id)
    state["gates"][gate_key] = status
    save(state)
    return state


def set_handoff(
    lesson_id: str,
    stage: str,
    status: str,
    brief_path: str | None = None,
    result_path: str | None = None,
) -> dict:
    state = load(lesson_id)
    handoff = state["handoff"]
    handoff["stage"] = stage
    handoff["status"] = status
    if brief_path is not None:
        handoff["brief_path"] = brief_path
    if result_path is not None:
        handoff["result_path"] = result_path
    save(state)
    return state


def set_artifact(lesson_id: str, key: str, path: str) -> dict:
    state = load(lesson_id)
    state["artifacts"][key] = path
    save(state)
    return state


def _print(state: dict) -> None:
    print(json.dumps(state, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RL pipeline state checkpoint")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create state file if absent")
    p_init.add_argument("lesson_id")

    p_get = sub.add_parser("get", help="print state JSON")
    p_get.add_argument("lesson_id")

    p_owner = sub.add_parser("set-owner")
    p_owner.add_argument("lesson_id")
    p_owner.add_argument("owner", choices=OWNERS)

    p_gate = sub.add_parser("set-gate")
    p_gate.add_argument("lesson_id")
    p_gate.add_argument("gate_key", choices=GATE_KEYS)
    p_gate.add_argument("status", choices=GATE_STATUSES)

    p_handoff = sub.add_parser("set-handoff")
    p_handoff.add_argument("lesson_id")
    p_handoff.add_argument("--stage", required=True)
    p_handoff.add_argument("--status", required=True)
    p_handoff.add_argument("--brief", dest="brief_path", default=None)
    p_handoff.add_argument("--result", dest="result_path", default=None)

    p_art = sub.add_parser("set-artifact")
    p_art.add_argument("lesson_id")
    p_art.add_argument("key")
    p_art.add_argument("path")

    args = parser.parse_args(argv)

    if args.command == "init":
        _print(init(args.lesson_id))
    elif args.command == "get":
        _print(load(args.lesson_id))
    elif args.command == "set-owner":
        _print(set_owner(args.lesson_id, args.owner))
    elif args.command == "set-gate":
        _print(set_gate(args.lesson_id, args.gate_key, args.status))
    elif args.command == "set-handoff":
        _print(
            set_handoff(
                args.lesson_id,
                stage=args.stage,
                status=args.status,
                brief_path=args.brief_path,
                result_path=args.result_path,
            )
        )
    elif args.command == "set-artifact":
        _print(set_artifact(args.lesson_id, args.key, args.path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
