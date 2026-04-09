import 'package:flutter/material.dart';

class AppSplashScreen extends StatelessWidget {
  const AppSplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF0A1325),
              Color(0xFF12345D),
              Color(0xFF1A73E8),
            ],
          ),
        ),
        child: const SafeArea(
          child: Center(
            child: _SplashBrand(),
          ),
        ),
      ),
    );
  }
}

class _SplashBrand extends StatelessWidget {
  const _SplashBrand();

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 320,
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(24),
          ),
          child: Image.asset(
            'assets/branding/rl_logo_transparent.png',
            fit: BoxFit.contain,
          ),
        ),
      ],
    );
  }
}
