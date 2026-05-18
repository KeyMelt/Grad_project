import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

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

  const MainLayout({
    super.key,
    this.cubit,
    this.showOnboardingOnStart = false,
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
              onRun: _cubit.run,
              onReconnectWorkspace: _cubit.refreshWorkspaceConnection,
              statusMessage: state.statusMessage,
              runStatusLabel: state.runStatusLabel,
              failureKind: state.failureKind,
              unresolvedBlanks: state.unresolvedBlanks,
              studentFeedback: state.studentFeedback,
              totalReward: state.totalReward,
              averageReward: state.averageReward,
              bestEpisodeReward: state.bestEpisodeReward,
              episodesCompleted: state.currentEpisode,
              stepsRecorded: state.currentStep,
              videoPath: state.videoPath,
              testResults: state.testResults,
              stepTrace: state.stepTrace,
              onConceptVideoSession: _cubit.recordConceptVideoSession,
              onWorkspaceFocusSession: _cubit.recordWorkspaceFocusSession,
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

            // Wide layout: 50/50 exercise brief + workspace, Study Buddy drawer overlay.
            // Narrow: workspace fills full width (exercise brief lives inside code pane).
            final isWide = constraints.maxWidth >= 980;
            final mainContent = isWide
                ? Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // FORTH (GREEN): exercise brief, full height, 50% width.
                      Expanded(
                        child: StudyBuddyExerciseBrief(
                          lesson: state.selectedLesson,
                        ),
                      ),
                      const SizedBox(width: 12),
                      // SIXTH (PINK): code editor, 50% width.
                      Expanded(child: workspace),
                    ],
                  )
                : workspace;

            return Padding(
              padding: const EdgeInsets.fromLTRB(10, 10, 10, 10),
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  Positioned.fill(child: mainContent),
                  // FIFTH (PURPLE): Study Buddy sliding drawer from the right.
                  Positioned(
                    top: 0,
                    bottom: 0,
                    right: 0,
                    child: _StudyBuddyDrawer(
                      isOpen: _studyBuddyDrawerOpen,
                      drawerWidth:
                          _studyBuddyRailWidth(constraints.maxWidth),
                      hasIntervention:
                          state.studyBuddyIntervention != null,
                      onToggle: () => setState(() {
                        _studyBuddyDrawerOpen = !_studyBuddyDrawerOpen;
                      }),
                      panel: studyBuddyPanel,
                    ),
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
          statusMessage: state.quizStatusMessage,
          onStartQuiz: _cubit.startQuiz,
          onAnswerQuestion: _cubit.answerQuizQuestion,
          onSubmitQuiz: _cubit.submitQuiz,
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
          onSaveLesson: _cubit.saveAdminLesson,
        );
    }
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
        preferredSize: const Size.fromHeight(52),
        child: Container(
          decoration: const BoxDecoration(
            border: Border(
              bottom: BorderSide(color: Color(0xFFE5E7EB)),
            ),
          ),
          padding: const EdgeInsets.fromLTRB(10, 0, 10, 8),
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
      backgroundColor: AppTheme.surfaceWhite,
      elevation: 0,
      toolbarHeight: 58,
      bottom: bottomBar,
      title: LayoutBuilder(
        builder: (context, constraints) {
          final showLogo = constraints.maxWidth > 300;
          return Row(
            children: [
              if (showLogo) ...[
                // FIRST (RED): logo acts as home button in workspace mode.
                InkWell(
                  onTap: isWorkspace
                      ? () => _cubit.navigateTo(AppSection.home)
                      : null,
                  borderRadius: BorderRadius.circular(8),
                  child: Image.asset(
                    'assets/branding/rl_logo_trimmed.png',
                    height: 38,
                    fit: BoxFit.contain,
                  ),
                ),
                const SizedBox(width: 18),
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
                          selected:
                              state.currentSection == AppSection.home,
                          onTap: () => _cubit.navigateTo(AppSection.home),
                        ),
                        const SizedBox(width: 8),
                        _NavChip(
                          label: 'Workspace',
                          selected: state.currentSection ==
                              AppSection.workspace,
                          onTap: () =>
                              _cubit.navigateTo(AppSection.workspace),
                        ),
                        const SizedBox(width: 8),
                        _NavChip(
                          label: 'Quiz',
                          selected:
                              state.currentSection == AppSection.quiz,
                          onTap: () => _cubit.navigateTo(AppSection.quiz),
                        ),
                        const SizedBox(width: 8),
                        if (state.canAccessAuthoring)
                          _NavChip(
                            label: 'Authoring',
                            selected:
                                state.currentSection == AppSection.admin,
                            onTap: () =>
                                _cubit.navigateTo(AppSection.admin),
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
        if (state.learner != null)
          Container(
            margin: const EdgeInsets.symmetric(vertical: 10),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFFE8F0FE),
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
          tooltip: 'Show onboarding tutorial',
          onPressed: () => _openOnboarding(markSeen: false),
          icon: const Icon(Icons.lightbulb_outline_rounded),
        ),
        const SizedBox(width: 10),
      ],
    );
  }
}

// ── Study Buddy drawer ────────────────────────────────────────────────────────

class _StudyBuddyDrawer extends StatefulWidget {
  final bool isOpen;
  final double drawerWidth;
  final bool hasIntervention;
  final VoidCallback onToggle;
  final Widget panel;

  const _StudyBuddyDrawer({
    required this.isOpen,
    required this.drawerWidth,
    required this.hasIntervention,
    required this.onToggle,
    required this.panel,
  });

  @override
  State<_StudyBuddyDrawer> createState() => _StudyBuddyDrawerState();
}

class _StudyBuddyDrawerState extends State<_StudyBuddyDrawer>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1100),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Handle tab — clickable vertical strip on left edge of drawer.
        GestureDetector(
          onTap: widget.onToggle,
          child: Container(
            width: 22,
            decoration: BoxDecoration(
              color: AppTheme.surfaceWhite,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                bottomLeft: Radius.circular(12),
              ),
              border: Border.all(color: const Color(0xFFE5E7EB)),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x12000000),
                  blurRadius: 6,
                  offset: Offset(-2, 0),
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
                  size: 16,
                  color: const Color(0xFF6B7280),
                ),
                // Pulsing intervention dot — visible only when closed and an
                // intervention is available, so users know there's a cue.
                if (widget.hasIntervention && !widget.isOpen) ...[
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
                            const Color(0xFF93C5FD),
                            t,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: AppTheme.primaryBlue
                                  .withValues(alpha: 0.35 + 0.35 * t),
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
    return InkWell(
      borderRadius: BorderRadius.circular(999),
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFFE8F0FE) : Colors.transparent,
          borderRadius: BorderRadius.circular(999),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: selected ? AppTheme.primaryBlue : AppTheme.textPrimary,
            fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
          ),
        ),
      ),
    );
  }
}

double _studyBuddyRailWidth(double maxWidth) {
  return (maxWidth * 0.26).clamp(300.0, AppConstants.rightPanelWidth);
}
