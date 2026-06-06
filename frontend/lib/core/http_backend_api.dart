import 'dart:convert';

import 'package:http/http.dart' as http;

import 'backend_api.dart';
// ignore: unnecessary_import — explicit import required on Linux Dart (macOS resolves via export chain but Linux does not)
import 'backend_api_models.dart';
import 'constants.dart';
import 'lesson_models.dart';

class HttpBackendApi extends BackendApi {
  final http.Client _client;
  String? _accessToken;
  String get baseUrl => BackendConnectionManager().baseUrl;
  static const Map<String, String> _jsonHeaders = {
    'Content-Type': 'application/json',
  };

  HttpBackendApi({
    http.Client? client,
  }) : _client = client ?? http.Client();

  @override
  String? get accessToken => _accessToken;

  @override
  void clearAuthToken() {
    _accessToken = null;
    AuthSessionStore.accessToken = null;
  }

  @override
  Future<List<LessonSection>> fetchLessonSections() async {
    final responseJson = await _getJson('/lessons');
    final sections = responseJson['sections'];
    if (sections is List) {
      return sections
          .whereType<Map<String, dynamic>>()
          .map(LessonSection.fromJson)
          .where((section) => section.lessons.isNotEmpty)
          .toList(growable: false);
    }

    final lessons = responseJson['lessons'];
    if (lessons is List) {
      return _groupLessonsByCategory(
        lessons
            .whereType<Map<String, dynamic>>()
            .map(LessonDefinition.fromJson)
            .toList(growable: false),
      );
    }

    throw const BackendApiException('Lesson catalog could not be loaded.');
  }

  @override
  Future<List<LessonDefinition>> fetchAuthoredLessons() async {
    final responseJson = await _getJson('/admin/lessons/authored');
    final lessons = responseJson['lessons'];
    if (lessons is! List) {
      return const [];
    }
    return lessons
        .whereType<Map<String, dynamic>>()
        .map(LessonDefinition.fromJson)
        .toList(growable: false);
  }

  @override
  Future<LessonDefinition> saveAuthoredLesson({
    required LessonDefinition lesson,
  }) async {
    final responseJson = await _putJson(
      '/admin/lessons/authored/${Uri.encodeComponent(lesson.id)}',
      {'lesson': lesson.toJson()},
    );
    final lessonJson = responseJson['lesson'];
    if (lessonJson is Map<String, dynamic>) {
      return LessonDefinition.fromJson(lessonJson);
    }
    return lesson;
  }

  @override
  Future<void> deleteAuthoredLesson(String lessonId) async {
    await _delete('/admin/lessons/authored/${Uri.encodeComponent(lessonId)}');
  }

  @override
  Future<void> uploadLectureNotes({
    required String lessonId,
    required List<int> bytes,
    required String filename,
  }) async {
    final uri = Uri.parse(
        '$baseUrl/admin/lessons/${Uri.encodeComponent(lessonId)}/lecture-notes');
    final request = http.MultipartRequest('PUT', uri)
      ..files
          .add(http.MultipartFile.fromBytes('file', bytes, filename: filename));
    if (accessToken != null) {
      request.headers['Authorization'] = 'Bearer $accessToken';
    }
    final streamed = await request.send();
    if (streamed.statusCode >= 400) {
      final body = await streamed.stream.bytesToString();
      throw Exception('Upload failed (${streamed.statusCode}): $body');
    }
  }

  @override
  Future<void> deleteLectureNotes(String lessonId) async {
    await _delete(
        '/admin/lessons/${Uri.encodeComponent(lessonId)}/lecture-notes');
  }

  @override
  Future<LearnerDashboard> signIn({
    required String displayName,
    required String password,
    String? firebaseIdToken,
  }) async {
    final responseJson = await _postJson(
      '/auth/sign-in',
      {
        'display_name': displayName,
        'password': password,
        if (firebaseIdToken != null) 'firebase_id_token': firebaseIdToken,
      },
    );
    _accessToken = responseJson['access_token'] as String?;
    AuthSessionStore.accessToken = _accessToken;
    return LearnerDashboard.fromJson(responseJson);
  }

