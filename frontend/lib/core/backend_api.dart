import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

const String defaultBackendBaseUrl = String.fromEnvironment(
  'BACKEND_BASE_URL',
  defaultValue: kIsWeb ? 'http://127.0.0.1:8000' : 'http://127.0.0.1:8000',
);

class BackendApiException implements Exception {
  final String message;
  final List<ExecutionTestCaseResult> testResults;

  const BackendApiException(this.message, {this.testResults = const []});

  @override
  String toString() => message;
}

enum QuizPhase { pretest, posttest }

String quizPhaseApiValue(QuizPhase phase) {
  switch (phase) {
    case QuizPhase.pretest:
      return 'pretest';
    case QuizPhase.posttest:
      return 'posttest';
  }
}

String quizPhaseLabel(QuizPhase phase) {
  switch (phase) {
    case QuizPhase.pretest:
      return 'Pre-test';
    case QuizPhase.posttest:
      return 'Post-test';
  }
}

QuizPhase _parseQuizPhase(String? value) {
  switch (value) {
    case 'pretest':
      return QuizPhase.pretest;
    case 'posttest':
      return QuizPhase.posttest;
    default:
      throw const BackendApiException(
        'Backend returned an unknown quiz phase.',
      );
  }
}

enum ExecutionTaskStatus { queued, running, succeeded, failed }

ExecutionTaskStatus _parseTaskStatus(String? value) {
  switch (value) {
    case 'queued':
      return ExecutionTaskStatus.queued;
    case 'running':
      return ExecutionTaskStatus.running;
    case 'succeeded':
      return ExecutionTaskStatus.succeeded;
    case 'failed':
      return ExecutionTaskStatus.failed;
    default:
      throw const BackendApiException(
        'Backend returned an unknown task status.',
      );
  }
}

class LearnerProfile {
  final String id;
  final String displayName;

  const LearnerProfile({
    required this.id,
    required this.displayName,
  });

  factory LearnerProfile.fromJson(Map<String, dynamic> json) {
    return LearnerProfile(
      id: json['id'] as String? ?? '',
      displayName: json['display_name'] as String? ?? 'Student',
    );
  }
}

class LearnerProgress {
  final List<String> completedLessonIds;
  final int successfulRuns;
  final String? latestLessonId;
  final double? pretestScore;
  final double? posttestScore;
  final double? nGain;
  final Map<String, int> quizAttempts;

  const LearnerProgress({
    required this.completedLessonIds,
    required this.successfulRuns,
    required this.latestLessonId,
    required this.pretestScore,
    required this.posttestScore,
    required this.nGain,
    required this.quizAttempts,
  });

  const LearnerProgress.empty()
      : completedLessonIds = const [],
        successfulRuns = 0,
        latestLessonId = null,
        pretestScore = null,
        posttestScore = null,
        nGain = null,
        quizAttempts = const {
          'pretest': 0,
          'posttest': 0,
        };

  int get lessonsCompleted => completedLessonIds.length;

  factory LearnerProgress.fromJson(Map<String, dynamic> json) {
    final rawQuizAttempts =
        (json['quiz_attempts'] as Map<String, dynamic>?) ?? const {};
    return LearnerProgress(
      completedLessonIds:
          (json['completed_lesson_ids'] as List<dynamic>? ?? const [])
              .map((value) => value.toString())
              .toList(growable: false),
      successfulRuns: (json['successful_runs'] as num?)?.toInt() ?? 0,
      latestLessonId: json['latest_lesson_id'] as String?,
      pretestScore: (json['pretest_score'] as num?)?.toDouble(),
      posttestScore: (json['posttest_score'] as num?)?.toDouble(),
      nGain: (json['n_gain'] as num?)?.toDouble(),
      quizAttempts: rawQuizAttempts.map(
        (key, value) => MapEntry(key, (value as num).toInt()),
      ),
    );
  }
}

class LearnerDashboard {
  final LearnerProfile student;
  final LearnerProgress progress;

  const LearnerDashboard({
    required this.student,
    required this.progress,
  });

  factory LearnerDashboard.fromJson(Map<String, dynamic> json) {
    return LearnerDashboard(
      student: LearnerProfile.fromJson(
        (json['student'] as Map<String, dynamic>?) ?? const {},
      ),
      progress: LearnerProgress.fromJson(
        (json['progress'] as Map<String, dynamic>?) ?? const {},
      ),
    );
  }
}

class QuizQuestionData {
  final String id;
  final String concept;
  final String prompt;
  final List<String> options;

  const QuizQuestionData({
    required this.id,
    required this.concept,
    required this.prompt,
    required this.options,
  });

