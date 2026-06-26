---
sidebar_position: 1
title: "Drydock"
description: "An idea-to-launch product pipeline for Claude Code: 19 specialized agents take a product from architecture and UX through tested, secured, shipped code to go-to-market."
---

# Drydock

Drydock is an open-source plugin for Claude Code that turns it into a full product team. You describe what you want in plain English, and a single orchestrator routes the work to 19 specialized agents — covering product, architecture, UX, engineering, QA, security, DevOps, SRE, compliance, docs, and go-to-market. The agents research, build, test, secure, document, and launch a real system. You stay in the strategist's seat and approve at three checkpoints; the agents do the work in between.

Each agent is invocable as a `drydock:<skill>` skill. Throughout these docs, "agent" and "skill" mean the same thing: a specialized worker the orchestrator routes to.

:::info Version
This documents Drydock `2.5.0`. Source: [github.com/sundarshahi/drydock](https://github.com/sundarshahi/drydock) (MIT licensed).
:::

## What Drydock is

Drydock is a team of 19 agents coordinated by one orchestrator:

- **15 agents** run as isolated subagents (`agents/*.md`), each in its own context.
- **The orchestrator** (`drydock`) plus **3 planning agents** — Product Manager, Solution Architect, and Polymath — run in-context as skills.

You don't manage the agents directly. You describe a goal, pick an autonomy level (how often Drydock checks in), and the orchestrator infers what work is needed and routes it. It installs entirely inside Claude Code — no local clone required.

## The idea-to-launch pipeline

A full build flows through six phases. The agents work autonomously inside each phase; you weigh in only at the three approval gates.

```text
Your idea
   │
   ▼
DEFINE   → requirements (BRD) · architecture + API · UX design system & flows
   │   ◆ Gate 1: approve requirements
   │   ◆ Gate 2: approve architecture
   ▼
BUILD    → backend · frontend · DevOps · QA · security · code review · SRE   (parallel)
   │
   ▼
HARDEN   → tests · security audit · code review · container build            (parallel)
   │
   ▼
SHIP     → IaC + CI/CD · SRE · remediation
   │   ◆ Gate 3: approve production readiness
   ▼
LAUNCH   → marketing/growth · sales · customer success                       (parallel)
   │
   ▼
SUSTAIN  → docs · project-specific skills · compound learning
   │
   ▼
A tested, secured, documented, deployed system — ready to launch.
```

The three human approval gates are non-negotiable checkpoints:

| Gate | You approve |
|---|---|
| **Gate 1** | Requirements (the BRD) |
| **Gate 2** | Architecture |
| **Gate 3** | Production readiness |

:::note Not every request runs the whole pipeline
Drydock picks an execution **mode** to match what you asked for. There are 14 modes — Full Build runs all 19 agents through every phase; the other 13 (Feature, Harden, Pentest, Compliance, Ship, Test, Review, Architect, Design, Document, Explore, Optimize, Launch) route to a subset with fewer or zero gates. A Custom fallback shows a menu when nothing matches. You don't pick the mode — it's inferred from your request.
:::

## Who it's for

- **Founders and solo builders** who want to go from a one-line idea to a launched product without assembling a team.
- **Engineering teams** that want production-grade scaffolding — architecture, tests, security, CI/CD, observability, compliance — generated and enforced rather than hand-rolled.
- **Anyone working inside Claude Code** who wants to invoke a specific specialist (`/drydock:security-engineer`, `/drydock:ux-designer`, and so on) for a focused task.

## What makes it different

Drydock is built so the output is trustworthy, not just plausible:

- **Receipts** — every agent writes JSON proof of its work, and gates verify the receipts (and the artifacts they claim) before opening.
- **Re-anchoring** — specs are re-read from disk at every phase transition, so long runs don't drift from the original requirements.
- **Gates** — `production-ready` is blocked on failing tests, coverage, performance budget, compliance controls, or architecture-boundary violations. An override requires a logged "accepted with justification" receipt.
- **Security by default** — a `security-defaults` protocol plus a real `secret-guard` hook that blocks secret writes/commits and scans staged diffs.
- **Grounding** — evidence-first generation: every claim cites `file:line`, command output, or a retrieved source, tagged `[verified]` / `[inferred]` / `[unverified]`. Agents never invent CVEs or CVSS scores.

:::tip
You only approve direction at the gates. Between them, the agents run autonomously — and the autonomy level you pick (Autopilot, Copilot, Checkpoint, or Manual) governs only the smaller, agent-level questions, never the three pipeline gates.
:::

## Next steps

- [Installation](/docs/getting-started/installation) — add the marketplace and install the plugin inside Claude Code.
- [Quickstart](/docs/getting-started/quickstart) — describe your first build and walk through the gates.
