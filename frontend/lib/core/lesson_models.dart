import 'package:flutter/foundation.dart';

@immutable
class LessonTheoryVerification {
  final String claim;
  final String sourceUrl;
  final String validationNote;
  final bool isInference;

  const LessonTheoryVerification({
    required this.claim,
    required this.sourceUrl,
    required this.validationNote,
    required this.isInference,
  });

  factory LessonTheoryVerification.fromJson(Map<String, dynamic> json) {
    return LessonTheoryVerification(
      claim: json['claim'] as String? ?? '',
      sourceUrl: json['source_url'] as String? ?? '',
      validationNote: json['validation_note'] as String? ?? '',
      isInference: json['is_inference'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'claim': claim,
      'source_url': sourceUrl,
      'validation_note': validationNote,
      'is_inference': isInference,
    };
  }
}

@immutable
class StudyFlashcard {
  final String term;
  final String category;
  final String explanation;

  const StudyFlashcard({
    required this.term,
    required this.category,
    required this.explanation,
  });

  factory StudyFlashcard.fromJson(Map<String, dynamic> json) {
    return StudyFlashcard(
      term: json['term'] as String? ?? '',
      category: json['category'] as String? ?? '',
      explanation: json['explanation'] as String? ?? '',
    );
  }
}

@immutable
class LessonConceptVideo {
  final String streamPath;
  final String captionPath;
  final String durationLabel;
  final String summary;
  final List<String> highlights;
  final String theoryEquation;
  final String workedExample;
  final String misconceptionToPrevent;
  final String takeawayLine;
  final String lectureNotes;
  final List<LessonTheoryVerification> theoryVerification;

  const LessonConceptVideo({
    required this.streamPath,
    required this.durationLabel,
    required this.summary,
    required this.highlights,
    this.captionPath = '',
    this.theoryEquation = '',
    this.workedExample = '',
    this.misconceptionToPrevent = '',
    this.takeawayLine = '',
    this.lectureNotes = '',
    this.theoryVerification = const [],
  });

  factory LessonConceptVideo.fromJson(Map<String, dynamic> json) {
    final theoryVerification = json['theory_verification'];
    return LessonConceptVideo(
      streamPath: json['stream_path'] as String? ?? '',
      captionPath: json['caption_path'] as String? ?? '',
      durationLabel: json['duration_label'] as String? ?? '',
      summary: json['summary'] as String? ?? '',
      highlights: (json['highlights'] as List<dynamic>? ?? const [])
          .map((value) => value.toString())
          .toList(growable: false),
      theoryEquation: json['theory_equation'] as String? ?? '',
      workedExample: json['worked_example'] as String? ?? '',
      misconceptionToPrevent: json['misconception_to_prevent'] as String? ?? '',
      takeawayLine: json['takeaway_line'] as String? ?? '',
      lectureNotes: json['lecture_notes'] as String? ?? '',
      theoryVerification: theoryVerification is List
          ? theoryVerification
              .whereType<Map<String, dynamic>>()
              .map(LessonTheoryVerification.fromJson)
              .toList(growable: false)
          : const [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'stream_path': streamPath,
      'caption_path': captionPath,
      'duration_label': durationLabel,
      'summary': summary,
      'highlights': highlights,
      'theory_equation': theoryEquation,
      'worked_example': workedExample,
      'misconception_to_prevent': misconceptionToPrevent,
      'takeaway_line': takeawayLine,
      'lecture_notes': lectureNotes,
      'theory_verification':
          theoryVerification.map((item) => item.toJson()).toList(),
    };
  }

  LessonConceptVideo copyWith({
    String? streamPath,
    String? captionPath,
    String? durationLabel,
    String? summary,
    List<String>? highlights,
    String? theoryEquation,
    String? workedExample,
    String? misconceptionToPrevent,
    String? takeawayLine,
    String? lectureNotes,
    List<LessonTheoryVerification>? theoryVerification,
  }) {
    return LessonConceptVideo(
      streamPath: streamPath ?? this.streamPath,
      captionPath: captionPath ?? this.captionPath,
      durationLabel: durationLabel ?? this.durationLabel,
      summary: summary ?? this.summary,
      highlights: highlights ?? this.highlights,
      theoryEquation: theoryEquation ?? this.theoryEquation,
      workedExample: workedExample ?? this.workedExample,
      misconceptionToPrevent:
          misconceptionToPrevent ?? this.misconceptionToPrevent,
      takeawayLine: takeawayLine ?? this.takeawayLine,
      lectureNotes: lectureNotes ?? this.lectureNotes,
      theoryVerification: theoryVerification ?? this.theoryVerification,
    );
  }

  String get effectiveStreamPath => streamPath;
}

@immutable
class LessonExerciseBrief {
  final String title;
  final String overview;
  final List<String> tasks;
  final List<LessonTemplateBlank> templateBlanks;
  final List<String> successCriteria;
  final String codeTip;

  const LessonExerciseBrief({
    required this.title,
    required this.overview,
    required this.tasks,
    this.templateBlanks = const [],
    required this.successCriteria,
    required this.codeTip,
  });

