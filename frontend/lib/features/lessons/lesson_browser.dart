import 'package:flutter/material.dart';

import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';
import 'lesson_card.dart';

class CourseOutlineLauncher extends StatelessWidget {
  final LessonDefinition selectedLesson;
  final bool canGoPrevious;
  final bool canGoNext;
  final VoidCallback onPrevious;
  final VoidCallback onNext;
  final VoidCallback onOpenOutline;

  const CourseOutlineLauncher({
    super.key,
    required this.selectedLesson,
    required this.canGoPrevious,
    required this.canGoNext,
    required this.onPrevious,
    required this.onNext,
    required this.onOpenOutline,
  });

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 420),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: AppTheme.surfaceWhite,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFCBD5E1)),
          boxShadow: const [
            BoxShadow(
              color: Color(0x120F172A),
              blurRadius: 20,
              offset: Offset(0, 8),
            ),
          ],
        ),
        child: Row(
          children: [
            _OutlineArrowButton(
              tooltip: 'Previous lesson',
              icon: Icons.arrow_back_rounded,
              onPressed: canGoPrevious ? onPrevious : null,
            ),
            Expanded(
              child: InkWell(
                borderRadius: BorderRadius.circular(12),
                onTap: onOpenOutline,
                child: Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                  child: Row(
                    children: [
                      const Icon(Icons.menu_rounded, size: 20),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Course Outline',
                              style: Theme.of(context)
                                  .textTheme
                                  .titleMedium
                                  ?.copyWith(fontWeight: FontWeight.w800),
                            ),
                            Text(
                              selectedLesson.title,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            _OutlineArrowButton(
              tooltip: 'Next lesson',
              icon: Icons.arrow_forward_rounded,
              onPressed: canGoNext ? onNext : null,
            ),
          ],
        ),
      ),
    );
  }
}

Future<void> showCourseOutlineDialog({
  required BuildContext context,
  required List<LessonSection> sections,
  required LessonDefinition selectedLesson,
  required ValueChanged<LessonDefinition> onLessonSelected,
}) {
  final mediaSize = MediaQuery.sizeOf(context);
  return showDialog<void>(
    context: context,
    barrierColor: const Color(0x990F172A),
    builder: (dialogContext) {
      return Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: const EdgeInsets.all(28),
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxWidth: mediaSize.width.clamp(0.0, 1180.0).toDouble(),
              maxHeight: mediaSize.height.clamp(0.0, 900.0).toDouble(),
            ),
            child: Material(
              color: AppTheme.surfaceWhite,
              borderRadius: BorderRadius.circular(28),
              clipBehavior: Clip.antiAlias,
              child: _CourseOutlineDialog(
                sections: sections,
                selectedLesson: selectedLesson,
                onLessonSelected: (lesson) {
                  Navigator.of(dialogContext).pop();
                  onLessonSelected(lesson);
                },
              ),
            ),
          ),
        ),
      );
    },
  );
}

class LessonBrowser extends StatelessWidget {
  final List<LessonSection> sections;
  final LessonDefinition selectedLesson;
  final ValueChanged<LessonDefinition> onLessonSelected;
  final VoidCallback onToggleVisibility;

  const LessonBrowser({
    super.key,
    required this.sections,
    required this.selectedLesson,
    required this.onLessonSelected,
    required this.onToggleVisibility,
  });

