# Frontend Structure

The Flutter frontend is organized around a small app shell, shared core services, and feature folders.

## Entry Points

- `main.dart`: initializes backend discovery and launches the application.
- `layout/main_layout.dart`: owns the main navigation shell and composes major screens.

## Core

- `core/backend_api.dart`: HTTP client, task polling, response models, and backend connection state.
- `core/workbench_state.dart`: current app state and workflow logic for lessons, workspace, quiz, and admin flows.
- `core/theme.dart`: visual theme.
- `core/onboarding_prefs.dart`: onboarding preference persistence.

## Features

- `features/home/`: dashboard and progress entry points.
- `features/lessons/`: lesson browser and lesson cards.
- `features/workspace/`: concept, code, terminal, replay, and trace panels.
- `features/quiz/`: pre-test and post-test UI.
- `features/admin/`: lesson editing and metric export UI.
- `features/flashcards/`: concept flashcards.
- `features/onboarding/`: onboarding and splash screen.

## Current Refactor Targets

The frontend is functional, but a few files remain intentionally large after the cleanup pass:

- `core/workbench_state.dart`: should eventually split lesson content, cubit workflow logic, and state models.
- `core/backend_api.dart`: should eventually split API models from HTTP client methods.
- `features/workspace/trace_replay_panel.dart`: should eventually split replay timeline, metric summary, and trace details into smaller widgets.

Those refactors should be done incrementally with focused widget tests after each step.

## Test Command

```bash
rtk proxy flutter test
```
