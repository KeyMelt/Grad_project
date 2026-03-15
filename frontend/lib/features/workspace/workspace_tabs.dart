import 'package:flutter/material.dart';
import '../../core/backend_api.dart';
import '../../core/workbench_state.dart';
import '../../core/theme.dart';
import 'code_editor.dart';
import 'video_player.dart';

class WorkspaceTabs extends StatelessWidget {
  final LessonDefinition lesson;
  final String code;
  final ValueChanged<String> onCodeChanged;
  final String statusMessage;
  final String runStatusLabel;
  final double totalReward;
  final double averageReward;
  final double bestEpisodeReward;
  final int episodesCompleted;
  final int stepsRecorded;
  final String videoPath;
  final List<ExecutionTestCaseResult> testResults;

  const WorkspaceTabs({
    super.key,
    required this.lesson,
    required this.code,
    required this.onCodeChanged,
    required this.statusMessage,
    required this.runStatusLabel,
    required this.totalReward,
    required this.averageReward,
    required this.bestEpisodeReward,
    required this.episodesCompleted,
    required this.stepsRecorded,
    required this.videoPath,
    required this.testResults,
  });

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          Container(
            color: AppTheme.surfaceWhite,
            child: const TabBar(
              indicatorColor: AppTheme.primaryBlue,
              labelColor: AppTheme.primaryBlue,
              unselectedLabelColor: AppTheme.textPrimary,
              tabs: [
                Tab(text: 'Video'),
                Tab(text: 'Code'),
              ],
            ),
          ),
          Expanded(
            child: TabBarView(
              children: [
                VideoPlayerTab(
                  lessonTitle: lesson.title,
                  runStatusLabel: runStatusLabel,
                  statusMessage: statusMessage,
                  totalReward: totalReward,
                  averageReward: averageReward,
                  bestEpisodeReward: bestEpisodeReward,
                  episodesCompleted: episodesCompleted,
                  stepsRecorded: stepsRecorded,
                  videoPath: videoPath,
                  testResults: testResults,
                ),
                CodeEditorTab(
                  lessonTitle: lesson.title,
                  code: code,
                  onChanged: onCodeChanged,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
