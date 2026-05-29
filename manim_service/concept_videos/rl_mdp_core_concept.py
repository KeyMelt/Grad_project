from __future__ import annotations

import os
from pathlib import Path

import gymnasium
import numpy as np
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    CurvedArrow,
    Create,
    DashedLine,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    Indicate,
    LaggedStart,
    MathTex,
    Rectangle,
    RoundedRectangle,
    Text,
    TransformMatchingTex,
    VGroup,
    Write,
    config,
)

from manim_service.scenes import (
    ACTION_COLOR,
    BG_GRID,
    BG_PANEL,
    CODE_ACCENT,
    OPACITY_PRIMARY,
    OPACITY_SECONDARY,
    PENALTY_COLOR,
    POLICY_COLOR,
    REWARD_COLOR,
    STATE_COLOR,
    VALUE_COLOR,
    ActionBarChart,
    BaseConceptScene,
    CodeStepper,
    cross_highlight_pair,
    equation_morph,
    pan_to_follow,
    sprite_action_binding,
    trace_vector,
    zoom_reset,
    zoom_to,
)


ASSET_DIR = Path(gymnasium.__file__).parent / "envs" / "toy_text" / "img"
REQUIRED_ASSETS = [
    "ice.png",
    "stool.png",
    "hole.png",
    "goal.png",
    "elf_right.png",
    "elf_left.png",
    "elf_up.png",
    "elf_down.png",
]
missing = [name for name in REQUIRED_ASSETS if not (ASSET_DIR / name).exists()]
if missing:
    raise FileNotFoundError(f"MISSING_ASSETS: {missing}")


def compute_return(gamma: float, rewards: list[float]) -> float:
    return sum((gamma**idx) * reward for idx, reward in enumerate(rewards))


