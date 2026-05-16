import 'dart:async';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'backend_api.dart';
import 'export_file_saver.dart';
import 'flashcard_catalog.dart';
import 'lesson_models.dart';
import 'local_lesson_catalog.dart';
export 'lesson_models.dart';

/// Current run lifecycle shown in the workspace controls and status strip.
enum RunStatus { idle, running, success, failed, stopped }

/// Top-level application destinations owned by [MainLayout].
enum AppSection { home, workspace, flashcards, quiz, admin }

const Object _sentinel = Object();

@immutable
class RLWorkbenchState {
  final List<LessonSection> sections;
  final List<StudyFlashcard> flashcards;
  final AppSection currentSection;
  final LearnerProfile? learner;
  final LearnerProgress progress;
  final bool isSigningIn;
  final bool isQuizLoading;
  final String homeMessage;
  final String quizStatusMessage;
  final QuizSessionData? activeQuiz;
  final Map<String, int> quizAnswers;
  final QuizAttemptSummary? lastQuizSummary;
  final LessonDefinition selectedLesson;
  final String code;
  final String? workspaceSessionId;
  final bool workspaceReady;
  final WorkspaceConnectionStatus editorConnectionStatus;
  final WorkspaceConnectionStatus consoleConnectionStatus;
  final String? activeRunId;
  final String runOutputBuffer;
  final int scriptVersion;
  final RunStatus runStatus;
  final int currentEpisode;
  final int currentStep;
  final double totalReward;
  final double averageReward;
  final double bestEpisodeReward;
  final String statusMessage;
  final String videoPath;
  final List<ExecutionTestCaseResult> testResults;
  final List<ExecutionTraceStep> stepTrace;
  final String? failureKind;
  final List<String> unresolvedBlanks;
  final ExecutionStudentFeedback? studentFeedback;
  final bool sidebarVisible;
  final String? adminSelectedLessonId;
  final String adminMessage;
  final bool isAdminExporting;

  const RLWorkbenchState({
    required this.sections,
    required this.flashcards,
    required this.currentSection,
    required this.learner,
    required this.progress,
    required this.isSigningIn,
    required this.isQuizLoading,
    required this.homeMessage,
    required this.quizStatusMessage,
    required this.activeQuiz,
    required this.quizAnswers,
    required this.lastQuizSummary,
    required this.selectedLesson,
    required this.code,
    required this.workspaceSessionId,
    required this.workspaceReady,
    required this.editorConnectionStatus,
    required this.consoleConnectionStatus,
    required this.activeRunId,
    required this.runOutputBuffer,
    required this.scriptVersion,
    required this.runStatus,
    required this.currentEpisode,
    required this.currentStep,
    required this.totalReward,
    required this.averageReward,
    required this.bestEpisodeReward,
    required this.statusMessage,
    required this.videoPath,
    required this.testResults,
    required this.stepTrace,
    required this.failureKind,
    required this.unresolvedBlanks,
    required this.studentFeedback,
    required this.sidebarVisible,
    required this.adminSelectedLessonId,
    required this.adminMessage,
    required this.isAdminExporting,
  });

  factory RLWorkbenchState.initial() {
    final selectedLesson = fallbackLessonSections.first.lessons.first;
    return RLWorkbenchState(
      sections: fallbackLessonSections,
      flashcards: studyFlashcards,
      currentSection: AppSection.home,
      learner: null,
      progress: const LearnerProgress.empty(),
      isSigningIn: false,
      isQuizLoading: false,
      homeMessage: 'Sign in to save quiz results and lesson progress.',
      quizStatusMessage:
          'Take a randomized pre-test before you begin the lessons.',
      activeQuiz: null,
      quizAnswers: const {},
      lastQuizSummary: null,
      selectedLesson: selectedLesson,
      code: selectedLesson.starterCode,
      workspaceSessionId: null,
      workspaceReady: false,
      editorConnectionStatus: WorkspaceConnectionStatus.disconnected,
      consoleConnectionStatus: WorkspaceConnectionStatus.disconnected,
      activeRunId: null,
      runOutputBuffer: '',
      scriptVersion: 1,
      runStatus: RunStatus.idle,
      currentEpisode: 0,
      currentStep: 0,
      totalReward: 0.0,
      averageReward: 0.0,
      bestEpisodeReward: 0.0,
      statusMessage: 'Ready to run ${selectedLesson.title}.',
      videoPath: '',
      testResults: const [],
      stepTrace: const [],
      failureKind: null,
      unresolvedBlanks: const [],
      studentFeedback: null,
      sidebarVisible: true,
      adminSelectedLessonId: selectedLesson.id,
      adminMessage: 'Edit lessons in this session.',
      isAdminExporting: false,
    );
  }

  String get runStatusLabel {
    switch (runStatus) {
      case RunStatus.idle:
        return 'Idle';
      case RunStatus.running:
        return 'Running';
      case RunStatus.success:
        return 'Complete';
      case RunStatus.failed:
        return 'Failed';
      case RunStatus.stopped:
        return 'Stopped';
    }
  }

