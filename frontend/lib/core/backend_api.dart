import 'dart:async';

import 'backend_api_models.dart';
import 'lesson_models.dart';

export 'backend_api_models.dart';
export 'backend_connection_manager.dart';

abstract class BackendApi {
  Future<List<LessonSection>> fetchLessonSections();

  Future<List<LessonDefinition>> fetchAuthoredLessons() async {
    return const [];
  }

  Future<LessonDefinition> saveAuthoredLesson({
    required LessonDefinition lesson,
  }) {
    throw UnimplementedError();
  }

  Future<void> deleteAuthoredLesson(String lessonId) async {}

  /// Upload a Markdown file as lecture notes for [lessonId].
  Future<void> uploadLectureNotes({
    required String lessonId,
    required List<int> bytes,
    required String filename,
  }) async {}

  /// Remove the admin-uploaded lecture notes for [lessonId].
  Future<void> deleteLectureNotes(String lessonId) async {}

  Future<LearnerDashboard> signIn({
    required String displayName,
    required String password,
    String? firebaseIdToken,
  });

  Future<LearnerDashboard?> restoreSession() async {
    return null;
  }

  Future<void> signOut() async {}

  Future<LearnerDashboard> getDashboard();

  Future<List<StaffStudentSummary>> fetchStaffStudents();

  Future<LearnerDashboard> fetchStaffStudentDashboard(String studentId);

  Future<QuizSessionData> startQuiz({
    required QuizPhase phase,
  });

  Future<QuizAttemptSummary> submitQuiz({
    required String sessionId,
    required Map<String, int> answers,
  });

  Future<SubmittedExecutionTask> submitCode({
    required String lessonId,
    required String code,
    String? studentId,
    String? sessionId,
  });

  Future<void> submitTelemetryBatch({
    required List<LearningTelemetryEvent> events,
  }) async {}

  Future<StudyBuddyIntervention?> fetchPendingStudyBuddyIntervention({
    required String sessionId,
  }) async {
    return null;
  }

  Future<StudyBuddyIntervention?> respondToStudyBuddyIntervention({
    required String interventionId,
    required String response,
  }) async {
    return null;
  }

  Future<StudyBuddySummary?> fetchStudyBuddySummary() async {
    return null;
  }

  Future<StudyBuddyChatResponse> sendStudyBuddyChat({
    required String lessonId,
    required String sessionId,
    required String message,
    required List<StudyBuddyChatMessage> history,
    String? currentCode,
    List<String> unresolvedBlanks = const [],
    String? failureKind,
    Map<String, dynamic> latestFeedback = const {},
  }) {
    throw UnimplementedError();
  }

  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId);

  Future<ReplayRenderStatus> getReplayRenderStatus(String jobId) {
    throw UnimplementedError();
  }

  Future<NGainMetricsExport> exportNGainMetrics();

  Future<LearningAnalyticsExport> exportLearningAnalytics() {
    throw UnimplementedError();
  }

  Future<ALEIComponentsExport> exportALEIComponents() {
    throw UnimplementedError();
  }

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
  }) {
    throw UnimplementedError();
  }

  Future<WorkspaceSessionData> createWorkspaceSession({
    required String lessonId,
  });

  Future<WorkspaceHealthData> getWorkspaceHealth();

  Future<WorkspaceSessionData> getWorkspaceSession(String sessionId);

  Future<WorkspaceFileSnapshot> getWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
  });

  Future<WorkspaceFileSnapshot> updateWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
    required String content,
  });

  Future<WorkspaceRunData> runWorkspaceScript({
    required String sessionId,
  });

  Future<WorkspaceRunData> getWorkspaceRun({
    required String sessionId,
    required String runId,
  });

  Future<String> workspaceEditorShellUrl(String sessionId);

  String? get accessToken;

  void clearAuthToken();

  Future<ExecutionResult> executeCode({
    required String lessonId,
    required String code,
    String? studentId,
  }) async {
    final task = await submitCode(
      lessonId: lessonId,
      code: code,
      studentId: studentId,
    );

    while (true) {
      final snapshot = await getTaskStatus(task.taskId);
      if (snapshot.status == ExecutionTaskStatus.succeeded &&
          snapshot.result != null) {
        return snapshot.result!;
      }
      if (snapshot.status == ExecutionTaskStatus.failed) {
        throw BackendApiException(
          snapshot.errorMessage ?? 'Execution task failed.',
          testResults: snapshot.testResults,
          failureKind: snapshot.failureKind,
          unresolvedBlanks: snapshot.unresolvedBlanks,
          studentFeedback: snapshot.studentFeedback,
        );
      }

      await Future<void>.delayed(const Duration(milliseconds: 500));
    }
  }
}

class LearningTelemetryClient {
  final BackendApi _api;
  final Duration flushInterval;
  final int maxBufferSize;
  final List<LearningTelemetryEvent> _buffer = [];
  Timer? _flushTimer;
  Timer? _retryTimer;
  bool _flushInProgress = false;
  bool _disposed = false;
  int _consecutiveFailures = 0;

  LearningTelemetryClient({
    required BackendApi api,
    this.flushInterval = const Duration(seconds: 10),
    this.maxBufferSize = 200,
    bool autoStart = true,
  }) : _api = api {
    if (autoStart) {
      start();
    }
  }

  int get pendingCount => _buffer.length;

  void start() {
    if (_disposed || _flushTimer != null) {
      return;
    }
    _flushTimer = Timer.periodic(
      flushInterval,
      (_) => unawaited(flush()),
    );
  }

  void record(LearningTelemetryEvent event) {
    if (_disposed) {
      return;
    }
    while (_buffer.length >= maxBufferSize) {
      _buffer.removeAt(0);
    }
    _buffer.add(event);
  }

  Future<void> flush({bool retryOnFailure = true}) async {
    if (_disposed || _flushInProgress || _buffer.isEmpty) {
      return;
    }

    _flushInProgress = true;
    final batch = List<LearningTelemetryEvent>.from(_buffer);
    try {
      await _api.submitTelemetryBatch(events: batch);
      for (final event in batch) {
        _buffer.remove(event);
      }
      _consecutiveFailures = 0;
      _retryTimer?.cancel();
      _retryTimer = null;
    } catch (_) {
      _consecutiveFailures += 1;
      if (retryOnFailure) {
        _scheduleRetry();
      }
    } finally {
      _flushInProgress = false;
    }
  }

  Future<void> dispose() async {
    _flushTimer?.cancel();
    _retryTimer?.cancel();
    await flush(retryOnFailure: false);
    _disposed = true;
  }

  void _scheduleRetry() {
    if (_disposed || (_retryTimer?.isActive ?? false)) {
      return;
    }
    final cappedFailures = _consecutiveFailures > 6 ? 6 : _consecutiveFailures;
    final seconds = 1 << (cappedFailures - 1);
    _retryTimer = Timer(
      Duration(seconds: seconds),
      () => unawaited(flush()),
    );
  }
}
