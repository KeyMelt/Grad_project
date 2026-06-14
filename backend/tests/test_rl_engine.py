from __future__ import annotations

from types import SimpleNamespace

from backend.rl_engine import engine as engine_module
from backend.rl_engine.engine import EnvironmentAdapter, RLEngine


def test_cliff_walking_adapter_uses_current_gymnasium_version(monkeypatch):
    created_env_ids: list[str] = []

    def fake_make(env_id, **kwargs):
        del kwargs
        created_env_ids.append(env_id)
        return SimpleNamespace()

    monkeypatch.setattr(engine_module.gym, "make", fake_make)

    EnvironmentAdapter("CliffWalking")

    assert created_env_ids == ["CliffWalking-v1"]


def test_frozen_lake_grid_metadata_is_derived_from_desc():
    adapter = EnvironmentAdapter.__new__(EnvironmentAdapter)
    adapter.env_name = "FrozenLake"
    adapter.env = SimpleNamespace(
        unwrapped=SimpleNamespace(
            desc=[
                [b"S", b"F"],
                [b"H", b"G"],
            ]
        )
    )

    metadata = adapter.grid_metadata(
        state=0,
        next_state=1,
        action=2,
        reward=0.0,
        terminated=False,
        truncated=False,
    )

    assert metadata["environment"] == "FrozenLake"
    assert metadata["rows"] == 2
    assert metadata["columns"] == 2
    assert metadata["state_coordinates"] == {"row": 0, "column": 0}
    assert metadata["next_state_coordinates"] == {"row": 0, "column": 1}
    assert metadata["action_label"] == "Right"
    assert metadata["cells"][2]["tile_type"] == "H"
    assert metadata["cells"][3]["terminal"] is True


def test_cliff_walking_grid_metadata_marks_cliff_and_goal_cells():
    adapter = EnvironmentAdapter.__new__(EnvironmentAdapter)
    adapter.env_name = "CliffWalking"
    adapter.env = SimpleNamespace(unwrapped=SimpleNamespace())

    metadata = adapter.grid_metadata(
        state=36,
        next_state=24,
        action=0,
        reward=-1.0,
        terminated=False,
        truncated=False,
    )

    cliff_cells = [cell for cell in metadata["cells"] if cell["tile_type"] == "C"]
    goal_cells = [cell for cell in metadata["cells"] if cell["tile_type"] == "G"]
    assert metadata["environment"] == "CliffWalking"
    assert metadata["rows"] == 4
    assert metadata["columns"] == 12
    assert metadata["state_coordinates"] == {"row": 3, "column": 0}
    assert metadata["next_state_coordinates"] == {"row": 2, "column": 0}
    assert metadata["action_label"] == "Up"
    assert len(cliff_cells) == 10
    assert goal_cells == [
        {
            "state": 47,
            "row": 3,
            "column": 11,
            "tile_type": "G",
            "terminal": True,
        }
    ]


