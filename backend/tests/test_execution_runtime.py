from __future__ import annotations

import os
from dataclasses import dataclass

import backend.execution_runtime as execution_runtime
import backend.lesson_registry as lesson_registry
from backend.execution_runtime import (
    _derive_timeout_seconds,
    _resolve_submission_lesson_contract,
    _run_execution_pipeline,
)
from backend.rl_engine.engine import RLEngine
from backend.validation.validator import ValidationResult


@dataclass(frozen=True)
class _Lesson:
    id: str = "demo_lesson"
    title: str = "Demo Lesson"
    environment_name: str = "FrozenLake"
    required_function: str = "demo"


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
    def __init__(self, env_name: str, frame_dir: str, env_params: dict | None = None) -> None:
        del env_name, env_params
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


class _FakeThreeEpisodeEngine:
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
                "reward": -5.0,
                "updated_values": {"V(0)": 0.0},
                "grid_metadata": {"terminated": False, "truncated": True},
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
        self.logger.log_step(
            {
                "state": 4,
                "action": 0,
                "next_state": 5,
                "reward": -1.0,
                "updated_values": {"V(4)": 0.5},
                "grid_metadata": {"terminated": False, "truncated": False},
            }
        )
        self.logger.end_episode()


class _FakeTdEvaluationEngine:
    def __init__(self, adapter: _FakeAdapter, logger) -> None:
        self.adapter = adapter
        self.logger = logger

    def run_episodes(self, lesson_id, code_module_str, num_episodes, hyperparameters):
        del lesson_id, code_module_str, num_episodes, hyperparameters
        self.logger.log_step(
            {
                "state": 12,
                "action": 2,
                "next_state": 13,
                "reward": -1.0,
                "updated_values": {"Q(12, 2)": 0.5},
                "grid_metadata": {"terminated": False, "truncated": False},
                "equation_update": {
                    "kind": "q_learning",
                    "lhs": "Q(12,2)",
                    "td_target": 0.5,
                    "new_value": 0.5,
                },
            }
        )
        self.logger.log_step(
            {
                "state": 13,
                "action": 4,
                "next_state": 14,
                "reward": 20.0,
                "updated_values": {"Q(13, 4)": 1.0},
                "grid_metadata": {"terminated": True, "truncated": False},
                "equation_update": {
                    "kind": "q_learning",
                    "lhs": "Q(13,4)",
                    "td_target": 1.0,
                    "new_value": 1.0,
                },
            }
        )
        self.logger.end_episode()
        return {
            "evaluation_summary": {
                "mode": "greedy_evaluation",
                "training_episodes_run": 500,
                "evaluation_attempts_run": 3,
                "selected_seed": 2,
                "selected_step_count": 2,
                "selected_total_reward": 19.0,
                "selected_terminated": True,
            }
        }


class _FakeBlackjackActionSpace:
    def sample(self) -> int:
        return 0


class _FakeBlackjackEnv:
    action_space = _FakeBlackjackActionSpace()


class _FakeBlackjackAdapter:
    env = _FakeBlackjackEnv()

    def reset(self, seed: int | None = None):
        del seed
        return (16, 10, False), {}

    def step(self, action: int):
        del action
        return (18, 10, False), 1.0, True, False, {"p": 1.0}

    def action_label(self, action: int) -> str:
        return f"action {action}"

    def capture_frame_png(self, state=None, prefix: str = "step") -> str:
        del prefix
        assert state is None
        return ""


class _FakeTraceLogger:
    def __init__(self) -> None:
        self.episodes: list[list[dict]] = [[]]

    def log_step(self, step: dict) -> None:
        self.episodes[-1].append(step)

    def end_episode(self) -> None:
        self.episodes.append([])


class _FakeVisualizationService:
    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir

    def generate_animation(self, log_data, lesson_id):
        del log_data, lesson_id
        return ""


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


def test_submission_lesson_contract_resolves_stale_selected_lesson(monkeypatch):
    lessons = {
        "dp_policy_eval": _Lesson(
            id="dp_policy_eval",
            title="Policy Evaluation",
            required_function="policy_evaluation",
        ),
        "mc_first_visit": _Lesson(
            id="mc_first_visit",
            title="First-Visit Monte Carlo",
            required_function="mc_first_visit_prediction",
        ),
    }
    monkeypatch.setattr(
        "backend.execution_runtime.get_lesson_definition",
        lambda lesson_id: lessons.get(lesson_id),
    )
    monkeypatch.setattr(
        "backend.execution_runtime.list_lesson_definitions",
        lambda: list(lessons.values()),
    )

    resolved = _resolve_submission_lesson_contract(
        {
            "lesson_id": "dp_policy_eval",
            "code": (
                "def mc_first_visit_prediction(episode, V, returns, gamma=0.95):\n"
                "    return V\n"
            ),
        }
    )

    assert resolved["lesson_id"] == "mc_first_visit"
    assert resolved["requested_lesson_id"] == "dp_policy_eval"
    assert (
        resolved["lesson_contract_resolved_from_function"]
        == "mc_first_visit_prediction"
    )


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


