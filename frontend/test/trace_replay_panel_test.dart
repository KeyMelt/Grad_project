import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/features/workspace/trace_replay_panel.dart';
import 'package:video_player/video_player.dart';

import 'support/fake_video_player_platform.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  installFakeVideoPlayerPlatform();

  testWidgets('renders TD equation card and Q-table inspector on wide layouts',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TraceReplayPanel(
            runStatusLabel: 'Passed',
            statusMessage: 'ok',
            totalReward: -1,
            averageReward: -1,
            bestEpisodeReward: -1,
            episodesCompleted: 1,
            stepsRecorded: 1,
            videoPath: '',
            testResults: const [],
            stepTrace: [
              ExecutionTraceStep.fromJson({
                'state': 36,
                'action': 0,
                'next_state': 24,
                'reward': -1,
                'transition_probability': 1,
                'agent_caption': 'SARSA uses the sampled next action Right.',
                'code_title': 'Code Trace',
                'code_lines': [
                  'Q[state][action] = Q[state][action] + alpha * error',
                ],
                'math_title': 'TD / SARSA',
                'math_equation':
                    r'Q(s,a)\leftarrow Q(s,a)+\alpha[r+\gamma Q(s^\prime,a^\prime)-Q(s,a)]',
                'math_lines': ['TD target = -1.0.'],
                'updated_values': {'Q(36, 0)': -0.1},
                'trace_schema_version': 2,
                'tables': {
                  'kind': 'q_table',
                  'before': [
                    [0, 0],
                    [0, 0],
                  ],
                  'after': [
                    [0, 0],
                    [-0.1, 0],
                  ],
                  'active_cell': {'row': 1, 'column': 0},
                  'bootstrap_cell': {'row': 0, 'column': 1},
                  'changed_cells': [
                    {'row': 1, 'column': 0},
                  ],
                  'action_labels': ['Up', 'Right'],
                },
                'equation_update': {
                  'kind': 'sarsa',
                  'lhs': 'Q(36,0)',
                  'old_value': 0,
                  'reward': -1,
                  'gamma': 0.95,
                  'bootstrap_label': 'Q(24,1)',
                  'bootstrap_value': 0,
                  'td_target': -1,
                  'td_error': -1,
                  'alpha': 0.1,
                  'new_value': -0.1,
                  'substitution': '0.0 + 0.1 * (-1.0 + 0.95 * 0.0 - 0.0)',
                  'code_focus':
                      'Q[state][action] += alpha * (td_target - Q[state][action])',
                },
                'explanation': {
                  'summary': 'SARSA updates one Q cell.',
                  'why_correct':
                      'SARSA uses the sampled next action in the TD target.',
                  'code_focus':
                      'Q[state][action] += alpha * (td_target - Q[state][action])',
                  'table_focus': 'row 1, column 0',
                },
              }),
            ],
          ),
        ),
      ),
    );

    await _selectBinderSection(tester, 'Math');
    expect(find.text('SARSA numeric update'), findsOneWidget);
    await _selectBinderSection(tester, 'Math');
    expect(find.text('Q-table Inspector'), findsOneWidget);
    expect(find.text('active s1, a0'), findsOneWidget);
    expect(find.text('bootstrap s0, a1'), findsOneWidget);
    await _selectBinderSection(tester, 'Math');
    expect(find.textContaining('0.0 + 0.1'), findsOneWidget);
    await _selectBinderSection(tester, 'Math');
    expect(
        find.byKey(const ValueKey('trace-code-focus-line-0')), findsOneWidget);
    await _selectBinderSection(tester, 'Step');
    expect(find.text('Why this update is correct'), findsOneWidget);
    expect(
      find.text('SARSA uses the sampled next action in the TD target.'),
      findsOneWidget,
    );
  });

  testWidgets('renders DP backup card and value table inspector',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TraceReplayPanel(
            runStatusLabel: 'Passed',
            statusMessage: 'ok',
            totalReward: 0,
            averageReward: 0,
            bestEpisodeReward: 0,
            episodesCompleted: 1,
            stepsRecorded: 1,
            videoPath: '',
            testResults: const [],
            stepTrace: [
              ExecutionTraceStep.fromJson({
                'state': 0,
                'action': 0,
                'next_state': 0,
                'reward': 0,
                'transition_probability': 1,
                'agent_caption': 'Value iteration backs up state 0.',
                'code_title': 'Code Trace',
                'code_lines': ['V[state] = max(action_values)'],
                'math_title': 'Bellman Optimality',
                'math_equation':
                    r'V_*(s)=\max_a \sum_{s^\prime,r} p(s^\prime,r|s,a)[r+\gamma V(s^\prime)]',
                'math_lines': ['best action = Left'],
                'updated_values': {'V(0)': 1.9},
                'trace_schema_version': 2,
                'tables': {
                  'kind': 'value_table',
                  'after': [
                    [1.9],
                    [1.0],
                  ],
                  'active_cell': {'row': 0, 'column': 0},
                  'changed_cells': [
                    {'row': 0, 'column': 0},
                  ],
                  'action_labels': ['Value'],
                },
                'equation_update': {
                  'kind': 'value_iteration',
                  'lhs': 'V(0)',
                  'gamma': 0.9,
                  'td_target': 1.9,
                  'new_value': 1.9,
                  'code_focus': 'V[state] = max(action_values)',
                  'dp_details': {
                    'selected_action': 0,
                    'selected_action_label': 'Left',
                    'backup_value': 1.9,
                    'delta': 0,
                    'action_backups': [
                      {
                        'action': 0,
                        'action_label': 'Left',
                        'expected_return': 1.9,
                        'weighted_contribution': 1.9,
                        'transition_terms': [
                          {
                            'probability': 1,
                            'next_state': 1,
                            'reward': 1,
                            'done': false,
                            'future_value': 1,
                            'contribution': 1.9,
                          },
                        ],
                      },
                    ],
                  },
                },
              }),
            ],
          ),
        ),
      ),
    );

    await _selectBinderSection(tester, 'Math');
    expect(find.text('Value iteration action comparison'), findsOneWidget);
    expect(find.text('Selected action'), findsOneWidget);
    expect(find.text('Left'), findsWidgets);
    await _selectBinderSection(tester, 'Math');
    expect(find.text('Value Table Inspector'), findsOneWidget);
    await _selectBinderSection(tester, 'Math');
    expect(find.textContaining('1.00*(r 1.00 + V 1.00)'), findsOneWidget);
  });

  testWidgets('renders MC Blackjack observation and return ladder',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TraceReplayPanel(
            runStatusLabel: 'Passed',
            statusMessage: 'ok',
            totalReward: 1,
            averageReward: 1,
            bestEpisodeReward: 1,
            episodesCompleted: 1,
            stepsRecorded: 1,
            videoPath: '',
            testResults: const [],
            stepTrace: [
              ExecutionTraceStep.fromJson({
                'state': 0,
                'action': 1,
                'next_state': 0,
                'reward': 0,
                'transition_probability': 1,
                'agent_caption':
                    'First-visit Monte Carlo updates a Blackjack state.',
                'code_title': 'Code Trace',
                'code_lines': [
                  'V[state] = sum(returns[state]) / len(returns[state])',
                ],
                'math_title': 'First-Visit Return',
                'math_equation': r'G_t=\sum_{k=0}^{T-t-1}\gamma^k R_{t+k+1}',
                'math_lines': ['G = 0.9'],
                'trace_schema_version': 2,
                'equation_update': {
                  'kind': 'mc_first_visit',
                  'lhs': 'V((15, 10, False))',
                  'gamma': 0.9,
                  'td_target': 0.9,
                  'new_value': 0.9,
                  'code_focus':
                      'V[state] = sum(returns[state]) / len(returns[state])',
                  'mc_details': {
                    'episode_index': 0,
                    'episode_step': 0,
                    'phase': 'first_visit_update',
                    'observation': {
                      'player_sum': 15,
                      'dealer_card': 10,
                      'usable_ace': false,
                    },
                    'action': 1,
                    'action_label': 'Hit',
                    'reward': 0,
                    'first_visit': true,
                    'return_value': 0.9,
                    'return_terms': [
                      {
                        'episode_step': 0,
                        'discount': 1,
                        'reward': 0,
                        'discounted_reward': 0,
                        'running_return': 0,
                      },
                      {
                        'episode_step': 1,
                        'discount': 0.9,
                        'reward': 1,
                        'discounted_reward': 0.9,
                        'running_return': 0.9,
                      },
                    ],
                    'returns_history': [0.9],
                    'episode_strip': [
                      {
                        'step_index': 0,
                        'state': '(15, 10, False)',
                        'observation': {
                          'player_sum': 15,
                          'dealer_card': 10,
                          'usable_ace': false,
                        },
                        'action': 1,
                        'action_label': 'Hit',
                        'reward': 0,
                        'next_state': '(20, 10, False)',
                        'next_observation': {
                          'player_sum': 20,
                          'dealer_card': 10,
                          'usable_ace': false,
                        },
                        'terminated': false,
                        'truncated': false,
                      },
                    ],
                  },
                },
              }),
            ],
          ),
        ),
      ),
    );

    await _selectBinderSection(tester, 'Step');
    expect(find.text('Blackjack observation'), findsOneWidget);
    await _selectBinderSection(tester, 'Math');
    expect(find.text('First-visit return update'), findsOneWidget);
    await _selectBinderSection(tester, 'Math');
    expect(find.text('Monte Carlo Episode Inspector'), findsOneWidget);
    expect(find.text('Return ladder'), findsOneWidget);
    await _selectBinderSection(tester, 'Step');
    expect(find.text('Player sum'), findsOneWidget);
    expect(find.text('15'), findsWidgets);
  });

  testWidgets('renders grid-world companion from grid metadata',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TraceReplayPanel(
            runStatusLabel: 'Passed',
            statusMessage: 'ok',
            totalReward: -1,
            averageReward: -1,
            bestEpisodeReward: -1,
            episodesCompleted: 1,
            stepsRecorded: 1,
            videoPath: '',
            testResults: const [],
            stepTrace: [
              ExecutionTraceStep.fromJson({
                'state': 0,
                'action': 2,
                'next_state': 1,
                'reward': 0,
                'transition_probability': 1,
                'agent_caption': 'Agent moves right from the start tile.',
                'grid_metadata': {
                  'environment': 'FrozenLake',
                  'rows': 2,
                  'columns': 2,
                  'state': 0,
                  'next_state': 1,
                  'state_coordinates': {'row': 0, 'column': 0},
                  'next_state_coordinates': {'row': 0, 'column': 1},
                  'action': 2,
                  'action_label': 'Right',
                  'reward': 0,
                  'terminated': false,
                  'truncated': false,
                  'cells': [
                    {
                      'state': 0,
                      'row': 0,
                      'column': 0,
                      'tile_type': 'S',
                      'terminal': false,
                    },
                    {
                      'state': 1,
                      'row': 0,
                      'column': 1,
                      'tile_type': 'F',
                      'terminal': false,
                    },
                    {
                      'state': 2,
                      'row': 1,
                      'column': 0,
                      'tile_type': 'H',
                      'terminal': true,
                    },
                    {
                      'state': 3,
                      'row': 1,
                      'column': 1,
                      'tile_type': 'G',
                      'terminal': true,
                    },
                  ],
                },
              }),
            ],
          ),
        ),
      ),
    );

    await _selectBinderSection(tester, 'Step');
    expect(find.text('FrozenLake grid'), findsOneWidget);
    expect(find.text('state 0'), findsOneWidget);
    expect(find.text('next 1'), findsOneWidget);
    // The action label now appears both in the grid companion and in the
    // always-visible toolbar transition chip.
    expect(find.text('Right'), findsWidgets);
  });

  testWidgets('selects complete trace episodes and resets the step cursor',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final episodeOneSteps = [
      ExecutionTraceStep.fromJson({
        'state': 0,
        'action': 1,
        'next_state': 1,
        'reward': -1,
        'agent_caption': 'Episode one first step.',
      }),
      ExecutionTraceStep.fromJson({
        'state': 1,
        'action': 2,
        'next_state': 2,
        'reward': 0,
        'agent_caption': 'Episode one second step.',
      }),
    ];
    final episodeTwoSteps = [
      ExecutionTraceStep.fromJson({
        'state': 5,
        'action': 0,
        'next_state': 6,
        'reward': 2,
        'agent_caption': 'Episode two first step.',
      }),
      ExecutionTraceStep.fromJson({
        'state': 6,
        'action': 3,
        'next_state': 7,
        'reward': 0,
        'agent_caption': 'Episode two second step.',
      }),
    ];

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TraceReplayPanel(
            runStatusLabel: 'Passed',
            statusMessage: 'ok',
            totalReward: 1,
            averageReward: 0.5,
            bestEpisodeReward: 2,
            episodesCompleted: 2,
            stepsRecorded: 4,
            videoPath: '',
            testResults: const [],
            stepTrace: episodeTwoSteps,
            traceEpisodes: [
              ExecutionTraceEpisode(
                episodeIndex: 0,
                steps: episodeOneSteps,
              ),
              ExecutionTraceEpisode(
                episodeIndex: 1,
                steps: episodeTwoSteps,
              ),
            ],
            episodeSummaries: const [
              ExecutionEpisodeSummary(
                episodeIndex: 0,
                stepCount: 2,
                totalReward: -1,
                terminated: false,
                truncated: false,
              ),
              ExecutionEpisodeSummary(
                episodeIndex: 1,
                stepCount: 2,
                totalReward: 2,
                terminated: true,
                truncated: false,
              ),
            ],
          ),
        ),
      ),
    );

    // The curated selector defaults to the last ("Late") episode.
    expect(find.text('Early'), findsOneWidget);
    expect(find.text('Late'), findsOneWidget);
    expect(find.text('Episode two first step.'), findsWidgets);
    expect(find.text('s5 -> 6'), findsWidgets);

    // Switch to the early episode via the curated Early/Mid/Late control.
    await tester.tap(find.text('Early'));
    await tester.pumpAndSettle();

    expect(find.text('Episode one first step.'), findsWidgets);
    expect(find.text('s0 -> 1'), findsWidgets);
    expect(find.text('Episode two first step.'), findsNothing);
  });

  testWidgets('keeps mobile panes synchronized with keyboard step changes',
      (tester) async {
    tester.view.physicalSize = const Size(520, 900);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TraceReplayPanel(
            runStatusLabel: 'Passed',
            statusMessage: 'ok',
            totalReward: 1,
            averageReward: 0.5,
            bestEpisodeReward: 1,
            episodesCompleted: 1,
            stepsRecorded: 2,
            videoPath: '',
            testResults: const [],
            stepTrace: [
              ExecutionTraceStep.fromJson({
                'state': 0,
                'action': 1,
                'next_state': 1,
                'reward': 0,
                'math_title': 'First step math',
                'math_lines': ['first target'],
                'agent_caption': 'First mobile step.',
              }),
              ExecutionTraceStep.fromJson({
                'state': 1,
                'action': 2,
                'next_state': 2,
                'reward': 1,
                'math_title': 'Second step math',
                'math_lines': ['second target'],
                'agent_caption': 'Second mobile step.',
              }),
            ],
          ),
        ),
      ),
    );

    await _selectBinderSection(tester, 'Math');

    expect(find.text('First step math'), findsOneWidget);
    expect(find.text('Second step math'), findsNothing);

    await tester.sendKeyEvent(LogicalKeyboardKey.arrowRight);
    await tester.pumpAndSettle();

    expect(find.text('Step 2 / 2'), findsOneWidget);
    expect(find.text('Second step math'), findsOneWidget);
    expect(find.text('First step math'), findsNothing);
  });

  testWidgets('renders populated replay without overflow at QA breakpoints',
      (tester) async {
    final semantics = tester.ensureSemantics();
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    try {
      for (final size in const [
        Size(375, 900),
        Size(768, 900),
        Size(1440, 1000),
      ]) {
        tester.view.physicalSize = size;
        tester.view.devicePixelRatio = 1;

        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pumpWidget(_traceReplayHarness());
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull, reason: 'breakpoint $size');
        // Curated Early/Late episode selector instead of a per-episode dump.
        expect(find.text('Late'), findsOneWidget, reason: 'breakpoint $size');
        expect(find.text('Why this update is correct'), findsOneWidget,
            reason: 'breakpoint $size');
        await _selectBinderSection(tester, 'Math');
        expect(find.text('Q-learning numeric update'), findsOneWidget);
        expect(find.byType(Slider), findsOneWidget);
        // Curated episode selector renders its Early/Late labels.
        expect(find.text('Early'), findsOneWidget);
        expect(find.text('Late'), findsOneWidget);
      }
    } finally {
      semantics.dispose();
    }
  });

  testWidgets('keeps replay binder sections deterministic', (tester) async {
    tester.view.physicalSize = const Size(1500, 900);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(_traceReplayHarness());
    await tester.pumpAndSettle();

    expect(find.text('Step'), findsOneWidget);
    expect(find.text('Math'), findsOneWidget);
    expect(find.text('Replay'), findsOneWidget);
    expect(find.byIcon(Icons.tune_rounded), findsNothing);
    expect(find.text('Customize visible binder sections'), findsNothing);
  });

  testWidgets('shows generated replay video even when step trace is empty',
      (tester) async {
    await tester.pumpWidget(
      _replayOnlyHarness(
        videoPath: '/tmp/generated-replay.mp4',
        replayRenderStatus: 'ready',
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Manim Equation Replay'), findsOneWidget);
    expect(find.byKey(const ValueKey('replay-video-frame')), findsOneWidget);
    expect(find.byType(VideoProgressIndicator), findsOneWidget);
    expect(
        find.byKey(const ValueKey('replay-video-status-chip')), findsOneWidget);
    expect(find.text('Ready'), findsOneWidget);
    expect(
      find.byKey(const ValueKey('replay-video-timeline')),
      findsOneWidget,
    );
    expect(find.text('00:00 / 02:00'), findsOneWidget);
    expect(find.text('Run code to see replay steps here.'), findsNothing);
    expect(
      find.text(
        'Generated video links each agent step to the Bellman or TD numeric update.',
      ),
      findsNothing,
    );
  });

  testWidgets('swaps from replay render status placeholder to loaded video',
      (tester) async {
    await tester.pumpWidget(
      _replayOnlyHarness(
        videoPath: '',
        replayRenderStatus: 'rendering',
      ),
    );
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey('replay-video-status-message')),
      findsOneWidget,
    );
    expect(find.text('Rendering'), findsOneWidget);
    expect(
      find.text(
          'The generated MP4 is rendering. Use the interactive trace meanwhile.'),
      findsOneWidget,
    );
    expect(find.byType(VideoProgressIndicator), findsNothing);

    await tester.pumpWidget(
      _replayOnlyHarness(
        videoPath: '/tmp/generated-replay.mp4',
        replayRenderStatus: 'ready',
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(VideoProgressIndicator), findsOneWidget);
    expect(find.text('Ready'), findsOneWidget);
    expect(find.text('00:00 / 02:00'), findsOneWidget);
    expect(
      find.text(
          'The generated MP4 is rendering. Use the interactive trace meanwhile.'),
      findsNothing,
    );
  });

  testWidgets('shows queued replay placeholder state', (tester) async {
    await tester.pumpWidget(
      _replayOnlyHarness(
        videoPath: '',
        replayRenderStatus: 'queued',
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Queued'), findsOneWidget);
    expect(
      find.text(
          'The generated MP4 is queued. Use the interactive trace meanwhile.'),
      findsOneWidget,
    );
  });

  testWidgets('shows failed replay placeholder state', (tester) async {
    await tester.pumpWidget(
      _replayOnlyHarness(
        videoPath: '',
        replayRenderStatus: 'failed',
        replayRenderError: 'render crashed',
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Failed'), findsOneWidget);
    expect(find.text('render crashed'), findsOneWidget);
  });

  testWidgets('shows timeout replay placeholder state', (tester) async {
    await tester.pumpWidget(
      _replayOnlyHarness(
        videoPath: '',
        replayRenderStatus: 'timeout',
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Running'), findsOneWidget);
    expect(
      find.text('The generated MP4 is still running in the background.'),
      findsOneWidget,
    );
  });

  testWidgets('shows unavailable replay placeholder state', (tester) async {
    await tester.pumpWidget(
      _replayOnlyHarness(
        videoPath: '',
        replayRenderStatus: 'unavailable',
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Unavailable'), findsOneWidget);
    expect(
      find.text(
          'Interactive replay is available. Generated video is not ready.'),
      findsOneWidget,
    );
  });

  testWidgets('replay placeholder can jump back to the interactive step trace',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(_traceReplayHarness());
    await tester.pumpAndSettle();

    await _selectBinderSection(tester, 'Replay');
    expect(find.text('Pending'), findsOneWidget);
    expect(
        find.byKey(const ValueKey('replay-open-step-trace')), findsOneWidget);
    expect(
      find.byKey(const ValueKey('replay-open-step-trace-inline')),
      findsOneWidget,
    );

    await tester.ensureVisible(
      find.byKey(const ValueKey('replay-open-step-trace')),
    );
    await tester.tap(find.byKey(const ValueKey('replay-open-step-trace')));
    await tester.pumpAndSettle();

    expect(find.text('What This Step Means'), findsOneWidget);
    expect(find.text('Trace Outline'), findsOneWidget);
  });

  testWidgets('toolbar jump pills move to reward and terminal steps',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TraceReplayPanel(
            runStatusLabel: 'Passed',
            statusMessage: 'ok',
            totalReward: 0,
            averageReward: 0,
            bestEpisodeReward: 1,
            episodesCompleted: 1,
            stepsRecorded: 3,
            videoPath: '',
            testResults: const [],
            stepTrace: [
              ExecutionTraceStep.fromJson({
                'state': 0,
                'action': 0,
                'next_state': 1,
                'reward': 0,
                'agent_caption': 'Opening step.',
              }),
              ExecutionTraceStep.fromJson({
                'state': 1,
                'action': 1,
                'next_state': 2,
                'reward': 1,
                'agent_caption': 'Reward step.',
              }),
              ExecutionTraceStep.fromJson({
                'state': 2,
                'action': 2,
                'next_state': 3,
                'reward': 0,
                'agent_caption': 'Terminal step.',
                'grid_metadata': {
                  'environment': 'FrozenLake',
                  'rows': 2,
                  'columns': 2,
                  'state': 2,
                  'next_state': 3,
                  'state_coordinates': {'row': 1, 'column': 0},
                  'next_state_coordinates': {'row': 1, 'column': 1},
                  'action': 2,
                  'action_label': 'Right',
                  'reward': 0,
                  'terminated': true,
                  'truncated': false,
                  'cells': [
                    {
                      'state': 0,
                      'row': 0,
                      'column': 0,
                      'tile_type': 'S',
                      'terminal': false,
                    },
                    {
                      'state': 1,
                      'row': 0,
                      'column': 1,
                      'tile_type': 'F',
                      'terminal': false,
                    },
                    {
                      'state': 2,
                      'row': 1,
                      'column': 0,
                      'tile_type': 'F',
                      'terminal': false,
                    },
                    {
                      'state': 3,
                      'row': 1,
                      'column': 1,
                      'tile_type': 'G',
                      'terminal': true,
                    },
                  ],
                },
              }),
            ],
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Reward'), findsOneWidget);
    expect(find.text('Terminal'), findsOneWidget);
    expect(find.text('End'), findsOneWidget);

    await tester.tap(find.text('Reward'));
    await tester.pumpAndSettle();
    expect(find.text('Step 2 / 3'), findsOneWidget);
    expect(find.text('Reward step.'), findsWidgets);

    await tester.tap(find.text('Terminal'));
    await tester.pumpAndSettle();
    expect(find.text('Step 3 / 3'), findsOneWidget);
    expect(find.text('Terminal step.'), findsWidgets);

    await tester.tap(find.text('Start'));
    await tester.pumpAndSettle();
    expect(find.text('Step 1 / 3'), findsOneWidget);
    expect(find.text('Opening step.'), findsWidgets);
  });

  testWidgets('renders Taxi grid with passenger and destination overlays',
      (tester) async {
    tester.view.physicalSize = const Size(1400, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TraceReplayPanel(
            runStatusLabel: 'Passed',
            statusMessage: 'ok',
            totalReward: -1,
            averageReward: -1,
            bestEpisodeReward: -1,
            episodesCompleted: 1,
            stepsRecorded: 1,
            videoPath: '',
            testResults: const [],
            stepTrace: [
              ExecutionTraceStep.fromJson({
                'state': 328,
                'action': 0,
                'next_state': 428,
                'reward': -1,
                'transition_probability': 1,
                'agent_caption': 'Agent selected South.',
                'grid_metadata': {
                  'environment': 'Taxi',
                  'rows': 5,
                  'columns': 5,
                  'state': 13,
                  'next_state': 18,
                  'encoded_state': 328,
                  'encoded_next_state': 428,
                  'state_coordinates': {'row': 2, 'column': 3},
                  'next_state_coordinates': {'row': 3, 'column': 3},
                  'passenger': {
                    'location': 'R',
                    'row': 0,
                    'column': 0,
                    'in_taxi': false,
                  },
                  'destination': {
                    'label': 'B',
                    'row': 4,
                    'column': 3,
                  },
                  'action': 0,
                  'action_label': 'South',
                  'reward': -1,
                  'terminated': false,
                  'truncated': false,
                  'cells': [
                    for (var r = 0; r < 5; r++)
                      for (var c = 0; c < 5; c++)
                        {
                          'state': r * 5 + c,
                          'row': r,
                          'column': c,
                          'tile_type': (r == 0 && c == 0)
                              ? 'R'
                              : (r == 0 && c == 4)
                                  ? 'G'
                                  : (r == 4 && c == 0)
                                      ? 'Y'
                                      : (r == 4 && c == 3)
                                          ? 'B'
                                          : 'F',
                          'terminal': false,
                        },
                  ],
                },
                'equation_update': {
                  'kind': 'q_learning',
                  'lhs': 'Q(328,0)',
                  'old_value': 0,
                  'reward': -1,
                  'gamma': 0.95,
                  'bootstrap_label': 'max_a Q(428,a)',
                  'bootstrap_value': 0,
                  'td_target': -1,
                  'td_error': -1,
                  'alpha': 0.1,
                  'new_value': -0.1,
                  'code_focus':
                      'Q[state][action] += alpha * (td_target - Q[state][action])',
                },
              }),
            ],
          ),
        ),
      ),
    );

    await _selectBinderSection(tester, 'Step');
    expect(find.text('Taxi grid'), findsOneWidget);
    expect(find.text('state 328'), findsOneWidget);
    expect(find.text('South'), findsWidgets);
    expect(find.text('passenger @ R'), findsOneWidget);
    expect(find.text('dest B'), findsOneWidget);
  });
}

Future<void> _selectBinderSection(WidgetTester tester, String label) async {
  final visibleLabel = find.text(label);
  if (visibleLabel.evaluate().isNotEmpty) {
    await tester.tap(visibleLabel.first);
    await tester.pumpAndSettle();
    return;
  }

  final dropdown = find.byWidgetPredicate((widget) => widget is DropdownButton);
  if (dropdown.evaluate().isEmpty) {
    throw StateError('Could not find replay binder section "$label".');
  }
  await tester.tap(dropdown.last);
  await tester.pumpAndSettle();
  await tester.tap(find.text(label).last);
  await tester.pumpAndSettle();
}

Widget _traceReplayHarness() {
  final episodeOne = [
    ExecutionTraceStep.fromJson({
      'state': 36,
      'action': 1,
      'next_state': 36,
      'reward': -100,
      'agent_caption': 'Earlier episode fell into the cliff.',
    }),
  ];
  final episodeTwo = [_qLearningTraceStep()];

  return MaterialApp(
    home: Scaffold(
      body: TraceReplayPanel(
        runStatusLabel: 'Passed',
        statusMessage: 'ok',
        totalReward: -1,
        averageReward: -50.5,
        bestEpisodeReward: -1,
        episodesCompleted: 2,
        stepsRecorded: 2,
        videoPath: '',
        testResults: const [],
        stepTrace: episodeTwo,
        traceEpisodes: [
          ExecutionTraceEpisode(episodeIndex: 0, steps: episodeOne),
          ExecutionTraceEpisode(episodeIndex: 1, steps: episodeTwo),
        ],
        episodeSummaries: const [
          ExecutionEpisodeSummary(
            episodeIndex: 0,
            stepCount: 1,
            totalReward: -100,
            terminated: false,
            truncated: false,
          ),
          ExecutionEpisodeSummary(
            episodeIndex: 1,
            stepCount: 1,
            totalReward: -1,
            terminated: true,
            truncated: false,
          ),
        ],
      ),
    ),
  );
}

Widget _replayOnlyHarness({
  required String videoPath,
  required String replayRenderStatus,
  String? replayRenderError,
}) {
  return MaterialApp(
    home: Scaffold(
      body: TraceReplayPanel(
        runStatusLabel: 'Passed',
        statusMessage: 'ok',
        totalReward: 0,
        averageReward: 0,
        bestEpisodeReward: 0,
        episodesCompleted: 0,
        stepsRecorded: 0,
        videoPath: videoPath,
        replayRenderStatus: replayRenderStatus,
        replayRenderError: replayRenderError,
        testResults: const [],
        stepTrace: const [],
        traceEpisodes: const [],
        episodeSummaries: const [],
      ),
    ),
  );
}

ExecutionTraceStep _qLearningTraceStep() {
  return ExecutionTraceStep.fromJson({
    'state': 36,
    'action': 0,
    'next_state': 24,
    'reward': -1,
    'transition_probability': 1,
    'agent_caption':
        'Q-learning selects Up, observes reward -1, and applies the max-next-state bootstrap.',
    'code_title': 'Code Trace',
    'code_lines': [
      'action = epsilon_greedy(Q[state], epsilon)',
      'best_next_value = max(Q[next_state])',
      'td_target = reward + gamma * best_next_value',
      'Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])',
    ],
    'math_title': 'TD / Q-Learning',
    'math_equation':
        r'Q(s,a)\leftarrow Q(s,a)+\alpha[r+\gamma\max_{a^\prime}Q(s^\prime,a^\prime)-Q(s,a)]',
    'math_lines': [
      'TD target = -1 + 0.95 * 0 = -1.',
      'Q(36, 0) moves by alpha times the TD error.',
    ],
    'updated_values': {'Q(36, 0)': -0.1},
    'trace_schema_version': 2,
    'grid_metadata': {
      'environment': 'CliffWalking',
      'rows': 4,
      'columns': 12,
      'state': 36,
      'next_state': 24,
      'state_coordinates': {'row': 3, 'column': 0},
      'next_state_coordinates': {'row': 2, 'column': 0},
      'action': 0,
      'action_label': 'Up',
      'reward': -1,
      'terminated': false,
      'truncated': false,
      'cells': [
        {
          'state': 24,
          'row': 2,
          'column': 0,
          'tile_type': 'F',
          'terminal': false,
        },
        {
          'state': 36,
          'row': 3,
          'column': 0,
          'tile_type': 'S',
          'terminal': false,
        },
        {
          'state': 47,
          'row': 3,
          'column': 11,
          'tile_type': 'G',
          'terminal': true,
        },
      ],
    },
    'tables': {
      'kind': 'q_table',
      'before': [
        [0, 0],
        [0, 0],
      ],
      'after': [
        [0, 0],
        [-0.1, 0],
      ],
      'active_cell': {'row': 1, 'column': 0},
      'bootstrap_cell': {'row': 0, 'column': 0},
      'changed_cells': [
        {'row': 1, 'column': 0},
      ],
      'action_labels': ['Up', 'Right'],
    },
    'equation_update': {
      'kind': 'q_learning',
      'lhs': 'Q(36,0)',
      'old_value': 0,
      'reward': -1,
      'gamma': 0.95,
      'bootstrap_label': 'max_a Q(24,a)',
      'bootstrap_value': 0,
      'td_target': -1,
      'td_error': -1,
      'alpha': 0.1,
      'new_value': -0.1,
      'substitution': '0.0 + 0.1 * (-1.0 + 0.95 * 0.0 - 0.0)',
      'code_focus':
          'Q[state][action] += alpha * (td_target - Q[state][action])',
    },
    'explanation': {
      'summary': 'Q-learning updates one action-value cell.',
      'why_correct':
          'Q-learning uses the observed reward plus the best next-state value, then updates only the highlighted Q cell.',
      'code_focus':
          'Q[state][action] += alpha * (td_target - Q[state][action])',
      'table_focus': 'row 1, column 0',
    },
  });
}