def test_q_learning_behavior_uses_epsilon_greedy_q_row(monkeypatch):
    selected_q_rows: list[list[float]] = []
    selected_epsilons: list[float] = []
    lesson_actions: list[int] = []

    class FakeActionSpace:
        n = 4

        def sample(self):
            return 3

    class FakeEnv:
        observation_space = SimpleNamespace(n=2)
        action_space = FakeActionSpace()

        @property
        def unwrapped(self):
            return self

    class FakeAdapter:
        env = FakeEnv()

        def reset(self, seed=None):
            del seed
            return 0, {}

        def step(self, action):
            return 1, -1.0, True, False, {"p": 1.0, "action": action}

        def capture_frame_png(self, prefix="step", state=None):
            del prefix, state
            return ""

        def action_label(self, action):
            return f"Action {action}"

    class FakeLogger:
        def log_step(self, payload):
            self.payload = payload

        def end_episode(self):
            self.ended = True

    def fake_choose(self, q_row, epsilon):
        del self
        selected_q_rows.append(list(q_row))
        selected_epsilons.append(epsilon)
        return 1

    def lesson_function(Q, state, action, reward, next_state, alpha, gamma):
        del reward, next_state, alpha, gamma
        lesson_actions.append(action)
        Q[state][action] = 0.5
        return Q

    monkeypatch.setattr(RLEngine, "_choose_epsilon_greedy_action", fake_choose)

    rl_engine = RLEngine(FakeAdapter(), FakeLogger())
    rl_engine._run_q_learning(
        lesson_function,
        num_episodes=1,
        hyperparameters={"alpha": 0.1, "gamma": 0.95, "epsilon": 0.2},
    )

    assert selected_q_rows == [[0.0, 0.0, 0.0, 0.0]]
    assert selected_epsilons == [0.2]
    assert lesson_actions == [1]
    payload = rl_engine.logger.payload
    assert payload["trace_schema_version"] == 2
    assert payload["equation_update"]["kind"] == "q_learning"
    assert payload["equation_update"]["td_target"] == -1.0
    assert payload["equation_update"]["td_error"] == -1.0
    assert payload["equation_update"]["bootstrap_label"] == "0 terminal"
    assert payload["equation_update"]["bootstrap_value"] == 0.0
    assert payload["tables"]["kind"] == "q_table"
    assert payload["tables"]["active_cell"] == {"row": 0, "column": 1}
    assert payload["tables"]["bootstrap_cell"] is None
    assert payload["tables"]["changed_cells"] == [{"row": 0, "column": 1}]
    assert payload["tables"]["before"][0][1] == 0.0
    assert payload["tables"]["after"][0][1] == 0.5
    assert payload["explanation"]["code_focus"] == payload["equation_update"]["code_focus"]
    assert "Q-learning uses the observed reward" in payload["explanation"]["why_correct"]
    assert payload["explanation"]["table_focus"] == "row 0, column 1"


def test_q_learning_respects_episode_step_limit(monkeypatch):
    lesson_actions: list[int] = []

    class FakeActionSpace:
        n = 2

        def sample(self):
            return 0

    class FakeEnv:
        observation_space = SimpleNamespace(n=2)
        action_space = FakeActionSpace()

        @property
        def unwrapped(self):
            return self

    class FakeAdapter:
        env = FakeEnv()

        def reset(self, seed=None):
            del seed
            return 0, {}

        def step(self, action):
            return 0, -1.0, False, False, {"p": 1.0, "action": action}

        def capture_frame_png(self, prefix="step", state=None):
            del prefix, state
            return ""

        def action_label(self, action):
            return f"Action {action}"

    class FakeLogger:
        def __init__(self):
            self.steps = []

        def log_step(self, payload):
            self.steps.append(payload)

        def end_episode(self):
            self.ended = True

    def fake_choose(self, q_row, epsilon):
        del self, q_row, epsilon
        return 0

    def lesson_function(Q, state, action, reward, next_state, alpha, gamma):
        del Q, state, reward, next_state, alpha, gamma
        lesson_actions.append(action)

    monkeypatch.setattr(RLEngine, "_choose_epsilon_greedy_action", fake_choose)

    logger = FakeLogger()
    rl_engine = RLEngine(FakeAdapter(), logger)
    rl_engine._run_q_learning(
        lesson_function,
        num_episodes=1,
        hyperparameters={
            "alpha": 0.1,
            "gamma": 0.95,
            "epsilon": 0.2,
            "max_steps_per_episode": 3,
        },
    )

    assert lesson_actions == [0, 0, 0]
    assert len(logger.steps) == 3