def test_execution_response_prefers_terminated_episode_for_featured_trace(
    monkeypatch, tmp_path
):
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

    assert result["step_trace"] == result["trace_episodes"][1]["steps"]


def test_featured_episode_prefers_non_truncated_best_reward_when_none_terminate():
    log_data = [
        [
            {
                "state": 0,
                "reward": -10.0,
                "grid_metadata": {"terminated": False, "truncated": True},
            }
        ],
        [
            {
                "state": 1,
                "reward": -3.0,
                "grid_metadata": {"terminated": False, "truncated": False},
            }
        ],
        [
            {
                "state": 2,
                "reward": -5.0,
                "grid_metadata": {"terminated": False, "truncated": False},
            }
        ],
    ]
    rewards = [-10.0, -3.0, -5.0]

    featured_index, featured = execution_runtime._select_featured_episode(log_data, rewards)

    assert featured_index == 1
    assert featured == log_data[1]


def test_execution_response_moves_featured_episode_to_end_for_initial_replay(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "backend.execution_runtime.get_lesson_definition",
        lambda lesson_id: _Lesson(id=lesson_id),
    )
    monkeypatch.setattr("backend.execution_runtime.CodeValidator", lambda: _FakeValidator())
    monkeypatch.setattr("backend.execution_runtime.EnvironmentAdapter", _FakeAdapter)
    monkeypatch.setattr("backend.execution_runtime.RLEngine", _FakeThreeEpisodeEngine)
    monkeypatch.setattr(
        "backend.execution_runtime.VisualizationService",
        _FakeVisualizationService,
    )
    monkeypatch.setattr("backend.execution_runtime.load_user_context", lambda code: {})

    result = _run_execution_pipeline(
        {
            "lesson_id": "demo_lesson",
            "code": "def demo(): pass",
            "episode_count": 3,
        }
    )

    assert [episode["episode_index"] for episode in result["trace_episodes"]] == [0, 2, 1]
    assert result["trace_episodes"][-1]["episode_index"] == 1
    assert result["episode_summaries"][-1]["episode_index"] == 1
    assert result["step_trace"] == result["trace_episodes"][-1]["steps"]


def test_move_index_to_end_keeps_last_position_unchanged():
    items = [{"episode_index": 0}, {"episode_index": 1}]

    reordered = execution_runtime._move_index_to_end(items, 1)

    assert reordered == items


def test_build_success_response_exposes_normalized_replay_state():
    validation_result = ValidationResult(
        is_valid=True,
        errors=[],
        test_results=[],
        unresolved_blanks=[],
    )
    log_data = [[{"state": 0, "action": 1, "next_state": 1, "reward": 0.0}]]

    queued_response = execution_runtime._build_success_response(
        lesson=_Lesson(),
        log_data=log_data,
        validation_result=validation_result,
        replay_render={
            "replay_render_job_id": "job-1",
            "replay_render_status": "queued",
            "video_path": "",
        },
    )
    ready_response = execution_runtime._build_success_response(
        lesson=_Lesson(),
        log_data=log_data,
        validation_result=validation_result,
        replay_render={
            "replay_render_job_id": "job-1",
            "replay_render_status": "complete",
            "video_path": "/tmp/replay.mp4",
        },
    )

    assert queued_response["replay_state"] == "queued"
    assert ready_response["replay_state"] == "ready"


