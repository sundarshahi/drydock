# Shipyard evals

Two tiers of evaluation guard the plugin. They have very different cost,
determinism, and CI characteristics — keep them separate.

## Tier 1 — Deterministic (free, runs in CI)

Pure-Python structural checks over the repo. **No API key, no Claude CLI, no
model calls.** Every check is fully deterministic, so it gates every pull
request via [`.github/workflows/evals.yml`](../.github/workflows/evals.yml) and
runs locally with:

```sh
make evals          # == python3 evals/run_deterministic.py
```

> Requires PyYAML locally (`pip install pyyaml`); CI installs it automatically.

The runner discovers every `evals/deterministic/test_*.py`, executes each as an
isolated subprocess, prints a `PASS`/`FAIL` summary table, and exits non-zero if
any test fails. Each test is itself pure stdlib (PyYAML allowed) and exposes a
`run() -> list[str]` returning human-readable failure strings.

### What the deterministic tests guard

| Test | Regression it guards |
| --- | --- |
| **Loader resolution** | Every worker `SKILL.md` loads each shared protocol with the exact belt-and-suspenders `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` / `Shipyard/.protocols/` fallback chain — so protocols still resolve on a cold first run. |
| **Dead-tool regression** | The removed tools (`TeamCreate`, `TeamDelete`, `smart_outline`, `smart_search`, `smart_unfold`) never reappear as live tool calls — only as prose documenting their removal. |
| **Agent/skill cross-reference** | The 11 `agents/*.md` subagent names map 1:1 to same-named worker skills, and the 4 main-context skills (`shipyard`, `product-manager`, `solution-architect`, `polymath`) intentionally have no agent file. |
| **Manifest integrity** | `plugin.json` and `marketplace.json` agree and pin the same version, with required fields present. |
| **Frontmatter** | Every `skills/*/SKILL.md` and `agents/*.md` has valid YAML frontmatter with a non-empty `name` and a `description` ≤ 1024 chars. |

> Exact test set is whatever lives under `evals/deterministic/`; the table above
> describes the invariants the suite is designed to cover.

## Tier 2 — Behavioral (local-only, spends usage)

Non-deterministic routing/behavior checks driven by your local Claude Code
session (`claude -p`). These exercise *how the orchestrator routes* a prompt to
skills/subagents — inherently probabilistic at `temperature=1.0`.

```sh
make evals-behavioral   # == python3 evals/behavioral/run.py
```

This tier uses **your Claude Code login and spends usage**. It is intentionally
**NOT in CI**:

- CI has **no API key** and we do not want one in the free per-PR gate.
- Output is **non-deterministic** (temp 1.0), so it cannot be a hard pass/fail
  gate without flaking.

Run it locally before shipping orchestration/routing changes.
