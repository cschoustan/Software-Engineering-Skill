# Maintaining Engineering Rules

Review recurring defects, failed builds, code review comments, and verified operational incidents. Use only records the task authorizes; avoid unrelated private content.

## Improvement loop

1. Group repeated observations by failure mechanism rather than wording.
2. Find the cause in interface design, state ownership, type coverage, static checking, tests, runtime verification, or project instructions.
3. Choose the earliest practical preventive layer: architecture, types, lint/CI, behavioral test, then documentation for judgment calls.
4. Add a failing example that proves the safeguard rejects the known mistake, plus a valid example that passes.
5. Apply the change in small increments, measure false positives, and document migration or exceptions.
6. Retire obsolete instructions once a stronger, maintained control replaces them.

Do not create new rules for isolated incidents without considering frequency, severity, and cost. A single severe security or data-loss issue may warrant immediate enforcement.

Use [guardrail change](../templates/guardrail-change.md).
