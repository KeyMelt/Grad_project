import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'backend_api.dart';
import 'export_file_saver.dart';

enum RunStatus { idle, running, success, failed, stopped }

enum AppSection { home, workspace, flashcards, quiz, admin }

@immutable
class StudyFlashcard {
  final String term;
  final String category;
  final String explanation;

  const StudyFlashcard({
    required this.term,
    required this.category,
    required this.explanation,
  });
}

@immutable
class LessonConceptVideo {
  final String assetPath;
  final String durationLabel;
  final String summary;
  final List<String> highlights;

  const LessonConceptVideo({
    required this.assetPath,
    required this.durationLabel,
    required this.summary,
    required this.highlights,
  });

  LessonConceptVideo copyWith({
    String? assetPath,
    String? durationLabel,
    String? summary,
    List<String>? highlights,
  }) {
    return LessonConceptVideo(
      assetPath: assetPath ?? this.assetPath,
      durationLabel: durationLabel ?? this.durationLabel,
      summary: summary ?? this.summary,
      highlights: highlights ?? this.highlights,
    );
  }
}

@immutable
class LessonExerciseBrief {
  final String title;
  final String overview;
  final List<String> tasks;
  final List<String> successCriteria;
  final String codeTip;

  const LessonExerciseBrief({
    required this.title,
    required this.overview,
    required this.tasks,
    required this.successCriteria,
    required this.codeTip,
  });

  LessonExerciseBrief copyWith({
    String? title,
    String? overview,
    List<String>? tasks,
    List<String>? successCriteria,
    String? codeTip,
  }) {
    return LessonExerciseBrief(
      title: title ?? this.title,
      overview: overview ?? this.overview,
      tasks: tasks ?? this.tasks,
      successCriteria: successCriteria ?? this.successCriteria,
      codeTip: codeTip ?? this.codeTip,
    );
  }
}

@immutable
class LessonDefinition {
  final String id;
  final String title;
  final String description;
  final String category;
  final String starterCode;
  final LessonConceptVideo conceptVideo;
  final LessonExerciseBrief exercise;
  final bool backendEnabled;

  const LessonDefinition({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.starterCode,
    required this.conceptVideo,
    required this.exercise,
    this.backendEnabled = true,
  });

  bool get hasVideo => conceptVideo.assetPath.isNotEmpty;

  LessonDefinition copyWith({
    String? id,
    String? title,
    String? description,
    String? category,
    String? starterCode,
    LessonConceptVideo? conceptVideo,
    LessonExerciseBrief? exercise,
    bool? backendEnabled,
  }) {
    return LessonDefinition(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      category: category ?? this.category,
      starterCode: starterCode ?? this.starterCode,
      conceptVideo: conceptVideo ?? this.conceptVideo,
      exercise: exercise ?? this.exercise,
      backendEnabled: backendEnabled ?? this.backendEnabled,
    );
  }
}

@immutable
class LessonSection {
  final String title;
  final List<LessonDefinition> lessons;

  const LessonSection({
    required this.title,
    required this.lessons,
  });

  LessonSection copyWith({
    String? title,
    List<LessonDefinition>? lessons,
  }) {
    return LessonSection(
      title: title ?? this.title,
      lessons: lessons ?? this.lessons,
    );
  }
}

