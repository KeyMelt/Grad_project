import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';

void main() {
  group('resolveBackendBaseUrl', () {
    test('uses configured backend base url when provided', () {
      final resolved = resolveBackendBaseUrl(
        configuredBaseUrl: 'https://api.example.com/',
        isWeb: true,
        isReleaseMode: true,
        currentUri: Uri.parse('https://app.example.com/workspace'),
      );

      expect(resolved, 'https://api.example.com');
    });

    test('uses same origin for production-style web hosts without config', () {
      final resolved = resolveBackendBaseUrl(
        configuredBaseUrl: '',
        isWeb: true,
        isReleaseMode: true,
        currentUri: Uri.parse('https://app.example.com/workspace'),
      );

      expect(resolved, 'https://app.example.com');
    });

    test('uses current private-network host on local web sessions', () {
      final resolved = resolveBackendBaseUrl(
        configuredBaseUrl: '',
        isWeb: true,
        isReleaseMode: false,
        currentUri: Uri.parse('http://192.168.1.25:54321/workspace'),
      );

      expect(resolved, 'http://192.168.1.25:8000');
    });

    test('keeps localhost-style web sessions on the local backend port', () {
      final resolved = resolveBackendBaseUrl(
        configuredBaseUrl: '',
        isWeb: true,
        isReleaseMode: false,
        currentUri: Uri.parse('http://localhost:54321/workspace'),
      );

      expect(resolved, 'http://localhost:8000');
    });

    test('uses local backend for non-web clients without config', () {
      final resolved = resolveBackendBaseUrl(
        configuredBaseUrl: '',
        isWeb: false,
        isReleaseMode: false,
      );

      expect(resolved, 'http://127.0.0.1:8000');
    });
  });
}
