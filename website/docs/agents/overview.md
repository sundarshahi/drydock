---
sidebar_position: 1
title: "The 19-agent roster"
description: "Every Drydock agent, what it owns, and how the orchestrator dispatches them."
---

# The 19-agent roster

Drydock is a team of 19 specialized agents coordinated by one orchestrator. You describe what you want in plain English; the orchestrator classifies the request, routes it to the right agents, and runs them through the pipeline — pausing only at the human approval gates.

Throughout these docs, "agent" and "skill" mean the same thing: a specialized worker the orchestrator routes to. Each is invocable as `drydock:<name>`.

:::info Pipeline phases
A full build flows through six phases — **DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN** — with three human approval gates: Gate 1 (requirements/BRD), Gate 2 (architecture), and Gate 3 (production readiness). See [How it works](/docs/concepts/how-it-works) for the full pipeline.
:::

## The full roster

The table below lists all 19 agents, what each owns, and the phase it primarily works in. The orchestrator routes to them automatically based on your request; you can also [invoke any one directly](#invoking-a-single-agent-directly).

| # | Agent | Owns | Phase |
|---|-------|------|-------|
| 1 | Orchestrator | Routing, gates, receipts | All (coordinator) |
| 2 | Polymath | Research, ideation, translation | DEFINE / Explore |
| 3 | Product Manager | Requirements (the WHAT) | DEFINE |
| 4 | Solution Architect | Architecture + API (the HOW) | DEFINE |
| 5 | UX Designer | UX research, IA, design-system spec | DEFINE → BUILD |
| 6 | Software Engineer | Backend services, APIs, data layers | BUILD |
| 7 | Frontend Engineer | Web UI, typed API clients, perf budgets | BUILD |
| 8 | QA Engineer | Test pyramid, coverage/mutation gates | HARDEN |
| 9 | Security Engineer | STRIDE/OWASP audit + VAPT | HARDEN |
| 10 | Code Reviewer | Code quality, architecture conformance | HARDEN |
| 11 | DevOps | CI/CD, IaC, containers, supply chain | SHIP |
| 12 | SRE | SLOs, runbooks, production-readiness review | SHIP |
| 13 | Data Scientist | LLM/ML optimization (conditional) | SHIP |
| 14 | Compliance Officer | Regulatory control mapping + gate | HARDEN |
| 15 | Technical Writer | API reference, developer/ops guides | SUSTAIN |
| 16 | Skill Maker | Project-specific Claude Code skills | SUSTAIN |
| 17 | Growth Marketer | Positioning, GTM/launch plan, marketing | LAUNCH |
| 18 | Sales Strategist | Pricing, collateral, sales process | LAUNCH |
| 19 | Customer Success | Onboarding, support, retention | LAUNCH → SUSTAIN |

:::note Not every request runs the whole roster
The orchestrator picks an [execution mode](/docs/concepts/modes) to match what you asked for. A code review or a single feature engages only the relevant agents, with fewer (or zero) gates. Only **Full Build** mode runs all 19.
:::

## Two ways agents run

The 19 agents split into two execution models. The distinction is about **context isolation** — where each agent runs and whether it can talk to you directly.

### 4 in-context agents

Four agents run **in the main conversation** as skills, sharing the orchestrator's context window:

- **Orchestrator** (`drydock`) — classifies the request, builds the task graph, dispatches the other agents, and runs the approval gate ceremonies.
- **Product Manager** — interviews you to produce the BRD; runs the Gate 1 conversation.
- **Solution Architect** — designs the system and API; runs the Gate 2 conversation.
- **Polymath** — research, ideation, and the gate "translator" that explains artifacts in plain language when you pick "Chat about this."

These run in-context because their work is **sequential and user-interactive** — they conduct interviews, surface decisions, and run approval gates that need the conversation with you. They are dispatched with the Skill tool:

```python
Skill(skill="product-manager")
```

### 15 isolated subagents

The other 15 agents ship as subagent definitions at `agents/<name>.md` and run in **their own isolated context window**, backgrounded and parallel:

```
code-reviewer        compliance-officer    customer-success
data-scientist       devops                frontend-engineer
growth-marketer      qa-engineer           sales-strategist
security-engineer    skill-maker           software-engineer
sre                  technical-writer      ux-designer
```

Each declares `background: true` in its own frontmatter and invokes the matching `drydock:<name>` skill in its body. The orchestrator delegates to them in natural language — it does **not** restate the role or pass `subagent_type`/`isolation`/`background`; those live in the subagent's own definition. They run their work autonomously, write a receipt JSON to `drydock/.orchestrator/receipts/`, and mark their task complete.

:::tip Why isolate?
Isolated subagents do the heavy, autonomous work — implementing services, writing tests, running security audits — without polluting the main context window. That keeps the orchestrator's context lean across long runs and lets independent work proceed **in parallel**.
:::

## Worktree isolation

Most of the isolated subagents also declare `isolation: worktree` in their frontmatter. Each runs inside its **own git worktree**, so concurrent agents editing the codebase never clobber each other's files. After a parallel wave finishes, the orchestrator merges each worktree branch back into the working branch before the next phase reads those outputs.

A worktree subagent's worktree **auto-cleans** once its branch has been merged back — there is no team to tear down. On a gate rejection, in-flight subagents finish or are abandoned on their own and their worktrees auto-clean.

:::note Requirements
Worktree isolation uses git. The build and ship phases also use Docker and Docker Compose (container builds, IaC). Install them if you plan to run a full build.
:::

## Invoking a single agent directly

You don't have to run the whole pipeline. Let the orchestrator route for you, or call any agent by name with `/drydock:<name>`:

```text
/drydock:security-engineer audit my API for OWASP Top 10
/drydock:technical-writer document the public API
/drydock:code-reviewer review my latest changes
```

To let the orchestrator classify and route the request itself, invoke the orchestrator directly:

```text
/drydock:drydock build a SaaS for booking dog walkers — auth, payments, dashboard
```

Every agent maps to a `/drydock:<name>` command — for example `/drydock:product-manager`, `/drydock:solution-architect`, `/drydock:frontend-engineer`, `/drydock:devops`, `/drydock:growth-marketer`. The name matches the agent's slug in the [roster table](#the-full-roster).

:::warning
The isolated subagents are designed to be dispatched by the orchestrator during a pipeline run. Invoking one directly still works, but the orchestrator normally sets up the workspace, re-anchors specs from disk, and verifies receipts at gates — context a standalone call skips.
:::

## Explore each category

The 19 agents group into five categories. Each page below covers the agents in that group, what they produce, and how they hand off to one another:

- **[Planning and design](/docs/agents/planning-and-design)** — Polymath, Product Manager, Solution Architect, UX Designer.
- **[Engineering](/docs/agents/engineering)** — Software Engineer, Frontend Engineer, Data Scientist.
- **[Quality and security](/docs/agents/quality-and-security)** — QA Engineer, Security Engineer, Code Reviewer, Compliance Officer.
- **[Delivery](/docs/agents/delivery)** — DevOps, SRE, Technical Writer, Skill Maker.
- **[Go-to-market](/docs/agents/go-to-market)** — Growth Marketer, Sales Strategist, Customer Success.

:::info
Drydock is an open-source plugin for Claude Code (version 2.5.0). Install it from inside Claude Code:

```text
/plugin marketplace add sundarshahi/drydock
/plugin install drydock@drydock
```

Source: [github.com/sundarshahi/drydock](https://github.com/sundarshahi/drydock)
:::
