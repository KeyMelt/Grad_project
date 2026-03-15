import 'package:flutter/material.dart';
import 'package:rl_ide/core/theme.dart';
import 'package:rl_ide/layout/main_layout.dart';

void main() {
  runApp(const RLSimulationIDE());
}

class RLSimulationIDE extends StatelessWidget {
  final MainLayout? home;

  const RLSimulationIDE({super.key, this.home});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RL Setup Environment',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: home ?? const MainLayout(),
    );
  }
}
