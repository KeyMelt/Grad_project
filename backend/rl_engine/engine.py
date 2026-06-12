import os
from typing import Any, Dict

import gymnasium as gym
from PIL import Image

from backend.lesson_registry import get_lesson_definition
from backend.user_code import load_user_function


class ActionValueRow(list):
    """List-backed action values with dict-style values() compatibility."""

    def values(self) -> list[float]:
        return list(self)


class EnvironmentAdapter:
    """Manages Gymnasium environments and exports render frames for visualization."""

    def __init__(
        self,
        env_name: str,
        frame_dir: str | None = None,
        render_mode: str = "rgb_array",
        env_params: dict | None = None,
    ):
        self.env_name = env_name
        self.render_mode = render_mode
        self.frame_dir = frame_dir
        self.env_params: dict = env_params or {}
        self._frame_index = 0
        if self.frame_dir is not None:
            os.makedirs(self.frame_dir, exist_ok=True)
        # Shared library for static state renders
        self.library_dir = (
            os.path.join(os.path.dirname(self.frame_dir), "library", self.env_name)
            if self.frame_dir
            else None
        )
        if self.library_dir:
            os.makedirs(self.library_dir, exist_ok=True)
        self.env = self._create_env()

    def _create_env(self):
        if self.env_name == "FrozenLake":
            return gym.make(
                "FrozenLake-v1",
                desc=None,
                map_name=self.env_params.get("map_name", "4x4"),
                is_slippery=self.env_params.get("is_slippery", True),
                render_mode=self.render_mode,
            )
        if self.env_name == "Blackjack":
            return gym.make(
                "Blackjack-v1",
                sab=self.env_params.get("sab", True),
                render_mode=self.render_mode,
            )
        if self.env_name == "CliffWalking":
            return gym.make(
                "CliffWalking-v1",
                render_mode=self.render_mode,
            )
        raise ValueError(f"Environment {self.env_name} is not currently supported.")

    def reset(self, seed: int | None = None):
        return self.env.reset(seed=seed)

    def step(self, action):
        return self.env.step(action)

    def close(self):
        self.env.close()

    def transition_details(self, state: int, action: int) -> list[dict[str, Any]]:
        if not hasattr(self.env.unwrapped, "P"):
            return []
        return [
            {
                "probability": float(probability),
                "next_state": int(next_state),
                "reward": float(reward),
                "done": bool(done),
            }
            for probability, next_state, reward, done in self.env.unwrapped.P[state][action]
        ]

    def action_label(self, action: int) -> str:
        mappings = {
            "FrozenLake": {
                0: "Left",
                1: "Down",
                2: "Right",
                3: "Up",
            },
            "CliffWalking": {
                0: "Up",
                1: "Right",
                2: "Down",
                3: "Left",
            },
            "Blackjack": {
                0: "Stand",
                1: "Hit",
            },
        }
        return mappings.get(self.env_name, {}).get(action, f"Action {action}")

    def grid_metadata(
        self,
        state: int,
        next_state: int | None = None,
        action: int | None = None,
        reward: float | None = None,
        terminated: bool = False,
        truncated: bool = False,
    ) -> dict[str, Any] | None:
        if self.env_name == "FrozenLake":
            desc = getattr(self.env.unwrapped, "desc", None)
            if desc is None:
                return None
            rows = len(desc)
            columns = len(desc[0])
            cells = []
            for row in range(rows):
                for column in range(columns):
                    tile = desc[row][column].decode("utf-8")
                    cells.append(
                        {
                            "state": row * columns + column,
                            "row": row,
                            "column": column,
                            "tile_type": tile,
                            "terminal": tile in {"H", "G"},
                        }
                    )
            return {
                "environment": self.env_name,
                "rows": rows,
                "columns": columns,
                "cells": cells,
                "state": int(state),
                "next_state": None if next_state is None else int(next_state),
                "state_coordinates": self._grid_coordinates(state, columns),
                "next_state_coordinates": (
                    None if next_state is None else self._grid_coordinates(next_state, columns)
                ),
                "action": action,
                "action_label": None if action is None or action < 0 else self.action_label(action),
                "reward": None if reward is None else round(float(reward), 4),
                "terminated": bool(terminated),
                "truncated": bool(truncated),
            }

        if self.env_name == "CliffWalking":
            rows = 4
            columns = 12
            cells = []
            start_state = (rows - 1) * columns
            goal_state = rows * columns - 1
            cliff_states = set(range(start_state + 1, goal_state))
            for row in range(rows):
                for column in range(columns):
                    cell_state = row * columns + column
                    tile = "C" if cell_state in cliff_states else "F"
                    if cell_state == start_state:
                        tile = "S"
                    elif cell_state == goal_state:
                        tile = "G"
                    cells.append(
                        {
                            "state": cell_state,
                            "row": row,
                            "column": column,
                            "tile_type": tile,
                            "terminal": cell_state == goal_state,
                        }
                    )
            return {
                "environment": self.env_name,
                "rows": rows,
                "columns": columns,
                "cells": cells,
                "state": int(state),
                "next_state": None if next_state is None else int(next_state),
                "state_coordinates": self._grid_coordinates(state, columns),
                "next_state_coordinates": (
                    None if next_state is None else self._grid_coordinates(next_state, columns)
                ),
                "action": action,
                "action_label": None if action is None or action < 0 else self.action_label(action),
                "reward": None if reward is None else round(float(reward), 4),
                "terminated": bool(terminated),
                "truncated": bool(truncated),
            }
        return None

    def _grid_coordinates(self, state: int, columns: int) -> dict[str, int]:
        row, column = divmod(int(state), columns)
        return {"row": row, "column": column}

    def set_render_state(self, state: int) -> None:
        if hasattr(self.env.unwrapped, "s"):
            self.env.unwrapped.s = state

    def capture_frame_png(self, state: int | None = None, prefix: str = "step") -> str:
        if self.frame_dir is None:
            return ""

        # Check library for static state render first (if state is provided)
        if state is not None and self.library_dir:
            cache_path = os.path.join(self.library_dir, f"state_{state:03d}.png")
            if os.path.exists(cache_path):
                return cache_path

        if state is not None:
            self.set_render_state(state)

        frame = self.env.render()
        if frame is None:
            return ""
        if not hasattr(frame, "__array_interface__"):
            return ""

        self._frame_index += 1

        # Determine where to save: library (if state-based) or specific run dir
        if state is not None and self.library_dir:
            save_path = os.path.join(self.library_dir, f"state_{state:03d}.png")
        else:
            save_path = os.path.join(self.frame_dir, f"{prefix}_{self._frame_index:03d}.png")

        Image.fromarray(frame).save(save_path)
        return save_path


