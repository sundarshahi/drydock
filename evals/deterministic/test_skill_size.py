#!/usr/bin/env python3
"""Enforces the progressive-disclosure size budget on every SKILL.md.

WHAT THIS GUARDS / WHY IT MATTERS
---------------------------------
A skill's SKILL.md is loaded into the context window every time that skill
activates. SOTA skill-authoring keeps it small and defers heavy per-phase
detail to phases/ or reference/ files that are read ON DEMAND. Letting a
SKILL.md grow unbounded silently inflates token cost on every activation and
regresses the progressive-disclosure refactor that split the oversized skills.

This test fails if any skills/*/SKILL.md exceeds the line budget, pointing the
author at the fix (move detail into phases/ or reference/ files and reference
them from a Phase/Reference Index). The phase/reference files themselves are
intentionally EXEMPT — they ARE the deferred detail and have no budget.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Progressive-disclosure budget. The orchestrator and every worker skill must
# keep their always-loaded SKILL.md body under this; detail lives in phases/.
MAX_LINES = 500


def run() -> list[str]:
    failures: list[str] = []
    skill_mds = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skill_mds:
        return ["no skills/*/SKILL.md files found to size-check"]
    for md in skill_mds:
        n = len(md.read_text(encoding="utf-8").splitlines())
        if n > MAX_LINES:
            rel = md.relative_to(ROOT)
            failures.append(
                f"{rel} is {n} lines (budget {MAX_LINES}); defer detail to "
                "phases/ or reference/ files and link them from a Phase/Reference Index"
            )
    return failures


if __name__ == "__main__":
    results = run()
    if not results:
        print(f"PASS: {Path(__file__).name}")
        sys.exit(0)
    for f in results:
        print(f"FAIL: {f}")
    sys.exit(1)
