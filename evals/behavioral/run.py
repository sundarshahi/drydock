#!/usr/bin/env python3
"""
Local only. Requires you to be logged into Claude Code. Spends subscription usage.
Run: python3 evals/behavioral/run.py

Behavioral routing eval CLI for Shipyard. Loads cases.yaml, drives the real
`claude -p` router (one constrained turn, no tools) for each fixture via
harness.run_route, and compares the model's chosen entry skill against the
expected one with a loose/substring match (routing is non-deterministic at
temp=1.0). Prints a table and a pass count.

This tier is INFORMATIONAL and NEVER a CI gate: it always exits 0. A failing
row is a routing signal to investigate, not a build break.

Optional args:
  --model <id>   pass a model id through to `claude`
  --timeout <s>  per-case timeout in seconds (default 180)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

# Import the harness as a sibling module regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = Path(__file__).resolve().parent / "cases.yaml"


def _picked_skill(result: harness.RouteResult) -> str:
    """Best-effort: what skill did the router land on? Prefer the ROUTE line."""
    candidates = []
    if result.route_line:
        candidates.append(result.route_line)
    candidates.extend(result.skills_invoked)
    return candidates[0] if candidates else ""


def _matches(picked: str, expect_skill: str) -> bool:
    """Loose match: the expected skill name appears in the picked route/skill."""
    return expect_skill.lower() in (picked or "").lower()


def main() -> int:
    ap = argparse.ArgumentParser(description="Shipyard behavioral routing eval")
    ap.add_argument("--model", default=None, help="model id to pass to claude")
    ap.add_argument("--timeout", type=int, default=180, help="per-case timeout (s)")
    args = ap.parse_args()

    cases = yaml.safe_load(CASES.read_text())
    if not isinstance(cases, list) or not cases:
        print(f"No cases found in {CASES}")
        return 0

    print("Local behavioral routing eval (informational; never gates).")
    print(f"Repo: {ROOT}")
    print(f"Cases: {len(cases)}\n")

    header = f"{'id':<26} {'expect':<18} {'picked':<32} {'result'}"
    print(header)
    print("-" * len(header))

    passed = 0
    plugin_error_seen = False

    for case in cases:
        cid = str(case.get("id", "?"))
        prompt = case.get("prompt", "")
        expect = str(case.get("expect_skill", ""))

        result = harness.run_route(
            prompt, repo_root=ROOT, model=args.model, timeout=args.timeout
        )

        if result.plugin_errors:
            plugin_error_seen = True

        picked = _picked_skill(result)
        ok = _matches(picked, expect)
        if ok:
            passed += 1

        status = "PASS" if ok else "FAIL"
        if result.exit_code not in (0,):
            status = f"ERR({result.exit_code})"

        print(f"{cid:<26} {expect:<18} {(picked or '-'):<32} {status}")

    print("-" * len(header))
    print(f"\nPassed {passed}/{len(cases)} routing cases.")
    if plugin_error_seen:
        print("WARNING: plugin_errors were reported by `claude` init — "
              "the plugin may not be loading cleanly.")
    print("(Behavioral tier is informational and never gates a merge.)")

    return 0  # never a gate


if __name__ == "__main__":
    sys.exit(main())
