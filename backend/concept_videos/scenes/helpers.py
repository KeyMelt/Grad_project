from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Mapping, Sequence

import numpy as np
from PIL import Image
from PIL.Image import Resampling
from manim import (
    Animation,
    AnimationGroup,
    Create,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    Mobject,
    ORIGIN,
    OUT,
    Rectangle,
    ReplacementTransform,
    Scene,
    Succession,
    SurroundingRectangle,
    Transform,
    TransformMatchingTex,
    VGroup,
    WHITE,
    YELLOW,
    rgb_to_color,
    smooth,
)

DEFAULT_GRID_WIDTH = 5.6
DEFAULT_GRID_HEIGHT = 5.6
DEFAULT_CELL_LINE_Z = OUT * 0.01
DEFAULT_TILE_Z = ORIGIN
DEFAULT_TRAVERSER_Z = OUT * 0.12


@dataclass
class StaticTileAsset:
    """Static visual content occupying a grid cell."""

    name: str
    asset_path: Path
    mobject: Mobject


@dataclass
class GridCell:
    """Logical metadata for one cell in an IterableGrid."""

    row: int
    col: int
    center: np.ndarray
    bounds: tuple[float, float, float, float]
    cell_mobject: Rectangle
    static_tile: StaticTileAsset | None = None
    anchored_contents: list[Mobject] = field(default_factory=list)


@dataclass(frozen=True)
class EquationTransformPlan:
    """Plan for partial equation transforms.

    `tex_pairs` maps source tex token -> target tex token.
    `index_pairs` maps source submobject index -> target submobject index.
    """

    tex_pairs: tuple[tuple[str, str], ...] = ()
    index_pairs: tuple[tuple[int, int], ...] = ()


@dataclass
class GridAnchor:
    row: int
    col: int
    offset: np.ndarray


@dataclass
class CameraSpherePin:
    sphere_radius: float
    orient_to_camera: bool
    updater: Callable[[Mobject], None]


