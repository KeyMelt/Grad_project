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
  final VoidCallback onReconnect;

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
    required this.onReconnect,
  });

  @override
  Widget build(BuildContext context) {
    final hasLocalDraft = code.trim().isNotEmpty;
    final shellLoading =
        editorConnectionStatus == WorkspaceConnectionStatus.connecting ||
            (!workspaceReady && workspaceSessionId == null);
    final shellMessage = shellLoading
        ? 'Connecting to workspace...'
        : 'Connection failed, Try again.';

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE5E7EB)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF111827),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFF1F2937)),
                ),
                child: Column(
                  children: [
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
                        child: WorkspaceShellHost(
                          url: editorShellUrl,
                          workspaceReady: workspaceReady,
                          isLoading: shellLoading,
                          placeholderMessage: shellMessage,
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
                      child: _EditorFooterBar(
                        runStatusLabel: runStatusLabel,
                        statusMessage: statusMessage,
                        scriptVersion: scriptVersion,
                        hasLocalDraft: hasLocalDraft,
                        canUseWorkspace: workspaceSessionId != null,
                        canSubmit:
                            lesson.backendEnabled && workspaceSessionId != null,
                        onSubmit: onSubmit,
                        onStop: onStop,
                        onReset: onReset,
                        onReconnect: onReconnect,
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
}

class _RunStatusFooter extends StatelessWidget {
  final String runStatusLabel;
  final String statusMessage;
  final int scriptVersion;
  final bool hasLocalDraft;

  const _RunStatusFooter({
    required this.runStatusLabel,
    required this.statusMessage,
    required this.scriptVersion,
    required this.hasLocalDraft,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xCC0F172A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            runStatusLabel,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFF93C5FD),
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            statusMessage,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFFE2E8F0),
                  height: 1.4,
                ),
          ),
          const SizedBox(height: 6),
          Text(
            '${hasLocalDraft ? 'Local draft ready' : 'Waiting for draft'} • v$scriptVersion',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFF94A3B8),
                ),
          ),
        ],
      ),
    );
  }
}

class _EditorFooterBar extends StatelessWidget {
  final String runStatusLabel;
  final String statusMessage;
  final int scriptVersion;
  final bool hasLocalDraft;
  final bool canUseWorkspace;
  final bool canSubmit;
  final VoidCallback onSubmit;
  final VoidCallback onStop;
  final VoidCallback onReset;
  final VoidCallback onReconnect;

  const _EditorFooterBar({
    required this.runStatusLabel,
    required this.statusMessage,
    required this.scriptVersion,
    required this.hasLocalDraft,
    required this.canUseWorkspace,
    required this.canSubmit,
    required this.onSubmit,
    required this.onStop,
    required this.onReset,
    required this.onReconnect,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isNarrow = constraints.maxWidth < 720;
        final status = _RunStatusFooter(
          runStatusLabel: runStatusLabel,
          statusMessage: statusMessage,
          scriptVersion: scriptVersion,
          hasLocalDraft: hasLocalDraft,
        );
        final actions = Wrap(
          alignment: WrapAlignment.end,
          spacing: 8,
          runSpacing: 8,
          children: [
            _EditorActionButton(
              onPressed: onReconnect,
              icon: Icons.sync_rounded,
              label: 'Reconnect',
            ),
            _EditorActionButton(
              onPressed: canSubmit ? onSubmit : null,
              icon: Icons.task_alt_rounded,
              label: 'Submit',
              variant: _EditorActionVariant.primary,
            ),
            _EditorActionButton(
              onPressed: canUseWorkspace ? onStop : null,
              icon: Icons.stop_rounded,
              label: 'Stop',
            ),
            _EditorActionButton(
              onPressed: canUseWorkspace ? onReset : null,
              icon: Icons.refresh_rounded,
              label: 'Reset',
            ),
          ],
        );

        if (isNarrow) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              status,
              const SizedBox(height: 10),
              Align(alignment: Alignment.centerRight, child: actions),
            ],
          );
        }

        return Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(child: status),
            const SizedBox(width: 12),
            Flexible(child: actions),
          ],
        );
      },
    );
  }
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
