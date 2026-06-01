import 'dart:async';
import 'dart:convert';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'backend_api.dart';
import 'export_file_saver.dart';
import 'http_backend_api.dart';
import 'flashcard_catalog.dart';
import 'lesson_models.dart';
import 'local_lesson_catalog.dart';
export 'lesson_models.dart';

/// Current run lifecycle shown in the workspace controls and status strip.
enum RunStatus { idle, running, success, failed, stopped }

/// Top-level application destinations owned by [MainLayout].
enum AppSection { home, workspace, flashcards, quiz, admin }

const Object _sentinel = Object();
const String _authoredLessonsPrefsKey = 'rl_ide_authored_lessons_v1';

bool _canUseGoogleSignInOnCurrentOrigin() {
  final uri = Uri.base;
  if (uri.scheme == 'https') {
    return true;
  }
  final host = uri.host.toLowerCase();
  return host == 'localhost' || host == '127.0.0.1';
}

@immutable
class RLWorkbenchState {
  final List<LessonSection> sections;
  final List<StudyFlashcard> flashcards;
  final AppSection currentSection;
  final LearnerProfile? learner;
  final String currentRole;
  final bool isAuthenticated;
  final LearnerProgress progress;
  final bool isSigningIn;
  final bool isQuizLoading;
  final String homeMessage;
  final String quizStatusMessage;
  final QuizSessionData? activeQuiz;
  final Map<String, int> quizAnswers;
  final QuizAttemptSummary? lastQuizSummary;
  final LessonDefinition selectedLesson;
  final String studySessionId;
  final String code;
  final String? workspaceSessionId;
  final String? editorShellUrl;
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
  final List<ExecutionTraceEpisode> traceEpisodes;
  final List<ExecutionEpisodeSummary> episodeSummaries;
  final String? failureKind;
  final List<String> unresolvedBlanks;
  final ExecutionStudentFeedback? studentFeedback;
  final bool sidebarVisible;
  final String? adminSelectedLessonId;
  final String adminMessage;
  final bool isAdminExporting;
  final List<StaffStudentSummary> staffStudents;
  final String? selectedProgressStudentId;
  final LearnerDashboard? selectedProgressDashboard;
  final bool isProgressDashboardLoading;
  final StudyBuddyIntervention? studyBuddyIntervention;
  final bool studyBuddyLoading;
  final bool studyBuddyPanelDismissed;
  final StudyBuddySummary studyBuddySummary;
  final bool studyBuddySummaryLoading;
  final List<StudyBuddyChatMessage> studyBuddyChatMessages;
  final bool studyBuddyChatLoading;
  final String? studyBuddyChatError;
  final bool isPostStudySurveySubmitting;
  final bool postStudySurveyCompleted;
  final String postStudySurveyMessage;

  const RLWorkbenchState({
    required this.sections,
    required this.flashcards,
    required this.currentSection,
    required this.learner,
    required this.currentRole,
    required this.isAuthenticated,
    required this.progress,
    required this.isSigningIn,
    required this.isQuizLoading,
    required this.homeMessage,
    required this.quizStatusMessage,
    required this.activeQuiz,
    required this.quizAnswers,
    required this.lastQuizSummary,
    required this.selectedLesson,
    required this.studySessionId,
    required this.code,
    required this.workspaceSessionId,
    required this.editorShellUrl,
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
    required this.traceEpisodes,
    required this.episodeSummaries,
    required this.failureKind,
    required this.unresolvedBlanks,
    required this.studentFeedback,
    required this.sidebarVisible,
    required this.adminSelectedLessonId,
    required this.adminMessage,
    required this.isAdminExporting,
    required this.staffStudents,
    required this.selectedProgressStudentId,
    required this.selectedProgressDashboard,
    required this.isProgressDashboardLoading,
    required this.studyBuddyIntervention,
    required this.studyBuddyLoading,
    required this.studyBuddyPanelDismissed,
    required this.studyBuddySummary,
    required this.studyBuddySummaryLoading,
    required this.studyBuddyChatMessages,
    required this.studyBuddyChatLoading,
    required this.studyBuddyChatError,
    required this.isPostStudySurveySubmitting,
    required this.postStudySurveyCompleted,
    required this.postStudySurveyMessage,
  });

