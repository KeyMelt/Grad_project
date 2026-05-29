"""MDP foundations concept video.

Full-pipeline stage artifact for lesson_id ``mdp_foundations``.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    MathTex,
    Rectangle,
    ReplacementTransform,
    RoundedRectangle,
    Text,
    VGroup,
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
    ActionBarChart,
    BackupDiagram,
    BaseConceptScene,
    CodeStepper,
    PolicyArrowGrid,
    ValueHeatmap,
    cross_highlight_pair,
    equation_morph,
    note_stack,
    panel,
    pill,
    trace_vector,
    zoom_reset,
    zoom_to,
)


HOLES = {5, 7, 11, 12}
TERMINALS = {5, 7, 11, 12, 15}
GOAL = 15
SUCCESSORS = [(1 / 3, 7, 0.0, True), (1 / 3, 2, 0.0, False), (1 / 3, 10, 0.0, False)]


class MdpFoundationsScene(BaseConceptScene):
    """Geometry-first MDP foundations scene."""

    def construct(self) -> None:
        self._caption = None
        self._phase_a_framework()
        self._phase_b_returns()
        self._phase_c_transition_probability()
        self._phase_d_policies()
        self._phase_e_values()
        self._phase_recap()
        self._phase_f_bellman()
        self._phase_closing()

    def _make_grid(self, width: float = 4.4) -> VGroup:
        cell = width / 4
        group = VGroup()
        self._grid_cells: dict[int, Rectangle] = {}
        self._grid_labels: dict[int, Text] = {}
        for state in range(16):
            row, col = divmod(state, 4)
            fill = BG_GRID
            opacity = 0.24
            if state in HOLES:
                fill = PENALTY_COLOR
                opacity = 0.55
            elif state == GOAL:
                fill = REWARD_COLOR
                opacity = 0.55
            rect = Rectangle(
                width=cell - 0.04,
                height=cell - 0.04,
                fill_color=fill,
                fill_opacity=opacity,
                stroke_color=STATE_COLOR,
                stroke_width=1.0,
            )
            rect.move_to((col - 1.5) * cell * RIGHT + (1.5 - row) * cell * UP)
            label = Text(str(state), font_size=18, color=WHITE).move_to(rect)
            self._grid_cells[state] = rect
            self._grid_labels[state] = label
            group.add(rect, label)
        frame = RoundedRectangle(
            width=width + 0.2,
            height=width + 0.2,
            corner_radius=0.14,
            fill_color=BG_PANEL,
            fill_opacity=0.35,
            stroke_color=STATE_COLOR,
            stroke_width=1.4,
            stroke_opacity=0.7,
        )
        frame.move_to(group)
        group.add_to_back(frame)
        return group

    def _state_center(self, state: int):
        return self._grid_cells[state].get_center()

    def _replace_caption(self, text: str) -> None:
        new_caption = self.place_caption(text, font_size=18)
        if self._caption is None:
            self.play(FadeIn(new_caption, shift=UP * 0.08), run_time=0.6)
        else:
            self.play(FadeOut(self._caption), FadeIn(new_caption, shift=UP * 0.08), run_time=0.6)
        self._caption = new_caption

    def _phase_a_framework(self) -> None:
        self.mark_phase("mdp_framework")
        self.header = self.show_header("MDP Foundations", "From states to the Bellman equation")
        self.grid = self._make_grid()
        self.grid.move_to(DOWN * 0.15)
        self.play(FadeIn(self.grid, shift=DOWN * 0.12), run_time=1.0)

        action_legend = VGroup(
            Text("Actions", font_size=22, color=ACTION_COLOR),
            Text("0 LEFT", font_size=18, color=WHITE),
            Text("1 DOWN", font_size=18, color=WHITE),
            Text("2 RIGHT", font_size=18, color=WHITE),
            Text("3 UP", font_size=18, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        self.action_legend = panel("A(s)", action_legend, ACTION_COLOR, width=2.6).to_edge(RIGHT, buff=0.45)

        markov = MathTex(
            r"\Pr",
            r"\{S_{t+1},R_{t+1}\mid S_t,A_t\}",
            r"\text{ only}",
            font_size=25,
        )
        markov[1].set_color(STATE_COLOR)
        self.markov_note = panel("Markov property", markov, STATE_COLOR, width=4.2).to_edge(LEFT, buff=0.45)
        self.play(
            LaggedStart(FadeIn(self.markov_note), FadeIn(self.action_legend), lag_ratio=0.2),
            run_time=1.0,
        )
        self._replace_caption("The present state and action are enough to model the next state and reward.")
        self.wait(2.0)
        self.wait(244)  # narration-pacing hold — phase (a) target ~250 s
        self.play(FadeOut(self.markov_note), FadeOut(self.action_legend), run_time=0.7)

    def _phase_b_returns(self) -> None:
        self.mark_phase("rewards_returns")
        path_states = [6, 10, 14, 15]
        dots = VGroup(*[Dot(self._state_center(s), radius=0.08, color=REWARD_COLOR) for s in path_states])
        stream = VGroup(
            Text("rewards", font_size=20, color=REWARD_COLOR),
            MathTex(r"[0,\;0,\;1]", font_size=32, color=WHITE),
            MathTex(r"\gamma=0.99", font_size=30, color=VALUE_COLOR),
            MathTex(r"G=0+0.99\cdot0+0.99^2\cdot1=0.9801", font_size=26, color=WHITE),
        ).arrange(DOWN, buff=0.18)
        self.reward_panel = panel("Return example", stream, REWARD_COLOR, width=4.8).to_edge(RIGHT, buff=0.45)
        self.play(FadeIn(dots), FadeIn(self.reward_panel), run_time=1.0)
        self.wait(1.5)

        self.return_eq = MathTex(
            r"G_t", r"=", r"R_{t+1}", r"+", r"\gamma R_{t+2}", r"+", r"\gamma^2R_{t+3}", r"+", r"\cdots",
            font_size=31,
        ).to_edge(LEFT, buff=0.5).shift(UP * 0.5)
        self.return_eq[0].set_color(VALUE_COLOR)
        self.return_eq[2].set_color(REWARD_COLOR)
        self.return_eq[4].set_color(REWARD_COLOR)
        self.return_eq[6].set_color(REWARD_COLOR)
        self.play(Write(self.return_eq), run_time=1.0)
        trace_vector(self, dots[-1], self.return_eq[2], color=REWARD_COLOR, run_time=0.8)

        self.recursion_eq = MathTex(
            r"G_t", r"=", r"R_{t+1}", r"+", r"\gamma", r"G_{t+1}",
            font_size=34,
        ).move_to(self.return_eq)
        self.recursion_eq[0].set_color(VALUE_COLOR)
        self.recursion_eq[2].set_color(REWARD_COLOR)
        self.recursion_eq[5].set_color(VALUE_COLOR)
        self.play(ReplacementTransform(self.return_eq, self.recursion_eq), run_time=1.0)
        trace_vector(self, self.reward_panel, self.recursion_eq[5], color=VALUE_COLOR, run_time=0.8)
        self._replace_caption("The recursion G_t = R_{t+1} + gamma G_{t+1} will become Bellman's equation.")
        self.ingestion_wait(2.5)
        self.wait(269)  # narration-pacing hold — phase (b) target ~280 s
        self.play(FadeOut(dots), FadeOut(self.reward_panel), run_time=0.7)

    def _phase_c_transition_probability(self) -> None:
        self.mark_phase("transition_probability")
        focal = self._grid_cells[6]
        halo = Rectangle(
            width=focal.width + 0.16,
            height=focal.height + 0.16,
            stroke_color=ACTION_COLOR,
            stroke_width=3,
            fill_opacity=0,
        ).move_to(focal)
        arrows = VGroup()
        tuple_labels = VGroup()
        for prob, state, reward, done in SUCCESSORS:
            arrow = Arrow(self._state_center(6), self._state_center(state), buff=0.18, color=ACTION_COLOR)
            label = Text(f"{state}: 1/3, r=0, done={done}", font_size=14, color=WHITE)
            label.next_to(self._grid_cells[state], UP if state == 2 else DOWN, buff=0.06)
            arrows.add(arrow)
            tuple_labels.add(label)
        self.fan_group = VGroup(halo, arrows, tuple_labels)
        self.play(Create(halo), run_time=0.5)
        zoom_to(self, self.fan_group, scale=0.75)
        self.play(LaggedStart(*[Create(a) for a in arrows], *[FadeIn(t) for t in tuple_labels], lag_ratio=0.15), run_time=1.2)
        self.ingestion_wait(1.5)
        zoom_reset(self)

        self.p_chart = ActionBarChart(["7", "2", "10"], [1 / 3, 1 / 3, 1 / 3], width=3.5, height=2.4, bar_color=POLICY_COLOR)
        self.p_chart.to_edge(RIGHT, buff=0.45)
        sigma = MathTex(r"\sum_{s',r}p(s',r\mid s,a)=1", font_size=25, color=WHITE)
        sigma.next_to(self.p_chart, DOWN, buff=0.25)
        self.p_eq = MathTex(r"p", r"(", r"s'", r",", r"r", r"\mid", r"s", r",", r"a", r")", font_size=34)
        self.p_eq.to_edge(LEFT, buff=0.55).shift(UP * 0.2)
        self.p_eq[2].set_color(STATE_COLOR)
        self.p_eq[4].set_color(REWARD_COLOR)
        self.p_eq[6].set_color(STATE_COLOR)
        self.p_eq[8].set_color(ACTION_COLOR)
        self.play(FadeIn(self.p_chart), Write(self.p_eq), FadeIn(sigma), run_time=1.0)
        trace_vector(self, arrows, self.p_eq[2], color=STATE_COLOR, run_time=0.8)

        code_lines = [
            'env = gym.make("FrozenLake-v1", is_slippery=True)',
            "for prob, next_state, reward, done in env.unwrapped.P[6][2]:",
            "    print(prob, next_state, reward, done)",
            "policy = np.ones((env.observation_space.n, env.action_space.n)) / env.action_space.n",
        ]
        self.code = CodeStepper(code_lines, title="Runnable model access", width=5.8, font_size=14)
        self.code.panel.scale(0.82).to_edge(LEFT, buff=0.25).shift(DOWN * 1.55)
        self.play(FadeIn(self.code.panel), run_time=0.8)
        for idx, target in [(0, self.grid), (1, arrows), (2, self.p_chart)]:
            self.play(*self.code.step(self, idx), run_time=0.45)
            cross_highlight_pair(self, self.code.lines[idx], target, primary_color=CODE_ACCENT, pulse_run_time=0.65)
            self.wait(1.0)
        self._replace_caption("For state 6 and RIGHT, the environment has three successors: {7, 2, 10}.")
        self.wait(1.5)
        self.wait(249)  # narration-pacing hold — phase (c) target ~270 s
        self.play(FadeOut(self.fan_group), FadeOut(self.p_chart), FadeOut(sigma), FadeOut(self.p_eq), run_time=0.8)

    def _phase_d_policies(self) -> None:
        self.mark_phase("policies")
        deterministic = [2, 2, 1, 0, 2, 0, 1, 0, 2, 2, 1, 0, 0, 2, 2, 0]
        self.policy_grid = PolicyArrowGrid(4, 4, policy=deterministic, holes={(1, 1), (1, 3), (2, 3), (3, 0)}, goal=(3, 3), width=3.2)
        self.policy_grid.to_edge(LEFT, buff=0.45).shift(UP * 0.35)
        self.pi_bars = ActionBarChart(["L", "D", "R", "U"], [0.25, 0.25, 0.25, 0.25], width=3.4, height=2.3, bar_color=POLICY_COLOR)
        self.pi_bars.to_edge(RIGHT, buff=0.45).shift(UP * 0.25)
        pi_eq = MathTex(r"\pi(a\mid s)", r"=", r"\Pr\{A_t=a\mid S_t=s\}", r"\quad", r"\sum_a\pi(a\mid s)=1", font_size=28)
        pi_eq[0].set_color(POLICY_COLOR)
        pi_eq[4].set_color(POLICY_COLOR)
        pi_eq.next_to(self.grid, DOWN, buff=0.22)
        self.pi_eq = pi_eq
        self.play(FadeIn(self.policy_grid), FadeIn(self.pi_bars), Write(pi_eq), run_time=1.0)
        self.play(*self.code.step(self, 3), run_time=0.45)
        cross_highlight_pair(self, self.code.lines[3], self.pi_bars, primary_color=POLICY_COLOR, pulse_run_time=0.7)
        self._replace_caption("p is the environment's response; pi is the agent's action distribution.")
        self.wait(1.5)
        self.wait(202)  # narration-pacing hold — phase (d) target ~210 s
        self.play(FadeOut(self.policy_grid), FadeOut(self.pi_bars), FadeOut(self.pi_eq), FadeOut(self.code.panel), run_time=0.8)

    def _phase_e_values(self) -> None:
        self.mark_phase("value_functions")
        values = [0.04, 0.05, 0.07, 0.05, 0.05, 0.0, 0.12, 0.0, 0.08, 0.14, 0.22, 0.0, 0.0, 0.20, 0.46, 0.0]
        self.heatmap = ValueHeatmap(4, 4, values=values, holes={(1, 1), (1, 3), (2, 3), (3, 0)}, terminal={(3, 3)}, width=3.9)
        self.heatmap.move_to(self.grid)
        self.play(self.grid.animate.set_opacity(OPACITY_BACKGROUND), FadeIn(self.heatmap), run_time=1.0)
        self.wait(1.5)

        v_eq = MathTex(r"v_\pi(s)", r"\doteq", r"\mathbb{E}_\pi", r"[G_t\mid S_t=s]", font_size=30)
        q_eq = MathTex(r"q_\pi(s,a)", r"\doteq", r"\mathbb{E}_\pi", r"[G_t\mid S_t=s,A_t=a]", font_size=30)
        bridge = MathTex(r"v_\pi(s)", r"=", r"\sum_a", r"\pi(a\mid s)", r"q_\pi(s,a)", font_size=30)
        for eq in (v_eq, q_eq, bridge):
            eq.to_edge(LEFT, buff=0.45)
        q_eq.next_to(v_eq, DOWN, buff=0.18, aligned_edge=LEFT)
        bridge.next_to(q_eq, DOWN, buff=0.18, aligned_edge=LEFT)
        self.value_eqs = VGroup(v_eq, q_eq, bridge)
        self.play(LaggedStart(Write(v_eq), Write(q_eq), Write(bridge), lag_ratio=0.25), run_time=1.4)
        trace_vector(self, self.heatmap.cells[(1, 2)], v_eq[0], color=VALUE_COLOR, run_time=0.8)
        self.q_bars = ActionBarChart(["L", "D", "R", "U"], [0.05, 0.10, 0.07, 0.04], width=3.4, height=2.3, bar_color=VALUE_COLOR)
        self.q_bars.to_edge(RIGHT, buff=0.45)
        self.play(FadeIn(self.q_bars), run_time=0.8)
        self._replace_caption("v_pi is defined for any policy pi, including uniform-random.")
        self.wait(1.5)
        self.wait(239)  # narration-pacing hold — phase (e) target ~250 s
        self.play(FadeOut(self.q_bars), run_time=0.6)

    def _phase_recap(self) -> None:
        self.mark_phase("recap")
        self.play(self.heatmap.animate.set_opacity(OPACITY_BACKGROUND), self.value_eqs.animate.set_opacity(OPACITY_SECONDARY), run_time=0.8)
        recap_lines = note_stack([
            "pi chooses actions",
            "p chooses outcomes",
            "r is immediate reward",
            "gamma carries future return",
            "v_pi is expected return under pi",
        ], font_size=20)
        self.recap = panel("Recap before Bellman", recap_lines, VALUE_COLOR, width=5.2).move_to(UP * 0.05)
        self.play(FadeIn(self.recap, shift=DOWN * 0.1), run_time=0.8)
        self.ingestion_wait(2.5)
        self.wait(74)  # narration-pacing hold — recap target ~80 s
        self.play(FadeOut(self.recap), FadeOut(self.value_eqs), run_time=0.7)

    def _phase_f_bellman(self) -> None:
        self.mark_phase("bellman_expectation")
        start = MathTex(r"G_t", r"=", r"R_{t+1}", r"+", r"\gamma", r"G_{t+1}", font_size=32)
        start.to_edge(LEFT, buff=0.45).shift(UP * 1.2)
        self.play(Write(start), run_time=0.8)
        zoom_to(self, start, scale=0.65)
        first = MathTex(r"v_\pi(s)", r"=", r"\mathbb{E}_\pi", r"[G_t\mid S_t=s]", font_size=32)
        equation_morph(self, start, first, run_time=1.0)
        self.ingestion_wait(2.5)
        second = MathTex(r"v_\pi(s)", r"=", r"\mathbb{E}_\pi", r"[R_{t+1}", r"+", r"\gamma G_{t+1}", r"\mid S_t=s]", font_size=30)
        equation_morph(self, first, second, run_time=1.0)
        self.ingestion_wait(2.5)
        zoom_reset(self)

        self.backup = BackupDiagram(
            n_actions=3,
            n_outcomes=2,
            root_label=r"s",
            action_labels=["a1", "a2", "a3"],
            outcome_labels=[[r"s',r", r"s',r"], [r"s',r", r"s',r"], [r"s',r", r"s',r"]],
            total_width=4.6,
            level_height=1.05,
        )
        self.backup.to_edge(RIGHT, buff=0.35).shift(DOWN * 0.2)
        self.play(FadeIn(self.backup), run_time=1.0)
        branch_pi = MathTex(r"\pi(a\mid s)", font_size=28, color=POLICY_COLOR).next_to(self.backup, UP, buff=0.08)
        leaf_p = MathTex(r"p(s',r\mid s,a)", font_size=28, color=STATE_COLOR).next_to(self.backup, DOWN, buff=0.08)
        leaf_value = MathTex(r"[r+\gamma v_\pi(s')]", font_size=28, color=VALUE_COLOR).next_to(leaf_p, DOWN, buff=0.1)
        self.play(Write(branch_pi), run_time=0.6)
        trace_vector(self, self.backup.action_nodes[1], branch_pi, color=POLICY_COLOR, run_time=0.8)
        self.play(Write(leaf_p), run_time=0.6)
        trace_vector(self, self.backup.outcome_nodes[1][0], leaf_p, color=STATE_COLOR, run_time=0.8)
        self.play(Write(leaf_value), run_time=0.6)
        trace_vector(self, self.backup.outcome_nodes[1][1], leaf_value, color=VALUE_COLOR, run_time=0.8)

        final = MathTex(
            r"v_\pi(s)", r"=", r"\sum_a", r"\pi(a\mid s)", r"\sum_{s',r}", r"p(s',r\mid s,a)", r"[r+\gamma v_\pi(s')]",
            font_size=28,
        )
        final.to_edge(LEFT, buff=0.35).shift(UP * 0.6)
        final[0].set_color(VALUE_COLOR)
        final[3].set_color(POLICY_COLOR)
        final[5].set_color(STATE_COLOR)
        final[6].set_color(VALUE_COLOR)
        equation_morph(self, second, final, run_time=1.2)
        self.final_eq = final
        self.ingestion_wait(2.5)
        self.wait(259)  # narration-pacing hold — phase (f) target ~280 s

    def _phase_closing(self) -> None:
        self.mark_phase("closing")
        next_pill = pill("Next: dp_policy_eval", color=POLICY_COLOR)
        next_pill.to_edge(RIGHT, buff=0.6).to_edge(DOWN, buff=0.75)
        self.play(FadeIn(next_pill, shift=UP * 0.1), run_time=0.7)
        self._replace_caption("Policy evaluation turns this equality into an assignment.")
        self.wait(2.5)
        self.wait(75)  # narration-pacing hold — closing target ~80 s
