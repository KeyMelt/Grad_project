# Reinforcement Learning IDE

This repository is organized around two real application folders:

- `backend/`: FastAPI service for lesson execution, Gymnasium simulation, validation, and Manim rendering.
- `frontend/`: Flutter application that calls the backend and displays lesson state, metrics, and video output paths.

The old top-level Flutter starter app has been removed so the repo structure matches the actual project.

## Run

Start the backend from the repository root with the existing Manim virtual environment:

```bash
cd /Users/ultramarine/Desktop/grad_project
source /Users/ultramarine/.venvs/manim/bin/activate
python -m backend.main
```

Start the Flutter app in a second terminal:

```bash
cd /Users/ultramarine/Desktop/grad_project/frontend
flutter pub get
flutter run -d macos
```

You can also run the frontend in Chrome:

```bash
cd /Users/ultramarine/Desktop/grad_project/frontend
flutter run -d chrome
```

## Notes

- Keep the app in `Simulation` mode. `Hardware` mode is still a placeholder.
- The backend listens on `http://127.0.0.1:8000`.
- The frontend now submits runs to `/submit`, polls `/tasks/{task_id}`, and displays returned metrics and video path information.
- The older synchronous `/execute` endpoint is still available for direct smoke testing.
- If Manim rendering is unavailable, execution can still succeed but return no video path.
