import json
import logging
import os
import subprocess
from pathlib import Path

from backend.logger.event_logger import NpEncoder
from backend.settings import VisualizationSettings

logging.basicConfig(level=logging.INFO)

REPLAY_TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "replay_scene.py.tmpl"


class VisualizationController:
    """Ingests EventLogger data to dynamically generate Manim animations."""

    def __init__(
        self,
        output_dir: str | None = None,
        manim_python_path: str | None = None,
    ):
        settings = VisualizationSettings.from_env()
        self.output_dir = output_dir or settings.output_dir
        self.manim_python_path = manim_python_path or settings.manim_python_path
        self.manim_timeout_seconds = settings.manim_timeout_seconds
        os.makedirs(self.output_dir, exist_ok=True)
        self.scenes_dir = os.path.join(self.output_dir, "scenes")
        os.makedirs(self.scenes_dir, exist_ok=True)

    def generate_animation(self, log_data: list, lesson_id: str) -> str:
        if not log_data or not log_data[0]:
            logging.warning("No log data provided for Manim visualization.")
            return ""

        latest_episode = log_data[-1]
        data_path = self._write_trace_data(latest_episode)
        scene_file = os.path.join(self.scenes_dir, f"{lesson_id}_scene.py")
        self._write_manim_script(scene_file, data_path, lesson_id)
        return self._render_scene(scene_file, lesson_id)

    def _write_trace_data(self, latest_episode: list) -> str:
        data_path = os.path.join(self.scenes_dir, "temp_data.json")
        with open(data_path, "w", encoding="utf-8") as file_handle:
            json.dump(latest_episode, file_handle, cls=NpEncoder)
        return data_path

    def _render_scene(self, scene_file: str, lesson_id: str) -> str:
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
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=self.manim_timeout_seconds,
            )
            logging.info("Manim generated successfully.")
            expected_mp4 = self._expected_video_path(lesson_id)
            return expected_mp4 if os.path.exists(expected_mp4) else ""
        except subprocess.TimeoutExpired as error:
            logging.error("Manim generation timed out after %s seconds.", error.timeout)
            return ""
        except subprocess.CalledProcessError as error:
            logging.error("Manim failure output: %s\n%s", error.stdout, error.stderr)
            return ""

    def _expected_video_path(self, lesson_id: str) -> str:
        return os.path.join(
            os.path.abspath(self.output_dir),
            "videos",
            f"{lesson_id}_scene",
            "480p15",
            "RLEpisodeScene.mp4",
        )

    def _write_manim_script(self, script_path: str, data_path: str, lesson_id: str):
        script_content = REPLAY_TEMPLATE_PATH.read_text(encoding="utf-8")
        script_content = script_content.replace("__DATA_PATH__", repr(data_path))
        script_content = script_content.replace("__LESSON_ID__", repr(lesson_id))
        with open(script_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(script_content)
