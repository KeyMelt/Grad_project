// ignore_for_file: depend_on_referenced_packages

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/workbench_state.dart';
import 'package:rl_ide/layout/main_layout.dart';

import 'support/fake_video_player_platform.dart';

const _layoutLesson = LessonDefinition(
  id: 'dp_policy_eval',
  title: 'Policy Evaluation',
  description: 'Evaluate a policy on FrozenLake.',
  category: 'Dynamic Programming',
  starterCode: 'def policy_evaluation():\n    return []\n',
  conceptVideo: LessonConceptVideo(
    streamPath: '/media/concept-videos/dp_policy_eval_concept.mp4',
    durationLabel: '00:10',
    summary: 'Bellman expectation walkthrough.',
    highlights: [],
  ),
  exercise: LessonExerciseBrief(
    title: 'Implement iterative policy evaluation',
    overview: 'Complete the Bellman update.',
    tasks: ['Fill the Bellman expectation backup.'],
    successCriteria: ['Submission passed'],
    codeTip: 'Use the supplied discount factor.',
  ),
);

const _layoutSections = [
  LessonSection(
    title: 'Dynamic Programming',
    lessons: [_layoutLesson],
  ),
];

class _WorkspaceLayoutApi extends BackendApi {
  String? _token;
  String _fileContent = 'print("policy evaluation")';
  int _fileVersion = 1;
  Map<String, dynamic>? latestChatRequest;

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
  Future<List<LessonSection>> fetchLessonSections() async => _layoutSections;

  @override
  Future<LearnerDashboard> getDashboard() async {
    return const LearnerDashboard(
      student: LearnerProfile(
        id: 'student-1',
        displayName: 'Maya',
        platformRole: 'student',
        rlExperience: 'Beginner',
      ),
      progress: LearnerProgress.empty(),
    );
  }

