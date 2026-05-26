import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/local_lesson_catalog.dart';
import 'package:rl_ide/core/workbench_state.dart';

class _FakeBackendApi extends BackendApi {
  _FakeBackendApi({
    this.shouldFailRun = false,
    this.shouldFailLessonFetch = false,
    this.lessonSections = const [],
  });

  final bool shouldFailRun;
  final bool shouldFailLessonFetch;
  final List<LessonSection> lessonSections;
  int _pollCount = 0;
  int _workspacePollCount = 0;
  String? _token;
  Map<String, dynamic>? latestChatRequest;

  @override
  String? get accessToken => _token;

  @override
  void clearAuthToken() {
    _token = null;
  }

  @override
  Future<List<LessonSection>> fetchLessonSections() async {
    if (shouldFailLessonFetch) {
      throw const BackendApiException('Lesson catalog unavailable.');
    }
    return lessonSections;
  }

  @override
  Future<LearnerDashboard> signIn({
    required String displayName,
    required String password,
    String? firebaseIdToken,
  }) async {
    if (firebaseIdToken != null) {}
    if (password == 'wrong') {
      throw const BackendApiException('Invalid display name or password.');
    }
    _token = 'fake-token';

    return LearnerDashboard(
      student: LearnerProfile(
        id: 'student-1',
        displayName: displayName,
        platformRole: 'student',
      ),
      progress: const LearnerProgress.empty(),
    );
  }

  @override
  Future<LearnerDashboard> getDashboard() async {
    const studentId = 'student-1';
    return const LearnerDashboard(
      student: LearnerProfile(
        id: studentId,
        displayName: 'Maya',
        platformRole: 'student',
      ),
      progress: LearnerProgress.empty(),
    );
  }

  @override
  Future<List<StaffStudentSummary>> fetchStaffStudents() async {
    return const [
      StaffStudentSummary(
        id: 'student-1',
        displayName: 'Maya',
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
        displayName: 'Maya',
        platformRole: 'student',
      ),
      progress: const LearnerProgress.empty(),
    );
  }

  @override
  Future<QuizSessionData> startQuiz({
    required QuizPhase phase,
  }) async {
    throw UnimplementedError();
  }

  @override
  Future<QuizAttemptSummary> submitQuiz({
    required String sessionId,
    required Map<String, int> answers,
  }) async {
    throw UnimplementedError();
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
      taskId: 'task-1',
      status: ExecutionTaskStatus.queued,
    );
  }

  @override
  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId) async {
    _pollCount += 1;
    if (shouldFailRun) {
      return const ExecutionTaskSnapshot(
        taskId: 'task-1',
        status: ExecutionTaskStatus.failed,
        errorMessage: 'Code validation failed.',
        failureKind: 'incomplete_template',
        unresolvedBlanks: ['policy_eval_expectation'],
        studentFeedback: ExecutionStudentFeedback(
          status: 'incomplete_template',
          summary: 'The submission still contains guided blanks.',
          likelyIssue: 'One or more placeholder sections were left unchanged.',
          affectedBlankIds: ['policy_eval_expectation'],
          nextSteps: ['Complete the expectation backup block.'],
          hintLevel: 'light',
        ),
      );
    }

    if (_pollCount == 1) {
      return const ExecutionTaskSnapshot(
        taskId: 'task-1',
        status: ExecutionTaskStatus.queued,
      );
    }
    return const ExecutionTaskSnapshot(
      taskId: 'task-1',
      status: ExecutionTaskStatus.succeeded,
      result: ExecutionResult(
        message: 'Execution pipeline completed.',
        lessonTitle: 'Policy Evaluation',
        videoPath: '/tmp/demo.mp4',
        visualizationReady: true,
        metrics: ExecutionMetrics(
          episodesCompleted: 3,
          stepsRecorded: 12,
          totalReward: 2.0,
          averageReward: 0.66,
          bestEpisodeReward: 1.0,
        ),
        testResults: [],
        stepTrace: [],
      ),
    );
  }

  @override
  Future<NGainMetricsExport> exportNGainMetrics() async {
    throw UnimplementedError();
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
    return const WorkspaceFileSnapshot(
      path: 'script.py',
      content: 'print("workspace")\n',
      version: 2,
      diagnostics: [],
    );
  }

  @override
  Future<WorkspaceFileSnapshot> updateWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
    required String content,
  }) async {
    return WorkspaceFileSnapshot(
      path: path,
      content: content,
      version: 3,
      diagnostics: const [],
    );
  }

  @override
  Future<WorkspaceRunData> runWorkspaceScript({
    required String sessionId,
  }) async {
    return const WorkspaceRunData(
      runId: 'run-1',
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
    _workspacePollCount += 1;
    return WorkspaceRunData(
      runId: runId,
      status: _workspacePollCount > 1 ? 'completed' : 'running',
      exitCode: _workspacePollCount > 1 ? 0 : null,
      startedAt: '2026-01-01T00:00:00Z',
      finishedAt: _workspacePollCount > 1 ? '2026-01-01T00:00:01Z' : null,
    );
  }

  @override
  Future<String> workspaceEditorShellUrl(String sessionId) async {
    return 'http://127.0.0.1:8000/workspace/editor-shell?session_id=$sessionId';
  }

  @override
  Future<StudyBuddyChatResponse> sendStudyBuddyChat({
    required String lessonId,
    required String sessionId,
    required String message,
    required List<StudyBuddyChatMessage> history,
    String? currentCode,
    List<String> unresolvedBlanks = const [],
    String? failureKind,
    Map<String, dynamic> latestFeedback = const {},
  }) async {
    latestChatRequest = {
      'lesson_id': lessonId,
      'session_id': sessionId,
      'message': message,
      'history_count': history.length,
      'current_code': currentCode,
      'unresolved_blanks': unresolvedBlanks,
      'failure_kind': failureKind,
      'latest_feedback': latestFeedback,
    };
    return const StudyBuddyChatResponse(
      message: StudyBuddyChatMessage(
        role: 'assistant',
        content: 'Start by checking the Bellman update target.',
      ),
      usedFallback: false,
      suggestedNextStep: 'Run one small check.',
      conceptIds: ['dp_policy_eval'],
      solutionLeakageRisk: 'low',
      observability: {'prompt_version': 'test_chat_prompt_v1'},
    );
  }
}

