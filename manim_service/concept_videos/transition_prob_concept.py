"""Canonical reference scene: transition probability p(s'|s,a).

Demonstrates every production pattern:
  - geometry-before-algebra sequencing (3Blue1Brown methodology)
  - SynchronizedFocusGroup across equation labels × grid arrows
  - ActionBarChart with ValueTracker-driven bars
  - CodeStepper for Gymnasium code integration
  - frozenlake_frame with actual PNG assets
  - MathTex component-array decomposition for TransformMatchingTex

Phase order (geometry-first):
  1 — Grid centered, caption                   (wait 2.0)
  2 — Three trial outcomes for RIGHT action    (wait 1.5)
  3 — ActionBarChart reveals distribution      (wait 1.5)
  4 — Grid/chart to anchors, equation earned   (wait 2.0)
  5 — Synchronized walkthrough per action      (wait 1.5 each)
  6 — Gymnasium code reveal                    (wait 1.5)
  7 — Hold frame                               (wait 2.5)

Environment: FrozenLake-v1, state 6, slippery ice.
Action convention: 0=LEFT 1=DOWN 2=RIGHT 3=UP
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `python -m manim -ql transition_prob_concept.py TransitionProbConcept`
# from any working directory (adds project root to path).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    FadeIn,
    FadeOut,
    LaggedStart,
    MathTex,
    ReplacementTransform,
    Text,
    VGroup,
    Write,
)

try:
    from manim import GREY_A
except ImportError:
    GREY_A = "#BBBBBB"

from manim_service.scenes import (
    ACTION_COLOR,
    OPACITY_SECONDARY,
    STATE_COLOR,
    ActionBarChart,
    BaseConceptScene,
    CodeStepper,
    SynchronizedFocusGroup,
    action_arrows_overlay,
    frozenlake_frame,
)

# ---------------------------------------------------------------------------
# FrozenLake-v1, state 6, action RIGHT — actual transition table values
# Index order: [prob landing LEFT, prob landing DOWN, prob landing RIGHT, prob landing UP]
# ---------------------------------------------------------------------------
_STOCHASTIC_PROBS = {
    "left":  [0.33, 0.33, 0.33, 0.0],
    "down":  [0.0,  0.33, 0.33, 0.33],
    "right": [0.33, 0.0,  0.33, 0.33],
    "up":    [0.33, 0.33, 0.0,  0.33],
}

# State 6 (row 1, col 2). RIGHT action → 3 non-zero outcomes:
#   state 7  (row 1, col 3) — went right as intended, prob 0.33
#   state 2  (row 0, col 2) — slipped up,             prob 0.33
#   state 5  (row 1, col 1) — slipped left,            prob 0.33
_TRIAL_OUTCOMES = [7, 2, 5]
_TRIAL_CAPTIONS = [
    "Trial 1: landed at state 7  (went right as intended)",
    "Trial 2: slipped to state 2  (ice pushed the agent up)",
    "Trial 3: slipped to state 5  (ice pushed the agent left)",
]

_ACTION_SYMBOLS = ["←", "↓", "→", "↑"]
_ACTION_NAMES   = ["LEFT", "DOWN", "RIGHT", "UP"]
_ACTION_KEYS    = ["left", "down", "right", "up"]
_ACTION_CAPTIONS = [
    "Go LEFT — three equally likely outcomes",
    "Go DOWN — three equally likely outcomes",
    "Go RIGHT — what we saw in the trials",
    "Go UP — three equally likely outcomes",
]

_GRID_HEIGHT_FULL   = 4.0   # Phase 1–3: grid centered large
_GRID_HEIGHT_SMALL  = 2.85  # Phase 4+: grid at left anchor
_CHART_WIDTH        = 3.2
_CHART_HEIGHT       = 2.6


class TransitionProbConcept(BaseConceptScene):
    """Reference scene for the manim_service production system."""

    STOCHASTIC_PROBS = _STOCHASTIC_PROBS

    def construct(self) -> None:
        self._phase1_geometry_entry()
        self._phase2_agent_trials()
        self._phase3_bar_chart_reveal()
        self._phase4_equation_earned()
        self._phase5_synchronized_walkthrough()
        self._phase6_code_reveal()
        self._phase7_hold_frame()

    # ------------------------------------------------------------------
    # Phase 1 — Geometry entry
    # ------------------------------------------------------------------

    def _phase1_geometry_entry(self) -> None:
        self._grid = frozenlake_frame(6, height=_GRID_HEIGHT_FULL)
        self._caption = self.place_caption(
            "Slippery ice — the agent doesn't always go where it intends"
        )
        self.play(
            FadeIn(self._grid, shift=DOWN * 0.12),
            FadeIn(self._caption, shift=UP * 0.08),
        )
        self.assimilation_wait(2.0)

    # ------------------------------------------------------------------
    # Phase 2 — Staggered agent traversal
    # ------------------------------------------------------------------

    def _phase2_agent_trials(self) -> None:
        intro_cap = self.place_caption('Try "go RIGHT" three times on slippery ice...')
        self.play(FadeOut(self._caption), FadeIn(intro_cap))
        self._caption = intro_cap
        self.wait(0.8)

        for state, cap_text in zip(_TRIAL_OUTCOMES, _TRIAL_CAPTIONS):
            new_frame = frozenlake_frame(state, height=_GRID_HEIGHT_FULL)
            new_cap = self.place_caption(cap_text)
            self.play(
                ReplacementTransform(self._grid, new_frame),
                FadeOut(self._caption),
                FadeIn(new_cap),
                run_time=0.65,
            )
            self._grid = new_frame
            self._caption = new_cap
            self.wait(0.55)

        # Return to state 6
        state6_frame = frozenlake_frame(6, height=_GRID_HEIGHT_FULL)
        final_cap = self.place_caption("Same action — three different outcomes. It's stochastic.")
        self.play(
            ReplacementTransform(self._grid, state6_frame),
            FadeOut(self._caption),
            FadeIn(final_cap),
            run_time=0.65,
        )
        self._grid = state6_frame
        self._caption = final_cap
        self.assimilation_wait(1.5)

    # ------------------------------------------------------------------
    # Phase 3 — ActionBarChart reveal
    # ------------------------------------------------------------------

    def _phase3_bar_chart_reveal(self) -> None:
        self._chart = ActionBarChart(
            _ACTION_SYMBOLS,
            [0.25, 0.25, 0.25, 0.25],
            width=_CHART_WIDTH,
            height=_CHART_HEIGHT,
        )
        self._chart.next_to(self._grid, RIGHT, buff=0.45)

        new_cap = self.place_caption(
            "The distribution over outcomes — for the RIGHT action from state 6"
        )
        self.play(
            FadeIn(self._chart, shift=LEFT * 0.18),
            FadeOut(self._caption),
            FadeIn(new_cap),
        )
        self._caption = new_cap

        # Animate to actual RIGHT-action probabilities: [0.33, 0.0, 0.33, 0.33]
        self._chart.update_bars(self, _STOCHASTIC_PROBS["right"])
        self.assimilation_wait(1.5)

    # ------------------------------------------------------------------
    # Phase 4 — Equation earned by the visual
    # ------------------------------------------------------------------

    def _phase4_equation_earned(self) -> None:
        # --- move grid (scaled down) to left anchor, chart to right anchor ---
        self.play(
            self._grid.animate.set_height(_GRID_HEIGHT_SMALL).to_edge(LEFT, buff=0.5),
            self._chart.animate.to_edge(RIGHT, buff=0.45),
            run_time=1.1,
        )

        # --- compact equation in center (component array for TransformMatchingTex) ---
        p_compact = MathTex(
            "p", "(", "s'", "|", "s", ",", "a", ")",
            font_size=58,
        )
        # 0:p  1:(  2:s'  3:|  4:s  5:,  6:a  7:)
        p_compact[2].set_color(STATE_COLOR)   # s'
        p_compact[4].set_color(STATE_COLOR)   # s
        p_compact[6].set_color(ACTION_COLOR)  # a

        earned_cap = self.place_caption(
            "Now we can name what we just saw — the transition probability"
        )
        self.play(
            FadeOut(self._caption),
            Write(p_compact),
        )
        self.play(FadeIn(earned_cap))
        self._caption = earned_cap
        self.assimilation_wait(2.0)

        # --- expand to formal probability notation ---
        p_formal = MathTex(
            "p", "(", "s'", "|", "s", ",", "a", ")",
            "=",
            "\\Pr",
            "\\bigl(",
            "S_{t+1}", "=", "s'",
            "\\mid",
            "S_t", "=", "s",
            ",\\,",
            "A_t", "=", "a",
            "\\bigr)",
            font_size=36,
        )
        # Color-geometry binding: same variables, same colors
        p_formal[2].set_color(STATE_COLOR)    # s' (compact side)
        p_formal[4].set_color(STATE_COLOR)    # s  (compact side)
        p_formal[6].set_color(ACTION_COLOR)   # a  (compact side)
        p_formal[13].set_color(STATE_COLOR)   # s' (expanded side)
        p_formal[16].set_color(STATE_COLOR)   # s  (expanded side)
        p_formal[19].set_color(ACTION_COLOR)  # a  (expanded side)

        self.play(ReplacementTransform(p_compact, p_formal))
        self._p_eq = p_formal
        self.assimilation_wait(2.0)

        # --- 4 action labels below equation for Phase 5 SynchronizedFocusGroup ---
        self._eq_action_labels = VGroup(*[
            MathTex(f"a {{{name}}}", font_size=20, color=ACTION_COLOR)
            for name in _ACTION_NAMES
        ]).arrange(RIGHT, buff=0.55)
        self._eq_action_labels.next_to(self._p_eq, DOWN, buff=0.42)

        self.play(
            LaggedStart(
                *[FadeIn(lbl, shift=UP * 0.08) for lbl in self._eq_action_labels],
                lag_ratio=0.2,
            )
        )

    # ------------------------------------------------------------------
    # Phase 5 — Synchronized walkthrough
    # ------------------------------------------------------------------

    def _phase5_synchronized_walkthrough(self) -> None:
        # Action arrows centered on the (now-scaled, left-positioned) grid
        grid_center = self._grid.get_center()
        self._arrows = action_arrows_overlay(
            grid_center,
            arrow_len=0.38,
            stroke_width=3.5,
            color=ACTION_COLOR,
        )
        self.play(FadeIn(self._arrows, shift=DOWN * 0.04))

        # SynchronizedFocusGroup: equation action labels × grid arrows
        # (chart bars are always_redraw mobs — updated separately via highlight_bar)
        eq_list     = list(self._eq_action_labels)
        arrows_list = list(self._arrows)
        sync = SynchronizedFocusGroup(eq_list, arrows_list)

        # Start with everything dimmed
        self.play(
            *sync.dim_all(),
            *[b.animate.set_opacity(OPACITY_SECONDARY) for b in self._chart._bars],
        )

        for idx, (key, cap_text) in enumerate(zip(_ACTION_KEYS, _ACTION_CAPTIONS)):
            new_cap = self.place_caption(cap_text)
            # Sync highlights label + arrow in one beat
            self.play(
                *sync.step(self, idx),
                FadeOut(self._caption),
                FadeIn(new_cap),
                self._chart._bars[idx].animate.set_opacity(1.0),
            )
            self._caption = new_cap
            # Chart updates in a separate beat so bar growth is its own visual event
            self._chart.update_bars(self, _STOCHASTIC_PROBS[key])
            self.assimilation_wait(1.5)

        # Reset opacity before Phase 6
        self.play(
            *sync.reset_all(),
            *[b.animate.set_opacity(1.0) for b in self._chart._bars],
        )

    # ------------------------------------------------------------------
    # Phase 6 — Gymnasium code reveal
    # ------------------------------------------------------------------

    def _phase6_code_reveal(self) -> None:
        code = CodeStepper(
            [
                "env = gym.make('FrozenLake-v1')",
                "P = env.unwrapped.P[s][a]",
                "# [(prob, next_s, reward, done), ...]",
            ],
            title="Gymnasium",
            width=5.1,
            font_size=17,
        )
        self.place_bottom_right_panel(code.panel)

        new_cap = self.place_caption(
            "The same distribution — accessible via env.unwrapped.P"
        )
        self.play(
            FadeIn(code.panel, shift=LEFT * 0.12),
            FadeOut(self._caption),
            FadeIn(new_cap),
        )
        self._caption = new_cap

        # Step through each line with a small pause between
        self.play(*code.step(self, 0))
        self.wait(0.55)
        self.play(*code.step(self, 1))
        self.wait(0.55)
        self.play(*code.step(self, 2))
        self.assimilation_wait(1.5)

    # ------------------------------------------------------------------
    # Phase 7 — Hold frame
    # ------------------------------------------------------------------

    def _phase7_hold_frame(self) -> None:
        final_cap = self.place_caption(
            "p(s'|s,a): the stochastic engine that drives every RL algorithm"
        )
        self.play(FadeOut(self._caption), FadeIn(final_cap))
        self._caption = final_cap
        self.assimilation_wait(2.5)
