#!/usr/bin/env python3
"""Every in-plugin file a SKILL.md points at must actually exist on disk.

WHAT THIS GUARDS / WHY IT MATTERS
---------------------------------
Skills dispatch sub-tasks and load detail by referencing sibling files via
`${CLAUDE_PLUGIN_ROOT}/skills/<skill>/(phases|reference|scripts)/<file>` or
`${CLAUDE_SKILL_DIR}/(phases|reference|scripts)/<file>`. If a referenced file
was renamed, moved, or never created, the reference dangles silently: the agent
is told to "follow <file>" and reads nothing, degrading the run with no error.

`test_loader_resolution.py` only validates the `_shared/protocols` loader lines,
so a dangling `phases/`/`reference/`/`scripts/` reference slips through. This
test closes that gap: it scans every Markdown file under `skills/` for those
references and asserts each target exists.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"

# Subdirs that hold real, resolvable in-plugin files referenced by skills.
_SUBDIRS = r"(?:phases|reference|scripts)"
_FILE = r"[\w./-]+?\.(?:md|sh|py|json|ya?ml)"

# ${CLAUDE_PLUGIN_ROOT}/skills/<skill>/<subdir>/<file>
_PLUGIN_ROOT_RE = re.compile(
    r"CLAUDE_PLUGIN_ROOT\}/skills/([\w-]+)/(" + _SUBDIRS + r")/(" + _FILE + r")"
)
# ${CLAUDE_SKILL_DIR}/<subdir>/<file>  (resolved relative to the scanned skill)
_SKILL_DIR_RE = re.compile(
    r"CLAUDE_SKILL_DIR\}/(" + _SUBDIRS + r")/(" + _FILE + r")"
)


def _skill_root_of(md_file: Path) -> Path:
    """The skills/<skill> directory that owns a given markdown file."""
    rel = md_file.relative_to(SKILLS)
    return SKILLS / rel.parts[0]


def run() -> list[str]:
    failures: list[str] = []
    if not SKILLS.is_dir():
        return [f"skills/ directory not found at {SKILLS}"]

    for md in sorted(SKILLS.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        rel_md = md.relative_to(ROOT)

        for skill, subdir, fname in _PLUGIN_ROOT_RE.findall(text):
            target = SKILLS / skill / subdir / fname
            if not target.is_file():
                failures.append(
                    f"{rel_md}: references ${{CLAUDE_PLUGIN_ROOT}}/skills/"
                    f"{skill}/{subdir}/{fname} but that file does not exist"
                )

        skill_root = _skill_root_of(md)
        for subdir, fname in _SKILL_DIR_RE.findall(text):
            target = skill_root / subdir / fname
            if not target.is_file():
                failures.append(
                    f"{rel_md}: references ${{CLAUDE_SKILL_DIR}}/{subdir}/{fname} "
                    f"but {target.relative_to(ROOT)} does not exist"
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
