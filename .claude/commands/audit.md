Use the orchestrator subagent to run the full codebase health workflow.

The orchestrator will:
1. Discover the codebase structure
2. Spawn code-reviewer, sanitizer, simplifier, and best-practices agents in parallel
3. Run security-auditor after the parallel phase completes
4. Synthesise all findings into .claude/reports/SUMMARY.md

Ensure the .claude/reports/ directory exists before starting:
mkdir -p .claude/reports

After the workflow completes, present the user with the path to SUMMARY.md and a brief
count of findings by severity.
