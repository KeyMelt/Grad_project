import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_math_fork/flutter_math.dart';

void main() {
  testWidgets('Math rendering test', (WidgetTester tester) async {
    const eq = r"V^{\pi}(s)=\sum_a \pi(a|s)\sum_{s',r} p(s',r|s,a)\left[r+\gamma V^{\pi}(s')\right]";
    
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Math.tex(eq),
        ),
      ),
    );
    
    expect(find.byType(Math), findsOneWidget);
  });
}
