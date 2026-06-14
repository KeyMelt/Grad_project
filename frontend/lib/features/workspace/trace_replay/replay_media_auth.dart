import '../../../core/backend_api.dart';

Map<String, String> replayMediaAuthHeaders() {
  final token = AuthSessionStore.accessToken;
  if (token == null || token.isEmpty) {
    return const <String, String>{};
  }
  return {'Authorization': 'Bearer $token'};
}
