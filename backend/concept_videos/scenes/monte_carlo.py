from manim import *

from backend.concept_videos.scenes.helpers import (
    BaseConceptScene,
    StatefulHighlighter,
    blackjack_panel,
    code_panel,
    equation_panel,
    note_stack,
    panel,
)


class MonteCarloConcept(BaseConceptScene):
    def construct(self):
        self.show_header(
            "First-Visit Monte Carlo",
            "Blackjack episode first, then update from the first visit return",
        )

        frames_panel = blackjack_panel(
            title="Sampled Episode",
            player_text="Player 16",
            dealer_text="Dealer 10",
            caption="Sample until terminal.\nThen compute the first-visit return.",
            accent="#34D399",
        )
        frames_panel.scale(0.80)
        self.place_left_panel(frames_panel)

        equation_card = equation_panel(
            "Discounted Return",
            r"G_t=\sum_{k=0}^{T-t-1}\gamma^kR_{t+k+1},\quad V(s)\leftarrow \mathrm{mean}(G_t)",
            [
                "Wait for the hand to end before updating.",
                "Only the first occurrence of a state gets this return.",
            ],
            accent="#FACC15",
            width=5.4,
        )
        self.place_top_right_panel(equation_card)

        return_lines = note_stack(
            [
                "terminal reward = +1",
                "G <- 1",
                "G <- -0.95 + 1 = 0.05",
                "update the first visit only",
            ],
            font_size=22,
            color=WHITE,
        )
        return_lines.set_opacity(0.35)

        return_card = panel(
            "Return Build",
            return_lines,
            "#A78BFA",
            width=5.4,
        )
        self.place_mid_right_panel(return_card)

        code_card = code_panel(
            [
                "if state in visited_states: continue",
                "G += discount * reward",
                "returns.setdefault(state, []).append(G)",
                "V[state] = sum(returns[state]) / len(returns[state])",
            ],
            width=5.9,
        ).move_to(return_card)

        caption = self.place_caption(
            "The update waits for the full Blackjack episode, then uses the first visit only."
        )

        self.play(FadeIn(frames_panel))
        self.assimilation_wait(1.2)
        self.play(FadeIn(equation_card))
        self.assimilation_wait(1.0)
        self.play(FadeIn(return_card))
        self.assimilation_wait(0.8)
        return_highlighter = StatefulHighlighter(dim_opacity=0.35, active_opacity=1.0)
        for row in return_lines:
            self.play(*return_highlighter.step(row), run_time=0.5)
            self.assimilation_wait(0.55)
        self.play(ReplacementTransform(return_card, code_card), run_time=0.9)
        self.assimilation_wait(1.1)
        self.play(FadeIn(caption), run_time=0.45)
        self.assimilation_wait(3.4)
