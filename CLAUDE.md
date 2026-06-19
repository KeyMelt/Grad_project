# Codebase Health Workflow

This project uses a multi-agent orchestrator pattern to perform a full codebase audit,
sanitization, simplification, best-practice review, and security hardening.

## Subagents available

| Agent | Model | Role |
|---|---|---|
| `orchestrator` | opus | Plans and governs the full workflow |
| `code-reviewer` | sonnet | Reads and reviews code quality |
| `sanitizer` | sonnet | Removes dead code, fixes formatting, deduplication |
| `simplifier` | sonnet | Refactors for maintainability and clarity |
| `best-practices` | sonnet | Checks conventions, patterns, and standards |
| `security-auditor` | opus | Deep security vulnerability analysis |

## How to run

Use the slash command to kick off the full workflow:

```
/project:audit
```

Or invoke individual agents explicitly:

```
Use the security-auditor subagent to scan src/auth
Use the simplifier subagent on src/utils
```

## Output conventions

- Each agent writes its findings to `.claude/reports/<agent-name>.md`
- The orchestrator produces a final summary at `.claude/reports/SUMMARY.md`
- All agents are read-only by default — they PROPOSE changes in their reports
- To apply changes, run `/project:apply` after reviewing the reports

## Important rules

- Never apply changes without an orchestrator sign-off in SUMMARY.md
- Security fixes from the security-auditor take priority over all other changes
- Simplification must not alter external API surface — flag it if it would
- The orchestrator resolves conflicts between agent recommendations

## Branch Handoff Note

- Current working branch: `video/tql-four-element-polish`
- Current dirty set was reviewed for pre-presentation stability on 2026-06-19.
- Backend `gymnasium` was intentionally bumped to `1.3.0` to support Taxi v4. RL engine verification passed via `backend/tests/test_rl_engine.py`.
- Frontend/backend connection changes are intentional for local development and iOS install behavior. Focused Flutter analyze/tests passed.
- Manim/media-path risk was investigated and reduced. Root cause was frozen derived media paths after introducing configurable concept/trace directories.
- The fix keeps explicit `CONCEPT_VIDEO_MEDIA_DIR` / `TRACE_MEDIA_DIR` overrides working, while deriving from `SHARED_MEDIA_DIR` at call time when those overrides are not explicitly configured.
- Verified after the fix:
  - `manim_service/tests/test_trace_routes.py::TestGetVideo::test_existing_file_served` passed.
  - `manim_service/tests/test_trace_renderer.py manim_service/tests/test_trace_routes.py` passed (`50 passed`).
  - Production-shaped path check still resolved to `/srv/rl-platform/animations/concept_videos/...` and `/srv/rl-platform/animations/traces/...`.
- Remaining branch work may continue, but the current set was considered commit-safe after the checks above.
