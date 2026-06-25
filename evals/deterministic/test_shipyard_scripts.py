#!/usr/bin/env python3
"""Exercises the bundled orchestrator helper scripts end-to-end.

WHAT THIS GUARDS / WHY IT MATTERS
---------------------------------
The orchestrator delegates two deterministic procedures to bundled scripts
instead of re-deriving them in prose every run:
  - scripts/bootstrap-workspace.sh : scaffold Shipyard/ + deploy shared protocols
  - scripts/aggregate-cost.py       : sum effort/cost metrics across receipts

If either script silently breaks (bad path resolution, a botched copy, an
aggregation bug), the orchestrator's workspace setup or final cost summary
would be wrong with no runtime error. This runs both against throwaway fixtures
and asserts their observable behavior, so a regression fails CI for free.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "shipyard" / "scripts"
BOOTSTRAP = SCRIPTS / "bootstrap-workspace.sh"
AGGREGATE = SCRIPTS / "aggregate-cost.py"
PROTOCOLS_DIR = ROOT / "skills" / "_shared" / "protocols"


def _check_bootstrap(failures: list[str]) -> None:
    if not BOOTSTRAP.is_file():
        failures.append(f"missing script: {BOOTSTRAP.relative_to(ROOT)}")
        return
    expected = sorted(p.name for p in PROTOCOLS_DIR.glob("*.md"))
    with tempfile.TemporaryDirectory() as tmp:
        # Run with CLAUDE_* unset so the script must fall back to script-relative
        # resolution (the deployed-plugin reality), with cwd in the temp dir.
        proc = subprocess.run(
            ["/bin/bash", str(BOOTSTRAP)],
            cwd=tmp,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin"},
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            failures.append(f"bootstrap exited {proc.returncode}: {proc.stderr.strip()}")
            return
        base = Path(tmp) / "Shipyard"
        for d in (".protocols", ".orchestrator/receipts", ".orchestrator/overrides"):
            if not (base / d).is_dir():
                failures.append(f"bootstrap did not create Shipyard/{d}")
        deployed = sorted(p.name for p in (base / ".protocols").glob("*.md"))
        if deployed != expected:
            failures.append(
                f"bootstrap deployed {len(deployed)} protocols, expected "
                f"{len(expected)} (missing: {sorted(set(expected) - set(deployed))})"
            )


def _check_aggregate(failures: list[str]) -> None:
    if not AGGREGATE.is_file():
        failures.append(f"missing script: {AGGREGATE.relative_to(ROOT)}")
        return
    with tempfile.TemporaryDirectory() as tmp:
        receipts = Path(tmp) / "Shipyard" / ".orchestrator" / "receipts"
        receipts.mkdir(parents=True)
        (receipts / "T1.json").write_text(json.dumps(
            {"effort": {"tool_calls": 10, "files_read": 5, "files_written": 3},
             "artifacts": ["a.md", "b.md"]}))
        (receipts / "T2.json").write_text(json.dumps(
            {"effort": {"tool_calls": 7, "files_read": 2, "files_written": 4},
             "artifacts": ["b.md", "c.md"]}))  # b.md duplicates T1 -> dedup to 3
        (receipts / "T3.json").write_text("not valid json")  # must be ignored
        (Path(tmp) / "Shipyard" / ".orchestrator" / "rework-log.md").write_text(
            "## Gate 2 — Rework 1\n## Gate 3 — Rework 1\n")

        proc = subprocess.run(
            [sys.executable, str(AGGREGATE), str(Path(tmp) / "Shipyard")],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            failures.append(f"aggregate exited {proc.returncode}: {proc.stderr.strip()}")
            return
        try:
            got = json.loads(proc.stdout)
        except ValueError:
            failures.append(f"aggregate did not emit JSON: {proc.stdout[:120]!r}")
            return
        expected = {
            "agents": 3, "tool_calls": 17, "files_read": 7, "files_written": 7,
            "files_total": 14, "unique_artifacts": 3, "rework_cycles": 2,
        }
        for k, v in expected.items():
            if got.get(k) != v:
                failures.append(f"aggregate {k}={got.get(k)!r}, expected {v}")


def run() -> list[str]:
    failures: list[str] = []
    _check_bootstrap(failures)
    _check_aggregate(failures)
    return failures


if __name__ == "__main__":
    results = run()
    if not results:
        print(f"PASS: {Path(__file__).name}")
        sys.exit(0)
    for f in results:
        print(f"FAIL: {f}")
    sys.exit(1)
