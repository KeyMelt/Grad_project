from __future__ import annotations

from manim import Circle, DEGREES, FadeIn, OUT, ThreeDScene, WHITE

try:
    from backend.concept_videos.scenes.helpers import (
        create_iterable_grid,
        gymnasium_toy_text_asset_dir,
        traverse_grid,
    )
except ModuleNotFoundError:
    from helpers import create_iterable_grid, gymnasium_toy_text_asset_dir, traverse_grid


class IterableGridOrbitDemo(ThreeDScene):
    """Demo: sprite traverses grid while camera revolves around grid center."""

    def construct(self):
        self.camera.background_color = "#020617"
        asset_dir = gymnasium_toy_text_asset_dir()

        asset_dict = {
            "start": "stool.png",
            "ice": "ice.png",
            "hole": "hole.png",
            "goal": "goal.png",
        }
        tile_placement = [
            ["start", "ice", "ice", "hole"],
            ["ice", "hole", "ice", "hole"],
            ["ice", "ice", "ice", "hole"],
            ["hole", "ice", "ice", "goal"],
        ]

        grid = create_iterable_grid(
            rows=4,
            cols=4,
            asset_dict=asset_dict,
            tile_placement=tile_placement,
            asset_dir=asset_dir,
            width=5.6,
            height=5.6,
            grid_line_thickness=2.4,
            grid_line_color="#E2E8F0",
        )

        agent = Circle(
            radius=grid.cell_width * 0.20,
            stroke_color=WHITE,
            stroke_width=3.0,
            fill_color="#F59E0B",
            fill_opacity=0.95,
        )
        grid.anchor_traverser(agent, 0, 1, offset=OUT * 0.22)

        self.set_camera_orientation(
            phi=0,
            theta=-90 * DEGREES,
            frame_center=grid.get_center(),
            zoom=1.0,
        )
        self.play(FadeIn(grid), run_time=0.8)

        self.move_camera(
            phi=60 * DEGREES,
            theta=-45 * DEGREES,
            frame_center=grid.get_center(),
            run_time=1.2,
        )
        self.begin_ambient_camera_rotation(rate=0.18, about="theta")

        traverse_grid(
            self,
            grid,
            agent,
            [(0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (1, 1), (1, 2), (2, 2)],
            run_time_per_step=0.48,
        )

        self.wait(1.4)
        self.stop_ambient_camera_rotation()
