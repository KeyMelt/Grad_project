import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../core/brand_mark.dart';
import '../core/constants.dart';
import '../core/onboarding_prefs.dart';
import '../core/theme.dart';
import '../core/workbench_state.dart';
import '../features/admin/admin_console.dart';
import '../features/flashcards/flashcards_section.dart';
import '../features/home/home_dashboard.dart';
import '../features/lessons/lesson_browser.dart';
import '../features/onboarding/onboarding_tutorial.dart';
import '../features/quiz/quiz_section.dart';
import '../features/study_buddy/study_buddy_panel.dart';
import '../features/workspace/workspace_tabs.dart';

class MainLayout extends StatefulWidget {
  final RLWorkbenchCubit? cubit;
  final bool showOnboardingOnStart;
  final bool isDarkMode;
  final VoidCallback? onToggleThemeMode;

  const MainLayout({
    super.key,
    this.cubit,
    this.showOnboardingOnStart = false,
    this.isDarkMode = false,
    this.onToggleThemeMode,
  });

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  late final RLWorkbenchCubit _cubit;
  bool _onboardingShown = false;
  bool _studyBuddyDrawerOpen = false;

  @override
  void initState() {
    super.initState();
    _cubit = widget.cubit ?? RLWorkbenchCubit();
    if (widget.showOnboardingOnStart) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _openOnboarding(markSeen: true);
      });
    }
  }

  @override
  void dispose() {
    if (widget.cubit == null) {
      _cubit.close();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: _cubit,
      child: BlocBuilder<RLWorkbenchCubit, RLWorkbenchState>(
        builder: (context, state) {
          return Scaffold(
            appBar: _buildAppBar(context, state),
            body: _buildCurrentSection(context, state),
          );
        },
      ),
    );
  }

  Widget _buildCurrentSection(BuildContext context, RLWorkbenchState state) {
    switch (state.currentSection) {
      case AppSection.home:
        return HomeDashboard(
          learner: state.learner,
          progress: state.progress,
          studyBuddySummary: state.studyBuddySummary,
          isStudyBuddySummaryLoading: state.studyBuddySummaryLoading,
          sections: state.sections,
          isSigningIn: state.isSigningIn,
          canAccessAuthoring: state.canAccessAuthoring,
          message: state.homeMessage,
          onSignIn: _cubit.signIn,
          onSignUp: _cubit.signUp,
          onSignInWithGoogle: _cubit.signInWithGoogle,
          onOpenLesson: _cubit.openLesson,
          onOpenQuiz: () => _cubit.navigateTo(AppSection.quiz),
          onOpenFlashcards: () => _cubit.navigateTo(AppSection.flashcards),
          onOpenAuthoring: () => _cubit.navigateTo(AppSection.admin),
          onSignOut: _cubit.signOut,
        );
      case AppSection.workspace:
        return LayoutBuilder(
          builder: (context, constraints) {
            final workspace = WorkspaceTabs(
              lesson: state.selectedLesson,
              code: state.code,
              workspaceSessionId: state.workspaceSessionId,
              workspaceReady: state.workspaceReady,
              editorConnectionStatus: state.editorConnectionStatus,
              consoleConnectionStatus: state.consoleConnectionStatus,
              editorShellUrl: state.editorShellUrl,
              scriptVersion: state.scriptVersion,
              onSubmit: () => _cubit.submit(),
              onStop: _cubit.stop,
              onReset: _cubit.reset,
              onReconnectWorkspace: _cubit.refreshWorkspaceConnection,
              statusMessage: state.statusMessage,
              runStatusLabel: state.runStatusLabel,
              failureKind: state.failureKind,
              unresolvedBlanks: state.unresolvedBlanks,
              studentFeedback: state.studentFeedback,
              feedbackDismissed: state.workspaceFeedbackDismissed,
              totalReward: state.totalReward,
              averageReward: state.averageReward,
              bestEpisodeReward: state.bestEpisodeReward,
              episodesCompleted: state.currentEpisode,
              stepsRecorded: state.currentStep,
              videoPath: state.videoPath,
              testResults: state.testResults,
              stepTrace: state.stepTrace,
              traceEpisodes: state.traceEpisodes,
              episodeSummaries: state.episodeSummaries,
              onConceptVideoSession: _cubit.recordConceptVideoSession,
              onWorkspaceFocusSession: _cubit.recordWorkspaceFocusSession,
              onDismissFeedback: _cubit.dismissWorkspaceFeedback,
              showExerciseBriefInCodePane: true,
            );

            final studyBuddyPanel = StudyBuddyPanel(
              lesson: state.selectedLesson,
              intervention: state.studyBuddyIntervention,
              isLoading: state.studyBuddyLoading,
              isDismissed: state.studyBuddyPanelDismissed,
              chatMessages: state.studyBuddyChatMessages,
              isChatLoading: state.studyBuddyChatLoading,
              chatError: state.studyBuddyChatError,
              onDismiss: () => _cubit.dismissStudyBuddy(),
              onComplete: () => _cubit.completeStudyBuddy(),
              onReopen: _cubit.reopenStudyBuddy,
              onRefresh: () => _cubit.refreshStudyBuddy(),
              onSendChatMessage: _cubit.sendStudyBuddyChat,
            );

            return Padding(
              padding: const EdgeInsets.fromLTRB(8, 6, 8, 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Expanded(child: workspace),
                  _StudyBuddyDrawer(
                    isOpen: _studyBuddyDrawerOpen,
                    drawerWidth: _studyBuddyRailWidth(constraints.maxWidth),
                    hasIntervention: state.studyBuddyIntervention != null,
                    onToggle: () => _setStudyBuddyDrawerOpen(
                      !_studyBuddyDrawerOpen,
                    ),
                    onOpen: () => _setStudyBuddyDrawerOpen(true),
                    onClose: () => _setStudyBuddyDrawerOpen(false),
                    panel: studyBuddyPanel,
                  ),
                ],
              ),
            );
          },
        );
      case AppSection.flashcards:
        return FlashcardsSection(
          flashcards: state.flashcards,
          onBackHome: () => _cubit.navigateTo(AppSection.home),
        );
      case AppSection.quiz:
        return QuizSection(
          learner: state.learner,
          progress: state.progress,
          activeQuiz: state.activeQuiz,
          quizAnswers: state.quizAnswers,
          lastQuizSummary: state.lastQuizSummary,
          isLoading: state.isQuizLoading,
          isPostStudySurveySubmitting: state.isPostStudySurveySubmitting,
          postStudySurveyCompleted: state.postStudySurveyCompleted,
          postStudySurveyMessage: state.postStudySurveyMessage,
          statusMessage: state.quizStatusMessage,
          onStartQuiz: _cubit.startQuiz,
          onAnswerQuestion: _cubit.answerQuizQuestion,
          onSubmitQuiz: _cubit.submitQuiz,
          onSubmitPostStudySurvey: _cubit.submitPostStudySurvey,
        );
      case AppSection.admin:
        if (!state.canAccessAuthoring) {
          return HomeDashboard(
            learner: state.learner,
            progress: state.progress,
            studyBuddySummary: state.studyBuddySummary,
            isStudyBuddySummaryLoading: state.studyBuddySummaryLoading,
            sections: state.sections,
            isSigningIn: state.isSigningIn,
            canAccessAuthoring: state.canAccessAuthoring,
            message:
                'Authoring is available to instructor and admin roles only.',
            onSignIn: _cubit.signIn,
            onSignUp: _cubit.signUp,
            onSignInWithGoogle: _cubit.signInWithGoogle,
            onOpenLesson: _cubit.openLesson,
            onOpenQuiz: () => _cubit.navigateTo(AppSection.quiz),
            onOpenFlashcards: () => _cubit.navigateTo(AppSection.flashcards),
            onOpenAuthoring: () => _cubit.navigateTo(AppSection.admin),
            onSignOut: _cubit.signOut,
          );
        }
        return AdminConsole(
          sections: state.sections,
          selectedLessonId: state.adminSelectedLessonId,
          progressDashboard: state.selectedProgressDashboard,
          students: state.staffStudents,
          selectedStudentId: state.selectedProgressStudentId,
          message: state.adminMessage,
          isExportingMetrics: state.isAdminExporting,
          isProgressLoading: state.isProgressDashboardLoading,
          isAdmin: state.isAdmin,
          onSelectLesson: _cubit.selectAdminLesson,
          onSelectStudent: (studentId) =>
              _cubit.selectProgressStudent(studentId),
          onRefreshProgressDirectory: () =>
              _cubit.loadStaffProgressDirectory(quiet: false),
          onCreateDraftLesson: _cubit.createDraftLesson,
          onDeleteLesson: _cubit.deleteAdminLesson,
          onExportNGainMetrics: _cubit.exportAdminNGainMetrics,
          onExportLearningAnalytics: _cubit.exportAdminLearningAnalytics,
          onExportALEIComponents: _cubit.exportAdminALEIComponents,
          onSaveLesson: _cubit.saveAdminLesson,
          onUploadLectureNotes: _cubit.uploadLectureNotes,
          onDeleteLectureNotes: _cubit.deleteLectureNotes,
        );
    }
  }

  void _setStudyBuddyDrawerOpen(bool isOpen) {
    if (_studyBuddyDrawerOpen == isOpen) {
      return;
    }
    setState(() {
      _studyBuddyDrawerOpen = isOpen;
    });
  }

  Future<void> _openOnboarding({required bool markSeen}) async {
    if (!mounted || _onboardingShown) {
      return;
    }

    _onboardingShown = true;
    await showOnboardingTutorial(
      context,
      onNavigate: _cubit.navigateTo,
      role: _cubit.state.currentRole,
    );

    if (markSeen) {
      await OnboardingPrefs.markOnboardingSeen();
    }
    if (mounted) {
      _onboardingShown = false;
    }
  }

  PreferredSizeWidget _buildAppBar(
      BuildContext context, RLWorkbenchState state) {
    final isWorkspace = state.currentSection == AppSection.workspace;

    // Build course outline launcher bottom bar for workspace mode.
    PreferredSizeWidget? bottomBar;
    if (isWorkspace) {
      final orderedLessons = state.sections
          .expand((section) => section.lessons)
          .toList(growable: false);
      final currentLessonIndex = orderedLessons.indexWhere(
        (lesson) => lesson.id == state.selectedLesson.id,
      );
      final canGoPrevious = currentLessonIndex > 0;
      final canGoNext = currentLessonIndex >= 0 &&
          currentLessonIndex < orderedLessons.length - 1;

      bottomBar = PreferredSize(
        preferredSize: const Size.fromHeight(42),
        child: Container(
          decoration: const BoxDecoration(
            border: Border(
              bottom: BorderSide(color: AppTheme.borderLight),
            ),
          ),
          padding: const EdgeInsets.fromLTRB(10, 0, 10, 5),
          child: Center(
            child: CourseOutlineLauncher(
              selectedLesson: state.selectedLesson,
              canGoPrevious: canGoPrevious,
              canGoNext: canGoNext,
              onPrevious: canGoPrevious
                  ? () => _cubit
                      .selectLesson(orderedLessons[currentLessonIndex - 1])
                  : () {},
              onNext: canGoNext
                  ? () => _cubit
                      .selectLesson(orderedLessons[currentLessonIndex + 1])
                  : () {},
              onOpenOutline: () => showCourseOutlineDialog(
                context: context,
                sections: state.sections,
                selectedLesson: state.selectedLesson,
                onLessonSelected: _cubit.selectLesson,
              ),
            ),
          ),
        ),
      );
    }

    return AppBar(
      primary: false,
      elevation: 0,
      toolbarHeight: 56,
      bottom: bottomBar,
      title: LayoutBuilder(
        builder: (context, constraints) {
          final showLogo = constraints.maxWidth > 300;
          return Row(
            children: [
              if (showLogo) ...[
                // FIRST (RED): logo acts as home button in workspace mode.
                InkWell(
                  key: const ValueKey('home-logo-button'),
                  onTap: isWorkspace
                      ? () => _cubit.navigateTo(AppSection.home)
                      : null,
                  borderRadius: BorderRadius.circular(8),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(
                      minWidth: 34,
                      minHeight: 34,
                    ),
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: ReinfourceMark(
                        size: 30,
                        foreground:
                            Theme.of(context).brightness == Brightness.dark
                                ? AppTheme.light
                                : AppTheme.navy,
                        accent: AppTheme.primaryBlue,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
              ],
              // FIRST (RED): hide nav chips when inside workspace.
              if (!isWorkspace)
                Expanded(
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        _NavChip(
                          label: 'Home',
                          selected: state.currentSection == AppSection.home,
                          onTap: () => _cubit.navigateTo(AppSection.home),
                        ),
                        const SizedBox(width: 8),
                        _NavChip(
                          label: 'Workspace',
                          selected:
                              state.currentSection == AppSection.workspace,
                          onTap: () => _cubit.navigateTo(AppSection.workspace),
                        ),
                        const SizedBox(width: 8),
                        _NavChip(
                          label: 'Quiz',
                          selected: state.currentSection == AppSection.quiz,
                          onTap: () => _cubit.navigateTo(AppSection.quiz),
                        ),
                        const SizedBox(width: 8),
                        if (state.canAccessAuthoring)
                          _NavChip(
                            label: 'Authoring',
                            selected: state.currentSection == AppSection.admin,
                            onTap: () => _cubit.navigateTo(AppSection.admin),
                          ),
                      ],
                    ),
                  ),
                )
              else
                const Spacer(),
            ],
          );
        },
      ),
      actions: [
        if (state.learner == null) ...[
          TextButton(
            style: TextButton.styleFrom(
              visualDensity: VisualDensity.compact,
              padding: const EdgeInsets.symmetric(horizontal: 10),
            ),
            onPressed: state.isSigningIn
                ? null
                : () => _showAuthDialog(initialMode: _AuthMode.signIn),
            child: const Text('Sign in'),
          ),
          const SizedBox(width: 4),
          FilledButton(
            style: FilledButton.styleFrom(
              visualDensity: VisualDensity.compact,
              padding: const EdgeInsets.symmetric(horizontal: 14),
            ),
            onPressed: state.isSigningIn
                ? null
                : () => _showAuthDialog(initialMode: _AuthMode.signUp),
            child: const Text('Sign up'),
          ),
          const SizedBox(width: 6),
        ] else ...[
          Container(
            margin: const EdgeInsets.symmetric(vertical: 7),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: AppTheme.tealSurface,
              borderRadius: BorderRadius.circular(999),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.person_outline,
                  color: AppTheme.primaryBlue,
                  size: 16,
                ),
                const SizedBox(width: 6),
                Text(
                  state.learner!.displayName,
                  style: const TextStyle(
                    color: AppTheme.primaryBlue,
                    fontWeight: FontWeight.w700,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 6),
          IconButton(
            tooltip: 'Sign out',
            onPressed: _cubit.signOut,
            icon: const Icon(Icons.logout_rounded),
          ),
        ],
        const SizedBox(width: 6),
        IconButton(
          visualDensity: VisualDensity.compact,
          tooltip: widget.isDarkMode ? 'Use light mode' : 'Use dark mode',
          onPressed: widget.onToggleThemeMode,
          icon: Icon(
            widget.isDarkMode
                ? Icons.light_mode_outlined
                : Icons.dark_mode_outlined,
          ),
        ),
        const SizedBox(width: 2),
        IconButton(
          visualDensity: VisualDensity.compact,
          tooltip: 'Show onboarding tutorial',
          onPressed: () => _openOnboarding(markSeen: false),
          icon: const Icon(Icons.lightbulb_outline_rounded),
        ),
        const SizedBox(width: 10),
      ],
    );
  }

  Future<void> _showAuthDialog({required _AuthMode initialMode}) {
    _cubit.clearAuthMessage();
    return showDialog<void>(
      context: context,
      builder: (context) => _AuthDialog(
        cubit: _cubit,
        initialMode: initialMode,
        googleAvailable: true,
        onSignIn: _cubit.signIn,
        onSignUp: _cubit.signUp,
        onGoogle: _cubit.signInWithGoogle,
      ),
    );
  }
}