class IterableGrid(Group):
    """Flat 2D grid in 3D space with static tiles and anchored traversers."""

    def __init__(
        self,
        rows: int,
        cols: int,
        *,
        width: float = DEFAULT_GRID_WIDTH,
        height: float = DEFAULT_GRID_HEIGHT,
    ):
        if rows <= 0 or cols <= 0:
            raise ValueError("rows and cols must both be positive")

        super().__init__()
        self.rows = int(rows)
        self.cols = int(cols)
        self.width_value = float(width)
        self.height_value = float(height)
        self.cell_width = self.width_value / self.cols
        self.cell_height = self.height_value / self.rows

        self.tile_layer = Group()
        self.cell_layer = VGroup()
        self.traverser_layer = Group()
        self.add(self.tile_layer, self.cell_layer, self.traverser_layer)

        self.cells: dict[tuple[int, int], GridCell] = {}
        self.anchors: dict[Mobject, GridAnchor] = {}
        self.camera_sphere_pins: dict[Mobject, CameraSpherePin] = {}

        left_x = -self.width_value / 2
        top_y = self.height_value / 2
        for row in range(self.rows):
            for col in range(self.cols):
                x0 = left_x + col * self.cell_width
                x1 = x0 + self.cell_width
                y1 = top_y - row * self.cell_height
                y0 = y1 - self.cell_height
                center = np.array([(x0 + x1) / 2.0, (y0 + y1) / 2.0, 0.0], dtype=float)
                cell = Rectangle(width=self.cell_width, height=self.cell_height)
                cell.move_to(center + DEFAULT_CELL_LINE_Z)
                self.cell_layer.add(cell)
                self.cells[(row, col)] = GridCell(
                    row=row,
                    col=col,
                    center=center,
                    bounds=(x0, x1, y0, y1),
                    cell_mobject=cell,
                )

    def __iter__(self):
        for row in range(self.rows):
            for col in range(self.cols):
                yield self.cells[(row, col)]

    def validate_cell(self, row: int, col: int) -> None:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError(f"cell ({row}, {col}) is outside a {self.rows}x{self.cols} grid")

    def cell(self, row: int, col: int) -> GridCell:
        self.validate_cell(row, col)
        return self.cells[(row, col)]

    def cell_center(self, row: int, col: int) -> np.ndarray:
        return self.cell(row, col).center

    def _remove_from_all_cells(self, traverser: Mobject) -> None:
        for cell in self:
            if traverser in cell.anchored_contents:
                cell.anchored_contents.remove(traverser)

    def release_traverser(self, traverser: Mobject, *, keep_camera_pin: bool = False) -> None:
        """Detach a traverser from occupancy metadata."""

        if not keep_camera_pin:
            self.detach_camera_sphere_pin(traverser)
        self.anchors.pop(traverser, None)
        self._remove_from_all_cells(traverser)

    def anchor_traverser(
        self,
        traverser: Mobject,
        row: int,
        col: int,
        *,
        offset: np.ndarray = DEFAULT_TRAVERSER_Z,
        move_to_cell: bool = True,
    ) -> None:
        """Anchor traverser state to one cell and optionally move it there."""

        self.validate_cell(row, col)
        offset_vector = np.array(offset, dtype=float)

        self.release_traverser(traverser, keep_camera_pin=True)
        if traverser not in self.traverser_layer.submobjects:
            self.traverser_layer.add(traverser)
        if move_to_cell:
            traverser.move_to(self._position_for_anchor(traverser, row, col, offset_vector))

        self.anchors[traverser] = GridAnchor(row=row, col=col, offset=offset_vector)
        self.cell(row, col).anchored_contents.append(traverser)

    def _camera_forward_unit_vector(self, scene: Scene) -> np.ndarray:
        """Return world-space unit vector from grid center toward the active camera."""

        camera = getattr(scene, "camera", None)
        if camera is None:
            return np.array(OUT, dtype=float)

        camera.reset_rotation_matrix()
        rotation = np.array(camera.get_rotation_matrix(), dtype=float)
        direction = rotation @ np.array(OUT, dtype=float)
        norm = float(np.linalg.norm(direction))
        if norm <= 1e-8:
            return np.array(OUT, dtype=float)
        return direction / norm

    def _position_for_anchor(
        self,
        traverser: Mobject,
        row: int,
        col: int,
        default_offset: np.ndarray,
    ) -> np.ndarray:
        center = self.cell_center(row, col)
        return center + default_offset

    def attach_camera_sphere_pin(
        self,
        scene: Scene,
        traverser: Mobject,
        *,
        sphere_radius: float | None = None,
        orient_to_camera: bool = True,
    ) -> None:
        """Pin a traverser center to a camera-rotating sphere around its cell anchor."""

        anchor = self.anchors.get(traverser)
        if anchor is None:
            raise ValueError("attach_camera_sphere_pin requires traverser to be anchored to a grid cell")

        self.detach_camera_sphere_pin(traverser)

        radius = float(
            np.linalg.norm(anchor.offset) if sphere_radius is None else sphere_radius
        )
        if radius <= 0:
            raise ValueError("sphere_radius must be positive")

        def _pin_updater(mob: Mobject) -> None:
            active_anchor = self.anchors.get(mob)
            if active_anchor is None:
                return
            target = self.cell_center(active_anchor.row, active_anchor.col)
            target = target + self._camera_forward_unit_vector(scene) * radius
            mob.move_to(target)

        traverser.add_updater(_pin_updater)
        # Cairo 3D + ImageMobject can disappear when fixed-orientation is applied.
        # Raster sprites are already camera-facing in this pipeline, so keep center pin only.
        contains_raster = any(isinstance(submob, ImageMobject) for submob in traverser.get_family())
        if orient_to_camera and not contains_raster and hasattr(scene, "add_fixed_orientation_mobjects"):
            scene.add_fixed_orientation_mobjects(traverser)
        self.camera_sphere_pins[traverser] = CameraSpherePin(
            sphere_radius=radius,
            orient_to_camera=bool(orient_to_camera),
            updater=_pin_updater,
        )
        _pin_updater(traverser)

    def detach_camera_sphere_pin(self, traverser: Mobject) -> CameraSpherePin | None:
        """Remove camera-sphere pinning and optional camera-facing orientation lock."""

        pin = self.camera_sphere_pins.pop(traverser, None)
        if pin is None:
            return None

        traverser.remove_updater(pin.updater)
        return pin

    def set_static_tile(
        self,
        *,
        row: int,
        col: int,
        tile_name: str,
        tile_asset_path: Path,
        tile_mobject: Mobject,
    ) -> None:
        """Register static tile metadata for one cell."""

        cell = self.cell(row, col)
        cell.static_tile = StaticTileAsset(
            name=tile_name,
            asset_path=tile_asset_path,
            mobject=tile_mobject,
        )


