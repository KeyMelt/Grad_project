from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
from manim import *


ROOT = Path(__file__).resolve().parents[3]
FRAME_DIR = ROOT / "frontend" / "assets" / "lesson_media" / "frozenlake"
FROZEN_LAKE_DEFAULT_LAYOUT = ("SFFF", "FHFH", "FFFH", "HFFG")
FROZEN_LAKE_TILE_ASSETS = {
    "S": "stool.png",
    "F": "ice.png",
    "H": "hole.png",
    "G": "goal.png",
}
FROZEN_LAKE_ELF_ASSETS = {
    "left": "elf_left.png",
    "down": "elf_down.png",
    "right": "elf_right.png",
    "up": "elf_up.png",
}


class BaseConceptScene(Scene):
    def setup(self):
        self.camera.background_color = "#020617"

    def show_header(self, title: str, subtitle: str | None = None):
        title_text = Text(title, font_size=38, weight=BOLD)
        if subtitle:
            subtitle_text = Text(subtitle, font_size=24, color=GREY_B).next_to(
                title_text, DOWN, buff=0.16
            )
            header = VGroup(title_text, subtitle_text).to_edge(UP, buff=0.45)
            self.play(
                LaggedStart(
                    FadeIn(title_text, shift=UP * 0.2),
                    FadeIn(subtitle_text),
                    lag_ratio=0.18,
                )
            )
        else:
            header = VGroup(title_text).to_edge(UP, buff=0.45)
            self.play(FadeIn(title_text, shift=UP * 0.2))
        return header

    def assimilation_wait(self, duration: float = 1.0):
        self.wait(duration)

    def place_caption(self, text: str):
        return Text(text, font_size=23, color=GREY_B).to_edge(DOWN, buff=0.22)

    def place_left_panel(self, mobject: Mobject, buff: float = 0.55):
        return mobject.to_edge(LEFT, buff=buff).shift(DOWN * 0.15)

    def place_top_right_panel(self, mobject: Mobject, buff: float = 0.55):
        return mobject.to_edge(RIGHT, buff=buff).shift(UP * 1.25)

    def place_mid_right_panel(self, mobject: Mobject, buff: float = 0.55):
        return mobject.to_edge(RIGHT, buff=buff).shift(DOWN * 0.25)

    def place_bottom_right_panel(self, mobject: Mobject, buff: float = 0.55):
        return mobject.to_edge(RIGHT, buff=buff).shift(DOWN * 2.25)


def note_stack(
    lines: Sequence[str],
    *,
    font_size: float = 22,
    color=GREY_A,
    line_buff: float = 0.14,
    aligned_edge=LEFT,
) -> VGroup:
    rows = VGroup(
        *[
            Text(str(line), font_size=font_size, color=color)
            for line in lines
        ]
    )
    rows.arrange(DOWN, aligned_edge=aligned_edge, buff=line_buff)
    return rows


def panel(
    title: str,
    body: Mobject,
    accent="#38BDF8",
    *,
    width: float = 5.4,
    min_height: float = 1.6,
    padding: float = 0.28,
    title_font_size: float = 24,
    fill_color="#0F172A",
    fill_opacity: float = 0.88,
) -> VGroup:
    title_mob = Text(title, font_size=title_font_size, color=accent, weight=BOLD)
    content = VGroup(title_mob, body).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    height = max(content.height + 2 * padding, min_height)
    box = RoundedRectangle(
        corner_radius=0.16,
        width=width,
        height=height,
        stroke_color=accent,
        stroke_width=2.0,
        fill_color=fill_color,
        fill_opacity=fill_opacity,
    )
    content.move_to(box).align_to(box, LEFT).shift(RIGHT * padding)
    return VGroup(box, content)


