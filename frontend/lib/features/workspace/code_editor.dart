import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/workbench_state.dart';
import 'workspace_shell_host.dart';

class CodeEditorTab extends StatelessWidget {
  final LessonDefinition lesson;
  final String code;
  final String? workspaceSessionId;
  final bool workspaceReady;
  final WorkspaceConnectionStatus editorConnectionStatus;
  final WorkspaceConnectionStatus consoleConnectionStatus;
  final String? editorShellUrl;
  final String statusMessage;
  final String runStatusLabel;
  final int scriptVersion;
  final VoidCallback onSubmit;
  final VoidCallback onStop;
  final VoidCallback onReset;

  const CodeEditorTab({
    super.key,
    required this.lesson,
    required this.code,
    required this.workspaceSessionId,
    required this.workspaceReady,
    required this.editorConnectionStatus,
    required this.consoleConnectionStatus,
    required this.editorShellUrl,
    required this.statusMessage,
    required this.runStatusLabel,
    required this.scriptVersion,
    required this.onSubmit,
    required this.onStop,
    required this.onReset,
  });

  @override
  Widget build(BuildContext context) {
    final editorStatus = _workspaceStatusLabel(editorConnectionStatus);
    final consoleStatus = _workspaceStatusLabel(consoleConnectionStatus);

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE5E7EB)),
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
                    lesson.exercise.title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ),
                _StatusChip(
                  label: editorStatus.label,
                  color: editorStatus.color,
                ),
                const SizedBox(width: 8),
                _StatusChip(
                  label: 'Console ${consoleStatus.label.toLowerCase()}',
                  color: consoleStatus.color,
                ),
              ],
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(18, 0, 18, 18),
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF111827),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFF1F2937)),
                ),
                child: Column(
                  children: [
                    Container(
                      height: 54,
                      padding: const EdgeInsets.symmetric(horizontal: 14),
                      decoration: const BoxDecoration(
                        color: Color(0xFF0F172A),
                        borderRadius:
                            BorderRadius.vertical(top: Radius.circular(18)),
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
                              'script.py',
                              style: Theme.of(context)
                                  .textTheme
                                  .bodyMedium
                                  ?.copyWith(
                                    color: const Color(0xFFE5E7EB),
                                    fontWeight: FontWeight.w700,
                                  ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            workspaceSessionId == null
                                ? 'No workspace session'
                                : 'v$scriptVersion',
                            style: Theme.of(context)
                                .textTheme
                                .bodySmall
                                ?.copyWith(color: const Color(0xFF94A3B8)),
                          ),
                          const Spacer(),
                          _EditorActionButton(
                            onPressed: lesson.backendEnabled ? onSubmit : null,
                            icon: Icons.task_alt_rounded,
                            label: 'Submit',
                            variant: _EditorActionVariant.primary,
                          ),
                          const SizedBox(width: 8),
                          _EditorActionButton(
                            onPressed: onStop,
                            icon: Icons.stop_rounded,
                            label: 'Stop',
                          ),
                          const SizedBox(width: 8),
                          _EditorActionButton(
                            onPressed: onReset,
                            icon: Icons.refresh_rounded,
                            label: 'Reset',
                          ),
                        ],
                      ),
                    ),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 10,
                      ),
                      decoration: const BoxDecoration(
                        color: Color(0xFF0B1220),
                        border: Border(
                          bottom: BorderSide(color: Color(0xFF1F2937)),
                        ),
                      ),
                      child: Text(
                        '$runStatusLabel: $statusMessage',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: const Color(0xFFCBD5E1),
                              fontWeight: FontWeight.w600,
                            ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: WorkspaceShellHost(
                          url: editorShellUrl,
                          workspaceReady: workspaceReady,
                          fallbackMessage: workspaceReady
                              ? 'Workspace host unavailable for this platform.'
                              : 'Preparing the lesson workspace for ${lesson.title}...',
                        ),
                      ),
                    ),
                    if (!workspaceReady)
                      Padding(
                        padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
                        child: Text(
                          code.trim().isEmpty
                              ? 'Starter code will appear when the workspace session is ready.'
                              : 'Latest starter snapshot loaded while the remote workspace connects.',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: const Color(0xFF94A3B8),
                                  ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  _WorkspaceVisual _workspaceStatusLabel(WorkspaceConnectionStatus status) {
    switch (status) {
      case WorkspaceConnectionStatus.connecting:
        return const _WorkspaceVisual('Connecting', Color(0xFF1D4ED8));
      case WorkspaceConnectionStatus.ready:
        return const _WorkspaceVisual('Ready', Color(0xFF059669));
      case WorkspaceConnectionStatus.failed:
        return const _WorkspaceVisual('Failed', Color(0xFFDC2626));
      case WorkspaceConnectionStatus.disconnected:
        return const _WorkspaceVisual('Offline', Color(0xFF64748B));
    }
  }
}

class _StatusChip extends StatelessWidget {
  final String label;
  final Color color;

  const _StatusChip({
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withOpacity(0.25)),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
            ),
      ),
    );
  }
}

class _WorkspaceVisual {
  final String label;
  final Color color;

  const _WorkspaceVisual(this.label, this.color);
}

enum _EditorActionVariant { normal, primary }

class _EditorActionButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final IconData icon;
  final String label;
  final _EditorActionVariant variant;

  const _EditorActionButton({
    required this.onPressed,
    required this.icon,
    required this.label,
    this.variant = _EditorActionVariant.normal,
  });

  @override
  Widget build(BuildContext context) {
    final isPrimary = variant == _EditorActionVariant.primary;
    return FilledButton.tonalIcon(
      onPressed: onPressed,
      style: FilledButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        backgroundColor:
            isPrimary ? const Color(0xFF2563EB) : const Color(0xFF1F2937),
        foregroundColor: Colors.white,
      ),
      icon: Icon(icon, size: 18),
      label: Text(label),
    );
  }
}
