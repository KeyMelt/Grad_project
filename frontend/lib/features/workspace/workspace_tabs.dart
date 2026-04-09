import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/workbench_state.dart';
import 'code_editor.dart';
import 'exercise_brief_panel.dart';
import 'trace_replay_panel.dart';
import 'video_player.dart';

class WorkspaceTabs extends StatelessWidget {
  final LessonDefinition lesson;
  final String code;
  final String? workspaceSessionId;
  final bool workspaceReady;
  final WorkspaceConnectionStatus editorConnectionStatus;
  final WorkspaceConnectionStatus consoleConnectionStatus;
  final String? editorShellUrl;
  final int scriptVersion;
  final VoidCallback onSubmit;
  final VoidCallback onStop;
  final VoidCallback onReset;
  final String statusMessage;
  final String runStatusLabel;
  final double totalReward;
  final double averageReward;
  final double bestEpisodeReward;
  final int episodesCompleted;
  final int stepsRecorded;
  final String videoPath;
  final List<ExecutionTestCaseResult> testResults;
  final List<ExecutionTraceStep> stepTrace;

  const WorkspaceTabs({
    super.key,
    required this.lesson,
    required this.code,
    required this.workspaceSessionId,
    required this.workspaceReady,
    required this.editorConnectionStatus,
    required this.consoleConnectionStatus,
    required this.editorShellUrl,
    required this.scriptVersion,
    required this.onSubmit,
    required this.onStop,
    required this.onReset,
    required this.statusMessage,
    required this.runStatusLabel,
    required this.totalReward,
    required this.averageReward,
    required this.bestEpisodeReward,
    required this.episodesCompleted,
    required this.stepsRecorded,
    required this.videoPath,
    required this.testResults,
    required this.stepTrace,
  });

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: const Color(0xFFE5E7EB)),
              ),
              child: const TabBar(
                indicatorColor: Color(0xFF1A73E8),
                labelColor: Color(0xFF1A73E8),
                unselectedLabelColor: Color(0xFF6B7280),
                tabs: [
                  Tab(text: 'Concept'),
                  Tab(text: 'Code'),
                  Tab(text: 'Replay'),
                ],
              ),
            ),
            const SizedBox(height: 12),
            _RunStatusStrip(
              runStatusLabel: runStatusLabel,
              statusMessage: statusMessage,
            ),
            const SizedBox(height: 10),
            Expanded(
              child: TabBarView(
                children: [
                  VideoPlayerTab(lesson: lesson),
                  _CodeExercisePane(
                    lesson: lesson,
                    code: code,
                    workspaceSessionId: workspaceSessionId,
                    workspaceReady: workspaceReady,
                    editorConnectionStatus: editorConnectionStatus,
                    consoleConnectionStatus: consoleConnectionStatus,
                    editorShellUrl: editorShellUrl,
                    scriptVersion: scriptVersion,
                    statusMessage: statusMessage,
                    runStatusLabel: runStatusLabel,
                    onSubmit: onSubmit,
                    onStop: onStop,
                    onReset: onReset,
                  ),
                  TraceReplayPanel(
                    runStatusLabel: runStatusLabel,
                    statusMessage: statusMessage,
                    totalReward: totalReward,
                    averageReward: averageReward,
                    bestEpisodeReward: bestEpisodeReward,
                    episodesCompleted: episodesCompleted,
                    stepsRecorded: stepsRecorded,
                    videoPath: videoPath,
                    testResults: testResults,
                    stepTrace: stepTrace,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RunStatusStrip extends StatelessWidget {
  final String runStatusLabel;
  final String statusMessage;

  const _RunStatusStrip({
    required this.runStatusLabel,
    required this.statusMessage,
  });

  @override
  Widget build(BuildContext context) {
    final style = _statusStyleFor(runStatusLabel);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: style.background,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: style.border),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            style.icon,
            color: style.foreground,
            size: 19,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              '$runStatusLabel: $statusMessage',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: style.foreground,
                    fontWeight: FontWeight.w600,
                    height: 1.4,
                  ),
            ),
          ),
        ],
      ),
    );
  }

  _RunStatusVisual _statusStyleFor(String status) {
    switch (status) {
      case 'Running':
        return const _RunStatusVisual(
          foreground: Color(0xFF1D4ED8),
          background: Color(0xFFEFF6FF),
          border: Color(0xFFBFDBFE),
          icon: Icons.autorenew_rounded,
        );
      case 'Complete':
        return const _RunStatusVisual(
          foreground: Color(0xFF047857),
          background: Color(0xFFECFDF5),
          border: Color(0xFFA7F3D0),
          icon: Icons.task_alt_rounded,
        );
      case 'Failed':
        return const _RunStatusVisual(
          foreground: Color(0xFFB91C1C),
          background: Color(0xFFFEF2F2),
          border: Color(0xFFFECACA),
          icon: Icons.error_outline_rounded,
        );
      case 'Stopped':
        return const _RunStatusVisual(
          foreground: Color(0xFF7C3AED),
          background: Color(0xFFF5F3FF),
          border: Color(0xFFDDD6FE),
          icon: Icons.stop_circle_outlined,
        );
      default:
        return const _RunStatusVisual(
          foreground: Color(0xFF334155),
          background: Color(0xFFF8FAFC),
          border: Color(0xFFE2E8F0),
          icon: Icons.hourglass_empty_rounded,
        );
    }
  }
}

