"""Panel infrastructure, base scene, and animation helpers for concept videos.

All helpers used by the Manim Expert live here or in helpers.py.
Scenes import from manim_service.scenes (the __init__ re-exports everything).
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol, runtime_checkable

import numpy as np
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    WHITE,
    YELLOW,
    AnimationGroup,
    Arrow,
    Create,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    Indicate,
    LaggedStart,
    MathTex,
    Mobject,
    MovingCameraScene,
    Rectangle,
    RoundedRectangle,
    Scene,
    SurroundingRectangle,
    Text,
    VGroup,
    ValueTracker,
    Write,
    always_redraw,
)

try:
    from manim import GREY_A
except ImportError:
    GREY_A = "#BBBBBB"

# ---------------------------------------------------------------------------
# Semantic color palette (source of truth for all concept video colors)
# ---------------------------------------------------------------------------

STATE_COLOR = "#38BDF8"     # blue   — states, cells, s
VALUE_COLOR = "#FACC15"     # yellow — V(s), Q(s,a), values
REWARD_COLOR = "#34D399"    # green  — rewards, positive outcomes
PENALTY_COLOR = "#F87171"   # red    — penalties, holes, negative outcomes
POLICY_COLOR = "#A78BFA"    # purple — policy π, action choices
ACTION_COLOR = "#FB923C"    # orange — actions, arrows
BG_COLOR = "#020617"        # scene background
BG_PANEL = "#0F172A"        # panel fill
BG_GRID = "#1E293B"         # structural background grids (use at 0.15 opacity)
CODE_ACCENT = "#64748B"     # muted  — code panel headers

# Legacy aliases (kept for backward compat with any existing scenes)
ACCENT_BLUE = STATE_COLOR
ACCENT_YELLOW = VALUE_COLOR
ACCENT_GREEN = REWARD_COLOR
ACCENT_SLATE = CODE_ACCENT
BG_DEEP = BG_COLOR

# ---------------------------------------------------------------------------
# Opacity hierarchy constants
# ---------------------------------------------------------------------------

OPACITY_PRIMARY = 1.0       # active equations, targeted vectors, current state
OPACITY_SECONDARY = 0.4     # surrounding graph, historical paths, inactive states
OPACITY_BACKGROUND = 0.17   # coordinate axes, grid planes, lattice structure

# Default Manim frame width (16:9 at height 8)
_DEFAULT_FRAME_WIDTH = 14.222


# ---------------------------------------------------------------------------
# BaseConceptScene
# ---------------------------------------------------------------------------

class BaseConceptScene(MovingCameraScene):
    """Base class for all concept video scenes.

    Sets the dark background, exposes standard layout anchors, and wraps
    common operations (header, caption, assimilation waits).
    """

    def setup(self) -> None:
        super().setup()
        self.camera.background_color = BG_COLOR
        self.camera.frame.save_state()

    def show_header(self, title: str, subtitle: str | None = None) -> VGroup:
        """Fade in a title (and optional subtitle) at the top of the frame."""
        title_mob = Text(title, font_size=36, color=WHITE)
        title_mob.to_edge(UP, buff=0.35)
        items: list[Mobject] = [FadeIn(title_mob, shift=DOWN * 0.15)]
        header = VGroup(title_mob)
        if subtitle is not None:
            sub_mob = Text(subtitle, font_size=22, color=GREY_A)
            sub_mob.next_to(title_mob, DOWN, buff=0.12)
            items.append(FadeIn(sub_mob, shift=DOWN * 0.1))
            header.add(sub_mob)
        self.play(LaggedStart(*items, lag_ratio=0.25))
        return header

    def assimilation_wait(self, duration: float = 1.5) -> None:
        """Pause for the viewer to absorb what's on screen."""
        self.wait(duration)

    def place_caption(self, text: str, font_size: int = 22) -> Text:
        """Return a caption Text mobject anchored to the bottom edge."""
        cap = Text(text, font_size=font_size, color=GREY_A)
        cap.to_edge(DOWN, buff=0.28)
        return cap

    def place_left_panel(self, mob: Mobject, buff: float = 0.55) -> Mobject:
        mob.to_edge(LEFT, buff=buff).shift(DOWN * 0.15)
        return mob

    def place_top_right_panel(self, mob: Mobject) -> Mobject:
        mob.to_edge(RIGHT, buff=0.45).to_edge(UP, buff=0.55)
        return mob

    def place_mid_right_panel(self, mob: Mobject) -> Mobject:
        mob.to_edge(RIGHT, buff=0.45)
        return mob

    def place_bottom_right_panel(self, mob: Mobject) -> Mobject:
        mob.to_edge(RIGHT, buff=0.45).to_edge(DOWN, buff=0.55)
        return mob


