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


def test_q_learning_respects_episode_step_limit(monkeypatch):
    lesson_actions: list[int] = []

    class FakeActionSpace:
        n = 2

        def sample(self):
            return 0

    class FakeEnv:
        observation_space = SimpleNamespace(n=2)
        action_space = FakeActionSpace()

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
