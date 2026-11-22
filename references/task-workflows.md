# Task Workflows

Use the procedure that matches the request. Do not apply every workflow to every change.

## Investigate

1. Identify the requested behavior and relevant files.
2. Trace callers, dependencies, state changes, tests, and relevant history.
3. Distinguish direct observations from inference; cite file paths and lines where possible.
4. Do not edit the repository for a read-only request.

## Fix a defect

1. Capture the reported symptom and exact steps to reproduce.
2. Compare expected and observed behavior, environment, and recent changes.
3. Trace inputs and outputs through boundaries to find the first incorrect state.
4. Add a regression that fails on the original behavior where practical.
5. Change the narrowest cause, not just a visible symptom.
6. Execute the regression and relevant surrounding tests, then repeat the original user scenario.
7. If the fix fails, revisit the hypothesis. Do not stack speculative patches.

## Build a feature

1. Define user-visible acceptance criteria, non-goals, and edge cases.
2. Model data shape, lifecycle, ownership, permissions, and API/CLI/UI contracts.
3. Make an implementation plan that can be tested in small increments.
4. Write tests at useful boundaries and implement the feature.
5. Run the actual user path including loading, errors, and denied or empty states when relevant.
6. Review compatibility, performance, security, and failure recovery.

## Refactor

1. Freeze the current observable contract and tests.
2. Identify the coupling, duplication, or complexity being removed.
3. Migrate callers in independently testable steps.
4. Run parity and integration checks; inspect final diff for unintended behavior changes.
5. Remove legacy interfaces only after consumers are confirmed migrated.

## Performance

1. Choose a representative workload and success measure.
2. Record the baseline, environment, sample size, and bottleneck evidence.
3. Change one meaningful cause at a time.
4. Repeat the same workload and verify correctness, resource usage, and variance.
5. Report raw values and units. Do not claim a speedup without comparable measurements.

## Code review

1. Read the intended behavior, diff, neighboring code, and applicable project rules.
2. Examine correctness, security, data integrity, permissions, concurrency, compatibility, tests, and operational safety.
3. Reproduce suspected failures where practical; distinguish proven failures from risks and suggestions.
4. Report file and line, severity, observable impact, and reproduction or supporting evidence.
5. Avoid unrelated style complaints and unsubstantiated certainty.

## Release preparation

1. Inspect release scope, branch state, build configuration, environment and approval policy.
2. Run required tests, static checks, reproducible builds, and relevant runtime verification.
3. Confirm migration order, feature flags, monitoring, and rollback/compensation procedures.
4. Verify versioned artifacts and secrets are handled appropriately.
5. Report readiness and unresolved checks. Do not merge, deploy, or announce release without authorization.
