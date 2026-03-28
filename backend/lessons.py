from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(frozen=True)
class LessonDefinition:
    id: str
    title: str
    description: str
    category: str
    required_function: str
    environment_name: str
    starter_code: str


LESSON_DEFINITIONS = {
    "dp_policy_eval": LessonDefinition(
        id="dp_policy_eval",
        title="Dynamic Programming: Policy Evaluation",
        description="Evaluate a policy over FrozenLake using Bellman expectation updates.",
        category="Dynamic Programming",
        required_function="policy_evaluation",
        environment_name="FrozenLake",
        starter_code="""
DISCOUNT_FACTOR = 0.95

def policy_evaluation(V, policy, env, gamma=DISCOUNT_FACTOR, theta=1e-8):
    delta = float("inf")
    while delta > theta:
        delta = 0.0
        for state in range(len(V)):
            old_value = V[state]
            new_value = 0.0
            for action, action_prob in enumerate(policy[state]):
                for transition_prob, next_state, reward, done in env.P[state][action]:
                    future = 0.0 if done else V[next_state]
                    new_value += action_prob * transition_prob * (reward + gamma * future)
            V[state] = new_value
            delta = max(delta, abs(old_value - new_value))
    return V
""".strip(),
    ),
    "dp_value_iteration": LessonDefinition(
        id="dp_value_iteration",
        title="Dynamic Programming: Value Iteration",
        description="Compute optimal FrozenLake state values with Bellman optimality backups.",
        category="Dynamic Programming",
        required_function="value_iteration",
        environment_name="FrozenLake",
        starter_code="""
DISCOUNT_FACTOR = 0.95

def value_iteration(V, env, gamma=DISCOUNT_FACTOR, theta=1e-8):
    delta = float("inf")
    action_count = env.action_space.n
    while delta > theta:
        delta = 0.0
        for state in range(len(V)):
            old_value = V[state]
            action_values = []
            for action in range(action_count):
                action_value = 0.0
                for transition_prob, next_state, reward, done in env.P[state][action]:
                    future = 0.0 if done else V[next_state]
                    action_value += transition_prob * (reward + gamma * future)
                action_values.append(action_value)
            V[state] = max(action_values)
            delta = max(delta, abs(old_value - V[state]))
    return V
""".strip(),
    ),
    "mc_first_visit": LessonDefinition(
        id="mc_first_visit",
        title="Monte Carlo: First-Visit Prediction",
        description="Estimate FrozenLake state values from complete episodes and first-visit returns.",
        category="Monte Carlo Methods",
        required_function="mc_first_visit_prediction",
        environment_name="FrozenLake",
        starter_code="""
DISCOUNT_FACTOR = 0.95
EPISODE_COUNT = 6

def mc_first_visit_prediction(episode, V, returns, gamma=DISCOUNT_FACTOR):
    visited_states = set()
    for index, (state, _action, _reward) in enumerate(episode):
        if state in visited_states:
            continue
        visited_states.add(state)
        G = 0.0
        discount = 1.0
        for _next_state, _next_action, reward in episode[index:]:
            G += discount * reward
            discount *= gamma
        returns[state].append(G)
        V[state] = sum(returns[state]) / len(returns[state])
    return V
""".strip(),
    ),
    "td_q_learning": LessonDefinition(
        id="td_q_learning",
        title="Temporal Difference: Q-Learning",
        description="Update FrozenLake action values from one-step TD targets and epsilon-greedy samples.",
        category="Temporal Difference",
        required_function="q_learning_update",
        environment_name="FrozenLake",
        starter_code="""
LEARNING_RATE = 0.10
DISCOUNT_FACTOR = 0.95
EXPLORATION_RATE = 0.20
EPISODE_COUNT = 6

def q_learning_update(Q, state, action, reward, next_state, alpha=LEARNING_RATE, gamma=DISCOUNT_FACTOR):
    best_next_value = max(Q[next_state])
    td_target = reward + gamma * best_next_value
    Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])
    return Q
""".strip(),
    ),
}


def get_lesson_definition(lesson_id: str) -> Optional[LessonDefinition]:
    return LESSON_DEFINITIONS.get(lesson_id)


def list_lesson_definitions() -> list[LessonDefinition]:
    return list(LESSON_DEFINITIONS.values())


def serialize_lesson(lesson: LessonDefinition) -> dict:
    return asdict(lesson)
