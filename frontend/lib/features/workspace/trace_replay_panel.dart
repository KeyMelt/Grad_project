import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_math_fork/flutter_math.dart';
import 'package:video_player/video_player.dart';

import '../../core/backend_api.dart';

class TraceReplayPanel extends StatefulWidget {
  final String runStatusLabel;
  final String statusMessage;
  final double totalReward;
  final double averageReward;
  final double bestEpisodeReward;
  final int episodesCompleted;
  final int stepsRecorded;
  final String videoPath;
  final List<ExecutionTestCaseResult> testResults;
  final List<ExecutionTraceStep> stepTrace;

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
    required this.testResults,
    required this.stepTrace,
  });

  @override
  State<TraceReplayPanel> createState() => _TraceReplayPanelState();
}

class _TraceReplayPanelState extends State<TraceReplayPanel> {
  int _currentStepIndex = 0;
  VideoPlayerController? _replayController;
  bool _isReplayVideoLoading = false;
  String? _replayVideoError;

  @override
  void initState() {
    super.initState();
    if (widget.videoPath.isNotEmpty) {
      _initializeReplayVideo();
    }
  }

  @override
  void didUpdateWidget(covariant TraceReplayPanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!listEquals(oldWidget.stepTrace, widget.stepTrace)) {
      _currentStepIndex = 0;
    } else if (_currentStepIndex >= widget.stepTrace.length &&
        widget.stepTrace.isNotEmpty) {
      _currentStepIndex = widget.stepTrace.length - 1;
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
    _disposeReplayController();
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
      final controller = VideoPlayerController.networkUrl(uri);
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
    final base = Uri.parse(defaultBackendBaseUrl);
    return base.replace(
      path: '/visualization/video',
      queryParameters: {'path': path},
    );
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

  void _disposeReplayController() {
    _replayController?.removeListener(_onReplayControllerChanged);
    _replayController?.dispose();
    _replayController = null;
  }

  @override
  Widget build(BuildContext context) {
    final hasTrace = widget.stepTrace.isNotEmpty;
    final step = hasTrace ? widget.stepTrace[_currentStepIndex] : null;

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF020617),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(context, hasTrace),
            const SizedBox(height: 12),
            _buildReadGuide(context, hasTrace),
            const SizedBox(height: 18),
            if (widget.videoPath.isNotEmpty) ...[
              _buildManimReplayPanel(context),
              const SizedBox(height: 18),
            ],
            if (hasTrace) ...[
              _buildTraceOutline(context),
              const SizedBox(height: 18),
              _buildStepNavigator(context),
              const SizedBox(height: 18),
              _buildCurrentStepSummary(context, step!),
              const SizedBox(height: 16),
              _buildEnvironmentPanel(context, step),
              const SizedBox(height: 16),
              _buildCodePanel(context, step),
              const SizedBox(height: 16),
              _buildMathPanel(context, step),
              const SizedBox(height: 16),
              _buildUpdatePanel(context, step),
            ] else
              _buildWaitingPanel(context),
            const SizedBox(height: 18),
            _buildMetricsPanel(context),
            if (widget.runStatusLabel == 'Failed') ...[
              const SizedBox(height: 18),
              _buildErrorPanel(context),
            ],
            if (widget.testResults.isNotEmpty) ...[
              const SizedBox(height: 18),
              _buildSampleTests(context),
            ],
          ],
        ),
      ),
    );
  }

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

  Widget _buildStepNavigator(BuildContext context) {
    final totalSteps = widget.stepTrace.length;
    final step = widget.stepTrace[_currentStepIndex];
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
          Row(
            children: [
              Text(
                'Replay Controls',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const Spacer(),
              Text(
                'Step ${_currentStepIndex + 1} of $totalSteps',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: const Color(0xFFCBD5E1),
                    ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              _buildTag('State ${step.state}', const Color(0xFF7DD3FC)),
              _buildTag('Action ${step.action}', const Color(0xFFA7F3D0)),
              _buildTag(
                'Reward ${step.reward.toStringAsFixed(2)}',
                const Color(0xFFFDE68A),
              ),
              _buildTag(
                'Next ${step.nextState}',
                const Color(0xFFC4B5FD),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              OutlinedButton.icon(
                onPressed: _currentStepIndex > 0
                    ? () => setState(() => _currentStepIndex -= 1)
                    : null,
                icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
                label: const Text('Previous'),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Slider(
                  value: _currentStepIndex.toDouble(),
                  min: 0,
                  max: totalSteps > 1 ? (totalSteps - 1).toDouble() : 1.0,
                  divisions: totalSteps > 1 ? totalSteps - 1 : 1,
                  onChanged: totalSteps > 1
                      ? (value) =>
                          setState(() => _currentStepIndex = value.round())
                      : null,
                ),
              ),
              const SizedBox(width: 12),
              ElevatedButton.icon(
                onPressed: _currentStepIndex < totalSteps - 1
                    ? () => setState(() => _currentStepIndex += 1)
                    : null,
                icon: const Icon(Icons.arrow_forward_ios_rounded, size: 18),
                label: const Text('Next'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTraceOutline(BuildContext context) {
    return _panelShell(
      title: 'Trace Outline',
      child: SizedBox(
        height: 132,
        child: ListView.separated(
          scrollDirection: Axis.horizontal,
          itemCount: widget.stepTrace.length,
          separatorBuilder: (_, __) => const SizedBox(width: 10),
          itemBuilder: (context, index) {
            final step = widget.stepTrace[index];
            final isSelected = index == _currentStepIndex;
            return GestureDetector(
              onTap: () => setState(() => _currentStepIndex = index),
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
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12),
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

  Widget _buildFrameImage(String framePath) {
    if (framePath.isNotEmpty) {
      final frameUri = Uri.parse(
        '${BackendConnectionManager().baseUrl}/visualization/frame',
      ).replace(queryParameters: {'path': framePath});
      return Image.network(
        frameUri.toString(),
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
                children: step.codeLines
                    .map(
                      (line) => Text(
                        line,
                        style: const TextStyle(
                          color: Color(0xFFE5E7EB),
                          fontFamily: 'Courier',
                          fontSize: 13,
                          height: 1.45,
                        ),
                      ),
                    )
                    .toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMathPanel(BuildContext context, ExecutionTraceStep step) {
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
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
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
