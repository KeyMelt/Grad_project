from manim import *

from backend.concept_videos.scenes.helpers import (
    BaseConceptScene,
    StatefulHighlighter,
    code_panel,
    environment_panel,
    equation_panel,
    note_stack,
    panel,
)


class ValueIterationConcept(BaseConceptScene):
    def construct(self):
        self.show_header(
            "Value Iteration",
            "Keep the best action backup instead of averaging under a fixed policy",
        )

        env_card = environment_panel(
            4,
            title="FrozenLake State",
            caption="Freeze one state.\nCompare every action backup.\nKeep the largest one.",
            badge_text="State s = 4",
            accent="#38BDF8",
        )
        env_card.scale(0.78)
        self.place_left_panel(env_card)

        equation_card = equation_panel(
            "Bellman Optimality",
            r"V_*(s)=\max_a\sum_{s',r} p(s',r|s,a)\left[r+\gamma V_*(s')\right]",
            [
                "Build one expected return for each action.",
                "The largest one becomes the next state value.",
            ],
            accent="#F97316",
            width=5.3,
        )
        self.place_top_right_panel(equation_card)

        action_lines = note_stack(
            [
                "Left  -> 0.14",
                "Down  -> 0.09",
                "Right -> 0.28",
                "Up    -> 0.17",
            ],
            font_size=24,
            color=WHITE,
        )
        action_lines.set_opacity(0.35)

        action_values = panel(
            "Action Backups",
            action_lines,
            "#34D399",
            width=5.2,
        )
        self.place_mid_right_panel(action_values)

        code_card = code_panel(
            [
                "for action in range(action_count):",
                "    action_value += transition_prob * (reward + gamma * future)",
                "action_values.append(action_value)",
                "V[state] = max(action_values)",
            ],
            width=5.2,
        ).move_to(action_values)

        caption = self.place_caption(
            "Compare action backups one at a time, then keep the largest one."
        )

        self.play(FadeIn(env_card), FadeIn(equation_card))
        self.assimilation_wait(1.2)
        self.play(FadeIn(action_values))
        self.assimilation_wait(1.0)
        row_highlighter = StatefulHighlighter(dim_opacity=0.35, active_opacity=1.0)
        for row in action_lines:
            self.play(*row_highlighter.step(row), run_time=0.5)
            self.assimilation_wait(0.55)
        self.play(
            action_lines[2].animate.set_color("#34D399"),
            Circumscribe(action_lines[2], color="#F59E0B", buff=0.12),
            FadeIn(caption),
            run_time=0.8,
        )
        self.assimilation_wait(1.3)
        self.play(
            ReplacementTransform(action_values, code_card),
            run_time=0.9,
        )
        self.assimilation_wait(3.2)
