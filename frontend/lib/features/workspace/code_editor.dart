import 'package:flutter/material.dart';

import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';
import 'python_highlighting_controller.dart';

class CodeEditorTab extends StatefulWidget {
  final LessonDefinition lesson;
  final String code;
  final String statusMessage;
  final String runStatusLabel;
  final ValueChanged<String> onChanged;
  final VoidCallback onRun;
  final VoidCallback onStop;
  final VoidCallback onReset;

  const CodeEditorTab({
    super.key,
    required this.lesson,
    required this.code,
    required this.statusMessage,
    required this.runStatusLabel,
    required this.onChanged,
    required this.onRun,
    required this.onStop,
    required this.onReset,
  });

  @override
  State<CodeEditorTab> createState() => _CodeEditorTabState();
}

class _CodeEditorTabState extends State<CodeEditorTab> {
  late final PythonHighlightingController _controller;
  late final ScrollController _terminalScrollController;
  final List<String> _terminalLines = <String>[];
  double _terminalRatio = 0.30;

  @override
  void initState() {
    super.initState();
    _controller = PythonHighlightingController(text: widget.code);
    _terminalScrollController = ScrollController();
    _appendTerminalLine('rl-studio\$ workspace ready for ${widget.lesson.id}.py');
    _appendTerminalLine('[${_clockNow()}] ${widget.runStatusLabel}: ${widget.statusMessage}');
  }

  @override
  void didUpdateWidget(covariant CodeEditorTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.code != widget.code && _controller.text != widget.code) {
      _controller.value = TextEditingValue(
        text: widget.code,
        selection: TextSelection.collapsed(offset: widget.code.length),
      );
    }

