"""Isometric 3D value grid with the REAL FrozenLake sprites (STYLE_BIBLE §39.5/§39.6).

The actual gymnasium ice/hole/goal tiles laid flat on the floor and viewed
isometrically; the elf sprite walks it; values are shown as BILLBOARDED floating
numbers (always orthogonal to the camera, readable from any angle — no bars).
Use inside a ThreeDScene (see DPE3DSegmentScene). Equations/captions are a 2D HUD.

    g = IsoValueGrid()
    scene.add(g.tiles)
    g.place_elf(scene, 0); g.move_elf(scene, 1, "right")
    g.reveal_value(scene, 14, 1.00)          # one floating number (S2)
    g.set_values(scene, sweep_values)        # spread numbers across the grid (S4)
"""
from __future__ import annotations

from manim import (
    Group, VGroup, Text, RoundedRectangle, ImageMobject,
    FadeIn, FadeOut, Transform,
)

from manim_service.scenes.panels import VALUE_COLOR


def _asset_dir():
    from manim_service.scenes.rl_visuals import _gymnasium_toy_text_asset_dir
    return _gymnasium_toy_text_asset_dir()


class IsoValueGrid:
    """Real-sprite isometric FrozenLake grid with billboarded floating value labels."""

    def __init__(self, rows=4, cols=4, *, holes=frozenset({5, 7, 11, 12}), goal=15,
                 cell=1.0, float_z=0.5, number_size=26, origin=(0.0, 0.0)):
        self.rows, self.cols = rows, cols
        self.holes, self.goal = set(holes), goal
        self.cell, self.float_z, self.number_size = cell, float_z, number_size
        self.ox, self.oy = origin
        ad = _asset_dir()
        self.tiles = Group()
        for s in range(rows * cols):
            x, y = self.cell_xy(s)
            img = "hole.png" if s in self.holes else ("goal.png" if s == goal else "ice.png")
            t = ImageMobject(str(ad / img))
            t.set_height(cell * 1.02)
            t.move_to([x, y, 0.0])
            self.tiles.add(t)
        self._elf_path = str(ad / "elf_down.png")
        self.numbers: dict[int, VGroup] = {}
        self.agent: ImageMobject | None = None

    def cell_xy(self, state: int):
        r, c = divmod(state, self.cols)
        return ((c - (self.cols - 1) / 2) * self.cell + self.ox,
                ((self.rows - 1) / 2 - r) * self.cell + self.oy)

    def _num_mob(self, state, value, color):
        x, y = self.cell_xy(state)
        txt = Text(f"{value:.2f}", font_size=self.number_size, color=color)
        bg = RoundedRectangle(width=txt.width + 0.2, height=txt.height + 0.14,
                              corner_radius=0.07, fill_color="#0B1220",
                              fill_opacity=0.92, stroke_width=0)
        g = VGroup(bg, txt)
        txt.move_to(bg)
        g.move_to([x, y, self.float_z])
        return g

    # --- S2: reveal one floating number -----------------------------------
    def reveal_value(self, scene, state, value, *, color=VALUE_COLOR, run_time=0.5):
        g = self._num_mob(state, value, color)
        self.numbers[state] = g
        scene.add_fixed_orientation_mobjects(g)
        scene.play(FadeIn(g, scale=1.15), run_time=run_time)
        return g

    # --- S4: spread/update numbers across the grid ------------------------
    def set_values(self, scene, values, *, color=VALUE_COLOR, run_time=1.0, eps=0.005):
        anims = []
        keep = {}
        for s in range(self.rows * self.cols):
            if s in self.holes or s == self.goal:
                continue
            v = values[s]
            if v < eps:
                if s in self.numbers:
                    anims.append(FadeOut(self.numbers[s]))
                continue
            target = self._num_mob(s, v, color)
            if s in self.numbers:
                anims.append(Transform(self.numbers[s], target))
                keep[s] = self.numbers[s]
            else:
                scene.add_fixed_orientation_mobjects(target)
                anims.append(FadeIn(target, scale=1.1))
                keep[s] = target
        self.numbers = keep
        if anims:
            scene.play(*anims, run_time=run_time)

    # --- the elf (billboarded) --------------------------------------------
    def place_elf(self, scene, state, *, direction="down", run_time=0.5, height=0.8):
        x, y = self.cell_xy(state)
        elf = ImageMobject(self._elf_path)
        elf.set_height(height)
        elf.move_to([x, y, 0.42])
        self.agent = elf
        scene.add_fixed_orientation_mobjects(elf)
        scene.play(FadeIn(elf, scale=0.7), run_time=run_time)
        return elf

    def move_elf(self, scene, state, *, direction=None, run_time=0.5):
        if self.agent is None:
            return self.place_elf(scene, state, run_time=run_time)
        x, y = self.cell_xy(state)
        scene.play(self.agent.animate.move_to([x, y, 0.42]), run_time=run_time)
