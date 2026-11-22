# Software Engineering Skill

A reusable workflow for repository-based software development, debugging, refactoring, testing, review, and release preparation.

The Skill is language- and framework-independent. It uses repository instructions and installed dependency versions rather than a predefined stack. It emphasizes narrow changes, executable verification, and explicit reporting of unfinished checks.

## Scope

| Work | Default approach |
| --- | --- |
| Bug fix | Reproduce, identify the cause, add a regression check, repair, verify. |
| Feature | Define observable behavior and data contracts, implement, check the complete user path. |
| Refactor | Record current behavior and preserve compatibility unless a breaking change is approved. |
| Performance | Measure a representative baseline and compare equivalent workloads. |
| API or database update | Check consumers, rollout order, backfill, rollback, and data integrity. |
| Code review | Report concrete, relevant findings with supporting evidence. |
| Release preparation | Verify build, tests, security-sensitive changes, operational readiness, and approvals. |

The operating process has three levels: **Quick**, **Standard**, and **Critical**. Risk and reversibility determine the level.

## Installation

Copy the `software-engineering/` folder into a Skills directory supported by the development tool. Keep its directory structure intact. The Skill must include `SKILL.md`; the supporting references, templates, scripts, and tests are optional to load at runtime but should remain available on disk.

Example project layout:

```text
project/
├── src/
├── tests/
└── .agents/
    └── skills/
        └── software-engineering/
            ├── SKILL.md
            ├── references/
            ├── templates/
            ├── scripts/
            ├── tests/
            └── evals/
```

Skill discovery paths and invocation methods differ between development tools. Consult the current documentation for the installed tool before changing its configuration.

## Usage

Example task:

> Fix the settings form so saved values persist after a reload. Inspect the existing implementation, reproduce the failure, make a focused change, and run the applicable tests. Report the executed checks and any remaining limits.

For a larger change:

> Add the requested account settings API. Identify the existing data model, callers, authorization boundary, compatibility requirements, and error behavior. Define acceptance cases before implementation. Verify both successful requests and permission failures.

## Files

```text
software-engineering/
├── SKILL.md
├── README.md
├── MANIFEST.sha256
├── references/
│   ├── project-discovery.md
│   ├── operating-modes.md
│   ├── engineering-standards.md
│   ├── task-workflows.md
│   ├── verification.md
│   ├── changes-and-migrations.md
│   ├── security.md
│   ├── collaboration.md
│   ├── maintenance.md
│   └── evaluation.md
├── templates/
├── scripts/
├── tests/
└── evals/
```

## Local validation

The helper scripts use the Python standard library. Run these commands from the Skill directory:

```bash
python scripts/validate_skill.py .
python -m unittest discover -s tests -v
python scripts/inspect_project.py /path/to/repository
python scripts/summarize_evals.py evals/run-results.empty.json
```

`inspect_project.py` only inventories files and command names; inspect actual project scripts before executing them. `summarize_evals.py` reports `NO_MEASUREMENTS` for the empty example until actual paired trials are supplied.

The manifest verifies package integrity against recorded checksums. It is not a digital signature. Passing these local checks does not prove that an external application is functional or that the Skill improves software development outcomes.

## Permission boundary

The Skill does not authorize deployments, production data access, merges, publishing, credential changes, or destructive actions. Those operations require the permissions and approvals of the actual project.
