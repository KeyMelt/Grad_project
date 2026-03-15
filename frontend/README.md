# Frontend

Flutter client for the Reinforcement Learning IDE.

## Run

```bash
cd /Users/ultramarine/Desktop/grad_project/frontend
flutter pub get
flutter run -d macos
```

## Notes

- This app talks to the backend at `http://127.0.0.1:8000` by default.
- Keep `Run mode` on `Simulation`.
- Runs are submitted asynchronously and the app polls for task completion.
- macOS support lives under `frontend/macos/`.
