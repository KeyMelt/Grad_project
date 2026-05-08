from manim import *

try:
    from backend.concept_videos.scenes.helpers import (
        create_iterable_grid,
        gymnasium_toy_text_asset_dir,
        traverse_grid,
    )
except ModuleNotFoundError:
    from helpers import create_iterable_grid, gymnasium_toy_text_asset_dir, traverse_grid


class IterableGridOrbitDemo(ThreeDScene):
    def construct(self):
        self.camera.background_color = "#020617"
        asset_dir = gymnasium_toy_text_asset_dir()

        Asset_dict = {
            "white_tile": "ice.png",
            "trap_tile": "hole.png",
            "goal_tile": "goal.png",
        }
        tile_placement = [
            ["white_tile", "white_tile", "trap_tile"],
            ["trap_tile", "white_tile", "trap_tile"],
            ["white_tile", "goal_tile", "trap_tile"],
        ]

        grid = create_iterable_grid(
            rows=3,
            cols=3,
            Asset_dict=Asset_dict,
            tile_placement=tile_placement,
            asset_dir=asset_dir,
            width=4.8,
            height=4.8,
            grid_line_thickness=2.4,
            grid_line_color="#E2E8F0",
        )
        agent = ImageMobject(str(asset_dir / "elf_down.png"))
        agent.stretch_to_fit_width(grid.cell_width * 0.62)
        agent.stretch_to_fit_height(grid.cell_height * 0.62)
        grid.anchor(agent, 0, 0)

        self.set_camera_orientation(
            phi=0,
            theta=-90 * DEGREES,
            frame_center=grid.get_center(),
            zoom=1.0,
        )
        self.play(FadeIn(grid), FadeIn(agent), run_time=0.8)
        self.wait(0.25)

        self.move_camera(
            phi=58 * DEGREES,
            theta=-45 * DEGREES,
            frame_center=grid.get_center(),
            run_time=1.2,
        )
        self.begin_ambient_camera_rotation(rate=0.18, about="theta")
        traverse_grid(
            self,
            grid,
            agent,
            [(0, 1), (1, 1), (2, 1)],
            run_time_per_step=0.55,
        )
        self.wait(2.0)
        self.stop_ambient_camera_rotation()