class _RunStatusVisual {
  final Color foreground;
  final Color background;
  final Color border;
  final IconData icon;

  const _RunStatusVisual({
    required this.foreground,
    required this.background,
    required this.border,
    required this.icon,
  });
}

class _CodeExercisePane extends StatelessWidget {
  final LessonDefinition lesson;
  final String code;
  final String? workspaceSessionId;
  final bool workspaceReady;
  final WorkspaceConnectionStatus editorConnectionStatus;
  final WorkspaceConnectionStatus consoleConnectionStatus;
  final String? editorShellUrl;
  final int scriptVersion;
  final String statusMessage;
  final String runStatusLabel;
  final VoidCallback onSubmit;
  final VoidCallback onStop;
  final VoidCallback onReset;

  const _CodeExercisePane({
    required this.lesson,
    required this.code,
    required this.workspaceSessionId,
    required this.workspaceReady,
    required this.editorConnectionStatus,
    required this.consoleConnectionStatus,
    required this.editorShellUrl,
    required this.scriptVersion,
    required this.statusMessage,
    required this.runStatusLabel,
    required this.onSubmit,
    required this.onStop,
    required this.onReset,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 1100) {
          return Column(
            children: [
              SizedBox(
                height: 340,
                child: ExerciseBriefPanel(lesson: lesson),
              ),
              const SizedBox(height: 20),
              Expanded(
                child: CodeEditorTab(
                  lesson: lesson,
                  code: code,
                  workspaceSessionId: workspaceSessionId,
                  workspaceReady: workspaceReady,
                  editorConnectionStatus: editorConnectionStatus,
                  consoleConnectionStatus: consoleConnectionStatus,
                  editorShellUrl: editorShellUrl,
                  statusMessage: statusMessage,
                  runStatusLabel: runStatusLabel,
                  scriptVersion: scriptVersion,
                  onSubmit: onSubmit,
                  onStop: onStop,
                  onReset: onReset,
                ),
              ),
            ],
          );
        }

        return Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            SizedBox(
              width: 360,
              child: ExerciseBriefPanel(lesson: lesson),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: CodeEditorTab(
                lesson: lesson,
                code: code,
                workspaceSessionId: workspaceSessionId,
                workspaceReady: workspaceReady,
                editorConnectionStatus: editorConnectionStatus,
                consoleConnectionStatus: consoleConnectionStatus,
                editorShellUrl: editorShellUrl,
                statusMessage: statusMessage,
                runStatusLabel: runStatusLabel,
                scriptVersion: scriptVersion,
                onSubmit: onSubmit,
                onStop: onStop,
                onReset: onReset,
              ),
            ),
          ],
        );
      },
    );
  }
}
