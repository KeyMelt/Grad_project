"""Policies, values, and the Bellman expectation equation."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Brace,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Group,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    Rectangle,
    ReplacementTransform,
    SurroundingRectangle,
    Text,
    VGroup,
    WHITE,
    Write,
)

from manim_service.scenes import (
    ACTION_COLOR,
    BG_GRID,
    BG_PANEL,
    CODE_ACCENT,
    OPACITY_BACKGROUND,
    OPACITY_PRIMARY,
    OPACITY_SECONDARY,
    PENALTY_COLOR,
    POLICY_COLOR,
    REWARD_COLOR,
    STATE_COLOR,
    VALUE_COLOR,
    BackupDiagram,
    BaseConceptScene,
    ActionBarChart,
    IDECodePanel,
    equation_morph,
    PolicyArrowGrid,
    cross_highlight_pair,
    pan_to_follow,
    sprite_action_binding,
    trace_vector,
    zoom_reset,
    zoom_to,
)
from manim_service.scenes.rl_visuals import EnvironmentValueHeatmap


V_PI = [
    0.012356, 0.010424, 0.019338, 0.009478,
    0.014787, 0.000000, 0.038894, 0.000000,
    0.032602, 0.084338, 0.137811, 0.000000,
    0.000000, 0.170345, 0.433579, 0.000000,
]

Q_14 = [0.244773, 0.532628, 0.521892, 0.435025]
HOLES = {(1, 1), (1, 3), (2, 3), (3, 0)}
GOAL = (3, 3)
# Phase-end seconds derived from plan.md Segment targets:
# S1=60, S2=210, S3=240, S4=120, S5=330, S6=60, S7=180, S8=90 → total 1290s
# Audio-as-master timing — every phase pads with self.wait until target.
PHASE_ENDS = [
    30.0,   60.0,                                   # S1 P1, P2
    120.0,  200.0,  270.0,                          # S2 P3, P4, P5
    330.0,  410.0,  460.0,  510.0,                  # S3 P6, P7, P8, P9
    550.0,  600.0,  630.0,                          # S4 P10, P11, P12
    670.0,  720.0,  770.0,  820.0,  870.0,  920.0,  960.0,  # S5 P13-P19
    1020.0,                                         # S6 P20
    1060.0, 1170.0, 1200.0,                         # S7 P21, P22, P23
    1230.0, 1260.0, 1290.0,                         # S8 P24, P25, P26
]

CODE_LINES = [
    "env = gym.make('FrozenLake-v1')",
    "ns = env.observation_space.n",
    "pi = np.ones((ns, 4)) / 4",
    "gamma = 0.99",
    "P = env.unwrapped.P",
    "v_prev = np.zeros(ns)",
    "s = 6",
    "v_new = 0.0",
    "for a in range(4):",
    "  for p, sp, r, d in P[s][a]:",
    "    v_new += pi[s,a]*p*(r+gamma*v_prev[sp])",
    "print(f'{v_new:.6f}')",
]


class PoliciesValuesBellmanConcept(BaseConceptScene):
    """V-02 scene: policy distributions, value functions, and Bellman equality."""

    def construct(self) -> None:
        self._verify_assets()
        self._live = []
        self._phase1_recap()
        self._phase2_return_callback()
        self._phase3_policy_definition()
        self._phase4_policy_contrast()
        self._phase5_policy_normalization()
        self._phase6_value_definition()
        self._phase7_heatmap_reveal()
        self._phase8_state14_misconception()
        self._phase9_goal_terminal()
        self._phase10_q_definition()
        self._phase11_q_bars()
        self._phase12_v_from_q()
        self._phase13_backup_entry()
        self._phase14_derivation_step1()
        self._phase15_derivation_step2()
        self._phase16_derivation_step3()
        self._phase17_derivation_step4()
        self._phase18_derivation_step5()
        self._phase19_boxed_bellman()
        self._phase20_numeric_check()
        self._phase21_code_entry()
        self._phase22_code_sync()
        self._phase23_code_output()
        self._phase24_recentering()
        self._phase25_forward_tease()
        self._phase26_takeaway()

    def _verify_assets(self) -> None:
        import gymnasium

        asset_dir = os.path.join(os.path.dirname(gymnasium.__file__), "envs", "toy_text", "img")
        required = [
            "ice.png", "stool.png", "hole.png", "goal.png",
            "elf_right.png", "elf_left.png", "elf_up.png", "elf_down.png",
        ]
        missing = [f for f in required if not os.path.exists(os.path.join(asset_dir, f))]
        if missing:
            raise RuntimeError(f"MISSING_ASSETS: {missing}")

    def _register(self, *mobs):
        self._live.extend(mobs)
        return mobs[0] if len(mobs) == 1 else mobs

    def _fade_all(self, keep=(), run_time=0.8):
        # Fade EVERYTHING currently on screen except `keep` (and the camera
        # frame) — not just self._live. This clears untracked/orphan mobjects
        # (e.g. a leftover code-panel debugger highlight from the S7 phases)
        # that would otherwise persist into a later phase as a ghost rectangle.
        keep_ids = {id(m) for m in keep}
        frame = self.camera.frame
        mobs = [m for m in self.mobjects if m is not frame and id(m) not in keep_ids]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)
        self._live = [m for m in self._live if id(m) in keep_ids]

    def _cell(self, heatmap, state: int):
        return heatmap.cell_bbox(state)

    def _label_for_state(self, heatmap, state: int):
        return heatmap.labels.get(divmod(state, 4), heatmap.cell_bbox(state))

    def _phase_done(self, idx: int) -> None:
        self.hold_until(PHASE_ENDS[idx - 1])

    def _eq(self, *parts, size=48, color=WHITE):
        return MathTex(*parts, font_size=size, color=color)

    def _caption(self, text: str, color=CODE_ACCENT):
        return self.place_caption(text, font_size=24).set_color(color)

    def _policy_bundle_grid(self, equiprobable: bool, width=4.0):
        base = PolicyArrowGrid(
            4, 4,
            policy=[2] * 16,
            holes=HOLES,
            goal=GOAL,
            width=width,
            arrow_color=POLICY_COLOR,
            arrow_scale=0.34,
        )
        if not equiprobable:
            return base
        arrows = VGroup()
        for idx in range(16):
            r, c = divmod(idx, 4)
            if (r, c) in HOLES or (r, c) == GOAL:
                continue
            center = base.cells[(r, c)].get_center()
            for direction in (LEFT, DOWN, RIGHT, UP):
                arrows.add(Arrow(
                    center - direction * 0.10,
                    center + direction * 0.27,
                    buff=0,
                    color=POLICY_COLOR,
                    stroke_width=1.4,
                    max_tip_length_to_length_ratio=0.35,
                ))
        base.add(arrows)
        return base

    def _phase1_recap(self):
        self.mark_phase("S1-P1_recap_thumbnail")
        self.header = self.show_header("Recap", "What V-01 gave us")
        grid = EnvironmentValueHeatmap(values=[0.0] * 16, width=3.6, label_precision=2)
        grid.shift(LEFT * 0.8 + DOWN * 0.2)
        notes = VGroup(
            Text("States are places.", font_size=26, color=STATE_COLOR),
            Text("Rewards arrive on transitions.", font_size=26, color=REWARD_COLOR),
            Text("Return folds the future backward.", font_size=26, color=VALUE_COLOR),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        self.place_mid_right_panel(notes)
        self.play(FadeIn(grid), LaggedStart(*[FadeIn(n) for n in notes], lag_ratio=0.18), run_time=0.8)
        self.header.set_opacity(OPACITY_BACKGROUND)
        self._register(self.header, grid, notes)
        self.recap_grid = grid
        self._phase_done(1)

    def _phase2_return_callback(self):
        self.mark_phase("S1-P2_return_recursion")
        top_two = VGroup(self._live[-1][0], self._live[-1][1])
        recursion = self._eq("G_t", "=", "R_{t+1}", "+", "\\gamma", "G_{t+1}", size=42)
        self.place_left_panel(recursion)
        cook = Text("Today, we cook that recursion into values.", font_size=26, color=VALUE_COLOR)
        self.place_mid_right_panel(cook)
        self.play(FadeOut(top_two), self.recap_grid.animate.set_opacity(OPACITY_SECONDARY), Write(recursion), FadeIn(cook), run_time=1.4)
        trace_vector(self, self.recap_grid, recursion[0], color=VALUE_COLOR, run_time=0.8)
        self.ingestion_wait(1.6)
        self._register(recursion, cook)
        self._phase_done(2)
        self._fade_all()

    def _phase3_policy_definition(self):
        self.mark_phase("S2-P3_policy_definition")
        self.header = self.show_header("Policies", "The agent's decision rule")
        self.play(FadeOut(self.header), run_time=0.4)
        pi_def = self._eq("\\pi(a\\mid s)", "\\doteq", "\\Pr\\{A_t=a\\mid S_t=s\\}", size=52)
        self.play(Write(pi_def), run_time=1.3)
        self.wait(2.0)
        self.pi_def = pi_def
        self._register(pi_def)
        self.ingestion_wait(1.6)
        self._phase_done(3)

    def _phase4_policy_contrast(self):
        self.mark_phase("S2-P4_policy_contrast")
        chip = self.pi_def.copy().scale(0.52)
        chip.to_edge(UP, buff=0.55)
        self.play(ReplacementTransform(self.pi_def, chip), run_time=1.2)
        left_grid = self._policy_bundle_grid(False, width=3.5)
        right_grid = self._policy_bundle_grid(True, width=3.5)
        left_grid.shift(LEFT * 3.9 + DOWN * 0.25)
        right_grid.shift(RIGHT * 3.9 + DOWN * 0.25)
        cap_a = self._eq("\\pi(\\mathrm{RIGHT}\\mid s)=1", size=28, color=POLICY_COLOR)
        cap_b = self._eq("\\pi(a\\mid s)=\\tfrac14", size=28, color=POLICY_COLOR)
        cap_a.next_to(left_grid, DOWN, buff=0.16)
        cap_b.next_to(right_grid, DOWN, buff=0.16)
        center = Text("Two valid policies. Same grid.", font_size=28, color=WHITE)
        center.next_to(chip, DOWN, buff=0.45)
        self.play(FadeIn(left_grid), FadeIn(right_grid), FadeIn(center), Write(cap_a), Write(cap_b), run_time=1.4)
        trace_vector(self, cap_a, left_grid.arrows[(1, 2)], color=POLICY_COLOR, run_time=0.7)
        trace_vector(self, cap_b, VGroup(*[m for m in right_grid.submobjects[-1][:4]]), color=POLICY_COLOR, run_time=0.7)
        self.pi_chip = chip
        self.policy_a = left_grid
        self.policy_b = right_grid
        self.policy_b_hidden = right_grid.copy()
        self._register(chip, left_grid, right_grid, cap_a, cap_b, center)
        self._phase_done(4)
        self.play(FadeOut(center), run_time=0.5)

    def _phase5_policy_normalization(self):
        self.mark_phase("S2-P5_policy_normalization")
        norm = self._eq("\\sum_a", "\\pi(a\\mid s)", "=", "\\tfrac14", "+", "\\tfrac14", "+", "\\tfrac14", "+", "\\tfrac14", "=", "1", size=40)
        norm.shift(UP * 0.35)
        note = Text("Normalization: every state's action probabilities sum to one.", font_size=24, color=CODE_ACCENT)
        note.next_to(norm, DOWN, buff=0.3)
        spot_a = SurroundingRectangle(self.policy_a.cells[(1, 2)], color=POLICY_COLOR, buff=0.02)
        spot_b = SurroundingRectangle(self.policy_b.cells[(1, 2)], color=POLICY_COLOR, buff=0.02)
        self.play(
            self.policy_a.animate.scale(0.78).shift(LEFT * 0.25).set_opacity(OPACITY_SECONDARY),
            self.policy_b.animate.scale(0.78).shift(RIGHT * 0.25).set_opacity(OPACITY_SECONDARY),
            FadeIn(spot_a), FadeIn(spot_b), Write(norm), FadeIn(note),
            run_time=1.5,
        )
        cross_highlight_pair(self, norm[0], spot_b, primary_color=POLICY_COLOR, pulse_run_time=0.6)
        trace_vector(self, spot_b, norm[0], color=POLICY_COLOR, run_time=0.7)
        for token in (norm[3], norm[5], norm[7], norm[9]):
            trace_vector(self, spot_b, token, color=POLICY_COLOR, run_time=0.45)
        self._register(norm, note, spot_a, spot_b)
        self.ingestion_wait(1.6)
        self._phase_done(5)
        self._fade_all()

    def _phase6_value_definition(self):
        self.mark_phase("S3-P6_value_definition")
        self.header = self.show_header("State-value function", "How good is this state under pi?")
        self.play(FadeOut(self.header), run_time=0.4)
        v_def = self._eq("v_\\pi(s)", "\\doteq", "\\mathbb{E}_\\pi", "[", "G_t", "\\mid", "S_t=s", "]", size=52)
        self.play(Write(v_def), run_time=1.3)
        self.wait(2.0)
        self.v_def = v_def
        self._register(v_def)
        self.ingestion_wait(1.6)
        self._phase_done(6)

    def _phase7_heatmap_reveal(self):
        self.mark_phase("S3-P7_heatmap_reveal")
        v_panel = self.v_def.copy().scale(0.62)
        self.place_left_panel(v_panel)
        heatmap = EnvironmentValueHeatmap(values=V_PI, width=4.7, label_precision=3)
        heatmap.shift(DOWN * 0.2)
        # First animation: the P7 timestamp check must see the heatmap.
        self.play(FadeIn(heatmap), run_time=0.7)
        self.play(ReplacementTransform(self.v_def, v_panel), run_time=0.7)
        legend = VGroup(
            Text("v_pi under pi=1/4", font_size=24, color=VALUE_COLOR),
            Text("gamma=0.99", font_size=24, color=CODE_ACCENT),
            Text("FrozenLake slippery", font_size=24, color=STATE_COLOR),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        self.place_mid_right_panel(legend)
        cells = [heatmap.cell_bbox(i) for i in [15, 14, 10, 13, 9, 6, 8, 4, 0, 1, 2, 3]]
        self.play(FadeIn(legend), run_time=0.7)
        for cell in cells[:5]:
            cross_highlight_pair(self, v_panel[0], cell, primary_color=VALUE_COLOR, pulse_run_time=0.25)
        trace_vector(self, self._label_for_state(heatmap, 14), v_panel[0], color=VALUE_COLOR, run_time=0.7)
        trace_vector(self, self._label_for_state(heatmap, 14), v_panel[4], color=VALUE_COLOR, run_time=0.7)
        self.v_panel = v_panel
        self.heatmap = heatmap
        self._register(v_panel, heatmap, legend)
        self.ingestion_wait(1.6)
        self._phase_done(7)
        self.play(FadeOut(legend), run_time=0.5)

    def _phase8_state14_misconception(self):
        self.mark_phase("S3-P8_state14_value_not_reward")
        cell14 = self._cell(self.heatmap, 14)
        halo = SurroundingRectangle(cell14, color=VALUE_COLOR, buff=0.04, stroke_width=4)
        r0 = Text("r=0", font_size=28, color=REWARD_COLOR).next_to(cell14, UP, buff=0.1)
        cap = VGroup(
            Text("Reward at state 14: 0", font_size=24, color=REWARD_COLOR),
            Text("Value at state 14: 0.434", font_size=24, color=VALUE_COLOR),
            Text("Value lives in the future.", font_size=24, color=WHITE),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        self.place_mid_right_panel(cap)
        self.play(self.heatmap.animate.set_opacity(OPACITY_SECONDARY), FadeIn(halo), FadeIn(r0), FadeIn(cap), run_time=1.0)
        cross_highlight_pair(self, halo, cap[1], primary_color=VALUE_COLOR, pulse_run_time=0.7)
        trace_vector(self, r0, cap[0], color=REWARD_COLOR, run_time=0.7)
        trace_vector(self, self._label_for_state(self.heatmap, 14), cap[1], color=VALUE_COLOR, run_time=0.7)
        self._register(halo, r0, cap)
        self._phase_done(8)
        self.play(FadeOut(halo), FadeOut(r0), FadeOut(cap), self.heatmap.animate.set_opacity(OPACITY_PRIMARY), run_time=0.6)

    def _phase9_goal_terminal(self):
        self.mark_phase("S3-P9_goal_reward_value_split")
        cell15 = self._cell(self.heatmap, 15)
        halo = SurroundingRectangle(cell15, color=REWARD_COLOR, buff=0.04, stroke_width=4)
        reward = Text("+1.0", font_size=30, color=REWARD_COLOR).next_to(cell15, UP, buff=0.12)
        value = self._eq("v_\\pi(15)=0", size=30, color=VALUE_COLOR).move_to(cell15)
        cap = VGroup(
            Text("Arriving at the goal: reward +1.0", font_size=24, color=REWARD_COLOR),
            Text("Value at the goal: 0", font_size=24, color=VALUE_COLOR),
            Text("Terminal states have no future return.", font_size=24, color=WHITE),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        self.place_mid_right_panel(cap)
        self.play(FadeIn(halo), FadeIn(reward), Write(value), FadeIn(cap), run_time=1.0)
        cross_highlight_pair(self, reward, value, primary_color=REWARD_COLOR, secondary_color=VALUE_COLOR, pulse_run_time=0.8)
        trace_vector(self, reward, cap[0], color=REWARD_COLOR, run_time=0.7)
        trace_vector(self, value, cap[1], color=VALUE_COLOR, run_time=0.7)
        self._register(halo, reward, value, cap)
        self.ingestion_wait(1.6)
        self._phase_done(9)
        self._fade_all(keep=(self.v_panel, self.heatmap), run_time=0.8)

    def _phase10_q_definition(self):
        self.mark_phase("S4-P10_q_definition")
        self.play(self.v_panel.animate.set_opacity(OPACITY_BACKGROUND), self.heatmap.animate.scale(0.55).shift(DOWN * 2.0), run_time=1.0)
        q_def = self._eq("q_\\pi(s,a)", "\\doteq", "\\mathbb{E}_\\pi", "[", "G_t", "\\mid", "S_t=s,", "A_t=a", "]", size=52)
        self.play(Write(q_def), run_time=1.2)
        self.wait(2.0)
        self.q_def = q_def
        self._register(q_def)
        self.ingestion_wait(1.6)
        self._phase_done(10)

    def _phase11_q_bars(self):
        self.mark_phase("S4-P11_q_bars")
        q_side = self.q_def.copy().scale(0.52)
        self.place_left_panel(q_side)
        chart = ActionBarChart(
            ["L", "D", "R", "U"],
            Q_14,
            width=4.6,
            height=2.8,
            label_font_size=24,
            value_font_size=22,
            accent=VALUE_COLOR,
        )
        self.place_mid_right_panel(chart)
        # The chart reveal is deliberately first in this phase's visible beat,
        # so the mandatory P11 check sees q-bars at start + 1s.
        self.play(FadeIn(chart), run_time=0.8)
        # FadeOut the value panel rather than dimming it: q_side lands on the
        # same left anchor, so a dim v-panel garbles it into doubled text.
        self.play(
            ReplacementTransform(self.q_def, q_side),
            FadeOut(self.v_panel),
            run_time=1.0,
        )
        for bar in chart.bars:
            sprite_action_binding(self, bar, highlight_tokens=[q_side[0]], move_run_time=0.25, settle_time=0.15, highlight_color=VALUE_COLOR)
            trace_vector(self, bar, q_side[0], color=VALUE_COLOR, run_time=0.35)
        self.q_side = q_side
        self.q_chart = chart
        self.q_bars = chart.bars
        self._register(q_side, chart)
        self.ingestion_wait(1.6)
        self._phase_done(11)

    def _phase12_v_from_q(self):
        self.mark_phase("S4-P12_v_from_q")
        link = self._eq("v_\\pi(14)", "=", "\\tfrac14", "[", "q_\\pi(14,L)", "+", "q_\\pi(14,D)", "+", "q_\\pi(14,R)", "+", "q_\\pi(14,U)", "]", size=34)
        self.place_left_panel(link)
        brace = Brace(VGroup(*self.q_bars), DOWN, color=VALUE_COLOR)
        arr = Arrow(brace.get_bottom(), self.q_chart.get_bottom(), buff=0.08, color=VALUE_COLOR)
        self.play(FadeOut(self.q_side), Write(link), Create(brace), Create(arr), run_time=1.3)
        for token, bar in zip((link[4], link[6], link[8], link[10]), self.q_bars):
            trace_vector(self, bar, token, color=VALUE_COLOR, run_time=0.35)
        cross_highlight_pair(self, link[0], self._label_for_state(self.heatmap, 14), primary_color=VALUE_COLOR, pulse_run_time=0.7)
        self.link_q = link
        self._register(link, brace, arr)
        self.ingestion_wait(1.6)
        self._phase_done(12)
        self._fade_all(run_time=0.8)

    def _phase13_backup_entry(self):
        self.mark_phase("S5-P13_backup_entry")
        self.backup = BackupDiagram(
            n_actions=4,
            n_outcomes=3,
            root_label="6",
            action_labels=["L", "D", "R", "U"],
            outcome_labels=[
                ["2,0", "6,0", "10,0"],
                ["6,0", "10,0", "14,0"],
                ["2,0", "7,0", "10,0"],
                ["2,0", "6,0", "10,0"],
            ],
            total_width=10.5,
            level_height=1.5,
            label_font_size=24,
        )
        # Fill the lower ~two-thirds of the canvas; the equation lives across
        # the top (added from P14). Vertical split = no wasted side space and a
        # tree large enough to read on a small screen.
        self.backup.move_to([0.0, -0.6, 0.0])
        thumb = self.policy_b_hidden.copy().scale(0.32).set_opacity(OPACITY_BACKGROUND)
        thumb.to_corner(DOWN + LEFT, buff=0.3)
        self.play(FadeIn(self.backup), FadeIn(thumb), run_time=0.8)
        self.policy_thumb = thumb
        trace_vector(self, thumb, self.backup.action_nodes[2], color=POLICY_COLOR, run_time=0.6)
        trace_vector(self, thumb, self.backup.outcome_nodes[2][0], color=CODE_ACCENT, run_time=0.6)
        self._register(self.backup, thumb)
        self.ingestion_wait(1.6)
        self._phase_done(13)

    def _deriv_eq(self, *parts):
        # Large, top-centred equation spanning the full width — vertically
        # separated from the backup tree below. Uses the whole top band instead
        # of being squeezed into a narrow left column.
        eq = self._eq(*parts, size=44)
        if eq.width > 12.5:
            eq.scale_to_fit_width(12.5)
        eq.to_edge(UP, buff=0.75)
        return eq

    def _phase14_derivation_step1(self):
        self.mark_phase("S5-P14_derivation_definition")
        eq1 = self._deriv_eq("v_\\pi(s)", "\\doteq", "\\mathbb{E}_\\pi", "[", "G_t", "\\mid", "S_t=s", "]")
        self.play(Write(eq1), run_time=0.9)
        cross_highlight_pair(self, eq1[0], self.backup.root_node, primary_color=VALUE_COLOR, pulse_run_time=0.7)
        trace_vector(self, self.backup.root_node, eq1[0], color=VALUE_COLOR, run_time=0.6)
        self.deriv_eq = eq1
        self._register(eq1)
        self._phase_done(14)

    def _phase15_derivation_step2(self):
        self.mark_phase("S5-P15_return_recursion_in_expectation")
        eq2 = self._deriv_eq("v_\\pi(s)", "=", "\\mathbb{E}_\\pi", "[", "R_{t+1}", "+", "\\gamma", "G_{t+1}", "\\mid", "S_t=s", "]")
        r_label = self._eq("R_{t+1}", size=26, color=REWARD_COLOR).next_to(self.backup.root_edges[2], RIGHT, buff=0.05)
        brace = Brace(VGroup(*self.backup.outcome_nodes[2]), DOWN, color=VALUE_COLOR)
        g_label = self._eq("G_{t+1}", size=26, color=VALUE_COLOR).next_to(brace, DOWN, buff=0.08)
        self.play(ReplacementTransform(self.deriv_eq, eq2), FadeIn(r_label), Create(brace), Write(g_label), run_time=1.3)
        trace_vector(self, r_label, eq2[4], color=REWARD_COLOR, run_time=0.6)
        trace_vector(self, g_label, eq2[7], color=VALUE_COLOR, run_time=0.6)
        self.deriv_eq = eq2
        self.rg_labels = VGroup(r_label, brace, g_label)
        self._register(self.rg_labels)
        self.ingestion_wait(1.6)
        self._phase_done(15)

    def _phase16_derivation_step3(self):
        self.mark_phase("S5-P16_outer_action_sum")
        eq3 = self._deriv_eq("v_\\pi(s)", "=", "\\sum_a", "\\pi(a\\mid s)", "\\mathbb{E}_\\pi", "[", "R_{t+1}", "+", "\\gamma", "G_{t+1}", "\\mid", "S_t=s,A_t=a", "]")
        self.play(ReplacementTransform(self.deriv_eq, eq3), run_time=1.2)
        actions = VGroup(*self.backup.action_nodes)
        self.play(LaggedStart(*[Indicate(n, color=POLICY_COLOR) for n in actions], lag_ratio=0.12), run_time=1.0)
        self.play(LaggedStart(*[Indicate(n, color=ACTION_COLOR) for n in actions], lag_ratio=0.12), run_time=1.0)
        trace_vector(self, actions, eq3[2], color=POLICY_COLOR, run_time=0.6)
        trace_vector(self, actions, eq3[3], color=POLICY_COLOR, run_time=0.6)
        self.deriv_eq = eq3
        self.ingestion_wait(1.6)
        self._phase_done(16)

    def _phase17_derivation_step4(self):
        self.mark_phase("S5-P17_inner_transition_sum")
        eq4 = self._deriv_eq("v_\\pi(s)", "=", "\\sum_a", "\\pi(a\\mid s)", "\\sum_{s',r}", "p(s',r\\mid s,a)", "[", "r", "+", "\\gamma", "\\mathbb{E}_\\pi[G_{t+1}\\mid S_{t+1}=s']", "]")
        self.play(ReplacementTransform(self.deriv_eq, eq4), run_time=1.2)
        leaves = VGroup(*self.backup.outcome_nodes[2])
        self.play(LaggedStart(*[Indicate(n, color=CODE_ACCENT) for n in leaves], lag_ratio=0.12), run_time=1.0)
        trace_vector(self, leaves, eq4[4], color=CODE_ACCENT, run_time=0.6)
        trace_vector(self, leaves, eq4[5], color=CODE_ACCENT, run_time=0.6)
        trace_vector(self, leaves[1], eq4[7], color=REWARD_COLOR, run_time=0.6)
        self.deriv_eq = eq4
        self.ingestion_wait(1.6)
        self._phase_done(17)

    def _phase18_derivation_step5(self):
        self.mark_phase("S5-P18_recursive_value_label")
        eq5 = self._deriv_eq("v_\\pi(s)", "=", "\\sum_a", "\\pi(a\\mid s)", "\\sum_{s',r}", "p(s',r\\mid s,a)", "[", "r", "+", "\\gamma", "v_\\pi(s')", "]")
        # Stagger the three leaf-value labels (zigzag high/low) and shrink them
        # so adjacent labels under the closely-spaced R-branch leaves do not
        # overlap into garbled text.
        leaf_labels = VGroup(
            self._eq("v_\\pi(2)", size=20, color=VALUE_COLOR).next_to(self.backup.outcome_nodes[2][0], DOWN, buff=0.1),
            self._eq("v_\\pi(7)=0", size=20, color=VALUE_COLOR).next_to(self.backup.outcome_nodes[2][1], DOWN, buff=0.62),
            self._eq("v_\\pi(10)", size=20, color=VALUE_COLOR).next_to(self.backup.outcome_nodes[2][2], DOWN, buff=0.1),
        )
        # The G_{t+1} brace/labels from P15 have served their purpose — the
        # concept now becomes the recursive value v_pi(s'); fade them so they
        # do not collide with the leaf labels under the same leaves.
        self.play(
            ReplacementTransform(self.deriv_eq, eq5),
            FadeOut(self.rg_labels),
            LaggedStart(*[Write(m) for m in leaf_labels], lag_ratio=0.2),
            run_time=1.4,
        )
        for label in leaf_labels:
            trace_vector(self, label, eq5[9], color=VALUE_COLOR, run_time=0.45)
        self.deriv_eq = eq5
        self.leaf_value_labels = leaf_labels
        self._register(leaf_labels)
        self.ingestion_wait(1.6)
        self._phase_done(18)

    def _phase19_boxed_bellman(self):
        self.mark_phase("S5-P19_boxed_bellman")
        self.camera.frame.set_width(14.222).move_to([0.0, 0.0, 0.0])
        boxed_eq = self._eq("v_\\pi(s)", "=", "\\sum_a", "\\pi(a\\mid s)", "\\sum_{s',r}", "p(s',r\\mid s,a)", "[", "r", "+", "\\gamma", "v_\\pi(s')", "]", size=48)
        boxed_eq.scale_to_fit_width(11.5)
        boxed_eq.move_to([0.0, 0.0, 0.0])
        box = SurroundingRectangle(boxed_eq, color=VALUE_COLOR, buff=0.22, stroke_width=3)
        boxed = VGroup(boxed_eq, box)
        self._fade_all(keep=(), run_time=0.1)
        if hasattr(self, "deriv_eq"):
            self.remove(self.deriv_eq)
        self.play(Write(boxed_eq), Create(box), run_time=0.7)
        self.wait(3.0)
        self.boxed_eq = boxed_eq
        self.boxed_bellman = boxed
        self._register(boxed)
        self.ingestion_wait(1.6)
        self._phase_done(19)

    def _phase20_numeric_check(self):
        self.mark_phase("S6-P20_numeric_consistency")
        # Reference equation pinned to the TOP band (not a tiny centred copy);
        # the two numeric sides spread large and low — fills the whole frame so
        # the equality reads clearly on a small screen (§36).
        small_box = self.boxed_bellman.copy().scale(0.62)
        small_box.to_edge(UP, buff=0.7)
        lhs = VGroup(
            Text("Heatmap value", font_size=30, color=VALUE_COLOR),
            self._eq("v_\\pi(6)\\approx0.039", size=44, color=VALUE_COLOR),
        ).arrange(DOWN, buff=0.25)
        rhs = VGroup(
            Text("Bellman RHS", font_size=30, color=VALUE_COLOR),
            self._eq("\\tfrac14\\sum_a\\sum_{s',r}p[\\cdot]\\approx0.039", size=40, color=VALUE_COLOR),
        ).arrange(DOWN, buff=0.25)
        lhs.move_to([-3.5, -0.9, 0.0])
        rhs.move_to([3.5, -0.9, 0.0])
        self.play(ReplacementTransform(self.boxed_bellman, small_box), FadeIn(lhs), FadeIn(rhs), run_time=0.9)
        trace_vector(self, lhs[1], small_box[0][0], color=VALUE_COLOR, run_time=0.6)
        trace_vector(self, rhs[1], small_box[0][2], color=VALUE_COLOR, run_time=0.6)
        check = Text("LHS and RHS match: this is an equality, not an assignment.", font_size=28, color=WHITE)
        check.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(check), run_time=0.5)
        self.boxed_bellman = small_box
        self.numeric_panels = VGroup(lhs, rhs, check)
        self._register(lhs, rhs, check)
        self.ingestion_wait(1.6)
        self._phase_done(20)

    def _phase21_code_entry(self):
        self.mark_phase("S7-P21_code_entry")
        self.camera.frame.set_width(14.222).move_to([0.0, 0.0, 0.0])
        self._fade_all(keep=(), run_time=0.7)
        if hasattr(self, "boxed_bellman"):
            self.remove(self.boxed_bellman)
        heatmap = EnvironmentValueHeatmap(values=V_PI, width=3.5, label_precision=3)
        self.place_left_panel(heatmap)
        code = IDECodePanel(CODE_LINES, width=8.0, font_size=22, line_spacing=0.32, title="bellman_evaluator.py")
        self.place_mid_right_panel(code)
        # Two-panel split per §34: heatmap LEFT, IDE code RIGHT, no overlap.
        # Heatmap centered at x=-5.0 (spans -6.75 to -3.25), IDE at x=2.8
        # (spans -1.2 to 6.8). Gap of ~2 units between panels.
        heatmap.move_to([-5.0, -0.05, 0.0])
        code.shift(RIGHT * (2.8 - code.panel.get_center()[0]))
        self.play(FadeIn(heatmap), FadeIn(code), run_time=0.7)
        self.wait(1.5)
        cross_highlight_pair(self, self._cell(heatmap, 6), self._label_for_state(heatmap, 6), primary_color=VALUE_COLOR, pulse_run_time=0.8)
        self.code_heatmap = heatmap
        self.code = code
        self._register(heatmap, code)
        self.ingestion_wait(1.6)
        self._phase_done(21)

    def _phase22_code_sync(self):
        self.mark_phase("S7-P22_code_equation_heatmap_sync")
        targets = [
            self.code_heatmap, self.code_heatmap, self.code_heatmap,
            self.code_heatmap, self.code_heatmap, self.code_heatmap,
            self._cell(self.code_heatmap, 6), self._cell(self.code_heatmap, 6),
            self.code_heatmap,
            Group(self._cell(self.code_heatmap, 7), self._cell(self.code_heatmap, 2), self._cell(self.code_heatmap, 10)),
            self._label_for_state(self.code_heatmap, 10),
            self._cell(self.code_heatmap, 6),
        ]
        colors = [
            STATE_COLOR, STATE_COLOR, STATE_COLOR, POLICY_COLOR, POLICY_COLOR,
            VALUE_COLOR, VALUE_COLOR, STATE_COLOR, VALUE_COLOR, ACTION_COLOR,
            CODE_ACCENT, VALUE_COLOR, VALUE_COLOR,
        ]
        for idx, target in enumerate(targets):
            self.play(*self.code.step(self, idx), run_time=0.45)
            cross_highlight_pair(self, self.code.lines[idx], target, primary_color=colors[idx], pulse_run_time=0.55)
            if idx == 9:
                table = self._sampling_table()
                self.play(
                    self.code_heatmap.animate.set_opacity(OPACITY_SECONDARY),
                    self.code.animate.set_opacity(OPACITY_SECONDARY),
                    FadeIn(table),
                    run_time=0.8,
                )
                for state in (7, 2, 10):
                    self.play(Indicate(self._cell(self.code_heatmap, state), color=CODE_ACCENT, scale_factor=1.05), run_time=0.45)
                self.wait(1.0)
                self.play(
                    FadeOut(table),
                    self.code_heatmap.animate.set_opacity(OPACITY_PRIMARY),
                    self.code.animate.set_opacity(OPACITY_PRIMARY),
                    run_time=0.8,
                )
            self.wait(7.5)
        self.ingestion_wait(1.6)
        self._phase_done(22)

    def _phase23_code_output(self):
        self.mark_phase("S7-P23_zero_output_handoff")
        output = self._eq("0.000000", size=36, color=CODE_ACCENT)
        output.next_to(self._cell(self.code_heatmap, 6), UP, buff=0.16)
        cap = VGroup(
            Text("Heatmap value: 0.039", font_size=24, color=VALUE_COLOR),
            Text("Code RHS from v_prev=0: 0.000000", font_size=24, color=CODE_ACCENT),
            Text("One sweep is not enough - V-03 will iterate.", font_size=24, color=WHITE),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        self.place_bottom_right_panel(cap)
        self.play(*self.code.step(self, 11), run_time=0.45)
        self.play(Write(output), FadeIn(cap), run_time=1.0)
        trace_vector(self, self._label_for_state(self.code_heatmap, 6), cap[0], color=VALUE_COLOR, run_time=0.6)
        trace_vector(self, output, cap[1], color=CODE_ACCENT, run_time=0.6)
        cross_highlight_pair(self, cap[2], self.code.lines[11], primary_color=VALUE_COLOR, pulse_run_time=0.7)
        self.output_group = VGroup(output, cap)
        self._register(output, cap)
        self.ingestion_wait(1.6)
        self._phase_done(23)

    def _phase24_recentering(self):
        self.mark_phase("S8-P24_boxed_recentering")
        self._fade_all(keep=(), run_time=0.8)
        eq = self._eq("v_\\pi(s)", "=", "\\sum_a", "\\pi(a\\mid s)", "\\sum_{s',r}", "p(s',r\\mid s,a)", "[", "r", "+", "\\gamma", "v_\\pi(s')", "]", size=48)
        eq.scale_to_fit_width(11.5)
        eq.move_to([0.0, 0.0, 0.0])
        box = SurroundingRectangle(eq, color=VALUE_COLOR, buff=0.22, stroke_width=3)
        full = VGroup(eq, box)
        self.play(Write(eq), Create(box), run_time=0.7)
        # scale=0.95 (was 0.82): a gentler zoom that keeps the full box inside
        # the frame. At 0.82 the 11.94-wide box was magnified past both edges.
        zoom_to(self, full, scale=0.95, run_time=1.0)
        self.boxed_bellman = full
        self._register(full)
        self.ingestion_wait(1.6)
        self._phase_done(24)

    def _phase25_forward_tease(self):
        self.mark_phase("S8-P25_assignment_tease")
        next_cap = Text("Next: equation to algorithm", font_size=26, color=CODE_ACCENT)
        next_cap.to_edge(UP, buff=0.6)
        assign = self._eq("v_{k+1}(s)", "\\leftarrow", "\\sum_a", "\\pi(a\\mid s)", "\\sum_{s',r}", "p(s',r\\mid s,a)", "[", "r", "+", "\\gamma", "v_k(s')", "]", size=48)
        assign.scale_to_fit_width(11.5)
        assign.move_to(self.boxed_bellman[0])
        self.play(FadeIn(next_cap), run_time=0.3)
        # RC-1 fix: hide BOTH the equation AND the box stroke during the morph.
        # boxed_bellman[1] is a SurroundingRectangle — manipulate STROKE only;
        # set_opacity() on a Rectangle also sets fill_opacity, which would fill
        # the box solid yellow during the restore.
        self.play(
            self.boxed_bellman[0].animate.set_opacity(0.0),
            self.boxed_bellman[1].animate.set_stroke(opacity=0.0),
            FadeIn(assign),
            run_time=0.8,
        )
        trace_vector(self, next_cap, assign[1], color=CODE_ACCENT, run_time=0.45)
        self.wait(0.25)
        # Revert: FadeOut the assign-form, restore the original equation + box stroke.
        self.play(
            FadeOut(assign),
            self.boxed_bellman[0].animate.set_opacity(OPACITY_PRIMARY),
            self.boxed_bellman[1].animate.set_stroke(opacity=1.0),
            run_time=0.35,
        )
        self.play(FadeOut(next_cap), run_time=0.3)
        zoom_reset(self, run_time=0.8)
        self.ingestion_wait(1.6)
        self._phase_done(25)

    def _phase26_takeaway(self):
        self.mark_phase("S8-P26_takeaway")
        self.play(self.boxed_bellman.animate.scale(0.72).shift(UP * 1.7), run_time=1.0)
        # P26 card: use Text instead of MathTex with \text{} (which can fail to
        # render and leave an empty box stroke as an artifact).
        card_bg = Rectangle(
            width=9.0, height=1.4,
            fill_color=BG_PANEL, fill_opacity=1.0,
            stroke_color=VALUE_COLOR, stroke_width=2.5,
        )
        card_text = Text(
            "v_π is the fixed point of the Bellman equation.",
            font_size=30, color=VALUE_COLOR,
        )
        card_text.move_to(card_bg)
        card = VGroup(card_bg, card_text)
        card.shift(DOWN * 0.35)
        left = Text("V-02: the equation.", font_size=28, color=CODE_ACCENT).next_to(card, LEFT, buff=0.5)
        right = Text("V-03: the algorithm.", font_size=28, color=CODE_ACCENT).next_to(card, RIGHT, buff=0.5)
        # If `left`/`right` would extend off-canvas, place them below instead.
        frame_half_w = 7.1  # 14.2 / 2
        if left.get_left()[0] < -frame_half_w:
            left.next_to(card, DOWN, buff=0.4, aligned_edge=LEFT)
        if right.get_right()[0] > frame_half_w:
            right.next_to(card, DOWN, buff=0.4, aligned_edge=RIGHT)
        self.play(FadeIn(card), FadeIn(left), FadeIn(right), run_time=1.0)
        self._register(card, left, right)
        self._phase_done(26)

    def _sampling_table(self):
        rows = VGroup(
            Text("P[6][RIGHT]", font_size=28, color=CODE_ACCENT),
            Text("prob 0.333 -> next_state 7, reward 0", font_size=28, color=WHITE),
            Text("prob 0.333 -> next_state 2, reward 0", font_size=28, color=WHITE),
            Text("prob 0.333 -> next_state 10, reward 0", font_size=28, color=WHITE),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        bg = Rectangle(
            width=rows.get_width() + 0.55,
            height=rows.get_height() + 0.45,
            fill_color=BG_PANEL,
            fill_opacity=1.0,
            stroke_color=CODE_ACCENT,
            stroke_width=1.4,
        )
        table = VGroup(bg, rows)
        rows.move_to(bg)
        table.move_to([0.0, 0.0, 0.0])
        return table