const List<LessonSection> _lessonSections = [
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
                for transition_prob, next_state, reward, done in env.P[state][action]:
                    future = 0.0 if done else V[next_state]
                    new_value += action_prob * transition_prob * (reward + gamma * future)
            V[state] = new_value
            delta = max(delta, abs(old_value - new_value))
    return V
''',
        conceptVideo: LessonConceptVideo(
          assetPath: 'assets/videos/dp_policy_eval_concept.mp4',
          durationLabel: '00:11',
          summary:
              'This lesson video walks through one Bellman expectation sweep with the FrozenLake grid, the update loop, and the numerical backup shown together.',
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
            'Keep the sweep over every state until the largest value change is smaller than theta.',
            'For each state, combine the policy probability and the environment transition probability for every possible outcome.',
            'Use the discounted future value for non-terminal transitions.',
            'Edit the code constants at the top when you want a different discount factor.',
          ],
          successCriteria: [
            'The function returns a value table that passes the sample Bellman backup checks.',
            'The backend step replay can show the grid state, code trace, and expectation equation for the generated run.',
            'The implementation remains inside the provided function signature.',
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
                for transition_prob, next_state, reward, done in env.P[state][action]:
                    future = 0.0 if done else V[next_state]
                    action_value += transition_prob * (reward + gamma * future)
                action_values.append(action_value)
            V[state] = max(action_values)
            delta = max(delta, abs(old_value - V[state]))
    return V
''',
        conceptVideo: LessonConceptVideo(
          assetPath: 'assets/videos/dp_value_iteration_concept.mp4',
          durationLabel: '00:07',
          summary:
              'The concept video contrasts action backups for the same state so the learner can see why value iteration keeps only the best action value.',
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
            'Loop over all available actions for each state.',
            'Compute the expected return for each action using transition probabilities and discounted future values.',
            'Choose the maximum action value and store it in the state value table.',
            'Use the DISCOUNT_FACTOR constant in the code when exploring different behaviours.',
          ],
          successCriteria: [
            'The returned value table passes the toy optimal-backup sample test.',
            'The generated replay shows which action won the backup for the highlighted state.',
            'The function preserves the supplied signature and returns the updated table.',
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
            for transition_prob, next_state, reward, done in env.P[state][action]:
                future = 0.0 if done else V[next_state]
                action_value += transition_prob * (reward + gamma * future)
            action_values.append(action_value)

        best_action = max(range(action_count), key=lambda index: action_values[index])
        policy[state][best_action] = 1.0

    return policy
''',
        conceptVideo: LessonConceptVideo(
          assetPath: 'assets/videos/dp_policy_improvement_concept.mp4',
          durationLabel: '00:10',
          summary:
              'This lesson focuses on one greedy improvement step: compare every action backup, then place all policy mass on the best action.',
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
            'Loop through all actions available in the current state.',
            'Compute each action backup from transition probabilities, rewards, and discounted future values.',
            'Choose the best action and write a one-hot policy row.',
            'Adjust DISCOUNT_FACTOR in code when you want a different improvement step.',
          ],
          successCriteria: [
            'The returned policy selects the greedy action in the sample test.',
            'Each policy row remains a valid one-hot distribution.',
            'The generated replay can tie the chosen action to the backup values that justified it.',
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
            'Estimate state values from complete episodes by updating only the first occurrence of each state.',
        category: 'Monte Carlo Methods',
        starterCode: '''
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
''',
        conceptVideo: LessonConceptVideo(
          assetPath: 'assets/videos/mc_first_visit_concept.mp4',
          durationLabel: '00:06',
          summary:
              'This lesson video follows one sampled episode from start to finish, then walks backward through the return calculation for the first visit of each state.',
          highlights: [
            'Why Monte Carlo waits for the whole episode before updating.',
            'How first-visit logic skips repeated states.',
            'How the discounted return becomes a value estimate.',
          ],
        ),
        exercise: LessonExerciseBrief(
          title: 'Implement first-visit return updates',
          overview:
              'Process an entire sampled episode, compute the discounted return from the first occurrence of each state, and update the running averages in the value table.',
          tasks: [
            'Track which states have already been updated in the current episode.',
            'Compute the discounted return from the first visit index to the end of the episode.',
            'Append the return to the state history and recompute the state average.',
            'Change EPISODE_COUNT or DISCOUNT_FACTOR at the top of the code to explore different rollouts.',
          ],
          successCriteria: [
            'The returned value table matches the expected first-visit test values.',
            'The replay shows a full sampled trajectory before the update step.',
            'Repeated states are skipped after their first occurrence.',
          ],
          codeTip:
              'This exercise uses DISCOUNT_FACTOR and EPISODE_COUNT constants from the code block rather than a separate parameter panel.',
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
            'Update tabular action values with an on-policy TD target that uses the next sampled action.',
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
    bootstrap = 0.0 if next_action is None else Q[next_state][next_action]
    td_target = reward + gamma * bootstrap
    Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])
    return Q
''',
        conceptVideo: LessonConceptVideo(
          assetPath: 'assets/videos/td_sarsa_concept.mp4',
          durationLabel: '00:11',
          summary:
              'The lesson walkthrough keeps the sampled next action on screen so the learner can see why SARSA is an on-policy update.',
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
            'Accept the sampled next action as part of the function input.',
            'Use a zero bootstrap when the transition is terminal.',
            'Build the TD target from reward plus the discounted next-action value.',
            'Change LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, and EPISODE_COUNT directly in code when you want a different run.',
          ],
          successCriteria: [
            'The update passes the sample SARSA test case.',
            'The replay identifies the sampled next action used in the bootstrap.',
            'The function returns the updated Q-table without changing the required signature.',
          ],
          codeTip:
              'The key difference from Q-learning is the bootstrap term. Use the provided next_action rather than taking a max over the next-state row.',
        ),
      ),
      LessonDefinition(
        id: 'td_q_learning',
        title: 'Q-Learning',
        description:
            'Update tabular action values with one-step TD targets over FrozenLake transitions.',
        category: 'Temporal Difference',
        starterCode: '''
LEARNING_RATE = 0.10
DISCOUNT_FACTOR = 0.95
EXPLORATION_RATE = 0.20
EPISODE_COUNT = 6

def q_learning_update(Q, state, action, reward, next_state, alpha=LEARNING_RATE, gamma=DISCOUNT_FACTOR):
    best_next_value = max(Q[next_state])
    td_target = reward + gamma * best_next_value
    Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])
    return Q
''',
        conceptVideo: LessonConceptVideo(
          assetPath: 'assets/videos/td_q_learning_concept.mp4',
          durationLabel: '00:07',
          summary:
              'The pre-rendered explainer synchronizes the agent move, the highlighted update line, and the numeric TD target so the learner can see exactly how one Q-value changes.',
          highlights: [
            'How the sampled FrozenLake transition drives the update.',
            'Where the max next-state value appears in the TD target.',
            'How alpha controls the size of the Q-value change.',
          ],
        ),
        exercise: LessonExerciseBrief(
          title: 'Implement the Q-learning update rule',
          overview:
              'Complete the one-step TD update that adjusts a single Q-value from a sampled transition. Your code should match the reasoning shown in the lesson video and in the generated step replay.',
          tasks: [
            'Find the best next-state action value using the next-state row of the Q-table.',
            'Build the TD target from the immediate reward and the discounted bootstrap value.',
            'Apply the incremental update using the learning-rate constant at the top of the file.',
            'Change LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, and EPISODE_COUNT directly in the code when you want a different run configuration.',
          ],
          successCriteria: [
            'The Q-value update passes the provided TD sample test.',
            'The generated replay shows the sampled transition probability, the update line, and the numeric TD target together.',
            'The function returns the updated Q-table without changing the required signature.',
          ],
          codeTip:
              'The run configuration now lives in code constants. The backend reads LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, and EPISODE_COUNT from your submission.',
        ),
      ),
    ],
  ),
];

const List<StudyFlashcard> _studyFlashcards = [
  StudyFlashcard(
    term: 'Bellman Expectation',
    category: 'Dynamic Programming',
    explanation:
        'Policy evaluation updates each state with an expectation over policy choices and transition probabilities.',
  ),
  StudyFlashcard(
    term: 'Bellman Optimality',
    category: 'Dynamic Programming',
    explanation:
        'Value iteration selects the largest action backup instead of averaging under a fixed policy.',
  ),
  StudyFlashcard(
    term: 'Policy Improvement',
    category: 'Dynamic Programming',
    explanation:
        'Policy improvement chooses the greedy action for each state using the current value table.',
  ),
  StudyFlashcard(
    term: 'First-Visit Return',
    category: 'Monte Carlo Methods',
    explanation:
        'First-visit Monte Carlo updates a state only once per episode, using the full discounted return from its first occurrence.',
  ),
  StudyFlashcard(
    term: 'SARSA',
    category: 'Temporal Difference',
    explanation:
        'SARSA is on-policy because its TD target uses the next action that the behaviour policy actually sampled.',
  ),
  StudyFlashcard(
    term: 'TD Target',
    category: 'Temporal Difference',
    explanation:
        'The Q-learning target is the immediate reward plus gamma times the best next-state value.',
  ),
  StudyFlashcard(
    term: 'Transition Probability',
    category: 'Environment Model',
    explanation:
        'Transition probability tells us how likely the environment is to move to a particular next state after a chosen action.',
  ),
  StudyFlashcard(
    term: 'Normalized Gain',
    category: 'Assessment',
    explanation:
        'N-gain measures conceptual growth as (post - pre) / (100 - pre).',
  ),
];

