// ignore_for_file: depend_on_referenced_packages

import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_math_fork/flutter_math.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/lesson_models.dart';
import 'package:rl_ide/features/workspace/lesson_notes_panel.dart';

LessonDefinition _lesson({
  String lectureNotes = '',
  String summary = '',
  List<String> highlights = const [],
  String takeawayLine = '',
}) {
  return LessonDefinition(
    id: 'dp_policy_eval',
    title: 'Policy Evaluation',
    description: 'desc',
    category: 'Dynamic Programming',
    starterCode: '',
    conceptVideo: LessonConceptVideo(
      streamPath: '/media/concept-videos/dp_policy_eval_concept.mp4',
      durationLabel: '03:30',
      summary: summary,
      highlights: highlights,
      takeawayLine: takeawayLine,
      lectureNotes: lectureNotes,
    ),
    exercise: const LessonExerciseBrief(
      title: '',
      overview: '',
      tasks: [],
      successCriteria: [],
      codeTip: '',
    ),
  );
}

Future<void> _pumpPanel(WidgetTester tester, LessonDefinition lesson) async {
  // Selectable MarkdownBody registers with a SelectionRegistrar; unmount the
  // tree explicitly so dangling dependents do not leak into the next test.
  addTearDown(() async {
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: SelectionArea(
          child: SizedBox(
            width: 420,
            child: LessonNotesPanel(lesson: lesson),
          ),
        ),
      ),
    ),
  );
  await tester.pump();
}

void main() {
  testWidgets('renders markdown lecture notes when lectureNotes is non-empty',
      (tester) async {
    const notes = r'''
# Policy Evaluation

The Bellman expectation update is $v_\pi(s)$ computed iteratively.

$$
v_\pi(s) = \sum_a \pi(a|s) \sum_{s',r} p(s',r|s,a)[r + \gamma v_\pi(s')]
$$

- First bullet
- Second bullet
''';

    await _pumpPanel(tester, _lesson(lectureNotes: notes));

    // Markdown path: header + rendered MarkdownBody + LaTeX math widgets.
    expect(find.text('Lecture Notes'), findsOneWidget);
    expect(find.text('Lesson Notes'), findsNothing);
    expect(find.byType(MarkdownBody), findsOneWidget);
    expect(find.byType(Math), findsWidgets);
    expect(tester.takeException(), isNull);
  });

  testWidgets('renders structured fallback when lectureNotes is empty',
      (tester) async {
    await _pumpPanel(
      tester,
      _lesson(
        summary: 'A Bellman expectation sweep over FrozenLake.',
        highlights: const [
          'How a fixed policy weights each action.',
          'Why repeated sweeps converge.',
        ],
        takeawayLine: 'Repeated sweeps converge to stable state values.',
      ),
    );

    // Fallback path: legacy header + summary/highlights/takeaway, no markdown.
    expect(find.text('Lesson Notes'), findsOneWidget);
    expect(find.text('Lecture Notes'), findsNothing);
    expect(find.byType(MarkdownBody), findsNothing);
    expect(
      find.text('A Bellman expectation sweep over FrozenLake.'),
      findsOneWidget,
    );
    expect(find.text('How a fixed policy weights each action.'), findsOneWidget);
    expect(
      find.text('Repeated sweeps converge to stable state values.'),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('whitespace-only lectureNotes falls back to structured layout',
      (tester) async {
    await _pumpPanel(
      tester,
      _lesson(lectureNotes: '   \n  \t ', summary: 'Fallback summary.'),
    );

    expect(find.text('Lesson Notes'), findsOneWidget);
    expect(find.byType(MarkdownBody), findsNothing);
    expect(find.text('Fallback summary.'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