def test_sarsa_emits_sampled_bootstrap_q_table_schema(monkeypatch):
    selected_actions = iter([0, 1, 0])

    class FakeActionSpace:
        n = 2

        def sample(self):
            return 0

    class FakeEnv:
        observation_space = SimpleNamespace(n=2)
        action_space = FakeActionSpace()

        @property
        def unwrapped(self):
            return self

    class FakeAdapter:
        env = FakeEnv()

        def __init__(self):
            self.calls = 0

        def reset(self, seed=None):
            del seed
            return 0, {}

        def step(self, action):
            self.calls += 1
            if self.calls == 1:
                return 1, -1.0, False, False, {"p": 1.0, "action": action}
            return 1, 0.0, True, False, {"p": 1.0, "action": action}

        def capture_frame_png(self, prefix="step", state=None):
            del prefix, state
            return ""

        def action_label(self, action):
            return f"Action {action}"

    class FakeLogger:
        def __init__(self):
            self.steps = []

        def log_step(self, payload):
            self.steps.append(payload)

        def end_episode(self):
            self.ended = True

    def fake_choose(self, q_row, epsilon):
        del self, q_row, epsilon
        return next(selected_actions)

    def lesson_function(Q, state, action, reward, next_state, next_action, alpha, gamma):
        del reward, next_state, next_action, alpha, gamma
        Q[state][action] = -0.1
        return Q

    monkeypatch.setattr(RLEngine, "_choose_epsilon_greedy_action", fake_choose)

    rl_engine = RLEngine(FakeAdapter(), FakeLogger())
    rl_engine._run_sarsa(
        lesson_function,
        num_episodes=1,
        hyperparameters={"alpha": 0.1, "gamma": 0.95, "epsilon": 0.2},
    )

    payload = rl_engine.logger.steps[0]
    assert payload["trace_schema_version"] == 2
    assert payload["equation_update"]["kind"] == "sarsa"
    assert payload["equation_update"]["bootstrap_label"] == "Q(1,1)"
    assert payload["tables"]["active_cell"] == {"row": 0, "column": 0}
    assert payload["tables"]["bootstrap_cell"] == {"row": 1, "column": 1}
    assert payload["tables"]["changed_cells"] == [{"row": 0, "column": 0}]
    assert payload["tables"]["after"][0][0] == -0.1
    assert "SARSA uses the observed reward" in payload["explanation"]["why_correct"]
    assert payload["explanation"]["table_focus"] == "row 0, column 0"


def test_dynamic_programming_steps_emit_structured_backup_schema():
    class FakeActionSpace:
        n = 2

    class FakeEnv:
        observation_space = SimpleNamespace(n=2)
        action_space = FakeActionSpace()

        @property
        def unwrapped(self):
            return self

    class FakeAdapter:
        env = FakeEnv()

        def reset(self, seed=None):
            del seed
            return 0, {}

        def transition_details(self, state, action):
            if state == 0 and action == 0:
                return [
                    {
                        "probability": 1.0,
                        "next_state": 1,
                        "reward": 1.0,
                        "done": False,
                    }
                ]
            return [
                {
                    "probability": 1.0,
                    "next_state": state,
                    "reward": 0.0,
                    "done": True,
                }
            ]

        def capture_frame_png(self, prefix="step", state=None):
            del prefix, state
            return ""

        def action_label(self, action):
            return ["Left", "Right"][action]

    class FakeLogger:
        def __init__(self):
            self.steps = []

        def log_step(self, payload):
            self.steps.append(payload)

        def end_episode(self):
            self.ended = True

    def value_iteration(values, env, gamma):
        del env, gamma
        values[0] = 1.9
        values[1] = 1.0

    logger = FakeLogger()
    rl_engine = RLEngine(FakeAdapter(), logger)
    rl_engine._run_value_iteration(
        value_iteration,
        hyperparameters={"gamma": 0.9},
    )

    payload = logger.steps[0]
    assert payload["trace_schema_version"] == 2
    assert payload["tables"]["kind"] == "value_table"
    assert payload["tables"]["active_cell"] == {"row": 0, "column": 0}
    assert payload["equation_update"]["kind"] == "value_iteration"
    assert payload["equation_update"]["dp_details"]["selected_action"] == 0
    assert payload["equation_update"]["dp_details"]["backup_value"] == 1.9
    first_backup = payload["equation_update"]["dp_details"]["action_backups"][0]
    assert first_backup["action_label"] == "Left"
    assert first_backup["expected_return"] == 1.9
    assert first_backup["transition_terms"][0]["next_state"] == 1
    assert first_backup["transition_terms"][0]["contribution"] == 1.9
    assert "largest Bellman backup" in payload["explanation"]["why_correct"]
    assert payload["explanation"]["table_focus"] == "row 0, column 0"


