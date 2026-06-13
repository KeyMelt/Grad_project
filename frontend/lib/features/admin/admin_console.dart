import 'package:file_picker/file_picker.dart' show FilePicker, FileType;
import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';

class AdminConsole extends StatefulWidget {
  final List<LessonSection> sections;
  final String? selectedLessonId;
  final LearnerDashboard? progressDashboard;
  final List<StaffStudentSummary> students;
  final String? selectedStudentId;
  final String message;
  final bool isExportingMetrics;
  final bool isProgressLoading;
  final bool isAdmin;
  final ValueChanged<String> onSelectLesson;
  final ValueChanged<String> onSelectStudent;
  final VoidCallback onRefreshProgressDirectory;
  final VoidCallback onCreateDraftLesson;
  final ValueChanged<String> onDeleteLesson;
  final VoidCallback onExportNGainMetrics;
  final VoidCallback onExportLearningAnalytics;
  final VoidCallback onExportALEIComponents;
  final void Function({
    required String lessonId,
    required String title,
    required String category,
    required String description,
    required String conceptVideoStreamPath,
    required String conceptVideoDuration,
    required String conceptVideoSummary,
    required List<String> conceptHighlights,
    required String exerciseTitle,
    required String exerciseOverview,
    required List<String> exerciseTasks,
    required List<String> successCriteria,
    required String codeTip,
    required String starterCode,
    required bool backendEnabled,
    required bool hasCodeExercise,
  }) onSaveLesson;

  /// Called when the instructor picks a .md file to upload as lecture notes.
  final Future<void> Function({
    required String lessonId,
    required List<int> bytes,
    required String filename,
  }) onUploadLectureNotes;

  /// Called when the instructor removes uploaded lecture notes for a lesson.
  final Future<void> Function(String lessonId) onDeleteLectureNotes;

  const AdminConsole({
    super.key,
    required this.sections,
    required this.selectedLessonId,
    required this.progressDashboard,
    required this.students,
    required this.selectedStudentId,
    required this.message,
    required this.isExportingMetrics,
    required this.isProgressLoading,
    required this.isAdmin,
    required this.onSelectLesson,
    required this.onSelectStudent,
    required this.onRefreshProgressDirectory,
    required this.onCreateDraftLesson,
    required this.onDeleteLesson,
    required this.onExportNGainMetrics,
    required this.onExportLearningAnalytics,
    required this.onExportALEIComponents,
    required this.onSaveLesson,
    required this.onUploadLectureNotes,
    required this.onDeleteLectureNotes,
  });

  @override
  State<AdminConsole> createState() => _AdminConsoleState();
}

enum _AdminSection { lessonStudio, progressTracking }

class _AdminConsoleState extends State<AdminConsole> {
  late final TextEditingController _titleController;
  late final TextEditingController _categoryController;
  late final TextEditingController _descriptionController;
  late final TextEditingController _videoPathController;
  late final TextEditingController _videoDurationController;
  late final TextEditingController _videoSummaryController;
  late final TextEditingController _videoHighlightsController;
  late final TextEditingController _exerciseTitleController;
  late final TextEditingController _exerciseOverviewController;
  late final TextEditingController _exerciseTasksController;
  late final TextEditingController _successCriteriaController;
  late final TextEditingController _codeTipController;
  late final TextEditingController _starterCodeController;
  bool _backendEnabled = true;
  bool _hasCodeExercise = true;
  String? _loadedLessonId;
  _AdminSection _activeSection = _AdminSection.lessonStudio;
  bool _notesUploading = false;
  String? _notesStatusMessage;

  @override
  void initState() {
    super.initState();
    _titleController = TextEditingController();
    _categoryController = TextEditingController();
    _descriptionController = TextEditingController();
    _videoPathController = TextEditingController();
    _videoDurationController = TextEditingController();
    _videoSummaryController = TextEditingController();
    _videoHighlightsController = TextEditingController();
    _exerciseTitleController = TextEditingController();
    _exerciseOverviewController = TextEditingController();
    _exerciseTasksController = TextEditingController();
    _successCriteriaController = TextEditingController();
    _codeTipController = TextEditingController();
    _starterCodeController = TextEditingController();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _syncFromSelectedLesson();
  }