def gymnasium_toy_text_asset_dir() -> Path:
    """Return Gymnasium toy_text image asset directory."""

    try:
        import gymnasium.envs.toy_text.frozen_lake as frozen_lake
    except ImportError as exc:
        raise RuntimeError("Gymnasium is required to load toy_text assets") from exc
    return Path(frozen_lake.__file__).resolve().parent / "img"


def resolve_asset_path(asset_path: str | Path, asset_dir: str | Path | None = None) -> Path:
    """Resolve absolute, asset-dir-relative, or Gymnasium toy_text path."""

    path = Path(asset_path).expanduser()
    if path.is_absolute():
        return path
    if asset_dir is not None:
        return Path(asset_dir).expanduser() / path
    return gymnasium_toy_text_asset_dir() / path


def _validate_tile_placement(
    *,
    rows: int,
    cols: int,
    asset_dict: Mapping[str, str | Path],
    tile_placement: Sequence[Sequence[str]],
) -> None:
    if len(tile_placement) != rows:
        raise ValueError("tile_placement row count must match rows")

    for row_index, placement_row in enumerate(tile_placement):
        if len(placement_row) != cols:
            raise ValueError(
                f"tile_placement row {row_index} has {len(placement_row)} columns; expected {cols}"
            )
        for col_index, asset_name in enumerate(placement_row):
            if asset_name not in asset_dict:
                valid = ", ".join(sorted(asset_dict))
                raise ValueError(
                    f"tile_placement[{row_index}][{col_index}] references {asset_name!r}; valid names: {valid}"
                )


def _build_vector_tile(
    asset_path: Path,
    *,
    tile_width: float,
    tile_height: float,
    tile_asset_opacity: float,
    tile_vector_resolution: int,
    tile_vector_bleed: float,
    alpha_threshold: float = 0.02,
) -> VGroup:
    """Approximate a raster tile as a small vector mosaic in world space."""

    if tile_vector_resolution <= 0:
        raise ValueError("tile_vector_resolution must be positive")
    if tile_vector_bleed < 0:
        raise ValueError("tile_vector_bleed cannot be negative")

    image = Image.open(asset_path).convert("RGBA")
    image = image.resize((tile_vector_resolution, tile_vector_resolution), resample=Resampling.BOX)
    rgba = np.asarray(image, dtype=np.uint8)

    px_w = tile_width / tile_vector_resolution
    px_h = tile_height / tile_vector_resolution
    bleed_x = px_w * tile_vector_bleed
    bleed_y = px_h * tile_vector_bleed
    left = -tile_width / 2
    top = tile_height / 2

    tile_group = VGroup()
    for row in range(tile_vector_resolution):
        col = 0
        while col < tile_vector_resolution:
            r, g, b, a = [int(value) for value in rgba[row, col]]
            alpha = (a / 255.0) * tile_asset_opacity
            if alpha <= alpha_threshold:
                col += 1
                continue

            run_start = col
            col += 1
            while col < tile_vector_resolution and np.array_equal(rgba[row, col], rgba[row, run_start]):
                col += 1

            run_len = col - run_start
            width = px_w * run_len + bleed_x
            height = px_h + bleed_y
            x = left + px_w * run_start + (px_w * run_len) / 2
            y = top - px_h * row - px_h / 2

            block = Rectangle(width=width, height=height, stroke_width=0)
            block.set_fill(
                color=rgb_to_color((r / 255.0, g / 255.0, b / 255.0)),
                opacity=alpha,
            )
            block.move_to(np.array([x, y, 0.0]))
            tile_group.add(block)

    return tile_group


