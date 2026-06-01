import 'package:flutter/material.dart';
import '../../core/brand_mark.dart';
import '../../core/theme.dart';

class AppSplashScreen extends StatelessWidget {
  const AppSplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: AppTheme.navyDeep,
      body: SafeArea(
        child: Center(child: _SplashBrand()),
      ),
    );
  }
}

class _SplashBrand extends StatelessWidget {
  const _SplashBrand();

  @override
  Widget build(BuildContext context) {
    return const Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        ReinfourceLockup(
          markSize: 72,
          fontSize: 52,
          color: AppTheme.light,
          accent: AppTheme.primaryBlue,
        ),
      ],
    );
  }
}