class RLMDPCoreConcept(BaseConceptScene):
    cell_size = 0.86
    holes = {5, 7, 11, 12}
    goal = 15

    def construct(self) -> None:
        self.header = None
        self.caption = None
        self.grid = None
        self.state_labels = None
        self.agent = None
        self.action_arrow = None

        self._phase_s1_p1_grid_entry()
        self._phase_s1_p2a_failed_attempt_one()
        self._phase_s1_p2b_failed_attempt_two()
        self._phase_s1_p3_success()
        self._phase_s2_p4_state_indices()
        self._phase_s2_p5_markov()
        self._phase_s3a_p6_p_equation()
        self._phase_s3a_p7_branches()
        self._phase_s3b_p8_bars()
        self._phase_s3b_p9_code()
        self._phase_s3b_p10_normalization()
        self._phase_s4_p11_return_equation()
        self._phase_s4_p12_return_path()
        self._phase_s4_p13_gamma_sweep()
        self._phase_s4_p14_recursion()
        self._phase_s4_p15_hold()

    def _asset(self, name: str) -> str:
        return str(ASSET_DIR / name)

    def _tile_asset_for(self, state: int) -> str:
        if state == 0:
            return "stool.png"
        if state in self.holes:
            return "hole.png"
        if state == self.goal:
            return "goal.png"
        return "ice.png"

    def _make_grid(self, scale: float = 1.0, labels: bool = False) -> VGroup:
        size = self.cell_size * scale
        cells = Group()
        for state in range(16):
            row, col = divmod(state, 4)
            bg = RoundedRectangle(
                width=size,
                height=size,
                corner_radius=0.06,
                fill_color=BG_PANEL,
                fill_opacity=1.0,
                stroke_color=STATE_COLOR,
                stroke_width=1.0,
            )
            img = ImageMobject(self._asset(self._tile_asset_for(state))).set_height(size * 0.82)
            cell = Group(bg, img)
            cell.move_to(self._cell_point(row, col, size))
            cells.add(cell)
        frame = RoundedRectangle(
            width=size * 4 + 0.2,
            height=size * 4 + 0.2,
            corner_radius=0.12,
            fill_color=BG_GRID,
            fill_opacity=0.16,
            stroke_color=STATE_COLOR,
            stroke_width=1.4,
        )
        grid = Group(frame, cells)
        grid.cells = cells  # type: ignore[attr-defined]
        if labels:
            grid.labels = self._state_labels_for(cells)  # type: ignore[attr-defined]
            grid.add(grid.labels)  # type: ignore[attr-defined]
        return grid

    def _cell_point(self, row: int, col: int, size: float) -> np.ndarray:
        return np.array([(col - 1.5) * size, (1.5 - row) * size, 0.0])

    def _cell(self, state: int):
        return self.grid.cells[state]  # type: ignore[union-attr, attr-defined]

    def _cell_center(self, state: int) -> np.ndarray:
        return self._cell(state).get_center()

    def _state_labels_for(self, cells: VGroup) -> VGroup:
        labels = VGroup()
        for state, cell in enumerate(cells):
            label = Text(str(state), font_size=22, color=STATE_COLOR)
            label.move_to(cell.get_center() + UP * 0.24 + LEFT * 0.24)
            labels.add(label)
        return labels

    def _agent_sprite(self, direction: str = "right", height: float | None = None) -> ImageMobject:
        agent = ImageMobject(self._asset(f"elf_{direction}.png"))
        agent.set_height(height or self.cell_size * 0.62)
        return agent

    def _swap_caption(self, text: str, *, run_time: float = 0.45) -> None:
        new_caption = self.place_caption(text, font_size=22)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=run_time)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=run_time)
        self.caption = new_caption

    def _move_agent_to(self, state: int, direction: str = "right", run_time: float = 0.75) -> None:
        if self.agent is None:
            self.agent = self._agent_sprite(direction)
            self.agent.move_to(self._cell_center(state))
            self.play(FadeIn(self.agent), run_time=run_time)
            return
        replacement = self._agent_sprite(direction, height=self.agent.get_height())
        replacement.move_to(self.agent.get_center())
        self.play(FadeOut(self.agent), FadeIn(replacement), run_time=0.2)
        self.agent = replacement
        self.smooth_move_to(self.agent, self._cell_center(state), run_time=run_time)

    def _trail_dot(self, state: int) -> Rectangle:
        dot = Rectangle(
            width=self.cell_size * 0.22,
            height=self.cell_size * 0.22,
            fill_color=POLICY_COLOR,
            fill_opacity=OPACITY_SECONDARY,
            stroke_width=0,
        )
        dot.move_to(self._cell_center(state))
        return dot

    def _flash_cell(self, state: int, color: str) -> None:
        self.play(Indicate(self._cell(state), color=color, scale_factor=1.08), run_time=0.65)

    def _path_walk(self, states: list[int], directions: list[str], *, run_time: float = 0.75) -> VGroup:
        trail = VGroup()
        for idx, state in enumerate(states):
            if idx > 0:
                trail_dot = self._trail_dot(states[idx - 1])
                trail.add(trail_dot)
                self.play(FadeIn(trail_dot), run_time=0.18)
            self._move_agent_to(state, directions[min(idx, len(directions) - 1)], run_time=run_time)
        return trail

    def _make_branch(self, target_state: int, color: str, label_text: str) -> VGroup:
        start = self._cell_center(6)
        end = self._cell_center(target_state)
        arrow = Arrow(start, end, buff=0.28, color=color, stroke_width=4)
        label = Text(label_text, font_size=22, color=color)
        # Anchor labels relative to state-6 grid cell (geometry-relative, §4)
        y_offset = {2: 1.05, 7: 0.55, 10: 0.05}[target_state]
        label.move_to(self._cell_center(6) + RIGHT * 2.55 + UP * y_offset)
        return VGroup(arrow, label)

    def _scale_to_frame_width(self, eq: MathTex, fraction: float = 0.9) -> MathTex:
        max_width = config.frame_width * fraction
        if eq.get_width() > max_width:
            eq.scale_to_fit_width(max_width)
        eq.move_to(ORIGIN)
        return eq

    def _compact_p_eq(self) -> MathTex:
        eq = MathTex("p", "(", "s'", "\\mid", "s", ",", "a", ")", font_size=48)
        eq[2].set_color(STATE_COLOR)
        eq[4].set_color(STATE_COLOR)
        eq[6].set_color(ACTION_COLOR)
        eq.scale_to_fit_width(min(eq.get_width(), 3.0))
        # place_left_panel anchors to frame edge; shift UP to upper-left quadrant (§4)
        self.place_left_panel(eq)
        eq.shift(UP * 1.0)
        return eq

    def _compact_gt_eq(self) -> MathTex:
        eq = MathTex(
            "G_t", "=",
            "\\sum_{k=0}^{\\infty}", "\\gamma^k", "R_{t+k+1}",
            font_size=42,
        )
        eq[0].set_color(VALUE_COLOR)
        eq[3].set_color(VALUE_COLOR)
        eq[4].set_color(REWARD_COLOR)
        eq.scale_to_fit_width(min(eq.get_width(), 3.0))
        # place_left_panel anchors to frame edge; shift UP to upper-left quadrant (§4)
        self.place_left_panel(eq)
        eq.shift(UP * 0.95)
        return eq

    def _code_fadeouts(self) -> list:
        if not hasattr(self, "code"):
            return []
        fadeouts = [FadeOut(self.code.panel)]
        rect = getattr(self.code, "_rect", None)
        if rect is not None:
            fadeouts.append(FadeOut(rect))
            self.code._rect = None
        return fadeouts

    def _make_accumulator(self, text: str) -> VGroup:
        title = Text("Return accumulator", font_size=22, color=CODE_ACCENT)
        body = Text(text, font_size=24, color=VALUE_COLOR)
        group = VGroup(title, body).arrange(DOWN, buff=0.18)
        bg = RoundedRectangle(
            width=max(group.get_width() + 0.5, 3.1),
            height=group.get_height() + 0.45,
            corner_radius=0.12,
            fill_color=BG_PANEL,
            fill_opacity=1.0,
            stroke_color=VALUE_COLOR,
            stroke_width=1.4,
        )
        group.move_to(bg.get_center())
        return VGroup(bg, group)

    def _color_p_eq(self, eq: MathTex) -> MathTex:
        for idx in (2, 6, 15, 21):
            eq[idx].set_color(STATE_COLOR)
        for idx in (4, 18):
            eq[idx].set_color(REWARD_COLOR)
        for idx in (8, 24):
            eq[idx].set_color(ACTION_COLOR)
        return eq

    def _color_gt_sum(self, eq: MathTex) -> MathTex:
        for idx in (0, 4, 7, 13):
            eq[idx].set_color(VALUE_COLOR)
        for idx in (2, 5, 8, 14):
            eq[idx].set_color(REWARD_COLOR)
        return eq

    def _color_gt_recursive(self, eq: MathTex) -> MathTex:
        for idx in (0, 4, 5):
            eq[idx].set_color(VALUE_COLOR)
        eq[2].set_color(REWARD_COLOR)
        return eq

    def _phase_s1_p1_grid_entry(self) -> None:
        self.mark_phase("seg1_grid_entry")
        self.header = self.show_header(
            "Reinforcement Learning and the MDP Framework",
            subtitle="FrozenLake — the agent learns from scratch",
        )
        static_grid = self._make_grid(scale=1.08, labels=False)
        self.play(FadeIn(static_grid), run_time=1.2)
        self.ingestion_wait(2.5)
        self._swap_caption("An agent. A goal. A frozen lake.")
        self.wait(2.0)
        self.static_grid = static_grid
        self.hold_until(31.5)

    def _phase_s1_p2a_failed_attempt_one(self) -> None:
        self.mark_phase("seg1_fail1")
        self.grid = self._make_grid(scale=1.08, labels=False)
        self.play(FadeOut(self.static_grid), FadeIn(self.grid), run_time=1.0)
        self._move_agent_to(0, "right", run_time=0.45)
        self._swap_caption("No map. No hint. The elf goes.")
        pan_to_follow(self, self.agent, path_points=[self._cell_center(s) for s in [0, 1, 5]], frame_scale=0.82)
        trail = self._path_walk([1, 5], ["right", "down"], run_time=0.8)
        self._flash_cell(5, PENALTY_COLOR)
        self.play(self.grid.animate.set_opacity(OPACITY_SECONDARY), run_time=0.25)
        self.play(self.grid.animate.set_opacity(OPACITY_PRIMARY), run_time=0.25)
        zoom_reset(self, run_time=1.4)
        self._swap_caption("No map. No hint. Just a zero.")
        self.wait(2.0)
        self.trail = trail
        self.hold_until(74.1)

    def _phase_s1_p2b_failed_attempt_two(self) -> None:
        self.mark_phase("seg1_fail2")
        self.play(FadeOut(self.trail), run_time=0.35)
        self.smooth_move_to(self.agent, self._cell_center(0), run_time=1.2)
        self._swap_caption("It tried again.")
        pan_to_follow(self, self.agent, path_points=[self._cell_center(s) for s in [0, 4, 8, 9, 5]], frame_scale=0.82)
        self.trail = self._path_walk([4, 8, 9, 5], ["down", "down", "right", "up"], run_time=0.72)
        self._flash_cell(5, PENALTY_COLOR)
        self.play(self.grid.animate.set_opacity(OPACITY_SECONDARY), run_time=0.25)
        self.play(self.grid.animate.set_opacity(OPACITY_PRIMARY), run_time=0.25)
        zoom_reset(self, run_time=1.4)
        self._swap_caption("Same result. The ice moved it sideways.")
        self.wait(1.5)
        self.hold_until(121.0)

    def _phase_s1_p3_success(self) -> None:
        self.mark_phase("seg1_success")
        self.play(FadeOut(self.trail), run_time=0.35)
        self.smooth_move_to(self.agent, self._cell_center(0), run_time=1.2)
        self._swap_caption("One more time.")
        pan_to_follow(self, self.agent, path_points=[self._cell_center(s) for s in [0, 4, 8, 9, 10, 14, 15]], frame_scale=0.82)
        self.trail = self._path_walk([4, 8, 9, 10, 14, 15], ["down", "down", "right", "right", "down", "right"], run_time=0.65)
        self._flash_cell(15, REWARD_COLOR)
        zoom_reset(self, run_time=1.4)
        self.reward_label = Text("1.0", font_size=28, color=REWARD_COLOR)
        self.reward_label.next_to(self._cell(15), UP, buff=0.08)
        self.play(FadeIn(self.reward_label), run_time=0.6)
        self._swap_caption("One number. That is all the agent ever receives.")
        self.wait(2.5)
        self.hold_until(196.6)

    def _phase_s2_p4_state_indices(self) -> None:
        self.mark_phase("seg2_state_indices")
        self.play(FadeOut(self.reward_label), FadeOut(self.agent), FadeOut(self.trail), run_time=0.7)
        self.agent = None
        self._swap_caption("Each cell is a state. The agent always knows which one it occupies.")
        self.state_labels = self._state_labels_for(self.grid.cells)  # type: ignore[union-attr]
        self.play(LaggedStart(*[Write(label) for label in self.state_labels], lag_ratio=0.07), run_time=2.6)
        self.wait(2.0)
        self.hold_until(255.6)

    def _phase_s2_p5_markov(self) -> None:
        self.mark_phase("seg2_markov")
        self._move_agent_to(6, "right", run_time=0.6)
        arcs = VGroup(
            CurvedArrow(self._cell_center(1), self._cell_center(6), color=CODE_ACCENT),
            CurvedArrow(self._cell_center(9), self._cell_center(6), color=CODE_ACCENT),
            CurvedArrow(self._cell_center(10), self._cell_center(6), color=CODE_ACCENT),
        )
        history = Text("...history...", font_size=22, color=CODE_ACCENT)
        history.next_to(arcs, UP, buff=0.08)
        self.play(LaggedStart(*[Write(arc) for arc in arcs], Write(history), lag_ratio=0.2), run_time=1.2)
        self._swap_caption("The ice does not remember. Whatever path brought the agent here is gone.")
        self.play(FadeOut(arcs), FadeOut(history), run_time=0.7)
        self.action_arrow = Arrow(
            self._cell_center(6),
            self._cell_center(6) + RIGHT * self.cell_size * 0.78,
            buff=0.16,
            color=ACTION_COLOR,
            stroke_width=5,
        )
        action_label = Text("a = RIGHT", font_size=22, color=ACTION_COLOR)
        action_label.next_to(self.action_arrow, UP, buff=0.06)
        self.action_group = VGroup(self.action_arrow, action_label)
        self.play(Create(self.action_arrow), Write(action_label), run_time=0.9)
        sprite_action_binding(self, self.agent, highlight_tokens=[], settle_time=0.1)
        self._swap_caption("Only state 6 and the action RIGHT determine what comes next.")
        self.wait(2.0)
        self.hold_until(320.8)

    def _phase_s3a_p6_p_equation(self) -> None:
        self.mark_phase("seg3a_p_equation_solo")
        self.play(
            FadeOut(self.grid),
            FadeOut(self.state_labels),
            FadeOut(self.agent),
            FadeOut(self.action_group),
            FadeOut(self.caption),
            run_time=1.2,
        )
        self.caption = None
        self.p_eq_full = self._color_p_eq(
            MathTex(
                "p", "(", "s'", ",", "r",
                "\\mid", "s", ",", "a", ")",
                "\\doteq",
                "\\Pr", "\\bigl\\{",
                "S_{t+1}", "=", "s'", ",",
                "R_{t+1}", "=", "r",
                "\\mid",
                "S_t", "=", "s", ",",
                "A_t", "=", "a",
                "\\bigr\\}",
                font_size=48,
            )
        )
        self.p_eq_full.move_to(ORIGIN)
        self._scale_to_frame_width(self.p_eq_full, 0.9)
        self.play(LaggedStart(*[Write(part) for part in self.p_eq_full], lag_ratio=0.12), run_time=3.0)
        self.wait(2.0)
        self.ingestion_wait(2.5)
        self._swap_caption("The environment's response law. Given where you are and what you do, this is what you receive.")
        self.wait(1.0)
        self.hold_until(364.9)

    def _phase_s3a_p7_branches(self) -> None:
        self.mark_phase("seg3a_branches")
        self.grid = self._make_grid(scale=0.82, labels=True)
        self.grid.move_to(ORIGIN + DOWN * 0.05)
        self.action_arrow = Arrow(
            self._cell_center(6),
            self._cell_center(6) + RIGHT * self.cell_size * 0.58,
            buff=0.12,
            color=ACTION_COLOR,
            stroke_width=4,
        )
        self.p_eq_panel = self._compact_p_eq()
        self.play(FadeOut(self.p_eq_full), FadeIn(self.p_eq_panel), FadeIn(self.grid), FadeIn(self.action_arrow), run_time=1.2)
        self.ingestion_wait(2.5)
        self._swap_caption("Three equally likely outcomes. One action, three destinations.")
        trace_vector(self, self._cell(6), self.p_eq_panel[4], color=STATE_COLOR)
        trace_vector(self, self.action_arrow, self.p_eq_panel[6], color=ACTION_COLOR)
        self.branches = VGroup(
            self._make_branch(2, STATE_COLOR, "p=1/3 → s'=2"),
            self._make_branch(7, PENALTY_COLOR, "p=1/3 → s'=7 (hole)"),
            self._make_branch(10, STATE_COLOR, "p=1/3 → s'=10"),
        )
        self.play(LaggedStart(*[Create(branch) for branch in self.branches], lag_ratio=0.3), run_time=2.1)
        trace_vector(self, self._cell(2), self.p_eq_panel[2], color=STATE_COLOR)
        trace_vector(self, self._cell(7), self.p_eq_panel[2], color=PENALTY_COLOR)
        trace_vector(self, self._cell(10), self.p_eq_panel[2], color=STATE_COLOR)
        self.wait(2.0)
        self.ingestion_wait(2.5)
        self.hold_until(447.1)

    def _phase_s3b_p8_bars(self) -> None:
        self.mark_phase("seg3b_barchart")
        self.chart = ActionBarChart(
            ["s'=2", "s'=7", "s'=10"],
            [0.0, 0.0, 0.0],
            bar_color=POLICY_COLOR,
            label_font_size=22,
            value_font_size=22,
            accent=POLICY_COLOR,
        )
        self.place_mid_right_panel(self.chart)
        # Chart is PRIMARY; p_eq_panel and grid dim to SECONDARY (choreo §3 P8, §2 focus rule)
        self.play(
            FadeIn(self.chart),
            self.p_eq_panel.animate.set_opacity(OPACITY_SECONDARY),
            self.grid.animate.set_opacity(OPACITY_SECONDARY),
            run_time=1.0,
        )
        self.chart.update_bars(self, [1 / 3, 1 / 3, 1 / 3])
        self.play(Indicate(self.chart.bars[1], color=PENALTY_COLOR), run_time=0.8)
        self.sigma_annotation = Text("Σ = 1", font_size=22, color=REWARD_COLOR)
        self.sigma_annotation.next_to(self.chart, UP, buff=0.12)
        self.play(FadeIn(self.sigma_annotation), run_time=0.5)
        self._swap_caption("Each bar is how likely the agent actually ends up in that cell. Intention and outcome are different.")
        self.wait(1.5)
        self.ingestion_wait(2.5)
        self.hold_until(503.3)

    def _phase_s3b_p9_code(self) -> None:
        self.mark_phase("seg3b_codestepper")
        # Migrate chart to inset: anchor to place_bottom_right_panel position (§4)
        _chart_inset = self.chart.copy()
        self.place_bottom_right_panel(_chart_inset)
        self.smooth_move_to(self.chart, _chart_inset.get_center(), run_time=1.2)
        self.play(self.chart.animate.scale(0.72), self.sigma_annotation.animate.next_to(self.chart, UP, buff=0.08), run_time=0.7)
        code_lines = [
            'env = gym.make("FrozenLake-v1", is_slippery=True)',
            "for prob, next_state, reward, done in env.unwrapped.P[6][2]:",
            '    print(f"prob={prob:.3f}  next_state={next_state}  reward={reward}  done={done}")',
        ]
        self.code = CodeStepper(code_lines, title="Gymnasium", width=3.8, font_size=22)
        self.code.panel.scale(0.42)
        # Anchor code panel just below header, right-aligned — geometry-relative (§4)
        self.code.panel.next_to(self.header, DOWN, buff=0.25).to_edge(RIGHT, buff=0.45)
        zoom_reset(self, run_time=1.4)
        self.play(FadeIn(self.code.panel), run_time=0.8)
        self.ingestion_wait(2.5)
        self._swap_caption("The same distribution, readable in a single Python call.")
        self.play(*self.code.step(self, 0), run_time=0.8)
        cross_highlight_pair(self, self.code.lines[0], self.grid, primary_color=ACTION_COLOR, secondary_color=STATE_COLOR)
        self.wait(1.5)
        self.play(*self.code.step(self, 1), run_time=0.8)
        cross_highlight_pair(self, self.code.lines[1], self._cell(6), primary_color=ACTION_COLOR, secondary_color=STATE_COLOR)
        cross_highlight_pair(self, self.code.lines[1], self.action_arrow, primary_color=ACTION_COLOR, secondary_color=ACTION_COLOR)
        self.wait(1.5)
        self.play(*self.code.step(self, 2), run_time=0.8)
        cross_highlight_pair(self, self.code.lines[2], self._cell(10), primary_color=ACTION_COLOR, secondary_color=STATE_COLOR)
        self.play(Indicate(self.chart.bars[2], color=STATE_COLOR), run_time=0.7)
        self.wait(1.5)
        cross_highlight_pair(self, self.code.lines[2], self._cell(7), primary_color=ACTION_COLOR, secondary_color=PENALTY_COLOR)
        self.play(Indicate(self.chart.bars[1], color=PENALTY_COLOR), run_time=0.7)
        self.wait(1.5)
        cross_highlight_pair(self, self.code.lines[2], self._cell(2), primary_color=ACTION_COLOR, secondary_color=STATE_COLOR)
        self.play(Indicate(self.chart.bars[0], color=STATE_COLOR), Indicate(self.sigma_annotation, color=REWARD_COLOR), run_time=0.8)
        self.wait(1.5)
        self.hold_until(594.0)

    def _phase_s3b_p10_normalization(self) -> None:
        self.mark_phase("seg3b_normalization")
        self.play(*self._code_fadeouts(), FadeOut(self.branches), run_time=0.8)
        norm_eq = MathTex(
            "\\sum_{s'}", "\\sum_r",
            "p", "(", "s'", ",", "r",
            "\\mid", "s", ",", "a", ")",
            "=", "1",
            font_size=36,
        )
        norm_eq[4].set_color(STATE_COLOR)
        norm_eq[6].set_color(REWARD_COLOR)
        norm_eq[8].set_color(STATE_COLOR)
        norm_eq[10].set_color(ACTION_COLOR)
        # place_left_panel + relative DOWN offset keeps norm_eq in lower-left area (§4)
        self.place_left_panel(norm_eq)
        norm_eq.shift(DOWN * 0.65)
        self.play(FadeOut(self.p_eq_panel), FadeIn(norm_eq), run_time=1.0)
        self._swap_caption("The four-argument form is complete. Sum over rewards to get state-transition probability.")
        self.wait(2.0)
        self.marginal_eq = MathTex(
            "p", "(", "s'", "\\mid", "s", ",", "a", ")",
            "=", "\\sum_r",
            "p", "(", "s'", ",", "r",
            "\\mid", "s", ",", "a", ")",
            font_size=36,
        )
        for idx in (2, 4, 12, 16):
            self.marginal_eq[idx].set_color(STATE_COLOR)
        for idx in (6, 18):
            self.marginal_eq[idx].set_color(ACTION_COLOR)
        self.marginal_eq[14].set_color(REWARD_COLOR)
        equation_morph(self, norm_eq, self.marginal_eq, run_time=2.0)
        self.ingestion_wait(2.5)
        self.hold_until(652.3)

    def _cleanup_s3b_for_return_equation(self) -> None:
        self.play(
            FadeOut(self.marginal_eq),
            FadeOut(self.chart),
            FadeOut(self.sigma_annotation),
            FadeOut(self.grid),
            FadeOut(self.action_arrow),
            FadeOut(self.caption),
            run_time=1.1,
        )
        self.caption = None

    def _phase_s4_p11_return_equation(self) -> None:
        self.mark_phase("seg4_Gt_equation_solo")
        self._cleanup_s3b_for_return_equation()
        self.gt_sum = self._color_gt_sum(
            MathTex(
                "G_t", "=",
                "R_{t+1}", "+",
                "\\gamma", "R_{t+2}", "+",
                "\\gamma^2", "R_{t+3}", "+",
                "\\cdots",
                "=",
                "\\sum_{k=0}^{\\infty}", "\\gamma^k", "R_{t+k+1}",
                font_size=48,
            )
        )
        self.gt_sum.move_to(ORIGIN)
        self._scale_to_frame_width(self.gt_sum, 0.9)
        self.play(LaggedStart(*[Write(part) for part in self.gt_sum], lag_ratio=0.12), run_time=3.0)
        self.wait(2.0)
        self.ingestion_wait(2.5)
        self._swap_caption("The agent's goal is not the next reward. It is the sum of all future rewards, weighted by distance.")
        self.wait(1.0)
        self.hold_until(711.6)

    def _phase_s4_p12_return_path(self) -> None:
        self.mark_phase("seg4_return_computation")
        self.grid = self._make_grid(scale=0.82, labels=True)
        self.grid.move_to(ORIGIN + DOWN * 0.05)
        self.accumulator = self._make_accumulator("G₀ = 0")
        self.place_mid_right_panel(self.accumulator)
        self.gt_panel = self._compact_gt_eq()
        self.play(FadeOut(self.gt_sum), FadeIn(self.gt_panel), FadeIn(self.grid), FadeIn(self.accumulator), run_time=1.2)
        self.ingestion_wait(2.5)
        self._swap_caption("Five steps of nothing. Then a reward five steps away is still worth 95 cents on the dollar.")
        self.agent = None
        self._move_agent_to(0, "down", run_time=0.35)
        self.return_trail = VGroup()
        path = [4, 8, 9, 10, 14, 15]
        dirs = ["down", "down", "right", "right", "down", "right"]
        rewards = [0, 0, 0, 0, 0, 1.0]
        trace_vector(self, self._cell(0), self.gt_panel[4], color=REWARD_COLOR)
        for idx, (state, direction, reward) in enumerate(zip(path, dirs, rewards)):
            prev = 0 if idx == 0 else path[idx - 1]
            dot = self._trail_dot(prev)
            self.return_trail.add(dot)
            self.play(FadeIn(dot), run_time=0.18)
            self._move_agent_to(state, direction, run_time=0.62)
            label = Text("R=1.0" if reward else "R=0", font_size=22, color=REWARD_COLOR if reward else CODE_ACCENT)
            label.next_to(self._cell(state), UP, buff=0.05)
            self.play(FadeIn(label), run_time=0.25)
            if reward:
                g0 = round(0.99**5 * 1.0, 3)
                new_acc = self._make_accumulator(f"G₀ ≈ {g0:.3f}")
                new_acc.move_to(self.accumulator)
                self._flash_cell(15, REWARD_COLOR)
                self.play(FadeOut(self.accumulator), FadeIn(new_acc), run_time=0.55)
                self.accumulator = new_acc
                trace_vector(self, self._cell(15), self.gt_panel[4], color=REWARD_COLOR)
                trace_vector(self, self.accumulator, self.gt_panel[0], color=VALUE_COLOR)
            self.wait(1.5)
            self.play(FadeOut(label), run_time=0.2)
        self.ingestion_wait(2.5)
        self.hold_until(796.9)

    def _phase_s4_p13_gamma_sweep(self) -> None:
        self.mark_phase("seg4_gamma_sweep")
        # Migrate accumulator to inset: anchor to place_bottom_right_panel position (§4)
        _acc_inset = self.accumulator.copy()
        self.place_bottom_right_panel(_acc_inset)
        self.smooth_move_to(self.accumulator, _acc_inset.get_center(), run_time=1.2)
        self.play(self.accumulator.animate.scale(0.76), run_time=0.6)
        self.gamma_chart = ActionBarChart(
            ["γ=0.5", "γ=0.99", "γ=1.0"],
            [0.0, 0.0, 0.0],
            bar_color=VALUE_COLOR,
            label_font_size=22,
            value_font_size=22,
            accent=VALUE_COLOR,
        )
        self.place_mid_right_panel(self.gamma_chart)
        # Gamma chart is PRIMARY; gt_panel dims to SECONDARY (choreo §3 P13, §2 focus rule)
        self.play(
            FadeIn(self.gamma_chart),
            self.gt_panel.animate.set_opacity(OPACITY_SECONDARY),
            run_time=0.8,
        )
        self.gamma_chart.update_bars(self, [0.03125, 0.9509900499, 1.0])
        self.gamma_title = Text("discount sweep", font_size=22, color=VALUE_COLOR)
        self.gamma_title.next_to(self.gamma_chart, UP, buff=0.08)
        self.play(FadeIn(self.gamma_title), run_time=0.4)
        trace_vector(self, self.gamma_title, self.gt_panel[3], color=VALUE_COLOR)
        cross_highlight_pair(self, self.gt_panel[3], self.gamma_chart, primary_color=VALUE_COLOR, secondary_color=VALUE_COLOR)
        self._swap_caption("With γ=0.5, a reward five steps away is worth 3 cents. With γ=1.0, it is worth the full dollar.")
        self.wait(2.0)
        self._swap_caption("FrozenLake terminates, so γ=1 is valid here. For tasks that run forever, γ<1 is required.")
        self.ingestion_wait(2.5)
        self.hold_until(887.1)

    def _phase_s4_p14_recursion(self) -> None:
        self.mark_phase("seg4_recursion")
        # gamma_chart/title dim to SECONDARY (remain as context per choreo §4);
        # gt_panel restores to PRIMARY for the derivation morph (choreo §3 P14);
        # grid/accumulator/trail/agent exit (not needed for recursion derivation)
        self.play(
            FadeOut(self.grid),
            self.gamma_chart.animate.set_opacity(OPACITY_SECONDARY),
            self.gamma_title.animate.set_opacity(OPACITY_SECONDARY),
            self.gt_panel.animate.set_opacity(OPACITY_PRIMARY),
            FadeOut(self.accumulator),
            FadeOut(self.return_trail),
            FadeOut(self.agent),
            run_time=1.0,
        )
        intermediate = MathTex(
            "G_t", "=",
            "R_{t+1}", "+",
            "\\gamma", "\\bigl(",
            "R_{t+2}", "+", "\\gamma", "R_{t+3}", "+", "\\cdots",
            "\\bigr)",
            font_size=40,
        )
        for idx in (0, 4, 8):
            intermediate[idx].set_color(VALUE_COLOR)
        for idx in (2, 6, 9):
            intermediate[idx].set_color(REWARD_COLOR)
        intermediate.move_to(ORIGIN)
        # DERIVE step 1 — factor γ out of the tail (intermediate factored form)
        self.play(TransformMatchingTex(self.gt_panel, intermediate), run_time=2.0)
        self.ingestion_wait(1.5)  # absorb intermediate step: G_t = R_{t+1} + γ(R_{t+2}+...) (§18)
        # DERIVE step 2 — recognise the tail as G_{t+1} → return recursion
        self.gt_recursive = self._color_gt_recursive(
            MathTex("G_t", "=", "R_{t+1}", "+", "\\gamma", "G_{t+1}", font_size=48)
        )
        self.gt_recursive.move_to(ORIGIN)
        self.play(TransformMatchingTex(intermediate, self.gt_recursive), run_time=2.0)
        self.ingestion_wait(2.5)
        self._swap_caption("Factor out γ from the tail, and the entire future collapses into one term. This is the return recursion.")
        self.wait(2.0)
        self._swap_caption("We will see this identity again in the next video.")
        self.ingestion_wait(2.5)
        self.hold_until(953.2)

    def _phase_s4_p15_hold(self) -> None:
        self.mark_phase("seg4_hold_frame")
        self.grid = self._make_grid(scale=0.82, labels=True)
        self.grid.move_to(ORIGIN + DOWN * 0.05)
        self.grid.set_opacity(OPACITY_SECONDARY)
        # Anchor gt_recursive to place_left_panel position + relative UP offset (§4)
        _rec_anchor = self.gt_recursive.copy()
        self.place_left_panel(_rec_anchor)
        _rec_anchor.shift(UP * 0.85)
        self.smooth_move_to(self.gt_recursive, _rec_anchor.get_center(), run_time=1.2)
        self.play(
            self.gt_recursive.animate.set_opacity(OPACITY_SECONDARY),
            FadeIn(self.grid),
            run_time=1.0,
        )
        self._swap_caption("A Markov Decision Process. From any state and action, p tells you where you land and what reward you get.")
        self.wait(5.0)
        self._swap_caption("Next: we give the agent a strategy for choosing actions, and ask what each state is worth under that strategy.")
        self.wait(8.0)
        self.hold_until(1014.0)
