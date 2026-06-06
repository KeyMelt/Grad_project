import 'package:flutter/material.dart';

/// Active-recall prompt: before revealing the next step, the learner predicts
/// the agent's next action and the reward it earns, then reveals + is scored.
/// Retrieval practice is the strongest lever for retention, and the trace
/// already knows the answers — this widget just gates them behind a guess.
///
/// Self-contained: it owns its guess/reveal state and calls [onAdvance] when
/// the learner chooses to move on. The parent resets it per step via a key.
class TracePredictPrompt extends StatefulWidget {
  final List<String> actionOptions;
  final String actualActionLabel;
  final int actualRewardSign; // -1 lose, 0 none, +1 win
  final VoidCallback onAdvance;

  const TracePredictPrompt({
    super.key,
    required this.actionOptions,
    required this.actualActionLabel,
    required this.actualRewardSign,
    required this.onAdvance,
  });

  @override
  State<TracePredictPrompt> createState() => _TracePredictPromptState();
}

class _TracePredictPromptState extends State<TracePredictPrompt> {
  String? _guessAction;
  int? _guessReward;
  bool _revealed = false;

  static const _rewardOptions = [
    (sign: 1, label: 'Win (+)'),
    (sign: 0, label: 'None (0)'),
    (sign: -1, label: 'Lose (−)'),
  ];

  @override
  Widget build(BuildContext context) {
    final canReveal = _guessAction != null && _guessReward != null;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF11203A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF3B82F6)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.psychology_alt_rounded,
                  color: Color(0xFF93C5FD), size: 20),
              const SizedBox(width: 8),
              Text(
                _revealed ? 'Revealed' : 'Predict the next step',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w800,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _question('Which action will the agent take?'),
          const SizedBox(height: 6),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final option in widget.actionOptions)
                _choice(
                  label: option,
                  selected: _guessAction == option,
                  correct: _revealed ? option == widget.actualActionLabel : null,
                  onTap: _revealed
                      ? null
                      : () => setState(() => _guessAction = option),
                ),
            ],
          ),
          const SizedBox(height: 12),
          _question('What reward will it earn?'),
          const SizedBox(height: 6),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final option in _rewardOptions)
                _choice(
                  label: option.label,
                  selected: _guessReward == option.sign,
                  correct: _revealed
                      ? option.sign == widget.actualRewardSign
                      : null,
                  onTap: _revealed
                      ? null
                      : () => setState(() => _guessReward = option.sign),
                ),
            ],
          ),
          const SizedBox(height: 14),
          if (!_revealed)
            FilledButton.icon(
              onPressed:
                  canReveal ? () => setState(() => _revealed = true) : null,
              icon: const Icon(Icons.visibility_rounded),
              label: const Text('Reveal'),
            )
          else ...[
            _scoreLine(),
            const SizedBox(height: 10),
            FilledButton.icon(
              onPressed: widget.onAdvance,
              icon: const Icon(Icons.skip_next_rounded),
              label: const Text('Next step'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _scoreLine() {
    final actionOk = _guessAction == widget.actualActionLabel;
    final rewardOk = _guessReward == widget.actualRewardSign;
    final score = (actionOk ? 1 : 0) + (rewardOk ? 1 : 0);
    final color = score == 2
        ? const Color(0xFF34D399)
        : score == 1
            ? const Color(0xFFFBBF24)
            : const Color(0xFFF87171);
    return Text(
      score == 2
          ? 'Both right — you predicted the policy and the outcome.'
          : 'Scored $score / 2. Actual: ${widget.actualActionLabel}, '
              '${_rewardWord(widget.actualRewardSign)}.',
      style: TextStyle(color: color, fontWeight: FontWeight.w700, height: 1.35),
    );
  }

  String _rewardWord(int sign) =>
      sign > 0 ? 'win' : (sign < 0 ? 'lose' : 'no reward');

  Widget _question(String text) => Text(
        text,
        style: const TextStyle(
          color: Color(0xFFCBD5E1),
          fontSize: 13,
          fontWeight: FontWeight.w700,
        ),
      );

  Widget _choice({
    required String label,
    required bool selected,
    required bool? correct,
    required VoidCallback? onTap,
  }) {
    Color border = const Color(0xFF334155);
    Color fill = const Color(0xFF0B1220);
    if (correct == true) {
      border = const Color(0xFF34D399);
      fill = const Color(0xFF052E2B);
    } else if (correct == false && selected) {
      border = const Color(0xFFF87171);
      fill = const Color(0xFF3F1D20);
    } else if (selected) {
      border = const Color(0xFF60A5FA);
      fill = const Color(0xFF172554);
    }
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
        decoration: BoxDecoration(
          color: fill,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: border, width: selected ? 2 : 1),
        ),
        child: Text(
          label,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w700,
            fontSize: 13,
          ),
        ),
      ),
    );
  }
}
