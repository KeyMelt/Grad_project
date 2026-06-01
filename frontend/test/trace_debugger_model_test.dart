import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';

void main() {
  group('ExecutionTraceStep trace debugger fields', () {
    test('parses TD equation updates and Q-table snapshots', () {
      final step = ExecutionTraceStep.fromJson({
        'state': 36,
        'action': 0,
        'next_state': 24,
        'reward': -1,
        'transition_probability': 1,
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
          'summary': 'Q-learning updates one Q cell.',
          'why_correct':
              'The TD target uses the reward plus the best next-state value.',
          'code_focus':
              'Q[state][action] += alpha * (td_target - Q[state][action])',
          'table_focus': 'row 1, column 0',
        },
      });

      expect(step.traceSchemaVersion, 2);
      expect(step.equationUpdate?.kind, 'q_learning');
      expect(step.equationUpdate?.isTemporalDifference, isTrue);
      expect(step.equationUpdate?.tdError, -1);
      expect(step.tableSnapshot?.kind, 'q_table');
      expect(step.tableSnapshot?.activeCell?.row, 1);
      expect(step.tableSnapshot?.bootstrapCell?.column, 1);
      expect(step.tableSnapshot?.isChanged(1, 0), isTrue);
      expect(
          step.tableSnapshot?.valueAfter(step.tableSnapshot?.activeCell), -0.1);
      expect(step.explanation?.whyCorrect, contains('TD target'));
      expect(step.explanation?.tableFocus, 'row 1, column 0');
    });

    test('ignores non-numeric legacy updated values instead of crashing', () {
      final step = ExecutionTraceStep.fromJson({
        'updated_values': {
          'pi(0)': 'Right',
          'backup': 0.42,
        },
      });

      expect(step.updatedValues, {'backup': 0.42});
    });

    test('parses DP action backups and transition branch terms', () {
      final step = ExecutionTraceStep.fromJson({
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
      });

      final details = step.equationUpdate?.dpDetails;
      expect(step.equationUpdate?.isDynamicProgramming, isTrue);
      expect(details?.selectedActionLabel, 'Left');
      expect(details?.actionBackups.single.expectedReturn, 1.9);
      expect(details?.actionBackups.single.transitionTerms.single.nextState, 1);
      expect(details?.actionBackups.single.transitionTerms.single.contribution,
          1.9);
      expect(step.tableSnapshot?.kind, 'value_table');
    });

    test('parses MC Blackjack observation and return ladder details', () {
      final step = ExecutionTraceStep.fromJson({
        'trace_schema_version': 2,
        'equation_update': {
          'kind': 'mc_first_visit',
          'lhs': 'V((15, 10, False))',
          'gamma': 0.9,
          'td_target': 0.9,
          'new_value': 0.9,
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
      });

      final details = step.equationUpdate?.mcDetails;
      expect(step.equationUpdate?.isMonteCarlo, isTrue);
      expect(details?.observation?.playerSum, 15);
      expect(
          details?.observation?.label, 'Player 15 | Dealer 10 | Usable ace no');
      expect(details?.returnTerms.last.runningReturn, 0.9);
      expect(details?.returnsHistory, [0.9]);
      expect(details?.episodeStrip.single.actionLabel, 'Hit');
    });

    test('parses grid metadata for grid-world companion renderers', () {
      final step = ExecutionTraceStep.fromJson({
        'state': 36,
        'next_state': 24,
        'action': 0,
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
              'state': 36,
              'row': 3,
              'column': 0,
              'tile_type': 'S',
              'terminal': false,
            },
            {
              'state': 37,
              'row': 3,
              'column': 1,
              'tile_type': 'C',
              'terminal': false,
            },
          ],
        },
      });

      expect(step.gridMetadata?.environment, 'CliffWalking');
      expect(step.gridMetadata?.rows, 4);
      expect(step.gridMetadata?.stateCoordinates?.row, 3);
      expect(step.gridMetadata?.nextStateCoordinates?.column, 0);
      expect(step.gridMetadata?.actionLabel, 'Up');
      expect(step.gridMetadata?.cellAtState(37)?.tileType, 'C');
    });

    test('parses full trace episodes while preserving legacy step trace', () {
      final result = ExecutionResult.fromJson({
        'message': 'Execution completed.',
        'lesson': {'title': 'SARSA'},
        'metrics': {
          'total_reward': 1,
          'average_reward': 0.5,
          'best_episode_reward': 2,
          'episodes_completed': 2,
          'steps_recorded': 3,
        },
        'step_trace': [
          {
            'state': 2,
            'action': 0,
            'next_state': 3,
            'reward': 2,
          },
        ],
        'trace_episodes': [
          {
            'episode_index': 0,
            'steps': [
              {
                'state': 0,
                'action': 1,
                'next_state': 1,
                'reward': -1,
              },
            ],
          },
          {
            'episode_index': 1,
            'steps': [
              {
                'state': 2,
                'action': 0,
                'next_state': 3,
                'reward': 2,
              },
            ],
          },
        ],
        'episode_summaries': [
          {
            'episode_index': 0,
            'step_count': 1,
            'total_reward': -1,
            'terminated': false,
            'truncated': false,
          },
          {
            'episode_index': 1,
            'step_count': 1,
            'total_reward': 2,
            'terminated': true,
            'truncated': false,
          },
        ],
      });

      expect(result.stepTrace.single.state, 2);
      expect(result.traceEpisodes, hasLength(2));
      expect(result.traceEpisodes.first.episodeIndex, 0);
      expect(result.traceEpisodes.first.steps.single.reward, -1);
      expect(result.traceEpisodes.last.steps.single.nextState, 3);
      expect(result.episodeSummaries.last.totalReward, 2);
      expect(result.episodeSummaries.last.terminated, isTrue);
    });
  });
}
