from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TheoryVerification:
    claim: str
    source_url: str
    validation_note: str
    is_inference: bool = False


@dataclass(frozen=True)
class LessonVideoSpec:
    lesson_id: str
    title: str
    environment_name: str
    theory_equation: str
    worked_example: str
    code_focus_lines: tuple[str, ...]
    misconception_to_prevent: str
    takeaway_line: str
    pacing_notes: tuple[str, ...]
    target_duration_label: str
    theory_verification: tuple[TheoryVerification, ...]


LESSON_VIDEO_SPECS: dict[str, LessonVideoSpec] = {
    "dp_policy_eval": LessonVideoSpec(
        lesson_id="dp_policy_eval",
        title="Policy Evaluation",
        environment_name="FrozenLake",
        theory_equation=r"V^{\pi}(s)=\sum_a \pi(a|s)\sum_{s',r}p(s',r|s,a)\left[r+\gamma V^{\pi}(s')\right]",
        worked_example="Freeze one slippery FrozenLake state, show both branches of one action, then connect the full Bellman expectation sweep to the code loop.",
        code_focus_lines=(
            "for action, action_prob in enumerate(policy[state]):",
            "for transition_prob, next_state, reward, done in env.P[state][action]:",
            "new_value += action_prob * transition_prob * (reward + gamma * future)",
            "V[state] = new_value",
        ),
        misconception_to_prevent="Policy evaluation updates state values while keeping the policy fixed.",
        takeaway_line="Policy evaluation repeatedly recomputes each state from all modeled outcomes under the current policy.",
        pacing_notes=(
            "Pause after the Bellman expectation equation appears.",
            "Pause after branch probabilities are revealed in the FrozenLake state.",
            "Let the numeric backup settle before the code line highlight begins.",
            "End with a long hold on the fixed-policy reminder.",
        ),
        target_duration_label="03:30",
        theory_verification=(
            TheoryVerification(
                claim="Dynamic programming policy evaluation uses Bellman expectation backups under a fixed policy.",
                source_url="https://incompleteideas.net/book/the-book-2nd.html",
                validation_note="Sutton and Barto Chapter 4 is the primary theory reference for policy evaluation.",
            ),
            TheoryVerification(
                claim="FrozenLake exposes tabular transitions suitable for full-backup illustrations.",
                source_url="https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/",
                validation_note="Gymnasium documents the discrete state/action structure and slippery transition behavior.",
                is_inference=True,
            ),
        ),
    ),
    "dp_value_iteration": LessonVideoSpec(
        lesson_id="dp_value_iteration",
        title="Value Iteration",
        environment_name="FrozenLake",
        theory_equation=r"V_*(s)=\max_a \sum_{s',r}p(s',r|s,a)\left[r+\gamma V_*(s')\right]",
        worked_example="Freeze one FrozenLake state, compare all four action backups one at a time, then keep only the best one.",
        code_focus_lines=(
            "for action in range(action_count):",
            "action_value += transition_prob * (reward + gamma * future)",
            "action_values.append(action_value)",
            "V[state] = max(action_values)",
        ),
        misconception_to_prevent="Value iteration does not average over a fixed policy; it compares action backups and keeps the best one.",
        takeaway_line="Value iteration replaces the policy-weighted expectation with the best one-step backup.",
        pacing_notes=(
            "Pause after each action backup before revealing the next one.",
            "Hold on the maximum decision so the winning action is readable.",
            "Give the code trace its own beat after the math comparison settles.",
        ),
        target_duration_label="03:20",
        theory_verification=(
            TheoryVerification(
                claim="Value iteration uses Bellman optimality backups with a max over actions.",
                source_url="https://incompleteideas.net/book/the-book-2nd.html",
                validation_note="Sutton and Barto Chapter 4 is the primary theory reference for value iteration.",
            ),
            TheoryVerification(
                claim="FrozenLake is a suitable discrete environment for action-backup comparisons.",
                source_url="https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/",
                validation_note="Gymnasium documents the discrete tabular action/state structure.",
                is_inference=True,
            ),
        ),
    ),
    "dp_policy_improvement": LessonVideoSpec(
        lesson_id="dp_policy_improvement",
        title="Policy Improvement",
        environment_name="FrozenLake",
        theory_equation=r"\pi'(s)=\arg\max_a \sum_{s',r}p(s',r|s,a)\left[r+\gamma V(s')\right]",
        worked_example="Take one state with known values, compare the one-step lookahead returns for each action, then update the policy row.",
        code_focus_lines=(
            "for action in range(action_count):",
            "action_value += transition_prob * (reward + gamma * future)",
            "best_action = max(range(action_count), key=lambda index: action_values[index])",
            "policy[state][best_action] = 1.0",
        ),
        misconception_to_prevent="Policy improvement changes the action choice while treating the value table as given.",
        takeaway_line="Policy improvement chooses the greedy action by comparing one-step lookahead returns built from the current value table.",
        pacing_notes=(
            "Pause after the argmax token expands into the comparison block.",
            "Hold before the policy arrow changes so the decision beat reads clearly.",
            "Keep the updated policy row on screen long enough to compare against the unchanged values.",
        ),
        target_duration_label="03:00",
        theory_verification=(
            TheoryVerification(
                claim="Policy improvement chooses greedy actions using one-step lookahead backed by the current value table.",
                source_url="https://incompleteideas.net/book/the-book-2nd.html",
                validation_note="Sutton and Barto Chapter 4 is the primary theory reference for policy improvement.",
            ),
            TheoryVerification(
                claim="FrozenLake remains appropriate for state-level action comparisons in DP.",
                source_url="https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/",
                validation_note="Gymnasium documents the discrete transition structure needed for action-level lookahead.",
                is_inference=True,
            ),
        ),
    ),
    "mc_first_visit": LessonVideoSpec(
        lesson_id="mc_first_visit",
        title="First-Visit Monte Carlo",
        environment_name="Blackjack",
        theory_equation=r"G_t=\sum_{k=0}^{T-t-1}\gamma^kR_{t+k+1},\quad V(s)\leftarrow \text{mean}(G_t)",
        worked_example="Show one Blackjack episode from initial hand to terminal reward, then compute the first-visit return for the first state occurrence only.",
        code_focus_lines=(
            "if state in visited_states: continue",
            "G += discount * reward",
            "returns[state].append(G)",
            "V[state] = sum(returns[state]) / len(returns[state])",
        ),
        misconception_to_prevent="Monte Carlo waits for the full episode and does not bootstrap from a next-state estimate.",
        takeaway_line="First-visit Monte Carlo updates a state only after the episode ends, using the full discounted return from its first occurrence.",
        pacing_notes=(
            "Keep the full episode visible before beginning the return calculation.",
            "Pause on the first-visit rule before showing the return update.",
            "Let the return accumulation unfold slowly enough to read each reward contribution.",
        ),
        target_duration_label="05:10",
        theory_verification=(
            TheoryVerification(
                claim="Blackjack is the canonical episodic Monte Carlo teaching example from Sutton and Barto.",
                source_url="https://gymnasium.farama.org/v0.26.3/tutorials/blackjack_tutorial/",
                validation_note="Gymnasium explicitly states that Blackjack-v1 follows Sutton and Barto's setup.",
            ),
            TheoryVerification(
                claim="First-visit Monte Carlo uses complete-episode returns rather than bootstrapped targets.",
                source_url="https://incompleteideas.net/book/the-book-2nd.html",
                validation_note="Sutton and Barto Chapter 5 is the primary theory reference for first-visit Monte Carlo.",
            ),
        ),
    ),
    "td_sarsa": LessonVideoSpec(
        lesson_id="td_sarsa",
        title="SARSA",
        environment_name="CliffWalking",
        theory_equation=r"Q(s,a)\leftarrow Q(s,a)+\alpha\left[r+\gamma Q(s',a')-Q(s,a)\right]",
        worked_example="Show a CliffWalking transition, keep the sampled next action visible, then build the on-policy TD target from that exact action.",
        code_focus_lines=(
            "next_action = behavior_policy(next_state)",
            "bootstrap = 0.0 if next_action is None else Q[next_state][next_action]",
            "td_target = reward + gamma * bootstrap",
            "Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])",
        ),
        misconception_to_prevent="SARSA is on-policy because the target uses the next action the behavior policy actually sampled.",
        takeaway_line="SARSA updates one Q-value using the reward plus the discounted value of the next sampled action.",
        pacing_notes=(
            "Pause on the sampled next action before constructing the TD target.",
            "Let the CliffWalking successor state and next action remain visible during the update.",
            "End with a slow contrast beat between fixed transition and updated Q-value.",
        ),
        target_duration_label="05:00",
        theory_verification=(
            TheoryVerification(
                claim="SARSA uses the next sampled action in its TD target and is on-policy.",
                source_url="https://incompleteideas.net/book/the-book-2nd.html",
                validation_note="Sutton and Barto Chapter 6 is the primary theory reference for SARSA.",
            ),
            TheoryVerification(
                claim="CliffWalking is the canonical environment for illustrating SARSA behavior.",
                source_url="https://gymnasium.farama.org/v0.26.3/environments/toy_text/cliff_walking/",
                validation_note="Gymnasium explicitly notes CliffWalking is adapted from Sutton and Barto Example 6.6.",
            ),
        ),
    ),
    "td_q_learning": LessonVideoSpec(
        lesson_id="td_q_learning",
        title="Q-Learning",
        environment_name="CliffWalking",
        theory_equation=r"Q(s,a)\leftarrow Q(s,a)+\alpha\left[r+\gamma \max_{a'}Q(s',a')-Q(s,a)\right]",
        worked_example="Use the same CliffWalking transition framing as SARSA, but replace the sampled next action with the greedy max over the next-state row.",
        code_focus_lines=(
            "best_next_value = max(Q[next_state])",
            "td_target = reward + gamma * best_next_value",
            "Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])",
        ),
        misconception_to_prevent="Q-learning does not use the sampled next action in the target; it bootstraps from the greedy next-state value.",
        takeaway_line="Q-learning updates one Q-value using a greedy next-state target even when behavior still explores.",
        pacing_notes=(
            "Pause after the max term is highlighted so the off-policy target can be read.",
            "Contrast the sampled behavior transition with the greedy target in separate beats.",
            "Hold after the numeric TD update before moving to the final takeaway.",
        ),
        target_duration_label="04:40",
        theory_verification=(
            TheoryVerification(
                claim="Q-learning uses reward plus discounted max next-state action value and is off-policy.",
                source_url="https://incompleteideas.net/book/the-book-2nd.html",
                validation_note="Sutton and Barto Chapter 6 is the primary theory reference for Q-learning.",
            ),
            TheoryVerification(
                claim="CliffWalking is the canonical environment for contrasting Q-learning with SARSA.",
                source_url="https://gymnasium.farama.org/v0.26.3/environments/toy_text/cliff_walking/",
                validation_note="Gymnasium explicitly notes CliffWalking is adapted from Sutton and Barto Example 6.6.",
            ),
        ),
    ),
}
