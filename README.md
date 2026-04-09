# Reinforcement Learning IDE

This repository is organized around two real application folders:

- `backend/`: FastAPI service for lesson execution, Gymnasium simulation, validation, and Manim rendering.
- `frontend/`: Flutter application that calls the backend and displays lesson state, metrics, and video output paths.

The old top-level Flutter starter app has been removed so the repo structure matches the actual project.

## One-command startup

Start Docker if needed, bring up the execution worker and gateway, then launch Flutter:

```bash
cd /Users/ultramarine/Desktop/grad_project
./start_app.sh
```

Use a different Flutter target if needed:

```bash
./start_app.sh chrome
```

## Run (Local, Single-Service)

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

## Run (Local, Split Services)

Start the execution worker first:

```bash
cd /Users/ultramarine/Desktop/grad_project
source /Users/ultramarine/.venvs/manim/bin/activate
python -m backend.execution_worker.main
```

Then start the gateway in another terminal:

```bash
cd /Users/ultramarine/Desktop/grad_project
source /Users/ultramarine/.venvs/manim/bin/activate
export RL_IDE_EXECUTION_MODE=remote
export RL_IDE_EXECUTION_WORKER_URL=http://127.0.0.1:8100
python -m backend.main
```

## Test Commands

```bash
cd /Users/ultramarine/Desktop/grad_project
source /Users/ultramarine/.venvs/manim/bin/activate
pytest -c backend/pytest.ini backend/tests
```

```bash
cd /Users/ultramarine/Desktop/grad_project/frontend
flutter test
```

## Firebase Mode

Gateway defaults to SQL persistence. To use Firebase-backed auth/data:

```bash
export RL_IDE_PROGRESS_BACKEND=firebase
export RL_IDE_FIREBASE_CREDENTIALS_PATH=/absolute/path/to/firebase-service-account.json
```

In Firebase mode, `/auth/sign-in` expects `firebase_id_token` in the request body.

## Notes

- Keep the app in `Simulation` mode. `Hardware` mode is still a placeholder.
- The backend listens on `http://127.0.0.1:8000`.
- The execution worker listens on `http://127.0.0.1:8100` when split mode is enabled.
- Learner data is now persisted in SQL (`backend/data/rl_learning_platform.db` by default).
- Set `RL_IDE_DB_URL` to use a production database (for example PostgreSQL via `psycopg`).
- Admin can export N-gain metrics as Excel from `GET /admin/metrics/n-gain/export`.
- The frontend now submits runs to `/submit`, polls `/tasks/{task_id}`, and displays returned metrics and video path information.
- The older synchronous `/execute` endpoint is still available for direct smoke testing.
- If Manim rendering is unavailable, execution can still succeed but return no video path.
