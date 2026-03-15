import subprocess
import os
import json
import logging
from backend.logger.event_logger import NpEncoder

logging.basicConfig(level=logging.INFO)

class VisualizationController:
    """Ingests EventLogger data to dynamically generate Manim animations."""
    
    def __init__(self, output_dir="backend/visualization/animations", manim_python_path="/Users/ultramarine/.venvs/manim/bin/python3"):
        self.output_dir = output_dir
        self.manim_python_path = manim_python_path
        os.makedirs(self.output_dir, exist_ok=True)
        # Directory where temporary scene files will be built before rendering
        self.scenes_dir = os.path.join(self.output_dir, "scenes")
        os.makedirs(self.scenes_dir, exist_ok=True)

    def generate_animation(self, log_data: list, lesson_id: str) -> str:
        """
        Takes the log_data from EventLogger and uses Manim to generate an mp4.
        Returns the path to the generated MP4.
        """
        if not log_data or not log_data[0]:
            logging.warning("No log data provided for Manim visualization.")
            return ""

        # Dump the latest episode log to a temporary JSON file to feed into Manim script
        latest_episode = log_data[-1] 
        data_path = os.path.join(self.scenes_dir, "temp_data.json")
        with open(data_path, "w") as f:
            json.dump(latest_episode, f, cls=NpEncoder)

        # Generate the Manim scene file dynamically
        scene_file = os.path.join(self.scenes_dir, f"{lesson_id}_scene.py")
        self._write_manim_script(scene_file, data_path, lesson_id)
        
        # Build the Manim executing command
        # manim -pqL <scene_file.py> RLEpisodeScene
        video_output_dir = os.path.abspath(self.output_dir)
        cmd = [
            self.manim_python_path, "-m", "manim",
            "-pqL", # Preview quality (L) for speed in IDE. p for preview (renders mp4). qL = Low Quality.
            "--media_dir", video_output_dir,
            scene_file,
            "RLEpisodeScene"
        ]
        
        logging.info(f"Triggering Manim generation: {' '.join(cmd)}")
        if not os.path.exists(self.manim_python_path):
            logging.warning("Manim python path does not exist: %s", self.manim_python_path)
            return ""

        try:
             subprocess.run(cmd, capture_output=True, text=True, check=True)
             logging.info("Manim generated successfully.")
             # manim output path structure: media_dir/videos/{scene_file}/480p15/RLEpisodeScene.mp4
             expected_mp4 = os.path.join(video_output_dir, "videos", f"{lesson_id}_scene", "480p15", "RLEpisodeScene.mp4")
             return expected_mp4 if os.path.exists(expected_mp4) else ""
             
        except subprocess.CalledProcessError as e:
            logging.error(f"Manim failure output: {e.stdout}\n{e.stderr}")
            return ""

    def _write_manim_script(self, script_path: str, data_path: str, lesson_id: str):
         """Generates a dynamic Manim python file using the recorded data."""
         script_content = f"""
from manim import *
import json

class RLEpisodeScene(Scene):
    def construct(self):
        # Load the RL steps data
        with open("{data_path}", "r") as f:
            log_data = json.load(f)
            
        # Draw base grid (Assuming FrozenLake 4x4)
        grid = NumberPlane(
            x_range=[-2, 2, 1],
            y_range=[-2, 2, 1],
            background_line_style={{"stroke_color": TEAL, "stroke_width": 2, "stroke_opacity": 0.6}}
        )
        self.add(grid)
        
        title = Text("Simulation: {lesson_id}", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # We start agent at state 0 (top-left) in 4x4 grid. Coordinates roughly map to [-1.5, 1.5]
        agent = Dot(color=RED, radius=0.2).move_to(grid.c2p(-1.5, 1.5))
        self.add(agent)
        
        for step in log_data:
            state = step.get("state", 0)
            next_state = step.get("next_state", 0)
            reward = step.get("reward", 0)
            action = step.get("action", 0)
            
            # Simple State -> Coordinate Mapping for 4x4 FrozenLake
            def s_to_coord(s):
                row = s // 4
                col = s % 4
                x = -1.5 + col
                y = 1.5 - row
                return grid.c2p(x, y)
                
            # Move Agent
            new_pos = s_to_coord(next_state)
            self.play(agent.animate.move_to(new_pos), run_time=0.5)
            
            # If Q_learning or similar, show value updates
            updated_vals = step.get("updated_values", {{}})
            for key, val in updated_vals.items():
                val_text = Text(f"{{key}} = {{val}}", font_size=20, color=YELLOW).next_to(agent, DOWN)
                self.play(FadeIn(val_text), run_time=0.3)
                self.play(FadeOut(val_text), run_time=0.3)
                
        self.wait(2)
"""
         with open(script_path, "w") as f:
             f.write(script_content)
