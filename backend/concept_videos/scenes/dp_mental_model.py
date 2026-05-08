import numpy as np
from manim import *

from backend.concept_videos.scenes.helpers import FormulaStepper, StatefulHighlighter


class DPMentalModelScene(Scene):
    BASE_COLOR = "#94A3B8"
    TEXT_COLOR = "#E2E8F0"
    EMPHASIS_COLOR = "#F59E0B"
    EDGE_GREEN = "#22C55E"
    EDGE_BLUE = "#3B82F6"
    EDGE_NEUTRAL = "#94A3B8"
    DIM_OPACITY = 0.38
    ACTIVE_OPACITY = 1.0
    NODE_RADIUS = 0.42

    def build_graph(self):
        s1_center = np.array([-1.45, 0.70, 0.0])
        s2_center = np.array([-1.45, -0.75, 0.0])
        terminal_center = np.array([0.35, -0.05, 0.0])

        self.state_s1 = Circle(
            radius=self.NODE_RADIUS, stroke_color=self.BASE_COLOR, fill_opacity=0.06
        ).move_to(s1_center)
        self.state_s2 = Circle(
            radius=self.NODE_RADIUS, stroke_color=self.BASE_COLOR, fill_opacity=0.06
        ).move_to(s2_center)
        self.state_terminal = Circle(
            radius=self.NODE_RADIUS, stroke_color=self.BASE_COLOR, fill_opacity=0.12
        ).move_to(terminal_center)

        self.text_s1 = Text("S1", font_size=28, color=self.TEXT_COLOR).move_to(self.state_s1)
        self.text_s2 = Text("S2", font_size=28, color=self.TEXT_COLOR).move_to(self.state_s2)
        self.text_terminal = Text("Terminal", font_size=21, color=self.TEXT_COLOR).move_to(
            self.state_terminal
        )

        self.edge_s1_s2 = self._arrow_between(s1_center, s2_center, self.EDGE_GREEN)
        self.edge_s1_terminal = self._arrow_between(s1_center, terminal_center, self.EDGE_BLUE)
        self.edge_s2_terminal = self._arrow_between(s2_center, terminal_center, self.EDGE_NEUTRAL)

        self.label_s1_s2 = self._edge_label(
            self.edge_s1_s2, "a, p=0.7, r=+2", side="left", color=self.EDGE_GREEN
        )
        self.label_s1_terminal = self._edge_label(
            self.edge_s1_terminal, "a, p=0.3, r=0", side="above", color=self.EDGE_BLUE
        )
        self.label_s2_terminal = self._edge_label(
            self.edge_s2_terminal, "p=1, r=+1", side="below", color=self.EDGE_NEUTRAL
        )

        self.label_s1_s2.set_opacity(0.0)
        self.label_s1_terminal.set_opacity(0.0)
        self.label_s2_terminal.set_opacity(0.0)

        self.graph_group = VGroup(
            self.state_s1,
            self.state_s2,
            self.state_terminal,
            self.text_s1,
            self.text_s2,
            self.text_terminal,
            self.edge_s1_s2,
            self.edge_s1_terminal,
            self.edge_s2_terminal,
            self.label_s1_s2,
            self.label_s1_terminal,
            self.label_s2_terminal,
        )

        self.graph_named = {
            "state_s1": self.state_s1,
            "state_s2": self.state_s2,
            "state_terminal": self.state_terminal,
            "text_s1": self.text_s1,
            "text_s2": self.text_s2,
            "text_terminal": self.text_terminal,
            "edge_s1_s2": self.edge_s1_s2,
            "edge_s1_terminal": self.edge_s1_terminal,
            "edge_s2_terminal": self.edge_s2_terminal,
            "label_s1_s2": self.label_s1_s2,
            "label_s1_terminal": self.label_s1_terminal,
            "label_s2_terminal": self.label_s2_terminal,
        }
        self.revealed_labels = set()

    def build_right_panel(self):
        self.title = Text(
            "Dynamic Programming for Finite MDPs", font_size=40, color=self.TEXT_COLOR, weight=BOLD
        ).to_edge(UP, buff=0.2)

        self.equation = MathTex(
            r"V(s)",
            r"\leftarrow",
            r"\sum_{s',r}",
            r"p(s',r \mid s,a)",
            r"\,[r + \gamma V(s')]",
            font_size=44,
            color=self.TEXT_COLOR,
        )

        self.bullet_group = VGroup(
            Text("finite MDP", font_size=23, color=self.TEXT_COLOR),
            Text("full model known", font_size=23, color=self.TEXT_COLOR),
            Text("planning, not trial-and-error", font_size=23, color=self.TEXT_COLOR),
            Text("full backup", font_size=23, color=self.TEXT_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)

        self.caption = Text(
            "DP updates values by considering all modeled outcomes.",
            font_size=29,
            color=self.TEXT_COLOR,
        ).to_edge(DOWN, buff=0.22)

        self.equation_group = VGroup(self.equation)
        self.right_panel_group = VGroup(
            self.title, self.equation_group, self.bullet_group, self.caption
        )

    def set_graph_focus(self, active_names):
        active = set(active_names)
        animations = []
        for name, mob in self.graph_named.items():
            if name.startswith("label_") and name not in self.revealed_labels:
                animations.append(mob.animate.set_opacity(0.0))
            else:
                target_opacity = self.ACTIVE_OPACITY if name in active else self.DIM_OPACITY
                animations.append(mob.animate.set_opacity(target_opacity))
        return animations

    def reset_graph_focus(self):
        animations = []
        for name, mob in self.graph_named.items():
            if name.startswith("label_") and name not in self.revealed_labels:
                animations.append(mob.animate.set_opacity(0.0))
            else:
                animations.append(mob.animate.set_opacity(self.ACTIVE_OPACITY))
        return animations

    def construct(self):
        self.camera.background_color = "#020617"
        self.build_graph()
        self.build_right_panel()

        compact_equation = self.equation.copy().scale(0.86).move_to(ORIGIN)
        self.play(Write(compact_equation), run_time=1.15)
        self.wait(0.1)

        self.equation.move_to(np.array([0.0, 2.0, 0.0]))
        self.play(
            ReplacementTransform(compact_equation, self.equation), FadeIn(self.title), run_time=0.8
        )

        block_content = VGroup(self.graph_group, self.bullet_group).arrange(
            RIGHT, buff=0.8, aligned_edge=UP
        )
        block_content.scale(0.95)
        block_content.move_to(np.array([0.0, 0.05, 0.0]))
        model_block = SurroundingRectangle(
            block_content,
            buff=0.25,
            corner_radius=0.18,
            stroke_color=self.BASE_COLOR,
            stroke_width=2.2,
        )

        sum_token = self.equation[2]
        sum_slot = sum_token.get_center().copy()
        self.play(Transform(sum_token, model_block), run_time=0.7)
        self.play(
            LaggedStart(
                FadeIn(self.graph_group),
                FadeIn(self.bullet_group),
                lag_ratio=0.25,
            ),
            run_time=0.8,
        )

        self.play(*self.set_graph_focus([]), run_time=0.4)

        self.revealed_labels.add("label_s1_s2")
        self.revealed_labels.add("label_s1_terminal")
        self.play(FadeIn(self.label_s1_s2), FadeIn(self.label_s1_terminal), run_time=0.35)

        branch_1 = VGroup(self.edge_s1_s2, self.label_s1_s2, self.state_s1, self.text_s1)
        branch_2 = VGroup(
            self.edge_s1_terminal, self.label_s1_terminal, self.state_s1, self.text_s1
        )
        branch_highlighter = StatefulHighlighter(
            dim_opacity=self.DIM_OPACITY, active_opacity=self.ACTIVE_OPACITY
        )

        contribution_stepper = FormulaStepper(
            [
                r"0.7\,[2 + \gamma V(S2)]",
                r"0.3\,[0 + \gamma V(T)]",
                r"0.7\,[2 + \gamma V(S2)] + 0.3\,[0 + \gamma V(T)]",
            ],
            font_size=36,
            color=self.TEXT_COLOR,
        )
        contribution = contribution_stepper.get()
        contribution.next_to(self.equation, DOWN, buff=0.55)

        self.play(*branch_highlighter.step(branch_1), run_time=0.45)
        self.play(FadeIn(contribution), run_time=0.35)
        self.play(Indicate(branch_1, color=self.EMPHASIS_COLOR, scale_factor=1.02), run_time=0.35)

        self.play(*branch_highlighter.step(branch_2), run_time=0.45)
        next_contribution = contribution_stepper.next()
        next_contribution.move_to(contribution)
        self.play(ReplacementTransform(contribution, next_contribution), run_time=0.45)
        contribution = next_contribution
        self.play(Indicate(branch_2, color=self.EMPHASIS_COLOR, scale_factor=1.02), run_time=0.35)

        self.revealed_labels.add("label_s2_terminal")
        self.play(FadeIn(self.label_s2_terminal), run_time=0.3)

        final_contribution = contribution_stepper.next()
        final_contribution.move_to(contribution)
        self.play(ReplacementTransform(contribution, final_contribution), run_time=0.5)
        contribution = final_contribution

        self.play(*self.reset_graph_focus(), run_time=0.4)
        self.play(
            Indicate(self.equation, color=self.EMPHASIS_COLOR, scale_factor=1.02), run_time=0.45
        )

        sum_token_target = MathTex(r"\sum_{s',r}", font_size=44, color=self.TEXT_COLOR).move_to(
            sum_slot
        )
        self.play(
            FadeOut(block_content),
            FadeOut(contribution),
            Transform(sum_token, sum_token_target),
            run_time=0.7,
        )

        self.play(FadeIn(self.caption), run_time=0.4)
        self.wait(0.75)

    def _arrow_between(self, start_center, end_center, color):
        direction = end_center - start_center
        unit = direction / np.linalg.norm(direction)
        return Arrow(
            start=start_center + unit * self.NODE_RADIUS,
            end=end_center - unit * self.NODE_RADIUS,
            buff=0.0,
            stroke_width=2.8,
            max_tip_length_to_length_ratio=0.14,
            color=color,
        )

    def _edge_label(self, edge, text, *, side, color):
        start = edge.get_start()
        end = edge.get_end()
        direction = end - start
        perp = np.array([-direction[1], direction[0], 0.0])
        perp = perp / np.linalg.norm(perp)
        offset = 0.34
        if side == "above":
            anchor = (start + end) / 2 + perp * offset
        elif side == "below":
            anchor = (start + end) / 2 - perp * offset
        else:
            anchor = (start + end) / 2 - perp * offset
        return Text(text, font_size=20, color=color).move_to(anchor)