def test_build_success_response_curates_dynamic_programming_trace_family():
    validation_result = ValidationResult(
        is_valid=True,
        errors=[],
        test_results=[],
        unresolved_blanks=[],
    )
    log_data = [
        [
            {
                "state": 0,
                "action": 1,
                "next_state": 1,
                "reward": 0.0,
                "updated_values": {"V(0)": 0.2},
                "equation_update": {
                    "kind": "value_iteration",
                    "lhs": "V(0)",
                    "td_target": 0.2,
                    "new_value": 0.2,
                    "dp_details": {"delta": 0.2},
                },
            },
            {
                "state": 1,
                "action": 1,
                "next_state": 2,
                "reward": 0.0,
                "updated_values": {"V(1)": 0.3},
                "equation_update": {
                    "kind": "value_iteration",
                    "lhs": "V(1)",
                    "td_target": 0.3,
                    "new_value": 0.3,
                    "dp_details": {"delta": 0.3},
                },
            },
            {
                "state": 2,
                "action": 1,
                "next_state": 3,
                "reward": 0.0,
                "updated_values": {"V(2)": 1.6},
                "equation_update": {
                    "kind": "value_iteration",
                    "lhs": "V(2)",
                    "td_target": 1.6,
                    "new_value": 1.6,
                    "dp_details": {"delta": 1.6},
                },
            },
            {
                "state": 3,
                "action": 1,
                "next_state": 4,
                "reward": 1.0,
                "updated_values": {"V(3)": 2.0},
                "equation_update": {
                    "kind": "value_iteration",
                    "lhs": "V(3)",
                    "td_target": 2.0,
                    "new_value": 2.0,
                    "dp_details": {"delta": 0.0},
                },
                "grid_metadata": {"terminated": True, "truncated": False},
            },
        ]
    ]

    result = execution_runtime._build_success_response(
        lesson=_Lesson(id="dp_value_iteration", title="Value Iteration"),
        log_data=log_data,
        validation_result=validation_result,
    )

    assert result["trace_family"] == "DynamicProgramming"
    assert result["trace_mode"] == "curated backup trace"
    assert result["trace_summary"] == {
        "selection_strategy": "dp_curated_backup_trace",
        "visible_step_count": 4,
        "source_episode_indices": [0],
        "contains_terminal_goal": True,
    }
    assert len(result["step_trace"]) == 4
    assert [step["state"] for step in result["step_trace"]] == [0, 1, 2, 3]
    assert result["trace_episodes"][0]["steps"] == result["step_trace"]
    assert result["episode_summaries"] == [
        {
            "episode_index": 0,
            "step_count": 4,
            "total_reward": 1.0,
            "terminated": True,
            "truncated": False,
        }
    ]
    assert "evaluation_summary" not in result


def test_build_success_response_curates_monte_carlo_trace_family():
    validation_result = ValidationResult(
        is_valid=True,
        errors=[],
        test_results=[],
        unresolved_blanks=[],
    )
    log_data = [
        [
            {
                "state": "(15, 10, False)",
                "action": 1,
                "next_state": "(20, 10, False)",
                "reward": 0.0,
                "equation_update": {
                    "kind": "mc_sampling",
                    "mc_details": {
                        "phase": "sampling",
                        "episode_step": 0,
                        "terminated": False,
                        "truncated": False,
                    },
                },
            },
            {
                "state": "(20, 10, False)",
                "action": 0,
                "next_state": "(20, 10, False)",
                "reward": 1.0,
                "equation_update": {
                    "kind": "mc_sampling",
                    "mc_details": {
                        "phase": "sampling",
                        "episode_step": 1,
                        "terminated": True,
                        "truncated": False,
                    },
                },
            },
            {
                "state": "(15, 10, False)",
                "action": 1,
                "next_state": "(15, 10, False)",
                "reward": 0.0,
                "updated_values": {"V((15,10,False))": 0.9},
                "equation_update": {
                    "kind": "mc_first_visit",
                    "lhs": "V((15,10,False))",
                    "td_target": 0.9,
                    "new_value": 0.9,
                    "mc_details": {
                        "phase": "first_visit_update",
                        "episode_step": 0,
                        "return_value": 0.9,
                        "terminated": True,
                        "truncated": False,
                    },
                },
            },
        ]
    ]

    result = execution_runtime._build_success_response(
        lesson=_Lesson(id="mc_first_visit", title="First-Visit Monte Carlo"),
        log_data=log_data,
        validation_result=validation_result,
    )

    assert result["trace_family"] == "MonteCarlo"
    assert result["trace_mode"] == "curated episode return trace"
    assert result["trace_summary"] == {
        "selection_strategy": "mc_curated_episode_return_trace",
        "visible_step_count": 3,
        "source_episode_indices": [0],
        "contains_terminal_goal": True,
    }
    assert [step["equation_update"]["kind"] for step in result["step_trace"]] == [
        "mc_sampling",
        "mc_sampling",
        "mc_first_visit",
    ]
    assert result["trace_episodes"][0]["steps"] == result["step_trace"]
    assert "evaluation_summary" not in result


def test_mc_first_visit_runtime_handles_tuple_observation_states():
    logger = _FakeTraceLogger()
    engine = RLEngine(adapter=_FakeBlackjackAdapter(), logger=logger)

    def lesson_function(episode, values, returns, gamma):
        del gamma
        state = episode[0][0]
        returns.setdefault(state, []).append(1.0)
        values[state] = 1.0
        return values

    engine._run_mc_first_visit(
        lesson_function,
        num_episodes=1,
        hyperparameters={"gamma": 1.0},
    )

    steps = logger.episodes[0]
    assert len(steps) == 2
    assert steps[-1]["equation_update"]["kind"] == "mc_first_visit"
    assert steps[-1]["state"] == (16, 10, False)


