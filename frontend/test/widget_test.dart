import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/workbench_state.dart';
import 'package:rl_ide/features/home/home_dashboard.dart';
import 'package:rl_ide/features/workspace/code_editor.dart';
import 'package:rl_ide/features/workspace/exercise_brief_panel.dart';
import 'package:rl_ide/layout/main_layout.dart';
import 'package:rl_ide/main.dart';
import 'package:shared_preferences/shared_preferences.dart';

class FakeBackendApi extends BackendApi {
  LearnerProfile? _student;
  LearnerProgress _progress = const LearnerProgress.empty();
  QuizPhase? _latestPhase;
  String _workspaceContent = 'print("workspace")\n';
  String? _token;
  List<int>? submittedSusResponses;
  int? submittedTlxMentalDemand;
  String? signInError;
  bool failNextSubmission = false;

  @override
  String? get accessToken => _token;

  @override
  Future<LearnerDashboard> updateProfile({
    required String displayName,
    required String rlExperience,
  }) {
    throw UnimplementedError();
  }

  @override
  void clearAuthToken() {
    _token = null;
  }

  @override
  Future<List<LessonSection>> fetchLessonSections() async => const [];

  @override
  Future<LearnerDashboard> signIn({
    required String displayName,
    required String password,
    String? firebaseIdToken,
  }) async {
    if (firebaseIdToken != null) {}
    final error = signInError;
    if (error != null) {
      throw BackendApiException(error);
    }
    _student = LearnerProfile(
      id: 'student-123',
      displayName: displayName,
      platformRole: 'student',
      rlExperience: 'Beginner',
    );
    _token = 'fake-token';
    return LearnerDashboard(student: _student!, progress: _progress);
  }

  @override
  Future<LearnerDashboard> getDashboard() async {
    return LearnerDashboard(
      student: _student!,
      progress: _progress,
    );
  }

  @override
  Future<List<StaffStudentSummary>> fetchStaffStudents() async {
    return const [
      StaffStudentSummary(
        id: 'student-123',
        displayName: 'student-123',
        role: 'student',
        status: 'active',
      ),
    ];
  }

  @override
  Future<LearnerDashboard> fetchStaffStudentDashboard(String studentId) async {
    return LearnerDashboard(
      student: LearnerProfile(
        id: studentId,
        displayName: 'student-123',
        platformRole: 'student',
        rlExperience: 'Beginner',
      ),
      progress: _progress,
    );
  }

  @override
  Future<QuizSessionData> startQuiz({
    required QuizPhase phase,
  }) async {
    _latestPhase = phase;
    return QuizSessionData(
      sessionId: '${quizPhaseApiValue(phase)}-session',
      phase: phase,
      questionCount: 2,
      questions: const [
        QuizQuestionData(
          id: 'q1',
          concept: 'Core RL',
          prompt: 'What does gamma control?',
          options: [
            'How much future rewards matter',
            'How fast the video plays',
            'How many states exist',
            'How many files Manim writes',
          ],
        ),
        QuizQuestionData(
          id: 'q2',
          concept: 'Temporal Difference',
          prompt: 'What is the TD target in Q-learning?',
          options: [
            'Reward plus discounted best next-state action value',
            'Average reward minus epsilon',
            'The current value of the same state',
            'Only the immediate reward',
          ],
        ),
      ],
    );
  }

