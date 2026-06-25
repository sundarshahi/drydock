#!/usr/bin/env python3
"""verify-gate.py — independently RE-DERIVE Gate 3 metrics from ground-truth
artifacts instead of trusting the agents' self-reported receipt numbers.

WHY: each worker writes its own `metrics` into its receipt (tests_passing,
coverage_lines, ...). The production-readiness gate previously trusted those
values verbatim. A buggy or optimistic agent could report green while the real
test/coverage artifacts say otherwise. This script reads the actual artifacts
the build produced and reports DERIVED metrics next to the CLAIMED ones, so the
orchestrator can gate on ground truth and treat any mismatch as a breach.

Re-derives:
  - tests   from JUnit XML report(s)            (pytest/jest/go/surefire/... all emit this)
  - coverage from Istanbul coverage-summary.json, Cobertura coverage.xml, or lcov.info
Also verifies every receipt's claimed `artifacts` exist on disk.

Anything it cannot find a parseable artifact for is reported status="unverified"
(the orchestrator falls back to the receipt value and flags it), NOT silently
passed.

Usage:
  python3 verify-gate.py [WORKSPACE_DIR] [PROJECT_ROOT]
    WORKSPACE_DIR  default: drydock
    PROJECT_ROOT   default: .   (where tests/coverage artifacts live)

Emits a JSON verdict to stdout. Exit code is always 0 (it reports, it does not
gate — the orchestrator decides); parse the JSON.
"""

from __future__ import annotations

import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

COVERAGE_TOLERANCE_PP = 1.0  # percentage-points of slack before coverage is a "mismatch"
_PRUNE = {"node_modules", ".git", "dist", "build", ".next", "vendor", "__pycache__",
          ".venv", "venv", "target/classes", "drydock"}
_WALK_FILE_CAP = 20000  # safety cap so we never walk an enormous tree forever


def _walk_files(root):
    """Yield file paths under root, pruning heavy/irrelevant dirs, bounded."""
    seen = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _PRUNE]
        for fn in filenames:
            seen += 1
            if seen > _WALK_FILE_CAP:
                return
            yield os.path.join(dirpath, fn)


# ---------------------------------------------------------------- receipts ----
def _load_receipts(workspace):
    files = sorted(glob.glob(os.path.join(workspace, ".orchestrator", "receipts", "*.json")))
    out = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
            if isinstance(d, dict):
                out.append((os.path.basename(f), d))
        except (OSError, ValueError):
            continue
    return out


def _claimed(receipts):
    """Aggregate claimed metrics: take the max reported value per key across receipts."""
    keys = ["tests_passing", "tests_failing", "coverage_lines", "coverage_branches",
            "mutation_score", "patch_coverage"]
    claimed = {k: None for k in keys}
    for _, d in receipts:
        m = d.get("metrics")
        if not isinstance(m, dict):
            continue
        for k in keys:
            v = m.get(k)
            if isinstance(v, (int, float)):
                claimed[k] = v if claimed[k] is None else max(claimed[k], v)
    return claimed


def _missing_artifacts(receipts, project_root):
    missing = []
    checked = 0
    for name, d in receipts:
        for art in d.get("artifacts") or []:
            if not isinstance(art, str):
                continue
            checked += 1
            if not os.path.exists(os.path.join(project_root, art)):
                missing.append({"receipt": name, "path": art})
    return checked, missing


# ------------------------------------------------------------------- tests ----
def _derive_tests(project_root):
    """Find + parse JUnit XML; aggregate tests/failures/errors/skipped."""
    candidates = []
    for p in _walk_files(project_root):
        base = os.path.basename(p).lower()
        if base.endswith(".xml") and ("junit" in base or "test" in base or "surefire" in p.lower()):
            candidates.append(p)
    total = failures = errors = skipped = 0
    used = []
    for path in candidates:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        suites = [root] if root.tag == "testsuite" else root.iter("testsuite")
        matched = False
        for s in suites:
            a = s.attrib
            if "tests" not in a:
                continue
            matched = True
            total += int(float(a.get("tests", 0)))
            failures += int(float(a.get("failures", 0)))
            errors += int(float(a.get("errors", 0)))
            skipped += int(float(a.get("skipped", a.get("skip", 0)) or 0))
        if matched:
            used.append(os.path.relpath(path, project_root))
    if not used:
        return {"status": "unverified", "source": None,
                "derived_passing": None, "derived_failing": None}
    failing = failures + errors
    passing = total - failing - skipped
    return {"status": "ok", "source": used,
            "derived_passing": passing, "derived_failing": failing,
            "derived_total": total, "derived_skipped": skipped}