def code_panel(
    lines: Sequence[str],
    *,
    title: str = "Code",
    width: float = 5.4,
    font_size: float = 19,
    accent="#64748B",
) -> VGroup:
    code = VGroup(
        *[
            Text(str(line), font="Monospace", font_size=font_size, color="#E2E8F0")
            for line in lines
        ]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    return panel(title, code, accent, width=width, title_font_size=22)


def environment_panel(
    state: int,
    *,
    title: str = "Environment",
    caption: str = "",
    badge_text: str | None = None,
    accent="#38BDF8",
    width: float = 4.7,
) -> VGroup:
    image = frozenlake_frame(state, height=2.35)
    pieces = [image]
    if badge_text:
        pieces.append(pill(badge_text, accent).scale(0.82))
    if caption:
        pieces.append(Text(caption, font_size=19, color=GREY_A, line_spacing=0.86))
    body = VGroup(*pieces).arrange(DOWN, buff=0.18)
    return panel(title, body, accent, width=width)


def blackjack_panel(
    *,
    title: str = "Blackjack Episode",
    player_text: str = "Player 16",
    dealer_text: str = "Dealer 10",
    caption: str = "",
    accent="#34D399",
    width: float = 4.8,
) -> VGroup:
    table = RoundedRectangle(
        corner_radius=0.18,
        width=3.6,
        height=1.9,
        stroke_color=accent,
        stroke_width=2,
        fill_color="#064E3B",
        fill_opacity=0.65,
    )
    player = Text(player_text, font_size=24, color=WHITE, weight=BOLD)
    dealer = Text(dealer_text, font_size=22, color=GREY_A)
    hand = VGroup(dealer, player).arrange(DOWN, buff=0.36).move_to(table)
    pieces = [VGroup(table, hand)]
    if caption:
        pieces.append(Text(caption, font_size=19, color=GREY_A, line_spacing=0.86))
    body = VGroup(*pieces).arrange(DOWN, buff=0.18)
    return panel(title, body, accent, width=width)


def cliffwalking_panel(
    *,
    title: str = "CliffWalking",
    caption: str = "",
    accent="#38BDF8",
    width: float = 4.9,
) -> VGroup:
    rows, cols = 2, 6
    cells = VGroup()
    for row in range(rows):
        for col in range(cols):
            is_cliff = row == 1 and 1 <= col <= 4
            cell = Square(side_length=0.46)
            cell.set_stroke("#94A3B8", width=1.2)
            cell.set_fill("#7F1D1D" if is_cliff else "#0F172A", opacity=0.88)
            cell.move_to(RIGHT * (col - (cols - 1) / 2) * 0.46 + DOWN * (row - 0.5) * 0.46)
            cells.add(cell)
    start = Text("S", font_size=18, color=accent, weight=BOLD).move_to(cells[-6])
    goal = Text("G", font_size=18, color="#34D399", weight=BOLD).move_to(cells[-1])
    cliff = Text("cliff", font_size=16, color="#FCA5A5").move_to(VGroup(*cells[7:11]))
    grid = VGroup(cells, start, goal, cliff)
    pieces = [grid]
    if caption:
        pieces.append(Text(caption, font_size=19, color=GREY_A, line_spacing=0.86))
    body = VGroup(*pieces).arrange(DOWN, buff=0.2)
    return panel(title, body, accent, width=width)


def equation_panel(
    title: str,
    equation: str,
    notes: Sequence[str] | None = None,
    *,
    accent="#FACC15",
    width: float = 5.6,
    font_size: float = 30,
) -> VGroup:
    equation_mob = MathTex(equation, font_size=font_size, color=WHITE)
    if equation_mob.width > width - 0.7:
        equation_mob.scale_to_fit_width(width - 0.7)
    pieces = [equation_mob]
    if notes:
        pieces.append(note_stack(notes, font_size=19, color=GREY_A))
    body = VGroup(*pieces).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
    return panel(title, body, accent, width=width)


class HighlightedAnimation(AnimationGroup):
    """Run an animation while a temporary rectangle highlights its target."""

    def __init__(
        self,
        mobject: Mobject,
        animation: Animation | None = None,
        *,
        color=YELLOW,
        buff: float = 0.12,
        stroke_width: float = 4.0,
        run_time: float | None = None,
        lag_ratio: float = 0.0,
        leave_highlight: bool = False,
        **kwargs,
    ):
        self.highlight_box = SurroundingRectangle(
            mobject,
            color=color,
            buff=buff,
            stroke_width=stroke_width,
        )
        self.highlight_box.add_updater(
            lambda box: box.become(
                SurroundingRectangle(
                    mobject,
                    color=color,
                    buff=buff,
                    stroke_width=stroke_width,
                )
            )
        )
        animations: list[Animation] = [Create(self.highlight_box)]
        if animation is not None:
            animations.append(animation)
        if not leave_highlight:
            animations.append(FadeOut(self.highlight_box))
        super().__init__(*animations, run_time=run_time, lag_ratio=lag_ratio, **kwargs)


def highlighted_animation(
    mobject: Mobject,
    animation: Animation | None = None,
    **kwargs,
) -> HighlightedAnimation:
    return HighlightedAnimation(mobject, animation, **kwargs)


class StatefulHighlighter:
    """One-at-a-time opacity highlighter for rows, branches, or cells."""

    def __init__(self, dim_opacity=0.35, active_opacity=1.0):
        self.prev = None
        self.dim_opacity = dim_opacity
        self.active_opacity = active_opacity

    def step(self, mob: Mobject):
        animations = []
        if self.prev is not None:
            animations.append(self.prev.animate.set_opacity(self.dim_opacity))
        animations.append(mob.animate.set_opacity(self.active_opacity))
        self.prev = mob
        return animations


def gymnasium_toy_text_asset_dir() -> Path:
    """Return Gymnasium's installed toy_text image directory."""

    try:
        import gymnasium.envs.toy_text.frozen_lake as frozen_lake
    except ImportError as exc:
        raise RuntimeError("Gymnasium is required to load toy_text assets") from exc
    return Path(frozen_lake.__file__).resolve().parent / "img"


def resolve_asset_path(file_name: str | Path, asset_dir: str | Path | None = None) -> Path:
    path = Path(file_name).expanduser()
    if path.is_absolute():
        return path
    if asset_dir is not None:
        return Path(asset_dir).expanduser() / path
    return gymnasium_toy_text_asset_dir() / path


def image_asset_mobject(
    file_name: str | Path,
    *,
    asset_dir: str | Path | None = None,
    width: float | None = None,
    height: float | None = None,
):
    image = ImageMobject(str(resolve_asset_path(file_name, asset_dir)))
    if width is not None:
        image.stretch_to_fit_width(width)
    if height is not None:
        image.stretch_to_fit_height(height)
    return image


def asset_from_map_mobject(
    asset_map: Mapping[str, str | Path],
    key: str,
    *,
    asset_dir: str | Path | None = None,
    width: float | None = None,
    height: float | None = None,
):
    if key not in asset_map:
        valid = ", ".join(sorted(asset_map))
        raise ValueError(f"asset key {key!r} was not found. Valid keys: {valid}")
    return image_asset_mobject(asset_map[key], asset_dir=asset_dir, width=width, height=height)


def frozenlake_elf_mobject(
    direction: str = "down",
    *,
    width: float | None = None,
    height: float | None = None,
):
    return asset_from_map_mobject(
        FROZEN_LAKE_ELF_ASSETS,
        direction,
        asset_dir=gymnasium_toy_text_asset_dir(),
        width=width,
        height=height,
    )


def _coerce_grid_layout(
    rows: int,
    cols: int,
    grid_asset_layout: Sequence[str] | Sequence[Sequence[str]] | None,
    *,
    grid_assets: Mapping[str, str | Path] | None = None,
    default_asset_key: str | None = None,
):
    """Normalize tile placement into a rows x cols tuple of asset keys.

    Preferred input is a true 2D array of asset names, for example:
    [["white_tile", "white_tile", "trap_tile"], ...].

    A legacy compact layout such as ("SFFG", "FHFF") is still supported
    when each character is an asset key.
    """

    if grid_asset_layout is None:
        if default_asset_key is None:
            if grid_assets is None or len(grid_assets) != 1:
                raise ValueError(
                    "tile_placement/grid_asset_layout is required unless exactly one "
                    "grid asset or default_asset_key is provided"
                )
            default_asset_key = next(iter(grid_assets))
        return tuple(tuple(default_asset_key for _ in range(cols)) for _ in range(rows))

    if len(grid_asset_layout) != rows:
        raise ValueError("tile placement row count must match rows")

    normalized_rows: list[tuple[str, ...]] = []
    valid_keys = set(grid_assets or ())
    for layout_row in grid_asset_layout:
        if isinstance(layout_row, bytes):
            layout_row = layout_row.decode("utf-8")

        if isinstance(layout_row, str):
            if valid_keys and layout_row in valid_keys and cols == 1:
                row_keys = (layout_row,)
            elif len(layout_row) == cols:
                row_keys = tuple(layout_row)
            else:
                raise ValueError(
                    "string tile placement rows are only valid for compact one-character "
                    "asset keys; use a 2D array for multi-character names"
                )
        else:
            row_keys = tuple(str(key) for key in layout_row)

        if len(row_keys) != cols:
            raise ValueError("tile placement column count must match cols")
        normalized_rows.append(row_keys)

    return tuple(normalized_rows)


class ViewportGrid(Group):
    """
    Inherits from Group (NOT VGroup) to safely contain both 
    Vector mobjects (cells) and Raster mobjects (images).
    """
    def __init__(self, rows: int, cols: int, **kwargs):
        if rows <= 0 or cols <= 0:
            raise ValueError("rows and cols must both be positive")

        super().__init__(**kwargs)
        self.rows = rows
        self.cols = cols
        
        # Subgroups
        self.tile_assets = Group()
        self.cells = VGroup()
        self.add(self.tile_assets, self.cells)
        
        # Track objects placed on the grid
        self.anchored_objects = {}

    def __iter__(self):
        """Iterates over the grid cells, not over the internal subgroups."""
        return iter(self.cells)

    def _validate_cell(self, row: int, col: int):
        if not 0 <= row < self.rows or not 0 <= col < self.cols:
            raise IndexError(f"cell ({row}, {col}) is outside a {self.rows}x{self.cols} grid")

    def cell(self, row: int, col: int) -> Rectangle:
        """Returns the specific cell rectangle."""
        self._validate_cell(row, col)
        return self.cells[row * self.cols + col]

    def cell_center(self, row: int, col: int) -> np.ndarray:
        """Returns the 3D coordinate of the cell's center."""
        return self.cell(row, col).get_center()

    def anchor(self, mobject: Mobject, row: int, col: int, offset: np.ndarray = ORIGIN):
        """Snaps a traversing mobject to the given cell with an optional offset."""
        mobject.move_to(self.cell_center(row, col) + offset)
        self.anchored_objects[mobject] = (row, col)

    def release(self, mobject: Mobject):
        """Removes the mobject from the grid's tracked anchors."""
        if mobject in self.anchored_objects:
            del self.anchored_objects[mobject]


def create_iterable_grid(
    rows: int,
    cols: int,
    asset_dict: Mapping[str, str | Path],
    tile_placement: Sequence[Sequence[str]],
    *,
    width: float | None = None,
    height: float | None = None,
    grid_line_thickness: float = 2.0,
    grid_line_color = GREY_B,
    asset_dir: str | Path | None = None,
    fill_color = "#020617",
    fill_opacity: float = 0.0,
    tile_asset_opacity: float = 1.0,
    **kwargs,
) -> ViewportGrid:
    if len(tile_placement) != rows:
        raise ValueError("tile_placement row count must match rows")
    if any(len(row) != cols for row in tile_placement):
        raise ValueError("tile_placement column count must match cols")
    
    grid = ViewportGrid(rows, cols, **kwargs)

    # Calculate dimensions
    total_w = width if width is not None else cols
    total_h = height if height is not None else rows
    cell_w = total_w / cols
    cell_h = total_h / rows

    # Top-left starting coordinates
    start_x = -total_w / 2 + cell_w / 2
    start_y = total_h / 2 - cell_h / 2

    # 1. GENERATE CELLS (VGroup)
    for r in range(rows):
        for c in range(cols):
            cell = Rectangle(
                width=cell_w,
                height=cell_h,
                stroke_width=grid_line_thickness,
                stroke_color=grid_line_color,
                fill_color=fill_color,
                fill_opacity=fill_opacity
            )
            # Rows map to Y (descending), Cols map to X (ascending)
            x = start_x + c * cell_w
            y = start_y - r * cell_h
            cell.move_to(np.array([x, y, 0]))
            grid.cells.add(cell)

    # Helper to resolve image paths
    def get_asset_path(asset_name: str) -> str:
        path = asset_dict.get(asset_name)
        if path is None:
            raise ValueError(f"Asset '{asset_name}' not found in asset_dict.")
        path = Path(path)
        if path.is_absolute():
            return str(path)
        if asset_dir:
            return str(Path(asset_dir) / path)
        return str(path)

    # 2. GENERATE TILE ASSETS (Group)
    for r in range(rows):
        for c in range(cols):
            asset_key = tile_placement[r][c]
            img_path = get_asset_path(asset_key)
            img = ImageMobject(img_path)
            
            # Stretch the image to perfectly fill the grid cell
            img.stretch_to_fit_width(cell_w)
            img.stretch_to_fit_height(cell_h)
            img.set_opacity(tile_asset_opacity)
            
            # Move flat onto the grid cell, just behind the cell outline.
            img.move_to(grid.cell_center(r, c) + IN * 0.01)
            
            # Add to the internal tile asset group (inherits grid transforms)
            grid.tile_assets.add(img)

    return grid

def traverse_grid_object(
    scene: Scene, 
    grid: ViewportGrid, 
    mobject: Mobject, 
    path: Sequence[tuple[int, int]], 
    offset: np.ndarray = ORIGIN,
    run_time_per_step: float = 0.5
):
    """Animates a mobject moving cell-by-cell along a valid path."""
    if not path:
        return

    # Validate traversal rules (No diagonals, no skipped cells)
    previous = grid.anchored_objects.get(mobject)
    for r, c in path:
        grid.cell(r, c)

    if previous is not None and abs(path[0][0] - previous[0]) + abs(path[0][1] - previous[1]) != 1:
        raise ValueError(
            f"Invalid traversal from {previous} to {path[0]}. "
            "The agent can only move 1 cell horizontally or vertically."
        )

    for i in range(1, len(path)):
        r1, c1 = path[i-1]
        r2, c2 = path[i]
        
        # Manhattan distance must be exactly 1
        if abs(r2 - r1) + abs(c2 - c1) != 1:
            raise ValueError(
                f"Invalid traversal from {(r1, c1)} to {(r2, c2)}. "
                "The agent can only move 1 cell horizontally or vertically."
            )

    # Execute Animations
    for r, c in path:
        target_pos = grid.cell_center(r, c) + offset
        scene.play(mobject.animate.move_to(target_pos), run_time=run_time_per_step)
        
        # Update tracked state post-animation
        grid.anchored_objects[mobject] = (r, c)


def orbit_camera_to_45_degrees(
    scene: Scene,
    center_mobject: Mobject,
    *,
    radius: float = 8.0,
    reference_radius: float = 8.0,
    phi: float = 45 * DEGREES,
    theta: float = -45 * DEGREES,
    gamma: float = 0.0,
    run_time: float = 1.4,
    rate_func=smooth,
    added_anims: Iterable[Animation] | None = None,
):
    """Move a ThreeDScene camera from upright view to a 45-degree orbit view."""

    if radius <= 0:
        raise ValueError("radius must be positive")
    if reference_radius <= 0:
        raise ValueError("reference_radius must be positive")
    if not hasattr(scene, "move_camera"):
        raise TypeError("orbit_camera_to_45_degrees requires a ThreeDScene")

    scene.move_camera(
        phi=phi,
        theta=theta,
        gamma=gamma,
        focal_distance=radius,
        zoom=reference_radius / radius,
        frame_center=center_mobject.get_center(),
        run_time=run_time,
        rate_func=rate_func,
        added_anims=[] if added_anims is None else list(added_anims),
    )
    return center_mobject


def reset_orbit_camera(
    scene: Scene,
    *,
    frame_center=ORIGIN,
    radius: float = 8.0,
    run_time: float = 1.0,
    rate_func=smooth,
):
    """Return a ThreeDScene camera to the upright default orientation."""

    if radius <= 0:
        raise ValueError("radius must be positive")
    if not hasattr(scene, "move_camera"):
        raise TypeError("reset_orbit_camera requires a ThreeDScene")

    if run_time <= 0:
        scene.set_camera_orientation(
            phi=0,
            theta=-90 * DEGREES,
            gamma=0,
            focal_distance=radius,
            zoom=1.0,
            frame_center=frame_center,
        )
        return

    scene.move_camera(
        phi=0,
        theta=-90 * DEGREES,
        gamma=0,
        focal_distance=radius,
        zoom=1.0,
        frame_center=frame_center,
        run_time=run_time,
        rate_func=rate_func,
    )


def transform_equation(
    scene: Scene,
    source_equation: MathTex,
    target_equation: MathTex | str,
    *,
    source_part: str | None = None,
    target_part: str | None = None,
    transform_type=ReplacementTransform,
    run_time: float = 0.9,
):
    """Transform a full equation or only matching parts between equations."""

    target = (
        MathTex(target_equation, font_size=source_equation.font_size)
        if isinstance(target_equation, str)
        else target_equation
    )
    target.move_to(source_equation)

    if source_part is None and target_part is None:
        scene.play(transform_type(source_equation, target), run_time=run_time)
        return target

    if source_part is None or target_part is None:
        raise ValueError("source_part and target_part must be provided together")

    source_piece = source_equation.get_part_by_tex(source_part)
    target_piece = target.get_part_by_tex(target_part)
    if source_piece is None:
        raise ValueError(f"source_part {source_part!r} was not found in source_equation")
    if target_piece is None:
        raise ValueError(f"target_part {target_part!r} was not found in target_equation")

    animations: list[Animation] = []
    if (
        source_piece in source_equation.submobjects
        and target_piece in target.submobjects
        and len(source_equation.submobjects) == len(target.submobjects)
    ):
        source_index = source_equation.submobjects.index(source_piece)
        target_index = target.submobjects.index(target_piece)
        for index, source_child in enumerate(source_equation.submobjects):
            if index == source_index:
                continue
            if source_index != target_index and index == target_index:
                continue
            animations.append(Transform(source_child, target.submobjects[index]))
        animations.append(transform_type(source_piece, target_piece))
    else:
        animations.append(transform_type(source_piece, target_piece))
        animations.append(Transform(source_equation, target))

    scene.play(*animations, run_time=run_time)
    scene.remove(source_equation)
    scene.add(target)
    return target


class FormulaStepper:
    def __init__(self, formulas: Iterable[str], *, font_size=36, color=WHITE):
        self.formulas = list(formulas)
        self.font_size = font_size
        self.color = color
        self.current = 0
        self.formula = self._make_formula(0)

    def _make_formula(self, index):
        return MathTex(self.formulas[index], font_size=self.font_size, color=self.color)

    def get(self):
        return self.formula

    def next(self):
        self.current += 1
        updated = self._make_formula(self.current)
        updated.move_to(self.formula)
        self.formula = updated
        return updated


def frozenlake_frame(state: int, height: float = 2.8) -> Mobject:
    path = FRAME_DIR / f"state_{state:02d}.png"
    if path.exists():
        image = ImageMobject(str(path))
        image.scale_to_fit_height(height)
        return image
    fallback = RoundedRectangle(
        corner_radius=0.16,
        width=3.0,
        height=height,
        stroke_color=BLUE_E,
        fill_color="#0F172A",
        fill_opacity=1.0,
    )
    label = Text(f"State {state}", font_size=24).move_to(fallback)
    return VGroup(fallback, label)


def pill(label: str, color: str) -> VGroup:
    text = Text(label, font_size=22, color=color, weight=BOLD)
    box = RoundedRectangle(
        corner_radius=0.16,
        width=text.width + 0.5,
        height=text.height + 0.24,
        stroke_color=color,
        fill_color=color,
        fill_opacity=0.08,
    )
    text.move_to(box)
    return VGroup(box, text)