const Object _sentinel = Object();

@immutable
class RLWorkbenchState {
  final List<LessonSection> sections;
  final List<StudyFlashcard> flashcards;
  final AppSection currentSection;
  final LearnerProfile? learner;
  final LearnerProgress progress;
  final bool isSigningIn;
  final bool isQuizLoading;
  final String homeMessage;
  final String quizStatusMessage;
  final QuizSessionData? activeQuiz;
  final Map<String, int> quizAnswers;
  final QuizAttemptSummary? lastQuizSummary;
  final LessonDefinition selectedLesson;
  final String code;
  final String? workspaceSessionId;
  final bool workspaceReady;
  final WorkspaceConnectionStatus editorConnectionStatus;
  final WorkspaceConnectionStatus consoleConnectionStatus;
  final String? activeRunId;
  final String runOutputBuffer;
  final int scriptVersion;
  final RunStatus runStatus;
  final int currentEpisode;
  final int currentStep;
  final double totalReward;
  final double averageReward;
  final double bestEpisodeReward;
  final String statusMessage;
  final String videoPath;
  final List<ExecutionTestCaseResult> testResults;
  final List<ExecutionTraceStep> stepTrace;
  final bool sidebarVisible;
  final String? adminSelectedLessonId;
  final String adminMessage;
  final bool isAdminExporting;

  const RLWorkbenchState({
    required this.sections,
    required this.flashcards,
    required this.currentSection,
    required this.learner,
    required this.progress,
    required this.isSigningIn,
    required this.isQuizLoading,
    required this.homeMessage,
    required this.quizStatusMessage,
    required this.activeQuiz,
    required this.quizAnswers,
    required this.lastQuizSummary,
    required this.selectedLesson,
    required this.code,
    required this.workspaceSessionId,
    required this.workspaceReady,
    required this.editorConnectionStatus,
    required this.consoleConnectionStatus,
    required this.activeRunId,
    required this.runOutputBuffer,
    required this.scriptVersion,
    required this.runStatus,
    required this.currentEpisode,
    required this.currentStep,
    required this.totalReward,
    required this.averageReward,
    required this.bestEpisodeReward,
    required this.statusMessage,
    required this.videoPath,
    required this.testResults,
    required this.stepTrace,
    required this.sidebarVisible,
    required this.adminSelectedLessonId,
    required this.adminMessage,
    required this.isAdminExporting,
  });

  factory RLWorkbenchState.initial() {
    final selectedLesson = _lessonSections.first.lessons.first;
    return RLWorkbenchState(
      sections: _lessonSections,
      flashcards: _studyFlashcards,
      currentSection: AppSection.home,
      learner: null,
      progress: const LearnerProgress.empty(),
      isSigningIn: false,
      isQuizLoading: false,
      homeMessage: 'Sign in to save quiz results and lesson progress.',
      quizStatusMessage:
          'Take a randomized pre-test before you begin the lessons.',
      activeQuiz: null,
      quizAnswers: const {},
      lastQuizSummary: null,
      selectedLesson: selectedLesson,
      code: selectedLesson.starterCode,
      workspaceSessionId: null,
      workspaceReady: false,
      editorConnectionStatus: WorkspaceConnectionStatus.disconnected,
      consoleConnectionStatus: WorkspaceConnectionStatus.disconnected,
      activeRunId: null,
      runOutputBuffer: '',
      scriptVersion: 1,
      runStatus: RunStatus.idle,
      currentEpisode: 0,
      currentStep: 0,
      totalReward: 0.0,
      averageReward: 0.0,
      bestEpisodeReward: 0.0,
      statusMessage: 'Ready to run ${selectedLesson.title}.',
      videoPath: '',
      testResults: const [],
      stepTrace: const [],
      sidebarVisible: true,
      adminSelectedLessonId: selectedLesson.id,
      adminMessage: 'Edit lessons in this session.',
      isAdminExporting: false,
    );
  }

  String get runStatusLabel {
    switch (runStatus) {
      case RunStatus.idle:
        return 'Idle';
      case RunStatus.running:
        return 'Running';
      case RunStatus.success:
        return 'Complete';
      case RunStatus.failed:
        return 'Failed';
      case RunStatus.stopped:
        return 'Stopped';
    }
  }

