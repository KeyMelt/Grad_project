import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/features/feedback/feedback_section.dart';

void main() {
  testWidgets(
      'feedback section exposes multi-step survey for signed-in learner',
      (tester) async {
    tester.view.physicalSize = const Size(1100, 1400);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    List<int>? submittedSusResponses;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: FeedbackSection(
            learner: const LearnerProfile(
              id: 'student-1',
              displayName: 'Maya',
              platformRole: 'student',
            ),
            isSubmitting: false,
            isComplete: false,
            message: 'Your feedback helps improve our services.',
            onSubmit: ({
              required susResponses,
              required tlxMentalDemand,
              required tlxPhysicalDemand,
              required tlxTemporalDemand,
              required tlxPerformance,
              required tlxEffort,
              required tlxFrustration,
              feedbackHelpful,
              feedbackConfusing,
              feedbackImprovement,
            }) {
              submittedSusResponses = susResponses;
            },
          ),
        ),
      ),
    );

    expect(find.text('Session feedback'), findsOneWidget);
    expect(find.text('Using the service'), findsOneWidget);

    await tester.ensureVisible(find.text('Next'));
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();
    expect(find.text('Session effort'), findsOneWidget);

    await tester.ensureVisible(find.text('Next'));
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();
    expect(find.text('Optional feedback'), findsOneWidget);

    await tester.ensureVisible(find.text('Submit feedback'));
    await tester.tap(find.text('Submit feedback'));
    await tester.pump();

    expect(submittedSusResponses, List<int>.filled(10, 3));
  });

  testWidgets('feedback section requires sign-in', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: FeedbackSection(
            learner: null,
            isSubmitting: false,
            isComplete: false,
            message: '',
            onSubmit: ({
              required susResponses,
              required tlxMentalDemand,
              required tlxPhysicalDemand,
              required tlxTemporalDemand,
              required tlxPerformance,
              required tlxEffort,
              required tlxFrustration,
              feedbackHelpful,
              feedbackConfusing,
              feedbackImprovement,
            }) {},
          ),
        ),
      ),
    );

    expect(find.text('Sign in to submit session feedback.'), findsOneWidget);
  });
}
