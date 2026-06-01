import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ── Brand palette ─────────────────────────────────────────────────────────
  static const Color navyDeep = Color(0xFF14223F);   // primary dark background
  static const Color navy = Color(0xFF1A2B4A);        // text / UI on dark
  static const Color primaryBlue = Color(0xFF00C9A7); // teal accent (brand primary)
  static const Color amber = Color(0xFFF5A623);       // alt accent
  static const Color light = Color(0xFFF4F7FC);       // mark on dark / light bg
  static const Color paper = Color(0xFFF5F3EE);       // warm off-white

  // ── Semantic aliases ──────────────────────────────────────────────────────
  static const Color backgroundLight = light;
  static const Color surfaceWhite = Color(0xFFFFFFFF);
  static const Color textPrimary = navy;
  static const Color textSecondary = Color(0xFF6B7280);
  static const Color borderLight = Color(0xFFE5E7EB);
  static const Color successGreen = Color(0xFF10B981);

  // ── Teal-tinted surface/border tokens (replaces old blue-tinted E8F0FE) ──
  static const Color tealSurface = Color(0xFFE0F7F3);
  static const Color tealBorder = Color(0xFF7DDDD0);

  static ThemeData get lightTheme => _buildTheme(Brightness.light);
  static ThemeData get darkTheme => _buildTheme(Brightness.dark);

  static ThemeData _buildTheme(Brightness brightness) {
    final isDark = brightness == Brightness.dark;
    final background = isDark ? const Color(0xFF0A1320) : backgroundLight;
    final surface = isDark ? navyDeep : surfaceWhite;
    final text = isDark ? light : textPrimary;
    final secondary = isDark ? const Color(0xFF94A3B8) : textSecondary;
    final border = isDark ? const Color(0xFF1E3050) : borderLight;

    return ThemeData(
      brightness: brightness,
      useMaterial3: true,
      scaffoldBackgroundColor: background,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryBlue,
        brightness: brightness,
        primary: primaryBlue,
        surface: surface,
      ),
      cardColor: surface,
      dialogTheme: DialogThemeData(
        backgroundColor: surface,
        surfaceTintColor: surface,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: surface,
        foregroundColor: text,
        surfaceTintColor: surface,
        elevation: 0,
      ),
      fontFamily: GoogleFonts.dmSans().fontFamily,
      textTheme: TextTheme(
        titleLarge: TextStyle(
          color: text,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
        titleMedium: TextStyle(
          color: text,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
        bodyLarge: TextStyle(color: text, fontSize: 16),
        bodyMedium: TextStyle(color: secondary, fontSize: 14),
      ),
      dividerTheme: DividerThemeData(
        color: border,
        thickness: 1,
        space: 1,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryBlue,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: text,
          side: BorderSide(color: border),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
        ),
      ),
    );
  }
}
