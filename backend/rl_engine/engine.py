import os
from typing import Any, Dict

import gymnasium as gym
from PIL import Image

from backend.lesson_registry import get_lesson_definition
from backend.rl_engine.taxi import TAXI_ACTION_LABELS, taxi_grid_metadata
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
        if self.env_name == "Taxi":
            return gym.make(
                "Taxi-v4",
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
            "Taxi": TAXI_ACTION_LABELS,
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

        if self.env_name == "Taxi":
            return taxi_grid_metadata(
                state=state,
                next_state=next_state,
                action=action,
                reward=reward,
                terminated=terminated,
                truncated=truncated,
            )
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
            return None
        elif lesson_id == "dp_value_iteration":
            self._run_value_iteration(lesson_function, hyperparameters)
            return None
        elif lesson_id == "dp_policy_improvement":
            self._run_policy_improvement(lesson_function, hyperparameters)
            return None
        elif lesson_id == "mc_first_visit":
            self._run_mc_first_visit(lesson_function, num_episodes, hyperparameters)
            return None
        elif lesson_id == "td_sarsa":
            return self._run_td_control_with_greedy_evaluation(
                lesson_id,
                lesson_function,
                hyperparameters,
            )
        elif lesson_id == "td_q_learning":
            return self._run_td_control_with_greedy_evaluation(
                lesson_id,
                lesson_function,
                hyperparameters,
            )
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
            action_count = len(q_row)
            if action_count == getattr(self.adapter.env.action_space, "n", action_count):
                return int(self.adapter.env.action_space.sample())
            if rng is not None:
                return int(rng.integers(action_count))
            return 0

        best_value = max(q_row)
        best_actions = [action for action, value in enumerate(q_row) if value == best_value]
        if len(best_actions) == 1:
            return best_actions[0]
        if rng is not None:
            return best_actions[int(rng.integers(len(best_actions)))]
        return best_actions[0]

    def _legal_actions(self, action_mask: Any, action_count: int) -> list[int]:
        if action_mask is None:
            return list(range(action_count))
        try:
            values = [int(value) for value in action_mask]
        except TypeError:
            return list(range(action_count))
        legal_actions = [
            action
            for action, enabled in enumerate(values[:action_count])
            if enabled
        ]
        return legal_actions or list(range(action_count))

    def _choose_masked_epsilon_greedy_action(
        self,
        q_row: list[float],
        epsilon: float,
        action_mask: Any,
    ) -> int:
        legal_actions = self._legal_actions(action_mask, len(q_row))
        if len(legal_actions) == len(q_row):
            return self._choose_epsilon_greedy_action(q_row, epsilon)
        masked_row = [q_row[action] for action in legal_actions]
        chosen_offset = self._choose_epsilon_greedy_action(masked_row, epsilon)
        return legal_actions[chosen_offset]

    def _best_masked_action_value(
        self,
        q_row: list[float],
        action_mask: Any,
    ) -> tuple[int, float]:
        legal_actions = self._legal_actions(action_mask, len(q_row))
        best_value = max(q_row[action] for action in legal_actions)
        best_actions = [action for action in legal_actions if q_row[action] == best_value]
        if len(best_actions) == 1:
            return best_actions[0], float(best_value)
        rng = getattr(self.adapter.env.unwrapped, "np_random", None)
        if rng is not None:
            return best_actions[int(rng.integers(len(best_actions)))], float(best_value)
        return best_actions[0], float(best_value)

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

    def _td_control_config(self, lesson_id: str) -> dict[str, int | float | bool]:
        if lesson_id == "td_sarsa":
            # Budgets raised to actually CONVERGE (CliffWalking SARSA solves in
            # ~200 episodes, ~0.1s) so the greedy episode reaches the goal.
            return {
                "base_training_episodes": 400,
                "adaptive_extension": 100,
                "max_training_episodes": 800,
                "evaluation_attempts": 8,
                "training_max_steps": 100,
                "visible_step_cap": 40,
                "epsilon_start": 0.30,
                "epsilon_end": 0.02,
                "use_action_mask": False,
            }
        if lesson_id == "td_q_learning":
            # Taxi Q-learning needs ~2000+ episodes to converge (measured ~2.3s);
            # the previous default of 500 did NOT solve the task, so the greedy
            # episode truncated and the replay looked weak.
            return {
                "base_training_episodes": 2000,
                "adaptive_extension": 500,
                "max_training_episodes": 4000,
                "evaluation_attempts": 20,
                "training_max_steps": 200,
                "visible_step_cap": 50,
                "epsilon_start": 0.30,
                "epsilon_end": 0.02,
                "use_action_mask": True,
            }
        raise ValueError(f"Unsupported TD control lesson '{lesson_id}'.")

    def _scheduled_epsilon(
        self,
        episode_index: int,
        total_episodes: int,
        start: float,
        end: float,
    ) -> float:
        if total_episodes <= 1:
            return round(float(end), 4)
        progress = min(max(episode_index / float(total_episodes - 1), 0.0), 1.0)
        return round(float(start + (end - start) * progress), 4)

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

            return_lengths_before = {
                state_key: len(history)
                for state_key, history in returns.items()
                if isinstance(history, list)
            }
            result = lesson_function(
                episode_trace,
                values,
                returns,
                hyperparameters["gamma"],
            )
            self._apply_mc_prediction_result(result, values, returns)

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
                previous_return_count = return_lengths_before.get(visited_state, 0)
                current_return_count = len(returns.get(visited_state, []))
                if current_return_count <= previous_return_count:
                    returns.setdefault(visited_state, []).append(discounted_return)
                if visited_state not in values:
                    values[visited_state] = (
                        sum(returns[visited_state]) / len(returns[visited_state])
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

    def _apply_mc_prediction_result(
        self,
        result: Any,
        values: dict[Any, float],
        returns: dict[Any, list[float]],
    ) -> None:
        """Accept in-place and returned-table Monte Carlo prediction styles."""
        if result is None:
            return

        if isinstance(result, dict):
            returned_values = result.get("V") or result.get("values")
            returned_returns = result.get("returns")
            if isinstance(returned_values, dict):
                values.update(returned_values)
            elif "V" not in result and "values" not in result and "returns" not in result:
                values.update(result)
            if isinstance(returned_returns, dict):
                returns.update(returned_returns)
            return

        if isinstance(result, (list, tuple)):
            if len(result) >= 1 and isinstance(result[0], dict):
                values.update(result[0])
            if len(result) >= 2 and isinstance(result[1], dict):
                returns.update(result[1])

    def _run_td_control_with_greedy_evaluation(
        self,
        lesson_id: str,
        lesson_function,
        hyperparameters: Dict[str, float],
    ) -> dict[str, Any]:
        config = self._td_control_config(lesson_id)
        q_table = self._empty_q_table()
        training_episodes_run = 0
        evaluation_attempts_run = 0
        selected_trace = None
        selected_seed = None
        best_selected_trace = None
        best_selected_seed = None
        target_training_episodes = int(config["base_training_episodes"])
        capture_targets = self._td_stage_capture_targets(int(config["base_training_episodes"]))
        captured_training_traces: dict[str, dict[str, Any]] = {}

        while True:
            while training_episodes_run < target_training_episodes:
                epsilon = self._scheduled_epsilon(
                    training_episodes_run,
                    int(config["max_training_episodes"]),
                    float(config["epsilon_start"]),
                    float(config["epsilon_end"]),
                )
                capture_stage = capture_targets.get(training_episodes_run)
                record_trace = capture_stage is not None and capture_stage not in captured_training_traces
                if lesson_id == "td_q_learning":
                    trace = self._run_q_learning_td_episode(
                        lesson_function,
                        q_table,
                        alpha=float(hyperparameters["alpha"]),
                        gamma=float(hyperparameters["gamma"]),
                        epsilon=epsilon,
                        max_steps=int(config["training_max_steps"]),
                        seed=training_episodes_run,
                        use_action_mask=bool(config["use_action_mask"]),
                        apply_updates=True,
                        record_trace=record_trace,
                    )
                else:
                    trace = self._run_sarsa_td_episode(
                        lesson_function,
                        q_table,
                        alpha=float(hyperparameters["alpha"]),
                        gamma=float(hyperparameters["gamma"]),
                        epsilon=epsilon,
                        max_steps=int(config["training_max_steps"]),
                        seed=training_episodes_run,
                        apply_updates=True,
                        record_trace=record_trace,
                    )
                if record_trace and trace["steps"]:
                    captured_training_traces[capture_stage] = self._build_td_stage_trace(
                        stage=capture_stage,
                        episode_index=training_episodes_run,
                        trace=trace,
                    )
                training_episodes_run += 1

            remaining_attempts = int(config["evaluation_attempts"]) - evaluation_attempts_run
            if remaining_attempts <= 0:
                break
            attempt_budget = (
                remaining_attempts
                if training_episodes_run >= int(config["max_training_episodes"])
                else 1
            )
            selected_trace, selected_seed, attempts_used = self._evaluate_td_policy(
                lesson_id=lesson_id,
                lesson_function=lesson_function,
                q_table=q_table,
                alpha=float(hyperparameters["alpha"]),
                gamma=float(hyperparameters["gamma"]),
                max_steps=int(config["visible_step_cap"]),
                attempt_count=attempt_budget,
                seed_offset=training_episodes_run + evaluation_attempts_run,
                use_action_mask=bool(config["use_action_mask"]),
            )
            evaluation_attempts_run += attempts_used
            if self._prefer_td_trace(selected_trace, best_selected_trace):
                best_selected_trace = selected_trace
                best_selected_seed = selected_seed
            if bool(selected_trace and selected_trace["terminated"]):
                break
            if training_episodes_run >= int(config["max_training_episodes"]):
                break
            target_training_episodes = min(
                training_episodes_run + int(config["adaptive_extension"]),
                int(config["max_training_episodes"]),
            )

        selected_trace = best_selected_trace
        selected_seed = best_selected_seed
        if selected_trace:
            for step in selected_trace["steps"]:
                self._log_trace_step(step)
            self.logger.end_episode()

        selected_steps = [] if selected_trace is None else selected_trace["steps"]
        selected_total_reward = 0.0 if selected_trace is None else float(selected_trace["total_reward"])
        selected_terminated = bool(selected_trace and selected_trace["terminated"])
        staged_trace_episodes = [
            captured_training_traces[stage]
            for stage in ("untrained", "improving")
            if stage in captured_training_traces
        ]
        if selected_trace is not None:
            staged_trace_episodes.append(
                self._build_td_stage_trace(
                    stage="converged",
                    episode_index=training_episodes_run,
                    trace=selected_trace,
                )
            )
        return {
            "evaluation_summary": {
                "mode": "greedy_evaluation",
                "training_episodes_run": training_episodes_run,
                "evaluation_attempts_run": evaluation_attempts_run,
                "selected_seed": selected_seed,
                "selected_step_count": len(selected_steps),
                "selected_total_reward": round(selected_total_reward, 4),
                "selected_terminated": selected_terminated,
            },
            "staged_trace_episodes": staged_trace_episodes,
        }

    def _td_stage_capture_targets(self, base_training_episodes: int) -> dict[int, str]:
        if base_training_episodes <= 1:
            return {0: "untrained"}

        improving_index = max(1, (base_training_episodes // 2) - 1)
        return {
            0: "untrained",
            improving_index: "improving",
        }

    def _build_td_stage_trace(
        self,
        *,
        stage: str,
        episode_index: int,
        trace: dict[str, Any],
    ) -> dict[str, Any]:
        step_count = int(trace.get("step_count") or len(trace.get("steps") or []))
        terminated = bool(trace.get("terminated"))
        total_reward = round(float(trace.get("total_reward") or 0.0), 4)
        stage_label = self._td_stage_label(
            stage=stage,
            episode_index=episode_index,
            step_count=step_count,
            terminated=terminated,
        )
        return {
            "stage": stage,
            "stage_label": stage_label,
            "episode_index": episode_index,
            "step_count": step_count,
            "total_reward": total_reward,
            "terminated": terminated,
            "steps": trace.get("steps") or [],
        }

    def _td_stage_label(
        self,
        *,
        stage: str,
        episode_index: int,
        step_count: int,
        terminated: bool,
    ) -> str:
        if stage == "untrained":
            return f"① Untrained · episode {episode_index + 1}"
        if stage == "improving":
            return f"② Improving · episode {episode_index + 1}"
        if terminated:
            step_label = "step" if step_count == 1 else "steps"
            return f"③ Converged · solved in {step_count} {step_label}"
        return f"③ Converged · best evaluation after {episode_index} training episodes"

    def _evaluate_td_policy(
        self,
        *,
        lesson_id: str,
        lesson_function,
        q_table: list[ActionValueRow],
        alpha: float,
        gamma: float,
        max_steps: int,
        attempt_count: int,
        seed_offset: int,
        use_action_mask: bool,
    ) -> tuple[dict[str, Any] | None, int | None, int]:
        best_terminal_trace = None
        best_terminal_seed = None
        best_fallback_trace = None
        best_fallback_seed = None
        attempts_used = 0

        for attempt in range(attempt_count):
            seed = seed_offset + attempt
            if lesson_id == "td_q_learning":
                trace = self._run_q_learning_td_episode(
                    lesson_function,
                    q_table,
                    alpha=alpha,
                    gamma=gamma,
                    epsilon=0.0,
                    max_steps=max_steps,
                    seed=seed,
                    use_action_mask=use_action_mask,
                    apply_updates=False,
                    record_trace=True,
                )
            else:
                trace = self._run_sarsa_td_episode(
                    lesson_function,
                    q_table,
                    alpha=alpha,
                    gamma=gamma,
                    epsilon=0.0,
                    max_steps=max_steps,
                    seed=seed,
                    apply_updates=False,
                    record_trace=True,
                )
            attempts_used += 1
            if trace["terminated"]:
                if best_terminal_trace is None:
                    best_terminal_trace = trace
                    best_terminal_seed = seed
                    continue
                if trace["step_count"] < best_terminal_trace["step_count"]:
                    best_terminal_trace = trace
                    best_terminal_seed = seed
                    continue
                if (
                    trace["step_count"] == best_terminal_trace["step_count"]
                    and trace["total_reward"] > best_terminal_trace["total_reward"]
                ):
                    best_terminal_trace = trace
                    best_terminal_seed = seed
                continue

            if best_fallback_trace is None:
                best_fallback_trace = trace
                best_fallback_seed = seed
                continue
            if trace["total_reward"] > best_fallback_trace["total_reward"]:
                best_fallback_trace = trace
                best_fallback_seed = seed
                continue
            if (
                trace["total_reward"] == best_fallback_trace["total_reward"]
                and self._trace_is_not_truncated(trace)
                and not self._trace_is_not_truncated(best_fallback_trace)
            ):
                best_fallback_trace = trace
                best_fallback_seed = seed
                continue
            if (
                trace["total_reward"] == best_fallback_trace["total_reward"]
                and self._trace_is_not_truncated(trace)
                == self._trace_is_not_truncated(best_fallback_trace)
                and trace["step_count"] < best_fallback_trace["step_count"]
            ):
                best_fallback_trace = trace
                best_fallback_seed = seed

        if best_terminal_trace is not None:
            return best_terminal_trace, best_terminal_seed, attempts_used
        return best_fallback_trace, best_fallback_seed, attempts_used

    def _trace_is_not_truncated(self, trace: dict[str, Any]) -> bool:
        steps = trace.get("steps") or []
        last_step = steps[-1] if steps else {}
        grid_metadata = last_step.get("grid_metadata") or {}
        return not bool(grid_metadata.get("truncated"))

    def _prefer_td_trace(
        self,
        candidate: dict[str, Any] | None,
        incumbent: dict[str, Any] | None,
    ) -> bool:
        if candidate is None:
            return False
        if incumbent is None:
            return True
        if bool(candidate.get("terminated")) != bool(incumbent.get("terminated")):
            return bool(candidate.get("terminated"))
        candidate_reward = float(candidate.get("total_reward") or 0.0)
        incumbent_reward = float(incumbent.get("total_reward") or 0.0)
        if candidate_reward != incumbent_reward:
            return candidate_reward > incumbent_reward
        candidate_not_truncated = self._trace_is_not_truncated(candidate)
        incumbent_not_truncated = self._trace_is_not_truncated(incumbent)
        if candidate_not_truncated != incumbent_not_truncated:
            return candidate_not_truncated
        return int(candidate.get("step_count") or 0) < int(incumbent.get("step_count") or 0)

    def _run_q_learning_td_episode(
        self,
        lesson_function,
        q_table: list[ActionValueRow],
        *,
        alpha: float,
        gamma: float,
        epsilon: float,
        max_steps: int,
        seed: int,
        use_action_mask: bool,
        apply_updates: bool,
        record_trace: bool,
    ) -> dict[str, Any]:
        state, reset_info = self.adapter.reset(seed=seed)
        info = reset_info if isinstance(reset_info, dict) else {}
        action_mask = info.get("action_mask")
        done = False
        step_count = 0
        total_reward = 0.0
        steps: list[dict[str, Any]] = []
        action_count = self.adapter.env.action_space.n

        while not done and step_count < max_steps:
            action = (
                self._choose_masked_epsilon_greedy_action(q_table[state], epsilon, action_mask)
                if use_action_mask
                else self._choose_epsilon_greedy_action(q_table[state], epsilon)
            )
            next_state, reward, terminated, truncated, info = self.adapter.step(action)
            step_count += 1
            total_reward += float(reward)
            episode_limit_reached = step_count >= max_steps
            effective_truncated = bool(truncated or episode_limit_reached)
            terminal_transition = bool(terminated or effective_truncated)
            next_action_mask = info.get("action_mask")

            if terminal_transition:
                best_next_action = None
                best_next_value = 0.0
            elif use_action_mask:
                best_next_action, best_next_value = self._best_masked_action_value(
                    q_table[next_state],
                    next_action_mask,
                )
            else:
                best_next_value = float(max(q_table[next_state]))
                best_next_action = q_table[next_state].index(best_next_value)

            if apply_updates:
                lesson_function(
                    q_table,
                    state,
                    action,
                    reward,
                    next_state,
                    alpha,
                    gamma,
                )

            if record_trace:
                steps.append(
                    self._td_evaluation_step_payload(
                        state=state,
                        action=action,
                        reward=float(reward),
                        next_state=next_state,
                        terminated=bool(terminated),
                        truncated=effective_truncated,
                        transition_probability=float(info.get("p", 1.0)),
                        q_table=q_table,
                        active_column=action,
                        bootstrap_column=best_next_action,
                        action_count=action_count,
                        prefix="q_learning_eval",
                    )
                )

            state = next_state
            action_mask = next_action_mask
            done = terminal_transition

        return {
            "steps": steps,
            "step_count": step_count,
            "total_reward": total_reward,
            "terminated": done and not (steps[-1]["grid_metadata"]["truncated"] if steps else False),
        }

    def _run_sarsa_td_episode(
        self,
        lesson_function,
        q_table: list[ActionValueRow],
        *,
        alpha: float,
        gamma: float,
        epsilon: float,
        max_steps: int,
        seed: int,
        apply_updates: bool,
        record_trace: bool,
    ) -> dict[str, Any]:
        state, _ = self.adapter.reset(seed=seed)
        action = self._choose_epsilon_greedy_action(q_table[state], epsilon)
        done = False
        step_count = 0
        total_reward = 0.0
        steps: list[dict[str, Any]] = []
        action_count = self.adapter.env.action_space.n

        while not done and step_count < max_steps:
            next_state, reward, terminated, truncated, info = self.adapter.step(action)
            step_count += 1
            total_reward += float(reward)
            episode_limit_reached = step_count >= max_steps
            effective_truncated = bool(truncated or episode_limit_reached)
            next_action = None
            if not (terminated or effective_truncated):
                next_action = self._choose_epsilon_greedy_action(q_table[next_state], epsilon)

            if apply_updates:
                lesson_function(
                    q_table,
                    state,
                    action,
                    reward,
                    next_state,
                    next_action,
                    alpha,
                    gamma,
                )

            if record_trace:
                steps.append(
                    self._td_evaluation_step_payload(
                        state=state,
                        action=action,
                        reward=float(reward),
                        next_state=next_state,
                        terminated=bool(terminated),
                        truncated=effective_truncated,
                        transition_probability=float(info.get("p", 1.0)),
                        q_table=q_table,
                        active_column=action,
                        bootstrap_column=next_action,
                        action_count=action_count,
                        prefix="sarsa_eval",
                    )
                )

            state = next_state
            action = 0 if next_action is None else next_action
            done = bool(terminated or effective_truncated)

        return {
            "steps": steps,
            "step_count": step_count,
            "total_reward": total_reward,
            "terminated": done and not (steps[-1]["grid_metadata"]["truncated"] if steps else False),
        }

    def _td_evaluation_step_payload(
        self,
        *,
        state: int,
        action: int,
        reward: float,
        next_state: int,
        terminated: bool,
        truncated: bool,
        transition_probability: float,
        q_table: list[ActionValueRow],
        active_column: int,
        bootstrap_column: int | None,
        action_count: int,
        prefix: str,
    ) -> dict[str, Any]:
        frame_path = self.adapter.capture_frame_png(prefix=prefix)
        return {
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": next_state,
            "transition_probability": round(float(transition_probability), 4),
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
                f"Greedy evaluation followed {self.adapter.action_label(action)} "
                f"from state {state} to {next_state} using the policy learned by your code."
            ),
            "code_title": "Greedy Policy Evaluation",
            "code_lines": [
                "action = argmax_a Q[state][a]",
                "follow the learned policy without exploration",
                "record the real environment transition for replay",
            ],
            "math_title": "Greedy Evaluation",
            "math_equation": r"a=\arg\max_a Q(s,a)",
            "math_lines": [
                f"Exploration is disabled, so epsilon = 0.0 and the learned greedy action is selected.",
                f"The evaluation transition carries reward {round(reward, 4)} and probability {round(float(transition_probability), 4)}.",
            ],
            "updated_values": {f"Q({state}, {action})": round(float(q_table[state][action]), 4)},
            "trace_schema_version": 2,
            "tables": {
                "kind": "q_table",
                "after": self._rounded_table(q_table),
                "active_cell": {"row": state, "column": active_column},
                "bootstrap_cell": (
                    None
                    if bootstrap_column is None
                    else {"row": next_state, "column": bootstrap_column}
                ),
                "changed_cells": [],
                "action_labels": [
                    self.adapter.action_label(action_index)
                    for action_index in range(action_count)
                ],
            },
        }

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
                episode_limit_reached = step_count >= max_steps
                old_value = q_table[state][action]
                effective_truncated = bool(truncated or episode_limit_reached)
                terminal_transition = bool(terminated or effective_truncated)
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
                            truncated=effective_truncated,
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
                done = terminated or effective_truncated

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
                effective_truncated = bool(truncated or episode_limit_reached)
                next_action = None
                if not (terminated or effective_truncated):
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
                            truncated=effective_truncated,
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
                done = terminated or effective_truncated

            self.logger.end_episode()
