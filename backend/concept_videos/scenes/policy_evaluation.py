from manim import *

from backend.concept_videos.scenes.helpers import (
    code_panel,
    environment_panel,
    equation_panel,
    BaseConceptScene,
)


class PolicyEvaluationConcept(BaseConceptScene):
    def construct(self):
        self.show_header(
            "Policy Evaluation",
            "Agent frame, Bellman expectation, and iterative code sweep",
        )

        env_card = (
            environment_panel(
                0,
                title="FrozenLake State",
                caption="We freeze one state and ask: what return should this policy expect from here?",
                badge_text="State s = 0",
            )
            .to_edge(LEFT, buff=0.45)
            .shift(DOWN * 0.1)
        )

        equation_card = (
            equation_panel(
                "Bellman Expectation",
                r"V^{\pi}(s)=\sum_a \pi(a|s)\sum_{s',r} p(s',r|s,a)\left[r+\gamma V^{\pi}(s')\right]",
                [
                    "Policy weights each action before the model branches.",
                    "Every successor contributes according to its transition probability.",
                ],
            )
            .to_edge(RIGHT, buff=0.45)
            .shift(UP * 0.6)
        )

        code_card = code_panel(
            [
                "for action, action_prob in enumerate(policy[state]):",
                "    for transition_prob, next_state, reward, done in env.P[state][action]:",
                "        new_value += action_prob * transition_prob * (reward + gamma * future)",
                "V[state] = new_value",
            ],
            width=6.0,
        ).next_to(equation_card, DOWN, buff=0.25)

        numeric = equation_panel(
            "Numerical Backup",
            r"V(0)\leftarrow 0.25(0+\gamma V(1))+0.25(0+\gamma V(4))+\cdots",
            [
                "One sweep updates every state once.",
                "Repeated sweeps continue until the values stabilize.",
            ],
            accent="#A78BFA",
            width=6.0,
        ).move_to(equation_card)

        self.play(FadeIn(env_card), FadeIn(equation_card), FadeIn(code_card))
        self.wait(0.8)
        self.play(Transform(equation_card, numeric))
        self.wait(1.0)
