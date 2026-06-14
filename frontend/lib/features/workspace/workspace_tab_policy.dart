import '../../core/workbench_state.dart';

enum WorkspaceTabId {
  concept('concept'),
  code('code'),
  replay('replay');

  const WorkspaceTabId(this.value);

  final String value;

  static WorkspaceTabId fromValue(String value) {
    return switch (value) {
      'code' => WorkspaceTabId.code,
      'replay' => WorkspaceTabId.replay,
      _ => WorkspaceTabId.concept,
    };
  }
}

class WorkspaceTabPolicy {
  static const orderedTabs = <WorkspaceTabId>[
    WorkspaceTabId.concept,
    WorkspaceTabId.code,
    WorkspaceTabId.replay,
  ];

  static bool isAvailable({
    required LessonDefinition lesson,
    required WorkspaceTabId tab,
  }) {
    return switch (tab) {
      WorkspaceTabId.concept => true,
      WorkspaceTabId.code || WorkspaceTabId.replay => lesson.hasCodeExercise,
    };
  }

  static double labelOpacity({
    required LessonDefinition lesson,
    required WorkspaceTabId tab,
  }) {
    return isAvailable(lesson: lesson, tab: tab) ? 1.0 : 0.35;
  }

  static bool showsCourseOutline(WorkspaceTabId tab) {
    return tab != WorkspaceTabId.replay;
  }
}
