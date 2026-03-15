import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../core/theme.dart';
import '../core/workbench_state.dart';
import '../features/controls/parameters_panel.dart';
import '../features/controls/run_panel.dart';
import '../features/lessons/lesson_browser.dart';
import '../features/workspace/workspace_tabs.dart';

class MainLayout extends StatefulWidget {
  final RLWorkbenchController? controller;

  const MainLayout({super.key, this.controller});

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  late final RLWorkbenchController _controller;

  @override
  void initState() {
    super.initState();
    _controller = widget.controller ?? RLWorkbenchController();
  }

  @override
  void dispose() {
    if (widget.controller == null) {
      _controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        return Scaffold(
          appBar: _buildFigmaAppBar(),
          body: LayoutBuilder(
            builder: (context, constraints) {
              final lessonBrowser = LessonBrowser(
                sections: _controller.sections,
                selectedLesson: _controller.selectedLesson,
                onLessonSelected: _controller.selectLesson,
              );
              final workspace = WorkspaceTabs(
                lesson: _controller.selectedLesson,
                code: _controller.code,
                onCodeChanged: _controller.updateCode,
                statusMessage: _controller.statusMessage,
                runStatusLabel: _controller.runStatusLabel,
                totalReward: _controller.totalReward,
                averageReward: _controller.averageReward,
                bestEpisodeReward: _controller.bestEpisodeReward,
                episodesCompleted: _controller.currentEpisode,
                stepsRecorded: _controller.currentStep,
                videoPath: _controller.videoPath,
                testResults: _controller.testResults,
              );
              final controls = _buildControlsSection();

              if (constraints.maxWidth < 1200) {
                return SingleChildScrollView(
                  padding: const EdgeInsets.all(AppConstants.defaultPadding),
                  child: Column(
                    children: [
                      SizedBox(height: 360, child: lessonBrowser),
                      const SizedBox(height: AppConstants.defaultPadding),
                      controls,
                      const SizedBox(height: AppConstants.defaultPadding),
                      SizedBox(height: 520, child: workspace),
                    ],
                  ),
                );
              }

              return Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  SizedBox(
                    width: AppConstants.leftPanelWidth,
                    child: lessonBrowser,
                  ),
                  const VerticalDivider(),
                  Expanded(child: workspace),
                  const VerticalDivider(),
                  SizedBox(
                    width: AppConstants.rightPanelWidth,
                    child: SingleChildScrollView(
                      padding:
                          const EdgeInsets.all(AppConstants.defaultPadding),
                      child: controls,
                    ),
                  ),
                ],
              );
            },
          ),
        );
      },
    );
  }

  Widget _buildControlsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ParametersPanel(
          learningRate: _controller.learningRate,
          discountFactor: _controller.discountFactor,
          explorationRate: _controller.explorationRate,
          episodeCount: _controller.episodeCount,
          runMode: _controller.runMode,
          onLearningRateChanged: _controller.updateLearningRate,
          onDiscountFactorChanged: _controller.updateDiscountFactor,
          onExplorationRateChanged: _controller.updateExplorationRate,
          onEpisodeCountChanged: _controller.updateEpisodeCount,
          onRunModeChanged: _controller.updateRunMode,
        ),
        const SizedBox(height: AppConstants.defaultPadding),
        RunPanel(
          episodeCount: _controller.episodeCount,
          currentEpisode: _controller.currentEpisode,
          currentStep: _controller.currentStep,
          connectionLabel: _controller.connectionLabel,
          runStatusLabel: _controller.runStatusLabel,
          statusMessage: _controller.statusMessage,
          totalReward: _controller.totalReward,
          onRun: () {
            _controller.run();
          },
          onStop: _controller.stop,
          onReset: _controller.reset,
        ),
      ],
    );
  }

  PreferredSizeWidget _buildFigmaAppBar() {
    return AppBar(
      backgroundColor: AppTheme.surfaceWhite,
      title: Row(
        children: [
          const Icon(Icons.menu, color: AppTheme.textPrimary),
          const SizedBox(width: 16),
          const Text(
            'RL_IDE',
            style: TextStyle(
              color: AppTheme.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
          const Spacer(),
          IconButton(
            icon: const Icon(Icons.person_outline, color: AppTheme.textPrimary),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.play_arrow_outlined,
                color: AppTheme.textPrimary),
            onPressed: () {
              _controller.run();
            },
          ),
          ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
            child: const Text('Share'),
          ),
        ],
      ),
      elevation: 0,
      bottom: const PreferredSize(
        preferredSize: Size.fromHeight(1),
        child: Divider(height: 1),
      ),
    );
  }
}
