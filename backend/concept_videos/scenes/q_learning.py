from manim import *

from backend.concept_videos.scenes.helpers import (
    BaseConceptScene,
    StatefulHighlighter,
    cliffwalking_panel,
    code_panel,
    equation_panel,
    note_stack,
    panel,
)


class QLearningConcept(BaseConceptScene):
    def construct(self):
        self.show_header(
            "Q-Learning",
            "CliffWalking transition, greedy bootstrap, and one numerical TD update",
        )

        env_card = cliffwalking_panel(
            title="Agent Transition",
            caption="Sample one transition.\nTarget still uses the greedy next value.",
            accent="#38BDF8",
        )
        env_card.scale(0.78)
        self.place_left_panel(env_card)

        equation_card = equation_panel(
            "TD Target",
            r"Q(s,a)\leftarrow Q(s,a)+\alpha\left[r+\gamma\max_{a'}Q(s',a')-Q(s,a)\right]",
            [
                "The max term ignores the sampled next action.",
                "It asks only for the best next-state estimate.",
            ],
            accent="#FACC15",
            width=5.4,
        )
        self.place_top_right_panel(equation_card)

        numeric_lines = note_stack(
            [
                "best_next_value = max Q(4, ·) = 3.00",
                "td_target = 2.00 + 0.50 * 3.00 = 3.50",
                "Q(0,1) <- 0.00 + 0.50 * (3.50 - 0.00)",
                "Q(0,1) = 1.75",
            ],
            font_size=22,
            color=WHITE,
        )
        numeric_lines.set_opacity(0.35)

        numeric_card = panel(
            "Numerical Update",
            numeric_lines,
            "#34D399",
            width=5.4,
        )
        self.place_mid_right_panel(numeric_card)

        code_card = code_panel(
            [
                "best_next_value = max(Q[next_state])",
                "td_target = reward + gamma * best_next_value",
                "Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])",
            ],
            width=5.4,
        ).move_to(numeric_card)

        caption = self.place_caption("Q-learning bootstraps from the best next-state action value.")

        self.play(FadeIn(env_card), FadeIn(equation_card))
        self.assimilation_wait(1.2)
        self.play(FadeIn(numeric_card))
        self.assimilation_wait(0.9)
        numeric_highlighter = StatefulHighlighter(dim_opacity=0.35, active_opacity=1.0)
        for row in numeric_lines:
            self.play(*numeric_highlighter.step(row), run_time=0.52)
            self.assimilation_wait(0.55)
        self.play(FadeIn(caption), run_time=0.45)
        self.assimilation_wait(1.3)
        self.play(
            ReplacementTransform(numeric_card, code_card),
            run_time=0.9,
        )
        self.assimilation_wait(3.0)