  factory RLWorkbenchState.initial() {
    final selectedLesson = fallbackLessonSections.first.lessons.first;
    return RLWorkbenchState(
      sections: fallbackLessonSections,
      flashcards: studyFlashcards,
      currentSection: AppSection.home,
      learner: null,
      currentRole: 'guest',
      isAuthenticated: false,
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
      studySessionId: _newStudySessionId(),
      code: selectedLesson.starterCode,
      workspaceSessionId: null,
      editorShellUrl: null,
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
      traceEpisodes: const [],
      episodeSummaries: const [],
      failureKind: null,
      unresolvedBlanks: const [],
      studentFeedback: null,
      sidebarVisible: true,
      adminSelectedLessonId: selectedLesson.id,
      adminMessage: 'Edit lessons in this session.',
      isAdminExporting: false,
      staffStudents: const [],
      selectedProgressStudentId: null,
      selectedProgressDashboard: null,
      isProgressDashboardLoading: false,
      studyBuddyIntervention: null,
      studyBuddyLoading: false,
      studyBuddyPanelDismissed: false,
      studyBuddySummary: const StudyBuddySummary.empty(),
      studyBuddySummaryLoading: false,
      studyBuddyChatMessages: const [],
      studyBuddyChatLoading: false,
      studyBuddyChatError: null,
      isPostStudySurveySubmitting: false,
      postStudySurveyCompleted: false,
      postStudySurveyMessage:
          'Complete the post-study survey to record workload and usability.',
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
    String? currentRole,
    bool? isAuthenticated,
    LearnerProgress? progress,
    bool? isSigningIn,
    bool? isQuizLoading,
    String? homeMessage,
    String? quizStatusMessage,
    Object? activeQuiz = _sentinel,
    Map<String, int>? quizAnswers,
    Object? lastQuizSummary = _sentinel,
    LessonDefinition? selectedLesson,
    String? studySessionId,
    String? code,
    Object? workspaceSessionId = _sentinel,
    Object? editorShellUrl = _sentinel,
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
    List<ExecutionTraceEpisode>? traceEpisodes,
    List<ExecutionEpisodeSummary>? episodeSummaries,
    Object? failureKind = _sentinel,
    List<String>? unresolvedBlanks,
    Object? studentFeedback = _sentinel,
    bool? sidebarVisible,
    Object? adminSelectedLessonId = _sentinel,
    String? adminMessage,
    bool? isAdminExporting,
    List<StaffStudentSummary>? staffStudents,
    Object? selectedProgressStudentId = _sentinel,
    Object? selectedProgressDashboard = _sentinel,
    bool? isProgressDashboardLoading,
    Object? studyBuddyIntervention = _sentinel,
    bool? studyBuddyLoading,
    bool? studyBuddyPanelDismissed,
    StudyBuddySummary? studyBuddySummary,
    bool? studyBuddySummaryLoading,
    List<StudyBuddyChatMessage>? studyBuddyChatMessages,
    bool? studyBuddyChatLoading,
    Object? studyBuddyChatError = _sentinel,
    bool? isPostStudySurveySubmitting,
    bool? postStudySurveyCompleted,
    String? postStudySurveyMessage,
  }) {
    return RLWorkbenchState(
      sections: sections ?? this.sections,
      flashcards: flashcards ?? this.flashcards,
      currentSection: currentSection ?? this.currentSection,
      learner: identical(learner, _sentinel)
          ? this.learner
          : learner as LearnerProfile?,
      currentRole: currentRole ?? this.currentRole,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
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
      studySessionId: studySessionId ?? this.studySessionId,
      code: code ?? this.code,
      workspaceSessionId: identical(workspaceSessionId, _sentinel)
          ? this.workspaceSessionId
          : workspaceSessionId as String?,
      editorShellUrl: identical(editorShellUrl, _sentinel)
          ? this.editorShellUrl
          : editorShellUrl as String?,
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
      traceEpisodes: traceEpisodes ?? this.traceEpisodes,
      episodeSummaries: episodeSummaries ?? this.episodeSummaries,
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
      staffStudents: staffStudents ?? this.staffStudents,
      selectedProgressStudentId: identical(selectedProgressStudentId, _sentinel)
          ? this.selectedProgressStudentId
          : selectedProgressStudentId as String?,
      selectedProgressDashboard: identical(selectedProgressDashboard, _sentinel)
          ? this.selectedProgressDashboard
          : selectedProgressDashboard as LearnerDashboard?,
      isProgressDashboardLoading:
          isProgressDashboardLoading ?? this.isProgressDashboardLoading,
      studyBuddyIntervention: identical(studyBuddyIntervention, _sentinel)
          ? this.studyBuddyIntervention
          : studyBuddyIntervention as StudyBuddyIntervention?,
      studyBuddyLoading: studyBuddyLoading ?? this.studyBuddyLoading,
      studyBuddyPanelDismissed:
          studyBuddyPanelDismissed ?? this.studyBuddyPanelDismissed,
      studyBuddySummary: studyBuddySummary ?? this.studyBuddySummary,
      studyBuddySummaryLoading:
          studyBuddySummaryLoading ?? this.studyBuddySummaryLoading,
      studyBuddyChatMessages:
          studyBuddyChatMessages ?? this.studyBuddyChatMessages,
      studyBuddyChatLoading:
          studyBuddyChatLoading ?? this.studyBuddyChatLoading,
      studyBuddyChatError: identical(studyBuddyChatError, _sentinel)
          ? this.studyBuddyChatError
          : studyBuddyChatError as String?,
      isPostStudySurveySubmitting:
          isPostStudySurveySubmitting ?? this.isPostStudySurveySubmitting,
      postStudySurveyCompleted:
          postStudySurveyCompleted ?? this.postStudySurveyCompleted,
      postStudySurveyMessage:
          postStudySurveyMessage ?? this.postStudySurveyMessage,
    );
  }

  bool get canAccessAuthoring =>
      isAuthenticated &&
      (currentRole == 'instructor' || currentRole == 'admin');

  bool get isAdmin => isAuthenticated && currentRole == 'admin';

  bool get isPrivileged => canAccessAuthoring;
}

/// Coordinates learner actions across auth, lesson selection, execution,
/// workspace sync, quizzes, and admin editing.
class RLWorkbenchCubit extends Cubit<RLWorkbenchState> {
  RLWorkbenchCubit({
    BackendApi? api,
    bool autoStartTelemetry = true,
  })  : _api = api ?? HttpBackendApi(),
        super(RLWorkbenchState.initial()) {
    _telemetry = LearningTelemetryClient(
      api: _api,
      autoStart: autoStartTelemetry,
    );
    unawaited(loadBackendLessonCatalog());
  }

  final BackendApi _api;
  late final LearningTelemetryClient _telemetry;
  String? _activeTaskId;
  String? _activeWorkspaceRunId;
  Timer? _studyBuddyPollTimer;
  int _studyBuddyPollAttempts = 0;

  BackendApi get api => _api;

