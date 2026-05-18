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
  @override
  String? get accessToken => null;

  @override
  void clearAuthToken() {}

  @override
  Future<List<LessonSection>> fetchLessonSections() async => const [];

  @override
  Future<LearnerDashboard> getDashboard() {
    throw UnimplementedError();
  }

  @override
  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId) {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceFileSnapshot> getWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
  }) {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceHealthData> getWorkspaceHealth() {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceRunData> getWorkspaceRun({
    required String sessionId,
    required String runId,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceSessionData> getWorkspaceSession(String sessionId) {
    throw UnimplementedError();
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
  }) {
    throw UnimplementedError();
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
  }) {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceFileSnapshot> updateWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
    required String content,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<String> workspaceEditorShellUrl(String sessionId) {
    throw UnimplementedError();
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
    expect(find.text('Current Exercise'), findsOneWidget);

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
    expect(find.text('Current Exercise'), findsOneWidget);
    expect(
        find.byKey(const ValueKey('study-buddy-chat-input')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

Future<void> _pumpWorkspace(WidgetTester tester, Size size) async {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  final cubit = RLWorkbenchCubit(
    api: _WorkspaceLayoutApi(),
    autoStartTelemetry: false,
  );
  addTearDown(() async {
    await cubit.close();
  });
  cubit.openLesson(cubit.state.selectedLesson);

  await tester.pumpWidget(
    MaterialApp(
      home: MainLayout(cubit: cubit),
    ),
  );
  await tester.pumpAndSettle();
}