  @override
  Future<QuizAttemptSummary> submitQuiz({
    required String sessionId,
    required Map<String, int> answers,
  }) async {
    if (_latestPhase == QuizPhase.pretest) {
      _progress = const LearnerProgress(
        completedLessonIds: ['dp_policy_eval'],
        successfulRuns: 1,
        latestLessonId: 'dp_policy_eval',
        pretestScore: 50.0,
        posttestScore: null,
        nGain: null,
        quizAttempts: {
          'pretest': 1,
          'posttest': 0,
        },
      );
      return QuizAttemptSummary(
        phase: QuizPhase.pretest,
        score: 1,
        totalQuestions: 2,
        percentage: 50.0,
        nGain: null,
        progress: _progress,
      );
    }

    _progress = const LearnerProgress(
      completedLessonIds: ['dp_policy_eval'],
      successfulRuns: 1,
      latestLessonId: 'dp_policy_eval',
      pretestScore: 50.0,
      posttestScore: 100.0,
      nGain: 1.0,
      quizAttempts: {
        'pretest': 1,
        'posttest': 1,
      },
    );
    return QuizAttemptSummary(
      phase: QuizPhase.posttest,
      score: 2,
      totalQuestions: 2,
      percentage: 100.0,
      nGain: 1.0,
      progress: _progress,
    );
  }

  @override
  Future<SubmittedExecutionTask> submitCode({
    required String lessonId,
    required String code,
    String? studentId,
    String? sessionId,
  }) async {
    if (sessionId != null) {}
    return const SubmittedExecutionTask(
      taskId: 'task-123',
      status: ExecutionTaskStatus.queued,
    );
  }

  @override
  Future<StudySessionSurveyResult> submitStudySessionSurvey({
    required String studySessionId,
    required String condition,
    required List<int> susResponses,
    required int tlxMentalDemand,
    required int tlxPhysicalDemand,
    required int tlxTemporalDemand,
    required int tlxPerformance,
    required int tlxEffort,
    required int tlxFrustration,
    String? feedbackHelpful,
    String? feedbackConfusing,
    String? feedbackImprovement,
  }) async {
    submittedSusResponses = susResponses;
    submittedTlxMentalDemand = tlxMentalDemand;
    return const StudySessionSurveyResult(
      susScore: 75,
      tlxOverall: 40,
    );
  }

