import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/workbench_state.dart';
import 'code_editor.dart';
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
  final String? failureKind;
  final List<String> unresolvedBlanks;
  final ExecutionStudentFeedback? studentFeedback;
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
    required this.failureKind,
    required this.unresolvedBlanks,
    required this.studentFeedback,
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
        padding: const EdgeInsets.fromLTRB(10, 8, 10, 8),
        child: Column(
          children: [
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
                    failureKind: failureKind,
                    unresolvedBlanks: unresolvedBlanks,
                    studentFeedback: studentFeedback,
                    testResults: testResults,
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
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(5),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFE5E7EB)),
              ),
              child: const TabBar(
                indicatorColor: Color(0xFF1A73E8),
                labelColor: Color(0xFF1A73E8),
                unselectedLabelColor: Color(0xFF6B7280),
                indicatorSize: TabBarIndicatorSize.tab,
                tabs: [
                  Tab(height: 36, text: 'Concept'),
                  Tab(height: 36, text: 'Code'),
                  Tab(height: 36, text: 'Replay'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
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
  final String? failureKind;
  final List<String> unresolvedBlanks;
  final ExecutionStudentFeedback? studentFeedback;
  final List<ExecutionTestCaseResult> testResults;
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
    required this.failureKind,
    required this.unresolvedBlanks,
    required this.studentFeedback,
    required this.testResults,
    required this.onSubmit,
    required this.onStop,
    required this.onReset,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 1100) {
          return CodeEditorTab(
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
            failureKind: failureKind,
            unresolvedBlanks: unresolvedBlanks,
            studentFeedback: studentFeedback,
            testResults: testResults,
            onSubmit: onSubmit,
            onStop: onStop,
            onReset: onReset,
          );
        }

        return CodeEditorTab(
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
          failureKind: failureKind,
          unresolvedBlanks: unresolvedBlanks,
          studentFeedback: studentFeedback,
          testResults: testResults,
          onSubmit: onSubmit,
          onStop: onStop,
          onReset: onReset,
        );
      },
    );
  }
}
