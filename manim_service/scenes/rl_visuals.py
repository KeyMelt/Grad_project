"""RL-specific visualization classes for concept video scenes.

Designed to work with SynchronizedFocusGroup for three-way synchronized
animations linking equations, environment visuals, and these charts.

Import via:
    from manim_service.scenes import BackupDiagram, PolicyArrowGrid, ...
"""
from __future__ import annotations

import numpy as np
from manim import (
    AnimationGroup,
    Arrow,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    Mobject,
    Rectangle,
    Scene,
    SurroundingRectangle,
    Text,
    VGroup,
    Write,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
)

try:
    from manim import GREY_A
except ImportError:
    GREY_A = "#BBBBBB"  # type: ignore[assignment]

from .panels import (
    ACTION_COLOR,
    BG_GRID,
    BG_PANEL,
    CODE_ACCENT,
    OPACITY_BACKGROUND,
    OPACITY_PRIMARY,
    OPACITY_SECONDARY,
    PENALTY_COLOR,
    POLICY_COLOR,
    REWARD_COLOR,
    STATE_COLOR,
    VALUE_COLOR,
)


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------


def _lerp_hex(c1: str, c2: str, t: float) -> str:
    """Linearly interpolate between two hex color strings. t in [0, 1]."""
    t = max(0.0, min(1.0, t))
    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"


# ---------------------------------------------------------------------------
# BackupDiagram
# ---------------------------------------------------------------------------


