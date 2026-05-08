import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:multicast_dns/multicast_dns.dart';

import 'package:shared_preferences/shared_preferences.dart';

import 'constants.dart';
import 'lesson_models.dart';

class BackendConnectionManager extends ChangeNotifier {
  static final BackendConnectionManager _instance =
      BackendConnectionManager._internal();
  factory BackendConnectionManager() => _instance;
  BackendConnectionManager._internal();

  String _baseUrl = defaultBackendBaseUrl;
  WorkspaceConnectionStatus _status = WorkspaceConnectionStatus.disconnected;
  String? _lastError;
  Timer? _healthTimer;
  MDnsClient? _mDnsClient;

  String get baseUrl => _baseUrl;
  WorkspaceConnectionStatus get status => _status;
  String? get lastError => _lastError;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    final savedUrl = prefs.getString(AppConstants.backendUrlPreferenceKey);
    if (savedUrl != null && savedUrl.isNotEmpty) {
      _baseUrl = savedUrl;
    }
    notifyListeners();
    unawaited(checkHealth());
    _healthTimer = Timer.periodic(
      AppConstants.backendHealthInterval,
      (_) => checkHealth(),
    );
    unawaited(_autoDiscover());
  }

  Future<void> _autoDiscover() async {
    try {
      _mDnsClient = MDnsClient();
      await _mDnsClient!.start();
      await for (final PtrResourceRecord ptr in _mDnsClient!
          .lookup<PtrResourceRecord>(
              ResourceRecordQuery.serverPointer('_rl-ide._tcp.local'))) {
        await for (final SrvResourceRecord srv in _mDnsClient!
            .lookup<SrvResourceRecord>(
                ResourceRecordQuery.service(ptr.domainName))) {
          await for (final IPAddressResourceRecord ip in _mDnsClient!
              .lookup<IPAddressResourceRecord>(
                  ResourceRecordQuery.addressIPv4(srv.target))) {
            final discoveredUrl = 'http://${ip.address.address}:${srv.port}';
            if (discoveredUrl != _baseUrl) {
              await updateUrl(discoveredUrl);
            }
            break;
          }
        }
      }
    } catch (e) {
      debugPrint('mDNS discovery failed: $e');
    } finally {
      _mDnsClient?.stop();
    }
  }

  Future<void> updateUrl(String newUrl) async {
    final sanitized = _normalizeBackendUrl(newUrl);
    _baseUrl = sanitized;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.backendUrlPreferenceKey, sanitized);
    notifyListeners();
    await checkHealth();
  }

  Future<void> checkHealth() async {
    try {
      final response = await http.get(Uri.parse('$_baseUrl/')).timeout(
            AppConstants.backendHealthTimeout,
          );
      if (response.statusCode == 200) {
        _status = WorkspaceConnectionStatus.ready;
        _lastError = null;
      } else {
        _status = WorkspaceConnectionStatus.failed;
        _lastError = 'Server returned ${response.statusCode}';
      }
    } catch (e) {
      _status = WorkspaceConnectionStatus.failed;
      _lastError = e.toString();
    }
    notifyListeners();
  }

  @override
  void dispose() {
    _healthTimer?.cancel();
    _mDnsClient?.stop();
    super.dispose();
  }
}

const String defaultBackendBaseUrl = String.fromEnvironment(
  'BACKEND_BASE_URL',
  defaultValue: AppConstants.defaultBackendLocalUrl,
);

String _normalizeBackendUrl(String rawUrl) {
  var sanitized = rawUrl.trim();
  if (!sanitized.startsWith('http')) {
    sanitized = 'http://$sanitized';
  }
  if (sanitized.endsWith('/')) {
    sanitized = sanitized.substring(0, sanitized.length - 1);
  }
  return sanitized;
}

class BackendApiException implements Exception {
  final String message;
  final List<ExecutionTestCaseResult> testResults;
  final String? failureKind;
  final List<String> unresolvedBlanks;
  final ExecutionStudentFeedback? studentFeedback;

  const BackendApiException(
    this.message, {
    this.testResults = const [],
    this.failureKind,
    this.unresolvedBlanks = const [],
    this.studentFeedback,
  });

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

enum WorkspaceConnectionStatus { disconnected, connecting, ready, failed }

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
  final int totalSubmissionAttempts;
  final int passedSubmissionAttempts;
  final int validationFailures;
  final int runtimeFailures;
  final int testFailures;

