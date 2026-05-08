from __future__ import annotations

import subprocess
import sys

from backend.visualization.controller import VisualizationController


def test_visualization_controller_returns_empty_path_on_manim_timeout(
    monkeypatch,
    tmp_path,
):
    captured_timeout: list[int] = []

    def fake_run(*args, **kwargs):
        del args
        captured_timeout.append(kwargs["timeout"])
        raise subprocess.TimeoutExpired(cmd="manim", timeout=kwargs["timeout"])

    monkeypatch.setenv("RL_IDE_MANIM_TIMEOUT_SECONDS", "7")
    monkeypatch.setattr(subprocess, "run", fake_run)

    controller = VisualizationController(
        output_dir=str(tmp_path / "animations"),
        manim_python_path=sys.executable,
    )

    video_path = controller.generate_animation(
        [[{"state": 0, "action": 1, "reward": 0, "next_state": 1}]],
        "td_q_learning",
    )

    assert video_path == ""
    assert captured_timeout == [7]


def test_visualization_controller_writes_stepwise_equation_replay_scene(tmp_path):
    controller = VisualizationController(
        output_dir=str(tmp_path / "animations"),
        manim_python_path=sys.executable,
    )
    scene_path = tmp_path / "td_q_learning_scene.py"
    data_path = tmp_path / "temp_data.json"

    controller._write_manim_script(
        script_path=str(scene_path),
        data_path=str(data_path),
        lesson_id="td_q_learning",
    )

    script = scene_path.read_text()
    assert "Manim replay: agent step to Bellman update" in script
    assert "build_backup" in script
    assert "build_update" in script
    assert "equation_update" in script
    assert "stack = Group(title, state_line, visual)" in script
    assert "Circumscribe(current_backup" in script