# ---------------------------------------------------------------------------
# Utility builders
# ---------------------------------------------------------------------------

def note_stack(
    lines: list[str],
    *,
    font_size: int = 22,
    color: str = GREY_A,
    line_buff: float = 0.14,
) -> VGroup:
    """VGroup of Text rows arranged downward."""
    rows = [Text(line, font_size=font_size, color=color) for line in lines]
    group = VGroup(*rows).arrange(DOWN, buff=line_buff, aligned_edge=LEFT)
    return group


def panel(
    title: str,
    body: Mobject,
    accent: str = ACCENT_BLUE,
    *,
    width: float = 5.4,
    min_height: float = 1.6,
    padding: float = 0.28,
    corner_radius: float = 0.14,
) -> VGroup:
    """Rounded panel with a title bar and a body mobject.

    Returns VGroup(background_rect, VGroup(title_mob, body)).
    """
    title_mob = Text(title, font_size=20, color=accent)
    content = VGroup(title_mob, body).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
    content_w = max(content.get_width() + padding * 2, width)
    content_h = max(content.get_height() + padding * 2, min_height)

    bg = RoundedRectangle(
        width=content_w,
        height=content_h,
        corner_radius=corner_radius,
        fill_color=BG_PANEL,
        fill_opacity=1.0,
        stroke_color=accent,
        stroke_width=1.5,
    )
    content.move_to(bg.get_center())
    return VGroup(bg, content)


