import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';

class HomeDashboard extends StatefulWidget {
  final LearnerProfile? learner;
  final LearnerProgress progress;
  final StudyBuddySummary studyBuddySummary;
  final bool isStudyBuddySummaryLoading;
  final List<LessonSection> sections;
  final bool isSigningIn;
  final bool canAccessAuthoring;
  final String message;
  final void Function(String displayName, String password) onSignIn;
  final void Function(String email, String password) onSignUp;
  final VoidCallback onSignInWithGoogle;
  final ValueChanged<LessonDefinition> onOpenLesson;
  final VoidCallback onOpenQuiz;
  final VoidCallback onOpenFlashcards;
  final VoidCallback onOpenAuthoring;
  final VoidCallback onSignOut;

  const HomeDashboard({
    super.key,
    required this.learner,
    required this.progress,
    required this.studyBuddySummary,
    required this.isStudyBuddySummaryLoading,
    required this.sections,
    required this.isSigningIn,
    required this.canAccessAuthoring,
    required this.message,
    required this.onSignIn,
    required this.onSignUp,
    required this.onSignInWithGoogle,
    required this.onOpenLesson,
    required this.onOpenQuiz,
    required this.onOpenFlashcards,
    required this.onOpenAuthoring,
    required this.onSignOut,
  });

  @override
  State<HomeDashboard> createState() => _HomeDashboardState();
}