def _build_tile_mobject(
    *,
    asset_path: Path,
    tile_width: float,
    tile_height: float,
    tile_asset_opacity: float,
    tile_render_mode: str,
    tile_vector_resolution: int,
    tile_vector_bleed: float,
) -> Mobject:
    """Build tile content as either raster image or vectorized mosaic."""

    mode = tile_render_mode.lower().strip()
    if mode == "image":
        tile = ImageMobject(str(asset_path))
        tile.stretch_to_fit_width(tile_width)
        tile.stretch_to_fit_height(tile_height)
        tile.set_opacity(tile_asset_opacity)
        return tile
    if mode == "vector":
        return _build_vector_tile(
            asset_path,
            tile_width=tile_width,
            tile_height=tile_height,
            tile_asset_opacity=tile_asset_opacity,
            tile_vector_resolution=tile_vector_resolution,
            tile_vector_bleed=tile_vector_bleed,
        )

    raise ValueError("tile_render_mode must be either 'vector' or 'image'")


def create_iterable_grid(
    rows: int,
    cols: int,
    asset_dict: Mapping[str, str | Path],
    tile_placement: Sequence[Sequence[str]],
    *,
    width: float | None = None,
    height: float | None = None,
    asset_dir: str | Path | None = None,
    grid_line_thickness: float = 2.0,
    grid_line_color=WHITE,
    fill_color: str = "#020617",
    fill_opacity: float = 0.0,
    tile_asset_opacity: float = 1.0,
    tile_render_mode: str = "vector",
    tile_vector_resolution: int = 32,
    tile_vector_bleed: float = 0.08,
) -> IterableGrid:
    """Build a grid with static cell tiles and explicit cell metadata."""

    _validate_tile_placement(
        rows=rows,
        cols=cols,
        asset_dict=asset_dict,
        tile_placement=tile_placement,
    )

    grid = IterableGrid(
        rows=rows,
        cols=cols,
        width=DEFAULT_GRID_WIDTH if width is None else width,
        height=DEFAULT_GRID_HEIGHT if height is None else height,
    )

    for cell in grid:
        cell.cell_mobject.set_stroke(color=grid_line_color, width=grid_line_thickness)
        cell.cell_mobject.set_fill(color=fill_color, opacity=fill_opacity)

    tile_templates: dict[str, tuple[Path, Mobject]] = {}
    for asset_name, asset_path in asset_dict.items():
        resolved = resolve_asset_path(asset_path, asset_dir)
        tile_templates[asset_name] = (
            resolved,
            _build_tile_mobject(
                asset_path=resolved,
                tile_width=grid.cell_width,
                tile_height=grid.cell_height,
                tile_asset_opacity=tile_asset_opacity,
                tile_render_mode=tile_render_mode,
                tile_vector_resolution=tile_vector_resolution,
                tile_vector_bleed=tile_vector_bleed,
            ),
        )

    for row in range(rows):
        for col in range(cols):
            asset_name = tile_placement[row][col]
            resolved, template_tile = tile_templates[asset_name]
            tile = template_tile.copy()
            tile.move_to(grid.cell_center(row, col) + DEFAULT_TILE_Z)
            grid.tile_layer.add(tile)
            grid.set_static_tile(
                row=row,
                col=col,
                tile_name=asset_name,
                tile_asset_path=resolved,
                tile_mobject=tile,
            )

    return grid


