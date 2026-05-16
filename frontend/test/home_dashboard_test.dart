import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/workbench_state.dart';
import 'package:rl_ide/features/home/home_dashboard.dart';

void main() {
  testWidgets('home dashboard renders lessons and triggers sign-in callback',
      (tester) async {
    tester.view.physicalSize = const Size(1440, 1600);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    String? submittedName;
    String? submittedPassword;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: HomeDashboard(
            learner: null,
            progress: const LearnerProgress.empty(),
            studyBuddySummary: const StudyBuddySummary.empty(),
            isStudyBuddySummaryLoading: false,
            sections: [_sampleSection()],
            isSigningIn: false,
            canAccessAuthoring: false,
            message: 'Welcome message',
            onSignIn: (displayName, password) {
              submittedName = displayName;
              submittedPassword = password;
            },
            onSignUp: (_, __) {},
            onSignInWithGoogle: () {},
            onOpenLesson: (_) {},
            onOpenQuiz: () {},
            onOpenFlashcards: () {},
            onOpenAuthoring: () {},
            onSignOut: () {},
          ),
        ),
      ),
    );

    await tester.tap(find.text('Open Sign In / Sign Up'));
    await tester.pumpAndSettle();

    await tester.enterText(find.byType(TextField).first, 'maya@example.com');
    await tester.enterText(find.byType(TextField).last, 'Password123!');
    await tester.tap(find.text('Sign In').last);
    await tester.pumpAndSettle();

    await tester.scrollUntilVisible(
      find.text('Lesson Summaries'),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('Lesson Summaries'), findsOneWidget);
    expect(find.text('Policy Evaluation'), findsOneWidget);
    expect(submittedName, 'maya@example.com');
    expect(submittedPassword, 'Password123!');
    expect(find.text('Progress Overview'), findsNothing);
  });

  testWidgets('home dashboard shows low-confidence mastery indicator',
      (tester) async {
    tester.view.physicalSize = const Size(1440, 1600);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: HomeDashboard(
            learner: const LearnerProfile(
              id: 'student-1',
              displayName: 'Maya',
              platformRole: 'student',
            ),
            progress: const LearnerProgress.empty(),
            studyBuddySummary: const StudyBuddySummary(
              masterySnapshots: [
                StudyBuddyMasterySnapshot(
                  id: 'snapshot-1',
                  lessonId: 'dp_policy_eval',
                  conceptId: 'dp_policy_eval',
                  masteryScore: 0.46,
                  supportNeedScore: 0.35,
                  confidenceScore: 0.22,
                  stalenessDays: 0,
                  evidenceSummary: {},
                  recordedAtUtc: null,
                ),
              ],
              reviewRecommendation: null,
              recentInterventions: [],
            ),
            isStudyBuddySummaryLoading: false,
            sections: [_sampleSection()],
            isSigningIn: false,
            canAccessAuthoring: false,
            message: 'Welcome message',
            onSignIn: (_, __) {},
            onSignUp: (_, __) {},
            onSignInWithGoogle: () {},
            onOpenLesson: (_) {},
            onOpenQuiz: () {},
            onOpenFlashcards: () {},
            onOpenAuthoring: () {},
            onSignOut: () {},
          ),
        ),
      ),
    );

    await tester.scrollUntilVisible(
      find.text('Low evidence'),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('Concept Mastery'), findsOneWidget);
    expect(find.text('Low evidence'), findsOneWidget);
  });
}

LessonSection _sampleSection() {
  return const LessonSection(
    title: 'Dynamic Programming',
    lessons: [
      LessonDefinition(
        id: 'dp_policy_eval',
        title: 'Policy Evaluation',
        description: 'Evaluate a policy on FrozenLake.',
        category: 'Dynamic Programming',
        starterCode: 'print("hello")\n',
        conceptVideo: LessonConceptVideo(
          streamPath: '',
          durationLabel: '00:00',
          summary: 'summary',
          highlights: [],
        ),
        exercise: LessonExerciseBrief(
          title: 'Exercise',
          overview: 'Overview',
          tasks: ['Task'],
          successCriteria: ['Criteria'],
          codeTip: 'Tip',
        ),
      ),
    ],
  );
}
