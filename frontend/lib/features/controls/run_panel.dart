import 'package:flutter/material.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';

class RunPanel extends StatelessWidget {
  final int episodeCount;
  final int currentEpisode;
  final int currentStep;
  final String connectionLabel;
  final String runStatusLabel;
  final String statusMessage;
  final double totalReward;
  final VoidCallback onRun;
  final VoidCallback onStop;
  final VoidCallback onReset;

  const RunPanel({
    super.key,
    required this.episodeCount,
    required this.currentEpisode,
    required this.currentStep,
    required this.connectionLabel,
    required this.runStatusLabel,
    required this.statusMessage,
    required this.totalReward,
    required this.onRun,
    required this.onStop,
    required this.onReset,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Run Controls',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: onRun,
            icon: const Icon(Icons.play_arrow_outlined),
            label: const Text('Run'),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onStop,
                  icon: const Icon(Icons.stop_outlined, size: 20),
                  label: const Text('Stop'),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onReset,
                  icon: const Icon(Icons.refresh_outlined, size: 20),
                  label: const Text('Reset'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          const Divider(),
          const SizedBox(height: 24),
          _buildMetricRow(context, 'Episode:', '$currentEpisode / $episodeCount'),
          const SizedBox(height: 12),
          _buildMetricRow(context, 'Step:', '$currentStep'),
          const SizedBox(height: 12),
          _buildMetricRow(
            context,
            'Connection:',
            connectionLabel,
            valueColor: AppTheme.successGreen,
          ),
          const SizedBox(height: 12),
          _buildMetricRow(context, 'Run status:', runStatusLabel),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppTheme.borderLight),
            ),
            child: Row(
              children: [
                const Icon(Icons.show_chart, color: AppTheme.textPrimary),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Metrics',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Text(
                  totalReward.toStringAsFixed(1),
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: AppTheme.primaryBlue,
                      ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Text(
            statusMessage,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.textPrimary,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricRow(
    BuildContext context,
    String label,
    String value, {
    Color? valueColor,
  }) {
    return Row(
      children: [
        Expanded(
          child: Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.textPrimary,
                ),
          ),
        ),
        const SizedBox(width: 12),
        Flexible(
          child: Text(
            value,
            textAlign: TextAlign.right,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: valueColor ?? AppTheme.textPrimary,
                  fontWeight: FontWeight.w500,
                ),
          ),
        ),
      ],
    );
  }
}
