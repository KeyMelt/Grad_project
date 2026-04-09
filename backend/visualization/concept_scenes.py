from pathlib import Path

from manim import *
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
FRAME_DIR = ROOT / "frontend" / "assets" / "lesson_media" / "frozenlake"


def frozenlake_frame(state: int, height: float = 2.8) -> Mobject:
    path = FRAME_DIR / f"state_{state:02d}.png"
    if path.exists():
        image = ImageMobject(str(path))
        image.scale_to_fit_height(height)
        return image

    fallback = RoundedRectangle(
        corner_radius=0.16,
        width=3.0,
        height=height,
        stroke_color=BLUE_E,
        fill_color="#0F172A",
        fill_opacity=1.0,
    )
    label = Text(f"State {state}", font_size=24).move_to(fallback.get_center())
    return VGroup(fallback, label)


def pill(label: str, color: str) -> VGroup:
    text = Text(label, font_size=22, color=color, weight=BOLD)
    box = RoundedRectangle(
        corner_radius=0.16,
        width=text.width + 0.5,
        height=text.height + 0.24,
        stroke_color=color,
        fill_color=color,
        fill_opacity=0.08,
    )
    text.move_to(box.get_center())
    return VGroup(box, text)


def panel(title: str, body: Mobject, color: str, width: float = 5.5) -> VGroup:
    heading = Text(title, font_size=26, color=color, weight=BOLD)
    content = Group(heading, body).arrange(
        DOWN,
        aligned_edge=LEFT,
        buff=0.22,
    )
    card = RoundedRectangle(
        corner_radius=0.18,
        width=max(width, content.width + 0.45),
        height=max(2.1, content.height + 0.45),
        stroke_color=color,
        fill_color="#0F172A",
        fill_opacity=0.94,
    )
    content.move_to(card.get_center())
    return Group(card, content)