  RLWorkbenchState copyWith({
    List<LessonSection>? sections,
    List<StudyFlashcard>? flashcards,
    AppSection? currentSection,
    Object? learner = _sentinel,
    LearnerProgress? progress,
    bool? isSigningIn,
    bool? isQuizLoading,
    String? homeMessage,
    String? quizStatusMessage,
    Object? activeQuiz = _sentinel,
    Map<String, int>? quizAnswers,
    Object? lastQuizSummary = _sentinel,
    LessonDefinition? selectedLesson,
    String? code,
    Object? workspaceSessionId = _sentinel,
    bool? workspaceReady,
    WorkspaceConnectionStatus? editorConnectionStatus,
    WorkspaceConnectionStatus? consoleConnectionStatus,
    Object? activeRunId = _sentinel,
    String? runOutputBuffer,
    int? scriptVersion,
    RunStatus? runStatus,
    int? currentEpisode,
    int? currentStep,
    double? totalReward,
    double? averageReward,
    double? bestEpisodeReward,
    String? statusMessage,
    String? videoPath,
    List<ExecutionTestCaseResult>? testResults,
    List<ExecutionTraceStep>? stepTrace,
    Object? failureKind = _sentinel,
    List<String>? unresolvedBlanks,
    Object? studentFeedback = _sentinel,
    bool? sidebarVisible,
    Object? adminSelectedLessonId = _sentinel,
    String? adminMessage,
    bool? isAdminExporting,
  }) {
    return RLWorkbenchState(
      sections: sections ?? this.sections,
      flashcards: flashcards ?? this.flashcards,
      currentSection: currentSection ?? this.currentSection,
      learner: identical(learner, _sentinel)
          ? this.learner
          : learner as LearnerProfile?,
      progress: progress ?? this.progress,
      isSigningIn: isSigningIn ?? this.isSigningIn,
      isQuizLoading: isQuizLoading ?? this.isQuizLoading,
      homeMessage: homeMessage ?? this.homeMessage,
      quizStatusMessage: quizStatusMessage ?? this.quizStatusMessage,
      activeQuiz: identical(activeQuiz, _sentinel)
          ? this.activeQuiz
          : activeQuiz as QuizSessionData?,
      quizAnswers: quizAnswers ?? this.quizAnswers,
      lastQuizSummary: identical(lastQuizSummary, _sentinel)
          ? this.lastQuizSummary
          : lastQuizSummary as QuizAttemptSummary?,
      selectedLesson: selectedLesson ?? this.selectedLesson,
      code: code ?? this.code,
      workspaceSessionId: identical(workspaceSessionId, _sentinel)
          ? this.workspaceSessionId
          : workspaceSessionId as String?,
      workspaceReady: workspaceReady ?? this.workspaceReady,
      editorConnectionStatus:
          editorConnectionStatus ?? this.editorConnectionStatus,
      consoleConnectionStatus:
          consoleConnectionStatus ?? this.consoleConnectionStatus,
      activeRunId: identical(activeRunId, _sentinel)
          ? this.activeRunId
          : activeRunId as String?,
      runOutputBuffer: runOutputBuffer ?? this.runOutputBuffer,
      scriptVersion: scriptVersion ?? this.scriptVersion,
      runStatus: runStatus ?? this.runStatus,
      currentEpisode: currentEpisode ?? this.currentEpisode,
      currentStep: currentStep ?? this.currentStep,
      totalReward: totalReward ?? this.totalReward,
      averageReward: averageReward ?? this.averageReward,
      bestEpisodeReward: bestEpisodeReward ?? this.bestEpisodeReward,
      statusMessage: statusMessage ?? this.statusMessage,
      videoPath: videoPath ?? this.videoPath,
      testResults: testResults ?? this.testResults,
      stepTrace: stepTrace ?? this.stepTrace,
      failureKind: identical(failureKind, _sentinel)
          ? this.failureKind
          : failureKind as String?,
      unresolvedBlanks: unresolvedBlanks ?? this.unresolvedBlanks,
      studentFeedback: identical(studentFeedback, _sentinel)
          ? this.studentFeedback
          : studentFeedback as ExecutionStudentFeedback?,
      sidebarVisible: sidebarVisible ?? this.sidebarVisible,
      adminSelectedLessonId: identical(adminSelectedLessonId, _sentinel)
          ? this.adminSelectedLessonId
          : adminSelectedLessonId as String?,
      adminMessage: adminMessage ?? this.adminMessage,
      isAdminExporting: isAdminExporting ?? this.isAdminExporting,
    );
  }
}

/// Coordinates learner actions across auth, lesson selection, execution,
/// workspace sync, quizzes, and admin editing.
class RLWorkbenchCubit extends Cubit<RLWorkbenchState> {
  RLWorkbenchCubit({
    BackendApi? api,
  })  : _api = api ?? HttpBackendApi(),
        super(RLWorkbenchState.initial()) {
    unawaited(loadBackendLessonCatalog());
    if (state.selectedLesson.backendEnabled) {
      unawaited(
          _attachWorkspaceSession(state.selectedLesson, announceStatus: false));
    }
  }

  final BackendApi _api;
  String? _activeTaskId;
  String? _activeWorkspaceRunId;

  BackendApi get api => _api;