class BackupDiagram(VGroup):
    """S&B-style backup diagram: state → action → state' tree.

    Draws open state circles, filled action dots, and connecting lines in
    the Sutton & Barto textbook style. The tree shows n_actions branches
    from the root state, each with n_outcomes next-state leaves.

    Attributes:
        root_node:      Circle — the root state node.
        action_nodes:   list[Dot] — one per action branch.
        outcome_nodes:  list[list[Circle]] — outcome_nodes[i][j] is the
                        j-th next-state node under action i.
        root_edges:     VGroup of Lines (root → action nodes).
        subtree_edges:  list[VGroup] — one per action, edges to its outcomes.

    Usage::

        diag = BackupDiagram(n_actions=4, n_outcomes=2)
        self.add(diag)
        self.play(*diag.highlight_action(2))
        self.play(*diag.dim_all_except_action(2))
        self.play(*diag.reset_opacity())
    """

    def __init__(
        self,
        n_actions: int = 4,
        n_outcomes: int = 2,
        *,
        root_label: str = "s",
        action_labels: list[str] | None = None,
        outcome_labels: list[list[str]] | None = None,
        total_width: float = 6.0,
        level_height: float = 1.5,
        state_radius: float = 0.22,
        action_radius: float = 0.12,
        state_color: str = STATE_COLOR,
        action_color: str = ACTION_COLOR,
        line_color: str = GREY_A,
        label_font_size: int = 18,
    ) -> None:
        super().__init__()

        n_leaves = n_actions * n_outcomes
        leaf_gap = total_width / n_leaves
        action_gap = total_width / n_actions

        # --- Positions ---
        root_pos = np.array([0.0, level_height, 0.0])

        action_pos: list[np.ndarray] = [
            np.array([-total_width / 2 + (i + 0.5) * action_gap, 0.0, 0.0])
            for i in range(n_actions)
        ]

        outcome_pos: list[list[np.ndarray]] = []
        for i in range(n_actions):
            ax = action_pos[i][0]
            row: list[np.ndarray] = []
            for j in range(n_outcomes):
                ox = ax - ((n_outcomes - 1) / 2 - j) * leaf_gap
                row.append(np.array([ox, -level_height, 0.0]))
            outcome_pos.append(row)

        # --- Root ---
        self.root_node = Circle(
            radius=state_radius,
            stroke_color=state_color,
            stroke_width=2.5,
            fill_opacity=0.15,
            fill_color=state_color,
        ).move_to(root_pos)
        root_lbl = MathTex(root_label, font_size=label_font_size, color=state_color)
        root_lbl.move_to(root_pos)

        # --- Root edges ---
        self.root_edges = VGroup(*[
            Line(
                root_pos + DOWN * state_radius,
                action_pos[i] + UP * action_radius,
                stroke_color=line_color,
                stroke_width=1.5,
                stroke_opacity=0.7,
            )
            for i in range(n_actions)
        ])

        # --- Action nodes + labels ---
        self.action_nodes: list[Dot] = [
            Dot(point=action_pos[i], radius=action_radius, color=action_color)
            for i in range(n_actions)
        ]
        action_lbl_mobs: list[Text] = []
        for i in range(n_actions):
            lbl = (action_labels[i] if action_labels and i < len(action_labels)
                   else f"a{i}")
            m = Text(lbl, font_size=label_font_size - 2, color=action_color)
            m.next_to(self.action_nodes[i], LEFT, buff=0.08)
            action_lbl_mobs.append(m)

        # --- Outcome nodes + edges ---
        self.outcome_nodes: list[list[Circle]] = []
        self.subtree_edges: list[VGroup] = []
        outcome_lbl_mobs: list[MathTex] = []

        for i in range(n_actions):
            row_nodes: list[Circle] = []
            row_edges = VGroup()
            for j in range(n_outcomes):
                lbl = (outcome_labels[i][j]
                       if outcome_labels
                       and i < len(outcome_labels)
                       and j < len(outcome_labels[i])
                       else "s'")
                circ = Circle(
                    radius=state_radius * 0.88,
                    stroke_color=state_color,
                    stroke_width=2.0,
                    fill_opacity=0.12,
                    fill_color=state_color,
                ).move_to(outcome_pos[i][j])
                olbl = MathTex(lbl, font_size=label_font_size - 4, color=state_color)
                olbl.move_to(outcome_pos[i][j])
                outcome_lbl_mobs.append(olbl)

                edge = Line(
                    action_pos[i] + DOWN * action_radius,
                    outcome_pos[i][j] + UP * (state_radius * 0.88),
                    stroke_color=line_color,
                    stroke_width=1.2,
                    stroke_opacity=0.6,
                )
                row_nodes.append(circ)
                row_edges.add(edge)

            self.outcome_nodes.append(row_nodes)
            self.subtree_edges.append(row_edges)

        # --- Add to VGroup in z-order (back-to-front) ---
        self.add(self.root_edges)
        for grp in self.subtree_edges:
            self.add(grp)
        self.add(self.root_node, root_lbl)
        for i, dot in enumerate(self.action_nodes):
            self.add(dot)
            self.add(action_lbl_mobs[i])
        for row in self.outcome_nodes:
            for circ in row:
                self.add(circ)
        for lbl in outcome_lbl_mobs:
            self.add(lbl)

    # -- highlight / dim helpers (return animation lists for scene.play) --

    def highlight_action(self, idx: int, *, color: str = ACTION_COLOR) -> list:
        """Return animations that Indicate the idx-th action node."""
        return [Indicate(self.action_nodes[idx], color=color, scale_factor=1.4)]

    def highlight_outcome(self, action_idx: int, outcome_idx: int) -> list:
        """Return animations that Indicate a specific next-state node."""
        node = self.outcome_nodes[action_idx][outcome_idx]
        return [Indicate(node, color=REWARD_COLOR, scale_factor=1.3)]

    def dim_all_except_action(self, idx: int) -> list:
        """Dim all branches except the idx-th action branch."""
        anims: list = []
        for i, node in enumerate(self.action_nodes):
            if i != idx:
                anims.append(node.animate.set_opacity(OPACITY_SECONDARY))
                for circ in self.outcome_nodes[i]:
                    anims.append(circ.animate.set_opacity(OPACITY_SECONDARY))
                anims.append(
                    self.subtree_edges[i].animate.set_opacity(OPACITY_BACKGROUND)
                )
        return anims

    def reset_opacity(self) -> list:
        """Return all nodes to OPACITY_PRIMARY."""
        anims: list = [self.root_node.animate.set_opacity(OPACITY_PRIMARY)]
        for node in self.action_nodes:
            anims.append(node.animate.set_opacity(OPACITY_PRIMARY))
        for row in self.outcome_nodes:
            for circ in row:
                anims.append(circ.animate.set_opacity(OPACITY_PRIMARY))
        for grp in self.subtree_edges:
            anims.append(grp.animate.set_opacity(OPACITY_PRIMARY))
        return anims


# ---------------------------------------------------------------------------
# PolicyArrowGrid
# ---------------------------------------------------------------------------


