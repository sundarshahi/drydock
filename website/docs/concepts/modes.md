---
sidebar_position: 4
title: "Modes"
description: "Drydock is not all-or-nothing: 14 modes from a full greenfield build to a single-skill audit."
---

# Modes

Drydock is not all-or-nothing. Before any work begins, the orchestrator classifies your request into one of **14 execution modes** and runs only the agents that mode needs — from a single read-only code review to the full 19-agent greenfield-to-launch pipeline.

The overhead of classifying is near zero: most modes invoke one to three agents and finish in a single pass. Only **Full Build** runs the complete `DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN` pipeline with all three strategic gates.

:::info How a mode gets picked
The orchestrator matches the trigger signals in your prompt against the mode table, then either invokes immediately (single-skill modes) or presents a short plan for confirmation (multi-skill modes). You can always reply "I want the full Drydock pipeline" to switch any mode into Full Build. See [/docs/concepts/how-it-works](/docs/concepts/how-it-works) for the routing detail.
:::

## The 14 modes

| Mode | What it does | Triggers on | Gates |
|------|--------------|-------------|-------|
| **Full Build** | Greenfield build of a complete production system: requirements, architecture, tested backend/frontend, security audit, CI/CD, docs, and launch. All 19 agents across the full pipeline. | "build a SaaS", "from scratch", "production quality", "full stack", greenfield intent | **3** (BRD, architecture, production-readiness) |
| **Feature** | Add a feature to an existing codebase. Lightweight `DEFINE → BUILD → TEST`, scoped to the feature — not a system redesign. | "add [feature]", "implement [feature]", "new endpoint", "new page", "integrate [service]" | **1** (scope) |
| **Harden** | Security + quality audit on existing code. Security, QA, and Code Review run in parallel, findings are merged and sorted by severity, then Critical/High issues are fixed. No building. | "review", "audit", "secure", "harden", "before launch", "production ready" | **1** (findings) |
| **Pentest (VAPT)** | Vulnerability Assessment & Penetration Testing. Static phases 1–6, then **live DAST/fuzzing** against an authorized target, then a report. Can send real payloads to a running system. | "pentest", "vapt", "penetration test", "security testing", "dast", "exploit this", "owasp api", "owasp llm" | **1** (authorization — see below) |
| **Compliance** | Map implemented controls to in-scope frameworks (SOC 2 / HIPAA / GDPR / PCI / CCPA / ISO 27001 / FedRAMP). Consumes the security audit; never re-derives it. | "compliance", "SOC 2", "HIPAA", "GDPR", "PCI", "ISO 27001", "FedRAMP", "audit readiness", "DPIA", "SSP" | **1** (scoping — see below) |
| **Ship** | Get existing code deployed: Dockerfiles, CI/CD, IaC (Terraform/Pulumi), monitoring (DevOps), then SLOs, runbooks, alerting, chaos plan (SRE). | "deploy", "CI/CD", "containerize", "infrastructure", "terraform", "docker" | **1** (infra) |
| **Test** | Write and run tests for existing code. QA reads the code, writes a test plan, implements tests, and runs them autonomously. | "write tests", "test coverage", "test this", "add tests" | **0** |
| **Review** | Read-only code quality review. Code Reviewer produces a findings report with severity distribution. | "review my code", "code review", "code quality", "check my code" | **0** |
| **Architect** | Design or redesign architecture. Full discovery interview, then ADRs, diagrams, tech stack, API contracts, and scaffold. | "design", "architecture", "API design", "data model", "tech stack", "how should I structure" | **1** (architecture) |
| **Document** | Generate documentation for existing code: API reference, dev guides, architecture overview. Technical Writer runs autonomously. | "document", "write docs", "API docs", "README" | **0** |
| **Explore** | Thinking partner. Polymath researches, advises, and ideates, then offers to hand off to any other mode when you're ready. | "explain", "understand", "help me think", "what should I", "I'm not sure" | **0** |
| **Optimize** | Performance + reliability analysis. Code Reviewer finds anti-patterns, N+1 queries, and memory leaks; SRE does capacity and scaling analysis. Top issues are then fixed. | "performance", "slow", "optimize", "scale", "reliability" | **1** (analysis) |
| **Design (UX)** | UX research → information architecture → design-system spec → interaction design → usability/accessibility. Writes the design-system spec for the frontend to implement (or a UX audit on brownfield). | "design the UX", "wireframes", "user flows", "design system", "UX research", "usability", "personas" | **0** |
| **Launch (GTM)** | Go-to-market for a shipped product: positioning, launch plan, site copy, and funnels (Growth Marketer); pricing, collateral, and trust pack (Sales Strategist); onboarding, support, and retention (Customer Success). Runs in parallel. | "launch", "go to market", "GTM", "pricing", "positioning", "marketing", "sales collateral", "onboarding", "support" | **1** (GTM plan) |
| **Custom** | Doesn't fit the patterns above. Pick the agents you need from a menu; they execute in dependency order. | Any request that doesn't match the other modes | varies |

