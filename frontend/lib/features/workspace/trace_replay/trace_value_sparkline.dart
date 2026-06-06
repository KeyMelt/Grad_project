import 'package:flutter/material.dart';

/// A tiny convergence sparkline: plots how one cell's value evolved across the
/// steps that touched it, so learners see the estimate *settle* rather than
/// reading a single isolated number. Pure CustomPainter — no dependencies.
class TraceValueSparkline extends StatelessWidget {
  final List<double> values;
  final String label;

  const TraceValueSparkline({
    super.key,
    required this.values,
    this.label = '',
  });

  @override
  Widget build(BuildContext context) {
    if (values.length < 2) {
      return const SizedBox.shrink();
    }
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  label.isEmpty ? 'Value history' : label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Color(0xFF93C5FD),
                    fontWeight: FontWeight.w800,
                    fontSize: 12,
                  ),
                ),
              ),
              Text(
                '${values.length} updates · now ${values.last.toStringAsFixed(3)}',
                style: const TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 48,
            width: double.infinity,
            child: CustomPaint(painter: _SparklinePainter(values)),
          ),
        ],
      ),
    );
  }
}

class _SparklinePainter extends CustomPainter {
  final List<double> values;

  _SparklinePainter(this.values);

  @override
  void paint(Canvas canvas, Size size) {
    var lo = values.reduce((a, b) => a < b ? a : b);
    var hi = values.reduce((a, b) => a > b ? a : b);
    if ((hi - lo).abs() < 1e-9) {
      lo -= 1;
      hi += 1;
    }
    final range = hi - lo;
    double x(int i) => values.length == 1
        ? size.width / 2
        : i / (values.length - 1) * size.width;
    double y(double v) => size.height - ((v - lo) / range) * size.height;

    // zero baseline if 0 is in range
    if (lo <= 0 && hi >= 0) {
      final zeroY = y(0);
      final basePaint = Paint()
        ..color = const Color(0xFF334155)
        ..strokeWidth = 1;
      canvas.drawLine(Offset(0, zeroY), Offset(size.width, zeroY), basePaint);
    }

    final path = Path()..moveTo(x(0), y(values.first));
    for (var i = 1; i < values.length; i++) {
      path.lineTo(x(i), y(values[i]));
    }
    final linePaint = Paint()
      ..color = const Color(0xFF34D399)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke
      ..strokeJoin = StrokeJoin.round;
    canvas.drawPath(path, linePaint);

    // current (last) point dot
    final dotPaint = Paint()..color = const Color(0xFFFDE68A);
    canvas.drawCircle(
      Offset(x(values.length - 1), y(values.last)),
      3,
      dotPaint,
    );
  }

  @override
  bool shouldRepaint(covariant _SparklinePainter old) =>
      !identical(old.values, values);
}
