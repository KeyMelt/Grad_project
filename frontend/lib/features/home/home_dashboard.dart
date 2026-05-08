import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';

class HomeDashboard extends StatefulWidget {
  final LearnerProfile? learner;
  final LearnerProgress progress;
  final List<LessonSection> sections;
  final bool isSigningIn;
  final String message;
  final void Function(String displayName, String password) onSignIn;
  final ValueChanged<LessonDefinition> onOpenLesson;
  final VoidCallback onOpenQuiz;
  final VoidCallback onOpenFlashcards;
  final VoidCallback onSignOut;

  const HomeDashboard({
    super.key,
    required this.learner,
    required this.progress,
    required this.sections,
    required this.isSigningIn,
    required this.message,
    required this.onSignIn,
    required this.onOpenLesson,
    required this.onOpenQuiz,
    required this.onOpenFlashcards,
    required this.onSignOut,
  });

  @override
  State<HomeDashboard> createState() => _HomeDashboardState();
}

class _HomeDashboardState extends State<HomeDashboard> {
  late final TextEditingController _nameController;
  late final TextEditingController _passwordController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController();
    _passwordController = TextEditingController();
  }

  @override
  void didUpdateWidget(covariant HomeDashboard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.learner != null &&
        widget.learner?.displayName != oldWidget.learner?.displayName) {
      _nameController.text = widget.learner!.displayName;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final lessons = widget.sections
        .expand((section) => section.lessons)
        .toList(growable: false);
    final totalLessons = lessons.length;

    return ListenableBuilder(
      listenable: BackendConnectionManager(),
      builder: (context, _) => SingleChildScrollView(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildConnectionBadge(),
            const SizedBox(height: 12),
            _buildHeroCard(totalLessons),
            const SizedBox(height: AppConstants.defaultPadding),
            _buildProgressOverview(totalLessons),
            const SizedBox(height: AppConstants.defaultPadding),
            _buildSectionHeader(
              title: 'Lesson Summaries',
              subtitle: 'Pick a lesson to start coding.',
            ),
            const SizedBox(height: AppConstants.smallPadding),
            LayoutBuilder(
              builder: (context, constraints) {
                final cardWidth = constraints.maxWidth > 1300
                    ? (constraints.maxWidth - 24) / 2
                    : constraints.maxWidth;
                return Wrap(
                  spacing: AppConstants.defaultPadding,
                  runSpacing: AppConstants.defaultPadding,
                  children: lessons
                      .map(
                        (lesson) => SizedBox(
                          width: cardWidth,
                          child: _LessonSummaryCard(
                            lesson: lesson,
                            completed: widget.progress.completedLessonIds
                                .contains(lesson.id),
                            onOpen: () => widget.onOpenLesson(lesson),
                          ),
                        ),
                      )
                      .toList(growable: false),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConnectionBadge() {
    final manager = BackendConnectionManager();
    final isReady = manager.status == WorkspaceConnectionStatus.ready;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isReady
            ? AppTheme.successGreen.withValues(alpha: 0.08)
            : Colors.red.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isReady
              ? AppTheme.successGreen.withValues(alpha: 0.2)
              : Colors.red.withValues(alpha: 0.2),
        ),
      ),
      child: Row(
        children: [
          Icon(
            isReady ? Icons.cloud_done_rounded : Icons.cloud_off_rounded,
            color: isReady ? AppTheme.successGreen : Colors.red,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isReady
                      ? 'Connected to RL Backend'
                      : 'Disconnected from Backend',
                  style: TextStyle(
                    color: isReady ? AppTheme.successGreen : Colors.red,
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                  ),
                ),
                Text(
                  isReady ? manager.baseUrl : (manager.lastError ?? 'Offline'),
                  style: TextStyle(
                    color: isReady ? AppTheme.textSecondary : Colors.redAccent,
                    fontSize: 11,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          OutlinedButton.icon(
            onPressed: _showServerSettings,
            icon: const Icon(Icons.settings_ethernet_rounded, size: 16),
            label: const Text('Update IP'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              minimumSize: Size.zero,
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
          ),
        ],
      ),
    );
  }

  void _showServerSettings() {
    final manager = BackendConnectionManager();
    final controller = TextEditingController(text: manager.baseUrl);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Server Connection Settings'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Enter the backend URL or IP address of your machine for the iPad to connect.',
              style: TextStyle(fontSize: 13, height: 1.4),
            ),
            const SizedBox(height: 18),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'Backend URL / IP',
                hintText: 'http://192.168.1.5:8000',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.link_rounded),
              ),
              autofocus: true,
            ),
            const SizedBox(height: 8),
            const Text(
              'Example: http://192.168.x.x:8000',
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 11),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              manager.updateUrl(controller.text);
              Navigator.pop(context);
            },
            child: const Text('Save & Connect'),
          ),
        ],
      ),
    );
  }

  Widget _buildHeroCard(int totalLessons) {
    final learner = widget.learner;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        gradient: const LinearGradient(
          colors: [
            Color(0xFF132238),
            Color(0xFF1A73E8),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Wrap(
        spacing: 24,
        runSpacing: 24,
        alignment: WrapAlignment.spaceBetween,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 520),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.16),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: const Text(
                    'Student Home',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const SizedBox(height: 18),
                Text(
                  learner == null
                      ? 'Welcome to the RL learning studio'
                      : 'Welcome back, ${learner.displayName}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 32,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Track lessons, quizzes, and N-gain across $totalLessons lessons.',
                  style: const TextStyle(
                    color: Color(0xFFE6EEF9),
                    fontSize: 16,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 18),
                Text(
                  widget.message,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    height: 1.45,
                  ),
                ),
              ],
            ),
          ),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 360),
            child: Card(
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: learner == null
                    ? Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text(
                            'Student Sign In',
                            style: TextStyle(
                              color: AppTheme.textPrimary,
                              fontSize: 20,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Sign in to save your progress.',
                            style: TextStyle(
                              color: AppTheme.textSecondary,
                              height: 1.45,
                            ),
                          ),
                          const SizedBox(height: 18),
                          TextField(
                            controller: _nameController,
                            decoration: const InputDecoration(
                              labelText: 'Student name',
                              border: OutlineInputBorder(),
                            ),
                          ),
                          const SizedBox(height: 10),
                          TextField(
                            controller: _passwordController,
                            obscureText: true,
                            decoration: const InputDecoration(
                              labelText: 'Password',
                              border: OutlineInputBorder(),
                            ),
                            onSubmitted: (_) => widget.onSignIn(
                              _nameController.text,
                              _passwordController.text,
                            ),
                          ),
                          const SizedBox(height: 14),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton.icon(
                              onPressed: widget.isSigningIn
                                  ? null
                                  : () => widget.onSignIn(
                                        _nameController.text,
                                        _passwordController.text,
                                      ),
                              icon: widget.isSigningIn
                                  ? const SizedBox(
                                      width: 18,
                                      height: 18,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        color: Colors.white,
                                      ),
                                    )
                                  : const Icon(Icons.login),
                              label: Text(
                                widget.isSigningIn
                                    ? 'Signing In...'
                                    : 'Sign In',
                              ),
                            ),
                          ),
                        ],
                      )
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text(
                            'Current Learner',
                            style: TextStyle(
                              color: AppTheme.textSecondary,
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            learner.displayName,
                            style: const TextStyle(
                              color: AppTheme.textPrimary,
                              fontSize: 24,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 18),
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton.icon(
                              onPressed: widget.onOpenQuiz,
                              icon: const Icon(Icons.quiz_outlined),
                              label: const Text('Open Quizzes'),
                            ),
                          ),
                          const SizedBox(height: 10),
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton.icon(
                              onPressed: widget.onOpenFlashcards,
                              icon: const Icon(Icons.style_outlined),
                              label: const Text('Study Flashcards'),
                            ),
                          ),
                          const SizedBox(height: 10),
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton.icon(
                              onPressed: widget.onSignOut,
                              icon: const Icon(Icons.logout_rounded),
                              label: const Text('Sign Out'),
                            ),
                          ),
                        ],
                      ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressOverview(int totalLessons) {
    final progress = widget.progress;
    final cards = [
      _ProgressStat(
        label: 'Lessons completed',
        value: '${progress.lessonsCompleted} / $totalLessons',
        caption: 'Completed lesson runs',
      ),
      _ProgressStat(
        label: 'Successful runs',
        value: '${progress.successfulRuns}',
        caption: 'Runs completed',
      ),
      _ProgressStat(
        label: 'Pre-test',
        value: progress.pretestScore == null
            ? 'Pending'
            : '${progress.pretestScore!.toStringAsFixed(1)}%',
        caption: 'Baseline score',
      ),
      _ProgressStat(
        label: 'Post-test',
        value: progress.posttestScore == null
            ? 'Pending'
            : '${progress.posttestScore!.toStringAsFixed(1)}%',
        caption: 'After-practice score',
      ),
      _ProgressStat(
        label: 'N-gain',
        value: progress.nGain == null
            ? 'Pending'
            : progress.nGain!.toStringAsFixed(3),
        caption: 'Learning gain score',
      ),
      _ProgressStat(
        label: 'Submission attempts',
        value: '${progress.totalSubmissionAttempts}',
        caption: 'All code submissions',
      ),
      _ProgressStat(
        label: 'Passed checks',
        value: '${progress.passedSubmissionAttempts}',
        caption: 'Submissions that passed lesson checks',
      ),
      _ProgressStat(
        label: 'Validation issues',
        value: '${progress.validationFailures}',
        caption: 'Interface or syntax failures',
      ),
      _ProgressStat(
        label: 'Test failures',
        value: '${progress.testFailures}',
        caption: 'Code ran but lesson checks failed',
      ),
      _ProgressStat(
        label: 'Runtime failures',
        value: '${progress.runtimeFailures}',
        caption: 'Execution-time breakdowns',
      ),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(
          title: 'Progress Overview',
          subtitle: 'Your latest run and quiz stats.',
        ),
        const SizedBox(height: AppConstants.smallPadding),
        Wrap(
          spacing: AppConstants.defaultPadding,
          runSpacing: AppConstants.defaultPadding,
          children: cards
              .map(
                (stat) => SizedBox(
                  width: 250,
                  child: _ProgressStatCard(stat: stat),
                ),
              )
              .toList(growable: false),
        ),
      ],
    );
  }

  Widget _buildSectionHeader({
    required String title,
    required String subtitle,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            color: AppTheme.textPrimary,
            fontSize: 24,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          subtitle,
          style: const TextStyle(
            color: AppTheme.textSecondary,
            fontSize: 14,
          ),
        ),
      ],
    );
  }
}