  factory LessonExerciseBrief.fromJson(Map<String, dynamic> json) {
    final blanks = json['template_blanks'];
    return LessonExerciseBrief(
      title: json['title'] as String? ?? '',
      overview: json['overview'] as String? ?? '',
      tasks: (json['tasks'] as List<dynamic>? ?? const [])
          .map((value) => value.toString())
          .toList(growable: false),
      templateBlanks: blanks is List
          ? blanks
              .whereType<Map<String, dynamic>>()
              .map(LessonTemplateBlank.fromJson)
              .toList(growable: false)
          : const [],
      successCriteria: (json['success_criteria'] as List<dynamic>? ?? const [])
          .map((value) => value.toString())
          .toList(growable: false),
      codeTip: json['code_tip'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'overview': overview,
      'tasks': tasks,
      'template_blanks': templateBlanks.map((blank) => blank.toJson()).toList(),
      'success_criteria': successCriteria,
      'code_tip': codeTip,
    };
  }

  LessonExerciseBrief copyWith({
    String? title,
    String? overview,
    List<String>? tasks,
    List<LessonTemplateBlank>? templateBlanks,
    List<String>? successCriteria,
    String? codeTip,
  }) {
    return LessonExerciseBrief(
      title: title ?? this.title,
      overview: overview ?? this.overview,
      tasks: tasks ?? this.tasks,
      templateBlanks: templateBlanks ?? this.templateBlanks,
      successCriteria: successCriteria ?? this.successCriteria,
      codeTip: codeTip ?? this.codeTip,
    );
  }
}

@immutable
class LessonTemplateBlank {
  final String blankId;
  final String kind;
  final String prompt;
  final String expectedConcept;
  final int approxLineAnchor;

  const LessonTemplateBlank({
    required this.blankId,
    required this.kind,
    required this.prompt,
    required this.expectedConcept,
    required this.approxLineAnchor,
  });

  factory LessonTemplateBlank.fromJson(Map<String, dynamic> json) {
    return LessonTemplateBlank(
      blankId: json['blank_id'] as String? ?? '',
      kind: json['kind'] as String? ?? '',
      prompt: json['prompt'] as String? ?? '',
      expectedConcept: json['expected_concept'] as String? ?? '',
      approxLineAnchor: (json['approx_line_anchor'] as num?)?.toInt() ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'blank_id': blankId,
      'kind': kind,
      'prompt': prompt,
      'expected_concept': expectedConcept,
      'approx_line_anchor': approxLineAnchor,
    };
  }
}

@immutable
class LessonDefinition {
  final String id;
  final String title;
  final String description;
  final String category;
  final String starterCode;
  final LessonConceptVideo conceptVideo;
  final LessonExerciseBrief exercise;
  final bool backendEnabled;

  const LessonDefinition({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.starterCode,
    required this.conceptVideo,
    required this.exercise,
    this.backendEnabled = true,
  });

  factory LessonDefinition.fromJson(Map<String, dynamic> json) {
    final conceptVideo = json['concept_video'];
    final exercise = json['exercise'];
    return LessonDefinition(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      category: json['category'] as String? ?? '',
      starterCode: json['starter_code'] as String? ?? '',
      conceptVideo: conceptVideo is Map<String, dynamic>
          ? LessonConceptVideo.fromJson(conceptVideo)
          : const LessonConceptVideo(
              streamPath: '',
              durationLabel: '',
              summary: '',
              highlights: [],
            ),
      exercise: exercise is Map<String, dynamic>
          ? LessonExerciseBrief.fromJson(exercise)
          : const LessonExerciseBrief(
              title: '',
              overview: '',
              tasks: [],
              successCriteria: [],
              codeTip: '',
            ),
      backendEnabled: json['backend_enabled'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'category': category,
      'starter_code': starterCode,
      'concept_video': conceptVideo.toJson(),
      'exercise': exercise.toJson(),
      'backend_enabled': backendEnabled,
    };
  }

  bool get hasVideo => conceptVideo.effectiveStreamPath.isNotEmpty;

  LessonDefinition copyWith({
    String? id,
    String? title,
    String? description,
    String? category,
    String? starterCode,
    LessonConceptVideo? conceptVideo,
    LessonExerciseBrief? exercise,
    bool? backendEnabled,
  }) {
    return LessonDefinition(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      category: category ?? this.category,
      starterCode: starterCode ?? this.starterCode,
      conceptVideo: conceptVideo ?? this.conceptVideo,
      exercise: exercise ?? this.exercise,
      backendEnabled: backendEnabled ?? this.backendEnabled,
    );
  }
}

@immutable
class LessonSection {
  final String title;
  final List<LessonDefinition> lessons;

  const LessonSection({
    required this.title,
    required this.lessons,
  });

  factory LessonSection.fromJson(Map<String, dynamic> json) {
    final lessons = json['lessons'];
    return LessonSection(
      title: json['title'] as String? ?? '',
      lessons: lessons is List
          ? lessons
              .whereType<Map<String, dynamic>>()
              .map(LessonDefinition.fromJson)
              .toList(growable: false)
          : const [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'lessons': lessons.map((lesson) => lesson.toJson()).toList(),
    };
  }

  LessonSection copyWith({
    String? title,
    List<LessonDefinition>? lessons,
  }) {
    return LessonSection(
      title: title ?? this.title,
      lessons: lessons ?? this.lessons,
    );
  }
}