  @override
  Future<LearnerDashboard?> restoreSession() async {
    try {
      final responseJson = await _getJson('/me/dashboard');
      return LearnerDashboard.fromJson(responseJson);
    } on BackendApiException {
      clearAuthToken();
      return null;
    }
  }

  @override
  Future<void> signOut() async {
    try {
      await _postJson('/auth/sign-out', const {});
    } catch (_) {}
    _accessToken = null;
    AuthSessionStore.accessToken = null;
  }

  @override
  Future<LearnerDashboard> getDashboard() async {
    final responseJson = await _getJson('/me/dashboard');
    return LearnerDashboard.fromJson(responseJson);
  }

  @override
  Future<List<StaffStudentSummary>> fetchStaffStudents() async {
    final responseJson = await _getJson('/staff/students');
    final students = responseJson['students'] as List<dynamic>? ?? const [];
    return students
        .whereType<Map<String, dynamic>>()
        .map(StaffStudentSummary.fromJson)
        .toList(growable: false);
  }

  @override
  Future<LearnerDashboard> fetchStaffStudentDashboard(String studentId) async {
    final responseJson = await _getJson('/staff/students/$studentId/dashboard');
    return LearnerDashboard.fromJson(responseJson);
  }

  @override
  Future<QuizSessionData> startQuiz({
    required QuizPhase phase,
  }) async {
    final responseJson = await _postJson(
      '/quiz/start',
      {
        'phase': quizPhaseApiValue(phase),
      },
    );
    return QuizSessionData.fromJson(responseJson);
  }

  @override
  Future<QuizAttemptSummary> submitQuiz({
    required String sessionId,
    required Map<String, int> answers,
  }) async {
    final responseJson = await _postJson(
      '/quiz/submit',
      {
        'session_id': sessionId,
        'answers': answers.entries
            .map(
              (entry) => {
                'question_id': entry.key,
                'selected_index': entry.value,
              },
            )
            .toList(growable: false),
      },
    );
    return QuizAttemptSummary.fromJson(responseJson);
  }

  @override
  Future<SubmittedExecutionTask> submitCode({
    required String lessonId,
    required String code,
    String? studentId,
    String? sessionId,
  }) async {
    final responseJson = await _postJson(
      '/submit',
      {
        'lesson_id': lessonId,
        'code': code,
        if (sessionId != null) 'session_id': sessionId,
      },
    );
    return SubmittedExecutionTask.fromJson(responseJson);
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
    if (susResponses.length != 10) {
      throw const BackendApiException('SUS requires exactly 10 responses.');
    }

    final responseJson = await _postJson(
      '/evaluation/survey/submit',
      {
        'study_session_id': studySessionId,
        'condition': condition,
        for (var index = 0; index < susResponses.length; index += 1)
          'sus_q${index + 1}': susResponses[index],
        'tlx_mental_demand': tlxMentalDemand,
        'tlx_physical_demand': tlxPhysicalDemand,
        'tlx_temporal_demand': tlxTemporalDemand,
        'tlx_performance': tlxPerformance,
        'tlx_effort': tlxEffort,
        'tlx_frustration': tlxFrustration,
        if (feedbackHelpful != null && feedbackHelpful.trim().isNotEmpty)
          'feedback_helpful': feedbackHelpful.trim(),
        if (feedbackConfusing != null && feedbackConfusing.trim().isNotEmpty)
          'feedback_confusing': feedbackConfusing.trim(),
        if (feedbackImprovement != null &&
            feedbackImprovement.trim().isNotEmpty)
          'feedback_improvement': feedbackImprovement.trim(),
      },
    );
    return StudySessionSurveyResult.fromJson(responseJson);
  }

