import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_markdown_latex/flutter_markdown_latex.dart';
import 'package:markdown/markdown.dart' as md;

import '../../core/lesson_models.dart';
import '../../core/theme.dart';

/// Supplemental lesson notes shown beside the concept video.
///
/// Renders [LessonConceptVideo.lectureNotes] as Markdown (with LaTeX math and
/// images) when present, and otherwise falls back to the structured
/// summary / highlights / takeaway layout.
class LessonNotesPanel extends StatelessWidget {
  final LessonDefinition lesson;

  const LessonNotesPanel({super.key, required this.lesson});

  @override
  Widget build(BuildContext context) {
    final video = lesson.conceptVideo;
    final hasMarkdown = video.lectureNotes.trim().isNotEmpty;
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppTheme.borderLight),
      ),
      padding: const EdgeInsets.all(18),
      child: hasMarkdown
          ? _LessonNotesMarkdown(notes: video.lectureNotes)
          : _LessonNotesFallback(video: video),
    );
  }
}

class _LessonNotesMarkdown extends StatelessWidget {
  final String notes;

  const _LessonNotesMarkdown({required this.notes});

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final styleSheet = MarkdownStyleSheet(
      p: text.bodyMedium?.copyWith(
        color: AppTheme.textPrimary,
        height: 1.55,
        fontSize: 14.5,
      ),
      h1: text.titleLarge?.copyWith(
        fontWeight: FontWeight.w800,
        color: AppTheme.textPrimary,
        height: 1.3,
      ),
      h2: text.titleMedium?.copyWith(
        fontWeight: FontWeight.w800,
        color: AppTheme.textPrimary,
        height: 1.3,
      ),
      h3: text.titleSmall?.copyWith(
        fontWeight: FontWeight.w700,
        color: AppTheme.textPrimary,
        height: 1.3,
      ),
      strong: const TextStyle(fontWeight: FontWeight.w700),
      em: const TextStyle(fontStyle: FontStyle.italic),
      code: const TextStyle(
        fontFamily: 'monospace',
        fontSize: 13,
        backgroundColor: Color(0xFFEFF3F8),
        color: AppTheme.textPrimary,
      ),
      codeblockDecoration: BoxDecoration(
        color: const Color(0xFFF1F4F8),
        border: Border.all(color: AppTheme.borderLight),
        borderRadius: BorderRadius.circular(8),
      ),
      codeblockPadding: const EdgeInsets.all(12),
      blockquote: text.bodyMedium?.copyWith(
        color: AppTheme.textSecondary,
        fontStyle: FontStyle.italic,
        height: 1.45,
      ),
      blockquoteDecoration: const BoxDecoration(
        border: Border(
          left: BorderSide(color: AppTheme.primaryBlue, width: 3),
        ),
      ),
      blockquotePadding: const EdgeInsets.only(left: 12, top: 4, bottom: 4),
      listBullet: text.bodyMedium?.copyWith(color: AppTheme.primaryBlue),
      tableHead: const TextStyle(fontWeight: FontWeight.w700),
      tableBorder: TableBorder.all(color: AppTheme.borderLight),
      tableCellsPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      a: const TextStyle(
        color: AppTheme.primaryBlue,
        decoration: TextDecoration.underline,
      ),
      horizontalRuleDecoration: const BoxDecoration(
        border: Border(
          top: BorderSide(color: AppTheme.borderLight, width: 1),
        ),
      ),
    );
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Lecture Notes',
            style: text.titleMedium?.copyWith(fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 12),
          MarkdownBody(
            data: notes,
            selectable: true,
            styleSheet: styleSheet,
            softLineBreak: true,
            extensionSet: md.ExtensionSet(
              <md.BlockSyntax>[
                LatexBlockSyntax(),
                ...md.ExtensionSet.gitHubFlavored.blockSyntaxes,
              ],
              <md.InlineSyntax>[
                LatexInlineSyntax(),
                ...md.ExtensionSet.gitHubFlavored.inlineSyntaxes,
              ],
            ),
            builders: <String, MarkdownElementBuilder>{
              'latex': LatexElementBuilder(
                textStyle: styleSheet.p,
              ),
            },
            sizedImageBuilder: (config) => _NotesImage(
              uri: config.uri,
              alt: config.alt ?? config.title ?? '',
            ),
          ),
        ],
      ),
    );
  }
}

class _LessonNotesFallback extends StatelessWidget {
  final LessonConceptVideo video;

  const _LessonNotesFallback({required this.video});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Lesson Notes',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 12),
          if (video.summary.isNotEmpty)
            Text(
              video.summary,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textPrimary,
                    height: 1.45,
                  ),
            ),
          if (video.highlights.isNotEmpty) ...[
            const SizedBox(height: 16),
            ...video.highlights.map(
              (highlight) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Padding(
                      padding: EdgeInsets.only(top: 6),
                      child: Icon(
                        Icons.circle,
                        size: 7,
                        color: AppTheme.primaryBlue,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        highlight,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: AppTheme.textPrimary,
                              height: 1.4,
                            ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
          if (video.takeawayLine.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              video.takeawayLine,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textPrimary,
                    fontWeight: FontWeight.w700,
                    height: 1.4,
                  ),
            ),
          ],
        ],
      ),
    );
  }
}

class _NotesImage extends StatelessWidget {
  final Uri uri;
  final String alt;

  const _NotesImage({required this.uri, required this.alt});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.network(
              uri.toString(),
              fit: BoxFit.contain,
              errorBuilder: (context, error, stackTrace) => Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFFDECEC),
                  border: Border.all(color: AppTheme.borderLight),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Image unavailable: ${uri.toString()}',
                  style: Theme.of(context)
                      .textTheme
                      .bodySmall
                      ?.copyWith(color: AppTheme.textSecondary),
                ),
              ),
            ),
          ),
          if (alt.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              alt,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textSecondary,
                    fontStyle: FontStyle.italic,
                  ),
            ),
          ],
        ],
      ),
    );
  }
}
