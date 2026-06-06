import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/features/workspace/trace_replay_panel.dart';
import 'package:rl_ide/features/workspace/trace_replay/trace_predict_prompt.dart';
import 'package:rl_ide/features/workspace/trace_replay/trace_step_markers.dart';
import 'package:rl_ide/features/workspace/trace_replay/trace_value_sparkline.dart';

Widget _wrap(Widget child) => MaterialApp(home: Scaffold(body: child));

TraceReplayPanel _panel(List<ExecutionTraceStep> steps) => TraceReplayPanel(
      runStatusLabel: 'Completed',
      statusMessage: '',
      totalReward: 1,
      averageReward: 1,
      bestEpisodeReward: 1,
      episodesCompleted: 1,
      stepsRecorded: steps.length,
      videoPath: '',
      testResults: const [],
      stepTrace: steps,
    );

void _wide(WidgetTester tester) {
  tester.view.physicalSize = const Size(1400, 1000);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);
}

ExecutionTraceStep _dpStep() => ExecutionTraceStep.fromJson({
      'state': 6,
      'action': 2,
      'next_state': 10,
      'reward': 0.0,
      'transition_probability': 0.333,
      'agent_caption': 'Policy evaluation backs up state 6.',
      'code_lines': ['V[s] = sum(p * (r + gamma * V[s2]))'],
      'math_lines': ['expected value 0.0'],
      'updated_values': {'V(6)': 0.0},
      'tables': {
        'kind': 'value_table',
        'after': [
          [0.0],
          [0.0],
        ],
        'active_cell': {'row': 6, 'column': 0},
        'changed_cells': [
          {'row': 6, 'column': 0},
        ],
        'action_labels': ['Value'],
      },
      'equation_update': {'kind': 'policy_evaluation', 'lhs': 'V(6)'},
    });

ExecutionTraceStep _tdStep() => ExecutionTraceStep.fromJson({
      'state': 0,
      'action': 1,
      'next_state': 1,
      'reward': 0.0,
      'transition_probability': 1,
      'agent_caption': 'Q-learning updates Q(0,1).',
      'code_lines': ['Q[s][a] += alpha * error'],
      'math_lines': ['TD target 0.5'],
      'updated_values': {'Q(0, 1)': 0.1},
      'tables': {
        'kind': 'q_table',
        'after': [
          [0.0, 0.1],
        ],
        'active_cell': {'row': 0, 'column': 1},
        'changed_cells': [
          {'row': 0, 'column': 1},
        ],
        'action_labels': ['Up', 'Right'],
      },
      'equation_update': {
        'kind': 'q_learning',
        'lhs': 'Q(0,1)',
        'old_value': 0.0,
        'new_value': 0.1,
        'td_target': 0.5,
        'td_error': 0.5,
        'alpha': 0.1,
        'bootstrap_label': 'max Q(1,*)',
        'bootstrap_value': 0.5,
      },
    });

void main() {
  testWidgets('predict prompt scores a correct guess and advances',
      (tester) async {
    var advanced = false;
    await tester.pumpWidget(_wrap(TracePredictPrompt(
      actionOptions: const ['Left', 'Right'],
      actualActionLabel: 'Right',
      actualRewardSign: 1,
      onAdvance: () => advanced = true,
    )));

    await tester.tap(find.text('Right'));
    await tester.pump();
    await tester.tap(find.text('Win (+)'));
    await tester.pump();
    await tester.tap(find.text('Reveal'));
    await tester.pump();

    expect(find.textContaining('Both right'), findsOneWidget);

    await tester.tap(find.text('Next step'));
    await tester.pump();
    expect(advanced, isTrue);
  });

  testWidgets('sparkline hidden with <2 points, shown with >=2',
      (tester) async {
    await tester.pumpWidget(_wrap(const TraceValueSparkline(values: [0.5])));
    expect(find.textContaining('updates'), findsNothing);

    await tester.pumpWidget(
      _wrap(const TraceValueSparkline(values: [0.1, 0.4, 0.6])),
    );
    expect(find.textContaining('updates'), findsOneWidget);
  });

  testWidgets('step markers render without error', (tester) async {
    await tester.pumpWidget(_wrap(const SizedBox(
      width: 320,
      child: TraceStepMarkers(
        totalSteps: 6,
        markers: [
          (index: 2, kind: TraceMarkerKind.rewardPositive),
          (index: 5, kind: TraceMarkerKind.terminal),
        ],
      ),
    )));
    expect(find.byType(TraceStepMarkers), findsOneWidget);
  });

  testWidgets('DP step shows the transition probability p', (tester) async {
    _wide(tester);
    await tester.pumpWidget(_wrap(_panel([_dpStep()])));
    await tester.pumpAndSettle();
    expect(find.text('Probability (p)'), findsWidgets);
    expect(find.text('sampled · model-free'), findsNothing);
  });

  testWidgets('model-free TD step hides p and shows "sampled"',
      (tester) async {
    _wide(tester);
    await tester.pumpWidget(_wrap(_panel([_tdStep()])));
    await tester.pumpAndSettle();
    expect(find.text('sampled · model-free'), findsWidgets);
    expect(find.text('Probability (p)'), findsNothing);
  });
}