def _manhattan_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def traverse_grid(
    scene: Scene,
    grid: IterableGrid,
    traverser: Mobject,
    path: Sequence[tuple[int, int]],
    *,
    offset: np.ndarray | None = None,
    run_time_per_step: float = 0.45,
    rate_func=smooth,
) -> Mobject:
    """Traverse a path with strict Manhattan steps and live anchor updates."""

    if not path:
        return traverser

    for row, col in path:
        grid.validate_cell(row, col)

    current_anchor = grid.anchors.get(traverser)
    current_cell = None if current_anchor is None else (current_anchor.row, current_anchor.col)
    offset_vector = np.array(
        DEFAULT_TRAVERSER_Z
        if offset is None and current_anchor is None
        else (current_anchor.offset if offset is None else offset),
        dtype=float,
    )

    check_points: list[tuple[int, int]] = []
    if current_cell is not None:
        check_points.append(current_cell)
    check_points.extend(path)

    for previous, nxt in zip(check_points, check_points[1:]):
        if previous == nxt:
            continue
        if _manhattan_distance(previous, nxt) != 1:
            raise ValueError(
                f"invalid traversal from {previous} to {nxt}; movement must be one cell in forward/backward/left/right"
            )

    suspended_pin = grid.detach_camera_sphere_pin(traverser)

    if current_cell is None:
        first_row, first_col = path[0]
        grid.anchor_traverser(
            traverser,
            first_row,
            first_col,
            offset=offset_vector,
            move_to_cell=True,
        )
        remaining_path = path[1:]
    else:
        remaining_path = path

    for row, col in remaining_path:
        anchor = grid.anchors.get(traverser)
        if anchor is not None and (anchor.row, anchor.col) == (row, col):
            continue

        target_position = grid._position_for_anchor(traverser, row, col, offset_vector)
        scene.play(
            traverser.animate.move_to(target_position),
            run_time=run_time_per_step,
            rate_func=rate_func,
        )
        grid.anchor_traverser(
            traverser,
            row,
            col,
            offset=offset_vector,
            move_to_cell=False,
        )

    if suspended_pin is not None:
        grid.attach_camera_sphere_pin(
            scene,
            traverser,
            sphere_radius=suspended_pin.sphere_radius,
            orient_to_camera=suspended_pin.orient_to_camera,
        )

    return traverser


def make_highlighter(
    target: Mobject,
    *,
    color=YELLOW,
    stroke_width: float = 3.0,
    buff: float = 0.1,
    corner_radius: float = 0.08,
    fill_opacity: float = 0.0,
    dynamic: bool = True,
) -> SurroundingRectangle:
    """Create a highlight wrapper around a target mobject."""

    highlighter = SurroundingRectangle(
        target,
        color=color,
        buff=buff,
        stroke_width=stroke_width,
        corner_radius=corner_radius,
    )
    highlighter.set_fill(color=color, opacity=fill_opacity)

    if dynamic:
        highlighter.add_updater(
            lambda box: box.become(
                SurroundingRectangle(
                    target,
                    color=color,
                    buff=buff,
                    stroke_width=stroke_width,
                    corner_radius=corner_radius,
                ).set_fill(color=color, opacity=fill_opacity)
            )
        )
    return highlighter


def highlight_animation(
    target: Mobject,
    animation: Animation | None = None,
    *,
    leave_highlight: bool = False,
    **highlighter_kwargs,
) -> AnimationGroup:
    """Run an animation while emphasizing its target with a highlighter."""

    highlighter = make_highlighter(target, **highlighter_kwargs)
    phases: list[Animation] = [Create(highlighter)]
    if animation is not None:
        phases.append(animation)
    if not leave_highlight:
        phases.append(FadeOut(highlighter))
    return Succession(*phases)


def _normalize_transform_plan(
    *,
    source_parts: Sequence[str] | None,
    target_parts: Sequence[str] | None,
    part_map: Mapping[str, str] | None,
    index_pairs: Sequence[tuple[int, int]] | None,
) -> EquationTransformPlan:
    tex_pairs: list[tuple[str, str]] = []
    if part_map is not None:
        tex_pairs.extend((str(src), str(dst)) for src, dst in part_map.items())
    if source_parts is not None or target_parts is not None:
        if source_parts is None or target_parts is None:
            raise ValueError("source_parts and target_parts must be provided together")
        if len(source_parts) != len(target_parts):
            raise ValueError("source_parts and target_parts must have equal length")
        tex_pairs.extend((str(src), str(dst)) for src, dst in zip(source_parts, target_parts))

    normalized_index_pairs = () if index_pairs is None else tuple((int(a), int(b)) for a, b in index_pairs)
    return EquationTransformPlan(tex_pairs=tuple(tex_pairs), index_pairs=normalized_index_pairs)


