"""Reusable visual primitives for the trace replay — the toolbox that makes the
GRID carry the algorithm instead of leaving everything to the side text card.

Design: these are pure manim helpers that know NOTHING about the trace schema.
Callers (the per-step director and the env boards) pass already-extracted points,
values, and label strings; this module owns the *motion*, the boards own the
*geometry*. That keeps the new visuals in one testable place.

The geometry/colour core (``sign_color``, ``fan_layout``) is render-free and unit
tested; the animating primitives are exercised by the render-smoke steps.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from manim import (
    Arrow,
    Circle,
    CurvedArrow,
    DashedVMobject,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    MathTex,
    MoveAlongPath,
    VGroup,
)

from . import trace_common as C

# Direction keyword / action label (lowercased) -> outward angle (radians).
_DIR_ANGLE: dict[str, float] = {
    "right": 0.0, "east": 0.0,
    "up": np.pi / 2, "north": np.pi / 2,
    "left": np.pi, "west": np.pi,
    "down": -np.pi / 2, "south": -np.pi / 2,
}


# --------------------------------------------------------------- pure helpers
def sign_color(value: float) -> str:
    """Green for value flowing *in* (>=0), red for a negative contribution."""
    return C.REWARD if (value or 0.0) >= 0 else C.PENALTY


def fan_layout(
    dir_values: list[tuple[str, float]],
    chosen_idx: int,
    cell_w: float,
) -> list[dict]:
    """Lay out an action fan: one outward spoke per action, length & opacity
    scaled by |value| (normalised to the strongest action), the chosen action
    flagged. Pure — returns plain dicts so it can be unit-tested without a render.

    Each row: ``{label, value, angle, length, opacity, chosen}``.
    """
    n = len(dir_values)
    # Length encodes how GOOD an action is, so the longest spoke is the best
    # action. Use min-max over the raw values (not |value|): for negative Q rows
    # (CliffWalking/Taxi) the least-negative action must be the longest, and for
    # positive DP returns the largest is longest — min-max gives both correctly.
    vals = [C.as_float(v) or 0.0 for _, v in dir_values]
    lo, hi = (min(vals), max(vals)) if vals else (0.0, 0.0)
    rng = hi - lo
    base = cell_w * 0.30          # minimum visible spoke
    span = cell_w * 0.62          # extra length for the best action
    rows: list[dict] = []
    for i, (label, value) in enumerate(dir_values):
        key = str(label).strip().lower()
        # Known compass/arrow directions map to real angles; anything else
        # (e.g. Taxi Pickup/Dropoff) falls back to an even fan so it still draws.
        angle = _DIR_ANGLE.get(key)
        if angle is None:
            angle = np.pi / 2 - (2 * np.pi * i / max(n, 1))
        norm = ((vals[i] - lo) / rng) if rng > 1e-9 else 0.0
        rows.append({
            "label": label,
            "value": C.as_float(value),
            "angle": float(angle),
            "length": float(base + span * norm),
            "opacity": 1.0 if i == chosen_idx else 0.45,
            "chosen": i == chosen_idx,
        })
    return rows


def _as_point(p: Any) -> np.ndarray:
    arr = np.array(p, dtype=float)
    if arr.shape == (2,):
        arr = np.array([arr[0], arr[1], 0.0])
    return arr


# ------------------------------------------------------- animating primitives
def value_flow_arrow(
    scene,
    src_pt,
    dst_pt,
    label_tex: str,
    *,
    color: str,
    dashed: bool = False,
    run_time: float = 0.6,
) -> VGroup:
    """Draw an arrow from ``src_pt`` (the neighbour s') INTO ``dst_pt`` (the state
    being backed up) with ``label_tex`` riding along it — value visibly flowing
    back into the state. ``dashed=True`` reads as a softer 'borrow' link (TD
    bootstrap). Returns the arrow+label group (left on the scene)."""
    src, dst = _as_point(src_pt), _as_point(dst_pt)
    arrow = CurvedArrow(src, dst, color=color, angle=-0.42,
                        stroke_width=4.0, tip_length=0.18).set_z_index(32)
    body = DashedVMobject(arrow, num_dashes=14, dashed_ratio=0.55) if dashed else arrow
    body.set_z_index(32)
    label = MathTex(label_tex, font_size=20, color=color).set_z_index(33)
    label.move_to(src)
    path = Line(src, dst)
    scene.play(FadeIn(body, run_time=run_time * 0.45))
    scene.play(MoveAlongPath(label, path), run_time=run_time * 0.55)
    return VGroup(body, label)


def action_fan(
    scene,
    center_pt,
    dir_values: list[tuple[str, float]],
    chosen_idx: int,
    *,
    cell_w: float,
    run_time: float = 0.6,
) -> VGroup:
    """Fan of directional spokes from a cell, length/opacity ∝ |Q(s,a)|, the
    chosen action thickened and bright. Returns the spoke group (left on scene)."""
    center = _as_point(center_pt)
    rows = fan_layout(dir_values, chosen_idx, cell_w)
    spokes = []
    for r in rows:
        unit = np.array([np.cos(r["angle"]), np.sin(r["angle"]), 0.0])
        tip = center + unit * r["length"]
        col = C.VALUE if r["chosen"] else C.MUTED
        spoke = Arrow(center, tip, buff=0.0, color=col,
                      stroke_width=6.0 if r["chosen"] else 3.0,
                      tip_length=0.16 if r["chosen"] else 0.12,
                      max_tip_length_to_length_ratio=0.4)
        spoke.set_opacity(r["opacity"]).set_z_index(34)
        spokes.append(spoke)
    group = VGroup(*spokes)
    scene.play(FadeIn(group), run_time=run_time)
    return group


def reward_pulse(scene, pt, text: str, *, color: str, run_time: float = 0.5) -> None:
    """A brief expanding ring + number pop where a non-zero reward lands."""
    center = _as_point(pt)
    ring = Circle(radius=0.12, color=color, stroke_width=4.0).move_to(center).set_z_index(38)
    num = MathTex(text, font_size=24, color=color).move_to(center).set_z_index(39)
    scene.play(FadeIn(num, scale=0.6),
               ring.animate.scale(4.0).set_stroke(opacity=0.0),
               run_time=run_time)
    scene.play(FadeOut(num), run_time=run_time * 0.5)


def bind_pulse(scene, *mobs, color: str = C.TEAL, run_time: float = 0.4) -> None:
    """Cross-highlight: pulse a card term and its grid partner together so the
    eye binds them. No-op if nothing valid is passed."""
    valid = [m for m in mobs if m is not None]
    if not valid:
        return
    scene.play(*[Indicate(m, color=color, scale_factor=1.12) for m in valid],
               run_time=run_time)


class AgentTrail:
    """A fading breadcrumb path the spatial boards append to as the agent moves,
    so a rollout reads as a journey rather than teleporting dots."""

    def __init__(self, *, color: str = C.POLICY, radius: float = 0.07, keep: int = 8):
        self.color = color
        self.radius = radius
        self.keep = keep
        self.dots: list = []

    def drop(self, scene, pt) -> None:
        dot = Dot(_as_point(pt), radius=self.radius, color=self.color)
        dot.set_opacity(0.55).set_z_index(35)
        scene.add(dot)
        self.dots.append(dot)
        # Fade and forget the oldest so the trail stays short.
        if len(self.dots) > self.keep:
            old = self.dots.pop(0)
            scene.play(FadeOut(old), run_time=0.15)

    def clear(self, scene) -> None:
        if self.dots:
            scene.play(*[FadeOut(d) for d in self.dots], run_time=0.3)
        self.dots = []


def cross_dissolve(scene, old_mobs: list, new_mobs: list, *, run_time: float = 0.4) -> None:
    """Soft beat/episode transition: fade old out while fading new in together."""
    anims = [FadeOut(m) for m in (old_mobs or []) if m is not None]
    anims += [FadeIn(m) for m in (new_mobs or []) if m is not None]
    if anims:
        scene.play(*anims, run_time=run_time)
