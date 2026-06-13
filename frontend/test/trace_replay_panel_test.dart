import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/features/workspace/trace_replay_panel.dart';

void main() {
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

    await _selectBinderSection(tester, 'Equation');
    expect(find.text('SARSA numeric update'), findsOneWidget);
    await _selectBinderSection(tester, 'Table');
    expect(find.text('Q-table Inspector'), findsOneWidget);
    expect(find.text('active s1, a0'), findsOneWidget);
    expect(find.text('bootstrap s0, a1'), findsOneWidget);
    await _selectBinderSection(tester, 'Equation');
    expect(find.textContaining('0.0 + 0.1'), findsOneWidget);
    await _selectBinderSection(tester, 'Code');
    expect(
        find.byKey(const ValueKey('trace-code-focus-line-0')), findsOneWidget);
    await _selectBinderSection(tester, 'Overview');
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

    await _selectBinderSection(tester, 'Equation');
    expect(find.text('Value iteration action comparison'), findsOneWidget);
    expect(find.text('Selected action'), findsOneWidget);
    expect(find.text('Left'), findsWidgets);
    await _selectBinderSection(tester, 'Table');
    expect(find.text('Value Table Inspector'), findsOneWidget);
    await _selectBinderSection(tester, 'Equation');
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

    await _selectBinderSection(tester, 'Environment');
    expect(find.text('Blackjack observation'), findsOneWidget);
    await _selectBinderSection(tester, 'Equation');
    expect(find.text('First-visit return update'), findsOneWidget);
    await _selectBinderSection(tester, 'Table');
    expect(find.text('Monte Carlo Episode Inspector'), findsOneWidget);
    expect(find.text('Return ladder'), findsOneWidget);
    await _selectBinderSection(tester, 'Environment');
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

    await _selectBinderSection(tester, 'Environment');
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

    await _selectBinderSection(tester, 'Equation');

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
        expect(find.text('Generated Step Replay'), findsOneWidget);
        // Curated Early/Late episode selector instead of a per-episode dump.
        expect(find.text('Late'), findsOneWidget, reason: 'breakpoint $size');
        expect(find.text('Why this update is correct'), findsOneWidget,
            reason: 'breakpoint $size');
        await _selectBinderSection(tester, 'Equation');
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

  testWidgets('customizes visible replay binder sections', (tester) async {
    tester.view.physicalSize = const Size(1500, 900);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(_traceReplayHarness());
    await tester.pumpAndSettle();

    expect(find.text('Code'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.tune_rounded));
    await tester.pumpAndSettle();
    await tester.tap(_visibleBinderMenuItem('Code').last);
    await tester.pumpAndSettle();

    expect(find.text('Code'), findsNothing);

    await tester.tap(find.byIcon(Icons.tune_rounded));
    await tester.pumpAndSettle();
    await tester.tap(_visibleBinderMenuItem('Code').last);
    await tester.pumpAndSettle();

    expect(find.text('Code'), findsOneWidget);
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

Finder _visibleBinderMenuItem(String label) {
  return find.ancestor(
    of: find.text(label).last,
    matching: find.byWidgetPredicate(
      (widget) => widget is CheckedPopupMenuItem,
    ),
  );
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
