import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';

class QuizSection extends StatelessWidget {
  final LearnerProfile? learner;
  final LearnerProgress progress;
  final QuizCatalogData quizCatalog;
  final QuizSessionData? activeQuiz;
  final Map<String, int> quizAnswers;
  final QuizAttemptSummary? lastQuizSummary;
  final bool isLoading;
  final bool isPostStudySurveySubmitting;
  final bool postStudySurveyCompleted;
  final String postStudySurveyMessage;
  final String statusMessage;
  final ValueChanged<QuizPhase> onStartQuiz;
  final void Function({required String phaseId, String? phaseLabel})
      onStartQuizByPhaseId;
  final void Function(String questionId, int selectedIndex) onAnswerQuestion;
  final VoidCallback onSubmitQuiz;
  final VoidCallback onOpenPostStudySurvey;
  final void Function({
    required List<int> susResponses,
    required int tlxMentalDemand,
    required int tlxPhysicalDemand,
    required int tlxTemporalDemand,
    required int tlxPerformance,
    required int tlxEffort,
    required int tlxFrustration,
    String? feedbackHelpful,
    String? feedbackConfusing,
    String? feedbackImprovement,
  }) onSubmitPostStudySurvey;

  const QuizSection({
    super.key,
    required this.learner,
    required this.progress,
    required this.quizCatalog,
    required this.activeQuiz,
    required this.quizAnswers,
    required this.lastQuizSummary,
    required this.isLoading,
    required this.isPostStudySurveySubmitting,
    required this.postStudySurveyCompleted,
    required this.postStudySurveyMessage,
    required this.statusMessage,
    required this.onStartQuiz,
    required this.onStartQuizByPhaseId,
    required this.onAnswerQuestion,
    required this.onSubmitQuiz,
    required this.onOpenPostStudySurvey,
    required this.onSubmitPostStudySurvey,
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
            _buildLatestResultWithFollowup(lastQuizSummary!),
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
    final assessmentPhases = quizCatalog.assessmentPhases;
    if (assessmentPhases.isEmpty && quizCatalog.categoryQuizzes.isEmpty) {
      return const _QuizGateCard(
        title: 'Quiz Catalog',
        message: 'Quiz catalog is unavailable. Try again shortly.',
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: AppConstants.defaultPadding,
          runSpacing: AppConstants.defaultPadding,
          children: [
            for (final phase in assessmentPhases)
              _QuizActionCard(
                title: phase.label,
                description: phase.description,
                footer: _assessmentFooter(phase),
                buttonLabel:
                    isLoading ? 'Preparing...' : 'Start ${phase.label}',
                onPressed: isLoading || _isLocked(phase)
                    ? null
                    : () => onStartQuizByPhaseId(
                          phaseId: phase.id,
                          phaseLabel: phase.label,
                        ),
              ),
          ],
        ),
        if (quizCatalog.categoryQuizzes.isNotEmpty) ...[
          const SizedBox(height: AppConstants.defaultPadding),
          Text(
            quizCatalog.categorySectionLabel.isEmpty
                ? 'Category quizzes'
                : quizCatalog.categorySectionLabel,
            style: const TextStyle(
              color: AppTheme.textPrimary,
              fontSize: 22,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          if (quizCatalog.categorySectionDescription.isNotEmpty) ...[
            Text(
              quizCatalog.categorySectionDescription,
              style: const TextStyle(
                color: AppTheme.textSecondary,
                height: 1.45,
              ),
            ),
          ],
          const SizedBox(height: AppConstants.defaultPadding),
          Wrap(
            spacing: AppConstants.defaultPadding,
            runSpacing: AppConstants.defaultPadding,
            children: [
              for (final quiz in quizCatalog.categoryQuizzes)
                _QuizActionCard(
                  title: quiz.label,
                  description: quiz.description,
                  footer:
                      'Questions: ${quiz.questionCount} • Attempts: ${progress.quizAttempts[quiz.id] ?? 0}',
                  buttonLabel: isLoading ? 'Preparing...' : 'Start Quiz',
                  onPressed: isLoading
                      ? null
                      : () => onStartQuizByPhaseId(
                            phaseId: quiz.id,
                            phaseLabel: quiz.label,
                          ),
                ),
            ],
          ),
        ],
      ],
    );
  }

  bool _isLocked(QuizCatalogPhaseData phase) {
    return phase.requiresSuccessfulRun && progress.successfulRuns == 0;
  }

  String _assessmentFooter(QuizCatalogPhaseData phase) {
    if (_isLocked(phase)) {
      return 'Complete at least one lesson run to unlock this quiz.';
    }
    final latestScore = switch (phase.id) {
      'pretest' => progress.pretestScore,
      'posttest' => progress.posttestScore,
      _ => null,
    };
    final scoreText =
        latestScore == null ? '' : ' • Latest: ${_formatScore(latestScore)}';
    final questionText =
        phase.questionCount > 0 ? ' • Questions: ${phase.questionCount}' : '';
    return 'Attempts: ${progress.quizAttempts[phase.id] ?? 0}$scoreText$questionText';
  }

  String _quizTitle(QuizSessionData quiz) {
    if (quiz.phaseLabel.isNotEmpty) {
      return quiz.phaseLabel;
    }
    return quizPhaseLabel(quiz.phase);
  }

  bool _isPosttestSummary(QuizAttemptSummary summary) {
    return _catalogPhase(summary.phaseId)?.triggersPostStudySurvey ?? false;
  }

  String _summaryTitle(QuizAttemptSummary summary) {
    if (summary.phaseLabel.isNotEmpty) {
      return summary.phaseLabel;
    }
    return quizPhaseLabel(summary.phase);
  }

  bool _shouldOfferPostStudySurvey(QuizAttemptSummary summary) {
    return _isPosttestSummary(summary) && !postStudySurveyCompleted;
  }

  bool _shouldShowFeedbackRecorded(QuizAttemptSummary summary) {
    return _isPosttestSummary(summary) && postStudySurveyCompleted;
  }

  Widget _buildPostQuizFollowup(QuizAttemptSummary summary) {
    if (_shouldOfferPostStudySurvey(summary)) {
      return SessionFeedbackCallout(
        message: postStudySurveyMessage,
        onPressed: onOpenPostStudySurvey,
      );
    }
    if (_shouldShowFeedbackRecorded(summary)) {
      return _FeedbackRecordedCallout(message: postStudySurveyMessage);
    }
    return const SizedBox.shrink();
  }

  bool _hasPostQuizFollowup(QuizAttemptSummary summary) {
    return _shouldOfferPostStudySurvey(summary) ||
        _shouldShowFeedbackRecorded(summary);
  }

  Widget _buildLatestResultWithFollowup(QuizAttemptSummary summary) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildLatestResult(summary),
        if (_hasPostQuizFollowup(summary)) ...[
          const SizedBox(height: AppConstants.defaultPadding),
          _buildPostQuizFollowup(summary),
        ],
      ],
    );
  }

  Widget _buildQuestionProgress(QuizSessionData quiz) {
    return Text(
      '${quizAnswers.length}/${quiz.questions.length} answered',
      style: const TextStyle(
        color: AppTheme.textSecondary,
        fontWeight: FontWeight.w600,
      ),
    );
  }

  Widget _buildQuizIntro(QuizSessionData quiz) {
    final phase = _catalogPhase(quiz.phaseId);
    return Text(
      phase == null || phase.concepts.isEmpty
          ? 'Questions are randomized for every attempt.'
          : 'This quiz focuses on ${_quizTitle(quiz).toLowerCase()} questions from the editable catalog.',
      style: const TextStyle(
        color: AppTheme.textSecondary,
        height: 1.45,
      ),
    );
  }

  QuizCatalogPhaseData? _catalogPhase(String phaseId) {
    for (final phase in quizCatalog.assessmentPhases) {
      if (phase.id == phaseId) {
        return phase;
      }
    }
    for (final phase in quizCatalog.categoryQuizzes) {
      if (phase.id == phaseId) {
        return phase;
      }
    }
    return null;
  }

  Widget _buildSubmitButton() {
    return ElevatedButton.icon(
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
    );
  }

  Widget _buildResultMetricLabel(QuizAttemptSummary summary) {
    return _ResultMetric(
      label: _summaryTitle(summary),
      value: '${summary.score}/${summary.totalQuestions}',
      caption: 'Latest score',
    );
  }

  Widget _buildNGainMetric(QuizAttemptSummary summary) {
    return _ResultMetric(
      label: 'N-gain',
      value:
          summary.nGain == null ? 'Pending' : summary.nGain!.toStringAsFixed(3),
      caption: 'Shown after both quizzes',
    );
  }

  Widget _buildPercentageMetric(QuizAttemptSummary summary) {
    return _ResultMetric(
      label: 'Percentage',
      value: '${summary.percentage.toStringAsFixed(1)}%',
      caption: 'Score percent',
    );
  }

  Widget _buildQuizHeader(QuizSessionData quiz) {
    return Row(
      children: [
        Text(
          '${_quizTitle(quiz)} in progress',
          style: const TextStyle(
            color: AppTheme.textPrimary,
            fontSize: 24,
            fontWeight: FontWeight.w700,
          ),
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
            Expanded(child: _buildQuizHeader(quiz)),
            const Spacer(),
            _buildQuestionProgress(quiz),
          ],
        ),
        const SizedBox(height: 8),
        _buildQuizIntro(quiz),
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
          child: _buildSubmitButton(),
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
            _buildResultMetricLabel(summary),
            _buildPercentageMetric(summary),
            if (_catalogPhase(summary.phaseId)?.showsNGain ?? false)
              _buildNGainMetric(summary),
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

class SessionFeedbackCallout extends StatelessWidget {
  final String message;
  final VoidCallback onPressed;

  const SessionFeedbackCallout({
    super.key,
    required this.message,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Wrap(
      crossAxisAlignment: WrapCrossAlignment.center,
      spacing: 8,
      runSpacing: 4,
      children: [
        Text(
          message,
          style: const TextStyle(color: AppTheme.textSecondary),
        ),
        TextButton.icon(
          onPressed: onPressed,
          icon: const Icon(Icons.rate_review_outlined, size: 18),
          label: const Text('Share feedback'),
          style: TextButton.styleFrom(
            foregroundColor: AppTheme.textSecondary,
            visualDensity: VisualDensity.compact,
          ),
        ),
      ],
    );
  }
}

class _FeedbackRecordedCallout extends StatelessWidget {
  final String message;

  const _FeedbackRecordedCallout({required this.message});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Icon(
          Icons.check_circle_outline_rounded,
          size: 18,
          color: AppTheme.successGreen,
        ),
        const SizedBox(width: 8),
        Flexible(
          child: Text(
            message,
            style: const TextStyle(
              color: AppTheme.textSecondary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}

class PostStudySurveyCard extends StatefulWidget {
  final bool isSubmitting;
  final bool isComplete;
  final String message;
  final void Function({
    required List<int> susResponses,
    required int tlxMentalDemand,
    required int tlxPhysicalDemand,
    required int tlxTemporalDemand,
    required int tlxPerformance,
    required int tlxEffort,
    required int tlxFrustration,
    String? feedbackHelpful,
    String? feedbackConfusing,
    String? feedbackImprovement,
  }) onSubmit;

  const PostStudySurveyCard({
    super.key,
    required this.isSubmitting,
    required this.isComplete,
    required this.message,
    required this.onSubmit,
  });

  @override
  State<PostStudySurveyCard> createState() => _PostStudySurveyCardState();
}

class _PostStudySurveyCardState extends State<PostStudySurveyCard> {
  final List<int> _susResponses = List<int>.filled(10, 3);
  final _helpfulController = TextEditingController();
  final _confusingController = TextEditingController();
  final _improvementController = TextEditingController();
  int _step = 0;
  int _mentalDemand = 50;
  int _physicalDemand = 10;
  int _temporalDemand = 40;
  int _performance = 50;
  int _effort = 50;
  int _frustration = 30;

  static const _susPrompts = [
    'I would like to use this system frequently.',
    'I found the system unnecessarily complex.',
    'I thought the system was easy to use.',
    'I would need support to use this system.',
    'The functions in this system were well integrated.',
    'There was too much inconsistency in this system.',
    'Most people would learn to use this system quickly.',
    'I found the system cumbersome to use.',
    'I felt confident using this system.',
    'I needed to learn a lot before I could get going.',
  ];

  @override
  void dispose() {
    _helpfulController.dispose();
    _confusingController.dispose();
    _improvementController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final stepContent = switch (_step) {
      0 => _buildUsabilityStep(),
      1 => _buildWorkloadStep(),
      _ => _buildFeedbackStep(),
    };

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
            const Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.fact_check_outlined,
                  color: AppTheme.primaryBlue,
                ),
                SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Quick session feedback',
                        style: TextStyle(
                          color: AppTheme.textPrimary,
                          fontSize: 22,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      SizedBox(height: 6),
                      Text(
                        'Your feedback helps improve our services.',
                        style: TextStyle(
                          color: AppTheme.textSecondary,
                          height: 1.45,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              widget.message,
              style: TextStyle(
                color: widget.isComplete
                    ? AppTheme.successGreen
                    : AppTheme.textSecondary,
                fontWeight: FontWeight.w600,
              ),
            ),
            if (!widget.isComplete) ...[
              const SizedBox(height: 18),
              _buildProgressHeader(),
              const SizedBox(height: 18),
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 180),
                child: stepContent,
              ),
              const SizedBox(height: 18),
              _buildNavigation(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildProgressHeader() {
    const labels = ['Experience', 'Effort', 'Notes'];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        LinearProgressIndicator(
          value: (_step + 1) / labels.length,
          minHeight: 6,
          borderRadius: BorderRadius.circular(999),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (var index = 0; index < labels.length; index += 1)
              _SurveyStepPill(
                label: '${index + 1}. ${labels[index]}',
                selected: index == _step,
                complete: index < _step,
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildUsabilityStep() {
    return KeyedSubtree(
      key: const ValueKey('survey-usability-step'),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionTitle('Using the service'),
          const SizedBox(height: 8),
          const Text(
            'Choose 1 for strongly disagree and 5 for strongly agree.',
            style: TextStyle(color: AppTheme.textSecondary),
          ),
          const SizedBox(height: 12),
          ..._susPrompts.asMap().entries.map(
                (entry) => _buildSusQuestion(entry.key, entry.value),
              ),
        ],
      ),
    );
  }

  Widget _buildWorkloadStep() {
    return KeyedSubtree(
      key: const ValueKey('survey-workload-step'),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionTitle('Session effort'),
          const SizedBox(height: 8),
          const Text(
            'Rate how this session felt from 0 to 100.',
            style: TextStyle(color: AppTheme.textSecondary),
          ),
          const SizedBox(height: 12),
          _buildTlxSlider(
            label: 'Mental demand',
            value: _mentalDemand,
            onChanged: (value) => setState(() => _mentalDemand = value),
          ),
          _buildTlxSlider(
            label: 'Physical demand',
            value: _physicalDemand,
            onChanged: (value) => setState(() => _physicalDemand = value),
          ),
          _buildTlxSlider(
            label: 'Temporal demand',
            value: _temporalDemand,
            onChanged: (value) => setState(() => _temporalDemand = value),
          ),
          _buildTlxSlider(
            label: 'Performance',
            value: _performance,
            onChanged: (value) => setState(() => _performance = value),
          ),
          _buildTlxSlider(
            label: 'Effort',
            value: _effort,
            onChanged: (value) => setState(() => _effort = value),
          ),
          _buildTlxSlider(
            label: 'Frustration',
            value: _frustration,
            onChanged: (value) => setState(() => _frustration = value),
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackStep() {
    return KeyedSubtree(
      key: const ValueKey('survey-feedback-step'),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionTitle('Optional feedback'),
          const SizedBox(height: 8),
          const Text(
            'Add notes only where they help explain the ratings.',
            style: TextStyle(color: AppTheme.textSecondary),
          ),
          const SizedBox(height: 12),
          _buildFeedbackField(
            controller: _helpfulController,
            label: 'What helped most?',
          ),
          _buildFeedbackField(
            controller: _confusingController,
            label: 'What was confusing?',
          ),
          _buildFeedbackField(
            controller: _improvementController,
            label: 'What should improve?',
          ),
        ],
      ),
    );
  }

  Widget _buildNavigation() {
    final isLastStep = _step == 2;
    return Row(
      children: [
        TextButton.icon(
          onPressed: widget.isSubmitting || _step == 0
              ? null
              : () => setState(() => _step -= 1),
          icon: const Icon(Icons.arrow_back_rounded),
          label: const Text('Back'),
        ),
        const Spacer(),
        if (!isLastStep)
          ElevatedButton.icon(
            onPressed:
                widget.isSubmitting ? null : () => setState(() => _step += 1),
            icon: const Icon(Icons.arrow_forward_rounded),
            label: const Text('Next'),
          )
        else
          ElevatedButton.icon(
            onPressed: widget.isSubmitting ? null : _submit,
            icon: widget.isSubmitting
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Icon(Icons.send_outlined),
            label: Text(
              widget.isSubmitting ? 'Submitting...' : 'Submit feedback',
            ),
          ),
      ],
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        color: AppTheme.textPrimary,
        fontSize: 18,
        fontWeight: FontWeight.w700,
      ),
    );
  }

  Widget _buildSusQuestion(int index, String prompt) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        children: [
          Expanded(
            child: Text(
              '${index + 1}. $prompt',
              style: const TextStyle(
                color: AppTheme.textPrimary,
                height: 1.35,
              ),
            ),
          ),
          const SizedBox(width: 12),
          DropdownButton<int>(
            value: _susResponses[index],
            items: const [
              DropdownMenuItem(value: 1, child: Text('1')),
              DropdownMenuItem(value: 2, child: Text('2')),
              DropdownMenuItem(value: 3, child: Text('3')),
              DropdownMenuItem(value: 4, child: Text('4')),
              DropdownMenuItem(value: 5, child: Text('5')),
            ],
            onChanged: widget.isSubmitting
                ? null
                : (value) {
                    if (value != null) {
                      setState(() => _susResponses[index] = value);
                    }
                  },
          ),
        ],
      ),
    );
  }

  Widget _buildTlxSlider({
    required String label,
    required int value,
    required ValueChanged<int> onChanged,
  }) {
    return Row(
      children: [
        SizedBox(
          width: 160,
          child: Text(
            label,
            style: const TextStyle(
              color: AppTheme.textPrimary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        Expanded(
          child: Slider(
            value: value.toDouble(),
            min: 0,
            max: 100,
            divisions: 20,
            label: '$value',
            onChanged:
                widget.isSubmitting ? null : (next) => onChanged(next.round()),
          ),
        ),
        SizedBox(
          width: 36,
          child: Text(
            '$value',
            textAlign: TextAlign.right,
            style: const TextStyle(color: AppTheme.textSecondary),
          ),
        ),
      ],
    );
  }

  Widget _buildFeedbackField({
    required TextEditingController controller,
    required String label,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TextField(
        controller: controller,
        minLines: 1,
        maxLines: 2,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
      ),
    );
  }

  void _submit() {
    widget.onSubmit(
      susResponses: List<int>.unmodifiable(_susResponses),
      tlxMentalDemand: _mentalDemand,
      tlxPhysicalDemand: _physicalDemand,
      tlxTemporalDemand: _temporalDemand,
      tlxPerformance: _performance,
      tlxEffort: _effort,
      tlxFrustration: _frustration,
      feedbackHelpful: _helpfulController.text,
      feedbackConfusing: _confusingController.text,
      feedbackImprovement: _improvementController.text,
    );
  }
}

class _SurveyStepPill extends StatelessWidget {
  final String label;
  final bool selected;
  final bool complete;

  const _SurveyStepPill({
    required this.label,
    required this.selected,
    required this.complete,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: selected ? AppTheme.tealSurface : Colors.white,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: selected || complete
              ? AppTheme.primaryBlue
              : AppTheme.borderLight,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            complete
                ? Icons.check_circle_rounded
                : selected
                    ? Icons.radio_button_checked_rounded
                    : Icons.radio_button_unchecked_rounded,
            size: 16,
            color: selected || complete
                ? AppTheme.primaryBlue
                : AppTheme.textSecondary,
          ),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              color: selected ? AppTheme.primaryBlue : AppTheme.textSecondary,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
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
                    color: AppTheme.tealSurface,
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
              color: selected ? AppTheme.primaryBlue : AppTheme.borderLight,
            ),
            color: selected ? AppTheme.tealSurface : Colors.transparent,
          ),
          child: Row(
            children: [
              Icon(
                selected ? Icons.radio_button_checked : Icons.radio_button_off,
                color: selected ? AppTheme.primaryBlue : AppTheme.textSecondary,
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