  @override
  Widget build(BuildContext context) {
    final sectionCount = sections.length;
    return Container(
      color: AppTheme.backgroundLight,
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Course Outline',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              IconButton(
                tooltip: 'Hide lesson sidebar',
                onPressed: onToggleVisibility,
                icon: const Icon(Icons.chevron_left_rounded),
              ),
            ],
          ),
          const SizedBox(height: AppConstants.smallPadding),
          _SelectedLessonBrief(lesson: selectedLesson),
          const SizedBox(height: AppConstants.smallPadding),
          Expanded(
            child: ListView.builder(
              itemCount: sectionCount,
              itemBuilder: (context, sectionIndex) {
                final section = sections[sectionIndex];
                return Padding(
                  padding: const EdgeInsets.only(
                    bottom: AppConstants.defaultPadding,
                  ),
                  child: _SectionLessonList(
                    title: section.title,
                    lessons: section.lessons,
                    selectedLessonId: selectedLesson.id,
                    onLessonSelected: onLessonSelected,
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _CourseOutlineDialog extends StatelessWidget {
  final List<LessonSection> sections;
  final LessonDefinition selectedLesson;
  final ValueChanged<LessonDefinition> onLessonSelected;

  const _CourseOutlineDialog({
    required this.sections,
    required this.selectedLesson,
    required this.onLessonSelected,
  });

  @override
  Widget build(BuildContext context) {
    final lessonCount = sections.fold<int>(
      0,
      (count, section) => count + section.lessons.length,
    );

    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 20, 24, 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      selectedLesson.title,
                      style:
                          Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.w800,
                              ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '$lessonCount lesson${lessonCount == 1 ? '' : 's'} available',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppTheme.textSecondary,
                          ),
                    ),
                  ],
                ),
              ),
              IconButton(
                tooltip: 'Close course outline',
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.close_rounded),
              ),
            ],
          ),
          const SizedBox(height: 18),
          Expanded(
            child: Scrollbar(
              thumbVisibility: true,
              child: ListView.builder(
                itemCount: sections.length,
                itemBuilder: (context, sectionIndex) {
                  final section = sections[sectionIndex];
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: _OutlineSectionCard(
                      section: section,
                      selectedLessonId: selectedLesson.id,
                      onLessonSelected: onLessonSelected,
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _OutlineArrowButton extends StatelessWidget {
  final String tooltip;
  final IconData icon;
  final VoidCallback? onPressed;

  const _OutlineArrowButton({
    required this.tooltip,
    required this.icon,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: tooltip,
      child: SizedBox(
        width: 48,
        height: 42,
        child: IconButton(
          visualDensity: VisualDensity.compact,
          onPressed: onPressed,
          icon: Icon(icon, size: 24),
          color: AppTheme.textPrimary,
          disabledColor: const Color(0xFFCBD5E1),
        ),
      ),
    );
  }
}

class _OutlineSectionCard extends StatelessWidget {
  final LessonSection section;
  final String selectedLessonId;
  final ValueChanged<LessonDefinition> onLessonSelected;

  const _OutlineSectionCard({
    required this.section,
    required this.selectedLessonId,
    required this.onLessonSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            section.title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 14),
          for (final lesson in section.lessons)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _OutlineLessonTile(
                lesson: lesson,
                isSelected: lesson.id == selectedLessonId,
                onTap: () => onLessonSelected(lesson),
              ),
            ),
        ],
      ),
    );
  }
}

class _OutlineLessonTile extends StatelessWidget {
  final LessonDefinition lesson;
  final bool isSelected;
  final VoidCallback onTap;

  const _OutlineLessonTile({
    required this.lesson,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(16),
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFE8F0FE) : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? AppTheme.primaryBlue : const Color(0xFFE2E8F0),
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 34,
              height: 34,
              decoration: BoxDecoration(
                color:
                    isSelected ? AppTheme.primaryBlue : const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(12),
              ),
              alignment: Alignment.center,
              child: Icon(
                lesson.hasVideo ? Icons.play_arrow_rounded : Icons.code_rounded,
                color: isSelected ? Colors.white : AppTheme.textPrimary,
                size: 18,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                lesson.title,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: AppTheme.textPrimary,
                    ),
              ),
            ),
            const SizedBox(width: 12),
            Icon(
              isSelected
                  ? Icons.check_circle_rounded
                  : Icons.arrow_outward_rounded,
              color: isSelected ? AppTheme.primaryBlue : AppTheme.textSecondary,
              size: 20,
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionLessonList extends StatelessWidget {
  final String title;
  final List<LessonDefinition> lessons;
  final String selectedLessonId;
  final ValueChanged<LessonDefinition> onLessonSelected;

  const _SectionLessonList({
    required this.title,
    required this.lessons,
    required this.selectedLessonId,
    required this.onLessonSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: AppTheme.textSecondary,
              ),
        ),
        const SizedBox(height: AppConstants.smallPadding),
        for (final lesson in lessons)
          Padding(
            padding: const EdgeInsets.only(bottom: AppConstants.smallPadding),
            child: LessonCard(
              title: lesson.title,
              description: lesson.description,
              isActive: lesson.id == selectedLessonId,
              hasVideo: lesson.hasVideo,
              backendEnabled: lesson.backendEnabled,
              onTap: () => onLessonSelected(lesson),
            ),
          ),
      ],
    );
  }
}

class _SelectedLessonBrief extends StatelessWidget {
  final LessonDefinition lesson;

  const _SelectedLessonBrief({
    required this.lesson,
  });

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            lesson.exercise.title,
            style: textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            lesson.exercise.overview,
            style: textTheme.bodySmall?.copyWith(
              color: AppTheme.textPrimary,
              height: 1.35,
            ),
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
          ),
          if (lesson.exercise.templateBlanks.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              'Exercise checklist',
              style: textTheme.bodyMedium?.copyWith(
                color: AppTheme.primaryBlue,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 8),
            ...lesson.exercise.templateBlanks.map(
              (blank) => _BriefBullet(
                icon: Icons.radio_button_unchecked_rounded,
                color: const Color(0xFFF59E0B),
                text: blank.prompt,
              ),
            ),
          ],
          if (lesson.exercise.successCriteria.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              'Success criteria',
              style: textTheme.bodyMedium?.copyWith(
                color: AppTheme.successGreen,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 8),
            ...lesson.exercise.successCriteria.take(3).map(
                  (criterion) => _BriefBullet(
                    icon: Icons.check_circle_outline_rounded,
                    color: AppTheme.successGreen,
                    text: criterion,
                  ),
                ),
          ],
        ],
      ),
    );
  }
}

class _BriefBullet extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String text;

  const _BriefBullet({
    required this.icon,
    required this.color,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 7),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 15),
          const SizedBox(width: 7),
          Expanded(
            child: Text(
              text,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textPrimary,
                    height: 1.3,
                  ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