def code_panel(
    lines: list[str],
    *,
    title: str = "Code",
    width: float = 5.4,
    font_size: int = 19,
    accent: str = CODE_ACCENT,
) -> VGroup:
    """Monospace code lines inside a panel."""
    code_lines = VGroup(
        *[Text(line, font_size=font_size, color=WHITE, font="Courier") for line in lines]
    ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    return panel(title, code_lines, accent, width=width)


def equation_panel(
    title: str,
    equation: str,
    notes: list[str] | None = None,
    *,
    accent: str = ACCENT_YELLOW,
    width: float = 5.6,
    font_size: int = 30,
) -> VGroup:
    """MathTex equation (and optional text notes) inside a panel."""
    eq_mob = MathTex(equation, font_size=font_size, color=WHITE)
    if notes:
        note_mob = note_stack(notes, font_size=18)
        body = VGroup(eq_mob, note_mob).arrange(DOWN, buff=0.18)
    else:
        body = eq_mob
    return panel(title, body, accent, width=width)


def pill(label: str, color: str) -> VGroup:
    """Small badge chip: rounded rect + label text."""
    text = Text(label, font_size=16, color=WHITE)
    bg = RoundedRectangle(
        width=text.get_width() + 0.3,
        height=text.get_height() + 0.14,
        corner_radius=0.08,
        fill_color=color,
        fill_opacity=0.85,
        stroke_width=0,
    )
    text.move_to(bg.get_center())
    return VGroup(bg, text)


# ---------------------------------------------------------------------------
# Environment asset helpers
# ---------------------------------------------------------------------------

def frozenlake_frame(state: int, height: float = 2.8) -> Mobject:
    """ImageMobject for a FrozenLake state, or fallback colored rect."""
    asset_dir = Path(__file__).resolve().parents[3] / "frontend" / "assets" / "lesson_media" / "frozenlake"
    img_path = asset_dir / f"state_{state:02d}.png"
    if img_path.exists():
        mob = ImageMobject(str(img_path))
        mob.set_height(height)
        return mob
    # Fallback: plain rectangle
    rect = Rectangle(
        width=height,
        height=height,
        fill_color=BG_GRID,
        fill_opacity=1.0,
        stroke_color=STATE_COLOR,
        stroke_width=2.0,
    )
    label = Text(f"s={state}", font_size=24, color=STATE_COLOR)
    label.move_to(rect.get_center())
    return VGroup(rect, label)


def environment_panel(
    state: int,
    *,
    title: str,
    caption: str,
    badge_text: str,
    accent: str = STATE_COLOR,
    width: float = 4.8,
) -> VGroup:
    """FrozenLake frame wrapped in a panel with a badge and caption."""
    frame = frozenlake_frame(state)
    badge = pill(badge_text, accent)
    body = VGroup(frame, badge).arrange(DOWN, buff=0.14)
    p = panel(title, body, accent, width=width)
    if caption:
        cap = Text(caption, font_size=17, color=GREY_A)
        cap.next_to(p, DOWN, buff=0.12)
        return VGroup(p, cap)
    return p


def card_mobject(
    code: str,
    *,
    height: float = 1.2,
    asset_dir: Path | None = None,
) -> Mobject:
    """ImageMobject for a playing card (e.g. 'CA', 'H7', 'Card' for back)."""
    if asset_dir is None:
        try:
            import gymnasium.envs.toy_text.frozen_lake as _fl
            asset_dir = Path(_fl.__file__).resolve().parent / "img"
        except ImportError:
            asset_dir = None

    if asset_dir is not None:
        img_path = asset_dir / f"{code}.png"
        if img_path.exists():
            mob = ImageMobject(str(img_path))
            mob.set_height(height)
            return mob

    # Fallback: rectangle with label
    rect = Rectangle(
        width=height * 0.7,
        height=height,
        fill_color=WHITE,
        fill_opacity=0.9,
        stroke_color=BG_GRID,
        stroke_width=1.5,
    )
    label = Text(code, font_size=14, color=BG_COLOR)
    label.move_to(rect.get_center())
    return VGroup(rect, label)


def blackjack_panel(
    player_hand: list[str],
    dealer_visible: str,
    dealer_hidden: bool = True,
    *,
    title: str = "Blackjack",
    caption: str = "",
    accent: str = REWARD_COLOR,
    width: float = 4.8,
) -> VGroup:
    """Blackjack table panel with actual card images (with fallback)."""
    try:
        import gymnasium.envs.toy_text.frozen_lake as _fl
        _asset_dir: Path | None = Path(_fl.__file__).resolve().parent / "img"
    except ImportError:
        _asset_dir = None

    dealer_cards = Group(card_mobject(dealer_visible, asset_dir=_asset_dir))
    if dealer_hidden:
        dealer_cards.add(card_mobject("Card", asset_dir=_asset_dir))
    dealer_cards.arrange(RIGHT, buff=0.05)

    player_cards = Group(*[card_mobject(c, asset_dir=_asset_dir) for c in player_hand])
    player_cards.arrange(RIGHT, buff=0.05)

    dealer_label = Text("Dealer", font_size=15, color=GREY_A)
    player_label = Text("Player", font_size=15, color=GREY_A)

    dealer_row = VGroup(dealer_label, dealer_cards).arrange(DOWN, buff=0.08)
    player_row = VGroup(player_label, player_cards).arrange(DOWN, buff=0.08)
    body = VGroup(dealer_row, player_row).arrange(DOWN, buff=0.22)

    p = panel(title, body, accent, width=width)
    if caption:
        cap = Text(caption, font_size=17, color=GREY_A)
        cap.next_to(p, DOWN, buff=0.12)
        return VGroup(p, cap)
    return p


def cliffwalking_panel(
    agent_pos: tuple[int, int] | None = None,
    episode_path: list[tuple[int, int]] | None = None,
    *,
    title: str = "CliffWalking",
    caption: str = "",
    accent: str = STATE_COLOR,
    width: float = 4.9,
) -> VGroup:
    """CliffWalking 4×12 grid panel with cliff, agent, and optional trail."""
    rows, cols = 4, 12
    cell_w = (width - 0.3) / cols
    cell_h = cell_w * 0.85

    cells = VGroup()
    for r in range(rows):
        for c in range(cols):
            is_cliff = (r == 3 and 1 <= c <= 10)
            is_start = (r == 3 and c == 0)
            is_goal = (r == 3 and c == 11)
            fill = (
                PENALTY_COLOR if is_cliff
                else REWARD_COLOR if is_goal
                else BG_GRID
            )
            cell = Rectangle(
                width=cell_w - 0.02,
                height=cell_h - 0.02,
                fill_color=fill,
                fill_opacity=0.7 if (is_cliff or is_goal) else 0.3,
                stroke_color=accent,
                stroke_width=0.5,
            )
            cell.move_to([
                (c - cols / 2 + 0.5) * cell_w,
                -(r - rows / 2 + 0.5) * cell_h,
                0,
            ])
            cells.add(cell)
            if is_start:
                lbl = Text("S", font_size=10, color=STATE_COLOR)
                lbl.move_to(cell.get_center())
                cells.add(lbl)
            elif is_goal:
                lbl = Text("G", font_size=10, color=WHITE)
                lbl.move_to(cell.get_center())
                cells.add(lbl)

    # Episode path trail
    if episode_path and len(episode_path) > 1:
        for (r1, c1), (r2, c2) in zip(episode_path[:-1], episode_path[1:]):
            start = np.array([
                (c1 - cols / 2 + 0.5) * cell_w,
                -(r1 - rows / 2 + 0.5) * cell_h,
                0,
            ])
            end = np.array([
                (c2 - cols / 2 + 0.5) * cell_w,
                -(r2 - rows / 2 + 0.5) * cell_h,
                0,
            ])
            arrow = Arrow(
                start, end,
                buff=0,
                stroke_width=1.2,
                color=POLICY_COLOR,
                max_tip_length_to_length_ratio=0.3,
            )
            arrow.set_opacity(OPACITY_SECONDARY)
            cells.add(arrow)

    # Agent marker
    if agent_pos is not None:
        r, c = agent_pos
        agent_dot = Rectangle(
            width=cell_w * 0.55,
            height=cell_h * 0.55,
            fill_color=STATE_COLOR,
            fill_opacity=0.95,
            stroke_width=0,
        )
        agent_dot.move_to([
            (c - cols / 2 + 0.5) * cell_w,
            -(r - rows / 2 + 0.5) * cell_h,
            0,
        ])
        cells.add(agent_dot)

    return panel(title, cells, accent, width=width)


# ---------------------------------------------------------------------------
# Stepper / highlighter classes
# ---------------------------------------------------------------------------

class FormulaStepper:
    """Cycles through a sequence of MathTex formulas.

    Usage:
        fs = FormulaStepper(["V(s)", "V(s) = \\\\max_a Q(s,a)"], font_size=32)
        self.play(Write(fs.get()))
        self.play(fs.next(self))
    """

    def __init__(
        self,
        formulas: list[str],
        *,
        font_size: int = 32,
        color: str = WHITE,
    ) -> None:
        self._formulas = formulas
        self._font_size = font_size
        self._color = color
        self._idx = 0
        self._current: MathTex = MathTex(formulas[0], font_size=font_size, color=color)

    def get(self) -> MathTex:
        return self._current

    def next(self, scene: Scene) -> MathTex:
        if self._idx + 1 >= len(self._formulas):
            return self._current
        self._idx += 1
        new = MathTex(
            self._formulas[self._idx],
            font_size=self._font_size,
            color=self._color,
        ).move_to(self._current.get_center())
        from manim import ReplacementTransform
        scene.play(ReplacementTransform(self._current, new))
        self._current = new
        return self._current


class StatefulHighlighter:
    """Dims the previously focused mobject and highlights the new one.

    Usage:
        hl = StatefulHighlighter()
        self.play(*hl.step(equation[0]))
        self.play(*hl.step(equation[1]))
    """

    def __init__(self) -> None:
        self._prev: Mobject | None = None

    def step(self, mob: Mobject) -> list:
        anims = []
        if self._prev is not None:
            anims.append(self._prev.animate.set_opacity(OPACITY_SECONDARY))
        anims.append(mob.animate.set_opacity(OPACITY_PRIMARY))
        self._prev = mob
        return anims


class HighlightedAnimation(AnimationGroup):
    """Wraps an animation with a temporary SurroundingRectangle highlight."""

    def __init__(
        self,
        mobject: Mobject,
        animation,
        *,
        color: str = YELLOW,
        **kwargs,
    ) -> None:
        rect = SurroundingRectangle(mobject, color=color, buff=0.05)
        super().__init__(Create(rect), animation, **kwargs)


def highlighted_animation(
    mobject: Mobject,
    animation,
    *,
    color: str = YELLOW,
) -> HighlightedAnimation:
    return HighlightedAnimation(mobject, animation, color=color)


class CodeStepper:
    """Manages step-by-step code line highlighting for three-way sync.

    Usage:
        stepper = CodeStepper(["line 1", "line 2", "line 3"])
        self.add(stepper.panel)
        self.play(*stepper.step(self, 0))   # highlight line 0
        self.play(*stepper.step(self, 1))   # dim line 0, highlight line 1
        self.play(*stepper.reset(self))
    """

    def __init__(
        self,
        lines: list[str],
        *,
        title: str = "Code",
        width: float = 5.4,
        font_size: float = 19,
        highlight_color: str = ACTION_COLOR,
        dim_opacity: float = OPACITY_SECONDARY,
    ) -> None:
        self._lines_mobs = [
            Text(line, font_size=font_size, color=WHITE, font="Courier")
            for line in lines
        ]
        code_group = VGroup(*self._lines_mobs).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        self.panel = panel(title, code_group, CODE_ACCENT, width=width)
        self._highlight_color = highlight_color
        self._dim_opacity = dim_opacity
        self._active_idx: int | None = None
        self._rect: SurroundingRectangle | None = None

    def step(self, scene: Scene, line_idx: int) -> list:
        anims: list = []
        if self._active_idx is not None and self._rect is not None:
            anims.append(FadeOut(self._rect))
            if self._active_idx != line_idx:
                anims.append(
                    self._lines_mobs[self._active_idx].animate.set_opacity(self._dim_opacity)
                )
        for i, mob in enumerate(self._lines_mobs):
            if i != line_idx and i != self._active_idx:
                mob.set_opacity(self._dim_opacity)
        target = self._lines_mobs[line_idx]
        anims.append(target.animate.set_opacity(OPACITY_PRIMARY))
        new_rect = SurroundingRectangle(
            target, color=self._highlight_color, buff=0.06, stroke_width=1.5
        )
        anims.append(Create(new_rect))
        self._active_idx = line_idx
        self._rect = new_rect
        return anims

    def reset(self, scene: Scene) -> list:
        anims: list = []
        if self._rect is not None:
            anims.append(FadeOut(self._rect))
            self._rect = None
        for mob in self._lines_mobs:
            anims.append(mob.animate.set_opacity(OPACITY_PRIMARY))
        self._active_idx = None
        return anims


# ---------------------------------------------------------------------------
# ActionBarChart — ValueTracker-driven bar chart
# ---------------------------------------------------------------------------

class ActionBarChart(VGroup):
    """Bar chart for action probabilities / Q-values driven by ValueTrackers.

    Bars resize smoothly via ValueTracker + always_redraw so they update
    correctly during scene.play(tracker.animate.set_value(...)).

    Usage:
        chart = ActionBarChart(["←","↓","→","↑"], [0.25, 0.25, 0.25, 0.25])
        self.add(chart)
        chart.update_bars(self, [0.33, 0.0, 0.33, 0.33])
    """

    def __init__(
        self,
        actions: list[str],
        values: list[float],
        *,
        width: float = 3.2,
        height: float = 2.4,
        bar_color: str = VALUE_COLOR,
        label_font_size: float = 20,
        value_font_size: float = 18,
        accent: str = STATE_COLOR,
    ) -> None:
        super().__init__()
        n = len(actions)
        self._trackers = [ValueTracker(v) for v in values]
        self._n = n
        bar_area_height = height * 0.62
        bar_width = width / (n * 1.6)

        bg = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.12,
            fill_color=BG_PANEL,
            fill_opacity=1.0,
            stroke_color=accent,
            stroke_width=1.5,
        )
        self.add(bg)
        self._bg = bg

        self._bars: list[Mobject] = []
        self._val_labels: list[Mobject] = []

        for i, (action, tracker) in enumerate(zip(actions, self._trackers)):
            # x position relative to bg, so bars follow when chart is moved
            rel_x = -width / 2 + width * (i + 0.5) / n
            bottom_rel_y = -height / 2 + 0.38

            bar = always_redraw(
                lambda t=tracker, ref=bg, rx=rel_x, bry=bottom_rel_y,
                bw=bar_width, bah=bar_area_height, bc=bar_color:
                Rectangle(
                    width=bw,
                    height=max(0.02, t.get_value() * bah),
                    fill_color=bc,
                    fill_opacity=0.88,
                    stroke_width=0,
                ).move_to([
                    ref.get_center()[0] + rx,
                    ref.get_center()[1] + bry + t.get_value() * bah / 2,
                    0,
                ])
            )
            self._bars.append(bar)
            self.add(bar)

            val_label = always_redraw(
                lambda t=tracker, ref=bg, rx=rel_x, bry=bottom_rel_y,
                bah=bar_area_height, vfs=value_font_size:
                Text(f"{t.get_value():.2f}", font_size=vfs, color=WHITE).move_to([
                    ref.get_center()[0] + rx,
                    ref.get_center()[1] + bry + t.get_value() * bah + 0.18,
                    0,
                ])
            )
            self._val_labels.append(val_label)
            self.add(val_label)

            act_label = Text(action, font_size=label_font_size, color=WHITE)
            # Position action label relative to bg bottom
            act_label.move_to([0, 0, 0])  # temporary; shifted via updater below
            act_label.add_updater(
                lambda m, ref=bg, rx=rel_x:
                m.move_to([ref.get_center()[0] + rx, ref.get_bottom()[1] + 0.22, 0])
            )
            self.add(act_label)

    def update_bars(self, scene: Scene, new_values: list[float]) -> None:
        """Animate bars to new_values in-place (plays immediately)."""
        scene.play(
            *[t.animate.set_value(v) for t, v in zip(self._trackers, new_values)],
            run_time=0.6,
        )

    def highlight_bar(self, idx: int) -> Indicate:
        return Indicate(self._bars[idx], color=YELLOW, scale_factor=1.15)

    def dim_all(self) -> list:
        return [b.animate.set_opacity(OPACITY_SECONDARY) for b in self._bars]

    def reset_all(self) -> list:
        return [b.animate.set_opacity(OPACITY_PRIMARY) for b in self._bars]