class _FakeMcVisualizationService:
    """Records the enqueue_replay_render call and returns a fake job id."""

    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        self.last_lesson_id: str = ""
        self.last_log_data: list = []

    def enqueue_replay_render(self, log_data: list, lesson_id: str) -> dict:
        self.last_lesson_id = lesson_id
        self.last_log_data = log_data
        return {
            "replay_render_job_id": "mc-job-abc",
            "replay_render_status": "queued",
            "replay_episode_indices": [0],
        }


class _FakeMcEngine:
    """Simulates a one-episode MC run with tuple Blackjack states."""

    def __init__(self, adapter, logger) -> None:
        self.adapter = adapter
        self.logger = logger

    def run_episodes(self, lesson_id, code_module_str, num_episodes, hyperparameters):
        del lesson_id, code_module_str, num_episodes, hyperparameters
        self.logger.log_step(
            {
                "state": (16, 10, False),
                "action": 1,
                "reward": 0.0,
                "next_state": (18, 10, False),
                "equation_update": {
                    "kind": "mc_sampling",
                    "mc_details": {
                        "observation": {"player_sum": 16, "dealer_card": 10,
                                        "usable_ace": False},
                        "action_label": "Hit",
                        "reward": 0.0,
                        "terminated": False,
                    },
                },
            }
        )
        self.logger.log_step(
            {
                "state": (16, 10, False),
                "action": 1,
                "reward": -1.0,
                "next_state": (16, 10, False),
                "updated_values": {"V((16, 10, False))": 0.0},
                "equation_update": {
                    "kind": "mc_first_visit",
                    "mc_details": {
                        "observation": {"player_sum": 16, "dealer_card": 10,
                                        "usable_ace": False},
                        "action_label": "Hit",
                        "return_value": -1.0,
                        "returns_history": [-1.0],
                        "terminated": True,
                    },
                },
            }
        )
        self.logger.end_episode()


def test_mc_first_visit_enqueue_replay_render_returns_non_empty_job_id(
    monkeypatch, tmp_path
):
    """MC execution must produce a non-empty replay_render_job_id.

    This test caught the root cause bug: tuple Blackjack states cause a 422
    when POSTed to manim_service because TraceStep.state was typed as int.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "backend.execution_runtime.get_lesson_definition",
        lambda lesson_id: _Lesson(
            id=lesson_id,
            environment_name="Blackjack",
        ),
    )
    monkeypatch.setattr("backend.execution_runtime.CodeValidator", lambda: _FakeValidator())
    monkeypatch.setattr("backend.execution_runtime.EnvironmentAdapter", _FakeAdapter)
    monkeypatch.setattr("backend.execution_runtime.RLEngine", _FakeMcEngine)
    monkeypatch.setattr(
        "backend.execution_runtime.VisualizationService",
        _FakeMcVisualizationService,
    )
    monkeypatch.setattr("backend.execution_runtime.load_user_context", lambda code: {})

    result = _run_execution_pipeline(
        {
            "lesson_id": "mc_first_visit",
            "code": "def mc_first_visit_prediction(e, V, R, gamma): pass",
            "episode_count": 1,
        }
    )

    assert result["replay_render_job_id"] == "mc-job-abc", (
        "replay_render_job_id must not be empty for MC executions"
    )
    assert result["replay_render_status"] == "queued"


def test_td_execution_response_exposes_evaluation_summary(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "backend.execution_runtime.get_lesson_definition",
        lambda lesson_id: _Lesson(
            id=lesson_id,
            title="Taxi TD Control",
            environment_name="Taxi",
        ),
    )
    monkeypatch.setattr("backend.execution_runtime.CodeValidator", lambda: _FakeValidator())
    monkeypatch.setattr("backend.execution_runtime.EnvironmentAdapter", _FakeAdapter)
    monkeypatch.setattr("backend.execution_runtime.RLEngine", _FakeTdEvaluationEngine)
    monkeypatch.setattr(
        "backend.execution_runtime.VisualizationService",
        _FakeVisualizationService,
    )
    monkeypatch.setattr("backend.execution_runtime.load_user_context", lambda code: {})

    result = _run_execution_pipeline(
        {
            "lesson_id": "td_q_learning",
            "code": "def q_learning_update(Q, state, action, reward, next_state, alpha, gamma): pass",
            "episode_count": 1,
        }
    )

    assert result["trace_family"] == "TemporalDifferenceControl"
    assert result["trace_mode"] == "greedy evaluation replay from the policy learned by your code"
    assert result["trace_summary"] == {
        "selection_strategy": "td_greedy_evaluation_trace",
        "visible_step_count": 2,
        "source_episode_indices": [0],
        "contains_terminal_goal": True,
    }
    assert result["evaluation_summary"] == {
        "mode": "greedy_evaluation",
        "training_episodes_run": 500,
        "evaluation_attempts_run": 3,
        "selected_seed": 2,
        "selected_step_count": 2,
        "selected_total_reward": 19.0,
        "selected_terminated": True,
    }


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
