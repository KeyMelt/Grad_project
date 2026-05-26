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
    "rl_intro": LessonVideoSpec(
        lesson_id="rl_intro",
        title="What Is Reinforcement Learning?",
        environment_name="FrozenLake",
        theory_equation="none",
        worked_example=(
            "Show an elf navigating FrozenLake-v1 across three attempts — two failures "
            "(holes 7 and 12) and one success (path 0→4→8→9→10→14→15, reward +1). "
            "Contrast this with supervised and unsupervised learning via a three-panel "
            "diagram, then build the abstract agent–environment loop."
        ),
        code_focus_lines=(),
        misconception_to_prevent=(
            "RL is not supervised learning with delayed feedback. "
            "There is no supervisor and no labeled dataset — only a reward signal "
            "the agent discovers through interaction."
        ),
        takeaway_line=(
            "Reinforcement learning is the science of learning to act by trial and error "
            "— no labels, just rewards."
        ),
        pacing_notes=(
            "Hold 3.5 s on the first grid reveal before elf moves.",
            "Hold 3.5 s after each elf failure before the next attempt.",
            "Hold 4.5 s on the complete loop diagram before the cycle animation.",
            "Final takeaway hold is 8.0 s — maintain full duration.",
        ),
        target_duration_label="03:38",
        theory_verification=(
            TheoryVerification(
                claim=(
                    "Reinforcement learning is distinct from supervised and unsupervised "
                    "learning because it uses a reward signal rather than labeled examples "
                    "or unlabeled data."
                ),
                source_url="https://incompleteideas.net/book/the-book-2nd.html",
                validation_note=(
                    "Sutton and Barto Chapter 1, Section 1.1 (pp. 1–3) defines RL as a "
                    "third machine-learning paradigm and explicitly contrasts it with "
                    "supervised and unsupervised learning."
                ),
            ),
            TheoryVerification(
                claim=(
                    "FrozenLake-v1 hole states are {5, 7, 11, 12}; goal is state 15; "
                    "reward 1.0 fires on arrival at state 15."
                ),
                source_url="https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/",
                validation_note=(
                    "Confirmed by Technical Validator via live Gymnasium env.unwrapped.P "
                    "inspection. Reward fires from arrival transitions (e.g. P[14][action] "
                    "→ state 15), not from P[15] self-loop (which returns reward 0)."
                ),
                is_inference=True,
            ),
        ),
    ),
    "mdp_foundations": LessonVideoSpec(
        lesson_id="mdp_foundations",
        title="MDP Foundations: From States to the Bellman Equation",
        environment_name="FrozenLake",
        theory_equation=r"v_{\pi}(s)=\sum_a \pi(a|s)\sum_{s',r}p(s',r|s,a)\left[r+\gamma v_{\pi}(s')\right]",
        worked_example=(
            "Use FrozenLake-v1 4×4 (is_slippery=True) throughout. Build one accreting "
            "grid across six segments: (a) state indices 0–15 + Markov property; "
            "(b) return G_t with one gamma animation showing G=0.9801 for rewards [0,0,1] "
            "at γ=0.99, plus the recursion G_t = R_{t+1} + γ G_{t+1}; (c) state 6, "
            "action RIGHT — three slippery outcomes {7,2,10} each 1/3, Σp=1; "
            "(d) uniform-random policy arrows vs. probability bars (each 0.25); "
            "(e) value heatmap with terminal={5,7,11,12,15}=0 under non-optimal policy; "
            "(f) one backup diagram deriving the Bellman expectation equation term-by-term "
            "from G_t = R_{t+1} + γG_{t+1}."
        ),
        code_focus_lines=(
            "env = gym.make('FrozenLake-v1', is_slippery=True)",
            "for prob, next_state, reward, done in env.unwrapped.P[6][2]:",
            "    print(prob, next_state, reward, done)",
            "policy = np.ones((env.observation_space.n, env.action_space.n)) / env.action_space.n",
        ),
        misconception_to_prevent=(
            "The transition function p(s',r|s,a) is the environment's response, not "
            "the agent's action choice (that is the policy π(a|s)); and v_π is "
            "defined for ANY policy, including the uniform-random policy, not only the "
            "optimal one."
        ),
        takeaway_line=(
            "A finite MDP is (states, actions, p); a policy plus a discount turns rewards "
            "into returns; value functions measure those returns under any policy; and the "
            "Bellman expectation equation expresses each state's value recursively from its "
            "successors — the exact equality the next video turns into an algorithm."
        ),
        pacing_notes=(
            "Segment (a): build the grid once with state indices; state the Markov property; "
            "do not enumerate transitions. ~4:10.",
            "Segment (b): animate gamma exactly once; surface G_t = R_{t+1} + gamma*G_{t+1} "
            "for reuse in (f). ~4:40.",
            "Segment (c): reuse/corrected transition_prob scene beat; hold on the three 1/3 "
            "bars and the sum-to-one. State-6 RIGHT successors are {7,2,10}, NOT {7,2,5}. ~4:30.",
            "Segment (d): one deterministic-vs-stochastic policy contrast; foreshadow the "
            "uniform-random policy used by dp_policy_eval. ~3:30.",
            "Segment (e): heatmap reading + q-bars; show terminal cells at 0; use a "
            "non-optimal policy. ~4:10.",
            "Recap card: π/p/r/γ/v_π summary before Bellman. ~1:20.",
            "Segment (f): derive the Bellman equation from G_t's recursion via one backup "
            "diagram; preview policy evaluation without showing its loop. ~4:40.",
            "Closing: preview dp_policy_eval by name; do not show the iteration loop. ~1:20.",
        ),
        target_duration_label="28:20",
        theory_verification=(
            TheoryVerification(
                claim=(
                    "A finite MDP is defined by states, actions, and the four-argument "
                    "dynamics p(s',r|s,a); the return is G_t = Σ_{k≥0} γ^k R_{t+k+1}; "
                    "and the Bellman expectation equation v_π(s) = Σ_a π(a|s) "
                    "Σ_{s',r} p(s',r|s,a)[r + γv_π(s')] characterises the value function."
                ),
                source_url="https://incompleteideas.net/book/the-book-2nd.html",
                validation_note=(
                    "Sutton and Barto Chapter 3: p(s',r|s,a) eq. 3.2 (p. 48); return G_t "
                    "eq. 3.8 and recursion eq. 3.9 (pp. 54–55); v_π eq. 3.12 (p. 58); "
                    "Bellman expectation eq. 3.14 (p. 59)."
                ),
            ),
            TheoryVerification(
                claim=(
                    "FrozenLake-v1 is_slippery=True: state 6, action RIGHT yields exactly "
                    "three transitions — to states {7, 2, 10} each with probability 1/3, "
                    "reward 0.0, done=True only for state 7 (hole). Sum of probabilities = 1."
                ),
                source_url="https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/",
                validation_note=(
                    "Confirmed by Gate 2 Technical Validator via live Gymnasium: "
                    "env.unwrapped.P[6][2] = [(0.333,10,0.0,False),(0.333,7,0.0,True),"
                    "(0.333,2,0.0,False)]. Corrected from erroneous {7,2,5} in prior "
                    "reference scene transition_prob_concept.py."
                ),
                is_inference=False,
            ),
        ),
    ),
    "transition_prob": LessonVideoSpec(
        lesson_id="transition_prob",
        title="Transition Probability",
        environment_name="FrozenLake",
        theory_equation=r"p(s', r \mid s, a) \geq 0, \quad \sum_{s'}\sum_{r} p(s', r \mid s, a) = 1",
        worked_example=(
            "Focus on FrozenLake state 6 with action RIGHT. "
            "Show the three slippery outcomes (lands RIGHT, UP, DOWN) with their "
            "probabilities from env.unwrapped.P, then assemble the full "
            "probability distribution and verify it sums to 1."
        ),
        code_focus_lines=(
            "env = gym.make('FrozenLake-v1', is_slippery=True)",
            "for prob, next_state, reward, done in env.unwrapped.P[state][action]:",
            "    print(prob, next_state, reward, done)",
        ),
        misconception_to_prevent=(
            "Transition probability is not the probability of choosing an action; "
            "it is the probability that the environment places the agent in next "
            "state s' with reward r given that action a was taken in state s."
        ),
        takeaway_line=(
            "p(s',r|s,a) is the environment's complete specification: for every "
            "state and action it gives the full distribution over successor states "
            "and rewards."
        ),
        pacing_notes=(
            "Pause after each slippery outcome cell lights up before revealing the next.",
            "Hold on the ActionBarChart once all three bars appear — let probabilities read.",
            "Let the summation constraint Σ=1 settle before the code panel enters.",
            "End with the takeaway caption visible for the full final hold.",
        ),
        target_duration_label="06:00",
        theory_verification=(
            TheoryVerification(
                claim=(
                    "The four-argument dynamics function p(s',r|s,a) is the "
                    "complete specification of a finite MDP environment."
                ),
                source_url="https://incompleteideas.net/book/the-book-2nd.html",
                validation_note=(
                    "Sutton and Barto Chapter 3, Section 3.1 defines p(s',r|s,a) "
                    "as the probability of transition to s' with reward r from (s,a)."
                ),
            ),
            TheoryVerification(
                claim=(
                    "FrozenLake-v1 with is_slippery=True produces three-way "
                    "stochastic outcomes for each action, exposing the dynamics "
                    "clearly via env.unwrapped.P."
                ),
                source_url="https://gymnasium.farama.org/v0.26.3/environments/toy_text/frozen_lake/",
                validation_note=(
                    "Gymnasium documents the slippery tile mechanics: each intended "
                    "direction has 1/3 probability; the two perpendicular directions "
                    "each also have 1/3 probability."
                ),
                is_inference=True,
            ),
        ),
    ),
    "dp_policy_eval": LessonVideoSpec(
        lesson_id="dp_policy_eval",
        title="Policy Evaluation",
        environment_name="FrozenLake",
        theory_equation=r"V^{\pi}(s)=\sum_a \pi(a|s)\sum_{s',r}p(s',r|s,a)\left[r+\gamma V^{\pi}(s')\right]",
        worked_example="Freeze one slippery FrozenLake state, show both branches of one action, then connect the full Bellman expectation sweep to the code loop.",
        code_focus_lines=(
            "for action, action_prob in enumerate(policy[state]):",
            "    for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:",
            "        new_value += action_prob * transition_prob * (reward + gamma * V[next_state])",
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
            "for action in range(env.action_space.n):",
            "    action_value = 0.0",
            "    for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:",
            "        action_value += transition_prob * (reward + gamma * V[next_state])",
            "    action_values.append(action_value)",
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
            "for action in range(env.action_space.n):",
            "    action_value = 0.0",
            "    for transition_prob, next_state, reward, done in env.unwrapped.P[state][action]:",
            "        action_value += transition_prob * (reward + gamma * V[next_state])",
            "    action_values.append(action_value)",
            "best_action = int(np.argmax(action_values))",
            "policy[state] = np.eye(env.action_space.n)[best_action]",
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