// ── Study Buddy drawer ────────────────────────────────────────────────────────

enum _AuthMode { signIn, signUp }

class _AuthDialog extends StatefulWidget {
  final RLWorkbenchCubit cubit;
  final _AuthMode initialMode;
  final bool googleAvailable;
  final void Function(String email, String password) onSignIn;
  final void Function(String email, String password) onSignUp;
  final VoidCallback onGoogle;

  const _AuthDialog({
    required this.cubit,
    required this.initialMode,
    required this.googleAvailable,
    required this.onSignIn,
    required this.onSignUp,
    required this.onGoogle,
  });

  @override
  State<_AuthDialog> createState() => _AuthDialogState();
}

class _AuthDialogState extends State<_AuthDialog> {
  late _AuthMode _mode;
  late final TextEditingController _emailController;
  late final TextEditingController _passwordController;

  @override
  void initState() {
    super.initState();
    _mode = widget.initialMode;
    _emailController = TextEditingController();
    _passwordController = TextEditingController();
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<RLWorkbenchCubit, RLWorkbenchState>(
      bloc: widget.cubit,
      listenWhen: (previous, current) =>
          !previous.isAuthenticated && current.isAuthenticated,
      listener: (context, state) {
        Navigator.of(context).pop();
      },
      builder: (context, state) {
        final isBusy = state.isSigningIn;
        final authMessage = state.authMessage.trim();
        return AlertDialog(
          title: Text(_mode == _AuthMode.signUp ? 'Create account' : 'Sign in'),
          content: SizedBox(
            width: 380,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: _AuthModeButton(
                        label: 'Sign in',
                        selected: _mode == _AuthMode.signIn,
                        onTap: isBusy
                            ? () {}
                            : () {
                                widget.cubit.clearAuthMessage();
                                setState(() => _mode = _AuthMode.signIn);
                              },
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _AuthModeButton(
                        label: 'Sign up',
                        selected: _mode == _AuthMode.signUp,
                        onTap: isBusy
                            ? () {}
                            : () {
                                widget.cubit.clearAuthMessage();
                                setState(() => _mode = _AuthMode.signUp);
                              },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                TextField(
                  controller: _emailController,
                  enabled: !isBusy,
                  keyboardType: TextInputType.emailAddress,
                  autofillHints: const [AutofillHints.email],
                  decoration: const InputDecoration(
                    labelText: 'Email address',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _passwordController,
                  enabled: !isBusy,
                  obscureText: true,
                  autofillHints: _mode == _AuthMode.signUp
                      ? const [AutofillHints.newPassword]
                      : const [AutofillHints.password],
                  decoration: InputDecoration(
                    labelText: _mode == _AuthMode.signUp
                        ? 'Create password'
                        : 'Password',
                    border: const OutlineInputBorder(),
                  ),
                  onSubmitted: (_) {
                    if (!isBusy) {
                      _submit();
                    }
                  },
                ),
                if (authMessage.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _AuthMessage(message: authMessage),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: isBusy ? null : () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            if (widget.googleAvailable)
              TextButton.icon(
                onPressed: isBusy
                    ? null
                    : () {
                        widget.cubit.clearAuthMessage();
                        widget.onGoogle();
                      },
                icon: const Icon(Icons.g_mobiledata_rounded),
                label: const Text('Google'),
              ),
            FilledButton(
              onPressed: isBusy ? null : _submit,
              child: isBusy
                  ? const SizedBox.square(
                      dimension: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(
                      _mode == _AuthMode.signUp ? 'Create account' : 'Sign in',
                    ),
            ),
          ],
        );
      },
    );
  }

  void _submit() {
    widget.cubit.clearAuthMessage();
    if (_mode == _AuthMode.signUp) {
      widget.onSignUp(_emailController.text, _passwordController.text);
    } else {
      widget.onSignIn(_emailController.text, _passwordController.text);
    }
  }
}

class _AuthMessage extends StatelessWidget {
  final String message;

  const _AuthMessage({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF7ED),
        border: Border.all(color: const Color(0xFFFDBA74)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(
            Icons.info_outline,
            size: 18,
            color: Color(0xFFC2410C),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                color: Color(0xFF7C2D12),
                fontSize: 13,
                height: 1.35,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _AuthModeButton extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _AuthModeButton({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 160),
        padding: const EdgeInsets.symmetric(vertical: 10),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: selected ? AppTheme.primaryBlue : AppTheme.tealSurface,
          borderRadius: BorderRadius.circular(10),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: selected ? Colors.white : AppTheme.primaryBlue,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}

class _StudyBuddyDrawer extends StatefulWidget {
  final bool isOpen;
  final double drawerWidth;
  final bool hasIntervention;
  final VoidCallback onToggle;
  final VoidCallback onOpen;
  final VoidCallback onClose;
  final Widget panel;

  const _StudyBuddyDrawer({
    required this.isOpen,
    required this.drawerWidth,
    required this.hasIntervention,
    required this.onToggle,
    required this.onOpen,
    required this.onClose,
    required this.panel,
  });

  @override
  State<_StudyBuddyDrawer> createState() => _StudyBuddyDrawerState();
}

class _StudyBuddyDrawerState extends State<_StudyBuddyDrawer>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulseController;
  double _dragDistance = 0;

  bool get _shouldPulse => widget.hasIntervention && !widget.isOpen;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1100),
    );
    _syncPulseAnimation();
  }

  @override
  void didUpdateWidget(covariant _StudyBuddyDrawer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.hasIntervention != widget.hasIntervention ||
        oldWidget.isOpen != widget.isOpen) {
      _syncPulseAnimation();
    }
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  void _syncPulseAnimation() {
    if (_shouldPulse) {
      if (!_pulseController.isAnimating) {
        _pulseController.repeat(reverse: true);
      }
      return;
    }
    _pulseController.stop();
    _pulseController.value = 0;
  }

  void _handleDragStart(DragStartDetails details) {
    _dragDistance = 0;
  }

  void _handleDragUpdate(DragUpdateDetails details) {
    _dragDistance += details.primaryDelta ?? details.delta.dx;
    if (widget.isOpen && _dragDistance > 32) {
      _dragDistance = 0;
      widget.onClose();
    } else if (!widget.isOpen && _dragDistance < -32) {
      _dragDistance = 0;
      widget.onOpen();
    }
  }

  void _handleDragEnd(DragEndDetails details) {
    final velocity =
        details.primaryVelocity ?? details.velocity.pixelsPerSecond.dx;
    if (velocity > 280 || _dragDistance > 32) {
      widget.onClose();
    } else if (velocity < -280 || _dragDistance < -32) {
      widget.onOpen();
    }
    _dragDistance = 0;
  }

  void _handleDragCancel() {
    _dragDistance = 0;
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Handle tab — clickable vertical strip on left edge of drawer.
        Semantics(
          button: true,
          toggled: widget.isOpen,
          label: widget.isOpen ? 'Close Study Buddy' : 'Open Study Buddy',
          child: Tooltip(
            message: widget.isOpen ? 'Close Study Buddy' : 'Open Study Buddy',
            child: MouseRegion(
              cursor: SystemMouseCursors.resizeLeftRight,
              child: GestureDetector(
                key: const ValueKey('study-buddy-drawer-handle'),
                behavior: HitTestBehavior.opaque,
                onTap: widget.onToggle,
                onHorizontalDragStart: _handleDragStart,
                onHorizontalDragUpdate: _handleDragUpdate,
                onHorizontalDragEnd: _handleDragEnd,
                onHorizontalDragCancel: _handleDragCancel,
                child: Container(
                  width: widget.isOpen ? 24 : 34,
                  decoration: BoxDecoration(
                    color: widget.isOpen
                        ? AppTheme.primaryBlue.withValues(alpha: 0.1)
                        : AppTheme.primaryBlue,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(14),
                      bottomLeft: Radius.circular(14),
                    ),
                    border: Border.all(
                      color: widget.isOpen
                          ? AppTheme.tealBorder
                          : AppTheme.primaryBlue,
                    ),
                    boxShadow: const [
                      BoxShadow(
                        color: Color(0x24000000),
                        blurRadius: 10,
                        offset: Offset(-3, 0),
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        widget.isOpen
                            ? Icons.chevron_right_rounded
                            : Icons.chevron_left_rounded,
                        size: widget.isOpen ? 18 : 24,
                        color:
                            widget.isOpen ? AppTheme.primaryBlue : Colors.white,
                      ),
                      if (!widget.isOpen) ...[
                        const SizedBox(height: 8),
                        RotatedBox(
                          quarterTurns: 3,
                          child: Text(
                            'Buddy',
                            style: Theme.of(context)
                                .textTheme
                                .labelSmall
                                ?.copyWith(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0,
                                ),
                          ),
                        ),
                      ],
                      // Pulsing intervention dot — visible only when closed and
                      // an intervention is available, so users know there's a cue.
                      if (_shouldPulse) ...[
                        const SizedBox(height: 10),
                        AnimatedBuilder(
                          animation: _pulseController,
                          builder: (context, _) {
                            final t = _pulseController.value;
                            return Container(
                              width: 8,
                              height: 8,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Color.lerp(
                                  AppTheme.primaryBlue,
                                  AppTheme.tealBorder,
                                  t,
                                ),
                                boxShadow: [
                                  BoxShadow(
                                    color: AppTheme.primaryBlue.withValues(
                                      alpha: 0.35 + 0.35 * t,
                                    ),
                                    blurRadius: 4 + 5 * t,
                                    spreadRadius: 1 + 2 * t,
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
        // Animated drawer panel — expands/collapses horizontally.
        AnimatedContainer(
          duration: const Duration(milliseconds: 280),
          curve: Curves.easeInOut,
          width: widget.isOpen ? widget.drawerWidth : 0,
          child: OverflowBox(
            maxWidth: widget.drawerWidth,
            minWidth: 0,
            alignment: Alignment.centerLeft,
            child: SizedBox(
              width: widget.drawerWidth,
              child: widget.panel,
            ),
          ),
        ),
      ],
    );
  }
}

// ── Nav chip ──────────────────────────────────────────────────────────────────

class _NavChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _NavChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return InkWell(
      borderRadius: BorderRadius.circular(999),
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: selected
              ? (isDark
                  ? AppTheme.primaryBlue.withValues(alpha: 0.18)
                  : AppTheme.tealSurface)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(999),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: selected ? AppTheme.primaryBlue : colorScheme.onSurface,
            fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
          ),
        ),
      ),
    );
  }
}

double _studyBuddyRailWidth(double maxWidth) {
  return (maxWidth * 0.28).clamp(320.0, AppConstants.rightPanelWidth);
}
