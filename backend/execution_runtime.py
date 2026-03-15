import multiprocessing
from typing import Any

from backend.lessons import get_lesson_definition
from backend.logger.event_logger import EventLogger
from backend.rl_engine.engine import EnvironmentAdapter, RLEngine
from backend.validation.validator import CodeValidator
from backend.visualization.controller import VisualizationController


class ExecutionPipelineError(Exception):
    def __init__(self, status_code: int, detail: Any):
        super().__init__(str(detail))
        self.status_code = status_code
        self.detail = detail


def run_submission_with_timeout(
    submission_payload: dict[str, Any],
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    ctx = multiprocessing.get_context("spawn")
    queue: multiprocessing.Queue = ctx.Queue()
    process = ctx.Process(
        target=_execution_worker,
        args=(submission_payload, queue),
        daemon=True,
    )
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()
        raise ExecutionPipelineError(
            status_code=408,
            detail={
                "message": "Execution timed out.",
                "issues": [
                    f"The lesson execution exceeded the {timeout_seconds}-second limit.",
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
    visualizer = VisualizationController(output_dir="backend/visualization/animations")

    try:
        adapter = EnvironmentAdapter(env_name=lesson.environment_name)
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

        engine = RLEngine(adapter=adapter, logger=logger)
        engine.run_episodes(
            submission_payload["lesson_id"],
            submission_payload["code"],
            num_episodes=submission_payload["episode_count"],
            hyperparameters={
                "alpha": submission_payload["learning_rate"],
                "gamma": submission_payload["discount_factor"],
                "epsilon": submission_payload["exploration_rate"],
            },
        )
    finally:
        if adapter is not None:
            adapter.close()

    log_data = logger.get_logs()
    episode_rewards = [
        sum(step.get("reward", 0) for step in episode)
        for episode in log_data
    ]
    video_path = visualizer.generate_animation(log_data, submission_payload["lesson_id"])

    return {
        "status": "success",
        "message": "Execution pipeline completed.",
        "lesson": {"id": lesson.id, "title": lesson.title},
        "video_path": video_path,
        "visualization_ready": bool(video_path),
        "test_results": validation_result.test_results,
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
