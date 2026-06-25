#!/usr/bin/env python3
"""Guards the first-run protocol-loader bug.

Every worker SKILL.md pulls shared protocols at load time with a
"belt-and-suspenders" shell line of the shape:

    !`cat "${CLAUDE_PLUGIN_ROOT}/skills/_shared/protocols/P.md" 2>/dev/null \
      || cat "${CLAUDE_SKILL_DIR}/../_shared/protocols/P.md" 2>/dev/null \
      || cat drydock/.protocols/P.md 2>/dev/null || true`

If a protocol file is missing, typo'd, or renamed, the loader silently
resolves to EMPTY (the `|| true` tail) and the worker boots with no
governance text -- a dangerous, invisible regression. WHY it matters:
the protocols are the only thing constraining a subagent's behavior, so
a dangling reference is a security/quality hole that no runtime error
would surface.

This test asserts three independent things:
  (a) all 14 canonical protocol files exist (source of truth),
  (b) every protocol referenced by a loader line resolves to a real
      file (no dangling refs across all skills/*/SKILL.md), and
  (c) the loader snippet itself resolves correctly under each of the
      four real fallback scenarios (PLUGIN_ROOT hit, SKILL_DIR hit,
      drydock/.protocols hit, and graceful-empty cold start).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# evals/deterministic/<this file> -> parents[2] == repo root
ROOT = Path(__file__).resolve().parents[2]
PROTOCOLS_DIR = ROOT / "skills" / "_shared" / "protocols"

# Canonical source-of-truth list (verified against the live repo).
EXPECTED_PROTOCOLS = [
    "architecture-boundaries.md",
    "boundary-safety.md",
    "compliance-protocol.md",
    "conflict-resolution.md",
    "freshness-protocol.md",
    "grounding-protocol.md",
    "input-validation.md",
    "observability-contract.md",
    "receipt-protocol.md",
    "security-defaults.md",
    "security-testing-protocol.md",
    "tool-efficiency.md",
    "ux-protocol.md",
    "visual-identity.md",
]

# Sample protocol used for the live fallback-resolution scenarios.
SAMPLE = "grounding-protocol.md"

# Matches the protocol basename inside any loader reference.
REF_RE = re.compile(r"_shared/protocols/([A-Za-z0-9._-]+\.md)")

# Every executable loader line MUST keep all three fallback paths. Dropping
# the ${CLAUDE_PLUGIN_ROOT} primary (or the ${CLAUDE_SKILL_DIR}/../ secondary)
# is exactly the first-run-empty regression this whole test exists to prevent.
REQUIRED_FALLBACKS = (
    "${CLAUDE_PLUGIN_ROOT}/skills/_shared/protocols/",
    "${CLAUDE_SKILL_DIR}/../_shared/protocols/",
    "drydock/.protocols/",
)


def _loader_snippet(stem: str) -> str:
    """Reconstruct the exact loader shell line for protocol `stem.md`."""
    return (
        f'cat "${{CLAUDE_PLUGIN_ROOT}}/skills/_shared/protocols/{stem}" 2>/dev/null '
        f'|| cat "${{CLAUDE_SKILL_DIR}}/../_shared/protocols/{stem}" 2>/dev/null '
        f"|| cat drydock/.protocols/{stem} 2>/dev/null || true"
    )


def _run_loader(stem: str, env_overrides: dict, cwd: str) -> str:
    """Execute the loader snippet under /bin/sh; return raw stdout."""
    # Start from a clean env, then apply overrides. Keys mapped to None
    # are removed so a scenario can guarantee a var is unset.
    env = {k: v for k, v in os.environ.items()}
    for key, val in env_overrides.items():
        if val is None:
            env.pop(key, None)
        else:
            env[key] = val
    proc = subprocess.run(
        ["/bin/sh", "-c", _loader_snippet(stem)],
        env=env,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def run() -> list[str]:
    failures: list[str] = []

    # (a) Source of truth: all 14 canonical files must exist.
    for name in EXPECTED_PROTOCOLS:
        if not (PROTOCOLS_DIR / name).is_file():
            failures.append(f"(a) missing canonical protocol file: skills/_shared/protocols/{name}")

    # Guard against the canonical list silently drifting from the dir.
    if PROTOCOLS_DIR.is_dir():
        on_disk = {p.name for p in PROTOCOLS_DIR.iterdir() if p.suffix == ".md"}
        extra = sorted(on_disk - set(EXPECTED_PROTOCOLS))
        if extra:
            failures.append(
                "(a) protocols dir has .md files not in EXPECTED_PROTOCOLS "
                f"(update the canonical list or the dir): {extra}"
            )
    else:
        failures.append(f"(a) protocols dir does not exist: {PROTOCOLS_DIR}")

    # (b) No dangling refs: every protocol referenced by any loader line
    #     in any skills/*/SKILL.md must resolve to a real file.
    skill_mds = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skill_mds:
        failures.append("(b) found no skills/*/SKILL.md files to scan")
    for md in skill_mds:
        text = md.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "_shared/protocols/" not in line:
                continue
            for basename in REF_RE.findall(line):
                if not (PROTOCOLS_DIR / basename).is_file():
                    rel = md.relative_to(ROOT)
                    failures.append(
                        f"(b) dangling protocol ref in {rel}: '{basename}' "
                        "has no file in skills/_shared/protocols/ "
                        "(would silently load EMPTY)"
                    )
            # (b2) Shape conformance: an EXECUTABLE loader directive (a line
            #      that starts with the skill `!`cat ...`` command form and
            #      references a shared protocol) must retain ALL THREE fallback
            #      paths. A SKILL.md that dropped the ${CLAUDE_PLUGIN_ROOT}
            #      primary would reintroduce the first-run-empty bug while still
            #      referencing a real protocol file -- so (b) alone misses it.
            #      Scoped to `!`cat`-prefixed lines so prose that merely
            #      *mentions* a loader (e.g. a doc bullet) is not mis-flagged.
            if line.lstrip().startswith("!`cat") and "2>/dev/null" in line:
                missing = [fb for fb in REQUIRED_FALLBACKS if fb not in line]
                if missing:
                    rel = md.relative_to(ROOT)
                    failures.append(
                        f"(b2) loader line in {rel} dropped fallback path(s) "
                        f"{missing} -- reintroduces the first-run-empty bug"
                    )

    # (c) Fallback resolution -- execute the real loader snippet for the
    #     sample protocol under each scenario.
    sample_path = PROTOCOLS_DIR / SAMPLE
    if not sample_path.is_file():
        # Already reported by (a); skip the live scenarios cleanly rather than
        # crashing with a traceback that hides the (a)/(b) diagnostics.
        failures.append(
            f"(c) sample protocol {SAMPLE} is missing; skipping live "
            "fallback-resolution scenarios"
        )
        return failures
    real_content = sample_path.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        # SCENARIO 1: CLAUDE_PLUGIN_ROOT set -> path-1 hit.
        out = _run_loader(
            SAMPLE,
            {"CLAUDE_PLUGIN_ROOT": str(ROOT), "CLAUDE_SKILL_DIR": None},
            cwd=tmp,
        )
        if out != real_content:
            failures.append(
                "(c1) PLUGIN_ROOT scenario did not resolve to real protocol content "
                f"(got {len(out)} bytes, expected {len(real_content)})"
            )

        # SCENARIO 2: only CLAUDE_SKILL_DIR set -> path-2 (../_shared) hit.
        skill_dir = str(ROOT / "skills" / "qa-engineer")
        out = _run_loader(
            SAMPLE,
            {"CLAUDE_PLUGIN_ROOT": None, "CLAUDE_SKILL_DIR": skill_dir},
            cwd=tmp,
        )
        if out != real_content:
            failures.append(
                "(c2) SKILL_DIR (../_shared) scenario did not resolve to real "
                f"protocol content (got {len(out)} bytes, expected {len(real_content)})"
            )

    # SCENARIO 3: both unset, cwd contains drydock/.protocols/<sample> -> path-3 hit.
    sentinel = "SENTINEL-DRYDOCK-PROTOCOLS-FALLBACK\n"
    with tempfile.TemporaryDirectory() as tmp3:
        proto_dir = Path(tmp3) / "drydock" / ".protocols"
        proto_dir.mkdir(parents=True)
        (proto_dir / SAMPLE).write_text(sentinel, encoding="utf-8")
        out = _run_loader(
            SAMPLE,
            {"CLAUDE_PLUGIN_ROOT": None, "CLAUDE_SKILL_DIR": None},
            cwd=tmp3,
        )
        if out != sentinel:
            failures.append(
                "(c3) drydock/.protocols fallback did not resolve to the sentinel "
                f"(got {out!r}, expected {sentinel!r})"
            )

    # SCENARIO 4: cold first run -- nothing set, no drydock/.protocols ->
    #             loader degrades gracefully to empty via `|| true`.
    with tempfile.TemporaryDirectory() as tmp4:
        out = _run_loader(
            SAMPLE,
            {"CLAUDE_PLUGIN_ROOT": None, "CLAUDE_SKILL_DIR": None},
            cwd=tmp4,
        )
        if out != "":
            failures.append(
                "(c4) cold-start scenario expected empty stdout (graceful degrade) "
                f"but got {out!r}"
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
