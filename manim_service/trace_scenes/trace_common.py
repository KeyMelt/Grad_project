"""Shared helpers for the overhauled trace-replay renderer.

The trace video is a SILENT, real-time replay of one successful run: it shows, step by
step, what the learner's code did under the hood — the agent acting on the REAL Gymnasium
environment, the value/Q table updating, and the exact arithmetic of each update (what was
sampled, the target, the error, the nudge). No narration; the visuals carry it.

This module is intentionally dependency-light (palette, env detection, action maps, and
structured extractors) so the scene + board adapters stay readable.
"""
from __future__ import annotations

from typing import Any

# --------------------------------------------------------------------- palette
BG = "#020617"
PANEL = "#0F172A"
PANEL_2 = "#0B1220"
STROKE = "#1E293B"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
STATE = "#38BDF8"        # states, s, s'
ACTION = "#FB923C"       # actions, a
REWARD = "#34D399"       # reward, goal, positive
PENALTY = "#F87171"      # cliff/hole, negative, done
VALUE = "#FACC15"        # values, gamma, returns
POLICY = "#A78BFA"       # probabilities, sampled
TEAL = "#2DD4BF"         # bootstrap source

# ----------------------------------------------------------- action conventions
# Gymnasium action index -> (label, elf/agent facing direction)
_ACTIONS: dict[str, dict[int, tuple[str, str]]] = {
    "FrozenLake": {0: ("Left", "left"), 1: ("Down", "down"),
                   2: ("Right", "right"), 3: ("Up", "up")},
    "CliffWalking": {0: ("Up", "up"), 1: ("Right", "right"),
                     2: ("Down", "down"), 3: ("Left", "left")},
    "Blackjack": {0: ("Stand", "down"), 1: ("Hit", "up")},
}

_TD_KINDS = {"sarsa", "q_learning", "td_prediction"}
_DP_KINDS = {"policy_evaluation", "value_iteration", "policy_improvement"}
_MC_KINDS = {"mc_first_visit", "mc_sampling"}


def detect_env(steps: list[dict]) -> str:
    """FrozenLake / CliffWalking / Blackjack from the richest signal available."""
    for s in steps:
        gm = s.get("grid_metadata") or {}
        if gm.get("environment"):
            return gm["environment"]
        eu = s.get("equation_update") or {}
        if (eu.get("mc_details") or {}).get("observation") is not None:
            return "Blackjack"
    kinds = {(s.get("equation_update") or {}).get("kind") for s in steps}
    if kinds & _MC_KINDS:
        return "Blackjack"
    if kinds & _TD_KINDS:
        return "CliffWalking"
    return "FrozenLake"


def grid_shape(env: str) -> tuple[int, int]:
    return {"CliffWalking": (4, 12), "FrozenLake": (4, 4)}.get(env, (4, 4))


def action_label(env: str, action: Any) -> str:
    try:
        return _ACTIONS.get(env, _ACTIONS["FrozenLake"])[int(action)][0]
    except (TypeError, ValueError, KeyError):
        return f"a{action}"


def action_dir(env: str, action: Any) -> str:
    try:
        return _ACTIONS.get(env, _ACTIONS["FrozenLake"])[int(action)][1]
    except (TypeError, ValueError, KeyError):
        return "down"


def family(step: dict) -> str:
    """'td' | 'dp' | 'mc' | '' — which update family this step belongs to."""
    kind = (step.get("equation_update") or {}).get("kind", "")
    if kind in _TD_KINDS:
        return "td"
    if kind in _DP_KINDS:
        return "dp"
    if kind in _MC_KINDS:
        return "mc"
    return ""


# --------------------------------------------------------------- formatting
def fmt(value: Any, nd: int = 2) -> str:
    # ASCII minus only — these strings feed MathTex/LaTeX.
    try:
        return f"{float(value):.{nd}f}"
    except (TypeError, ValueError):
        return "?"


def signed(value: Any, nd: int = 2) -> str:
    try:
        v = float(value)
        return f"{'+' if v >= 0 else '-'}{abs(v):.{nd}f}"
    except (TypeError, ValueError):
        return "?"


def as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def tex_escape(value: Any) -> str:
    return str(value).replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")


# --------------------------------------------------------------- extractors
def transition(step: dict, env: str) -> dict:
    """The S-A-R-S' (and A' for SARSA) of one step, with labels."""
    eu = step.get("equation_update") or {}
    return {
        "state": step.get("state"),
        "action": step.get("action"),
        "action_label": action_label(env, step.get("action")),
        "reward": step.get("reward"),
        "next_state": step.get("next_state"),
        "kind": eu.get("kind", ""),
    }


def td_pieces(step: dict) -> dict | None:
    """Numbers for a TD/Q-learning/SARSA update card, or None."""
    eu = step.get("equation_update") or {}
    if eu.get("kind") not in _TD_KINDS:
        return None
    old = as_float(eu.get("old_value"))
    new = as_float(eu.get("new_value"))
    target = as_float(eu.get("td_target"))
    error = as_float(eu.get("td_error"))
    if error is None and target is not None and old is not None:
        error = target - old
    return {
        "kind": eu.get("kind"),
        "lhs": eu.get("lhs", "Q(s,a)"),
        "reward": as_float(eu.get("reward")),
        "gamma": as_float(eu.get("gamma")),
        "alpha": as_float(eu.get("alpha")),
        "bootstrap_label": eu.get("bootstrap_label", ""),
        "bootstrap_value": as_float(eu.get("bootstrap_value")),
        "target": target,
        "error": error,
        "old": old,
        "new": new,
        "on_policy": eu.get("kind") == "sarsa",
    }


def dp_pieces(step: dict) -> dict | None:
    eu = step.get("equation_update") or {}
    if eu.get("kind") not in _DP_KINDS:
        return None
    d = eu.get("dp_details") or {}
    return {
        "kind": eu.get("kind"),
        "lhs": eu.get("lhs", "V(s)"),
        "gamma": as_float(eu.get("gamma")),
        "backup": as_float(d.get("backup_value", eu.get("td_target"))),
        "delta": as_float(d.get("delta")),
        "new": as_float(eu.get("new_value")) if eu.get("kind") != "policy_improvement" else None,
        "selected_action_label": d.get("selected_action_label", ""),
        "action_backups": d.get("action_backups", []),
        "show_policy": eu.get("kind") == "policy_evaluation",
    }


def mc_pieces(step: dict) -> dict | None:
    eu = step.get("equation_update") or {}
    d = eu.get("mc_details") or step.get("mc_details") or {}
    if eu.get("kind") not in _MC_KINDS and not d:
        return None
    obs = d.get("observation") or {}
    return {
        "kind": eu.get("kind", "mc_sampling"),
        "observation_label": obs.get("label", ""),
        "player_sum": obs.get("player_sum"),
        "dealer_card": obs.get("dealer_card"),
        "usable_ace": obs.get("usable_ace"),
        "action_label": d.get("action_label", ""),
        "reward": as_float(d.get("reward")),
        "return_value": as_float(d.get("return_value")),
        "returns_history": d.get("returns_history", []),
        "return_terms": d.get("return_terms", []),
        "episode_strip": d.get("episode_strip", []),
        "terminated": bool(d.get("terminated")),
        "is_return_update": eu.get("kind") == "mc_first_visit",
    }


def table_snapshot(step: dict) -> dict | None:
    """tables: kind, before/after grids, active/bootstrap/changed cells, action labels."""
    tb = step.get("tables")
    if not isinstance(tb, dict) or not tb.get("after"):
        return None
    return tb
