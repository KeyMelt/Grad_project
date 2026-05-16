class AppConstants {
  static const int defaultBackendPort = 8000;
  static const String defaultBackendLocalUrl = 'http://127.0.0.1:8000';
  static const String backendUrlPreferenceKey = 'rl_ide_backend_url';
  static const Duration backendHealthInterval = Duration(seconds: 10);
  static const Duration backendHealthTimeout = Duration(seconds: 2);
  static const Duration backendRequestTimeout = Duration(seconds: 20);
  static const Duration backendAuthTimeout = Duration(seconds: 45);

  // Layout Dimensions
  static const double leftPanelWidth = 320.0;
  static const double rightPanelWidth = 350.0;

  static const double defaultPadding = 24.0;
  static const double smallPadding = 12.0;

  static const double cardRadius = 12.0;
}