def test_policy_improvement_steps_emit_policy_before_after_schema(monkeypatch):
    class FakeActionSpace:
        n = 2

    class FakeEnv:
        observation_space = SimpleNamespace(n=2)
        action_space = FakeActionSpace()

        @property
        def unwrapped(self):
            return self

    class FakeAdapter:
        env = FakeEnv()

        def reset(self, seed=None):
            del seed
            return 0, {}

        def transition_details(self, state, action):
            return [
                {
                    "probability": 1.0,
                    "next_state": state,
                    "reward": float(action),
                    "done": False,
                }
            ]

        def capture_frame_png(self, prefix="step", state=None):
            del prefix, state
            return ""

        def action_label(self, action):
            return ["Left", "Right"][action]

    class FakeLogger:
        def __init__(self):
            self.steps = []

        def log_step(self, payload):
            self.steps.append(payload)

        def end_episode(self):
            self.ended = True

    def fake_values(self):
        del self
        return [0.2, 0.4]

    def policy_improvement(values, env, gamma):
        del values, env, gamma
        return [[0.0, 1.0], [1.0, 0.0]]

    monkeypatch.setattr(
        RLEngine,
        "_build_policy_improvement_values",
        fake_values,
    )

    logger = FakeLogger()
    rl_engine = RLEngine(FakeAdapter(), logger)
    rl_engine._run_policy_improvement(
        policy_improvement,
        hyperparameters={"gamma": 0.9},
    )

    payload = logger.steps[0]
    assert payload["trace_schema_version"] == 2
    assert payload["tables"]["kind"] == "policy_table"
    assert payload["tables"]["before"][0] == [0.5, 0.5]
    assert payload["tables"]["after"][0] == [0.0, 1.0]
    assert payload["tables"]["active_cell"] == {"row": 0, "column": 1}
    details = payload["equation_update"]["dp_details"]
    assert details["selected_action_label"] == "Right"
    assert details["policy_row_before"] == [0.5, 0.5]
    assert details["policy_row_after"] == [0.0, 1.0]
    assert details["value_source"] == [[0.2], [0.4]]
    assert "greedy action" in payload["explanation"]["why_correct"]
    assert payload["explanation"]["table_focus"] == "row 0, column 1"


def test_monte_carlo_emits_blackjack_observation_and_return_ladder():
    class FakeActionSpace:
        def __init__(self):
            self.actions = iter([1, 0])

        def sample(self):
            return next(self.actions)

    class FakeEnv:
        action_space = FakeActionSpace()

    class FakeAdapter:
        env = FakeEnv()

        def __init__(self):
            self.calls = 0

        def reset(self, seed=None):
            del seed
            return (15, 10, False), {}

        def step(self, action):
            self.calls += 1
            if self.calls == 1:
                return (20, 10, False), 0.0, False, False, {"p": 1.0, "action": action}
            return (20, 10, False), 1.0, True, False, {"p": 1.0, "action": action}

        def capture_frame_png(self, prefix="step", state=None):
            del prefix, state
            return ""

        def action_label(self, action):
            return ["Stand", "Hit"][action]

    class FakeLogger:
        def __init__(self):
            self.steps = []

        def log_step(self, payload):
            self.steps.append(payload)

        def end_episode(self):
            self.ended = True

    def first_visit_mc(episode_trace, values, returns, gamma):
        visited = set()
        for index, (state, _action, _reward) in enumerate(episode_trace):
            if state in visited:
                continue
            visited.add(state)
            total = 0.0
            discount = 1.0
            for _state, _action, reward in episode_trace[index:]:
                total += discount * reward
                discount *= gamma
            returns.setdefault(state, []).append(total)
            values[state] = sum(returns[state]) / len(returns[state])

    logger = FakeLogger()
    rl_engine = RLEngine(FakeAdapter(), logger)
    rl_engine._run_mc_first_visit(
        first_visit_mc,
        num_episodes=1,
        hyperparameters={"gamma": 0.9},
    )

    sample_payload = logger.steps[0]
    assert sample_payload["trace_schema_version"] == 2
    sample_details = sample_payload["equation_update"]["mc_details"]
    assert sample_payload["equation_update"]["kind"] == "mc_sampling"
    assert "No value changes during sampling" in sample_payload["explanation"]["why_correct"]
    assert sample_details["observation"] == {
        "player_sum": 15,
        "dealer_card": 10,
        "usable_ace": False,
    }
    assert sample_details["next_observation"]["player_sum"] == 20
    assert sample_details["episode_strip"][0]["action_label"] == "Hit"

    return_payload = next(
        step
        for step in logger.steps
        if step.get("equation_update", {}).get("kind") == "mc_first_visit"
    )
    return_details = return_payload["equation_update"]["mc_details"]
    assert return_details["first_visit"] is True
    assert return_details["return_value"] == 0.9
    assert return_details["return_terms"][0]["discounted_reward"] == 0.0
    assert return_details["return_terms"][1]["discounted_reward"] == 0.9
    assert return_details["returns_history"] == [0.9]
    assert return_payload["tables"]["kind"] == "returns_table"
    assert "First-visit Monte Carlo" in return_payload["explanation"]["why_correct"]
    assert return_payload["explanation"]["table_focus"] == "row 0, column 0"


