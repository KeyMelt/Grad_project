import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/lesson_models.dart';

void main() {
  test('LessonSection parses backend lesson catalog JSON', () {
    final section = LessonSection.fromJson(const {
      'title': 'Dynamic Programming',
      'lessons': [
        {
          'id': 'dp_policy_eval',
          'title': 'Policy Evaluation',
          'category': 'Dynamic Programming',
          'description': 'Evaluate a fixed policy.',
          'starter_code': 'def policy_evaluation(): pass',
          'backend_enabled': true,
          'concept_video': {
            'stream_path': '/media/concept-videos/dp_policy_eval_concept.mp4',
            'duration_label': '03:30',
            'summary': 'Bellman expectation walkthrough.',
            'highlights': ['Policy weighting'],
            'theory_equation': r'V^\pi(s)=\sum_a \pi(a|s) \cdots',
            'worked_example': 'One Bellman expectation sweep.',
            'misconception_to_prevent':
                'Policy evaluation does not change the policy.',
            'takeaway_line':
                'Policy evaluation recomputes state values under a fixed policy.',
            'theory_verification': [
              {
                'claim': 'Policy evaluation uses Bellman expectation backups.',
                'source_url':
                    'https://incompleteideas.net/book/the-book-2nd.html',
                'validation_note': 'Sutton and Barto Chapter 4.',
                'is_inference': false,
              },
            ],
          },
          'exercise': {
            'title': 'Implement iterative policy evaluation',
            'overview': 'Complete the Bellman update.',
            'tasks': ['Fill the backup loop.'],
            'template_blanks': [
              {
                'blank_id': 'policy_eval_expectation',
                'kind': 'block',
                'prompt': 'Accumulate transition branches.',
                'expected_concept': 'Bellman expectation backup',
                'approx_line_anchor': 11,
              },
            ],
            'success_criteria': ['The function returns values.'],
            'code_tip': 'Tune DISCOUNT_FACTOR in code.',
          },
        },
      ],
    });

    final lesson = section.lessons.single;
    expect(section.title, 'Dynamic Programming');
    expect(lesson.id, 'dp_policy_eval');
    expect(lesson.conceptVideo.durationLabel, '03:30');
    expect(lesson.conceptVideo.effectiveStreamPath,
        '/media/concept-videos/dp_policy_eval_concept.mp4');
    expect(lesson.conceptVideo.theoryEquation, contains(r'V^\pi'));
    expect(lesson.conceptVideo.theoryVerification.single.claim,
        contains('Bellman expectation'));
    expect(lesson.exercise.templateBlanks.single.blankId,
        'policy_eval_expectation');
    expect(
        lesson.exercise.successCriteria.single, 'The function returns values.');
  });
}
