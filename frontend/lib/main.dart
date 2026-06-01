import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:mcp_toolkit/mcp_toolkit.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/theme.dart';
import 'package:rl_ide/core/onboarding_prefs.dart';
import 'package:rl_ide/features/onboarding/splash_screen.dart';
import 'package:rl_ide/layout/main_layout.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  MCPToolkitBinding.instance
    ..initialize()
    ..initializeFlutterToolkit();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  await BackendConnectionManager().init();
  runApp(const RLSimulationIDE());
}

const String _themeModePrefsKey = 'rl_ide_dark_mode';

class RLSimulationIDE extends StatefulWidget {
  final MainLayout? home;

  const RLSimulationIDE({super.key, this.home});

  @override
  State<RLSimulationIDE> createState() => _RLSimulationIDEState();
}

class _RLSimulationIDEState extends State<RLSimulationIDE> {
  bool _isDarkMode = false;

  @override
  void initState() {
    super.initState();
    _loadThemeMode();
  }

  Future<void> _loadThemeMode() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      if (!mounted) {
        return;
      }
      setState(() {
        _isDarkMode = prefs.getBool(_themeModePrefsKey) ?? false;
      });
    } catch (_) {}
  }

  Future<void> _toggleThemeMode() async {
    final nextValue = !_isDarkMode;
    setState(() => _isDarkMode = nextValue);
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(_themeModePrefsKey, nextValue);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final providedHome = widget.home;

    return MaterialApp(
      title: 'Reinfource',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: _isDarkMode ? ThemeMode.dark : ThemeMode.light,
      home: providedHome != null
          ? MainLayout(
              cubit: providedHome.cubit,
              showOnboardingOnStart: providedHome.showOnboardingOnStart,
              isDarkMode: _isDarkMode,
              onToggleThemeMode: _toggleThemeMode,
            )
          : _AppBootstrapper(
              isDarkMode: _isDarkMode,
              onToggleThemeMode: _toggleThemeMode,
            ),
    );
  }
}

class _AppBootstrapper extends StatefulWidget {
  final bool isDarkMode;
  final VoidCallback onToggleThemeMode;

  const _AppBootstrapper({
    required this.isDarkMode,
    required this.onToggleThemeMode,
  });

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
      isDarkMode: widget.isDarkMode,
      onToggleThemeMode: widget.onToggleThemeMode,
    );
  }
}
