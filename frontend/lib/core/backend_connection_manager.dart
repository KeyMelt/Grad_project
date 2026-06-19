import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:multicast_dns/multicast_dns.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'backend_api_models.dart';
import 'constants.dart';

class BackendConnectionManager extends ChangeNotifier {
  static final BackendConnectionManager _instance =
      BackendConnectionManager._internal();
  factory BackendConnectionManager() => _instance;
  BackendConnectionManager._internal() : _baseUrl = defaultBackendBaseUrl;

  String _baseUrl;
  WorkspaceConnectionStatus _status = WorkspaceConnectionStatus.disconnected;
  String? _lastError;
  Timer? _healthTimer;
  MDnsClient? _mDnsClient;

  String get baseUrl => _baseUrl;
  WorkspaceConnectionStatus get status => _status;
  String? get lastError => _lastError;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    final savedUrl = prefs.getString(AppConstants.backendUrlPreferenceKey);
    if (shouldUseSavedBackendUrl(
      configuredBaseUrl: _configuredBackendBaseUrl,
      savedUrl: savedUrl,
    )) {
      _baseUrl = _normalizeBackendUrl(savedUrl!);
    }
    notifyListeners();
    unawaited(checkHealth());
    _healthTimer = Timer.periodic(
      AppConstants.backendHealthInterval,
      (_) => checkHealth(),
    );
    if (shouldAutoDiscoverBackend(
      savedUrl: savedUrl,
      configuredBaseUrl: _configuredBackendBaseUrl,
      isWeb: kIsWeb,
      nativePlatform: defaultTargetPlatform,
    )) {
      unawaited(_autoDiscover());
    }
  }

  Future<void> _autoDiscover() async {
    try {
      _mDnsClient = MDnsClient();
      await _mDnsClient!.start();
      await for (final PtrResourceRecord ptr in _mDnsClient!
          .lookup<PtrResourceRecord>(
              ResourceRecordQuery.serverPointer('_rl-ide._tcp.local'))) {
        await for (final SrvResourceRecord srv in _mDnsClient!
            .lookup<SrvResourceRecord>(
                ResourceRecordQuery.service(ptr.domainName))) {
          await for (final IPAddressResourceRecord ip in _mDnsClient!
              .lookup<IPAddressResourceRecord>(
                  ResourceRecordQuery.addressIPv4(srv.target))) {
            final discoveredUrl = 'http://${ip.address.address}:${srv.port}';
            if (discoveredUrl != _baseUrl) {
              await updateUrl(discoveredUrl);
            }
            break;
          }
        }
      }
    } catch (e) {
      debugPrint('mDNS discovery failed: $e');
    } finally {
      _mDnsClient?.stop();
    }
  }

  Future<void> updateUrl(String newUrl) async {
    final sanitized = _normalizeBackendUrl(newUrl);
    _baseUrl = sanitized;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.backendUrlPreferenceKey, sanitized);
    notifyListeners();
    await checkHealth();
  }

  Future<void> checkHealth() async {
    if (_baseUrl.isEmpty) {
      _status = WorkspaceConnectionStatus.failed;
      _lastError =
          'BACKEND_BASE_URL is required for iOS installs. Rebuild with the VPS URL.';
      notifyListeners();
      return;
    }

    try {
      final response = await http.get(Uri.parse('$_baseUrl/')).timeout(
            AppConstants.backendHealthTimeout,
          );
      if (response.statusCode == 200) {
        _status = WorkspaceConnectionStatus.ready;
        _lastError = null;
      } else {
        _status = WorkspaceConnectionStatus.failed;
        _lastError = 'Server returned ${response.statusCode}';
      }
    } catch (e) {
      _status = WorkspaceConnectionStatus.failed;
      _lastError = e.toString();
    }
    notifyListeners();
  }

  @override
  void dispose() {
    _healthTimer?.cancel();
    _mDnsClient?.stop();
    super.dispose();
  }
}

