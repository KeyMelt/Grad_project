import 'dart:math' as math;
import 'package:flutter/material.dart';

/// The Reinfource dot-matrix "R" mark, reproduced from the brand identity spec.
///
/// [foreground] is the dot color — use [AppColors.light] on dark backgrounds,
/// [AppColors.navy] on light backgrounds.
/// [accent] is the teal or amber highlight dot color.
class ReinfourceMark extends StatelessWidget {
  final double size;
  final Color foreground;
  final Color accent;

  const ReinfourceMark({
    super.key,
    required this.size,
    this.foreground = const Color(0xFFF4F7FC),
    this.accent = const Color(0xFF00C9A7),
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _MarkPainter(foreground: foreground, accent: accent),
      ),
    );
  }
}

/// The horizontal brand lockup: mark + "Reinfource" wordmark side by side.
class ReinfourceLockup extends StatelessWidget {
  final double markSize;
  final double fontSize;
  final Color color;
  final Color accent;

  const ReinfourceLockup({
    super.key,
    this.markSize = 40,
    this.fontSize = 32,
    this.color = const Color(0xFFF4F7FC),
    this.accent = const Color(0xFF00C9A7),
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        ReinfourceMark(size: markSize, foreground: color, accent: accent),
        SizedBox(width: markSize * 0.3),
        _Wordmark(fontSize: fontSize, color: color, accent: accent),
      ],
    );
  }
}

/// "Reinfource" text with the teal accent band through the "i".
class _Wordmark extends StatelessWidget {
  final double fontSize;
  final Color color;
  final Color accent;

  const _Wordmark({
    required this.fontSize,
    required this.color,
    required this.accent,
  });

  @override
  Widget build(BuildContext context) {
    final style = TextStyle(
      fontSize: fontSize,
      fontWeight: FontWeight.w600,
      letterSpacing: -0.025 * fontSize,
      height: 1,
      color: color,
    );
    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.baseline,
      textBaseline: TextBaseline.alphabetic,
      children: [
        Text('Re', style: style),
        ShaderMask(
          shaderCallback: (bounds) => LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            stops: const [0.0, 0.07, 0.07, 0.22, 0.22, 1.0],
            colors: [color, color, accent, accent, color, color],
          ).createShader(bounds),
          blendMode: BlendMode.srcIn,
          child: Text('i', style: style),
        ),
        Text('nfource', style: style),
      ],
    );
  }
}

class _MarkPainter extends CustomPainter {
  final Color foreground;
  final Color accent;

  // Dot positions in the SVG 0–100 space (viewBox "-3 -3 106 106").
  static const _xs = [11.0, 30.0, 50.0, 70.0, 89.0];
  static const _ys = [9.0, 25.0, 41.0, 57.0, 73.0, 89.0];

  // "R" pattern: 1 = filled square, 0 = ghost dot.
  static const _pat = [
    [1, 1, 1, 1, 0],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 0, 0],
    [1, 0, 0, 1, 0],
    [1, 0, 0, 0, 1],
  ];

  const _MarkPainter({required this.foreground, required this.accent});

  @override
  void paint(Canvas canvas, Size size) {
    // viewBox is "-3 -3 106 106", so map 106 SVG units → canvas width.
    final scale = size.width / 106.0;

    canvas.save();
    final cx = size.width / 2;
    final cy = size.height / 2;
    canvas.translate(cx, cy);
    canvas.rotate(-2.5 * math.pi / 180.0);
    canvas.translate(-cx, -cy);

    for (int r = 0; r < 6; r++) {
      for (int c = 0; c < 5; c++) {
        // Offset by +3 to compensate for viewBox minX/minY = -3.
        final x = (_xs[c] + 3) * scale;
        final y = (_ys[r] + 3) * scale;
        final filled = _pat[r][c] == 1;
        final isTeal = r == 5 && c == 4;
        final t = (c + r) / 9.0;
        final d = math.sqrt(math.pow(c - 4, 2) + math.pow(r - 5, 2));
        final tint = (1.0 - d / 2.5).clamp(0.0, 1.0) * 0.42;

        if (isTeal) {
          final hsT = 11.0 * scale;
          final ringPaint = Paint()
            ..color = accent.withValues(alpha: 0.4)
            ..style = PaintingStyle.stroke
            ..strokeWidth = 1.4 * scale;
          canvas.drawRRect(
            RRect.fromRectAndRadius(
              Rect.fromCenter(
                  center: Offset(x, y), width: hsT * 2.5, height: hsT * 2.5),
              Radius.circular(hsT * 0.5),
            ),
            ringPaint,
          );
          // Soft glow behind the dot.
          final glowPaint = Paint()
            ..color = accent.withValues(alpha: 0.5)
            ..maskFilter = MaskFilter.blur(BlurStyle.normal, 3.5 * scale);
          final dotRect = RRect.fromRectAndRadius(
            Rect.fromCenter(
                center: Offset(x, y), width: hsT * 2, height: hsT * 2),
            Radius.circular(hsT * 0.38),
          );
          canvas.drawRRect(dotRect, glowPaint);
          canvas.drawRRect(dotRect, Paint()..color = accent);
        } else if (filled) {
          final hs = (5.0 + t * 3.2) * scale;
          final opacity = (0.65 + t * 0.35).clamp(0.0, 1.0);
          final cellColor =
              tint > 0.04 ? Color.lerp(foreground, accent, tint)! : foreground;
          canvas.drawRRect(
            RRect.fromRectAndRadius(
              Rect.fromCenter(
                  center: Offset(x, y), width: hs * 2, height: hs * 2),
              const Radius.circular(2.5),
            ),
            Paint()..color = cellColor.withValues(alpha: opacity),
          );
        } else {
          // Ghost dot — very subtle.
          final radius = (1.2 + t * 1.4) * scale;
          final opacity = (0.14 + t * 0.16).clamp(0.0, 1.0);
          final ghostColor =
              tint > 0.06 ? Color.lerp(foreground, accent, tint * 0.55)! : foreground;
          canvas.drawCircle(
            Offset(x, y),
            radius,
            Paint()..color = ghostColor.withValues(alpha: opacity),
          );
        }
      }
    }

    canvas.restore();
  }

  @override
  bool shouldRepaint(_MarkPainter old) =>
      old.foreground != foreground || old.accent != accent;
}
