import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_math_fork/flutter_math.dart';
import 'package:flutter/services.dart';
import 'package:video_player/video_player.dart';

import '../../core/backend_api.dart';
import '../../core/lesson_models.dart';
import 'trace_replay/trace_predict_prompt.dart';
import 'trace_replay/trace_step_markers.dart';
import 'trace_replay/trace_td_error_bar.dart';
import 'trace_replay/trace_value_sparkline.dart';

/// Design tokens for the Trace/Replay tab.
class _Ink {
  static const canvas = Color(0xFF0B1120);
  static const panel = Color(0xFF111C30);
  static const raised = Color(0xFF1B2840);
  static const control = Color(0xFF24344F);

  static const borderSubtle = Color(0xFF24344F);
  static const borderStrong = Color(0xFF3E5170);

  static const textHigh = Color(0xFFF1F5F9);
  static const textMed = Color(0xFFC7D2E1);
  static const textLow = Color(0xFF93A4BC);

  static const primary = Color(0xFF3B82F6);
  static const primaryText = Colors.white;
  static const state = Color(0xFF38BDF8);
  static const success = Color(0xFF34D399);
  static const warn = Color(0xFFFBBF24);
  static const danger = Color(0xFFF87171);
}

class TraceReplayPanel extends StatefulWidget {
  final String runStatusLabel;
  final String statusMessage;
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
  final LessonConceptVideo? conceptVideo;
  final VoidCallback? onWatchConcept;
  final VoidCallback? onReplayCompleted;

  const TraceReplayPanel({
    super.key,
    required this.runStatusLabel,
    required this.statusMessage,
    required this.totalReward,
    required this.averageReward,
    required this.bestEpisodeReward,
    required this.episodesCompleted,
    required this.stepsRecorded,
    required this.videoPath,
    this.replayRenderStatus = 'idle',
    this.replayRenderError,
    required this.testResults,
    required this.stepTrace,
    this.traceEpisodes = const [],
    this.episodeSummaries = const [],
    this.conceptVideo,
    this.onWatchConcept,
    this.onReplayCompleted,
  });

  @override
  State<TraceReplayPanel> createState() => _TraceReplayPanelState();
}

enum _ReplayBinderSection {
  step(Icons.dashboard_customize_rounded, 'Step'),
  math(Icons.functions_rounded, 'Math'),
  replay(Icons.movie_rounded, 'Replay');

  const _ReplayBinderSection(this.icon, this.label);

  final IconData icon;
  final String label;
}

class _TraceReplayPanelState extends State<TraceReplayPanel> {
  int _selectedEpisodeIndex = 0;
  int _currentStepIndex = 0;
  int _selectedBinderIndex = 0;
  final Set<_ReplayBinderSection> _visibleBinderSections = {
    _ReplayBinderSection.step,
    _ReplayBinderSection.math,
    _ReplayBinderSection.replay,
  };
  bool _quizMode = false;
  int _playbackMs = 1200;
  bool _guideExpanded = false;
  bool _guideDismissed = false;
  bool _conceptCtaDismissed = false;
  bool _replayCompletionFired = false;
  int? _jumpState;
  VideoPlayerController? _replayController;
  Timer? _tracePlaybackTimer;
  bool _isTracePlaying = false;
  bool _isReplayVideoLoading = false;
  String? _replayVideoError;
  final FocusNode _debuggerFocusNode = FocusNode(debugLabel: 'Trace debugger');

  @override
  void initState() {
    super.initState();
    _selectedEpisodeIndex = _initialEpisodeIndex();
    if (widget.videoPath.isNotEmpty) {
      _initializeReplayVideo();
    }
  }