  factory QuizQuestionData.fromJson(Map<String, dynamic> json) {
    return QuizQuestionData(
      id: json['id'] as String? ?? '',
      concept: json['concept'] as String? ?? 'Concept',
      prompt: json['prompt'] as String? ?? '',
      options: (json['options'] as List<dynamic>? ?? const [])
          .map((option) => option.toString())
          .toList(growable: false),
    );
  }
}

class QuizSessionData {
  final String sessionId;
  final QuizPhase phase;
  final int questionCount;
  final List<QuizQuestionData> questions;

  const QuizSessionData({
    required this.sessionId,
    required this.phase,
    required this.questionCount,
    required this.questions,
  });

  factory QuizSessionData.fromJson(Map<String, dynamic> json) {
    return QuizSessionData(
      sessionId: json['session_id'] as String? ?? '',
      phase: _parseQuizPhase(json['phase'] as String?),
      questionCount: (json['question_count'] as num?)?.toInt() ?? 0,
      questions: (json['questions'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(QuizQuestionData.fromJson)
          .toList(growable: false),
    );
  }
}

class QuizAttemptSummary {
  final QuizPhase phase;
  final int score;
  final int totalQuestions;
  final double percentage;
  final double? nGain;
  final LearnerProgress progress;

  const QuizAttemptSummary({
    required this.phase,
    required this.score,
    required this.totalQuestions,
    required this.percentage,
    required this.nGain,
    required this.progress,
  });

  factory QuizAttemptSummary.fromJson(Map<String, dynamic> json) {
    return QuizAttemptSummary(
      phase: _parseQuizPhase(json['phase'] as String?),
      score: (json['score'] as num?)?.toInt() ?? 0,
      totalQuestions: (json['total_questions'] as num?)?.toInt() ?? 0,
      percentage: (json['percentage'] as num?)?.toDouble() ?? 0.0,
      nGain: (json['n_gain'] as num?)?.toDouble(),
      progress: LearnerProgress.fromJson(
        (json['progress'] as Map<String, dynamic>?) ?? const {},
      ),
    );
  }
}

class ExecutionMetrics {
  final int episodesCompleted;
  final int stepsRecorded;
  final double totalReward;
  final double averageReward;
  final double bestEpisodeReward;

  const ExecutionMetrics({
    required this.episodesCompleted,
    required this.stepsRecorded,
    required this.totalReward,
    required this.averageReward,
    required this.bestEpisodeReward,
  });

  factory ExecutionMetrics.fromJson(Map<String, dynamic> json) {
    return ExecutionMetrics(
      episodesCompleted: (json['episodes_completed'] as num?)?.toInt() ?? 0,
      stepsRecorded: (json['steps_recorded'] as num?)?.toInt() ?? 0,
      totalReward: (json['total_reward'] as num?)?.toDouble() ?? 0,
      averageReward: (json['average_reward'] as num?)?.toDouble() ?? 0,
      bestEpisodeReward: (json['best_episode_reward'] as num?)?.toDouble() ?? 0,
    );
  }
}

class ExecutionTestCaseResult {
  final String name;
  final bool passed;
  final String message;
  final String expected;
  final String actual;

  const ExecutionTestCaseResult({
    required this.name,
    required this.passed,
    required this.message,
    required this.expected,
    required this.actual,
  });

  factory ExecutionTestCaseResult.fromJson(Map<String, dynamic> json) {
    return ExecutionTestCaseResult(
      name: json['name'] as String? ?? 'sample_test',
      passed: json['passed'] as bool? ?? false,
      message: json['message'] as String? ?? '',
      expected: json['expected'] as String? ?? '',
      actual: json['actual'] as String? ?? '',
    );
  }
}

class ExecutionTraceStep {
  final int state;
  final int action;
  final int nextState;
  final double reward;
  final double transitionProbability;
  final String framePath;
  final String agentCaption;
  final String codeTitle;
  final List<String> codeLines;
  final String mathTitle;
  final String mathEquation;
  final List<String> mathLines;
  final Map<String, double> updatedValues;

  const ExecutionTraceStep({
    required this.state,
    required this.action,
    required this.nextState,
    required this.reward,
    required this.transitionProbability,
    required this.framePath,
    required this.agentCaption,
    required this.codeTitle,
    required this.codeLines,
    required this.mathTitle,
    required this.mathEquation,
    required this.mathLines,
    required this.updatedValues,
  });

  factory ExecutionTraceStep.fromJson(Map<String, dynamic> json) {
    final rawUpdatedValues =
        (json['updated_values'] as Map<String, dynamic>?) ?? const {};
    return ExecutionTraceStep(
      state: (json['state'] as num?)?.toInt() ?? 0,
      action: (json['action'] as num?)?.toInt() ?? 0,
      nextState: (json['next_state'] as num?)?.toInt() ?? 0,
      reward: (json['reward'] as num?)?.toDouble() ?? 0.0,
      transitionProbability:
          (json['transition_probability'] as num?)?.toDouble() ?? 1.0,
      framePath: json['frame_path'] as String? ?? '',
      agentCaption: json['agent_caption'] as String? ?? '',
      codeTitle: json['code_title'] as String? ?? 'Code Trace',
      codeLines: (json['code_lines'] as List<dynamic>? ?? const [])
          .map((line) => line.toString())
          .toList(growable: false),
      mathTitle: json['math_title'] as String? ?? 'Mathematics',
      mathEquation: json['math_equation'] as String? ?? '',
      mathLines: (json['math_lines'] as List<dynamic>? ?? const [])
          .map((line) => line.toString())
          .toList(growable: false),
      updatedValues: rawUpdatedValues.map(
        (key, value) => MapEntry(key, (value as num).toDouble()),
      ),
    );
  }
}

class ExecutionResult {
  final String message;
  final String lessonTitle;
  final String videoPath;
  final bool visualizationReady;
  final ExecutionMetrics metrics;
  final List<ExecutionTestCaseResult> testResults;
  final List<ExecutionTraceStep> stepTrace;

  const ExecutionResult({
    required this.message,
    required this.lessonTitle,
    required this.videoPath,
    required this.visualizationReady,
    required this.metrics,
    required this.testResults,
    required this.stepTrace,
  });

  factory ExecutionResult.fromJson(Map<String, dynamic> json) {
    final lesson = (json['lesson'] as Map<String, dynamic>?) ?? const {};
    final metrics = (json['metrics'] as Map<String, dynamic>?) ?? const {};
    final testResults = (json['test_results'] as List<dynamic>? ?? const [])
        .whereType<Map<String, dynamic>>()
        .map(ExecutionTestCaseResult.fromJson)
        .toList(growable: false);
    final stepTrace = (json['step_trace'] as List<dynamic>? ?? const [])
        .whereType<Map<String, dynamic>>()
        .map(ExecutionTraceStep.fromJson)
        .toList(growable: false);

    return ExecutionResult(
      message: json['message'] as String? ?? 'Execution completed.',
      lessonTitle: lesson['title'] as String? ?? '',
      videoPath: json['video_path'] as String? ?? '',
      visualizationReady: json['visualization_ready'] as bool? ?? false,
      metrics: ExecutionMetrics.fromJson(metrics),
      testResults: testResults,
      stepTrace: stepTrace,
    );
  }
}

class SubmittedExecutionTask {
  final String taskId;
  final ExecutionTaskStatus status;

  const SubmittedExecutionTask({
    required this.taskId,
    required this.status,
  });

  factory SubmittedExecutionTask.fromJson(Map<String, dynamic> json) {
    return SubmittedExecutionTask(
      taskId: json['task_id'] as String? ?? '',
      status: _parseTaskStatus(json['status'] as String?),
    );
  }
}

class ExecutionTaskSnapshot {
  final String taskId;
  final ExecutionTaskStatus status;
  final ExecutionResult? result;
  final String? errorMessage;
  final List<ExecutionTestCaseResult> testResults;

  const ExecutionTaskSnapshot({
    required this.taskId,
    required this.status,
    this.result,
    this.errorMessage,
    this.testResults = const [],
  });

  bool get isTerminal =>
      status == ExecutionTaskStatus.succeeded ||
      status == ExecutionTaskStatus.failed;

  factory ExecutionTaskSnapshot.fromJson(Map<String, dynamic> json) {
    final resultJson = json['result'];
    return ExecutionTaskSnapshot(
      taskId: json['task_id'] as String? ?? '',
      status: _parseTaskStatus(json['status'] as String?),
      result: resultJson is Map<String, dynamic>
          ? ExecutionResult.fromJson(resultJson)
          : null,
      errorMessage: _extractTaskErrorMessage(json['error']),
      testResults: _extractTaskTestResults(json['error']),
    );
  }
}

class NGainMetricsExport {
  final String fileName;
  final List<int> bytes;

  const NGainMetricsExport({
    required this.fileName,
    required this.bytes,
  });
}

abstract class BackendApi {
  Future<LearnerDashboard> signIn({
    required String displayName,
  });

  Future<LearnerDashboard> getDashboard({
    required String studentId,
  });

  Future<QuizSessionData> startQuiz({
    required String studentId,
    required QuizPhase phase,
  });

  Future<QuizAttemptSummary> submitQuiz({
    required String studentId,
    required String sessionId,
    required Map<String, int> answers,
  });

  Future<SubmittedExecutionTask> submitCode({
    required String lessonId,
    required String code,
    String? studentId,
  });

  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId);

  Future<NGainMetricsExport> exportNGainMetrics();

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
        );
      }

      await Future<void>.delayed(const Duration(milliseconds: 500));
    }
  }
}

