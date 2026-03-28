import json
import os
import uuid
import multiprocessing
import ast
from typing import Any

from backend.lessons import get_lesson_definition
from backend.logger.event_logger import EventLogger, NpEncoder
from backend.rl_engine.engine import EnvironmentAdapter, RLEngine
from backend.services.visualization_service import VisualizationService
from backend.user_code import load_user_context
from backend.validation.validator import CodeValidator


class ExecutionPipelineError(Exception):
    def __init__(self, status_code: int, detail: Any):
        super().__init__(str(detail))
        self.status_code = status_code
        self.detail = detail


def run_submission_with_timeout(
    submission_payload: dict[str, Any],
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    effective_timeout = timeout_seconds or _derive_timeout_seconds(submission_payload)
    ctx = multiprocessing.get_context("spawn")
    queue: multiprocessing.Queue = ctx.Queue()
    process = ctx.Process(
        target=_execution_worker,
        args=(submission_payload, queue),
        daemon=True,
    )
    process.start()
    process.join(effective_timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        raise ExecutionPipelineError(
            status_code=408,
            detail={
                "message": "Execution timed out.",
                "issues": [
                    f"The lesson execution exceeded the {effective_timeout}-second limit.",
                ],
            },
        )

    if queue.empty():
        raise ExecutionPipelineError(
            status_code=500,
            detail="Execution process exited without returning a result.",
        )

    outcome = queue.get()
    if outcome["ok"]:
        return outcome["result"]
    raise ExecutionPipelineError(
        status_code=outcome["status_code"],
        detail=outcome["detail"],
    )


def _execution_worker(submission_payload: dict[str, Any], queue: multiprocessing.Queue) -> None:
    try:
        queue.put(
            {
                "ok": True,
                "result": _run_execution_pipeline(submission_payload),
            },
        )
    except ExecutionPipelineError as error:
        queue.put(
            {
                "ok": False,
                "status_code": error.status_code,
                "detail": error.detail,
            },
        )
    except Exception as error:
        queue.put(
            {
                "ok": False,
                "status_code": 500,
                "detail": {
                    "message": "Unhandled execution failure.",
                    "issues": [str(error)],
                },
            },
        )


def _run_execution_pipeline(submission_payload: dict[str, Any]) -> dict[str, Any]:
    validator = CodeValidator()
    lesson = get_lesson_definition(submission_payload["lesson_id"])
    if lesson is None:
        raise ExecutionPipelineError(
            status_code=404,
            detail=f"Unknown lesson '{submission_payload['lesson_id']}'.",
        )

    adapter = None
    logger = EventLogger(log_dir="backend/logger/logs")
    visualizer = VisualizationService(output_dir="backend/visualization/animations")
    capture_dir = os.path.join(
        "backend/visualization/animations",
        "captures",
        submission_payload["lesson_id"],
        uuid.uuid4().hex,
    )

    try:
        adapter = EnvironmentAdapter(
            env_name=lesson.environment_name,
            frame_dir=capture_dir,
        )
    except Exception as error:
        raise ExecutionPipelineError(status_code=400, detail=str(error)) from error

    try:
        validation_result = validator.validate_code(
            submission_payload["code"],
            submission_payload["lesson_id"],
        )
        if not validation_result.is_valid:
            raise ExecutionPipelineError(
                status_code=400,
                detail={
                    "message": "Code validation failed.",
                    "issues": validation_result.errors,
                    "test_results": validation_result.test_results,
                },
            )

        user_context = load_user_context(submission_payload["code"])
        hyperparameters = _extract_hyperparameters(submission_payload, user_context)
        engine = RLEngine(adapter=adapter, logger=logger)
        engine.run_episodes(
            submission_payload["lesson_id"],
            submission_payload["code"],
            num_episodes=hyperparameters["episodes"],
            hyperparameters=hyperparameters,
        )
    finally:
        if adapter is not None:
            adapter.close()

    log_data = logger.get_logs()
    episode_rewards = [
        sum(step.get("reward", 0) for step in episode)
        for episode in log_data
    ]
    latest_episode = (
        json.loads(json.dumps(log_data[-1], cls=NpEncoder)) if log_data else []
    )
    video_path = visualizer.generate_animation(log_data, submission_payload["lesson_id"])

    return {
        "status": "success",
        "message": "Execution pipeline completed.",
        "lesson": {"id": lesson.id, "title": lesson.title},
        "video_path": video_path,
        "visualization_ready": bool(video_path),
        "test_results": validation_result.test_results,
        "step_trace": latest_episode,
        "metrics": {
            "episodes_completed": len(log_data),
            "steps_recorded": sum(len(episode) for episode in log_data),
            "total_reward": sum(episode_rewards),
            "average_reward": round(sum(episode_rewards) / len(episode_rewards), 4)
            if episode_rewards
            else 0.0,
            "best_episode_reward": max(episode_rewards, default=0),
        },
    }


def _extract_hyperparameters(
    submission_payload: dict[str, Any],
    user_context: dict[str, Any],
) -> dict[str, float | int]:
    return {
        "alpha": _coerce_float(
            user_context.get("LEARNING_RATE", submission_payload.get("learning_rate")),
            default=0.1,
            min_value=0.0001,
            max_value=1.0,
            label="LEARNING_RATE",
        ),
        "gamma": _coerce_float(
            user_context.get("DISCOUNT_FACTOR", submission_payload.get("discount_factor")),
            default=0.95,
            min_value=0.0001,
            max_value=1.0,
            label="DISCOUNT_FACTOR",
        ),
        "epsilon": _coerce_float(
            user_context.get("EXPLORATION_RATE", submission_payload.get("exploration_rate")),
            default=0.2,
            min_value=0.0,
            max_value=1.0,
            label="EXPLORATION_RATE",
        ),
        "episodes": _coerce_int(
            user_context.get("EPISODE_COUNT", submission_payload.get("episode_count")),
            default=5,
            min_value=1,
            max_value=500,
            label="EPISODE_COUNT",
        ),
    }


def _coerce_float(
    value: Any,
    *,
    default: float,
    min_value: float,
    max_value: float,
    label: str,
) -> float:
    if value is None:
        return default
    try:
        numeric = float(value)
    except (TypeError, ValueError) as error:
        raise ExecutionPipelineError(
            status_code=400,
            detail={
                "message": "Code configuration is invalid.",
                "issues": [f"{label} must be numeric."],
            },
        ) from error

    if numeric < min_value or numeric > max_value:
        raise ExecutionPipelineError(
            status_code=400,
            detail={
                "message": "Code configuration is invalid.",
                "issues": [f"{label} must be between {min_value} and {max_value}."],
            },
        )
    return numeric


def _derive_timeout_seconds(submission_payload: dict[str, Any]) -> int:
    """Choose a practical timeout window based on lesson workload hints."""
    base_seconds = 90
    per_episode_seconds = 2
    max_seconds = 600

    episodes = _extract_episode_count_from_source(submission_payload.get("code", ""))
    if episodes is None:
        payload_episodes = submission_payload.get("episode_count")
        if isinstance(payload_episodes, int):
            episodes = payload_episodes
        elif isinstance(payload_episodes, str) and payload_episodes.isdigit():
            episodes = int(payload_episodes)
        else:
            episodes = 5

    bounded_episodes = max(1, min(episodes, 500))
    return min(max_seconds, base_seconds + bounded_episodes * per_episode_seconds)


def _extract_episode_count_from_source(source: str) -> int | None:
    if not source.strip():
        return None

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "EPISODE_COUNT":
                    value = node.value
                    if isinstance(value, ast.Constant) and isinstance(value.value, (int, float)):
                        return int(value.value)
                    if isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub):
                        if isinstance(value.operand, ast.Constant) and isinstance(value.operand.value, (int, float)):
                            return int(-value.operand.value)
    return None


def _coerce_int(
    value: Any,
    *,
    default: int,
    min_value: int,
    max_value: int,
    label: str,
) -> int:
    if value is None:
        return default
    try:
        numeric = int(value)
    except (TypeError, ValueError) as error:
        raise ExecutionPipelineError(
            status_code=400,
            detail={
                "message": "Code configuration is invalid.",
                "issues": [f"{label} must be an integer."],
            },
        ) from error

    if numeric < min_value or numeric > max_value:
        raise ExecutionPipelineError(
            status_code=400,
            detail={
                "message": "Code configuration is invalid.",
                "issues": [f"{label} must be between {min_value} and {max_value}."],
            },
        )
    return numeric
