import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_math_fork/flutter_math.dart';

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

  @override
  void didUpdateWidget(covariant TraceReplayPanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!listEquals(oldWidget.stepTrace, widget.stepTrace)) {
      _currentStepIndex = 0;
    } else if (_currentStepIndex >= widget.stepTrace.length &&
        widget.stepTrace.isNotEmpty) {
      _currentStepIndex = widget.stepTrace.length - 1;
    }
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
            if (hasTrace) ...[
              _buildStepNavigator(context),
              const SizedBox(height: 18),
              _buildEnvironmentPanel(context, step!),
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
            if (widget.videoPath.isNotEmpty) ...[
              const SizedBox(height: 18),
              _buildExportPanel(context),
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
                  max: (totalSteps - 1).toDouble(),
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

  Widget _buildEnvironmentPanel(BuildContext context, ExecutionTraceStep step) {
    return _panelShell(
      title: '1. Agent and Environment',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AspectRatio(
            aspectRatio: 1.0,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: _buildFrameImage(step.framePath),
            ),
          ),
          const SizedBox(height: 14),
          Text(
            step.agentCaption,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.white,
                  height: 1.5,
                ),
          ),
          const SizedBox(height: 10),
          Text(
            'State ${step.state} -> ${step.nextState}    Reward ${step.reward.toStringAsFixed(2)}    p=${step.transitionProbability.toStringAsFixed(3)}',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFF94A3B8),
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildFrameImage(String framePath) {
    if (!kIsWeb && framePath.isNotEmpty && File(framePath).existsSync()) {
      return Image.file(
        File(framePath),
        fit: BoxFit.cover,
      );
    }

    return Container(
      color: const Color(0xFF1E293B),
      child: const Center(
        child: Icon(
          Icons.grid_4x4_rounded,
          color: Color(0xFF64748B),
          size: 56,
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
          ...step.codeLines.map(
            (line) => Container(
              width: double.infinity,
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(
                color: const Color(0xFF111827),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                line,
                style: const TextStyle(
                  color: Color(0xFFE5E7EB),
                  fontFamily: 'Courier',
                  fontSize: 13,
                  height: 1.45,
                ),
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
            child: Math.tex(
              step.mathEquation.isEmpty
                  ? r"\text{No\ equation\ provided}"
                  : step.mathEquation,
              textStyle: const TextStyle(
                color: Colors.white,
                fontSize: 18,
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

  Widget _buildExportPanel(BuildContext context) {
    return _panelShell(
      title: 'Exported Render',
      child: SelectableText(
        widget.videoPath,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.white,
            ),
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
