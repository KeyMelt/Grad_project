import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/theme.dart';
import 'package:rl_ide/core/onboarding_prefs.dart';
import 'package:rl_ide/firebase_options.dart';
import 'package:rl_ide/features/onboarding/splash_screen.dart';
import 'package:rl_ide/layout/main_layout.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  if (kIsWeb) {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
  }
  await BackendConnectionManager().init();
  runApp(const RLSimulationIDE());
}

class RLSimulationIDE extends StatelessWidget {
  final MainLayout? home;

  const RLSimulationIDE({super.key, this.home});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RL Learning Platform',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: home ?? const _AppBootstrapper(),
    );
  }
}

class _AppBootstrapper extends StatefulWidget {
  const _AppBootstrapper();

  @override
  State<_AppBootstrapper> createState() => _AppBootstrapperState();
}

class _AppBootstrapperState extends State<_AppBootstrapper> {
  bool _loading = true;
  bool _showOnboarding = false;

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    final shouldShowOnboarding = await OnboardingPrefs.shouldShowOnboarding();
    await Future<void>.delayed(const Duration(milliseconds: 1500));

    if (!mounted) {
      return;
    }

    setState(() {
      _showOnboarding = shouldShowOnboarding;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const AppSplashScreen();
    }

    return MainLayout(
      showOnboardingOnStart: _showOnboarding,
    );
  }
}