# ---------------------------------------------------------------------------
# SynchronizedFocusGroup
# ---------------------------------------------------------------------------

class SynchronizedFocusGroup:
    """Coordinates dim/highlight across multiple parallel item lists.

    Each list corresponds to one panel (e.g., equation terms, grid arrows,
    chart bars). item_lists[i][j] is the j-th element in panel i.

    Usage:
        sync = SynchronizedFocusGroup(eq_terms, grid_arrows, chart_bars)
        self.play(*sync.step(self, 2))  # highlight index 2 in all panels
    """

    def __init__(self, *item_lists: list[Mobject]) -> None:
        self._lists = item_lists
        self._current_idx: int | None = None

    def step(self, scene: Scene, idx: int) -> list:
        anims: list = []
        # Dim current across all panels
        if self._current_idx is not None and self._current_idx != idx:
            for lst in self._lists:
                if self._current_idx < len(lst):
                    anims.append(lst[self._current_idx].animate.set_opacity(OPACITY_SECONDARY))
        # Highlight new across all panels
        for lst in self._lists:
            if idx < len(lst):
                anims.append(lst[idx].animate.set_opacity(OPACITY_PRIMARY))
        self._current_idx = idx
        return anims

    def dim_all(self) -> list:
        anims: list = []
        for lst in self._lists:
            for mob in lst:
                anims.append(mob.animate.set_opacity(OPACITY_SECONDARY))
        self._current_idx = None
        return anims

    def reset_all(self) -> list:
        anims: list = []
        for lst in self._lists:
            for mob in lst:
                anims.append(mob.animate.set_opacity(OPACITY_PRIMARY))
        self._current_idx = None
        return anims


