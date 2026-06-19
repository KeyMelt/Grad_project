import 'package:flutter/foundation.dart';
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
        nativePlatform: TargetPlatform.macOS,
      );

      expect(resolved, 'http://127.0.0.1:8000');
    });

    test('requires explicit backend config for iOS installs', () {
      final resolved = resolveBackendBaseUrl(
        configuredBaseUrl: '',
        isWeb: false,
        isReleaseMode: true,
        nativePlatform: TargetPlatform.iOS,
      );

      expect(resolved, '');
    });
  });

  group('shouldUseSavedBackendUrl', () {
    test('ignores saved backend url when build-time config is provided', () {
      final shouldUseSaved = shouldUseSavedBackendUrl(
        configuredBaseUrl: 'https://reinfource.app',
        savedUrl: 'http://192.168.1.25:8000',
      );

      expect(shouldUseSaved, isFalse);
    });

    test('uses saved backend url when build-time config is absent', () {
      final shouldUseSaved = shouldUseSavedBackendUrl(
        configuredBaseUrl: '',
        savedUrl: 'http://192.168.1.25:8000',
      );

      expect(shouldUseSaved, isTrue);
    });
  });

  group('shouldAutoDiscoverBackend', () {
    test('does not auto-discover on iOS without explicit config', () {
      final shouldAutoDiscover = shouldAutoDiscoverBackend(
        savedUrl: null,
        configuredBaseUrl: '',
        isWeb: false,
        nativePlatform: TargetPlatform.iOS,
      );

      expect(shouldAutoDiscover, isFalse);
    });

    test('auto-discovers on macOS without saved or configured url', () {
      final shouldAutoDiscover = shouldAutoDiscoverBackend(
        savedUrl: null,
        configuredBaseUrl: '',
        isWeb: false,
        nativePlatform: TargetPlatform.macOS,
      );

      expect(shouldAutoDiscover, isTrue);
    });
  });
}
