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
          const SizedBox(height: AppConstants.defaultPadding),
          
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

  Widget _buildCategory(BuildContext context, String title, List<Widget> lessons) {
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
