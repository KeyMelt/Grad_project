"""Floating value chips over a FLAT 2D grid (STYLE_BIBLE §39.6).

The grid stays a crisp, undistorted top-down FrozenLake grid (the proven
`EnvironmentValueHeatmap`); value is shown as a number chip that *floats above*
its cell, with a soft drop shadow on the tile to sell the height. No camera tilt
(top-down sprites skew under perspective), no bars — just clean numbers that hover.

    hm = scene._build_value_heatmap(values=ZEROS)
    fv = FloatingValues(hm)
    fv.reveal_value(scene, 14, 1.00)        # one floating number (S2 back-fill)
    fv.set_values(scene, v_pi_list)         # the whole field hovering (S4 sweeps)
"""
from __future__ import annotations

from manim import (
    VGroup, Text, RoundedRectangle, Ellipse, UP, DOWN,
    FadeIn, FadeOut, Transform,
)

from manim_service.scenes.panels import VALUE_COLOR

_CHIP_BG = "#0B1220"


class FloatingValues:
    """Billboard-free floating value chips bound to an EnvironmentValueHeatmap."""

    def __init__(self, heatmap, *, number_size=24, float_h=0.30, shadow_drop=0.26):
        self.hm = heatmap
        self.number_size = number_size
        self.float_h = float_h          # chip lift above cell centre (× cell height)
        self.shadow_drop = shadow_drop  # shadow offset below cell centre (× cell h)
        self.chips: dict[int, VGroup] = {}
        self.shadows: dict[int, Ellipse] = {}
        # Hide the heatmap's own flat labels — the floating chips replace them.
        for lbl in getattr(heatmap, "labels", {}).values():
            lbl.set_opacity(0.0)
        for sh in getattr(heatmap, "label_shadows", {}).values():
            sh.set_opacity(0.0)

    # --- geometry ----------------------------------------------------------
    def _cell_center(self, state):
        return self.hm.cell_bbox(state).get_center()

    def _cell_h(self):
        return self.hm.cell_bbox(0).height

    def _make(self, state, value, color):
        c = self._cell_center(state)
        ch = self._cell_h()
        txt = Text(f"{value:.2f}", font_size=self.number_size, color=color)
        bg = RoundedRectangle(width=txt.width + 0.18, height=txt.height + 0.13,
                              corner_radius=0.06, fill_color=_CHIP_BG,
                              fill_opacity=0.95, stroke_width=0)
        chip = VGroup(bg, txt)
        txt.move_to(bg)
        chip.move_to(c + UP * ch * self.float_h)
        chip.set_z_index(6)
        shadow = Ellipse(width=bg.width * 0.72, height=ch * 0.14,
                         fill_color="#000000", fill_opacity=0.38, stroke_width=0)
        shadow.move_to(c + DOWN * ch * self.shadow_drop)
        shadow.set_z_index(5)
        return chip, shadow

    # --- S2: reveal one floating number (rises into place) -----------------
    def reveal_value(self, scene, state, value, *, color=VALUE_COLOR, run_time=0.5):
        chip, shadow = self._make(state, value, color)
        start = chip.copy().move_to(self._cell_center(state)).set_opacity(0.0)
        chip.become(start)
        self.chips[state] = chip
        self.shadows[state] = shadow
        target = self._make(state, value, color)[0]
        scene.add(shadow, chip)
        scene.play(FadeIn(shadow), Transform(chip, target), run_time=run_time)
        return chip

    # --- S4: spread / update the whole field -------------------------------
    def set_values(self, scene, values, *, color=VALUE_COLOR, run_time=1.0, eps=0.005):
        anims = []
        keep_c, keep_s = {}, {}
        terminal = set(getattr(self.hm, "_holes", set())) | {getattr(self.hm, "_goal", None)}
        for s in range(16):
            rc = divmod(s, 4)
            if rc in terminal:
                continue
            v = values[s]
            if v < eps:
                if s in self.chips:
                    anims += [FadeOut(self.chips[s]), FadeOut(self.shadows[s])]
                continue
            tgt_chip, tgt_sh = self._make(s, v, color)
            if s in self.chips:
                anims += [Transform(self.chips[s], tgt_chip)]
                keep_c[s], keep_s[s] = self.chips[s], self.shadows[s]
            else:
                scene.add(tgt_sh, tgt_chip)
                anims += [FadeIn(tgt_sh), FadeIn(tgt_chip, shift=UP * 0.12)]
                keep_c[s], keep_s[s] = tgt_chip, tgt_sh
        self.chips, self.shadows = keep_c, keep_s
        if anims:
            scene.play(*anims, run_time=run_time)
