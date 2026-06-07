# Project Agent Instructions

## Shell Usage

Prefer `rtk` for noisy shell commands in this repository to reduce token usage and context bloat.

Use `rtk` by default for:

- `git` commands
- directory listings such as `ls`
- file discovery such as `find`
- text search when output may be large
- test runners such as `pytest`; use `rtk proxy` for tools that RTK does not wrap directly
- log-heavy commands
- Docker commands with verbose output

Preferred examples in this repository:

- `rtk git status`
- `rtk git diff`
- `rtk ls`
- `rtk find backend -name '*.py'`
- `rtk pytest -c backend/pytest.ini backend/tests`
- `rtk proxy flutter test`
- `rtk docker compose ps`

Use raw commands instead of `rtk` when exact output fidelity matters, including:

- precise debugging of failing commands
- exact compiler or runtime stderr inspection
- commands where spacing, byte layout, or full raw formatting matters
- cases where filtering may hide information needed to diagnose backend, frontend, or infrastructure issues

## Repository Context

This project contains:

- `backend/`: FastAPI-based RL execution, validation, persistence, and visualization services
- `frontend/`: Flutter client for lessons, workspace, replay, and quiz flows

When running tests or diagnostics, prefer targeted commands over broad full-suite runs unless the task requires wider verification.

## Support Document Routing

Do not create or keep thesis material, planning docs, audit reports, codebase traces, hierarchy/orientation files, study-buddy plans, generated report PDFs, or similar support documents in this repository.

Route those materials to:

- `/Users/ultramarine/Desktop/grad_support_files`

Preserve a `grad_project/` subfolder inside that directory when useful, so moved files keep their original project-relative context. Keep only source code, app assets, tests, runtime configuration, and essential project README-style documentation in the main codebase.

## StudyBuddy Branch Progress

When working on the `StudyBuddy` branch, check the progress tracker before making changes:

- `/Users/ultramarine/Desktop/grad_support_files/grad_project/study_buddy_progress.md`

That file is the working reference for what has been completed and what remains. Keep it updated after each meaningful Study Buddy implementation slice.

Current high-level status:

- Completed through Phase 5 in a targeted V1 form: telemetry foundation, deterministic trigger/coordinator layer, bounded Gemini-backed intervention generation with deterministic fallback, reflection/guardrail pass, coach panel, mastery snapshots, spaced-review dashboard summary, timeline/summary APIs, learning analytics export, and evidence packaging.
- The Study Buddy now uses AI when `GEMINI_API_KEY` is present in the ignored local `.env` file and `RL_IDE_STUDY_BUDDY_AI_ENABLED` is not disabled.
- Phase 5 artifacts live under `/Users/ultramarine/Desktop/grad_support_files/grad_project/study_buddy_phase5`.

Remaining major work:

- Optional hardening: SQLite migration/backfill handling, broader dashboard/timeline UI coverage, and live manual QA. Mocked Gemini success/fallback tests and route-level quiz mastery evidence tests are already implemented.
- Keep `.env` ignored and do not print or commit secrets.

Backend verification for this branch should use the Manim venv:

- `/Users/ultramarine/.venvs/manim/bin/python3`

Use the relevant Flutter skills for frontend Study Buddy UI and tests, especially:

- `flutter-add-widget-test`
- `flutter-build-responsive-layout` when responsive layout changes are involved

## Communication Guidelines

- Reduce flattery and pleasantries.
- Be objective and blunt in your responses.
- Do not commit or start the CI/CD pipeline unless explicitly instructed to do so.

## Development & Deployment Guidelines

- **No Placeholder Code in Production**: Never push code containing placeholder links, dummy URLs, or skeleton components to the `main` branch. All paths, buttons, and routing logic must be fully functional and pointing to the correct integration endpoints before merging.
- **Pre-Merge Verification**: Double-check all UI interactability and routing logic before initiating any CI/CD deployment or executing a merge to `main`. This is a high-stakes environment; verify all links.
