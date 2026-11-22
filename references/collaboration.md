# Collaboration and Review

## Shared work

Before dividing a task, identify which files, state, branches, services, ports, and test data may be shared. Prefer separate worktrees and test environments where the project supports them.

Assign clear ownership. Do not let multiple workers change the same branch or mutable state without coordination. Integrate only after inspecting combined diffs and rerunning affected checks.

## Independent review

A review finding should state: observed behavior, expected behavior, affected file or boundary, severity, and a reproducible command or other supporting evidence. A plausible concern is a risk to investigate, not a proven defect.

A second implementation or reviewer can help with difficult decisions, but additional workers are not a substitute for one verified end-to-end path.

## Handoff

Record intent, changed files, important decisions, checks run and results, unresolved problems, ownership, and the next reproducible action. Prefer a short actionable handoff over a chronological transcript.

See [review findings](../templates/review-findings.md) and [handoff](../templates/handoff.md).
