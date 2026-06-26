---
sidebar_position: 1
title: "Installation"
description: "Install Drydock from the Claude Code plugin marketplace in two commands."
---

# Installation

Drydock is an open-source plugin for [Claude Code](https://docs.claude.com/en/docs/claude-code/overview). It installs from a plugin marketplace in two commands — no local clone required. This page covers the prerequisites, the install commands, what gets registered, how updates work, and how to run an unreleased checkout for local development.

:::info Current version
This page documents Drydock **2.5.0**. The repository lives at [github.com/sundarshahi/drydock](https://github.com/sundarshahi/drydock).
:::

## Prerequisites

Claude Code is the only thing you need to install Drydock and route work to its agents.

| Tool | Required for | When you need it |
|---|---|---|
| **Claude Code** | Installing and running Drydock | Always |
| **Git** | Worktree isolation during builds | The BUILD / SHIP phases |
| **Docker** | Container builds | The HARDEN / SHIP phases |
| **Docker Compose** | Local multi-service orchestration | The HARDEN / SHIP phases |

Git, Docker, and Docker Compose are used by the build and ship phases for git-worktree isolation, container builds, and infrastructure-as-code. Install them if you plan to run a [full build](/docs/concepts/how-it-works); they are not needed just to install the plugin or route requests.

:::tip
If you only want to try Drydock's planning and routing — for example a code review or an architecture pass — Claude Code alone is enough. You can add Git and Docker later when you reach a phase that needs them.
:::

## Install

Run both commands from inside Claude Code. The first registers the Drydock marketplace; the second installs the plugin from it.

```text
/plugin marketplace add sundarshahi/drydock
```

```text
/plugin install drydock@drydock
```

The `drydock@drydock` syntax is `<plugin-name>@<marketplace-name>` — both happen to be named `drydock`.

That's it. Describe what you want in plain English and Drydock takes over:

```text
Build a SaaS for booking dog walkers — auth, payments, and a dashboard.
```

Drydock picks an [execution mode](/docs/concepts/how-it-works) to match your request, asks you to choose an autonomy level, then runs the pipeline — pausing only at the three approval gates.

## What the marketplace install registers

Installing `drydock@drydock` registers the full plugin into your Claude Code environment:

- **19 agents**, each invocable as `drydock:<skill>`. Fifteen run as isolated subagents; the orchestrator (`drydock`) plus three planning agents — `product-manager`, `solution-architect`, and `polymath` — run in-context as skills.
- **Hooks**, including the `secret-guard` hook that blocks secret writes and commits and scans staged diffs.
- **Shared protocols** that enforce architecture boundaries, security defaults, grounding, and the gate logic.

No files are cloned into your project at install time. Drydock scaffolds a `drydock/` workspace directory inside a project only when you actually start a run.

## How updates work

The marketplace entry is **version-pinned** — `marketplace.json` records the plugin version (currently `2.5.0`), so you always install a known, reproducible build rather than whatever is on the tip of the default branch.

To move to a newer release, refresh the marketplace and reinstall:

```text
/plugin marketplace update drydock
```

```text
/plugin install drydock@drydock
```

The update pulls the latest pinned version from the marketplace; reinstalling activates it.

:::note
Because the version is pinned in the marketplace entry, an install is deterministic: two people who add the marketplace and install the plugin at the same time get the same Drydock build.
:::

## Local development (unreleased checkout)

To run an unreleased checkout — for example a feature branch, or the tip of `main` — instead of the marketplace build, clone the repository into Claude Code's plugins directory and launch Claude Code with that plugin directory:

```bash
git clone https://github.com/sundarshahi/drydock ~/.claude/plugins/drydock
claude --plugin-dir ~/.claude/plugins/drydock
```

This loads the plugin straight from your working tree, so any local edits take effect immediately. Use it for contributing or testing changes; for everyday use, prefer the marketplace install above so you stay on a pinned, reproducible version.

:::warning
A local checkout tracks whatever is in your working tree, not a pinned release. Pull changes yourself to stay current, and expect unreleased behavior to differ from the marketplace build.
:::

## Next steps

- Learn the pipeline and the three approval gates in [How it works](/docs/concepts/how-it-works).
- Run your first build with the [Quick start](/docs/getting-started/quickstart) guide.
