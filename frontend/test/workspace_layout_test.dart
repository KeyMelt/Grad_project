// ignore_for_file: depend_on_referenced_packages

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/workbench_state.dart';
import 'package:rl_ide/layout/main_layout.dart';
import 'package:video_player_platform_interface/video_player_platform_interface.dart';

class _FakeVideoPlayerPlatform extends VideoPlayerPlatform {
  final Map<int, Stream<VideoEvent>> _eventStreams = {};
  int _nextPlayerId = 1;

  @override
  Future<void> init() async {}

  @override
  Future<int?> createWithOptions(VideoCreationOptions options) async {
    final playerId = _nextPlayerId++;
    _eventStreams[playerId] = Stream<VideoEvent>.value(
      VideoEvent(
        eventType: VideoEventType.initialized,
        duration: const Duration(minutes: 2),
        size: const Size(1280, 720),
      ),
    );
    return playerId;
  }

  @override
  Stream<VideoEvent> videoEventsFor(int playerId) {
    return _eventStreams[playerId] ?? const Stream<VideoEvent>.empty();
  }

  @override
  Widget buildViewWithOptions(VideoViewOptions options) {
    return const ColoredBox(color: Colors.black12);
  }

  @override
  Future<void> dispose(int playerId) async {}

  @override
  Future<void> pause(int playerId) async {}

  @override
  Future<void> play(int playerId) async {}

  @override
  Future<void> seekTo(int playerId, Duration position) async {}

  @override
  Future<void> setLooping(int playerId, bool looping) async {}

  @override
  Future<void> setPlaybackSpeed(int playerId, double speed) async {}

  @override
  Future<void> setVolume(int playerId, double volume) async {}

  @override
  Future<Duration> getPosition(int playerId) async => Duration.zero;

  @override
  Future<void> setMixWithOthers(bool mixWithOthers) async {}
}

class _WorkspaceLayoutApi extends BackendApi {
  String? _token;
  String _fileContent = 'print("policy evaluation")';
  int _fileVersion = 1;
  Map<String, dynamic>? latestChatRequest;

  @override
  String? get accessToken => _token;

  @override
  void clearAuthToken() {
    _token = null;
  }

  @override
  Future<List<LessonSection>> fetchLessonSections() async => const [];

  @override
  Future<LearnerDashboard> getDashboard() async {
    return const LearnerDashboard(
      student: LearnerProfile(
        id: 'student-1',
        displayName: 'Maya',
        platformRole: 'student',
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
  VideoPlayerPlatform.instance = _FakeVideoPlayerPlatform();

  testWidgets('workspace desktop layout opens course outline dialog', (
    tester,
  ) async {
    await _pumpWorkspace(tester, const Size(1440, 900));

    expect(find.text('Course Outline'), findsOneWidget);
    expect(find.text('Study Buddy'), findsOneWidget);
    expect(find.text('Concept lesson video'), findsOneWidget);

    await tester.tap(find.text('Course Outline'));
    await tester.pumpAndSettle();

    expect(find.byTooltip('Close course outline'), findsOneWidget);
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
  cubit.openLesson(cubit.state.selectedLesson);

  await tester.pumpWidget(
    MaterialApp(
      home: MainLayout(cubit: cubit),
    ),
  );
  await tester.pumpAndSettle();
  return harness;
}