# ---------------------------------------------------------------------------
# action_arrows_overlay
# ---------------------------------------------------------------------------

def action_arrows_overlay(
    cell_center: np.ndarray,
    *,
    arrow_len: float = 0.28,
    stroke_width: float = 3.0,
    color: str = WHITE,
) -> VGroup:
    """Four arrows (UP/DOWN/LEFT/RIGHT) centered at cell_center.

    Each arrow has `.action_idx` set to its index (0=left,1=down,2=right,3=up)
    for SynchronizedFocusGroup mapping.
    """
    directions = [LEFT, DOWN, RIGHT, UP]
    arrows = VGroup()
    for idx, direction in enumerate(directions):
        start = np.array(cell_center, dtype=float)
        end = start + direction * arrow_len
        arr = Arrow(
            start,
            end,
            buff=0,
            stroke_width=stroke_width,
            color=color,
            max_tip_length_to_length_ratio=0.4,
        )
        arr.action_idx = idx  # type: ignore[attr-defined]
        arrows.add(arr)
    return arrows


# ---------------------------------------------------------------------------
# Camera helpers
# ---------------------------------------------------------------------------

def zoom_to(
    scene: MovingCameraScene,
    target: Mobject,
    *,
    scale: float = 0.5,
    run_time: float = 1.2,
) -> None:
    """Reframe camera onto target at given scale factor."""
    scene.play(
        scene.camera.frame.animate.scale(scale).move_to(target),
        run_time=run_time,
    )


