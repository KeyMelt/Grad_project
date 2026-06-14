"""Submission execution pipeline for guided RL lessons.

The gateway and task services call this module when a learner submits code.
The pipeline keeps learner code in a spawned subprocess, validates the lesson
contract first, then runs the RL engine and returns replay-ready trace data.
"""

import ast
import json
import multiprocessing
import os
import time
import uuid
from typing import Any

from backend.lesson_registry import get_lesson_definition, list_lesson_definitions
from backend.logger.event_logger import EventLogger, NpEncoder
from backend.replay_contract import normalize_replay_state
from backend.rl_engine.engine import EnvironmentAdapter, RLEngine
from backend.services.student_feedback_service import StudentFeedbackService
from backend.services.visualization_service import VisualizationService
from backend.settings import ExecutionSettings
from backend.user_code import defined_function_names, load_user_context
from backend.validation.validator import CodeValidator

_PROCESS_REGISTRY_DATABASE = None


class ExecutionPipelineError(Exception):
    def __init__(self, status_code: int, detail: Any):
        super().__init__(str(detail))
        self.status_code = status_code
        self.detail = detail


def run_submission_with_timeout(
    submission_payload: dict[str, Any],
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    """Run one lesson submission in a spawned process with a hard timeout."""
    _ensure_process_lesson_registry()
    submission_payload = _resolve_submission_lesson_contract(submission_payload)
    effective_timeout = timeout_seconds or _derive_timeout_seconds(submission_payload)
    lesson = get_lesson_definition(submission_payload["lesson_id"])
    feedback_service = StudentFeedbackService()
    ctx = multiprocessing.get_context("spawn")
    parent_conn, child_conn = ctx.Pipe(duplex=False)
    process = ctx.Process(
        target=_execution_worker,
        args=(submission_payload, child_conn),
        daemon=True,
    )
    process.start()
    child_conn.close()

    deadline = time.monotonic() + effective_timeout
    outcome: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        if parent_conn.poll(0.1):
            outcome = parent_conn.recv()
            break
        if not process.is_alive():
            break

    if outcome is None and parent_conn.poll():
        outcome = parent_conn.recv()

    if outcome is None and process.is_alive():
        process.terminate()
        process.join()
        parent_conn.close()
        issues = [
            f"The lesson execution exceeded the {effective_timeout}-second limit.",
        ]
        raise ExecutionPipelineError(
            status_code=408,
            detail=_failure_detail(
                lesson=lesson,
                submitted_code=submission_payload.get("code", ""),
                failure_kind="runtime_error",
                message="Execution timed out.",
                issues=issues,
                feedback_service=feedback_service,
            ),
        )

    process.join(timeout=1.0)
    if process.is_alive():
        process.terminate()
        process.join()
    parent_conn.close()

    if outcome is None:
        raise ExecutionPipelineError(
            status_code=500,
            detail=_failure_detail(
                lesson=lesson,
                submitted_code=submission_payload.get("code", ""),
                failure_kind="runtime_error",
                message="Execution process exited without returning a result.",
                issues=["The execution subprocess stopped before producing a result."],
                feedback_service=feedback_service,
            ),
        )

    if outcome["ok"]:
        return outcome["result"]
    raise ExecutionPipelineError(
        status_code=outcome["status_code"],
        detail=outcome["detail"],
    )


def _execution_worker(submission_payload: dict[str, Any], result_conn: Any) -> None:
    _ensure_process_lesson_registry()
    submission_payload = _resolve_submission_lesson_contract(submission_payload)
    lesson = get_lesson_definition(submission_payload["lesson_id"])
    feedback_service = StudentFeedbackService()
    try:
        result_conn.send(
            {
                "ok": True,
                "result": _run_execution_pipeline(submission_payload),
            },
        )
    except ExecutionPipelineError as error:
        result_conn.send(
            {
                "ok": False,
                "status_code": error.status_code,
                "detail": error.detail,
            },
        )
    except Exception as error:
        result_conn.send(
            {
                "ok": False,
                "status_code": 500,
                "detail": _failure_detail(
                    lesson=lesson,
                    submitted_code=submission_payload.get("code", ""),
                    failure_kind="runtime_error",
                    message="Unhandled execution failure.",
                    issues=[str(error)],
                    feedback_service=feedback_service,
                ),
            },
        )
    finally:
        result_conn.close()


def _ensure_process_lesson_registry() -> None:
    """Initialise the DB-backed lesson registry inside spawned processes."""
    global _PROCESS_REGISTRY_DATABASE

    import backend.lesson_registry as _lr

    try:
        _lr.list_lesson_definitions()
        return
    except RuntimeError:
        pass

    from backend.persistence import Database
    from backend.services.lesson_registry_service import LessonRegistryService

    database = Database()
    database.create_schema()
    registry = LessonRegistryService(database=database)
    _lr.set_registry(registry)
    _PROCESS_REGISTRY_DATABASE = database


def _run_execution_pipeline(submission_payload: dict[str, Any]) -> dict[str, Any]:
    """Validate code, execute the lesson environment, and package replay output."""
    validator, feedback_service, lesson, logger, visualizer, adapter = _validate_and_prepare(
        submission_payload
    )
    try:
        validation_result = _validate_submission_code(
            validator=validator,
            feedback_service=feedback_service,
            lesson=lesson,
            submission_payload=submission_payload,
        )
        _run_lesson_engine(
            adapter=adapter,
            logger=logger,
            feedback_service=feedback_service,
            lesson=lesson,
            submission_payload=submission_payload,
        )
    finally:
        adapter.close()
    return _package_results(
        lesson=lesson,
        logger=logger,
        visualizer=visualizer,
        validation_result=validation_result,
        submission_payload=submission_payload,
    )


def _resolve_submission_lesson_contract(
    submission_payload: dict[str, Any],
) -> dict[str, Any]:
    """Correct stale UI lesson ids when code clearly matches another lesson.

    The workspace editor can lag behind lesson selection. If the learner submits
    a program that defines exactly one known lesson function, use that function's
    lesson instead of grading the code against a stale selected lesson.
    """
    requested_lesson = get_lesson_definition(submission_payload["lesson_id"])
    submitted_code = str(submission_payload.get("code") or "")
    if requested_lesson is None or not submitted_code.strip():
        return submission_payload

    try:
        function_names = defined_function_names(submitted_code)
    except Exception:
        return submission_payload

    if requested_lesson.required_function in function_names:
        return submission_payload

    lessons_by_required_function = {
        lesson.required_function: lesson
        for lesson in list_lesson_definitions()
        if lesson.required_function
    }
    matching_lessons = [
        lessons_by_required_function[name]
        for name in function_names
        if name in lessons_by_required_function
    ]
    if len(matching_lessons) != 1:
        return submission_payload

    inferred_lesson = matching_lessons[0]
    resolved = dict(submission_payload)
    resolved["lesson_id"] = inferred_lesson.id
    resolved["requested_lesson_id"] = submission_payload["lesson_id"]
    resolved["lesson_contract_resolved_from_function"] = inferred_lesson.required_function
    return resolved


def _validate_and_prepare(
    submission_payload: dict[str, Any],
) -> tuple[
    CodeValidator,
    StudentFeedbackService,
    Any,
    EventLogger,
    VisualizationService,
    EnvironmentAdapter,
]:
    validator = CodeValidator()
    feedback_service = StudentFeedbackService()
    settings = ExecutionSettings.from_env()
    lesson = get_lesson_definition(submission_payload["lesson_id"])
    if lesson is None:
        raise ExecutionPipelineError(
            status_code=404,
            detail=f"Unknown lesson '{submission_payload['lesson_id']}'.",
        )
    logger = EventLogger(log_dir=settings.logger_dir)
    visualization_output_dir = os.path.abspath(settings.visualization_output_dir)
    visualizer = VisualizationService(output_dir=visualization_output_dir)
    adapter = _create_environment_adapter(
        lesson=lesson,
        lesson_id=submission_payload["lesson_id"],
        visualization_output_dir=visualization_output_dir,
    )
    return validator, feedback_service, lesson, logger, visualizer, adapter


def _package_results(
    *,
    lesson: Any,
    logger: EventLogger,
    visualizer: VisualizationService,
    validation_result: Any,
    submission_payload: dict[str, Any],
) -> dict[str, Any]:
    log_data = logger.get_logs()
    replay_render = _enqueue_replay_render(
        visualizer,
        log_data,
        submission_payload["lesson_id"],
    )
    return _build_success_response(
        lesson=lesson,
        log_data=log_data,
        validation_result=validation_result,
        replay_render=replay_render,
    )


def _enqueue_replay_render(
    visualizer: VisualizationService,
    log_data: list[list[dict[str, Any]]],
    lesson_id: str,
) -> dict[str, Any]:
    enqueue = getattr(visualizer, "enqueue_replay_render", None)
    if callable(enqueue):
        return enqueue(log_data, lesson_id)

    video_path = visualizer.generate_animation(log_data, lesson_id)
    return {
        "video_path": video_path,
        "replay_render_job_id": "",
        "replay_render_status": "complete" if video_path else "unavailable",
        "replay_episode_indices": [],
    }


def _create_environment_adapter(
    *,
    lesson: Any,
    lesson_id: str,
    visualization_output_dir: str,
) -> EnvironmentAdapter:
    capture_dir = os.path.join(
        visualization_output_dir,
        "captures",
        lesson_id,
        uuid.uuid4().hex,
    )

    try:
        return EnvironmentAdapter(
            env_name=lesson.environment_name,
            frame_dir=capture_dir,
            env_params=getattr(lesson, "env_params", {}),
        )
    except Exception as error:
        raise ExecutionPipelineError(status_code=400, detail=str(error)) from error


def _validate_submission_code(
    *,
    validator: CodeValidator,
    feedback_service: StudentFeedbackService,
    lesson: Any,
    submission_payload: dict[str, Any],
):
    validation_result = validator.validate_code(
        submission_payload["code"],
        submission_payload["lesson_id"],
    )
    if validation_result.is_valid:
        return validation_result

    raise ExecutionPipelineError(
        status_code=400,
        detail=_failure_detail(
            lesson=lesson,
            submitted_code=submission_payload["code"],
            failure_kind=validation_result.failure_kind or "validation_error",
            message="Code validation failed.",
            issues=validation_result.errors,
            test_results=validation_result.test_results,
            unresolved_blanks=validation_result.unresolved_blanks or [],
            feedback_service=feedback_service,
        ),
    )


def _run_lesson_engine(
    *,
    adapter: EnvironmentAdapter,
    logger: EventLogger,
    feedback_service: StudentFeedbackService,
    lesson: Any,
    submission_payload: dict[str, Any],
) -> None:
    try:
        user_context = load_user_context(submission_payload["code"])
        hyperparameters = _extract_hyperparameters(submission_payload, user_context)
        engine = RLEngine(adapter=adapter, logger=logger)
        engine.run_episodes(
            submission_payload["lesson_id"],
            submission_payload["code"],
            num_episodes=hyperparameters["episodes"],
            hyperparameters=hyperparameters,
        )
    except ExecutionPipelineError:
        raise
    except Exception as error:
        raise ExecutionPipelineError(
            status_code=500,
            detail=_failure_detail(
                lesson=lesson,
                submitted_code=submission_payload["code"],
                failure_kind="runtime_error",
                message="Execution failed while running your lesson code.",
                issues=[f"{type(error).__name__}: {error}"],
                feedback_service=feedback_service,
            ),
        ) from error


def _build_success_response(
    *,
    lesson: Any,
    log_data: list[list[dict[str, Any]]],
    validation_result: Any,
    replay_render: dict[str, Any] | None = None,
) -> dict[str, Any]:
    episode_rewards = [sum(step.get("reward", 0) for step in episode) for episode in log_data]
    latest_episode = json.loads(json.dumps(log_data[-1], cls=NpEncoder)) if log_data else []
    trace_episodes = json.loads(
        json.dumps(
            [
                {
                    "episode_index": index,
                    "steps": episode,
                }
                for index, episode in enumerate(log_data)
            ],
            cls=NpEncoder,
        )
    )
    episode_summaries = [
        _episode_summary(index, episode, episode_rewards[index])
        for index, episode in enumerate(log_data)
    ]
    replay_render = replay_render or {}
    video_path = str(replay_render.get("video_path") or "")
    render_status = str(replay_render.get("replay_render_status") or "unavailable")
    replay_state = normalize_replay_state(
        render_status,
        video_path=video_path,
        error=replay_render.get("error"),
    )
    return {
        "status": "success",
        "message": "Execution pipeline completed.",
        "lesson": {"id": lesson.id, "title": lesson.title},
        "video_path": video_path,
        "visualization_ready": bool(video_path),
        "replay_render_job_id": str(replay_render.get("replay_render_job_id") or ""),
        "replay_render_status": render_status,
        "replay_state": replay_state,
        "replay_episode_indices": replay_render.get("replay_episode_indices") or [],
        "test_results": validation_result.test_results,
        "step_trace": latest_episode,
        "trace_episodes": trace_episodes,
        "episode_summaries": episode_summaries,
        "metrics": {
            "episodes_completed": len(log_data),
            "steps_recorded": sum(len(episode) for episode in log_data),
            "total_reward": sum(episode_rewards),
            "average_reward": (
                round(sum(episode_rewards) / len(episode_rewards), 4) if episode_rewards else 0.0
            ),
            "best_episode_reward": max(episode_rewards, default=0),
        },
    }


def _episode_summary(
    episode_index: int,
    episode: list[dict[str, Any]],
    total_reward: float,
) -> dict[str, Any]:
    last_step = episode[-1] if episode else {}
    grid_metadata = last_step.get("grid_metadata") or {}
    mc_details = (last_step.get("equation_update") or {}).get("mc_details") or {}
    terminated = bool(grid_metadata.get("terminated") or mc_details.get("terminated"))
    truncated = bool(grid_metadata.get("truncated") or mc_details.get("truncated"))
    return {
        "episode_index": episode_index,
        "step_count": len(episode),
        "total_reward": round(float(total_reward), 4),
        "terminated": terminated,
        "truncated": truncated,
    }


def _failure_detail(
    *,
    lesson: Any,
    submitted_code: str,
    failure_kind: str,
    message: str,
    issues: list[str],
    feedback_service: StudentFeedbackService,
    test_results: list[dict[str, Any]] | None = None,
    unresolved_blanks: list[str] | None = None,
) -> dict[str, Any]:
    unresolved = unresolved_blanks or []
    detail = {
        "message": message,
        "issues": issues,
        "failure_kind": failure_kind,
        "test_results": test_results or [],
    }
    if unresolved:
        detail["unresolved_blanks"] = unresolved
    if lesson is not None:
        detail["student_feedback"] = feedback_service.build_feedback(
            lesson=lesson,
            submitted_code=submitted_code,
            failure_kind=failure_kind,
            issues=issues,
            unresolved_blanks=unresolved,
            test_results=test_results or [],
        )
    return detail


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
        "max_steps_per_episode": _coerce_int(
            user_context.get(
                "MAX_STEPS_PER_EPISODE", submission_payload.get("max_steps_per_episode")
            ),
            default=80,
            min_value=1,
            max_value=500,
            label="MAX_STEPS_PER_EPISODE",
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
    settings = ExecutionSettings.from_env()

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
    return min(
        settings.timeout_max_seconds,
        settings.timeout_base_seconds + bounded_episodes * settings.timeout_per_episode_seconds,
    )


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
                        if isinstance(value.operand, ast.Constant) and isinstance(
                            value.operand.value, (int, float)
                        ):
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