  @override
  void didUpdateWidget(covariant AdminConsole oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.selectedLessonId != widget.selectedLessonId ||
        oldWidget.sections != widget.sections) {
      _syncFromSelectedLesson();
    }
  }

  @override
  void dispose() {
    _titleController.dispose();
    _categoryController.dispose();
    _descriptionController.dispose();
    _videoPathController.dispose();
    _videoDurationController.dispose();
    _videoSummaryController.dispose();
    _videoHighlightsController.dispose();
    _exerciseTitleController.dispose();
    _exerciseOverviewController.dispose();
    _exerciseTasksController.dispose();
    _successCriteriaController.dispose();
    _codeTipController.dispose();
    _starterCodeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final activeSection = _activeSection;
    final lessons = widget.sections
        .expand((section) => section.lessons)
        .toList(growable: false);
    final selectedLesson = _findSelectedLesson();

    return Padding(
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildSectionSwitcher(context),
          const SizedBox(height: AppConstants.defaultPadding),
          Expanded(
            child: activeSection == _AdminSection.lessonStudio
                ? _buildLessonStudioLayout(context, lessons, selectedLesson)
                : _buildProgressTrackingSection(context),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionSwitcher(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: Row(
        children: [
          Expanded(
            child: _SectionButton(
              label: 'Lesson Studio',
              selected: _activeSection == _AdminSection.lessonStudio,
              icon: Icons.edit_note_rounded,
              onTap: () {
                setState(() => _activeSection = _AdminSection.lessonStudio);
              },
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _SectionButton(
              label: 'Progress',
              selected: _activeSection == _AdminSection.progressTracking,
              icon: Icons.insights_outlined,
              onTap: () {
                setState(() => _activeSection = _AdminSection.progressTracking);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLessonStudioLayout(
    BuildContext context,
    List<LessonDefinition> lessons,
    LessonDefinition? selectedLesson,
  ) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 800) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(
                height: 300,
                child: _buildLessonList(context, lessons),
              ),
              const SizedBox(height: AppConstants.defaultPadding),
              Expanded(
                child: selectedLesson == null
                    ? _emptyState(context)
                    : _buildEditor(context, selectedLesson),
              ),
            ],
          );
        }
        return Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            SizedBox(
              width: 300,
              child: _buildLessonList(context, lessons),
            ),
            const SizedBox(width: AppConstants.defaultPadding),
            Expanded(
              child: selectedLesson == null
                  ? _emptyState(context)
                  : _buildEditor(context, selectedLesson),
            ),
          ],
        );
      },
    );
  }

  Widget _buildProgressTrackingSection(BuildContext context) {
    final dashboard = widget.progressDashboard;
    final progress = dashboard?.progress ?? const LearnerProgress.empty();
    final stats = _buildProgressStats(progress);

    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      padding: const EdgeInsets.all(24),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final columns = (constraints.maxWidth / 280).floor().clamp(1, 4);
          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Progress Tracking',
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Review student quiz and coding progress from a privileged console instead of the learner home screen.',
                            style: Theme.of(context)
                                .textTheme
                                .bodyMedium
                                ?.copyWith(
                                  color: AppTheme.textPrimary,
                                  height: 1.45,
                                ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    OutlinedButton.icon(
                      onPressed: widget.onRefreshProgressDirectory,
                      icon: const Icon(Icons.refresh_rounded),
                      label: const Text('Refresh'),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                DropdownButtonFormField<String>(
                  initialValue: widget.students.any(
                    (student) => student.id == widget.selectedStudentId,
                  )
                      ? widget.selectedStudentId
                      : null,
                  decoration: const InputDecoration(
                    labelText: 'Learner',
                    border: OutlineInputBorder(),
                  ),
                  items: widget.students
                      .map(
                        (student) => DropdownMenuItem<String>(
                          value: student.id,
                          child: Text(student.displayName),
                        ),
                      )
                      .toList(growable: false),
                  onChanged: widget.isProgressLoading
                      ? null
                      : (value) {
                          if (value != null) {
                            widget.onSelectStudent(value);
                          }
                        },
                ),
                const SizedBox(height: 16),
                if (widget.isProgressLoading) const LinearProgressIndicator(),
                if (dashboard != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    dashboard.student.displayName,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                  const SizedBox(height: 12),
                  GridView.builder(
                    itemCount: stats.length,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: columns,
                      mainAxisSpacing: AppConstants.defaultPadding,
                      crossAxisSpacing: AppConstants.defaultPadding,
                      mainAxisExtent: 180,
                    ),
                    itemBuilder: (context, index) {
                      return _ProgressStatCard(stat: stats[index]);
                    },
                  ),
                ] else if (!widget.isProgressLoading) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Select a learner to view progress.',
                    style: TextStyle(color: AppTheme.textSecondary),
                  ),
                ],
                const SizedBox(height: 24),
                Text(
                  'Exports',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    SizedBox(
                      width: 220,
                      child: FilledButton.icon(
                        onPressed: widget.isAdmin && !widget.isExportingMetrics
                            ? widget.onExportNGainMetrics
                            : null,
                        icon: widget.isExportingMetrics
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Icon(Icons.table_view_outlined),
                        label: Text(
                          widget.isExportingMetrics
                              ? 'Exporting...'
                              : 'Export N-gain',
                        ),
                      ),
                    ),
                    SizedBox(
                      width: 260,
                      child: OutlinedButton.icon(
                        onPressed: widget.isAdmin && !widget.isExportingMetrics
                            ? widget.onExportLearningAnalytics
                            : null,
                        icon: const Icon(Icons.psychology_alt_outlined),
                        label: const Text('Export Learning Analytics'),
                      ),
                    ),
                    SizedBox(
                      width: 240,
                      child: OutlinedButton.icon(
                        onPressed: widget.isAdmin && !widget.isExportingMetrics
                            ? widget.onExportALEIComponents
                            : null,
                        icon: const Icon(Icons.science_outlined),
                        label: const Text('Export ALEI Metrics'),
                      ),
                    ),
                  ],
                ),
                if (!widget.isAdmin) ...[
                  const SizedBox(height: 8),
                  const Text(
                    'Analytics exports are admin-only.',
                    style: TextStyle(color: AppTheme.textSecondary),
                  ),
                ],
                const SizedBox(height: 18),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: AppTheme.borderLight),
                  ),
                  child: Text(
                    widget.message,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppTheme.textPrimary,
                          height: 1.45,
                        ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  List<_ProgressStat> _buildProgressStats(LearnerProgress progress) {
    return [
      _ProgressStat(
        label: 'Lessons completed',
        value: '${progress.lessonsCompleted}',
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
  }

  Widget _buildLessonList(
      BuildContext context, List<LessonDefinition> lessons) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    'Lesson Studio',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: widget.onCreateDraftLesson,
                  icon: const Icon(Icons.add),
                  label: const Text('New Draft'),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Text(
              widget.message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textPrimary,
                    height: 1.45,
                  ),
            ),
          ),
          const SizedBox(height: 14),
          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              itemBuilder: (context, index) {
                final lesson = lessons[index];
                final isSelected = lesson.id == widget.selectedLessonId;
                return InkWell(
                  borderRadius: BorderRadius.circular(16),
                  onTap: () => widget.onSelectLesson(lesson.id),
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? AppTheme.tealSurface
                          : AppTheme.backgroundLight,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isSelected
                            ? AppTheme.primaryBlue
                            : AppTheme.borderLight,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          lesson.title,
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 6),
                        Text(
                          lesson.category,
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      ],
                    ),
                  ),
                );
              },
              separatorBuilder: (_, __) =>
                  const SizedBox(height: AppConstants.smallPadding),
              itemCount: lessons.length,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEditor(BuildContext context, LessonDefinition lesson) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Author Lesson Content',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Edit lesson text, video metadata, and starter code. Drafts are saved locally.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textPrimary,
                    height: 1.45,
                  ),
            ),
            const SizedBox(height: 20),
            _field('Lesson title', _titleController),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(child: _field('Category', _categoryController)),
                const SizedBox(width: 14),
                Expanded(
                  child: SwitchListTile(
                    title: const Text('Runnable exercise'),
                    subtitle: const Text('Disable for content-only drafts'),
                    value: _backendEnabled,
                    onChanged: (value) =>
                        setState(() => _backendEnabled = value),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                      side: const BorderSide(color: AppTheme.borderLight),
                    ),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: SwitchListTile(
                    title: const Text('Has coding exercise'),
                    subtitle: const Text('Disable to grey out Code & Replay tabs'),
                    value: _hasCodeExercise,
                    onChanged: (value) =>
                        setState(() => _hasCodeExercise = value),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                      side: const BorderSide(color: AppTheme.borderLight),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            _field(
              'Lesson summary',
              _descriptionController,
              minLines: 3,
              maxLines: 4,
            ),
            const SizedBox(height: 20),
            Text(
              'Concept Video',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _field('Video path', _videoPathController)),
                const SizedBox(width: 14),
                SizedBox(
                  width: 160,
                  child: _field('Duration', _videoDurationController),
                ),
              ],
            ),
            const SizedBox(height: 14),
            _field(
              'Video summary',
              _videoSummaryController,
              minLines: 3,
              maxLines: 4,
            ),
            const SizedBox(height: 14),
            _field(
              'Video highlights (one per line)',
              _videoHighlightsController,
              minLines: 4,
              maxLines: 6,
            ),
            const SizedBox(height: 20),
            Text(
              'Coding Exercise',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            _field('Exercise title', _exerciseTitleController),
            const SizedBox(height: 14),
            _field(
              'Exercise overview',
              _exerciseOverviewController,
              minLines: 4,
              maxLines: 6,
            ),
            const SizedBox(height: 14),
            _field(
              'Instructions (one per line)',
              _exerciseTasksController,
              minLines: 5,
              maxLines: 8,
            ),
            const SizedBox(height: 14),
            _field(
              'Success criteria (one per line)',
              _successCriteriaController,
              minLines: 4,
              maxLines: 7,
            ),
            const SizedBox(height: 14),
            _field(
              'Code configuration guidance',
              _codeTipController,
              minLines: 3,
              maxLines: 4,
            ),
            const SizedBox(height: 14),
            _field(
              'Starter code',
              _starterCodeController,
              minLines: 12,
              maxLines: 18,
              monospace: true,
            ),
            const SizedBox(height: 24),
            _buildLectureNotesSection(context, lesson),
            const SizedBox(height: 24),
            Row(
              children: [
                OutlinedButton.icon(
                  onPressed: () => _confirmDelete(context, lesson),
                  icon: const Icon(Icons.delete_outline),
                  label: const Text('Delete lesson'),
                ),
                const Spacer(),
                ElevatedButton.icon(
                  onPressed: () => widget.onSaveLesson(
                    lessonId: lesson.id,
                    title: _titleController.text,
                    category: _categoryController.text,
                    description: _descriptionController.text,
                    conceptVideoStreamPath: _videoPathController.text,
                    conceptVideoDuration: _videoDurationController.text,
                    conceptVideoSummary: _videoSummaryController.text,
                    conceptHighlights:
                        _linesFromController(_videoHighlightsController),
                    exerciseTitle: _exerciseTitleController.text,
                    exerciseOverview: _exerciseOverviewController.text,
                    exerciseTasks:
                        _linesFromController(_exerciseTasksController),
                    successCriteria:
                        _linesFromController(_successCriteriaController),
                    codeTip: _codeTipController.text,
                    starterCode: _starterCodeController.text,
                    backendEnabled: _backendEnabled,
                    hasCodeExercise: _hasCodeExercise,
                  ),
                  icon: const Icon(Icons.save_outlined),
                  label: const Text('Save lesson content'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLectureNotesSection(
      BuildContext context, LessonDefinition lesson) {
    final hasNotes = lesson.conceptVideo.lectureNotes.trim().isNotEmpty;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.backgroundLight,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Lecture Notes',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w800,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Upload a Markdown (.md) file to accompany this lesson\'s concept video. '
                      'Admin-uploaded notes override built-in generated notes.',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppTheme.textSecondary,
                            height: 1.4,
                          ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Chip(
                label: Text(hasNotes ? 'Notes present' : 'No notes'),
                avatar: Icon(
                  hasNotes
                      ? Icons.check_circle_outline
                      : Icons.radio_button_unchecked,
                  size: 16,
                  color: hasNotes
                      ? const Color(0xFF16A34A)
                      : AppTheme.textSecondary,
                ),
                backgroundColor: hasNotes
                    ? const Color(0xFFDCFCE7)
                    : const Color(0xFFF1F5F9),
                side: BorderSide(
                  color: hasNotes
                      ? const Color(0xFF86EFAC)
                      : AppTheme.borderLight,
                ),
                labelStyle: TextStyle(
                  color: hasNotes
                      ? const Color(0xFF166534)
                      : AppTheme.textSecondary,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          if (_notesStatusMessage != null) ...[
            Text(
              _notesStatusMessage!,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
            ),
            const SizedBox(height: 10),
          ],
          Row(
            children: [
              FilledButton.icon(
                onPressed: _notesUploading
                    ? null
                    : () => _pickAndUploadNotes(lesson.id),
                icon: _notesUploading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.upload_file_outlined),
                label:
                    Text(_notesUploading ? 'Uploading…' : 'Upload notes (.md)'),
              ),
              if (hasNotes) ...[
                const SizedBox(width: 10),
                OutlinedButton.icon(
                  onPressed: _notesUploading
                      ? null
                      : () => _confirmDeleteNotes(context, lesson.id),
                  icon: const Icon(Icons.delete_outline, size: 18),
                  label: const Text('Remove notes'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.red.shade700,
                    side: BorderSide(color: Colors.red.shade200),
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _pickAndUploadNotes(String lessonId) async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: const ['md'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) return;
    final file = result.files.first;
    final bytes = file.bytes;
    if (bytes == null) return;
    setState(() {
      _notesUploading = true;
      _notesStatusMessage = null;
    });
    try {
      await widget.onUploadLectureNotes(
        lessonId: lessonId,
        bytes: bytes,
        filename: file.name,
      );
      setState(() => _notesStatusMessage = 'Notes uploaded: ${file.name}');
    } catch (e) {
      setState(() => _notesStatusMessage = 'Upload failed: $e');
    } finally {
      setState(() => _notesUploading = false);
    }
  }

  Future<void> _confirmDeleteNotes(
      BuildContext context, String lessonId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Remove lecture notes?'),
        content: const Text(
          'This removes the uploaded notes file. Built-in generated notes '
          'will be shown instead if they exist.',
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.of(ctx).pop(false),
              child: const Text('Cancel')),
          FilledButton(
              onPressed: () => Navigator.of(ctx).pop(true),
              child: const Text('Remove')),
        ],
      ),
    );
    if (confirmed != true) return;
    setState(() {
      _notesUploading = true;
      _notesStatusMessage = null;
    });
    try {
      await widget.onDeleteLectureNotes(lessonId);
      setState(() => _notesStatusMessage = 'Lecture notes removed.');
    } catch (e) {
      setState(() => _notesStatusMessage = 'Remove failed: $e');
    } finally {
      setState(() => _notesUploading = false);
    }
  }

  Widget _emptyState(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: Center(
        child: Text(
          'Choose a lesson to start editing.',
          style: Theme.of(context).textTheme.titleMedium,
        ),
      ),
    );
  }

  Widget _field(
    String label,
    TextEditingController controller, {
    int minLines = 1,
    int maxLines = 1,
    bool monospace = false,
  }) {
    return TextField(
      controller: controller,
      minLines: minLines,
      maxLines: maxLines,
      style: monospace
          ? const TextStyle(fontFamily: 'Courier', fontSize: 13, height: 1.45)
          : null,
      decoration: InputDecoration(
        labelText: label,
        alignLabelWithHint: maxLines > 1,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
    );
  }

  void _syncFromSelectedLesson() {
    final lesson = _findSelectedLesson();
    if (lesson == null || _loadedLessonId == lesson.id) {
      return;
    }

    _loadedLessonId = lesson.id;
    _titleController.text = lesson.title;
    _categoryController.text = lesson.category;
    _descriptionController.text = lesson.description;
    _videoPathController.text = lesson.conceptVideo.effectiveStreamPath;
    _videoDurationController.text = lesson.conceptVideo.durationLabel;
    _videoSummaryController.text = lesson.conceptVideo.summary;
    _videoHighlightsController.text = lesson.conceptVideo.highlights.join('\n');
    _exerciseTitleController.text = lesson.exercise.title;
    _exerciseOverviewController.text = lesson.exercise.overview;
    _exerciseTasksController.text = lesson.exercise.tasks.join('\n');
    _successCriteriaController.text =
        lesson.exercise.successCriteria.join('\n');
    _codeTipController.text = lesson.exercise.codeTip;
    _starterCodeController.text = lesson.starterCode;
    _backendEnabled = lesson.backendEnabled;
    _hasCodeExercise = lesson.hasCodeExercise;
    if (mounted) {
      setState(() {});
    }
  }

  LessonDefinition? _findSelectedLesson() {
    final selectedId = widget.selectedLessonId;
    for (final section in widget.sections) {
      for (final lesson in section.lessons) {
        if (selectedId == null || lesson.id == selectedId) {
          return lesson;
        }
      }
    }
    return null;
  }

  List<String> _linesFromController(TextEditingController controller) {
    return controller.text
        .split('\n')
        .map((line) => line.trim())
        .where((line) => line.isNotEmpty)
        .toList(growable: false);
  }

  Future<void> _confirmDelete(
    BuildContext context,
    LessonDefinition lesson,
  ) async {
    final shouldDelete = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Delete lesson?'),
          content: Text(
            'Delete "${lesson.title}" from this session?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(dialogContext).pop(true),
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );

    if (shouldDelete == true) {
      widget.onDeleteLesson(lesson.id);
    }
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

  const _ProgressStatCard({
    required this.stat,
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

class _SectionButton extends StatelessWidget {
  final String label;
  final bool selected;
  final IconData icon;
  final VoidCallback onTap;

  const _SectionButton({
    required this.label,
    required this.selected,
    required this.icon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: selected ? AppTheme.tealSurface : AppTheme.backgroundLight,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: selected ? AppTheme.primaryBlue : AppTheme.borderLight,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 18,
              color: selected ? AppTheme.primaryBlue : AppTheme.textSecondary,
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color:
                        selected ? AppTheme.primaryBlue : AppTheme.textPrimary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
