#!/usr/bin/env python3
"""Guard against regressing to nonexistent ("dead") tooling.

Shipyard once referenced tools that have since been removed from the harness:
TeamCreate, TeamDelete, smart_outline, smart_search, smart_unfold. If any
skill/agent prose starts *calling* these again (or treats them as live), the
orchestrator will silently emit instructions the runtime cannot honor — a
class of bug that is invisible in review but breaks at execution time.

This test scans every *.md under skills/ and agents/ and fails if a dead token
appears as a CALL (token immediately followed by "(") OR appears bare on a line
that carries no removal/negation marker. A bare mention is only benign when it
is BOTH (a) not a call-form AND (b) accompanied by a negation marker on the same
line — e.g. the documented "TeamCreate/TeamDelete no longer exist" note in
skills/shipyard/SKILL.md. We positively assert that benign line passes through,
so the heuristic itself is proven, not just assumed.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DEAD_TOKENS = ["TeamCreate", "TeamDelete", "smart_outline", "smart_search", "smart_unfold"]

NEGATION_MARKERS = [
    "no longer",
    "removed",
    "never",
    "not a real",
    "do not use",
    "don't use",
    "deprecated",
    "replaced",
    "instead of",
    "made-up",
    "nonexistent",
]

# The known-benign documented line we expect to slip through untouched.
BENIGN_FILE = "skills/shipyard/SKILL.md"
BENIGN_SUBSTR = "TeamCreate/TeamDelete no longer exist"


def _has_negation(line: str) -> bool:
    low = line.lower()
    return any(marker in low for marker in NEGATION_MARKERS)


def _line_violations(line: str):
    """Return the list of dead tokens that make this line a violation."""
    bad = []
    negated = _has_negation(line)
    for token in DEAD_TOKENS:
        if token not in line:
            continue
        # Call-form: token followed by optional whitespace then "(".
        is_call = re.search(re.escape(token) + r"\s*\(", line) is not None
        # A match is benign ONLY if it is not a call AND a negation marker is present.
        benign = (not is_call) and negated
        if not benign:
            bad.append(token)
    return bad


def _iter_md_files():
    for base in ("skills", "agents"):
        root = ROOT / base
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.md")):
            yield path


def run() -> list[str]:
    failures: list[str] = []

    # --- Positive self-check: the documented benign line must NOT be flagged. ---
    benign_path = ROOT / BENIGN_FILE
    if not benign_path.is_file():
        failures.append(f"benign anchor file missing: {BENIGN_FILE}")
    else:
        benign_lines = [
            ln
            for ln in benign_path.read_text(encoding="utf-8").splitlines()
            if BENIGN_SUBSTR in ln
        ]
        if not benign_lines:
            failures.append(
                f"expected benign marker {BENIGN_SUBSTR!r} not found in {BENIGN_FILE} "
                "(anchor moved? update this test)"
            )
        for ln in benign_lines:
            flagged = _line_violations(ln)
            if flagged:
                failures.append(
                    "benign-detection regression: documented line flagged dead tokens "
                    f"{flagged} despite negation marker -> {ln.strip()!r}"
                )

    # --- Scan all markdown for real violations. ---
    for path in _iter_md_files():
        rel = path.relative_to(ROOT).as_posix()
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            bad = _line_violations(line)
            if bad:
                failures.append(
                    f"{rel}:{i} dead tool(s) {bad} used as live reference -> {line.strip()!r}"
                )

    return failures


if __name__ == "__main__":
    fails = run()
    if not fails:
        print(f"PASS: {Path(__file__).relative_to(ROOT).as_posix()}")
        sys.exit(0)
    for f in fails:
        print(f"FAIL: {f}")
    sys.exit(1)
