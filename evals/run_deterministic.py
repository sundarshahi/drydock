#!/usr/bin/env python3
"""Deterministic eval runner for the Shipyard plugin.

WHAT THIS GUARDS / WHY IT MATTERS
---------------------------------
This is the free, no-API-key CI gate. It discovers every
``evals/deterministic/test_*.py`` file, runs each as an isolated subprocess
(``python3 <file>``), collects exit codes, prints a summary table, and exits
non-zero if ANY test failed. Each deterministic test is itself a pure-stdlib
(+ optional PyYAML) module that asserts a structural invariant of the repo
(loader-resolution shape, dead-tool regression, agent/skill cross-reference,
manifest integrity, frontmatter, ...). Running them as subprocesses keeps each
test hermetic — a crash or import error in one cannot mask another.

This file is itself pure stdlib so it can run anywhere CI runs Python 3.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DETERMINISTIC_DIR = HERE / "deterministic"


def discover() -> list[Path]:
    """Return every test_*.py under evals/deterministic/, sorted by name."""
    if not DETERMINISTIC_DIR.is_dir():
        return []
    return sorted(DETERMINISTIC_DIR.glob("test_*.py"))


def run_one(path: Path) -> tuple[int, str]:
    """Run a single test file as a subprocess; return (exit_code, output)."""
    proc = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output


def main() -> int:
    tests = discover()
    if not tests:
        # A gate that guards nothing must not report green. If the dir was
        # emptied, renamed, or the test_ prefix was lost, fail loudly so the
        # suite cannot silently disable itself.
        print(f"::error::no deterministic tests found under {DETERMINISTIC_DIR}")
        return 1

    results: list[tuple[str, int, str]] = []
    for path in tests:
        code, output = run_one(path)
        results.append((path.name, code, output))

    # Stream per-test output so failures are debuggable in CI logs.
    for name, code, output in results:
        if code != 0 and output.strip():
            print(f"\n----- output: {name} -----")
            print(output.rstrip())

    width = max((len(name) for name, _, _ in results), default=0)
    print("\n=== Deterministic eval summary ===")
    failed = 0
    for name, code, _ in results:
        status = "PASS" if code == 0 else "FAIL"
        if code != 0:
            failed += 1
        print(f"  {name.ljust(width)}  {status}")

    total = len(results)
    passed = total - failed
    print(f"\n{passed}/{total} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
