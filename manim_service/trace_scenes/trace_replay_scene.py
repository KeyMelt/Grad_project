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
    DOWN, FadeIn, FadeOut, Scene, Text, Transform, ReplacementTransform, VGroup, UP,
)

from manim_service.trace_scenes import trace_common as C  # noqa: E402
from manim_service.trace_scenes.trace_boards import make_board  # noqa: E402
from manim_service.trace_scenes.trace_update_card import make_update_card  # noqa: E402

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
            steps = json.loads(Path(DATA_PATH).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            return self._error(f"Could not load trace data: {exc}")
        if not isinstance(steps, list) or not steps:
            return self._error("No replay trace available.")

        env = C.detect_env(steps)
        kind = (steps[0].get("equation_update") or {}).get("kind", "")
        algo = _KIND_NAME.get(kind, "Trace replay")

        # ---- header -------------------------------------------------------
        header_txt = EPISODE_LABEL or f"{algo}  ·  {env}"
        header = Text(header_txt, font_size=26, color=C.TEXT).to_edge(UP, buff=0.3)
        counter = self._counter(1, len(steps)).next_to(header, DOWN, buff=0.12)

        # ---- board + first card ------------------------------------------
        board = make_board(env, steps[0])
        card_pos = [0.0, -2.2, 0.0] if env == "CliffWalking" else [3.35, 0.15, 0.0]
        card = make_update_card(steps[0], env)
        card.move_to(card_pos)
        if card.width > (5.9 if env != "CliffWalking" else 6.4):
            card.scale_to_fit_width(5.9 if env != "CliffWalking" else 6.4)

        self.play(FadeIn(header), FadeIn(counter), FadeIn(board.mob), run_time=0.6)
        board.place(self, steps[0], run_time=0.35)
        self.play(FadeIn(card), run_time=0.4)
        self.wait(0.3)

        # ---- step loop ----------------------------------------------------
        n = len(steps)
        step_rt = max(0.22, min(0.5, 36.0 / n))
        card_rt = max(0.2, min(0.4, 30.0 / n))
        for idx, step in enumerate(steps[1:], start=2):
            board.step(self, step, run_time=step_rt)
            new_card = make_update_card(step, env).move_to(card_pos)
            if new_card.width > (5.9 if env != "CliffWalking" else 6.4):
                new_card.scale_to_fit_width(5.9 if env != "CliffWalking" else 6.4)
            new_counter = self._counter(idx, n).next_to(header, DOWN, buff=0.12)
            self.play(
                ReplacementTransform(card, new_card),
                Transform(counter, new_counter),
                run_time=card_rt,
            )
            card = new_card
            self.wait(max(0.12, step_rt * 0.4))

        self.wait(1.0)

    def _counter(self, i: int, n: int) -> Text:
        return Text(f"step {i} / {n}", font_size=18, color=C.MUTED)

    def _error(self, message: str) -> None:
        self.add(Text(message, font_size=26, color=C.TEXT))
        self.wait(1.0)
