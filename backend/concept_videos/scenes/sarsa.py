import numpy as np
from manim import *

from backend.concept_videos.scenes.helpers import (
    BaseConceptScene,
    StatefulHighlighter,
    cliffwalking_panel,
    code_panel,
    pill,
)


class SARSAConcept(BaseConceptScene):
    BASE_COLOR = "#94A3B8"
    TEXT_COLOR = "#E2E8F0"
    EMPHASIS_COLOR = "#F59E0B"
    ACTION_COLOR = "#38BDF8"
    DIM_OPACITY = 0.35
    ACTIVE_OPACITY = 1.0

    def construct(self):
        equation = MathTex(
            r"Q(s,a)",
            r"\leftarrow",
            r"Q(s,a)+\alpha\left[r+\gamma",
            r"Q(s',a')",
            r"-Q(s,a)\right]",
            font_size=38,
            color=self.TEXT_COLOR,
        )
        self.play(Write(equation), run_time=1.5)
        self.assimilation_wait(0.6)

        equation.generate_target()
        equation.target.move_to(np.array([0.0, 2.75, 0.0]))
        self.play(MoveToTarget(equation), run_time=0.9)

        title = Text(
            "SARSA",
            font_size=34,
            color=self.TEXT_COLOR,
            weight=BOLD,
        ).next_to(equation, DOWN, buff=0.16)
        self.play(FadeIn(title, shift=UP * 0.12), run_time=0.45)

        env_card = cliffwalking_panel(
            title="Sampled Transition",
            caption="Sample one transition.\nUse the next sampled action in the target.",
            accent=self.ACTION_COLOR,
        )
        env_card.scale(0.72)
        self.place_left_panel(env_card)

        action_block = VGroup(
            pill("Next action a' is sampled", self.ACTION_COLOR),
            Text("sampled a' = Right", font_size=28, color=self.TEXT_COLOR, weight=BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        action_box = SurroundingRectangle(
            action_block,
            buff=0.25,
            corner_radius=0.18,
            stroke_color=self.BASE_COLOR,
            stroke_width=2.0,
        )
        action_group = Group(action_box, action_block)
        self.place_mid_right_panel(action_group)
        action_group.shift(UP * 0.28)

        numeric_lines = VGroup(
            Text("sampled next action = Right", font_size=26, color=self.TEXT_COLOR),
            Text("td_target = 0.00 + 0.95 * Q(4, Right)", font_size=26, color=self.TEXT_COLOR),
            Text("Q(0, Down) <- 0.10 + 0.10 * (0.57 - 0.10)", font_size=26, color=self.TEXT_COLOR),
            Text("Q(0, Down) = 0.147", font_size=26, color=self.ACTION_COLOR, weight=BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        numeric_box = SurroundingRectangle(
            numeric_lines,
            buff=0.24,
            corner_radius=0.18,
            stroke_color=self.BASE_COLOR,
            stroke_width=2.0,
        )
        numeric_group = VGroup(numeric_box, numeric_lines)
        self.place_bottom_right_panel(numeric_group)
        numeric_group.shift(DOWN * 0.32)
        numeric_lines.set_opacity(self.DIM_OPACITY)

        code_card = code_panel(
            [
                "next_action = behavior_policy(next_state)",
                "bootstrap = Q[next_state][next_action]",
                "td_target = reward + gamma * bootstrap",
                "Q[state][action] += alpha * (td_target - Q[state][action])",
            ],
            width=5.1,
        ).move_to(numeric_group)

        next_token = equation[3]
        next_slot = next_token.get_center().copy()
        self.play(FadeIn(env_card), run_time=0.75)
        self.assimilation_wait(1.0)
        self.play(Transform(next_token, action_box), run_time=0.8)
        self.play(FadeIn(action_block), FadeIn(numeric_group), run_time=0.85)
        self.assimilation_wait(0.9)

        self.play(
            Circumscribe(action_block[1], color=self.EMPHASIS_COLOR, buff=0.12),
            run_time=0.6,
        )
        self.assimilation_wait(0.8)

        numeric_highlighter = StatefulHighlighter(
            dim_opacity=self.DIM_OPACITY,
            active_opacity=self.ACTIVE_OPACITY,
        )
        for row in numeric_lines:
            self.play(*numeric_highlighter.step(row), run_time=0.48)
            self.assimilation_wait(0.55)

        caption = self.place_caption(
            "SARSA bootstraps from the next action the behavior policy actually chose."
        )
        self.play(FadeIn(caption), run_time=0.45)
        self.assimilation_wait(1.2)
        self.play(
            FadeOut(numeric_group, shift=DOWN * 0.08),
            FadeIn(code_card, shift=UP * 0.08),
            run_time=0.9,
        )
        self.assimilation_wait(1.2)

        next_target = MathTex(r"Q(s',a')", font_size=42, color=self.TEXT_COLOR).move_to(next_slot)
        self.play(
            FadeOut(action_block, shift=DOWN * 0.06),
            FadeOut(action_box),
            Transform(next_token, next_target),
            run_time=0.8,
        )
        self.assimilation_wait(2.8)