class RLEngine:
    """Core engine to run RL simulations and record reasoning traces."""

    DEFAULT_MAX_STEPS_PER_EPISODE = 50

    def __init__(self, adapter: EnvironmentAdapter, logger):
        self.adapter = adapter
        self.logger = logger

    def run_episodes(
        self,
        lesson_id: str,
        code_module_str: str,
        num_episodes: int,
        hyperparameters: Dict[str, float],
    ):
        self.logger.clear()
        lesson = get_lesson_definition(lesson_id)
        if lesson is None:
            raise ValueError(f"Unsupported lesson '{lesson_id}'.")

        lesson_function = load_user_function(code_module_str, lesson.required_function)

        if lesson_id == "dp_policy_eval":
            self._run_policy_evaluation(lesson_function, hyperparameters)
        elif lesson_id == "dp_value_iteration":
            self._run_value_iteration(lesson_function, hyperparameters)
        elif lesson_id == "dp_policy_improvement":
            self._run_policy_improvement(lesson_function, hyperparameters)
        elif lesson_id == "mc_first_visit":
            self._run_mc_first_visit(lesson_function, num_episodes, hyperparameters)
        elif lesson_id == "td_sarsa":
            self._run_sarsa(lesson_function, num_episodes, hyperparameters)
        elif lesson_id == "td_q_learning":
            self._run_q_learning(lesson_function, num_episodes, hyperparameters)
        else:
            raise ValueError(f"Lesson '{lesson_id}' is not implemented.")

    def _build_policy_improvement_values(self) -> list[float]:
        desc = getattr(self.adapter.env.unwrapped, "desc", None)
        state_count = self.adapter.env.observation_space.n
        if desc is None:
            return [0.0 for _ in range(state_count)]

        row_count = len(desc)
        column_count = len(desc[0])
        goal_row, goal_col = row_count - 1, column_count - 1
        values: list[float] = []

        for state in range(state_count):
            row, col = divmod(state, column_count)
            tile = desc[row][col].decode("utf-8")
            if tile == "G":
                values.append(1.0)
                continue
            if tile == "H":
                values.append(0.0)
                continue

            distance = abs(goal_row - row) + abs(goal_col - col)
            shaped_value = max(0.05, 1.0 - 0.15 * distance)
            if tile == "S":
                shaped_value = max(shaped_value, 0.2)
            values.append(round(shaped_value, 4))

        return values

    def _choose_epsilon_greedy_action(self, q_row: list[float], epsilon: float) -> int:
        rng = getattr(self.adapter.env.unwrapped, "np_random", None)
        sample_threshold = float(rng.random()) if rng is not None else 1.0
        if sample_threshold < epsilon:
            return int(self.adapter.env.action_space.sample())

        best_value = max(q_row)
        best_actions = [action for action, value in enumerate(q_row) if value == best_value]
        if len(best_actions) == 1:
            return best_actions[0]
        if rng is not None:
            return best_actions[int(rng.integers(len(best_actions)))]
        return best_actions[0]

    def _max_steps_per_episode(self, hyperparameters: Dict[str, float]) -> int:
        raw_limit = hyperparameters.get("max_steps_per_episode")
        if isinstance(raw_limit, (int, float)) and raw_limit > 0:
            return int(raw_limit)
        return self.DEFAULT_MAX_STEPS_PER_EPISODE

    def _rounded_table(self, table: list[list[float]]) -> list[list[float]]:
        return [[round(float(value), 4) for value in row] for row in table]

    def _empty_q_table(self) -> list[ActionValueRow]:
        state_count = self.adapter.env.observation_space.n
        action_count = self.adapter.env.action_space.n
        return [
            ActionValueRow([0.0 for _ in range(action_count)])
            for _ in range(state_count)
        ]

    def _rounded_vector_table(self, values: list[float]) -> list[list[float]]:
        return [[round(float(value), 4)] for value in values]

    def _grid_metadata_for_step(
        self,
        state: int,
        next_state: int | None = None,
        action: int | None = None,
        reward: float | None = None,
        terminated: bool = False,
        truncated: bool = False,
    ) -> dict[str, Any] | None:
        metadata = getattr(self.adapter, "grid_metadata", None)
        if not callable(metadata):
            return None
        return metadata(
            state=state,
            next_state=next_state,
            action=action,
            reward=reward,
            terminated=terminated,
            truncated=truncated,
        )

    def _log_trace_step(self, payload: dict[str, Any]) -> None:
        if payload.get("trace_schema_version") == 2 and "explanation" not in payload:
            payload = {
                **payload,
                "explanation": self._trace_explanation(payload),
            }
        self.logger.log_step(payload)

    def _trace_explanation(self, payload: dict[str, Any]) -> dict[str, str]:
        equation_update = payload.get("equation_update") or {}
        kind = equation_update.get("kind", "")
        lhs = equation_update.get("lhs", "")
        new_value = equation_update.get("new_value", "")
        code_focus = equation_update.get("code_focus", "")
        summary = payload.get("agent_caption", "")
        table_focus = self._table_focus_label(payload.get("tables") or {})

        why_by_kind = {
            "policy_evaluation": (
                "The value is the policy-weighted Bellman expectation backup: each "
                "transition branch contributes probability times reward plus discounted future value."
            ),
            "value_iteration": (
                "The value is correct when it equals the largest Bellman backup across "
                "available actions for this state."
            ),
            "policy_improvement": (
                "The policy row changes because the action with the largest one-step "
                "lookahead becomes the greedy action."
            ),
            "mc_sampling": (
                "No value changes during sampling; the transition is stored so returns "
                "can be computed after the full episode is known."
            ),
            "mc_first_visit": (
                "First-visit Monte Carlo updates only the first occurrence of this state "
                "using the discounted return observed from that point onward."
            ),
            "q_learning": (
                "Q-learning uses the observed reward plus the discounted best next-state "
                "Q value, with terminal bootstraps recorded as 0.0, then moves only the "
                "visited Q cell by alpha times the TD error."
            ),
            "sarsa": (
                "SARSA uses the observed reward plus the discounted Q value of the sampled "
                "next action, so the update follows the same behavior policy that generated the step."
            ),
        }
        why_correct = why_by_kind.get(
            kind,
            "The update follows the recorded equation terms and changes only the highlighted table cell.",
        )
        if lhs:
            why_correct = f"{why_correct} The recorded result is {lhs} = {new_value}."

        return {
            "summary": str(summary),
            "why_correct": why_correct,
            "code_focus": str(code_focus),
            "table_focus": table_focus,
        }

    def _table_focus_label(self, table: dict[str, Any]) -> str:
        active_cell = table.get("active_cell") or {}
        row = active_cell.get("row")
        column = active_cell.get("column")
        if row is None or column is None:
            return ""
        return f"row {row}, column {column}"

    def _dp_action_backups(
        self,
        state: int,
        values: list[float],
        gamma: float,
        policy_row: list[float] | None = None,
    ) -> list[dict[str, Any]]:
        action_count = self.adapter.env.action_space.n
        backups: list[dict[str, Any]] = []
        for action in range(action_count):
            transitions = self.adapter.transition_details(state, action)
            expected_return = 0.0
            transition_terms = []
            for transition in transitions:
                future = 0.0 if transition["done"] else values[transition["next_state"]]
                contribution = transition["probability"] * (transition["reward"] + gamma * future)
                expected_return += contribution
                transition_terms.append(
                    {
                        "probability": round(float(transition["probability"]), 4),
                        "next_state": transition["next_state"],
                        "reward": round(float(transition["reward"]), 4),
                        "done": transition["done"],
                        "future_value": round(float(future), 4),
                        "contribution": round(float(contribution), 4),
                    }
                )

            policy_probability = (
                None
                if policy_row is None or action >= len(policy_row)
                else float(policy_row[action])
            )
            weighted_contribution = (
                expected_return
                if policy_probability is None
                else policy_probability * expected_return
            )
            backups.append(
                {
                    "action": action,
                    "action_label": self.adapter.action_label(action),
                    "policy_probability": (
                        None if policy_probability is None else round(policy_probability, 4)
                    ),
                    "expected_return": round(float(expected_return), 4),
                    "weighted_contribution": round(float(weighted_contribution), 4),
                    "transition_terms": transition_terms,
                }
            )
        return backups

    def _blackjack_observation(self, state: Any) -> dict[str, Any]:
        if not isinstance(state, tuple) or len(state) < 3:
            return {"raw": str(state)}
        return {
            "player_sum": int(state[0]),
            "dealer_card": int(state[1]),
            "usable_ace": bool(state[2]),
        }

    def _mc_episode_strip(self, episode_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "step_index": step["step_index"],
                "state": str(step["state"]),
                "observation": self._blackjack_observation(step["state"]),
                "action": step["action"],
                "action_label": self.adapter.action_label(step["action"]),
                "reward": round(float(step["reward"]), 4),
                "next_state": str(step["next_state"]),
                "next_observation": self._blackjack_observation(step["next_state"]),
                "terminated": step["terminated"],
                "truncated": step["truncated"],
            }
            for step in episode_steps
        ]

    def _mc_return_ladder(
        self,
        episode_trace: list[tuple[Any, int, float]],
        start_index: int,
        gamma: float,
    ) -> tuple[float, list[dict[str, Any]]]:
        discounted_return = 0.0
        discount = 1.0
        terms: list[dict[str, Any]] = []
        for offset, (_next_state, _next_action, reward) in enumerate(episode_trace[start_index:]):
            discounted_reward = discount * reward
            discounted_return += discounted_reward
            terms.append(
                {
                    "episode_step": start_index + offset,
                    "discount": round(float(discount), 4),
                    "reward": round(float(reward), 4),
                    "discounted_reward": round(float(discounted_reward), 4),
                    "running_return": round(float(discounted_return), 4),
                }
            )
            discount *= gamma
        return discounted_return, terms

    def _run_policy_evaluation(self, lesson_function, hyperparameters: Dict[str, float]):
        state_count = self.adapter.env.observation_space.n
        action_count = self.adapter.env.action_space.n
        values = [0.0 for _ in range(state_count)]
        policy = [[1.0 / action_count for _ in range(action_count)] for _ in range(state_count)]

        lesson_function(values, policy, self.adapter.env.unwrapped, hyperparameters["gamma"])
        self.adapter.reset(seed=7)

        for state in range(state_count):
            reasoning_lines = [
                "Bellman expectation backup:",
                "V(s) = sum_a pi(a|s) sum_s',r p(s',r|s,a) [r + gamma V(s')]",
            ]
            action_backups = self._dp_action_backups(
                state,
                values,
                hyperparameters["gamma"],
                policy[state],
            )
            backup_value = sum(backup["weighted_contribution"] for backup in action_backups)
            action_summaries = [
                (
                    f"a={backup['action']}, pi={backup['policy_probability']}, "
                    f"expected={backup['expected_return']}"
                )
                for backup in action_backups
            ]

            frame_path = self.adapter.capture_frame_png(state=state, prefix="policy_eval")
            self._log_trace_step(
                {
                    "state": state,
                    "action": -1,
                    "reward": 0.0,
                    "next_state": state,
                    "transition_probability": 1.0,
                    "frame_path": frame_path,
                    "grid_metadata": self._grid_metadata_for_step(
                        state=state,
                        next_state=state,
                        action=None,
                        reward=0.0,
                    ),
                    "agent_caption": f"Dynamic-programming sweep focuses on state {state}.",
                    "code_title": "Code Trace",
                    "code_lines": [
                        "for action, action_prob in enumerate(policy[state]):",
                        "    for transition_prob, next_state, reward, done in env.P[state][action]:",
                        "        new_value += action_prob * transition_prob * (reward + gamma * future)",
                    ],
                    "math_title": "Bellman Expectation",
                    "math_equation": r"V^{\pi}(s)=\sum_a \pi(a|s)\sum_{s',r} p(s',r|s,a)\left[r+\gamma V^{\pi}(s')\right]",
                    "math_lines": reasoning_lines + action_summaries[:3],
                    "updated_values": {f"V({state})": round(values[state], 4)},
                    "trace_schema_version": 2,
                    "tables": {
                        "kind": "value_table",
                        "after": self._rounded_vector_table(values),
                        "active_cell": {"row": state, "column": 0},
                        "changed_cells": [{"row": state, "column": 0}],
                        "action_labels": ["Value"],
                    },
                    "equation_update": {
                        "kind": "policy_evaluation",
                        "lhs": f"V({state})",
                        "gamma": round(float(hyperparameters["gamma"]), 4),
                        "td_target": round(float(backup_value), 4),
                        "new_value": round(float(values[state]), 4),
                        "td_error": round(float(values[state] - backup_value), 4),
                        "code_focus": "new_value += action_prob * transition_prob * (reward + gamma * future)",
                        "dp_details": {
                            "action_backups": action_backups,
                            "backup_value": round(float(backup_value), 4),
                            "delta": round(float(abs(values[state] - backup_value)), 4),
                        },
                    },
                }
            )

        self.logger.end_episode()

    def _run_value_iteration(self, lesson_function, hyperparameters: Dict[str, float]):
        state_count = self.adapter.env.observation_space.n
        values = [0.0 for _ in range(state_count)]

        lesson_function(values, self.adapter.env.unwrapped, hyperparameters["gamma"])
        self.adapter.reset(seed=11)

        for state in range(state_count):
            action_backups = self._dp_action_backups(
                state,
                values,
                hyperparameters["gamma"],
            )
            action_values = [
                (backup["action"], backup["expected_return"]) for backup in action_backups
            ]

            best_action, best_value = max(action_values, key=lambda item: item[1])
            frame_path = self.adapter.capture_frame_png(state=state, prefix="value_iter")
            self._log_trace_step(
                {
                    "state": state,
                    "action": best_action,
                    "reward": 0.0,
                    "next_state": state,
                    "transition_probability": 1.0,
                    "frame_path": frame_path,
                    "grid_metadata": self._grid_metadata_for_step(
                        state=state,
                        next_state=state,
                        action=best_action,
                        reward=0.0,
                    ),
                    "agent_caption": f"Value iteration backs up state {state} and keeps best action {self.adapter.action_label(best_action)}.",
                    "code_title": "Code Trace",
                    "code_lines": [
                        "for action in range(action_count):",
                        "    action_value += transition_prob * (reward + gamma * future)",
                        "V[state] = max(action_values)",
                    ],
                    "math_title": "Bellman Optimality",
                    "math_equation": r"V_*(s)=\max_a \sum_{s',r} p(s',r|s,a)\left[r+\gamma V_*(s')\right]",
                    "math_lines": [
                        "Bellman optimality backup:",
                        "V(s) = max_a sum_s',r p(s',r|s,a) [r + gamma V(s')]",
                        *[f"a={action} -> {round(value, 3)}" for action, value in action_values],
                        f"best action = {best_action}",
                    ],
                    "updated_values": {
                        f"V({state})": round(values[state], 4),
                        "backup": round(best_value, 4),
                    },
                    "trace_schema_version": 2,
                    "tables": {
                        "kind": "value_table",
                        "after": self._rounded_vector_table(values),
                        "active_cell": {"row": state, "column": 0},
                        "changed_cells": [{"row": state, "column": 0}],
                        "action_labels": ["Value"],
                    },
                    "equation_update": {
                        "kind": "value_iteration",
                        "lhs": f"V({state})",
                        "gamma": round(float(hyperparameters["gamma"]), 4),
                        "bootstrap_label": f"max action {self.adapter.action_label(best_action)}",
                        "td_target": round(float(best_value), 4),
                        "new_value": round(float(values[state]), 4),
                        "td_error": round(float(values[state] - best_value), 4),
                        "code_focus": "V[state] = max(action_values)",
                        "dp_details": {
                            "action_backups": action_backups,
                            "selected_action": best_action,
                            "selected_action_label": self.adapter.action_label(best_action),
                            "backup_value": round(float(best_value), 4),
                            "delta": round(float(abs(values[state] - best_value)), 4),
                        },
                    },
                }
            )

        self.logger.end_episode()

    def _run_policy_improvement(self, lesson_function, hyperparameters: Dict[str, float]):
        state_count = self.adapter.env.observation_space.n
        values = self._build_policy_improvement_values()
        policy = lesson_function(
            values,
            self.adapter.env.unwrapped,
            hyperparameters["gamma"],
        )
        if policy is None:
            raise ValueError("policy_improvement must return a policy table.")

        self.adapter.reset(seed=13)

        for state in range(state_count):
            action_backups = self._dp_action_backups(
                state,
                values,
                hyperparameters["gamma"],
            )
            action_values = [
                (backup["action"], backup["expected_return"]) for backup in action_backups
            ]

            best_action, best_value = max(action_values, key=lambda item: item[1])
            policy_row = policy[state] if state < len(policy) else []
            selected_action = (
                max(range(len(policy_row)), key=lambda index: policy_row[index])
                if policy_row
                else best_action
            )
            policy_before = [
                [
                    1.0 / self.adapter.env.action_space.n
                    for _ in range(self.adapter.env.action_space.n)
                ]
                for _ in range(state_count)
            ]
            changed_cells = [
                {"row": state, "column": column}
                for column, value in enumerate(policy_row)
                if column < self.adapter.env.action_space.n
                and round(float(value), 4) != round(float(policy_before[state][column]), 4)
            ]
            frame_path = self.adapter.capture_frame_png(
                state=state,
                prefix="policy_improvement",
            )
            self._log_trace_step(
                {
                    "state": state,
                    "action": selected_action,
                    "reward": 0.0,
                    "next_state": state,
                    "transition_probability": 1.0,
                    "frame_path": frame_path,
                    "grid_metadata": self._grid_metadata_for_step(
                        state=state,
                        next_state=state,
                        action=selected_action,
                        reward=0.0,
                    ),
                    "agent_caption": (
                        f"Policy improvement backs up state {state} and chooses "
                        f"{self.adapter.action_label(selected_action)} as the greedy action."
                    ),
                    "code_title": "Code Trace",
                    "code_lines": [
                        "for action in range(env.action_space.n):",
                        "    action_value += transition_prob * (reward + gamma * future)",
                        "policy[state][best_action] = 1.0",
                    ],
                    "math_title": "Greedy Policy Improvement",
                    "math_equation": r"\pi'(s)=\arg\max_a \sum_{s',r} p(s',r|s,a)\left[r+\gamma V(s')\right]",
                    "math_lines": [
                        "Use the current value table to score each available action.",
                        *[f"a={action} -> {round(value, 3)}" for action, value in action_values],
                        f"greedy action = {self.adapter.action_label(selected_action)}",
                    ],
                    "updated_values": {
                        f"pi({state})": self.adapter.action_label(selected_action),
                        "backup": round(best_value, 4),
                    },
                    "trace_schema_version": 2,
                    "tables": {
                        "kind": "policy_table",
                        "before": self._rounded_table(policy_before),
                        "after": self._rounded_table(policy),
                        "active_cell": {"row": state, "column": selected_action},
                        "changed_cells": changed_cells,
                        "action_labels": [
                            self.adapter.action_label(action_index)
                            for action_index in range(self.adapter.env.action_space.n)
                        ],
                    },
                    "equation_update": {
                        "kind": "policy_improvement",
                        "lhs": f"pi({state})",
                        "old_value": "old_pi",
                        "new_value": self.adapter.action_label(selected_action),
                        "bootstrap_label": f"V source for state {state}",
                        "td_target": round(float(best_value), 4),
                        "code_focus": "policy[state][best_action] = 1.0",
                        "dp_details": {
                            "action_backups": action_backups,
                            "selected_action": selected_action,
                            "selected_action_label": self.adapter.action_label(selected_action),
                            "backup_value": round(float(best_value), 4),
                            "policy_row_before": [
                                round(float(value), 4) for value in policy_before[state]
                            ],
                            "policy_row_after": [round(float(value), 4) for value in policy_row],
                            "value_source": self._rounded_vector_table(values),
                        },
                    },
                }
            )

        self.logger.end_episode()

    def _run_mc_first_visit(
        self, lesson_function, num_episodes: int, hyperparameters: Dict[str, float]
    ):
        values: dict[Any, float] = {}
        returns: dict[Any, list[float]] = {}

        for episode_index in range(num_episodes):
            state, _ = self.adapter.reset(seed=episode_index)
            done = False
            episode_trace = []
            episode_steps: list[dict[str, Any]] = []
            step_index = 0

            while not done:
                action = self.adapter.env.action_space.sample()
                next_state, reward, terminated, truncated, info = self.adapter.step(action)
                episode_trace.append((state, action, reward))
                episode_steps.append(
                    {
                        "step_index": step_index,
                        "state": state,
                        "action": action,
                        "reward": reward,
                        "next_state": next_state,
                        "terminated": bool(terminated),
                        "truncated": bool(truncated),
                    }
                )
                frame_path = self.adapter.capture_frame_png(prefix="mc")
                self._log_trace_step(
                    {
                        "state": state,
                        "action": action,
                        "reward": reward,
                        "next_state": next_state,
                        "transition_probability": round(float(info.get("p", 1.0)), 4),
                        "frame_path": frame_path,
                        "agent_caption": f"Agent sampled {self.adapter.action_label(action)} from state {state} to state {next_state}.",
                        "code_title": "Code Trace",
                        "code_lines": [
                            "episode_trace.append((state, action, reward))",
                            "done = terminated or truncated",
                            "updates wait until the full episode is collected",
                        ],
                        "math_title": "Episode Sampling",
                        "math_equation": r"\text{Sample a complete trajectory } (S_0,A_0,R_1,\dots,S_T)",
                        "math_lines": [
                            "A full episode is sampled before any value update is applied.",
                            f"Observed transition probability p = {round(float(info.get('p', 1.0)), 4)}",
                        ],
                        "updated_values": {f"V({state})": round(values.get(state, 0.0), 4)},
                        "trace_schema_version": 2,
                        "equation_update": {
                            "kind": "mc_sampling",
                            "lhs": f"episode[{episode_index}][{step_index}]",
                            "reward": round(float(reward), 4),
                            "new_value": str(next_state),
                            "code_focus": "episode_trace.append((state, action, reward))",
                            "mc_details": {
                                "episode_index": episode_index,
                                "episode_step": step_index,
                                "phase": "sampling",
                                "observation": self._blackjack_observation(state),
                                "next_observation": self._blackjack_observation(next_state),
                                "action": action,
                                "action_label": self.adapter.action_label(action),
                                "reward": round(float(reward), 4),
                                "terminated": bool(terminated),
                                "truncated": bool(truncated),
                                "episode_strip": self._mc_episode_strip(episode_steps),
                            },
                        },
                    }
                )
                state = next_state
                done = terminated or truncated
                step_index += 1

            lesson_function(episode_trace, values, returns, hyperparameters["gamma"])

            visited_states = set()
            for index, (visited_state, action, _reward) in enumerate(episode_trace):
                if visited_state in visited_states:
                    continue
                visited_states.add(visited_state)
                discounted_return, return_terms = self._mc_return_ladder(
                    episode_trace,
                    index,
                    hyperparameters["gamma"],
                )

                frame_path = self.adapter.capture_frame_png(prefix="mc_return")
                self._log_trace_step(
                    {
                        "state": visited_state,
                        "action": action,
                        "reward": 0.0,
                        "next_state": visited_state,
                        "transition_probability": 1.0,
                        "frame_path": frame_path,
                        "agent_caption": (
                            "First-visit Monte Carlo revisits the first occurrence of "
                            f"state {visited_state} after the Blackjack episode has finished."
                        ),
                        "code_title": "Code Trace",
                        "code_lines": [
                            "if state in visited_states: continue",
                            "G += discount * reward",
                            "V[state] = sum(returns[state]) / len(returns[state])",
                        ],
                        "math_title": "First-Visit Return",
                        "math_equation": r"G_t=\sum_{k=0}^{T-t-1}\gamma^k R_{t+k+1},\quad V(s)\leftarrow \text{mean}(G_t)",
                        "math_lines": [
                            f"First visit to state {visited_state} occurs at time index {index}.",
                            f"G = {round(discounted_return, 4)} is appended to returns[{visited_state}].",
                            f"V({visited_state}) becomes the mean of observed first-visit returns.",
                        ],
                        "updated_values": {f"V({visited_state})": round(values[visited_state], 4)},
                        "trace_schema_version": 2,
                        "tables": {
                            "kind": "returns_table",
                            "after": [[round(float(values[visited_state]), 4)]],
                            "active_cell": {"row": 0, "column": 0},
                            "changed_cells": [{"row": 0, "column": 0}],
                            "action_labels": ["V(s)"],
                        },
                        "equation_update": {
                            "kind": "mc_first_visit",
                            "lhs": f"V({visited_state})",
                            "gamma": round(float(hyperparameters["gamma"]), 4),
                            "td_target": round(float(discounted_return), 4),
                            "new_value": round(float(values[visited_state]), 4),
                            "code_focus": "V[state] = sum(returns[state]) / len(returns[state])",
                            "mc_details": {
                                "episode_index": episode_index,
                                "episode_step": index,
                                "phase": "first_visit_update",
                                "observation": self._blackjack_observation(visited_state),
                                "action": action,
                                "action_label": self.adapter.action_label(action),
                                "first_visit": True,
                                "return_value": round(float(discounted_return), 4),
                                "return_terms": return_terms,
                                "returns_history": [
                                    round(float(value), 4)
                                    for value in returns.get(visited_state, [])
                                ],
                                "episode_strip": self._mc_episode_strip(episode_steps),
                            },
                        },
                    }
                )

            self.logger.end_episode()

    def _run_q_learning(
        self, lesson_function, num_episodes: int, hyperparameters: Dict[str, float]
    ):
        action_count = self.adapter.env.action_space.n
        q_table = self._empty_q_table()

        for episode_index in range(num_episodes):
            state, _ = self.adapter.reset(seed=episode_index)
            done = False
            step_count = 0
            max_steps = self._max_steps_per_episode(hyperparameters)

            while not done and step_count < max_steps:
                action = self._choose_epsilon_greedy_action(
                    q_table[state],
                    hyperparameters["epsilon"],
                )
                next_state, reward, terminated, truncated, info = self.adapter.step(action)
                step_count += 1
                old_value = q_table[state][action]
                terminal_transition = bool(terminated or truncated)
                if terminal_transition:
                    best_next_value = 0.0
                    best_next_action = None
                else:
                    best_next_value = max(q_table[next_state])
                    best_next_action = q_table[next_state].index(best_next_value)
                td_target = reward + hyperparameters["gamma"] * best_next_value
                q_table_before = self._rounded_table(q_table)
                lesson_function(
                    q_table,
                    state,
                    action,
                    reward,
                    next_state,
                    hyperparameters["alpha"],
                    hyperparameters["gamma"],
                )
                new_value = q_table[state][action]
                frame_path = self.adapter.capture_frame_png(prefix="q_learning")
                self._log_trace_step(
                    {
                        "state": state,
                        "action": action,
                        "reward": reward,
                        "next_state": next_state,
                        "transition_probability": round(float(info.get("p", 1.0)), 4),
                        "frame_path": frame_path,
                        "grid_metadata": self._grid_metadata_for_step(
                            state=state,
                            next_state=next_state,
                            action=action,
                            reward=reward,
                            terminated=terminated,
                            truncated=truncated,
                        ),
                        "agent_caption": (
                            "Agent selected "
                            f"{self.adapter.action_label(action)} from Q({state}, ·) "
                            f"using epsilon-greedy exploration and moved to {next_state}."
                        ),
                        "code_title": "Code Trace",
                        "code_lines": [
                            "action = epsilon_greedy(Q[state], epsilon)",
                            "best_next_value = max(Q[next_state])",
                            "td_target = reward + gamma * best_next_value",
                            "Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])",
                        ],
                        "math_title": "TD / Q-Learning",
                        "math_equation": r"Q(s,a)\leftarrow Q(s,a)+\alpha\left[r+\gamma \max_{a'}Q(s',a')-Q(s,a)\right]",
                        "math_lines": [
                            "The behavior action is selected from the current Q-row, not by a blind grid step.",
                            f"Sampled transition probability p = {round(float(info.get('p', 1.0)), 4)}.",
                            f"TD target = reward + gamma * max Q(next_state, ·) = {round(td_target, 4)}.",
                            f"Q({state}, {action}) updates from {round(old_value, 4)} to {round(new_value, 4)}.",
                        ],
                        "updated_values": {f"Q({state}, {action})": round(new_value, 4)},
                        "trace_schema_version": 2,
                        "tables": {
                            "kind": "q_table",
                            "before": q_table_before,
                            "after": self._rounded_table(q_table),
                            "active_cell": {"row": state, "column": action},
                            "bootstrap_cell": (
                                None
                                if best_next_action is None
                                else {"row": next_state, "column": best_next_action}
                            ),
                            "changed_cells": [{"row": state, "column": action}],
                            "action_labels": [
                                self.adapter.action_label(action_index)
                                for action_index in range(action_count)
                            ],
                        },
                        "equation_update": {
                            "kind": "q_learning",
                            "lhs": f"Q({state},{action})",
                            "old_value": round(old_value, 4),
                            "reward": round(float(reward), 4),
                            "gamma": round(float(hyperparameters["gamma"]), 4),
                            "bootstrap_label": (
                                "0 terminal" if terminal_transition else f"max_a Q({next_state},a)"
                            ),
                            "bootstrap_value": round(float(best_next_value), 4),
                            "td_target": round(float(td_target), 4),
                            "td_error": round(float(td_target - old_value), 4),
                            "alpha": round(float(hyperparameters["alpha"]), 4),
                            "new_value": round(float(new_value), 4),
                            "substitution": (
                                f"{round(old_value, 4)} + {round(float(hyperparameters['alpha']), 4)} "
                                f"* ({round(float(reward), 4)} + "
                                f"{round(float(hyperparameters['gamma']), 4)} * "
                                f"{round(float(best_next_value), 4)} - {round(old_value, 4)})"
                            ),
                            "code_focus": "Q[state][action] += alpha * (td_target - Q[state][action])",
                        },
                    }
                )
                state = next_state
                done = terminated or truncated or step_count >= max_steps

            self.logger.end_episode()

    def _run_sarsa(self, lesson_function, num_episodes: int, hyperparameters: Dict[str, float]):
        action_count = self.adapter.env.action_space.n
        q_table = self._empty_q_table()

        for episode_index in range(num_episodes):
            state, _ = self.adapter.reset(seed=episode_index)
            action = self._choose_epsilon_greedy_action(
                q_table[state],
                hyperparameters["epsilon"],
            )
            done = False
            step_count = 0
            max_steps = self._max_steps_per_episode(hyperparameters)

            while not done and step_count < max_steps:
                next_state, reward, terminated, truncated, info = self.adapter.step(action)
                step_count += 1
                episode_limit_reached = step_count >= max_steps
                next_action = None
                if not (terminated or truncated or episode_limit_reached):
                    next_action = self._choose_epsilon_greedy_action(
                        q_table[next_state],
                        hyperparameters["epsilon"],
                    )
                old_value = q_table[state][action]
                bootstrap = 0.0 if next_action is None else q_table[next_state][next_action]
                td_target = reward + hyperparameters["gamma"] * bootstrap
                q_table_before = self._rounded_table(q_table)
                lesson_function(
                    q_table,
                    state,
                    action,
                    reward,
                    next_state,
                    next_action,
                    hyperparameters["alpha"],
                    hyperparameters["gamma"],
                )
                new_value = q_table[state][action]
                frame_path = self.adapter.capture_frame_png(prefix="sarsa")
                sampled_next_action = (
                    "terminal" if next_action is None else self.adapter.action_label(next_action)
                )
                self._log_trace_step(
                    {
                        "state": state,
                        "action": action,
                        "reward": reward,
                        "next_state": next_state,
                        "transition_probability": round(float(info.get("p", 1.0)), 4),
                        "frame_path": frame_path,
                        "grid_metadata": self._grid_metadata_for_step(
                            state=state,
                            next_state=next_state,
                            action=action,
                            reward=reward,
                            terminated=terminated,
                            truncated=truncated,
                        ),
                        "agent_caption": (
                            f"SARSA uses the sampled next action {sampled_next_action} "
                            f"after moving from state {state} to {next_state}."
                        ),
                        "code_title": "Code Trace",
                        "code_lines": [
                            "next_action = behavior_policy(next_state)",
                            "td_target = reward + gamma * Q[next_state][next_action]",
                            "Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])",
                        ],
                        "math_title": "TD / SARSA",
                        "math_equation": r"Q(s,a)\leftarrow Q(s,a)+\alpha\left[r+\gamma Q(s',a')-Q(s,a)\right]",
                        "math_lines": [
                            f"Sampled transition probability p = {round(float(info.get('p', 1.0)), 4)}.",
                            f"Next action a' = {sampled_next_action}.",
                            f"TD target = {round(td_target, 4)} updates Q({state}, {action}) from {round(old_value, 4)} to {round(new_value, 4)}.",
                        ],
                        "updated_values": {f"Q({state}, {action})": round(new_value, 4)},
                        "trace_schema_version": 2,
                        "tables": {
                            "kind": "q_table",
                            "before": q_table_before,
                            "after": self._rounded_table(q_table),
                            "active_cell": {"row": state, "column": action},
                            "bootstrap_cell": (
                                None
                                if next_action is None
                                else {"row": next_state, "column": next_action}
                            ),
                            "changed_cells": [{"row": state, "column": action}],
                            "action_labels": [
                                self.adapter.action_label(action_index)
                                for action_index in range(action_count)
                            ],
                        },
                        "equation_update": {
                            "kind": "sarsa",
                            "lhs": f"Q({state},{action})",
                            "old_value": round(old_value, 4),
                            "reward": round(float(reward), 4),
                            "gamma": round(float(hyperparameters["gamma"]), 4),
                            "bootstrap_label": (
                                "0 terminal"
                                if next_action is None
                                else f"Q({next_state},{next_action})"
                            ),
                            "bootstrap_value": round(float(bootstrap), 4),
                            "td_target": round(float(td_target), 4),
                            "td_error": round(float(td_target - old_value), 4),
                            "alpha": round(float(hyperparameters["alpha"]), 4),
                            "new_value": round(float(new_value), 4),
                            "substitution": (
                                f"{round(old_value, 4)} + {round(float(hyperparameters['alpha']), 4)} "
                                f"* ({round(float(reward), 4)} + "
                                f"{round(float(hyperparameters['gamma']), 4)} * "
                                f"{round(float(bootstrap), 4)} - {round(old_value, 4)})"
                            ),
                            "code_focus": "Q[state][action] += alpha * (td_target - Q[state][action])",
                        },
                    }
                )
                state = next_state
                action = next_action if next_action is not None else 0
                done = terminated or truncated or episode_limit_reached

            self.logger.end_episode()