void main() {
  test('cubit replaces fallback catalog with backend lesson sections',
      () async {
    final backendLesson = fallbackLessonSections.first.lessons.first.copyWith(
      title: 'Backend Policy Evaluation',
      starterCode: 'def policy_evaluation():\n    return []\n',
    );
    final cubit = RLWorkbenchCubit(
      api: _FakeBackendApi(
        lessonSections: [
          LessonSection(
            title: 'Dynamic Programming',
            lessons: [backendLesson],
          ),
        ],
      ),
    );

    await cubit.loadBackendLessonCatalog();

    expect(cubit.state.sections.first.lessons.first.title,
        'Backend Policy Evaluation');
    expect(cubit.state.selectedLesson.title, 'Backend Policy Evaluation');
    expect(cubit.state.code, contains('def policy_evaluation'));

    await cubit.close();
  });

  test('cubit keeps fallback lessons when backend lesson fetch fails',
      () async {
    final cubit = RLWorkbenchCubit(
      api: _FakeBackendApi(shouldFailLessonFetch: true),
    );

    await cubit.loadBackendLessonCatalog();

    expect(cubit.state.sections.first.lessons.first.id, 'dp_policy_eval');
    expect(cubit.state.homeMessage, contains('Lesson sync is unavailable'));

    await cubit.close();
  });

  test('cubit sign-in then sign-out updates auth state', () async {
    final cubit = RLWorkbenchCubit(api: _FakeBackendApi());

    await cubit.signIn('Maya', 'Password123!');
    expect(cubit.state.learner?.displayName, 'Maya');
    expect(cubit.state.homeMessage, contains('Signed in as Maya.'));

    cubit.signOut();
    expect(cubit.state.learner, isNull);
    expect(cubit.state.homeMessage, contains('Signed out.'));

    await cubit.close();
  });

  test('cubit workspace run lifecycle reaches terminal status', () async {
    final cubit = RLWorkbenchCubit(api: _FakeBackendApi());

    await cubit.signIn('Maya', 'Password123!');
    cubit.openLesson(cubit.state.selectedLesson);
    await Future<void>.delayed(const Duration(milliseconds: 20));
    await cubit.run();

    expect(cubit.state.workspaceSessionId, isNotNull);
    expect(cubit.state.activeRunId, isNull);
    expect(cubit.state.statusMessage, contains('Workspace run completed.'));

    await cubit.close();
  });

  test('cubit submit lifecycle handles failure state', () async {
    final cubit = RLWorkbenchCubit(api: _FakeBackendApi(shouldFailRun: true));

    await cubit.signIn('Maya', 'Password123!');
    await cubit.submit();

    expect(cubit.state.runStatus, RunStatus.failed);
    expect(cubit.state.statusMessage, contains('Code validation failed.'));
    expect(cubit.state.failureKind, 'incomplete_template');
    expect(cubit.state.unresolvedBlanks, contains('policy_eval_expectation'));
    expect(
      cubit.state.studentFeedback?.summary,
      'The submission still contains guided blanks.',
    );

    await cubit.close();
  });

  test('cubit sends Study Buddy chat with lesson context', () async {
    final api = _FakeBackendApi();
    final cubit = RLWorkbenchCubit(api: api);

    await cubit.signIn('Maya', 'Password123!');
    await cubit.sendStudyBuddyChat('What should I inspect next?');

    expect(cubit.state.studyBuddyChatLoading, isFalse);
    expect(cubit.state.studyBuddyChatError, isNull);
    expect(cubit.state.studyBuddyChatMessages, hasLength(2));
    expect(cubit.state.studyBuddyChatMessages.first.role, 'user');
    expect(cubit.state.studyBuddyChatMessages.last.content,
        contains('Bellman update target'));
    expect(api.latestChatRequest?['lesson_id'], cubit.state.selectedLesson.id);
    expect(api.latestChatRequest?['message'], 'What should I inspect next?');
    expect(
        api.latestChatRequest?['current_code'], contains('policy_evaluation'));

    await cubit.close();
  });
}
