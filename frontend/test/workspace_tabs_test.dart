import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/workbench_state.dart';
import 'package:rl_ide/features/workspace/workspace_tabs.dart';

import 'support/fake_video_player_platform.dart';

const _conceptOnlyLesson = LessonDefinition(
  id: 'rl_intro',
  title: 'RL Intro',
  description: 'Concept-only lesson.',
  category: 'Foundations',
  starterCode: '',
  conceptVideo: LessonConceptVideo(
    streamPath: '/media/concept-videos/rl_intro.mp4',
    durationLabel: '00:10',
    summary: 'Intro video.',
    highlights: [],
  ),
  exercise: LessonExerciseBrief(
    title: 'Concept only',
    overview: 'No coding exercise.',
    tasks: [],
    successCriteria: [],
    codeTip: '',
  ),
  hasCodeExercise: false,
);

const _codingLesson = LessonDefinition(
  id: 'dp_policy_eval',
  title: 'Policy Evaluation',
  description: 'Coding lesson.',
  category: 'Dynamic Programming',
  starterCode: 'def policy_evaluation():\n    return []\n',
  conceptVideo: LessonConceptVideo(
    streamPath: '/media/concept-videos/dp_policy_eval_concept.mp4',
    durationLabel: '00:10',
    summary: 'Bellman expectation walkthrough.',
    highlights: [],
  ),
  exercise: LessonExerciseBrief(
    title: 'Implement iterative policy evaluation',
    overview: 'Complete the Bellman update.',
    tasks: ['Fill the Bellman expectation backup.'],
    successCriteria: ['Submission passed'],
    codeTip: 'Use the supplied discount factor.',
  ),
);

Widget _wrapWorkspaceTabs(LessonDefinition lesson) {
  return MaterialApp(
    home: Scaffold(
      body: WorkspaceTabs(
        lesson: lesson,
        code: lesson.starterCode,
        workspaceSessionId: null,
        workspaceReady: true,
        editorConnectionStatus: WorkspaceConnectionStatus.ready,
        consoleConnectionStatus: WorkspaceConnectionStatus.ready,
        editorShellUrl: null,
        scriptVersion: 1,
        onSubmit: () {},
        onStop: () {},
        onReset: () {},
        onReconnectWorkspace: () {},
        statusMessage: '',
        runStatusLabel: 'Idle',
        failureKind: null,
        unresolvedBlanks: const [],
        studentFeedback: null,
        feedbackDismissed: false,
        totalReward: 0,
        averageReward: 0,
        bestEpisodeReward: 0,
        episodesCompleted: 0,
        stepsRecorded: 0,
        videoPath: '',
        replayRenderStatus: 'idle',
        replayRenderError: null,
        testResults: const <ExecutionTestCaseResult>[],
        stepTrace: const <ExecutionTraceStep>[],
        traceEpisodes: const <ExecutionTraceEpisode>[],
        episodeSummaries: const <ExecutionEpisodeSummary>[],
        isAuthenticated: true,
      ),
    ),
  );
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  installFakeVideoPlayerPlatform();

  testWidgets('concept-only lessons grey out Code and Replay tabs', (
    tester,
  ) async {
    await tester.pumpWidget(_wrapWorkspaceTabs(_conceptOnlyLesson));
    await tester.pumpAndSettle();

    expect(
      tester.widget<Opacity>(
        find.byKey(const ValueKey('workspace-tab-code-opacity')),
      ).opacity,
      0.35,
    );
    expect(
      tester.widget<Opacity>(
        find.byKey(const ValueKey('workspace-tab-replay-opacity')),
      ).opacity,
      0.35,
    );
  });

  testWidgets('coding lessons keep Code and Replay tabs fully active', (
    tester,
  ) async {
    await tester.pumpWidget(_wrapWorkspaceTabs(_codingLesson));
    await tester.pumpAndSettle();

    expect(
      tester.widget<Opacity>(
        find.byKey(const ValueKey('workspace-tab-code-opacity')),
      ).opacity,
      1.0,
    );
    expect(
      tester.widget<Opacity>(
        find.byKey(const ValueKey('workspace-tab-replay-opacity')),
      ).opacity,
      1.0,
    );
  });
}
