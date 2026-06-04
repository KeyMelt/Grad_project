from __future__ import annotations

import os
from dataclasses import dataclass

import backend.execution_runtime as execution_runtime
import backend.lesson_registry as lesson_registry
from backend.execution_runtime import _derive_timeout_seconds, _run_execution_pipeline
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


class _FakeMultiEpisodeEngine:
    def __init__(self, adapter: _FakeAdapter, logger) -> None:
        self.adapter = adapter
        self.logger = logger

    def run_episodes(self, lesson_id, code_module_str, num_episodes, hyperparameters):
        del lesson_id, code_module_str, num_episodes, hyperparameters
        self.logger.log_step(
            {
                "state": 0,
                "action": 1,
                "next_state": 1,
                "reward": -1.0,
                "updated_values": {"V(0)": 0.0},
            }
        )
        self.logger.end_episode()
        self.logger.log_step(
            {
                "state": 2,
                "action": 0,
                "next_state": 3,
                "reward": 2.0,
                "updated_values": {"V(2)": 1.0},
                "grid_metadata": {"terminated": True, "truncated": False},
            }
        )
        self.logger.end_episode()


class _FakeVisualizationService:
    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir

    def generate_animation(self, log_data, lesson_id):
        del log_data, lesson_id
        return ""

    def enqueue_replay_render(self, log_data, lesson_id):
        del log_data, lesson_id
        return {
            "replay_render_job_id": "render-job",
            "replay_render_status": "queued",
            "replay_episode_indices": [0],
        }


def test_derived_submission_timeout_scales_but_remains_capped(monkeypatch):
    monkeypatch.delenv("RL_IDE_EXECUTION_TIMEOUT_BASE_SECONDS", raising=False)
    monkeypatch.delenv("RL_IDE_EXECUTION_TIMEOUT_PER_EPISODE_SECONDS", raising=False)
    monkeypatch.delenv("RL_IDE_EXECUTION_TIMEOUT_MAX_SECONDS", raising=False)

    timeout_seconds = _derive_timeout_seconds(
        {
            "lesson_id": "demo_lesson",
            "code": "EPISODE_COUNT = 500\n",
        }
    )

    assert timeout_seconds == 900


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


def test_execution_response_includes_episode_summaries_and_traces(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "backend.execution_runtime.get_lesson_definition",
        lambda lesson_id: _Lesson(id=lesson_id),
    )
    monkeypatch.setattr("backend.execution_runtime.CodeValidator", lambda: _FakeValidator())
    monkeypatch.setattr("backend.execution_runtime.EnvironmentAdapter", _FakeAdapter)
    monkeypatch.setattr("backend.execution_runtime.RLEngine", _FakeMultiEpisodeEngine)
    monkeypatch.setattr(
        "backend.execution_runtime.VisualizationService",
        _FakeVisualizationService,
    )
    monkeypatch.setattr("backend.execution_runtime.load_user_context", lambda code: {})

    result = _run_execution_pipeline(
        {
            "lesson_id": "demo_lesson",
            "code": "def demo(): pass",
            "episode_count": 2,
        }
    )

    assert [episode["episode_index"] for episode in result["trace_episodes"]] == [0, 1]
    assert result["trace_episodes"][0]["steps"][0]["state"] == 0
    assert result["trace_episodes"][1]["steps"][0]["state"] == 2
    assert result["step_trace"] == result["trace_episodes"][-1]["steps"]
    assert result["episode_summaries"] == [
        {
            "episode_index": 0,
            "step_count": 1,
            "total_reward": -1.0,
            "terminated": False,
            "truncated": False,
        },
        {
            "episode_index": 1,
            "step_count": 1,
            "total_reward": 2.0,
            "terminated": True,
            "truncated": False,
        },
    ]


def test_execution_runtime_initializes_registry_for_spawned_process(monkeypatch, tmp_path):
    database_path = tmp_path / "spawn_registry.db"
    monkeypatch.setenv("RL_IDE_DB_URL", f"sqlite:///{database_path}")
    lesson_registry.set_registry(None)  # type: ignore[arg-type]

    previous_database = execution_runtime._PROCESS_REGISTRY_DATABASE
    execution_runtime._PROCESS_REGISTRY_DATABASE = None
    try:
        execution_runtime._ensure_process_lesson_registry()

        lesson = lesson_registry.get_lesson_definition("td_sarsa")
        assert lesson is not None
        assert lesson.required_function == "sarsa_update"
    finally:
        database = execution_runtime._PROCESS_REGISTRY_DATABASE
        if database is not None:
            database.close()
        execution_runtime._PROCESS_REGISTRY_DATABASE = previous_database
