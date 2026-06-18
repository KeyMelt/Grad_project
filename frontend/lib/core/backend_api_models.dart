import 'replay_contract.dart';

class AuthSessionStore {
  static String? accessToken;
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

QuizPhase _parseQuizPhaseCompat(String? value) {
  if (value == 'posttest') {
    return QuizPhase.posttest;
  }
  return QuizPhase.pretest;
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
        'Unknown task status.',
      );
  }
}

class LearnerProfile {
  final String id;
  final String displayName;
  final String platformRole;
  final String? rlExperience;

  const LearnerProfile({
    required this.id,
    required this.displayName,
    required this.platformRole,
    this.rlExperience,
  });

  factory LearnerProfile.fromJson(Map<String, dynamic> json) {
    return LearnerProfile(
      id: json['id'] as String? ?? '',
      displayName: json['display_name'] as String? ?? 'Student',
      platformRole: (json['role'] as String? ?? 'student').toLowerCase(),
      rlExperience: json['rl_experience'] as String?,
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
  final Map<String, FamilyQuizScore> familyQuizScores;
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
    this.familyQuizScores = const {},
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
        familyQuizScores = const {},
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
    final rawFamilyScores =
        (json['family_quiz_scores'] as Map<String, dynamic>?) ?? const {};
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
      familyQuizScores: rawFamilyScores.map(
        (key, value) => MapEntry(
          key,
          FamilyQuizScore.fromJson(
            (value as Map<String, dynamic>?) ?? const {},
          ),
        ),
      ),
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

class FamilyQuizScore {
  final double? pretestScore;
  final double? posttestScore;
  final double? nGain;
  final Map<String, int> attempts;

  const FamilyQuizScore({
    this.pretestScore,
    this.posttestScore,
    this.nGain,
    this.attempts = const {},
  });

  factory FamilyQuizScore.fromJson(Map<String, dynamic> json) {
    final rawAttempts = (json['attempts'] as Map<String, dynamic>?) ?? const {};
    return FamilyQuizScore(
      pretestScore: (json['pretest_score'] as num?)?.toDouble(),
      posttestScore: (json['posttest_score'] as num?)?.toDouble(),
      nGain: (json['n_gain'] as num?)?.toDouble(),
      attempts: rawAttempts.map(
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

class StaffStudentSummary {
  final String id;
  final String displayName;
  final String role;
  final String status;

  const StaffStudentSummary({
    required this.id,
    required this.displayName,
    required this.role,
    required this.status,
  });

  factory StaffStudentSummary.fromJson(Map<String, dynamic> json) {
    return StaffStudentSummary(
      id: json['id'] as String? ?? '',
      displayName: json['display_name'] as String? ?? 'Student',
      role: (json['role'] as String? ?? 'student').toLowerCase(),
      status: (json['status'] as String? ?? 'active').toLowerCase(),
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
  final String phaseId;
  final String phaseLabel;
  final String familyId;
  final String familyLabel;
  final String stage;
  final int questionCount;
  final List<QuizQuestionData> questions;

  const QuizSessionData({
    required this.sessionId,
    required this.phase,
    this.phaseId = 'pretest',
    this.phaseLabel = 'Pre-test',
    this.familyId = '',
    this.familyLabel = '',
    this.stage = '',
    required this.questionCount,
    required this.questions,
  });

  factory QuizSessionData.fromJson(Map<String, dynamic> json) {
    final rawPhase = json['phase'] as String? ?? 'pretest';
    return QuizSessionData(
      sessionId: json['session_id'] as String? ?? '',
      phase: _parseQuizPhaseCompat(rawPhase),
      phaseId: rawPhase,
      phaseLabel: json['phase_label'] as String? ?? rawPhase,
      familyId: json['family_id'] as String? ?? '',
      familyLabel: json['family_label'] as String? ?? '',
      stage: json['stage'] as String? ?? '',
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
  final String phaseId;
  final String phaseLabel;
  final String familyId;
  final String familyLabel;
  final String stage;
  final int score;
  final int totalQuestions;
  final double percentage;
  final double? nGain;
  final LearnerProgress progress;

  const QuizAttemptSummary({
    required this.phase,
    this.phaseId = 'pretest',
    this.phaseLabel = 'Pre-test',
    this.familyId = '',
    this.familyLabel = '',
    this.stage = '',
    required this.score,
    required this.totalQuestions,
    required this.percentage,
    required this.nGain,
    required this.progress,
  });

  factory QuizAttemptSummary.fromJson(Map<String, dynamic> json) {
    final rawPhase = json['phase'] as String? ?? 'pretest';
    return QuizAttemptSummary(
      phase: _parseQuizPhaseCompat(rawPhase),
      phaseId: rawPhase,
      phaseLabel: json['phase_label'] as String? ?? rawPhase,
      familyId: json['family_id'] as String? ?? '',
      familyLabel: json['family_label'] as String? ?? '',
      stage: json['stage'] as String? ?? '',
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

class QuizCatalogPhaseData {
  final String id;
  final String label;
  final String description;
  final int questionCount;
  final List<String> concepts;
  final String familyId;
  final String familyLabel;
  final String stage;
  final List<String> lessonIds;
  final bool requiresSuccessfulRun;
  final bool requiresLessonCompletion;
  final bool triggersPostStudySurvey;
  final bool showsNGain;

  const QuizCatalogPhaseData({
    required this.id,
    required this.label,
    required this.description,
    required this.questionCount,
    this.concepts = const [],
    this.familyId = '',
    this.familyLabel = '',
    this.stage = '',
    this.lessonIds = const [],
    this.requiresSuccessfulRun = false,
    this.requiresLessonCompletion = false,
    this.triggersPostStudySurvey = false,
    this.showsNGain = false,
  });

  factory QuizCatalogPhaseData.fromJson(Map<String, dynamic> json) {
    return QuizCatalogPhaseData(
      id: json['id'] as String? ?? '',
      label: json['label'] as String? ?? '',
      description: json['description'] as String? ?? '',
      questionCount: (json['question_count'] as num?)?.toInt() ?? 0,
      concepts: (json['concepts'] as List<dynamic>? ?? const [])
          .map((value) => value.toString())
          .toList(growable: false),
      familyId: json['family_id'] as String? ?? '',
      familyLabel: json['family_label'] as String? ?? '',
      stage: json['stage'] as String? ?? '',
      lessonIds: (json['lesson_ids'] as List<dynamic>? ?? const [])
          .map((value) => value.toString())
          .toList(growable: false),
      requiresSuccessfulRun: json['requires_successful_run'] as bool? ?? false,
      requiresLessonCompletion:
          json['requires_lesson_completion'] as bool? ?? false,
      triggersPostStudySurvey:
          json['triggers_post_study_survey'] as bool? ?? false,
      showsNGain: json['shows_n_gain'] as bool? ?? false,
    );
  }
}

class QuizFamilyData {
  final String id;
  final String label;
  final String description;
  final List<String> lessonIds;
  final QuizCatalogPhaseData pretest;
  final QuizCatalogPhaseData posttest;

  const QuizFamilyData({
    required this.id,
    required this.label,
    required this.description,
    required this.lessonIds,
    required this.pretest,
    required this.posttest,
  });

  factory QuizFamilyData.fromJson(Map<String, dynamic> json) {
    final id = json['id'] as String? ?? '';
    final lessonIds = (json['lesson_ids'] as List<dynamic>? ?? const [])
        .map((value) => value.toString())
        .toList(growable: false);
    final pretestJson = (json['pretest'] as Map<String, dynamic>?) ?? const {};
    final posttestJson =
        (json['posttest'] as Map<String, dynamic>?) ?? const {};
    return QuizFamilyData(
      id: id,
      label: json['label'] as String? ?? id,
      description: json['description'] as String? ?? '',
      lessonIds: lessonIds,
      pretest: QuizCatalogPhaseData.fromJson({
        'family_id': id,
        'family_label': json['label'] as String? ?? id,
        'stage': 'pre',
        'lesson_ids': lessonIds,
        ...pretestJson,
      }),
      posttest: QuizCatalogPhaseData.fromJson({
        'family_id': id,
        'family_label': json['label'] as String? ?? id,
        'stage': 'post',
        'lesson_ids': lessonIds,
        'requires_lesson_completion': true,
        ...posttestJson,
      }),
    );
  }
}

class QuizCatalogData {
  final String categorySectionLabel;
  final String categorySectionDescription;
  final List<QuizCatalogPhaseData> assessmentPhases;
  final List<QuizCatalogPhaseData> categoryQuizzes;
  final List<QuizFamilyData> quizFamilies;

  const QuizCatalogData({
    this.categorySectionLabel = '',
    this.categorySectionDescription = '',
    required this.assessmentPhases,
    required this.categoryQuizzes,
    this.quizFamilies = const [],
  });

  const QuizCatalogData.empty()
      : categorySectionLabel = '',
        categorySectionDescription = '',
        assessmentPhases = const [],
        categoryQuizzes = const [],
        quizFamilies = const [];

  factory QuizCatalogData.fromJson(Map<String, dynamic> json) {
    return QuizCatalogData(
      categorySectionLabel: json['category_section_label'] as String? ?? '',
      categorySectionDescription:
          json['category_section_description'] as String? ?? '',
      assessmentPhases:
          (json['assessment_phases'] as List<dynamic>? ?? const [])
              .whereType<Map<String, dynamic>>()
              .map(QuizCatalogPhaseData.fromJson)
              .toList(growable: false),
      categoryQuizzes: (json['category_quizzes'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(QuizCatalogPhaseData.fromJson)
          .toList(growable: false),
      quizFamilies: (json['quiz_families'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(QuizFamilyData.fromJson)
          .toList(growable: false),
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
  final int traceSchemaVersion;
  final TraceEquationUpdate? equationUpdate;
  final TraceTableSnapshot? tableSnapshot;
  final TraceGridMetadata? gridMetadata;
  final TraceStepExplanation? explanation;

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
    this.traceSchemaVersion = 1,
    this.equationUpdate,
    this.tableSnapshot,
    this.gridMetadata,
    this.explanation,
  });

  factory ExecutionTraceStep.fromJson(Map<String, dynamic> json) {
    final rawUpdatedValues =
        (json['updated_values'] as Map<String, dynamic>?) ?? const {};
    final rawEquationUpdate = json['equation_update'];
    final rawTableSnapshot = json['tables'];
    final rawGridMetadata = json['grid_metadata'];
    final rawExplanation = json['explanation'];
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
      updatedValues: {
        for (final entry in rawUpdatedValues.entries)
          if (_jsonDouble(entry.value) != null)
            entry.key: _jsonDouble(entry.value)!,
      },
      traceSchemaVersion: (json['trace_schema_version'] as num?)?.toInt() ?? 1,
      equationUpdate: rawEquationUpdate is Map<String, dynamic>
          ? TraceEquationUpdate.fromJson(rawEquationUpdate)
          : null,
      tableSnapshot: rawTableSnapshot is Map<String, dynamic>
          ? TraceTableSnapshot.fromJson(rawTableSnapshot)
          : null,
      gridMetadata: rawGridMetadata is Map<String, dynamic>
          ? TraceGridMetadata.fromJson(rawGridMetadata)
          : null,
      explanation: rawExplanation is Map<String, dynamic>
          ? TraceStepExplanation.fromJson(rawExplanation)
          : null,
    );
  }
}

class TraceStepExplanation {
  final String summary;
  final String whyCorrect;
  final String codeFocus;
  final String tableFocus;

  const TraceStepExplanation({
    required this.summary,
    required this.whyCorrect,
    required this.codeFocus,
    required this.tableFocus,
  });

  factory TraceStepExplanation.fromJson(Map<String, dynamic> json) {
    return TraceStepExplanation(
      summary: json['summary'] as String? ?? '',
      whyCorrect: json['why_correct'] as String? ?? '',
      codeFocus: json['code_focus'] as String? ?? '',
      tableFocus: json['table_focus'] as String? ?? '',
    );
  }
}

class TraceGridMetadata {
  final String environment;
  final int rows;
  final int columns;
  final List<TraceGridCell> cells;
  final int state;
  final int? nextState;
  final TraceGridCoordinate? stateCoordinates;
  final TraceGridCoordinate? nextStateCoordinates;
  final int? action;
  final String actionLabel;
  final double? reward;
  final bool terminated;
  final bool truncated;
  final int? encodedState;
  final int? encodedNextState;
  final TaxiPassenger? passenger;
  final TaxiPassenger? nextPassenger;
  final TaxiDestination? destination;
  final List<TraceGridWall> walls;

  const TraceGridMetadata({
    required this.environment,
    required this.rows,
    required this.columns,
    required this.cells,
    required this.state,
    required this.nextState,
    required this.stateCoordinates,
    required this.nextStateCoordinates,
    required this.action,
    required this.actionLabel,
    required this.reward,
    required this.terminated,
    required this.truncated,
    this.encodedState,
    this.encodedNextState,
    this.passenger,
    this.nextPassenger,
    this.destination,
    this.walls = const [],
  });

  bool get isTaxi => environment == 'Taxi';

  factory TraceGridMetadata.fromJson(Map<String, dynamic> json) {
    final rawCells = json['cells'] as List<dynamic>? ?? const [];
    final rawWalls = json['walls'] as List<dynamic>? ?? const [];
    return TraceGridMetadata(
      environment: json['environment'] as String? ?? '',
      rows: (json['rows'] as num?)?.toInt() ?? 0,
      columns: (json['columns'] as num?)?.toInt() ?? 0,
      cells: rawCells
          .whereType<Map<String, dynamic>>()
          .map(TraceGridCell.fromJson)
          .toList(growable: false),
      state: (json['state'] as num?)?.toInt() ?? 0,
      nextState: (json['next_state'] as num?)?.toInt(),
      stateCoordinates:
          TraceGridCoordinate.fromNullableJson(json['state_coordinates']),
      nextStateCoordinates:
          TraceGridCoordinate.fromNullableJson(json['next_state_coordinates']),
      action: (json['action'] as num?)?.toInt(),
      actionLabel: json['action_label'] as String? ?? '',
      reward: _jsonDouble(json['reward']),
      terminated: json['terminated'] as bool? ?? false,
      truncated: json['truncated'] as bool? ?? false,
      encodedState: (json['encoded_state'] as num?)?.toInt(),
      encodedNextState: (json['encoded_next_state'] as num?)?.toInt(),
      passenger: TaxiPassenger.fromNullableJson(json['passenger']),
      nextPassenger: TaxiPassenger.fromNullableJson(json['next_passenger']),
      destination: TaxiDestination.fromNullableJson(json['destination']),
      walls: rawWalls
          .whereType<Map<String, dynamic>>()
          .map(TraceGridWall.fromJson)
          .toList(growable: false),
    );
  }

  TraceGridCell? cellAtState(int state) {
    for (final cell in cells) {
      if (cell.state == state) {
        return cell;
      }
    }
    return null;
  }
}

class TraceGridCell {
  final int state;
  final int row;
  final int column;
  final String tileType;
  final bool terminal;

  const TraceGridCell({
    required this.state,
    required this.row,
    required this.column,
    required this.tileType,
    required this.terminal,
  });

  factory TraceGridCell.fromJson(Map<String, dynamic> json) {
    return TraceGridCell(
      state: (json['state'] as num?)?.toInt() ?? 0,
      row: (json['row'] as num?)?.toInt() ?? 0,
      column: (json['column'] as num?)?.toInt() ?? 0,
      tileType: json['tile_type'] as String? ?? '',
      terminal: json['terminal'] as bool? ?? false,
    );
  }
}

class TaxiPassenger {
  final String location;
  final int row;
  final int column;
  final bool inTaxi;

  const TaxiPassenger({
    required this.location,
    required this.row,
    required this.column,
    required this.inTaxi,
  });

  static TaxiPassenger? fromNullableJson(Object? json) {
    if (json is! Map<String, dynamic>) {
      return null;
    }
    return TaxiPassenger(
      location: json['location'] as String? ?? '',
      row: (json['row'] as num?)?.toInt() ?? 0,
      column: (json['column'] as num?)?.toInt() ?? 0,
      inTaxi: json['in_taxi'] as bool? ?? false,
    );
  }
}

class TaxiDestination {
  final String label;
  final int row;
  final int column;

  const TaxiDestination({
    required this.label,
    required this.row,
    required this.column,
  });

  static TaxiDestination? fromNullableJson(Object? json) {
    if (json is! Map<String, dynamic>) {
      return null;
    }
    return TaxiDestination(
      label: json['label'] as String? ?? '',
      row: (json['row'] as num?)?.toInt() ?? 0,
      column: (json['column'] as num?)?.toInt() ?? 0,
    );
  }
}

class TraceGridWall {
  final TraceGridCoordinate start;
  final TraceGridCoordinate end;

  const TraceGridWall({
    required this.start,
    required this.end,
  });

  factory TraceGridWall.fromJson(Map<String, dynamic> json) {
    return TraceGridWall(
      start: TraceGridCoordinate.fromNullableJson(json['start']) ??
          const TraceGridCoordinate(row: 0, column: 0),
      end: TraceGridCoordinate.fromNullableJson(json['end']) ??
          const TraceGridCoordinate(row: 0, column: 0),
    );
  }
}

class TraceGridCoordinate {
  final int row;
  final int column;

  const TraceGridCoordinate({
    required this.row,
    required this.column,
  });

  static TraceGridCoordinate? fromNullableJson(Object? json) {
    if (json is! Map<String, dynamic>) {
      return null;
    }
    final row = (json['row'] as num?)?.toInt();
    final column = (json['column'] as num?)?.toInt();
    if (row == null || column == null) {
      return null;
    }
    return TraceGridCoordinate(row: row, column: column);
  }
}

class TraceEquationUpdate {
  final String kind;
  final String lhs;
  final Object? oldValue;
  final double? reward;
  final double? gamma;
  final double? alpha;
  final String bootstrapLabel;
  final double? bootstrapValue;
  final double? tdTarget;
  final double? tdError;
  final Object? newValue;
  final String substitution;
  final String codeFocus;
  final TraceDpDetails? dpDetails;
  final TraceMcDetails? mcDetails;

  const TraceEquationUpdate({
    required this.kind,
    required this.lhs,
    required this.oldValue,
    required this.reward,
    required this.gamma,
    required this.alpha,
    required this.bootstrapLabel,
    required this.bootstrapValue,
    required this.tdTarget,
    required this.tdError,
    required this.newValue,
    required this.substitution,
    required this.codeFocus,
    required this.dpDetails,
    required this.mcDetails,
  });

  bool get isTemporalDifference =>
      kind == 'sarsa' || kind == 'q_learning' || kind == 'td_prediction';

  bool get isDynamicProgramming =>
      kind == 'policy_evaluation' ||
      kind == 'value_iteration' ||
      kind == 'policy_improvement';

  bool get isMonteCarlo => kind == 'mc_sampling' || kind == 'mc_first_visit';

  factory TraceEquationUpdate.fromJson(Map<String, dynamic> json) {
    final rawDpDetails = json['dp_details'];
    final rawMcDetails = json['mc_details'];
    return TraceEquationUpdate(
      kind: json['kind'] as String? ?? '',
      lhs: json['lhs'] as String? ?? '',
      oldValue: _jsonScalar(json['old_value']),
      reward: _jsonDouble(json['reward']),
      gamma: _jsonDouble(json['gamma']),
      alpha: _jsonDouble(json['alpha']),
      bootstrapLabel: json['bootstrap_label'] as String? ?? '',
      bootstrapValue: _jsonDouble(json['bootstrap_value']),
      tdTarget: _jsonDouble(json['td_target']),
      tdError: _jsonDouble(json['td_error']),
      newValue: _jsonScalar(json['new_value']),
      substitution: json['substitution'] as String? ?? '',
      codeFocus: json['code_focus'] as String? ?? '',
      dpDetails: rawDpDetails is Map<String, dynamic>
          ? TraceDpDetails.fromJson(rawDpDetails)
          : null,
      mcDetails: rawMcDetails is Map<String, dynamic>
          ? TraceMcDetails.fromJson(rawMcDetails)
          : null,
    );
  }
}

class TraceMcDetails {
  final int episodeIndex;
  final int episodeStep;
  final String phase;
  final BlackjackObservation? observation;
  final BlackjackObservation? nextObservation;
  final int? action;
  final String actionLabel;
  final double? reward;
  final bool terminated;
  final bool truncated;
  final bool firstVisit;
  final double? returnValue;
  final List<TraceMcReturnTerm> returnTerms;
  final List<double> returnsHistory;
  final List<TraceMcEpisodeStep> episodeStrip;

  const TraceMcDetails({
    required this.episodeIndex,
    required this.episodeStep,
    required this.phase,
    required this.observation,
    required this.nextObservation,
    required this.action,
    required this.actionLabel,
    required this.reward,
    required this.terminated,
    required this.truncated,
    required this.firstVisit,
    required this.returnValue,
    required this.returnTerms,
    required this.returnsHistory,
    required this.episodeStrip,
  });

  factory TraceMcDetails.fromJson(Map<String, dynamic> json) {
    final rawReturnTerms = json['return_terms'] as List<dynamic>? ?? const [];
    final rawEpisodeStrip = json['episode_strip'] as List<dynamic>? ?? const [];
    return TraceMcDetails(
      episodeIndex: (json['episode_index'] as num?)?.toInt() ?? 0,
      episodeStep: (json['episode_step'] as num?)?.toInt() ?? 0,
      phase: json['phase'] as String? ?? '',
      observation: BlackjackObservation.fromNullableJson(json['observation']),
      nextObservation:
          BlackjackObservation.fromNullableJson(json['next_observation']),
      action: (json['action'] as num?)?.toInt(),
      actionLabel: json['action_label'] as String? ?? '',
      reward: _jsonDouble(json['reward']),
      terminated: json['terminated'] as bool? ?? false,
      truncated: json['truncated'] as bool? ?? false,
      firstVisit: json['first_visit'] as bool? ?? false,
      returnValue: _jsonDouble(json['return_value']),
      returnTerms: rawReturnTerms
          .whereType<Map<String, dynamic>>()
          .map(TraceMcReturnTerm.fromJson)
          .toList(growable: false),
      returnsHistory: _jsonDoubleList(json['returns_history']),
      episodeStrip: rawEpisodeStrip
          .whereType<Map<String, dynamic>>()
          .map(TraceMcEpisodeStep.fromJson)
          .toList(growable: false),
    );
  }
}

class BlackjackObservation {
  final int? playerSum;
  final int? dealerCard;
  final bool? usableAce;
  final String raw;

  const BlackjackObservation({
    required this.playerSum,
    required this.dealerCard,
    required this.usableAce,
    required this.raw,
  });

  static BlackjackObservation? fromNullableJson(Object? json) {
    if (json is! Map<String, dynamic>) {
      return null;
    }
    return BlackjackObservation(
      playerSum: (json['player_sum'] as num?)?.toInt(),
      dealerCard: (json['dealer_card'] as num?)?.toInt(),
      usableAce: json['usable_ace'] as bool?,
      raw: json['raw'] as String? ?? '',
    );
  }

  String get label {
    if (playerSum == null || dealerCard == null || usableAce == null) {
      return raw.isEmpty ? 'Unknown observation' : raw;
    }
    return 'Player $playerSum | Dealer $dealerCard | Usable ace ${usableAce! ? 'yes' : 'no'}';
  }
}

class TraceMcEpisodeStep {
  final int stepIndex;
  final String state;
  final BlackjackObservation? observation;
  final int action;
  final String actionLabel;
  final double reward;
  final String nextState;
  final BlackjackObservation? nextObservation;
  final bool terminated;
  final bool truncated;

  const TraceMcEpisodeStep({
    required this.stepIndex,
    required this.state,
    required this.observation,
    required this.action,
    required this.actionLabel,
    required this.reward,
    required this.nextState,
    required this.nextObservation,
    required this.terminated,
    required this.truncated,
  });

  factory TraceMcEpisodeStep.fromJson(Map<String, dynamic> json) {
    return TraceMcEpisodeStep(
      stepIndex: (json['step_index'] as num?)?.toInt() ?? 0,
      state: json['state'] as String? ?? '',
      observation: BlackjackObservation.fromNullableJson(json['observation']),
      action: (json['action'] as num?)?.toInt() ?? 0,
      actionLabel: json['action_label'] as String? ?? '',
      reward: _jsonDouble(json['reward']) ?? 0.0,
      nextState: json['next_state'] as String? ?? '',
      nextObservation:
          BlackjackObservation.fromNullableJson(json['next_observation']),
      terminated: json['terminated'] as bool? ?? false,
      truncated: json['truncated'] as bool? ?? false,
    );
  }
}

class TraceMcReturnTerm {
  final int episodeStep;
  final double discount;
  final double reward;
  final double discountedReward;
  final double runningReturn;

  const TraceMcReturnTerm({
    required this.episodeStep,
    required this.discount,
    required this.reward,
    required this.discountedReward,
    required this.runningReturn,
  });

  factory TraceMcReturnTerm.fromJson(Map<String, dynamic> json) {
    return TraceMcReturnTerm(
      episodeStep: (json['episode_step'] as num?)?.toInt() ?? 0,
      discount: _jsonDouble(json['discount']) ?? 0.0,
      reward: _jsonDouble(json['reward']) ?? 0.0,
      discountedReward: _jsonDouble(json['discounted_reward']) ?? 0.0,
      runningReturn: _jsonDouble(json['running_return']) ?? 0.0,
    );
  }
}

class TraceDpDetails {
  final List<TraceDpActionBackup> actionBackups;
  final int? selectedAction;
  final String selectedActionLabel;
  final double? backupValue;
  final double? delta;
  final List<double> policyRowBefore;
  final List<double> policyRowAfter;
  final List<List<double>> valueSource;

  const TraceDpDetails({
    required this.actionBackups,
    required this.selectedAction,
    required this.selectedActionLabel,
    required this.backupValue,
    required this.delta,
    required this.policyRowBefore,
    required this.policyRowAfter,
    required this.valueSource,
  });

  factory TraceDpDetails.fromJson(Map<String, dynamic> json) {
    final rawBackups = json['action_backups'] as List<dynamic>? ?? const [];
    return TraceDpDetails(
      actionBackups: rawBackups
          .whereType<Map<String, dynamic>>()
          .map(TraceDpActionBackup.fromJson)
          .toList(growable: false),
      selectedAction: (json['selected_action'] as num?)?.toInt(),
      selectedActionLabel: json['selected_action_label'] as String? ?? '',
      backupValue: _jsonDouble(json['backup_value']),
      delta: _jsonDouble(json['delta']),
      policyRowBefore: _jsonDoubleList(json['policy_row_before']),
      policyRowAfter: _jsonDoubleList(json['policy_row_after']),
      valueSource: _jsonDoubleMatrix(json['value_source']),
    );
  }
}

class TraceDpActionBackup {
  final int action;
  final String actionLabel;
  final double? policyProbability;
  final double expectedReturn;
  final double weightedContribution;
  final List<TraceDpTransitionTerm> transitionTerms;

  const TraceDpActionBackup({
    required this.action,
    required this.actionLabel,
    required this.policyProbability,
    required this.expectedReturn,
    required this.weightedContribution,
    required this.transitionTerms,
  });

  factory TraceDpActionBackup.fromJson(Map<String, dynamic> json) {
    final rawTerms = json['transition_terms'] as List<dynamic>? ?? const [];
    return TraceDpActionBackup(
      action: (json['action'] as num?)?.toInt() ?? 0,
      actionLabel: json['action_label'] as String? ?? '',
      policyProbability: _jsonDouble(json['policy_probability']),
      expectedReturn: _jsonDouble(json['expected_return']) ?? 0.0,
      weightedContribution: _jsonDouble(json['weighted_contribution']) ?? 0.0,
      transitionTerms: rawTerms
          .whereType<Map<String, dynamic>>()
          .map(TraceDpTransitionTerm.fromJson)
          .toList(growable: false),
    );
  }
}

class TraceDpTransitionTerm {
  final double probability;
  final int nextState;
  final double reward;
  final bool done;
  final double futureValue;
  final double contribution;

  const TraceDpTransitionTerm({
    required this.probability,
    required this.nextState,
    required this.reward,
    required this.done,
    required this.futureValue,
    required this.contribution,
  });

  factory TraceDpTransitionTerm.fromJson(Map<String, dynamic> json) {
    return TraceDpTransitionTerm(
      probability: _jsonDouble(json['probability']) ?? 0.0,
      nextState: (json['next_state'] as num?)?.toInt() ?? 0,
      reward: _jsonDouble(json['reward']) ?? 0.0,
      done: json['done'] as bool? ?? false,
      futureValue: _jsonDouble(json['future_value']) ?? 0.0,
      contribution: _jsonDouble(json['contribution']) ?? 0.0,
    );
  }
}

class TraceTableSnapshot {
  final String kind;
  final List<List<double>> before;
  final List<List<double>> after;
  final TraceTableCell? activeCell;
  final TraceTableCell? bootstrapCell;
  final List<TraceTableCell> changedCells;
  final List<String> actionLabels;

  const TraceTableSnapshot({
    required this.kind,
    required this.before,
    required this.after,
    required this.activeCell,
    required this.bootstrapCell,
    required this.changedCells,
    required this.actionLabels,
  });

  factory TraceTableSnapshot.fromJson(Map<String, dynamic> json) {
    final rawChangedCells = json['changed_cells'] as List<dynamic>? ?? const [];
    return TraceTableSnapshot(
      kind: json['kind'] as String? ?? '',
      before: _jsonDoubleMatrix(json['before']),
      after: _jsonDoubleMatrix(json['after']),
      activeCell: TraceTableCell.fromNullableJson(json['active_cell']),
      bootstrapCell: TraceTableCell.fromNullableJson(json['bootstrap_cell']),
      changedCells: rawChangedCells
          .map(TraceTableCell.fromNullableJson)
          .whereType<TraceTableCell>()
          .toList(growable: false),
      actionLabels: (json['action_labels'] as List<dynamic>? ?? const [])
          .map((label) => label.toString())
          .toList(growable: false),
    );
  }

  double? valueAfter(TraceTableCell? cell) => _matrixValue(after, cell);

  double? valueBefore(TraceTableCell? cell) => _matrixValue(before, cell);

  bool isChanged(int row, int column) {
    return changedCells.any((cell) => cell.row == row && cell.column == column);
  }

  bool isActive(int row, int column) {
    final cell = activeCell;
    return cell != null && cell.row == row && cell.column == column;
  }

  bool isBootstrap(int row, int column) {
    final cell = bootstrapCell;
    return cell != null && cell.row == row && cell.column == column;
  }
}

class TraceTableCell {
  final int row;
  final int column;

  const TraceTableCell({
    required this.row,
    required this.column,
  });

  static TraceTableCell? fromNullableJson(Object? json) {
    if (json is! Map<String, dynamic>) {
      return null;
    }
    final row = (json['row'] as num?)?.toInt();
    final column = (json['column'] as num?)?.toInt();
    if (row == null || column == null) {
      return null;
    }
    return TraceTableCell(row: row, column: column);
  }
}

Object? _jsonScalar(Object? value) {
  if (value == null || value is num || value is String || value is bool) {
    return value;
  }
  return value.toString();
}

double? _jsonDouble(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  if (value is String) {
    return double.tryParse(value);
  }
  return null;
}

List<List<double>> _jsonDoubleMatrix(Object? value) {
  if (value is! List<dynamic>) {
    return const [];
  }
  return value
      .whereType<List<dynamic>>()
      .map(
        (row) =>
            row.map(_jsonDouble).whereType<double>().toList(growable: false),
      )
      .toList(growable: false);
}

List<double> _jsonDoubleList(Object? value) {
  if (value is! List<dynamic>) {
    return const [];
  }
  return value.map(_jsonDouble).whereType<double>().toList(growable: false);
}

double? _matrixValue(List<List<double>> matrix, TraceTableCell? cell) {
  if (cell == null ||
      cell.row < 0 ||
      cell.column < 0 ||
      cell.row >= matrix.length ||
      cell.column >= matrix[cell.row].length) {
    return null;
  }
  return matrix[cell.row][cell.column];
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
  final List<ExecutionTraceEpisode> traceEpisodes;
  final List<ExecutionEpisodeSummary> episodeSummaries;
  final String traceMode;
  final String traceFamily;
  final Map<String, dynamic>? traceSummary;
  final Map<String, dynamic>? evaluationSummary;
  final String replayRenderJobId;
  final String replayRenderStatus;
  final List<int> replayEpisodeIndices;

  const ExecutionResult({
    required this.message,
    required this.lessonTitle,
    required this.videoPath,
    required this.visualizationReady,
    required this.metrics,
    required this.testResults,
    required this.stepTrace,
    this.traceEpisodes = const [],
    this.episodeSummaries = const [],
    this.traceMode = '',
    this.traceFamily = '',
    this.traceSummary,
    this.evaluationSummary,
    this.replayRenderJobId = '',
    this.replayRenderStatus = 'unavailable',
    this.replayEpisodeIndices = const [],
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
    final traceEpisodes = (json['trace_episodes'] as List<dynamic>? ?? const [])
        .whereType<Map<String, dynamic>>()
        .map(ExecutionTraceEpisode.fromJson)
        .toList(growable: false);
    final episodeSummaries =
        (json['episode_summaries'] as List<dynamic>? ?? const [])
            .whereType<Map<String, dynamic>>()
            .map(ExecutionEpisodeSummary.fromJson)
            .toList(growable: false);

    final videoPath = json['video_path'] as String? ?? '';
    return ExecutionResult(
      message: json['message'] as String? ?? 'Execution completed.',
      lessonTitle: lesson['title'] as String? ?? '',
      videoPath: videoPath,
      visualizationReady: json['visualization_ready'] as bool? ?? false,
      metrics: ExecutionMetrics.fromJson(metrics),
      testResults: testResults,
      stepTrace: stepTrace,
      traceEpisodes: traceEpisodes,
      episodeSummaries: episodeSummaries,
      traceMode: json['trace_mode'] as String? ?? '',
      traceFamily: json['trace_family'] as String? ?? '',
      traceSummary:
          (json['trace_summary'] as Map<String, dynamic>?) ?? const {},
      evaluationSummary: (json['evaluation_summary'] as Map<String, dynamic>?),
      replayRenderJobId: json['replay_render_job_id'] as String? ?? '',
      replayRenderStatus: ReplayStateSnapshot.resolve(
        rawStatus: (json['replay_state'] as String?) ??
            (json['replay_render_status'] as String? ?? 'unavailable'),
        videoPath: videoPath,
      ).statusId,
      replayEpisodeIndices:
          (json['replay_episode_indices'] as List<dynamic>? ?? const [])
              .map((value) => (value as num?)?.toInt())
              .whereType<int>()
              .toList(growable: false),
    );
  }
}

class ReplayRenderStatus {
  final String jobId;
  final String status;
  final String videoPath;
  final String? error;

  const ReplayRenderStatus({
    required this.jobId,
    required this.status,
    required this.videoPath,
    this.error,
  });

  bool get isComplete => status == 'ready' && videoPath.isNotEmpty;
  bool get isFailed => status == 'failed';

  factory ReplayRenderStatus.fromJson(Map<String, dynamic> json) {
    final videoPath =
        (json['video_path'] as String?) ?? (json['video_url'] as String? ?? '');
    final error = json['error'] as String?;
    return ReplayRenderStatus(
      jobId: json['job_id'] as String? ?? '',
      status: ReplayStateSnapshot.resolve(
        rawStatus: (json['replay_state'] as String?) ??
            (json['status'] as String? ?? ''),
        videoPath: videoPath,
        error: error,
      ).statusId,
      videoPath: videoPath,
      error: error,
    );
  }
}

class ExecutionTraceEpisode {
  final int episodeIndex;
  final List<ExecutionTraceStep> steps;

  const ExecutionTraceEpisode({
    required this.episodeIndex,
    required this.steps,
  });

  factory ExecutionTraceEpisode.fromJson(Map<String, dynamic> json) {
    return ExecutionTraceEpisode(
      episodeIndex: (json['episode_index'] as num?)?.toInt() ?? 0,
      steps: (json['steps'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(ExecutionTraceStep.fromJson)
          .toList(growable: false),
    );
  }
}

class ExecutionEpisodeSummary {
  final int episodeIndex;
  final int stepCount;
  final double totalReward;
  final bool terminated;
  final bool truncated;

  const ExecutionEpisodeSummary({
    required this.episodeIndex,
    required this.stepCount,
    required this.totalReward,
    required this.terminated,
    required this.truncated,
  });

  factory ExecutionEpisodeSummary.fromJson(Map<String, dynamic> json) {
    return ExecutionEpisodeSummary(
      episodeIndex: (json['episode_index'] as num?)?.toInt() ?? 0,
      stepCount: (json['step_count'] as num?)?.toInt() ?? 0,
      totalReward: (json['total_reward'] as num?)?.toDouble() ?? 0.0,
      terminated: json['terminated'] as bool? ?? false,
      truncated: json['truncated'] as bool? ?? false,
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

class NGainMetricsExport {
  final String fileName;
  final List<int> bytes;

  const NGainMetricsExport({
    required this.fileName,
    required this.bytes,
  });
}

class LearningAnalyticsExport {
  final String fileName;
  final List<int> bytes;

  const LearningAnalyticsExport({
    required this.fileName,
    required this.bytes,
  });
}

class ALEIComponentsExport {
  final String fileName;
  final List<int> bytes;

  const ALEIComponentsExport({
    required this.fileName,
    required this.bytes,
  });
}

class StudySessionSurveyResult {
  final double susScore;
  final double tlxOverall;

  const StudySessionSurveyResult({
    required this.susScore,
    required this.tlxOverall,
  });

  factory StudySessionSurveyResult.fromJson(Map<String, dynamic> json) {
    return StudySessionSurveyResult(
      susScore: (json['sus_score'] as num? ?? 0).toDouble(),
      tlxOverall: (json['tlx_overall'] as num? ?? 0).toDouble(),
    );
  }
}

class LearningTelemetryEvent {
  final String lessonId;
  final String? conceptId;
  final String sessionId;
  final String eventType;
  final DateTime occurredAtUtc;
  final Map<String, dynamic> payloadJson;
  final String sourceVersion;

  const LearningTelemetryEvent({
    required this.lessonId,
    required this.conceptId,
    required this.sessionId,
    required this.eventType,
    required this.occurredAtUtc,
    required this.payloadJson,
    this.sourceVersion = 'study_buddy_v1_flutter',
  });

  Map<String, dynamic> toJson() {
    return {
      'lesson_id': lessonId,
      if (conceptId != null) 'concept_id': conceptId,
      'session_id': sessionId,
      'event_type': eventType,
      'occurred_at_utc': occurredAtUtc.toUtc().toIso8601String(),
      'payload_json': payloadJson,
      'source_version': sourceVersion,
    };
  }
}

class StudyBuddyInterventionContent {
  final String interventionType;
  final String title;
  final String message;
  final String diagnosticQuestion;
  final List<String> choices;
  final String? checkpoint;
  final String nextStep;
  final List<String> conceptIds;
  final String solutionLeakageRisk;

  const StudyBuddyInterventionContent({
    required this.interventionType,
    required this.title,
    required this.message,
    required this.diagnosticQuestion,
    required this.choices,
    required this.checkpoint,
    required this.nextStep,
    required this.conceptIds,
    required this.solutionLeakageRisk,
  });

  factory StudyBuddyInterventionContent.fromJson(Map<String, dynamic> json) {
    return StudyBuddyInterventionContent(
      interventionType: json['intervention_type'] as String? ?? '',
      title: json['title'] as String? ?? 'Study Buddy',
      message: json['message'] as String? ?? '',
      diagnosticQuestion: json['diagnostic_question'] as String? ?? '',
      choices: (json['choices'] as List<dynamic>? ?? const [])
          .map((value) => value.toString())
          .toList(growable: false),
      checkpoint: json['checkpoint'] as String?,
      nextStep: json['next_step'] as String? ?? '',
      conceptIds: (json['concept_ids'] as List<dynamic>? ?? const [])
          .map((value) => value.toString())
          .toList(growable: false),
      solutionLeakageRisk: json['solution_leakage_risk'] as String? ?? 'low',
    );
  }
}

class StudyBuddyIntervention {
  final String id;
  final String lessonId;
  final String? conceptId;
  final String sessionId;
  final String triggerType;
  final double triggerScore;
  final String interventionType;
  final String status;
  final String promptVersion;
  final String reflectionPassResult;
  final StudyBuddyInterventionContent content;

  const StudyBuddyIntervention({
    required this.id,
    required this.lessonId,
    required this.conceptId,
    required this.sessionId,
    required this.triggerType,
    required this.triggerScore,
    required this.interventionType,
    required this.status,
    required this.promptVersion,
    required this.reflectionPassResult,
    required this.content,
  });

  factory StudyBuddyIntervention.fromJson(Map<String, dynamic> json) {
    final response = (json['response'] as Map<String, dynamic>?) ?? const {};
    return StudyBuddyIntervention(
      id: json['id'] as String? ?? '',
      lessonId: json['lesson_id'] as String? ?? '',
      conceptId: json['concept_id'] as String?,
      sessionId: json['session_id'] as String? ?? '',
      triggerType: json['trigger_type'] as String? ?? '',
      triggerScore: (json['trigger_score'] as num?)?.toDouble() ?? 0,
      interventionType: json['intervention_type'] as String? ?? '',
      status: json['status'] as String? ?? '',
      promptVersion: json['prompt_version'] as String? ?? '',
      reflectionPassResult: json['reflection_pass_result'] as String? ?? '',
      content: StudyBuddyInterventionContent.fromJson(response),
    );
  }
}

class StudyBuddyChatMessage {
  final String role;
  final String content;

  const StudyBuddyChatMessage({
    required this.role,
    required this.content,
  });

  bool get isUser => role == 'user';

  Map<String, dynamic> toJson() {
    return {
      'role': role,
      'content': content,
    };
  }

  factory StudyBuddyChatMessage.fromJson(Map<String, dynamic> json) {
    return StudyBuddyChatMessage(
      role: json['role'] as String? ?? 'assistant',
      content: json['content'] as String? ?? '',
    );
  }
}

class StudyBuddyChatResponse {
  final StudyBuddyChatMessage message;
  final bool usedFallback;
  final String? suggestedNextStep;
  final List<String> conceptIds;
  final String solutionLeakageRisk;
  final Map<String, dynamic> observability;

  const StudyBuddyChatResponse({
    required this.message,
    required this.usedFallback,
    required this.suggestedNextStep,
    required this.conceptIds,
    required this.solutionLeakageRisk,
    required this.observability,
  });

  factory StudyBuddyChatResponse.fromJson(Map<String, dynamic> json) {
    final message = json['message'];
    return StudyBuddyChatResponse(
      message: StudyBuddyChatMessage.fromJson(
        message is Map<String, dynamic>
            ? message
            : {
                'role': 'assistant',
                'content': json['reply'] as String? ?? '',
              },
      ),
      usedFallback: json['used_fallback'] as bool? ?? false,
      suggestedNextStep: json['suggested_next_step'] as String?,
      conceptIds: (json['concept_ids'] as List<dynamic>? ?? const [])
          .map((value) => value.toString())
          .toList(growable: false),
      solutionLeakageRisk: json['solution_leakage_risk'] as String? ?? 'low',
      observability:
          (json['observability'] as Map<String, dynamic>?) ?? const {},
    );
  }
}

class StudyBuddyMasterySnapshot {
  final String id;
  final String lessonId;
  final String conceptId;
  final double masteryScore;
  final double supportNeedScore;
  final double confidenceScore;
  final int stalenessDays;
  final Map<String, dynamic> evidenceSummary;
  final DateTime? recordedAtUtc;

  const StudyBuddyMasterySnapshot({
    required this.id,
    required this.lessonId,
    required this.conceptId,
    required this.masteryScore,
    required this.supportNeedScore,
    required this.confidenceScore,
    required this.stalenessDays,
    required this.evidenceSummary,
    required this.recordedAtUtc,
  });

  bool get isLowConfidence => confidenceScore < 0.30;

  factory StudyBuddyMasterySnapshot.fromJson(Map<String, dynamic> json) {
    return StudyBuddyMasterySnapshot(
      id: json['id'] as String? ?? '',
      lessonId: json['lesson_id'] as String? ?? '',
      conceptId: json['concept_id'] as String? ?? '',
      masteryScore: (json['mastery_score'] as num?)?.toDouble() ?? 0.50,
      supportNeedScore: (json['support_need_score'] as num?)?.toDouble() ?? 0.0,
      confidenceScore: (json['confidence_score'] as num?)?.toDouble() ?? 0.10,
      stalenessDays: (json['staleness_days'] as num?)?.toInt() ?? 0,
      evidenceSummary:
          (json['evidence_summary'] as Map<String, dynamic>?) ?? const {},
      recordedAtUtc:
          DateTime.tryParse(json['recorded_at_utc'] as String? ?? ''),
    );
  }
}

class StudyBuddyReviewRecommendation {
  final String conceptId;
  final String lessonId;
  final double masteryScore;
  final double supportNeedScore;
  final double confidenceScore;
  final int stalenessDays;
  final double reviewPriority;

  const StudyBuddyReviewRecommendation({
    required this.conceptId,
    required this.lessonId,
    required this.masteryScore,
    required this.supportNeedScore,
    required this.confidenceScore,
    required this.stalenessDays,
    required this.reviewPriority,
  });

  factory StudyBuddyReviewRecommendation.fromJson(Map<String, dynamic> json) {
    return StudyBuddyReviewRecommendation(
      conceptId: json['concept_id'] as String? ?? '',
      lessonId: json['lesson_id'] as String? ?? '',
      masteryScore: (json['mastery_score'] as num?)?.toDouble() ?? 0.50,
      supportNeedScore: (json['support_need_score'] as num?)?.toDouble() ?? 0.0,
      confidenceScore: (json['confidence_score'] as num?)?.toDouble() ?? 0.10,
      stalenessDays: (json['staleness_days'] as num?)?.toInt() ?? 0,
      reviewPriority: (json['review_priority'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class SurveyTemplateItemData {
  final String id;
  final int orderIndex;
  final String questionText;
  final String questionType;
  final bool required;

  const SurveyTemplateItemData({
    required this.id,
    required this.orderIndex,
    required this.questionText,
    required this.questionType,
    required this.required,
  });

  factory SurveyTemplateItemData.fromJson(Map<String, dynamic> json) {
    return SurveyTemplateItemData(
      id: json['id'] as String? ?? '',
      orderIndex: (json['order_index'] as num?)?.toInt() ?? 0,
      questionText: json['question_text'] as String? ?? '',
      questionType: json['question_type'] as String? ?? 'likert_5',
      required: json['required'] as bool? ?? true,
    );
  }
}

class SurveyTemplateData {
  final String id;
  final String name;
  final String contextTrigger;
  final int version;
  final List<SurveyTemplateItemData> items;

  const SurveyTemplateData({
    required this.id,
    required this.name,
    required this.contextTrigger,
    required this.version,
    required this.items,
  });

  factory SurveyTemplateData.fromJson(Map<String, dynamic> json) {
    return SurveyTemplateData(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      contextTrigger: json['context_trigger'] as String? ?? '',
      version: (json['version'] as num?)?.toInt() ?? 1,
      items: (json['items'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(SurveyTemplateItemData.fromJson)
          .toList(growable: false),
    );
  }
}

class MicroSurveySubmitResult {
  final String surveyResponseId;

  const MicroSurveySubmitResult({required this.surveyResponseId});

  factory MicroSurveySubmitResult.fromJson(Map<String, dynamic> json) {
    return MicroSurveySubmitResult(
      surveyResponseId: json['survey_response_id'] as String? ?? '',
    );
  }
}

class StudyBuddySummary {
  final List<StudyBuddyMasterySnapshot> masterySnapshots;
  final StudyBuddyReviewRecommendation? reviewRecommendation;
  final List<StudyBuddyIntervention> recentInterventions;

  const StudyBuddySummary({
    required this.masterySnapshots,
    required this.reviewRecommendation,
    required this.recentInterventions,
  });

  const StudyBuddySummary.empty()
      : masterySnapshots = const [],
        reviewRecommendation = null,
        recentInterventions = const [];

  factory StudyBuddySummary.fromJson(Map<String, dynamic> json) {
    final recommendation = json['review_recommendation'];
    return StudyBuddySummary(
      masterySnapshots:
          (json['mastery_snapshots'] as List<dynamic>? ?? const [])
              .whereType<Map<String, dynamic>>()
              .map(StudyBuddyMasterySnapshot.fromJson)
              .toList(growable: false),
      reviewRecommendation: recommendation is Map<String, dynamic>
          ? StudyBuddyReviewRecommendation.fromJson(recommendation)
          : null,
      recentInterventions:
          (json['recent_interventions'] as List<dynamic>? ?? const [])
              .whereType<Map<String, dynamic>>()
              .map(StudyBuddyIntervention.fromJson)
              .toList(growable: false),
    );
  }
}
