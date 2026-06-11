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
  final bool feedbackDismissed;
  final double totalReward;
  final double averageReward;
  final double bestEpisodeReward;
  final int episodesCompleted;
  final int stepsRecorded;
  final String videoPath;
  final String replayRenderStatus;
  final String? replayRenderError;
  final List<ExecutionTestCaseResult> testResults;
  final List<ExecutionTraceStep> stepTrace;
  final List<ExecutionTraceEpisode> traceEpisodes;
  final List<ExecutionEpisodeSummary> episodeSummaries;
  final ValueChanged<Map<String, dynamic>>? onConceptVideoSession;
  final VoidCallback? onVideoMicroSurveyRequest;
  final VoidCallback? onReplayMicroSurveyRequest;
  final void Function(String viewId, Duration duration)?
      onWorkspaceFocusSession;
  final VoidCallback? onDismissFeedback;
  final bool canShareSessionFeedback;
  final VoidCallback? onOpenSessionFeedback;
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
    required this.feedbackDismissed,
    required this.totalReward,
    required this.averageReward,
    required this.bestEpisodeReward,
    required this.episodesCompleted,
    required this.stepsRecorded,
    required this.videoPath,
    required this.replayRenderStatus,
    required this.replayRenderError,
    required this.testResults,
    required this.stepTrace,
    required this.traceEpisodes,
    required this.episodeSummaries,
    this.onConceptVideoSession,
    this.onVideoMicroSurveyRequest,
    this.onReplayMicroSurveyRequest,
    this.onWorkspaceFocusSession,
    this.onDismissFeedback,
    this.canShareSessionFeedback = false,
    this.onOpenSessionFeedback,
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
    final feedbackDismissed = widget.feedbackDismissed;
    final totalReward = widget.totalReward;
    final averageReward = widget.averageReward;
    final bestEpisodeReward = widget.bestEpisodeReward;
    final episodesCompleted = widget.episodesCompleted;
    final stepsRecorded = widget.stepsRecorded;
    final videoPath = widget.videoPath;
    final replayRenderStatus = widget.replayRenderStatus;
    final replayRenderError = widget.replayRenderError;
    final testResults = widget.testResults;
    final stepTrace = widget.stepTrace;
    final traceEpisodes = widget.traceEpisodes;
    final episodeSummaries = widget.episodeSummaries;

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
                        onVideoCompleted: widget.onVideoMicroSurveyRequest,
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
                        feedbackDismissed: feedbackDismissed,
                        testResults: testResults,
                        onSubmit: widget.onSubmit,
                        onStop: widget.onStop,
                        onReset: widget.onReset,
                        onReconnectWorkspace: widget.onReconnectWorkspace,
                        onDismissFeedback: widget.onDismissFeedback,
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
                        replayRenderStatus: replayRenderStatus,
                        replayRenderError: replayRenderError,
                        testResults: testResults,
                        stepTrace: stepTrace,
                        traceEpisodes: traceEpisodes,
                        episodeSummaries: episodeSummaries,
                        conceptVideo: lesson.conceptVideo,
                        onWatchConcept: () => _tabController.animateTo(0),
                        onReplayCompleted: widget.onReplayMicroSurveyRequest,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          if (widget.canShareSessionFeedback &&
              widget.onOpenSessionFeedback != null) ...[
            _SessionFeedbackPrompt(onPressed: widget.onOpenSessionFeedback!),
            const SizedBox(height: 8),
          ],
          Container(
            padding: const EdgeInsets.all(5),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE5E7EB)),
            ),
            child: TabBar(
              controller: _tabController,
              indicatorColor: AppTheme.primaryBlue,
              labelColor: AppTheme.primaryBlue,
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

class _SessionFeedbackPrompt extends StatelessWidget {
  final VoidCallback onPressed;

  const _SessionFeedbackPrompt({required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerRight,
      child: TextButton.icon(
        onPressed: onPressed,
        icon: const Icon(Icons.rate_review_outlined, size: 18),
        label: const Text('Share feedback'),
        style: TextButton.styleFrom(
          foregroundColor: AppTheme.textSecondary,
          visualDensity: VisualDensity.compact,
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
  final bool feedbackDismissed;
  final List<ExecutionTestCaseResult> testResults;
  final VoidCallback onSubmit;
  final VoidCallback onStop;
  final VoidCallback onReset;
  final VoidCallback onReconnectWorkspace;
  final VoidCallback? onDismissFeedback;
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
    required this.feedbackDismissed,
    required this.testResults,
    required this.onSubmit,
    required this.onStop,
    required this.onReset,
    required this.onReconnectWorkspace,
    this.onDismissFeedback,
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
                  child: _BriefAndFeedbackPanel(
                    lesson: lesson,
                    runStatusLabel: runStatusLabel,
                    statusMessage: statusMessage,
                    failureKind: failureKind,
                    unresolvedBlanks: unresolvedBlanks,
                    studentFeedback: studentFeedback,
                    testResults: testResults,
                    feedbackDismissed: feedbackDismissed,
                    onDismissFeedback: onDismissFeedback,
                  ),
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
                    onSubmit: onSubmit,
                    onStop: onStop,
                    onReset: onReset,
                    onReconnect: onReconnectWorkspace,
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
                child: _BriefAndFeedbackPanel(
                  lesson: lesson,
                  runStatusLabel: runStatusLabel,
                  statusMessage: statusMessage,
                  failureKind: failureKind,
                  unresolvedBlanks: unresolvedBlanks,
                  studentFeedback: studentFeedback,
                  testResults: testResults,
                  feedbackDismissed: feedbackDismissed,
                  onDismissFeedback: onDismissFeedback,
                ),
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
                  onReconnect: onReconnectWorkspace,
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
          onSubmit: onSubmit,
          onStop: onStop,
          onReset: onReset,
          onReconnect: onReconnectWorkspace,
        );
      },
    );
  }
}

class _BriefAndFeedbackPanel extends StatelessWidget {
  final LessonDefinition lesson;
  final String runStatusLabel;
  final String statusMessage;
  final String? failureKind;
  final List<String> unresolvedBlanks;
  final ExecutionStudentFeedback? studentFeedback;
  final bool feedbackDismissed;
  final List<ExecutionTestCaseResult> testResults;
  final VoidCallback? onDismissFeedback;

  const _BriefAndFeedbackPanel({
    required this.lesson,
    required this.runStatusLabel,
    required this.statusMessage,
    required this.failureKind,
    required this.unresolvedBlanks,
    required this.studentFeedback,
    required this.feedbackDismissed,
    required this.testResults,
    required this.onDismissFeedback,
  });

  @override
  Widget build(BuildContext context) {
    final showFeedback = !feedbackDismissed &&
        (studentFeedback != null ||
            testResults.isNotEmpty ||
            unresolvedBlanks.isNotEmpty ||
            failureKind != null);

    return LayoutBuilder(
      builder: (context, constraints) {
        final feedbackMaxHeight = constraints.maxHeight < 360
            ? (constraints.maxHeight * 0.36).clamp(80.0, 130.0).toDouble()
            : (constraints.maxHeight * 0.42).clamp(150.0, 300.0).toDouble();

        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: ExerciseBriefPanel(lesson: lesson),
            ),
            if (showFeedback) ...[
              const SizedBox(height: 12),
              ConstrainedBox(
                constraints: BoxConstraints(maxHeight: feedbackMaxHeight),
                child: SingleChildScrollView(
                  child: WorkspaceFeedbackPanel(
                    lesson: lesson,
                    runStatusLabel: runStatusLabel,
                    statusMessage: statusMessage,
                    failureKind: failureKind,
                    unresolvedBlanks: unresolvedBlanks,
                    studentFeedback: studentFeedback,
                    testResults: testResults,
                    onDismiss: onDismissFeedback,
                  ),
                ),
              ),
            ],
          ],
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
                  color: isOpen ? AppTheme.tealBorder : AppTheme.primaryBlue,
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
