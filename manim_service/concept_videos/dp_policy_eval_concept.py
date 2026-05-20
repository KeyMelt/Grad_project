"""Policy Evaluation concept scene — dp_policy_eval (v3 rebuild, 2026-05-20).

v3 corrects every issue the user flagged on the v2 render:
- The FrozenLake env grid is the spine. ONE EnvironmentValueHeatmap is
  instantiated in Phase 1 and migrates/resizes through to Phase 8 — it
  never re-instantiates and never sits stale (Phases 2–3 work directly
  inside it via in-grid highlights, not a synthetic Bellman fork).
- The agent is the actual `elf_down.png` Gymnasium sprite via
  `EnvironmentValueHeatmap.place_agent()`, not a `Dot`.
- The iteration display uses the env-asset value heatmap with proper
  cell-bounded numeric labels.
- Only ONE equation is written (the iterative form). No morph chain.
- Sprite motion in Phase 4 is bound to equation token highlights via
  `sprite_action_binding` per STYLE_BIBLE §26.
- Code panel in Phase 5 is cross-highlighted with actual heatmap cells
  via `cross_highlight_pair` against `heatmap.cell_bbox()`.

Phase order:
  1. Motivation — elf walks the grid under equiprobable π
  2. Slippery outcomes IN-GRID — focal cell + 3 outcome arrows on real cells
  3. Earn v_iter — one equation, 4 trace_vectors to grid anchors
  4. Iteration on env-heatmap — sprite-math binding demo + 5 V_k sweeps
  5. Code walkthrough — verbatim specs.py + cross-highlight to cells
  6. Misconception — contrast pair of env-heatmaps
  7. Boundaries — terminal cells + Δ-vs-k plot
  8. Closing — next-DAG preview
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from manim import (
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    MathTex,
    ReplacementTransform,
    SurroundingRectangle,
    Text,
    VGroup,
    Write,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
)

try:
    from manim import GREY_A
except ImportError:
    GREY_A = "#BBBBBB"

from manim_service.scenes import (
    ACTION_COLOR,
    BG_PANEL,
    OPACITY_PRIMARY,
    OPACITY_SECONDARY,
    PENALTY_COLOR,
    POLICY_COLOR,
    REWARD_COLOR,
    STATE_COLOR,
    VALUE_COLOR,
    BaseConceptScene,
    CodeStepper,
    EnvironmentValueHeatmap,
    cross_highlight_pair,
    pan_to_follow,
    sprite_action_binding,
    trace_vector,
    zoom_reset,
    zoom_to,
)


# ---------------------------------------------------------------------------
# Verified V_k snapshots (Technical Validator 2026-05-20, equiprobable π, γ=0.99)
# ---------------------------------------------------------------------------
_V_0 = [0.0] * 16
_V_1 = [0.0] * 16; _V_1[14] = 0.25
_V_2 = [0.0] * 16; _V_2[10] = 0.062; _V_2[13] = 0.062; _V_2[14] = 0.312
_V_5 = [
    0.0000, 0.0009, 0.0057, 0.0009,
    0.0019, 0.0000, 0.0257, 0.0000,
    0.0123, 0.0561, 0.1093, 0.0000,
    0.0000, 0.1340, 0.3984, 0.0000,
]
_V_10 = [
    0.0051, 0.0053, 0.0140, 0.0056,
    0.0094, 0.0000, 0.0356, 0.0000,
    0.0274, 0.0788, 0.1328, 0.0000,
    0.0000, 0.1643, 0.4276, 0.0000,
]
_V_CONVERGED = [
    0.0124, 0.0104, 0.0193, 0.0095,
    0.0148, 0.0000, 0.0389, 0.0000,
    0.0326, 0.0843, 0.1378, 0.0000,
    0.0000, 0.1703, 0.4336, 0.0000,
]
_V_LEFT_POLICY = [0.0] * 16


# Code lines — VERBATIM from specs.py.code_focus_lines (real Python)
_CODE_LINES: tuple[str, ...] = (
    "for action, action_prob in enumerate(policy[state]):",
    "    for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:",
    "        new_value += action_prob * transition_prob * (reward + gamma * V[next_state])",
    "V[state] = new_value",
)


# ---------------------------------------------------------------------------
# Main scene
# ---------------------------------------------------------------------------
class PolicyEvaluationConcept(BaseConceptScene):
    """Policy Evaluation — env-asset-driven throughout."""

    def construct(self) -> None:
        self._phase1_motivation()
        self._phase2_slippery_outcomes()
        self._phase3_earn_equation()
        self._phase4_iteration_demo()
        self._phase5_code_walkthrough()
        self._phase6_misconception()
        self._phase7_boundaries()
        self._phase8_closing()

    # ------------------------------------------------------------------
    # Phase 1 — Motivation: elf walks the grid
    # ------------------------------------------------------------------
    def _phase1_motivation(self) -> None:
        self.mark_phase("motivation")
        self._header = self.show_header(
            "Policy Evaluation",
            subtitle="Computing v_π under a fixed policy",
        )

        # THE spine — single EnvironmentValueHeatmap, lives 1→8
        self._heatmap = EnvironmentValueHeatmap(
            rows=4, cols=4,
            values=_V_0,
            width=5.6,
        )
        self._heatmap.move_to(np.array([0.0, -0.4, 0.0]))

        cap1 = self.place_caption(
            "FrozenLake. The agent follows a policy π — each action with probability 1/4."
        )
        self.play(FadeIn(self._heatmap, shift=DOWN * 0.1), FadeIn(cap1), run_time=1.6)
        self._caption = cap1
        self.wait(3.5)

        # Elf walks a short episode
        self._heatmap.place_agent(self, state=0, direction="down", run_time=0.6)
        self.wait(1.5)

        path = [
            (4, "down"),
            (8, "down"),
            (9, "right"),
            (13, "down"),
            (14, "right"),
        ]
        for s, dirn in path:
            self._heatmap.move_agent(self, state=s, direction=dirn, run_time=0.85)
            self.wait(0.45)

        cap2 = self.place_caption(
            "But the ice is slippery — the agent doesn't always end up where it intended."
        )
        self.play(FadeOut(self._caption), FadeIn(cap2), run_time=0.8)
        self._caption = cap2
        self.wait(4.5)

        cap3 = self.place_caption(
            "Given a fixed π, how good is each state? We compute v_π(s) recursively."
        )
        self.play(FadeOut(self._caption), FadeIn(cap3), run_time=0.8)
        self._caption = cap3
        self.wait(5.0)

        self._heatmap.remove_agent(self, run_time=0.6)

        # End of phase: dismiss header (heatmap stays)
        self.play(FadeOut(self._header), FadeOut(self._caption), run_time=0.8)
        self.ingestion_wait(1.6)

    # ------------------------------------------------------------------
    # Phase 2 — Slippery outcomes shown IN-GRID
    # ------------------------------------------------------------------
    def _phase2_slippery_outcomes(self) -> None:
        self.mark_phase("slippery_outcomes")

        # Focal cell: state 14 (row 3, col 2) — adjacent to goal, classic example
        focal_cell = self._heatmap.cell_bbox(14)
        self._focal_halo = SurroundingRectangle(
            focal_cell, color=STATE_COLOR, buff=0.02, stroke_width=3.5,
        )
        self._focal_halo.set_z_index(35)

        s_label = MathTex("s", color=STATE_COLOR, font_size=30)
        s_label.next_to(self._heatmap, UP, buff=0.18).shift(LEFT * 0.6)
        self._s_label = s_label

        cap = self.place_caption("Stand at state s. Pick one action — say, RIGHT.")
        self.play(Create(self._focal_halo), Write(s_label), FadeIn(cap), run_time=1.4)
        self._caption = cap
        self.wait(3.0)

        # The RIGHT action arrow goes from the focal cell — outside the heatmap edge for clarity
        right_arrow_start = focal_cell.get_center()
        right_arrow_end = right_arrow_start + RIGHT * 0.55
        from manim import Arrow
        right_arrow = Arrow(
            right_arrow_start, right_arrow_end,
            buff=0.05, stroke_width=3.5, color=ACTION_COLOR,
            max_tip_length_to_length_ratio=0.35,
        )
        right_arrow.set_z_index(36)
        a_label = MathTex("a = \\text{RIGHT}", color=ACTION_COLOR, font_size=24)
        a_label.next_to(right_arrow, UP, buff=0.08)
        self.play(FadeIn(right_arrow), Write(a_label), run_time=1.2)
        self.wait(2.5)

        cap2 = self.place_caption(
            "Slippery ice — RIGHT can land on any of three cells with probability 1/3 each."
        )
        self.play(FadeOut(self._caption), FadeIn(cap2), run_time=0.8)
        self._caption = cap2
        self.wait(3.5)

        # Three short arrows from focal cell to outcome cells (states 10, 7, 2)
        outcome_states = [10, 7, 2]
        outcome_arrows = VGroup()
        outcome_halos = VGroup()
        prob_labels = VGroup()
        for ns in outcome_states:
            target_cell = self._heatmap.cell_bbox(ns)
            src = focal_cell.get_center()
            dst = target_cell.get_center()
            arr = Arrow(
                src, dst,
                buff=0.18, stroke_width=2.5, color=STATE_COLOR,
                max_tip_length_to_length_ratio=0.15,
            )
            arr.set_z_index(37)
            outcome_arrows.add(arr)

            halo = SurroundingRectangle(
                target_cell, color=STATE_COLOR, buff=0.02, stroke_width=2.0,
            )
            halo.set_stroke(opacity=0.6)
            halo.set_z_index(34)
            outcome_halos.add(halo)

            pl = MathTex(r"\tfrac{1}{3}", color=GREY_A, font_size=20)
            midpoint = (src + dst) / 2.0
            pl.move_to(midpoint).shift(np.array([0.0, 0.18, 0.0]))
            pl.set_z_index(38)
            prob_labels.add(pl)

        self._outcome_arrows = outcome_arrows
        self._outcome_halos = outcome_halos
        self._prob_labels = prob_labels

        self.play(
            LaggedStart(
                *[FadeIn(a) for a in outcome_arrows],
                *[Create(h) for h in outcome_halos],
                *[Write(p) for p in prob_labels],
                lag_ratio=0.12,
            ),
            run_time=2.4,
        )
        self.wait(5.5)

        # Floating r + γv_π(s') annotation just below the focal cell, outside the grid
        leaf_anno = MathTex(
            "r", "+", r"\gamma\,", "v_\\pi", "(", "s'", ")",
            font_size=28,
        )
        leaf_anno[0].set_color(REWARD_COLOR)
        leaf_anno[3].set_color(VALUE_COLOR)
        leaf_anno[5].set_color(STATE_COLOR)
        leaf_anno.next_to(self._heatmap, DOWN, buff=0.20).shift(RIGHT * 1.4)
        self._leaf_anno = leaf_anno

        cap3 = self.place_caption(
            "Each outcome contributes r + γ v_π(s') — reward plus discounted future."
        )
        self.play(FadeOut(self._caption), FadeIn(cap3), Write(leaf_anno), run_time=1.6)
        self._caption = cap3
        self.ingestion_wait(3.0)

        # Dismiss the RIGHT-action-arrow + a_label + outcome arrows + prob labels
        # KEEP focal_halo, s_label, leaf_anno, outcome_halos for Phase 3 traces
        self.play(
            FadeOut(right_arrow),
            FadeOut(a_label),
            FadeOut(outcome_arrows),
            FadeOut(prob_labels),
            FadeOut(self._caption),
            run_time=1.0,
        )
        self.ingestion_wait(1.8)

    # ------------------------------------------------------------------
    # Phase 3 — Earn the iterative equation (ONE equation, 4 traces)
    # ------------------------------------------------------------------
    def _phase3_earn_equation(self) -> None:
        self.mark_phase("equation_earned")

        # Migrate heatmap to LEFT (smaller) to make room for the equation
        self.smooth_move_to(
            self._heatmap,
            np.array([-3.4, -0.4, 0.0]),
            run_time=1.6,
        )
        # Heatmap also shrinks a touch to give equation room
        self.play(
            self._heatmap.animate.set_width(4.0),
            self._focal_halo.animate.move_to(self._heatmap.cell_bbox(14).get_center()),
            self._s_label.animate.next_to(self._heatmap, UP, buff=0.12).shift(LEFT * 0.6),
            *[h.animate.move_to(self._heatmap.cell_bbox(s).get_center())
              for h, s in zip(self._outcome_halos, [10, 7, 2])],
            self._leaf_anno.animate.next_to(self._heatmap, DOWN, buff=0.15),
            run_time=1.4,
        )
        self.ingestion_wait(1.5)

        # The iterative equation — single MathTex (no morph chain)
        v_iter = MathTex(
            "v_{k+1}", "(", "s", ")", r"\;\leftarrow\;",
            r"\sum_{a}", r"\pi", "(", "a", r"\,\mid\,", "s", ")",
            r"\sum_{s',r}", "p", "(", "s'", ",", "r", r"\,\mid\,", "s", ",", "a", ")",
            "\\big[", "r", "+", r"\gamma\,", "v_k", "(", "s'", ")", "\\big]",
            font_size=30,
        )
        # Coloring per STYLE_BIBLE §13 semantic palette
        v_iter[0].set_color(VALUE_COLOR)    # v_{k+1}
        v_iter[2].set_color(STATE_COLOR)    # s
        v_iter[6].set_color(POLICY_COLOR)   # π
        v_iter[8].set_color(ACTION_COLOR)   # a
        v_iter[10].set_color(STATE_COLOR)   # s
        v_iter[15].set_color(STATE_COLOR)   # s'
        v_iter[17].set_color(REWARD_COLOR)  # r (inside p)
        v_iter[19].set_color(STATE_COLOR)   # s
        v_iter[21].set_color(ACTION_COLOR)  # a
        v_iter[24].set_color(REWARD_COLOR)  # r (in bracket)
        v_iter[27].set_color(VALUE_COLOR)   # v_k
        v_iter[29].set_color(STATE_COLOR)   # s'
        v_iter.move_to(np.array([2.4, 0.6, 0.0]))
        self._v_iter = v_iter

        cap = self.place_caption(
            "Treat the Bellman expectation as an assignment. Sweep across states until values stop changing."
        )
        self.play(Write(v_iter), FadeIn(cap), run_time=3.5)
        self._caption = cap
        self.ingestion_wait(2.5)

        # Four trace_vectors to ground the equation
        trace_vector(self, self._focal_halo, v_iter[2], color=STATE_COLOR, run_time=1.4)
        trace_vector(self, self._heatmap.cell_bbox(15), v_iter[24], color=REWARD_COLOR, run_time=1.4)
        trace_vector(self, self._outcome_halos[0], v_iter[29], color=STATE_COLOR, run_time=1.4)
        trace_vector(self, self._leaf_anno, VGroup(*v_iter[24:31]), color=VALUE_COLOR, run_time=1.4)
        self.ingestion_wait(2.5)

        # Dismiss the now-redundant Phase 2 anchors
        self.play(
            FadeOut(self._focal_halo),
            FadeOut(self._s_label),
            FadeOut(self._outcome_halos),
            FadeOut(self._leaf_anno),
            FadeOut(self._caption),
            run_time=1.2,
        )
        self.ingestion_wait(2.5)

    # ------------------------------------------------------------------
    # Phase 4 — Iteration on the env-heatmap with sprite-math binding
    # ------------------------------------------------------------------
    def _phase4_iteration_demo(self) -> None:
        self.mark_phase("iteration_demo")

        # Migrate equation up-left (smaller); grow heatmap back a touch for label readability
        self.play(
            self._v_iter.animate.scale(0.78).to_edge(UP, buff=0.95).shift(LEFT * 0.4),
            self._heatmap.animate.set_width(4.6).move_to(np.array([-2.6, -0.4, 0.0])),
            run_time=1.6,
        )
        self.ingestion_wait(1.6)

        # Iteration counter + Δ label
        k_label = MathTex("k", "=", "0", font_size=34)
        delta_label = MathTex(r"\Delta", "=", "0.00", font_size=30)
        k_label.move_to(np.array([3.0, 0.8, 0.0]))
        delta_label.next_to(k_label, DOWN, buff=0.35).align_to(k_label, LEFT)
        self._k_label = k_label
        self._delta_label = delta_label
        self.play(Write(k_label), Write(delta_label), run_time=1.2)
        self.wait(2.0)

        # ----- Sprite-math binding demo (single Bellman backup) -----
        cap = self.place_caption(
            "Before the full sweep — one backup. The elf shows what one update looks like."
        )
        self.play(FadeIn(cap), run_time=0.8)
        self._caption = cap
        self.wait(2.0)

        # Place the elf at state 14 (focal cell)
        self._heatmap.place_agent(self, state=14, direction="up", run_time=0.7)
        # Camera follows the binding demo
        pan_to_follow(
            self, self._heatmap.cell_bbox(14),
            path_points=[self._heatmap.cell_bbox(14)],
            per_step_run_time=0.8,
            frame_scale=0.95,
        )

        v_kp1_block = VGroup(*self._v_iter[0:5])   # v_{k+1}(s) ←
        v_k_block = VGroup(*self._v_iter[27:32])   # v_k(s')
        other_eq = VGroup(*self._v_iter[5:27])     # everything in between

        cap2 = self.place_caption(
            "Elf at state s. The left side — v_{k+1}(s) — is what we're computing."
        )
        self.play(FadeOut(self._caption), FadeIn(cap2), run_time=0.8)
        self._caption = cap2
        sprite_action_binding(
            self, self._heatmap.agent,
            move_to=self._heatmap.cell_bbox(14),
            highlight_tokens=[v_kp1_block],
            dim_tokens=[v_k_block, other_eq],
            move_run_time=1.0,
            settle_time=3.0,
        )

        cap3 = self.place_caption(
            "Look ahead to one possible next state s'. v_k(s') is the future-value term."
        )
        self.play(FadeOut(self._caption), FadeIn(cap3), run_time=0.8)
        self._caption = cap3
        self._heatmap.move_agent(self, state=10, direction="up", run_time=1.0)
        sprite_action_binding(
            self, self._heatmap.agent,
            move_to=self._heatmap.cell_bbox(10),
            highlight_tokens=[v_k_block],
            dim_tokens=[v_kp1_block, other_eq],
            move_run_time=0.1,  # already moved
            settle_time=3.5,
        )

        cap4 = self.place_caption(
            "Return and write the new value back to v_{k+1}(s). One Bellman backup."
        )
        self.play(FadeOut(self._caption), FadeIn(cap4), run_time=0.8)
        self._caption = cap4
        self._heatmap.move_agent(self, state=14, direction="down", run_time=1.0)
        sprite_action_binding(
            self, self._heatmap.agent,
            move_to=self._heatmap.cell_bbox(14),
            highlight_tokens=[v_kp1_block],
            dim_tokens=[v_k_block, other_eq],
            move_run_time=0.1,
            settle_time=3.0,
        )

        # Cleanup binding demo
        self._heatmap.remove_agent(self, run_time=0.6)
        self.play(
            *[m.animate.set_opacity(OPACITY_PRIMARY) for m in (v_kp1_block, v_k_block, other_eq)],
            run_time=0.8,
        )
        zoom_reset(self, run_time=1.4)
        self.ingestion_wait(2.5)

        # ----- Multi-V_k sweep -----
        cap5 = self.place_caption(
            "Now repeat that backup across every cell, sweep after sweep, until values converge."
        )
        self.play(FadeOut(self._caption), FadeIn(cap5), run_time=0.8)
        self._caption = cap5
        self.wait(3.0)

        # V_1
        cap_v1 = self.place_caption(
            "V_1: only state 14 picks up value. Going RIGHT slips to the goal with prob 1/3 — that's 0.25."
        )
        self.play(FadeOut(self._caption), FadeIn(cap_v1), run_time=0.8)
        self._caption = cap_v1
        self._heatmap.sweep_update(self, _V_1, per_cell_run_time=0.18, carry_indicator=True)
        self._update_k_delta(k=1, delta=0.25)
        self.wait(7.5)

        # V_2
        cap_v2 = self.place_caption(
            "V_2: cells that can transition to 14 pick up value — states 10 and 13."
        )
        self.play(FadeOut(self._caption), FadeIn(cap_v2), run_time=0.8)
        self._caption = cap_v2
        self._heatmap.sweep_update(self, _V_2, per_cell_run_time=0.14, carry_indicator=True)
        self._update_k_delta(k=2, delta=0.062)
        self.wait(7.5)

        # V_5
        cap_v5 = self.place_caption(
            "V_5: a faint gradient extends across most of the grid. Value propagates outward."
        )
        self.play(FadeOut(self._caption), FadeIn(cap_v5), run_time=0.8)
        self._caption = cap_v5
        self._heatmap.sweep_update(self, _V_5, per_cell_run_time=0.10, carry_indicator=False)
        self._update_k_delta(k=5, delta=0.0257)
        self.wait(7.0)

        # V_10
        cap_v10 = self.place_caption(
            "V_10: close to the converged shape. Δ is shrinking exponentially."
        )
        self.play(FadeOut(self._caption), FadeIn(cap_v10), run_time=0.8)
        self._caption = cap_v10
        self._heatmap.sweep_update(self, _V_10, per_cell_run_time=0.08, carry_indicator=False)
        self._update_k_delta(k=10, delta=0.0028)
        self.wait(6.0)

        # V_converged
        cap_vc = self.place_caption(
            "At iteration 71, Δ < θ = 1e-8. We have v_π."
        )
        self.play(FadeOut(self._caption), FadeIn(cap_vc), run_time=0.8)
        self._caption = cap_vc
        self._heatmap.sweep_update(self, _V_CONVERGED, per_cell_run_time=0.08, carry_indicator=False)
        self._update_k_delta(k=71, delta=8.3e-9)
        self.ingestion_wait(3.0)
        self.wait(4.0)

    def _update_k_delta(self, *, k: int, delta: float) -> None:
        new_k = MathTex("k", "=", str(k), font_size=34).move_to(self._k_label)
        new_d = MathTex(
            r"\Delta", "=",
            f"{delta:.2e}" if delta < 0.01 else f"{delta:.4f}",
            font_size=30,
        ).move_to(self._delta_label).align_to(self._k_label, LEFT)
        self.play(
            ReplacementTransform(self._k_label, new_k),
            ReplacementTransform(self._delta_label, new_d),
            run_time=0.7,
        )
        self._k_label = new_k
        self._delta_label = new_d

    # ------------------------------------------------------------------
    # Phase 5 — Code walkthrough with cross-highlights on real heatmap cells
    # ------------------------------------------------------------------
    def _phase5_code_walkthrough(self) -> None:
        self.mark_phase("code_walkthrough")

        # Reposition: heatmap stays LEFT; equation dims to SECONDARY; code panel arrives RIGHT
        self.play(
            self._v_iter.animate.set_opacity(OPACITY_SECONDARY).scale(0.85).to_edge(UP, buff=0.7),
            self._heatmap.animate.set_width(4.0).move_to(np.array([-3.6, -0.6, 0.0])),
            self._k_label.animate.set_opacity(OPACITY_SECONDARY),
            self._delta_label.animate.set_opacity(OPACITY_SECONDARY),
            run_time=1.6,
        )
        self.ingestion_wait(1.6)

        # CodeStepper enters RIGHT
        code = CodeStepper(
            list(_CODE_LINES),
            title="Policy Evaluation update",
            width=7.4,
            font_size=15,
        )
        code.panel.to_edge(RIGHT, buff=0.3).shift(DOWN * 0.2)
        self._code = code

        cap = self.place_caption("Code follows the equation, line by line — bound to grid cells.")
        self.play(FadeOut(self._caption), FadeIn(code.panel, shift=LEFT * 0.15), FadeIn(cap), run_time=1.8)
        self._caption = cap
        self.ingestion_wait(2.5)

        focal_target = self._heatmap.cell_bbox(14)
        next_state_group = VGroup(
            self._heatmap.cell_bbox(10),
            self._heatmap.cell_bbox(13),
            self._heatmap.cell_bbox(14),
        )
        goal_target = self._heatmap.cell_bbox(15)

        # Step 0
        cap0 = self.place_caption("Line 1: loop over actions — the outer sum over π(a|s).")
        self.play(FadeOut(self._caption), FadeIn(cap0), *code.step(self, 0), run_time=1.4)
        self._caption = cap0
        cross_highlight_pair(self, code.lines[0], focal_target, primary_color=ACTION_COLOR, pulse_run_time=1.0)
        self.wait(6.0)

        # Step 1
        cap1 = self.place_caption("Line 2: loop over transitions — outcome cells for one (s, a).")
        self.play(FadeOut(self._caption), FadeIn(cap1), *code.step(self, 1), run_time=1.4)
        self._caption = cap1
        cross_highlight_pair(self, code.lines[1], next_state_group, primary_color=STATE_COLOR, pulse_run_time=1.0)
        self.wait(7.0)

        # Step 2
        cap2 = self.place_caption("Line 3: accumulate (reward + γ × V[next_state]).")
        self.play(FadeOut(self._caption), FadeIn(cap2), *code.step(self, 2), run_time=1.4)
        self._caption = cap2
        cross_highlight_pair(self, code.lines[2], goal_target, primary_color=REWARD_COLOR, pulse_run_time=1.0)
        self.wait(7.5)

        # Step 3
        cap3 = self.place_caption("Line 4: assign the new value to V[state] — the focal cell label updates.")
        self.play(FadeOut(self._caption), FadeIn(cap3), *code.step(self, 3), run_time=1.4)
        self._caption = cap3
        cross_highlight_pair(self, code.lines[3], focal_target, primary_color=VALUE_COLOR, pulse_run_time=1.0)
        self.wait(7.0)

        # Cleanup focus
        self.play(*code.reset(self), run_time=1.0)
        self.ingestion_wait(2.0)

    # ------------------------------------------------------------------
    # Phase 6 — Misconception via contrast pair
    # ------------------------------------------------------------------
    def _phase6_misconception(self) -> None:
        self.mark_phase("misconception")

        # Dismiss code, equation, k/Δ; keep heatmap (will move LEFT, smaller still)
        self.play(
            FadeOut(self._code.panel),
            FadeOut(self._v_iter),
            FadeOut(self._k_label),
            FadeOut(self._delta_label),
            FadeOut(self._caption),
            run_time=1.0,
        )
        self.smooth_move_to(self._heatmap, np.array([-3.2, -0.5, 0.0]), run_time=1.2)
        self.play(self._heatmap.animate.set_width(3.8), run_time=0.8)

        cap = self.place_caption(
            "Misconception: policy evaluation finds the *best* policy. It does not."
        )
        self.play(FadeIn(cap), run_time=1.0)
        self._caption = cap
        self.wait(4.0)

        # Build the LEFT-policy contrast heatmap
        hm_left = EnvironmentValueHeatmap(
            rows=4, cols=4,
            values=_V_LEFT_POLICY,
            width=3.8,
        )
        hm_left.move_to(np.array([3.2, -0.5, 0.0]))
        self._hm_left = hm_left

        title_a = Text("π = equiprobable", font_size=22, color=POLICY_COLOR)
        title_b = Text("π = always LEFT", font_size=22, color=POLICY_COLOR)
        title_a.next_to(self._heatmap, UP, buff=0.18)
        title_b.next_to(hm_left, UP, buff=0.18)

        self.play(
            LaggedStart(
                FadeIn(hm_left, shift=LEFT * 0.15),
                FadeIn(title_a),
                FadeIn(title_b),
                lag_ratio=0.35,
            ),
            run_time=2.4,
        )
        self.ingestion_wait(2.5)
        self.wait(4.0)

        cap2 = self.place_caption(
            "Same algorithm, two policies. Going LEFT never reaches the goal — v_π ≡ 0 everywhere."
        )
        self.play(FadeOut(self._caption), FadeIn(cap2), run_time=0.8)
        self._caption = cap2
        self.wait(7.0)

        cap3 = self.place_caption(
            "Finding the best policy needs *improvement* — next video — or value iteration."
        )
        self.play(FadeOut(self._caption), FadeIn(cap3), run_time=0.8)
        self._caption = cap3
        self.wait(7.0)

        # End of Phase 6: fade the LEFT-policy heatmap and its title
        self.play(FadeOut(hm_left), FadeOut(title_b), run_time=1.0)
        self._title_a = title_a

    # ------------------------------------------------------------------
    # Phase 7 — Boundaries: terminal cells + Δ-vs-k plot
    # ------------------------------------------------------------------
    def _phase7_boundaries(self) -> None:
        self.mark_phase("boundaries")

        cap = self.place_caption(
            "Two boundary conditions: terminal states stay at zero, and convergence is asymptotic."
        )
        self.play(FadeOut(self._caption), FadeIn(cap), run_time=0.8)
        self._caption = cap
        self.wait(3.5)

        # Indicate hole cells and goal
        hole_states = [5, 7, 11, 12]
        for s in hole_states:
            self.play(Indicate(self._heatmap.cell_bbox(s), color=PENALTY_COLOR, scale_factor=1.07), run_time=0.6)
        self.play(Indicate(self._heatmap.cell_bbox(15), color=REWARD_COLOR, scale_factor=1.10), run_time=0.8)
        self.wait(2.5)

        # Δ-vs-k plot
        axes = Axes(
            x_range=[0, 75, 15],
            y_range=[-9, 0, 2],
            x_length=4.2,
            y_length=2.6,
            tips=False,
            axis_config={"include_numbers": True, "font_size": 16, "color": GREY_A},
        )
        axes.move_to(np.array([3.2, -0.5, 0.0]))

        def log_delta(k_val):
            return float(np.log10(0.25 * (0.99 ** k_val) + 1e-12))

        curve = axes.plot(log_delta, x_range=[1, 71], color=VALUE_COLOR, stroke_width=3.0)
        log_theta = float(np.log10(1e-8))
        theta_line = DashedLine(
            axes.c2p(0, log_theta), axes.c2p(75, log_theta),
            color=REWARD_COLOR, stroke_width=1.8,
        )
        theta_label = MathTex(r"\theta = 10^{-8}", font_size=16, color=REWARD_COLOR)
        theta_label.next_to(theta_line, RIGHT, buff=0.05).shift(UP * 0.08)
        cross_dot = Dot(axes.c2p(71, log_theta), color=REWARD_COLOR, radius=0.07)
        cross_lbl = MathTex("k = 71", font_size=16, color=REWARD_COLOR)
        cross_lbl.next_to(cross_dot, UP, buff=0.08)

        x_lbl = Text("iteration k", font_size=16, color=GREY_A).next_to(axes, DOWN, buff=0.05)
        y_lbl = MathTex(r"\log_{10}\Delta", font_size=20, color=GREY_A).next_to(axes, LEFT, buff=0.05).rotate(np.pi / 2)

        self._boundary_group = VGroup(axes, x_lbl, y_lbl, curve, theta_line, theta_label, cross_dot, cross_lbl)

        self.play(FadeIn(axes), FadeIn(x_lbl), FadeIn(y_lbl), run_time=1.2)
        self.play(Create(curve), run_time=2.0)
        self.wait(2.0)
        self.play(Create(theta_line), Write(theta_label), run_time=1.4)
        self.play(FadeIn(cross_dot), Write(cross_lbl), run_time=1.0)

        cap2 = self.place_caption(
            "Δ shrinks exponentially but never quite reaches zero. We stop when Δ < θ."
        )
        self.play(FadeOut(self._caption), FadeIn(cap2), run_time=0.8)
        self._caption = cap2
        self.ingestion_wait(2.5)
        self.wait(5.0)

    # ------------------------------------------------------------------
    # Phase 8 — Closing
    # ------------------------------------------------------------------
    def _phase8_closing(self) -> None:
        self.mark_phase("closing")

        self.play(self._boundary_group.animate.set_opacity(OPACITY_SECONDARY), run_time=0.8)

        cap = self.place_caption(
            "Policy evaluation answers: how good is *this* policy? Now we know."
        )
        self.play(FadeOut(self._caption), FadeIn(cap), run_time=0.8)
        self._caption = cap
        self.wait(4.0)

        pill_text = Text("Next: Policy Improvement", font_size=28, color=POLICY_COLOR)
        pill_sub = Text("make π greedy w.r.t. v_π", font_size=20, color=GREY_A)
        pill_sub.next_to(pill_text, DOWN, buff=0.12)
        pill_group = VGroup(pill_text, pill_sub).move_to(np.array([0.5, 0.2, 0.0]))

        self.play(LaggedStart(FadeIn(pill_text, shift=UP * 0.15), FadeIn(pill_sub), lag_ratio=0.4), run_time=2.2)
        self.wait(4.0)

        cap2 = self.place_caption(
            "Improvement is what we do with that answer. See you in the next video."
        )
        self.play(FadeOut(self._caption), FadeIn(cap2), run_time=0.8)
        self._caption = cap2
        self.wait(6.0)
