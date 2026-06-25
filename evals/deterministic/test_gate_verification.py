#!/usr/bin/env python3
"""Exercises verify-gate.py — the Gate 3 ground-truth re-derivation script.

WHAT THIS GUARDS / WHY IT MATTERS
---------------------------------
verify-gate.py is the orchestrator's defense against trusting an agent's
self-reported gate metrics. It re-derives tests (JUnit XML) and coverage
(Istanbul/Cobertura/lcov) from the real build artifacts and flags any receipt
whose claimed numbers contradict ground truth. If this script regressed (e.g.
stopped parsing JUnit, or stopped flagging a mismatch), the production-readiness
gate would silently go back to trusting whatever the agent wrote — exactly the
hole this feature closes. This drives it against fixtures and asserts it both
CONFIRMS a truthful receipt and CATCHES a lying one.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "drydock" / "scripts" / "verify-gate.py"

_JUNIT = '<testsuite name="all" tests="10" failures="1" errors="0" skipped="1"></testsuite>\n'
_COV = '{"total":{"lines":{"pct":82.5},"branches":{"pct":75.0}}}'


def _fixture(tmp: Path, receipt_metrics: dict, artifacts: list[str]) -> None:
    (tmp / "test-results").mkdir(parents=True, exist_ok=True)
    (tmp / "coverage").mkdir(parents=True, exist_ok=True)
    (tmp / "services" / "api").mkdir(parents=True, exist_ok=True)
    (tmp / "test-results" / "junit.xml").write_text(_JUNIT)
    (tmp / "coverage" / "coverage-summary.json").write_text(_COV)
    (tmp / "services" / "api" / "foo.txt").write_text("ok")
    rdir = tmp / "drydock" / ".orchestrator" / "receipts"
    rdir.mkdir(parents=True, exist_ok=True)
    (rdir / "Tqa.json").write_text(json.dumps(
        {"metrics": receipt_metrics, "artifacts": artifacts}))


def _run(tmp: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp / "drydock"), str(tmp)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"verify-gate exited {proc.returncode}: {proc.stderr}")
    return json.loads(proc.stdout)


def run() -> list[str]:
    failures: list[str] = []
    if not SCRIPT.is_file():
        return [f"missing script: {SCRIPT.relative_to(ROOT)}"]

    # Ground truth from fixtures: 8 passing, 1 failing, 82.5% lines.
    # CASE A — truthful receipt → verified + trustworthy.
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        _fixture(tmp, {"tests_passing": 8, "tests_failing": 1, "coverage_lines": 82.5},
                 ["services/api/foo.txt"])
        r = _run(tmp)
        if r["tests"]["status"] != "verified":
            failures.append(f"A: tests status {r['tests']['status']!r}, expected verified")
        if r["tests"]["derived_passing"] != 8 or r["tests"]["derived_failing"] != 1:
            failures.append(f"A: derived tests {r['tests']['derived_passing']}/"
                            f"{r['tests']['derived_failing']}, expected 8/1")
        if r["coverage"]["status"] != "verified":
            failures.append(f"A: coverage status {r['coverage']['status']!r}, expected verified")
        if not r["trustworthy"]:
            failures.append("A: expected trustworthy=True for a truthful receipt")

    # CASE B — lying receipt (10/0, 95%) + a missing artifact → both mismatch, not trustworthy.
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        _fixture(tmp, {"tests_passing": 10, "tests_failing": 0, "coverage_lines": 95.0},
                 ["services/api/foo.txt", "services/api/missing.txt"])
        r = _run(tmp)
        if r["tests"]["status"] != "mismatch":
            failures.append(f"B: tests status {r['tests']['status']!r}, expected mismatch")
        if r["coverage"]["status"] != "mismatch":
            failures.append(f"B: coverage status {r['coverage']['status']!r}, expected mismatch")
        if not any(m["path"] == "services/api/missing.txt" for m in r["artifacts"]["missing"]):
            failures.append("B: expected the missing artifact to be flagged")
        if r["trustworthy"]:
            failures.append("B: expected trustworthy=False for a lying receipt")

    # CASE C — no artifacts at all → unverified (must NOT claim verified).
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        rdir = tmp / "drydock" / ".orchestrator" / "receipts"
        rdir.mkdir(parents=True)
        (rdir / "Tqa.json").write_text(json.dumps({"metrics": {"tests_passing": 5}}))
        r = _run(tmp)
        if r["tests"]["status"] != "unverified":
            failures.append(f"C: tests status {r['tests']['status']!r}, expected unverified")
        if r["coverage"]["status"] != "unverified":
            failures.append(f"C: coverage status {r['coverage']['status']!r}, expected unverified")

    return failures


if __name__ == "__main__":
    results = run()
    if not results:
        print(f"PASS: {Path(__file__).name}")
        sys.exit(0)
    for f in results:
        print(f"FAIL: {f}")
    sys.exit(1)
