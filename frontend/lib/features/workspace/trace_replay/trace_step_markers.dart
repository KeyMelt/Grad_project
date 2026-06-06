import 'package:flutter/material.dart';

enum TraceMarkerKind { rewardPositive, rewardNegative, terminal }

/// A thin tick strip rendered just above the step slider, flagging where the
/// reward signal arrives (green/red) and where episodes terminate (red ring).
/// Lets a learner see the sparse-reward structure of a run at a glance instead
/// of scrubbing blindly. Aligned approximately to the Material slider track.
class TraceStepMarkers extends StatelessWidget {
  final int totalSteps;
  final List<({int index, TraceMarkerKind kind})> markers;

  const TraceStepMarkers({
    super.key,
    required this.totalSteps,
    required this.markers,
  });

  @override
  Widget build(BuildContext context) {
    if (totalSteps < 2 || markers.isEmpty) {
      return const SizedBox(height: 8);
    }
    return SizedBox(
      height: 10,
      child: LayoutBuilder(
        builder: (context, constraints) {
          // Material slider reserves ~12px of horizontal padding for the thumb.
          const inset = 12.0;
          final usable = (constraints.maxWidth - inset * 2).clamp(1.0, double.infinity);
          return Stack(
            clipBehavior: Clip.none,
            children: [
              for (final marker in markers)
                Positioned(
                  left: inset +
                      (marker.index / (totalSteps - 1)) * usable -
                      3,
                  top: 1,
                  child: _tick(marker.kind),
                ),
            ],
          );
        },
      ),
    );
  }

  Widget _tick(TraceMarkerKind kind) {
    final color = switch (kind) {
      TraceMarkerKind.rewardPositive => const Color(0xFF34D399),
      TraceMarkerKind.rewardNegative => const Color(0xFFF87171),
      TraceMarkerKind.terminal => const Color(0xFFFBBF24),
    };
    final isRing = kind == TraceMarkerKind.terminal;
    return Container(
      width: 6,
      height: 6,
      decoration: BoxDecoration(
        color: isRing ? Colors.transparent : color,
        shape: BoxShape.circle,
        border: Border.all(color: color, width: isRing ? 1.6 : 0.0),
      ),
    );
  }
}
