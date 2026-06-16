"""Taxi-specific trace replay board helpers."""
from __future__ import annotations

from typing import Any

from manim import (
    DOWN,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    ReplacementTransform,
    RoundedRectangle,
    SurroundingRectangle,
    Text,
    VGroup,
)

from backend.rl_engine.taxi import decode_taxi_state

from . import trace_common as C

_LOCATION_COLORS = {
    "R": "#7F1D1D",
    "G": "#14532D",
    "Y": "#713F12",
    "B": "#1E3A5F",
}


def classify_taxi_transition(step: dict[str, Any]) -> str:
    """Classify pickup/dropoff semantics from explicit state metadata."""
    gm = step.get("grid_metadata") or {}
    passenger = gm.get("passenger") or {}
    next_passenger = gm.get("next_passenger") or {}
    action_label = gm.get("action_label") or C.action_label("Taxi", gm.get("action"))
    reward = C.as_float(gm.get("reward"))

    if action_label == "Pickup":
        if not passenger.get("in_taxi") and next_passenger.get("in_taxi"):
            return "pickup"
        if reward is not None and reward <= -10:
            return "illegal_pickup"
    if action_label == "Dropoff":
        if passenger.get("in_taxi") and not next_passenger.get("in_taxi") and (reward or 0) > 0:
            return "dropoff"
        if reward is not None and reward <= -10:
            return "illegal_dropoff"
    return ""