  @override
  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId) async {
    if (failNextSubmission) {
      failNextSubmission = false;
      return const ExecutionTaskSnapshot(
        taskId: 'task-123',
        status: ExecutionTaskStatus.failed,
        errorMessage: 'Lesson checks failed.',
        failureKind: 'test_failure',
        studentFeedback: ExecutionStudentFeedback(
          status: 'test_failure',
          summary: 'The value table did not match the expected update.',
          likelyIssue: 'Review the Bellman expectation loops.',
          affectedBlankIds: ['policy_eval_expectation'],
          nextSteps: [
            'Accumulate every transition branch for each action.',
            'Keep terminal future value at zero.',
          ],
          hintLevel: 'targeted',
        ),
        testResults: [
          ExecutionTestCaseResult(
            name: 'policy_evaluation_bellman_backup',
            passed: false,
            message: 'The Bellman backup did not include every branch.',
            expected: 'Every model branch contributes to the backup.',
            actual: 'At least one model branch was missing.',
          ),
        ],
      );
    }

    _progress = const LearnerProgress(
      completedLessonIds: ['dp_policy_eval'],
      successfulRuns: 1,
      latestLessonId: 'dp_policy_eval',
      pretestScore: null,
      posttestScore: null,
      nGain: null,
      quizAttempts: {
        'pretest': 0,
        'posttest': 0,
      },
    );

    return const ExecutionTaskSnapshot(
      taskId: 'task-123',
      status: ExecutionTaskStatus.succeeded,
      result: ExecutionResult(
        message: 'Execution pipeline completed.',
        lessonTitle: 'Dynamic Programming: Policy Evaluation',
        videoPath: '/tmp/dp_policy_eval.mp4',
        visualizationReady: true,
        metrics: ExecutionMetrics(
          episodesCompleted: 5,
          stepsRecorded: 17,
          totalReward: 3,
          averageReward: 0.6,
          bestEpisodeReward: 1,
        ),
        testResults: [
          ExecutionTestCaseResult(
            name: 'policy_evaluation_bellman_backup',
            passed: true,
            message: 'Applies the Bellman expectation update.',
            expected: 'V[0] reflects discounted successor values',
            actual: 'V[0] reflects discounted successor values',
          ),
        ],
        stepTrace: [
          ExecutionTraceStep(
            state: 0,
            action: 1,
            nextState: 4,
            reward: 0,
            transitionProbability: 0.333,
            framePath: '',
            agentCaption: 'Agent sampled Down from state 0 to state 4.',
            codeTitle: 'Code Trace',
            codeLines: [
              'new_value += action_prob * transition_prob * (reward + gamma * future)',
            ],
            mathTitle: 'Bellman Expectation',
            mathEquation:
                r"V(s) \leftarrow \sum_a \pi(a|s)\sum_{s',r} p(s',r|s,a)(r + \gamma V(s'))",
            mathLines: [
              'Each transition contributes according to policy and model probability.',
            ],
            updatedValues: {
              'V(0)': 0.17,
            },
          ),
        ],
      ),
    );
  }

  @override
  Future<NGainMetricsExport> exportNGainMetrics() async {
    return const NGainMetricsExport(
      fileName: 'n_gain_metrics_test.xlsx',
      bytes: <int>[1, 2, 3],
    );
  }

  @override
  Future<WorkspaceSessionData> createWorkspaceSession({
    required String lessonId,
  }) async {
    return WorkspaceSessionData(
      sessionId: 'workspace-$lessonId',
      lessonId: lessonId,
      visibleFiles: const ['script.py'],
      consoleReady: true,
    );
  }

  @override
  Future<WorkspaceHealthData> getWorkspaceHealth() async {
    return const WorkspaceHealthData(
      ready: true,
      workerReachable: true,
      dockerCliAvailable: true,
      dockerDaemonReachable: true,
      runtimeMode: 'docker',
      message: 'Workspace runtime is ready.',
      issues: [],
    );
  }

  @override
  Future<WorkspaceSessionData> getWorkspaceSession(String sessionId) async {
    return WorkspaceSessionData(
      sessionId: sessionId,
      lessonId: 'dp_policy_eval',
      visibleFiles: const ['script.py'],
      consoleReady: true,
    );
  }

  @override
  Future<WorkspaceFileSnapshot> getWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
  }) async {
    return WorkspaceFileSnapshot(
      path: path,
      content: _workspaceContent,
      version: 1,
      diagnostics: const [],
    );
  }

  @override
  Future<WorkspaceFileSnapshot> updateWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
    required String content,
  }) async {
    _workspaceContent = content;
    return WorkspaceFileSnapshot(
      path: path,
      content: content,
      version: 2,
      diagnostics: const [],
    );
  }

  @override
  Future<WorkspaceRunData> runWorkspaceScript({
    required String sessionId,
  }) async {
    return const WorkspaceRunData(
      runId: 'run-123',
      status: 'running',
      exitCode: null,
      startedAt: '2026-01-01T00:00:00Z',
      finishedAt: null,
    );
  }

  @override
  Future<WorkspaceRunData> getWorkspaceRun({
    required String sessionId,
    required String runId,
  }) async {
    return const WorkspaceRunData(
      runId: 'run-123',
      status: 'completed',
      exitCode: 0,
      startedAt: '2026-01-01T00:00:00Z',
      finishedAt: '2026-01-01T00:00:02Z',
    );
  }

  @override
  Future<String> workspaceEditorShellUrl(String sessionId) async {
    return 'http://127.0.0.1:8000/workspace/editor-shell?session_id=$sessionId';
  }
}