  const LearnerProgress({
    required this.completedLessonIds,
    required this.successfulRuns,
    required this.latestLessonId,
    required this.pretestScore,
    required this.posttestScore,
    required this.nGain,
    required this.quizAttempts,
    this.totalSubmissionAttempts = 0,
    this.passedSubmissionAttempts = 0,
    this.validationFailures = 0,
    this.runtimeFailures = 0,
    this.testFailures = 0,
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
        },
        totalSubmissionAttempts = 0,
        passedSubmissionAttempts = 0,
        validationFailures = 0,
        runtimeFailures = 0,
        testFailures = 0;

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
      totalSubmissionAttempts:
          (json['total_submission_attempts'] as num?)?.toInt() ?? 0,
      passedSubmissionAttempts:
          (json['passed_submission_attempts'] as num?)?.toInt() ?? 0,
      validationFailures: (json['validation_failures'] as num?)?.toInt() ?? 0,
      runtimeFailures: (json['runtime_failures'] as num?)?.toInt() ?? 0,
      testFailures: (json['test_failures'] as num?)?.toInt() ?? 0,
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

class ExecutionStudentFeedback {
  final String status;
  final String summary;
  final String likelyIssue;
  final List<String> affectedBlankIds;
  final List<String> nextSteps;
  final String hintLevel;

  const ExecutionStudentFeedback({
    required this.status,
    required this.summary,
    required this.likelyIssue,
    required this.affectedBlankIds,
    required this.nextSteps,
    required this.hintLevel,
  });

  factory ExecutionStudentFeedback.fromJson(Map<String, dynamic> json) {
    return ExecutionStudentFeedback(
      status: json['status'] as String? ?? 'validation_error',
      summary: json['summary'] as String? ?? '',
      likelyIssue: json['likely_issue'] as String? ?? '',
      affectedBlankIds:
          (json['affected_blank_ids'] as List<dynamic>? ?? const [])
              .map((value) => value.toString())
              .toList(growable: false),
      nextSteps: (json['next_steps'] as List<dynamic>? ?? const [])
          .map((value) => value.toString())
          .toList(growable: false),
      hintLevel: json['hint_level'] as String? ?? 'light',
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

class WorkspaceSessionData {
  final String sessionId;
  final String lessonId;
  final List<String> visibleFiles;
  final bool consoleReady;

  const WorkspaceSessionData({
    required this.sessionId,
    required this.lessonId,
    required this.visibleFiles,
    required this.consoleReady,
  });

  factory WorkspaceSessionData.fromJson(Map<String, dynamic> json) {
    return WorkspaceSessionData(
      sessionId: json['session_id'] as String? ?? '',
      lessonId: json['lesson_id'] as String? ?? '',
      visibleFiles: (json['visible_files'] as List<dynamic>? ?? const [])
          .map((value) => value.toString())
          .toList(growable: false),
      consoleReady: json['console_ready'] as bool? ?? false,
    );
  }
}

class WorkspaceFileSnapshot {
  final String path;
  final String content;
  final int version;
  final List<WorkspaceDiagnostic> diagnostics;

  const WorkspaceFileSnapshot({
    required this.path,
    required this.content,
    required this.version,
    required this.diagnostics,
  });

  factory WorkspaceFileSnapshot.fromJson(Map<String, dynamic> json) {
    return WorkspaceFileSnapshot(
      path: json['path'] as String? ?? 'script.py',
      content: json['content'] as String? ?? '',
      version: (json['version'] as num?)?.toInt() ?? 1,
      diagnostics: (json['diagnostics'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(WorkspaceDiagnostic.fromJson)
          .toList(growable: false),
    );
  }
}

class WorkspaceDiagnostic {
  final String message;
  final int line;
  final int column;
  final String severity;

  const WorkspaceDiagnostic({
    required this.message,
    required this.line,
    required this.column,
    required this.severity,
  });

  factory WorkspaceDiagnostic.fromJson(Map<String, dynamic> json) {
    return WorkspaceDiagnostic(
      message: json['message'] as String? ?? 'Unknown workspace diagnostic.',
      line: (json['line'] as num?)?.toInt() ?? 1,
      column: (json['column'] as num?)?.toInt() ?? 1,
      severity: json['severity'] as String? ?? 'error',
    );
  }
}

class WorkspaceRunData {
  final String runId;
  final String status;
  final int? exitCode;
  final String? startedAt;
  final String? finishedAt;

  const WorkspaceRunData({
    required this.runId,
    required this.status,
    required this.exitCode,
    required this.startedAt,
    required this.finishedAt,
  });

  bool get isTerminal => status == 'completed' || status == 'failed';

  factory WorkspaceRunData.fromJson(Map<String, dynamic> json) {
    return WorkspaceRunData(
      runId: json['run_id'] as String? ?? '',
      status: json['status'] as String? ?? 'running',
      exitCode: (json['exit_code'] as num?)?.toInt(),
      startedAt: json['started_at'] as String?,
      finishedAt: json['finished_at'] as String?,
    );
  }
}

class WorkspaceHealthData {
  final bool ready;
  final bool workerReachable;
  final bool dockerCliAvailable;
  final bool dockerDaemonReachable;
  final String runtimeMode;
  final String message;
  final List<String> issues;

  const WorkspaceHealthData({
    required this.ready,
    required this.workerReachable,
    required this.dockerCliAvailable,
    required this.dockerDaemonReachable,
    required this.runtimeMode,
    required this.message,
    required this.issues,
  });

  factory WorkspaceHealthData.fromJson(Map<String, dynamic> json) {
    return WorkspaceHealthData(
      ready: json['ready'] as bool? ?? false,
      workerReachable: json['worker_reachable'] as bool? ?? false,
      dockerCliAvailable: json['docker_cli_available'] as bool? ?? false,
      dockerDaemonReachable: json['docker_daemon_reachable'] as bool? ?? false,
      runtimeMode: json['runtime_mode'] as String? ?? 'docker',
      message: json['message'] as String? ?? 'Workspace runtime unavailable.',
      issues: (json['issues'] as List<dynamic>? ?? const [])
          .map((issue) => issue.toString())
          .toList(growable: false),
    );
  }
}

class ExecutionTaskSnapshot {
  final String taskId;
  final ExecutionTaskStatus status;
  final ExecutionResult? result;
  final String? errorMessage;
  final List<ExecutionTestCaseResult> testResults;
  final String? failureKind;
  final List<String> unresolvedBlanks;
  final ExecutionStudentFeedback? studentFeedback;

  const ExecutionTaskSnapshot({
    required this.taskId,
    required this.status,
    this.result,
    this.errorMessage,
    this.testResults = const [],
    this.failureKind,
    this.unresolvedBlanks = const [],
    this.studentFeedback,
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
      failureKind: _extractTaskFailureKind(json['error']),
      unresolvedBlanks: _extractTaskUnresolvedBlanks(json['error']),
      studentFeedback: _extractTaskStudentFeedback(json['error']),
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
  Future<List<LessonSection>> fetchLessonSections();

  Future<LearnerDashboard> signIn({
    required String displayName,
    required String password,
    String? firebaseIdToken,
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

  String workspaceEditorShellUrl(String sessionId);

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

class HttpBackendApi extends BackendApi {
  final http.Client _client;
  String get baseUrl => BackendConnectionManager().baseUrl;
  static const Map<String, String> _jsonHeaders = {
    'Content-Type': 'application/json',
  };

  HttpBackendApi({
    http.Client? client,
  }) : _client = client ?? http.Client();

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

    throw const BackendApiException(
      'Backend returned an invalid lesson catalog.',
    );
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
  String workspaceEditorShellUrl(String sessionId) {
    final encodedSession = Uri.encodeComponent(sessionId);
    return '$baseUrl/workspace/editor-shell?session_id=$encodedSession';
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

  Future<Map<String, dynamic>> _putJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    final uri = Uri.parse('$baseUrl$path');
    final response = await _client.put(
      uri,
      headers: _jsonHeaders,
      body: jsonEncode(body),
    );
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

String? _extractTaskFailureKind(Object? error) {
  if (error is Map<String, dynamic>) {
    return error['failure_kind'] as String?;
  }
  return null;
}

List<String> _extractTaskUnresolvedBlanks(Object? error) {
  if (error is Map<String, dynamic>) {
    return (error['unresolved_blanks'] as List<dynamic>? ?? const [])
        .map((value) => value.toString())
        .toList(growable: false);
  }
  return const [];
}

ExecutionStudentFeedback? _extractTaskStudentFeedback(Object? error) {
  if (error is Map<String, dynamic>) {
    final feedback = error['student_feedback'];
    if (feedback is Map<String, dynamic>) {
      return ExecutionStudentFeedback.fromJson(feedback);
    }
  }
  return null;
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