  Future<void> loadBackendLessonCatalog() async {
    final authoredSections = await _loadAuthoredLessonSections();
    if (authoredSections.isNotEmpty) {
      final sectionsWithAuthored =
          _mergeNonCoreLessons(state.sections, authoredSections);
      final selectedLesson =
          _findLessonById(sectionsWithAuthored, state.selectedLesson.id) ??
              sectionsWithAuthored.first.lessons.first;
      emit(
        state.copyWith(
          sections: sectionsWithAuthored,
          selectedLesson: selectedLesson,
          code: state.code == state.selectedLesson.starterCode
              ? selectedLesson.starterCode
              : state.code,
          adminSelectedLessonId: selectedLesson.id,
          adminMessage: 'Loaded locally saved authored lessons.',
        ),
      );
    }

    try {
      final backendSections = await _api.fetchLessonSections();
      if (backendSections.isEmpty ||
          backendSections.every((section) => section.lessons.isEmpty)) {
        return;
      }

      final mergedSections =
          _mergeNonCoreLessons(backendSections, state.sections);

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
              ? 'Lessons are ready. Sign in to save quiz results and lesson progress.'
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

  Future<void> loadCloudAuthoredLessons() async {
    if (!state.canAccessAuthoring) {
      return;
    }
    try {
      final lessons = await _api.fetchAuthoredLessons();
      if (lessons.isEmpty) {
        return;
      }
      var updatedSections = state.sections;
      for (final lesson in lessons) {
        if (!_isCoreLessonId(lesson.id)) {
          updatedSections = _upsertLessonInSections(updatedSections, lesson);
        }
      }
      final selectedLesson =
          _findLessonById(updatedSections, state.selectedLesson.id) ??
              state.selectedLesson;
      emit(
        state.copyWith(
          sections: updatedSections,
          selectedLesson: selectedLesson,
          code: state.code == state.selectedLesson.starterCode
              ? selectedLesson.starterCode
              : state.code,
          adminMessage: 'Loaded cloud-authored lessons.',
        ),
      );
      unawaited(_persistAuthoredLessonSections(updatedSections));
    } on BackendApiException catch (error) {
      emit(state.copyWith(adminMessage: error.message));
    } catch (_) {
      emit(
        state.copyWith(adminMessage: 'Could not load cloud-authored lessons.'),
      );
    }
  }

  void _retainFallbackLessonCatalog() {
    if (state.learner != null) {
      return;
    }
    emit(
      state.copyWith(
        homeMessage:
            'Lesson sync is unavailable. Local practice content is ready.',
      ),
    );
  }

  void navigateTo(AppSection section) {
    if (section == AppSection.admin && !state.canAccessAuthoring) {
      emit(
        state.copyWith(
          currentSection: AppSection.home,
          homeMessage:
              'Authoring is available to instructor and admin roles only.',
        ),
      );
      return;
    }
    emit(state.copyWith(currentSection: section));
    if (section == AppSection.admin && state.canAccessAuthoring) {
      unawaited(loadStaffProgressDirectory());
    }
  }

  void toggleSidebar() {
    emit(state.copyWith(sidebarVisible: !state.sidebarVisible));
  }

  Future<void> signIn(String displayName, String password) async {
    final normalizedEmail = displayName.trim();
    if (normalizedEmail.isEmpty) {
      emit(
        state.copyWith(
          homeMessage: 'Enter your email address to continue.',
        ),
      );
      return;
    }
    if (password.trim().isEmpty) {
      emit(state.copyWith(homeMessage: 'Enter your password to continue.'));
      return;
    }

    emit(state.copyWith(
      isSigningIn: true,
      homeMessage: 'Signing in $normalizedEmail...',
    ));

    try {
      await _signInWithOptionalFirebase(
        normalizedEmail: normalizedEmail,
        password: password,
      );
    } on BackendApiException catch (error) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: error.message,
      ));
    } on FirebaseAuthException catch (error) {
      emit(
        state.copyWith(
          isSigningIn: false,
          homeMessage: _firebaseAuthMessage(error),
        ),
      );
    } catch (_) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: 'Connection unavailable. Try again shortly.',
      ));
    }
  }

  Future<void> signUp(String email, String password) async {
    final normalizedEmail = email.trim();
    if (normalizedEmail.isEmpty) {
      emit(
        state.copyWith(
          homeMessage: 'Enter your email address to create an account.',
        ),
      );
      return;
    }
    if (password.trim().length < 8) {
      emit(
        state.copyWith(
          homeMessage: 'Use a password with at least 8 characters.',
        ),
      );
      return;
    }

    emit(state.copyWith(
      isSigningIn: true,
      homeMessage: 'Creating account for $normalizedEmail...',
    ));

    try {
      String? firebaseIdToken;
      if (kIsWeb) {
        final credential =
            await FirebaseAuth.instance.createUserWithEmailAndPassword(
          email: normalizedEmail,
          password: password,
        );
        firebaseIdToken = await credential.user?.getIdToken(true);
      }

      final dashboard = await _api.signIn(
        displayName: normalizedEmail,
        password: password,
        firebaseIdToken: firebaseIdToken,
      );
      _applyAuthenticatedSession(
        dashboard,
        successMessage: 'Account ready for ${dashboard.student.displayName}.',
      );
    } on BackendApiException catch (error) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: error.message,
      ));
    } on FirebaseAuthException catch (error) {
      emit(
        state.copyWith(
          isSigningIn: false,
          homeMessage: _firebaseAuthMessage(error),
        ),
      );
    } catch (_) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: 'Connection unavailable. Try again shortly.',
      ));
    }
  }

  Future<void> signInWithGoogle() async {
    if (kIsWeb && !_canUseGoogleSignInOnCurrentOrigin()) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage:
            'Google sign-in will be available after secure publishing.',
      ));
      return;
    }

    emit(state.copyWith(
      isSigningIn: true,
      homeMessage: 'Opening Google sign-in...',
    ));

    try {
      String? firebaseIdToken;
      var displayName = 'Google User';
      if (kIsWeb) {
        if (!_canUseGoogleSignInOnCurrentOrigin()) {
          throw FirebaseAuthException(
            code: 'google-requires-secure-origin',
          );
        }
        final provider = GoogleAuthProvider()
          ..setCustomParameters({'prompt': 'select_account'});
        final credential =
            await FirebaseAuth.instance.signInWithPopup(provider);
        firebaseIdToken = await credential.user?.getIdToken(true);
        displayName = credential.user?.displayName ??
            credential.user?.email ??
            displayName;
      }

      final dashboard = await _api.signIn(
        displayName: displayName,
        password: '__firebase_google__',
        firebaseIdToken: firebaseIdToken,
      );
      _applyAuthenticatedSession(
        dashboard,
        successMessage: 'Signed in as ${dashboard.student.displayName}.',
      );
    } on BackendApiException catch (error) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: error.message,
      ));
    } on FirebaseAuthException catch (error) {
      emit(
        state.copyWith(
          isSigningIn: false,
          homeMessage: _firebaseAuthMessage(error),
        ),
      );
    } catch (_) {
      emit(state.copyWith(
        isSigningIn: false,
        homeMessage: 'Google sign-in failed. Try again.',
      ));
    }
  }

  void signOut() {
    unawaited(_api.signOut());
    _api.clearAuthToken();
    _activeTaskId = null;
    _activeWorkspaceRunId = null;
    try {
      FirebaseAuth.instance.signOut().ignore();
    } catch (_) {}
    emit(
      state.copyWith(
        learner: null,
        currentRole: 'guest',
        isAuthenticated: false,
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
        editorShellUrl: null,
        workspaceReady: false,
        editorConnectionStatus: WorkspaceConnectionStatus.disconnected,
        consoleConnectionStatus: WorkspaceConnectionStatus.disconnected,
        activeRunId: null,
        runOutputBuffer: '',
        scriptVersion: 1,
        studySessionId: _newStudySessionId(),
        staffStudents: const [],
        selectedProgressStudentId: null,
        selectedProgressDashboard: null,
        isProgressDashboardLoading: false,
        studyBuddyIntervention: null,
        studyBuddyLoading: false,
        studyBuddyPanelDismissed: false,
        studyBuddySummary: const StudyBuddySummary.empty(),
        studyBuddySummaryLoading: false,
        studyBuddyChatMessages: const [],
        studyBuddyChatLoading: false,
        studyBuddyChatError: null,
        isPostStudySurveySubmitting: false,
        postStudySurveyCompleted: false,
        postStudySurveyMessage:
            'Complete the post-study survey to record workload and usability.',
      ),
    );
  }

  String _firebaseAuthMessage(FirebaseAuthException error) {
    switch (error.code) {
      case 'invalid-email':
        return 'Enter a valid email address.';
      case 'email-already-in-use':
        return 'An account already exists for that email.';
      case 'user-disabled':
        return 'This account has been disabled.';
      case 'user-not-found':
      case 'wrong-password':
      case 'invalid-credential':
        return 'Invalid email or password.';
      case 'weak-password':
        return 'Use a stronger password.';
      case 'popup-closed-by-user':
        return 'Google sign-in was cancelled.';
      case 'google-requires-secure-origin':
        return 'Google sign-in requires HTTPS publishing.';
      case 'too-many-requests':
        return 'Too many attempts. Try again later.';
      default:
        return 'Sign-in failed. Check your credentials and try again.';
    }
  }

  Future<void> _signInWithOptionalFirebase({
    required String normalizedEmail,
    required String password,
  }) async {
    String? firebaseIdToken;
    if (kIsWeb) {
      try {
        final credential =
            await FirebaseAuth.instance.signInWithEmailAndPassword(
          email: normalizedEmail,
          password: password,
        );
        firebaseIdToken = await credential.user?.getIdToken(true);
      } on FirebaseAuthException catch (error) {
        if (!_shouldFallBackToBackendSignIn(error)) {
          rethrow;
        }
      }
    }

    final dashboard = await _api.signIn(
      displayName: normalizedEmail,
      password: password,
      firebaseIdToken: firebaseIdToken,
    );
    _applyAuthenticatedSession(
      dashboard,
      successMessage: 'Signed in as ${dashboard.student.displayName}.',
    );
  }

  bool _shouldFallBackToBackendSignIn(FirebaseAuthException error) {
    return error.code == 'user-not-found' ||
        error.code == 'wrong-password' ||
        error.code == 'invalid-credential';
  }

  Future<void> refreshDashboard({bool quiet = false}) async {
    final learner = state.learner;
    if (learner == null) {
      return;
    }

    try {
      final dashboard = await _api.getDashboard();
      final nextState = quiet
          ? state.copyWith(
              learner: dashboard.student,
              currentRole: dashboard.student.platformRole,
              progress: dashboard.progress,
              quizStatusMessage: _quizPromptForProgress(dashboard.progress),
            )
          : state.copyWith(
              learner: dashboard.student,
              currentRole: dashboard.student.platformRole,
              progress: dashboard.progress,
              homeMessage: 'Progress updated.',
              quizStatusMessage: _quizPromptForProgress(dashboard.progress),
            );
      emit(nextState);
      unawaited(refreshStudyBuddySummary(quiet: true));
    } on BackendApiException catch (error) {
      if (!quiet) {
        emit(state.copyWith(homeMessage: error.message));
      }
    }
  }

  Future<void> loadStaffProgressDirectory({bool quiet = true}) async {
    if (!state.canAccessAuthoring) {
      return;
    }
    if (!quiet) {
      emit(
        state.copyWith(
          isProgressDashboardLoading: true,
          adminMessage: 'Loading learner progress directory...',
        ),
      );
    }

    try {
      final students = await _api.fetchStaffStudents();
      final selectedStudentId = _resolveSelectedStaffStudentId(students);
      emit(
        state.copyWith(
          staffStudents: students,
          selectedProgressStudentId: selectedStudentId,
        ),
      );

      if (selectedStudentId == null) {
        emit(
          state.copyWith(
            selectedProgressDashboard: null,
            isProgressDashboardLoading: false,
            adminMessage: 'No student progress records are available yet.',
          ),
        );
        return;
      }

      await selectProgressStudent(selectedStudentId, quiet: quiet);
    } on BackendApiException catch (error) {
      emit(
        state.copyWith(
          isProgressDashboardLoading: false,
          adminMessage: error.message,
        ),
      );
    }
  }

  Future<void> selectProgressStudent(
    String studentId, {
    bool quiet = false,
  }) async {
    if (!state.canAccessAuthoring || studentId.isEmpty) {
      return;
    }

    emit(
      state.copyWith(
        selectedProgressStudentId: studentId,
        isProgressDashboardLoading: true,
        adminMessage:
            quiet ? state.adminMessage : 'Loading learner progress...',
      ),
    );

    try {
      final dashboard = await _api.fetchStaffStudentDashboard(studentId);
      emit(
        state.copyWith(
          selectedProgressDashboard: dashboard,
          isProgressDashboardLoading: false,
          adminMessage: quiet
              ? state.adminMessage
              : 'Loaded progress for ${dashboard.student.displayName}.',
        ),
      );
    } on BackendApiException catch (error) {
      emit(
        state.copyWith(
          selectedProgressDashboard: null,
          isProgressDashboardLoading: false,
          adminMessage: error.message,
        ),
      );
    }
  }

  Future<void> refreshStudyBuddySummary({bool quiet = false}) async {
    final learner = state.learner;
    if (learner == null) {
      return;
    }

    if (!quiet) {
      emit(state.copyWith(studyBuddySummaryLoading: true));
    }

    try {
      final summary = await _api.fetchStudyBuddySummary();
      if (summary == null) {
        emit(state.copyWith(studyBuddySummaryLoading: false));
        return;
      }
      emit(
        state.copyWith(
          studyBuddySummary: summary,
          studyBuddySummaryLoading: false,
        ),
      );
    } catch (_) {
      emit(state.copyWith(studyBuddySummaryLoading: false));
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
        studySessionId:
            preserveWorkspace ? state.studySessionId : _newStudySessionId(),
        code: preserveWorkspace ? state.code : lesson.starterCode,
        currentSection: AppSection.workspace,
        workspaceSessionId: preserveWorkspace ? state.workspaceSessionId : null,
        editorShellUrl: preserveWorkspace ? state.editorShellUrl : null,
        workspaceReady: preserveWorkspace ? state.workspaceReady : false,
        editorConnectionStatus: preserveWorkspace
            ? state.editorConnectionStatus
            : state.isAuthenticated && lesson.backendEnabled
                ? WorkspaceConnectionStatus.connecting
                : WorkspaceConnectionStatus.disconnected,
        consoleConnectionStatus: preserveWorkspace
            ? state.consoleConnectionStatus
            : state.isAuthenticated && lesson.backendEnabled
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
        traceEpisodes: const [],
        episodeSummaries: const [],
        failureKind: null,
        unresolvedBlanks: const [],
        studentFeedback: null,
        studyBuddyIntervention: null,
        studyBuddyLoading: false,
        studyBuddyPanelDismissed: false,
        studyBuddyChatMessages: const [],
        studyBuddyChatLoading: false,
        studyBuddyChatError: null,
        isPostStudySurveySubmitting: false,
        postStudySurveyCompleted:
            preserveWorkspace ? state.postStudySurveyCompleted : false,
        postStudySurveyMessage: preserveWorkspace
            ? state.postStudySurveyMessage
            : 'Complete the post-study survey to record workload and usability.',
        statusMessage: preserveWorkspace
            ? state.statusMessage
            : !state.isAuthenticated
                ? 'Sign in to open the live workspace for ${lesson.title}.'
                : lesson.backendEnabled
                    ? 'Ready to run ${lesson.title}.'
                    : '${lesson.title} is draft-only.',
      ),
    );
    if (lesson.backendEnabled && state.isAuthenticated && !preserveWorkspace) {
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
        isPostStudySurveySubmitting: phase == QuizPhase.posttest
            ? false
            : state.isPostStudySurveySubmitting,
        postStudySurveyCompleted: phase == QuizPhase.posttest
            ? false
            : state.postStudySurveyCompleted,
        postStudySurveyMessage: phase == QuizPhase.posttest
            ? 'Complete the post-study survey to record workload and usability.'
            : state.postStudySurveyMessage,
        quizStatusMessage:
            'Preparing ${quizPhaseLabel(phase).toLowerCase()}...',
      ),
    );

    try {
      final session = await _api.startQuiz(
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
          quizStatusMessage: 'Could not start quiz. Try again shortly.',
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
          quizStatusMessage: 'Could not submit quiz. Try again shortly.',
        ),
      );
    }
  }

  Future<void> submitPostStudySurvey({
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
    if (state.learner == null || state.postStudySurveyCompleted) {
      return;
    }

    emit(
      state.copyWith(
        isPostStudySurveySubmitting: true,
        postStudySurveyMessage: 'Submitting post-study survey...',
      ),
    );

    try {
      final result = await _api.submitStudySessionSurvey(
        studySessionId: state.studySessionId,
        condition: 'adaptive',
        susResponses: susResponses,
        tlxMentalDemand: tlxMentalDemand,
        tlxPhysicalDemand: tlxPhysicalDemand,
        tlxTemporalDemand: tlxTemporalDemand,
        tlxPerformance: tlxPerformance,
        tlxEffort: tlxEffort,
        tlxFrustration: tlxFrustration,
        feedbackHelpful: feedbackHelpful,
        feedbackConfusing: feedbackConfusing,
        feedbackImprovement: feedbackImprovement,
      );
      emit(
        state.copyWith(
          isPostStudySurveySubmitting: false,
          postStudySurveyCompleted: true,
          postStudySurveyMessage:
              'Survey recorded. SUS ${result.susScore.toStringAsFixed(1)}, '
              'TLX ${result.tlxOverall.toStringAsFixed(1)}.',
        ),
      );
    } on BackendApiException catch (error) {
      emit(
        state.copyWith(
          isPostStudySurveySubmitting: false,
          postStudySurveyMessage: error.message,
        ),
      );
    } catch (_) {
      emit(
        state.copyWith(
          isPostStudySurveySubmitting: false,
          postStudySurveyMessage:
              'Could not submit the survey. Try again shortly.',
        ),
      );
    }
  }

  Future<void> run() async {
    await runWorkspace();
  }

  void recordConceptVideoSession(Map<String, dynamic> payload) {
    _recordTelemetry('concept_video_session', payload, flushAfter: true);
  }

  void recordWorkspaceFocusSession(String viewId, Duration duration) {
    if (duration.inMilliseconds <= 0) {
      return;
    }
    _recordTelemetry(
      'workspace_focus_session',
      {
        'view_id': viewId,
        'duration_seconds': duration.inMilliseconds / 1000,
      },
      flushAfter: true,
    );
  }

  Future<void> refreshStudyBuddy() async {
    await _pollStudyBuddyPending();
  }

  Future<void> sendStudyBuddyChat(String message) async {
    final trimmed = message.trim();
    if (trimmed.isEmpty) {
      return;
    }
    if (state.learner == null) {
      emit(
        state.copyWith(
          studyBuddyChatError: 'Sign in to ask Study Buddy.',
        ),
      );
      return;
    }
    if (state.studyBuddyChatLoading) {
      return;
    }

    final history = state.studyBuddyChatMessages;
    final userMessage = StudyBuddyChatMessage(
      role: 'user',
      content: trimmed,
    );
    emit(
      state.copyWith(
        studyBuddyChatMessages: [...history, userMessage],
        studyBuddyChatLoading: true,
        studyBuddyChatError: null,
        studyBuddyPanelDismissed: false,
      ),
    );

    try {
      final currentCode = await _latestSubmissionCode();
      final response = await _api.sendStudyBuddyChat(
        lessonId: state.selectedLesson.id,
        sessionId: state.studySessionId,
        message: trimmed,
        history: history.length <= 12
            ? history
            : history.sublist(history.length - 12),
        currentCode: currentCode,
        unresolvedBlanks: state.unresolvedBlanks,
        failureKind: state.failureKind,
        latestFeedback: _feedbackPayload(state.studentFeedback),
      );
      if (isClosed) {
        return;
      }
      emit(
        state.copyWith(
          studyBuddyChatMessages: [
            ...state.studyBuddyChatMessages,
            response.message,
          ],
          studyBuddyChatLoading: false,
          studyBuddyChatError: null,
        ),
      );
    } on BackendApiException catch (error) {
      emit(
        state.copyWith(
          studyBuddyChatLoading: false,
          studyBuddyChatError: error.message,
        ),
      );
    } catch (_) {
      emit(
        state.copyWith(
          studyBuddyChatLoading: false,
          studyBuddyChatError: 'Study Buddy could not reply. Try again.',
        ),
      );
    }
  }

  Future<void> dismissStudyBuddy() async {
    final intervention = state.studyBuddyIntervention;
    emit(
      state.copyWith(
        studyBuddyPanelDismissed: true,
        studyBuddyLoading: false,
      ),
    );
    if (intervention != null) {
      _recordTelemetry(
        'study_buddy_intervention_response',
        {
          'intervention_id': intervention.id,
          'response': 'dismissed',
          'trigger_type': intervention.triggerType,
          'intervention_type': intervention.interventionType,
        },
        flushAfter: true,
      );
      try {
        await _api.respondToStudyBuddyIntervention(
          interventionId: intervention.id,
          response: 'dismissed',
        );
      } catch (_) {}
      unawaited(refreshStudyBuddySummary(quiet: true));
    }
  }

  Future<void> completeStudyBuddy() async {
    final intervention = state.studyBuddyIntervention;
    if (intervention == null) {
      return;
    }
    try {
      _recordTelemetry(
        'study_buddy_intervention_response',
        {
          'intervention_id': intervention.id,
          'response': 'completed',
          'trigger_type': intervention.triggerType,
          'intervention_type': intervention.interventionType,
        },
        flushAfter: true,
      );
      await _api.respondToStudyBuddyIntervention(
        interventionId: intervention.id,
        response: 'completed',
      );
    } catch (_) {}
    emit(
      state.copyWith(
        studyBuddyIntervention: null,
        studyBuddyLoading: false,
        studyBuddyPanelDismissed: false,
      ),
    );
    unawaited(refreshStudyBuddySummary(quiet: true));
  }

  void reopenStudyBuddy() {
    emit(state.copyWith(studyBuddyPanelDismissed: false));
  }

  Future<void> runWorkspace() async {
    final sessionId = await _ensureWorkspaceSession();
    if (sessionId == null) {
      emit(
        state.copyWith(
          statusMessage: state.isAuthenticated
              ? 'Workspace runtime is not ready for this lesson.'
              : 'Sign in to open the live workspace for this lesson.',
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
      _recordTelemetry(
        'code_run_result',
        {
          'passed': false,
          'failure_kind': 'workspace_start_failed',
          'message': error.message,
        },
        flushAfter: true,
      );
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
      _recordTelemetry(
        'code_run_result',
        {
          'passed': false,
          'failure_kind': 'workspace_unavailable',
        },
        flushAfter: true,
      );
      emit(
        state.copyWith(
          activeRunId: null,
          statusMessage: 'Workspace runtime unavailable. Try again shortly.',
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
        ),
      );
    }
  }

  Future<void> refreshWorkspaceConnection() async {
    if (!state.isAuthenticated) {
      emit(
        state.copyWith(
          workspaceSessionId: null,
          editorShellUrl: null,
          workspaceReady: false,
          editorConnectionStatus: WorkspaceConnectionStatus.disconnected,
          consoleConnectionStatus: WorkspaceConnectionStatus.disconnected,
          statusMessage: 'Sign in to refresh the live workspace connection.',
        ),
      );
      return;
    }

    if (!state.selectedLesson.backendEnabled) {
      emit(
        state.copyWith(
          statusMessage:
              '${state.selectedLesson.title} does not use a live workspace.',
        ),
      );
      return;
    }

    final sessionId = state.workspaceSessionId;
    emit(
      state.copyWith(
        editorConnectionStatus: WorkspaceConnectionStatus.connecting,
        consoleConnectionStatus: WorkspaceConnectionStatus.connecting,
        statusMessage: 'Refreshing workspace connection...',
      ),
    );

    if (sessionId == null) {
      await _attachWorkspaceSession(state.selectedLesson);
      return;
    }

    try {
      final file = await _api.getWorkspaceFile(sessionId: sessionId);
      final editorShellUrl = await _api.workspaceEditorShellUrl(sessionId);
      if (isClosed || state.workspaceSessionId != sessionId) {
        return;
      }
      emit(
        state.copyWith(
          code: file.content,
          editorShellUrl: editorShellUrl,
          workspaceReady: true,
          editorConnectionStatus: WorkspaceConnectionStatus.ready,
          consoleConnectionStatus: WorkspaceConnectionStatus.ready,
          scriptVersion: file.version,
          statusMessage: 'Workspace connection refreshed.',
        ),
      );
    } on BackendApiException {
      await _attachWorkspaceSession(state.selectedLesson);
    } catch (_) {
      if (isClosed || state.workspaceSessionId != sessionId) {
        return;
      }
      emit(
        state.copyWith(
          editorShellUrl: null,
          workspaceReady: false,
          editorConnectionStatus: WorkspaceConnectionStatus.failed,
          consoleConnectionStatus: WorkspaceConnectionStatus.failed,
          statusMessage:
              'Workspace connection could not be refreshed. Try again shortly.',
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

    if (!state.isAuthenticated) {
      emit(
        state.copyWith(
          currentSection: AppSection.home,
          runStatus: RunStatus.failed,
          statusMessage:
              'Sign in before using the live workspace or submitting code.',
          homeMessage:
              'Sign in before using the live workspace or submitting code.',
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
        traceEpisodes: const [],
        episodeSummaries: const [],
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
        sessionId: state.studySessionId,
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
      _recordTelemetry(
        'submission_result',
        {
          'passed': false,
          'failure_kind': error.failureKind ?? 'submission_request_failed',
          'message': error.message,
          'origin': 'frontend_submit',
        },
        flushAfter: true,
      );
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
          traceEpisodes: const [],
          episodeSummaries: const [],
          failureKind: error.failureKind,
          unresolvedBlanks: error.unresolvedBlanks,
          studentFeedback: error.studentFeedback,
          statusMessage: error.message,
        ),
      );
    } catch (_) {
      _activeTaskId = null;
      _recordTelemetry(
        'submission_result',
        {
          'passed': false,
          'failure_kind': 'backend_unavailable',
          'origin': 'frontend_submit',
        },
        flushAfter: true,
      );
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
          traceEpisodes: const [],
          episodeSummaries: const [],
          failureKind: null,
          unresolvedBlanks: const [],
          studentFeedback: null,
          statusMessage: 'Connection unavailable. Try again shortly.',
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
        traceEpisodes: const [],
        episodeSummaries: const [],
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
    if (!state.canAccessAuthoring) {
      return;
    }
    emit(
      state.copyWith(
        currentSection: AppSection.admin,
        adminSelectedLessonId: lessonId,
      ),
    );
  }

  void createDraftLesson() {
    if (!state.canAccessAuthoring) {
      emit(state.copyWith(
          adminMessage: 'Authoring requires instructor or admin access.'));
      return;
    }
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
        adminMessage: 'Draft lesson created and saved locally.',
      ),
    );
    unawaited(_persistAuthoredLessonSections(sections));
    unawaited(_syncAuthoredLessonToCloud(draftLesson));
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
    if (!state.canAccessAuthoring) {
      emit(state.copyWith(
          adminMessage: 'Authoring requires instructor or admin access.'));
      return;
    }
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
        adminMessage: 'Saved "${updatedLesson.title}" locally.',
      ),
    );
    unawaited(_persistAuthoredLessonSections(updatedSections));
    unawaited(_syncAuthoredLessonToCloud(updatedLesson));
  }

  void deleteAdminLesson(String lessonId) {
    if (!state.canAccessAuthoring) {
      emit(state.copyWith(
          adminMessage: 'Authoring requires instructor or admin access.'));
      return;
    }
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
        adminMessage: 'Deleted lesson $lessonId from local authoring.',
      ),
    );
    unawaited(_persistAuthoredLessonSections(updatedSections));
    unawaited(_deleteAuthoredLessonFromCloud(lessonId));
  }

  Future<void> uploadLectureNotes({
    required String lessonId,
    required List<int> bytes,
    required String filename,
  }) async {
    if (!state.canAccessAuthoring) {
      throw Exception('Authoring requires instructor or admin access.');
    }
    await _api.uploadLectureNotes(
      lessonId: lessonId,
      bytes: bytes,
      filename: filename,
    );
    // Reload sections so the notes-present chip updates.
    unawaited(loadBackendLessonCatalog());
  }

  Future<void> deleteLectureNotes(String lessonId) async {
    if (!state.canAccessAuthoring) {
      throw Exception('Authoring requires instructor or admin access.');
    }
    await _api.deleteLectureNotes(lessonId);
    // Reload sections so the notes-present chip updates.
    unawaited(loadBackendLessonCatalog());
  }

  Future<void> exportAdminNGainMetrics() async {
    if (!state.isAdmin) {
      emit(state.copyWith(
          adminMessage: 'Only admin users can export evaluation data.'));
      return;
    }
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
          adminMessage: 'Could not export metrics. Try again shortly.',
        ),
      );
    }
  }

  Future<void> exportAdminLearningAnalytics() async {
    if (!state.isAdmin) {
      emit(state.copyWith(
          adminMessage: 'Only admin users can export learning analytics.'));
      return;
    }
    emit(
      state.copyWith(
        isAdminExporting: true,
        adminMessage: 'Exporting Study Buddy learning analytics...',
      ),
    );

    try {
      final export = await _api.exportLearningAnalytics();
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
          adminMessage:
              'Could not export learning analytics. Try again shortly.',
        ),
      );
    }
  }

  Future<void> exportAdminALEIComponents() async {
    if (!state.isAdmin) {
      emit(state.copyWith(
          adminMessage: 'Only admin users can export evaluation data.'));
      return;
    }
    emit(
      state.copyWith(
        isAdminExporting: true,
        adminMessage: 'Exporting ALEI component metrics...',
      ),
    );
    try {
      final export = await _api.exportALEIComponents();
      await saveExportFile(
        fileName: export.fileName,
        bytes: export.bytes,
      );
      if (!isClosed) {
        emit(
          state.copyWith(
            isAdminExporting: false,
            adminMessage: 'ALEI component metrics exported.',
          ),
        );
      }
    } on BackendApiException catch (error) {
      if (!isClosed) {
        emit(
          state.copyWith(
            isAdminExporting: false,
            adminMessage: error.message,
          ),
        );
      }
    } catch (_) {
      if (!isClosed) {
        emit(
          state.copyWith(
            isAdminExporting: false,
            adminMessage: 'Could not export ALEI metrics. Try again shortly.',
          ),
        );
      }
    }
  }

  Future<String?> _ensureWorkspaceSession() async {
    if (!state.isAuthenticated) {
      return null;
    }

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
    if (!state.isAuthenticated) {
      emit(
        state.copyWith(
          workspaceSessionId: null,
          editorShellUrl: null,
          workspaceReady: false,
          editorConnectionStatus: WorkspaceConnectionStatus.disconnected,
          consoleConnectionStatus: WorkspaceConnectionStatus.disconnected,
          statusMessage:
              'Sign in to open the live workspace for ${lesson.title}.',
        ),
      );
      return;
    }

    final requestedLessonId = lesson.id;
    final showProgress =
        announceStatus || state.currentSection == AppSection.workspace;
    emit(
      state.copyWith(
        editorShellUrl: null,
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
      String? editorShellUrl;
      var editorConnectionStatus = WorkspaceConnectionStatus.ready;
      try {
        editorShellUrl = await _api.workspaceEditorShellUrl(session.sessionId);
      } on BackendApiException {
        editorConnectionStatus = WorkspaceConnectionStatus.failed;
      }
      if (isClosed || state.selectedLesson.id != requestedLessonId) {
        return;
      }

      emit(
        state.copyWith(
          code: file.content,
          workspaceSessionId: session.sessionId,
          editorShellUrl: editorShellUrl,
          workspaceReady: true,
          editorConnectionStatus: editorConnectionStatus,
          consoleConnectionStatus: session.consoleReady
              ? WorkspaceConnectionStatus.ready
              : WorkspaceConnectionStatus.connecting,
          scriptVersion: file.version,
          statusMessage: showProgress
              ? editorConnectionStatus == WorkspaceConnectionStatus.ready
                  ? 'Workspace ready for ${lesson.title}.'
                  : 'Workspace session ready, but the embedded editor could not be loaded.'
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
          editorShellUrl: null,
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
          editorShellUrl: null,
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

  void _applyAuthenticatedSession(
    LearnerDashboard dashboard, {
    required String successMessage,
  }) {
    final shouldAnnounceWorkspace =
        state.currentSection == AppSection.workspace;
    emit(
      state.copyWith(
        learner: dashboard.student,
        currentRole: dashboard.student.platformRole,
        isAuthenticated: true,
        progress: dashboard.progress,
        isSigningIn: false,
        homeMessage: successMessage,
        quizStatusMessage: _quizPromptForProgress(dashboard.progress),
        currentSection: AppSection.home,
      ),
    );
    if (state.selectedLesson.backendEnabled) {
      unawaited(
        _attachWorkspaceSession(
          state.selectedLesson,
          announceStatus: shouldAnnounceWorkspace,
        ),
      );
    }
    if (state.canAccessAuthoring) {
      unawaited(loadCloudAuthoredLessons());
      unawaited(loadStaffProgressDirectory());
    }
    unawaited(refreshStudyBuddySummary(quiet: true));
  }

  String? _resolveSelectedStaffStudentId(List<StaffStudentSummary> students) {
    if (students.isEmpty) {
      return null;
    }
    final current = state.selectedProgressStudentId;
    if (current != null && students.any((student) => student.id == current)) {
      return current;
    }
    return students.first.id;
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
      traceEpisodes: const [],
      episodeSummaries: const [],
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
              'Task completed without returning a result.',
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
              traceEpisodes: result.traceEpisodes,
              episodeSummaries: result.episodeSummaries,
              failureKind: null,
              unresolvedBlanks: const [],
              studentFeedback: null,
              statusMessage: result.visualizationReady
                  ? '${result.message} Replay ready.'
                  : '${result.message} No replay video generated.',
            ),
          );
          _recordTelemetry(
            'submission_result',
            {
              'passed': true,
              'task_id': taskId,
              'test_count': result.testResults.length,
              'origin': 'frontend_submit',
            },
            flushAfter: true,
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
              traceEpisodes: const [],
              episodeSummaries: const [],
              failureKind: snapshot.failureKind,
              unresolvedBlanks: snapshot.unresolvedBlanks,
              studentFeedback: snapshot.studentFeedback,
              statusMessage: snapshot.errorMessage ?? 'Execution task failed.',
            ),
          );
          _recordTelemetry(
            'submission_result',
            {
              'passed': false,
              'task_id': taskId,
              'failure_kind': snapshot.failureKind,
              'origin': 'frontend_submit',
            },
            flushAfter: true,
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
        _recordTelemetry(
          'code_run_result',
          {
            'passed': snapshot.exitCode == 0,
            'run_id': runId,
            'exit_code': snapshot.exitCode,
          },
          flushAfter: true,
        );
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

  List<LessonSection> _mergeNonCoreLessons(
    List<LessonSection> baseSections,
    List<LessonSection> authoredSections,
  ) {
    var mergedSections = baseSections;
    for (final section in authoredSections) {
      for (final lesson in section.lessons) {
        if (!_isCoreLessonId(lesson.id)) {
          mergedSections = _upsertLessonInSections(mergedSections, lesson);
        }
      }
    }
    return mergedSections;
  }

  Future<List<LessonSection>> _loadAuthoredLessonSections() async {
    try {
      final preferences = await SharedPreferences.getInstance();
      final rawValue = preferences.getString(_authoredLessonsPrefsKey);
      if (rawValue == null || rawValue.isEmpty) {
        return const [];
      }
      final decoded = jsonDecode(rawValue);
      if (decoded is! List) {
        return const [];
      }
      return decoded
          .whereType<Map<String, dynamic>>()
          .map(LessonSection.fromJson)
          .toList(growable: false);
    } catch (_) {
      return const [];
    }
  }

  Future<void> _syncAuthoredLessonToCloud(LessonDefinition lesson) async {
    if (!state.canAccessAuthoring || _isCoreLessonId(lesson.id)) {
      return;
    }
    try {
      final savedLesson = await _api.saveAuthoredLesson(lesson: lesson);
      final updatedSections =
          _upsertLessonInSections(state.sections, savedLesson);
      if (!isClosed) {
        emit(
          state.copyWith(
            sections: updatedSections,
            adminMessage: 'Saved "${savedLesson.title}" to cloud authoring.',
          ),
        );
      }
      unawaited(_persistAuthoredLessonSections(updatedSections));
    } on BackendApiException catch (error) {
      if (!isClosed) {
        emit(state.copyWith(adminMessage: error.message));
      }
    } catch (_) {
      if (!isClosed) {
        emit(
          state.copyWith(
            adminMessage: 'Saved locally, but cloud authoring sync failed.',
          ),
        );
      }
    }
  }

  Future<void> _deleteAuthoredLessonFromCloud(String lessonId) async {
    if (!state.canAccessAuthoring || _isCoreLessonId(lessonId)) {
      return;
    }
    try {
      await _api.deleteAuthoredLesson(lessonId);
    } on BackendApiException catch (error) {
      if (!isClosed && error.message.contains('not found') == false) {
        emit(state.copyWith(adminMessage: error.message));
      }
    } catch (_) {
      if (!isClosed) {
        emit(
          state.copyWith(
            adminMessage: 'Deleted locally, but cloud authoring sync failed.',
          ),
        );
      }
    }
  }

  Future<void> _persistAuthoredLessonSections(
    List<LessonSection> sections,
  ) async {
    final authoredSections = <LessonSection>[];
    for (final section in sections) {
      final authoredLessons = section.lessons
          .where((lesson) => !_isCoreLessonId(lesson.id))
          .toList(growable: false);
      if (authoredLessons.isNotEmpty) {
        authoredSections.add(
          LessonSection(title: section.title, lessons: authoredLessons),
        );
      }
    }

    try {
      final preferences = await SharedPreferences.getInstance();
      if (authoredSections.isEmpty) {
        await preferences.remove(_authoredLessonsPrefsKey);
        return;
      }
      await preferences.setString(
        _authoredLessonsPrefsKey,
        jsonEncode(
            authoredSections.map((section) => section.toJson()).toList()),
      );
    } catch (_) {
      if (!isClosed) {
        emit(state.copyWith(
          adminMessage: 'Could not save authored lessons locally.',
        ));
      }
    }
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

  void _recordTelemetry(
    String eventType,
    Map<String, dynamic> payload, {
    bool flushAfter = false,
  }) {
    final learner = state.learner;
    if (learner == null) {
      return;
    }

    _telemetry.record(
      LearningTelemetryEvent(
        lessonId: state.selectedLesson.id,
        conceptId: state.selectedLesson.id,
        sessionId: state.studySessionId,
        eventType: eventType,
        occurredAtUtc: DateTime.now().toUtc(),
        payloadJson: payload,
      ),
    );
    if (flushAfter) {
      unawaited(_telemetry.flush());
      _scheduleStudyBuddyPolling();
    }
  }

  void _scheduleStudyBuddyPolling() {
    if (state.studyBuddyIntervention != null) {
      return;
    }
    _studyBuddyPollTimer?.cancel();
    _studyBuddyPollAttempts = 0;
    emit(
      state.copyWith(
        studyBuddyLoading: true,
        studyBuddyPanelDismissed: false,
      ),
    );
    _studyBuddyPollTimer = Timer.periodic(
      const Duration(seconds: 3),
      (timer) {
        _studyBuddyPollAttempts += 1;
        unawaited(_pollStudyBuddyPending());
        if (_studyBuddyPollAttempts >= 4) {
          timer.cancel();
          if (state.studyBuddyIntervention == null) {
            emit(state.copyWith(studyBuddyLoading: false));
          }
        }
      },
    );
    unawaited(_pollStudyBuddyPending());
  }

  Future<void> _pollStudyBuddyPending() async {
    if (state.learner == null) {
      return;
    }
    try {
      final intervention = await _api.fetchPendingStudyBuddyIntervention(
        sessionId: state.studySessionId,
      );
      if (intervention == null) {
        return;
      }
      _studyBuddyPollTimer?.cancel();
      emit(
        state.copyWith(
          studyBuddyIntervention: intervention,
          studyBuddyLoading: false,
          studyBuddyPanelDismissed: false,
        ),
      );
    } catch (_) {
      if (_studyBuddyPollAttempts >= 4) {
        emit(state.copyWith(studyBuddyLoading: false));
      }
    }
  }

  @override
  Future<void> close() async {
    _studyBuddyPollTimer?.cancel();
    await _telemetry.dispose();
    return super.close();
  }
}

String _newStudySessionId() {
  return 'study-${DateTime.now().microsecondsSinceEpoch}';
}

Map<String, dynamic> _feedbackPayload(ExecutionStudentFeedback? feedback) {
  if (feedback == null) {
    return const {};
  }
  return {
    'status': feedback.status,
    'summary': feedback.summary,
    'likely_issue': feedback.likelyIssue,
    'affected_blank_ids': feedback.affectedBlankIds,
    'next_steps': feedback.nextSteps,
    'hint_level': feedback.hintLevel,
  };
}
