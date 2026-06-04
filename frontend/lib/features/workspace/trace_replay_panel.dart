import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_math_fork/flutter_math.dart';
import 'package:flutter/services.dart';
import 'package:video_player/video_player.dart';

import '../../core/backend_api.dart';
import '../../core/theme.dart';

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
  final List<int> replayEpisodeIndices;
  final List<ExecutionTestCaseResult> testResults;
  final List<ExecutionTraceStep> stepTrace;
  final List<ExecutionTraceEpisode> traceEpisodes;
  final List<ExecutionEpisodeSummary> episodeSummaries;

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
    this.replayEpisodeIndices = const [],
    required this.testResults,
    required this.stepTrace,
    this.traceEpisodes = const [],
    this.episodeSummaries = const [],
  });

  @override
  State<TraceReplayPanel> createState() => _TraceReplayPanelState();
}

class _TraceReplayPanelState extends State<TraceReplayPanel> {
  int _selectedEpisodeIndex = 0;
  int _currentStepIndex = 0;
  int _selectedMobilePane = 0;
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
      const Duration(milliseconds: 1200),
      (_) {
        if (!mounted || _currentEpisodeSteps.isEmpty) {
          _stopTracePlayback();
          return;
        }
        if (_currentStepIndex >= _currentEpisodeSteps.length - 1) {
          _stopTracePlayback();
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
    setState(() => _currentStepIndex = index.clamp(0, lastIndex));
  }

  void _selectEpisode(int episodeIndex) {
    _stopTracePlayback();
    setState(() {
      _selectedEpisodeIndex = episodeIndex;
      _currentStepIndex = 0;
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
          color: AppTheme.navyDeep,
          borderRadius: BorderRadius.circular(14),
          border:
              Border.all(color: AppTheme.primaryBlue.withValues(alpha: 0.22)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(12),
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
          _buildCompactControlBar(context, hasTrace: false),
          const SizedBox(height: 12),
          Expanded(child: _buildWaitingPanel(context)),
        ],
      );
    }
    if (isWide) {
      return _buildDesktopReplayDashboard(context, step);
    }
    return _buildMobileReplayDashboard(context, step);
  }

  Widget _buildDesktopReplayDashboard(
    BuildContext context,
    ExecutionTraceStep step,
  ) {
    return Column(
      children: [
        _buildCompactControlBar(context, hasTrace: true),
        const SizedBox(height: 12),
        Expanded(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                flex: 6,
                child: Column(
                  children: [
                    Expanded(
                        child:
                            _scrollPane(_buildEnvironmentPanel(context, step))),
                    const SizedBox(height: 10),
                    SizedBox(height: 190, child: _buildTraceOutline(context)),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Expanded(flex: 6, child: _buildDetailTabs(context, step)),
              const SizedBox(width: 12),
              SizedBox(width: 310, child: _buildSecondaryDrawer(context, step)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMobileReplayDashboard(
    BuildContext context,
    ExecutionTraceStep step,
  ) {
    return Column(
      children: [
        _buildCompactControlBar(context, hasTrace: true),
        const SizedBox(height: 10),
        Expanded(
          child: DefaultTabController(
            length: 5,
            child: Column(
              children: [
                _buildReplayTabBar(
                  const ['Env', 'Code', 'Math', 'Table', 'Video'],
                ),
                const SizedBox(height: 10),
                Expanded(
                  child: TabBarView(
                    children: [
                      _scrollPane(_buildEnvironmentPanel(context, step)),
                      _scrollPane(_buildCodePanel(context, step)),
                      _scrollPane(_buildMathPanel(context, step)),
                      _scrollPane(_buildTableInspector(context, step)),
                      _scrollPane(_buildSecondaryDrawer(context, step)),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCompactControlBar(
    BuildContext context, {
    required bool hasTrace,
  }) {
    final steps = _currentEpisodeSteps;
    final step = hasTrace && steps.isNotEmpty ? steps[_currentStepIndex] : null;
    final renderLabel = _renderStatusLabel();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppTheme.navy,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppTheme.primaryBlue.withValues(alpha: 0.25)),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxWidth < 760;
          final controls = Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              IconButton.outlined(
                tooltip: 'Previous step',
                onPressed: hasTrace && _currentStepIndex > 0
                    ? () => _selectTraceStep(_currentStepIndex - 1)
                    : null,
                icon: const Icon(Icons.chevron_left_rounded),
              ),
              const SizedBox(width: 6),
              IconButton.filled(
                tooltip: _isTracePlaying ? 'Pause trace' : 'Play trace',
                onPressed:
                    hasTrace && steps.length > 1 ? _toggleTracePlayback : null,
                icon: Icon(
                  _isTracePlaying
                      ? Icons.pause_rounded
                      : Icons.play_arrow_rounded,
                ),
              ),
              const SizedBox(width: 6),
              IconButton.outlined(
                tooltip: 'Next step',
                onPressed: hasTrace && _currentStepIndex < steps.length - 1
                    ? () => _selectTraceStep(_currentStepIndex + 1)
                    : null,
                icon: const Icon(Icons.chevron_right_rounded),
              ),
            ],
          );
          final chips = Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildTag(widget.runStatusLabel, AppTheme.primaryBlue),
              if (hasTrace)
                _buildTag('Step ${_currentStepIndex + 1} / ${steps.length}',
                    AppTheme.light),
              if (step != null)
                _buildTag(
                    'r ${step.reward.toStringAsFixed(2)}', AppTheme.amber),
              _buildTag(renderLabel, _renderStatusColor()),
            ],
          );
          final episodeSelector = _hasMultipleEpisodes
              ? ConstrainedBox(
                  constraints:
                      BoxConstraints(maxWidth: compact ? double.infinity : 210),
                  child: _buildEpisodeSelector(context, fillWidth: compact),
                )
              : _buildTag(
                  'Episodes ${widget.episodesCompleted}', AppTheme.primaryBlue);

          if (compact) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Generated Step Replay',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: AppTheme.light,
                        fontWeight: FontWeight.w900,
                      ),
                ),
                const SizedBox(height: 8),
                Row(children: [Expanded(child: episodeSelector), controls]),
                const SizedBox(height: 8),
                chips,
              ],
            );
          }
          return Row(
            children: [
              Text(
                'Generated Step Replay',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: AppTheme.light,
                      fontWeight: FontWeight.w900,
                    ),
              ),
              const SizedBox(width: 12),
              SizedBox(width: 220, child: episodeSelector),
              const SizedBox(width: 10),
              controls,
              const SizedBox(width: 10),
              Expanded(child: chips),
            ],
          );
        },
      ),
    );
  }

  Widget _buildDetailTabs(BuildContext context, ExecutionTraceStep step) {
    return DefaultTabController(
      length: 4,
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: AppTheme.navy,
          borderRadius: BorderRadius.circular(10),
          border:
              Border.all(color: AppTheme.primaryBlue.withValues(alpha: 0.18)),
        ),
        child: Column(
          children: [
            _buildReplayTabBar(const ['Code', 'Math', 'Table', 'Why']),
            const SizedBox(height: 10),
            Expanded(
              child: TabBarView(
                children: [
                  _scrollPane(_buildCodePanel(context, step)),
                  _scrollPane(_buildMathPanel(context, step)),
                  _scrollPane(_buildTableInspector(context, step)),
                  _scrollPane(_buildCurrentStepSummary(context, step)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReplayTabBar(List<String> labels) {
    return Container(
      height: 38,
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(
        color: AppTheme.navyDeep,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.primaryBlue.withValues(alpha: 0.18)),
      ),
      child: TabBar(
        indicator: BoxDecoration(
          color: AppTheme.primaryBlue.withValues(alpha: 0.18),
          borderRadius: BorderRadius.circular(6),
        ),
        indicatorSize: TabBarIndicatorSize.tab,
        dividerColor: Colors.transparent,
        labelColor: AppTheme.primaryBlue,
        unselectedLabelColor: AppTheme.light.withValues(alpha: 0.72),
        labelStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 12),
        tabs: labels.map((label) => Tab(text: label)).toList(growable: false),
      ),
    );
  }

  Widget _buildSecondaryDrawer(BuildContext context, ExecutionTraceStep step) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: AppTheme.navy,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppTheme.primaryBlue.withValues(alpha: 0.18)),
      ),
      child: ListView(
        children: [
          _buildRenderStatusPanel(context),
          if (widget.videoPath.isNotEmpty) ...[
            const SizedBox(height: 10),
            _buildManimReplayPanel(context),
          ],
          const SizedBox(height: 10),
          _buildMetricsPanel(context),
          const SizedBox(height: 10),
          _buildUpdatePanel(context, step),
          if (widget.runStatusLabel == 'Failed') ...[
            const SizedBox(height: 10),
            _buildErrorPanel(context),
          ],
          if (widget.testResults.isNotEmpty) ...[
            const SizedBox(height: 10),
            _buildSampleTests(context),
          ],
        ],
      ),
    );
  }

  Widget _buildRenderStatusPanel(BuildContext context) {
    return _panelShell(
      title: 'Replay Video',
      child: Text(
        widget.videoPath.isNotEmpty
            ? 'Generated video is ready.'
            : widget.replayRenderError ?? _renderStatusMessage(),
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppTheme.light,
              height: 1.35,
            ),
      ),
    );
  }

  Widget _scrollPane(Widget child) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(10),
      child: SingleChildScrollView(
        child: child,
      ),
    );
  }

  String _renderStatusLabel() {
    if (widget.videoPath.isNotEmpty) {
      return 'Video ready';
    }
    return switch (widget.replayRenderStatus) {
      'queued' => 'Video queued',
      'rendering' => 'Video rendering',
      'failed' => 'Video failed',
      'timeout' => 'Video pending',
      'unavailable' => 'Trace only',
      _ => widget.replayRenderStatus == 'idle'
          ? 'Trace only'
          : widget.replayRenderStatus,
    };
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
      _ => 'Interactive replay is available. Generated video is not ready.',
    };
  }

  Color _renderStatusColor() {
    if (widget.videoPath.isNotEmpty) {
      return AppTheme.successGreen;
    }
    return switch (widget.replayRenderStatus) {
      'queued' || 'rendering' || 'timeout' => AppTheme.amber,
      'failed' => const Color(0xFFEF4444),
      _ => AppTheme.light,
    };
  }

  // ignore: unused_element
  Widget _buildStepToolbar(BuildContext context) {
    final steps = _currentEpisodeSteps;
    final totalSteps = steps.length;
    final step = steps[_currentStepIndex];
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isCompact = constraints.maxWidth < 720;
          final controls = Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Tooltip(
                message: 'Previous step',
                child: IconButton.outlined(
                  onPressed: _currentStepIndex > 0
                      ? () => _selectTraceStep(_currentStepIndex - 1)
                      : null,
                  icon: const Icon(Icons.chevron_left_rounded),
                ),
              ),
              const SizedBox(width: 8),
              Tooltip(
                message: _isTracePlaying ? 'Pause trace' : 'Play trace',
                child: IconButton.filled(
                  onPressed: totalSteps > 1 ? _toggleTracePlayback : null,
                  icon: Icon(
                    _isTracePlaying
                        ? Icons.pause_rounded
                        : Icons.play_arrow_rounded,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Tooltip(
                message: 'Next step',
                child: IconButton.outlined(
                  onPressed: _currentStepIndex < totalSteps - 1
                      ? () => _selectTraceStep(_currentStepIndex + 1)
                      : null,
                  icon: const Icon(Icons.chevron_right_rounded),
                ),
              ),
            ],
          );
          final summary = Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildTag('Step ${_currentStepIndex + 1} / $totalSteps',
                  const Color(0xFF38BDF8)),
              _buildTag('s${step.state} -> ${step.nextState}',
                  const Color(0xFF7DD3FC)),
              _buildTag(
                'a${step.action}',
                const Color(0xFF06B6D4),
              ),
              _buildTag(
                'r ${step.reward.toStringAsFixed(2)}',
                step.reward < 0
                    ? const Color(0xFFF87171)
                    : const Color(0xFFFBBF24),
              ),
            ],
          );
          if (isCompact) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (_hasMultipleEpisodes) ...[
                  _buildEpisodeSelector(context, fillWidth: true),
                  const SizedBox(height: 10),
                ],
                Row(
                  children: [
                    controls,
                    const SizedBox(width: 12),
                    Expanded(child: summary),
                  ],
                ),
                const SizedBox(height: 10),
                _buildStepSlider(totalSteps),
              ],
            );
          }
          return Row(
            children: [
              controls,
              const SizedBox(width: 16),
              if (_hasMultipleEpisodes) ...[
                _buildEpisodeSelector(context),
                const SizedBox(width: 16),
              ],
              Expanded(child: _buildStepSlider(totalSteps)),
              const SizedBox(width: 16),
              summary,
            ],
          );
        },
      ),
    );
  }

  bool get _hasMultipleEpisodes =>
      widget.traceEpisodes.length > 1 || widget.episodeSummaries.length > 1;

  Widget _buildEpisodeSelector(
    BuildContext context, {
    bool fillWidth = false,
  }) {
    final episodeIndexes = _episodeIndexes;
    return Semantics(
      label: 'Trace episode selector',
      button: true,
      child: SizedBox(
        width: fillWidth ? double.infinity : 280,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10),
          decoration: BoxDecoration(
            color: const Color(0xFF111827),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFF334155)),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<int>(
              isExpanded: true,
              value: episodeIndexes.contains(_selectedEpisodeIndex)
                  ? _selectedEpisodeIndex
                  : episodeIndexes.last,
              dropdownColor: const Color(0xFF111827),
              iconEnabledColor: const Color(0xFF93C5FD),
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w700,
              ),
              items: [
                for (final index in episodeIndexes)
                  DropdownMenuItem<int>(
                    value: index,
                    child: Text(
                      _episodeLabel(index),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
              ],
              onChanged: (value) {
                if (value != null) {
                  _selectEpisode(value);
                }
              },
            ),
          ),
        ),
      ),
    );
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
    return Semantics(
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
        onChanged:
            totalSteps > 1 ? (value) => _selectTraceStep(value.round()) : null,
      ),
    );
  }

  // ignore: unused_element
  Widget _buildDesktopDebugger(
    BuildContext context,
    ExecutionTraceStep step,
  ) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 5,
          child: _buildEnvironmentPanel(context, step),
        ),
        const SizedBox(width: 16),
        Expanded(
          flex: 6,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildCurrentStepSummary(context, step),
              const SizedBox(height: 16),
              _buildMathPanel(context, step),
              const SizedBox(height: 16),
              _buildCodePanel(context, step),
            ],
          ),
        ),
      ],
    );
  }

  // ignore: unused_element
  Widget _buildMobileDebuggerTabs(
    BuildContext context,
    ExecutionTraceStep step,
  ) {
    final panes = <({IconData icon, String label, Widget child})>[
      (
        icon: Icons.insights_rounded,
        label: 'Summary',
        child: _buildCurrentStepSummary(context, step),
      ),
      (
        icon: Icons.public_rounded,
        label: 'Environment',
        child: _buildEnvironmentPanel(context, step),
      ),
      (
        icon: Icons.functions_rounded,
        label: 'Equation',
        child: _buildMathPanel(context, step),
      ),
      (
        icon: Icons.grid_on_rounded,
        label: 'Table',
        child: _buildTableInspector(context, step),
      ),
      (
        icon: Icons.code_rounded,
        label: 'Code',
        child: _buildCodePanel(context, step),
      ),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: ToggleButtons(
            isSelected: [
              for (var index = 0; index < panes.length; index++)
                index == _selectedMobilePane,
            ],
            borderRadius: BorderRadius.circular(10),
            selectedColor: Colors.white,
            color: const Color(0xFFCBD5E1),
            fillColor: const Color(0xFF1D4ED8),
            borderColor: const Color(0xFF334155),
            selectedBorderColor: const Color(0xFF60A5FA),
            onPressed: (index) => setState(() => _selectedMobilePane = index),
            children: [
              for (final pane in panes)
                Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(pane.icon, size: 18),
                      const SizedBox(width: 6),
                      Text(pane.label),
                    ],
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        panes[_selectedMobilePane].child,
      ],
    );
  }

  // ignore: unused_element
  Widget _buildBottomInspector(
    BuildContext context,
    ExecutionTraceStep step, {
    required bool isWide,
  }) {
    if (!isWide) {
      return _buildTraceOutline(context);
    }
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 6,
          child: _buildTableInspector(context, step),
        ),
        const SizedBox(width: 16),
        Expanded(
          flex: 5,
          child: _buildTraceOutline(context),
        ),
      ],
    );
  }

  // ignore: unused_element
  Widget _buildHeader(BuildContext context, bool hasTrace) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Generated Step Replay',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            hasTrace
                ? 'Step through environment, code, and math together.'
                : 'Run code to generate replay steps.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFFCBD5E1),
                  height: 1.45,
                ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              _buildTag(widget.runStatusLabel, const Color(0xFF38BDF8)),
              _buildTag(
                'Episodes ${widget.episodesCompleted}',
                const Color(0xFF34D399),
              ),
              _buildTag(
                'Steps ${widget.stepsRecorded}',
                const Color(0xFFFBBF24),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTag(String label, Color accent) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: accent.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(8),
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
        height: 100,
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
                  borderRadius: BorderRadius.circular(14),
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
                        borderRadius: BorderRadius.circular(10),
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
            step.agentCaption,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.white,
                  height: 1.45,
                ),
          ),
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
                borderRadius: BorderRadius.circular(12),
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
        ],
      ),
    );
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
                  borderRadius: BorderRadius.circular(14),
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
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
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
                      _buildMetricCard(
                        'Probability (p)',
                        step.transitionProbability.toStringAsFixed(3),
                        const Color(0xFFA7F3D0),
                      ),
                    ],
                  ),
                ],
              );

              if (isWide) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      flex: 4,
                      child: renderWidget,
                    ),
                    const SizedBox(width: 24),
                    Expanded(
                      flex: 5,
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
        color: AppTheme.navyDeep,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: accent.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: AppTheme.light,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              color: AppTheme.light,
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
        borderRadius: BorderRadius.circular(12),
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
        borderRadius: BorderRadius.circular(12),
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
          AspectRatio(
            aspectRatio: aspectRatio,
            child: GridView.builder(
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
            ),
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
      color: AppTheme.navy,
      padding: const EdgeInsets.all(10),
      child: Center(
        child: FittedBox(
          fit: BoxFit.scaleDown,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 240),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.image_not_supported_outlined,
                  color: AppTheme.light,
                  size: 30,
                ),
                const SizedBox(height: 6),
                const Text(
                  'Environment frame unavailable',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: AppTheme.light,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                if (framePath.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    framePath,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: AppTheme.light.withValues(alpha: 0.68),
                      fontSize: 10,
                      height: 1.2,
                    ),
                  ),
                ],
              ],
            ),
          ),
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
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFF111827),
              borderRadius: BorderRadius.circular(12),
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
              borderRadius: BorderRadius.circular(12),
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
        borderRadius: BorderRadius.circular(12),
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
            'Bootstrap source',
            '${update.bootstrapLabel} = ${_formatNullableDouble(update.bootstrapValue)}',
            accent: const Color(0xFF2DD4BF),
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
        borderRadius: BorderRadius.circular(12),
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
        borderRadius: BorderRadius.circular(12),
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
        borderRadius: BorderRadius.circular(10),
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
                        borderRadius: BorderRadius.circular(14),
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
            borderRadius: BorderRadius.circular(16),
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
        : (_replayVideoError ?? 'Generated replay video is not ready.');
    return Container(
      alignment: Alignment.center,
      padding: const EdgeInsets.all(10),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final cramped = constraints.maxHeight < 140;
          return FittedBox(
            fit: BoxFit.scaleDown,
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 240),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (_isReplayVideoLoading)
                    const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(
                        color: AppTheme.primaryBlue,
                        strokeWidth: 2.4,
                      ),
                    )
                  else
                    Icon(
                      Icons.ondemand_video_outlined,
                      color: AppTheme.light.withValues(alpha: 0.72),
                      size: 30,
                    ),
                  const SizedBox(height: 6),
                  Text(
                    message,
                    textAlign: TextAlign.center,
                    maxLines: cramped ? 1 : 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppTheme.light,
                        ),
                  ),
                  if (!_isReplayVideoLoading && !cramped) ...[
                    const SizedBox(height: 8),
                    OutlinedButton.icon(
                      onPressed: _initializeReplayVideo,
                      icon: const Icon(Icons.refresh_rounded),
                      label: const Text('Retry'),
                    ),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
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
        borderRadius: BorderRadius.circular(14),
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

  // ignore: unused_element
  Widget _buildReadGuide(BuildContext context, bool hasTrace) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(
            Icons.info_outline_rounded,
            color: Color(0xFF93C5FD),
            size: 20,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              hasTrace
                  ? 'Move step by step. Check environment, code, then math.'
                  : 'Replay becomes active after Run.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: const Color(0xFFE2E8F0),
                    height: 1.45,
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
        borderRadius: BorderRadius.circular(14),
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
                  borderRadius: BorderRadius.circular(14),
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
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppTheme.navy,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppTheme.primaryBlue.withValues(alpha: 0.18)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: AppTheme.light,
              fontWeight: FontWeight.w700,
              fontSize: 18,
            ),
          ),
          const SizedBox(height: 14),
          child,
        ],
      ),
    );
  }
}