def code_panel(lines: list[str], width: float = 5.6) -> VGroup:
    rendered_lines = VGroup(
        *[
            Text(line, font_size=20, font="Menlo", color=GREY_A)
            for line in lines
        ]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    return panel("Code Trace", rendered_lines, "#60A5FA", width=width)


def note_stack(lines: list[str], font_size: int = 22, color=GREY_A) -> VGroup:
    return VGroup(
        *[
            Text(line, font_size=font_size, color=color)
            for line in lines
        ]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)


def environment_panel(
    state: int,
    *,
    title: str,
    caption: str,
    badge_text: str,
    accent: str = "#34D399",
) -> VGroup:
    frame = frozenlake_frame(state)
    badge = pill(badge_text, accent)
    caption_text = Text(
        caption,
        font_size=22,
        color=GREY_A,
        line_spacing=0.7,
    )
    stack = Group(badge, frame, caption_text).arrange(
        DOWN,
        aligned_edge=LEFT,
        buff=0.22,
    )
    return panel(title, stack, accent, width=4.4)


def equation_panel(
    title: str,
    equation: str,
    notes: list[str],
    *,
    accent: str = "#FACC15",
    width: float = 6.0,
) -> VGroup:
    eq = MathTex(equation, font_size=34, color=WHITE)
    eq.scale_to_fit_width(width - 0.7)
    stack = VGroup(eq, note_stack(notes, font_size=21)).arrange(
        DOWN,
        aligned_edge=LEFT,
        buff=0.28,
    )
    return panel(title, stack, accent, width=width)


class BaseConceptScene(Scene):
    def setup(self):
        self.camera.background_color = "#020617"

    def show_header(self, title: str, subtitle: str):
        title_text = Text(title, font_size=38, weight=BOLD)
        subtitle_text = Text(
            subtitle,
            font_size=24,
            color=GREY_B,
        ).next_to(title_text, DOWN, buff=0.16)
        header = VGroup(title_text, subtitle_text).to_edge(UP, buff=0.45)
        self.play(LaggedStart(FadeIn(title_text, shift=UP * 0.2), FadeIn(subtitle_text), lag_ratio=0.18))
        return header


class PolicyEvaluationConcept(BaseConceptScene):
    def construct(self):
        self.show_header(
            "Policy Evaluation",
            "Agent frame, Bellman expectation, and iterative code sweep",
        )

        env_card = environment_panel(
            0,
            title="FrozenLake State",
            caption="We freeze one state and ask: what return should this policy expect from here?",
            badge_text="State s = 0",
        ).to_edge(LEFT, buff=0.45).shift(DOWN * 0.1)

        equation_card = equation_panel(
            "Bellman Expectation",
            r"V^{\pi}(s)=\sum_a \pi(a|s)\sum_{s',r} p(s',r|s,a)\left[r+\gamma V^{\pi}(s')\right]",
            [
                "Policy weights each action before the model branches.",
                "Every successor contributes according to its transition probability.",
            ],
        ).to_edge(RIGHT, buff=0.45).shift(UP * 0.6)

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


class ValueIterationConcept(BaseConceptScene):
    def construct(self):
        self.show_header(
            "Value Iteration",
            "Keep the best action backup instead of averaging under a fixed policy",
        )

        env_card = environment_panel(
            4,
            title="FrozenLake State",
            caption="For the same state we compare every action backup and keep the largest one.",
            badge_text="State s = 4",
            accent="#38BDF8",
        ).to_edge(LEFT, buff=0.45)

        equation_card = equation_panel(
            "Bellman Optimality",
            r"V_*(s)=\max_a\sum_{s',r} p(s',r|s,a)\left[r+\gamma V_*(s')\right]",
            [
                "Each action produces its own expected return.",
                "The maximum action value becomes the next state value.",
            ],
            accent="#F97316",
        ).to_edge(RIGHT, buff=0.45).shift(UP * 0.6)

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
            width=4.7,
        ).next_to(equation_card, DOWN, buff=0.25)

        code_card = code_panel(
            [
                "for action in range(action_count):",
                "    action_value += transition_prob * (reward + gamma * future)",
                "action_values.append(action_value)",
                "V[state] = max(action_values)",
            ],
            width=5.6,
        ).move_to(Group(equation_card, action_values).get_center())

        caption = Text(
            "Compare action backups one at a time, then keep the largest one.",
            font_size=23,
            color=GREY_B,
        ).to_edge(DOWN, buff=0.22)

        self.play(FadeIn(env_card), FadeIn(equation_card))
        self.play(FadeIn(action_values))
        row_highlighter = StatefulHighlighter(dim_opacity=0.35, active_opacity=1.0)
        for row in action_lines:
            self.play(*row_highlighter.step(row), run_time=0.38)
        self.play(
            action_lines[2].animate.set_color("#34D399"),
            Circumscribe(action_lines[2], color="#F59E0B", buff=0.12),
            FadeIn(caption),
            run_time=0.65,
        )
        self.play(
            AnimationGroup(
                FadeOut(action_values, shift=DOWN * 0.1),
                FadeIn(code_card, shift=UP * 0.1),
                lag_ratio=0.12,
            )
        )
        self.wait(0.8)


