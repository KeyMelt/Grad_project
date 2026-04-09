import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';

class FlashcardsSection extends StatelessWidget {
  final List<StudyFlashcard> flashcards;
  final VoidCallback onBackHome;

  const FlashcardsSection({
    super.key,
    required this.flashcards,
    required this.onBackHome,
  });

  @override
  Widget build(BuildContext context) {
    final grouped = <String, List<StudyFlashcard>>{};
    for (final card in flashcards) {
      grouped.putIfAbsent(card.category, () => <StudyFlashcard>[]).add(card);
    }
    final topics = grouped.keys.toList()..sort();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Flashcards',
                      style: TextStyle(
                        color: AppTheme.textPrimary,
                        fontSize: 28,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    SizedBox(height: 6),
                    Text(
                      'Tap any card to flip between question and answer.',
                      style: TextStyle(
                        color: AppTheme.textSecondary,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
              OutlinedButton.icon(
                onPressed: onBackHome,
                icon: const Icon(Icons.home_outlined),
                label: const Text('Back Home'),
              ),
            ],
          ),
          const SizedBox(height: 20),
          ...topics.map((topic) {
            final cards = grouped[topic]!;
            return Padding(
              padding: const EdgeInsets.only(bottom: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    topic,
                    style: const TextStyle(
                      color: AppTheme.textPrimary,
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 14,
                    runSpacing: 14,
                    children: cards
                        .map(
                          (card) => SizedBox(
                            width: 320,
                            height: 220,
                            child: _FlipFlashcard(card: card),
                          ),
                        )
                        .toList(growable: false),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }
}

class _FlipFlashcard extends StatefulWidget {
  final StudyFlashcard card;

  const _FlipFlashcard({
    required this.card,
  });

  @override
  State<_FlipFlashcard> createState() => _FlipFlashcardState();
}

class _FlipFlashcardState extends State<_FlipFlashcard> {
  bool _isFlipped = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        setState(() {
          _isFlipped = !_isFlipped;
        });
      },
      child: TweenAnimationBuilder<double>(
        tween: Tween<double>(begin: 0, end: _isFlipped ? math.pi : 0),
        duration: const Duration(milliseconds: 320),
        curve: Curves.easeInOut,
        builder: (context, angle, _) {
          final isBackFace = angle > (math.pi / 2);
          return Transform(
            alignment: Alignment.center,
            transform: Matrix4.identity()
              ..setEntry(3, 2, 0.001)
              ..rotateY(angle),
            child: isBackFace
                ? Transform(
                    alignment: Alignment.center,
                    transform: Matrix4.identity()..rotateY(math.pi),
                    child: _CardFace(
                      title: 'Answer',
                      body: widget.card.explanation,
                      footer: 'Tap to view question',
                    ),
                  )
                : _CardFace(
                    title: widget.card.category,
                    body: 'What is ${widget.card.term}?',
                    footer: 'Tap to reveal answer',
                  ),
          );
        },
      ),
    );
  }
}

class _CardFace extends StatelessWidget {
  final String title;
  final String body;
  final String footer;

  const _CardFace({
    required this.title,
    required this.body,
    required this.footer,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderLight),
        boxShadow: const [
          BoxShadow(
            color: Color(0x11000000),
            blurRadius: 12,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: AppTheme.primaryBlue,
              fontSize: 13,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: SingleChildScrollView(
              child: Text(
                body,
                style: const TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                  height: 1.35,
                ),
              ),
            ),
          ),
          const SizedBox(height: 10),
          Text(
            footer,
            style: const TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
