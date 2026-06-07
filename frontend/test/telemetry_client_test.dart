import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/lesson_models.dart';

class _TelemetryApi extends BackendApi {
  _TelemetryApi({this.failFirstFlush = false});

  final bool failFirstFlush;
  final List<List<LearningTelemetryEvent>> batches = [];
  int calls = 0;

  @override
  String? get accessToken => null;

  @override
  Future<LearnerDashboard> updateProfile({
    required String displayName,
    required String rlExperience,
  }) {
    throw UnimplementedError();
  }

  @override
  void clearAuthToken() {}

  @override
  Future<List<LessonSection>> fetchLessonSections() async => const [];

  @override
  Future<LearnerDashboard> signIn({
    required String displayName,
    required String password,
    String? firebaseIdToken,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<LearnerDashboard> getDashboard() {
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
  Future<QuizSessionData> startQuiz({
    required QuizPhase phase,
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
  Future<SubmittedExecutionTask> submitCode({
    required String lessonId,
    required String code,
    String? studentId,
    String? sessionId,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId) {
    throw UnimplementedError();
  }

  @override
  Future<NGainMetricsExport> exportNGainMetrics() {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceSessionData> createWorkspaceSession({
    required String lessonId,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceHealthData> getWorkspaceHealth() {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceSessionData> getWorkspaceSession(String sessionId) {
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
  Future<WorkspaceFileSnapshot> updateWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
    required String content,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceRunData> runWorkspaceScript({required String sessionId}) {
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
  Future<String> workspaceEditorShellUrl(String sessionId) async {
    throw UnimplementedError();
  }

  @override
  Future<void> submitTelemetryBatch({
    required List<LearningTelemetryEvent> events,
  }) async {
    calls += 1;
    if (failFirstFlush && calls == 1) {
      throw const BackendApiException('temporary failure');
    }
    batches.add(List<LearningTelemetryEvent>.from(events));
  }
}

void main() {
  LearningTelemetryEvent event(String eventType) {
    return LearningTelemetryEvent(
      lessonId: 'dp_policy_eval',
      conceptId: 'bellman_expectation',
      sessionId: 'study-session-1',
      eventType: eventType,
      occurredAtUtc: DateTime.utc(2026, 5, 13, 10),
      payloadJson: const {'value': 1},
    );
  }

  group('LearningTelemetryClient', () {
    test('flushes buffered events as one batch', () async {
      final api = _TelemetryApi();
      final client = LearningTelemetryClient(api: api, autoStart: false);

      client
        ..record(event('concept_video_session'))
        ..record(event('submission_result'));

      await client.flush();

      expect(client.pendingCount, 0);
      expect(api.batches, hasLength(1));
      expect(api.batches.single.map((item) => item.eventType), [
        'concept_video_session',
        'submission_result',
      ]);
    });

    test('keeps events in memory when a flush fails', () async {
      final api = _TelemetryApi(failFirstFlush: true);
      final client = LearningTelemetryClient(api: api, autoStart: false);

      client.record(event('code_run_result'));
      await client.flush();

      expect(client.pendingCount, 1);
      expect(api.batches, isEmpty);

      await client.flush();

      expect(client.pendingCount, 0);
      expect(api.batches.single.single.eventType, 'code_run_result');
    });

    test('caps the buffer by dropping oldest events', () async {
      final api = _TelemetryApi();
      final client = LearningTelemetryClient(
        api: api,
        autoStart: false,
        maxBufferSize: 2,
      );

      client
        ..record(event('first'))
        ..record(event('second'))
        ..record(event('third'));

      expect(client.pendingCount, 2);
      await client.flush();
      expect(api.batches.single.map((item) => item.eventType), [
        'second',
        'third',
      ]);
    });
  });
}
