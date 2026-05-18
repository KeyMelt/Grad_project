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
  final String? failureKind;
  final List<String> unresolvedBlanks;
  final ExecutionStudentFeedback? studentFeedback;
  final List<ExecutionTestCaseResult> testResults;
  final VoidCallback onSubmit;
  final VoidCallback onStop;
  final VoidCallback onReset;
  final VoidCallback onReconnect;
  final VoidCallback? onRun;

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
    required this.failureKind,
    required this.unresolvedBlanks,
    required this.studentFeedback,
    this.testResults = const [],
    required this.onSubmit,
    required this.onStop,
    required this.onReset,
    required this.onReconnect,
    this.onRun,
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
                    if (studentFeedback != null)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
                        decoration: const BoxDecoration(
                          color: Color(0xFF111827),
                          border: Border(
                            bottom: BorderSide(color: Color(0x00000000)),
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _FeedbackPanel(
                              failureKind: failureKind,
                              feedback: studentFeedback!,
                            ),
                          ],
                        ),
                      ),
                    if (studentFeedback != null || testResults.isNotEmpty)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.fromLTRB(12, 10, 12, 0),
                        decoration: const BoxDecoration(
                          color: Color(0xFF111827),
                          border: Border(
                            bottom: BorderSide(color: Color(0x00000000)),
                          ),
                        ),
                        child: _EvaluationSummaryPanel(
                          lesson: lesson,
                          failureKind: failureKind,
                          unresolvedBlanks: unresolvedBlanks,
                          testResults: testResults,
                        ),
                      ),
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
                        onRun: onRun,
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
  final VoidCallback? onRun;

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
    this.onRun,
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
              onPressed: canUseWorkspace ? onRun : null,
              icon: Icons.play_arrow_rounded,
              label: 'Run',
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

class _FeedbackPanel extends StatelessWidget {
  final String? failureKind;
  final ExecutionStudentFeedback feedback;

  const _FeedbackPanel({
    required this.failureKind,
    required this.feedback,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            failureKind == 'incomplete_template'
                ? 'Fill the remaining blanks'
                : 'Submission feedback',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 6),
          Text(
            feedback.summary,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFFCBD5E1),
                ),
          ),
          if (feedback.likelyIssue.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              feedback.likelyIssue,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: const Color(0xFF94A3B8),
                  ),
            ),
          ],
          if (feedback.nextSteps.isNotEmpty) ...[
            const SizedBox(height: 8),
            for (final step in feedback.nextSteps)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  '• $step',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: const Color(0xFFE2E8F0),
                      ),
                ),
              ),
          ],
        ],
      ),
    );
  }
}

class _EvaluationSummaryPanel extends StatelessWidget {
  final LessonDefinition lesson;
  final String? failureKind;
  final List<String> unresolvedBlanks;
  final List<ExecutionTestCaseResult> testResults;

  const _EvaluationSummaryPanel({
    required this.lesson,
    required this.failureKind,
    required this.unresolvedBlanks,
    required this.testResults,
  });

  @override
  Widget build(BuildContext context) {
    final passedTests = testResults.where((result) => result.passed).length;
    final failedTests = testResults.length - passedTests;
    final allTestsPassed = testResults.isNotEmpty && failedTests == 0;
    final hasEvaluation = failureKind != null ||
        testResults.isNotEmpty ||
        unresolvedBlanks.isNotEmpty;

    final verdict = _buildVerdict(
      hasEvaluation: hasEvaluation,
      allTestsPassed: allTestsPassed,
      failedTests: failedTests,
    );

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: verdict.color.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(verdict.icon, color: verdict.color, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  verdict.title,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ),
              if (testResults.isNotEmpty)
                Text(
                  '$passedTests/${testResults.length} checks passed',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: const Color(0xFFCBD5E1),
                        fontWeight: FontWeight.w600,
                      ),
                ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            verdict.subtitle,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFFCBD5E1),
                  height: 1.45,
                ),
          ),
          if (unresolvedBlanks.isNotEmpty) ...[
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: unresolvedBlanks
                  .map(
                    (blankId) => Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFF3F1D1D),
                        borderRadius: BorderRadius.circular(999),
                      ),
                      child: Text(
                        blankId,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: const Color(0xFFFCA5A5),
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                    ),
                  )
                  .toList(growable: false),
            ),
          ],
          if (testResults.isNotEmpty) ...[
            const SizedBox(height: 12),
            ...testResults.map(
              (result) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF111827),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: result.passed
                          ? const Color(0xFF065F46)
                          : const Color(0xFF7F1D1D),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            result.passed
                                ? Icons.check_circle_rounded
                                : Icons.cancel_rounded,
                            size: 16,
                            color: result.passed
                                ? const Color(0xFF34D399)
                                : const Color(0xFFFCA5A5),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              result.name,
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(
                                    color: Colors.white,
                                    fontWeight: FontWeight.w700,
                                  ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        result.message,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: const Color(0xFFCBD5E1),
                              height: 1.4,
                            ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
          if (lesson.exercise.successCriteria.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              'Target behavior',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: const Color(0xFF94A3B8),
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 6),
            ...lesson.exercise.successCriteria.map(
              (criterion) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  '• $criterion',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: const Color(0xFFE2E8F0),
                        height: 1.4,
                      ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  _EvaluationVerdict _buildVerdict({
    required bool hasEvaluation,
    required bool allTestsPassed,
    required int failedTests,
  }) {
    if (failureKind == 'incomplete_template') {
      return const _EvaluationVerdict(
        title: 'Template still incomplete',
        subtitle:
            'The submission still contains guided blanks, so it is not ready for correctness evaluation yet.',
        color: Color(0xFFF59E0B),
        icon: Icons.rule_folder_outlined,
      );
    }
    if (allTestsPassed) {
      return const _EvaluationVerdict(
        title: 'Current submission satisfies the lesson checks',
        subtitle:
            'The backend sample checks passed for this lesson. This is the strongest signal the platform currently has that the implementation is behaving as required.',
        color: Color(0xFF10B981),
        icon: Icons.verified_rounded,
      );
    }
    if (failedTests > 0 || failureKind == 'test_failure') {
      return const _EvaluationVerdict(
        title: 'Code runs, but behavior is still incorrect',
        subtitle:
            'At least one lesson-specific check failed, so the implementation does not yet match the required algorithmic update.',
        color: Color(0xFFEF4444),
        icon: Icons.assignment_late_rounded,
      );
    }
    if (failureKind == 'runtime_error' || failureKind == 'validation_error') {
      return const _EvaluationVerdict(
        title: 'Submission could not be validated',
        subtitle:
            'The backend could not complete the lesson evaluation because the code raised an error or did not satisfy the lesson contract.',
        color: Color(0xFFEF4444),
        icon: Icons.error_outline_rounded,
      );
    }
    if (!hasEvaluation) {
      return const _EvaluationVerdict(
        title: 'No correctness result yet',
        subtitle:
            'Submit the current lesson code to run lesson-specific checks.',
        color: Color(0xFF64748B),
        icon: Icons.pending_outlined,
      );
    }
    return const _EvaluationVerdict(
      title: 'Evaluation in progress',
      subtitle:
          'The platform has started collecting correctness signals for this lesson.',
      color: Color(0xFF3B82F6),
      icon: Icons.analytics_outlined,
    );
  }
}

class _EvaluationVerdict {
  final String title;
  final String subtitle;
  final Color color;
  final IconData icon;

  const _EvaluationVerdict({
    required this.title,
    required this.subtitle,
    required this.color,
    required this.icon,
  });
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