class _ProgressStat {
  final String label;
  final String value;
  final String caption;

  const _ProgressStat({
    required this.label,
    required this.value,
    required this.caption,
  });
}

class _ProgressStatCard extends StatelessWidget {
  final _ProgressStat stat;

  const _ProgressStatCard({required this.stat});

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
            Text(
              stat.label,
              style: const TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 14),
            Text(
              stat.value,
              style: const TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 28,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              stat.caption,
              style: const TextStyle(
                color: AppTheme.textSecondary,
                height: 1.45,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LessonSummaryCard extends StatelessWidget {
  final LessonDefinition lesson;
  final bool completed;
  final VoidCallback onOpen;

  const _LessonSummaryCard({
    required this.lesson,
    required this.completed,
    required this.onOpen,
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
                    lesson.category,
                    style: const TextStyle(
                      color: AppTheme.primaryBlue,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const Spacer(),
                Icon(
                  completed ? Icons.check_circle : Icons.play_circle_outline,
                  color: completed
                      ? AppTheme.successGreen
                      : AppTheme.textSecondary,
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              lesson.title,
              style: const TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 20,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              lesson.description,
              style: const TextStyle(
                color: AppTheme.textSecondary,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 18),
            Align(
              alignment: Alignment.centerLeft,
              child: OutlinedButton.icon(
                onPressed: onOpen,
                icon: const Icon(Icons.arrow_forward),
                label: const Text('Open Lesson'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