  @override
  Future<void> submitTelemetryBatch({
    required List<LearningTelemetryEvent> events,
  }) async {
    if (events.isEmpty) {
      return;
    }
    await _postJson(
      '/telemetry/events',
      {
        'events': events.map((event) => event.toJson()).toList(growable: false),
      },
    );
  }

  @override
  Future<StudyBuddyIntervention?> fetchPendingStudyBuddyIntervention({
    required String sessionId,
  }) async {
    final responseJson = await _getJson(
      '/study-buddy/interventions/$sessionId/pending',
    );
    final intervention = responseJson['intervention'];
    if (intervention is Map<String, dynamic>) {
      return StudyBuddyIntervention.fromJson(intervention);
    }
    return null;
  }

  @override
  Future<StudyBuddyIntervention?> respondToStudyBuddyIntervention({
    required String interventionId,
    required String response,
  }) async {
    final responseJson = await _postJson(
      '/study-buddy/interventions/$interventionId/respond',
      {'response': response},
    );
    final intervention = responseJson['intervention'];
    if (intervention is Map<String, dynamic>) {
      return StudyBuddyIntervention.fromJson(intervention);
    }
    return null;
  }

  @override
  Future<StudyBuddySummary?> fetchStudyBuddySummary() async {
    final responseJson = await _getJson('/me/study-buddy/summary');
    return StudyBuddySummary.fromJson(responseJson);
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
    final responseJson = await _postJson(
      '/me/study-buddy/chat',
      {
        'lesson_id': lessonId,
        'session_id': sessionId,
        'message': message,
        if (currentCode != null) 'current_code': currentCode,
        'unresolved_blanks': unresolvedBlanks,
        if (failureKind != null) 'failure_kind': failureKind,
        'latest_feedback': latestFeedback,
        'history':
            history.map((entry) => entry.toJson()).toList(growable: false),
      },
    );
    return StudyBuddyChatResponse.fromJson(responseJson);
  }

