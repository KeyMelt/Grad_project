import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/lesson_models.dart';
import 'package:rl_ide/features/study_buddy/study_buddy_panel.dart';

void main() {
  testWidgets('study buddy panel renders intervention and actions', (
    tester,
  ) async {
    var completed = false;
    var dismissed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Align(
            alignment: Alignment.bottomRight,
            child: StudyBuddyPanel(
              lesson: _lesson(),
              intervention: _intervention(),
              isLoading: false,
              isDismissed: false,
              onDismiss: () => dismissed = true,
              onComplete: () => completed = true,
              onReopen: () {},
              onRefresh: () {},
              onSendChatMessage: (_) {},
            ),
          ),
        ),
      ),
    );

    expect(find.text('Check the failing pattern'), findsOneWidget);
    expect(find.text('What feels unclear?'), findsOneWidget);
    expect(find.text('Current Exercise'), findsNothing);

    await tester.ensureVisible(find.text('Done'));
    await tester.pump();
    await tester.tap(find.text('Done'));
    await tester.pump();
    expect(completed, isTrue);

    await tester.tap(find.byTooltip('Dismiss Study Buddy'));
    await tester.pump();
    expect(dismissed, isTrue);
  });

  testWidgets('dismissed study buddy panel shows reopen button', (
    tester,
  ) async {
    var reopened = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: StudyBuddyPanel(
            lesson: _lesson(),
            intervention: _intervention(),
            isLoading: false,
            isDismissed: true,
            onDismiss: () {},
            onComplete: () {},
            onReopen: () => reopened = true,
            onRefresh: () {},
            onSendChatMessage: (_) {},
          ),
        ),
      ),
    );

    await tester.tap(find.byTooltip('Open Study Buddy'));
    await tester.pump();

    expect(reopened, isTrue);
  });

  testWidgets('idle study buddy panel stays visible without intervention', (
    tester,
  ) async {
    String? sentMessage;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: StudyBuddyPanel(
            lesson: _lesson(),
            intervention: null,
            isLoading: false,
            isDismissed: false,
            onDismiss: _noop,
            onComplete: _noop,
            onReopen: _noop,
            onRefresh: _noop,
            onSendChatMessage: (message) => sentMessage = message,
          ),
        ),
      ),
    );

    expect(find.text('Study Buddy'), findsOneWidget);
    expect(find.text('AI Coach'), findsOneWidget);
    expect(find.text('Ask Study Buddy about the current exercise.'),
        findsOneWidget);
    expect(
        find.byKey(const ValueKey('study-buddy-chat-input')), findsOneWidget);

    await tester.pump();
    await tester.ensureVisible(find.widgetWithText(ActionChip, 'Quick recap'));
    await tester.tap(find.widgetWithText(ActionChip, 'Quick recap'));
    await tester.pump();
    expect(sentMessage, contains('quick recap'));

    await tester.ensureVisible(find.widgetWithText(ActionChip, 'Find blocker'));
    await tester.tap(find.widgetWithText(ActionChip, 'Find blocker'));
    await tester.pump();
    expect(sentMessage, contains('most likely blocker'));
  });

  testWidgets('long-running trace state offers review actions', (
    tester,
  ) async {
    String? sentMessage;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: StudyBuddyPanel(
            lesson: _lesson(),
            intervention: null,
            isLoading: false,
            isDismissed: false,
            isSubmissionTakingLong: true,
            onDismiss: _noop,
            onComplete: _noop,
            onReopen: _noop,
            onRefresh: _noop,
            onSendChatMessage: (message) => sentMessage = message,
          ),
        ),
      ),
    );

    expect(find.text('Replay trace is still building'), findsOneWidget);
    expect(find.widgetWithText(ActionChip, 'Review question'), findsOneWidget);

    await tester.pump();
    await tester.ensureVisible(
      find.widgetWithText(ActionChip, 'Review question'),
    );
    await tester.tap(find.widgetWithText(ActionChip, 'Review question'));
    await tester.pump();

    expect(sentMessage, contains('Ask me one concise review question'));
  });

  testWidgets('current exercise brief renders as standalone widget', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: StudyBuddyExerciseBrief(lesson: _lesson()),
        ),
      ),
    );

    expect(find.text('Current Exercise'), findsOneWidget);
    expect(find.text('Implement iterative policy evaluation'), findsOneWidget);
    expect(find.text('What to do'), findsOneWidget);
  });

  testWidgets('study buddy chat input sends learner message', (
    tester,
  ) async {
    String? sentMessage;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: StudyBuddyPanel(
            lesson: _lesson(),
            intervention: null,
            isLoading: false,
            isDismissed: false,
            chatMessages: const [
              StudyBuddyChatMessage(
                role: 'assistant',
                content: 'Start with the Bellman update target.',
              ),
            ],
            onDismiss: _noop,
            onComplete: _noop,
            onReopen: _noop,
            onRefresh: _noop,
            onSendChatMessage: (message) => sentMessage = message,
          ),
        ),
      ),
    );

    expect(find.text('Start with the Bellman update target.'), findsOneWidget);

    await tester.enterText(
      find.byKey(const ValueKey('study-buddy-chat-input')),
      'What should I inspect next?',
    );
    await tester.tap(find.byTooltip('Send message'));
    await tester.pump();

    expect(sentMessage, 'What should I inspect next?');
  });
}

void _noop() {}

LessonDefinition _lesson() {
  return const LessonDefinition(
    id: 'dp_policy_eval',
    title: 'Policy Evaluation',
    description:
        'Evaluate a fixed policy over FrozenLake using Bellman expectation backups and iterative sweeps.',
    category: 'Dynamic Programming',
    starterCode: 'print("policy evaluation")',
    conceptVideo: LessonConceptVideo(
      streamPath: '',
      durationLabel: '',
      summary: '',
      highlights: [],
    ),
    exercise: LessonExerciseBrief(
      title: 'Implement iterative policy evaluation',
      overview:
          'Complete the Bellman expectation update so each state value is replaced by the expected return under the supplied policy. The lesson video gives the conceptual walkthrough; this exercise asks you to express that reasoning in code.',
      tasks: [
        'Fill the expectation TODO block so it accumulates every policy-weighted transition branch.',
        'Replace the convergence placeholder with the updated state-value comparison.',
        'Keep the discounted future value at zero for terminal transitions.',
      ],
      successCriteria: [
        'The function computes the Bellman expectation update for every policy-weighted action branch.',
      ],
      codeTip: 'Use DISCOUNT_FACTOR when you want a different gamma.',
    ),
  );
}

StudyBuddyIntervention _intervention() {
  return const StudyBuddyIntervention(
    id: 'intervention-1',
    lessonId: 'dp_policy_eval',
    conceptId: 'dp_policy_eval',
    sessionId: 'study-session-1',
    triggerType: 'submission_failure_streak',
    triggerScore: 1,
    interventionType: 'mini_example',
    status: 'ready',
    promptVersion: 'test_prompt_v1',
    reflectionPassResult: 'passed',
    content: StudyBuddyInterventionContent(
      interventionType: 'mini_example',
      title: 'Check the failing pattern',
      message: 'Focus on one concept checkpoint.',
      diagnosticQuestion: 'What feels unclear?',
      choices: ['Concept', 'Checkpoint', 'Try again'],
      checkpoint: 'Name the update target.',
      nextStep: 'Run one small check.',
      conceptIds: ['dp_policy_eval'],
      solutionLeakageRisk: 'low',
    ),
  );
}
