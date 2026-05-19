"""Value Iteration concept scene — dp_value_iteration.

Phase order (geometry-first, STYLE_BIBLE §7):
  1 — FrozenLake grid centered, agent at state 6, dim action arrows   (wait 2.0)
  2 — Per-action backup: arrow highlights, outcome arrows, bar grows  (wait 1.0 each, then 1.5)
  3 — Grid+chart shift to anchors, update equation earned             (wait 2.0)
  4 — CodeStepper replaces bar chart RIGHT                            (wait 1.5)
  5 — SynchronizedFocusGroup walkthrough ×4 steps                    (wait 1.5 each)
  6 — equation_morph v_{k+1} → V* (convergence insight)              (wait 1.5)
  7 — Hold frame                                                      (wait 2.5)

Environment: FrozenLake-v1 (is_slippery=True), state 6 — one step left of hole at 7.
Action convention: 0=LEFT 1=DOWN 2=RIGHT 3=UP
Bar heights use converged V* at gamma=0.99 (fast-forwarded sweep context).
Tie: LEFT and RIGHT share the optimal backup (0.358), shown explicitly.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    MathTex,
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
    OPACITY_BACKGROUND,
    OPACITY_PRIMARY,
    OPACITY_SECONDARY,
    REWARD_COLOR,
    STATE_COLOR,
    VALUE_COLOR,
    ActionBarChart,
    BaseConceptScene,
    CodeStepper,
    SynchronizedFocusGroup,
    action_arrows_overlay,
    frozenlake_frame,
    panel,
)

# ---------------------------------------------------------------------------
# Scene constants
# ---------------------------------------------------------------------------

_ACTION_SYMBOLS = ["←", "↓", "→", "↑"]
_ACTION_NAMES = ["LEFT", "DOWN", "RIGHT", "UP"]

# Converged V* backups at state 6 (gamma=0.99).
# Verified by Technical Validator — tied optimal: LEFT=RIGHT=0.358.
_BACKUP_VALUES = [0.358, 0.203, 0.358, 0.155]

# Stochastic outcomes per action at state 6 (FrozenLake-v1 slippery).
# Each entry: list of (next_state, terminated) for the 3 non-zero transitions.
# Derived from env.unwrapped.P[6][action] live query.
_OUTCOMES = {
    0: [(2, False), (5, False), (10, False)],   # LEFT → 2, 5, 10
    1: [(5, False), (10, False), (7, True)],    # DOWN → 5, 10, 7(hole)
    2: [(10, False), (7, True), (2, False)],    # RIGHT → 10, 7(hole), 2
    3: [(7, True), (2, False), (5, False)],     # UP → 7(hole), 2, 5
}

_GRID_HEIGHT_FULL = 4.0
_GRID_HEIGHT_SMALL = 2.85
_CHART_WIDTH = 3.2
_CHART_HEIGHT = 2.6


# ---------------------------------------------------------------------------
# Helper — outcome arrows on FrozenLake 4×4 grid
# ---------------------------------------------------------------------------

def _cell_center_abs(grid_mob, state: int) -> np.ndarray:
    """Compute the world-space center of a grid cell given the current grid mob."""
    rows, cols = 4, 4
    cell_w = grid_mob.get_width() / cols
    cell_h = grid_mob.get_height() / rows
    row, col = divmod(state, cols)
    x = grid_mob.get_left()[0] + (col + 0.5) * cell_w
    y = grid_mob.get_top()[1] - (row + 0.5) * cell_h
    return np.array([x, y, 0.0])


def _outcome_arrows(grid_mob, from_state: int, action_idx: int) -> VGroup:
    """Short arrows from from_state center toward each outcome cell center."""
    outcomes = _OUTCOMES[action_idx]
    group = VGroup()
    src = _cell_center_abs(grid_mob, from_state)
    for next_state, terminated in outcomes:
        dst = _cell_center_abs(grid_mob, next_state)
        direction = dst - src
        length = np.linalg.norm(direction)
        if length < 1e-6:
            continue
        arr = Arrow(
            src,
            src + direction * 0.72,
            buff=0.0,
            stroke_width=2.5,
            color=STATE_COLOR,
            max_tip_length_to_length_ratio=0.3,
        )
        arr.set_opacity(OPACITY_PRIMARY)
        group.add(arr)
    return group


# ---------------------------------------------------------------------------
# Main scene
# ---------------------------------------------------------------------------

class ValueIterationConcept(BaseConceptScene):
    """Value Iteration concept video — dp_value_iteration."""

    def construct(self) -> None:
        self._phase1_geometry_entry()
        self._phase2_per_action_backup()
        self._phase3_equation_earned()
        self._phase4_code_panel()
        self._phase5_synchronized_walkthrough()
        self._phase6_convergence_insight()
        self._phase7_hold_frame()

    # ------------------------------------------------------------------
    # Phase 1 — Geometry entry: FrozenLake grid + dim action arrows
    # ------------------------------------------------------------------

    def _phase1_geometry_entry(self) -> None:
        self.show_header("Value Iteration", subtitle="dp_value_iteration")

        self._grid = frozenlake_frame(6, height=_GRID_HEIGHT_FULL)
        self._grid.center()

        self._arrows = action_arrows_overlay(
            self._grid.get_center(),
            arrow_len=0.42,
            stroke_width=3.5,
            color=ACTION_COLOR,
        )
        self._arrows.set_opacity(OPACITY_SECONDARY)

        self._caption = self.place_caption(
            "State 6 — four possible actions, but the ice is slippery."
        )

        self.play(
            FadeIn(self._grid, shift=DOWN * 0.12),
            FadeIn(self._caption, shift=UP * 0.08),
        )
        self.play(FadeIn(self._arrows))
        self.assimilation_wait(2.0)

    # ------------------------------------------------------------------
    # Phase 2 — Per-action backup: highlight arrow, show outcome arrows,
    #           grow ActionBarChart bar, dim arrow back
    # ------------------------------------------------------------------

    def _phase2_per_action_backup(self) -> None:
        # Fast-forward context caption
        fwd_cap = self.place_caption(
            "Fast-forward to after many sweeps — values have settled."
        )
        self.play(FadeOut(self._caption), FadeIn(fwd_cap))
        self._caption = fwd_cap
        self.wait(0.8)

        # Build chart (starts at zero — grows bar by bar)
        self._chart = ActionBarChart(
            _ACTION_SYMBOLS,
            [0.0, 0.0, 0.0, 0.0],
            width=_CHART_WIDTH,
            height=_CHART_HEIGHT,
        )
        self._chart.next_to(self._grid, RIGHT, buff=0.5)
        self.play(FadeIn(self._chart, shift=LEFT * 0.18))

        action_captions = [
            "LEFT: three stochastic outcomes, expected backup ≈ 0.358",
            "DOWN: one outcome leads to the hole — lower backup ≈ 0.203",
            "RIGHT: same outcomes as LEFT, backup ≈ 0.358  (tied optimal)",
            "UP: hole risk again — lowest backup ≈ 0.155",
        ]

        current_values = [0.0, 0.0, 0.0, 0.0]

        for action_idx in range(4):
            # Highlight this action's arrow
            main_arrow = list(self._arrows)[action_idx]
            self.play(main_arrow.animate.set_opacity(OPACITY_PRIMARY))

            # Outcome arrows fade in
            out_arrs = _outcome_arrows(self._grid, 6, action_idx)
            self.play(LaggedStart(*[FadeIn(a) for a in out_arrs], lag_ratio=0.18))

            # Grow bar to backup value
            current_values[action_idx] = _BACKUP_VALUES[action_idx]
            self._chart.update_bars(self, list(current_values))

            # Update caption
            new_cap = self.place_caption(action_captions[action_idx])
            self.play(FadeOut(self._caption), FadeIn(new_cap))
            self._caption = new_cap

            self.wait(1.0)

            # Clean up outcome arrows, dim action arrow back
            self.play(
                FadeOut(out_arrs),
                main_arrow.animate.set_opacity(OPACITY_SECONDARY),
            )

        end_cap = self.place_caption(
            "Each action has a different expected future. LEFT and RIGHT are tied at the top."
        )
        self.play(FadeOut(self._caption), FadeIn(end_cap))
        self._caption = end_cap
        self.assimilation_wait(1.5)

    # ------------------------------------------------------------------
    # Phase 3 — Grid+chart shift to anchors; update equation earned
    # ------------------------------------------------------------------

    def _phase3_equation_earned(self) -> None:
        # Reposition grid (smaller) to left and chart to right
        self.play(
            self._grid.animate.set_height(_GRID_HEIGHT_SMALL).to_edge(LEFT, buff=0.5),
            self._chart.animate.to_edge(RIGHT, buff=0.45),
            self._arrows.animate.set_opacity(0.0),  # hide arrows during reposition
            run_time=1.1,
        )

        # Build the update equation as a component array (mandatory for TransformMatchingTex)
        self._v_update = MathTex(
            "v_{k+1}", "(", "s", ")", "=",
            r"\max_a",
            r"\sum_{s',r}",
            "p(", "s'", ",", "r",
            r"\mid", "s", ",", "a", ")",
            "[", "r", "+",
            r"\gamma",
            "v_k", "(", "s'", ")", "]",
            font_size=28,
        )
        # Color-geometry binding (STYLE_BIBLE §1 rule)
        self._v_update[0].set_color(VALUE_COLOR)   # v_{k+1}
        self._v_update[2].set_color(STATE_COLOR)   # s
        self._v_update[5].set_color(ACTION_COLOR)  # max_a
        self._v_update[8].set_color(STATE_COLOR)   # s'
        self._v_update[10].set_color(REWARD_COLOR) # r (inside p)
        self._v_update[12].set_color(STATE_COLOR)  # s (inside p)
        self._v_update[14].set_color(ACTION_COLOR) # a (inside p)
        self._v_update[17].set_color(REWARD_COLOR) # r (in brackets)
        self._v_update[20].set_color(VALUE_COLOR)  # v_k
        self._v_update[22].set_color(STATE_COLOR)  # s'

        # Wrap in a panel with the equation as the body Mobject
        self._eq_panel = panel(
            "Update Rule",
            self._v_update,
            accent=VALUE_COLOR,
            width=5.6,
            min_height=2.0,
        )
        self.place_left_panel(self._eq_panel)

        eq_cap = self.place_caption(
            "The update rule: take the maximum one-step backup."
        )
        self.play(
            FadeOut(self._caption),
            FadeIn(self._eq_panel, shift=RIGHT * 0.12),
        )
        self.play(FadeIn(eq_cap))
        self._caption = eq_cap
        self.assimilation_wait(2.0)

    # ------------------------------------------------------------------
    # Phase 4 — CodeStepper fades in RIGHT; chart dims
    # ------------------------------------------------------------------

    def _phase4_code_panel(self) -> None:
        self._code = CodeStepper(
            [
                "for action in range(action_count):",
                "  action_value += t_prob*(reward+gamma*future)",
                "  action_values.append(action_value)",
                "V[state] = max(action_values)",
            ],
            title="Value Iteration",
            width=5.4,
            font_size=17,
        )
        self.place_mid_right_panel(self._code.panel)

        # Dim chart before swapping
        self.play(
            *self._chart.dim_all(),
            FadeIn(self._code.panel, shift=LEFT * 0.12),
        )

        code_cap = self.place_caption("These are the core update lines.")
        self.play(FadeOut(self._caption), FadeIn(code_cap))
        self._caption = code_cap
        self.assimilation_wait(1.5)

    # ------------------------------------------------------------------
    # Phase 5 — Synchronized walkthrough: eq × arrows × code ×4 steps
    # ------------------------------------------------------------------

    def _phase5_synchronized_walkthrough(self) -> None:
        # Re-show action arrows on the repositioned (smaller) grid
        self._arrows = action_arrows_overlay(
            self._grid.get_center(),
            arrow_len=0.32,
            stroke_width=3.0,
            color=ACTION_COLOR,
        )
        self._arrows.set_opacity(OPACITY_SECONDARY)
        self.play(FadeIn(self._arrows))

        # Restore chart to primary, ensure bars are set
        self.play(*self._chart.reset_all())
        self._chart.update_bars(self, _BACKUP_VALUES)

        # Items to synchronize:
        # eq group: the key sub-mobjects of the update equation
        eq_max_a = self._v_update[5]        # max_a
        eq_sum   = self._v_update[6]        # sum_{s',r}
        eq_p     = VGroup(*self._v_update[7:16])  # p(s',r|s,a)
        eq_vk    = VGroup(
            self._v_update[20],
            self._v_update[21],
            self._v_update[22],
            self._v_update[23],
            self._v_update[24],
        )  # v_k(s')

        # Action arrows: list indexed 0=LEFT 1=DOWN 2=RIGHT 3=UP
        arrows_list = list(self._arrows)

        # Chart opacity trackers for each bar
        chart_opacities = self._chart._opacity_trackers

        sync_labels = [
            "max_a: iterate over all actions — the loop",
            "Weighted sum — stochastic transitions p(s',r|s,a)",
            "Store each action's backup value",
            "Keep the maximum — that becomes v_{k+1}(s)",
        ]

        # Dim everything to SECONDARY first
        all_eq_items = [eq_max_a, eq_sum, eq_p, eq_vk]
        self.play(
            *[m.animate.set_opacity(OPACITY_SECONDARY) for m in all_eq_items],
            *[a.animate.set_opacity(OPACITY_SECONDARY) for a in arrows_list],
            *self._chart.dim_all(),
        )

        # Step 0: loop over actions — max_a + all arrows pulse
        step0_cap = self.place_caption(sync_labels[0])
        self.play(
            eq_max_a.animate.set_opacity(OPACITY_PRIMARY),
            *[a.animate.set_opacity(OPACITY_PRIMARY) for a in arrows_list],
            *self._chart.reset_all(),
            *self._code.step(self, 0),
            FadeOut(self._caption), FadeIn(step0_cap),
        )
        self._caption = step0_cap
        self.assimilation_wait(1.5)

        # Step 1: summation — eq_sum + eq_p + outcome arrows flash, current bar highlights
        step1_cap = self.place_caption(sync_labels[1])
        out_arrs_all = VGroup(*[
            _outcome_arrows(self._grid, 6, a) for a in range(4)
        ])
        self.play(
            eq_max_a.animate.set_opacity(OPACITY_SECONDARY),
            eq_sum.animate.set_opacity(OPACITY_PRIMARY),
            eq_p.animate.set_opacity(OPACITY_PRIMARY),
            FadeIn(out_arrs_all),
            *self._code.step(self, 1),
            FadeOut(self._caption), FadeIn(step1_cap),
        )
        self._caption = step1_cap
        self.assimilation_wait(1.5)

        # Step 2: store backup — brackets highlight, outcome arrows fade
        step2_cap = self.place_caption(sync_labels[2])
        eq_brackets = VGroup(self._v_update[16], self._v_update[24])  # [ and ]
        self.play(
            eq_sum.animate.set_opacity(OPACITY_SECONDARY),
            eq_p.animate.set_opacity(OPACITY_SECONDARY),
            eq_brackets.animate.set_opacity(OPACITY_PRIMARY),
            eq_vk.animate.set_opacity(OPACITY_PRIMARY),
            FadeOut(out_arrs_all),
            *self._code.step(self, 2),
            FadeOut(self._caption), FadeIn(step2_cap),
        )
        self._caption = step2_cap
        self.assimilation_wait(1.5)

        # Step 3: max → winning bars (LEFT idx=0, RIGHT idx=2 tied), flash state 6
        step3_cap = self.place_caption(
            "Two actions tie — value iteration can produce multiple optimal policies."
        )
        self.play(
            eq_brackets.animate.set_opacity(OPACITY_SECONDARY),
            eq_vk.animate.set_opacity(OPACITY_SECONDARY),
            eq_max_a.animate.set_opacity(OPACITY_PRIMARY),
            self._v_update[0].animate.set_opacity(OPACITY_PRIMARY),  # v_{k+1}
            *self._chart.dim_all(),
            chart_opacities[0].animate.set_value(OPACITY_PRIMARY),  # LEFT bar
            chart_opacities[2].animate.set_value(OPACITY_PRIMARY),  # RIGHT bar
            *self._code.step(self, 3),
            FadeOut(self._caption), FadeIn(step3_cap),
        )
        self._caption = step3_cap

        # Flash tied optimal bars to indicate the tie
        self.play(
            self._chart.highlight_bar(0),
            self._chart.highlight_bar(2),
        )
        self.assimilation_wait(1.5)

    # ------------------------------------------------------------------
    # Phase 6 — Convergence insight: v_{k+1}(s) → V*(s)
    # ------------------------------------------------------------------

    def _phase6_convergence_insight(self) -> None:
        # V* equation — same token structure but k+1 subscript → * and v_k → V*
        self._v_star = MathTex(
            "V_*", "(", "s", ")", "=",
            r"\max_a",
            r"\sum_{s',r}",
            "p(", "s'", ",", "r",
            r"\mid", "s", ",", "a", ")",
            "[", "r", "+",
            r"\gamma",
            "V_*", "(", "s'", ")", "]",
            font_size=28,
        )
        self._v_star[0].set_color(VALUE_COLOR)   # V*
        self._v_star[2].set_color(STATE_COLOR)   # s
        self._v_star[5].set_color(ACTION_COLOR)  # max_a
        self._v_star[8].set_color(STATE_COLOR)   # s'
        self._v_star[10].set_color(REWARD_COLOR) # r
        self._v_star[12].set_color(STATE_COLOR)  # s
        self._v_star[14].set_color(ACTION_COLOR) # a
        self._v_star[17].set_color(REWARD_COLOR) # r
        self._v_star[20].set_color(VALUE_COLOR)  # V*
        self._v_star[22].set_color(STATE_COLOR)  # s'

        conv_cap = self.place_caption(
            "Repeat sweep by sweep — when values stop changing, you have V*."
        )

        # Restore all equation parts to primary before morph
        self.play(
            *[m.animate.set_opacity(OPACITY_PRIMARY) for m in self._v_update],
        )

        from manim_service.scenes import equation_morph
        equation_morph(self, self._v_update, self._v_star, run_time=1.3)

        self.play(FadeOut(self._caption), FadeIn(conv_cap))
        self._caption = conv_cap
        self.assimilation_wait(1.5)

    # ------------------------------------------------------------------
    # Phase 7 — Hold frame: stable scene, final caption
    # ------------------------------------------------------------------

    def _phase7_hold_frame(self) -> None:
        # Dim supporting elements to SECONDARY; V* equation stays PRIMARY
        self.play(
            *self._code.reset(self),
            *[a.animate.set_opacity(OPACITY_SECONDARY) for a in list(self._arrows)],
            *self._chart.dim_all(),
        )

        final_cap = self.place_caption(
            "Value iteration: replace the policy average with the best one-step backup."
            " Ties mean multiple optimal policies."
        )
        self.play(FadeOut(self._caption), FadeIn(final_cap))
        self._caption = final_cap
        self.assimilation_wait(2.5)