def transform_equation_parts(
    scene: Scene,
    source_equation: Mobject,
    target_equation: Mobject | str,
    *,
    plan: EquationTransformPlan | None = None,
    part_map: Mapping[str, str] | None = None,
    source_parts: Sequence[str] | None = None,
    target_parts: Sequence[str] | None = None,
    index_pairs: Sequence[tuple[int, int]] | None = None,
    transform_type=ReplacementTransform,
    preserve_unmapped: bool = True,
    run_time: float = 0.9,
) -> Mobject:
    """Transform full equations or selected subparts while preserving untouched parts."""

    target = (
        target_equation.copy()
        if isinstance(target_equation, Mobject)
        else source_equation.__class__(target_equation, font_size=getattr(source_equation, "font_size", 36))
    )
    target.move_to(source_equation)

    resolved_plan = plan or _normalize_transform_plan(
        source_parts=source_parts,
        target_parts=target_parts,
        part_map=part_map,
        index_pairs=index_pairs,
    )

    if not resolved_plan.tex_pairs and not resolved_plan.index_pairs:
        if transform_type is TransformMatchingTex:
            scene.play(TransformMatchingTex(source_equation, target), run_time=run_time)
        else:
            scene.play(transform_type(source_equation, target), run_time=run_time)
        return target

    source_submobjects = list(source_equation.submobjects)
    target_submobjects = list(target.submobjects)

    pairings: list[tuple[Mobject, Mobject]] = []
    used_source: set[Mobject] = set()
    used_target: set[Mobject] = set()

    for source_tex, target_tex in resolved_plan.tex_pairs:
        source_piece = getattr(source_equation, "get_part_by_tex", lambda _: None)(source_tex)
        target_piece = getattr(target, "get_part_by_tex", lambda _: None)(target_tex)
        if source_piece is None:
            raise ValueError(f"source token {source_tex!r} was not found in source equation")
        if target_piece is None:
            raise ValueError(f"target token {target_tex!r} was not found in target equation")
        pairings.append((source_piece, target_piece))
        used_source.add(source_piece)
        used_target.add(target_piece)

    for source_index, target_index in resolved_plan.index_pairs:
        if source_index < 0 or source_index >= len(source_submobjects):
            raise ValueError(f"source index {source_index} is out of range")
        if target_index < 0 or target_index >= len(target_submobjects):
            raise ValueError(f"target index {target_index} is out of range")
        source_piece = source_submobjects[source_index]
        target_piece = target_submobjects[target_index]
        pairings.append((source_piece, target_piece))
        used_source.add(source_piece)
        used_target.add(target_piece)

    animations: list[Animation] = []
    for source_piece, target_piece in pairings:
        animations.append(transform_type(source_piece, target_piece))

    if preserve_unmapped:
        for index, source_piece in enumerate(source_submobjects):
            if source_piece in used_source:
                continue
            if index < len(target_submobjects) and target_submobjects[index] not in used_target:
                target_piece = target_submobjects[index]
                animations.append(Transform(source_piece, target_piece))
                used_target.add(target_piece)
            else:
                animations.append(FadeOut(source_piece))
    else:
        for source_piece in source_submobjects:
            if source_piece not in used_source:
                animations.append(FadeOut(source_piece))

    for target_piece in target_submobjects:
        if target_piece not in used_target:
            animations.append(FadeIn(target_piece))

    scene.play(AnimationGroup(*animations, lag_ratio=0.0), run_time=run_time)
    scene.remove(source_equation)
    scene.add(target)
    return target


__all__ = [
    "CameraSpherePin",
    "EquationTransformPlan",
    "GridCell",
    "IterableGrid",
    "StaticTileAsset",
    "create_iterable_grid",
    "gymnasium_toy_text_asset_dir",
    "highlight_animation",
    "make_highlighter",
    "resolve_asset_path",
    "transform_equation_parts",
    "traverse_grid",
]