class TaxiBoard:
    is_spatial = True
    ROWS = 5
    COLS = 5

    def __init__(self, first_step: dict[str, Any] | None = None, width=5.6, at=(-3.2, 0.2)):
        self._step = first_step or {}
        self._gm = (first_step or {}).get("grid_metadata") or {}
        self._cell_size = width / self.COLS
        self._at = at
        self._cells: dict[int, RoundedRectangle] = {}
        self.group = self._build_grid(width=width, at=at)
        self.agent = None
        self.destination = None
        self.passenger = None
        self._onboard = False

    def _build_grid(self, *, width: float, at: tuple[float, float]) -> VGroup:
        grid = VGroup()
        for row in range(self.ROWS):
            for column in range(self.COLS):
                state = row * self.COLS + column
                tile_type = self._tile_type(row, column)
                cell = RoundedRectangle(
                    width=self._cell_size,
                    height=self._cell_size,
                    corner_radius=0.06,
                    fill_color=_LOCATION_COLORS.get(tile_type, C.PANEL_2),
                    fill_opacity=1.0,
                    stroke_color=C.STROKE,
                    stroke_width=1.4,
                )
                cell.move_to(self._center0(row, column))
                self._cells[state] = cell
                grid.add(cell)
                label = self._cell_label(tile_type)
                if label is not None:
                    label.move_to(cell.get_center()).set_z_index(6)
                    grid.add(label)

        for wall in self._gm.get("walls") or []:
            line = self._wall_line(wall)
            if line is not None:
                grid.add(line)

        title = Text("Taxi-v3", font_size=20, color=C.TEXT)
        title.move_to([0.0, self._cell_size * 3.05, 0.0]).set_z_index(6)
        grid.add(title)
        grid.move_to([at[0], at[1], 0.0])
        return grid

    def _tile_type(self, row: int, column: int) -> str:
        for cell in self._gm.get("cells") or []:
            if cell.get("row") == row and cell.get("column") == column:
                return str(cell.get("tile_type") or "F")
        return "F"

    def _cell_label(self, tile_type: str):
        if tile_type == "F":
            return None
        return Text(tile_type, font_size=20, color=C.TEXT, weight="BOLD")

    def _wall_line(self, wall: dict[str, Any]) -> Line | None:
        start = wall.get("start") or {}
        end = wall.get("end") or {}
        start_row, start_column = start.get("row"), start.get("column")
        end_row, end_column = end.get("row"), end.get("column")
        if None in {start_row, start_column, end_row, end_column}:
            return None
        left_state = int(start_row) * self.COLS + int(start_column)
        right_state = int(end_row) * self.COLS + int(end_column)
        left_cell = self._cells.get(left_state)
        right_cell = self._cells.get(right_state)
        if left_cell is None or right_cell is None:
            return None
        if start_row == end_row:
            top = min(left_cell.get_top()[1], right_cell.get_top()[1])
            bottom = max(left_cell.get_bottom()[1], right_cell.get_bottom()[1])
            x = (left_cell.get_right()[0] + right_cell.get_left()[0]) / 2
            return Line(
                [x, top, 0.0],
                [x, bottom, 0.0],
                color=C.PENALTY,
                stroke_width=5.0,
            ).set_z_index(8)
        if start_column == end_column:
            left = min(left_cell.get_left()[0], right_cell.get_left()[0])
            right = max(left_cell.get_right()[0], right_cell.get_right()[0])
            y = (left_cell.get_bottom()[1] + right_cell.get_top()[1]) / 2
            return Line(
                [left, y, 0.0],
                [right, y, 0.0],
                color=C.PENALTY,
                stroke_width=5.0,
            ).set_z_index(8)
        return None

    def _center0(self, row: int, column: int):
        return [
            (column - (self.COLS - 1) / 2) * self._cell_size,
            -((row - (self.ROWS - 1) / 2) * self._cell_size),
            0.0,
        ]

    @property
    def mob(self):
        return self.group

    def center(self, state):
        cell = self._cells.get(self._display_state(state))
        if cell is None:
            return self.group.get_center()
        return cell.get_center()

    def ring(self, state, *, color=C.STATE, sw=3.5):
        cell = self._cells.get(self._display_state(state))
        if cell is None:
            return SurroundingRectangle(self.group, color=color, buff=0.04, stroke_width=sw)
        return SurroundingRectangle(cell, color=color, buff=0.02, stroke_width=sw).set_z_index(20)

    def place(self, scene, step, *, run_time=0.35):
        gm = step.get("grid_metadata") or {}
        self._ensure_destination(scene, gm)
        self._ensure_passenger(scene, gm)
        self._onboard = bool((gm.get("passenger") or {}).get("in_taxi"))
        self.agent = self._make_agent(self._onboard).move_to(self.center(step.get("state")))
        scene.play(FadeIn(self.agent, scale=0.7), run_time=run_time)

    def step(self, scene, step, *, run_time=0.45):
        gm = step.get("grid_metadata") or {}
        if self.agent is None:
            self.place(scene, step, run_time=run_time * 0.7)
        self._ensure_destination(scene, gm)
        self._sync_passenger_marker(scene, gm)

        next_state = step.get("next_state")
        current_center = self.center(step.get("state"))
        next_center = self.center(next_state)
        if C.is_taxi_action_spatial(step.get("action")) and current_center is not None:
            scene.play(self.agent.animate.move_to(next_center), run_time=run_time)

        outcome = classify_taxi_transition(step)
        if outcome == "pickup":
            self._animate_pickup(scene, gm, run_time=run_time)
        elif outcome == "dropoff":
            self._animate_dropoff(scene, gm, run_time=run_time)
        elif outcome.startswith("illegal_"):
            self._animate_penalty(scene, run_time=run_time)
        else:
            self._sync_onboard(scene, bool((gm.get("next_passenger") or {}).get("in_taxi")))

    def flash(self, scene, state, *, color=C.TEAL, run_time=0.4):
        rect = self.ring(state, color=color, sw=4.0)
        scene.play(FadeIn(rect), run_time=run_time * 0.45)
        scene.play(FadeOut(rect), run_time=run_time * 0.55)

    def _ensure_destination(self, scene, gm: dict[str, Any]) -> None:
        if self.destination is not None:
            return
        destination = gm.get("destination") or {}
        row, column = destination.get("row"), destination.get("column")
        if row is None or column is None:
            return
        state = int(row) * self.COLS + int(column)
        cell = self._cells.get(state)
        if cell is None:
            return
        badge = SurroundingRectangle(
            cell,
            color=C.REWARD,
            buff=0.03,
            stroke_width=3.0,
        ).set_z_index(14)
        icon = Text("D", font_size=16, color=C.REWARD, weight="BOLD")
        icon.move_to(cell.get_center() + DOWN * (self._cell_size * 0.22)).set_z_index(15)
        self.destination = VGroup(badge, icon)
        scene.add(self.destination)

    def _ensure_passenger(self, scene, gm: dict[str, Any]) -> None:
        passenger = gm.get("passenger") or {}
        if passenger.get("in_taxi"):
            self.passenger = None
            return
        marker = self._passenger_marker(passenger)
        if marker is None:
            self.passenger = None
            return
        self.passenger = marker
        scene.add(marker)

    def _sync_passenger_marker(self, scene, gm: dict[str, Any]) -> None:
        passenger = gm.get("passenger") or {}
        next_passenger = gm.get("next_passenger") or {}
        outcome = classify_taxi_transition({"grid_metadata": gm})

        if outcome == "pickup":
            return
        if outcome == "dropoff":
            return
        if passenger.get("in_taxi") or next_passenger.get("in_taxi"):
            if self.passenger is not None:
                scene.remove(self.passenger)
                self.passenger = None
            return

        target = self._passenger_marker(next_passenger or passenger)
        if target is None:
            return
        if self.passenger is None:
            self.passenger = target
            scene.add(target)
            return
        scene.play(ReplacementTransform(self.passenger, target), run_time=0.2)
        self.passenger = target

    def _animate_pickup(self, scene, gm: dict[str, Any], *, run_time: float) -> None:
        self._sync_onboard(scene, True)
        if self.passenger is None:
            return
        scene.play(self.passenger.animate.move_to(self.agent.get_center()), run_time=run_time * 0.4)
        scene.play(FadeOut(self.passenger), run_time=run_time * 0.2)
        self.passenger = None

    def _animate_dropoff(self, scene, gm: dict[str, Any], *, run_time: float) -> None:
        self._sync_onboard(scene, False)
        marker = self._passenger_marker(gm.get("next_passenger") or gm.get("destination") or {})
        if marker is not None:
            self.passenger = marker
            scene.play(FadeIn(marker, scale=0.7), run_time=run_time * 0.35)
        if self.destination is not None:
            glow = self.destination.copy()
            scene.play(FadeIn(glow), run_time=run_time * 0.15)
            scene.play(FadeOut(glow), run_time=run_time * 0.2)

    def _animate_penalty(self, scene, *, run_time: float) -> None:
        ring = SurroundingRectangle(
            self.agent,
            color=C.PENALTY,
            buff=0.05,
            stroke_width=4.0,
        ).set_z_index(30)
        scene.play(FadeIn(ring), run_time=run_time * 0.25)
        scene.play(FadeOut(ring), run_time=run_time * 0.3)

    def _sync_onboard(self, scene, onboard: bool) -> None:
        if self.agent is None or onboard == self._onboard:
            self._onboard = onboard
            return
        replacement = self._make_agent(onboard).move_to(self.agent.get_center())
        scene.play(ReplacementTransform(self.agent, replacement), run_time=0.2)
        self.agent = replacement
        self._onboard = onboard

    def _make_agent(self, onboard: bool) -> VGroup:
        body = RoundedRectangle(
            width=self._cell_size * 0.52,
            height=self._cell_size * 0.42,
            corner_radius=0.08,
            fill_color="#FBBF24" if not onboard else "#F59E0B",
            fill_opacity=1.0,
            stroke_color=C.TEXT,
            stroke_width=1.4,
        ).set_z_index(25)
        label = Text("T*" if onboard else "T", font_size=18, color=C.PANEL, weight="BOLD")
        label.move_to(body.get_center()).set_z_index(26)
        return VGroup(body, label)

    def _passenger_marker(self, payload: dict[str, Any]):
        row, column = payload.get("row"), payload.get("column")
        if row is None or column is None:
            return None
        state = int(row) * self.COLS + int(column)
        cell = self._cells.get(state)
        if cell is None:
            return None
        marker = Dot(
            point=cell.get_center() + DOWN * (self._cell_size * 0.18),
            radius=self._cell_size * 0.1,
            color=C.POLICY,
        ).set_z_index(18)
        return marker

    def _display_state(self, value: Any) -> int:
        try:
            state = int(value)
        except (TypeError, ValueError):
            return 0
        if 0 <= state < self.ROWS * self.COLS:
            return state
        row, column, _passenger, _destination = decode_taxi_state(state)
        return row * self.COLS + column