const String _configuredBackendBaseUrl =
    String.fromEnvironment('BACKEND_BASE_URL', defaultValue: '');

String get defaultBackendBaseUrl => resolveBackendBaseUrl(
      configuredBaseUrl: _configuredBackendBaseUrl,
      isWeb: kIsWeb,
      isReleaseMode: kReleaseMode,
      currentUri: kIsWeb ? Uri.base : null,
      nativePlatform: defaultTargetPlatform,
    );

@visibleForTesting
String resolveBackendBaseUrl({
  required String configuredBaseUrl,
  required bool isWeb,
  required bool isReleaseMode,
  Uri? currentUri,
  TargetPlatform? nativePlatform,
}) {
  final configured = configuredBaseUrl.trim();
  if (configured.isNotEmpty) {
    return _normalizeBackendUrl(configured);
  }

  if (!isWeb) {
    if ((nativePlatform ?? defaultTargetPlatform) == TargetPlatform.iOS) {
      return '';
    }
    return AppConstants.defaultBackendLocalUrl;
  }

  final runtimeUri = currentUri ?? Uri.base;
  final host = runtimeUri.host.toLowerCase();
  if (_isLocalDevelopmentHost(host)) {
    return Uri(
      scheme: 'http',
      host: _normalizeLocalHost(host),
      port: AppConstants.defaultBackendPort,
    ).toString();
  }

  return _originWithoutTrailingSlash(runtimeUri);
}

@visibleForTesting
bool shouldUseSavedBackendUrl({
  required String configuredBaseUrl,
  required String? savedUrl,
}) {
  if (configuredBaseUrl.trim().isNotEmpty) {
    return false;
  }

  return savedUrl != null && savedUrl.trim().isNotEmpty;
}

@visibleForTesting
bool shouldAutoDiscoverBackend({
  required String? savedUrl,
  required String configuredBaseUrl,
  required bool isWeb,
  required TargetPlatform nativePlatform,
}) {
  if (savedUrl != null && savedUrl.trim().isNotEmpty) {
    return false;
  }
  if (configuredBaseUrl.trim().isNotEmpty) {
    return false;
  }
  if (!isWeb) {
    return nativePlatform == TargetPlatform.macOS;
  }

  return _isLocalDevelopmentHost(Uri.base.host.toLowerCase());
}

String _normalizeBackendUrl(String rawUrl) {
  var sanitized = rawUrl.trim();
  if (!sanitized.startsWith('http')) {
    sanitized = 'http://$sanitized';
  }
  if (sanitized.endsWith('/')) {
    sanitized = sanitized.substring(0, sanitized.length - 1);
  }
  return sanitized;
}

String _originWithoutTrailingSlash(Uri uri) {
  final origin = uri.origin;
  return origin.endsWith('/') ? origin.substring(0, origin.length - 1) : origin;
}

bool _isLocalDevelopmentHost(String host) {
  if (host.isEmpty ||
      host == 'localhost' ||
      host == '127.0.0.1' ||
      host == '0.0.0.0' ||
      host == '::1' ||
      host == '[::1]' ||
      host == '::' ||
      host == '[::]') {
    return true;
  }

  if (host.endsWith('.local')) {
    return true;
  }

  final ipv4Match =
      RegExp(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$').firstMatch(host);
  if (ipv4Match == null) {
    return false;
  }

  final octets = ipv4Match
      .groups([1, 2, 3, 4])
      .whereType<String>()
      .map(int.parse)
      .toList();
  if (octets.any((octet) => octet < 0 || octet > 255)) {
    return false;
  }

  return octets[0] == 10 ||
      (octets[0] == 172 && octets[1] >= 16 && octets[1] <= 31) ||
      (octets[0] == 192 && octets[1] == 168);
}

String _normalizeLocalHost(String host) {
  switch (host) {
    case '':
    case '0.0.0.0':
    case '::':
    case '[::]':
    case '::1':
    case '[::1]':
      return '127.0.0.1';
    default:
      return host;
  }
}
