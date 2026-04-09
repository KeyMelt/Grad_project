import 'package:flutter/material.dart';

Widget buildWorkspaceShellHost({
  required BuildContext context,
  required String? url,
  required bool workspaceReady,
  required String fallbackMessage,
}) {
  final message = workspaceReady && url != null
      ? 'Workspace host is not available on this platform.'
      : fallbackMessage;

  return _WorkspaceShellPlaceholder(message: message);
}

class _WorkspaceShellPlaceholder extends StatelessWidget {
  final String message;

  const _WorkspaceShellPlaceholder({
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
      child: Column(
        children: [
          Container(
            height: 44,
            padding: const EdgeInsets.symmetric(horizontal: 14),
            decoration: const BoxDecoration(
              color: Color(0xFF0F172A),
              borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
              border: Border(
                bottom: BorderSide(color: Color(0xFF1F2937)),
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0xFF172554),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    'script.py',
                    style: textTheme.bodySmall?.copyWith(
                      color: const Color(0xFFDBEAFE),
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                const Spacer(),
                _PlaceholderChip(label: 'Editor'),
                const SizedBox(width: 8),
                _PlaceholderChip(label: 'Console'),
              ],
            ),
          ),
          Expanded(
            child: Column(
              children: [
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(14, 14, 14, 10),
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        color: const Color(0xFF111827),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF1F2937)),
                      ),
                      child: const _PlaceholderLines(
                        padding: EdgeInsets.all(16),
                        lineCount: 9,
                        lineWidthScale: <double>[
                          0.88,
                          0.72,
                          0.66,
                          0.79,
                          0.54,
                          0.83,
                          0.58,
                          0.76,
                          0.49,
                        ],
                      ),
                    ),
                  ),
                ),
                SizedBox(
                  height: 168,
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF1F2937)),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Interactive Python console',
                              style: textTheme.bodyMedium?.copyWith(
                                color: const Color(0xFFE5E7EB),
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              message,
                              style: textTheme.bodySmall?.copyWith(
                                color: const Color(0xFF94A3B8),
                                height: 1.45,
                              ),
                            ),
                            const Spacer(),
                            Text(
                              '>>> ',
                              style: textTheme.bodyMedium?.copyWith(
                                color: const Color(0xFF86EFAC),
                                fontFamily: 'Menlo',
                                fontFamilyFallback: const [
                                  'Monaco',
                                  'Consolas'
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PlaceholderChip extends StatelessWidget {
  final String label;

  const _PlaceholderChip({
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFF172033),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: const Color(0xFFCBD5E1),
              fontWeight: FontWeight.w600,
            ),
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
        return Padding(
          padding: padding,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: List.generate(lineCount, (index) {
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
