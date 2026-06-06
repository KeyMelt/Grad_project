import 'package:flutter/material.dart';

/// Visualises a temporal-difference update as a *fractional step* toward the
/// target: the value moves from `oldValue` only part of the way to `target`
/// (the amount is the learning rate times the TD error). Makes the "TD nudges,
/// it doesn't jump" intuition visceral, complementing the numeric rows.
class TraceTdErrorBar extends StatelessWidget {
  final double oldValue;
  final double newValue;
  final double target;
  final double? tdError;

  const TraceTdErrorBar({
    super.key,
    required this.oldValue,
    required this.newValue,
    required this.target,
    this.tdError,
  });

  @override
  Widget build(BuildContext context) {
    final gap = target - oldValue;
    final move = newValue - oldValue;
    final frac = gap.abs() < 1e-9 ? 0.0 : (move / gap).clamp(0.0, 1.0);
    final delta = tdError ?? gap;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Flexible(child: _chip('old', oldValue, const Color(0xFF94A3B8))),
            const SizedBox(width: 8),
            Text(
              'δ = ${delta >= 0 ? '+' : ''}${delta.toStringAsFixed(3)}',
              style: const TextStyle(
                color: Color(0xFFFDE68A),
                fontFamily: 'Courier',
                fontWeight: FontWeight.w800,
                fontSize: 12,
              ),
            ),
            const SizedBox(width: 8),
            Flexible(
              child: Align(
                alignment: Alignment.centerRight,
                child: _chip('target', target, const Color(0xFF2DD4BF)),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        LayoutBuilder(
          builder: (context, constraints) {
            final width = constraints.maxWidth;
            return Stack(
              alignment: Alignment.centerLeft,
              children: [
                // full track: old .. target
                Container(
                  height: 8,
                  decoration: BoxDecoration(
                    color: const Color(0xFF1F2937),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: const Color(0xFF334155)),
                  ),
                ),
                // moved portion: old .. new (the actual alpha step)
                Container(
                  height: 8,
                  width: (width * frac).clamp(0.0, width),
                  decoration: BoxDecoration(
                    color: const Color(0xFF34D399),
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
              ],
            );
          },
        ),
        const SizedBox(height: 6),
        Text(
          'new = ${newValue.toStringAsFixed(3)} — a ${(frac * 100).round()}% step toward the target',
          style: const TextStyle(
            color: Color(0xFFCBD5E1),
            fontSize: 11,
            height: 1.3,
          ),
        ),
      ],
    );
  }

  Widget _chip(String label, double value, Color color) {
    return Text(
      '$label ${value.toStringAsFixed(3)}',
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
      style: TextStyle(
        color: color,
        fontFamily: 'Courier',
        fontSize: 11,
        fontWeight: FontWeight.w700,
      ),
    );
  }
}
