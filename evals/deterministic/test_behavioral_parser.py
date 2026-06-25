#!/usr/bin/env python3
"""Runs the behavioral NDJSON parser's self-test under the deterministic gate.

WHAT THIS GUARDS / WHY IT MATTERS
---------------------------------
The behavioral tier as a whole is local-only — driving the live router via
``claude -p`` spends subscription usage and is non-deterministic, so it never
runs in CI. But its ``stream-json`` PARSER (``parse_stream_json``) is a pure,
deterministic function. If the parser silently broke, every local behavioral
run would mis-report which skill the router picked — a quiet failure of the
only tool we have for catching routing drift.

Guarding the parser here means a parser regression is caught for FREE on every
PR (no API key, no model call), even though the live routing run itself does
not execute in CI. This simply re-runs the harness's own parser self-test.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evals" / "behavioral"))

import harness  # noqa: E402  (resolved via the sys.path insert above)


def run() -> list[str]:
    return [f"behavioral parser self-test: {f}" for f in harness._self_test()]


if __name__ == "__main__":
    results = run()
    if not results:
        print(f"PASS: {Path(__file__).name}")
        sys.exit(0)
    for f in results:
        print(f"FAIL: {f}")
    sys.exit(1)