def zoom_reset(scene: MovingCameraScene, *, run_time: float = 0.9) -> None:
    """Restore camera to default full-frame view."""
    scene.play(
        scene.camera.frame.animate.set_width(_DEFAULT_FRAME_WIDTH).move_to(ORIGIN),
        run_time=run_time,
    )


# ---------------------------------------------------------------------------
# EnvironmentPanel protocol + concrete implementations
# ---------------------------------------------------------------------------

@runtime_checkable
class EnvironmentPanel(Protocol):
    """Common interface for all environment visualizations.

    Implementors are returned by env_panel() and conform to this protocol so
    SynchronizedFocusGroup and CodeStepper can treat all environments uniformly.
    """

    panel: VGroup

    def set_state(self, scene: Scene, state) -> list:
        """Animate the environment to reflect `state`."""
        ...

    def highlight_cell(self, scene: Scene, identifier) -> list:
        """Flash or outline a cell/region (used by SynchronizedFocusGroup)."""
        ...

    def show_transition(self, scene: Scene, s, a, s_prime) -> list:
        """Animate a single (s, a) → s' transition."""
        ...


class _FrozenLakePanelImpl:
    """FrozenLake-v1 environment panel (4×4 grid with state images)."""

    def __init__(
        self,
        initial_state: int = 0,
        *,
        title: str = "FrozenLake",
        width: float = 4.8,
        accent: str = STATE_COLOR,
    ) -> None:
        self._state = initial_state
        self._accent = accent
        self._width = width
        self._title = title
        frame = frozenlake_frame(initial_state)
        self.panel = panel(title, frame, accent, width=width)
        self._frame_mob = frame

    def set_state(self, scene: Scene, state: int) -> list:
        new_frame = frozenlake_frame(state)
        new_frame.move_to(self._frame_mob.get_center())
        self._state = state
        from manim import ReplacementTransform
        anims = [ReplacementTransform(self._frame_mob, new_frame)]
        self._frame_mob = new_frame
        return anims

    def highlight_cell(self, scene: Scene, identifier) -> list:
        return [Indicate(self._frame_mob, color=STATE_COLOR, scale_factor=1.08)]

    def show_transition(self, scene: Scene, s, a, s_prime) -> list:
        return self.set_state(scene, s_prime)