def test_monte_carlo_runtime_accepts_returned_value_table_style():
    class FakeActionSpace:
        def __init__(self):
            self.actions = iter([1, 0])

        def sample(self):
            return next(self.actions)

    class FakeEnv:
        action_space = FakeActionSpace()

    class FakeAdapter:
        env = FakeEnv()

        def __init__(self):
            self.calls = 0

        def reset(self, seed=None):
            del seed
            return (15, 10, False), {}

        def step(self, action):
            self.calls += 1
            if self.calls == 1:
                return (20, 10, False), 0.0, False, False, {"p": 1.0, "action": action}
            return (20, 10, False), 1.0, True, False, {"p": 1.0, "action": action}

        def capture_frame_png(self, prefix="step", state=None):
            del prefix, state
            return ""

        def action_label(self, action):
            return ["Stand", "Hit"][action]

    class FakeLogger:
        def __init__(self):
            self.steps = []

        def log_step(self, payload):
            self.steps.append(payload)

        def end_episode(self):
            self.ended = True

    def returned_value_table_mc(episode_trace, values, returns, gamma):
        del returns
        new_values = dict(values)
        visited = set()
        for index, (state, _action, _reward) in enumerate(episode_trace):
            if state in visited:
                continue
            visited.add(state)
            total = 0.0
            discount = 1.0
            for _state, _action, reward in episode_trace[index:]:
                total += discount * reward
                discount *= gamma
            new_values[state] = total
        return new_values

    logger = FakeLogger()
    rl_engine = RLEngine(FakeAdapter(), logger)
    rl_engine._run_mc_first_visit(
        returned_value_table_mc,
        num_episodes=1,
        hyperparameters={"gamma": 0.9},
    )

    return_payload = next(
        step
        for step in logger.steps
        if step.get("equation_update", {}).get("kind") == "mc_first_visit"
    )
    assert return_payload["updated_values"]["V((15, 10, False))"] == 0.9
    assert return_payload["equation_update"]["mc_details"]["returns_history"] == [0.9]


def test_taxi_adapter_creates_taxi_v3(monkeypatch):
    created_env_ids: list[str] = []

    def fake_make(env_id, **kwargs):
        del kwargs
        created_env_ids.append(env_id)
        return SimpleNamespace()

    monkeypatch.setattr(engine_module.gym, "make", fake_make)

    EnvironmentAdapter("Taxi")

    assert created_env_ids == ["Taxi-v3"]


def test_taxi_action_labels():
    adapter = EnvironmentAdapter.__new__(EnvironmentAdapter)
    adapter.env_name = "Taxi"

    assert adapter.action_label(0) == "South"
    assert adapter.action_label(1) == "North"
    assert adapter.action_label(2) == "East"
    assert adapter.action_label(3) == "West"
    assert adapter.action_label(4) == "Pickup"
    assert adapter.action_label(5) == "Dropoff"


