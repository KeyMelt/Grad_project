"""Backend lesson registry.

Each lesson definition is both a learner-facing template contract and a backend
execution contract. Keep this file aligned with `lesson_tests.py`, the Flutter
lesson catalog, and the visualization assets that explain each algorithm.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass(frozen=True)
class TemplateBlank:
    blank_id: str
    kind: str
    prompt: str
    expected_concept: str
    approx_line_anchor: int


@dataclass(frozen=True)
class LessonDefinition:
    id: str
    title: str
    description: str
    category: str
    required_function: str
    environment_name: str
    starter_code: str
    template_kind: str = "guided_fill_in"
    template_blanks: list[TemplateBlank] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)


LESSON_DEFINITIONS = {
    "dp_policy_eval": LessonDefinition(
        id="dp_policy_eval",
        title="Dynamic Programming: Policy Evaluation",
        description="Evaluate a fixed policy over FrozenLake using Bellman expectation backups and iterative sweeps.",
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
                # TODO(student): combine model branches into the expectation for this action.
                raise NotImplementedError("TODO: policy_eval_expectation")
            V[state] = new_value
            delta = max(delta, abs(old_value - __BLANK_policy_eval_delta__))
    return V
""".strip(),
        template_blanks=[
            TemplateBlank(
                blank_id="policy_eval_expectation",
                kind="block",
                prompt="Accumulate each action branch into the Bellman expectation update.",
                expected_concept="Bellman expectation backup",
                approx_line_anchor=11,
            ),
            TemplateBlank(
                blank_id="policy_eval_delta",
                kind="expression",
                prompt="Compare the previous value against the newly computed value in the convergence check.",
                expected_concept="sweep convergence",
                approx_line_anchor=13,
            ),
        ],
        success_criteria=[
            "The function computes the Bellman expectation update for every policy-weighted action branch.",
            "The convergence check uses the previous and updated state values.",
            "The function returns a value table that passes the sample lesson tests.",
        ],
    ),
    "dp_value_iteration": LessonDefinition(
        id="dp_value_iteration",
        title="Dynamic Programming: Value Iteration",
        description="Compute optimal FrozenLake state values by repeatedly taking the best Bellman backup at each state.",
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
                # TODO(student): back up one action value from transition branches.
                raise NotImplementedError("TODO: value_iteration_backup")
                action_values.append(action_value)
            V[state] = __BLANK_value_iteration_best_action__
            delta = max(delta, abs(old_value - V[state]))
    return V
""".strip(),
        template_blanks=[
            TemplateBlank(
                blank_id="value_iteration_backup",
                kind="block",
                prompt="Compute one action backup from transition probabilities, rewards, and discounted future values.",
                expected_concept="Bellman optimality backup",
                approx_line_anchor=12,
            ),
            TemplateBlank(
                blank_id="value_iteration_best_action",
                kind="expression",
                prompt="Select the best action value for the current state.",
                expected_concept="greedy max backup",
                approx_line_anchor=14,
            ),
        ],
        success_criteria=[
            "Each action value is computed from all transition branches for that action.",
            "The state value is updated with the maximum action value.",
            "The returned value table passes the sample optimal-backup lesson test.",
        ],
    ),
    "dp_policy_improvement": LessonDefinition(
        id="dp_policy_improvement",
        title="Dynamic Programming: Policy Improvement",
        description="Turn a FrozenLake state-value table into a greedy policy by backing up each available action.",
        category="Dynamic Programming",
        required_function="policy_improvement",
        environment_name="FrozenLake",
        starter_code="""
DISCOUNT_FACTOR = 0.95

def policy_improvement(V, env, gamma=DISCOUNT_FACTOR):
    action_count = env.action_space.n
    policy = [[0.0 for _ in range(action_count)] for _ in range(len(V))]

    for state in range(len(V)):
        action_values = []
        for action in range(action_count):
            action_value = 0.0
            # TODO(student): compute the one-step lookahead return for this action.
            raise NotImplementedError("TODO: policy_improvement_backup")
            action_values.append(action_value)

        best_action = __BLANK_policy_improvement_best_action__
        policy[state][best_action] = 1.0

    return policy
""".strip(),
        template_blanks=[
            TemplateBlank(
                blank_id="policy_improvement_backup",
                kind="block",
                prompt="Compute each action's one-step lookahead return from the value table.",
                expected_concept="greedy policy backup",
                approx_line_anchor=11,
            ),
            TemplateBlank(
                blank_id="policy_improvement_best_action",
                kind="expression",
                prompt="Choose the greedy action index from the action values list.",
                expected_concept="argmax policy improvement",
                approx_line_anchor=14,
            ),
        ],
        success_criteria=[
            "Each action score is computed from transition probabilities, rewards, and discounted future values.",
            "The selected action index is the greedy argmax over the action scores.",
            "Each output policy row remains one-hot and passes the sample lesson test.",
        ],
    ),
    "mc_first_visit": LessonDefinition(
        id="mc_first_visit",
        title="Monte Carlo: First-Visit Prediction",
        description="Estimate Blackjack state values from complete episodes and first-visit returns.",
        category="Monte Carlo Methods",
        required_function="mc_first_visit_prediction",
        environment_name="Blackjack",
        starter_code="""
DISCOUNT_FACTOR = 0.95
EPISODE_COUNT = 6

def mc_first_visit_prediction(episode, V, returns, gamma=DISCOUNT_FACTOR):
    visited_states = set()
    for index, (state, _action, _reward) in enumerate(episode):
        if __BLANK_mc_first_visit_seen_state__:
            continue
        visited_states.add(state)
        G = 0.0
        discount = 1.0
        # TODO(student): roll the discounted return forward from the first visit.
        raise NotImplementedError("TODO: mc_first_visit_return")
        returns.setdefault(state, []).append(G)
        V[state] = sum(returns[state]) / len(returns[state])
    return V
""".strip(),
        template_blanks=[
            TemplateBlank(
                blank_id="mc_first_visit_seen_state",
                kind="expression",
                prompt="Skip repeated states after their first occurrence in the episode.",
                expected_concept="first-visit filtering",
                approx_line_anchor=7,
            ),
            TemplateBlank(
                blank_id="mc_first_visit_return",
                kind="block",
                prompt="Compute the discounted return from the first-visit index to the end of the episode.",
                expected_concept="Monte Carlo return accumulation",
                approx_line_anchor=11,
            ),
        ],
        success_criteria=[
            "Repeated states are skipped after the first occurrence in the episode.",
            "The discounted return is accumulated from the first-visit index onward.",
            "The value table update passes the sample first-visit Monte Carlo test.",
        ],
    ),
    "td_q_learning": LessonDefinition(
        id="td_q_learning",
        title="Temporal Difference: Q-Learning",
        description="Update CliffWalking action values from one-step TD targets and epsilon-greedy samples.",
        category="Temporal Difference",
        required_function="q_learning_update",
        environment_name="CliffWalking",
        starter_code="""
LEARNING_RATE = 0.10
DISCOUNT_FACTOR = 0.95
EXPLORATION_RATE = 0.20
EPISODE_COUNT = 6

def q_learning_update(Q, state, action, reward, next_state, alpha=LEARNING_RATE, gamma=DISCOUNT_FACTOR):
    best_next_value = __BLANK_q_learning_best_next__
    td_target = reward + gamma * best_next_value
    # TODO(student): apply the one-step TD update to the chosen Q-value.
    raise NotImplementedError("TODO: q_learning_update_rule")
    return Q
""".strip(),
        template_blanks=[
            TemplateBlank(
                blank_id="q_learning_best_next",
                kind="expression",
                prompt="Select the greedy bootstrap value from the next-state row of Q.",
                expected_concept="max next-state bootstrap",
                approx_line_anchor=7,
            ),
            TemplateBlank(
                blank_id="q_learning_update_rule",
                kind="block",
                prompt="Apply the incremental Q-learning update using alpha and the TD target.",
                expected_concept="one-step TD update",
                approx_line_anchor=9,
            ),
        ],
        success_criteria=[
            "The bootstrap term uses the maximum next-state action value.",
            "The chosen Q-value is updated incrementally toward the TD target.",
            "The function returns the updated Q-table and passes the sample lesson test.",
        ],
    ),
    "td_sarsa": LessonDefinition(
        id="td_sarsa",
        title="Temporal Difference: SARSA",
        description="Update CliffWalking action values with on-policy TD targets that use the next sampled action.",
        category="Temporal Difference",
        required_function="sarsa_update",
        environment_name="CliffWalking",
        starter_code="""
LEARNING_RATE = 0.10
DISCOUNT_FACTOR = 0.95
EXPLORATION_RATE = 0.20
EPISODE_COUNT = 6

def sarsa_update(
    Q,
    state,
    action,
    reward,
    next_state,
    next_action,
    alpha=LEARNING_RATE,
    gamma=DISCOUNT_FACTOR,
):
    bootstrap = __BLANK_sarsa_bootstrap__
    td_target = reward + gamma * bootstrap
    # TODO(student): apply the on-policy SARSA update to the selected Q-value.
    raise NotImplementedError("TODO: sarsa_update_rule")
    return Q
""".strip(),
        template_blanks=[
            TemplateBlank(
                blank_id="sarsa_bootstrap",
                kind="expression",
                prompt="Use the sampled next action for the bootstrap, with zero on terminal transitions.",
                expected_concept="on-policy bootstrap",
                approx_line_anchor=13,
            ),
            TemplateBlank(
                blank_id="sarsa_update_rule",
                kind="block",
                prompt="Apply the incremental SARSA update using the TD target.",
                expected_concept="SARSA TD update",
                approx_line_anchor=15,
            ),
        ],
        success_criteria=[
            "The bootstrap term uses the sampled next action, not a max over the row.",
            "Terminal transitions use a zero bootstrap.",
            "The updated Q-table passes the sample SARSA lesson test.",
        ],
    ),
}


def get_lesson_definition(lesson_id: str) -> Optional[LessonDefinition]:
    return LESSON_DEFINITIONS.get(lesson_id)


def list_lesson_definitions() -> list[LessonDefinition]:
    return list(LESSON_DEFINITIONS.values())


def serialize_lesson(lesson: LessonDefinition) -> dict:
    return asdict(lesson)
