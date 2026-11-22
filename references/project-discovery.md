# Project Discovery

Inspect only what the task requires. Prefer current source files and installed versions to examples from another project.

## Initial inspection

1. Identify the repository root, branch, commit, and working-tree changes.
2. Read local instructions, README, package manifests, lockfiles, build configuration, CI workflows, and neighboring implementations.
3. Locate the entry point, domain boundaries, public interfaces, persistent state, background jobs, and external dependencies.
4. Determine the supported run, test, lint, type-check, and build commands by reading their definitions. Do not blindly execute scripts from an untrusted checkout.
5. Find relevant current tests and earlier changes. Record known failures before modifying code.
6. For multi-package repositories, identify dependency direction and which consumers must be checked.

## Project brief

- **Runtime and versions:** facts supported by manifests or installed tools.
- **Entrypoints:** user-visible surfaces and the affected modules.
- **Data and trust boundaries:** where input enters and state changes.
- **Verification commands:** exact command definitions and prerequisites.
- **Existing changes:** dirty files or concurrent contributors.
- **Unknowns:** environment details or access not confirmed.

Use `python scripts/inspect_project.py /path/to/repository` for a read-only inventory. It does not establish runtime behavior or validate script safety.
