import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';

class QuizSection extends StatelessWidget {
  final LearnerProfile? learner;
  final LearnerProgress progress;
  final QuizSessionData? activeQuiz;
  final Map<String, int> quizAnswers;
  final QuizAttemptSummary? lastQuizSummary;
  final bool isLoading;
  final String statusMessage;
  final ValueChanged<QuizPhase> onStartQuiz;
  final void Function(String questionId, int selectedIndex) onAnswerQuestion;
  final VoidCallback onSubmitQuiz;

  const QuizSection({
    super.key,
    required this.learner,
    required this.progress,
    required this.activeQuiz,
    required this.quizAnswers,
    required this.lastQuizSummary,
    required this.isLoading,
    required this.statusMessage,
    required this.onStartQuiz,
    required this.onAnswerQuestion,
    required this.onSubmitQuiz,
  });

  @override
  Widget build(BuildContext context) {
    if (learner == null) {
      return const _QuizGateCard(
        title: 'Quiz Section',
        message: 'Sign in first to start quizzes.',
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHero(),
          const SizedBox(height: AppConstants.defaultPadding),
          if (activeQuiz == null) _buildQuizLauncher(),
          if (activeQuiz != null) _buildActiveQuiz(),
          if (lastQuizSummary != null) ...[
            const SizedBox(height: AppConstants.defaultPadding),
            _buildLatestResult(lastQuizSummary!),
          ],
        ],
      ),
    );
  }

  Widget _buildHero() {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(28),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          gradient: const LinearGradient(
            colors: [
              Color(0xFF0F172A),
              Color(0xFF155EEF),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Assessment Flow for ${learner!.displayName}',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Take pre-test, practice, then post-test.',
              style: TextStyle(
                color: Color(0xFFE2E8F0),
                height: 1.5,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              statusMessage,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuizLauncher() {
    return Wrap(
      spacing: AppConstants.defaultPadding,
      runSpacing: AppConstants.defaultPadding,
      children: [
        _QuizActionCard(
          title: 'Randomized Pre-test',
          description: 'Check your starting understanding.',
          footer:
              'Attempts: ${progress.quizAttempts['pretest'] ?? 0} • Latest: ${_formatScore(progress.pretestScore)}',
          buttonLabel: isLoading ? 'Preparing...' : 'Start Pre-test',
          onPressed: isLoading ? null : () => onStartQuiz(QuizPhase.pretest),
        ),
        _QuizActionCard(
          title: 'Randomized Post-test',
          description: 'Measure progress after practice.',
          footer: progress.successfulRuns == 0
              ? 'Complete at least one lesson run to unlock the post-test.'
              : 'Attempts: ${progress.quizAttempts['posttest'] ?? 0} • Latest: ${_formatScore(progress.posttestScore)}',
          buttonLabel: isLoading ? 'Preparing...' : 'Start Post-test',
          onPressed: isLoading || progress.successfulRuns == 0
              ? null
              : () => onStartQuiz(QuizPhase.posttest),
        ),
      ],
    );
  }

  Widget _buildActiveQuiz() {
    final quiz = activeQuiz!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              '${quizPhaseLabel(quiz.phase)} in progress',
              style: const TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 24,
                fontWeight: FontWeight.w700,
              ),
            ),
            const Spacer(),
            Text(
              '${quizAnswers.length}/${quiz.questions.length} answered',
              style: const TextStyle(
                color: AppTheme.textSecondary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        const Text(
          'Questions are randomized for every attempt.',
          style: TextStyle(
            color: AppTheme.textSecondary,
            height: 1.45,
          ),
        ),
        const SizedBox(height: AppConstants.defaultPadding),
        ...quiz.questions.asMap().entries.map(
              (entry) => Padding(
                padding: const EdgeInsets.only(
                  bottom: AppConstants.defaultPadding,
                ),
                child: _QuestionCard(
                  questionNumber: entry.key + 1,
                  question: entry.value,
                  selectedIndex: quizAnswers[entry.value.id],
                  onSelect: (index) => onAnswerQuestion(entry.value.id, index),
                ),
              ),
            ),
        Align(
          alignment: Alignment.centerRight,
          child: ElevatedButton.icon(
            onPressed: isLoading ? null : onSubmitQuiz,
            icon: isLoading
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Icon(Icons.assignment_turned_in_outlined),
            label: Text(
              isLoading ? 'Submitting...' : 'Submit Quiz',
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLatestResult(QuizAttemptSummary summary) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        side: const BorderSide(color: AppTheme.borderLight),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Wrap(
          spacing: 24,
          runSpacing: 16,
          children: [
            _ResultMetric(
              label: quizPhaseLabel(summary.phase),
              value: '${summary.score}/${summary.totalQuestions}',
              caption: 'Latest score',
            ),
            _ResultMetric(
              label: 'Percentage',
              value: '${summary.percentage.toStringAsFixed(1)}%',
              caption: 'Score percent',
            ),
            _ResultMetric(
              label: 'N-gain',
              value: summary.nGain == null
                  ? 'Pending'
                  : summary.nGain!.toStringAsFixed(3),
              caption: 'Shown after both quizzes',
            ),
          ],
        ),
      ),
    );
  }

  String _formatScore(double? value) {
    if (value == null) {
      return 'Pending';
    }
    return '${value.toStringAsFixed(1)}%';
  }
}

class _QuizGateCard extends StatelessWidget {
  final String title;
  final String message;

  const _QuizGateCard({
    required this.title,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 620),
        child: Card(
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
            side: const BorderSide(color: AppTheme.borderLight),
          ),
          child: Padding(
            padding: const EdgeInsets.all(28),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.lock_outline,
                  size: 42,
                  color: AppTheme.primaryBlue,
                ),
                const SizedBox(height: 18),
                Text(
                  title,
                  style: const TextStyle(
                    color: AppTheme.textPrimary,
                    fontSize: 24,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  message,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    color: AppTheme.textSecondary,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _QuizActionCard extends StatelessWidget {
  final String title;
  final String description;
  final String footer;
  final String buttonLabel;
  final VoidCallback? onPressed;

  const _QuizActionCard({
    required this.title,
    required this.description,
    required this.footer,
    required this.buttonLabel,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 380,
      child: Card(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppConstants.cardRadius),
          side: const BorderSide(color: AppTheme.borderLight),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                description,
                style: const TextStyle(
                  color: AppTheme.textSecondary,
                  height: 1.45,
                ),
              ),
              const SizedBox(height: 18),
              Text(
                footer,
                style: const TextStyle(
                  color: AppTheme.textSecondary,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 18),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: onPressed,
                  child: Text(buttonLabel),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _QuestionCard extends StatelessWidget {
  final int questionNumber;
  final QuizQuestionData question;
  final int? selectedIndex;
  final ValueChanged<int> onSelect;

  const _QuestionCard({
    required this.questionNumber,
    required this.question,
    required this.selectedIndex,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        side: const BorderSide(color: AppTheme.borderLight),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0xFFE8F0FE),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    'Q$questionNumber',
                    style: const TextStyle(
                      color: AppTheme.primaryBlue,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  question.concept,
                  style: const TextStyle(
                    color: AppTheme.textSecondary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              question.prompt,
              style: const TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 18,
                fontWeight: FontWeight.w700,
                height: 1.35,
              ),
            ),
            const SizedBox(height: 12),
            ...question.options.asMap().entries.map(
                  (entry) => _QuizOptionTile(
                    label: entry.value,
                    selected: selectedIndex == entry.key,
                    onTap: () => onSelect(entry.key),
                  ),
                ),
          ],
        ),
      ),
    );
  }
}

class _QuizOptionTile extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _QuizOptionTile({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: InkWell(
        borderRadius: BorderRadius.circular(10),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: selected
                  ? AppTheme.primaryBlue
                  : AppTheme.borderLight,
            ),
            color: selected
                ? const Color(0xFFE8F0FE)
                : Colors.transparent,
          ),
          child: Row(
            children: [
              Icon(
                selected
                    ? Icons.radio_button_checked
                    : Icons.radio_button_off,
                color: selected
                    ? AppTheme.primaryBlue
                    : AppTheme.textSecondary,
                size: 20,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  label,
                  style: const TextStyle(
                    color: AppTheme.textPrimary,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ResultMetric extends StatelessWidget {
  final String label;
  final String value;
  final String caption;

  const _ResultMetric({
    required this.label,
    required this.value,
    required this.caption,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 220,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: AppTheme.textSecondary,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              color: AppTheme.textPrimary,
              fontSize: 28,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            caption,
            style: const TextStyle(
              color: AppTheme.textSecondary,
              height: 1.45,
            ),
          ),
        ],
      ),
    );
  }
}