  @override
  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId) {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceFileSnapshot> getWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
  }) async {
    return WorkspaceFileSnapshot(
      path: path,
      content: _fileContent,
      version: _fileVersion,
      diagnostics: const [],
    );
  }

  @override
  Future<WorkspaceHealthData> getWorkspaceHealth() async {
    return const WorkspaceHealthData(
      ready: true,
      workerReachable: true,
      dockerCliAvailable: true,
      dockerDaemonReachable: true,
      runtimeMode: 'test',
      message: 'ready',
      issues: [],
    );
  }

  @override
  Future<WorkspaceRunData> getWorkspaceRun({
    required String sessionId,
    required String runId,
  }) {
    throw UnimplementedError();
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
  Future<NGainMetricsExport> exportNGainMetrics() {
    throw UnimplementedError();
  }

  @override
  Future<List<StaffStudentSummary>> fetchStaffStudents() {
    throw UnimplementedError();
  }

  @override
  Future<LearnerDashboard> fetchStaffStudentDashboard(String studentId) {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceSessionData> createWorkspaceSession({
    required String lessonId,
  }) async {
    return WorkspaceSessionData(
      sessionId: 'workspace-session-1',
      lessonId: lessonId,
      visibleFiles: const ['script.py'],
      consoleReady: true,
    );
  }

  @override
  Future<WorkspaceRunData> runWorkspaceScript({
    required String sessionId,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<QuizSessionData> startQuiz({required QuizPhase phase}) {
    throw UnimplementedError();
  }

  @override
  Future<SubmittedExecutionTask> submitCode({
    required String lessonId,
    required String code,
    String? studentId,
    String? sessionId,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<QuizAttemptSummary> submitQuiz({
    required String sessionId,
    required Map<String, int> answers,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<LearnerDashboard> signIn({
    required String displayName,
    required String password,
    String? firebaseIdToken,
  }) async {
    _token = 'fake-token';
    return LearnerDashboard(
      student: LearnerProfile(
        id: 'student-1',
        displayName: displayName,
        platformRole: 'student',
        rlExperience: 'Beginner',
      ),
      progress: const LearnerProgress.empty(),
    );
  }

  @override
  Future<WorkspaceFileSnapshot> updateWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
    required String content,
  }) async {
    _fileContent = content;
    _fileVersion += 1;
    return WorkspaceFileSnapshot(
      path: path,
      content: _fileContent,
      version: _fileVersion,
      diagnostics: const [],
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

class _WorkspaceHarness {
  final RLWorkbenchCubit cubit;
  final _WorkspaceLayoutApi api;
  bool _closed = false;

  _WorkspaceHarness({
    required this.cubit,
    required this.api,
  });

  Future<void> close() async {
    if (_closed) {
      return;
    }
    _closed = true;
    await cubit.close();
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  installFakeVideoPlayerPlatform();

  testWidgets('workspace desktop layout keeps course outline on concept/code only', (
    tester,
  ) async {
    await _pumpWorkspace(tester, const Size(1440, 900));

    expect(find.text('Course Outline'), findsOneWidget);
    expect(find.text('Study Buddy'), findsOneWidget);
    expect(find.text('Concept'), findsOneWidget);

    await tester.tap(find.text('Code'));
    await tester.pumpAndSettle();

    expect(find.text('Course Outline'), findsOneWidget);

    await tester.tap(find.text('Replay'));
    await tester.pumpAndSettle();

    expect(find.text('Course Outline'), findsNothing);
    expect(find.byKey(const ValueKey('study-buddy-chat-input')), findsWidgets);
    expect(tester.takeException(), isNull);
  });

  testWidgets('workspace tablet layout stays visible without overflow', (
    tester,
  ) async {
    await _pumpWorkspace(tester, const Size(900, 1200));

    expect(find.text('Course Outline'), findsOneWidget);
    expect(find.text('Study Buddy'), findsOneWidget);
    expect(find.byKey(const ValueKey('study-buddy-drawer-handle')),
        findsOneWidget);
    expect(
        find.byKey(const ValueKey('study-buddy-chat-input')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('workspace lesson notes expand and minimize over concept video', (
    tester,
  ) async {
    await _pumpWorkspace(tester, const Size(1440, 900));

    final handle = find.byKey(const ValueKey('lesson-notes-drawer-handle'));
    expect(handle, findsOneWidget);

    await tester.tap(handle);
    await tester.pumpAndSettle();

    final expandButton =
        find.byKey(const ValueKey('lesson-notes-expand-button'));
    expect(expandButton, findsOneWidget);

    await tester.tap(expandButton);
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey('lesson-notes-expanded-overlay')),
      findsOneWidget,
    );
    expect(
      find.byKey(const ValueKey('lesson-notes-minimize-button')),
      findsOneWidget,
    );

    await tester
        .tap(find.byKey(const ValueKey('lesson-notes-minimize-button')));
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey('lesson-notes-expanded-overlay')),
      findsNothing,
    );
    expect(expandButton, findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('workspace study buddy expands and minimizes from drawer', (
    tester,
  ) async {
    await _pumpWorkspace(tester, const Size(1440, 900));

    final handle = find.byKey(const ValueKey('study-buddy-drawer-handle'));
    expect(handle, findsOneWidget);

    await tester.drag(handle, const Offset(-180, 0));
    await tester.pumpAndSettle();

    final expandButton =
        find.byKey(const ValueKey('study-buddy-expand-button'));
    expect(expandButton, findsOneWidget);

    await tester.tap(expandButton);
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey('study-buddy-expanded-overlay')),
      findsOneWidget,
    );
    expect(
      find.byKey(const ValueKey('study-buddy-minimize-button')),
      findsOneWidget,
    );

    await tester.tap(find.byKey(const ValueKey('study-buddy-minimize-button')));
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey('study-buddy-expanded-overlay')),
      findsNothing,
    );
    expect(expandButton, findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('workspace study buddy drawer drags and coach actions send chat',
      (
    tester,
  ) async {
    final harness = await _pumpWorkspace(tester, const Size(1440, 900));

    await harness.cubit.signIn('maya@example.com', 'Password123!');
    harness.cubit.openLesson(harness.cubit.state.selectedLesson);
    await tester.pumpAndSettle();

    final handle = find.byKey(const ValueKey('study-buddy-drawer-handle'));
    expect(handle, findsOneWidget);

    final closedHandleCenter = tester.getCenter(handle);
    await tester.drag(handle, const Offset(-180, 0));
    await tester.pumpAndSettle();
    final openHandleCenter = tester.getCenter(handle);
    expect(openHandleCenter.dx, lessThan(closedHandleCenter.dx - 100));

    await tester.ensureVisible(
      find.byKey(const ValueKey('study-buddy-quick-recap')),
    );
    await tester.tap(find.byKey(const ValueKey('study-buddy-quick-recap')));
    await tester.pumpAndSettle();
    expect(harness.api.latestChatRequest?['message'], contains('quick recap'));
    expect(
      find.text('Start by checking the Bellman update target.'),
      findsOneWidget,
    );

    await tester.ensureVisible(
      find.byKey(const ValueKey('study-buddy-find-blocker')),
    );
    await tester.tap(find.byKey(const ValueKey('study-buddy-find-blocker')));
    await tester.pumpAndSettle();
    expect(
      harness.api.latestChatRequest?['message'],
      contains('most likely blocker'),
    );

    await tester.drag(handle, const Offset(180, 0));
    await tester.pumpAndSettle();
    expect(tester.getCenter(handle).dx, greaterThan(openHandleCenter.dx + 100));
    expect(tester.takeException(), isNull);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
    await harness.close();
  });

  testWidgets('generate marketing screenshots', (tester) async {
    const shouldRunGoldens =
        bool.fromEnvironment('RL_IDE_GENERATE_MARKETING_GOLDENS');
    if (!shouldRunGoldens) {
      return;
    }

    final harness = await _pumpWorkspace(tester, const Size(1440, 900));

    await harness.cubit.signIn('maya@example.com', 'Password123!');
    harness.cubit.openLesson(harness.cubit.state.selectedLesson);
    await tester.pumpAndSettle();

    // 1. Capture Workspace (Code Editor)
    await expectLater(
        find.byType(MainLayout), matchesGoldenFile('workspace.png'));

    // 2. Capture Trace Replay
    await tester.tap(find.text('Replay'));
    await tester.pumpAndSettle();
    await expectLater(find.byType(MainLayout), matchesGoldenFile('trace.png'));

    // 3. Capture StudyBuddy
    await tester.tap(find.text('Concept')); // switch back
    await tester.pumpAndSettle();
    final handle = find.byKey(const ValueKey('study-buddy-drawer-handle'));
    await tester.drag(handle, const Offset(-250, 0)); // open wide
    await tester.pumpAndSettle();

    // send a message so it shows some text
    await tester.tap(find.byKey(const ValueKey('study-buddy-quick-recap')));
    await tester.pumpAndSettle();

    await expectLater(
        find.byType(MainLayout), matchesGoldenFile('studybuddy.png'));

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
    await harness.close();
  });
}

Future<_WorkspaceHarness> _pumpWorkspace(WidgetTester tester, Size size) async {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  final api = _WorkspaceLayoutApi();
  final cubit = RLWorkbenchCubit(
    api: api,
    autoStartTelemetry: false,
  );
  final harness = _WorkspaceHarness(cubit: cubit, api: api);
  addTearDown(() async {
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
    await harness.close();
  });
  await cubit.loadBackendLessonCatalog();
  cubit.openLesson(cubit.state.selectedLesson);

  await tester.pumpWidget(
    MaterialApp(
      home: MainLayout(cubit: cubit),
    ),
  );
  await tester.pumpAndSettle();
  return harness;
}
