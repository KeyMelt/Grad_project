import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';
import 'code_editor.dart';
import 'exercise_brief_panel.dart';
import 'lesson_notes_panel.dart';
import 'trace_replay_panel.dart';
import 'video_player.dart';

class WorkspaceTabs extends StatefulWidget {
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
  final VoidCallback onReconnectWorkspace;
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
  final ValueChanged<Map<String, dynamic>>? onConceptVideoSession;
  final void Function(String viewId, Duration duration)?
      onWorkspaceFocusSession;
  final VoidCallback? onRun;
  final bool showExerciseBriefInCodePane;

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
    required this.onReconnectWorkspace,
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
    this.onConceptVideoSession,
    this.onWorkspaceFocusSession,
    this.onRun,
    this.showExerciseBriefInCodePane = true,
  });

  @override
  State<WorkspaceTabs> createState() => _WorkspaceTabsState();
}

class _WorkspaceTabsState extends State<WorkspaceTabs>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  int _activeTabIndex = 0;
  DateTime _focusStartedAt = DateTime.now();
  bool _lessonNotesOpen = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(_handleTabChanged);
  }

  @override
  void didUpdateWidget(covariant WorkspaceTabs oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.lesson.id != widget.lesson.id) {
      _emitFocusSession();
      _focusStartedAt = DateTime.now();
    }
  }

  @override
  void dispose() {
    _emitFocusSession();
    _tabController.removeListener(_handleTabChanged);
    _tabController.dispose();
    super.dispose();
  }

  void _handleTabChanged() {
    if (_tabController.indexIsChanging ||
        _tabController.index == _activeTabIndex) {
      return;
    }
    _emitFocusSession();
    setState(() {
      _activeTabIndex = _tabController.index;
    });
    _focusStartedAt = DateTime.now();
  }

  void _emitFocusSession() {
    final duration = DateTime.now().difference(_focusStartedAt);
    widget.onWorkspaceFocusSession?.call(_tabId(_activeTabIndex), duration);
  }

  String _tabId(int index) {
    switch (index) {
      case 0:
        return 'concept';
      case 1:
        return 'code';
      case 2:
        return 'replay';
      default:
        return 'unknown';
    }
  }

  @override
  Widget build(BuildContext context) {
    final lesson = widget.lesson;
    final code = widget.code;
    final workspaceSessionId = widget.workspaceSessionId;
    final workspaceReady = widget.workspaceReady;
    final editorConnectionStatus = widget.editorConnectionStatus;
    final consoleConnectionStatus = widget.consoleConnectionStatus;
    final editorShellUrl = widget.editorShellUrl;
    final scriptVersion = widget.scriptVersion;
    final statusMessage = widget.statusMessage;
    final runStatusLabel = widget.runStatusLabel;
    final failureKind = widget.failureKind;
    final unresolvedBlanks = widget.unresolvedBlanks;
    final studentFeedback = widget.studentFeedback;
    final totalReward = widget.totalReward;
    final averageReward = widget.averageReward;
    final bestEpisodeReward = widget.bestEpisodeReward;
    final episodesCompleted = widget.episodesCompleted;
    final stepsRecorded = widget.stepsRecorded;
    final videoPath = widget.videoPath;
    final testResults = widget.testResults;
    final stepTrace = widget.stepTrace;

    return Padding(
      padding: const EdgeInsets.fromLTRB(6, 4, 6, 6),
      child: Column(
        children: [
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (_activeTabIndex == 0)
                  _LessonNotesDrawer(
                    lesson: lesson,
                    isOpen: _lessonNotesOpen,
                    onToggle: () =>
                        setState(() => _lessonNotesOpen = !_lessonNotesOpen),
                    onOpen: () => setState(() => _lessonNotesOpen = true),
                    onClose: () => setState(() => _lessonNotesOpen = false),
                  ),
                Expanded(
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      VideoPlayerTab(
                        lesson: lesson,
                        onSessionEnded: widget.onConceptVideoSession,
                      ),
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
                        onSubmit: widget.onSubmit,
                        onStop: widget.onStop,
                        onReset: widget.onReset,
                        onReconnectWorkspace: widget.onReconnectWorkspace,
                        onRun: widget.onRun,
                        showExerciseBrief: widget.showExerciseBriefInCodePane,
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
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(5),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE5E7EB)),
            ),
            child: TabBar(
              controller: _tabController,
              indicatorColor: const Color(0xFF1A73E8),
              labelColor: const Color(0xFF1A73E8),
              unselectedLabelColor: const Color(0xFF6B7280),
              indicatorSize: TabBarIndicatorSize.tab,
              tabs: const [
                Tab(height: 36, text: 'Concept'),
                Tab(height: 36, text: 'Code'),
                Tab(height: 36, text: 'Replay'),
              ],
            ),
          ),
        ],
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
  final VoidCallback onReconnectWorkspace;
  final VoidCallback? onRun;
  final bool showExerciseBrief;

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
    required this.onReconnectWorkspace,
    this.onRun,
    required this.showExerciseBrief,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (showExerciseBrief) {
          if (constraints.maxWidth >= 900) {
            final briefWidth =
                (constraints.maxWidth * 0.30).clamp(320.0, 420.0);
            return Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(
                  width: briefWidth,
                  child: ExerciseBriefPanel(lesson: lesson),
                ),
                const SizedBox(width: 18),
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
                    failureKind: failureKind,
                    unresolvedBlanks: unresolvedBlanks,
                    studentFeedback: studentFeedback,
                    testResults: testResults,
                    onSubmit: onSubmit,
                    onStop: onStop,
                    onReset: onReset,
                    onReconnect: onReconnectWorkspace,
                    onRun: onRun,
                  ),
                ),
              ],
            );
          }

          final briefHeight =
              (constraints.maxHeight * 0.30).clamp(220.0, 320.0);
          return Column(
            children: [
              SizedBox(
                height: briefHeight,
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
                  failureKind: failureKind,
                  unresolvedBlanks: unresolvedBlanks,
                  studentFeedback: studentFeedback,
                  testResults: testResults,
                  onSubmit: onSubmit,
                  onStop: onStop,
                  onReset: onReset,
                  onReconnect: onReconnectWorkspace,
                  onRun: onRun,
                ),
              ),
            ],
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
          onReconnect: onReconnectWorkspace,
          onRun: onRun,
        );
      },
    );
  }
}

