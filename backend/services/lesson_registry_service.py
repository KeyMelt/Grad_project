"""DB-backed lesson registry.

All lessons — the nine built-in RL curriculum lessons and any
instructor-authored additions — live in the AuthoredLesson table.
This service is the single source of truth for lesson definitions.

On first startup it seeds the nine core lessons so the system works
out-of-the-box without manual data entry.  Subsequent restarts skip
seeding if the rows already exist.
"""

from __future__ import annotations

import json
from threading import Lock
from typing import Any

from sqlmodel import select

from backend.models.authored_lesson import AuthoredLesson
from backend.models.lesson import LessonDefinition, TemplateBlank
from backend.persistence import Database

# ---------------------------------------------------------------------------
# Core lesson seed data
# Each entry is the canonical full payload stored in payload_json.
# Fields mirror LessonDefinition plus the presentation/exercise metadata
# previously split across PRESENTATION_METADATA in lesson_catalog_service.
# ---------------------------------------------------------------------------

_CORE_LESSONS: list[dict[str, Any]] = [
    {
        "id": "rl_mdp_core",
        "title": "MDP Foundations",
        "description": "Build the prerequisite mental model for reinforcement learning: states, actions, rewards, transitions, returns, and discounting.",
        "category": "Foundations",
        "required_function": "",
        "environment_name": "",
        "env_params": {},
        "template_kind": "reading_only",
        "backend_enabled": False,
        "starter_code": "",
        "template_blanks": [],
        "success_criteria": [
            "Explain the agent-environment loop in terms of state, action, reward, and next state.",
            "Distinguish immediate reward from long-run return.",
            "Describe how discounting changes the weight of future rewards.",
        ],
        "concept_video": {
            "stream_path": "/media/concept-videos/rl_mdp_core_concept.mp4",
            "caption_path": "/media/concept-videos/rl_mdp_core_captions.vtt",
            "duration_label": "Concept video",
            "summary": "A prerequisite overview of Markov decision processes and the agent-environment loop used throughout the course.",
            "highlights": [
                "How observations, actions, rewards, and next states form an RL timestep.",
                "Why transition dynamics make the next state uncertain.",
                "How return and discounting connect immediate rewards to long-run goals.",
            ],
        },
        "exercise": {
            "title": "Review the RL problem setup",
            "overview": "Use this preparatory lesson to anchor the vocabulary used by the later coding exercises.",
            "tasks": [
                "Identify the state, action, reward, and next-state pieces in a sample transition.",
                "Explain why a policy maps states to action choices.",
                "Connect discounting to the tradeoff between near-term and future rewards.",
            ],
            "success_criteria": [
                "You can describe one full agent-environment interaction step.",
                "You can state what a policy controls.",
                "You can explain why discounted return is not the same as immediate reward.",
            ],
            "code_tip": "This is a preparatory concept lesson. There is no code submission for this lesson.",
        },
    },
    {
        "id": "policies_values_bellman",
        "title": "Policies, Values, and Bellman Backups",
        "description": "Prepare for the equation-focused lessons by connecting policies, state values, action values, and Bellman backup notation.",
        "category": "Foundations",
        "required_function": "",
        "environment_name": "",
        "env_params": {},
        "template_kind": "reading_only",
        "backend_enabled": False,
        "starter_code": "",
        "template_blanks": [],
        "success_criteria": [
            "Distinguish a policy from a value function.",
            "Explain the difference between state values and action values.",
            "Read a Bellman backup as an expected one-step lookahead plus discounted continuation value.",
        ],
        "concept_video": {
            "stream_path": "/media/concept-videos/policies_values_bellman_concept.mp4",
            "caption_path": "/media/concept-videos/policies_values_bellman_captions.vtt",
            "duration_label": "Concept video",
            "summary": "A prerequisite walkthrough of policy notation, value functions, action values, and the Bellman backup shape reused across the course.",
            "highlights": [
                "How policies choose actions while value functions evaluate outcomes.",
                "Why state values and action values answer different questions.",
                "How Bellman backups combine reward, transition probabilities, and discounted future value.",
            ],
        },
        "exercise": {
            "title": "Read the Bellman notation",
            "overview": "Use this preparatory lesson before the dynamic programming and temporal-difference coding exercises.",
            "tasks": [
                "Name the policy, transition, reward, and value terms in a Bellman expression.",
                "Separate state-value notation from action-value notation.",
                "Explain why Bellman backups are recursive.",
            ],
            "success_criteria": [
                "You can identify the role of each term in a Bellman backup.",
                "You can explain how policy probabilities affect an expectation.",
                "You can connect the backup shape to later policy evaluation and value iteration lessons.",
            ],
            "code_tip": "This is a preparatory concept lesson. There is no code submission for this lesson.",
        },
    },
    {
        "id": "dp_policy_eval",
        "title": "Policy Evaluation",
        "description": "Evaluate a fixed policy over FrozenLake using Bellman expectation backups and iterative sweeps.",
        "category": "Dynamic Programming",
        "required_function": "policy_evaluation",
        "environment_name": "FrozenLake",
        "env_params": {"map_name": "4x4", "is_slippery": True},
        "template_kind": "guided_fill_in",
        "backend_enabled": True,
        "starter_code": (
            "DISCOUNT_FACTOR = 0.95\n\n"
            "def policy_evaluation(V, policy, env, gamma=DISCOUNT_FACTOR, theta=1e-8):\n"
            "    delta = float(\"inf\")\n"
            "    while delta > theta:\n"
            "        delta = 0.0\n"
            "        for state in range(len(V)):\n"
            "            old_value = V[state]\n"
            "            new_value = 0.0\n"
            "            for action, action_prob in enumerate(policy[state]):\n"
            "                # TODO(student): combine model branches into the expectation for this action.\n"
            "                raise NotImplementedError(\"TODO: policy_eval_expectation\")\n"
            "            V[state] = new_value\n"
            "            delta = max(delta, abs(old_value - __BLANK_policy_eval_delta__))\n"
            "    return V"
        ),
        "template_blanks": [
            {
                "blank_id": "policy_eval_expectation",
                "kind": "block",
                "prompt": "Accumulate each action branch into the Bellman expectation update.",
                "expected_concept": "Bellman expectation backup",
                "approx_line_anchor": 11,
            },
            {
                "blank_id": "policy_eval_delta",
                "kind": "expression",
                "prompt": "Compare the previous value against the newly computed value in the convergence check.",
                "expected_concept": "sweep convergence",
                "approx_line_anchor": 13,
            },
        ],
        "success_criteria": [
            "The function computes the Bellman expectation update for every policy-weighted action branch.",
            "The convergence check uses the previous and updated state values.",
            "The function returns a value table that passes the sample lesson tests.",
        ],
        "concept_video": {
            "stream_path": "/media/concept-videos/dp_policy_eval_concept.mp4",
            "caption_path": "/media/concept-videos/dp_policy_eval_captions.vtt",
            "duration_label": "03:30",
            "summary": "A Bellman expectation sweep over FrozenLake, showing how policy probabilities, transition branches, rewards, and discounted future values combine into each state update.",
            "theory_equation": r"V^\pi(s)=\sum_a \pi(a|s)\sum_{s',r}p(s',r|s,a)(r+\gamma V^\pi(s'))",
            "worked_example": "In FrozenLake, each policy-weighted action contributes every possible transition branch to the new state value.",
            "misconception_to_prevent": "Policy evaluation estimates values for a fixed policy; it does not choose a better action.",
            "takeaway_line": "Policy evaluation repeatedly applies Bellman expectation backups until the value table stabilizes.",
            "theory_verification": [
                {
                    "claim": "Iterative policy evaluation applies Bellman expectation backups for a fixed policy.",
                    "source_url": "https://incompleteideas.net/book/the-book-2nd.html",
                    "validation_note": "Sutton and Barto describe iterative policy evaluation in Chapter 4 as repeated Bellman expectation updates.",
                    "is_inference": False,
                }
            ],
            "highlights": [
                "How a fixed policy weights each action.",
                "How transition probabilities and discounted future values combine.",
                "Why repeated sweeps converge to stable state values.",
            ],
        },
        "exercise": {
            "title": "Implement iterative policy evaluation",
            "overview": "Complete the Bellman expectation update so each state value is replaced by the expected return under the supplied policy.",
            "tasks": [
                "Fill the expectation TODO block so it accumulates every policy-weighted transition branch.",
                "Replace the convergence placeholder with the updated state-value comparison.",
                "Keep the discounted future value at zero for terminal transitions.",
            ],
            "success_criteria": [
                "The function computes the Bellman expectation update for every policy-weighted action branch.",
                "The convergence check uses the previous and updated state values.",
                "The function returns a value table that passes the sample lesson tests.",
            ],
            "code_tip": "Set lesson configuration inside the code itself. For this lesson, the main editable constant is DISCOUNT_FACTOR.",
        },
    },
    {
        "id": "dp_value_iteration",
        "title": "Value Iteration",
        "description": "Compute optimal FrozenLake state values by repeatedly taking the best Bellman backup at each state.",
        "category": "Dynamic Programming",
        "required_function": "value_iteration",
        "environment_name": "FrozenLake",
        "env_params": {"map_name": "4x4", "is_slippery": True},
        "template_kind": "guided_fill_in",
        "backend_enabled": True,
        "starter_code": (
            "DISCOUNT_FACTOR = 0.95\n\n"
            "def value_iteration(V, env, gamma=DISCOUNT_FACTOR, theta=1e-8):\n"
            "    delta = float(\"inf\")\n"
            "    action_count = env.action_space.n\n"
            "    while delta > theta:\n"
            "        delta = 0.0\n"
            "        for state in range(len(V)):\n"
            "            old_value = V[state]\n"
            "            action_values = []\n"
            "            for action in range(action_count):\n"
            "                action_value = 0.0\n"
            "                # TODO(student): back up one action value from transition branches.\n"
            "                raise NotImplementedError(\"TODO: value_iteration_backup\")\n"
            "                action_values.append(action_value)\n"
            "            V[state] = __BLANK_value_iteration_best_action__\n"
            "            delta = max(delta, abs(old_value - V[state]))\n"
            "    return V"
        ),
        "template_blanks": [
            {
                "blank_id": "value_iteration_backup",
                "kind": "block",
                "prompt": "Compute one action backup from transition probabilities, rewards, and discounted future values.",
                "expected_concept": "Bellman optimality backup",
                "approx_line_anchor": 12,
            },
            {
                "blank_id": "value_iteration_best_action",
                "kind": "expression",
                "prompt": "Select the best action value for the current state.",
                "expected_concept": "greedy max backup",
                "approx_line_anchor": 14,
            },
        ],
        "success_criteria": [
            "Each action value is computed from all transition branches for that action.",
            "The state value is updated with the maximum action value.",
            "The returned value table passes the sample optimal-backup lesson test.",
        ],
        "concept_video": {
            "stream_path": "/media/concept-videos/dp_value_iteration_concept.mp4",
            "caption_path": "/media/concept-videos/dp_value_iteration_captions.vtt",
            "duration_label": "03:20",
            "summary": "A FrozenLake optimality backup walkthrough that compares action values and keeps the greedy value for each state.",
            "highlights": [
                "How the environment branches for each action.",
                "Why value iteration keeps the maximum action backup.",
                "How repeated sweeps produce an optimal value table.",
            ],
        },
        "exercise": {
            "title": "Implement Bellman optimality backups",
            "overview": "Update each state by computing every action backup and keeping the maximum action value.",
            "tasks": [
                "Fill the action-backup TODO block for one action at a time.",
                "Replace the best-action placeholder with the maximum over computed action values.",
                "Preserve the convergence check across sweeps.",
            ],
            "success_criteria": [
                "Each action value is computed from all transition branches for that action.",
                "The state value is updated with the maximum action value.",
                "The returned value table passes the sample optimal-backup lesson test.",
            ],
            "code_tip": "Tune DISCOUNT_FACTOR in code if you want to inspect different planning behavior.",
        },
    },
    {
        "id": "dp_policy_improvement",
        "title": "Policy Improvement",
        "description": "Turn a FrozenLake state-value table into a greedy policy by backing up each available action.",
        "category": "Dynamic Programming",
        "required_function": "policy_improvement",
        "environment_name": "FrozenLake",
        "env_params": {"map_name": "4x4", "is_slippery": True},
        "template_kind": "guided_fill_in",
        "backend_enabled": True,
        "starter_code": (
            "DISCOUNT_FACTOR = 0.95\n\n"
            "def policy_improvement(V, env, gamma=DISCOUNT_FACTOR):\n"
            "    action_count = env.action_space.n\n"
            "    policy = [[0.0 for _ in range(action_count)] for _ in range(len(V))]\n\n"
            "    for state in range(len(V)):\n"
            "        action_values = []\n"
            "        for action in range(action_count):\n"
            "            action_value = 0.0\n"
            "            # TODO(student): compute the one-step lookahead return for this action.\n"
            "            raise NotImplementedError(\"TODO: policy_improvement_backup\")\n"
            "            action_values.append(action_value)\n\n"
            "        best_action = __BLANK_policy_improvement_best_action__\n"
            "        policy[state][best_action] = 1.0\n\n"
            "    return policy"
        ),
        "template_blanks": [
            {
                "blank_id": "policy_improvement_backup",
                "kind": "block",
                "prompt": "Compute each action's one-step lookahead return from the value table.",
                "expected_concept": "greedy policy backup",
                "approx_line_anchor": 11,
            },
            {
                "blank_id": "policy_improvement_best_action",
                "kind": "expression",
                "prompt": "Choose the greedy action index from the action values list.",
                "expected_concept": "argmax policy improvement",
                "approx_line_anchor": 14,
            },
        ],
        "success_criteria": [
            "Each action score is computed from transition probabilities, rewards, and discounted future values.",
            "The selected action index is the greedy argmax over the action scores.",
            "Each output policy row remains one-hot and passes the sample lesson test.",
        ],
        "concept_video": {
            "stream_path": "/media/concept-videos/dp_policy_improvement_concept.mp4",
            "caption_path": "/media/concept-videos/dp_policy_improvement_captions.vtt",
            "duration_label": "03:10",
            "summary": "A greedy policy-improvement pass that converts state values into a one-hot action policy.",
            "highlights": [
                "How one-step lookahead scores each action.",
                "How the argmax action becomes the improved policy.",
                "Why policy rows remain one-hot after improvement.",
            ],
        },
        "exercise": {
            "title": "Implement greedy policy improvement",
            "overview": "Compute each action score from the value table and select the greedy action for every state.",
            "tasks": [
                "Fill the one-step lookahead TODO block.",
                "Replace the best-action placeholder with the greedy action index.",
                "Keep each returned policy row one-hot.",
            ],
            "success_criteria": [
                "Each action score is computed from transition probabilities, rewards, and discounted future values.",
                "The selected action index is the greedy argmax over the action scores.",
                "Each output policy row remains one-hot and passes the sample lesson test.",
            ],
            "code_tip": "Use DISCOUNT_FACTOR in code to keep the action lookahead aligned with the lesson configuration.",
        },
    },
    {
        "id": "mc_first_visit",
        "title": "First-Visit Monte Carlo",
        "description": "Estimate Blackjack state values from complete episodes and first-visit returns.",
        "category": "Monte Carlo Methods",
        "required_function": "mc_first_visit_prediction",
        "environment_name": "Blackjack",
        "env_params": {"sab": True},
        "template_kind": "guided_fill_in",
        "backend_enabled": True,
        "starter_code": (
            "DISCOUNT_FACTOR = 0.95\n"
            "EPISODE_COUNT = 6\n\n"
            "def mc_first_visit_prediction(episode, V, returns, gamma=DISCOUNT_FACTOR):\n"
            "    visited_states = set()\n"
            "    for index, (state, _action, _reward) in enumerate(episode):\n"
            "        if __BLANK_mc_first_visit_seen_state__:\n"
            "            continue\n"
            "        visited_states.add(state)\n"
            "        G = 0.0\n"
            "        discount = 1.0\n"
            "        # TODO(student): roll the discounted return forward from the first visit.\n"
            "        raise NotImplementedError(\"TODO: mc_first_visit_return\")\n"
            "        returns.setdefault(state, []).append(G)\n"
            "        V[state] = sum(returns[state]) / len(returns[state])\n"
            "    return V"
        ),
        "template_blanks": [
            {
                "blank_id": "mc_first_visit_seen_state",
                "kind": "expression",
                "prompt": "Skip repeated states after their first occurrence in the episode.",
                "expected_concept": "first-visit filtering",
                "approx_line_anchor": 7,
            },
            {
                "blank_id": "mc_first_visit_return",
                "kind": "block",
                "prompt": "Compute the discounted return from the first-visit index to the end of the episode.",
                "expected_concept": "Monte Carlo return accumulation",
                "approx_line_anchor": 11,
            },
        ],
        "success_criteria": [
            "Repeated states are skipped after the first occurrence in the episode.",
            "The discounted return is accumulated from the first-visit index onward.",
            "The value table update passes the sample first-visit Monte Carlo test.",
        ],
        "concept_video": {
            "stream_path": "/media/concept-videos/mc_first_visit_concept.mp4",
            "caption_path": "/media/concept-videos/mc_first_visit_captions.vtt",
            "duration_label": "03:45",
            "summary": "A Blackjack episode trace showing how first-visit Monte Carlo prediction estimates values from complete sampled returns.",
            "highlights": [
                "Why repeated states are skipped after the first visit.",
                "How discounted returns are accumulated from an episode.",
                "How repeated returns average into a value estimate.",
            ],
        },
        "exercise": {
            "title": "Implement first-visit return updates",
            "overview": "Skip repeated states, compute the discounted return from the first visit, and update the running value estimate.",
            "tasks": [
                "Replace the first-visit condition placeholder.",
                "Fill the return-accumulation TODO block.",
                "Append the return and average all returns for the state.",
            ],
            "success_criteria": [
                "Repeated states are skipped after the first occurrence in the episode.",
                "The discounted return is accumulated from the first-visit index onward.",
                "The value table update passes the sample first-visit Monte Carlo test.",
            ],
            "code_tip": "EPISODE_COUNT and DISCOUNT_FACTOR are defined in the submitted code so experiments stay visible.",
            "execution_contract_notes": [
                "Episode rows are (state, action, reward); Blackjack state is a tuple like (player sum, dealer card, usable ace).",
            ],
        },
    },
    {
        "id": "td_sarsa",
        "title": "SARSA",
        "description": "Update CliffWalking action values with on-policy TD targets that use the next sampled action.",
        "category": "Temporal Difference",
        "required_function": "sarsa_update",
        "environment_name": "CliffWalking",
        "env_params": {},
        "template_kind": "guided_fill_in",
        "backend_enabled": True,
        "starter_code": (
            "LEARNING_RATE = 0.10\n"
            "DISCOUNT_FACTOR = 0.95\n"
            "EXPLORATION_RATE = 0.20\n"
            "EPISODE_COUNT = 6\n\n"
            "def sarsa_update(\n"
            "    Q,\n"
            "    state,\n"
            "    action,\n"
            "    reward,\n"
            "    next_state,\n"
            "    next_action,\n"
            "    alpha=LEARNING_RATE,\n"
            "    gamma=DISCOUNT_FACTOR,\n"
            "):\n"
            "    bootstrap = __BLANK_sarsa_bootstrap__\n"
            "    td_target = reward + gamma * bootstrap\n"
            "    # TODO(student): apply the on-policy SARSA update to the selected Q-value.\n"
            "    raise NotImplementedError(\"TODO: sarsa_update_rule\")\n"
            "    return Q"
        ),
        "template_blanks": [
            {
                "blank_id": "sarsa_bootstrap",
                "kind": "expression",
                "prompt": "Use the sampled next action for the bootstrap, with zero on terminal transitions.",
                "expected_concept": "on-policy bootstrap",
                "approx_line_anchor": 13,
            },
            {
                "blank_id": "sarsa_update_rule",
                "kind": "block",
                "prompt": "Apply the incremental SARSA update using the TD target.",
                "expected_concept": "SARSA TD update",
                "approx_line_anchor": 15,
            },
        ],
        "success_criteria": [
            "The bootstrap term uses the sampled next action, not a max over the row.",
            "Terminal transitions use a zero bootstrap.",
            "The updated Q-table passes the sample SARSA lesson test.",
        ],
        "concept_video": {
            "stream_path": "/media/concept-videos/td_sarsa_concept.mp4",
            "caption_path": "/media/concept-videos/td_sarsa_captions.vtt",
            "duration_label": "03:35",
            "summary": "An on-policy CliffWalking update showing how SARSA bootstraps from the next sampled action.",
            "highlights": [
                "How SARSA uses the action actually selected by the behavior policy.",
                "How terminal transitions remove the bootstrap term.",
                "How the Q-table changes after a single TD update.",
            ],
        },
        "exercise": {
            "title": "Implement the SARSA update rule",
            "overview": "Complete the on-policy TD update that uses the sampled next action rather than a greedy maximum.",
            "tasks": [
                "Replace the bootstrap placeholder with the sampled next-action value.",
                "Fill the TODO block that performs the incremental SARSA update.",
                "Keep terminal transitions from bootstrapping future value.",
            ],
            "success_criteria": [
                "The bootstrap term uses the sampled next action, not a max over the row.",
                "Terminal transitions use a zero bootstrap.",
                "The updated Q-table passes the sample SARSA lesson test.",
            ],
            "code_tip": "LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, and EPISODE_COUNT are read from the submitted code.",
        },
    },
    {
        "id": "td_q_learning",
        "title": "Q-Learning",
        "description": "Update CliffWalking action values from one-step TD targets and epsilon-greedy samples.",
        "category": "Temporal Difference",
        "required_function": "q_learning_update",
        "environment_name": "CliffWalking",
        "env_params": {},
        "template_kind": "guided_fill_in",
        "backend_enabled": True,
        "starter_code": (
            "LEARNING_RATE = 0.10\n"
            "DISCOUNT_FACTOR = 0.95\n"
            "EXPLORATION_RATE = 0.20\n"
            "EPISODE_COUNT = 6\n\n"
            "def q_learning_update(Q, state, action, reward, next_state, alpha=LEARNING_RATE, gamma=DISCOUNT_FACTOR):\n"
            "    best_next_value = __BLANK_q_learning_best_next__\n"
            "    td_target = reward + gamma * best_next_value\n"
            "    # TODO(student): apply the one-step TD update to the chosen Q-value.\n"
            "    raise NotImplementedError(\"TODO: q_learning_update_rule\")\n"
            "    return Q"
        ),
        "template_blanks": [
            {
                "blank_id": "q_learning_best_next",
                "kind": "expression",
                "prompt": "Select the greedy bootstrap value from the next-state row of the list-backed Q-table.",
                "expected_concept": "max next-state bootstrap",
                "approx_line_anchor": 7,
            },
            {
                "blank_id": "q_learning_update_rule",
                "kind": "block",
                "prompt": "Apply the incremental Q-learning update using alpha and the TD target.",
                "expected_concept": "one-step TD update",
                "approx_line_anchor": 9,
            },
        ],
        "success_criteria": [
            "The bootstrap term uses the maximum next-state action value.",
            "The chosen Q-value is updated incrementally toward the TD target.",
            "The function returns the updated Q-table and passes the sample lesson test.",
        ],
        "concept_video": {
            "stream_path": "/media/concept-videos/td_q_learning_concept.mp4",
            "caption_path": "/media/concept-videos/td_q_learning_captions.vtt",
            "duration_label": "03:25",
            "summary": "An off-policy CliffWalking update showing how Q-learning bootstraps from the greedy next-state action value.",
            "highlights": [
                "How Q-learning uses a max over next-state action values.",
                "How the TD target combines reward and discounted bootstrap.",
                "How the selected Q-value moves toward the target.",
            ],
        },
        "exercise": {
            "title": "Implement the Q-learning update rule",
            "overview": "Complete the one-step TD update that adjusts a single Q-value from a sampled transition.",
            "tasks": [
                "Replace the bootstrap placeholder with the greedy next-state value from the list-backed Q row.",
                "Fill the TODO block that performs the incremental TD update.",
                "Keep the TD target expression that combines reward and discounted bootstrap.",
            ],
            "success_criteria": [
                "The bootstrap term uses the maximum next-state action value.",
                "The chosen Q-value is updated incrementally toward the TD target.",
                "The function returns the updated Q-table and passes the sample lesson test.",
            ],
            "code_tip": "Q is list-backed in the backend, so max(Q[next_state]) is the direct bootstrap expression. LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, and EPISODE_COUNT are read from the submitted code.",
        },
    },
]