class PolicyArrowGrid(VGroup):
    """Grid showing the greedy policy with directional arrows per cell.

    Action index convention (matches FrozenLake-v1 / CliffWalking-v0):
        0 = LEFT, 1 = DOWN, 2 = RIGHT, 3 = UP

    Attributes:
        cells:  dict[(row, col) → Rectangle] — background cell rectangles.
        arrows: dict[(row, col) → Arrow | None] — policy arrow per cell.

    Usage::

        grid = PolicyArrowGrid(4, 4, policy=[0]*16,
                               holes={(1,1),(1,3),(2,3),(3,0)},
                               goal=(3, 3))
        self.add(grid)
        grid.update_policy(self, new_policy_list)
    """

    _DIR = {0: LEFT, 1: DOWN, 2: RIGHT, 3: UP}

    def __init__(
        self,
        rows: int = 4,
        cols: int = 4,
        *,
        policy: dict | list | None = None,
        holes: set[tuple[int, int]] | None = None,
        goal: tuple[int, int] | None = None,
        width: float = 4.8,
        cell_color: str = BG_GRID,
        arrow_color: str = POLICY_COLOR,
        hole_color: str = PENALTY_COLOR,
        goal_color: str = REWARD_COLOR,
        stroke_color: str = STATE_COLOR,
        arrow_scale: float = 0.35,
    ) -> None:
        super().__init__()

        self._rows = rows
        self._cols = cols
        self._holes: set[tuple[int, int]] = holes or set()
        self._goal = goal
        self._cell_w = (width - 0.1) / cols
        self._cell_h = self._cell_w
        self._arrow_color = arrow_color
        self._arrow_scale = arrow_scale
        self._stroke_color = stroke_color
        self._cell_color = cell_color
        self._hole_color = hole_color
        self._goal_color = goal_color

        self._policy: dict[tuple[int, int], int] = self._normalize_policy(policy)
        self.cells: dict[tuple[int, int], Rectangle] = {}
        self.arrows: dict[tuple[int, int], Arrow | None] = {}

        for r in range(rows):
            for c in range(cols):
                is_hole = (r, c) in self._holes
                is_goal = (r, c) == goal
                fill = (hole_color if is_hole
                        else goal_color if is_goal
                        else cell_color)
                fill_op = 0.7 if (is_hole or is_goal) else 0.22
                cell = Rectangle(
                    width=self._cell_w - 0.04,
                    height=self._cell_h - 0.04,
                    fill_color=fill,
                    fill_opacity=fill_op,
                    stroke_color=stroke_color,
                    stroke_width=1.0,
                ).move_to(self._cell_center(r, c))
                self.cells[(r, c)] = cell
                self.add(cell)

        for (r, c), action in self._policy.items():
            if (r, c) not in self._holes and (r, c) != goal:
                arr = self._make_arrow(r, c, action)
                self.arrows[(r, c)] = arr
                if arr is not None:
                    self.add(arr)

    def _normalize_policy(
        self, policy: dict | list | None
    ) -> dict[tuple[int, int], int]:
        if policy is None:
            return {}
        if isinstance(policy, list):
            return {divmod(idx, self._cols): a for idx, a in enumerate(policy)}
        return dict(policy)

    def _cell_center(self, r: int, c: int) -> np.ndarray:
        return np.array([
            (c - self._cols / 2 + 0.5) * self._cell_w,
            -(r - self._rows / 2 + 0.5) * self._cell_h,
            0.0,
        ])

    def _make_arrow(self, r: int, c: int, action: int) -> Arrow | None:
        direction = self._DIR.get(action)
        if direction is None:
            return None
        center = self._cell_center(r, c)
        half = self._cell_w * self._arrow_scale / 2
        return Arrow(
            start=center - direction * half,
            end=center + direction * half,
            buff=0,
            color=self._arrow_color,
            stroke_width=2.0,
            max_tip_length_to_length_ratio=0.4,
        )

    def update_policy(
        self,
        scene: Scene,
        new_policy: dict | list,
        *,
        run_time: float = 0.8,
    ) -> None:
        """Animate policy arrows updating to new_policy."""
        old_arrows = [a for a in self.arrows.values() if a is not None]
        if old_arrows:
            scene.play(*[FadeOut(a) for a in old_arrows],
                       run_time=run_time * 0.4)
        for a in old_arrows:
            if a in self.submobjects:
                self.remove(a)

        self._policy = self._normalize_policy(new_policy)
        self.arrows.clear()
        new_mobs: list[Arrow] = []
        for (r, c), action in self._policy.items():
            if (r, c) not in self._holes and (r, c) != self._goal:
                arr = self._make_arrow(r, c, action)
                self.arrows[(r, c)] = arr
                if arr is not None:
                    self.add(arr)
                    new_mobs.append(arr)

        if new_mobs:
            scene.play(
                LaggedStart(*[FadeIn(a) for a in new_mobs], lag_ratio=0.04),
                run_time=run_time * 0.6,
            )

    def highlight_cell(self, r: int, c: int, *, color: str = ACTION_COLOR) -> list:
        """Return animations that Indicate the cell at (r, c)."""
        cell = self.cells.get((r, c))
        return [Indicate(cell, color=color)] if cell is not None else []