  @override
  void didUpdateWidget(covariant TraceReplayPanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!listEquals(oldWidget.stepTrace, widget.stepTrace) ||
        !listEquals(oldWidget.traceEpisodes, widget.traceEpisodes)) {
      _selectedEpisodeIndex = _initialEpisodeIndex();
      _currentStepIndex = 0;
      _stopTracePlayback(notify: false);
    } else if (_currentStepIndex >= _currentEpisodeSteps.length &&
        _currentEpisodeSteps.isNotEmpty) {
      _currentStepIndex = _currentEpisodeSteps.length - 1;
    }
    if (_currentEpisodeSteps.isEmpty) {
      _stopTracePlayback(notify: false);
    }
    if (oldWidget.videoPath != widget.videoPath) {
      _disposeReplayController();
      if (widget.videoPath.isNotEmpty) {
        _initializeReplayVideo();
      }
    }
  }

  @override
  void dispose() {
    _stopTracePlayback(notify: false);
    _disposeReplayController();
    _debuggerFocusNode.dispose();
    super.dispose();
  }

  Future<void> _initializeReplayVideo() async {
    if (_isReplayVideoLoading || widget.videoPath.isEmpty) {
      return;
    }

    setState(() {
      _isReplayVideoLoading = true;
      _replayVideoError = null;
    });

    final uri = _replayVideoUri(widget.videoPath);
    try {
      final controller = VideoPlayerController.networkUrl(
        uri,
        httpHeaders: _authHeaders(),
      );
      await controller.initialize().timeout(const Duration(seconds: 45));
      await controller.setLooping(false);
      controller.addListener(_onReplayControllerChanged);
      if (!mounted) {
        await controller.dispose();
        return;
      }
      setState(() {
        _replayController = controller;
        _isReplayVideoLoading = false;
      });
    } catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _isReplayVideoLoading = false;
        _replayVideoError = 'Replay video could not be loaded: $error';
      });
    }
  }

  Uri _replayVideoUri(String path) {
    final base = Uri.parse(BackendConnectionManager().baseUrl);
    return base.replace(
      path: '/visualization/video',
      queryParameters: {'path': path},
    );
  }

  Map<String, String> _authHeaders() {
    final token = AuthSessionStore.accessToken;
    if (token == null || token.isEmpty) {
      return const <String, String>{};
    }
    return {'Authorization': 'Bearer $token'};
  }

  void _onReplayControllerChanged() {
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> _toggleReplayPlayback() async {
    final controller = _replayController;
    if (controller == null || !controller.value.isInitialized) {
      return;
    }
    if (controller.value.isPlaying) {
      await controller.pause();
    } else {
      await controller.play();
    }
    if (mounted) {
      setState(() {});
    }
  }

  void _toggleTracePlayback() {
    if (_isTracePlaying) {
      _stopTracePlayback();
      return;
    }
    if (_currentEpisodeSteps.length < 2) {
      return;
    }
    setState(() {
      _isTracePlaying = true;
      if (_currentStepIndex >= _currentEpisodeSteps.length - 1) {
        _currentStepIndex = 0;
      }
    });
    _tracePlaybackTimer = Timer.periodic(
      Duration(milliseconds: _playbackMs),
      (_) {
        if (!mounted || _currentEpisodeSteps.isEmpty) {
          _stopTracePlayback();
          return;
        }
        if (_currentStepIndex >= _currentEpisodeSteps.length - 1) {
          _stopTracePlayback();
          _fireReplayCompleted();
          return;
        }
        setState(() => _currentStepIndex += 1);
      },
    );
  }

  void _stopTracePlayback({bool notify = true}) {
    _tracePlaybackTimer?.cancel();
    _tracePlaybackTimer = null;
    if (_isTracePlaying && mounted && notify) {
      setState(() => _isTracePlaying = false);
    } else {
      _isTracePlaying = false;
    }
  }

  void _selectTraceStep(int index) {
    _stopTracePlayback();
    final lastIndex = _currentEpisodeSteps.length - 1;
    if (lastIndex < 0) {
      return;
    }
    final clamped = index.clamp(0, lastIndex);
    setState(() => _currentStepIndex = clamped);
    if (clamped == lastIndex) {
      _fireReplayCompleted();
    }
  }

  void _fireReplayCompleted() {
    if (_replayCompletionFired) return;
    _replayCompletionFired = true;
    widget.onReplayCompleted?.call();
  }

  void _selectEpisode(int episodeIndex) {
    _stopTracePlayback();
    setState(() {
      _selectedEpisodeIndex = episodeIndex;
      _currentStepIndex = 0;
      _replayCompletionFired = false;
    });
  }

  KeyEventResult _handleDebuggerKey(FocusNode node, KeyEvent event) {
    if (event is! KeyDownEvent || _currentEpisodeSteps.isEmpty) {
      return KeyEventResult.ignored;
    }
    final key = event.logicalKey;
    if (key == LogicalKeyboardKey.arrowLeft) {
      _selectTraceStep(_currentStepIndex - 1);
      return KeyEventResult.handled;
    }
    if (key == LogicalKeyboardKey.arrowRight) {
      _selectTraceStep(_currentStepIndex + 1);
      return KeyEventResult.handled;
    }
    if (key == LogicalKeyboardKey.home) {
      _selectTraceStep(0);
      return KeyEventResult.handled;
    }
    if (key == LogicalKeyboardKey.end) {
      _selectTraceStep(_currentEpisodeSteps.length - 1);
      return KeyEventResult.handled;
    }
    if (key == LogicalKeyboardKey.space) {
      _toggleTracePlayback();
      return KeyEventResult.handled;
    }
    if (key == LogicalKeyboardKey.bracketLeft) {
      _selectTraceStep(_nearestRewardStep(reverse: true));
      return KeyEventResult.handled;
    }
    if (key == LogicalKeyboardKey.bracketRight) {
      _selectTraceStep(_nearestRewardStep(reverse: false));
      return KeyEventResult.handled;
    }
    return KeyEventResult.ignored;
  }

  int _nearestRewardStep({required bool reverse}) {
    final indexes = reverse
        ? Iterable<int>.generate(_currentStepIndex).toList().reversed
        : Iterable<int>.generate(
            _currentEpisodeSteps.length - _currentStepIndex - 1,
            (offset) => _currentStepIndex + offset + 1,
          );
    for (final index in indexes) {
      if (_currentEpisodeSteps[index].reward != 0) {
        return index;
      }
    }
    return _currentStepIndex;
  }

  void _disposeReplayController() {
    _replayController?.removeListener(_onReplayControllerChanged);
    _replayController?.dispose();
    _replayController = null;
  }

  @override
  Widget build(BuildContext context) {
    final steps = _currentEpisodeSteps;
    final hasTrace = steps.isNotEmpty;
    final step = hasTrace ? steps[_currentStepIndex] : null;

    return Focus(
      focusNode: _debuggerFocusNode,
      autofocus: true,
      onKeyEvent: _handleDebuggerKey,
      child: Container(
        decoration: BoxDecoration(
          color: _Ink.canvas,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: _Ink.borderSubtle),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: LayoutBuilder(
            builder: (context, constraints) => _buildDebuggerBody(
              context,
              hasTrace: hasTrace,
              step: step,
              isWide: constraints.maxWidth >= 980,
            ),
          ),
        ),
      ),
    );
  }

  List<ExecutionTraceStep> get _currentEpisodeSteps {
    if (widget.traceEpisodes.isEmpty) {
      return widget.stepTrace;
    }
    for (final episode in widget.traceEpisodes) {
      if (episode.episodeIndex == _selectedEpisodeIndex) {
        return episode.steps;
      }
    }
    return widget.traceEpisodes.last.steps;
  }

  int _initialEpisodeIndex() {
    if (widget.traceEpisodes.isNotEmpty) {
      return widget.traceEpisodes.last.episodeIndex;
    }
    if (widget.episodeSummaries.isNotEmpty) {
      return widget.episodeSummaries.last.episodeIndex;
    }
    return 0;
  }

  Widget _buildDebuggerBody(
    BuildContext context, {
    required bool hasTrace,
    required ExecutionTraceStep? step,
    required bool isWide,
  }) {
    if (!hasTrace || step == null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(child: _buildWaitingPanel(context)),
          const SizedBox(height: 12),
          _buildMetricsPanel(context),
        ],
      );
    }

    final sections = _activeBinderSections(hasTrace: hasTrace, step: step);
    final selectedIndex = _selectedBinderIndex.clamp(0, sections.length - 1);
    final selectedSection = sections[selectedIndex];
    // The Replay tab is the video on its own — the step transport/scrubber and
    // quiz prompt only apply to the inspectable Step/Math tabs.
    final showStepToolbar = selectedSection != _ReplayBinderSection.replay;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildBinderControls(context, sections, selectedIndex),
        if (showStepToolbar) ...[
          const SizedBox(height: 8),
          _buildStepToolbar(context),
          if (_quizMode &&
              _currentStepIndex < _currentEpisodeSteps.length - 1) ...[
            const SizedBox(height: 8),
            _buildQuizPrompt(),
          ],
        ],
        const SizedBox(height: 8),
        Expanded(
          child: _buildBinderPage(
            context,
            selectedSection,
            step,
            isWide: isWide,
          ),
        ),
      ],
    );
  }

  List<_ReplayBinderSection> _activeBinderSections({
    required bool hasTrace,
    required ExecutionTraceStep? step,
  }) {
    final sections = <_ReplayBinderSection>[
      _ReplayBinderSection.step,
      if (hasTrace) _ReplayBinderSection.math,
      _ReplayBinderSection.replay,
    ].where(_visibleBinderSections.contains).toList(growable: false);
    return sections.isEmpty ? [_ReplayBinderSection.step] : sections;
  }

  Widget _buildBinderControls(
    BuildContext context,
    List<_ReplayBinderSection> sections,
    int selectedIndex,
  ) {
    final selector = Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (var i = 0; i < sections.length; i++)
          _sectionPill(
            sections[i],
            i == selectedIndex,
            () => setState(() => _selectedBinderIndex = i),
          ),
      ],
    );

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: _Ink.panel,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: _Ink.borderSubtle),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(child: selector),
          const SizedBox(width: 8),
          _buildVisibilityMenu(sections),
        ],
      ),
    );
  }

  Widget _sectionPill(
    _ReplayBinderSection section,
    bool active,
    VoidCallback onTap,
  ) {
    return Tooltip(
      message: section.label,
      child: Material(
        color: active ? _Ink.primary : _Ink.raised,
        borderRadius: BorderRadius.circular(4),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onTap,
          child: Container(
            height: 40,
            padding: const EdgeInsets.symmetric(horizontal: 14),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(4),
              border: Border.all(
                color: active ? _Ink.primary : _Ink.borderStrong,
                width: 1.2,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(section.icon,
                    size: 18, color: active ? Colors.white : _Ink.state),
                const SizedBox(width: 8),
                Text(
                  section.label,
                  style: TextStyle(
                    color: active ? Colors.white : _Ink.textMed,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildVisibilityMenu(List<_ReplayBinderSection> activeSections) {
    return Tooltip(
      message: 'Customize visible binder sections',
      child: PopupMenuButton<_ReplayBinderSection>(
        tooltip: 'Customize visible binder sections',
        onSelected: (section) {
          setState(() {
            if (_visibleBinderSections.contains(section) &&
                _visibleBinderSections.length > 1) {
              _visibleBinderSections.remove(section);
              _selectedBinderIndex =
                  _selectedBinderIndex.clamp(0, activeSections.length - 1);
            } else {
              _visibleBinderSections.add(section);
            }
          });
        },
        itemBuilder: (context) => [
          for (final section in _ReplayBinderSection.values)
            CheckedPopupMenuItem(
              value: section,
              checked: _visibleBinderSections.contains(section),
              child: Row(
                children: [
                  Icon(section.icon, size: 18, color: const Color(0xFF1D4ED8)),
                  const SizedBox(width: 8),
                  Text(section.label),
                ],
              ),
            ),
        ],
        child: Container(
          height: 44,
          width: 44,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: _Ink.control,
            borderRadius: BorderRadius.circular(6),
            border: Border.all(color: _Ink.borderStrong, width: 1.2),
          ),
          child: const Icon(
            Icons.tune_rounded,
            color: Color(0xFF93C5FD),
          ),
        ),
      ),
    );
  }

  Widget _buildBinderPage(
    BuildContext context,
    _ReplayBinderSection section,
    ExecutionTraceStep step, {
    required bool isWide,
  }) {
    final child = switch (section) {
      _ReplayBinderSection.step =>
        _buildStepBinderPage(context, step, isWide: isWide),
      _ReplayBinderSection.math =>
        _buildMathBinderPage(context, step, isWide: isWide),
      _ReplayBinderSection.replay => _buildReplayBinderPage(context),
    };
    return ClipRect(
      child: child,
    );
  }

  /// Secondary context cards (run metrics, concept CTA, errors, tests, guide)
  /// that used to live on the old "Run" tab. They now ride along under the Step
  /// summary so the Replay tab can be the video alone.
  List<Widget> _stepExtras(BuildContext context) {
    return <Widget>[
      _buildMetricsPanel(context),
      if (widget.conceptVideo != null &&
          widget.conceptVideo!.streamPath.isNotEmpty &&
          widget.onWatchConcept != null)
        _buildConceptVideoCta(),
      if (widget.runStatusLabel == 'Failed') _buildErrorPanel(context),
      if (widget.testResults.isNotEmpty) _buildSampleTests(context),
      _buildReadGuide(context, true),
    ];
  }

  Widget _stack(List<Widget> children) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          for (var i = 0; i < children.length; i++) ...[
            if (i > 0) const SizedBox(height: 12),
            children[i],
          ],
        ],
      );

  Widget _buildStepBinderPage(
    BuildContext context,
    ExecutionTraceStep step, {
    required bool isWide,
  }) {
    // The environment panel uses an internal LayoutBuilder, so it must stay in
    // a bounded slot (never inside a scroll view). Everything else — the step
    // summary and the secondary context cards — is scroll-safe.
    final detail = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Expanded(
          child: SingleChildScrollView(
            child: _stack([
              _buildCurrentStepSummary(context, step),
              ..._stepExtras(context),
            ]),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(height: 150, child: _buildTraceOutline(context)),
      ],
    );

    if (isWide) {
      return Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(flex: 6, child: _buildEnvironmentPanel(context, step)),
          const SizedBox(width: 12),
          Expanded(flex: 5, child: detail),
        ],
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Expanded(flex: 5, child: _buildEnvironmentPanel(context, step)),
        const SizedBox(height: 12),
        Expanded(flex: 6, child: detail),
      ],
    );
  }

  Widget _buildMathBinderPage(
    BuildContext context,
    ExecutionTraceStep step, {
    required bool isWide,
  }) {
    final eq = _buildMathPanel(context, step);
    final code = _buildCodePanel(context, step);
    final table = _buildTableInspector(context, step);
    if (isWide) {
      return Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(child: SingleChildScrollView(child: eq)),
          const SizedBox(width: 12),
          Expanded(child: SingleChildScrollView(child: code)),
          const SizedBox(width: 12),
          Expanded(child: SingleChildScrollView(child: table)),
        ],
      );
    }
    return SingleChildScrollView(
      child: _stack([eq, code, table]),
    );
  }

  Widget _buildReplayBinderPage(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.only(bottom: 4),
      child: _buildManimReplayPanel(context),
    );
  }

  Widget _buildConceptVideoCta() {
    final video = widget.conceptVideo;
    if (video == null ||
        video.streamPath.isEmpty ||
        widget.onWatchConcept == null ||
        _conceptCtaDismissed) {
      return const SizedBox.shrink();
    }
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.fromLTRB(16, 14, 12, 14),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E3A8A), Color(0xFF111C30)],
        ),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF3B82F6)),
      ),
      child: Row(
        children: [
          const Icon(Icons.ondemand_video_rounded,
              color: Color(0xFFBFDBFE), size: 28),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Flexible(
                      child: Text(
                        'New to this algorithm?',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: 15,
                        ),
                      ),
                    ),
                    if (video.durationLabel.isNotEmpty) ...[
                      const SizedBox(width: 8),
                      _buildTag(video.durationLabel, const Color(0xFFBFDBFE)),
                    ],
                  ],
                ),
                if (video.summary.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Text(
                    video.summary,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: Color(0xFFDCE6F4),
                      height: 1.4,
                      fontSize: 12.5,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: 12),
          FilledButton.icon(
            onPressed: widget.onWatchConcept,
            icon: const Icon(Icons.play_arrow_rounded),
            label: const Text('Watch'),
          ),
          const SizedBox(width: 4),
          IconButton(
            tooltip: 'Dismiss',
            visualDensity: VisualDensity.compact,
            onPressed: () => setState(() => _conceptCtaDismissed = true),
            icon: const Icon(Icons.close_rounded,
                color: Color(0xFFBFDBFE), size: 20),
          ),
        ],
      ),
    );
  }

  Widget _buildQuizPrompt() {
    final steps = _currentEpisodeSteps;
    final nextIndex = _currentStepIndex + 1;
    if (nextIndex >= steps.length) {
      return const SizedBox.shrink();
    }
    final next = steps[nextIndex];
    final gridLabel = next.gridMetadata?.actionLabel ?? '';
    final mcLabel = next.equationUpdate?.mcDetails?.actionLabel ?? '';
    final nextActionLabel = gridLabel.isNotEmpty
        ? gridLabel
        : (mcLabel.isNotEmpty ? mcLabel : 'a${next.action}');
    final rewardSign = next.reward > 0 ? 1 : (next.reward < 0 ? -1 : 0);
    var options = _actionOptions();
    if (!options.contains(nextActionLabel)) {
      options = [...options, nextActionLabel];
    }
    return TracePredictPrompt(
      key: ValueKey('predict-$_selectedEpisodeIndex-$_currentStepIndex'),
      actionOptions: options,
      actualActionLabel: nextActionLabel,
      actualRewardSign: rewardSign,
      onAdvance: () => _selectTraceStep(nextIndex),
    );
  }

  List<String> _actionOptions() {
    final labels = <String>{};
    for (final step in _currentEpisodeSteps) {
      final grid = step.gridMetadata?.actionLabel ?? '';
      final mc = step.equationUpdate?.mcDetails?.actionLabel ?? '';
      if (grid.isNotEmpty) labels.add(grid);
      if (mc.isNotEmpty) labels.add(mc);
    }
    if (labels.isEmpty) {
      for (final step in _currentEpisodeSteps) {
        final table = step.tableSnapshot;
        if (table != null && table.actionLabels.isNotEmpty) {
          labels.addAll(table.actionLabels);
          break;
        }
      }
    }
    return labels.toList();
  }

  Widget _buildQuizToggle() {
    return _controlPill(
      icon: Icons.psychology_alt_rounded,
      label: 'Quiz',
      tooltip: 'Predict each step before revealing it',
      active: _quizMode,
      onTap: () => setState(() {
        _quizMode = !_quizMode;
        if (_quizMode) _stopTracePlayback();
      }),
    );
  }

  Widget _circleIconButton({
    required IconData icon,
    required VoidCallback? onTap,
    required String tooltip,
    bool primary = false,
    double size = 46,
  }) {
    final enabled = onTap != null;
    final Color bg = primary ? _Ink.primary : _Ink.raised;
    final Color fg = primary ? _Ink.primaryText : _Ink.textHigh;
    return Tooltip(
      message: tooltip,
      child: Opacity(
        opacity: enabled ? 1 : 0.38,
        child: Material(
          color: bg,
          shape: CircleBorder(
            side: primary
                ? BorderSide.none
                : const BorderSide(color: _Ink.borderStrong, width: 1.4),
          ),
          clipBehavior: Clip.antiAlias,
          child: InkWell(
            onTap: onTap,
            child: SizedBox(
              width: size,
              height: size,
              child: Icon(icon, color: fg, size: primary ? 26 : 22),
            ),
          ),
        ),
      ),
    );
  }

  Widget _controlPill({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
    String? tooltip,
    bool active = false,
  }) {
    final pill = Material(
      color: active ? _Ink.primary : _Ink.control,
      borderRadius: BorderRadius.circular(6),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Container(
          height: 40,
          padding: const EdgeInsets.symmetric(horizontal: 14),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(6),
            border: Border.all(
              color: active ? _Ink.primary : _Ink.borderStrong,
              width: 1.2,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 18, color: active ? Colors.white : _Ink.state),
              const SizedBox(width: 8),
              Text(
                label,
                style: TextStyle(
                  color: active ? Colors.white : _Ink.textHigh,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      ),
    );
    return tooltip == null ? pill : Tooltip(message: tooltip, child: pill);
  }

  Widget _buildSpeedSelector() {
    final label = switch (_playbackMs) {
      2400 => '0.5×',
      600 => '2×',
      _ => '1×',
    };
    return Tooltip(
      message: 'Playback speed',
      child: PopupMenuButton<int>(
        initialValue: _playbackMs,
        color: _Ink.raised,
        onSelected: (ms) => setState(() => _playbackMs = ms),
        itemBuilder: (context) => const [
          PopupMenuItem(value: 2400, child: Text('0.5× (slow)')),
          PopupMenuItem(value: 1200, child: Text('1× (normal)')),
          PopupMenuItem(value: 600, child: Text('2× (fast)')),
        ],
        child: Container(
          height: 40,
          padding: const EdgeInsets.symmetric(horizontal: 14),
          decoration: BoxDecoration(
            color: _Ink.control,
            borderRadius: BorderRadius.circular(6),
            border: Border.all(color: _Ink.borderStrong, width: 1.2),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.speed_rounded, size: 18, color: _Ink.state),
              const SizedBox(width: 8),
              Text(
                label,
                style: const TextStyle(
                  color: _Ink.textHigh,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(width: 4),
              const Icon(Icons.arrow_drop_down_rounded,
                  size: 18, color: _Ink.textLow),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStepToolbar(BuildContext context) {
    final steps = _currentEpisodeSteps;
    final totalSteps = steps.length;
    final step = steps[_currentStepIndex];

    final transport = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _circleIconButton(
          icon: Icons.chevron_left_rounded,
          tooltip: 'Previous step',
          size: 38,
          onTap: _currentStepIndex > 0
              ? () => _selectTraceStep(_currentStepIndex - 1)
              : null,
        ),
        const SizedBox(width: 8),
        _circleIconButton(
          icon:
              _isTracePlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
          tooltip: _isTracePlaying ? 'Pause trace' : 'Play trace',
          primary: true,
          size: 44,
          onTap: totalSteps > 1 ? _toggleTracePlayback : null,
        ),
        const SizedBox(width: 8),
        _circleIconButton(
          icon: Icons.chevron_right_rounded,
          tooltip: 'Next step',
          size: 38,
          onTap: _currentStepIndex < totalSteps - 1
              ? () => _selectTraceStep(_currentStepIndex + 1)
              : null,
        ),
      ],
    );

    Widget optionsWrap(WrapAlignment alignment) => Wrap(
          spacing: 8,
          runSpacing: 8,
          alignment: alignment,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            if (_hasMultipleEpisodes) _buildEpisodeSelector(context),
            _buildSpeedSelector(),
            _buildQuizToggle(),
          ],
        );

    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: _Ink.panel,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: _Ink.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          LayoutBuilder(
            builder: (context, c) {
              if (c.maxWidth < 640) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(children: [transport, const Spacer()]),
                    const SizedBox(height: 8),
                    optionsWrap(WrapAlignment.start),
                  ],
                );
              }
              return Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  transport,
                  const SizedBox(width: 12),
                  Expanded(child: optionsWrap(WrapAlignment.end)),
                ],
              );
            },
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              _counterChip(_currentStepIndex + 1, totalSteps),
              const SizedBox(width: 12),
              Expanded(child: _buildStepSlider(totalSteps)),
            ],
          ),
          const SizedBox(height: 6),
          _buildTransitionChips(step),
        ],
      ),
    );
  }

  Widget _counterChip(int current, int total) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
      decoration: BoxDecoration(
        color: _Ink.raised,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: _Ink.borderStrong),
      ),
      child: Text.rich(
        TextSpan(
          children: [
            const TextSpan(
              text: 'Step ',
              style: TextStyle(color: _Ink.textLow, fontSize: 12),
            ),
            TextSpan(
              text: '$current',
              style: const TextStyle(
                color: _Ink.state,
                fontWeight: FontWeight.w800,
              ),
            ),
            TextSpan(
              text: ' / $total',
              style: const TextStyle(
                color: _Ink.textLow,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTransitionChips(ExecutionTraceStep step) {
    final actionLabel = (step.gridMetadata?.actionLabel.isNotEmpty ?? false)
        ? step.gridMetadata!.actionLabel
        : (step.equationUpdate?.mcDetails?.actionLabel.isNotEmpty ?? false)
            ? step.equationUpdate!.mcDetails!.actionLabel
            : (step.action >= 0 ? 'a${step.action}' : '');
    final rewardColor = step.reward < 0
        ? _Ink.danger
        : (step.reward > 0 ? _Ink.success : _Ink.warn);
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        _buildTag('s${step.state}  →  s${step.nextState}', _Ink.state),
        if (actionLabel.isNotEmpty)
          _buildTag(actionLabel, const Color(0xFF22D3EE)),
        _buildTag('reward ${step.reward.toStringAsFixed(2)}', rewardColor),
      ],
    );
  }

  bool get _hasMultipleEpisodes =>
      widget.traceEpisodes.length > 1 || widget.episodeSummaries.length > 1;

  Widget _buildEpisodeSelector(BuildContext context) {
    final curated = _curatedEpisodeIndexes;
    final selected = curated.contains(_selectedEpisodeIndex)
        ? _selectedEpisodeIndex
        : curated.last;
    return Semantics(
      label: 'Trace episode selector',
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
        decoration: BoxDecoration(
          color: _Ink.control,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: _Ink.borderStrong, width: 1.2),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.only(left: 2, right: 6),
              child:
                  Icon(Icons.timeline_rounded, size: 16, color: _Ink.textLow),
            ),
            for (final index in curated)
              _episodeSegment(
                _episodeRole(index, curated),
                index == selected,
                () => _selectEpisode(index),
                _episodeLabel(index),
              ),
          ],
        ),
      ),
    );
  }

  Widget _episodeSegment(
    String label,
    bool active,
    VoidCallback onTap,
    String tooltip,
  ) {
    return Tooltip(
      message: tooltip,
      child: Material(
        color: active ? _Ink.primary : Colors.transparent,
        borderRadius: BorderRadius.circular(9),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onTap,
          child: Container(
            height: 32,
            alignment: Alignment.center,
            padding: const EdgeInsets.symmetric(horizontal: 13),
            child: Text(
              label,
              style: TextStyle(
                color: active ? Colors.white : _Ink.textMed,
                fontWeight: FontWeight.w700,
                fontSize: 13,
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Curate the episode set to Early / Mid / Late.
  List<int> get _curatedEpisodeIndexes {
    final all = _episodeIndexes;
    if (all.length <= 3) return all;
    return [all.first, all[(all.length - 1) ~/ 2], all.last];
  }

  String _episodeRole(int index, List<int> curated) {
    final pos = curated.indexOf(index);
    if (curated.length >= 3) {
      if (pos <= 0) return 'Early';
      if (pos >= curated.length - 1) return 'Late';
      return 'Mid';
    }
    if (curated.length == 2) return pos == 0 ? 'Early' : 'Late';
    return 'Run';
  }

  List<int> get _episodeIndexes {
    final indexes = <int>{
      ...widget.traceEpisodes.map((episode) => episode.episodeIndex),
      ...widget.episodeSummaries.map((summary) => summary.episodeIndex),
    }.toList()
      ..sort();
    if (indexes.isEmpty) {
      return const [0];
    }
    return indexes;
  }

  String _episodeLabel(int index) {
    ExecutionEpisodeSummary? summary;
    for (final candidate in widget.episodeSummaries) {
      if (candidate.episodeIndex == index) {
        summary = candidate;
        break;
      }
    }
    if (summary == null) {
      return 'Episode ${index + 1}';
    }
    return 'Episode ${index + 1} · ${summary.stepCount} steps · r ${summary.totalReward.toStringAsFixed(2)}';
  }

  Widget _buildStepSlider(int totalSteps) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        TraceStepMarkers(
          totalSteps: totalSteps,
          markers: _stepMarkers(),
        ),
        Semantics(
          label: 'Trace step slider',
          value: 'Step ${_currentStepIndex + 1} of $totalSteps',
          slider: true,
          child: Slider(
            value: _currentStepIndex.toDouble(),
            min: 0,
            max: totalSteps > 1 ? (totalSteps - 1).toDouble() : 1.0,
            divisions: totalSteps > 1 ? totalSteps - 1 : 1,
            semanticFormatterCallback: (value) =>
                'Step ${value.round() + 1} of $totalSteps',
            onChanged: totalSteps > 1
                ? (value) => _selectTraceStep(value.round())
                : null,
          ),
        ),
      ],
    );
  }

  List<({int index, TraceMarkerKind kind})> _stepMarkers() {
    final steps = _currentEpisodeSteps;
    final markers = <({int index, TraceMarkerKind kind})>[];
    for (var i = 0; i < steps.length; i++) {
      final step = steps[i];
      final terminal = step.gridMetadata?.terminated == true ||
          step.gridMetadata?.truncated == true ||
          step.equationUpdate?.mcDetails?.terminated == true;
      if (step.reward > 0) {
        markers.add((index: i, kind: TraceMarkerKind.rewardPositive));
      } else if (step.reward < 0) {
        markers.add((index: i, kind: TraceMarkerKind.rewardNegative));
      } else if (terminal) {
        markers.add((index: i, kind: TraceMarkerKind.terminal));
      }
    }
    return markers;
  }

  Widget _buildTag(String label, Color accent) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: accent.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: accent.withValues(alpha: 0.35)),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: accent,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _buildTraceOutline(BuildContext context) {
    final steps = _currentEpisodeSteps;
    return _panelShell(
      title: 'Trace Outline',
      child: SizedBox(
        height: 132,
        child: ListView.separated(
          scrollDirection: Axis.horizontal,
          itemCount: steps.length,
          separatorBuilder: (_, __) => const SizedBox(width: 10),
          itemBuilder: (context, index) {
            final step = steps[index];
            final isSelected = index == _currentStepIndex;
            return GestureDetector(
              onTap: () => _selectTraceStep(index),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 160),
                width: 170,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: isSelected
                      ? const Color(0xFF172554)
                      : const Color(0xFF111827),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(
                    color: isSelected
                        ? const Color(0xFF60A5FA)
                        : const Color(0xFF1E293B),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 24,
                          height: 24,
                          decoration: BoxDecoration(
                            color: isSelected
                                ? const Color(0xFF2563EB)
                                : const Color(0xFF1F2937),
                            borderRadius: BorderRadius.circular(999),
                          ),
                          alignment: Alignment.center,
                          child: Text(
                            '${index + 1}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            's${step.state} -> ${step.nextState}',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style:
                                Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: Colors.white,
                                      fontWeight: FontWeight.w700,
                                    ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Expanded(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: _buildFrameImage(step.framePath),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      step.agentCaption,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: const Color(0xFFCBD5E1),
                            height: 1.35,
                          ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildCurrentStepSummary(
    BuildContext context,
    ExecutionTraceStep step,
  ) {
    final explanation = step.explanation;
    final firstMathLine = step.mathLines.isNotEmpty
        ? step.mathLines.first
        : 'No math annotation was recorded for this step.';
    final updatedKeys = step.updatedValues.keys.take(2).join(', ');
    return _panelShell(
      title: 'What This Step Means',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            (explanation != null && explanation.summary.isNotEmpty)
                ? explanation.summary
                : step.agentCaption,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.white,
                  height: 1.45,
                ),
          ),
          if (explanation != null &&
              explanation.summary.isNotEmpty &&
              step.agentCaption.isNotEmpty &&
              step.agentCaption != explanation.summary) ...[
            const SizedBox(height: 6),
            Text(
              step.agentCaption,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: const Color(0xFFCBD5E1),
                    height: 1.4,
                  ),
            ),
          ],
          const SizedBox(height: 12),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              _buildMetricCard(
                'Code focus lines',
                '${step.codeLines.length}',
                const Color(0xFF93C5FD),
              ),
              _buildMetricCard(
                'Math notes',
                '${step.mathLines.length}',
                const Color(0xFFFDE68A),
              ),
              _buildMetricCard(
                'Updated values',
                updatedKeys.isEmpty ? 'None' : updatedKeys,
                const Color(0xFFA7F3D0),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            firstMathLine,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFFCBD5E1),
                  height: 1.45,
                ),
          ),
          if (explanation != null && explanation.whyCorrect.isNotEmpty) ...[
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF0B1220),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: const Color(0xFF1E3A8A)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Why this update is correct',
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                          color: const Color(0xFF93C5FD),
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    explanation.whyCorrect,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: const Color(0xFFE2E8F0),
                          height: 1.45,
                        ),
                  ),
                  if (explanation.tableFocus.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    _buildTag(
                      'table ${explanation.tableFocus}',
                      const Color(0xFFA7F3D0),
                    ),
                  ],
                ],
              ),
            ),
          ],
          Builder(
            builder: (context) {
              final lhs = step.equationUpdate?.lhs ?? '';
              final history = _valueHistory(lhs);
              if (history.length < 2) {
                return const SizedBox.shrink();
              }
              return Padding(
                padding: const EdgeInsets.only(top: 12),
                child: TraceValueSparkline(
                  values: history,
                  label: '$lhs across this episode',
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  List<double> _valueHistory(String lhs) {
    if (lhs.isEmpty) {
      return const [];
    }
    final out = <double>[];
    for (final step in _currentEpisodeSteps) {
      final update = step.equationUpdate;
      if (update != null && update.lhs == lhs && update.newValue is num) {
        out.add((update.newValue as num).toDouble());
      }
    }
    return out;
  }

  Widget _buildEnvironmentPanel(BuildContext context, ExecutionTraceStep step) {
    return _panelShell(
      title: '1. Agent and Environment',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth > 500;
              final renderWidget = AspectRatio(
                aspectRatio: 1.0,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: _buildFrameImage(step.framePath),
                ),
              );

              final metricsWidget = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (step.equationUpdate?.mcDetails?.observation != null) ...[
                    _buildBlackjackObservationCard(
                      context,
                      step.equationUpdate!.mcDetails!,
                    ),
                    const SizedBox(height: 16),
                  ],
                  if (step.gridMetadata != null) ...[
                    _buildGridWorldCompanion(context, step.gridMetadata!),
                    const SizedBox(height: 16),
                  ],
                  Text(
                    step.agentCaption,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: Colors.white,
                          height: 1.5,
                        ),
                  ),
                  const SizedBox(height: 16),
                  Builder(
                    builder: (context) {
                      final eq = step.equationUpdate;
                      final isDp = eq?.isDynamicProgramming ?? false;
                      final isBlackjack = eq?.mcDetails?.observation != null;
                      return Wrap(
                        spacing: 12,
                        runSpacing: 12,
                        children: [
                          if (!isBlackjack)
                            _buildMetricCard(
                              'State Transition',
                              '${step.state} ➔ ${step.nextState}',
                              const Color(0xFF7DD3FC),
                            ),
                          _buildMetricCard(
                            'Return / Reward',
                            step.reward.toStringAsFixed(2),
                            const Color(0xFFFDE68A),
                          ),
                          if (isDp)
                            _buildMetricCard(
                              'Probability (p)',
                              step.transitionProbability.toStringAsFixed(3),
                              const Color(0xFFA7F3D0),
                            )
                          else
                            _buildMetricCard(
                              'Transition',
                              'sampled · model-free',
                              const Color(0xFFC4B5FD),
                            ),
                        ],
                      );
                    },
                  ),
                ],
              );

              if (isWide) {
                // Explicit widths (not Expanded/flex) so this Row keeps an
                // intrinsic height and stays layout-safe inside a scroll view.
                final available = constraints.maxWidth - 24;
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: available * 4 / 9,
                      child: renderWidget,
                    ),
                    const SizedBox(width: 24),
                    SizedBox(
                      width: available * 5 / 9,
                      child: metricsWidget,
                    ),
                  ],
                );
              } else {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    renderWidget,
                    const SizedBox(height: 16),
                    metricsWidget,
                  ],
                );
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMetricCard(String label, String value, Color accent) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: accent.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: Color(0xFF94A3B8),
              fontSize: 12,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.3,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBlackjackObservationCard(
    BuildContext context,
    TraceMcDetails details,
  ) {
    final observation = details.observation;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF111827),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Blackjack observation',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: const Color(0xFF93C5FD),
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              _buildMetricCard(
                'Player sum',
                observation?.playerSum?.toString() ?? 'n/a',
                const Color(0xFF93C5FD),
              ),
              _buildMetricCard(
                'Dealer showing',
                observation?.dealerCard?.toString() ?? 'n/a',
                const Color(0xFF06B6D4),
              ),
              _buildMetricCard(
                'Usable ace',
                observation?.usableAce == true ? 'Yes' : 'No',
                const Color(0xFFA7F3D0),
              ),
              _buildMetricCard(
                'Action',
                details.actionLabel.isEmpty ? 'n/a' : details.actionLabel,
                const Color(0xFFC4B5FD),
              ),
              _buildMetricCard(
                'Reward',
                _formatNullableDouble(details.reward),
                const Color(0xFFFBBF24),
              ),
            ],
          ),
          if (details.nextObservation != null) ...[
            const SizedBox(height: 10),
            Text(
              'Next: ${details.nextObservation!.label}',
              style: const TextStyle(
                color: Color(0xFFCBD5E1),
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildGridWorldCompanion(
    BuildContext context,
    TraceGridMetadata grid,
  ) {
    final aspectRatio = grid.rows > 0 ? grid.columns / grid.rows : 1.0;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF111827),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${grid.environment} grid',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: const Color(0xFF93C5FD),
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 10),
          Builder(
            builder: (context) {
              final gridView = GridView.builder(
                physics: const NeverScrollableScrollPhysics(),
                padding: EdgeInsets.zero,
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: grid.columns <= 0 ? 1 : grid.columns,
                  childAspectRatio: 1,
                  mainAxisSpacing: 4,
                  crossAxisSpacing: 4,
                ),
                itemCount: grid.cells.length,
                itemBuilder: (context, index) {
                  return _buildGridCell(grid, grid.cells[index]);
                },
              );
              if (grid.columns > 8) {
                const cell = 38.0;
                return SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: SizedBox(
                    width: grid.columns * cell,
                    height: grid.rows * cell,
                    child: gridView,
                  ),
                );
              }
              return AspectRatio(
                aspectRatio: aspectRatio,
                child: gridView,
              );
            },
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildTag('state ${grid.state}', const Color(0xFF93C5FD)),
              if (grid.nextState != null)
                _buildTag('next ${grid.nextState}', const Color(0xFF2DD4BF)),
              if (grid.actionLabel.isNotEmpty)
                _buildTag(grid.actionLabel, const Color(0xFF06B6D4)),
              if (grid.reward != null)
                _buildTag(
                  'reward ${grid.reward!.toStringAsFixed(2)}',
                  grid.reward! < 0
                      ? const Color(0xFFF87171)
                      : const Color(0xFFFBBF24),
                ),
              if (grid.terminated || grid.truncated)
                _buildTag(
                  grid.terminated ? 'terminal' : 'truncated',
                  const Color(0xFFF87171),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildGridCell(TraceGridMetadata grid, TraceGridCell cell) {
    final isCurrent = cell.state == grid.state;
    final isNext = grid.nextState != null && cell.state == grid.nextState;
    final isCliff = cell.tileType == 'C';
    final isHole = cell.tileType == 'H';
    final isGoal = cell.tileType == 'G';
    final tileColor = isCliff || isHole
        ? const Color(0xFF7F1D1D)
        : isGoal
            ? const Color(0xFF065F46)
            : cell.tileType == 'S'
                ? const Color(0xFF1E3A8A)
                : const Color(0xFF1E293B);
    return Tooltip(
      message:
          'State ${cell.state} (${cell.row}, ${cell.column}) | ${_gridTileLabel(cell.tileType)}',
      child: Container(
        decoration: BoxDecoration(
          color: tileColor,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(
            color: isCurrent
                ? const Color(0xFF60A5FA)
                : isNext
                    ? const Color(0xFF2DD4BF)
                    : const Color(0xFF334155),
            width: isCurrent || isNext ? 2 : 1,
          ),
        ),
        child: Stack(
          children: [
            Positioned(
              top: 4,
              left: 4,
              child: Text(
                '${cell.state}',
                style: const TextStyle(
                  color: Color(0xFFE2E8F0),
                  fontSize: 9,
                  fontFamily: 'Courier',
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            Center(
              child: Text(
                isCurrent
                    ? _gridActionMarker(grid)
                    : isNext
                        ? 'N'
                        : _gridTileMarker(cell.tileType),
                style: TextStyle(
                  color: Colors.white,
                  fontSize: isCurrent ? 18 : 13,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _gridActionMarker(TraceGridMetadata grid) {
    return switch (grid.actionLabel) {
      'Up' => '↑',
      'Right' => '→',
      'Down' => '↓',
      'Left' => '←',
      _ => 'A',
    };
  }

  String _gridTileMarker(String tileType) {
    return switch (tileType) {
      'S' => 'S',
      'G' => 'G',
      'H' => 'H',
      'C' => '!',
      _ => '',
    };
  }

  String _gridTileLabel(String tileType) {
    return switch (tileType) {
      'S' => 'start',
      'G' => 'goal',
      'H' => 'hole',
      'C' => 'cliff',
      'F' => 'frozen/safe',
      _ => tileType.isEmpty ? 'empty' : tileType,
    };
  }

  Widget _buildFrameImage(String framePath) {
    if (framePath.isNotEmpty) {
      final frameUri = Uri.parse(
        '${BackendConnectionManager().baseUrl}/visualization/frame',
      ).replace(queryParameters: {'path': framePath});
      return Image.network(
        frameUri.toString(),
        headers: _authHeaders(),
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) =>
            _buildMissingFramePlaceholder(framePath),
      );
    }

    return _buildMissingFramePlaceholder(framePath);
  }

  Widget _buildMissingFramePlaceholder(String framePath) {
    return Container(
      color: const Color(0xFF1E293B),
      padding: const EdgeInsets.all(18),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.image_not_supported_outlined,
              color: Color(0xFF94A3B8),
              size: 42,
            ),
            const SizedBox(height: 12),
            const Text(
              'Environment frame unavailable',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Color(0xFFE2E8F0),
                fontWeight: FontWeight.w700,
              ),
            ),
            if (framePath.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                framePath,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  height: 1.3,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildCodePanel(BuildContext context, ExecutionTraceStep step) {
    final focusedLineIndex = _focusedCodeLineIndex(step);
    return _panelShell(
      title: '2. Code Trace',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            step.codeTitle,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: const Color(0xFF93C5FD),
                  fontWeight: FontWeight.w700,
                ),
          ),
          if (focusedLineIndex >= 0 &&
              step.tableSnapshot?.activeCell != null) ...[
            const SizedBox(height: 6),
            Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: Color(0xFF60A5FA),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    'Highlighted line updates the active cell '
                    's${step.tableSnapshot!.activeCell!.row}, a${step.tableSnapshot!.activeCell!.column}',
                    style: const TextStyle(
                      color: Color(0xFF93C5FD),
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
          ],
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFF111827),
              borderRadius: BorderRadius.circular(6),
            ),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (var index = 0; index < step.codeLines.length; index++)
                    _buildCodeLine(
                      step.codeLines[index],
                      index,
                      index == focusedLineIndex,
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  int _focusedCodeLineIndex(ExecutionTraceStep step) {
    final focus = step.equationUpdate?.codeFocus.trim() ?? '';
    if (focus.isEmpty || step.codeLines.isEmpty) {
      return -1;
    }

    final normalizedFocus = _normalizeCodeForMatch(focus);
    for (var index = 0; index < step.codeLines.length; index++) {
      if (step.codeLines[index].trim() == focus) {
        return index;
      }
    }
    for (var index = 0; index < step.codeLines.length; index++) {
      final normalizedLine = _normalizeCodeForMatch(step.codeLines[index]);
      if (normalizedLine.contains(normalizedFocus) ||
          normalizedFocus.contains(normalizedLine)) {
        return index;
      }
    }
    final focusTarget = _assignmentTarget(focus);
    if (focusTarget.isNotEmpty) {
      for (var index = 0; index < step.codeLines.length; index++) {
        final lineTarget = _assignmentTarget(step.codeLines[index]);
        if (lineTarget == focusTarget) {
          return index;
        }
      }
    }
    return -1;
  }

  String _normalizeCodeForMatch(String code) {
    return code.replaceAll(RegExp(r'\s+'), '');
  }

  String _assignmentTarget(String code) {
    final normalized = _normalizeCodeForMatch(code);
    final assignmentIndex = normalized.indexOf('=');
    if (assignmentIndex <= 0) {
      return '';
    }
    final target = normalized.substring(0, assignmentIndex);
    return target.endsWith('+') ||
            target.endsWith('-') ||
            target.endsWith('*') ||
            target.endsWith('/')
        ? target.substring(0, target.length - 1)
        : target;
  }

  Widget _buildCodeLine(String line, int index, bool isFocused) {
    return Container(
      key: ValueKey(isFocused
          ? 'trace-code-focus-line-$index'
          : 'trace-code-line-$index'),
      margin: const EdgeInsets.symmetric(vertical: 2),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
      decoration: BoxDecoration(
        color: isFocused ? const Color(0xFF172554) : const Color(0x00000000),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 3,
            height: 18,
            decoration: BoxDecoration(
              color:
                  isFocused ? const Color(0xFF60A5FA) : const Color(0x00000000),
              borderRadius: BorderRadius.circular(999),
            ),
          ),
          const SizedBox(width: 8),
          Text(
            line,
            style: TextStyle(
              color:
                  isFocused ? const Color(0xFFBFDBFE) : const Color(0xFFE5E7EB),
              fontFamily: 'Courier',
              fontSize: 13,
              fontWeight: isFocused ? FontWeight.w800 : FontWeight.w500,
              height: 1.45,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMathPanel(BuildContext context, ExecutionTraceStep step) {
    final equationUpdate = step.equationUpdate;
    return _panelShell(
      title: '3. Mathematics',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            step.mathTitle,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: const Color(0xFFFDE68A),
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF111827),
              borderRadius: BorderRadius.circular(6),
            ),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Math.tex(
                step.mathEquation.isEmpty
                    ? r'\text{No\ equation\ provided}'
                    : step.mathEquation,
                textStyle: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                ),
              ),
            ),
          ),
          if (equationUpdate != null &&
              equationUpdate.isTemporalDifference) ...[
            const SizedBox(height: 12),
            _buildTemporalDifferenceEquation(context, step, equationUpdate),
          ],
          if (equationUpdate != null &&
              equationUpdate.isDynamicProgramming) ...[
            const SizedBox(height: 12),
            _buildDynamicProgrammingEquation(context, equationUpdate),
          ],
          if (equationUpdate != null && equationUpdate.isMonteCarlo) ...[
            const SizedBox(height: 12),
            _buildMonteCarloEquation(context, equationUpdate),
          ],
          const SizedBox(height: 12),
          ...step.mathLines.map(
            (line) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(
                line,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: const Color(0xFFCBD5E1),
                      height: 1.45,
                    ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTemporalDifferenceEquation(
    BuildContext context,
    ExecutionTraceStep step,
    TraceEquationUpdate update,
  ) {
    final title = update.kind == 'q_learning'
        ? 'Q-learning numeric update'
        : update.kind == 'sarsa'
            ? 'SARSA numeric update'
            : 'TD numeric update';
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: const Color(0xFFFDE68A),
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 10),
          _buildEquationRow('Updated cell', update.lhs),
          _buildEquationRow('Formula with numbers', update.substitution),
          _buildEquationRow(
            'Environment reward',
            _formatNullableDouble(update.reward),
            accent: const Color(0xFFFBBF24),
          ),
          _buildEquationRow(
            update.kind == 'q_learning'
                ? 'Best next action (off-policy)'
                : update.kind == 'sarsa'
                    ? 'Next action you take (on-policy)'
                    : 'Bootstrap source',
            '${update.bootstrapLabel} = ${_formatNullableDouble(update.bootstrapValue)}',
            accent: const Color(0xFF2DD4BF),
          ),
          if (update.kind == 'q_learning' || update.kind == 'sarsa')
            Padding(
              padding: const EdgeInsets.only(bottom: 8, left: 132),
              child: Text(
                update.kind == 'q_learning'
                    ? "Off-policy: bootstraps off the BEST next action — even one it won't take."
                    : 'On-policy: bootstraps off the action it will ACTUALLY take next.',
                style: const TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  height: 1.3,
                ),
              ),
            ),
          _buildEquationRow(
            'TD target',
            _formatNullableDouble(update.tdTarget),
            accent: const Color(0xFF93C5FD),
          ),
          _buildEquationRow(
            'TD error',
            _formatNullableDouble(update.tdError),
            accent: const Color(0xFFA7F3D0),
          ),
          _buildEquationRow(
            'Result',
            '${_formatScalar(update.oldValue)} -> ${_formatScalar(update.newValue)}',
            accent: const Color(0xFF10B981),
          ),
          Builder(
            builder: (context) {
              final oldV = update.oldValue is num
                  ? (update.oldValue as num).toDouble()
                  : null;
              final newV = update.newValue is num
                  ? (update.newValue as num).toDouble()
                  : null;
              final target = update.tdTarget;
              if (oldV == null || newV == null || target == null) {
                return const SizedBox.shrink();
              }
              return Padding(
                padding: const EdgeInsets.only(top: 12),
                child: TraceTdErrorBar(
                  oldValue: oldV,
                  newValue: newV,
                  target: target,
                  tdError: update.tdError,
                ),
              );
            },
          ),
          if (update.codeFocus.isNotEmpty)
            _buildEquationRow(
              'Code line',
              update.codeFocus,
              accent: const Color(0xFF93C5FD),
            ),
        ],
      ),
    );
  }

  Widget _buildEquationRow(
    String label,
    String value, {
    Color accent = const Color(0xFFE2E8F0),
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 132,
            child: Text(
              label,
              style: const TextStyle(
                color: Color(0xFF94A3B8),
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value.isEmpty ? 'n/a' : value,
              style: TextStyle(
                color: accent,
                fontFamily: 'Courier',
                fontSize: 13,
                height: 1.35,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDynamicProgrammingEquation(
    BuildContext context,
    TraceEquationUpdate update,
  ) {
    final details = update.dpDetails;
    if (details == null) {
      return const SizedBox.shrink();
    }
    final title = switch (update.kind) {
      'policy_evaluation' => 'Policy evaluation branch backup',
      'value_iteration' => 'Value iteration action comparison',
      'policy_improvement' => 'Policy improvement lookahead',
      _ => 'Dynamic programming backup',
    };
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: const Color(0xFFFDE68A),
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 10),
          _buildEquationRow('Updated target', update.lhs),
          _buildEquationRow(
            'Backup value',
            _formatNullableDouble(details.backupValue ?? update.tdTarget),
            accent: const Color(0xFF93C5FD),
          ),
          if (details.delta != null)
            _buildEquationRow(
              'Delta',
              _formatNullableDouble(details.delta),
              accent: const Color(0xFFA7F3D0),
            ),
          if (details.selectedActionLabel.isNotEmpty)
            _buildEquationRow(
              'Selected action',
              details.selectedActionLabel,
              accent: const Color(0xFF06B6D4),
            ),
          if (details.policyRowBefore.isNotEmpty ||
              details.policyRowAfter.isNotEmpty)
            _buildEquationRow(
              'Policy row',
              '${_formatDoubleList(details.policyRowBefore)} -> ${_formatDoubleList(details.policyRowAfter)}',
              accent: const Color(0xFF10B981),
            ),
          if (update.codeFocus.isNotEmpty)
            _buildEquationRow(
              'Code line',
              update.codeFocus,
              accent: const Color(0xFF93C5FD),
            ),
          const SizedBox(height: 10),
          _buildDpActionBackupTable(context, update.kind, details),
        ],
      ),
    );
  }

  Widget _buildMonteCarloEquation(
    BuildContext context,
    TraceEquationUpdate update,
  ) {
    final details = update.mcDetails;
    if (details == null) {
      return const SizedBox.shrink();
    }
    final isReturnUpdate = update.kind == 'mc_first_visit';
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isReturnUpdate
                ? 'First-visit return update'
                : 'Monte Carlo episode sample',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: const Color(0xFFFDE68A),
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 10),
          _buildEquationRow(
              'Episode step', '${details.episodeIndex}:${details.episodeStep}'),
          if (details.observation != null)
            _buildEquationRow('Observation', details.observation!.label),
          if (details.actionLabel.isNotEmpty)
            _buildEquationRow(
              'Action',
              details.actionLabel,
              accent: const Color(0xFF06B6D4),
            ),
          if (details.reward != null)
            _buildEquationRow(
              'Reward',
              _formatNullableDouble(details.reward),
              accent: const Color(0xFFFBBF24),
            ),
          if (details.nextObservation != null)
            _buildEquationRow(
                'Next observation', details.nextObservation!.label),
          if (isReturnUpdate) ...[
            _buildEquationRow(
              'Return G',
              _formatNullableDouble(details.returnValue ?? update.tdTarget),
              accent: const Color(0xFF93C5FD),
            ),
            _buildEquationRow(
              'Returns history',
              _formatDoubleList(details.returnsHistory),
              accent: const Color(0xFF10B981),
            ),
          ],
          if (details.terminated || details.truncated)
            _buildEquationRow(
              'Episode status',
              details.terminated ? 'terminated' : 'truncated',
              accent: const Color(0xFFF87171),
            ),
          if (update.codeFocus.isNotEmpty)
            _buildEquationRow(
              'Code line',
              update.codeFocus,
              accent: const Color(0xFF93C5FD),
            ),
          if (details.returnTerms.isNotEmpty) ...[
            const SizedBox(height: 10),
            _buildReturnLadder(details.returnTerms),
          ],
        ],
      ),
    );
  }

  Widget _buildReturnLadder(List<TraceMcReturnTerm> terms) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _buildDpHeaderCell('Step', width: 64),
              _buildDpHeaderCell('Discount', width: 86),
              _buildDpHeaderCell('Reward', width: 86),
              _buildDpHeaderCell('Term', width: 86),
              _buildDpHeaderCell('G so far', width: 96),
            ],
          ),
          const SizedBox(height: 6),
          for (final term in terms)
            Container(
              margin: const EdgeInsets.only(bottom: 6),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              decoration: BoxDecoration(
                color: const Color(0xFF111827),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: Row(
                children: [
                  _buildDpValueCell('${term.episodeStep}', width: 54),
                  _buildDpValueCell(term.discount.toStringAsFixed(4),
                      width: 86),
                  _buildDpValueCell(term.reward.toStringAsFixed(4), width: 86),
                  _buildDpValueCell(
                    term.discountedReward.toStringAsFixed(4),
                    width: 86,
                    color: const Color(0xFFFBBF24),
                  ),
                  _buildDpValueCell(
                    term.runningReturn.toStringAsFixed(4),
                    width: 96,
                    color: const Color(0xFF10B981),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildDpActionBackupTable(
    BuildContext context,
    String kind,
    TraceDpDetails details,
  ) {
    final showPolicy = kind == 'policy_evaluation';
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _buildDpHeaderCell('Action', width: 96),
              if (showPolicy) _buildDpHeaderCell('pi(a|s)', width: 78),
              _buildDpHeaderCell('Expected', width: 94),
              _buildDpHeaderCell(
                showPolicy ? 'Weighted' : 'Backup',
                width: 94,
              ),
              _buildDpHeaderCell('Branch terms', width: 360),
            ],
          ),
          const SizedBox(height: 6),
          for (final backup in details.actionBackups)
            _buildDpActionBackupRow(
              backup,
              showPolicy: showPolicy,
              isSelected: details.selectedAction == backup.action,
            ),
        ],
      ),
    );
  }

  Widget _buildDpHeaderCell(String label, {required double width}) {
    return SizedBox(
      width: width,
      child: Text(
        label,
        style: const TextStyle(
          color: Color(0xFF94A3B8),
          fontSize: 11,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }

  Widget _buildDpActionBackupRow(
    TraceDpActionBackup backup, {
    required bool showPolicy,
    required bool isSelected,
  }) {
    final terms = backup.transitionTerms
        .map(
          (term) =>
              '${term.probability.toStringAsFixed(2)}*(r ${term.reward.toStringAsFixed(2)} + V ${term.futureValue.toStringAsFixed(2)}) -> ${term.contribution.toStringAsFixed(2)}',
        )
        .join('  ');
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: isSelected ? const Color(0xFF0F2F3A) : const Color(0xFF111827),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isSelected ? const Color(0xFF06B6D4) : const Color(0xFF334155),
          width: isSelected ? 2 : 1,
        ),
      ),
      child: Row(
        children: [
          _buildDpValueCell(backup.actionLabel, width: 86),
          if (showPolicy)
            _buildDpValueCell(
              _formatNullableDouble(backup.policyProbability),
              width: 78,
            ),
          _buildDpValueCell(
            backup.expectedReturn.toStringAsFixed(4),
            width: 94,
          ),
          _buildDpValueCell(
            backup.weightedContribution.toStringAsFixed(4),
            width: 94,
            color: isSelected ? const Color(0xFF06B6D4) : Colors.white,
          ),
          SizedBox(
            width: 360,
            child: Text(
              terms.isEmpty ? 'No model branches recorded.' : terms,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: Color(0xFFCBD5E1),
                fontFamily: 'Courier',
                fontSize: 11,
                height: 1.35,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDpValueCell(
    String value, {
    required double width,
    Color color = Colors.white,
  }) {
    return SizedBox(
      width: width,
      child: Text(
        value,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: TextStyle(
          color: color,
          fontFamily: 'Courier',
          fontSize: 12,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _buildTableInspector(BuildContext context, ExecutionTraceStep step) {
    final table = step.tableSnapshot;
    final mcDetails = step.equationUpdate?.mcDetails;
    if (mcDetails != null && table == null) {
      return _buildMonteCarloInspector(context, mcDetails);
    }
    if (table == null || table.after.isEmpty) {
      return _buildUpdatePanel(context, step);
    }
    final visibleRows = _focusedTableRows(table);
    return _panelShell(
      title: _tableInspectorTitle(table.kind),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              if (table.activeCell != null)
                _buildTag(
                  'active s${table.activeCell!.row}, a${table.activeCell!.column}',
                  const Color(0xFF10B981),
                ),
              if (table.bootstrapCell != null)
                _buildTag(
                  'bootstrap s${table.bootstrapCell!.row}, a${table.bootstrapCell!.column}',
                  const Color(0xFF2DD4BF),
                ),
              _buildTag(
                '${table.after.length} states x ${table.after.first.length} actions',
                const Color(0xFF94A3B8),
              ),
            ],
          ),
          const SizedBox(height: 10),
          _buildJumpToState(table.after.length),
          const SizedBox(height: 12),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildTableHeader(table),
                const SizedBox(height: 6),
                for (final rowIndex in visibleRows)
                  _buildTableRow(context, table, rowIndex),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildJumpToState(int stateCount) {
    return Row(
      children: [
        const Text(
          'Jump to state',
          style: TextStyle(
            color: Color(0xFF94A3B8),
            fontSize: 12,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(width: 10),
        SizedBox(
          width: 96,
          child: TextField(
            keyboardType: TextInputType.number,
            style: const TextStyle(color: Colors.white, fontFamily: 'Courier'),
            decoration: InputDecoration(
              isDense: true,
              hintText: '0–${stateCount - 1}',
              hintStyle: const TextStyle(color: Color(0xFF64748B)),
              filled: true,
              fillColor: const Color(0xFF111827),
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFF334155)),
              ),
            ),
            onSubmitted: (value) {
              final parsed = int.tryParse(value.trim());
              setState(() {
                _jumpState =
                    (parsed != null && parsed >= 0 && parsed < stateCount)
                        ? parsed
                        : null;
              });
            },
          ),
        ),
        if (_jumpState != null) ...[
          const SizedBox(width: 8),
          _buildTag('showing s$_jumpState', const Color(0xFF93C5FD)),
          IconButton(
            tooltip: 'Clear',
            visualDensity: VisualDensity.compact,
            onPressed: () => setState(() => _jumpState = null),
            icon: const Icon(Icons.clear_rounded,
                size: 16, color: Color(0xFF94A3B8)),
          ),
        ],
      ],
    );
  }

  String _tableInspectorTitle(String kind) {
    return switch (kind) {
      'q_table' => 'Q-table Inspector',
      'value_table' => 'Value Table Inspector',
      'policy_table' => 'Policy Table Inspector',
      'returns_table' => 'Returns Table Inspector',
      _ => 'Table Inspector',
    };
  }

  Widget _buildMonteCarloInspector(
    BuildContext context,
    TraceMcDetails details,
  ) {
    return _panelShell(
      title: 'Monte Carlo Episode Inspector',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (details.episodeStrip.isEmpty)
            Text(
              'No episode strip was recorded for this step.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: const Color(0xFFCBD5E1),
                  ),
            )
          else
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  for (final episodeStep in details.episodeStrip)
                    _buildEpisodeStripChip(episodeStep, details.episodeStep),
                ],
              ),
            ),
          if (details.returnTerms.isNotEmpty) ...[
            const SizedBox(height: 14),
            Text(
              'Return ladder',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: const Color(0xFFFDE68A),
                    fontWeight: FontWeight.w800,
                  ),
            ),
            const SizedBox(height: 8),
            _buildReturnLadder(details.returnTerms),
          ],
        ],
      ),
    );
  }

  Widget _buildEpisodeStripChip(
    TraceMcEpisodeStep step,
    int activeStep,
  ) {
    final isActive = step.stepIndex == activeStep;
    final terminal = step.terminated || step.truncated;
    return Container(
      width: 172,
      margin: const EdgeInsets.only(right: 8),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: isActive ? const Color(0xFF172554) : const Color(0xFF111827),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(
          color: terminal
              ? const Color(0xFFF87171)
              : isActive
                  ? const Color(0xFF60A5FA)
                  : const Color(0xFF334155),
          width: isActive || terminal ? 2 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'Step ${step.stepIndex}',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w800,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            step.observation?.label ?? step.state,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: Color(0xFFCBD5E1),
              fontSize: 11,
              height: 1.25,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            '${step.actionLabel} | r ${step.reward.toStringAsFixed(2)}',
            style: TextStyle(
              color: step.reward < 0
                  ? const Color(0xFFF87171)
                  : const Color(0xFFFBBF24),
              fontFamily: 'Courier',
              fontSize: 11,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTableHeader(TraceTableSnapshot table) {
    return Row(
      children: [
        const SizedBox(width: 68),
        for (var column = 0; column < table.after.first.length; column++)
          Container(
            width: 76,
            alignment: Alignment.center,
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: Text(
              column < table.actionLabels.length
                  ? table.actionLabels[column]
                  : 'a$column',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: Color(0xFFCBD5E1),
                fontSize: 11,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildTableRow(
    BuildContext context,
    TraceTableSnapshot table,
    int rowIndex,
  ) {
    final row = table.after[rowIndex];
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          SizedBox(
            width: 68,
            child: Text(
              's$rowIndex',
              style: const TextStyle(
                color: Color(0xFF94A3B8),
                fontFamily: 'Courier',
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          for (var column = 0; column < row.length; column++)
            _buildTableCell(table, rowIndex, column),
        ],
      ),
    );
  }

  Widget _buildTableCell(TraceTableSnapshot table, int row, int column) {
    final value = table.after[row][column];
    final before =
        row < table.before.length && column < table.before[row].length
            ? table.before[row][column]
            : value;
    final active = table.isActive(row, column);
    final bootstrap = table.isBootstrap(row, column);
    final changed = table.isChanged(row, column);
    final fill = _heatmapColor(value);
    return Tooltip(
      message:
          'State $row | Action $column | before ${before.toStringAsFixed(4)} | after ${value.toStringAsFixed(4)}',
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        width: 76,
        margin: const EdgeInsets.only(right: 6),
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 8),
        decoration: BoxDecoration(
          color: fill,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            width: active || bootstrap ? 2 : 1,
            color: active
                ? const Color(0xFF10B981)
                : bootstrap
                    ? const Color(0xFF2DD4BF)
                    : changed
                        ? const Color(0xFFFBBF24)
                        : const Color(0xFF334155),
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              value.toStringAsFixed(2),
              style: const TextStyle(
                color: Colors.white,
                fontFamily: 'Courier',
                fontSize: 12,
                fontWeight: FontWeight.w800,
              ),
            ),
            if (changed)
              Text(
                '${before.toStringAsFixed(2)} ->',
                style: const TextStyle(
                  color: Color(0xFFE2E8F0),
                  fontFamily: 'Courier',
                  fontSize: 9,
                ),
              ),
          ],
        ),
      ),
    );
  }

  List<int> _focusedTableRows(TraceTableSnapshot table) {
    final focusRows = <int>{
      if (table.activeCell != null) table.activeCell!.row,
      if (table.bootstrapCell != null) table.bootstrapCell!.row,
      if (_jumpState != null) _jumpState!,
      ...table.changedCells.map((cell) => cell.row),
    }.where((row) => row >= 0 && row < table.after.length).toList()
      ..sort();
    if (focusRows.isEmpty) {
      return [
        for (var index = 0; index < table.after.length && index < 8; index++)
          index,
      ];
    }
    final expanded = <int>{};
    for (final row in focusRows) {
      for (var index = row - 1; index <= row + 1; index++) {
        if (index >= 0 && index < table.after.length) {
          expanded.add(index);
        }
      }
    }
    return expanded.toList()..sort();
  }

  Color _heatmapColor(double value) {
    if (value < -0.01) {
      return Color.lerp(
        const Color(0xFF111827),
        const Color(0xFF991B1B),
        (-value).clamp(0.0, 1.0),
      )!;
    }
    if (value > 0.01) {
      return Color.lerp(
        const Color(0xFF111827),
        const Color(0xFF047857),
        value.clamp(0.0, 1.0),
      )!;
    }
    return const Color(0xFF111827);
  }

  String _formatNullableDouble(double? value) {
    if (value == null) {
      return 'n/a';
    }
    return value.toStringAsFixed(4);
  }

  String _formatScalar(Object? value) {
    if (value is num) {
      return value.toStringAsFixed(4);
    }
    return value?.toString() ?? 'n/a';
  }

  String _formatDoubleList(List<double> values) {
    if (values.isEmpty) {
      return 'n/a';
    }
    return values.map((value) => value.toStringAsFixed(2)).join(', ');
  }

  Widget _buildUpdatePanel(BuildContext context, ExecutionTraceStep step) {
    final entries = step.updatedValues.entries.toList(growable: false);
    return _panelShell(
      title: '4. Value Update',
      child: entries.isEmpty
          ? Text(
              'No explicit update was recorded for this step.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: const Color(0xFFCBD5E1),
                  ),
            )
          : Column(
              children: entries
                  .map(
                    (entry) => Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0xFF111827),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              entry.key,
                              style: Theme.of(context)
                                  .textTheme
                                  .titleMedium
                                  ?.copyWith(
                                    color: Colors.white,
                                  ),
                            ),
                          ),
                          Text(
                            entry.value.toStringAsFixed(4),
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  color: const Color(0xFFFDE68A),
                                  fontWeight: FontWeight.w700,
                                ),
                          ),
                        ],
                      ),
                    ),
                  )
                  .toList(growable: false),
            ),
    );
  }

  Widget _buildWaitingPanel(BuildContext context) {
    return _panelShell(
      title: 'Generated Replay',
      child: Text(
        'Run code to see replay steps here.',
        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: Colors.white,
              height: 1.5,
            ),
      ),
    );
  }

  Widget _buildManimReplayPanel(BuildContext context) {
    final controller = _replayController;
    final isReady = controller?.value.isInitialized ?? false;
    final isPlaying = controller?.value.isPlaying ?? false;

    return _panelShell(
      title: 'Manim Equation Replay',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Generated video links each agent step to the Bellman or TD numeric update.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFFE2E8F0),
                  height: 1.45,
                ),
          ),
          const SizedBox(height: 14),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Container(
              color: Colors.black,
              child: AspectRatio(
                aspectRatio: isReady ? controller!.value.aspectRatio : 16 / 9,
                child: isReady && controller != null
                    ? _buildReplayVideoSurface(controller, isPlaying)
                    : _buildReplayVideoPlaceholder(context),
              ),
            ),
          ),
          const SizedBox(height: 12),
          _buildReplayVideoControls(context, controller, isReady, isPlaying),
        ],
      ),
    );
  }

  Widget _buildReplayVideoSurface(
    VideoPlayerController controller,
    bool isPlaying,
  ) {
    return Stack(
      fit: StackFit.expand,
      children: [
        FittedBox(
          fit: BoxFit.contain,
          child: SizedBox(
            width: controller.value.size.width,
            height: controller.value.size.height,
            child: VideoPlayer(controller),
          ),
        ),
        Positioned.fill(
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: _toggleReplayPlayback,
              child: AnimatedOpacity(
                duration: const Duration(milliseconds: 180),
                opacity: isPlaying ? 0 : 1,
                child: const Center(
                  child: Icon(
                    Icons.play_circle_fill_rounded,
                    color: Colors.white,
                    size: 82,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildReplayVideoPlaceholder(BuildContext context) {
    final message = _isReplayVideoLoading
        ? 'Preparing generated replay video...'
        : (_replayVideoError ??
            widget.replayRenderError ??
            _renderStatusMessage());
    return Container(
      alignment: Alignment.center,
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (_isReplayVideoLoading)
            const CircularProgressIndicator(color: Color(0xFF38BDF8))
          else
            const Icon(
              Icons.ondemand_video_outlined,
              color: Color(0xFF94A3B8),
              size: 42,
            ),
          const SizedBox(height: 12),
          Text(
            message,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFFE2E8F0),
                ),
          ),
          if (!_isReplayVideoLoading) ...[
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: _initializeReplayVideo,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Retry'),
            ),
          ],
        ],
      ),
    );
  }

  String _renderStatusMessage() {
    return switch (widget.replayRenderStatus) {
      'queued' =>
        'The generated MP4 is queued. Use the interactive trace meanwhile.',
      'rendering' =>
        'The generated MP4 is rendering. Use the interactive trace meanwhile.',
      'failed' =>
        'The generated MP4 failed, but the interactive trace is ready.',
      'timeout' => 'The generated MP4 is still running in the background.',
      'unavailable' =>
        'Interactive replay is available. Generated video is not ready.',
      _ => 'Generated replay video is not ready.',
    };
  }

  Widget _buildReplayVideoControls(
    BuildContext context,
    VideoPlayerController? controller,
    bool isReady,
    bool isPlaying,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF111827),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              IconButton.filled(
                onPressed: isReady ? _toggleReplayPlayback : null,
                icon: Icon(
                  isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  _replayTimelineLabel(controller),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ),
              Text(
                isPlaying ? 'Playing' : 'Paused',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: const Color(0xFFCBD5E1),
                      fontWeight: FontWeight.w600,
                    ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          if (isReady && controller != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(999),
              child: VideoProgressIndicator(
                controller,
                allowScrubbing: true,
                padding: EdgeInsets.zero,
                colors: const VideoProgressColors(
                  playedColor: Color(0xFF38BDF8),
                  bufferedColor: Color(0xFF1D4ED8),
                  backgroundColor: Color(0xFF334155),
                ),
              ),
            )
          else
            Container(
              height: 6,
              decoration: BoxDecoration(
                color: const Color(0xFF334155),
                borderRadius: BorderRadius.circular(999),
              ),
            ),
        ],
      ),
    );
  }

  String _replayTimelineLabel(VideoPlayerController? controller) {
    if (controller == null || !controller.value.isInitialized) {
      return _isReplayVideoLoading
          ? 'Loading generated replay...'
          : 'Replay unavailable';
    }
    return '${_formatDuration(controller.value.position)} / ${_formatDuration(controller.value.duration)}';
  }

  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = duration.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  Widget _buildReadGuide(BuildContext context, bool hasTrace) {
    if (_guideDismissed) {
      return const SizedBox.shrink();
    }
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.info_outline_rounded,
                  color: Color(0xFF93C5FD), size: 20),
              const SizedBox(width: 10),
              const Expanded(
                child: Text(
                  'How to read this replay',
                  style: TextStyle(
                    color: Color(0xFFE2E8F0),
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              if (hasTrace)
                IconButton(
                  tooltip: _guideExpanded ? 'Collapse' : 'Show the steps',
                  visualDensity: VisualDensity.compact,
                  onPressed: () =>
                      setState(() => _guideExpanded = !_guideExpanded),
                  icon: Icon(
                    _guideExpanded
                        ? Icons.expand_less_rounded
                        : Icons.expand_more_rounded,
                    color: const Color(0xFF93C5FD),
                  ),
                ),
              IconButton(
                tooltip: 'Dismiss',
                visualDensity: VisualDensity.compact,
                onPressed: () => setState(() => _guideDismissed = true),
                icon: const Icon(Icons.close_rounded, color: Color(0xFF94A3B8)),
              ),
            ],
          ),
          if (!hasTrace)
            const Padding(
              padding: EdgeInsets.only(left: 30, top: 2),
              child: Text(
                'Replay becomes active after you Run your code.',
                style: TextStyle(color: Color(0xFFCBD5E1), height: 1.4),
              ),
            )
          else if (_guideExpanded) ...[
            const SizedBox(height: 8),
            _guideStep(
                '1', 'Environment', 'where the agent is and what it just did'),
            _guideStep('2', 'Code',
                'the exact line running at this step (highlighted)'),
            _guideStep(
                '3', 'Math', 'the numbers that line plugs into the update'),
            _guideStep('4', 'Predict',
                'flip on Quiz to guess each step before it reveals'),
          ] else
            const Padding(
              padding: EdgeInsets.only(left: 30, top: 2),
              child: Text(
                'Step through environment → code → math. '
                'Expand for the full guide.',
                style: TextStyle(color: Color(0xFFCBD5E1), height: 1.4),
              ),
            ),
        ],
      ),
    );
  }

  Widget _guideStep(String number, String title, String body) {
    return Padding(
      padding: const EdgeInsets.only(left: 30, top: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 20,
            height: 20,
            alignment: Alignment.center,
            decoration: const BoxDecoration(
              color: Color(0xFF1D4ED8),
              shape: BoxShape.circle,
            ),
            child: Text(
              number,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: const TextStyle(
                  color: Color(0xFFCBD5E1),
                  height: 1.4,
                  fontSize: 13,
                ),
                children: [
                  TextSpan(
                    text: '$title — ',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  TextSpan(text: body),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricsPanel(BuildContext context) {
    return _panelShell(
      title: 'Run Metrics',
      child: Wrap(
        spacing: 12,
        runSpacing: 12,
        children: [
          _metricCard('Total reward', widget.totalReward.toStringAsFixed(2)),
          _metricCard(
            'Average reward',
            widget.averageReward.toStringAsFixed(2),
          ),
          _metricCard(
            'Best episode',
            widget.bestEpisodeReward.toStringAsFixed(2),
          ),
        ],
      ),
    );
  }

  Widget _metricCard(String label, String value) {
    return Container(
      width: 140,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF111827),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: Color(0xFF94A3B8),
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorPanel(BuildContext context) {
    return _panelShell(
      title: 'Execution Status',
      child: Text(
        widget.statusMessage,
        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: const Color(0xFFFCA5A5),
              height: 1.5,
            ),
      ),
    );
  }

  Widget _buildSampleTests(BuildContext context) {
    return _panelShell(
      title: 'Sample Test Results',
      child: Column(
        children: widget.testResults
            .map(
              (result) => Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: result.passed
                      ? const Color(0xFF052E2B)
                      : const Color(0xFF3F1D20),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          result.passed
                              ? Icons.check_circle_outline_rounded
                              : Icons.error_outline_rounded,
                          color: result.passed
                              ? const Color(0xFF6EE7B7)
                              : const Color(0xFFFCA5A5),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            result.name,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      result.message,
                      style: const TextStyle(
                        color: Color(0xFFE2E8F0),
                        height: 1.4,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Expected: ${result.expected}',
                      style: const TextStyle(color: Color(0xFFCBD5E1)),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Actual: ${result.actual}',
                      style: const TextStyle(color: Color(0xFFCBD5E1)),
                    ),
                  ],
                ),
              ),
            )
            .toList(growable: false),
      ),
    );
  }

  Widget _panelShell({
    required String title,
    required Widget child,
  }) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final boundedHeight = constraints.hasBoundedHeight;
        // When bounded, fill and scroll internally. When unbounded (inside a
        // scroll view), size to content with MainAxisSize.min — never
        // IntrinsicHeight, which cannot measure a LayoutBuilder child.
        final content = Column(
          mainAxisSize: boundedHeight ? MainAxisSize.max : MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w700,
                fontSize: 18,
              ),
            ),
            const SizedBox(height: 14),
            if (boundedHeight)
              Expanded(
                child: SingleChildScrollView(
                  child: child,
                ),
              )
            else
              child,
          ],
        );

        return Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF0F172A),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFF1E293B)),
          ),
          child: content,
        );
      },
    );
  }
}
