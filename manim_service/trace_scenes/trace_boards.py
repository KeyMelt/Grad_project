"""Environment board adapters for the trace replay — REAL Gymnasium visuals.

Each board exposes a uniform interface the scene loop drives:
    .mob                      the mobject to FadeIn
    .place(scene, step)       initial agent placement / first observation
    .step(scene, step)        animate this step's transition (agent move / new hand)
    .center(state) -> point   move-aware cell centre (grid envs)
    .ring(state) -> Mobject    a highlight ring around a cell (grid envs)
    .is_spatial               True for grids (agent moves), False for Blackjack

FrozenLake  -> EnvironmentValueHeatmap (real ice/hole/goal tiles + elf hiker)
CliffWalking-> mountain sprite grid (mountain_bg/cliff/stool/cookie) + hiker elf
Blackjack   -> a card table reflecting the (player sum, dealer card, usable ace) obs
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import (
    DOWN, RIGHT, UP, Dot, FadeIn, FadeOut, Group, ImageMobject,
    Rectangle, RoundedRectangle, SurroundingRectangle, Text, Transform, VGroup,
)

from . import trace_common as C
from .taxi_board import TaxiBoard

_GYM_IMG = None


def _gym_img_dir() -> Path:
    global _GYM_IMG
    if _GYM_IMG is None:
        import gymnasium.envs.toy_text.cliffwalking as _cw
        _GYM_IMG = Path(_cw.__file__).resolve().parent / "img"
    return _GYM_IMG


# ============================================================ FrozenLake board
class FrozenLakeBoard:
    is_spatial = True
    # Fallback ONLY if a trace step carries no grid_metadata. The real map
    # (rows/cols/holes/goal) is read from the run's trace so the board reflects
    # the user's actual environment, never a hardcoded layout.
    _STD_HOLES = {(1, 1), (1, 3), (2, 3), (3, 0)}
    _STD_GOAL = (3, 3)

    def __init__(self, first_step=None, width=5.2, at=(-3.6, 0.2)):
        from manim_service.scenes.rl_visuals import EnvironmentValueHeatmap
        rows, cols, holes, goal, start = self._map_from_step(first_step)
        self._rows, self._cols = rows, cols
        self.hm = EnvironmentValueHeatmap(
            rows=rows, cols=cols, values=[0.0] * (rows * cols),
            holes=holes, goal=goal, start=start, width=width, label_precision=2)
        for lbl in self.hm.labels.values():
            lbl.set_opacity(0.0)
        for sh in self.hm.label_shadows.values():
            sh.set_opacity(0.0)
        self.hm.move_to([at[0], at[1], 0.0])
        self._ring = None
        self._shown: dict[tuple[int, int], float] = {}

    @classmethod
    def _map_from_step(cls, first_step):
        """Derive (rows, cols, holes, goal, start) from the trace's grid_metadata
        so the rendered map matches the user's actual run; fall back to the
        standard 4x4 FrozenLake map only when metadata is absent."""
        gm = (first_step or {}).get("grid_metadata") or {}
        cells = gm.get("cells")
        rows, cols = gm.get("rows"), gm.get("columns")
        if (isinstance(cells, list) and cells
                and isinstance(rows, int) and isinstance(cols, int)):
            holes, goal, start = set(), None, None
            for c in cells:
                rc = (c.get("row"), c.get("column"))
                tile = c.get("tile_type")
                if tile == "H":
                    holes.add(rc)
                elif tile == "G":
                    goal = rc
                elif tile == "S":
                    start = rc
            return rows, cols, holes, (goal or (rows - 1, cols - 1)), \
                (start or (0, 0))
        return 4, 4, set(cls._STD_HOLES), cls._STD_GOAL, (0, 0)

    @property
    def mob(self):
        return self.hm

    def center(self, state):
        return self.hm.cell_bbox(int(state)).get_center()

    def ring(self, state, *, color=C.VALUE, sw=5.0):
        return SurroundingRectangle(self.hm.cell_bbox(int(state)), color=color,
                                    buff=0.02, stroke_width=sw).set_z_index(30)

    def _target_values(self, step) -> dict[tuple[int, int], float]:
        """Accumulated (row, col) -> V values after this step, preferring the full
        table snapshot and overlaying the swept state's fresh value."""
        target = dict(self._shown)
        tb = step.get("tables") or {}
        after = tb.get("after")
        if isinstance(after, list) and after and isinstance(after[0], list):
            for i, row in enumerate(after):
                if row:
                    fv = C.as_float(row[0])
                    if fv is not None:
                        target[divmod(i, self._cols)] = fv
        eu = step.get("equation_update") or {}
        nv = C.as_float(eu.get("new_value"))
        st = step.get("state")
        if isinstance(st, int) and nv is not None:
            target[divmod(int(st), self._cols)] = nv
        return target

    def _apply_values(self, scene, step, *, run_time=0.3):
        """Make the value function visibly fill in: re-tint every overlay to its current
        magnitude and rebuild the number label only for cells that actually changed, so
        each DP step pops exactly the state it just backed up (no full-grid re-sweep)."""
        hm = self.hm
        target = self._target_values(step)
        changed = [(rc, v) for rc, v in target.items()
                   if rc in hm.value_overlays
                   and abs(self._shown.get(rc, 0.0) - v) > 1e-9]
        if not changed:
            return
        hm._values = {**hm._values, **target}
        anims = []
        # Re-tint all overlays (cheap) so the heat reflects the whole accumulated field.
        for rc, overlay in hm.value_overlays.items():
            v = target.get(rc, self._shown.get(rc, 0.0))
            anims.append(overlay.animate.set_fill(hm._tint_color,
                                                  opacity=hm._tint_alpha_for(v)))
        fs = max(10, int(hm._cell_w * 22))
        for rc, v in changed:
            # The heatmap Group was moved after construction, so _cell_center is stale;
            # the overlay's live centre is the true on-screen cell position.
            center = hm.value_overlays[rc].get_center()
            for old in (hm.labels.get(rc), hm.label_shadows.get(rc)):
                if old is not None and old in hm.submobjects:
                    hm.remove(old)
            lbl = Text(hm._format_value(v), font_size=fs, color=hm._label_font_color)
            if lbl.get_width() > hm._cell_w * 0.86:
                lbl.scale((hm._cell_w * 0.86) / lbl.get_width())
            lbl.move_to(center).set_z_index(4)
            sh = Rectangle(width=lbl.get_width() + 0.10, height=lbl.get_height() + 0.08,
                           fill_color=C.PANEL, fill_opacity=0.8, stroke_width=0)
            sh.move_to(center).set_z_index(3)
            hm.labels[rc], hm.label_shadows[rc] = lbl, sh
            hm.add(sh, lbl)
            anims += [FadeIn(sh), FadeIn(lbl)]
            self._shown[rc] = v
        scene.play(*anims, run_time=run_time)

    def place(self, scene, step, *, run_time=0.35):
        st = step.get("state", 0)
        self._ring = self.ring(st) if isinstance(st, int) else None
        if self._ring is not None:
            scene.play(FadeIn(self._ring), run_time=run_time)
        self._apply_values(scene, step)

    def step(self, scene, step, *, run_time=0.4):
        st = step.get("state")
        if isinstance(st, int):
            new_ring = self.ring(st)
            if getattr(self, "_ring", None) is not None:
                scene.play(Transform(self._ring, new_ring), run_time=run_time * 0.6)
            else:
                self._ring = new_ring
                scene.play(FadeIn(self._ring), run_time=run_time * 0.6)
        self._apply_values(scene, step)

    # -- fine-grained hooks for the paced step director ---------------------
    def focus(self, scene, state, *, run_time=0.5):
        """Move the focus ring onto the state being backed up (no value fill yet)."""
        if not isinstance(state, int):
            return
        new_ring = self.ring(state)
        if getattr(self, "_ring", None) is not None:
            scene.play(Transform(self._ring, new_ring), run_time=run_time)
        else:
            self._ring = new_ring
            scene.play(FadeIn(self._ring), run_time=run_time)

    def flash(self, scene, state, *, color=C.TEAL, run_time=0.4):
        """Transient highlight of a neighbour cell being LOOKED UP (V(s'))."""
        if not isinstance(state, int):
            return
        rect = SurroundingRectangle(self.hm.cell_bbox(int(state)), color=color,
                                    buff=0.02, stroke_width=4.0).set_z_index(29)
        scene.play(FadeIn(rect), run_time=run_time * 0.45)
        scene.play(FadeOut(rect), run_time=run_time * 0.55)

    def commit(self, scene, step, *, run_time=0.5):
        """Write the freshly-computed value into the grid cell."""
        self._apply_values(scene, step, run_time=run_time)


