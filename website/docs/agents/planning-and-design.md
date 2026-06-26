---
sidebar_position: 2
title: "Planning & design"
description: "Product Manager, Solution Architect, UX Designer, and Polymath: the agents that define what gets built."
---

# Planning & design

Before any production code is written, four agents decide *what* gets built and *how it should feel*. Three of them — the **Product Manager**, **Solution Architect**, and **Polymath** — run in-context as skills alongside the orchestrator. The **UX Designer** runs as an isolated subagent. Together they own the **DEFINE** phase and the bridge into **BUILD**, and they produce the artifacts (BRD, architecture, design-system spec) that every downstream agent reads.

:::info Where these sit in the pipeline
Drydock's pipeline runs **DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN**, with three human approval gates. The agents on this page concentrate in **DEFINE**, and they feed **Gate 1 (requirements/BRD)** and **Gate 2 (architecture)**. See [how it works](/docs/concepts/how-it-works) for the full flow.
:::

Each agent below has a single, non-overlapping authority. The boundaries are deliberate: an agent that owns "what" never owns "how," and vice-versa. The "Does NOT do" line for each is the load-bearing part — it's where one agent's authority hands off to the next.

---

## Product Manager

Turns product ideas and business goals into formal requirements.

| | |
|---|---|
| **Owns** | The Business Requirements Document (BRD) and the BRD folder — problem statement, user stories, acceptance criteria, business rules, prioritization, and the resolved compliance scope. |
| **Phase** | DEFINE. Feeds **Gate 1 (requirements/BRD)**. |
| **Run model** | In-context planning skill (works directly with you, the "CEO"). |

**Key inputs**

- The CEO interview — a structured conversation whose depth scales with the autonomy level (2–3 questions in Autopilot up to 8–12 across multiple rounds in Manual).
- A Polymath context package (`drydock/polymath/handoff/context-package.md`), if one exists, which shortens the interview to cover only the gaps.
- Domain research via web search when the space is unfamiliar.

**Key outputs**

- `drydock/product-manager/BRD/brd.md` — the canonical BRD, plus a living `INDEX.md` table of contents.
- Testable acceptance criteria (Given/When/Then) and unambiguous business rules.
- A **Compliance & Data Classification** section that is *always* resolved — even in Autopilot — capturing data types, geography, and customer segment, then mapping them to in-scope frameworks (or an explicit `out of scope: <framework> — no <signal>`).

**Does NOT do**

- Write code. It's a PM: it writes specs and verifies implementation against them. If you ask it to implement, it redirects to engineering.
- Make architecture or tech-stack decisions — that's the Solution Architect.
- Silently resolve compliance to "none." On an unsure answer it scopes the conservative framework set IN and tags it `confirm-with-compliance` for the compliance-officer.

:::warning Compliance is a blocking gate
The PM will not mark a BRD "Approved" while the Compliance & Data Classification section is missing or left as a TODO. The Solution Architect, security-engineer, and compliance-officer all *read* that scope and will design the wrong controls without it.
:::

---

## Solution Architect

Designs the system when you need to decide tech stack, API contracts, data models, or infrastructure shape.

| | |
|---|---|
| **Owns** | System architecture — Architecture Decision Records (ADRs), API contracts, data models, the performance budget, and the project scaffold. |
| **Phase** | DEFINE. Feeds **Gate 2 (architecture)**, which includes an explicit user review of the design. |
| **Run model** | In-context planning skill. |

**Key inputs**

- The approved BRD (including its compliance scope).
- `drydock/.orchestrator/codebase-context.md` in `brownfield` mode — existing patterns, tech stack, and API structure to design *around* rather than replace.
- The autonomy level, which sets discovery depth (auto-derive in Autopilot up to a full tech-stack walkthrough with cost modeling in Manual).

**Key outputs**

- ADRs under `docs/architecture/architecture-decision-records/`, system diagrams, and `tech-stack.md`.
- API contracts in `api/` (OpenAPI/gRPC/AsyncAPI) using reusable RFC 9457 `Problem`, `IdempotencyKey`, and `CursorPage` schemas — validated and linted before handoff.
- Data models in `schemas/` (ERD + SQL migrations) and a generated project scaffold.
- Three artifacts produced at **every** autonomy level: `docs/architecture/performance-budget.yaml` (the single source of truth that frontend/qa/sre/devops read), a `Compliance & Controls` design subsection, and a resolved feature-flag provider.

**Does NOT do**

- Write or change requirements — it derives from the BRD; the PM owns "what."
- Pick an architecture from a template. The pattern is *derived* from constraints (scale, team, budget, compliance) via a fitness function run first.
- Name a regulation without designing the control. It designs audit-log/encryption/RBAC/retention/residency/consent into the system; the compliance-officer maps and verifies.
- Hand off an unvalidated spec — it blocks handoff until the OpenAPI validator and Spectral lint both pass.

---

## UX Designer

Turns an approved BRD into the experience of *how* the product feels.