class _LessonNotesDrawer extends StatelessWidget {
  final LessonDefinition lesson;
  final bool isOpen;
  final VoidCallback onToggle;
  final VoidCallback onOpen;
  final VoidCallback onClose;

  const _LessonNotesDrawer({
    required this.lesson,
    required this.isOpen,
    required this.onToggle,
    required this.onOpen,
    required this.onClose,
  });

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final panelWidth = (width * 0.28).clamp(300.0, 420.0);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        AnimatedContainer(
          duration: const Duration(milliseconds: 240),
          curve: Curves.easeInOut,
          width: isOpen ? panelWidth : 0,
          child: OverflowBox(
            minWidth: 0,
            maxWidth: panelWidth,
            alignment: Alignment.centerRight,
            child: SizedBox(
              width: panelWidth,
              child: LessonNotesPanel(lesson: lesson),
            ),
          ),
        ),
        Tooltip(
          message: isOpen ? 'Close notes' : 'Open notes',
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: onToggle,
            onHorizontalDragUpdate: (details) {
              if (details.primaryDelta != null && details.primaryDelta! > 16) {
                onOpen();
              } else if (details.primaryDelta != null &&
                  details.primaryDelta! < -16) {
                onClose();
              }
            },
            child: Container(
              width: 32,
              decoration: BoxDecoration(
                color: isOpen
                    ? AppTheme.primaryBlue.withValues(alpha: 0.10)
                    : AppTheme.primaryBlue,
                borderRadius: const BorderRadius.only(
                  topRight: Radius.circular(14),
                  bottomRight: Radius.circular(14),
                ),
                border: Border.all(
                  color:
                      isOpen ? const Color(0xFFBFDBFE) : AppTheme.primaryBlue,
                ),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    isOpen
                        ? Icons.chevron_left_rounded
                        : Icons.chevron_right_rounded,
                    color: isOpen ? AppTheme.primaryBlue : Colors.white,
                  ),
                  if (!isOpen) ...[
                    const SizedBox(height: 8),
                    RotatedBox(
                      quarterTurns: 1,
                      child: Text(
                        'Notes',
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0,
                            ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
        const SizedBox(width: 10),
      ],
    );
  }
}
