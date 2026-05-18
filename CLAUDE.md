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
