// ignore_for_file: depend_on_referenced_packages

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/lesson_models.dart';
import 'package:rl_ide/features/workspace/lesson_notes_panel.dart';

/// Renders every authored `*_lecture_notes.md` file through [LessonNotesPanel]
/// to guard against crashes / overflows on real LaTeX, tables, and code blocks.
void main() {
  final notesDir = Directory('../manim_service/concept_videos');
  final files = notesDir.existsSync()
      ? (notesDir
          .listSync()
          .whereType<File>()
          .where((f) => f.path.endsWith('_lecture_notes.md'))
          .toList()
        ..sort((a, b) => a.path.compareTo(b.path)))
      : <File>[];

  test('authored lecture notes exist', () {
    expect(files, isNotEmpty,
        reason: 'expected *_lecture_notes.md files under $notesDir');
  });

  for (final file in files) {
    final name = file.uri.pathSegments.last;
    testWidgets('renders $name without exceptions', (tester) async {
      final notes = file.readAsStringSync();
      final lesson = LessonDefinition(
        id: name.replaceAll('_lecture_notes.md', ''),
        title: 'Lesson',
        description: '',
        category: 'Dynamic Programming',
        starterCode: '',
        conceptVideo: LessonConceptVideo(
          streamPath: '',
          durationLabel: '',
          summary: '',
          highlights: const [],
          lectureNotes: notes,
        ),
        exercise: const LessonExerciseBrief(
          title: '',
          overview: '',
          tasks: [],
          successCriteria: [],
          codeTip: '',
        ),
      );

      addTearDown(() async {
        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pump();
      });

      // Tall content lives in a scroll view; give it a roomy viewport so the
      // smoke test exercises layout for the full document, not just the top.
      tester.view.physicalSize = const Size(420, 4000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: LessonNotesPanel(lesson: lesson),
          ),
        ),
      );
      await tester.pump();

      expect(find.text('Lecture Notes'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  }
}
