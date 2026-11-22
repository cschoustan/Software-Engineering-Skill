#!/usr/bin/env python3
"""Read-only, stdlib-only structural and checksum audit for this Skill package.

This is not a full YAML parser, formal specification validation,
security scan, or assessment of engineering performance.
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import unquote

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")
META = re.compile(r"^([a-z][a-z-]*):(?:\s|$)(.*)$")
CHECKSUM = re.compile(r"^([0-9a-f]{64})  (.+)$")
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".DS_Store"}


def _files(root):
    return sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink() and not
                  (set(p.relative_to(root).parts) & SKIP_PARTS) and p.suffix != ".pyc")


def validate(root: Path) -> list[str]:
    issues = []
    root = root.resolve()
    skill = root / "SKILL.md"
    if not skill.is_file() or skill.is_symlink():
        return [f"missing required regular file: {skill}"]
    try:
        body = skill.read_text(encoding="utf-8")
    except UnicodeError:
        return ["SKILL.md is not UTF-8"]
    if not body.startswith("---\n"):
        return ["SKILL.md requires a YAML frontmatter opening delimiter"]
    chunks = body.split("\n---\n", 1)
    if len(chunks) != 2:
        return ["SKILL.md requires a YAML frontmatter closing delimiter"]
    fields = {}
    for line in chunks[0].splitlines()[1:]:
        found = META.match(line)
        if found:
            key, value = found.groups()
            if key in fields:
                issues.append(f"duplicate top-level frontmatter key: {key}")
            fields[key] = value.strip().strip('"').strip("'")
    name = fields.get("name", "")
    if not name or not NAME.fullmatch(name) or len(name) > 64:
        issues.append("frontmatter name must be 1-64 lowercase ASCII letters/digits/hyphens")
    if name and name != root.name:
        issues.append(f"frontmatter name ({name}) must match folder ({root.name})")
    description = fields.get("description", "")
    if not description or len(description) > 1024:
        issues.append("description must be present and at most 1024 characters")
    compatibility = fields.get("compatibility", "")
    if "compatibility" in fields and (not compatibility or len(compatibility) > 500):
        issues.append("compatibility must be 1-500 characters")
    if not chunks[1].strip():
        issues.append("SKILL.md body must not be empty")
    if len(body.splitlines()) > 500:
        issues.append("SKILL.md over 500 lines; move content to references (recommended)")

    for path in root.rglob("*"):
        if path.is_symlink():
            issues.append(f"symlink not allowed in distributable package: {path.relative_to(root)}")
    for file in _files(root):
        if file.suffix != ".md":
            continue
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeError:
            issues.append(f"non UTF-8 markdown: {file.relative_to(root)}")
            continue
        for raw in LINK.findall(text):
            target = unquote(raw.split("#", 1)[0])
            if not target or target.startswith(("http://", "https://", "mailto:", "notion://")):
                continue
            linked = (file.parent / target).resolve()
            if root != linked and root not in linked.parents:
                issues.append(f"path outside skill root: {file.relative_to(root)} -> {raw}")
            elif not linked.exists():
                issues.append(f"broken local link: {file.relative_to(root)} -> {raw}")

    manifest = root / "MANIFEST.sha256"
    if manifest.is_file():
        listed = {}
        for lineno, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
            match = CHECKSUM.fullmatch(line)
            if not match:
                issues.append(f"bad manifest format on line {lineno}")
                continue
            expected, rel = match.groups()
            if rel in listed:
                issues.append(f"duplicate manifest entry: {rel}")
                continue
            listed[rel] = expected
            target = root / rel
            if not target.is_file() or target.is_symlink() or target.resolve() == manifest.resolve() or target.resolve().parent != root and root not in target.resolve().parents:
                issues.append(f"manifest references missing/unsafe file: {rel}")
            elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                issues.append(f"checksum mismatch: {rel}")
        actual = {str(p.relative_to(root)) for p in _files(root) if p != manifest}
        if set(listed) != actual:
            for item in sorted(actual - set(listed)):
                issues.append(f"file not listed in manifest: {item}")
            for item in sorted(set(listed) - actual):
                issues.append(f"manifest entry not present: {item}")
    return sorted(set(issues))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.skill_dir)
    if not root.is_dir():
        print(f"FAIL: directory not found: {root}", file=sys.stderr)
        return 2
    issues = validate(root)
    if issues:
        print("FAIL: Skill checks found issues:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: frontmatter, Markdown links, package symlinks and manifest checks ({root.resolve()})")
    print("NOTE: structural checksum audit only; not runtime proof or official spec certification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