  Future<void> loadBackendLessonCatalog() async {
    try {
      final backendSections = await _api.fetchLessonSections();
      if (backendSections.isEmpty ||
          backendSections.every((section) => section.lessons.isEmpty)) {
        return;
      }

      var mergedSections = backendSections;
      for (final section in state.sections) {
        for (final lesson in section.lessons) {
          if (!_isCoreLessonId(lesson.id)) {
            mergedSections = _upsertLessonInSections(mergedSections, lesson);
          }
        }
      }

      final previousLesson = state.selectedLesson;
      final selectedLesson =
          _findLessonById(mergedSections, previousLesson.id) ??
              mergedSections.first.lessons.first;
      final selectedChanged = selectedLesson.id != previousLesson.id;
      final codeIsUntouchedStarter = state.code == previousLesson.starterCode;
      final shouldReplaceCode = selectedChanged || codeIsUntouchedStarter;

      emit(
        state.copyWith(
          sections: mergedSections,
          selectedLesson: selectedLesson,
          code: shouldReplaceCode ? selectedLesson.starterCode : state.code,
          adminSelectedLessonId:
              _findLessonById(mergedSections, state.adminSelectedLessonId ?? '')
                          ?.id !=
                      null
                  ? state.adminSelectedLessonId
                  : selectedLesson.id,
          homeMessage: state.learner == null
              ? 'Using backend lesson catalog. Sign in to save quiz results and lesson progress.'
              : state.homeMessage,
        ),
      );

      if (shouldReplaceCode && state.workspaceSessionId != null) {
        unawaited(_syncWorkspaceCode(
          state.workspaceSessionId!,
          selectedLesson.starterCode,
        ));
      }
      if (selectedChanged && selectedLesson.backendEnabled) {
        unawaited(_attachWorkspaceSession(
          selectedLesson,
          announceStatus: false,
        ));
      }
    } on BackendApiException {
      _retainFallbackLessonCatalog();
    } catch (_) {
      _retainFallbackLessonCatalog();
    }
  }

  void _retainFallbackLessonCatalog() {
    if (state.learner != null) {
      return;
    }
    emit(
      state.copyWith(
        homeMessage:
            'Using local fallback lessons. Start the backend to refresh lesson content.',
      ),
    );
  }

  void navigateTo(AppSection section) {
    emit(state.copyWith(currentSection: section));
  }

  void toggleSidebar() {
    emit(state.copyWith(sidebarVisible: !state.sidebarVisible));
  }

