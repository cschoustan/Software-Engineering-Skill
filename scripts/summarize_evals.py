#!/usr/bin/env python3
"""Summarize human/agent-recorded paired Skill trials; no execution or judgment.

Input: JSON with 'runs' containing (task_id, arm, trial, status, evidence,
optional tokens and duration_seconds). This validates records, computes only
complete PASS/FAIL pairs, and never treats BLOCKED/NOT_RUN as success.
"""

import argparse
import json
import math
import sys
from pathlib import Path

ARMS = ("baseline", "skill")
STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}


def _average(values):
    return round(sum(values) / len(values), 2) if values else None


def summarize(data: dict) -> dict:
    if not isinstance(data, dict) or not isinstance(data.get("runs"), list):
        raise ValueError("expected JSON object containing a 'runs' list")
    seen = {}
    for index, entry in enumerate(data["runs"]):
        if not isinstance(entry, dict):
            raise ValueError(f"runs[{index}]: expected object")
        task_id = entry.get("task_id")
        trial = entry.get("trial")
        arm = entry.get("arm")
        status = entry.get("status")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError(f"runs[{index}]: nonempty task_id required")
        if not isinstance(trial, int) or isinstance(trial, bool) or trial < 1:
            raise ValueError(f"runs[{index}]: positive integer trial required")
        if arm not in ARMS or status not in STATUSES:
            raise ValueError(f"runs[{index}]: invalid arm or status")
        if status in {"PASS", "FAIL"} and not isinstance(entry.get("evidence"), str):
            raise ValueError(f"runs[{index}]: measured PASS/FAIL needs evidence path")
        if status in {"PASS", "FAIL"} and not entry["evidence"].strip():
            raise ValueError(f"runs[{index}]: empty evidence path")
        for metric in ("tokens", "duration_seconds"):
            value = entry.get(metric)
            if value is not None:
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                    raise ValueError(f"runs[{index}]: invalid nonnegative numeric {metric}")
        if entry.get("safety_violation") not in (None, True, False):
            raise ValueError(f"runs[{index}]: safety_violation must be boolean")
        if status == "PASS" and entry.get("safety_violation") is True:
            raise ValueError(f"runs[{index}]: PASS cannot also have safety_violation=true")
        key = (task_id, trial)
        slot = seen.setdefault(key, {})
        if arm in slot:
            raise ValueError(f"runs[{index}]: duplicate record for {key}/{arm}")
        slot[arm] = entry

    pairs = []
    missing = []
    excluded = []
    safety_flags = 0
    for (task_id, trial), arms in sorted(seen.items()):
        safety_flags += sum(entry.get("safety_violation", False) is True for entry in arms.values())
        if set(arms) != set(ARMS):
            missing.append({"task_id": task_id, "trial": trial, "missing_arm": next(a for a in ARMS if a not in arms)})
            continue
        if any(arms[a]["status"] not in {"PASS", "FAIL"} for a in ARMS):
            excluded.append({"task_id": task_id, "trial": trial, "reason": "BLOCKED_OR_NOT_RUN"})
            continue
        pairs.append(arms)

    if not pairs:
        return {
            "status": "NO_MEASUREMENTS", "total_run_records": len(data["runs"]),
            "paired_trials": 0, "missing_pairs": missing,
            "excluded_pairs": excluded, "safety_violation_records": safety_flags,
            "note": "No complete executable PASS/FAIL paired trials; effectiveness is UNVERIFIED."
        }

    result = {"status": "MEASURED_SAMPLE", "total_run_records": len(data["runs"]), "paired_trials": len(pairs),
              "missing_pairs": missing, "excluded_pairs": excluded, "safety_violation_records": safety_flags,
              "arms": {}}
    for arm in ARMS:
        records = [pair[arm] for pair in pairs]
        token_numbers = [r["tokens"] for r in records if r.get("tokens") is not None]
        duration_numbers = [r["duration_seconds"] for r in records if r.get("duration_seconds") is not None]
        result["arms"][arm] = {
            "pass": sum(r["status"] == "PASS" for r in records),
            "fail": sum(r["status"] == "FAIL" for r in records),
            "pass_rate_percent": round(100 * sum(r["status"] == "PASS" for r in records) / len(records), 2),
            "mean_tokens_when_reported": _average(token_numbers),
            "token_observations": len(token_numbers),
            "mean_seconds_when_reported": _average(duration_numbers),
            "duration_observations": len(duration_numbers),
        }
    result["pass_rate_delta_percentage_points"] = round(result["arms"]["skill"]["pass_rate_percent"] - result["arms"]["baseline"]["pass_rate_percent"], 2)
    result["note"] = "Descriptive sample only; not a significance test. Review evidence paths and matched environments manually."
    if len(pairs) < 5:
        result["small_sample_warning"] = "Fewer than five paired trials: do not claim generalized improvement."
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", help="JSON of recorded paired trial outcomes")
    args = parser.parse_args()
    try:
        dataset = json.loads(Path(args.results).read_text(encoding="utf-8"))
        result = summarize(dataset)
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