  RLWorkbenchState copyWith({
    List<LessonSection>? sections,
    List<StudyFlashcard>? flashcards,
    AppSection? currentSection,
    Object? learner = _sentinel,
    LearnerProgress? progress,
    bool? isSigningIn,
    bool? isQuizLoading,
    String? homeMessage,
    String? quizStatusMessage,
    Object? activeQuiz = _sentinel,
    Map<String, int>? quizAnswers,
    Object? lastQuizSummary = _sentinel,
    LessonDefinition? selectedLesson,
    String? code,
    Object? workspaceSessionId = _sentinel,
    bool? workspaceReady,
    WorkspaceConnectionStatus? editorConnectionStatus,
    WorkspaceConnectionStatus? consoleConnectionStatus,
    Object? activeRunId = _sentinel,
    String? runOutputBuffer,
    int? scriptVersion,
    RunStatus? runStatus,
    int? currentEpisode,
    int? currentStep,
    double? totalReward,
    double? averageReward,
    double? bestEpisodeReward,
    String? statusMessage,
    String? videoPath,
    List<ExecutionTestCaseResult>? testResults,
    List<ExecutionTraceStep>? stepTrace,
    bool? sidebarVisible,
    Object? adminSelectedLessonId = _sentinel,
    String? adminMessage,
    bool? isAdminExporting,
  }) {
    return RLWorkbenchState(
      sections: sections ?? this.sections,
      flashcards: flashcards ?? this.flashcards,
      currentSection: currentSection ?? this.currentSection,
      learner: identical(learner, _sentinel)
          ? this.learner
          : learner as LearnerProfile?,
      progress: progress ?? this.progress,
      isSigningIn: isSigningIn ?? this.isSigningIn,
      isQuizLoading: isQuizLoading ?? this.isQuizLoading,
      homeMessage: homeMessage ?? this.homeMessage,
      quizStatusMessage: quizStatusMessage ?? this.quizStatusMessage,
      activeQuiz: identical(activeQuiz, _sentinel)
          ? this.activeQuiz
          : activeQuiz as QuizSessionData?,
      quizAnswers: quizAnswers ?? this.quizAnswers,
      lastQuizSummary: identical(lastQuizSummary, _sentinel)
          ? this.lastQuizSummary
          : lastQuizSummary as QuizAttemptSummary?,
      selectedLesson: selectedLesson ?? this.selectedLesson,
      code: code ?? this.code,
      workspaceSessionId: identical(workspaceSessionId, _sentinel)
          ? this.workspaceSessionId
          : workspaceSessionId as String?,
      workspaceReady: workspaceReady ?? this.workspaceReady,
      editorConnectionStatus:
          editorConnectionStatus ?? this.editorConnectionStatus,
      consoleConnectionStatus:
          consoleConnectionStatus ?? this.consoleConnectionStatus,
      activeRunId: identical(activeRunId, _sentinel)
          ? this.activeRunId
          : activeRunId as String?,
      runOutputBuffer: runOutputBuffer ?? this.runOutputBuffer,
      scriptVersion: scriptVersion ?? this.scriptVersion,
      runStatus: runStatus ?? this.runStatus,
      currentEpisode: currentEpisode ?? this.currentEpisode,
      currentStep: currentStep ?? this.currentStep,
      totalReward: totalReward ?? this.totalReward,
      averageReward: averageReward ?? this.averageReward,
      bestEpisodeReward: bestEpisodeReward ?? this.bestEpisodeReward,
      statusMessage: statusMessage ?? this.statusMessage,
      videoPath: videoPath ?? this.videoPath,
      testResults: testResults ?? this.testResults,
      stepTrace: stepTrace ?? this.stepTrace,
      sidebarVisible: sidebarVisible ?? this.sidebarVisible,
      adminSelectedLessonId: identical(adminSelectedLessonId, _sentinel)
          ? this.adminSelectedLessonId
          : adminSelectedLessonId as String?,
      adminMessage: adminMessage ?? this.adminMessage,
      isAdminExporting: isAdminExporting ?? this.isAdminExporting,
    );
  }
}

class RLWorkbenchCubit extends Cubit<RLWorkbenchState> {
  RLWorkbenchCubit({
    BackendApi? api,
  })  : _api = api ?? HttpBackendApi(),
        super(RLWorkbenchState.initial()) {
    if (state.selectedLesson.backendEnabled) {
      unawaited(
          _attachWorkspaceSession(state.selectedLesson, announceStatus: false));
    }
  }

  final BackendApi _api;
  String? _activeTaskId;
  String? _activeWorkspaceRunId;

  BackendApi get api => _api;

  void navigateTo(AppSection section) {
    emit(state.copyWith(currentSection: section));
  }

  void toggleSidebar() {
    emit(state.copyWith(sidebarVisible: !state.sidebarVisible));
  }

