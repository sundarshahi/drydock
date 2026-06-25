#!/usr/bin/env python3
"""Guard the agent<->skill dispatch wiring integrity.

Drydock dispatches work by spawning an isolated subagent (agents/<name>.md)
that immediately invokes the same-named worker skill (skills/<name>/SKILL.md)
via `Skill: drydock:<name>`. If an agent loses its 1:1 skill, points at the
wrong skill, or a new worker skill is added without an agent (or vice-versa),
dispatch silently breaks or a capability becomes unreachable.

This test pins that wiring so any drift fails loudly and forces a conscious
decision instead of shipping a broken orchestrator.

It asserts:
  (a) every agents/<name>.md has a matching skills/<name>/SKILL.md (11 expected);
  (b) skill dirs (excluding _shared) minus agent names == exactly the 4
      intentional main-context skills {drydock, product-manager,
      solution-architect, polymath};
  (c) every agent body instructs invoking its skill via literal "drydock:<name>";
  (d) every agent frontmatter has name==<filename>, plus non-empty
      'description' and 'tools' keys.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "agents"
SKILLS_DIR = ROOT / "skills"

# The skills that intentionally run in the main context and therefore have
# NO agents/<name>.md dispatcher.
MAIN_CONTEXT_SKILLS = {"drydock", "product-manager", "solution-architect", "polymath"}
EXPECTED_AGENT_COUNT = 15


def _parse_frontmatter(text: str) -> dict | None:
    """Return the YAML frontmatter dict, or None if not a well-formed block."""
    if not text.startswith("---"):
        return None
    # Split on the line-delimited fences: text == "---\n<yaml>\n---\n<body>"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def run() -> list[str]:
    failures: list[str] = []

    if not AGENTS_DIR.is_dir():
        return [f"agents/ dir not found at {AGENTS_DIR}"]
    if not SKILLS_DIR.is_dir():
        return [f"skills/ dir not found at {SKILLS_DIR}"]

    agent_names = sorted(p.stem for p in AGENTS_DIR.glob("*.md"))
    skill_names = sorted(
        p.name
        for p in SKILLS_DIR.iterdir()
        if p.is_dir() and p.name != "_shared"
    )

    # (a) every agent has a matching skill SKILL.md; 11 expected.
    if len(agent_names) != EXPECTED_AGENT_COUNT:
        failures.append(
            f"expected {EXPECTED_AGENT_COUNT} agent files, found "
            f"{len(agent_names)}: {agent_names}"
        )
    for name in agent_names:
        skill_md = SKILLS_DIR / name / "SKILL.md"
        if not skill_md.is_file():
            failures.append(
                f"agents/{name}.md has no matching skills/{name}/SKILL.md"
            )

    # (b) skills (minus _shared) minus agents == exactly the main-context set.
    orphan_skills = set(skill_names) - set(agent_names)
    if orphan_skills != MAIN_CONTEXT_SKILLS:
        missing = MAIN_CONTEXT_SKILLS - orphan_skills
        unexpected = orphan_skills - MAIN_CONTEXT_SKILLS
        msg = ["skills-without-agents drifted from the intended main-context set."]
        if unexpected:
            msg.append(
                f"NEW agent-less skill(s) {sorted(unexpected)} — add an "
                f"agents/<name>.md or whitelist intentionally."
            )
        if missing:
            msg.append(
                f"main-context skill(s) {sorted(missing)} now have an agent or "
                f"vanished — investigate."
            )
        failures.append(" ".join(msg))

    # (c) + (d) per-agent body wiring + frontmatter.
    for name in agent_names:
        agent_md = AGENTS_DIR / f"{name}.md"
        text = agent_md.read_text(encoding="utf-8")

        # (c) body must instruct invoking the same-named skill.
        if f"drydock:{name}" not in text:
            failures.append(
                f"agents/{name}.md does not reference its skill "
                f'"drydock:{name}"'
            )

        # (d) frontmatter integrity.
        front = _parse_frontmatter(text)
        if front is None:
            failures.append(f"agents/{name}.md: missing/invalid YAML frontmatter")
            continue
        if front.get("name") != name:
            failures.append(
                f"agents/{name}.md frontmatter name={front.get('name')!r} "
                f"!= filename {name!r}"
            )
        for key in ("description", "tools"):
            val = front.get(key)
            if val is None or (isinstance(val, str) and not val.strip()) or (
                isinstance(val, (list, dict)) and not val
            ):
                failures.append(
                    f"agents/{name}.md frontmatter missing/empty '{key}'"
                )

    return failures


if __name__ == "__main__":
    import sys

    fails = run()
    for f in fails:
        print(f"FAIL: {f}")
    if not fails:
        print(f"PASS: {Path(__file__).name}")
    sys.exit(0 if not fails else 1)