| | |
|---|---|
| **Owns** | User research, information architecture, interaction & motion design, and the **design-system SPECIFICATION** the frontend-engineer implements. |
| **Phase** | Runs between DEFINE and BUILD — after the BRD is approved and *before* the frontend-engineer writes code. |
| **Run model** | Isolated subagent. |

**Key inputs**

- `drydock/product-manager/BRD/` — the critical input (problem, personas, user stories, acceptance criteria, scope, compliance scope). If the BRD is missing or unapproved, it stops and requests it.
- Brownfield context: an existing design system, brand, or component library to *extend* rather than compete with.
- Live competitor and standards research via web search (every market/standard claim is cited to a source retrieved that session, never recalled from memory).

**Key outputs** (under `docs/design/`)

- Research synthesis — personas, jobs-to-be-done, and a cited competitive UX teardown.
- Information architecture — sitemap, navigation model, end-to-end user flows, and wireframe specs with enumerated empty/loading/error/success states.
- The **design-system spec** — tokens, a numbered type scale, a WCAG 2.1 AA color system (every text foreground/background pair computed and recorded as pass/fail), per-component states/variants, and brand direction. This is the handoff artifact.
- Interaction & motion specs (with `prefers-reduced-motion` fallbacks) and a usability/accessibility plan with measurable success metrics.

**Does NOT do**

- Write frontend code, token TypeScript, or Tailwind config — it hands over the **spec** (values + intent); the frontend-engineer writes the code in `frontend/`.
- Invent or rewrite requirements — if it finds a requirement gap or untestable criterion, it raises a finding for the PM rather than editing the BRD.
- Design API contracts, data models, or backend behavior — that's the Solution Architect / software-engineer.

:::note The boundary that matters most
UX produces the **specification**; the frontend-engineer produces the **code**. UX writes `docs/design/design-system/tokens.md` as named values and intent; the frontend-engineer reads it and implements `frontend/app/styles/tokens/*.ts` from it.
:::

---

## Polymath

The thinking partner for when you're not sure *what* to build or *how* — before committing to code.

| | |
|---|---|
| **Owns** | Understanding. It produces research, analysis, explanation, and dialogue — then hands off to the right executor when you're ready. |
| **Phase** | No fixed phase. It runs *before* the pipeline (direct exploration or pre-flight), and *during* it as a gate companion. |
| **Run model** | In-context planning skill — the only agent designed for genuine dialogue; every other agent executes a defined pipeline. |

**Three ways it activates**

1. **Direct** — you lead with "help me think about…", "what are my options", "explain this codebase." It researches first, then presents direction options.
2. **Pre-flight** — the orchestrator runs a readiness assessment before starting the PM. If it detects gaps (vague scope, no constraints, contradictions, an unoriented codebase), it invokes the Polymath for a quick consultation.
3. **Gate companion** — when you pick "Chat about this" at an approval gate, it reads the artifacts, explains the decision in plain language with trade-offs, then re-presents the original gate options unchanged.

**Key inputs**

- Read access to *any* artifact in the system (all `drydock/*/` workspaces, project-root deliverables, `.drydock.yaml`, `CLAUDE.md`) to inform its advice.
- Live web search — its primary superpower for current market, pricing, tech, and regulatory claims that training data gets wrong.

**Key outputs** (written only to `drydock/polymath/`)

- `context/repo-map.md`, `context/domain-research.md`, `context/decisions.md`, and timestamped `research/` notes.
- `handoff/context-package.md` — the crystallized context that travels into the pipeline. The PM reads it for a shorter interview; the Solution Architect reads the domain research; the orchestrator reads the decision log to skip redundant discovery.

**Does NOT do**

- Execute. It writes no production code, creates no infrastructure, runs no pipelines — it hands off to an executor instead.
- Modify other agents' outputs or project source. It is **read-only on everything except `drydock/polymath/`**.
- Block you or make decisions for you. If you select "skip — just build it" at any point, it hands off immediately. At gates, it explains and presents options but never decides on your behalf.

---

## How they hand off

```text
Polymath (optional)  →  Product Manager  →  Solution Architect  →  UX Designer  →  BUILD
   understanding          BRD + scope         architecture          design-system    (frontend/backend
   + context package      (Gate 1)            (Gate 2)              spec              engineers)
```

- The **Polymath** crystallizes a fuzzy idea into a context package, shortening everything downstream — then gets out of the way.
- The **Product Manager** turns that into an approved BRD with a resolved compliance scope (Gate 1).
- The **Solution Architect** derives the architecture from BRD constraints and emits the performance budget and control design (Gate 2).
- The **UX Designer** turns the approved BRD into the design-system spec the BUILD-phase engineers implement.

:::tip Next
See [how it works](/docs/concepts/how-it-works) for the full six-phase pipeline and the three approval gates, or the [build & harden agents](/docs/agents/engineering) for the engineers that consume these artifacts.
:::
