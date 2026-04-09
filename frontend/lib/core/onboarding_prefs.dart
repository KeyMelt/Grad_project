import 'package:shared_preferences/shared_preferences.dart';

class OnboardingPrefs {
  static const String _onboardingSeenKey = 'rl_ide_onboarding_seen';

  static Future<bool> shouldShowOnboarding() async {
    final prefs = await SharedPreferences.getInstance();
    return !(prefs.getBool(_onboardingSeenKey) ?? false);
  }

  static Future<void> markOnboardingSeen() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_onboardingSeenKey, true);
  }
}