  @override
  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId) async {
    final responseJson = await _getJson('/tasks/$taskId');
    return ExecutionTaskSnapshot.fromJson(responseJson);
  }

  @override
  Future<ReplayRenderStatus> getReplayRenderStatus(String jobId) async {
    final responseJson = await _getJson('/visualization/replay-render/$jobId');
    return ReplayRenderStatus.fromJson(responseJson);
  }

  @override
  Future<NGainMetricsExport> exportNGainMetrics() async {
    final response = await _client.get(
      Uri.parse('$baseUrl/admin/metrics/n-gain/export'),
      headers: _authorizedHeaders(),
    );

    if (response.statusCode >= 400) {
      throw _buildBackendException(_decodeBody(response.body));
    }

    final fileName = _extractExportFileName(
      response.headers['content-disposition'],
      fallback: 'n_gain_metrics.xlsx',
    );
    return NGainMetricsExport(
      fileName: fileName,
      bytes: response.bodyBytes,
    );
  }

  @override
  Future<LearningAnalyticsExport> exportLearningAnalytics() async {
    final response = await _client.get(
      Uri.parse('$baseUrl/admin/metrics/learning-analytics/export'),
      headers: _authorizedHeaders(),
    );

    if (response.statusCode >= 400) {
      throw _buildBackendException(_decodeBody(response.body));
    }

    final fileName = _extractExportFileName(
      response.headers['content-disposition'],
      fallback: 'learning_analytics.xlsx',
    );
    return LearningAnalyticsExport(
      fileName: fileName,
      bytes: response.bodyBytes,
    );
  }

  @override
  Future<ALEIComponentsExport> exportALEIComponents() async {
    final response = await _client.get(
      Uri.parse('$baseUrl/evaluation/export/alei-components'),
      headers: _authorizedHeaders(),
    );

    if (response.statusCode >= 400) {
      throw _buildBackendException(_decodeBody(response.body));
    }

    final fileName = _extractExportFileName(
      response.headers['content-disposition'],
      fallback: 'alei_components.xlsx',
    );
    return ALEIComponentsExport(
      fileName: fileName,
      bytes: response.bodyBytes,
    );
  }

  @override
  Future<WorkspaceSessionData> createWorkspaceSession({
    required String lessonId,
  }) async {
    final responseJson = await _postJson(
      '/workspace/sessions',
      {'lesson_id': lessonId},
    );
    return WorkspaceSessionData.fromJson(responseJson);
  }

  @override
  Future<WorkspaceHealthData> getWorkspaceHealth() async {
    final responseJson = await _getJson('/workspace/health');
    return WorkspaceHealthData.fromJson(responseJson);
  }

  @override
  Future<WorkspaceSessionData> getWorkspaceSession(String sessionId) async {
    final responseJson = await _getJson('/workspace/sessions/$sessionId');
    return WorkspaceSessionData.fromJson(responseJson);
  }

  @override
  Future<WorkspaceFileSnapshot> getWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
  }) async {
    final responseJson = await _getJson(
      '/workspace/sessions/$sessionId/files/$path',
    );
    return WorkspaceFileSnapshot.fromJson(responseJson);
  }

  @override
  Future<WorkspaceFileSnapshot> updateWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
    required String content,
  }) async {
    final responseJson = await _putJson(
      '/workspace/sessions/$sessionId/files/$path',
      {'content': content},
    );
    return WorkspaceFileSnapshot.fromJson(responseJson);
  }

  @override
  Future<WorkspaceRunData> runWorkspaceScript({
    required String sessionId,
  }) async {
    final responseJson = await _postJson(
      '/workspace/sessions/$sessionId/run',
      const {},
    );
    return WorkspaceRunData.fromJson(responseJson);
  }

  @override
  Future<WorkspaceRunData> getWorkspaceRun({
    required String sessionId,
    required String runId,
  }) async {
    final responseJson = await _getJson(
      '/workspace/sessions/$sessionId/runs/$runId',
    );
    return WorkspaceRunData.fromJson(responseJson);
  }

  @override
  Future<String> workspaceEditorShellUrl(String sessionId) async {
    final responseJson =
        await _getJson('/workspace/sessions/$sessionId/editor-shell');
    final rawUrl = responseJson['editor_shell_url'] as String?;
    if (rawUrl == null || rawUrl.trim().isEmpty) {
      throw const BackendApiException(
        'Workspace shell could not be opened.',
      );
    }
    return Uri.parse(baseUrl).resolve(rawUrl).toString();
  }

  Future<Map<String, dynamic>> _postJson(
    String path,
    Map<String, dynamic> payload,
  ) async {
    final response = await _client
        .post(
          Uri.parse('$baseUrl$path'),
          headers: _authorizedHeaders(_jsonHeaders),
          body: jsonEncode(payload),
        )
        .timeout(
          path == '/auth/sign-in'
              ? AppConstants.backendAuthTimeout
              : AppConstants.backendRequestTimeout,
        );
    return _decodeAndValidateResponse(response);
  }

  Future<Map<String, dynamic>> _getJson(String path) async {
    final response = await _client
        .get(
          Uri.parse('$baseUrl$path'),
          headers: _authorizedHeaders(),
        )
        .timeout(AppConstants.backendRequestTimeout);
    return _decodeAndValidateResponse(response);
  }

  Future<Map<String, dynamic>> _putJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    final uri = Uri.parse('$baseUrl$path');
    final response = await _client
        .put(
          uri,
          headers: _authorizedHeaders(_jsonHeaders),
          body: jsonEncode(body),
        )
        .timeout(AppConstants.backendRequestTimeout);
    return _decodeAndValidateResponse(response);
  }

  Future<void> _delete(String path) async {
    final response = await _client
        .delete(
          Uri.parse('$baseUrl$path'),
          headers: _authorizedHeaders(),
        )
        .timeout(AppConstants.backendRequestTimeout);
    _decodeAndValidateResponse(response);
  }

  Map<String, String> _authorizedHeaders([
    Map<String, String> base = const {},
  ]) {
    final headers = <String, String>{...base};
    final token = _accessToken;
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  Map<String, dynamic> _decodeAndValidateResponse(http.Response response) {
    final responseJson = _decodeBody(response.body);
    if (response.statusCode >= 400) {
      throw _buildBackendException(responseJson);
    }
    return responseJson;
  }

  Map<String, dynamic> _decodeBody(String body) {
    if (body.isEmpty) {
      return const {};
    }

    final decoded = jsonDecode(body);
    if (decoded is Map<String, dynamic>) {
      return decoded;
    }

    throw const BackendApiException('Unexpected platform response.');
  }
}