class _BlackjackPanelImpl:
    """Blackjack-v1 environment panel."""

    def __init__(
        self,
        player_hand: list[str] | None = None,
        dealer_visible: str = "CA",
        *,
        title: str = "Blackjack",
        width: float = 4.8,
        accent: str = REWARD_COLOR,
    ) -> None:
        player_hand = player_hand or ["CA", "H7"]
        self._player_hand = player_hand
        self._dealer_visible = dealer_visible
        self._title = title
        self._width = width
        self._accent = accent
        self.panel = blackjack_panel(player_hand, dealer_visible, title=title, accent=accent, width=width)

    def set_state(self, scene: Scene, state) -> list:
        return []

    def highlight_cell(self, scene: Scene, identifier) -> list:
        return [Indicate(self.panel, color=REWARD_COLOR)]

    def show_transition(self, scene: Scene, s, a, s_prime) -> list:
        return []


class _CliffWalkingPanelImpl:
    """CliffWalking-v0 environment panel."""

    def __init__(
        self,
        initial_state: int = 36,
        *,
        title: str = "CliffWalking",
        width: float = 4.9,
        accent: str = STATE_COLOR,
    ) -> None:
        # State 36 = row 3, col 0 (start) in 4×12 grid
        self._state = initial_state
        self._title = title
        self._width = width
        self._accent = accent
        r, c = divmod(initial_state, 12)
        self.panel = cliffwalking_panel((r, c), title=title, accent=accent, width=width)

    def set_state(self, scene: Scene, state: int) -> list:
        r, c = divmod(state, 12)
        new_panel = cliffwalking_panel((r, c), title=self._title, accent=self._accent, width=self._width)
        new_panel.move_to(self.panel.get_center())
        from manim import ReplacementTransform
        anims = [ReplacementTransform(self.panel, new_panel)]
        self.panel = new_panel
        self._state = state
        return anims

    def highlight_cell(self, scene: Scene, identifier) -> list:
        return [Indicate(self.panel, color=STATE_COLOR)]

    def show_transition(self, scene: Scene, s, a, s_prime) -> list:
        return self.set_state(scene, s_prime)


