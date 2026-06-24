# Contributing to Shipyard

Thanks for helping improve Shipyard. This plugin is a coordinated set of orchestrated skills, not a loose script collection — contributions are held to the same production bar the pipeline enforces.

## Before you start

- Read [`VISION.md`](VISION.md). Every skill must embody its principles.
- Read [`DEV_PROTOCOL.md`](DEV_PROTOCOL.md) for the internal architecture, protocol-loading rules, and harmonization discipline.

## Repository layout

- `.claude-plugin/plugin.json` — plugin manifest (name, version, keywords).
- `skills/<name>/SKILL.md` — one directory per orchestrated skill. Frontmatter must include `name` and `description`.
- `skills/_shared/protocols/` — protocol SOURCE files. The orchestrator copies these to `Shipyard/.protocols/` at bootstrap; that copied path is what worker-skill loaders read at runtime, not this source directory.
- `skills/_shared/templates/` — config and scaffold templates.
- `hooks/` — `hooks.json` plus the hook scripts it wires (e.g. `secret-guard.sh`).

## Making changes

1. **Branch** from `main`; do not commit directly to `main`.
2. **Read the target file fully** before editing. Keep edits surgical and consistent with existing structure and tone.
3. **Keep counts honest.** If you add or remove a skill, mode, or protocol, update every current-count claim in `README.md`, `plugin.json`, `VISION.md`, and the orchestrator SKILL.md. Mismatched counts fail review.
4. **Adding a protocol?** Add it to the orchestrator bootstrap deploy list and to the loader line of every skill that consumes it, or its `cat` loader will read a missing file.
5. **Adding a skill?** Create `skills/<name>/SKILL.md` with valid `name` + `description` frontmatter, give it a `shipyard:<name>` invocation, and add it to the README invocation table.
6. **Bump the version** in `plugin.json` and add a dated `CHANGELOG.md` entry. Flag anything potentially breaking under a `### Breaking` heading.

## Validation

CI runs `.github/workflows/validate.yml` on every PR: it checks `plugin.json` is valid JSON with required fields, lints `hooks/hooks.json`, and verifies every `skills/*/SKILL.md` has `name` + `description` frontmatter. Run the equivalent checks locally before pushing. Keep YAML and JSON lint-clean.

## Pull requests

- One logical change per PR. Describe what changed and why.
- Note any version bump, new skill/mode/protocol, or breaking change explicitly.
- Be responsive to review — the bar is production-readiness, not "it runs once."