# ---------------------------------------------------------------------------
# ValueHeatmap
# ---------------------------------------------------------------------------


class ValueHeatmap(VGroup):
    """Grid with cells colored by state value and numerical labels.

    Cells interpolate between low_color (min value) and high_color (max
    value). If neg_color is set and values go negative, the negative range
    separately interpolates toward neg_color.

    Attributes:
        cells:  dict[(row, col) → Rectangle] — colored cell rectangles.
        labels: dict[(row, col) → Text] — value text inside each cell.

    Usage::

        hm = ValueHeatmap(4, 4, values=[0.0]*16, holes={(1,1)})
        self.add(hm)
        hm.update_values(self, new_values_list)
    """

    def __init__(
        self,
        rows: int = 4,
        cols: int = 4,
        *,
        values: dict | list | None = None,
        holes: set[tuple[int, int]] | None = None,
        terminal: set[tuple[int, int]] | None = None,
        width: float = 4.8,
        low_color: str = BG_GRID,
        high_color: str = VALUE_COLOR,
        neg_color: str | None = PENALTY_COLOR,
        label_font_size: int = 16,
        label_precision: int = 2,
        stroke_color: str = STATE_COLOR,
    ) -> None:
        super().__init__()

        self._rows = rows
        self._cols = cols
        self._holes: set[tuple[int, int]] = holes or set()
        self._terminal: set[tuple[int, int]] = terminal or set()
        self._cell_w = (width - 0.1) / cols
        self._cell_h = self._cell_w
        self._low_color = low_color
        self._high_color = high_color
        self._neg_color = neg_color
        self._label_font_size = label_font_size
        self._label_precision = label_precision
        self._stroke_color = stroke_color

        self._values: dict[tuple[int, int], float] = self._normalize_values(values)
        self.cells: dict[tuple[int, int], Rectangle] = {}
        self.labels: dict[tuple[int, int], Text] = {}

        for r in range(rows):
            for c in range(cols):
                center = self._cell_center(r, c)
                if (r, c) in self._holes:
                    cell = Rectangle(
                        width=self._cell_w - 0.04,
                        height=self._cell_h - 0.04,
                        fill_color=PENALTY_COLOR,
                        fill_opacity=0.5,
                        stroke_color=stroke_color,
                        stroke_width=1.0,
                    ).move_to(center)
                    self.cells[(r, c)] = cell
                    self.add(cell)
                    continue

                v = self._values.get((r, c), 0.0)
                fill_color, fill_op = self._value_to_color(v)
                cell = Rectangle(
                    width=self._cell_w - 0.04,
                    height=self._cell_h - 0.04,
                    fill_color=fill_color,
                    fill_opacity=fill_op,
                    stroke_color=stroke_color,
                    stroke_width=1.0,
                ).move_to(center)
                self.cells[(r, c)] = cell
                self.add(cell)

                lbl = Text(
                    f"{v:.{label_precision}f}",
                    font_size=label_font_size,
                    color=WHITE,
                ).move_to(center)
                self.labels[(r, c)] = lbl
                self.add(lbl)

    def _normalize_values(
        self, values: dict | list | None
    ) -> dict[tuple[int, int], float]:
        if values is None:
            return {}
        if isinstance(values, list):
            result: dict[tuple[int, int], float] = {}
            for idx, v in enumerate(values):
                if v is not None:
                    result[divmod(idx, self._cols)] = float(v)
            return result
        return {k: float(v) for k, v in values.items() if v is not None}

    def _cell_center(self, r: int, c: int) -> np.ndarray:
        return np.array([
            (c - self._cols / 2 + 0.5) * self._cell_w,
            -(r - self._rows / 2 + 0.5) * self._cell_h,
            0.0,
        ])

    def _value_to_color(self, v: float) -> tuple[str, float]:
        if not self._values:
            return self._low_color, 0.25
        all_vals = [x for x in self._values.values()]
        vmin, vmax = min(all_vals), max(all_vals)
        if vmax == vmin:
            return self._low_color, 0.25
        if self._neg_color and vmin < 0:
            if v < 0:
                t = abs(v) / abs(vmin) if vmin != 0 else 0.0
                return _lerp_hex(self._low_color, self._neg_color, t * 0.85), 0.55
            t = v / vmax if vmax > 0 else 0.0
            return _lerp_hex(self._low_color, self._high_color, t * 0.85), 0.4 + t * 0.5
        t = (v - vmin) / (vmax - vmin)
        return _lerp_hex(self._low_color, self._high_color, t), 0.28 + t * 0.62

    def update_values(
        self,
        scene: Scene,
        new_values: dict | list,
        *,
        run_time: float = 1.0,
    ) -> None:
        """Animate cells recoloring and labels updating to reflect new_values."""
        self._values = self._normalize_values(new_values)

        # Fade out old labels + recolor cells simultaneously
        cell_anims: list = []
        old_label_anims: list = []
        for (r, c), cell in self.cells.items():
            if (r, c) in self._holes:
                continue
            v = self._values.get((r, c), 0.0)
            fill_color, fill_op = self._value_to_color(v)
            cell_anims.append(cell.animate.set_fill(fill_color, opacity=fill_op))
        for lbl in self.labels.values():
            old_label_anims.append(FadeOut(lbl))

        scene.play(
            AnimationGroup(*cell_anims, *old_label_anims),
            run_time=run_time,
        )

        # Remove old label mobjects and add new ones
        for lbl in self.labels.values():
            if lbl in self.submobjects:
                self.remove(lbl)
        self.labels.clear()

        new_label_mobs: list[Text] = []
        for (r, c) in self.cells:
            if (r, c) in self._holes:
                continue
            v = self._values.get((r, c), 0.0)
            lbl = Text(
                f"{v:.{self._label_precision}f}",
                font_size=self._label_font_size,
                color=WHITE,
            ).move_to(self._cell_center(r, c))
            self.labels[(r, c)] = lbl
            self.add(lbl)
            new_label_mobs.append(lbl)

        if new_label_mobs:
            scene.play(
                LaggedStart(*[FadeIn(m) for m in new_label_mobs], lag_ratio=0.03),
                run_time=run_time * 0.4,
            )


