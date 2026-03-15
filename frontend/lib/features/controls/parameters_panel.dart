import 'package:flutter/material.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';

class ParametersPanel extends StatefulWidget {
  final double learningRate;
  final double discountFactor;
  final double explorationRate;
  final int episodeCount;
  final RunMode runMode;
  final ValueChanged<double> onLearningRateChanged;
  final ValueChanged<double> onDiscountFactorChanged;
  final ValueChanged<double> onExplorationRateChanged;
  final ValueChanged<String> onEpisodeCountChanged;
  final ValueChanged<RunMode?> onRunModeChanged;

  const ParametersPanel({
    super.key,
    required this.learningRate,
    required this.discountFactor,
    required this.explorationRate,
    required this.episodeCount,
    required this.runMode,
    required this.onLearningRateChanged,
    required this.onDiscountFactorChanged,
    required this.onExplorationRateChanged,
    required this.onEpisodeCountChanged,
    required this.onRunModeChanged,
  });

  @override
  State<ParametersPanel> createState() => _ParametersPanelState();
}

class _ParametersPanelState extends State<ParametersPanel> {
  late final TextEditingController _episodesController;

  @override
  void initState() {
    super.initState();
    _episodesController = TextEditingController(
      text: widget.episodeCount.toString(),
    );
  }

  @override
  void didUpdateWidget(covariant ParametersPanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    final expected = widget.episodeCount.toString();
    if (_episodesController.text != expected) {
      _episodesController.value = TextEditingValue(
        text: expected,
        selection: TextSelection.collapsed(offset: expected.length),
      );
    }
  }

  @override
  void dispose() {
    _episodesController.dispose();
    super.dispose();
  }

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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Parameters',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 24),
          _buildSlider(
            context,
            'Learning rate α',
            widget.learningRate,
            widget.onLearningRateChanged,
          ),
          const SizedBox(height: 16),
          _buildSlider(
            context,
            'Discount γ',
            widget.discountFactor,
            widget.onDiscountFactorChanged,
          ),
          const SizedBox(height: 16),
          _buildSlider(
            context,
            'Exploration ε',
            widget.explorationRate,
            widget.onExplorationRateChanged,
          ),
          const SizedBox(height: 24),
          Text('Episodes', style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 8),
          TextField(
            controller: _episodesController,
            keyboardType: TextInputType.number,
            onChanged: widget.onEpisodeCountChanged,
            decoration: InputDecoration(
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: AppTheme.borderLight),
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 12,
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text('Run mode', style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(
              border: Border.all(color: AppTheme.borderLight),
              borderRadius: BorderRadius.circular(8),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: widget.runMode == RunMode.simulation
                    ? 'Simulation'
                    : 'Hardware',
                isExpanded: true,
                items: ['Simulation', 'Hardware'].map((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
                onChanged: (value) => widget.onRunModeChanged(
                  value == 'Simulation'
                      ? RunMode.simulation
                      : RunMode.hardware,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSlider(
    BuildContext context,
    String label,
    double value,
    ValueChanged<double> onChanged,
  ) {
    return Column(
      children: [
        Row(
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
            Text(
              value.toStringAsFixed(2),
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderThemeData(
            activeTrackColor: Colors.black,
            inactiveTrackColor: AppTheme.borderLight,
            thumbColor: Colors.white,
            overlayColor: Colors.black.withOpacity(0.1),
            trackHeight: 12,
            thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 10),
          ),
          child: Slider(
            value: value,
            onChanged: onChanged,
          ),
        ),
      ],
    );
  }
}
