import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';

class ExerciseBriefPanel extends StatelessWidget {
  final LessonDefinition lesson;

  const ExerciseBriefPanel({
    super.key,
    required this.lesson,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    lesson.exercise.title,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFF7ED),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: const Color(0xFFF59E0B)),
                  ),
                  child: Text(
                    lesson.category,
                    style: const TextStyle(
                      color: Color(0xFFB45309),
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              lesson.exercise.overview,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: AppTheme.textPrimary,
                    height: 1.55,
                  ),
            ),
            const SizedBox(height: 20),
            _SectionBlock(
              title: 'Instructions',
              accent: const Color(0xFF2563EB),
              bullets: lesson.exercise.tasks,
            ),
            const SizedBox(height: 18),
            _SectionBlock(
              title: 'Success Criteria',
              accent: const Color(0xFF10B981),
              bullets: lesson.exercise.successCriteria,
            ),
            const SizedBox(height: 18),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.borderLight),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Code Configuration',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    lesson.exercise.codeTip,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppTheme.textPrimary,
                          height: 1.45,
                        ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class WorkspaceFeedbackPanel extends StatelessWidget {
  final LessonDefinition lesson;
  final String runStatusLabel;
  final String statusMessage;
  final String? failureKind;
  final List<String> unresolvedBlanks;
  final ExecutionStudentFeedback? studentFeedback;
  final List<ExecutionTestCaseResult> testResults;
  final VoidCallback? onDismiss;

  const WorkspaceFeedbackPanel({
    super.key,
    required this.lesson,
    required this.runStatusLabel,
    required this.statusMessage,
    required this.failureKind,
    required this.unresolvedBlanks,
    required this.studentFeedback,
    required this.testResults,
    required this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    final passedTests = testResults.where((result) => result.passed).length;
    final failedTests = testResults.length - passedTests;
    final allTestsPassed = testResults.isNotEmpty && failedTests == 0;
    final verdict = _buildVerdict(
      allTestsPassed: allTestsPassed,
      failedTests: failedTests,
    );
    final feedback = studentFeedback;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: verdict.background,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: verdict.color.withValues(alpha: 0.32)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.only(top: 2),
                child: Icon(verdict.icon, color: verdict.color, size: 20),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      verdict.title,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            color: AppTheme.textPrimary,
                            fontWeight: FontWeight.w800,
                          ),
                    ),
                    if (statusMessage.trim().isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        statusMessage.trim(),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: AppTheme.textSecondary,
                              height: 1.4,
                            ),
                      ),
                    ],
                  ],
                ),
              ),
              if (onDismiss != null)
                IconButton(
                  onPressed: onDismiss,
                  tooltip: 'Dismiss feedback',
                  icon: const Icon(Icons.close_rounded),
                  iconSize: 18,
                  visualDensity: VisualDensity.compact,
                  color: AppTheme.textSecondary,
                ),
            ],
          ),
          if (feedback != null) ...[
            const SizedBox(height: 12),
            _FeedbackText(label: 'Summary', value: feedback.summary),
            if (feedback.likelyIssue.isNotEmpty)
              _FeedbackText(label: 'Likely issue', value: feedback.likelyIssue),
            if (feedback.nextSteps.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text(
                'Next steps',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppTheme.textPrimary,
                      fontWeight: FontWeight.w800,
                    ),
              ),
              const SizedBox(height: 6),
              ...feedback.nextSteps.map(
                (step) => _CompactBullet(text: step, color: verdict.color),
              ),
            ],
          ],
          if (unresolvedBlanks.isNotEmpty) ...[
            const SizedBox(height: 12),
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
                        color: const Color(0xFFFFEDD5),
                        borderRadius: BorderRadius.circular(999),
                      ),
                      child: Text(
                        blankId,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: const Color(0xFF9A3412),
                              fontWeight: FontWeight.w800,
                            ),
                      ),
                    ),
                  )
                  .toList(growable: false),
            ),
          ],
          if (testResults.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              '$passedTests/${testResults.length} checks passed',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textPrimary,
                    fontWeight: FontWeight.w800,
                  ),
            ),
            const SizedBox(height: 8),
            ...testResults.map(
              (result) => _TestResultRow(result: result),
            ),
          ],
        ],
      ),
    );
  }

  _WorkspaceVerdict _buildVerdict({
    required bool allTestsPassed,
    required int failedTests,
  }) {
    if (failureKind == 'incomplete_template') {
      return const _WorkspaceVerdict(
        title: 'Fill the remaining blanks',
        color: Color(0xFFF59E0B),
        background: Color(0xFFFFFBEB),
        icon: Icons.rule_folder_outlined,
      );
    }
    if (allTestsPassed || runStatusLabel == 'Complete') {
      return const _WorkspaceVerdict(
        title: 'Submission passed',
        color: Color(0xFF10B981),
        background: Color(0xFFF0FDF4),
        icon: Icons.verified_rounded,
      );
    }
    if (failedTests > 0 || failureKind == 'test_failure') {
      return const _WorkspaceVerdict(
        title: 'Code runs, but behavior is still incorrect',
        color: Color(0xFFEF4444),
        background: Color(0xFFFFF1F2),
        icon: Icons.assignment_late_rounded,
      );
    }
    return const _WorkspaceVerdict(
      title: 'Submission feedback',
      color: Color(0xFFEF4444),
      background: Color(0xFFFFF1F2),
      icon: Icons.error_outline_rounded,
    );
  }
}

class _FeedbackText extends StatelessWidget {
  final String label;
  final String value;

  const _FeedbackText({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.textPrimary,
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 3),
          Text(
            value,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.textSecondary,
                  height: 1.4,
                ),
          ),
        ],
      ),
    );
  }
}

class _CompactBullet extends StatelessWidget {
  final String text;
  final Color color;

  const _CompactBullet({
    required this.text,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 7),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 5),
            child: Icon(Icons.circle, size: 7, color: color),
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Text(
              text,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textPrimary,
                    height: 1.4,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

class _TestResultRow extends StatelessWidget {
  final ExecutionTestCaseResult result;

  const _TestResultRow({required this.result});

  @override
  Widget build(BuildContext context) {
    final accent =
        result.passed ? const Color(0xFF10B981) : const Color(0xFFEF4444);
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.65),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: accent.withValues(alpha: 0.28)),
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
                color: accent,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  result.name,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.textPrimary,
                        fontWeight: FontWeight.w800,
                      ),
                ),
              ),
            ],
          ),
          if (result.message.trim().isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              result.message,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textSecondary,
                    height: 1.4,
                  ),
            ),
          ],
        ],
      ),
    );
  }
}

class _WorkspaceVerdict {
  final String title;
  final Color color;
  final Color background;
  final IconData icon;

  const _WorkspaceVerdict({
    required this.title,
    required this.color,
    required this.background,
    required this.icon,
  });
}

class _SectionBlock extends StatelessWidget {
  final String title;
  final Color accent;
  final List<String> bullets;

  const _SectionBlock({
    required this.title,
    required this.accent,
    required this.bullets,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: accent.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: accent.withValues(alpha: 0.24)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: accent,
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 12),
          ...bullets.map(
            (bullet) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Icon(
                      Icons.circle,
                      size: 8,
                      color: accent,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      bullet,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppTheme.textPrimary,
                            height: 1.45,
                          ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
