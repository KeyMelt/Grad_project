"""Reusable motion primitives for concept video scenes.

Import via:
    from manim_service.scenes import equation_morph, token_expand, ...
"""
from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    FadeIn,
    LaggedStart,
    MathTex,
    Mobject,
    Rectangle,
    Scene,
    TransformMatchingTex,
    ValueTracker,
    Write,
    always_redraw,
)

from .panels import VALUE_COLOR


# ---------------------------------------------------------------------------
# Equation transformation helpers
# ---------------------------------------------------------------------------


def equation_morph(
    scene: Scene,
    old_eq: MathTex,
    new_eq: MathTex,
    *,
    run_time: float = 1.2,
    move_to_old: bool = True,
) -> None:
    """Transform old_eq → new_eq using TransformMatchingTex.

    Matched tokens slide into place; unmatched tokens FadeOut/FadeIn.
    Both arguments must be decomposed into component token strings in the
    MathTex constructor for token matching to work correctly.

    Example::

        v_eq = MathTex("V", "(", "s", ")", "=", "\\\\max_a", "Q", "(", "s", ",", "a", ")")
        q_eq = MathTex("Q", "(", "s", ",", "a", ")", "=", "r", "+", "\\\\gamma", "V", "(", "s'", ")")
        equation_morph(self, v_eq, q_eq)
    """
    if move_to_old:
        new_eq.move_to(old_eq.get_center())
    scene.play(TransformMatchingTex(old_eq, new_eq, run_time=run_time))


def token_expand(
    scene: Scene,
    compact: MathTex,
    expanded: MathTex,
    *,
    run_time: float = 1.4,
) -> None:
    """Animate compact symbolic form → expanded explanatory form.

    Intended for revealing the meaning behind shorthand notation, e.g.
    expanding p(s'|s,a) into its distributional interpretation. Matched
    tokens carry forward; new tokens FadeIn in place.

    The longer default run_time (vs equation_morph) gives the expansion
    room to breathe — the viewer needs to read the expanded form.

    Example::

        short = MathTex("p", "(", "s'", "|", "s", ",", "a", ")")
        long  = MathTex(
            "\\\\Pr", "(", "S_{t+1}", "=", "s'", "|",
            "S_t", "=", "s", ",", "A_t", "=", "a", ")"
        )
        token_expand(self, short, long)
    """
    expanded.move_to(compact.get_center())
    scene.play(TransformMatchingTex(compact, expanded, run_time=run_time))


# ---------------------------------------------------------------------------
# Staggered entrance helpers
# ---------------------------------------------------------------------------


def staggered_write(
    scene: Scene,
    mobs: list[Mobject],
    *,
    lag_ratio: float = 0.15,
    run_time: float = 1.5,
) -> None:
    """LaggedStart Write for a list of Mobjects.

    Required pattern for any object introduction with more than 2 items.
    Use for equations, note stacks, and any multi-element mathematical
    objects where stroke-drawing semantics are appropriate.
    """
    scene.play(
        LaggedStart(*[Write(m) for m in mobs], lag_ratio=lag_ratio),
        run_time=run_time,
    )


def staggered_fadein(
    scene: Scene,
    mobs: list[Mobject],
    *,
    lag_ratio: float = 0.15,
    run_time: float = 1.2,
    shift=None,
) -> None:
    """LaggedStart FadeIn for a list of Mobjects.

    Use for panels, image groups, and bar charts where Write (pen-stroke)
    semantics are inappropriate. Optional shift (e.g. UP * 0.2) applies
    a directional drift during the fade.
    """
    fadein_kwargs: dict = {}
    if shift is not None:
        fadein_kwargs["shift"] = shift
    scene.play(
        LaggedStart(*[FadeIn(m, **fadein_kwargs) for m in mobs], lag_ratio=lag_ratio),
        run_time=run_time,
    )


# ---------------------------------------------------------------------------
# Reactive bar primitive
# ---------------------------------------------------------------------------


def reactive_bar(
    tracker: ValueTracker,
    bottom_center: list | tuple = (0.0, 0.0, 0.0),
    *,
    max_height: float = 2.0,
    width: float = 0.35,
    color: str = VALUE_COLOR,
) -> Mobject:
    """Return an always_redraw Rectangle bar driven by a ValueTracker.

    The bar grows upward from bottom_center as tracker.get_value() increases.
    Expected tracker range: 0..1. max_height is the bar height at value = 1.0.

    The returned Mobject is always_redraw — add it to the scene once, then
    animate via ``scene.play(tracker.animate.set_value(...))``.

    Note: bottom_center is captured at construction time. If you need a bar
    that follows a moving reference object, use ActionBarChart instead.

    Example::

        t = ValueTracker(0.25)
        bar = reactive_bar(t, bottom_center=(-2, -1.5, 0), max_height=2.0)
        self.add(bar)
        self.play(t.animate.set_value(0.75), run_time=1.0)
    """
    bc = np.array(bottom_center, dtype=float)

    return always_redraw(
        lambda: Rectangle(
            width=width,
            height=max(0.02, tracker.get_value() * max_height),
            fill_color=color,
            fill_opacity=0.88,
            stroke_width=0,
        ).move_to([
            bc[0],
            bc[1] + tracker.get_value() * max_height / 2,
            0.0,
        ])
    )