def _payload_to_lesson(payload: dict[str, Any]) -> LessonDefinition:
    blanks = [
        TemplateBlank(**b) for b in payload.get("template_blanks", [])
    ]
    return LessonDefinition(
        id=payload["id"],
        title=payload.get("title", ""),
        description=payload.get("description", ""),
        category=payload.get("category", ""),
        required_function=payload.get("required_function", ""),
        environment_name=payload.get("environment_name", ""),
        starter_code=payload.get("starter_code", ""),
        template_kind=payload.get("template_kind", "guided_fill_in"),
        template_blanks=blanks,
        success_criteria=payload.get("success_criteria", []),
        env_params=payload.get("env_params", {}),
    )


class LessonRegistryService:
    """Single source of truth for all lesson definitions.

    Core lessons are seeded automatically on first startup.  Instructor-
    authored lessons are added/updated through the admin authoring API and
    stored in the same table.  Both are served identically to the rest of
    the application.
    """

    def __init__(self, *, database: Database) -> None:
        self._database = database
        self._lock = Lock()
        self._ensure_seeded()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_lesson(self, lesson_id: str) -> LessonDefinition | None:
        with self._database.session() as session:
            row = session.get(AuthoredLesson, lesson_id)
            if row is None:
                return None
            payload = self._decode(row.payload_json)
            return _payload_to_lesson(payload) if payload else None

    def list_lessons(self) -> list[LessonDefinition]:
        with self._database.session() as session:
            rows = session.exec(
                select(AuthoredLesson).order_by(
                    AuthoredLesson.category, AuthoredLesson.title
                )
            ).all()
            lessons = []
            for row in rows:
                payload = self._decode(row.payload_json)
                if payload:
                    lessons.append(_payload_to_lesson(payload))
            return lessons

    def get_lesson_payload(self, lesson_id: str) -> dict[str, Any] | None:
        """Return the full raw payload (including presentation metadata)."""
        with self._database.session() as session:
            row = session.get(AuthoredLesson, lesson_id)
            if row is None:
                return None
            return self._decode(row.payload_json)

    def list_lesson_payloads(self) -> list[dict[str, Any]]:
        with self._database.session() as session:
            rows = session.exec(
                select(AuthoredLesson).order_by(
                    AuthoredLesson.category, AuthoredLesson.title
                )
            ).all()
            return [p for row in rows if (p := self._decode(row.payload_json))]

    def upsert_lesson(
        self,
        *,
        lesson_id: str,
        payload: dict[str, Any],
        actor_user_id: str,
    ) -> dict[str, Any]:
        """Create or update a lesson.  Validates required fields."""
        from datetime import datetime, timezone

        normalized = dict(payload)
        normalized["id"] = lesson_id
        for key in ("title", "category", "description", "starter_code"):
            value = str(normalized.get(key) or "").strip()
            if not value:
                raise ValueError(f"Lesson requires '{key}'.")
            normalized[key] = value
        normalized.setdefault("concept_video", {})
        normalized.setdefault("exercise", {})
        normalized.setdefault("required_function", "")
        normalized.setdefault("environment_name", "")
        normalized.setdefault("template_kind", "guided_fill_in")
        normalized.setdefault("template_blanks", [])
        normalized.setdefault("success_criteria", [])
        normalized["backend_enabled"] = bool(normalized.get("backend_enabled", False))

        now = datetime.now(timezone.utc)
        with self._lock:
            with self._database.session() as session:
                row = session.get(AuthoredLesson, lesson_id)
                if row is None:
                    row = AuthoredLesson(
                        id=lesson_id,
                        title=normalized["title"],
                        category=normalized["category"],
                        description=normalized["description"],
                        payload_json=json.dumps(normalized, sort_keys=True),
                        created_by_user_id=actor_user_id,
                        updated_by_user_id=actor_user_id,
                        created_at_utc=now,
                        updated_at_utc=now,
                    )
                else:
                    row.title = normalized["title"]
                    row.category = normalized["category"]
                    row.description = normalized["description"]
                    row.payload_json = json.dumps(normalized, sort_keys=True)
                    row.updated_by_user_id = actor_user_id
                    row.updated_at_utc = now
                session.add(row)
                session.commit()
        return normalized

    def delete_lesson(self, lesson_id: str) -> bool:
        with self._lock:
            with self._database.session() as session:
                row = session.get(AuthoredLesson, lesson_id)
                if row is None:
                    return False
                session.delete(row)
                session.commit()
                return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_seeded(self) -> None:
        with self._lock:
            with self._database.session() as session:
                existing_rows = {
                    row.id: row
                    for row in session.exec(select(AuthoredLesson)).all()
                }
            for lesson_data in _CORE_LESSONS:
                row = existing_rows.get(lesson_data["id"])
                if row is None:
                    self._seed_lesson(lesson_data)
                elif row.created_by_user_id == "system":
                    self._refresh_system_lesson(lesson_data)

    def _seed_lesson(self, lesson_data: dict[str, Any]) -> None:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        with self._database.session() as session:
            row = AuthoredLesson(
                id=lesson_data["id"],
                title=lesson_data["title"],
                category=lesson_data["category"],
                description=lesson_data["description"],
                payload_json=json.dumps(lesson_data, sort_keys=True),
                created_by_user_id="system",
                updated_by_user_id="system",
                created_at_utc=now,
                updated_at_utc=now,
            )
            session.add(row)
            session.commit()

    def _refresh_system_lesson(self, lesson_data: dict[str, Any]) -> None:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        with self._database.session() as session:
            row = session.get(AuthoredLesson, lesson_data["id"])
            if row is None or row.created_by_user_id != "system":
                return
            row.title = lesson_data["title"]
            row.category = lesson_data["category"]
            row.description = lesson_data["description"]
            row.payload_json = json.dumps(lesson_data, sort_keys=True)
            row.updated_by_user_id = "system"
            row.updated_at_utc = now
            session.add(row)
            session.commit()

    @staticmethod
    def _decode(raw: str) -> dict[str, Any] | None:
        try:
            result = json.loads(raw)
            return result if isinstance(result, dict) else None
        except json.JSONDecodeError:
            return None