class _HomeDashboardState extends State<HomeDashboard> {
  static const double _contentMaxWidth = 1320;
  static const double _sectionSpacing = AppConstants.defaultPadding;
  static const double _lessonCardMinWidth = 380;

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
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) {
          return;
        }
        _nameController.text = widget.learner!.displayName;
      });
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
      builder: (context, _) => LayoutBuilder(
        builder: (context, constraints) {
          final contentWidth =
              constraints.maxWidth.clamp(0.0, _contentMaxWidth).toDouble();
          final lessonColumns = _resolveGridColumnCount(
            availableWidth: contentWidth,
            minTileWidth: _lessonCardMinWidth,
          );

          return Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: _contentMaxWidth),
              child: CustomScrollView(
                slivers: [
                  SliverPadding(
                    padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                    sliver: SliverToBoxAdapter(
                      child: _buildConnectionBadge(),
                    ),
                  ),
                  SliverPadding(
                    padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
                    sliver: SliverToBoxAdapter(
                      child: _buildHeroCard(totalLessons),
                    ),
                  ),
                  if (widget.learner != null) ...[
                    SliverPadding(
                      padding: const EdgeInsets.fromLTRB(
                        20,
                        _sectionSpacing,
                        20,
                        0,
                      ),
                      sliver: SliverToBoxAdapter(
                        child: _buildSectionHeader(
                          title: 'Study Buddy',
                          subtitle:
                              'Review priority and concept confidence signals.',
                        ),
                      ),
                    ),
                    SliverPadding(
                      padding: const EdgeInsets.fromLTRB(20, 10, 20, 0),
                      sliver: SliverToBoxAdapter(
                        child: _buildStudyBuddySummary(),
                      ),
                    ),
                  ],
                  SliverPadding(
                    padding:
                        const EdgeInsets.fromLTRB(20, _sectionSpacing, 20, 0),
                    sliver: SliverToBoxAdapter(
                      child: _buildSectionHeader(
                        title: 'Lesson Summaries',
                        subtitle: 'Pick a lesson to start coding.',
                      ),
                    ),
                  ),
                  SliverPadding(
                    padding: const EdgeInsets.fromLTRB(20, 10, 20, 20),
                    sliver: SliverGrid(
                      delegate: SliverChildBuilderDelegate(
                        (context, index) {
                          final lesson = lessons[index];
                          return _LessonSummaryCard(
                            lesson: lesson,
                            completed: widget.progress.completedLessonIds
                                .contains(lesson.id),
                            onOpen: () => widget.onOpenLesson(lesson),
                          );
                        },
                        childCount: lessons.length,
                      ),
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: lessonColumns,
                        mainAxisSpacing: _sectionSpacing,
                        crossAxisSpacing: _sectionSpacing,
                        mainAxisExtent: 290,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
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

  void _showAuthDialog() {
    var mode = _AuthMode.signIn;
    _passwordController.clear();

    showDialog<void>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => AlertDialog(
          title: const Text('Account Access'),
          content: SizedBox(
            width: 380,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: _AuthModeButton(
                        label: 'Sign In',
                        selected: mode == _AuthMode.signIn,
                        onTap: () {
                          setModalState(() => mode = _AuthMode.signIn);
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _AuthModeButton(
                        label: 'Sign Up',
                        selected: mode == _AuthMode.signUp,
                        onTap: () {
                          setModalState(() => mode = _AuthMode.signUp);
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                TextField(
                  controller: _nameController,
                  keyboardType: TextInputType.emailAddress,
                  autofillHints: const [AutofillHints.email],
                  decoration: const InputDecoration(
                    labelText: 'Email address',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  autofillHints: mode == _AuthMode.signUp
                      ? const [AutofillHints.newPassword]
                      : const [AutofillHints.password],
                  decoration: InputDecoration(
                    labelText: mode == _AuthMode.signUp
                        ? 'Create password'
                        : 'Password',
                    border: const OutlineInputBorder(),
                  ),
                  onSubmitted: (_) {
                    Navigator.of(context).pop();
                    if (mode == _AuthMode.signUp) {
                      widget.onSignUp(
                        _nameController.text,
                        _passwordController.text,
                      );
                    } else {
                      widget.onSignIn(
                        _nameController.text,
                        _passwordController.text,
                      );
                    }
                  },
                ),
                const SizedBox(height: 12),
                Text(
                  mode == _AuthMode.signUp
                      ? 'Create a Firebase-backed learner account with email and password.'
                      : 'Sign in with your Firebase account, or use Google below.',
                  style: const TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 12,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            TextButton.icon(
              onPressed: () {
                Navigator.of(context).pop();
                widget.onSignInWithGoogle();
              },
              icon: const Icon(Icons.g_mobiledata_rounded),
              label: const Text('Google'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                if (mode == _AuthMode.signUp) {
                  widget.onSignUp(
                    _nameController.text,
                    _passwordController.text,
                  );
                } else {
                  widget.onSignIn(
                    _nameController.text,
                    _passwordController.text,
                  );
                }
              },
              child:
                  Text(mode == _AuthMode.signUp ? 'Create Account' : 'Sign In'),
            ),
          ],
        ),
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
                  widget.canAccessAuthoring
                      ? 'Manage learning flows and review guided practice across $totalLessons lessons.'
                      : 'Practice reinforcement learning lessons across $totalLessons guided coding activities.',
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
                            'Authentication',
                            style: TextStyle(
                              color: AppTheme.textPrimary,
                              fontSize: 20,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Open a dedicated sign-in or sign-up window for Firebase email/password or Google.',
                            style: TextStyle(
                              color: AppTheme.textSecondary,
                              height: 1.45,
                            ),
                          ),
                          const SizedBox(height: 18),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton.icon(
                              onPressed:
                                  widget.isSigningIn ? null : _showAuthDialog,
                              icon: widget.isSigningIn
                                  ? const SizedBox(
                                      width: 18,
                                      height: 18,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        color: Colors.white,
                                      ),
                                    )
                                  : const Icon(Icons.login_rounded),
                              label: Text(
                                widget.isSigningIn
                                    ? 'Authorizing...'
                                    : 'Open Sign In / Sign Up',
                              ),
                            ),
                          ),
                          const SizedBox(height: 10),
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton.icon(
                              onPressed: widget.isSigningIn
                                  ? null
                                  : widget.onSignInWithGoogle,
                              icon: const Icon(Icons.g_mobiledata_rounded),
                              label: const Text('Continue with Google'),
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
                          if (widget.canAccessAuthoring) ...[
                            const SizedBox(height: 10),
                            SizedBox(
                              width: double.infinity,
                              child: OutlinedButton.icon(
                                onPressed: widget.onOpenAuthoring,
                                icon: const Icon(
                                    Icons.admin_panel_settings_outlined),
                                label: const Text('Open Authoring & Progress'),
                              ),
                            ),
                          ],
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

  Widget _buildStudyBuddySummary() {
    final summary = widget.studyBuddySummary;
    final recommendation = summary.reviewRecommendation;
    final snapshots = summary.masterySnapshots.take(3).toList(growable: false);

    if (widget.isStudyBuddySummaryLoading && snapshots.isEmpty) {
      return const _StudyBuddyLoadingPanel();
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final wide = constraints.maxWidth >= 880;
        final reviewPanel = _ReviewRecommendationPanel(
          recommendation: recommendation,
          onOpen: recommendation == null
              ? null
              : () {
                  final lesson = _findLessonById(recommendation.lessonId);
                  if (lesson != null) {
                    widget.onOpenLesson(lesson);
                  }
                },
        );
        final masteryPanel = _MasterySummaryPanel(snapshots: snapshots);

        if (wide) {
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: reviewPanel),
              const SizedBox(width: _sectionSpacing),
              Expanded(child: masteryPanel),
            ],
          );
        }

        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            reviewPanel,
            const SizedBox(height: _sectionSpacing),
            masteryPanel,
          ],
        );
      },
    );
  }

  LessonDefinition? _findLessonById(String lessonId) {
    for (final section in widget.sections) {
      for (final lesson in section.lessons) {
        if (lesson.id == lessonId) {
          return lesson;
        }
      }
    }
    return null;
  }

  int _resolveGridColumnCount({
    required double availableWidth,
    required double minTileWidth,
  }) {
    final columns = (availableWidth / minTileWidth).floor();
    return columns.clamp(1, 4);
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

class _StudyBuddyLoadingPanel extends StatelessWidget {
  const _StudyBuddyLoadingPanel();

  @override
  Widget build(BuildContext context) {
    return const Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(
          Radius.circular(AppConstants.cardRadius),
        ),
        side: BorderSide(color: AppTheme.borderLight),
      ),
      child: Padding(
        padding: EdgeInsets.all(20),
        child: Row(
          children: [
            SizedBox(
              width: 18,
              height: 18,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            SizedBox(width: 12),
            Expanded(child: Text('Loading Study Buddy summary...')),
          ],
        ),
      ),
    );
  }
}

class _ReviewRecommendationPanel extends StatelessWidget {
  final StudyBuddyReviewRecommendation? recommendation;
  final VoidCallback? onOpen;

  const _ReviewRecommendationPanel({
    required this.recommendation,
    required this.onOpen,
  });

  @override
  Widget build(BuildContext context) {
    final recommendation = this.recommendation;
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
                const Icon(
                  Icons.event_repeat_rounded,
                  color: AppTheme.primaryBlue,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Recommended Review',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            if (recommendation == null)
              const Text(
                'No spaced review is due.',
                style: TextStyle(
                  color: AppTheme.textSecondary,
                  height: 1.45,
                ),
              )
            else ...[
              Text(
                _formatConceptLabel(recommendation.conceptId),
                style: const TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 20,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${recommendation.stalenessDays} days stale, '
                '${(recommendation.masteryScore * 100).round()}% mastery',
                style: const TextStyle(
                  color: AppTheme.textSecondary,
                  height: 1.45,
                ),
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: onOpen,
                icon: const Icon(Icons.arrow_forward_rounded),
                label: const Text('Open Lesson'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _MasterySummaryPanel extends StatelessWidget {
  final List<StudyBuddyMasterySnapshot> snapshots;

  const _MasterySummaryPanel({required this.snapshots});

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
                const Icon(
                  Icons.insights_rounded,
                  color: AppTheme.primaryBlue,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Concept Mastery',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            if (snapshots.isEmpty)
              const Text(
                'No concept evidence yet.',
                style: TextStyle(
                  color: AppTheme.textSecondary,
                  height: 1.45,
                ),
              )
            else
              ...snapshots.map(
                (snapshot) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: _MasteryRow(snapshot: snapshot),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _MasteryRow extends StatelessWidget {
  final StudyBuddyMasterySnapshot snapshot;

  const _MasteryRow({required this.snapshot});

  @override
  Widget build(BuildContext context) {
    final masteryPercent = (snapshot.masteryScore * 100).round();
    final supportPercent = (snapshot.supportNeedScore * 100).round();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                _formatConceptLabel(snapshot.conceptId),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
            ),
            if (snapshot.isLowConfidence)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: AppTheme.borderLight),
                ),
                child: const Text(
                  'Low evidence',
                  style: TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(999),
          child: LinearProgressIndicator(
            value: snapshot.masteryScore.clamp(0.0, 1.0),
            minHeight: 8,
            backgroundColor: const Color(0xFFE5E7EB),
            valueColor: AlwaysStoppedAnimation<Color>(
              snapshot.isLowConfidence
                  ? AppTheme.textSecondary
                  : AppTheme.successGreen,
            ),
          ),
        ),
        const SizedBox(height: 6),
        Text(
          '$masteryPercent% mastery, $supportPercent% support need',
          style: const TextStyle(
            color: AppTheme.textSecondary,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}

String _formatConceptLabel(String conceptId) {
  if (conceptId.isEmpty) {
    return 'Unknown concept';
  }
  return conceptId
      .split(RegExp(r'[_\s-]+'))
      .where((part) => part.isNotEmpty)
      .map((part) => '${part[0].toUpperCase()}${part.substring(1)}')
      .join(' ');
}

enum _AuthMode { signIn, signUp }

class _AuthModeButton extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _AuthModeButton({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(12),
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFFE8F0FE) : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: selected ? AppTheme.primaryBlue : AppTheme.borderLight,
          ),
        ),
        alignment: Alignment.center,
        child: Text(
          label,
          style: TextStyle(
            color: selected ? AppTheme.primaryBlue : AppTheme.textPrimary,
            fontWeight: FontWeight.w700,
          ),
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
            Expanded(
              child: Text(
                lesson.description,
                maxLines: 4,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: AppTheme.textSecondary,
                  height: 1.5,
                ),
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
