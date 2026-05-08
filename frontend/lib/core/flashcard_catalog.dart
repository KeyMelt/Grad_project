import 'lesson_models.dart';

const List<StudyFlashcard> studyFlashcards = [
  StudyFlashcard(
    term: 'Bellman Expectation',
    category: 'Dynamic Programming',
    explanation:
        'Policy evaluation updates each state with an expectation over policy choices and transition probabilities.',
  ),
  StudyFlashcard(
    term: 'Bellman Optimality',
    category: 'Dynamic Programming',
    explanation:
        'Value iteration selects the largest action backup instead of averaging under a fixed policy.',
  ),
  StudyFlashcard(
    term: 'Policy Improvement',
    category: 'Dynamic Programming',
    explanation:
        'Policy improvement chooses the greedy action for each state using the current value table.',
  ),
  StudyFlashcard(
    term: 'First-Visit Return',
    category: 'Monte Carlo Methods',
    explanation:
        'First-visit Monte Carlo updates a state only once per episode, using the full discounted return from its first occurrence.',
  ),
  StudyFlashcard(
    term: 'SARSA',
    category: 'Temporal Difference',
    explanation:
        'SARSA is on-policy because its TD target uses the next action that the behaviour policy actually sampled.',
  ),
  StudyFlashcard(
    term: 'TD Target',
    category: 'Temporal Difference',
    explanation:
        'The Q-learning target is the immediate reward plus gamma times the best next-state value.',
  ),
  StudyFlashcard(
    term: 'Transition Probability',
    category: 'Environment Model',
    explanation:
        'Transition probability tells us how likely the environment is to move to a particular next state after a chosen action.',
  ),
  StudyFlashcard(
    term: 'Normalized Gain',
    category: 'Assessment',
    explanation:
        'N-gain measures conceptual growth as (post - pre) / (100 - pre).',
  ),
];
