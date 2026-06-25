"""Guard: skill/agent frontmatter quality (stricter local mirror of the CI check).

WHY THIS MATTERS
----------------
Claude Code discovers and routes skills and subagents purely from their YAML
frontmatter. A missing or empty `name`/`description`, a description longer than
the 1024-char platform limit, or a worker skill that forgets to declare
`allowed-tools` all degrade or break routing/tool-gating silently — the plugin
still "loads" but the affected component misbehaves at runtime. This test fails
loudly at author time so those regressions never reach a release.

SCOPE
-----
For every skills/<x>/SKILL.md (15) and agents/<x>.md (11):
  (a) file starts with a `---`-delimited YAML frontmatter block that
      yaml.safe_load parses into a dict.
  (b) `name` and `description` are present, non-empty strings; len(description) <= 1024.
  (c) For the 11 WORKER skills only (skill dir name == an agent filename), the
      SKILL.md frontmatter declares a non-empty `allowed-tools` (str or list).
      The 4 main-context skills (drydock, product-manager, solution-architect,
      polymath) are intentionally exempt.

The worker set is DERIVED from disk (agent filenames), matching the same
relationship test_agent_skill_xref asserts (agent names == worker skill names).
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DESC_MAX = 1024


def _split_frontmatter(text: str):
    """Return (yaml_text, error_or_None). Requires leading '---' fence."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "does not start with a '---' YAML frontmatter fence"
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), None
    return None, "frontmatter fence is not closed by a second '---'"


def _check_common(rel: str, fm) -> list[str]:
    failures: list[str] = []
    if not isinstance(fm, dict):
        return [f"{rel}: frontmatter did not parse to a mapping/dict"]
    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        failures.append(f"{rel}: missing or empty 'name'")
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        failures.append(f"{rel}: missing or empty 'description'")
    elif len(desc) > DESC_MAX:
        failures.append(
            f"{rel}: description length {len(desc)} exceeds limit {DESC_MAX}"
        )
    return failures


def run() -> list[str]:
    failures: list[str] = []

    agents_dir = ROOT / "agents"
    skills_dir = ROOT / "skills"

    agent_files = sorted(agents_dir.glob("*.md"))
    skill_files = sorted(skills_dir.glob("*/SKILL.md"))

    # Sanity-check the corpus matches the documented ground truth so this test
    # fails if files are added/removed without updating expectations.
    if len(agent_files) != 15:
        failures.append(f"expected 15 agents/*.md, found {len(agent_files)}")
    skill_dirs = [p.parent.name for p in skill_files if p.parent.name != "_shared"]
    if len(skill_dirs) != 19:
        failures.append(
            f"expected 19 skills/*/SKILL.md (excl _shared), found {len(skill_dirs)}"
        )

    # WORKER set derived from disk: an agent filename == a worker skill name.
    worker_names = {p.stem for p in agent_files}

    # Parse + check agents.
    for path in agent_files:
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        body, err = _split_frontmatter(text)
        if err:
            failures.append(f"{rel}: {err}")
            continue
        try:
            fm = yaml.safe_load(body)
        except yaml.YAMLError as e:
            failures.append(f"{rel}: frontmatter is not valid YAML ({e})")
            continue
        failures.extend(_check_common(rel, fm))

    # Parse + check skills (and allowed-tools for workers).
    for path in skill_files:
        dir_name = path.parent.name
        if dir_name == "_shared":
            continue
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        body, err = _split_frontmatter(text)
        if err:
            failures.append(f"{rel}: {err}")
            continue
        try:
            fm = yaml.safe_load(body)
        except yaml.YAMLError as e:
            failures.append(f"{rel}: frontmatter is not valid YAML ({e})")
            continue
        failures.extend(_check_common(rel, fm))

        if isinstance(fm, dict) and dir_name in worker_names:
            tools = fm.get("allowed-tools")
            if isinstance(tools, str):
                ok = bool(tools.strip())
            elif isinstance(tools, list):
                ok = len(tools) > 0
            else:
                ok = False
            if not ok:
                failures.append(
                    f"{rel}: worker skill missing non-empty 'allowed-tools' "
                    f"(str or list)"
                )

    return failures


if __name__ == "__main__":
    import sys

    fails = run()
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        sys.exit(1)
    print(f"PASS: {Path(__file__).name}")
    sys.exit(0)
