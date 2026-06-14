import 'package:flutter/material.dart';

import 'trace_step_markers.dart';

class TraceReplaySectionOption<T> {
  final T value;
  final IconData icon;
  final String label;

  const TraceReplaySectionOption({
    required this.value,
    required this.icon,
    required this.label,
  });
}

class TraceReplayTagData {
  final String label;
  final Color accent;

  const TraceReplayTagData({
    required this.label,
    required this.accent,
  });
}

class TraceReplayActionPill {
  final IconData icon;
  final String label;
  final String? tooltip;
  final VoidCallback onTap;
  final bool active;

  const TraceReplayActionPill({
    required this.icon,
    required this.label,
    required this.onTap,
    this.tooltip,
    this.active = false,
  });
}

class TraceReplayEpisodeOption {
  final String label;
  final String tooltip;
  final bool active;
  final VoidCallback onTap;

  const TraceReplayEpisodeOption({
    required this.label,
    required this.tooltip,
    required this.active,
    required this.onTap,
  });
}

class TraceReplayBinderControls<T> extends StatelessWidget {
  final List<TraceReplaySectionOption<T>> options;
  final T selectedValue;
  final ValueChanged<T> onSelected;

  const TraceReplayBinderControls({
    super.key,
    required this.options,
    required this.selectedValue,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    final selector = Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final option in options)
          _sectionPill(
            option,
            option.value == selectedValue,
            () => onSelected(option.value),
          ),
      ],
    );

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: _TraceReplayPalette.panel,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: _TraceReplayPalette.borderSubtle),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(child: selector),
        ],
      ),
    );
  }

  Widget _sectionPill(
    TraceReplaySectionOption<T> option,
    bool active,
    VoidCallback onTap,
  ) {
    return Tooltip(
      message: option.label,
      child: Material(
        color: active ? _TraceReplayPalette.primary : _TraceReplayPalette.raised,
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
                color: active
                    ? _TraceReplayPalette.primary
                    : _TraceReplayPalette.borderStrong,
                width: 1.2,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  option.icon,
                  size: 18,
                  color: active ? Colors.white : _TraceReplayPalette.state,
                ),
                const SizedBox(width: 8),
                Text(
                  option.label,
                  style: TextStyle(
                    color: active ? Colors.white : _TraceReplayPalette.textMed,
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
}

class TraceReplayStepToolbar extends StatelessWidget {
  final int currentStep;
  final int totalSteps;
  final bool isPlaying;
  final int playbackMs;
  final VoidCallback? onPrevious;
  final VoidCallback? onPlayPause;
  final VoidCallback? onNext;
  final ValueChanged<int> onPlaybackSpeedChanged;
  final ValueChanged<double>? onSliderChanged;
  final bool quizMode;
  final VoidCallback onToggleQuiz;
  final List<TraceReplayEpisodeOption> episodeOptions;
  final List<TraceReplayActionPill> jumpPills;
  final List<TraceReplayTagData> transitionTags;
  final List<({int index, TraceMarkerKind kind})> markers;

  const TraceReplayStepToolbar({
    super.key,
    required this.currentStep,
    required this.totalSteps,
    required this.isPlaying,
    required this.playbackMs,
    required this.onPrevious,
    required this.onPlayPause,
    required this.onNext,
    required this.onPlaybackSpeedChanged,
    required this.onSliderChanged,
    required this.quizMode,
    required this.onToggleQuiz,
    required this.episodeOptions,
    required this.jumpPills,
    required this.transitionTags,
    required this.markers,
  });

  @override
  Widget build(BuildContext context) {
    final transport = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _circleIconButton(
          icon: Icons.chevron_left_rounded,
          tooltip: 'Previous step',
          size: 38,
          onTap: onPrevious,
        ),
        const SizedBox(width: 8),
        _circleIconButton(
          icon: isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
          tooltip: isPlaying ? 'Pause trace' : 'Play trace',
          primary: true,
          size: 44,
          onTap: onPlayPause,
        ),
        const SizedBox(width: 8),
        _circleIconButton(
          icon: Icons.chevron_right_rounded,
          tooltip: 'Next step',
          size: 38,
          onTap: onNext,
        ),
      ],
    );

    Widget optionsWrap(WrapAlignment alignment) => Wrap(
          spacing: 8,
          runSpacing: 8,
          alignment: alignment,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            if (episodeOptions.isNotEmpty) _buildEpisodeSelector(),
            ...jumpPills.map(_buildActionPill),
            _buildSpeedSelector(),
            _buildQuizToggle(),
          ],
        );

    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: _TraceReplayPalette.panel,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: _TraceReplayPalette.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          LayoutBuilder(
            builder: (context, constraints) {
              if (constraints.maxWidth < 640) {
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
              _counterChip(),
              const SizedBox(width: 12),
              Expanded(child: _buildStepSlider()),
            ],
          ),
          const SizedBox(height: 6),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              for (final tag in transitionTags) _buildTag(tag.label, tag.accent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEpisodeSelector() {
    return Semantics(
      label: 'Trace episode selector',
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
        decoration: BoxDecoration(
          color: _TraceReplayPalette.control,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: _TraceReplayPalette.borderStrong, width: 1.2),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.only(left: 2, right: 6),
              child: Icon(
                Icons.timeline_rounded,
                size: 16,
                color: _TraceReplayPalette.textLow,
              ),
            ),
            for (final option in episodeOptions)
              Tooltip(
                message: option.tooltip,
                child: Material(
                  color: option.active
                      ? _TraceReplayPalette.primary
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(9),
                  clipBehavior: Clip.antiAlias,
                  child: InkWell(
                    onTap: option.onTap,
                    child: Container(
                      height: 32,
                      alignment: Alignment.center,
                      padding: const EdgeInsets.symmetric(horizontal: 13),
                      child: Text(
                        option.label,
                        style: TextStyle(
                          color: option.active
                              ? Colors.white
                              : _TraceReplayPalette.textMed,
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionPill(TraceReplayActionPill pill) {
    final widget = Material(
      color: pill.active ? _TraceReplayPalette.primary : _TraceReplayPalette.control,
      borderRadius: BorderRadius.circular(6),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: pill.onTap,
        child: Container(
          height: 40,
          padding: const EdgeInsets.symmetric(horizontal: 14),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(6),
            border: Border.all(
              color: pill.active
                  ? _TraceReplayPalette.primary
                  : _TraceReplayPalette.borderStrong,
              width: 1.2,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                pill.icon,
                size: 18,
                color: pill.active ? Colors.white : _TraceReplayPalette.state,
              ),
              const SizedBox(width: 8),
              Text(
                pill.label,
                style: TextStyle(
                  color: pill.active ? Colors.white : _TraceReplayPalette.textHigh,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      ),
    );
    return pill.tooltip == null ? widget : Tooltip(message: pill.tooltip!, child: widget);
  }

  Widget _buildQuizToggle() {
    return _buildActionPill(
      TraceReplayActionPill(
        icon: Icons.psychology_alt_rounded,
        label: 'Quiz',
        tooltip: 'Predict each step before revealing it',
        active: quizMode,
        onTap: onToggleQuiz,
      ),
    );
  }

  Widget _buildSpeedSelector() {
    final label = switch (playbackMs) {
      2400 => '0.5×',
      600 => '2×',
      _ => '1×',
    };
    return Tooltip(
      message: 'Playback speed',
      child: PopupMenuButton<int>(
        initialValue: playbackMs,
        color: _TraceReplayPalette.raised,
        onSelected: onPlaybackSpeedChanged,
        itemBuilder: (context) => const [
          PopupMenuItem(value: 2400, child: Text('0.5× (slow)')),
          PopupMenuItem(value: 1200, child: Text('1× (normal)')),
          PopupMenuItem(value: 600, child: Text('2× (fast)')),
        ],
        child: Container(
          height: 40,
          padding: const EdgeInsets.symmetric(horizontal: 14),
          decoration: BoxDecoration(
            color: _TraceReplayPalette.control,
            borderRadius: BorderRadius.circular(6),
            border: Border.all(color: _TraceReplayPalette.borderStrong, width: 1.2),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.speed_rounded,
                size: 18,
                color: _TraceReplayPalette.state,
              ),
              const SizedBox(width: 8),
              Text(
                label,
                style: const TextStyle(
                  color: _TraceReplayPalette.textHigh,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(width: 4),
              const Icon(
                Icons.arrow_drop_down_rounded,
                size: 18,
                color: _TraceReplayPalette.textLow,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _counterChip() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
      decoration: BoxDecoration(
        color: _TraceReplayPalette.raised,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: _TraceReplayPalette.borderStrong),
      ),
      child: Text.rich(
        TextSpan(
          children: [
            const TextSpan(
              text: 'Step ',
              style: TextStyle(color: _TraceReplayPalette.textLow, fontSize: 12),
            ),
            TextSpan(
              text: '$currentStep',
              style: const TextStyle(
                color: _TraceReplayPalette.state,
                fontWeight: FontWeight.w800,
              ),
            ),
            TextSpan(
              text: ' / $totalSteps',
              style: const TextStyle(
                color: _TraceReplayPalette.textLow,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepSlider() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        TraceStepMarkers(
          totalSteps: totalSteps,
          markers: markers,
        ),
        Semantics(
          label: 'Trace step slider',
          value: 'Step $currentStep of $totalSteps',
          slider: true,
          child: Slider(
            value: (currentStep - 1).toDouble(),
            min: 0,
            max: totalSteps > 1 ? (totalSteps - 1).toDouble() : 1.0,
            divisions: totalSteps > 1 ? totalSteps - 1 : 1,
            semanticFormatterCallback: (value) =>
                'Step ${value.round() + 1} of $totalSteps',
            onChanged: onSliderChanged,
          ),
        ),
      ],
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

  Widget _circleIconButton({
    required IconData icon,
    required VoidCallback? onTap,
    required String tooltip,
    bool primary = false,
    double size = 46,
  }) {
    final enabled = onTap != null;
    final bg = primary ? _TraceReplayPalette.primary : _TraceReplayPalette.raised;
    final fg = primary ? _TraceReplayPalette.primaryText : _TraceReplayPalette.textHigh;
    return Tooltip(
      message: tooltip,
      child: Opacity(
        opacity: enabled ? 1 : 0.38,
        child: Material(
          color: bg,
          shape: CircleBorder(
            side: primary
                ? BorderSide.none
                : const BorderSide(
                    color: _TraceReplayPalette.borderStrong,
                    width: 1.4,
                  ),
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
}

class _TraceReplayPalette {
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
}