## Single-skill vs. multi-skill modes

The orchestrator handles these two groups differently:

- **Single-skill modes** — Test, Review, Architect, Design (UX), Document, Explore. The intent is obvious, so there's no plan to confirm: Drydock classifies and invokes immediately. The agent prints its own header and per-phase progress.
- **Multi-skill modes** — Feature, Harden, Pentest (VAPT), Compliance, Ship, Optimize, Launch (GTM), Custom. Drydock presents a short execution plan for confirmation before running, then prints a completion box summarizing each agent's concrete metrics.

## The two special gates

Most gates are *strategic* — they exist to put a human decision in front of an expensive or irreversible step. Two modes carry a mandatory gate that exists for **safety and scope**, and neither can be skipped — even though both modes are otherwise single-skill-heavy, they are **never** routed through the silent single-skill path.

### Pentest (VAPT) — authorization gate

:::warning Active testing requires explicit authorization
Before any active testing, Pentest mode blocks on an authorization gate. DAST, fuzzing, and exploitation send **real payloads to a running target**, so the gate requires you to confirm explicit authorization, the exact in-scope hosts/URLs, and the rules of engagement (local/authorized-staging only, no DoS, no destructive payloads, no production data).

If you choose **Static/passive only**, the mode collapses to the Harden static path (phases 1–6, no execution). The choice and target allowlist are persisted to the workspace settings and an authorization receipt is written before any live testing begins.
:::

### Compliance — scoping gate

:::note Compliance mapping is framework-specific
The required controls differ per framework, so Compliance mode blocks on a scoping gate before mapping anything. You confirm which framework(s) are in scope (SOC 2, HIPAA/GDPR, PCI DSS / ISO 27001 / FedRAMP, and so on), and the in-scope list is persisted to the workspace settings with a scoping receipt.

Compliance **consumes** the security audit — the PII inventory, encryption audit, and OWASP/STRIDE findings produced by the Security Engineer — and never re-derives or overrides them. If no security audit exists yet, it flags that controls evidence will be incomplete and offers to run Harden first.
:::

## Gate counts at a glance

Across all 14 modes, only **Full Build** uses all three strategic gates. Every other mode that involves a meaningful, hard-to-reverse decision carries exactly one gate; the read-only and fully autonomous modes carry none.

| Gates | Modes |
|-------|-------|
| **3** | Full Build |
| **1** | Feature, Harden, Pentest (VAPT), Compliance, Ship, Architect, Optimize, Launch (GTM) |
| **0** | Test, Review, Document, Explore, Design (UX) |
| **varies** | Custom (depends on the agents you select) |

:::tip Start small, scale up
You don't have to commit to a full build. Run **Review** or **Harden** on code you already have, **Architect** to pressure-test a design, or **Explore** to think through an idea — then promote to **Full Build** whenever you're ready.
:::

For the full pipeline, the three strategic gates, and how agents coordinate, see [/docs/concepts/how-it-works](/docs/concepts/how-it-works).
