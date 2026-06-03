import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';
import '../quiz/quiz_section.dart';

class FeedbackSection extends StatelessWidget {
  final LearnerProfile? learner;
  final bool isSubmitting;
  final bool isComplete;
  final String message;
  final void Function({
    required List<int> susResponses,
    required int tlxMentalDemand,
    required int tlxPhysicalDemand,
    required int tlxTemporalDemand,
    required int tlxPerformance,
    required int tlxEffort,
    required int tlxFrustration,
    String? feedbackHelpful,
    String? feedbackConfusing,
    String? feedbackImprovement,
  }) onSubmit;

  const FeedbackSection({
    super.key,
    required this.learner,
    required this.isSubmitting,
    required this.isComplete,
    required this.message,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    if (learner == null) {
      return const Center(
        child: _FeedbackGate(),
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final wide = constraints.maxWidth >= 980;
        final intro = _FeedbackIntroCard(displayName: learner!.displayName);
        final form = PostStudySurveyCard(
          isSubmitting: isSubmitting,
          isComplete: isComplete,
          message: message,
          onSubmit: onSubmit,
        );

        return SingleChildScrollView(
          padding: const EdgeInsets.all(AppConstants.defaultPadding),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 1180),
              child: wide
                  ? Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SizedBox(width: 340, child: intro),
                        const SizedBox(width: AppConstants.defaultPadding),
                        Expanded(child: form),
                      ],
                    )
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        intro,
                        const SizedBox(height: AppConstants.defaultPadding),
                        form,
                      ],
                    ),
            ),
          ),
        );
      },
    );
  }
}

class _FeedbackIntroCard extends StatelessWidget {
  final String displayName;

  const _FeedbackIntroCard({required this.displayName});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        side: const BorderSide(color: AppTheme.borderLight),
      ),
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(
              Icons.rate_review_outlined,
              color: AppTheme.primaryBlue,
              size: 32,
            ),
            const SizedBox(height: 16),
            Text(
              'Session feedback',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                    color: AppTheme.textPrimary,
                  ),
            ),
            const SizedBox(height: 10),
            Text(
              'Thanks, $displayName. Your feedback helps improve our services.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textSecondary,
                    height: 1.45,
                  ),
            ),
            const SizedBox(height: 18),
            const _FeedbackFact(
              icon: Icons.view_agenda_outlined,
              title: 'Quick check-in',
              body: 'A few short ratings and optional notes.',
            ),
            const SizedBox(height: 12),
            const _FeedbackFact(
              icon: Icons.touch_app_outlined,
              title: 'Low effort',
              body: 'Most inputs are selectable ratings or sliders.',
            ),
            const SizedBox(height: 12),
            const _FeedbackFact(
              icon: Icons.privacy_tip_outlined,
              title: 'Optional notes',
              body: 'Only add written details you are comfortable sharing.',
            ),
          ],
        ),
      ),
    );
  }
}

class _FeedbackFact extends StatelessWidget {
  final IconData icon;
  final String title;
  final String body;

  const _FeedbackFact({
    required this.icon,
    required this.title,
    required this.body,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: AppTheme.primaryBlue),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                      color: AppTheme.textPrimary,
                    ),
              ),
              const SizedBox(height: 2),
              Text(
                body,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppTheme.textSecondary,
                      height: 1.35,
                    ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _FeedbackGate extends StatelessWidget {
  const _FeedbackGate();

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        side: const BorderSide(color: AppTheme.borderLight),
      ),
      child: const Padding(
        padding: EdgeInsets.all(28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.lock_outline,
              color: AppTheme.primaryBlue,
              size: 36,
            ),
            SizedBox(height: 14),
            Text(
              'Sign in to submit session feedback.',
              style: TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
