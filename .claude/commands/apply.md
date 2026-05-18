Apply changes from the audit reports, in the safe order recommended by the orchestrator.

Before applying anything, verify that .claude/reports/SUMMARY.md exists and has been
reviewed. The apply order is:

1. **Sanitization** — dead code removal (zero logic risk)
   Read .claude/reports/sanitize.md and apply each removal marked as confirmed safe.
   
2. **Security fixes** — CRITICAL and HIGH findings only
   Read .claude/reports/security.md and apply fixes for CRITICAL and HIGH severity.
   For each fix, verify the remediation by re-examining the file after the change.

3. **Best practice corrections** — non-breaking only
   Read .claude/reports/best-practices.md and apply LOW-RISK corrections only.
   Skip anything that changes a public interface.

4. **Simplification** — requires explicit user confirmation per change
   Read .claude/reports/simplify.md. For each HIGH priority item, describe the change
   to the user and ask for confirmation before applying. Never apply API-breaking
   simplifications automatically.

After applying, run any available test suite to verify nothing broke:
- npm test / yarn test
- pytest
- go test ./...
- mvn test / gradle test

If tests fail after a change, revert that change and add it to a .claude/reports/FAILED_APPLIES.md file.