# ---------------------------------------------------------------- coverage ----
def _derive_coverage(project_root):
    # 1) Istanbul coverage-summary.json
    for p in _walk_files(project_root):
        if os.path.basename(p) == "coverage-summary.json":
            try:
                with open(p, encoding="utf-8") as fh:
                    pct = json.load(fh)["total"]["lines"]["pct"]
                return {"status": "ok", "source": os.path.relpath(p, project_root),
                        "derived_lines": float(pct)}
            except (OSError, ValueError, KeyError, TypeError):
                pass
    # 2) Cobertura coverage.xml (line-rate attr, 0..1)
    for p in _walk_files(project_root):
        if os.path.basename(p) in ("coverage.xml", "cobertura-coverage.xml"):
            try:
                root = ET.parse(p).getroot()
                lr = root.attrib.get("line-rate")
                if lr is not None:
                    return {"status": "ok", "source": os.path.relpath(p, project_root),
                            "derived_lines": round(float(lr) * 100, 2)}
            except (ET.ParseError, ValueError):
                pass
    # 3) lcov.info (sum LF / LH)
    for p in _walk_files(project_root):
        if os.path.basename(p) == "lcov.info":
            try:
                lf = lh = 0
                with open(p, encoding="utf-8") as fh:
                    for line in fh:
                        if line.startswith("LF:"):
                            lf += int(line[3:].strip() or 0)
                        elif line.startswith("LH:"):
                            lh += int(line[3:].strip() or 0)
                if lf > 0:
                    return {"status": "ok", "source": os.path.relpath(p, project_root),
                            "derived_lines": round(lh / lf * 100, 2)}
            except (OSError, ValueError):
                pass
    return {"status": "unverified", "source": None, "derived_lines": None}


# --------------------------------------------------------------- assemble -----
def verify(workspace, project_root):
    receipts = _load_receipts(workspace)
    claimed = _claimed(receipts)
    checked, missing = _missing_artifacts(receipts, project_root)
    t = _derive_tests(project_root)
    c = _derive_coverage(project_root)

    discrepancies = []

    # tests verdict
    tests = {"claimed_passing": claimed["tests_passing"],
             "claimed_failing": claimed["tests_failing"],
             "derived_passing": t["derived_passing"],
             "derived_failing": t["derived_failing"],
             "source": t["source"]}
    if t["status"] != "ok":
        tests["status"] = "unverified"
    else:
        ok = True
        if claimed["tests_passing"] is not None and claimed["tests_passing"] != t["derived_passing"]:
            ok = False
        if claimed["tests_failing"] is not None and claimed["tests_failing"] != t["derived_failing"]:
            ok = False
        tests["status"] = "verified" if ok else "mismatch"
        if not ok:
            discrepancies.append(
                f"tests: receipt claims {claimed['tests_passing']} pass /"
                f" {claimed['tests_failing']} fail, JUnit reports"
                f" {t['derived_passing']} pass / {t['derived_failing']} fail")

    # coverage verdict
    cov = {"claimed_lines": claimed["coverage_lines"],
           "derived_lines": c["derived_lines"], "source": c["source"]}
    if c["status"] != "ok":
        cov["status"] = "unverified"
    else:
        if (claimed["coverage_lines"] is not None and
                abs(claimed["coverage_lines"] - c["derived_lines"]) > COVERAGE_TOLERANCE_PP):
            cov["status"] = "mismatch"
            discrepancies.append(
                f"coverage: receipt claims {claimed['coverage_lines']}% lines,"
                f" artifact reports {c['derived_lines']}%")
        else:
            cov["status"] = "verified"

    for m in missing:
        discrepancies.append(f"missing artifact: {m['path']} (claimed by {m['receipt']})")

    trustworthy = (not missing
                   and tests["status"] != "mismatch"
                   and cov["status"] != "mismatch")

    return {
        "receipts": len(receipts),
        "artifacts": {"checked": checked, "missing": missing},
        "tests": tests,
        "coverage": cov,
        "discrepancies": discrepancies,
        "trustworthy": trustworthy,
    }


def main(argv):
    workspace = argv[1] if len(argv) > 1 else "drydock"
    project_root = argv[2] if len(argv) > 2 else "."
    print(json.dumps(verify(workspace, project_root), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
