import 'package:flutter/material.dart';
import '../../core/backend_api.dart';
import '../../core/theme.dart';

class VideoPlayerTab extends StatelessWidget {
  final String lessonTitle;
  final String runStatusLabel;
  final String statusMessage;
  final double totalReward;
  final double averageReward;
  final double bestEpisodeReward;
  final int episodesCompleted;
  final int stepsRecorded;
  final String videoPath;
  final List<ExecutionTestCaseResult> testResults;

  const VideoPlayerTab({
    super.key,
    required this.lessonTitle,
    required this.runStatusLabel,
    required this.statusMessage,
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
    return Container(
      color: AppTheme.backgroundLight,
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: AppTheme.primaryBlue.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.play_arrow,
                  size: 40,
                  color: AppTheme.primaryBlue,
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'Visualization: $lessonTitle',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 12),
              Text(
                runStatusLabel,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: AppTheme.primaryBlue,
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const SizedBox(height: 8),
              ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 420),
                child: Text(
                  statusMessage,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Total reward: ${totalReward.toStringAsFixed(1)}',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.textPrimary,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Average reward: ${averageReward.toStringAsFixed(1)}',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Episodes completed: $episodesCompleted',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Steps recorded: $stepsRecorded',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Best episode: ${bestEpisodeReward.toStringAsFixed(1)}',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 16),
              Text(
                videoPath.isEmpty
                    ? 'Video path: not available yet'
                    : 'Video path: $videoPath',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.textSecondary,
                    ),
              ),
              if (runStatusLabel == 'Failed') ...[
                const SizedBox(height: 24),
                _buildErrorPanel(context),
              ],
              if (testResults.isNotEmpty) ...[
                const SizedBox(height: 24),
                _buildSampleTests(context),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildErrorPanel(BuildContext context) {
    return Container(
      width: 480,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF3F2),
        border: Border.all(color: const Color(0xFFD92D20)),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Execution Error',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: const Color(0xFFB42318),
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            statusMessage,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFFB42318),
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildSampleTests(BuildContext context) {
    return Container(
      width: 520,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        border: Border.all(color: AppTheme.borderLight),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Lesson Sample Tests',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          ...testResults.map((test) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildTestRow(context, test),
              )),
        ],
      ),
    );
  }

  Widget _buildTestRow(BuildContext context, ExecutionTestCaseResult test) {
    final Color accent =
        test.passed ? const Color(0xFF067647) : const Color(0xFFB42318);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: accent.withOpacity(0.06),
        border: Border.all(color: accent.withOpacity(0.25)),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                test.passed ? Icons.check_circle_outline : Icons.highlight_off,
                color: accent,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  test.name,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: accent,
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ),
              Text(
                test.passed ? 'Pass' : 'Fail',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: accent,
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(test.message, style: Theme.of(context).textTheme.bodyMedium),
          if (test.expected.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              'Expected: ${test.expected}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
          if (test.actual.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              'Actual: ${test.actual}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ],
      ),
    );
  }
}
