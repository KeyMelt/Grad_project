import math
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List


@dataclass(frozen=True)
class LessonTestCaseResult:
    name: str
    passed: bool
    message: str
    expected: str = ""
    actual: str = ""


def run_lesson_tests(
    lesson_id: str,
    lesson_function: Callable[..., Any],
) -> List[Dict[str, Any]]:
    if lesson_id == "dp_policy_eval":
        results = _test_policy_evaluation(lesson_function)
    elif lesson_id == "mc_first_visit":
        results = _test_mc_first_visit(lesson_function)
    elif lesson_id == "td_q_learning":
        results = _test_q_learning(lesson_function)
    else:
        results = [
            LessonTestCaseResult(
                name="unsupported_lesson",
                passed=False,
                message=f"No lesson tests are configured for '{lesson_id}'.",
            ),
        ]

    return [asdict(result) for result in results]


def _test_q_learning(lesson_function: Callable[..., Any]) -> list[LessonTestCaseResult]:
    q_table = [
        [0.0, 0.0],
        [1.0, 3.0],
    ]
    lesson_function(
        q_table,
        0,
        1,
        2.0,
        1,
        0.5,
        0.5,
    )
    updated_value = q_table[0][1]
    expected = 1.75
    passed = math.isclose(updated_value, expected, rel_tol=1e-6, abs_tol=1e-6)
    return [
        LessonTestCaseResult(
            name="q_learning_update_rule",
            passed=passed,
            message="Updates the selected Q-value using the one-step TD target.",
            expected=f"Q[0][1] = {expected}",
            actual=f"Q[0][1] = {round(updated_value, 6)}",
        ),
    ]


def _test_mc_first_visit(lesson_function: Callable[..., Any]) -> list[LessonTestCaseResult]:
    episode = [
        (0, 0, 1.0),
        (1, 0, 2.0),
    ]
    values = [0.0, 0.0]
    returns = {0: [], 1: []}
    lesson_function(episode, values, returns, 1.0)

    first_state_ok = math.isclose(values[0], 3.0, rel_tol=1e-6, abs_tol=1e-6)
    second_state_ok = math.isclose(values[1], 2.0, rel_tol=1e-6, abs_tol=1e-6)
    return [
        LessonTestCaseResult(
            name="mc_first_visit_returns",
            passed=first_state_ok and second_state_ok,
            message="Computes first-visit returns over a short episode.",
            expected="V[0] = 3.0 and V[1] = 2.0",
            actual=f"V[0] = {round(values[0], 6)} and V[1] = {round(values[1], 6)}",
        ),
    ]


def _test_policy_evaluation(lesson_function: Callable[..., Any]) -> list[LessonTestCaseResult]:
    class _ToyEnv:
        P = {
            0: {0: [(1.0, 0, 1.0, False)]},
            1: {0: [(1.0, 1, 0.0, True)]},
        }

    values = [0.0, 0.0]
    policy = [[1.0], [1.0]]
    lesson_function(values, policy, _ToyEnv(), 0.5)

    passed = math.isclose(values[0], 2.0, rel_tol=1e-4, abs_tol=1e-4) and math.isclose(
        values[1],
        0.0,
        rel_tol=1e-4,
        abs_tol=1e-4,
    )
    return [
        LessonTestCaseResult(
            name="policy_evaluation_toy_env",
            passed=passed,
            message="Evaluates a deterministic one-action toy environment.",
            expected="V[0] ~= 2.0 and V[1] = 0.0",
            actual=f"V[0] = {round(values[0], 6)} and V[1] = {round(values[1], 6)}",
        ),
    ]
