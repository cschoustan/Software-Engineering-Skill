#!/usr/bin/env python3
"""Read-only inventory of a repository's tools and likely verification entry points.

Does not execute any package manager, test script, build, install, or network call.
Does not print environment variables, file contents, secrets, or package scripts.
Treat the output as candidate evidence, not as a successful project audit.
"""

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

SKIP_DIRS = {
    ".git", ".hg", "node_modules", ".venv", "venv", "__pycache__",
    ".next", ".nuxt", "dist", "build", "target", "coverage", ".tox",
    ".cache", ".mypy_cache", ".pytest_cache", "vendor",
}
LANGUAGES = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript/TSX",
    ".js": "JavaScript", ".jsx": "JavaScript/JSX", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".kt": "Kotlin",
    ".cs": "C#", ".cpp": "C++", ".cc": "C++", ".c": "C",
    ".swift": "Swift", ".dart": "Dart", ".sql": "SQL",
}
MANIFESTS = [
    "package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json",
    "pyproject.toml", "requirements.txt", "uv.lock", "poetry.lock",
    "go.mod", "Cargo.toml", "Cargo.lock", "pom.xml", "build.gradle",
    "build.gradle.kts", "Gemfile", "composer.json", "Makefile",
    "justfile", "Dockerfile", "AGENTS.md",
]


def inventory(root: Path, limit: int) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    ext_count = Counter()
    relevant_tests = 0
    scanned = 0
    truncated = False
    workflows = []
    for here, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not Path(here, d).is_symlink()]
        path = Path(here)
        if path == root / ".github" / "workflows":
            workflows = sorted(f for f in files if f.endswith((".yml", ".yaml")))
        for file in files:
            scanned += 1
            if scanned > limit:
                truncated = True
                break
            if file.startswith(".") or Path(here, file).is_symlink():
                continue
            suffix = Path(file).suffix.lower()
            if suffix in LANGUAGES:
                ext_count[LANGUAGES[suffix]] += 1
            if file.startswith("test_") or file.endswith((".test.ts", ".spec.ts", ".test.js", ".spec.js", "_test.go", "_test.rs")):
                relevant_tests += 1
        if truncated:
            break
    manifests = [m for m in MANIFESTS if (root / m).is_file()]
    commands = []
    package = root / "package.json"
    if package.exists() and package.stat().st_size < 1_000_000:
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
            scripts = data.get("scripts", {})
            if isinstance(scripts, dict):
                # Names only: scripts may execute malicious or destructive commands.
                commands = [f"npm run {name} [INSPECT SCRIPT BEFORE RUNNING]" for name in sorted(scripts) if isinstance(name, str)]
        except (ValueError, UnicodeError, OSError):
            pass
    return {
        "repository_path": str(root),
        "git_metadata_present": (root / ".git").exists(),
        "manifests_present": manifests,
        "code_file_counts_by_language": dict(sorted(ext_count.items())),
        "approximate_test_file_count": relevant_tests,
        "github_workflow_filenames": workflows,
        "node_script_names_only": commands,
        "files_scanned": min(scanned, limit),
        "truncated": truncated,
        "verification_status": "NOT_RUN",
        "warning": "Read-only inventory: no code, tests, builds, security checks or external calls were executed. Review script definitions before any execution.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".", help="Repository root path")
    parser.add_argument("--max-files", type=int, default=10000, help="Max paths to scan (default 10000)")
    args = parser.parse_args()
    if args.max_files < 1:
        parser.error("--max-files must be positive")
    try:
        data = inventory(Path(args.repo), args.max_files)
    except (ValueError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
