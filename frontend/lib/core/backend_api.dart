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
      throw BackendApiException('Backend returned an unknown task status.');
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

class ExecutionResult {
  final String message;
  final String lessonTitle;
  final String videoPath;
  final bool visualizationReady;
  final ExecutionMetrics metrics;
  final List<ExecutionTestCaseResult> testResults;

  const ExecutionResult({
    required this.message,
    required this.lessonTitle,
    required this.videoPath,
    required this.visualizationReady,
    required this.metrics,
    required this.testResults,
  });

  factory ExecutionResult.fromJson(Map<String, dynamic> json) {
    final lesson = (json['lesson'] as Map<String, dynamic>?) ?? const {};
    final metrics = (json['metrics'] as Map<String, dynamic>?) ?? const {};
    final testResults = (json['test_results'] as List<dynamic>? ?? const [])
        .whereType<Map<String, dynamic>>()
        .map(ExecutionTestCaseResult.fromJson)
        .toList(growable: false);

    return ExecutionResult(
      message: json['message'] as String? ?? 'Execution completed.',
      lessonTitle: lesson['title'] as String? ?? '',
      videoPath: json['video_path'] as String? ?? '',
      visualizationReady: json['visualization_ready'] as bool? ?? false,
      metrics: ExecutionMetrics.fromJson(metrics),
      testResults: testResults,
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

abstract class BackendApi {
  Future<SubmittedExecutionTask> submitCode({
    required String lessonId,
    required String code,
    required double learningRate,
    required double discountFactor,
    required double explorationRate,
    required int episodeCount,
  });

  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId);

  Future<ExecutionResult> executeCode({
    required String lessonId,
    required String code,
    required double learningRate,
    required double discountFactor,
    required double explorationRate,
    required int episodeCount,
  }) async {
    final task = await submitCode(
      lessonId: lessonId,
      code: code,
      learningRate: learningRate,
      discountFactor: discountFactor,
      explorationRate: explorationRate,
      episodeCount: episodeCount,
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
        );
      }

      await Future<void>.delayed(const Duration(milliseconds: 500));
    }
  }
}

class HttpBackendApi extends BackendApi {
  final http.Client _client;
  final String baseUrl;

  HttpBackendApi({
    http.Client? client,
    this.baseUrl = defaultBackendBaseUrl,
  }) : _client = client ?? http.Client();

  @override
  Future<SubmittedExecutionTask> submitCode({
    required String lessonId,
    required String code,
    required double learningRate,
    required double discountFactor,
    required double explorationRate,
    required int episodeCount,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/submit'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({
        'lesson_id': lessonId,
        'code': code,
        'learning_rate': learningRate,
        'discount_factor': discountFactor,
        'exploration_rate': explorationRate,
        'episode_count': episodeCount,
      }),
    );

    final responseJson = _decodeBody(response.body);
    if (response.statusCode >= 400) {
      throw _buildBackendException(responseJson);
    }

    return SubmittedExecutionTask.fromJson(responseJson);
  }

  @override
  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId) async {
    final response = await _client.get(Uri.parse('$baseUrl/tasks/$taskId'));
    final responseJson = _decodeBody(response.body);
    if (response.statusCode >= 400) {
      throw _buildBackendException(responseJson);
    }

    return ExecutionTaskSnapshot.fromJson(responseJson);
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

  String _extractErrorMessage(Map<String, dynamic> responseJson) {
    return _extractApiErrorMessage(responseJson);
  }
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
    Map<String, dynamic> response) {
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
