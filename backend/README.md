# Backend Structure

The backend is a FastAPI-based service layer for lessons, code execution, RL simulation, visualization, workspace sessions, and learner evaluation.

## Entry Points

- `main.py`: local development launcher for the API gateway.
- `api_gateway/base.py`: public FastAPI gateway and route definitions.
- `execution_worker/main.py`: worker-service entry point for remote workspace and execution mode.

## Core Runtime Modules

- `execution_runtime.py`: validates and executes a submitted lesson in an isolated process.
- `rl_engine/engine.py`: wraps Gymnasium environments and runs RL episode loops.
- `validation/validator.py`: checks submitted code against lesson contracts.
- `logger/event_logger.py`: records step-level RL traces.
- `visualization/controller.py`: converts traces into Manim replay artifacts.

## Lesson and Assessment Modules

- `lessons.py`: backend lesson registry and starter templates.
- `lesson_tests.py`: lesson-specific sample tests.
- `exercise_templates.py`: utilities for filling guided code templates.
- `services/quiz_service.py`: pre-test and post-test sessions.
- `services/student_progress_service.py`: local SQL-backed learner progress.
- `services/user_evaluation_service.py`: composition layer for auth, quiz, dashboard, and N-gain.

## Persistence

- `persistence.py`: SQLModel database setup.
- `artifact_store_sqlite.py`: execution artifact references.
- `workspace_store_sqlite.py`: workspace sessions, runs, and artifacts.
- `job_store.py` and `job_store_sqlite.py`: execution task tracking.

## Generated Paths

These are runtime outputs, not source:

- `backend/data/`
- `backend/logger/logs/`
- `backend/visualization/animations/`
- `backend/concept_videos/_manim_media/`
- `backend/media/concept_videos/*.mp4`

They are ignored by `.gitignore`.

## Test Command

```bash
source /Users/ultramarine/.venvs/manim/bin/activate
rtk pytest -c backend/pytest.ini backend/tests
```
