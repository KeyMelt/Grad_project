import json
import logging
import os
import subprocess

from backend.logger.event_logger import NpEncoder

logging.basicConfig(level=logging.INFO)


class VisualizationController:
    """Ingests EventLogger data to dynamically generate Manim animations."""

    def __init__(
        self,
        output_dir="backend/visualization/animations",
        manim_python_path="/Users/ultramarine/.venvs/manim/bin/python3",
    ):
        self.output_dir = output_dir
        self.manim_python_path = manim_python_path
        os.makedirs(self.output_dir, exist_ok=True)
        self.scenes_dir = os.path.join(self.output_dir, "scenes")
        os.makedirs(self.scenes_dir, exist_ok=True)

    def generate_animation(self, log_data: list, lesson_id: str) -> str:
        if not log_data or not log_data[0]:
            logging.warning("No log data provided for Manim visualization.")
            return ""

        latest_episode = log_data[-1]
        data_path = os.path.join(self.scenes_dir, "temp_data.json")
        with open(data_path, "w") as file_handle:
            json.dump(latest_episode, file_handle, cls=NpEncoder)

        scene_file = os.path.join(self.scenes_dir, f"{lesson_id}_scene.py")
        self._write_manim_script(scene_file, data_path, lesson_id)

        video_output_dir = os.path.abspath(self.output_dir)
        cmd = [
            self.manim_python_path,
            "-m",
            "manim",
            "-pqL",
            "--media_dir",
            video_output_dir,
            scene_file,
            "RLEpisodeScene",
        ]

        logging.info("Triggering Manim generation: %s", " ".join(cmd))
        if not os.path.exists(self.manim_python_path):
            logging.warning("Manim python path does not exist: %s", self.manim_python_path)
            return ""

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logging.info("Manim generated successfully.")
            expected_mp4 = os.path.join(
                video_output_dir,
                "videos",
                f"{lesson_id}_scene",
                "480p15",
                "RLEpisodeScene.mp4",
            )
            return expected_mp4 if os.path.exists(expected_mp4) else ""
        except subprocess.CalledProcessError as error:
            logging.error("Manim failure output: %s\n%s", error.stdout, error.stderr)
            return ""

    def _write_manim_script(self, script_path: str, data_path: str, lesson_id: str):
        script_content = f"""
from manim import *
import json
import os


def build_frame(step):
    frame_path = step.get("frame_path", "")
    if frame_path and os.path.exists(frame_path):
        return ImageMobject(frame_path).scale_to_fit_height(4.4)

    fallback = Rectangle(width=4.8, height=4.4, color=BLUE_E)
    fallback_text = Text("FrozenLake frame unavailable", font_size=22).move_to(fallback.get_center())
    return VGroup(fallback, fallback_text)


def build_reasoning_panel(step):
    title = Text(step.get("code_title", "Code Trace"), font_size=26, weight=BOLD, color=BLUE_A)
    probability = step.get("transition_probability", 1.0)
    probability_text = Text(f"p = {{probability}}", font_size=20, color=GREY_A)

    lines = step.get("code_lines", [])
    rendered_lines = [
        Text(line, font_size=18, line_spacing=0.82, font="Menlo")
        for line in lines[:4]
    ]
    if not rendered_lines:
        rendered_lines = [Text("No code trace recorded.", font_size=18, font="Menlo")]

    stack = VGroup(title, probability_text, *rendered_lines).arrange(
        DOWN,
        aligned_edge=LEFT,
        buff=0.18,
    )
    box = RoundedRectangle(
        corner_radius=0.15,
        width=4.9,
        height=max(2.2, stack.height + 0.45),
        stroke_color=BLUE_E,
        fill_color="#1e293b",
        fill_opacity=0.86,
    )
    stack.move_to(box.get_center())
    return VGroup(box, stack)


def build_math_panel(step):
    title = Text(step.get("math_title", "Mathematics"), font_size=26, weight=BOLD, color=YELLOW_A)
    equation = MathTex(step.get("math_equation", r"\\text{{No equation provided}}"), font_size=34)
    lines = step.get("math_lines", [])
    rendered_lines = [
        Text(line, font_size=18, line_spacing=0.82)
        for line in lines[:4]
    ]
    stack = VGroup(title, equation, *rendered_lines).arrange(
        DOWN,
        aligned_edge=LEFT,
        buff=0.18,
    )
    box = RoundedRectangle(
        corner_radius=0.15,
        width=4.9,
        height=max(2.5, stack.height + 0.45),
        stroke_color=YELLOW_E,
        fill_color="#111827",
        fill_opacity=0.9,
    )
    stack.scale_to_fit_width(box.width - 0.45)
    stack.move_to(box.get_center())
    return VGroup(box, stack)


def build_update_panel(step):
    updated_values = step.get("updated_values", {{}})
    rows = [Text(f"{{key}} = {{value}}", font_size=22, color=YELLOW_B) for key, value in updated_values.items()]
    if not rows:
        rows = [Text("No value update recorded.", font_size=22, color=YELLOW_B)]

    stack = VGroup(*rows[:4]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    box = RoundedRectangle(
        corner_radius=0.15,
        width=4.9,
        height=max(1.4, stack.height + 0.35),
        stroke_color=YELLOW_E,
        fill_color="#020617",
        fill_opacity=0.86,
    )
    stack.move_to(box.get_center())
    return VGroup(box, stack)


class RLEpisodeScene(Scene):
    def construct(self):
        self.camera.background_color = "#020617"
        with open({data_path!r}, "r") as file_handle:
            log_data = json.load(file_handle)

        title = Text("FrozenLake lesson: {lesson_id}", font_size=34, color=WHITE).to_edge(UP)
        subtitle = Text("Agent state  •  code trace  •  mathematics", font_size=22, color=GREY_B).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(title), FadeIn(subtitle))

        if not log_data:
            empty = Text("No trace data available.", font_size=24).move_to(ORIGIN)
            self.play(FadeIn(empty))
            self.wait(1)
            return

        current_frame = build_frame(log_data[0]).to_edge(LEFT, buff=0.45)
        current_code = build_reasoning_panel(log_data[0]).move_to(ORIGIN + UP * 0.75)
        current_math = build_math_panel(log_data[0]).to_edge(RIGHT, buff=0.45).shift(UP * 0.75)
        current_update = build_update_panel(log_data[0]).next_to(current_code, DOWN, buff=0.28)
        caption = Text(log_data[0].get("agent_caption", "Step explanation"), font_size=20, color=WHITE).next_to(current_frame, DOWN, buff=0.2)
        step_label = Text("Step 1", font_size=24, color=GREEN_B).next_to(caption, DOWN, buff=0.12)

        self.play(FadeIn(current_frame), FadeIn(current_code), FadeIn(current_math), FadeIn(current_update), FadeIn(caption), FadeIn(step_label))

        for index, step in enumerate(log_data[1:], start=2):
            next_frame = build_frame(step).to_edge(LEFT, buff=0.45)
            next_code = build_reasoning_panel(step).move_to(ORIGIN + UP * 0.75)
            next_math = build_math_panel(step).to_edge(RIGHT, buff=0.45).shift(UP * 0.75)
            next_update = build_update_panel(step).next_to(next_code, DOWN, buff=0.28)
            next_caption = Text(step.get("agent_caption", "Step explanation"), font_size=20, color=WHITE).next_to(next_frame, DOWN, buff=0.2)
            next_step_label = Text(f"Step {{index}}", font_size=24, color=GREEN_B).next_to(next_caption, DOWN, buff=0.12)

            self.play(
                FadeOut(current_frame),
                FadeOut(current_code),
                FadeOut(current_math),
                FadeOut(current_update),
                FadeOut(caption),
                FadeOut(step_label),
                FadeIn(next_frame),
                FadeIn(next_code),
                FadeIn(next_math),
                FadeIn(next_update),
                FadeIn(next_caption),
                FadeIn(next_step_label),
                run_time=0.7,
            )

            current_frame = next_frame
            current_code = next_code
            current_math = next_math
            current_update = next_update
            caption = next_caption
            step_label = next_step_label

        self.wait(1.2)
"""
        with open(script_path, "w") as file_handle:
            file_handle.write(script_content)
