import 'package:flutter/material.dart';

class PythonHighlightingController extends TextEditingController {
  PythonHighlightingController({String? text}) : super(text: text);

  static final RegExp _tokenPattern = RegExp(
    "(#.*\$)|('[^'\\n]*'|\"[^\"\\n]*\")|\\b(def|return|for|while|if|else|elif|in|pass|continue|break|True|False|None|and|or|not|class|import|from|as)\\b|\\b\\d+(\\.\\d+)?\\b",
    multiLine: true,
  );

  static const Set<String> _keywords = {
    'def',
    'return',
    'for',
    'while',
    'if',
    'else',
    'elif',
    'in',
    'pass',
    'continue',
    'break',
    'True',
    'False',
    'None',
    'and',
    'or',
    'not',
    'class',
    'import',
    'from',
    'as',
  };

  static const TextStyle _baseStyle = TextStyle(
    fontFamily: 'Courier',
    fontSize: 14,
    color: Color(0xFF1D2939),
    height: 1.5,
  );

  static const TextStyle _keywordStyle = TextStyle(
    fontFamily: 'Courier',
    fontSize: 14,
    color: Color(0xFF1D4ED8),
    fontWeight: FontWeight.w700,
    height: 1.5,
  );

  static const TextStyle _stringStyle = TextStyle(
    fontFamily: 'Courier',
    fontSize: 14,
    color: Color(0xFFB54708),
    height: 1.5,
  );

  static const TextStyle _commentStyle = TextStyle(
    fontFamily: 'Courier',
    fontSize: 14,
    color: Color(0xFF667085),
    fontStyle: FontStyle.italic,
    height: 1.5,
  );

  static const TextStyle _numberStyle = TextStyle(
    fontFamily: 'Courier',
    fontSize: 14,
    color: Color(0xFF7A271A),
    height: 1.5,
  );

  @override
  TextSpan buildTextSpan({
    required BuildContext context,
    TextStyle? style,
    required bool withComposing,
  }) {
    final source = text;
    if (source.isEmpty) {
      return const TextSpan(text: '', style: _baseStyle);
    }

    final spans = <TextSpan>[];
    var currentIndex = 0;
    for (final match in _tokenPattern.allMatches(source)) {
      if (match.start > currentIndex) {
        spans.add(
          TextSpan(
            text: source.substring(currentIndex, match.start),
            style: _baseStyle,
          ),
        );
      }

      final token = match.group(0) ?? '';
      spans.add(TextSpan(text: token, style: _styleForToken(token)));
      currentIndex = match.end;
    }

    if (currentIndex < source.length) {
      spans.add(
        TextSpan(
          text: source.substring(currentIndex),
          style: _baseStyle,
        ),
      );
    }

    return TextSpan(style: style ?? _baseStyle, children: spans);
  }

  TextStyle _styleForToken(String token) {
    if (token.startsWith('#')) {
      return _commentStyle;
    }
    if (token.startsWith("'") || token.startsWith('"')) {
      return _stringStyle;
    }
    if (_keywords.contains(token)) {
      return _keywordStyle;
    }
    if (double.tryParse(token) != null) {
      return _numberStyle;
    }
    return _baseStyle;
  }
}