  Future<void> signIn(String displayName, String password) async {
    final normalizedName = displayName.trim();
    if (normalizedName.isEmpty) {
      emit(state.copyWith(homeMessage: 'Enter a student name to continue.'));
      return;
    }
    if (password.trim().isEmpty) {
      emit(state.copyWith(homeMessage: 'Enter your password to continue.'));
      return;
    }

    emit(state.copyWith(
      isSigningIn: true,
      homeMessage: 'Signing in $normalizedName...',
    ));

    final firebaseResult = await _firebaseSignIn(normalizedName, password);
    if (firebaseResult is _FirebaseAuthError) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: firebaseResult.message,
      ));
      return;
    }
    final firebaseIdToken = firebaseResult as String?;
    if (firebaseIdToken == null) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage:
            'Could not reach Firebase. Check your network and try again.',
      ));
      return;
    }

    try {
      final dashboard = await _api.signIn(
        displayName: normalizedName,
        password: password,
        firebaseIdToken: firebaseIdToken,
      );
      emit(
        state.copyWith(
          learner: dashboard.student,
          progress: dashboard.progress,
          isSigningIn: false,
          homeMessage: 'Signed in as ${dashboard.student.displayName}.',
          quizStatusMessage: _quizPromptForProgress(dashboard.progress),
          currentSection: AppSection.home,
        ),
      );
    } on BackendApiException catch (error) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: error.message,
      ));
    } catch (_) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: 'Backend unavailable. Start FastAPI and try again.',
      ));
    }
  }

  /// Returns the Firebase ID token string on success, or a [_FirebaseAuthError]
  /// when the user provides wrong credentials. Returns null only if Firebase
  /// auth is unavailable (network, misconfiguration).
  Future<Object?> _firebaseSignIn(String name, String password) async {
    final email = _emailFromName(name);
    try {
      UserCredential cred;
      try {
        cred = await FirebaseAuth.instance
            .signInWithEmailAndPassword(email: email, password: password);
      } on FirebaseAuthException catch (e) {
        if (e.code == 'user-not-found' || e.code == 'invalid-credential') {
          cred = await FirebaseAuth.instance
              .createUserWithEmailAndPassword(email: email, password: password);
          await cred.user?.updateDisplayName(name);
        } else {
          return _FirebaseAuthError(_friendlyFirebaseMessage(e));
        }
      }
      return await cred.user?.getIdToken();
    } on FirebaseAuthException catch (e) {
      return _FirebaseAuthError(_friendlyFirebaseMessage(e));
    } catch (_) {
      return null;
    }
  }

  static String _emailFromName(String name) {
    final slug = name
        .toLowerCase()
        .replaceAll(RegExp(r'[^a-z0-9]+'), '.')
        .replaceAll(RegExp(r'^\.+|\.+$'), '');
    return '$slug@rl-platform.students';
  }

  static String _friendlyFirebaseMessage(FirebaseAuthException e) {
    switch (e.code) {
      case 'wrong-password':
        return 'Incorrect password. Try again.';
      case 'too-many-requests':
        return 'Too many sign-in attempts. Wait a moment and try again.';
      case 'user-disabled':
        return 'This account has been disabled. Contact your instructor.';
      default:
        return e.message ?? 'Firebase authentication failed.';
    }
  }

  void signOut() {
    _activeTaskId = null;
    _activeWorkspaceRunId = null;
    FirebaseAuth.instance.signOut().ignore();
    emit(
      state.copyWith(
        learner: null,
        progress: const LearnerProgress.empty(),
        activeQuiz: null,
        quizAnswers: const {},
        lastQuizSummary: null,
        isQuizLoading: false,
        currentSection: AppSection.home,
        homeMessage:
            'Signed out. Sign in to save quiz results and lesson progress.',
        quizStatusMessage:
            'Take a randomized pre-test before you begin the lessons.',
        workspaceSessionId: null,
        workspaceReady: false,
        editorConnectionStatus: WorkspaceConnectionStatus.disconnected,
        consoleConnectionStatus: WorkspaceConnectionStatus.disconnected,
        activeRunId: null,
        runOutputBuffer: '',
        scriptVersion: 1,
      ),
    );
  }

  Future<void> refreshDashboard({bool quiet = false}) async {
    final learner = state.learner;
    if (learner == null) {
      return;
    }

    try {
      final dashboard = await _api.getDashboard(studentId: learner.id);
      final nextState = quiet
          ? state.copyWith(
              learner: dashboard.student,
              progress: dashboard.progress,
              quizStatusMessage: _quizPromptForProgress(dashboard.progress),
            )
          : state.copyWith(
              learner: dashboard.student,
              progress: dashboard.progress,
              homeMessage: 'Progress updated.',
              quizStatusMessage: _quizPromptForProgress(dashboard.progress),
            );
      emit(nextState);
    } on BackendApiException catch (error) {
      if (!quiet) {
        emit(state.copyWith(homeMessage: error.message));
      }
    }
  }

  void openLesson(LessonDefinition lesson) {
    _activeTaskId = null;
    _activeWorkspaceRunId = null;
    final preserveWorkspace = state.selectedLesson.id == lesson.id &&
        state.workspaceSessionId != null;
    emit(
      state.copyWith(
        selectedLesson: lesson,
        code: preserveWorkspace ? state.code : lesson.starterCode,
        currentSection: AppSection.workspace,
        workspaceSessionId: preserveWorkspace ? state.workspaceSessionId : null,
        workspaceReady: preserveWorkspace ? state.workspaceReady : false,
        editorConnectionStatus: preserveWorkspace
            ? state.editorConnectionStatus
            : lesson.backendEnabled
                ? WorkspaceConnectionStatus.connecting
                : WorkspaceConnectionStatus.disconnected,
        consoleConnectionStatus: preserveWorkspace
            ? state.consoleConnectionStatus
            : lesson.backendEnabled
                ? WorkspaceConnectionStatus.connecting
                : WorkspaceConnectionStatus.disconnected,
        activeRunId: null,
        runOutputBuffer: '',
        scriptVersion: preserveWorkspace ? state.scriptVersion : 1,
        runStatus: RunStatus.idle,
        currentEpisode: 0,
        currentStep: 0,
        totalReward: 0.0,
        averageReward: 0.0,
        bestEpisodeReward: 0.0,
        videoPath: '',
        testResults: const [],
        stepTrace: const [],
        failureKind: null,
        unresolvedBlanks: const [],
        studentFeedback: null,
        statusMessage: preserveWorkspace
            ? state.statusMessage
            : lesson.backendEnabled
                ? 'Ready to run ${lesson.title}.'
                : '${lesson.title} is draft-only.',
      ),
    );
    if (lesson.backendEnabled && !preserveWorkspace) {
      unawaited(_attachWorkspaceSession(lesson));
    }
  }

  void selectLesson(LessonDefinition lesson) {
    if (state.selectedLesson.id == lesson.id) {
      return;
    }

    openLesson(lesson);
  }

  void updateCode(String value) {
    emit(state.copyWith(code: value));
    final sessionId = state.workspaceSessionId;
    if (sessionId != null) {
      unawaited(_syncWorkspaceCode(sessionId, value));
    }
  }

  Future<void> startQuiz(QuizPhase phase) async {
    final learner = state.learner;
    if (learner == null) {
      emit(
        state.copyWith(
          currentSection: AppSection.home,
          homeMessage: 'Sign in first to save quiz scores.',
        ),
      );
      return;
    }

    if (phase == QuizPhase.posttest && state.progress.successfulRuns == 0) {
      emit(
        state.copyWith(
          currentSection: AppSection.quiz,
          quizStatusMessage:
              'Complete at least one lesson run before taking the post-test.',
        ),
      );
      return;
    }

    emit(
      state.copyWith(
        currentSection: AppSection.quiz,
        isQuizLoading: true,
        activeQuiz: null,
        lastQuizSummary: null,
        quizAnswers: const {},
        quizStatusMessage:
            'Preparing ${quizPhaseLabel(phase).toLowerCase()}...',
      ),
    );

    try {
      final session = await _api.startQuiz(
        studentId: learner.id,
        phase: phase,
      );
      emit(
        state.copyWith(
          isQuizLoading: false,
          activeQuiz: session,
          lastQuizSummary: null,
          quizAnswers: const {},
          quizStatusMessage: '${quizPhaseLabel(session.phase)} is ready.',
        ),
      );
    } on BackendApiException catch (error) {
      emit(
        state.copyWith(
          isQuizLoading: false,
          quizStatusMessage: error.message,
        ),
      );
    } catch (_) {
      emit(
        state.copyWith(
          isQuizLoading: false,
          quizStatusMessage: 'Could not start quiz. Check backend.',
        ),
      );
    }
  }

  void answerQuizQuestion(String questionId, int selectedIndex) {
    final updatedAnswers = Map<String, int>.from(state.quizAnswers)
      ..[questionId] = selectedIndex;
    emit(state.copyWith(quizAnswers: updatedAnswers));
  }

  Future<void> submitQuiz() async {
    final learner = state.learner;
    final activeQuiz = state.activeQuiz;
    if (learner == null || activeQuiz == null) {
      return;
    }

    if (state.quizAnswers.length < activeQuiz.questions.length) {
      emit(
        state.copyWith(
          quizStatusMessage: 'Answer all questions before submit.',
        ),
      );
      return;
    }

    emit(
      state.copyWith(
        isQuizLoading: true,
        quizStatusMessage: 'Submitting quiz...',
      ),
    );

    try {
      final summary = await _api.submitQuiz(
        studentId: learner.id,
        sessionId: activeQuiz.sessionId,
        answers: state.quizAnswers,
      );
      emit(
        state.copyWith(
          isQuizLoading: false,
          progress: summary.progress,
          activeQuiz: null,
          quizAnswers: const {},
          lastQuizSummary: summary,
          quizStatusMessage:
              'Submitted. Score: ${summary.score}/${summary.totalQuestions}.',
        ),
      );
    } on BackendApiException catch (error) {
      emit(
        state.copyWith(
          isQuizLoading: false,
          quizStatusMessage: error.message,
        ),
      );
    } catch (_) {
      emit(
        state.copyWith(
          isQuizLoading: false,
          quizStatusMessage: 'Could not submit quiz. Check backend.',
        ),
      );
    }
  }

  Future<void> run() async {
    await runWorkspace();
  }

  Future<void> runWorkspace() async {
    final sessionId = await _ensureWorkspaceSession();
    if (sessionId == null) {
      emit(
        state.copyWith(
          statusMessage: 'Workspace runtime is not ready for this lesson.',
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
        ),
      );
      return;
    }

    emit(
      state.copyWith(
        currentSection: AppSection.workspace,
        statusMessage: 'Running script.py in the workspace...',
        editorConnectionStatus: WorkspaceConnectionStatus.ready,
        consoleConnectionStatus: WorkspaceConnectionStatus.ready,
      ),
    );

    try {
      final run = await _api.runWorkspaceScript(sessionId: sessionId);
      _activeWorkspaceRunId = run.runId;
      emit(
        state.copyWith(
          activeRunId: run.runId,
          statusMessage: 'Workspace run ${run.runId} started.',
        ),
      );
      await _pollWorkspaceRun(sessionId, run.runId);
    } on BackendApiException catch (error) {
      _activeWorkspaceRunId = null;
      emit(
        state.copyWith(
          activeRunId: null,
          statusMessage: error.message,
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
        ),
      );
    } catch (_) {
      _activeWorkspaceRunId = null;
      emit(
        state.copyWith(
          activeRunId: null,
          statusMessage:
              'Workspace runtime unavailable at ${BackendConnectionManager().baseUrl}.',
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
        ),
      );
    }
  }

  Future<void> submit() async {
    if (!state.selectedLesson.backendEnabled) {
      emit(
        state.copyWith(
          runStatus: RunStatus.failed,
          statusMessage: 'This lesson is draft-only.',
        ),
      );
      return;
    }

    final submissionCode = await _latestSubmissionCode();
    if (submissionCode.trim().isEmpty) {
      emit(
        _resetProgressState(
          'Add code before running ${state.selectedLesson.title}.',
        ),
      );
      return;
    }

    emit(
      state.copyWith(
        currentSection: AppSection.workspace,
        runStatus: RunStatus.running,
        currentEpisode: 0,
        currentStep: _nonEmptyLineCount(submissionCode),
        totalReward: 0.0,
        averageReward: 0.0,
        bestEpisodeReward: 0.0,
        videoPath: '',
        testResults: const [],
        stepTrace: const [],
        failureKind: null,
        unresolvedBlanks: const [],
        studentFeedback: null,
        statusMessage:
            'Submitting ${state.selectedLesson.title} for grading...',
      ),
    );

    try {
      final task = await _api.submitCode(
        lessonId: state.selectedLesson.id,
        code: submissionCode,
        studentId: state.learner?.id,
      );
      _activeTaskId = task.taskId;
      emit(
        state.copyWith(
          statusMessage: 'Queued. Task ${task.taskId}.',
        ),
      );

      await _pollUntilComplete(task.taskId);
    } on BackendApiException catch (error) {
      _activeTaskId = null;
      emit(
        state.copyWith(
          runStatus: RunStatus.failed,
          currentEpisode: 0,
          currentStep: 0,
          totalReward: 0.0,
          averageReward: 0.0,
          bestEpisodeReward: 0.0,
          videoPath: '',
          testResults: error.testResults,
          stepTrace: const [],
          failureKind: error.failureKind,
          unresolvedBlanks: error.unresolvedBlanks,
          studentFeedback: error.studentFeedback,
          statusMessage: error.message,
        ),
      );
    } catch (_) {
      _activeTaskId = null;
      emit(
        state.copyWith(
          runStatus: RunStatus.failed,
          currentEpisode: 0,
          currentStep: 0,
          totalReward: 0.0,
          averageReward: 0.0,
          bestEpisodeReward: 0.0,
          videoPath: '',
          testResults: const [],
          stepTrace: const [],
          failureKind: null,
          unresolvedBlanks: const [],
          studentFeedback: null,
          statusMessage:
              'Backend unavailable at ${BackendConnectionManager().baseUrl}.',
        ),
      );
    }
  }

  void stop() {
    if (state.runStatus == RunStatus.idle && _activeWorkspaceRunId == null) {
      return;
    }

    _activeTaskId = null;
    _activeWorkspaceRunId = null;
    emit(
      state.copyWith(
        activeRunId: null,
        runStatus: RunStatus.stopped,
        statusMessage:
            'Stopped monitoring the current run. Background execution may continue.',
      ),
    );
  }

  void reset() {
    _activeTaskId = null;
    _activeWorkspaceRunId = null;
    emit(
      state.copyWith(
        code: state.selectedLesson.starterCode,
        activeRunId: null,
        runOutputBuffer: '',
        scriptVersion: 1,
        runStatus: RunStatus.idle,
        currentEpisode: 0,
        currentStep: 0,
        totalReward: 0.0,
        averageReward: 0.0,
        bestEpisodeReward: 0.0,
        videoPath: '',
        testResults: const [],
        stepTrace: const [],
        failureKind: null,
        unresolvedBlanks: const [],
        studentFeedback: null,
        statusMessage:
            'Reset ${state.selectedLesson.title} to its starter template.',
      ),
    );
    final sessionId = state.workspaceSessionId;
    if (sessionId != null) {
      unawaited(
          _syncWorkspaceCode(sessionId, state.selectedLesson.starterCode));
    }
  }

  void selectAdminLesson(String lessonId) {
    emit(
      state.copyWith(
        currentSection: AppSection.admin,
        adminSelectedLessonId: lessonId,
      ),
    );
  }

  void createDraftLesson() {
    final draftId = 'draft_${DateTime.now().millisecondsSinceEpoch}';
    final draftLesson = LessonDefinition(
      id: draftId,
      title: 'New Draft Lesson',
      description: 'Draft lesson content awaiting instructional copy.',
      category: 'Studio Drafts',
      starterCode: '''
# Draft lessons are content-only until a backend lesson id is wired.
DISCOUNT_FACTOR = 0.95

def lesson_function(*args, **kwargs):
    return None
''',
      conceptVideo: const LessonConceptVideo(
        streamPath: '/media/concept-videos/draft_placeholder.mp4',
        durationLabel: '00:45',
        summary: 'Add a concept video.',
        highlights: [
          'Key environment visual',
          'Key code trace',
          'Key math step',
        ],
      ),
      exercise: const LessonExerciseBrief(
        title: 'Describe the coding task',
        overview: 'Describe what the learner should implement.',
        tasks: [
          'Add the coding goal.',
          'Add the implementation steps.',
          'Add the success criteria.',
        ],
        successCriteria: [
          'A learner can tell what to write.',
          'A learner can tell when the solution is correct.',
        ],
        codeTip: 'Update starter code and constants here.',
      ),
      backendEnabled: false,
    );

    final sections = _upsertLessonInSections(state.sections, draftLesson);
    emit(
      state.copyWith(
        sections: sections,
        adminSelectedLessonId: draftId,
        adminMessage: 'Draft lesson created.',
      ),
    );
  }

  void saveAdminLesson({
    required String lessonId,
    required String title,
    required String category,
    required String description,
    required String conceptVideoStreamPath,
    required String conceptVideoDuration,
    required String conceptVideoSummary,
    required List<String> conceptHighlights,
    required String exerciseTitle,
    required String exerciseOverview,
    required List<String> exerciseTasks,
    required List<String> successCriteria,
    required String codeTip,
    required String starterCode,
    required bool backendEnabled,
  }) {
    final existingLesson = _findLessonById(state.sections, lessonId);
    if (existingLesson == null) {
      emit(state.copyWith(
        adminMessage: 'Could not find lesson $lessonId to update.',
      ));
      return;
    }

    final updatedLesson = existingLesson.copyWith(
      title: title.trim().isEmpty ? existingLesson.title : title.trim(),
      category:
          category.trim().isEmpty ? existingLesson.category : category.trim(),
      description: description.trim().isEmpty
          ? existingLesson.description
          : description.trim(),
      starterCode:
          starterCode.trim().isEmpty ? existingLesson.starterCode : starterCode,
      backendEnabled: backendEnabled,
      conceptVideo: existingLesson.conceptVideo.copyWith(
        streamPath: conceptVideoStreamPath.trim().isEmpty
            ? existingLesson.conceptVideo.streamPath
            : conceptVideoStreamPath.trim(),
        durationLabel: conceptVideoDuration.trim().isEmpty
            ? existingLesson.conceptVideo.durationLabel
            : conceptVideoDuration.trim(),
        summary: conceptVideoSummary.trim().isEmpty
            ? existingLesson.conceptVideo.summary
            : conceptVideoSummary.trim(),
        highlights: conceptHighlights.isEmpty
            ? existingLesson.conceptVideo.highlights
            : conceptHighlights,
      ),
      exercise: existingLesson.exercise.copyWith(
        title: exerciseTitle.trim().isEmpty
            ? existingLesson.exercise.title
            : exerciseTitle.trim(),
        overview: exerciseOverview.trim().isEmpty
            ? existingLesson.exercise.overview
            : exerciseOverview.trim(),
        tasks: exerciseTasks.isEmpty
            ? existingLesson.exercise.tasks
            : exerciseTasks,
        successCriteria: successCriteria.isEmpty
            ? existingLesson.exercise.successCriteria
            : successCriteria,
        codeTip: codeTip.trim().isEmpty
            ? existingLesson.exercise.codeTip
            : codeTip.trim(),
      ),
    );

    final updatedSections =
        _upsertLessonInSections(state.sections, updatedLesson);
    final selectedLesson = state.selectedLesson.id == updatedLesson.id
        ? updatedLesson
        : state.selectedLesson;

    emit(
      state.copyWith(
        sections: updatedSections,
        selectedLesson: selectedLesson,
        code: state.selectedLesson.id == updatedLesson.id
            ? updatedLesson.starterCode
            : state.code,
        adminSelectedLessonId: updatedLesson.id,
        adminMessage: 'Saved "${updatedLesson.title}".',
      ),
    );
  }

  void deleteAdminLesson(String lessonId) {
    if (_isCoreLessonId(lessonId)) {
      emit(
        state.copyWith(
          adminMessage:
              'Core lessons are locked and cannot be deleted from the studio.',
        ),
      );
      return;
    }

    var lessonFound = false;
    final updatedSections = <LessonSection>[];

    for (final section in state.sections) {
      final remainingLessons = section.lessons.where((lesson) {
        final keep = lesson.id != lessonId;
        if (!keep) {
          lessonFound = true;
        }
        return keep;
      }).toList(growable: false);

      if (remainingLessons.isNotEmpty) {
        updatedSections.add(section.copyWith(lessons: remainingLessons));
      }
    }

    if (!lessonFound) {
      emit(
        state.copyWith(
          adminMessage: 'Could not find lesson $lessonId to delete.',
        ),
      );
      return;
    }

    final fallbackLesson = updatedSections.first.lessons.first;
    final selectedLesson = state.selectedLesson.id == lessonId
        ? fallbackLesson
        : state.selectedLesson;

    emit(
      state.copyWith(
        sections: updatedSections,
        selectedLesson: selectedLesson,
        code: state.selectedLesson.id == lessonId
            ? fallbackLesson.starterCode
            : state.code,
        adminSelectedLessonId: state.adminSelectedLessonId == lessonId
            ? fallbackLesson.id
            : state.adminSelectedLessonId,
        adminMessage: 'Deleted lesson $lessonId from this session.',
      ),
    );
  }

  Future<void> exportAdminNGainMetrics() async {
    emit(
      state.copyWith(
        isAdminExporting: true,
        adminMessage: 'Exporting N-gain metrics to Excel...',
      ),
    );

    try {
      final export = await _api.exportNGainMetrics();
      final saveResult = await saveExportFile(
        fileName: export.fileName,
        bytes: export.bytes,
      );

      emit(
        state.copyWith(
          isAdminExporting: false,
          adminMessage: saveResult.success
              ? '${saveResult.message} ${saveResult.savedPath ?? ''}'.trim()
              : saveResult.message,
        ),
      );
    } on BackendApiException catch (error) {
      emit(
        state.copyWith(
          isAdminExporting: false,
          adminMessage: error.message,
        ),
      );
    } catch (_) {
      emit(
        state.copyWith(
          isAdminExporting: false,
          adminMessage: 'Could not export metrics. Check backend.',
        ),
      );
    }
  }

  Future<String?> _ensureWorkspaceSession() async {
    final existingSessionId = state.workspaceSessionId;
    if (existingSessionId != null && state.workspaceReady) {
      return existingSessionId;
    }

    if (!state.selectedLesson.backendEnabled) {
      return null;
    }

    await _attachWorkspaceSession(state.selectedLesson);
    return state.workspaceSessionId;
  }

  Future<void> _attachWorkspaceSession(
    LessonDefinition lesson, {
    bool announceStatus = true,
  }) async {
    final requestedLessonId = lesson.id;
    final showProgress =
        announceStatus || state.currentSection == AppSection.workspace;
    emit(
      state.copyWith(
        workspaceReady: false,
        editorConnectionStatus: WorkspaceConnectionStatus.connecting,
        consoleConnectionStatus: WorkspaceConnectionStatus.connecting,
        statusMessage: showProgress
            ? 'Preparing workspace for ${lesson.title}...'
            : state.statusMessage,
      ),
    );

    try {
      final session =
          await _api.createWorkspaceSession(lessonId: requestedLessonId);
      final file = await _api.getWorkspaceFile(sessionId: session.sessionId);
      if (isClosed || state.selectedLesson.id != requestedLessonId) {
        return;
      }

      emit(
        state.copyWith(
          code: file.content,
          workspaceSessionId: session.sessionId,
          workspaceReady: true,
          editorConnectionStatus: WorkspaceConnectionStatus.ready,
          consoleConnectionStatus: session.consoleReady
              ? WorkspaceConnectionStatus.ready
              : WorkspaceConnectionStatus.connecting,
          scriptVersion: file.version,
          statusMessage: showProgress
              ? 'Workspace ready for ${lesson.title}.'
              : state.statusMessage,
        ),
      );
    } on BackendApiException catch (error) {
      if (isClosed || state.selectedLesson.id != requestedLessonId) {
        return;
      }
      emit(
        state.copyWith(
          workspaceSessionId: null,
          workspaceReady: false,
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
          statusMessage: showProgress ? error.message : state.statusMessage,
        ),
      );
    } catch (_) {
      if (isClosed || state.selectedLesson.id != requestedLessonId) {
        return;
      }
      emit(
        state.copyWith(
          workspaceSessionId: null,
          workspaceReady: false,
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
          statusMessage: showProgress
              ? 'Workspace runtime unavailable. Start the gateway and worker in remote mode.'
              : state.statusMessage,
        ),
      );
    }
  }

  Future<void> _syncWorkspaceCode(String sessionId, String content) async {
    try {
      final snapshot = await _api.updateWorkspaceFile(
        sessionId: sessionId,
        content: content,
      );
      if (isClosed || state.workspaceSessionId != sessionId) {
        return;
      }
      emit(
        state.copyWith(
          code: snapshot.content,
          scriptVersion: snapshot.version,
        ),
      );
    } on BackendApiException {
      if (isClosed || state.workspaceSessionId != sessionId) {
        return;
      }
      emit(
        state.copyWith(
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
        ),
      );
    }
  }

  Future<String> _latestSubmissionCode() async {
    final sessionId = state.workspaceSessionId;
    if (sessionId == null) {
      return state.code;
    }

    try {
      final snapshot = await _api.getWorkspaceFile(sessionId: sessionId);
      emit(
        state.copyWith(
          code: snapshot.content,
          scriptVersion: snapshot.version,
        ),
      );
      return snapshot.content;
    } on BackendApiException {
      return state.code;
    }
  }

  RLWorkbenchState _resetProgressState(String message) {
    return state.copyWith(
      runStatus: RunStatus.idle,
      currentEpisode: 0,
      currentStep: 0,
      totalReward: 0.0,
      averageReward: 0.0,
      bestEpisodeReward: 0.0,
      videoPath: '',
      testResults: const [],
      stepTrace: const [],
      failureKind: null,
      unresolvedBlanks: const [],
      studentFeedback: null,
      statusMessage: message,
    );
  }

  int _nonEmptyLineCount(String source) {
    return source.split('\n').where((line) => line.trim().isNotEmpty).length;
  }

  Future<void> _pollUntilComplete(String taskId) async {
    while (_activeTaskId == taskId && state.runStatus == RunStatus.running) {
      final snapshot = await _api.getTaskStatus(taskId);

      if (_activeTaskId != taskId || state.runStatus != RunStatus.running) {
        return;
      }

      switch (snapshot.status) {
        case ExecutionTaskStatus.queued:
          emit(state.copyWith(
            statusMessage: 'Task $taskId queued.',
          ));
          break;
        case ExecutionTaskStatus.running:
          emit(state.copyWith(
            statusMessage: 'Task $taskId running.',
          ));
          break;
        case ExecutionTaskStatus.succeeded:
          final result = snapshot.result;
          if (result == null) {
            throw const BackendApiException(
              'Backend completed a task without returning a result.',
            );
          }

          _activeTaskId = null;
          emit(
            state.copyWith(
              runStatus: RunStatus.success,
              currentEpisode: result.metrics.episodesCompleted,
              currentStep: result.metrics.stepsRecorded,
              totalReward: result.metrics.totalReward,
              averageReward: result.metrics.averageReward,
              bestEpisodeReward: result.metrics.bestEpisodeReward,
              videoPath: result.videoPath,
              testResults: result.testResults,
              stepTrace: result.stepTrace,
              failureKind: null,
              unresolvedBlanks: const [],
              studentFeedback: null,
              statusMessage: result.visualizationReady
                  ? '${result.message} Replay ready.'
                  : '${result.message} No replay video generated.',
            ),
          );
          await refreshDashboard(quiet: true);
          return;
        case ExecutionTaskStatus.failed:
          _activeTaskId = null;
          emit(
            state.copyWith(
              runStatus: RunStatus.failed,
              currentEpisode: 0,
              currentStep: 0,
              totalReward: 0.0,
              averageReward: 0.0,
              bestEpisodeReward: 0.0,
              videoPath: '',
              testResults: snapshot.testResults,
              stepTrace: const [],
              failureKind: snapshot.failureKind,
              unresolvedBlanks: snapshot.unresolvedBlanks,
              studentFeedback: snapshot.studentFeedback,
              statusMessage: snapshot.errorMessage ?? 'Execution task failed.',
            ),
          );
          return;
      }

      await Future<void>.delayed(const Duration(milliseconds: 500));
    }
  }

  Future<void> _pollWorkspaceRun(String sessionId, String runId) async {
    while (_activeWorkspaceRunId == runId) {
      final snapshot = await _api.getWorkspaceRun(
        sessionId: sessionId,
        runId: runId,
      );
      if (_activeWorkspaceRunId != runId) {
        return;
      }

      if (snapshot.isTerminal) {
        _activeWorkspaceRunId = null;
        emit(
          state.copyWith(
            activeRunId: null,
            statusMessage: snapshot.exitCode == 0
                ? 'Workspace run completed.'
                : 'Workspace run failed with exit code ${snapshot.exitCode ?? 1}.',
            editorConnectionStatus: WorkspaceConnectionStatus.ready,
            consoleConnectionStatus: WorkspaceConnectionStatus.ready,
          ),
        );
        return;
      }

      await Future<void>.delayed(const Duration(milliseconds: 400));
    }
  }

  String _quizPromptForProgress(LearnerProgress progress) {
    if (progress.pretestScore == null) {
      return 'Take the pre-test first.';
    }
    if (progress.posttestScore == null) {
      return 'Post-test unlocks after one run.';
    }
    return 'Both quizzes complete. Check N-gain on Quiz.';
  }

  LessonDefinition? _findLessonById(
      List<LessonSection> sections, String lessonId) {
    for (final section in sections) {
      for (final lesson in section.lessons) {
        if (lesson.id == lessonId) {
          return lesson;
        }
      }
    }
    return null;
  }

  bool _isCoreLessonId(String lessonId) {
    for (final section in fallbackLessonSections) {
      for (final lesson in section.lessons) {
        if (lesson.id == lessonId) {
          return true;
        }
      }
    }
    return false;
  }

  List<LessonSection> _upsertLessonInSections(
    List<LessonSection> sections,
    LessonDefinition lesson,
  ) {
    final categoryOrder = <String>[
      for (final section in sections) section.title,
      if (!sections.any((section) => section.title == lesson.category))
        lesson.category,
    ];
    final lessonsByCategory = <String, List<LessonDefinition>>{
      for (final category in categoryOrder) category: <LessonDefinition>[],
    };

    for (final section in sections) {
      for (final item in section.lessons) {
        if (item.id == lesson.id) {
          continue;
        }
        lessonsByCategory.putIfAbsent(
            item.category, () => <LessonDefinition>[]);
        lessonsByCategory[item.category]!.add(item);
      }
    }

    lessonsByCategory.putIfAbsent(lesson.category, () => <LessonDefinition>[]);
    lessonsByCategory[lesson.category]!.add(lesson);

    return lessonsByCategory.entries
        .where((entry) => entry.value.isNotEmpty)
        .map(
          (entry) => LessonSection(
            title: entry.key,
            lessons: entry.value,
          ),
        )
        .toList(growable: false);
  }
}

class _FirebaseAuthError {
  const _FirebaseAuthError(this.message);
  final String message;
}