class MonteCarloConcept(BaseConceptScene):
    def construct(self):
        self.show_header(
            "First-Visit Monte Carlo",
            "Sample a full episode first, then update from the first visit of each state",
        )

        frames = Group(
            frozenlake_frame(0, height=2.2),
            Arrow(ORIGIN, RIGHT * 0.8, buff=0.2),
            frozenlake_frame(4, height=2.2),
            Arrow(ORIGIN, RIGHT * 0.8, buff=0.2),
            frozenlake_frame(8, height=2.2),
        ).arrange(RIGHT, buff=0.2)
        frames_panel = panel(
            "Sampled Episode",
            Group(
                pill("S0 -> S1 -> S2", "#34D399"),
                frames,
                Text(
                    "The environment is sampled forward before any value update happens.",
                    font_size=21,
                    color=GREY_A,
                ),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.2),
            "#34D399",
            width=6.2,
        ).to_edge(LEFT, buff=0.35).shift(DOWN * 0.1)

        equation_card = equation_panel(
            "Discounted Return",
            r"G_t=\sum_{k=0}^{T-t-1}\gamma^kR_{t+k+1},\quad V(s)\leftarrow \mathrm{mean}(G_t)",
            [
                "When a state appears again later in the episode, we skip it.",
                "Only the first occurrence receives the newly computed return.",
            ],
            accent="#FACC15",
            width=6.1,
        ).to_edge(RIGHT, buff=0.45).shift(UP * 0.5)

        code_card = code_panel(
            [
                "if state in visited_states: continue",
                "G += discount * reward",
                "returns[state].append(G)",
                "V[state] = sum(returns[state]) / len(returns[state])",
            ],
            width=6.1,
        ).next_to(equation_card, DOWN, buff=0.25)

        caption = Text(
            "The update waits for the full episode, then uses the first visit only.",
            font_size=23,
            color=GREY_B,
        ).to_edge(DOWN, buff=0.22)

        self.play(FadeIn(frames_panel))
        self.play(Circumscribe(frames, color="#F59E0B", buff=0.12), run_time=0.7)
        self.play(FadeIn(equation_card))
        self.play(FadeIn(code_card))
        self.play(FadeIn(caption), run_time=0.45)
        self.wait(0.9)


