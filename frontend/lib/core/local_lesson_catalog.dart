import 'lesson_models.dart';

const List<LessonSection> fallbackLessonSections = [
  LessonSection(
    title: 'Dynamic Programming',
    lessons: [
      LessonDefinition(
        id: 'dp_policy_eval',
        title: 'Policy Evaluation',
        description:
            'Evaluate a fixed policy over FrozenLake using Bellman expectation backups and iterative sweeps.',
        category: 'Dynamic Programming',
        starterCode: '''
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
''',
        conceptVideo: LessonConceptVideo(
          streamPath: '/media/concept-videos/dp_policy_eval_concept.mp4',
          durationLabel: '03:30',
          summary:
              'This lesson video slows down one Bellman expectation sweep over FrozenLake so the learner can read the equation, inspect the branches, and then map the full backup directly into code.',
          highlights: [
            'How a fixed policy weights each action.',
            'How transition probabilities and discounted future values combine.',
            'Why repeated sweeps converge to stable state values.',
          ],
        ),
        exercise: LessonExerciseBrief(
          title: 'Implement iterative policy evaluation',
          overview:
              'Complete the Bellman expectation update so each state value is replaced by the expected return under the supplied policy. The lesson video gives the conceptual walkthrough; this exercise asks you to express that reasoning in code.',
          tasks: [
            'Fill the expectation TODO block so it accumulates every policy-weighted transition branch.',
            'Replace the convergence placeholder with the updated state-value comparison.',
            'Keep the discounted future value at zero for terminal transitions.',
            'Use DISCOUNT_FACTOR in code when you want a different gamma.',
          ],
          templateBlanks: [
            LessonTemplateBlank(
              blankId: 'policy_eval_expectation',
              kind: 'block',
              prompt:
                  'Accumulate each action branch into the Bellman expectation update.',
              expectedConcept: 'Bellman expectation backup',
              approxLineAnchor: 11,
            ),
            LessonTemplateBlank(
              blankId: 'policy_eval_delta',
              kind: 'expression',
              prompt:
                  'Compare the previous value against the newly computed value in the convergence check.',
              expectedConcept: 'sweep convergence',
              approxLineAnchor: 13,
            ),
          ],
          successCriteria: [
            'The function computes the Bellman expectation update for every policy-weighted action branch.',
            'The convergence check uses the previous and updated state values.',
            'The function returns a value table that passes the sample lesson tests.',
          ],
          codeTip:
              'Set lesson configuration inside the code itself. For this lesson, the main editable constant is DISCOUNT_FACTOR at the top of the file.',
        ),
      ),
      LessonDefinition(
        id: 'dp_value_iteration',
        title: 'Value Iteration',
        description:
            'Compute optimal FrozenLake state values by repeatedly taking the best Bellman backup at each state.',
        category: 'Dynamic Programming',
        starterCode: '''
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
''',
        conceptVideo: LessonConceptVideo(
          streamPath: '/media/concept-videos/dp_value_iteration_concept.mp4',
          durationLabel: '03:20',
          summary:
              'The concept video compares FrozenLake action backups one at a time so the learner can follow why value iteration keeps the best action value instead of averaging under a policy.',
          highlights: [
            'How the environment branches for each action.',
            'Why the maximum action backup replaces the policy-weighted sum.',
            'How the optimal value function emerges across repeated sweeps.',
          ],
        ),
        exercise: LessonExerciseBrief(
          title: 'Implement Bellman optimality backups',
          overview:
              'Update each state by computing every action backup and keeping the maximum. The exercise mirrors the concept video, but now the student must express the optimality update directly in code.',
          tasks: [
            'Fill the action-backup TODO block for one action at a time.',
            'Replace the greedy-choice placeholder with the best action value expression.',
            'Preserve the discounted future value handling for terminal transitions.',
            'Use DISCOUNT_FACTOR in code when you want a different gamma.',
          ],
          templateBlanks: [
            LessonTemplateBlank(
              blankId: 'value_iteration_backup',
              kind: 'block',
              prompt:
                  'Compute one action backup from transition probabilities, rewards, and discounted future values.',
              expectedConcept: 'Bellman optimality backup',
              approxLineAnchor: 12,
            ),
            LessonTemplateBlank(
              blankId: 'value_iteration_best_action',
              kind: 'expression',
              prompt: 'Select the best action value for the current state.',
              expectedConcept: 'greedy max backup',
              approxLineAnchor: 14,
            ),
          ],
          successCriteria: [
            'Each action value is computed from all transition branches for that action.',
            'The state value is updated with the maximum action value.',
            'The returned value table passes the sample optimal-backup lesson test.',
          ],
          codeTip:
              'There is no slider for gamma anymore. Change DISCOUNT_FACTOR directly in the code to alter the backups.',
        ),
      ),
      LessonDefinition(
        id: 'dp_policy_improvement',
        title: 'Policy Improvement',
        description:
            'Turn a state-value table into a greedy FrozenLake policy by backing up each available action.',
        category: 'Dynamic Programming',
        starterCode: '''
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
''',
        conceptVideo: LessonConceptVideo(
          streamPath: '/media/concept-videos/dp_policy_improvement_concept.mp4',
          durationLabel: '03:00',
          summary:
              'This lesson focuses on one greedy improvement step: compare one-step lookahead returns at a FrozenLake state, then place all policy mass on the best action.',
          highlights: [
            'How the current value table scores each action.',
            'Why policy improvement uses argmax instead of an expectation.',
            'How the chosen action becomes a one-hot policy row.',
          ],
        ),
        exercise: LessonExerciseBrief(
          title: 'Implement greedy policy improvement',
          overview:
              'Build a greedy policy row for each state by evaluating every action backup against the current value table.',
          tasks: [
            'Fill the lookahead TODO block so each action receives its backup value.',
            'Replace the greedy-choice placeholder with the action index you want to keep.',
            'Keep the output as a one-hot policy row.',
            'Adjust DISCOUNT_FACTOR in code when you want a different improvement step.',
          ],
          templateBlanks: [
            LessonTemplateBlank(
              blankId: 'policy_improvement_backup',
              kind: 'block',
              prompt: 'Compute each action'
                  's one-step lookahead return from the value table.',
              expectedConcept: 'greedy policy backup',
              approxLineAnchor: 11,
            ),
            LessonTemplateBlank(
              blankId: 'policy_improvement_best_action',
              kind: 'expression',
              prompt:
                  'Choose the greedy action index from the action values list.',
              expectedConcept: 'argmax policy improvement',
              approxLineAnchor: 14,
            ),
          ],
          successCriteria: [
            'Each action score is computed from transition probabilities, rewards, and discounted future values.',
            'The selected action index is the greedy argmax over the action scores.',
            'Each output policy row remains one-hot and passes the sample lesson test.',
          ],
          codeTip:
              'Keep the output as a policy table. Each row should contain one 1.0 entry for the greedy action and 0.0 elsewhere.',
        ),
      ),
    ],
  ),
  LessonSection(
    title: 'Monte Carlo Methods',
    lessons: [
      LessonDefinition(
        id: 'mc_first_visit',
        title: 'First-Visit Monte Carlo',
        description:
            'Estimate Blackjack state values from complete episodes by updating only the first occurrence of each state.',
        category: 'Monte Carlo Methods',
        starterCode: '''
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
''',
        conceptVideo: LessonConceptVideo(
          streamPath: '/media/concept-videos/mc_first_visit_concept.mp4',
          durationLabel: '05:10',
          summary:
              'This lesson video follows one Blackjack episode from the initial hand to the terminal reward, then slowly walks through the first-visit return calculation and the dictionary-based value update.',
          highlights: [
            'Why Monte Carlo waits for the whole episode before updating.',
            'How the Blackjack state tuple becomes the key in the value table.',
            'How the discounted return becomes a first-visit value estimate.',
          ],
        ),
        exercise: LessonExerciseBrief(
          title: 'Implement first-visit return updates',
          overview:
              'Process an entire sampled Blackjack episode, compute the discounted return from the first occurrence of each state, and update the running averages in the value table.',
          tasks: [
            'Replace the repeated-state placeholder with the correct first-visit check.',
            'Fill the TODO block that accumulates the discounted return from the first visit onward.',
            'Keep the running average update over returns[state].',
            'Change EPISODE_COUNT or DISCOUNT_FACTOR at the top when exploring different rollouts.',
          ],
          templateBlanks: [
            LessonTemplateBlank(
              blankId: 'mc_first_visit_seen_state',
              kind: 'expression',
              prompt:
                  'Skip repeated states after their first occurrence in the episode.',
              expectedConcept: 'first-visit filtering',
              approxLineAnchor: 7,
            ),
            LessonTemplateBlank(
              blankId: 'mc_first_visit_return',
              kind: 'block',
              prompt:
                  'Compute the discounted return from the first-visit index to the end of the episode.',
              expectedConcept: 'Monte Carlo return accumulation',
              approxLineAnchor: 11,
            ),
          ],
          successCriteria: [
            'Repeated states are skipped after the first occurrence in the episode.',
            'The discounted return is accumulated from the first-visit index onward.',
            'The value table update passes the sample first-visit Monte Carlo test.',
          ],
          codeTip:
              'Blackjack states are observation tuples, so V and returns should be keyed by state rather than indexed by integer position.',
        ),
      ),
    ],
  ),
  LessonSection(
    title: 'Temporal Difference',
    lessons: [
      LessonDefinition(
        id: 'td_sarsa',
        title: 'SARSA',
        description:
            'Update CliffWalking action values with an on-policy TD target that uses the next sampled action.',
        category: 'Temporal Difference',
        starterCode: '''
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
''',
        conceptVideo: LessonConceptVideo(
          streamPath: '/media/concept-videos/td_sarsa_concept.mp4',
          durationLabel: '05:00',
          summary:
              'The lesson walkthrough keeps the sampled next action on screen in CliffWalking so the learner can see why SARSA is an on-policy update.',
          highlights: [
            'How the sampled next action enters the TD target.',
            'Why SARSA follows the same behaviour policy during learning.',
            'How alpha scales the change to one Q-value.',
          ],
        ),
        exercise: LessonExerciseBrief(
          title: 'Implement the SARSA update rule',
          overview:
              'Complete the on-policy TD update so the bootstrap term comes from the next sampled action rather than from a max over the next-state row.',
          tasks: [
            'Replace the bootstrap placeholder so it uses the sampled next action and a zero terminal bootstrap.',
            'Fill the TODO block that updates the selected Q-value toward the TD target.',
            'Keep the TD target definition that already uses reward plus the discounted bootstrap.',
            'Change LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, and EPISODE_COUNT in code when you want a different run.',
          ],
          templateBlanks: [
            LessonTemplateBlank(
              blankId: 'sarsa_bootstrap',
              kind: 'expression',
              prompt:
                  'Use the sampled next action for the bootstrap, with zero on terminal transitions.',
              expectedConcept: 'on-policy bootstrap',
              approxLineAnchor: 13,
            ),
            LessonTemplateBlank(
              blankId: 'sarsa_update_rule',
              kind: 'block',
              prompt: 'Apply the incremental SARSA update using the TD target.',
              expectedConcept: 'SARSA TD update',
              approxLineAnchor: 15,
            ),
          ],
          successCriteria: [
            'The bootstrap term uses the sampled next action, not a max over the row.',
            'Terminal transitions use a zero bootstrap.',
            'The updated Q-table passes the sample SARSA lesson test.',
          ],
          codeTip:
              'The key difference from Q-learning is the bootstrap term. Use the provided next_action rather than taking a max over the next-state row.',
        ),
      ),
      LessonDefinition(
        id: 'td_q_learning',
        title: 'Q-Learning',
        description:
            'Update CliffWalking action values with one-step TD targets over sampled transitions.',
        category: 'Temporal Difference',
        starterCode: '''
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
''',
        conceptVideo: LessonConceptVideo(
          streamPath: '/media/concept-videos/td_q_learning_concept.mp4',
          durationLabel: '04:40',
          summary:
              'The pre-rendered explainer synchronizes the CliffWalking transition, the highlighted update line, and the numeric TD target so the learner can see exactly how one Q-value changes.',
          highlights: [
            'How the sampled CliffWalking transition drives the update.',
            'Where the greedy max next-state value appears in the TD target.',
            'How alpha controls the size of the Q-value change.',
          ],
        ),
        exercise: LessonExerciseBrief(
          title: 'Implement the Q-learning update rule',
          overview:
              'Complete the one-step TD update that adjusts a single Q-value from a sampled transition. Your code should match the reasoning shown in the lesson video and in the generated step replay.',
          tasks: [
            'Replace the bootstrap placeholder with the greedy next-state value.',
            'Fill the TODO block that performs the incremental TD update.',
            'Keep the TD target expression that combines reward and discounted bootstrap.',
            'Change LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, and EPISODE_COUNT in code when you want a different run configuration.',
          ],
          templateBlanks: [
            LessonTemplateBlank(
              blankId: 'q_learning_best_next',
              kind: 'expression',
              prompt:
                  'Select the greedy bootstrap value from the next-state row of Q.',
              expectedConcept: 'max next-state bootstrap',
              approxLineAnchor: 7,
            ),
            LessonTemplateBlank(
              blankId: 'q_learning_update_rule',
              kind: 'block',
              prompt:
                  'Apply the incremental Q-learning update using alpha and the TD target.',
              expectedConcept: 'one-step TD update',
              approxLineAnchor: 9,
            ),
          ],
          successCriteria: [
            'The bootstrap term uses the maximum next-state action value.',
            'The chosen Q-value is updated incrementally toward the TD target.',
            'The function returns the updated Q-table and passes the sample lesson test.',
          ],
          codeTip:
              'The run configuration now lives in code constants. The backend reads LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, and EPISODE_COUNT from your submission.',
        ),
      ),
    ],
  ),
];