    if (oldWidget.runStatusLabel != widget.runStatusLabel ||
        oldWidget.statusMessage != widget.statusMessage) {
      if (widget.runStatusLabel == 'Running') {
        _appendTerminalLine('rl-studio\$ run ${widget.lesson.id}.py');
      }
      _appendTerminalLine('[${_clockNow()}] ${widget.runStatusLabel}: ${widget.statusMessage}');
    }
  }

  @override
  void dispose() {
    _terminalScrollController.dispose();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 16, 18, 8),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    '${widget.lesson.title} Exercise',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ),
                Text(
                  'Settings are defined in code constants',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.textSecondary,
                      ),
                ),
              ],
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(
                AppConstants.defaultPadding,
                0,
                AppConstants.defaultPadding,
                AppConstants.defaultPadding,
              ),
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF111827),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFF1F2937)),
                ),
                child: LayoutBuilder(
                  builder: (context, constraints) {
                    final availableHeight = constraints.maxHeight - 12;
                    final minCodeHeight = availableHeight > 360 ? 200.0 : 140.0;
                    final minTerminalHeight =
                        availableHeight > 360 ? 130.0 : 110.0;
                    final maxTerminalHeight =
                        (availableHeight - minCodeHeight).clamp(minTerminalHeight, availableHeight);
                    final terminalHeight = (availableHeight * _terminalRatio)
                        .clamp(minTerminalHeight, maxTerminalHeight);
                    final codeHeight = availableHeight - terminalHeight;

                    return Column(
                      children: [
                        SizedBox(
                          height: codeHeight,
                          child: _buildCodeWorkspace(context),
                        ),
                        GestureDetector(
                          behavior: HitTestBehavior.opaque,
                          onVerticalDragUpdate: (details) {
                            setState(() {
                              final nextRatio = _terminalRatio +
                                  (details.delta.dy / availableHeight);
                              _terminalRatio = nextRatio.clamp(0.18, 0.55);
                            });
                          },
                          child: Container(
                            height: 12,
                            alignment: Alignment.center,
                            child: Container(
                              width: 56,
                              height: 4,
                              decoration: BoxDecoration(
                                color: const Color(0xFF475569),
                                borderRadius: BorderRadius.circular(999),
                              ),
                            ),
                          ),
                        ),
                        SizedBox(
                          height: terminalHeight,
                          child: _buildTerminalPane(context),
                        ),
                      ],
                    );
                  },
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCodeWorkspace(BuildContext context) {
    final statusVisual = _statusVisualFor(widget.runStatusLabel);
    return Container(
      margin: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF1F2937)),
      ),
      child: Column(
        children: [
          Container(
            height: 50,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: const BoxDecoration(
              color: Color(0xFF111827),
              borderRadius: BorderRadius.vertical(top: Radius.circular(14)),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 7,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1F2937),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    '${widget.lesson.id}.py',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: const Color(0xFFE5E7EB),
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ),
                const Spacer(),
                _EditorActionButton(
                  onPressed: widget.lesson.backendEnabled ? widget.onRun : null,
                  icon: Icons.play_arrow_rounded,
                  label: 'Run',
                  variant: _EditorActionVariant.primary,
                ),
                const SizedBox(width: 8),
                _EditorActionButton(
                  onPressed: widget.onStop,
                  icon: Icons.stop_rounded,
                  label: 'Stop',
                ),
                const SizedBox(width: 8),
                _EditorActionButton(
                  onPressed: widget.onReset,
                  icon: Icons.refresh_rounded,
                  label: 'Reset',
                ),
                const SizedBox(width: 10),
                Text(
                  '${_lineCount(_controller.text)} lines',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: const Color(0xFF94A3B8),
                      ),
                ),
              ],
            ),
          ),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: const BoxDecoration(
              color: Color(0xFF0F172A),
            ),
            child: Row(
              children: [
                Icon(
                  statusVisual.icon,
                  size: 15,
                  color: statusVisual.color,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${widget.runStatusLabel}: ${widget.statusMessage}',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: statusVisual.color,
                          fontWeight: FontWeight.w600,
                        ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
          const Divider(color: Color(0xFF1F2937), height: 1),
          Expanded(
            child: TextField(
              controller: _controller,
              expands: true,
              maxLines: null,
              minLines: null,
              onChanged: widget.onChanged,
              decoration: const InputDecoration(
                border: InputBorder.none,
                contentPadding: EdgeInsets.all(14),
              ),
              style: const TextStyle(
                fontFamily: 'Courier',
                fontSize: 14,
                color: Color(0xFFE5E7EB),
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTerminalPane(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(14, 0, 14, 14),
      decoration: BoxDecoration(
        color: const Color(0xFF040B17),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Column(
        children: [
          Container(
            height: 34,
            padding: const EdgeInsets.symmetric(horizontal: 10),
            decoration: const BoxDecoration(
              color: Color(0xFF0F172A),
              borderRadius: BorderRadius.vertical(top: Radius.circular(14)),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.terminal_rounded,
                  size: 16,
                  color: Color(0xFF7DD3FC),
                ),
                const SizedBox(width: 8),
                Text(
                  'Execution Terminal',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: const Color(0xFFE2E8F0),
                        fontWeight: FontWeight.w600,
                      ),
                ),
                const Spacer(),
                IconButton(
                  tooltip: 'Clear terminal',
                  onPressed: () {
                    setState(() {
                      _terminalLines.clear();
                      _appendTerminalLine(
                        'rl-studio\$ terminal cleared',
                        autoScroll: false,
                      );
                    });
                  },
                  icon: const Icon(
                    Icons.delete_sweep_outlined,
                    color: Color(0xFF94A3B8),
                    size: 18,
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              controller: _terminalScrollController,
              padding: const EdgeInsets.all(12),
              itemCount: _terminalLines.length,
              itemBuilder: (context, index) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text(
                    _terminalLines[index],
                    style: const TextStyle(
                      fontFamily: 'Courier',
                      fontSize: 12.8,
                      color: Color(0xFFCFD9E8),
                      height: 1.45,
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  void _appendTerminalLine(String message, {bool autoScroll = true}) {
    _terminalLines.add(message);
    if (!autoScroll || !_terminalScrollController.hasClients) {
      return;
    }
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_terminalScrollController.hasClients) {
        return;
      }
      _terminalScrollController.animateTo(
        _terminalScrollController.position.maxScrollExtent + 44,
        duration: const Duration(milliseconds: 180),
        curve: Curves.easeOut,
      );
    });
  }

  String _clockNow() {
    final now = DateTime.now();
    final h = now.hour.toString().padLeft(2, '0');
    final m = now.minute.toString().padLeft(2, '0');
    final s = now.second.toString().padLeft(2, '0');
    return '$h:$m:$s';
  }

  int _lineCount(String source) {
    return source.isEmpty ? 0 : source.split('\n').length;
  }

  _RunVisual _statusVisualFor(String status) {
    switch (status) {
      case 'Running':
        return const _RunVisual(
          color: Color(0xFF60A5FA),
          icon: Icons.autorenew_rounded,
        );
      case 'Complete':
        return const _RunVisual(
          color: Color(0xFF34D399),
          icon: Icons.check_circle_outline_rounded,
        );
      case 'Failed':
        return const _RunVisual(
          color: Color(0xFFFCA5A5),
          icon: Icons.error_outline_rounded,
        );
      case 'Stopped':
        return const _RunVisual(
          color: Color(0xFFD8B4FE),
          icon: Icons.stop_circle_outlined,
        );
      default:
        return const _RunVisual(
          color: Color(0xFFCBD5E1),
          icon: Icons.hourglass_empty_rounded,
        );
    }
  }
}

class _RunVisual {
  final Color color;
  final IconData icon;

  const _RunVisual({
    required this.color,
    required this.icon,
  });
}

enum _EditorActionVariant { primary, neutral }

class _EditorActionButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final IconData icon;
  final String label;
  final _EditorActionVariant variant;

  const _EditorActionButton({
    required this.onPressed,
    required this.icon,
    required this.label,
    this.variant = _EditorActionVariant.neutral,
  });

  @override
  Widget build(BuildContext context) {
    final bool enabled = onPressed != null;
    final bool primary = variant == _EditorActionVariant.primary;
    final Color background = !enabled
        ? const Color(0xFF1E293B)
        : (primary ? AppTheme.primaryBlue : const Color(0xFF1F2937));
    final Color foreground = !enabled
        ? const Color(0xFF64748B)
        : const Color(0xFFE2E8F0);

    return Material(
      color: background,
      borderRadius: BorderRadius.circular(9),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(9),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 15, color: foreground),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  color: foreground,
                  fontSize: 12.5,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
