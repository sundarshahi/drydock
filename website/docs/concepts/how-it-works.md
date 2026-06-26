---
sidebar_position: 1
title: "How it works"
description: "The six-phase pipeline (DEFINE to SUSTAIN), the three approval gates, and per-phase parallelism."
---

# How it works

Drydock is an open-source plugin for [Claude Code](https://claude.com/claude-code) (version 2.5.0) that turns the editor into a full product team: **19 specialized agents coordinated by a single orchestrator**. You describe what you want in plain English; the orchestrator routes the work through a pipeline of phases, pauses at three human approval gates, and hands you back a real, tested, documented system.

This page explains the pipeline in depth — what each phase does, which agents run, what artifacts they produce, and how the gates and parallelism fit together.

:::note Agents and skills
Each agent shows up as a `drydock:<skill>` skill. Throughout the docs, "agent" and "skill" mean the same thing: a specialized worker the orchestrator routes to. Of the 19, **15 run as isolated subagents** (defined in `agents/*.md`, each in its own git worktree); the **orchestrator** plus the three planning agents (**product-manager**, **solution-architect**, **polymath**) run in-context as skills.
:::

## The shape of a run

The full build flows through six phases — **DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN** — and stops at three gates where you weigh in. Everything between the gates is autonomous.

```text
          Your idea, in plain English
                     │
                     ▼
   ┌─ DEFINE ─────────────────────────────────────┐
   │   Product Manager    → requirements (BRD)     │
   │   Solution Architect → architecture + API     │
   │   UX Designer        → design system + flows  │
   └───────────────────────────────────────────────┘
         ◆ GATE 1   you approve the requirements
         ◆ GATE 2   you approve the architecture
                     │
                     ▼
   ┌─ BUILD   ∥ in parallel ───────────────────────┐
   │   Software Engineer · Frontend Engineer ·     │
   │   DevOps (containerization)                   │
   └───────────────────────────────────────────────┘
                     │  (code written + BUILD-exit security gate)
                     ▼
   ┌─ HARDEN  ∥ in parallel ───────────────────────┐
   │   QA · Security · Code Review · Compliance    │
   └───────────────────────────────────────────────┘
                     │  (blocking findings → remediation)
                     ▼
   ┌─ SHIP    ∥ in parallel ───────────────────────┐
   │   DevOps (IaC + CI/CD) · Remediation ·        │
   │   SRE · Data Scientist (conditional)          │
   └───────────────────────────────────────────────┘
         ◆ GATE 3   you approve production readiness
                     │
                     ▼
   ┌─ LAUNCH  ∥ in parallel ───────────────────────┐
   │   Growth Marketer · Sales Strategist ·        │
   │   Customer Success                            │
   └───────────────────────────────────────────────┘
                     │
                     ▼
   ┌─ SUSTAIN ∥ in parallel ───────────────────────┐
   │   Technical Writer · Skill Maker ·            │
   │   compound learning + final assembly          │
   └───────────────────────────────────────────────┘
                     │
                     ▼
   A real system: tested, secured, documented, deployed — ready to launch.

   ∥  runs in parallel       ◆  you approve — everything between gates is autonomous
```

:::info Phases are sequential; agents within a phase are parallel
The two rules that govern execution are:

1. **Phases run strictly in order** — DEFINE finishes before BUILD starts, BUILD before HARDEN, and so on. Each phase re-reads the prior phase's artifacts from disk before it begins (re-anchoring), so long runs don't drift from the original requirements.
2. **Within a phase, independent agents run in parallel.** The orchestrator reads the architecture (number of services, page groups, modules) and spawns one agent per work unit — each isolated in its own git worktree so concurrent writes never collide. Branches are merged back after the wave.
:::

## The six phases

### DEFINE — requirements, architecture, design

| | |
|---|---|
| **Agents** | Product Manager (T1), Solution Architect (T2), UX Designer (T2b) |
| **Runs** | T1 → **Gate 1** → T2 ∥ T2b → **Gate 2** |
| **Key artifacts** | `drydock/product-manager/BRD/` (`brd.md`, `research-notes.md`, `constraints.md`, `compliance-signals.md`); `api/` (OpenAPI 3.1), `schemas/`, `docs/architecture/` (ADRs, system design, ERD); `docs/design/` (design-system spec) |

The Product Manager researches the domain, conducts a short CEO interview (including compliance-discovery questions about data classes and target markets), and writes the **Business Requirements Document (BRD)**. After **Gate 1**, the Solution Architect designs the architecture, tech stack, API contracts, and data model — while the UX Designer produces the design-system spec **in parallel** (both need only the approved BRD). The UX Designer is skipped when `features.frontend: false`.

:::tip Security requirements land before any code is written
At the start of BUILD, the Security Engineer (T6a) emits `drydock/security-engineer/security-requirements.md` — a STRIDE-derived, per-threat control list — **before** the build agents start coding. BUILD agents read it as a mandatory input and treat its controls (authn/authz, input validation, output encoding, secrets handling) as acceptance criteria.
:::

### BUILD — write the system

| | |
|---|---|
| **Agents** | Software Engineer (T3a), Frontend Engineer (T3b), DevOps (T4) |
| **Runs** | T3a ∥ T3b in parallel; T4 (containerization) starts once the backend is written |
| **Key artifacts** | `services/`, `libs/shared/`, `frontend/`, `Dockerfile` per service, `docker-compose.yml` |

The Software Engineer spawns one agent per service from the architecture; the Frontend Engineer spawns one per page group from the BRD and **implements the UX design-system spec** (it does not re-author it). Both write secure-by-default code under TDD and honor the shared protocols (`security-defaults`, `observability-contract`, `architecture-boundaries`). DevOps writes Dockerfiles and validates that `docker build` and `docker-compose up` succeed.

When the parallel wave merges, BUILD runs a **BUILD-exit security gate** over the unified tree — the same SCA, secret-scan, and SAST scanners DevOps later embeds in CI. Any Critical or High finding **blocks** BUILD and loops back to the owning agent for a fix; the phase does not advance with an open Critical/High.

### HARDEN — audit and test against the code

| | |
|---|---|
| **Agents** | QA Engineer (T5), Security Engineer (T6a), Code Reviewer (T6b), Compliance Officer (T6e) |
| **Runs** | All four in parallel |
| **Key artifacts** | `tests/`; `drydock/security-engineer/findings/`; `drydock/code-reviewer/findings/`; `drydock/compliance-officer/` control-evidence map |

All four agents run against the written code. **Authority boundaries are strict:** the Security Engineer is the *sole* authority on OWASP Top 10, STRIDE, PII, and encryption; the Code Reviewer does architecture, quality, and performance (read-only, adversarial — never security); the Compliance Officer maps regulatory controls to evidence and *consumes* the security audit rather than redoing it.

After the wave, the orchestrator reads gate/metric fields from the receipts and forms a **unified blocking set**: any Critical/High security finding, any failing test, sub-threshold coverage, a performance-budget regression, a missing mandatory compliance control, or a HIGH architecture-boundary violation. Every blocking item becomes a remediation task in SHIP.

### SHIP — infrastructure, remediation, readiness

| | |
|---|---|
| **Agents** | DevOps (T7), Software Engineer / Remediation (T8), SRE (T9), Data Scientist (T10, conditional) |
| **Runs** | T7 ∥ T8, then T9 ∥ T10 → **Gate 3** |
| **Key artifacts** | `infrastructure/` (Terraform/Pulumi, K8s manifests), `.github/workflows/`, `docs/runbooks/` |

DevOps generates IaC and CI/CD pipelines (embedding the same scanners the BUILD-exit gate used) and runs a **hard pipeline lint** — `actionlint`, `hadolint`, `tflint`, `terraform validate` — that must pass clean. In parallel, the Software Engineer fixes the full HARDEN blocking set. Once both finish, the SRE (sole SLO authority) does the production-readiness review, defines SLIs/SLOs, error budgets, burn-rate alerts, chaos scenarios, and runbooks; the Data Scientist optimizes LLM/ML usage **only if** AI/ML imports are detected.

:::warning Gate 3 is blocked on evidence
`production-ready` is **blocked** while any blocking gate is open — failing tests, sub-threshold coverage, a perf-budget regression, a missing mandatory compliance control, or a HIGH architecture-boundary violation. Gate 3 may present "production-ready" only when all blocking gates are clear, or each open item carries a logged "accepted with justification" override receipt.
:::

### LAUNCH — go to market

| | |
|---|---|
| **Agents** | Growth Marketer (T14), Sales Strategist (T15), Customer Success (T16) |
| **Runs** | All three in parallel, **after Gate 3 passes** |
| **Key artifacts** | `docs/marketing/`, `docs/sales/`, `docs/customer-success/` |

You don't launch software that isn't production-ready, so LAUNCH runs only after Gate 3 is green. The Growth Marketer owns positioning, messaging, the launch plan, and landing-page/SEO briefs. The Sales Strategist *consumes* that positioning and turns the security + compliance evidence into a buyer-facing **trust pack** (pricing, collateral, sales process). Customer Success builds onboarding, support ops, and retention playbooks, and routes prioritized feedback back to the Product Manager.

### SUSTAIN — document, learn, assemble

| | |
|---|---|
| **Agents** | Technical Writer (T11), Skill Maker (T12), plus compound learning + final assembly (T13) |
| **Runs** | T11 ∥ T12, then T13 |
| **Key artifacts** | `docs/` (API reference, dev/ops/architecture guides); `.claude/skills/` (3–5 project-specific skills); `drydock/.orchestrator/compound-learnings.md`; the `# Drydock Native` block in `CLAUDE.md` |

The Technical Writer produces the full documentation set from the OpenAPI specs and source; the Skill Maker mines the finished project for recurring patterns and emits project-specific skills. T13 records compound learnings, writes the **Drydock Native** directive into `CLAUDE.md` (so future sessions know to route changes through the pipeline), runs final validation (`docker-compose up`, `make test`, `terraform validate`), and asks how you want the code assembled. Customer Success carries over from LAUNCH as an ongoing operation and reconciles the help center against the now-complete docs.

## The three gates

The three gates always fire — your chosen [autonomy level](/docs/intro) governs only the smaller agent-level questions *between* gates, never the gates themselves.

| Gate | After | You approve | Blocks until |
|---|---|---|---|
| **Gate 1** | T1 (Product Manager) | The requirements (BRD) | You approve, request changes, or review details |
| **Gate 2** | T2 (Solution Architect) | The architecture, API contracts, and data model | You approve |
| **Gate 3** | SHIP | Production readiness | All blocking gates clear, or each open item carries an override receipt |

Before opening each gate, the orchestrator reads the relevant receipt JSON, verifies that every claimed artifact exists on disk, and uses the receipt metrics for the gate display — so a gate never opens on prose alone.

## Not every request runs the whole pipeline

Drydock infers an **execution mode** from what you ask for — 14 modes plus a Custom fallback. A code review or a single feature skips straight to the relevant agents with fewer (or zero) gates; only a Full Build runs all six phases and all three gates. You can also run a single phase directly, for example:

```text
/drydock just define     # requirements + architecture only
/drydock just harden     # requires BUILD output
/drydock skip frontend   # omit the frontend agent
```

## Why the output is trustworthy

A few mechanisms keep the result accurate rather than merely plausible:

- **Receipt enforcement** — every agent writes JSON proof of its work; gates verify the receipts and the artifacts they claim before opening.
- **Re-anchoring** — specs are re-read from disk at every phase transition, so long runs don't drift.
- **Adversarial review** — the Code Reviewer assumes the code is wrong until proven right.
- **Grounding** — every claim cites `file:line`, command output, or a retrieved source, tagged `[verified]` / `[inferred]` / `[unverified]`.
- **Worktree isolation** — parallel agents each run in their own git worktree, so concurrent work never clobbers files.

---

**Install Drydock** (from inside Claude Code):

```text
/plugin marketplace add sundarshahi/drydock
/plugin install drydock@drydock
```

Source: [github.com/sundarshahi/drydock](https://github.com/sundarshahi/drydock).
