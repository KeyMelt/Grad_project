import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/workbench_state.dart';
import 'package:rl_ide/features/workspace/code_editor.dart';

void main() {
  testWidgets('code tab shows checklist and feedback for unresolved blanks', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1280, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    const lesson = LessonDefinition(
      id: 'dp_policy_eval',
      title: 'Policy Evaluation',
      description: 'desc',
      category: 'Dynamic Programming',
      starterCode: 'def policy_evaluation():\n    pass\n',
      conceptVideo: LessonConceptVideo(
        streamPath: '/media/concept-videos/dp_policy_eval_concept.mp4',
        durationLabel: '00:10',
        summary: 'summary',
        highlights: [],
      ),
      exercise: LessonExerciseBrief(
        title: 'Implement iterative policy evaluation',
        overview: 'overview',
        tasks: [],
        templateBlanks: [
          LessonTemplateBlank(
            blankId: 'policy_eval_expectation',
            kind: 'block',
            prompt:
                'Accumulate each action branch into the Bellman expectation update.',
            expectedConcept: 'Bellman expectation backup',
            approxLineAnchor: 11,
          ),
        ],
        successCriteria: ['Return a value table that passes the lesson test.'],
        codeTip: 'tip',
      ),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CodeEditorTab(
            lesson: lesson,
            code: lesson.starterCode,
            workspaceSessionId: 'workspace-1',
            workspaceReady: true,
            editorConnectionStatus: WorkspaceConnectionStatus.ready,
            consoleConnectionStatus: WorkspaceConnectionStatus.ready,
            editorShellUrl: null,
            statusMessage: 'Code validation failed.',
            runStatusLabel: 'Failed',
            scriptVersion: 1,
            failureKind: 'incomplete_template',
            unresolvedBlanks: const ['policy_eval_expectation'],
            studentFeedback: const ExecutionStudentFeedback(
              status: 'incomplete_template',
              summary: 'The submission still contains guided blanks.',
              likelyIssue: 'A TODO block was left unchanged.',
              affectedBlankIds: ['policy_eval_expectation'],
              nextSteps: ['Complete the Bellman expectation block.'],
              hintLevel: 'light',
            ),
            onSubmit: () {},
            onStop: () {},
            onReset: () {},
          ),
        ),
      ),
    );

    await tester.pump();

    expect(find.text('Exercise checklist'), findsNothing);
    expect(find.text('Fill the remaining blanks'), findsOneWidget);
    expect(
      find.text('The submission still contains guided blanks.'),
      findsOneWidget,
    );
    expect(find.text('script.py'), findsNothing);
    expect(find.text('Editor'), findsNothing);
    expect(find.text('Console'), findsNothing);
    expect(find.text('Connection failed, Try again.'), findsOneWidget);
  });
}
