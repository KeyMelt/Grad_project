from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
from manim import *


DEFAULT_GRID_WIDTH = 5.4
DEFAULT_GRID_HEIGHT = 5.4
CELL_LINE_Z = OUT * 0.01
TRAVERSING_MOBJECT_Z = OUT * 0.12


def gymnasium_toy_text_asset_dir() -> Path:
    """Return Gymnasium's installed toy_text image directory."""

    try:
        import gymnasium.envs.toy_text.frozen_lake as frozen_lake
    except ImportError as exc:
        raise RuntimeError("Gymnasium is required to load toy_text assets") from exc
    return Path(frozen_lake.__file__).resolve().parent / "img"


def resolve_asset_path(file_path: str | Path, asset_dir: str | Path | None = None) -> Path:
    """Resolve an absolute, asset_dir-relative, or Gymnasium toy_text asset path."""

    path = Path(file_path).expanduser()
    if path.is_absolute():
        return path
    if asset_dir is not None:
        return Path(asset_dir).expanduser() / path
    return gymnasium_toy_text_asset_dir() / path


@dataclass
class GridAnchor:
    row: int
    col: int
    offset: np.ndarray


class ViewportGrid(Group):
    """Flat 2D grid in 3D space with static tile assets and traversing anchors."""

    def __init__(
        self,
        rows: int,
        cols: int,
        *,
        width: float,
        height: float,
        **kwargs,
    ):
        if rows <= 0 or cols <= 0:
            raise ValueError("rows and cols must both be positive")

        super().__init__(**kwargs)
        self.rows = rows
        self.cols = cols
        self.width_value = float(width)
        self.height_value = float(height)
        self.cell_width = self.width_value / cols
        self.cell_height = self.height_value / rows

        self.tile_assets = Group()
        self.cells = VGroup()
        self.anchored_objects: dict[Mobject, GridAnchor] = {}

        self.add(self.tile_assets, self.cells)

    def __iter__(self):
        return iter(self.cells)

    def __len__(self):
        return len(self.cells)

    def validate_cell(self, row: int, col: int):
        if not 0 <= row < self.rows or not 0 <= col < self.cols:
            raise IndexError(f"cell ({row}, {col}) is outside a {self.rows}x{self.cols} grid")

    def cell(self, row: int, col: int) -> Rectangle:
        self.validate_cell(row, col)
        return self.cells[row * self.cols + col]

    def cell_center(self, row: int, col: int) -> np.ndarray:
        return self.cell(row, col).get_center()

    def anchor(self, mobject: Mobject, row: int, col: int, offset: np.ndarray = TRAVERSING_MOBJECT_Z):
        """Snap a traversing mobject above a cell and record its grid state."""

        self.validate_cell(row, col)
        self.release(mobject)
        offset_vector = np.array(offset, dtype=float)
        mobject.move_to(self.cell_center(row, col) + offset_vector)
        self.anchored_objects[mobject] = GridAnchor(row, col, offset_vector)
        return mobject

    def release(self, mobject: Mobject):
        """Forget a traversing mobject's recorded grid anchor."""

        self.anchored_objects.pop(mobject, None)
        return mobject


def _validate_tile_placement(
    rows: int,
    cols: int,
    Asset_dict: Mapping[str, str | Path],
    tile_placement: Sequence[Sequence[str]],
):
    if len(tile_placement) != rows:
        raise ValueError("tile_placement row count must match rows")

    for row_index, row in enumerate(tile_placement):
        if len(row) != cols:
            raise ValueError(
                f"tile_placement row {row_index} has {len(row)} columns; expected {cols}"
            )
        for col_index, asset_name in enumerate(row):
            if asset_name not in Asset_dict:
                valid_assets = ", ".join(sorted(Asset_dict))
                raise ValueError(
                    f"tile_placement[{row_index}][{col_index}] references {asset_name!r}; "
                    f"valid asset names are: {valid_assets}"
                )


def create_iterable_grid(
    rows: int,
    cols: int,
    Asset_dict: Mapping[str, str | Path],
    tile_placement: Sequence[Sequence[str]],
    *,
    width: float | None = None,
    height: float | None = None,
    asset_dir: str | Path | None = None,
    grid_line_thickness: float = 2.0,
    grid_line_color=GREY_B,
    fill_color="#020617",
    fill_opacity: float = 0.0,
    tile_asset_opacity: float = 1.0,
    **kwargs,
) -> ViewportGrid:
    """Create an iterable flat grid themed by static per-cell Gymnasium assets."""

    _validate_tile_placement(rows, cols, Asset_dict, tile_placement)

    grid = ViewportGrid(
        rows,
        cols,
        width=DEFAULT_GRID_WIDTH if width is None else width,
        height=DEFAULT_GRID_HEIGHT if height is None else height,
        **kwargs,
    )

    left_x = -grid.width_value / 2 + grid.cell_width / 2
    top_y = grid.height_value / 2 - grid.cell_height / 2

    for row in range(rows):
        for col in range(cols):
            x = left_x + col * grid.cell_width
            y = top_y - row * grid.cell_height
            cell = Rectangle(
                width=grid.cell_width,
                height=grid.cell_height,
                stroke_color=grid_line_color,
                stroke_width=grid_line_thickness,
                fill_color=fill_color,
                fill_opacity=fill_opacity,
            )
            cell.move_to(np.array([x, y, 0.0]) + CELL_LINE_Z)
            cell.row = row
            cell.col = col
            grid.cells.add(cell)

    for row in range(rows):
        for col in range(cols):
            asset_name = tile_placement[row][col]
            image = ImageMobject(str(resolve_asset_path(Asset_dict[asset_name], asset_dir)))
            image.stretch_to_fit_width(grid.cell_width)
            image.stretch_to_fit_height(grid.cell_height)
            image.set_opacity(tile_asset_opacity)
            image.move_to(grid.cell_center(row, col) - CELL_LINE_Z)
            image.row = row
            image.col = col
            image.asset_name = asset_name
            grid.tile_assets.add(image)

    return grid


def _cell_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def traverse_grid(
    scene: Scene,
    grid: ViewportGrid,
    mobject: Mobject,
    path: Sequence[tuple[int, int]],
    *,
    offset: np.ndarray | None = None,
    run_time_per_step: float = 0.5,
    rate_func=smooth,
):
    """Move a traversing mobject along one-cell 90-degree grid steps."""

    if not path:
        return mobject

    for row, col in path:
        grid.validate_cell(row, col)

    current_anchor = grid.anchored_objects.get(mobject)
    current_cell = None if current_anchor is None else (current_anchor.row, current_anchor.col)
    offset_vector = (
        current_anchor.offset
        if offset is None and current_anchor is not None
        else np.array(TRAVERSING_MOBJECT_Z if offset is None else offset, dtype=float)
    )

    previous_cell = current_cell
    for next_cell in path:
        if previous_cell is not None:
            if next_cell == previous_cell:
                continue
            if _cell_distance(previous_cell, next_cell) != 1:
                raise ValueError(
                    f"invalid grid traversal from {previous_cell} to {next_cell}; "
                    "movement must be exactly one cell forward, backward, left, or right"
                )
        previous_cell = next_cell

    grid.release(mobject)

    last_cell = current_cell
    for row, col in path:
        if last_cell == (row, col):
            continue
        scene.play(
            mobject.animate.move_to(grid.cell_center(row, col) + offset_vector),
            run_time=run_time_per_step,
            rate_func=rate_func,
        )
        last_cell = (row, col)

    final_row, final_col = path[-1]
    grid.anchor(mobject, final_row, final_col, offset_vector)
    return mobject
