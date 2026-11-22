"""Standard-library tests of the packaged read-only helper tools."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_skill = load("validate_skill", ROOT / "scripts" / "validate_skill.py")
inspect_project = load("inspect_project", ROOT / "scripts" / "inspect_project.py")


class ValidateSkillTests(unittest.TestCase):
    def test_packaged_skill_passes(self):
        self.assertEqual(validate_skill.validate(ROOT), [])

    def test_broken_link_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "example-skill"
            root.mkdir()
            (root / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: Example.\n---\n[bad](missing.md)\n",
                encoding="utf-8",
            )
            self.assertTrue(any("broken local link" in x for x in validate_skill.validate(root)))

    def test_mismatched_name_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "another-skill"
            root.mkdir()
            (root / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: Example.\n---\nHello\n",
                encoding="utf-8",
            )
            self.assertTrue(any("must match folder" in x for x in validate_skill.validate(root)))


class PackageLayoutTests(unittest.TestCase):
    def test_required_entrypoint_has_nonempty_body(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertTrue(text.split("\n---\n", 1)[1].strip())

    def test_script_directory_has_validation_tools(self):
        for name in ("validate_skill.py", "inspect_project.py", "summarize_evals.py"):
            self.assertTrue((ROOT / "scripts" / name).is_file())

    def test_git_metadata_is_excluded_from_checksums(self):
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "example-skill"
            root.mkdir()
            body = "---\nname: example-skill\ndescription: Example.\n---\nHello\n"
            (root / "SKILL.md").write_text(body, encoding="utf-8")
            (root / ".git").mkdir()
            (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
            digest = hashlib.sha256((root / "SKILL.md").read_bytes()).hexdigest()
            (root / "MANIFEST.sha256").write_text(f"{digest}  SKILL.md\n", encoding="utf-8")
            self.assertEqual(validate_skill.validate(root), [])


class InspectProjectTests(unittest.TestCase):
    def test_no_scripts_executed_and_no_script_contents_leaked(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            secret = "definitely-not-to-be-printed-XYZ"
            (root / "package.json").write_text(
                json.dumps({"scripts": {"test": f"echo {secret}"}}), encoding="utf-8"
            )
            (root / "main.ts").write_text("const x = 1;", encoding="utf-8")
            result = inspect_project.inventory(root, limit=100)
            self.assertIn("package.json", result["manifests_present"])
            self.assertEqual(result["code_file_counts_by_language"]["TypeScript"], 1)
            self.assertEqual(result["verification_status"], "NOT_RUN")
            self.assertIn("npm run test [INSPECT SCRIPT BEFORE RUNNING]", result["node_script_names_only"])
            self.assertNotIn(secret, json.dumps(result))

    def test_scan_limit_is_respected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for i in range(6):
                (root / f"file{i}.py").write_text("pass", encoding="utf-8")
            result = inspect_project.inventory(root, limit=2)
            self.assertTrue(result["truncated"])
            self.assertEqual(result["files_scanned"], 2)


if __name__ == "__main__":
    unittest.main()


# Paired evaluation summaries and package hardening
summarize_evals = load("summarize_evals", ROOT / "scripts" / "summarize_evals.py")


class EvalSummaryTests(unittest.TestCase):
    def record(self, arm, status, trial=1, **extra):
        r = {"task_id": "task-a", "arm": arm, "trial": trial, "status": status}
        if status in ("PASS", "FAIL"):
            r["evidence"] = f"evidence/{arm}-{trial}.json"
        r.update(extra)
        return r

    def test_empty_template_reports_no_measurements(self):
        data = json.loads((ROOT / "evals" / "run-results.empty.json").read_text())
        result = summarize_evals.summarize(data)
        self.assertEqual(result["status"], "NO_MEASUREMENTS")
        self.assertEqual(result["paired_trials"], 0)

    def test_paired_rates_and_costs(self):
        rows = [
            self.record("baseline", "FAIL", trial=1, tokens=100, duration_seconds=10),
            self.record("skill", "PASS", trial=1, tokens=130, duration_seconds=12),
            self.record("baseline", "PASS", trial=2, tokens=200, duration_seconds=8),
            self.record("skill", "PASS", trial=2, tokens=220, duration_seconds=11),
        ]
        for r in rows:
            r["task_id"] = "task-a"
        result = summarize_evals.summarize({"runs": rows})
        self.assertEqual(result["status"], "MEASURED_SAMPLE")
        self.assertEqual(result["paired_trials"], 2)
        self.assertEqual(result["arms"]["baseline"]["pass_rate_percent"], 50.0)
        self.assertEqual(result["arms"]["skill"]["pass_rate_percent"], 100.0)
        self.assertEqual(result["pass_rate_delta_percentage_points"], 50.0)
        self.assertEqual(result["arms"]["skill"]["mean_tokens_when_reported"], 175.0)
        self.assertIn("small_sample_warning", result)

    def test_missing_and_blocked_excluded(self):
        result = summarize_evals.summarize({"runs": [
            self.record("baseline", "PASS"),
            self.record("skill", "BLOCKED"),
            self.record("baseline", "FAIL", trial=2),
        ]})
        self.assertEqual(result["status"], "NO_MEASUREMENTS")
        self.assertEqual(len(result["missing_pairs"]), 1)
        self.assertEqual(len(result["excluded_pairs"]), 1)

    def test_duplicate_fails(self):
        one = self.record("baseline", "PASS")
        with self.assertRaisesRegex(ValueError, "duplicate record"):
            summarize_evals.summarize({"runs": [one, one]})

    def test_unverified_pass_fails(self):
        with self.assertRaisesRegex(ValueError, "evidence"):
            summarize_evals.summarize({"runs": [{
                "task_id": "x", "arm": "skill", "trial": 1, "status": "PASS", "evidence": ""
            }]})

    def test_safety_violation_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "safety_violation"):
            summarize_evals.summarize({"runs": [self.record("skill", "PASS", safety_violation=True)]})

    def test_nonfinite_metrics_rejected(self):
        with self.assertRaisesRegex(ValueError, "duration_seconds"):
            summarize_evals.summarize({"runs": [self.record("baseline", "FAIL", duration_seconds=float("nan"))]})


class PackageHardeningTests(unittest.TestCase):
    def write_minimal(self, root):
        root.mkdir()
        (root / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Example.\n---\nHello\n", encoding="utf-8"
        )

    def test_duplicate_yaml_key_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "example-skill"
            self.write_minimal(root)
            (root / "SKILL.md").write_text(
                "---\nname: example-skill\nname: bogus-skill\ndescription: Example.\n---\nHello\n", encoding="utf-8"
            )
            issues = validate_skill.validate(root)
            self.assertTrue(any("duplicate" in issue for issue in issues))

    def test_manifest_digest_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "example-skill"
            self.write_minimal(root)
            (root / "MANIFEST.sha256").write_text("0" * 64 + "  SKILL.md\n", encoding="utf-8")
            issues = validate_skill.validate(root)
            self.assertTrue(any("checksum mismatch" in issue for issue in issues))

    def test_manifest_unlisted_file_detected(self):
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "example-skill"
            self.write_minimal(root)
            digest = hashlib.sha256((root / "SKILL.md").read_bytes()).hexdigest()
            (root / "MANIFEST.sha256").write_text(f"{digest}  SKILL.md\n", encoding="utf-8")
            (root / "extra.txt").write_text("added without manifest", encoding="utf-8")
            issues = validate_skill.validate(root)
            self.assertTrue(any("file not listed" in issue for issue in issues))

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "example-skill"
            self.write_minimal(root)
            (root / "linked.txt").symlink_to(root / "SKILL.md")
            issues = validate_skill.validate(root)
            self.assertTrue(any("symlink" in issue for issue in issues))
