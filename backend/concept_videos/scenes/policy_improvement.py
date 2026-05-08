import numpy as np
from manim import *

from backend.concept_videos.scenes.helpers import StatefulHighlighter, frozenlake_frame, pill


class PolicyImprovementConcept(Scene):
    BASE_COLOR = "#94A3B8"
    TEXT_COLOR = "#E2E8F0"
    EMPHASIS_COLOR = "#F59E0B"
    ACTION_COLOR = "#22C55E"
    DIM_OPACITY = 0.35
    ACTIVE_OPACITY = 1.0

    def construct(self):
        self.camera.background_color = "#020617"

        equation = MathTex(
            r"\pi'(s)",
            r"=",
            r"\arg\max_a",
            r"q(s,a)",
            font_size=46,
            color=self.TEXT_COLOR,
        )
        self.play(Write(equation), run_time=1.4)
        self.wait(0.25)

        equation.generate_target()
        equation.target.to_edge(UP, buff=0.55)
        self.play(MoveToTarget(equation), run_time=0.8)

        title = Text(
            "Policy Improvement",
            font_size=34,
            color=self.TEXT_COLOR,
            weight=BOLD,
        ).next_to(equation, DOWN, buff=0.18)
        self.play(FadeIn(title, shift=UP * 0.12), run_time=0.45)

        environment = Group(
            pill("State s = 4", self.ACTION_COLOR),
            frozenlake_frame(4, height=2.7),
            Text(
                "Keep one state fixed while each action is backed up.",
                font_size=22,
                color=GREY_A,
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        environment.move_to(np.array([-3.55, -0.2, 0.0]))

        backup_equation = MathTex(
            r"q(s,a)",
            r"=",
            r"\sum_{s',r}",
            r"p(s',r\mid s,a)",
            r"\left[r+\gamma V(s')\right]",
            font_size=40,
            color=self.TEXT_COLOR,
        )
        backup_equation.scale_to_fit_width(5.8)

        action_rows = VGroup(
            Text("Left  -> 0.18", font_size=26, color=self.TEXT_COLOR),
            Text("Down  -> 0.31", font_size=26, color=self.TEXT_COLOR),
            Text("Right -> 0.24", font_size=26, color=self.TEXT_COLOR),
            Text("Up    -> 0.12", font_size=26, color=self.TEXT_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        action_rows.set_opacity(self.DIM_OPACITY)

        action_block = VGroup(backup_equation, action_rows).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.3,
        )
        action_box = SurroundingRectangle(
            action_block,
            buff=0.25,
            corner_radius=0.18,
            stroke_color=self.BASE_COLOR,
            stroke_width=2.0,
        )
        action_group = VGroup(action_box, action_block)
        action_group.move_to(np.array([2.15, -0.1, 0.0]))

        q_token = equation[3]
        q_slot = q_token.get_center().copy()
        self.play(Transform(q_token, action_box), run_time=0.8)
        self.play(FadeIn(environment), FadeIn(backup_equation), FadeIn(action_rows), run_time=0.85)

        highlighter = StatefulHighlighter(
            dim_opacity=self.DIM_OPACITY,
            active_opacity=self.ACTIVE_OPACITY,
        )
        for row in action_rows:
            self.play(*highlighter.step(row), run_time=0.45)
            self.wait(0.12)

        selected = Text(
            "Greedy policy row: [0, 1, 0, 0]",
            font_size=28,
            color=self.ACTION_COLOR,
            weight=BOLD,
        )
        selected.next_to(action_block, DOWN, buff=0.32, aligned_edge=LEFT)
        caption = Text(
            "The largest Bellman-style backup becomes the policy choice.",
            font_size=24,
            color=GREY_B,
        ).to_edge(DOWN, buff=0.22)

        self.play(
            action_rows[1].animate.set_color(self.ACTION_COLOR),
            Circumscribe(action_rows[1], color=self.EMPHASIS_COLOR, buff=0.12),
            run_time=0.7,
        )
        self.play(FadeIn(selected, shift=UP * 0.12), FadeIn(caption), run_time=0.55)

        q_target = MathTex(r"q(s,a)", font_size=46, color=self.TEXT_COLOR).move_to(q_slot)
        self.play(
            FadeOut(action_rows, shift=DOWN * 0.06),
            FadeOut(backup_equation, shift=DOWN * 0.06),
            FadeOut(action_box),
            Transform(q_token, q_target),
            run_time=0.8,
        )
        self.wait(1.5)
