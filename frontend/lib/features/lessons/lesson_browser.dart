import 'package:flutter/material.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';
import 'lesson_card.dart';

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
            child: ListView(
              children: sections
                  .map(
                    (section) => Padding(
                      padding: const EdgeInsets.only(
                        bottom: AppConstants.defaultPadding,
                      ),
                      child: _buildCategory(
                        context,
                        section.title,
                        section.lessons
                            .map(
                              (lesson) => LessonCard(
                                title: lesson.title,
                                description: lesson.description,
                                isActive: lesson.id == selectedLesson.id,
                                hasVideo: lesson.hasVideo,
                                backendEnabled: lesson.backendEnabled,
                                onTap: () => onLessonSelected(lesson),
                              ),
                            )
                            .toList(),
                      ),
                    ),
                  )
                  .toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategory(
      BuildContext context, String title, List<Widget> lessons) {
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
        ...lessons.map((lesson) => Padding(
              padding: const EdgeInsets.only(bottom: AppConstants.smallPadding),
              child: lesson,
            )),
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