# ---------------------------------------------------------------------------
# QValueTable
# ---------------------------------------------------------------------------


class QValueTable(VGroup):
    """2D table of Q(s, a) values with state rows and action columns.

    Suitable for up to ~12 states before the table becomes too dense for
    on-screen readability. For larger environments, pass a subset of states.

    Attributes:
        cells:       dict[(state_idx, action_idx) → Text] — value Text mobjects.
        row_headers: list[Text] — one per state row.
        col_headers: list[Text] — one per action column.

    Usage::

        qt = QValueTable(
            n_states=8, n_actions=4,
            q_values=[[0.0]*4]*8,
            state_labels=[f"s{i}" for i in range(8)],
            action_labels=["←", "↓", "→", "↑"],
        )
        self.add(qt)
        self.play(*qt.highlight_row(self, 3))
        qt.update_cell(self, 3, 2, 0.75)
    """

    def __init__(
        self,
        n_states: int,
        n_actions: int,
        *,
        q_values: list[list[float]] | None = None,
        state_labels: list[str] | None = None,
        action_labels: list[str] | None = None,
        cell_width: float = 0.80,
        cell_height: float = 0.45,
        header_color: str = STATE_COLOR,
        action_header_color: str = ACTION_COLOR,
        value_color: str = VALUE_COLOR,
        bg_color: str = BG_PANEL,
        label_font_size: int = 14,
        value_font_size: int = 13,
    ) -> None:
        super().__init__()

        self._n_states = n_states
        self._n_actions = n_actions
        self._cell_w = cell_width
        self._cell_h = cell_height
        self._value_font_size = value_font_size
        self._value_color = value_color

        self._q: list[list[float]] = (
            q_values if q_values is not None
            else [[0.0] * n_actions for _ in range(n_states)]
        )
        s_labels = state_labels or [f"s{i}" for i in range(n_states)]
        a_labels = action_labels or [f"a{i}" for i in range(n_actions)]

        total_w = (n_actions + 1) * cell_width + 0.2
        total_h = (n_states + 1) * cell_height + 0.2

        bg = Rectangle(
            width=total_w,
            height=total_h,
            fill_color=bg_color,
            fill_opacity=0.95,
            stroke_color=CODE_ACCENT,
            stroke_width=1.0,
        )
        self.add(bg)

        # Top-left corner of first data cell
        ox = -total_w / 2 + cell_width + 0.1
        oy = total_h / 2 - cell_height - 0.1

        # Column headers
        self.col_headers: list[Text] = []
        for j, lbl in enumerate(a_labels):
            m = Text(lbl, font_size=label_font_size, color=action_header_color)
            m.move_to([
                ox + j * cell_width + cell_width / 2,
                oy + cell_height / 2,
                0,
            ])
            self.col_headers.append(m)
            self.add(m)

        # Row headers and data cells
        self.row_headers: list[Text] = []
        self.cells: dict[tuple[int, int], Text] = {}

        for i, slbl in enumerate(s_labels):
            row_y = oy - (i + 1) * cell_height
            sh = Text(slbl, font_size=label_font_size, color=header_color)
            sh.move_to([ox - cell_width / 2, row_y + cell_height / 2, 0])
            self.row_headers.append(sh)
            self.add(sh)

            for j in range(n_actions):
                v = (self._q[i][j]
                     if i < len(self._q) and j < len(self._q[i])
                     else 0.0)
                cell_mob = Text(
                    f"{v:.2f}",
                    font_size=value_font_size,
                    color=value_color,
                )
                cell_mob.move_to([
                    ox + j * cell_width + cell_width / 2,
                    row_y + cell_height / 2,
                    0,
                ])
                self.cells[(i, j)] = cell_mob
                self.add(cell_mob)

        # Grid lines
        grid_lines = VGroup()
        x_start = ox - cell_width
        for j in range(n_actions + 2):
            x = x_start + j * cell_width
            grid_lines.add(Line(
                [x, oy + cell_height, 0],
                [x, oy - n_states * cell_height, 0],
                stroke_color=CODE_ACCENT,
                stroke_width=0.5,
                stroke_opacity=0.4,
            ))
        for i in range(n_states + 2):
            y = oy + cell_height - i * cell_height
            grid_lines.add(Line(
                [x_start, y, 0],
                [x_start + (n_actions + 1) * cell_width, y, 0],
                stroke_color=CODE_ACCENT,
                stroke_width=0.5,
                stroke_opacity=0.4,
            ))
        self.add(grid_lines)

    def update_cell(
        self,
        scene: Scene,
        state_idx: int,
        action_idx: int,
        new_value: float,
        *,
        run_time: float = 0.6,
    ) -> None:
        """Animate a single cell fading out and in with new_value."""
        key = (state_idx, action_idx)
        old = self.cells.get(key)
        if old is None:
            return
        new_mob = Text(
            f"{new_value:.2f}",
            font_size=self._value_font_size,
            color=self._value_color,
        ).move_to(old.get_center())
        if old in self.submobjects:
            self.remove(old)
        self.add(new_mob)
        self.cells[key] = new_mob
        scene.play(
            FadeOut(old, run_time=run_time * 0.4),
            FadeIn(new_mob, run_time=run_time * 0.6),
        )

    def highlight_row(self, scene: Scene, state_idx: int) -> list:
        """Return Indicate animations for the entire state_idx row."""
        mobs: list[Text] = []
        if state_idx < len(self.row_headers):
            mobs.append(self.row_headers[state_idx])
        for j in range(self._n_actions):
            cell = self.cells.get((state_idx, j))
            if cell is not None:
                mobs.append(cell)
        return [Indicate(m, color=VALUE_COLOR) for m in mobs]

    def highlight_cell(self, scene: Scene, state_idx: int, action_idx: int) -> list:
        """Return an Indicate animation for a single Q-value cell."""
        cell = self.cells.get((state_idx, action_idx))
        if cell is None:
            return []
        return [Indicate(cell, color=ACTION_COLOR, scale_factor=1.5)]


