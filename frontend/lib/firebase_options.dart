import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

/// Default Firebase options used by the Flutter app.
///
/// This project currently targets Firebase-backed auth primarily on web.
class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    throw UnsupportedError(
      'DefaultFirebaseOptions are not configured for this platform.',
    );
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyDzP2Xx8uhYLuv07sFTIKImJj2iK3hN4UY',
    appId: '1:262941037092:web:1dc3da7c2e0281e8d9feb1',
    messagingSenderId: '262941037092',
    projectId: 'rlplat',
    authDomain: 'rlplat.firebaseapp.com',
    storageBucket: 'rlplat.firebasestorage.app',
    measurementId: 'G-7XGF0GN4RQ',
  );
}
