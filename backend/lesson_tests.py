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


class ActionValueRow(list):
    """List row that also supports dict-style values() from common Q-table examples."""

    def values(self) -> list[float]:
        return list(self)


def _q_table(rows: list[list[float]]) -> list[ActionValueRow]:
    return [ActionValueRow(row) for row in rows]


def run_lesson_tests(
    lesson_id: str,
    lesson_function: Callable[..., Any],
) -> List[Dict[str, Any]]:
    if lesson_id == "dp_policy_eval":
        results = _test_policy_evaluation(lesson_function)
    elif lesson_id == "dp_value_iteration":
        results = _test_value_iteration(lesson_function)
    elif lesson_id == "dp_policy_improvement":
        results = _test_policy_improvement(lesson_function)
    elif lesson_id == "mc_first_visit":
        results = _test_mc_first_visit(lesson_function)
    elif lesson_id == "td_sarsa":
        results = _test_sarsa(lesson_function)
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
    q_table = _q_table([
        [0.0, 0.0],
        [1.0, 3.0],
    ])
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


def _test_sarsa(lesson_function: Callable[..., Any]) -> list[LessonTestCaseResult]:
    q_table = _q_table([
        [0.0, 0.0],
        [4.0, 1.0],
    ])
    lesson_function(
        q_table,
        0,
        1,
        2.0,
        1,
        0,
        0.5,
        0.5,
    )
    updated_value = q_table[0][1]
    expected = 2.0
    terminal_q_table = _q_table([
        [0.0, 0.0],
        [4.0, 1.0],
    ])
    terminal_error = ""
    try:
        lesson_function(
            terminal_q_table,
            0,
            1,
            2.0,
            1,
            None,
            0.5,
            0.5,
        )
    except Exception as error:  # pragma: no cover - message is reported in result
        terminal_error = f"{type(error).__name__}: {error}"

    terminal_expected = 1.0
    terminal_updated_value = terminal_q_table[0][1]
    passed = (
        math.isclose(updated_value, expected, rel_tol=1e-6, abs_tol=1e-6)
        and not terminal_error
        and math.isclose(
            terminal_updated_value,
            terminal_expected,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
    )
    actual = f"Q[0][1] = {round(updated_value, 6)}"
    if terminal_error:
        actual = f"{actual}; terminal transition raised {terminal_error}"
    else:
        actual = (
            f"{actual}; terminal Q[0][1] = {round(terminal_updated_value, 6)}"
        )
    return [
        LessonTestCaseResult(
            name="sarsa_update_rule",
            passed=passed,
            message=(
                "Updates the selected Q-value using the sampled next action and "
                "uses zero bootstrap on terminal transitions."
            ),
            expected=f"Q[0][1] = {expected}; terminal Q[0][1] = {terminal_expected}",
            actual=actual,
        ),
    ]


def _test_mc_first_visit(lesson_function: Callable[..., Any]) -> list[LessonTestCaseResult]:
    episode = [
        ((16, 10, False), 1, 1.0),
        ((18, 10, False), 0, 2.0),
    ]
    values: dict[tuple[int, int, bool], float] = {}
    returns: dict[tuple[int, int, bool], list[float]] = {}
    lesson_function(episode, values, returns, 1.0)

    first_state = (16, 10, False)
    second_state = (18, 10, False)
    first_state_ok = math.isclose(values[first_state], 3.0, rel_tol=1e-6, abs_tol=1e-6)
    second_state_ok = math.isclose(values[second_state], 2.0, rel_tol=1e-6, abs_tol=1e-6)
    return [
        LessonTestCaseResult(
            name="mc_first_visit_returns",
            passed=first_state_ok and second_state_ok,
            message="Computes first-visit returns over a short episode.",
            expected="V[(16, 10, False)] = 3.0 and V[(18, 10, False)] = 2.0",
            actual=(
                f"V[(16, 10, False)] = {round(values[first_state], 6)} and "
                f"V[(18, 10, False)] = {round(values[second_state], 6)}"
            ),
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


def _test_value_iteration(lesson_function: Callable[..., Any]) -> list[LessonTestCaseResult]:
    class _ActionSpace:
        n = 2

    class _ToyEnv:
        action_space = _ActionSpace()
        P = {
            0: {
                0: [(1.0, 0, 0.0, False)],
                1: [(1.0, 1, 1.0, True)],
            },
            1: {
                0: [(1.0, 1, 0.0, True)],
                1: [(1.0, 1, 0.0, True)],
            },
        }

    values = [0.0, 0.0]
    lesson_function(values, _ToyEnv(), 0.9)

    passed = math.isclose(values[0], 1.0, rel_tol=1e-4, abs_tol=1e-4) and math.isclose(
        values[1],
        0.0,
        rel_tol=1e-4,
        abs_tol=1e-4,
    )
    return [
        LessonTestCaseResult(
            name="value_iteration_toy_env",
            passed=passed,
            message="Computes the optimal Bellman backup for a two-action toy environment.",
            expected="V[0] ~= 1.0 and V[1] = 0.0",
            actual=f"V[0] = {round(values[0], 6)} and V[1] = {round(values[1], 6)}",
        ),
    ]


def _test_policy_improvement(lesson_function: Callable[..., Any]) -> list[LessonTestCaseResult]:
    class _ActionSpace:
        n = 2

    class _ToyEnv:
        action_space = _ActionSpace()
        P = {
            0: {
                0: [(1.0, 0, 1.0, False)],
                1: [(1.0, 1, 0.0, False)],
            },
            1: {
                0: [(1.0, 1, 0.0, True)],
                1: [(1.0, 1, 0.0, True)],
            },
        }

    values = [0.0, 4.0]
    policy = lesson_function(values, _ToyEnv(), 0.9)
    state_zero_row = policy[0]
    row_sum = sum(state_zero_row)
    passed = (
        len(state_zero_row) == 2
        and math.isclose(state_zero_row[0], 0.0, rel_tol=1e-6, abs_tol=1e-6)
        and math.isclose(state_zero_row[1], 1.0, rel_tol=1e-6, abs_tol=1e-6)
        and math.isclose(row_sum, 1.0, rel_tol=1e-6, abs_tol=1e-6)
    )
    return [
        LessonTestCaseResult(
            name="policy_improvement_greedy_action",
            passed=passed,
            message="Builds a greedy one-hot policy from action-value backups.",
            expected="policy[0] = [0.0, 1.0]",
            actual=f"policy[0] = {[round(value, 6) for value in state_zero_row]}",
        ),
    ]
