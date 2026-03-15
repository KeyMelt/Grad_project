import 'package:flutter/material.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';
import 'python_highlighting_controller.dart';

class CodeEditorTab extends StatefulWidget {
  final String lessonTitle;
  final String code;
  final ValueChanged<String> onChanged;

  const CodeEditorTab({
    super.key,
    required this.lessonTitle,
    required this.code,
    required this.onChanged,
  });

  @override
  State<CodeEditorTab> createState() => _CodeEditorTabState();
}

class _CodeEditorTabState extends State<CodeEditorTab> {
  late final PythonHighlightingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = PythonHighlightingController(text: widget.code);
  }

  @override
  void didUpdateWidget(covariant CodeEditorTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.code != widget.code && _controller.text != widget.code) {
      _controller.value = TextEditingValue(
        text: widget.code,
        selection: TextSelection.collapsed(offset: widget.code.length),
      );
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppTheme.backgroundLight,
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            widget.lessonTitle,
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            'The selected lesson now drives the starter function and backend validation target.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.surfaceWhite,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppTheme.borderLight),
              ),
              child: TextField(
                controller: _controller,
                expands: true,
                maxLines: null,
                minLines: null,
                onChanged: widget.onChanged,
                decoration: const InputDecoration(border: InputBorder.none),
                style: const TextStyle(
                  fontFamily: 'Courier',
                  fontSize: 14,
                  color: AppTheme.textPrimary,
                  height: 1.5,
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: AppTheme.primaryBlue.withOpacity(0.05),
              border: const Border(
                  left: BorderSide(color: AppTheme.primaryBlue, width: 4)),
            ),
            child: Text(
              'Switching lessons resets this editor to the matching backend function signature, so the UI no longer encourages unsupported algorithms.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textPrimary,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}