class QLearningConcept(BaseConceptScene):
    def construct(self):
        self.show_header(
            "Q-Learning",
            "One sampled transition, one highlighted code line, one numerical TD update",
        )

        movement = Group(
            frozenlake_frame(0, height=2.5),
            Arrow(ORIGIN, RIGHT * 0.8, buff=0.15, color=BLUE_B),
            frozenlake_frame(4, height=2.5),
        ).arrange(RIGHT, buff=0.15)
        env_card = panel(
            "Agent Transition",
            Group(
                pill("s=0, a=Down, s'=4", "#38BDF8"),
                movement,
                Text(
                    "The environment supplies the transition that triggers the TD update.",
                    font_size=21,
                    color=GREY_A,
                ),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.18),
            "#38BDF8",
            width=6.0,
        ).to_edge(LEFT, buff=0.35).shift(DOWN * 0.1)

        equation_card = equation_panel(
            "TD Target",
            r"Q(s,a)\leftarrow Q(s,a)+\alpha\left[r+\gamma\max_{a'}Q(s',a')-Q(s,a)\right]",
            [
                "Bootstrap from the best action in the next state.",
                "Alpha determines how much of the TD error is applied.",
            ],
            accent="#FACC15",
            width=6.1,
        ).to_edge(RIGHT, buff=0.45).shift(UP * 0.5)

        numeric_lines = note_stack(
            [
                "best_next_value = 3.00",
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
            width=6.1,
        ).next_to(equation_card, DOWN, buff=0.25)

        code_card = code_panel(
            [
                "best_next_value = max(Q[next_state])",
                "td_target = reward + gamma * best_next_value",
                "Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])",
            ],
            width=6.1,
        ).move_to(numeric_card)

        caption = Text(
            "Q-learning bootstraps from the best next-state action value.",
            font_size=23,
            color=GREY_B,
        ).to_edge(DOWN, buff=0.22)

        self.play(FadeIn(env_card), FadeIn(equation_card))
        self.play(FadeIn(numeric_card))
        numeric_highlighter = StatefulHighlighter(dim_opacity=0.35, active_opacity=1.0)
        for row in numeric_lines:
            self.play(*numeric_highlighter.step(row), run_time=0.4)
        self.play(FadeIn(caption), run_time=0.45)
        self.play(
            AnimationGroup(
                FadeOut(numeric_card, shift=DOWN * 0.1),
                FadeIn(code_card, shift=UP * 0.1),
                lag_ratio=0.12,
            )
        )
        self.wait(0.8)


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


class SARSAConcept(Scene):
    BASE_COLOR = "#94A3B8"
    TEXT_COLOR = "#E2E8F0"
    EMPHASIS_COLOR = "#F59E0B"
    ACTION_COLOR = "#38BDF8"
    DIM_OPACITY = 0.35
    ACTIVE_OPACITY = 1.0

    def construct(self):
        self.camera.background_color = "#020617"

        equation = MathTex(
            r"Q(s,a)",
            r"\leftarrow",
            r"Q(s,a)+\alpha\left[r+\gamma",
            r"Q(s',a')",
            r"-Q(s,a)\right]",
            font_size=42,
            color=self.TEXT_COLOR,
        )
        self.play(Write(equation), run_time=1.5)
        self.wait(0.25)

        equation.generate_target()
        equation.target.to_edge(UP, buff=0.55)
        self.play(MoveToTarget(equation), run_time=0.8)

        title = Text(
            "SARSA",
            font_size=34,
            color=self.TEXT_COLOR,
            weight=BOLD,
        ).next_to(equation, DOWN, buff=0.18)
        self.play(FadeIn(title, shift=UP * 0.12), run_time=0.45)

        transition_strip = Group(
            frozenlake_frame(0, height=2.2),
            Arrow(ORIGIN, RIGHT * 0.75, buff=0.12, color=self.ACTION_COLOR),
            frozenlake_frame(4, height=2.2),
        ).arrange(RIGHT, buff=0.18)
        sampled_actions = VGroup(
            Text("Left  -> 0.11", font_size=25, color=self.TEXT_COLOR),
            Text("Down  -> 0.19", font_size=25, color=self.TEXT_COLOR),
            Text("Right -> 0.60", font_size=25, color=self.TEXT_COLOR),
            Text("Up    -> 0.08", font_size=25, color=self.TEXT_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        sampled_actions.set_opacity(self.DIM_OPACITY)

        next_action_block = Group(
            pill("Next action a' is sampled", self.ACTION_COLOR),
            transition_strip,
            sampled_actions,
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        next_action_box = SurroundingRectangle(
            next_action_block,
            buff=0.25,
            corner_radius=0.18,
            stroke_color=self.BASE_COLOR,
            stroke_width=2.0,
        )
        next_action_group = Group(next_action_box, next_action_block)
        next_action_group.move_to(np.array([-2.9, -0.2, 0.0]))

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
        numeric_group.move_to(np.array([3.0, -0.15, 0.0]))
        numeric_lines.set_opacity(self.DIM_OPACITY)

        next_token = equation[3]
        next_slot = next_token.get_center().copy()
        self.play(Transform(next_token, next_action_box), run_time=0.8)
        self.play(FadeIn(next_action_block), FadeIn(numeric_group), run_time=0.85)

        action_highlighter = StatefulHighlighter(
            dim_opacity=self.DIM_OPACITY,
            active_opacity=self.ACTIVE_OPACITY,
        )
        self.play(*action_highlighter.step(sampled_actions[2]), run_time=0.5)
        self.play(
            Circumscribe(sampled_actions[2], color=self.EMPHASIS_COLOR, buff=0.12),
            run_time=0.6,
        )

        numeric_highlighter = StatefulHighlighter(
            dim_opacity=self.DIM_OPACITY,
            active_opacity=self.ACTIVE_OPACITY,
        )
        for row in numeric_lines:
            self.play(*numeric_highlighter.step(row), run_time=0.45)
            self.wait(0.1)

        caption = Text(
            "SARSA bootstraps from the next action the behavior policy actually chose.",
            font_size=23,
            color=GREY_B,
        ).to_edge(DOWN, buff=0.22)
        self.play(FadeIn(caption), run_time=0.45)

        next_target = MathTex(r"Q(s',a')", font_size=42, color=self.TEXT_COLOR).move_to(next_slot)
        self.play(
            FadeOut(next_action_block, shift=DOWN * 0.06),
            FadeOut(next_action_box),
            Transform(next_token, next_target),
            run_time=0.8,
        )
        self.wait(1.5)


class StatefulHighlighter:
    """Stateful one-at-a-time opacity highlighter for branch groups."""

    def __init__(self, dim_opacity=0.35, active_opacity=1.0):
        self.prev = None
        self.dim_opacity = dim_opacity
        self.active_opacity = active_opacity

    def step(self, mob):
        animations = []
        if self.prev is not None:
            animations.append(self.prev.animate.set_opacity(self.dim_opacity))
        animations.append(mob.animate.set_opacity(self.active_opacity))
        self.prev = mob
        return animations


class FormulaStepper:
    """Stepwise formula updater using ReplacementTransform."""

    def __init__(self, formulas, *, font_size=36, color=WHITE):
        self.formulas = formulas
        self.font_size = font_size
        self.color = color
        self.current = 0
        self.formula = self._make_formula(0)

    def _make_formula(self, index):
        return MathTex(self.formulas[index], font_size=self.font_size, color=self.color)

    def get(self):
        return self.formula

    def next(self):
        self.current += 1
        updated = self._make_formula(self.current)
        updated.move_to(self.formula)
        self.formula = updated
        return updated


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

        self.state_s1 = Circle(radius=self.NODE_RADIUS, stroke_color=self.BASE_COLOR, fill_opacity=0.06).move_to(s1_center)
        self.state_s2 = Circle(radius=self.NODE_RADIUS, stroke_color=self.BASE_COLOR, fill_opacity=0.06).move_to(s2_center)
        self.state_terminal = Circle(radius=self.NODE_RADIUS, stroke_color=self.BASE_COLOR, fill_opacity=0.12).move_to(terminal_center)

        self.text_s1 = Text("S1", font_size=28, color=self.TEXT_COLOR).move_to(self.state_s1)
        self.text_s2 = Text("S2", font_size=28, color=self.TEXT_COLOR).move_to(self.state_s2)
        self.text_terminal = Text("Terminal", font_size=21, color=self.TEXT_COLOR).move_to(self.state_terminal)

        self.edge_s1_s2 = self._arrow_between(s1_center, s2_center, self.EDGE_GREEN)
        self.edge_s1_terminal = self._arrow_between(s1_center, terminal_center, self.EDGE_BLUE)
        self.edge_s2_terminal = self._arrow_between(s2_center, terminal_center, self.EDGE_NEUTRAL)

        self.label_s1_s2 = self._edge_label(self.edge_s1_s2, "a, p=0.7, r=+2", side="left", color=self.EDGE_GREEN)
        self.label_s1_terminal = self._edge_label(self.edge_s1_terminal, "a, p=0.3, r=0", side="above", color=self.EDGE_BLUE)
        self.label_s2_terminal = self._edge_label(self.edge_s2_terminal, "p=1, r=+1", side="below", color=self.EDGE_NEUTRAL)

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
        self.title = Text("Dynamic Programming for Finite MDPs", font_size=40, color=self.TEXT_COLOR, weight=BOLD).to_edge(UP, buff=0.2)

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
        self.right_panel_group = VGroup(self.title, self.equation_group, self.bullet_group, self.caption)

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
        self.play(ReplacementTransform(compact_equation, self.equation), FadeIn(self.title), run_time=0.8)

        block_content = VGroup(self.graph_group, self.bullet_group).arrange(RIGHT, buff=0.8, aligned_edge=UP)
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
        branch_2 = VGroup(self.edge_s1_terminal, self.label_s1_terminal, self.state_s1, self.text_s1)
        branch_highlighter = StatefulHighlighter(dim_opacity=self.DIM_OPACITY, active_opacity=self.ACTIVE_OPACITY)

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
        self.play(Indicate(self.equation, color=self.EMPHASIS_COLOR, scale_factor=1.02), run_time=0.45)

        sum_token_target = MathTex(r"\sum_{s',r}", font_size=44, color=self.TEXT_COLOR).move_to(sum_slot)
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