class HttpBackendApi extends BackendApi {
  final http.Client _client;
  final String baseUrl;
  static const Map<String, String> _jsonHeaders = {
    'Content-Type': 'application/json',
  };

  HttpBackendApi({
    http.Client? client,
    this.baseUrl = defaultBackendBaseUrl,
  }) : _client = client ?? http.Client();

  @override
  Future<LearnerDashboard> signIn({
    required String displayName,
  }) async {
    final responseJson = await _postJson(
      '/auth/sign-in',
      {
        'display_name': displayName,
      },
    );
    return LearnerDashboard.fromJson(responseJson);
  }

  @override
  Future<LearnerDashboard> getDashboard({
    required String studentId,
  }) async {
    final responseJson = await _getJson('/students/$studentId/dashboard');
    return LearnerDashboard.fromJson(responseJson);
  }

  @override
  Future<QuizSessionData> startQuiz({
    required String studentId,
    required QuizPhase phase,
  }) async {
    final responseJson = await _postJson(
      '/quiz/start',
      {
        'student_id': studentId,
        'phase': quizPhaseApiValue(phase),
      },
    );
    return QuizSessionData.fromJson(responseJson);
  }

  @override
  Future<QuizAttemptSummary> submitQuiz({
    required String studentId,
    required String sessionId,
    required Map<String, int> answers,
  }) async {
    final responseJson = await _postJson(
      '/quiz/submit',
      {
        'student_id': studentId,
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
  }) async {
    final responseJson = await _postJson(
      '/submit',
      {
        'lesson_id': lessonId,
        'code': code,
        if (studentId != null) 'student_id': studentId,
      },
    );
    return SubmittedExecutionTask.fromJson(responseJson);
  }

  @override
  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId) async {
    final responseJson = await _getJson('/tasks/$taskId');
    return ExecutionTaskSnapshot.fromJson(responseJson);
  }

