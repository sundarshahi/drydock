#!/usr/bin/env python3
"""Guards the protocol-loader mechanism (wrapper-script form).

Every worker SKILL.md pulls shared protocols at load time. Loaders are SINGLE
commands that invoke a bundled helper script, e.g.:

    !`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" grounding-protocol`

The helper does the three-path fallback (PLUGIN_ROOT -> script-relative ->
drydock/.protocols) INTERNALLY. This shape exists because the previous inline
form chained `cat ... || cat ... || cat ... || true`, and Claude Code's
permission checker rejects any `!` loader containing a compound operator
(`||`/`&&`/`;`/`|`) as "multiple operations", hard-failing skill load. So this
test asserts BOTH that protocols still resolve AND that no loader ever
reintroduces a compound operator.

Config/dir loaders use a sibling helper:

    !`bash "${CLAUDE_SKILL_DIR}/../_shared/load-file.sh" drydock/.orchestrator/settings.md`

Assertions:
  (a) all 14 canonical protocol files exist (source of truth), and the
      canonical list does not drift from the directory;
  (b) every protocol named by a load-protocol.sh loader resolves to a real
      file (no dangling refs -> would silently load EMPTY);
  (b2) no `!` loader line in any skill .md contains a compound shell operator
      (the exact permission-checker regression this whole change fixes);
  (c) load-protocol.sh resolves correctly under each real scenario
      (PLUGIN_ROOT hit, script-relative hit, drydock/.protocols hit,
      cold-start empty) and refuses path traversal; and
  (d) load-file.sh cats a file, lists a directory, degrades to empty for a
      missing path, and refuses absolute / parent-traversal paths.
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
SHARED = ROOT / "skills" / "_shared"
PROTOCOLS_DIR = SHARED / "protocols"
LOAD_PROTOCOL = SHARED / "load-protocol.sh"
LOAD_FILE = SHARED / "load-file.sh"

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

SAMPLE = "grounding-protocol"  # stem (no .md) used for live resolution scenarios

# Names a load-protocol.sh loader passes as its single argument.
PROTOCOL_REF_RE = re.compile(r'load-protocol\.sh"\s+([A-Za-z0-9._-]+)`')
# Any `!` inline-bash loader line (skill preprocessing directive).
LOADER_LINE_RE = re.compile(r"^\s*!`")
# Compound shell operators the permission checker decomposes on.
COMPOUND_RE = re.compile(r"\|\||&&|;|(?<![0-9])\|(?!\|)")


def _run(script: Path, arg: str, env_overrides: dict, cwd: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items()}
    for key, val in env_overrides.items():
        if val is None:
            env.pop(key, None)
        else:
            env[key] = val
    return subprocess.run(
        ["bash", str(script), arg],
        env=env,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def run() -> list[str]:
    failures: list[str] = []

    # --- helper scripts must exist and be executable -----------------------
    for s in (LOAD_PROTOCOL, LOAD_FILE):
        if not s.is_file():
            failures.append(f"(0) missing helper script: {s.relative_to(ROOT)}")

    # (a) Source of truth: all 14 canonical files exist; dir must not drift.
    for name in EXPECTED_PROTOCOLS:
        if not (PROTOCOLS_DIR / name).is_file():
            failures.append(f"(a) missing canonical protocol file: skills/_shared/protocols/{name}")
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

    # (b) No dangling refs + (b2) no compound operators in ANY loader line.
    skill_mds = sorted((ROOT / "skills").rglob("*.md"))
    if not skill_mds:
        failures.append("(b) found no skills/**/*.md files to scan")
    saw_loader = False
    for md in skill_mds:
        rel = md.relative_to(ROOT)
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if not LOADER_LINE_RE.match(line):
                continue
            saw_loader = True
            # (b2) the regression guard: loaders must be single commands.
            if COMPOUND_RE.search(line):
                failures.append(
                    f"(b2) compound operator in loader {rel}:{lineno} -- the "
                    f"permission checker rejects this as multiple operations: {line.strip()}"
                )
            # (b) every load-protocol.sh ref must resolve to a real file.
            for name in PROTOCOL_REF_RE.findall(line):
                stem = name[:-3] if name.endswith(".md") else name
                if not (PROTOCOLS_DIR / f"{stem}.md").is_file():
                    failures.append(
                        f"(b) dangling protocol ref in {rel}:{lineno}: '{name}' "
                        "has no file in skills/_shared/protocols/ (loads EMPTY)"
                    )
    if not saw_loader:
        failures.append("(b) scanned skills but found no `!` loader lines at all")

    if not LOAD_PROTOCOL.is_file():
        return failures  # (c)/(d) cannot run without the scripts

    real = (PROTOCOLS_DIR / f"{SAMPLE}.md").read_text(encoding="utf-8")

    # (c1) CLAUDE_PLUGIN_ROOT set -> candidate 1.
    with tempfile.TemporaryDirectory() as tmp:
        out = _run(LOAD_PROTOCOL, SAMPLE, {"CLAUDE_PLUGIN_ROOT": str(ROOT)}, cwd=tmp)
        if out.stdout != real:
            failures.append(f"(c1) PLUGIN_ROOT scenario got {len(out.stdout)}B, expected {len(real)}B")

    # (c2) PLUGIN_ROOT unset -> script-relative candidate (always in-plugin).
    with tempfile.TemporaryDirectory() as tmp:
        out = _run(LOAD_PROTOCOL, SAMPLE, {"CLAUDE_PLUGIN_ROOT": None}, cwd=tmp)
        if out.stdout != real:
            failures.append(f"(c2) script-relative scenario got {len(out.stdout)}B, expected {len(real)}B")

    # (c3) script copied somewhere WITHOUT a protocols/ sibling; cwd holds
    #      drydock/.protocols/<sample> -> candidate 3 (runtime path) hit.
    sentinel = "SENTINEL-DRYDOCK-PROTOCOLS-FALLBACK\n"
    with tempfile.TemporaryDirectory() as tmp3:
        lone = Path(tmp3) / "lone-load-protocol.sh"
        lone.write_text(LOAD_PROTOCOL.read_text(encoding="utf-8"), encoding="utf-8")
        proto = Path(tmp3) / "cwd" / "drydock" / ".protocols"
        proto.mkdir(parents=True)
        (proto / f"{SAMPLE}.md").write_text(sentinel, encoding="utf-8")
        out = _run(lone, SAMPLE, {"CLAUDE_PLUGIN_ROOT": None}, cwd=str(Path(tmp3) / "cwd"))
        if out.stdout != sentinel:
            failures.append(f"(c3) drydock/.protocols fallback got {out.stdout!r}, expected sentinel")

    # (c4) cold start: no PLUGIN_ROOT, no sibling protocols/, no runtime copy.
    with tempfile.TemporaryDirectory() as tmp4:
        lone = Path(tmp4) / "lone-load-protocol.sh"
        lone.write_text(LOAD_PROTOCOL.read_text(encoding="utf-8"), encoding="utf-8")
        out = _run(lone, SAMPLE, {"CLAUDE_PLUGIN_ROOT": None}, cwd=tmp4)
        if out.stdout != "" or out.returncode != 0:
            failures.append(f"(c4) cold start expected empty+exit0, got {out.stdout!r} rc={out.returncode}")

    # (c5) path-traversal / bad slug -> empty, exit 0 (no arbitrary read).
    with tempfile.TemporaryDirectory() as tmp5:
        for bad in ("../../../etc/passwd", "a/b", "Foo", ""):
            out = _run(LOAD_PROTOCOL, bad, {"CLAUDE_PLUGIN_ROOT": str(ROOT)}, cwd=tmp5)
            if out.stdout != "" or out.returncode != 0:
                failures.append(f"(c5) bad slug {bad!r} should be empty+exit0, got {out.stdout!r}")

    # (d) load-file.sh: cat file / ls dir / empty-missing / reject abs & traversal.
    if LOAD_FILE.is_file():
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / "f.txt").write_text("hello\n", encoding="utf-8")
            (cwd / "d").mkdir()
            (cwd / "d" / "x").write_text("x", encoding="utf-8")
            checks = [
                ("f.txt", "hello\n", "cat file"),
                ("d", "x\n", "ls dir"),
                ("missing.txt", "", "missing -> empty"),
                ("/etc/passwd", "", "absolute -> rejected"),
                ("d/../f.txt", "", "traversal -> rejected"),
            ]
            for arg, expect, label in checks:
                out = _run(LOAD_FILE, arg, {}, cwd=str(cwd))
                if out.stdout != expect or out.returncode != 0:
                    failures.append(
                        f"(d) load-file.sh {label}: arg={arg!r} got {out.stdout!r} "
                        f"rc={out.returncode}, expected {expect!r}"
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