void main() {
  testWidgets('Theme toggle switches dark mode and persists the preference', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final api = FakeBackendApi();
    final cubit = RLWorkbenchCubit(api: api);

    await tester.pumpWidget(
      RLSimulationIDE(
        home: MainLayout(cubit: cubit),
      ),
    );
    await tester.pumpAndSettle();

    final materialApp = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(materialApp.themeMode, ThemeMode.light);
    expect(find.byTooltip('Use dark mode'), findsOneWidget);

    await tester.tap(find.byTooltip('Use dark mode'));
    await tester.pumpAndSettle();

    final darkMaterialApp =
        tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(darkMaterialApp.themeMode, ThemeMode.dark);
    expect(find.byTooltip('Use light mode'), findsOneWidget);

    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getBool('rl_ide_dark_mode'), isTrue);

    await cubit.close();
  });

  testWidgets('Home dashboard signs in a learner through the auth dialog', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final api = FakeBackendApi();
    final cubit = RLWorkbenchCubit(api: api);

    await tester.pumpWidget(
      RLSimulationIDE(
        home: MainLayout(cubit: cubit),
      ),
    );

    expect(find.text('RL Learning Platform'), findsNothing);
    expect(find.text('Authentication'), findsNothing);
    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('Sign up'), findsOneWidget);

    await tester.tap(find.text('Sign in'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField).at(0), 'maya@example.com');
    await tester.enterText(find.byType(TextField).at(1), 'Password123!');
    await tester.tap(find.text('Sign in').last);
    await tester.pumpAndSettle();

    expect(
        find.textContaining('Welcome back, maya@example.com'), findsOneWidget);
    expect(find.text('Progress Overview'), findsNothing);
    expect(find.text('Study Flashcards'), findsOneWidget);

    await tester.tap(find.text('Sign Out'));
    await tester.pumpAndSettle();
    expect(find.text('Authentication'), findsNothing);
    expect(find.text('Sign in'), findsOneWidget);
    expect(find.textContaining('Signed out.'), findsOneWidget);

    await cubit.close();
  });

  testWidgets('Auth errors stay in the auth dialog', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final api = FakeBackendApi()
      ..signInError = 'Account is not provisioned for this Firebase user.';
    final cubit = RLWorkbenchCubit(api: api);

    await tester.pumpWidget(
      RLSimulationIDE(
        home: MainLayout(cubit: cubit),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Sign in'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField).at(0), 'maya@example.com');
    await tester.enterText(find.byType(TextField).at(1), 'Password123!');
    await tester.tap(find.text('Sign in').last);
    await tester.pumpAndSettle();

    expect(find.byType(AlertDialog), findsOneWidget);
    expect(
      find.descendant(
        of: find.byType(AlertDialog),
        matching:
            find.text('Account is not provisioned for this Firebase user.'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: find.byType(HomeDashboard),
        matching:
            find.text('Account is not provisioned for this Firebase user.'),
      ),
      findsNothing,
    );
    expect(
      find.text('Sign in to save quiz results and lesson progress.'),
      findsOneWidget,
    );

    await cubit.close();
  });

  testWidgets('Workspace feedback uses separate panel and dismisses', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final api = FakeBackendApi()..failNextSubmission = true;
    final cubit = RLWorkbenchCubit(api: api);

    await tester.pumpWidget(
      RLSimulationIDE(
        home: MainLayout(cubit: cubit),
      ),
    );

    await tester.tap(find.text('Sign in'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField).at(0), 'maya@example.com');
    await tester.enterText(find.byType(TextField).at(1), 'Password123!');
    await tester.tap(find.text('Sign in').last);
    await tester.pumpAndSettle();

    await tester.tap(find.text('Workspace'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Code'));
    await tester.pumpAndSettle();
    expect(find.widgetWithText(FilledButton, 'Run'), findsNothing);

    await tester.tap(find.text('Submit'));
    await tester.pumpAndSettle();

    const feedbackText = 'Review the Bellman expectation loops.';
    expect(
      find.descendant(
        of: find.byType(WorkspaceFeedbackPanel),
        matching: find.text(feedbackText),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: find.byType(ExerciseBriefPanel),
        matching: find.text(feedbackText),
      ),
      findsNothing,
    );
    expect(
      find.descendant(
        of: find.byType(CodeEditorTab),
        matching: find.text(feedbackText),
      ),
      findsNothing,
    );

    await tester.tap(find.byTooltip('Dismiss feedback'));
    await tester.pumpAndSettle();
    expect(find.text(feedbackText), findsNothing);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
    await cubit.close();
  });

  testWidgets('Workspace and quiz flow update learner progress end to end', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final api = FakeBackendApi();
    final cubit = RLWorkbenchCubit(api: api);

    await tester.pumpWidget(
      RLSimulationIDE(
        home: MainLayout(cubit: cubit),
      ),
    );

    await tester.tap(find.text('Sign in'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField).at(0), 'maya@example.com');
    await tester.enterText(find.byType(TextField).at(1), 'Password123!');
    await tester.tap(find.text('Sign in').last);
    await tester.pumpAndSettle();

    await tester.tap(find.text('Workspace'));
    await tester.pumpAndSettle();

    expect(find.text('Concept'), findsOneWidget);

    await tester.tap(find.text('Code'));
    await tester.pumpAndSettle();
    expect(find.text('Implement iterative policy evaluation'), findsWidgets);
    expect(find.widgetWithText(FilledButton, 'Run'), findsNothing);

    await tester.tap(find.text('Submit'));
    await tester.pumpAndSettle();
    expect(
      find.descendant(
        of: find.byType(WorkspaceFeedbackPanel),
        matching: find.text('Submission passed'),
      ),
      findsOneWidget,
    );
    expect(find.text('Share feedback'), findsOneWidget);

    await tester.tap(find.text('Replay'));
    await tester.pumpAndSettle();

    expect(find.text('Generated Step Replay'), findsOneWidget);
    expect(find.text('Sample Test Results'), findsOneWidget);

    await tester.tap(find.byKey(const ValueKey('home-logo-button')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Quiz').first);
    await tester.pumpAndSettle();

    await tester.tap(find.text('Start Pre-test'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('How much future rewards matter'));
    await tester.tap(
      find.text('Reward plus discounted best next-state action value'),
    );
    await tester.tap(find.text('Submit Quiz'));
    await tester.pumpAndSettle();

    expect(find.text('50.0%'), findsWidgets);

    await tester.tap(find.text('Start Post-test'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('How much future rewards matter'));
    await tester.tap(
      find.text('Reward plus discounted best next-state action value'),
    );
    await tester.tap(find.text('Submit Quiz'));
    await tester.pumpAndSettle();

    expect(find.text('1.000'), findsWidgets);
    expect(find.text('100.0%'), findsWidgets);
    expect(
      find.text('Your feedback helps improve our services.'),
      findsOneWidget,
    );
    expect(find.text('Share feedback'), findsOneWidget);

    await tester.tap(find.text('Share feedback'));
    await tester.pumpAndSettle();
    expect(find.text('Quick session feedback'), findsOneWidget);

    await tester.ensureVisible(find.text('Next'));
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();
    expect(find.text('Session effort'), findsOneWidget);
    await tester.ensureVisible(find.text('Next'));
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();
    expect(find.text('Optional feedback'), findsOneWidget);

    await tester.ensureVisible(find.text('Submit feedback'));
    await tester.tap(find.text('Submit feedback'));
    await tester.pumpAndSettle();

    expect(api.submittedSusResponses, List<int>.filled(10, 3));
    expect(api.submittedTlxMentalDemand, 50);
    expect(find.text('Thanks. Your feedback has been recorded.'), findsWidgets);

    await tester.tap(find.byTooltip('Close feedback'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Home'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Study Flashcards'));
    await tester.pumpAndSettle();
    expect(find.text('Tap any card to flip between question and answer.'),
        findsOneWidget);
    expect(find.text('What is Bellman Expectation?'), findsOneWidget);
    await tester.tap(find.text('What is Bellman Expectation?'));
    await tester.pumpAndSettle();
    expect(
      find.textContaining(
        'Policy evaluation updates each state with an expectation',
      ),
      findsOneWidget,
    );

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpAndSettle();
    await cubit.close();
  });
}
