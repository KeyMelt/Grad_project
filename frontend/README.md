# Frontend

Flutter client for the Reinforcement Learning IDE.

## Local macOS run

```bash
cd /Users/ultramarine/Desktop/grad_project/frontend
flutter pub get
flutter run -d macos
```

The macOS client defaults to `http://127.0.0.1:8000` when no backend URL is configured.

## iPad install-ready build

The iPad presentation path is build-time configured and should point directly at the deployed VPS.

```bash
cd /Users/ultramarine/Desktop/grad_project/frontend
flutter pub get
flutter build ios --simulator --dart-define=BACKEND_BASE_URL=https://<vps-domain>
```

For a real iPad install from Xcode:

1. Open [Runner.xcworkspace](/Users/ultramarine/Desktop/grad_project/frontend/ios/Runner.xcworkspace).
2. Select the `Runner` target and a connected physical iPad.
3. In `Signing & Capabilities`, set your Apple Developer Team.
4. Keep `Automatically manage signing` enabled.
5. Confirm the bundle identifier is `com.example.gradProject-yousefG`, or update it to another identifier that is also registered in Firebase before building.
6. In Xcode build settings or the Flutter build step, pass `BACKEND_BASE_URL=https://<vps-domain>`.
7. Build and run on device. If iPadOS asks you to trust the developer certificate, trust it in Settings and launch again.

Behavior notes:

- The current plugin stack requires iPadOS 15.0 or newer.
- iOS does not fall back to `127.0.0.1` or mDNS discovery on a fresh install.
- A build-time `BACKEND_BASE_URL` takes precedence over any previously saved backend override.
- The saved backend override still works when no build-time backend URL is supplied.
- Existing Firebase bootstrap remains tied to [GoogleService-Info.plist](/Users/ultramarine/Desktop/grad_project/frontend/ios/Runner/GoogleService-Info.plist) and [firebase_options.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/firebase_options.dart).
