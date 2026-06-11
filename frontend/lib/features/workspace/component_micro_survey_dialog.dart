import 'package:flutter/material.dart';

import '../../core/backend_api_models.dart';

class ComponentMicroSurveyDialog extends StatefulWidget {
  final SurveyTemplateData template;
  final void Function(List<Map<String, dynamic>> responses) onSubmit;
  final VoidCallback onSkip;

  const ComponentMicroSurveyDialog({
    super.key,
    required this.template,
    required this.onSubmit,
    required this.onSkip,
  });

  @override
  State<ComponentMicroSurveyDialog> createState() =>
      _ComponentMicroSurveyDialogState();
}

class _ComponentMicroSurveyDialogState
    extends State<ComponentMicroSurveyDialog> {
  final Map<String, int?> _likertValues = {};
  final Map<String, TextEditingController> _textControllers = {};

  @override
  void initState() {
    super.initState();
    for (final item in widget.template.items) {
      if (item.questionType == 'text') {
        _textControllers[item.id] = TextEditingController();
      }
    }
  }

  @override
  void dispose() {
    for (final controller in _textControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  bool get _canSubmit {
    for (final item in widget.template.items) {
      if (!item.required) continue;
      if (item.questionType == 'likert_5') {
        if (_likertValues[item.id] == null) return false;
      } else if (item.questionType == 'text') {
        final text = _textControllers[item.id]?.text.trim() ?? '';
        if (text.isEmpty) return false;
      }
    }
    return true;
  }

  void _submit() {
    final responses = <Map<String, dynamic>>[];
    for (final item in widget.template.items) {
      if (item.questionType == 'likert_5') {
        final value = _likertValues[item.id];
        if (value != null) {
          responses.add({'item_id': item.id, 'likert_value': value});
        }
      } else if (item.questionType == 'text') {
        final text = _textControllers[item.id]?.text.trim() ?? '';
        if (text.isNotEmpty) {
          responses.add({'item_id': item.id, 'text_value': text});
        }
      }
    }
    widget.onSubmit(responses);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Dialog(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 520),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                widget.template.name,
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 16),
              ConstrainedBox(
                constraints: const BoxConstraints(maxHeight: 400),
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      for (final item in widget.template.items) ...[
                        _SurveyItemWidget(
                          item: item,
                          likertValue: _likertValues[item.id],
                          textController: _textControllers[item.id],
                          onLikertChanged: (value) => setState(() {
                            _likertValues[item.id] = value;
                          }),
                          onTextChanged: (_) => setState(() {}),
                        ),
                        const SizedBox(height: 12),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: widget.onSkip,
                    child: const Text('Skip'),
                  ),
                  const SizedBox(width: 8),
                  FilledButton(
                    onPressed: _canSubmit ? _submit : null,
                    style: FilledButton.styleFrom(
                      backgroundColor: colorScheme.primary,
                    ),
                    child: const Text('Submit'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SurveyItemWidget extends StatelessWidget {
  final SurveyTemplateItemData item;
  final int? likertValue;
  final TextEditingController? textController;
  final ValueChanged<int> onLikertChanged;
  final ValueChanged<String> onTextChanged;

  const _SurveyItemWidget({
    required this.item,
    required this.likertValue,
    required this.textController,
    required this.onLikertChanged,
    required this.onTextChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          item.questionText,
          style: theme.textTheme.bodyMedium,
        ),
        const SizedBox(height: 6),
        if (item.questionType == 'likert_5')
          _LikertRow(
            selectedValue: likertValue,
            onChanged: onLikertChanged,
          )
        else
          TextField(
            controller: textController,
            onChanged: onTextChanged,
            maxLines: 3,
            decoration: const InputDecoration(
              hintText: 'Your response...',
              border: OutlineInputBorder(),
              contentPadding:
                  EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              isDense: true,
            ),
          ),
      ],
    );
  }
}

class _LikertRow extends StatelessWidget {
  final int? selectedValue;
  final ValueChanged<int> onChanged;

  const _LikertRow({
    required this.selectedValue,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'Strongly\nDisagree',
          style: Theme.of(context).textTheme.labelSmall,
          textAlign: TextAlign.center,
        ),
        for (int i = 1; i <= 5; i++)
          GestureDetector(
            onTap: () => onChanged(i),
            child: Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: selectedValue == i
                    ? colorScheme.primary
                    : colorScheme.surfaceContainerHighest,
              ),
              alignment: Alignment.center,
              child: Text(
                '$i',
                style: TextStyle(
                  color: selectedValue == i
                      ? colorScheme.onPrimary
                      : colorScheme.onSurface,
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                ),
              ),
            ),
          ),
        Text(
          'Strongly\nAgree',
          style: Theme.of(context).textTheme.labelSmall,
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