  @override
  Future<NGainMetricsExport> exportNGainMetrics() async {
    final response = await _client.get(
      Uri.parse('$baseUrl/admin/metrics/n-gain/export'),
    );

    if (response.statusCode >= 400) {
      throw _buildBackendException(_decodeBody(response.body));
    }

    final fileName = _extractExportFileName(
      response.headers['content-disposition'],
    );
    return NGainMetricsExport(
      fileName: fileName,
      bytes: response.bodyBytes,
    );
  }

  Future<Map<String, dynamic>> _postJson(
    String path,
    Map<String, dynamic> payload,
  ) async {
    final response = await _client.post(
      Uri.parse('$baseUrl$path'),
      headers: _jsonHeaders,
      body: jsonEncode(payload),
    );
    return _decodeAndValidateResponse(response);
  }

  Future<Map<String, dynamic>> _getJson(String path) async {
    final response = await _client.get(Uri.parse('$baseUrl$path'));
    return _decodeAndValidateResponse(response);
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

    throw const BackendApiException('Backend returned an unexpected response.');
  }
}

String _extractExportFileName(String? contentDisposition) {
  if (contentDisposition == null) {
    return 'n_gain_metrics.xlsx';
  }

  final parts = contentDisposition.split(';');
  for (final part in parts) {
    final trimmed = part.trim();
    if (trimmed.toLowerCase().startsWith('filename=')) {
      final value = trimmed.substring('filename='.length).trim();
      return value.replaceAll('"', '');
    }
  }

  return 'n_gain_metrics.xlsx';
}

BackendApiException _buildBackendException(Map<String, dynamic> responseJson) {
  return BackendApiException(
    _extractApiErrorMessage(responseJson),
    testResults: _extractTestResults(responseJson),
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

  return 'Backend request failed.';
}

String? _extractTaskErrorMessage(Object? error) {
  if (error == null) {
    return null;
  }

  if (error is String && error.isNotEmpty) {
    return error;
  }

  if (error is Map<String, dynamic>) {
    final message = error['message'];
    final issues = error['issues'];
    if (issues is List && issues.isNotEmpty) {
      return '$message ${issues.join(' ')}'.trim();
    }
    if (message is String && message.isNotEmpty) {
      return message;
    }
  }

  return error.toString();
}

List<ExecutionTestCaseResult> _extractTaskTestResults(Object? error) {
  if (error is Map<String, dynamic>) {
    final tests = error['test_results'];
    if (tests is List) {
      return tests
          .whereType<Map<String, dynamic>>()
          .map(ExecutionTestCaseResult.fromJson)
          .toList(growable: false);
    }
  }

  return const [];
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
