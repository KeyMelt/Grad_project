import 'package:flutter/material.dart';

import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';

class AdminConsole extends StatefulWidget {
  final List<LessonSection> sections;
  final String? selectedLessonId;
  final String message;
  final bool isExportingMetrics;
  final ValueChanged<String> onSelectLesson;
  final VoidCallback onCreateDraftLesson;
  final ValueChanged<String> onDeleteLesson;
  final VoidCallback onExportNGainMetrics;
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
  }) onSaveLesson;

  const AdminConsole({
    super.key,
    required this.sections,
    required this.selectedLessonId,
    required this.message,
    required this.isExportingMetrics,
    required this.onSelectLesson,
    required this.onCreateDraftLesson,
    required this.onDeleteLesson,
    required this.onExportNGainMetrics,
    required this.onSaveLesson,
  });

  @override
  State<AdminConsole> createState() => _AdminConsoleState();
}

enum _AdminSection { lessonStudio, evaluation }

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
  String? _loadedLessonId;
  _AdminSection _activeSection = _AdminSection.lessonStudio;

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
            child: _activeSection == _AdminSection.lessonStudio
                ? _buildLessonStudioLayout(context, lessons, selectedLesson)
                : _buildEvaluationSection(context),
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
              label: 'Evaluation',
              selected: _activeSection == _AdminSection.evaluation,
              icon: Icons.analytics_outlined,
              onTap: () {
                setState(() => _activeSection = _AdminSection.evaluation);
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

  Widget _buildEvaluationSection(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Evaluation',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            'Export N-gain metrics.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.textPrimary,
                  height: 1.45,
                ),
          ),
          const SizedBox(height: 18),
          SizedBox(
            width: 240,
            child: FilledButton.icon(
              onPressed: widget.isExportingMetrics
                  ? null
                  : widget.onExportNGainMetrics,
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
                widget.isExportingMetrics ? 'Exporting...' : 'Export N-gain',
              ),
            ),
          ),
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
                          ? const Color(0xFFE8F0FE)
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
              'Edit lesson text, video metadata, and starter code.',
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
                    title: const Text('Backend executable'),
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
                Expanded(
                    child: _field('Backend video path', _videoPathController)),
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
          color: selected ? const Color(0xFFE8F0FE) : AppTheme.backgroundLight,
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
