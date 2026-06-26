---
sidebar_position: 3
title: "Autonomy levels"
description: "Autopilot, Copilot, Checkpoint, Manual: tune how often Drydock checks in with you."
---

# Autonomy levels

Drydock runs as a team of 19 specialized agents coordinated by one orchestrator. The **autonomy level** is the single dial that decides how often that team pauses to ask you something — and how deeply it interviews you when it does. You pick it once, at the start of a Full Build, and it propagates to every agent for the rest of the run.

There are four levels: **Autopilot**, **Copilot** (recommended), **Checkpoint**, and **Manual**. They differ in how many decisions surface to you, how deep the planning interviews go, and how much intermediate output you review.

:::info
Autonomy tunes *how much you're involved*, not *what gets built*. The same DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN pipeline runs at every level, and the [3 approval gates](#the-3-gates-are-always-present) are always present regardless of which level you choose.
:::

## What each level changes

| | Autopilot | Copilot *(recommended)* | Checkpoint | Manual |
|---|---|---|---|---|
| **Goal** | Fastest, minimal interaction | Best balance of speed and control | Deeper planning, review summaries | Maximum depth and control |
| **PM interview depth** | 2–3 questions | 3–5 questions | 5–8 questions | 8–12 questions |
| **Architect discovery** | Auto-derive from BRD | 5–7 questions | 12–15 questions + capacity planning | Full walkthrough + individual ADR approval |
| **Phase summaries** | None | None | Intermediate outputs shown between phases | Intermediate outputs shown between phases |
| **Gate detail** | The 3 gates only | The 3 gates + moderate interview | The 3 gates + phase summaries | The 3 gates + per-agent output review |
| **Decisions surfaced** | Gates only; everything else auto-resolved | Gates + key planning choices | Gates + planning + phase checkpoints | Gates + planning + every ADR + every agent output |

A few things to note from the table:

- **Architecture derivation scales with the level.** On Autopilot, the solution-architect derives the architecture directly from the BRD with no extra questions. On Manual, you approve each Architecture Decision Record (ADR) individually.
- **Phase summaries only appear at Checkpoint and Manual.** These show intermediate outputs between phases — but they *inform*, they don't *gate*. The pipeline keeps moving; you're not blocked waiting to click through them.
- **Manual adds per-agent output review** at each gate, so you see what every agent produced, not just the consolidated gate artifact.

:::tip
If you're unsure, choose **Copilot**. It surfaces the strategic decisions worth your attention without turning the run into a questionnaire. You can always go deeper next time.
:::

## How the level is chosen

For a **Full Build**, the orchestrator MUST ask before any agent is dispatched or any code is written. After the workspace is bootstrapped and the codebase is classified as greenfield or brownfield, the very first thing you're asked is the autonomy level:

```text
How deeply should the pipeline involve you in decisions?

  Autonomy Level
  ▸ Copilot (Recommended) — 3 gates + moderate architect interview.
                            Best balance of speed and control.
    Autopilot             — Minimal interaction. 3 gates only,
                            auto-derive architecture from BRD. Fastest.
    Checkpoint            — Deep interviews at PM and Architect.
                            Full capacity planning. Review phase summaries.
    Manual                — Maximum depth. Approve each ADR individually.
                            Review every agent output. Full control.
```

Immediately after, you're asked a second question — the Performance Mode (parallelism) preference. These two prompts always come first, in this order.

:::warning
Drydock never assumes a default autonomy level, never skips straight to building, and never folds this choice into the work itself. You pick the level explicitly, up front.
:::

For **non-Full-Build modes** (Feature, Harden, Ship, and so on), the orchestrator only asks about autonomy when the mode involves **3 or more agents**. For 1–2 agent modes — like a single code review or a test run — it defaults to **Copilot** autonomy and sequential execution, because the overhead of asking isn't worth it.

## How the level propagates

Your choice is written once to `drydock/.orchestrator/settings.md`:

```markdown
# Pipeline Settings
Autonomy: [autopilot|copilot|checkpoint|manual]
Parallelism: [maximum|standard|sequential]
Worktrees: [enabled|disabled]
```

**Every skill reads this file at startup** and adapts its depth accordingly. This is what makes the dial a single source of truth across the whole team:

- An **Autopilot** architect doesn't ask 15 discovery questions — it auto-derives.
- A **Manual** product-manager doesn't shortcut to the BRD after two questions — it runs the full 8–12 question interview.

The level reaches every agent because each one consults `settings.md` rather than guessing. Ignoring the setting — for example, an architect over-asking on Autopilot, or a PM under-asking on Manual — is treated as a mistake, not a style choice.

:::note
Autonomy controls *interview depth and check-in frequency*. It does not control build quality. Regardless of level, every agent still builds and verifies its output, runs a validation loop, and holds the same quality bar — no TODOs, no stubs, tests pass.
:::

## The 3 gates are always present

No matter which autonomy level you choose, Drydock always stops at the same **three human approval gates**:

| Gate | When | What you approve |
|------|------|------------------|
| **Gate 1** | End of DEFINE | Requirements / BRD — *what* is being built |
| **Gate 2** | End of architecture | The system design and ADRs — *how* it's built |
| **Gate 3** | Before production | Production-readiness — a BLOCKING evaluation of tests, coverage, performance, compliance, and architecture |

Autonomy changes how *much surrounding detail* you see at a gate, not *whether the gate exists*. Autopilot presents the 3 gates and little else; Manual presents the same 3 gates plus per-agent output review. The gates themselves are non-negotiable at every level.

:::warning
Gate 3 is a hard stop. It won't offer "production ready" while tests, coverage, performance, compliance, or architecture checks are failing — unless each breach has a logged override. Autonomy level does not relax this.
:::

## Related

- [How it works](/docs/concepts/how-it-works) — the orchestrator, the 19 agents, and how the pipeline is wired
- [Pipeline phases](/docs/concepts/how-it-works) — DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN
- [Approval gates](/docs/concepts/how-it-works) — the three strategic gates in depth
