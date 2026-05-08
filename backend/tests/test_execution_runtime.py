from __future__ import annotations

import os
from dataclasses import dataclass

from backend.execution_runtime import _run_execution_pipeline
from backend.validation.validator import ValidationResult


@dataclass(frozen=True)
class _Lesson:
    id: str = "demo_lesson"
    title: str = "Demo Lesson"
    environment_name: str = "FrozenLake"


class _FakeValidator:
    def validate_code(self, submitted_code: str, lesson_id: str) -> ValidationResult:
        del submitted_code, lesson_id
        return ValidationResult(
            is_valid=True,
            errors=[],
            test_results=[],
            unresolved_blanks=[],
        )


class _FakeAdapter:
    def __init__(self, env_name: str, frame_dir: str) -> None:
        del env_name
        self.frame_dir = frame_dir

    def close(self) -> None:
        return None


class _FakeEngine:
    def __init__(self, adapter: _FakeAdapter, logger) -> None:
        self.adapter = adapter
        self.logger = logger

    def run_episodes(self, lesson_id, code_module_str, num_episodes, hyperparameters):
        del lesson_id, code_module_str, num_episodes, hyperparameters
        frame_path = os.path.join(self.adapter.frame_dir, "frame_001.png")
        os.makedirs(os.path.dirname(frame_path), exist_ok=True)
        with open(frame_path, "wb") as file_handle:
            file_handle.write(b"png")
        self.logger.log_step(
            {
                "state": 0,
                "action": 1,
                "next_state": 1,
                "reward": 0.0,
                "frame_path": frame_path,
                "updated_values": {"V(0)": 0.0},
            }
        )
        self.logger.end_episode()


class _FakeVisualizationService:
    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir

    def generate_animation(self, log_data, lesson_id):
        del log_data, lesson_id
        return ""


def test_execution_trace_frame_paths_are_absolute(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "backend.execution_runtime.get_lesson_definition",
        lambda lesson_id: _Lesson(id=lesson_id),
    )
    monkeypatch.setattr("backend.execution_runtime.CodeValidator", lambda: _FakeValidator())
    monkeypatch.setattr("backend.execution_runtime.EnvironmentAdapter", _FakeAdapter)
    monkeypatch.setattr("backend.execution_runtime.RLEngine", _FakeEngine)
    monkeypatch.setattr(
        "backend.execution_runtime.VisualizationService",
        _FakeVisualizationService,
    )
    monkeypatch.setattr("backend.execution_runtime.load_user_context", lambda code: {})

    result = _run_execution_pipeline(
        {
            "lesson_id": "demo_lesson",
            "code": "def demo(): pass",
            "episode_count": 1,
        }
    )

    frame_path = result["step_trace"][0]["frame_path"]
    assert os.path.isabs(frame_path)
    assert os.path.exists(frame_path)