# ============================================================ CliffWalking board
class CliffWalkingBoard:
    is_spatial = True
    ROWS, COLS = 4, 12
    GOAL_RC = (3, 11)
    _CLIFF_RC = {(3, c) for c in range(1, 11)}

    def __init__(self, width=9.6, at=(0.0, 1.35)):
        img = _gym_img_dir()
        self.cw = width / self.COLS
        self.ch = self.cw
        self._img = img
        self.cells: list = []
        grid = Group()
        for r in range(self.ROWS):
            for c in range(self.COLS):
                cell = self._compose(r, c)
                cell.move_to(self._center0(r, c))
                self.cells.append(cell)
                grid.add(cell)
        self.group = grid
        self.group.move_to([at[0], at[1], 0.0])
        self.elf = None
        self._dir = "up"
        self._state = None

    def _spr(self, name, *, scale=1.0):
        m = ImageMobject(str(self._img / name))
        m.set_height(self.ch * scale)
        return m

    def _compose(self, r, c):
        cell = Group()
        cell.add(self._spr("mountain_bg1.png" if (r + c) % 2 == 0 else "mountain_bg2.png"))
        if (r, c) in self._CLIFF_RC:
            cell.add(self._spr("mountain_cliff.png"))
        elif r == 2 and 1 <= c <= 10:
            cell.add(self._spr("mountain_near-cliff1.png" if c % 2 == 0
                               else "mountain_near-cliff2.png"))
        if (r, c) == (3, 0):
            cell.add(self._spr("stool.png", scale=0.85))
        if (r, c) == self.GOAL_RC:
            cell.add(self._spr("cookie.png", scale=0.85))
        return cell

    def _center0(self, r, c):
        return np.array([(c - (self.COLS - 1) / 2) * self.cw,
                         -(r - (self.ROWS - 1) / 2) * self.ch, 0.0])

    @property
    def mob(self):
        return self.group

    def center(self, state):
        r, c = divmod(int(state), self.COLS)
        return self.cells[r * self.COLS + c].get_center()

    def ring(self, state, *, color=C.STATE, sw=3.5):
        r, c = divmod(int(state), self.COLS)
        return SurroundingRectangle(self.cells[r * self.COLS + c], color=color,
                                    buff=0.0, stroke_width=sw).set_z_index(30)

    def _elf(self, direction):
        m = ImageMobject(str(self._img / f"elf_{direction}.png"))
        m.set_height(self.ch * 0.78)
        m.set_z_index(40)
        return m

    def place(self, scene, step, *, run_time=0.35):
        st = int(step.get("state", 36))
        d = C.action_dir("CliffWalking", step.get("action"))
        elf = self._elf(d).move_to(self.center(st))
        self.elf, self._dir, self._state = elf, d, st
        scene.play(FadeIn(elf, scale=0.7), run_time=run_time)

    def step(self, scene, step, *, run_time=0.4):
        ns = step.get("next_state")
        if not isinstance(ns, int):
            return
        d = C.action_dir("CliffWalking", step.get("action"))
        if self.elf is None:
            self.place(scene, step, run_time=run_time)
        if d != self._dir:
            new = self._elf(d).move_to(self.elf.get_center())
            scene.play(FadeOut(self.elf), FadeIn(new), run_time=run_time * 0.3)
            self.elf, self._dir = new, d
        dot = Dot(self.elf.get_center(), radius=self.cw * 0.09,
                  color=C.POLICY).set_opacity(0.5).set_z_index(35)
        scene.add(dot)
        scene.play(self.elf.animate.move_to(self.center(ns)), run_time=run_time)
        self._state = ns

    def flash(self, scene, state, *, color=C.TEAL, run_time=0.4):
        """Transient highlight of the bootstrap cell Q(s', ·) being looked up."""
        try:
            r, c = divmod(int(state), self.COLS)
        except (TypeError, ValueError):
            return
        rect = SurroundingRectangle(self.cells[r * self.COLS + c], color=color,
                                    buff=0.0, stroke_width=4.0).set_z_index(39)
        scene.play(FadeIn(rect), run_time=run_time * 0.45)
        scene.play(FadeOut(rect), run_time=run_time * 0.55)


