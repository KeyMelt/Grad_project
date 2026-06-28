"""Trace replay — a silent, real-time visualisation of one successful run.

Built entirely from the run data. Per step it shows the agent acting on the REAL Gymnasium
environment (FrozenLake elf, CliffWalking hiker, Blackjack hand), and an 'update card' with
the exact arithmetic of that step's value/Q update — what was sampled, the TD target, the
error, and the nudge. No narration; the visuals carry it.

Invoke (the trace renderer does this):
    python -m manim -q<quality> --media_dir <dir> trace_replay_scene.py TraceReplayScene
with TRACE_DATA_PATH set to a JSON file holding the list of step dicts (and optionally
TRACE_EPISODE_LABEL for a per-episode clip header).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from manim import (  # noqa: E402
    DOWN, FadeIn, FadeOut, Scene, Text, Transform, UP,
)

from manim_service.trace_scenes import trace_common as C  # noqa: E402
from manim_service.trace_scenes.trace_boards import make_board  # noqa: E402
from manim_service.trace_scenes.trace_step_director import play_step  # noqa: E402

DATA_PATH = os.environ.get("TRACE_DATA_PATH", "")
EPISODE_LABEL = os.environ.get("TRACE_EPISODE_LABEL", "")

_STATE_KEY_RE = re.compile(r"[QV]\(\s*(\d+)")


def _parse_updated_values(updated: dict | None) -> dict[int, float]:
    """Map ``updated_values`` keys like ``"Q(3, 1)"`` / ``"V(9)"`` to ``{state: value}``,
    keyed by the SOURCE state (the first index). Pure helper used by the renderer/tests."""
    out: dict[int, float] = {}
    for key, val in (updated or {}).items():
        m = _STATE_KEY_RE.match(str(key))
        if not m:
            continue
        try:
            out[int(m.group(1))] = float(val)
        except (TypeError, ValueError):
            continue
    return out


_KIND_NAME = {
    "q_learning": "Q-learning", "sarsa": "SARSA", "td_prediction": "TD(0) prediction",
    "policy_evaluation": "Policy evaluation", "value_iteration": "Value iteration",
    "policy_improvement": "Policy improvement", "mc_first_visit": "First-visit Monte Carlo",
    "mc_sampling": "Monte Carlo",
}


class TraceReplayScene(Scene):
    def construct(self) -> None:
        self.camera.background_color = C.BG

        if not DATA_PATH:
            return self._error("TRACE_DATA_PATH is not set.")
        try:
            data = json.loads(Path(DATA_PATH).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            return self._error(f"Could not load trace data: {exc}")
        if not isinstance(data, list) or not data:
            return self._error("No replay trace available.")

        # Staged learning-progression: a list of {stage, stage_label, steps:[...]}
        # episodes sampled across training (untrained -> improving -> converged).
        # Legacy: a flat list of step dicts (a single episode).
        if isinstance(data[0], dict) and "steps" in data[0] and "stage" in data[0]:
            stages = [s for s in data if s.get("steps")]
        else:
            stages = [{"stage": "converged", "stage_label": EPISODE_LABEL, "steps": data}]

        for si, ep in enumerate(stages):
            lite = ep.get("stage") not in (None, "converged")
            self._render_episode(
                ep["steps"], ep.get("stage_label") or "",
                lite=lite, last=(si == len(stages) - 1),
            )

        self.wait(1.0)

    def _render_episode(self, steps, stage_label, *, lite, last) -> None:
        env = C.detect_env(steps)
        kind = (steps[0].get("equation_update") or {}).get("kind", "")
        algo = _KIND_NAME.get(kind, "Trace replay")
        title = stage_label or EPISODE_LABEL or f"{algo}  ·  {env}"

        # Bound rendered steps so neither flailing nor a long solve blows up the
        # render time / video length. Lite stages get a tiny window; the rich
        # converged stage keeps the opening and the decisive ending (the goal).
        if lite and len(steps) > 8:
            steps = steps[:6] + steps[-2:]
        elif not lite and len(steps) > 16:
            steps = steps[:10] + steps[-6:]

        header = Text(title, font_size=24, color=C.TEXT).to_edge(UP, buff=0.3)
        n = len(steps)
        counter = self._counter(1, n).next_to(header, DOWN, buff=0.12)

        board = make_board(env, steps[0])
        # CliffWalking is a wide 4x12 grid -> a wide card sits below it; Taxi,
        # FrozenLake, and Blackjack leave room for a tall card on the right.
        if env == "CliffWalking":
            card_pos, card_w = [0.0, -2.35, 0.0], 9.4
        else:
            card_pos, card_w = [3.4, 0.1, 0.0], 5.7

        self.play(FadeIn(header), FadeIn(counter), FadeIn(board.mob), run_time=0.5)
        self.wait(0.15)

        for idx, step in enumerate(steps, start=1):
            new_counter = self._counter(idx, n).next_to(header, DOWN, buff=0.12)
            self.play(Transform(counter, new_counter), run_time=0.2)
            card = play_step(self, board, step, env, pos=card_pos, width=card_w,
                             first=(idx == 1), lite=lite, closing=(idx == n and not lite))
            if idx < n:
                card.fade()

        self.wait(0.5 if lite else 1.2)
        # Clean slate between staged episodes (fade everything, then clear).
        if not last and self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.4)
            self.clear()

    def _counter(self, i: int, n: int) -> Text:
        return Text(f"step {i} / {n}", font_size=18, color=C.MUTED)

    def _error(self, message: str) -> None:
        self.add(Text(message, font_size=26, color=C.TEXT))
        self.wait(1.0)