  Future<void> signIn(String displayName, String password) async {
    final normalizedName = displayName.trim();
    if (normalizedName.isEmpty) {
      emit(state.copyWith(homeMessage: 'Enter a student name to continue.'));
      return;
    }
    if (password.trim().isEmpty) {
      emit(state.copyWith(homeMessage: 'Enter your password to continue.'));
      return;
    }

    emit(state.copyWith(
      isSigningIn: true,
      homeMessage: 'Signing in $normalizedName...',
    ));

    try {
      final dashboard = await _api.signIn(
        displayName: normalizedName,
        password: password,
      );
      emit(
        state.copyWith(
          learner: dashboard.student,
          progress: dashboard.progress,
          isSigningIn: false,
          homeMessage: 'Signed in as ${dashboard.student.displayName}.',
          quizStatusMessage: _quizPromptForProgress(dashboard.progress),
          currentSection: AppSection.home,
        ),
      );
    } on BackendApiException catch (error) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: error.message,
      ));
    } catch (_) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: 'Backend unavailable. Start FastAPI and try again.',
      ));
    }
  }

  void signOut() {
    _activeTaskId = null;
    _activeWorkspaceRunId = null;
    emit(
      state.copyWith(
        learner: null,
        progress: const LearnerProgress.empty(),
        activeQuiz: null,
        quizAnswers: const {},
        lastQuizSummary: null,
        isQuizLoading: false,
        currentSection: AppSection.home,
        homeMessage:
            'Signed out. Sign in to save quiz results and lesson progress.',
        quizStatusMessage:
            'Take a randomized pre-test before you begin the lessons.',
        workspaceSessionId: null,
        workspaceReady: false,
        editorConnectionStatus: WorkspaceConnectionStatus.disconnected,
        consoleConnectionStatus: WorkspaceConnectionStatus.disconnected,
        activeRunId: null,
        runOutputBuffer: '',
        scriptVersion: 1,
      ),
    );
  }

  Future<void> refreshDashboard({bool quiet = false}) async {
    final learner = state.learner;
    if (learner == null) {
      return;
    }

    try {
      final dashboard = await _api.getDashboard(studentId: learner.id);
      final nextState = quiet
          ? state.copyWith(
              learner: dashboard.student,
              progress: dashboard.progress,
              quizStatusMessage: _quizPromptForProgress(dashboard.progress),
            )
          : state.copyWith(
              learner: dashboard.student,
              progress: dashboard.progress,
              homeMessage: 'Progress updated.',
              quizStatusMessage: _quizPromptForProgress(dashboard.progress),
            );
      emit(nextState);
    } on BackendApiException catch (error) {
      if (!quiet) {
        emit(state.copyWith(homeMessage: error.message));
      }
    }
  }

  void openLesson(LessonDefinition lesson) {
    _activeTaskId = null;
    _activeWorkspaceRunId = null;
    final preserveWorkspace = state.selectedLesson.id == lesson.id &&
        state.workspaceSessionId != null;
    emit(
      state.copyWith(
        selectedLesson: lesson,
        code: preserveWorkspace ? state.code : lesson.starterCode,
        currentSection: AppSection.workspace,
        workspaceSessionId: preserveWorkspace ? state.workspaceSessionId : null,
        workspaceReady: preserveWorkspace ? state.workspaceReady : false,
        editorConnectionStatus: preserveWorkspace
            ? state.editorConnectionStatus
            : lesson.backendEnabled
                ? WorkspaceConnectionStatus.connecting
                : WorkspaceConnectionStatus.disconnected,
        consoleConnectionStatus: preserveWorkspace
            ? state.consoleConnectionStatus
            : lesson.backendEnabled
                ? WorkspaceConnectionStatus.connecting
                : WorkspaceConnectionStatus.disconnected,
        activeRunId: null,
        runOutputBuffer: '',
        scriptVersion: preserveWorkspace ? state.scriptVersion : 1,
        runStatus: RunStatus.idle,
        currentEpisode: 0,
        currentStep: 0,
        totalReward: 0.0,
        averageReward: 0.0,
        bestEpisodeReward: 0.0,
        videoPath: '',
        testResults: const [],
        stepTrace: const [],
        statusMessage: preserveWorkspace
            ? state.statusMessage
            : lesson.backendEnabled
                ? 'Ready to run ${lesson.title}.'
                : '${lesson.title} is draft-only.',
      ),
    );
    if (lesson.backendEnabled && !preserveWorkspace) {
      unawaited(_attachWorkspaceSession(lesson));
    }
  }

  void selectLesson(LessonDefinition lesson) {
    if (state.selectedLesson.id == lesson.id) {
      return;
    }

    openLesson(lesson);
  }

  void updateCode(String value) {
    emit(state.copyWith(code: value));
    final sessionId = state.workspaceSessionId;
    if (sessionId != null) {
      unawaited(_syncWorkspaceCode(sessionId, value));
    }
  }

  Future<void> startQuiz(QuizPhase phase) async {
    final learner = state.learner;
    if (learner == null) {
      emit(
        state.copyWith(
          currentSection: AppSection.home,
          homeMessage: 'Sign in first to save quiz scores.',
        ),
      );
      return;
    }

    if (phase == QuizPhase.posttest && state.progress.successfulRuns == 0) {
      emit(
        state.copyWith(
          currentSection: AppSection.quiz,
          quizStatusMessage:
              'Complete at least one lesson run before taking the post-test.',
        ),
      );
      return;
    }

    emit(
      state.copyWith(
        currentSection: AppSection.quiz,
        isQuizLoading: true,
        activeQuiz: null,
        lastQuizSummary: null,
        quizAnswers: const {},
        quizStatusMessage:
            'Preparing ${quizPhaseLabel(phase).toLowerCase()}...',
      ),
    );

    try {
      final session = await _api.startQuiz(
        studentId: learner.id,
        phase: phase,
      );
      emit(
        state.copyWith(
          isQuizLoading: false,
          activeQuiz: session,
          lastQuizSummary: null,
          quizAnswers: const {},
          quizStatusMessage: '${quizPhaseLabel(session.phase)} is ready.',
        ),
      );
    } on BackendApiException catch (error) {
      emit(
        state.copyWith(
          isQuizLoading: false,
          quizStatusMessage: error.message,
        ),
      );
    } catch (_) {
      emit(
        state.copyWith(
          isQuizLoading: false,
          quizStatusMessage: 'Could not start quiz. Check backend.',
        ),
      );
    }
  }

  void answerQuizQuestion(String questionId, int selectedIndex) {
    final updatedAnswers = Map<String, int>.from(state.quizAnswers)
      ..[questionId] = selectedIndex;
    emit(state.copyWith(quizAnswers: updatedAnswers));
  }

  Future<void> submitQuiz() async {
    final learner = state.learner;
    final activeQuiz = state.activeQuiz;
    if (learner == null || activeQuiz == null) {
      return;
    }

    if (state.quizAnswers.length < activeQuiz.questions.length) {
      emit(
        state.copyWith(
          quizStatusMessage: 'Answer all questions before submit.',
        ),
      );
      return;
    }

    emit(
      state.copyWith(
        isQuizLoading: true,
        quizStatusMessage: 'Submitting quiz...',
      ),
    );

    try {
      final summary = await _api.submitQuiz(
        studentId: learner.id,
        sessionId: activeQuiz.sessionId,
        answers: state.quizAnswers,
      );
      emit(
        state.copyWith(
          isQuizLoading: false,
          progress: summary.progress,
          activeQuiz: null,
          quizAnswers: const {},
          lastQuizSummary: summary,
          quizStatusMessage:
              'Submitted. Score: ${summary.score}/${summary.totalQuestions}.',
        ),
      );
    } on BackendApiException catch (error) {
      emit(
        state.copyWith(
          isQuizLoading: false,
          quizStatusMessage: error.message,
        ),
      );
    } catch (_) {
      emit(
        state.copyWith(
          isQuizLoading: false,
          quizStatusMessage: 'Could not submit quiz. Check backend.',
        ),
      );
    }
  }

  Future<void> run() async {
    await runWorkspace();
  }

  Future<void> runWorkspace() async {
    final sessionId = await _ensureWorkspaceSession();
    if (sessionId == null) {
      emit(
        state.copyWith(
          statusMessage: 'Workspace runtime is not ready for this lesson.',
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
        ),
      );
      return;
    }

    emit(
      state.copyWith(
        currentSection: AppSection.workspace,
        statusMessage: 'Running script.py in the workspace...',
        editorConnectionStatus: WorkspaceConnectionStatus.ready,
        consoleConnectionStatus: WorkspaceConnectionStatus.ready,
      ),
    );

    try {
      final run = await _api.runWorkspaceScript(sessionId: sessionId);
      _activeWorkspaceRunId = run.runId;
      emit(
        state.copyWith(
          activeRunId: run.runId,
          statusMessage: 'Workspace run ${run.runId} started.',
        ),
      );
      await _pollWorkspaceRun(sessionId, run.runId);
    } on BackendApiException catch (error) {
      _activeWorkspaceRunId = null;
      emit(
        state.copyWith(
          activeRunId: null,
          statusMessage: error.message,
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
        ),
      );
    } catch (_) {
      _activeWorkspaceRunId = null;
      emit(
        state.copyWith(
          activeRunId: null,
          statusMessage:
              'Workspace runtime unavailable at $defaultBackendBaseUrl.',
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
        ),
      );
    }
  }

  Future<void> submit() async {
    if (!state.selectedLesson.backendEnabled) {
      emit(
        state.copyWith(
          runStatus: RunStatus.failed,
          statusMessage: 'This lesson is draft-only.',
        ),
      );
      return;
    }

    final submissionCode = await _latestSubmissionCode();
    if (submissionCode.trim().isEmpty) {
      emit(
        _resetProgressState(
          'Add code before running ${state.selectedLesson.title}.',
        ),
      );
      return;
    }

    emit(
      state.copyWith(
        currentSection: AppSection.workspace,
        runStatus: RunStatus.running,
        currentEpisode: 0,
        currentStep: _nonEmptyLineCount(submissionCode),
        totalReward: 0.0,
        averageReward: 0.0,
        bestEpisodeReward: 0.0,
        videoPath: '',
        testResults: const [],
        stepTrace: const [],
        statusMessage:
            'Submitting ${state.selectedLesson.title} for grading...',
      ),
    );

    try {
      final task = await _api.submitCode(
        lessonId: state.selectedLesson.id,
        code: submissionCode,
        studentId: state.learner?.id,
      );
      _activeTaskId = task.taskId;
      emit(
        state.copyWith(
          statusMessage: 'Queued. Task ${task.taskId}.',
        ),
      );

      await _pollUntilComplete(task.taskId);
    } on BackendApiException catch (error) {
      _activeTaskId = null;
      emit(
        state.copyWith(
          runStatus: RunStatus.failed,
          currentEpisode: 0,
          currentStep: 0,
          totalReward: 0.0,
          averageReward: 0.0,
          bestEpisodeReward: 0.0,
          videoPath: '',
          testResults: error.testResults,
          stepTrace: const [],
          statusMessage: error.message,
        ),
      );
    } catch (_) {
      _activeTaskId = null;
      emit(
        state.copyWith(
          runStatus: RunStatus.failed,
          currentEpisode: 0,
          currentStep: 0,
          totalReward: 0.0,
          averageReward: 0.0,
          bestEpisodeReward: 0.0,
          videoPath: '',
          testResults: const [],
          stepTrace: const [],
          statusMessage: 'Backend unavailable at $defaultBackendBaseUrl.',
        ),
      );
    }
  }

  void stop() {
    if (state.runStatus == RunStatus.idle && _activeWorkspaceRunId == null) {
      return;
    }

    _activeTaskId = null;
    _activeWorkspaceRunId = null;
    emit(
      state.copyWith(
        activeRunId: null,
        runStatus: RunStatus.stopped,
        statusMessage:
            'Stopped monitoring the current run. Background execution may continue.',
      ),
    );
  }

  void reset() {
    _activeTaskId = null;
    _activeWorkspaceRunId = null;
    emit(
      state.copyWith(
        code: state.selectedLesson.starterCode,
        activeRunId: null,
        runOutputBuffer: '',
        scriptVersion: 1,
        runStatus: RunStatus.idle,
        currentEpisode: 0,
        currentStep: 0,
        totalReward: 0.0,
        averageReward: 0.0,
        bestEpisodeReward: 0.0,
        videoPath: '',
        testResults: const [],
        stepTrace: const [],
        statusMessage:
            'Reset ${state.selectedLesson.title} to its starter template.',
      ),
    );
    final sessionId = state.workspaceSessionId;
    if (sessionId != null) {
      unawaited(
          _syncWorkspaceCode(sessionId, state.selectedLesson.starterCode));
    }
  }

  void selectAdminLesson(String lessonId) {
    emit(
      state.copyWith(
        currentSection: AppSection.admin,
        adminSelectedLessonId: lessonId,
      ),
    );
  }

  void createDraftLesson() {
    final draftId = 'draft_${DateTime.now().millisecondsSinceEpoch}';
    final draftLesson = LessonDefinition(
      id: draftId,
      title: 'New Draft Lesson',
      description: 'Draft lesson content awaiting instructional copy.',
      category: 'Studio Drafts',
      starterCode: '''
# Draft lessons are content-only until a backend lesson id is wired.
DISCOUNT_FACTOR = 0.95

def lesson_function(*args, **kwargs):
    return None
''',
      conceptVideo: const LessonConceptVideo(
        assetPath: 'assets/videos/draft_placeholder.mp4',
        durationLabel: '00:45',
        summary: 'Add a concept video.',
        highlights: [
          'Key environment visual',
          'Key code trace',
          'Key math step',
        ],
      ),
      exercise: const LessonExerciseBrief(
        title: 'Describe the coding task',
        overview: 'Describe what the learner should implement.',
        tasks: [
          'Add the coding goal.',
          'Add the implementation steps.',
          'Add the success criteria.',
        ],
        successCriteria: [
          'A learner can tell what to write.',
          'A learner can tell when the solution is correct.',
        ],
        codeTip: 'Update starter code and constants here.',
      ),
      backendEnabled: false,
    );

    final sections = _upsertLessonInSections(state.sections, draftLesson);
    emit(
      state.copyWith(
        sections: sections,
        adminSelectedLessonId: draftId,
        adminMessage: 'Draft lesson created.',
      ),
    );
  }

  void saveAdminLesson({
    required String lessonId,
    required String title,
    required String category,
    required String description,
    required String conceptVideoAssetPath,
    required String conceptVideoDuration,
    required String conceptVideoSummary,
    required List<String> conceptHighlights,
    required String exerciseTitle,
    required String exerciseOverview,
    required List<String> exerciseTasks,
    required List<String> successCriteria,
    required String codeTip,
    required String starterCode,
    required bool backendEnabled,
  }) {
    final existingLesson = _findLessonById(state.sections, lessonId);
    if (existingLesson == null) {
      emit(state.copyWith(
        adminMessage: 'Could not find lesson $lessonId to update.',
      ));
      return;
    }

    final updatedLesson = existingLesson.copyWith(
      title: title.trim().isEmpty ? existingLesson.title : title.trim(),
      category:
          category.trim().isEmpty ? existingLesson.category : category.trim(),
      description: description.trim().isEmpty
          ? existingLesson.description
          : description.trim(),
      starterCode:
          starterCode.trim().isEmpty ? existingLesson.starterCode : starterCode,
      backendEnabled: backendEnabled,
      conceptVideo: existingLesson.conceptVideo.copyWith(
        assetPath: conceptVideoAssetPath.trim().isEmpty
            ? existingLesson.conceptVideo.assetPath
            : conceptVideoAssetPath.trim(),
        durationLabel: conceptVideoDuration.trim().isEmpty
            ? existingLesson.conceptVideo.durationLabel
            : conceptVideoDuration.trim(),
        summary: conceptVideoSummary.trim().isEmpty
            ? existingLesson.conceptVideo.summary
            : conceptVideoSummary.trim(),
        highlights: conceptHighlights.isEmpty
            ? existingLesson.conceptVideo.highlights
            : conceptHighlights,
      ),
      exercise: existingLesson.exercise.copyWith(
        title: exerciseTitle.trim().isEmpty
            ? existingLesson.exercise.title
            : exerciseTitle.trim(),
        overview: exerciseOverview.trim().isEmpty
            ? existingLesson.exercise.overview
            : exerciseOverview.trim(),
        tasks: exerciseTasks.isEmpty
            ? existingLesson.exercise.tasks
            : exerciseTasks,
        successCriteria: successCriteria.isEmpty
            ? existingLesson.exercise.successCriteria
            : successCriteria,
        codeTip: codeTip.trim().isEmpty
            ? existingLesson.exercise.codeTip
            : codeTip.trim(),
      ),
    );

    final updatedSections =
        _upsertLessonInSections(state.sections, updatedLesson);
    final selectedLesson = state.selectedLesson.id == updatedLesson.id
        ? updatedLesson
        : state.selectedLesson;

    emit(
      state.copyWith(
        sections: updatedSections,
        selectedLesson: selectedLesson,
        code: state.selectedLesson.id == updatedLesson.id
            ? updatedLesson.starterCode
            : state.code,
        adminSelectedLessonId: updatedLesson.id,
        adminMessage: 'Saved "${updatedLesson.title}".',
      ),
    );
  }

  void deleteAdminLesson(String lessonId) {
    if (_isCoreLessonId(lessonId)) {
      emit(
        state.copyWith(
          adminMessage:
              'Core lessons are locked and cannot be deleted from the studio.',
        ),
      );
      return;
    }

    var lessonFound = false;
    final updatedSections = <LessonSection>[];

    for (final section in state.sections) {
      final remainingLessons = section.lessons.where((lesson) {
        final keep = lesson.id != lessonId;
        if (!keep) {
          lessonFound = true;
        }
        return keep;
      }).toList(growable: false);

      if (remainingLessons.isNotEmpty) {
        updatedSections.add(section.copyWith(lessons: remainingLessons));
      }
    }

    if (!lessonFound) {
      emit(
        state.copyWith(
          adminMessage: 'Could not find lesson $lessonId to delete.',
        ),
      );
      return;
    }

    final fallbackLesson = updatedSections.first.lessons.first;
    final selectedLesson = state.selectedLesson.id == lessonId
        ? fallbackLesson
        : state.selectedLesson;

    emit(
      state.copyWith(
        sections: updatedSections,
        selectedLesson: selectedLesson,
        code: state.selectedLesson.id == lessonId
            ? fallbackLesson.starterCode
            : state.code,
        adminSelectedLessonId: state.adminSelectedLessonId == lessonId
            ? fallbackLesson.id
            : state.adminSelectedLessonId,
        adminMessage: 'Deleted lesson $lessonId from this session.',
      ),
    );
  }

  Future<void> exportAdminNGainMetrics() async {
    emit(
      state.copyWith(
        isAdminExporting: true,
        adminMessage: 'Exporting N-gain metrics to Excel...',
      ),
    );

    try {
      final export = await _api.exportNGainMetrics();
      final saveResult = await saveExportFile(
        fileName: export.fileName,
        bytes: export.bytes,
      );

      emit(
        state.copyWith(
          isAdminExporting: false,
          adminMessage: saveResult.success
              ? '${saveResult.message} ${saveResult.savedPath ?? ''}'.trim()
              : saveResult.message,
        ),
      );
    } on BackendApiException catch (error) {
      emit(
        state.copyWith(
          isAdminExporting: false,
          adminMessage: error.message,
        ),
      );
    } catch (_) {
      emit(
        state.copyWith(
          isAdminExporting: false,
          adminMessage: 'Could not export metrics. Check backend.',
        ),
      );
    }
  }

  Future<String?> _ensureWorkspaceSession() async {
    final existingSessionId = state.workspaceSessionId;
    if (existingSessionId != null && state.workspaceReady) {
      return existingSessionId;
    }

    if (!state.selectedLesson.backendEnabled) {
      return null;
    }

    await _attachWorkspaceSession(state.selectedLesson);
    return state.workspaceSessionId;
  }

  Future<void> _attachWorkspaceSession(
    LessonDefinition lesson, {
    bool announceStatus = true,
  }) async {
    final requestedLessonId = lesson.id;
    final showProgress =
        announceStatus || state.currentSection == AppSection.workspace;
    emit(
      state.copyWith(
        workspaceReady: false,
        editorConnectionStatus: WorkspaceConnectionStatus.connecting,
        consoleConnectionStatus: WorkspaceConnectionStatus.connecting,
        statusMessage: showProgress
            ? 'Preparing workspace for ${lesson.title}...'
            : state.statusMessage,
      ),
    );

    try {
      final session =
          await _api.createWorkspaceSession(lessonId: requestedLessonId);
      final file = await _api.getWorkspaceFile(sessionId: session.sessionId);
      if (isClosed || state.selectedLesson.id != requestedLessonId) {
        return;
      }

      emit(
        state.copyWith(
          code: file.content,
          workspaceSessionId: session.sessionId,
          workspaceReady: true,
          editorConnectionStatus: WorkspaceConnectionStatus.ready,
          consoleConnectionStatus: session.consoleReady
              ? WorkspaceConnectionStatus.ready
              : WorkspaceConnectionStatus.connecting,
          scriptVersion: file.version,
          statusMessage: showProgress
              ? 'Workspace ready for ${lesson.title}.'
              : state.statusMessage,
        ),
      );
    } on BackendApiException catch (error) {
      if (isClosed || state.selectedLesson.id != requestedLessonId) {
        return;
      }
      emit(
        state.copyWith(
          workspaceSessionId: null,
          workspaceReady: false,
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
          statusMessage: showProgress ? error.message : state.statusMessage,
        ),
      );
    } catch (_) {
      if (isClosed || state.selectedLesson.id != requestedLessonId) {
        return;
      }
      emit(
        state.copyWith(
          workspaceSessionId: null,
          workspaceReady: false,
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
          statusMessage: showProgress
              ? 'Workspace runtime unavailable. Start the gateway and worker in remote mode.'
              : state.statusMessage,
        ),
      );
    }
  }

  Future<void> _syncWorkspaceCode(String sessionId, String content) async {
    try {
      final snapshot = await _api.updateWorkspaceFile(
        sessionId: sessionId,
        content: content,
      );
      if (isClosed || state.workspaceSessionId != sessionId) {
        return;
      }
      emit(
        state.copyWith(
          code: snapshot.content,
          scriptVersion: snapshot.version,
        ),
      );
    } on BackendApiException {
      if (isClosed || state.workspaceSessionId != sessionId) {
        return;
      }
      emit(
        state.copyWith(
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
        ),
      );
    }
  }

  Future<String> _latestSubmissionCode() async {
    final sessionId = state.workspaceSessionId;
    if (sessionId == null) {
      return state.code;
    }

    try {
      final snapshot = await _api.getWorkspaceFile(sessionId: sessionId);
      emit(
        state.copyWith(
          code: snapshot.content,
          scriptVersion: snapshot.version,
        ),
      );
      return snapshot.content;
    } on BackendApiException {
      return state.code;
    }
  }

  RLWorkbenchState _resetProgressState(String message) {
    return state.copyWith(
      runStatus: RunStatus.idle,
      currentEpisode: 0,
      currentStep: 0,
      totalReward: 0.0,
      averageReward: 0.0,
      bestEpisodeReward: 0.0,
      videoPath: '',
      testResults: const [],
      stepTrace: const [],
      statusMessage: message,
    );
  }

  int _nonEmptyLineCount(String source) {
    return source.split('\n').where((line) => line.trim().isNotEmpty).length;
  }

  Future<void> _pollUntilComplete(String taskId) async {
    while (_activeTaskId == taskId && state.runStatus == RunStatus.running) {
      final snapshot = await _api.getTaskStatus(taskId);

      if (_activeTaskId != taskId || state.runStatus != RunStatus.running) {
        return;
      }

      switch (snapshot.status) {
        case ExecutionTaskStatus.queued:
          emit(state.copyWith(
            statusMessage: 'Task $taskId queued.',
          ));
          break;
        case ExecutionTaskStatus.running:
          emit(state.copyWith(
            statusMessage: 'Task $taskId running.',
          ));
          break;
        case ExecutionTaskStatus.succeeded:
          final result = snapshot.result;
          if (result == null) {
            throw const BackendApiException(
              'Backend completed a task without returning a result.',
            );
          }

          _activeTaskId = null;
          emit(
            state.copyWith(
              runStatus: RunStatus.success,
              currentEpisode: result.metrics.episodesCompleted,
              currentStep: result.metrics.stepsRecorded,
              totalReward: result.metrics.totalReward,
              averageReward: result.metrics.averageReward,
              bestEpisodeReward: result.metrics.bestEpisodeReward,
              videoPath: result.videoPath,
              testResults: result.testResults,
              stepTrace: result.stepTrace,
              statusMessage: result.visualizationReady
                  ? '${result.message} Replay ready.'
                  : '${result.message} No replay video generated.',
            ),
          );
          await refreshDashboard(quiet: true);
          return;
        case ExecutionTaskStatus.failed:
          _activeTaskId = null;
          emit(
            state.copyWith(
              runStatus: RunStatus.failed,
              currentEpisode: 0,
              currentStep: 0,
              totalReward: 0.0,
              averageReward: 0.0,
              bestEpisodeReward: 0.0,
              videoPath: '',
              testResults: snapshot.testResults,
              stepTrace: const [],
              statusMessage: snapshot.errorMessage ?? 'Execution task failed.',
            ),
          );
          return;
      }

      await Future<void>.delayed(const Duration(milliseconds: 500));
    }
  }

  Future<void> _pollWorkspaceRun(String sessionId, String runId) async {
    while (_activeWorkspaceRunId == runId) {
      final snapshot = await _api.getWorkspaceRun(
        sessionId: sessionId,
        runId: runId,
      );
      if (_activeWorkspaceRunId != runId) {
        return;
      }

      if (snapshot.isTerminal) {
        _activeWorkspaceRunId = null;
        emit(
          state.copyWith(
            activeRunId: null,
            statusMessage: snapshot.exitCode == 0
                ? 'Workspace run completed.'
                : 'Workspace run failed with exit code ${snapshot.exitCode ?? 1}.',
            editorConnectionStatus: WorkspaceConnectionStatus.ready,
            consoleConnectionStatus: WorkspaceConnectionStatus.ready,
          ),
        );
        return;
      }

      await Future<void>.delayed(const Duration(milliseconds: 400));
    }
  }

  String _quizPromptForProgress(LearnerProgress progress) {
    if (progress.pretestScore == null) {
      return 'Take the pre-test first.';
    }
    if (progress.posttestScore == null) {
      return 'Post-test unlocks after one run.';
    }
    return 'Both quizzes complete. Check N-gain on Quiz.';
  }

  LessonDefinition? _findLessonById(
      List<LessonSection> sections, String lessonId) {
    for (final section in sections) {
      for (final lesson in section.lessons) {
        if (lesson.id == lessonId) {
          return lesson;
        }
      }
    }
    return null;
  }

  bool _isCoreLessonId(String lessonId) {
    for (final section in _lessonSections) {
      for (final lesson in section.lessons) {
        if (lesson.id == lessonId) {
          return true;
        }
      }
    }
    return false;
  }

  List<LessonSection> _upsertLessonInSections(
    List<LessonSection> sections,
    LessonDefinition lesson,
  ) {
    final categoryOrder = <String>[
      for (final section in sections) section.title,
      if (!sections.any((section) => section.title == lesson.category))
        lesson.category,
    ];
    final lessonsByCategory = <String, List<LessonDefinition>>{
      for (final category in categoryOrder) category: <LessonDefinition>[],
    };

    for (final section in sections) {
      for (final item in section.lessons) {
        if (item.id == lesson.id) {
          continue;
        }
        lessonsByCategory.putIfAbsent(
            item.category, () => <LessonDefinition>[]);
        lessonsByCategory[item.category]!.add(item);
      }
    }

    lessonsByCategory.putIfAbsent(lesson.category, () => <LessonDefinition>[]);
    lessonsByCategory[lesson.category]!.add(lesson);

    return lessonsByCategory.entries
        .where((entry) => entry.value.isNotEmpty)
        .map(
          (entry) => LessonSection(
            title: entry.key,
            lessons: entry.value,
          ),
        )
        .toList(growable: false);
  }
}
