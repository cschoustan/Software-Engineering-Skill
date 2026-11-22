# Verification

A check proves only what it actually exercised. Separate static validity, automated behavior, actual runtime behavior, and production readiness.

## Verification plan

Map each acceptance criterion to a check:

| Criterion | Action | Expected result | Observed result | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| Example: saved setting survives reload | Change value, save, reload | Persisted value displayed | Fill after run | NOT RUN | Fill after run |

## Select meaningful checks

- **Static:** syntax, formatter, type checker, linter, schema checks.
- **Unit:** edge cases and pure logic.
- **Contract/integration:** external boundaries, database behavior, permissions, and serialization.
- **Runtime:** real browser, desktop, CLI, or HTTP entry point operated in a safe environment.
- **Operational:** restart, retry, migration, queue, and failure recovery where relevant.
- **Formal/property:** invariants and state transitions when required by risk.

## Runtime procedure

1. Start a usable isolated instance with synthetic or approved fixtures.
2. Confirm readiness, build version, authentication, data prerequisites, and owned process/port.
3. Drive the user-visible entry point with stable selectors, CLI commands, or API requests.
4. Record actions, results, server-side effects, logs, exit codes, and screenshots or traces when helpful.
5. Check negative cases and restoration after failure.
6. Stop only the processes created for the check. Preserve evidence and avoid deleting unrelated data.

A page loading successfully does not prove the full flow works. Mock results only establish the mocked boundary and must be labeled accordingly.

## Evidence rules

- Mark each check **PASS**, **FAIL**, **BLOCKED**, or **NOT RUN**.
- Never report historical test results as a fresh run.
- Record the command, environment, exit code, and observed output needed to reproduce a conclusion.
- Do not claim manual inspection, browser verification, test coverage, or benchmarks that did not happen.
- If runtime tools are unavailable, describe what was checked and which behavior remains unverified.

Use [verification report](../templates/verification-report.md) for multi-step tasks and [feature map](../templates/feature-map.md) when the project lacks a repeatable way to drive user-facing behavior.