# ---------------------------------------------------------------------------
# EpisodeTrail
# ---------------------------------------------------------------------------


class EpisodeTrail(VGroup):
    """Animated agent trail through a grid environment.

    Draws the grid and an agent marker. Each call to step_to() or
    step_to_state() moves the agent and leaves a fading dot as history.

    Usage::

        trail = EpisodeTrail(rows=4, cols=4, width=4.8,
                             holes={(1,1),(1,3),(2,3),(3,0)},
                             goal=(3, 3))
        self.add(trail)
        trail.step_to_state(self, 0)   # start at state 0 = (0,0)
        trail.step_to_state(self, 1)
        trail.step_to_state(self, 5)
        trail.clear_trail(self)
    """

    def __init__(
        self,
        rows: int = 4,
        cols: int = 4,
        *,
        holes: set[tuple[int, int]] | None = None,
        goal: tuple[int, int] | None = None,
        width: float = 4.8,
        cell_color: str = BG_GRID,
        hole_color: str = PENALTY_COLOR,
        goal_color: str = REWARD_COLOR,
        agent_color: str = STATE_COLOR,
        trail_color: str = POLICY_COLOR,
        stroke_color: str = STATE_COLOR,
    ) -> None:
        super().__init__()

        self._rows = rows
        self._cols = cols
        self._holes: set[tuple[int, int]] = holes or set()
        self._goal = goal
        self._cell_w = (width - 0.1) / cols
        self._cell_h = self._cell_w
        self._agent_color = agent_color
        self._trail_color = trail_color
        self._current_pos: tuple[int, int] | None = None
        self._trail_dots: list[Dot] = []

        # Grid background
        for r in range(rows):
            for c in range(cols):
                is_hole = (r, c) in self._holes
                is_goal = (r, c) == goal
                fill = (hole_color if is_hole
                        else goal_color if is_goal
                        else cell_color)
                fill_op = 0.7 if (is_hole or is_goal) else 0.2
                cell = Rectangle(
                    width=self._cell_w - 0.04,
                    height=self._cell_h - 0.04,
                    fill_color=fill,
                    fill_opacity=fill_op,
                    stroke_color=stroke_color,
                    stroke_width=0.8,
                ).move_to(self._cell_center(r, c))
                self.add(cell)

        # Agent marker (hidden until first step)
        agent_size = self._cell_w * 0.42
        self._agent = Rectangle(
            width=agent_size,
            height=agent_size,
            fill_color=agent_color,
            fill_opacity=0.95,
            stroke_width=0,
        )
        self._agent.set_opacity(0)
        self.add(self._agent)

    def _cell_center(self, r: int, c: int) -> np.ndarray:
        return np.array([
            (c - self._cols / 2 + 0.5) * self._cell_w,
            -(r - self._rows / 2 + 0.5) * self._cell_h,
            0.0,
        ])

    def step_to(
        self,
        scene: Scene,
        row: int,
        col: int,
        *,
        run_time: float = 0.5,
    ) -> None:
        """Move agent to (row, col), leaving a trail dot at current position."""
        target = self._cell_center(row, col)

        if self._current_pos is None:
            self._agent.move_to(target)
            scene.play(FadeIn(self._agent), run_time=run_time * 0.6)
        else:
            # Leave trail dot at current agent center
            trail_dot = Dot(
                point=self._agent.get_center().copy(),
                radius=self._cell_w * 0.12,
                color=self._trail_color,
            ).set_opacity(OPACITY_SECONDARY)
            self.add(trail_dot)
            self._trail_dots.append(trail_dot)
            scene.play(self._agent.animate.move_to(target), run_time=run_time)

        self._current_pos = (row, col)

    def step_to_state(
        self,
        scene: Scene,
        state_idx: int,
        *,
        run_time: float = 0.5,
    ) -> None:
        """Move agent to the grid cell for the given FrozenLake state index."""
        row, col = divmod(state_idx, self._cols)
        self.step_to(scene, row, col, run_time=run_time)

    def clear_trail(self, scene: Scene, *, run_time: float = 0.4) -> None:
        """Fade out and remove all trail dots."""
        if not self._trail_dots:
            return
        scene.play(*[FadeOut(d) for d in self._trail_dots], run_time=run_time)
        for d in self._trail_dots:
            if d in self.submobjects:
                self.remove(d)
        self._trail_dots.clear()

    def reset(self, scene: Scene, *, run_time: float = 0.4) -> None:
        """Remove agent marker and clear all trail dots."""
        self.clear_trail(scene, run_time=run_time)
        if self._current_pos is not None:
            scene.play(FadeOut(self._agent), run_time=run_time)
            self._current_pos = None
