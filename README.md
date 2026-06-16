# Reinforcement Learning Learning Platform

Desktop and web learning platform for tabular reinforcement learning lessons. The app combines a Flutter workspace, a FastAPI gateway, an execution worker, a user/evaluation service, Docker-backed code execution, Gymnasium environments, and Manim replay generation.

## Quick Start

Prerequisites:

- macOS with Flutter installed.
- Docker Desktop installed and running.
- Python 3.10+ environment with the backend requirements installed.

Start the full local platform:

```bash
cd grad_project
./start_app.sh
```

Useful variants:

```bash
./start_app.sh chrome
./start_app.sh --backend-only
./start_app.sh --no-build
```

Start the production-shaped local stack on non-conflicting localhost ports:

```bash
cd grad_project
./deploy/local-prod.sh seed-media
./deploy/local-prod.sh up
```

This path keeps the VPS service topology (`gateway`, `execution-worker`, `user-evaluation`, `manim-service`, `frontend`) but defaults to safe local settings:

- Frontend: `http://127.0.0.1:18080`
- Gateway: `http://127.0.0.1:18000`
- Mutable state lives under `~/Desktop/grad_support_files/grad_project/local_prod`
- Auth and media default to local-safe behavior until you tighten the generated env file for stricter parity

Useful prep/diagnostic commands:

```bash
./deploy/local-prod.sh doctor
./deploy/local-prod.sh seed-media
./deploy/local-prod.sh build
./deploy/local-prod.sh ps
```

## Manual Startup

Start the three backend services through Docker Compose:

```bash
cd grad_project
PROJECT_ROOT="$PWD" docker compose up -d gateway execution-service user-evaluation-service
```

## Cloud Docker Image

This image packages the backend platform services (gateway, execution worker, and user/evaluation service). The Flutter client is deployed separately.

Build the production image:

```bash
cd grad_project
docker build -f Dockerfile.cloud -t rl-platform:cloud .
```

Run as a single cloud container (gateway + worker + user service in one image):

```bash
docker run --rm -p 8000:8000 \
  -e SERVICE_NAME=all-in-one \
  -e PORT=8000 \
  -e RL_IDE_INTERNAL_TOKEN=change-me \
  -e RL_IDE_WORKSPACE_USE_DOCKER=0 \
  rl-platform:cloud
```

Run as split services using the same image (recommended for scaling):

```bash
# execution worker
docker run -d --name rl-worker -p 8100:8100 \
  -e SERVICE_NAME=execution-worker \
  -e RL_IDE_INTERNAL_TOKEN=change-me \
  -e RL_IDE_WORKSPACE_USE_DOCKER=0 \
  rl-platform:cloud

# user/evaluation service
docker run -d --name rl-user -p 8200:8200 \
  -e SERVICE_NAME=user-evaluation \
  -e RL_IDE_INTERNAL_TOKEN=change-me \
  -e RL_IDE_PROGRESS_BACKEND=sql \
  rl-platform:cloud

# gateway
docker run --rm -p 8000:8000 \
  -e SERVICE_NAME=gateway \
  -e RL_IDE_EXECUTION_MODE=remote \
  -e RL_IDE_USER_SERVICE_MODE=remote \
  -e RL_IDE_EXECUTION_WORKER_URL=http://<worker-host>:8100 \
  -e RL_IDE_USER_SERVICE_URL=http://<user-service-host>:8200 \
  -e RL_IDE_INTERNAL_TOKEN=change-me \
  rl-platform:cloud
```

Start Flutter in another terminal:

```bash
cd grad_project/frontend
flutter pub get
flutter run -d macos
```

Run the frontend in Chrome:

```bash
cd grad_project/frontend
flutter run -d chrome
```

## Configuration

Copy `.env.example` when setting up a new local environment and override only the values that differ on your machine. Do not commit real Firebase credentials, Gemini keys, or production database URLs.

Important environment variables:

- `RL_IDE_EXECUTION_MODE`: `remote` for the worker service, `local` for single-process development.
- `RL_IDE_USER_SERVICE_MODE`: `remote` for the user/evaluation service, `local` for in-process development.
- `RL_IDE_INTERNAL_TOKEN`: shared gateway-to-service token for local service calls.
- `RL_IDE_DB_URL`: SQLModel database URL.
- `RL_IDE_WORKSPACE_USE_DOCKER`: must be `1` for the learner workspace runtime.
- `RL_IDE_MANIM_PYTHON`: Python executable used to run Manim.
- `GEMINI_API_KEY`: optional; used only for failed-submit feedback when Gemini is enabled.

## Project Structure

- `backend/api_gateway/`: public FastAPI gateway used by Flutter.
- `backend/execution_worker/`: internal execution and workspace service.
- `backend/user_evaluation_service/`: internal auth, dashboard, quiz, and N-gain service.
- `backend/services/`: business services shared by the backend entrypoints.
- `backend/rl_engine/`: Gymnasium environment adapters and lesson execution logic.
- `backend/concept_videos/`: Manim source and render registration for pre-rendered lesson videos.
- `backend/visualization/`: Manim replay rendering code for submitted lesson traces.
- `backend/tests/`: backend unit and integration tests.
- `frontend/lib/core/`: API client, app state, models, and shared constants.
- `frontend/lib/features/`: lesson browser, workspace, quiz, admin, home, onboarding, and flashcards.
- Support documents such as thesis notes, planning files, audits, and generated reports are kept outside the repository.

Generated files are intentionally excluded from source control:

- `backend/data/`
- `backend/visualization/animations/`
- `backend/concept_videos/_manim_media/`
- `backend/media/concept_videos/*.mp4`

## Test Commands

Backend:

```bash
cd grad_project
source .venv/bin/activate
pytest -c backend/pytest.ini backend/tests
```

Frontend:

```bash
cd grad_project/frontend
flutter test
flutter analyze
```

Python formatting and linting:

```bash
cd grad_project
black --check backend
ruff check backend
```

## Runtime Notes

- The public gateway listens on `http://127.0.0.1:8000`.
- The execution worker listens on `http://127.0.0.1:8100` outside Compose and `http://execution-service:8100` inside Compose.
- The user/evaluation service listens on `http://127.0.0.1:8200` outside Compose and `http://user-evaluation-service:8200` inside Compose.
- `Run` uses the Docker-backed workspace runtime.
- `Submit` uses the lesson validation, RL execution, trace logging, and Manim replay pipeline.
- If Manim rendering fails, execution can still return metrics and trace data without a replay video.
