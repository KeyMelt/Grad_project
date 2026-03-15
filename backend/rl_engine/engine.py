import gymnasium as gym
from typing import Dict, Any

from backend.lessons import get_lesson_definition
from backend.user_code import load_user_function

class EnvironmentAdapter:
    """Manages the instantiation and interfacing with Gymnasium environments."""
    
    def __init__(self, env_name: str):
        self.env_name = env_name
        self.env = self._create_env()

    def _create_env(self):
        if self.env_name == "FrozenLake":
            # Using 4x4 GridWorld 
            return gym.make('FrozenLake-v1', desc=None, map_name="4x4", is_slippery=False)
        else:
            raise ValueError(f"Environment {self.env_name} is not currently supported.")

    def reset(self):
        return self.env.reset()

    def step(self, action):
        return self.env.step(action)

    def close(self):
        self.env.close()

class RLEngine:
    """Core engine to run RL simulations."""
    
    def __init__(self, adapter: EnvironmentAdapter, logger):
        self.adapter = adapter
        self.logger = logger
        
    def run_episodes(self, lesson_id: str, code_module_str: str, num_episodes: int, hyperparameters: Dict[str, float]):
        """Runs the RL loop with the injected code snippet."""
        self.logger.clear()
        lesson = get_lesson_definition(lesson_id)
        if lesson is None:
            raise ValueError(f"Unsupported lesson '{lesson_id}'.")

        lesson_function = load_user_function(code_module_str, lesson.required_function)

        if lesson_id == "dp_policy_eval":
            self._run_policy_evaluation(lesson_function, num_episodes, hyperparameters)
        elif lesson_id == "mc_first_visit":
            self._run_mc_first_visit(lesson_function, num_episodes, hyperparameters)
        elif lesson_id == "td_q_learning":
            self._run_q_learning(lesson_function, num_episodes, hyperparameters)
        else:
            raise ValueError(f"Lesson '{lesson_id}' is not implemented.")

    def _run_policy_evaluation(self, lesson_function, num_episodes: int, hyperparameters: Dict[str, float]):
        state_count = self.adapter.env.observation_space.n
        action_count = self.adapter.env.action_space.n
        values = [0.0 for _ in range(state_count)]
        policy = [[1.0 / action_count for _ in range(action_count)] for _ in range(state_count)]

        lesson_function(values, policy, self.adapter.env.unwrapped, hyperparameters["gamma"])

        for _ in range(num_episodes):
            state, _ = self.adapter.reset()
            done = False

            while not done:
                action = self.adapter.env.action_space.sample()
                next_state, reward, terminated, truncated, _ = self.adapter.step(action)
                self.logger.log_step(
                    {
                        "state": state,
                        "action": action,
                        "reward": reward,
                        "next_state": next_state,
                        "updated_values": {f"V({state})": round(values[state], 4)},
                    }
                )
                state = next_state
                done = terminated or truncated

            self.logger.end_episode()

    def _run_mc_first_visit(self, lesson_function, num_episodes: int, hyperparameters: Dict[str, float]):
        state_count = self.adapter.env.observation_space.n
        values = [0.0 for _ in range(state_count)]
        returns = {state: [] for state in range(state_count)}

        for _ in range(num_episodes):
            state, _ = self.adapter.reset()
            done = False
            episode_trace = []

            while not done:
                action = self.adapter.env.action_space.sample()
                next_state, reward, terminated, truncated, _ = self.adapter.step(action)
                episode_trace.append((state, action, reward))
                self.logger.log_step(
                    {
                        "state": state,
                        "action": action,
                        "reward": reward,
                        "next_state": next_state,
                        "updated_values": {f"V({state})": round(values[state], 4)},
                    }
                )
                state = next_state
                done = terminated or truncated

            lesson_function(episode_trace, values, returns, hyperparameters["gamma"])
            self.logger.end_episode()

    def _run_q_learning(self, lesson_function, num_episodes: int, hyperparameters: Dict[str, float]):
        state_count = self.adapter.env.observation_space.n
        action_count = self.adapter.env.action_space.n
        q_table = [[0.0 for _ in range(action_count)] for _ in range(state_count)]

        for _ in range(num_episodes):
            state, _ = self.adapter.reset()
            done = False

            while not done:
                action = self.adapter.env.action_space.sample()
                next_state, reward, terminated, truncated, _ = self.adapter.step(action)
                lesson_function(
                    q_table,
                    state,
                    action,
                    reward,
                    next_state,
                    hyperparameters["alpha"],
                    hyperparameters["gamma"],
                )
                self.logger.log_step(
                    {
                        "state": state,
                        "action": action,
                        "reward": reward,
                        "next_state": next_state,
                        "updated_values": {
                            f"Q({state}, {action})": round(q_table[state][action], 4)
                        },
                    }
                )
                state = next_state
                done = terminated or truncated

            self.logger.end_episode()
