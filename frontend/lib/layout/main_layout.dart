import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../core/constants.dart';
import '../core/onboarding_prefs.dart';
import '../core/theme.dart';
import '../core/workbench_state.dart';
import '../features/admin/admin_console.dart';
import '../features/home/home_dashboard.dart';
import '../features/lessons/lesson_browser.dart';
import '../features/onboarding/onboarding_tutorial.dart';
import '../features/quiz/quiz_section.dart';
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
            appBar: _buildAppBar(state),
            body: _buildCurrentSection(state),
          );
        },
      ),
    );
  }

  Widget _buildCurrentSection(RLWorkbenchState state) {
    switch (state.currentSection) {
      case AppSection.home:
        return HomeDashboard(
          learner: state.learner,
          progress: state.progress,
          sections: state.sections,
          flashcards: state.flashcards,
          isSigningIn: state.isSigningIn,
          message: state.homeMessage,
          onSignIn: _cubit.signIn,
          onOpenLesson: _cubit.openLesson,
          onOpenQuiz: () => _cubit.navigateTo(AppSection.quiz),
        );
      case AppSection.workspace:
        return LayoutBuilder(
          builder: (context, constraints) {
            final lessonBrowser = LessonBrowser(
              sections: state.sections,
              selectedLesson: state.selectedLesson,
              onLessonSelected: _cubit.selectLesson,
              onToggleVisibility: _cubit.toggleSidebar,
            );
            final workspace = WorkspaceTabs(
              lesson: state.selectedLesson,
              code: state.code,
              onCodeChanged: _cubit.updateCode,
              onRun: _cubit.run,
              onStop: _cubit.stop,
              onReset: _cubit.reset,
              statusMessage: state.statusMessage,
              runStatusLabel: state.runStatusLabel,
              totalReward: state.totalReward,
              averageReward: state.averageReward,
              bestEpisodeReward: state.bestEpisodeReward,
              episodesCompleted: state.currentEpisode,
              stepsRecorded: state.currentStep,
              videoPath: state.videoPath,
              testResults: state.testResults,
              stepTrace: state.stepTrace,
            );

            if (constraints.maxWidth < 1100) {
              return Column(
                children: [
                  if (state.sidebarVisible)
                    SizedBox(
                      height: 320,
                      child: lessonBrowser,
                    )
                  else
                    _CollapsedOutlineRail(onTap: _cubit.toggleSidebar),
                  Expanded(child: workspace),
                ],
              );
            }

            return Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (state.sidebarVisible) ...[
                  SizedBox(
                    width: AppConstants.leftPanelWidth,
                    child: lessonBrowser,
                  ),
                  const VerticalDivider(),
                ] else
                  _CollapsedOutlineRail(onTap: _cubit.toggleSidebar),
                Expanded(child: workspace),
              ],
            );
          },
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
        return AdminConsole(
          sections: state.sections,
          selectedLessonId: state.adminSelectedLessonId,
          message: state.adminMessage,
          isExportingMetrics: state.isAdminExporting,
          onSelectLesson: _cubit.selectAdminLesson,
          onCreateDraftLesson: _cubit.createDraftLesson,
          onDeleteLesson: _cubit.deleteAdminLesson,
          onExportNGainMetrics: _cubit.exportAdminNGainMetrics,
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
    );

    if (markSeen) {
      await OnboardingPrefs.markOnboardingSeen();
    }
    if (mounted) {
      _onboardingShown = false;
    }
  }

  PreferredSizeWidget _buildAppBar(RLWorkbenchState state) {
    return AppBar(
      backgroundColor: AppTheme.surfaceWhite,
      elevation: 0,
      title: const Row(
        children: [
          Icon(Icons.school_outlined, color: AppTheme.textPrimary),
          SizedBox(width: 12),
          Text(
            'RL Learning Platform',
            style: TextStyle(
              color: AppTheme.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
      actions: [
        IconButton(
          tooltip: 'Show onboarding tutorial',
          onPressed: () => _openOnboarding(markSeen: false),
          icon: const Icon(Icons.lightbulb_outline_rounded),
        ),
        const SizedBox(width: 4),
        if (state.currentSection == AppSection.workspace)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: OutlinedButton.icon(
              onPressed: _cubit.toggleSidebar,
              icon: Icon(
                state.sidebarVisible
                    ? Icons.menu_open_rounded
                    : Icons.menu_rounded,
              ),
              label: Text(
                state.sidebarVisible ? 'Hide Sidebar' : 'Show Sidebar',
              ),
            ),
          ),
        const SizedBox(width: 12),
      ],
      bottom: PreferredSize(
        preferredSize: const Size.fromHeight(64),
        child: Column(
          children: [
            SizedBox(
              height: 56,
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
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
                      selected: state.currentSection == AppSection.workspace,
                      onTap: () => _cubit.navigateTo(AppSection.workspace),
                    ),
                    const SizedBox(width: 8),
                    _NavChip(
                      label: 'Quiz',
                      selected: state.currentSection == AppSection.quiz,
                      onTap: () => _cubit.navigateTo(AppSection.quiz),
                    ),
                    const SizedBox(width: 8),
                    _NavChip(
                      label: 'Admin',
                      selected: state.currentSection == AppSection.admin,
                      onTap: () => _cubit.navigateTo(AppSection.admin),
                    ),
                    if (state.learner != null) ...[
                      const SizedBox(width: 16),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 14,
                          vertical: 10,
                        ),
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
                              size: 18,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              state.learner!.displayName,
                              style: const TextStyle(
                                color: AppTheme.primaryBlue,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const Divider(height: 1),
          ],
        ),
      ),
    );
  }
}

class _CollapsedOutlineRail extends StatelessWidget {
  final VoidCallback onTap;

  const _CollapsedOutlineRail({
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 56,
      decoration: const BoxDecoration(
        color: AppTheme.surfaceWhite,
        border: Border(
          right: BorderSide(color: AppTheme.borderLight),
        ),
      ),
      child: Column(
        children: [
          const SizedBox(height: 20),
          IconButton(
            tooltip: 'Show lesson sidebar',
            onPressed: onTap,
            icon: const Icon(Icons.menu_open_rounded),
          ),
          const SizedBox(height: 8),
          RotatedBox(
            quarterTurns: 3,
            child: Text(
              'Course Outline',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}

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