List<LessonSection> _groupLessonsByCategory(List<LessonDefinition> lessons) {
  final grouped = <String, List<LessonDefinition>>{};
  for (final lesson in lessons) {
    grouped
        .putIfAbsent(lesson.category, () => <LessonDefinition>[])
        .add(lesson);
  }
  return grouped.entries
      .map((entry) => LessonSection(title: entry.key, lessons: entry.value))
      .toList(growable: false);
}

String _extractExportFileName(
  String? contentDisposition, {
  required String fallback,
}) {
  if (contentDisposition == null) {
    return fallback;
  }

  final parts = contentDisposition.split(';');
  for (final part in parts) {
    final trimmed = part.trim();
    if (trimmed.toLowerCase().startsWith('filename=')) {
      final value = trimmed.substring('filename='.length).trim();
      return value.replaceAll('"', '');
    }
  }

  return fallback;
}

BackendApiException _buildBackendException(Map<String, dynamic> responseJson) {
  return BackendApiException(
    _extractApiErrorMessage(responseJson),
    testResults: _extractTestResults(responseJson),
    failureKind: _extractFailureKind(responseJson),
    unresolvedBlanks: _extractUnresolvedBlanks(responseJson),
    studentFeedback: _extractStudentFeedback(responseJson),
  );
}

String _extractApiErrorMessage(Map<String, dynamic> responseJson) {
  final detail = responseJson['detail'];
  if (detail is String && detail.isNotEmpty) {
    return detail;
  }

  if (detail is Map<String, dynamic>) {
    final message = detail['message'];
    final issues = detail['issues'];
    if (issues is List && issues.isNotEmpty) {
      return '$message ${issues.join(' ')}'.trim();
    }
    if (message is String && message.isNotEmpty) {
      return message;
    }
  }

  return 'Request failed.';
}

List<ExecutionTestCaseResult> _extractTestResults(
  Map<String, dynamic> response,
) {
  final detail = response['detail'];
  if (detail is Map<String, dynamic>) {
    final tests = detail['test_results'];
    if (tests is List) {
      return tests
          .whereType<Map<String, dynamic>>()
          .map(ExecutionTestCaseResult.fromJson)
          .toList(growable: false);
    }
  }

  return const [];
}

String? _extractFailureKind(Map<String, dynamic> response) {
  final detail = response['detail'];
  if (detail is Map<String, dynamic>) {
    return detail['failure_kind'] as String?;
  }
  return null;
}

List<String> _extractUnresolvedBlanks(Map<String, dynamic> response) {
  final detail = response['detail'];
  if (detail is Map<String, dynamic>) {
    return (detail['unresolved_blanks'] as List<dynamic>? ?? const [])
        .map((value) => value.toString())
        .toList(growable: false);
  }
  return const [];
}

ExecutionStudentFeedback? _extractStudentFeedback(
  Map<String, dynamic> response,
) {
  final detail = response['detail'];
  if (detail is Map<String, dynamic>) {
    final feedback = detail['student_feedback'];
    if (feedback is Map<String, dynamic>) {
      return ExecutionStudentFeedback.fromJson(feedback);
    }
  }
  return null;
}
