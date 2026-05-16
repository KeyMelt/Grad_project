import 'package:flutter/material.dart';

Widget buildWorkspaceShellHost({
  required BuildContext context,
  required String? url,
  required bool workspaceReady,
  required bool isLoading,
  required String placeholderMessage,
}) {
  return _WorkspaceShellPlaceholder(
    isLoading: isLoading,
    message: placeholderMessage,
  );
}

class _WorkspaceShellPlaceholder extends StatelessWidget {
  final bool isLoading;
  final String message;

  const _WorkspaceShellPlaceholder({
    required this.isLoading,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1F2937)),
      ),
      child: Stack(
        children: [
          Positioned.fill(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: const Color(0xFF111827),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFF1F2937)),
                ),
                child: const _PlaceholderLines(
                  padding: EdgeInsets.fromLTRB(20, 22, 20, 120),
                  lineCount: 14,
                  lineWidthScale: <double>[
                    0.90,
                    0.74,
                    0.66,
                    0.82,
                    0.58,
                    0.86,
                    0.64,
                    0.78,
                    0.48,
                    0.88,
                    0.70,
                    0.62,
                    0.80,
                    0.54,
                  ],
                ),
              ),
            ),
          ),
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xCC0B1220),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 340),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (isLoading)
                        const SizedBox(
                          width: 30,
                          height: 30,
                          child: CircularProgressIndicator(strokeWidth: 2.4),
                        )
                      else
                        const Icon(
                          Icons.sync_problem_rounded,
                          size: 34,
                          color: Color(0xFFFCA5A5),
                        ),
                      const SizedBox(height: 14),
                      Text(
                        message,
                        textAlign: TextAlign.center,
                        style: textTheme.bodyMedium?.copyWith(
                          color: const Color(0xFFE2E8F0),
                          fontWeight: FontWeight.w700,
                          height: 1.45,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        isLoading
                            ? 'The workspace shell is still starting.'
                            : 'The embedded workspace shell could not be loaded.',
                        textAlign: TextAlign.center,
                        style: textTheme.bodySmall?.copyWith(
                          color: const Color(0xFF94A3B8),
                          height: 1.45,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          Positioned(
            left: 24,
            right: 24,
            bottom: 20,
            child: Text(
              '>>>',
              style: textTheme.bodyMedium?.copyWith(
                color: const Color(0xFF86EFAC),
                fontFamily: 'Menlo',
                fontFamilyFallback: const ['Monaco', 'Consolas'],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PlaceholderLines extends StatelessWidget {
  final EdgeInsets padding;
  final int lineCount;
  final List<double> lineWidthScale;

  const _PlaceholderLines({
    required this.padding,
    required this.lineCount,
    required this.lineWidthScale,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final availableHeight = (constraints.maxHeight - padding.vertical)
            .clamp(0.0, double.infinity);
        final visibleLineCount = availableHeight <= 0
            ? 0
            : (availableHeight / 22).floor().clamp(1, lineCount);
        return Padding(
          padding: padding,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: List.generate(visibleLineCount, (index) {
              final scale =
                  index < lineWidthScale.length ? lineWidthScale[index] : 0.7;
              return Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Container(
                  height: 12,
                  width: constraints.maxWidth * scale,
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
              );
            }),
          ),
        );
      },
    );
  }
}