# ============================================================ Blackjack board
class BlackjackBoard:
    """Non-spatial board for Blackjack-v1.

    Visual content comes exclusively from real Gymnasium env.render() frames
    captured during execution and stored as PNGs at step["frame_path"].  When a
    frame file is accessible, it is displayed as the background image with a
    small text overlay for key metadata.  When the file is absent or not
    reachable from the manim_service filesystem (e.g. Docker without a shared
    volume), a text-only observation panel is shown instead.  No synthetic card
    tables, card sprites, or simulated game-state visuals are produced.
    """

    is_spatial = False

    def __init__(self, width=5.4, at=(-3.4, 0.2)):
        self._at = at
        self._width = width
        self.panel = self._placeholder()
        self.panel.move_to([at[0], at[1], 0.0])

    # ---- placeholder shown before the first step is placed ------------------

    def _placeholder(self):
        box = RoundedRectangle(
            width=self._width, height=4.4, corner_radius=0.16,
            fill_color=C.PANEL, fill_opacity=1.0,
            stroke_color=C.REWARD, stroke_width=1.6,
        )
        title = Text("Blackjack-v1", font_size=20, color=C.REWARD)
        title.move_to(box.get_center())
        return Group(box, title)

    # ---- frame-aware panel builder ------------------------------------------

    def _frame_panel(self, step: dict):
        """Build panel from a real Gymnasium frame if available, else text-only."""
        from pathlib import Path as _Path
        frame_path = step.get("frame_path") or ""
        mc = C.mc_pieces(step) or {}

        if frame_path and _Path(frame_path).exists():
            return self._panel_with_frame(frame_path, mc)
        return self._text_only_panel(mc)

    def _panel_with_frame(self, frame_path: str, mc: dict):
        """Real Gymnasium env.render() frame as background + text overlay."""
        img = ImageMobject(frame_path)
        img.set_width(self._width - 0.1)

        psum = mc.get("player_sum")
        dealer = mc.get("dealer_card")
        ace = mc.get("usable_ace")
        action = mc.get("action_label") or ""
        reward = mc.get("reward")

        parts = []
        if psum is not None:
            parts.append(f"player {psum}")
        if dealer is not None:
            parts.append(f"dealer {dealer}")
        if ace is not None:
            parts.append("ace" if ace else "no ace")
        if action:
            parts.append(action)
        if reward is not None:
            parts.append(f"r={C.fmt(reward)}")
        label_str = "  ·  ".join(parts) if parts else "Blackjack-v1"

        label = Text(label_str, font_size=14, color=C.TEXT)
        label.next_to(img, DOWN, buff=0.08)
        return Group(img, label)

    def _text_only_panel(self, mc: dict):
        """Text-only observation panel — no synthetic card graphics."""
        psum = mc.get("player_sum")
        dealer = mc.get("dealer_card")
        ace = mc.get("usable_ace")
        action = mc.get("action_label") or ""
        reward = mc.get("reward")

        box = RoundedRectangle(
            width=self._width, height=4.4, corner_radius=0.16,
            fill_color=C.PANEL, fill_opacity=1.0,
            stroke_color=C.REWARD, stroke_width=1.6,
        )
        title = Text("Blackjack-v1", font_size=18, color=C.REWARD)
        note = Text("(frame unavailable)", font_size=12, color=C.MUTED)

        rows = VGroup(title, note)
        if psum is not None:
            rows.add(Text(f"Player sum: {psum}", font_size=16, color=C.TEXT))
        if dealer is not None:
            rows.add(Text(f"Dealer shows: {dealer}", font_size=16, color=C.TEXT))
        if ace is not None:
            rows.add(Text("Usable ace: " + ("yes" if ace else "no"),
                          font_size=16, color=C.MUTED))
        if action:
            rows.add(Text(f"Action: {action}", font_size=16, color=C.ACTION))
        if reward is not None:
            rows.add(Text(f"Reward: {C.fmt(reward)}", font_size=16, color=C.REWARD))

        rows.arrange(DOWN, buff=0.18)
        rows.move_to(box.get_center())
        return Group(box, rows)

    # ---- board interface used by the scene loop -----------------------------

    @property
    def mob(self):
        return self.panel

    def center(self, state):
        return self.panel.get_center()

    def ring(self, state, *, color=C.STATE, sw=3.0):
        return SurroundingRectangle(self.panel, color=color, buff=0.05, stroke_width=sw)

    def place(self, scene, step, *, run_time=0.35):
        new = self._frame_panel(step).move_to(self.panel.get_center())
        scene.remove(self.panel)
        self.panel = new
        scene.add(self.panel)

    def step(self, scene, step, *, run_time=0.4):
        # FadeOut/FadeIn (not ReplacementTransform): when consecutive steps share
        # the same observation the two panels are identical, and a transform
        # between identical mobjects renders ZERO frames — manim then lists a
        # partial-movie file it never writes, which crashes combine_to_movie.
        # A fade always produces real frames. (Same lesson as the TaxiGrid fix.)
        new = self._frame_panel(step).move_to(self.panel.get_center())
        scene.play(FadeOut(self.panel), FadeIn(new), run_time=run_time)
        self.panel = new


def make_board(env: str, first_step: dict):
    if env == "Taxi":
        return TaxiBoard(first_step)
    if env == "CliffWalking":
        return CliffWalkingBoard()
    if env == "Blackjack":
        return BlackjackBoard()
    # FrozenLake reads its actual map (rows/cols/holes/goal) from the run's
    # trace metadata rather than assuming the standard 4x4 layout.
    return FrozenLakeBoard(first_step)