# Registry: env_name prefix → builder callable
_ENV_PANEL_REGISTRY: dict[str, Callable[..., EnvironmentPanel]] = {
    "FrozenLake": lambda state, title, width, accent, **kw:
        _FrozenLakePanelImpl(state or 0, title=title, width=width, accent=accent),
    "Blackjack": lambda state, title, width, accent, **kw:
        _BlackjackPanelImpl(title=title, width=width, accent=accent),
    "CliffWalking": lambda state, title, width, accent, **kw:
        _CliffWalkingPanelImpl(state or 36, title=title, width=width, accent=accent),
}


def env_panel(
    env_name: str,
    initial_state=None,
    *,
    title: str | None = None,
    width: float = 4.8,
    accent: str = STATE_COLOR,
    **env_kwargs,
) -> EnvironmentPanel:
    """Factory: returns an EnvironmentPanel for the named Gymnasium environment.

    Dispatches by prefix so 'FrozenLake-v1' resolves to the FrozenLake builder.
    """
    resolved_title = title or env_name
    for prefix, builder in _ENV_PANEL_REGISTRY.items():
        if env_name.startswith(prefix):
            return builder(initial_state, resolved_title, width, accent, **env_kwargs)
    raise ValueError(
        f"No environment panel registered for '{env_name}'. "
        f"Known prefixes: {list(_ENV_PANEL_REGISTRY)}"
    )