def test_taxi_grid_metadata_decodes_state():
    adapter = EnvironmentAdapter.__new__(EnvironmentAdapter)
    adapter.env_name = "Taxi"
    adapter.env = SimpleNamespace(unwrapped=SimpleNamespace())

    state = 16
    row, col, pass_idx, dest_idx = adapter._decode_taxi(state)
    assert (row, col) == (0, 0)
    assert pass_idx == 4
    assert dest_idx == 0

    metadata = adapter.grid_metadata(
        state=state,
        next_state=None,
        action=5,
        reward=20.0,
        terminated=True,
        truncated=False,
    )

    assert metadata["environment"] == "Taxi"
    assert metadata["rows"] == 5
    assert metadata["columns"] == 5
    assert len(metadata["cells"]) == 25
    assert metadata["state_coordinates"] == {"row": 0, "column": 0}
    assert metadata["encoded_state"] == 16
    assert metadata["action_label"] == "Dropoff"
    assert metadata["reward"] == 20.0
    assert metadata["terminated"] is True

    assert metadata["passenger"]["in_taxi"] is True
    assert metadata["destination"]["label"] == "R"
    assert metadata["destination"]["row"] == 0
    assert metadata["destination"]["column"] == 0

    loc_cells = [c for c in metadata["cells"] if c["tile_type"] != "F"]
    loc_labels = {c["tile_type"] for c in loc_cells}
    assert loc_labels == {"R", "G", "Y", "B"}


def test_taxi_grid_metadata_shows_passenger_at_pickup_location():
    adapter = EnvironmentAdapter.__new__(EnvironmentAdapter)
    adapter.env_name = "Taxi"
    adapter.env = SimpleNamespace(unwrapped=SimpleNamespace())

    state = 0 * 100 + 0 * 20 + 0 * 4 + 0
    metadata = adapter.grid_metadata(state=state, next_state=None, action=None)

    assert metadata["passenger"]["in_taxi"] is False
    assert metadata["passenger"]["location"] == "R"
    assert metadata["passenger"]["row"] == 0
    assert metadata["passenger"]["column"] == 0


def test_taxi_q_learning_produces_correct_trace_schema(monkeypatch):
    class FakeActionSpace:
        n = 6

        def sample(self):
            return 0

    class FakeEnv:
        observation_space = SimpleNamespace(n=500)
        action_space = FakeActionSpace()

        @property
        def unwrapped(self):
            return self

    class FakeAdapter:
        env = FakeEnv()
        env_name = "Taxi"

        def reset(self, seed=None):
            del seed
            return 328, {}

        def step(self, action):
            return 428, -1.0, False, False, {"p": 1.0}

        def capture_frame_png(self, prefix="step", state=None):
            del prefix, state
            return ""

        def action_label(self, action):
            labels = {0: "South", 1: "North", 2: "East", 3: "West",
                      4: "Pickup", 5: "Dropoff"}
            return labels.get(action, f"Action {action}")

        def grid_metadata(self, **kwargs):
            return {"environment": "Taxi", "rows": 5, "columns": 5,
                    "cells": [], "state": 0, "next_state": 0}

    class FakeLogger:
        def log_step(self, payload):
            self.payload = payload

        def end_episode(self):
            self.ended = True

    def fake_choose(self, q_row, epsilon):
        del self, q_row, epsilon
        return 0

    def lesson_function(Q, state, action, reward, next_state, alpha, gamma):
        Q[state][action] = Q[state][action] + alpha * (
            reward + gamma * max(Q[next_state]) - Q[state][action]
        )
        return Q

    monkeypatch.setattr(RLEngine, "_choose_epsilon_greedy_action", fake_choose)

    rl_engine = RLEngine(FakeAdapter(), FakeLogger())
    rl_engine._run_q_learning(
        lesson_function,
        num_episodes=1,
        hyperparameters={
            "alpha": 0.1,
            "gamma": 0.95,
            "epsilon": 0.2,
            "max_steps_per_episode": 1,
        },
    )

    payload = rl_engine.logger.payload
    assert payload["trace_schema_version"] == 2
    assert payload["equation_update"]["kind"] == "q_learning"
    assert payload["tables"]["kind"] == "q_table"
    assert len(payload["tables"]["action_labels"]) == 6
    assert payload["tables"]["action_labels"][4] == "Pickup"
    assert payload["tables"]["action_labels"][5] == "Dropoff"
