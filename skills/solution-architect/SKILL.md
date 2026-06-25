---
name: solution-architect
description: >
  [shipyard internal] Designs system architecture when you need to
  decide tech stack, API contracts, data models, or infrastructure shape.
  Routed via the shipyard orchestrator.
---

# Solution Architect

## Protocols

!`cat Shipyard/.protocols/ux-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/input-validation.md 2>/dev/null || true`
!`cat Shipyard/.protocols/tool-efficiency.md 2>/dev/null || true`
!`cat Shipyard/.protocols/visual-identity.md 2>/dev/null || true`
!`cat Shipyard/.protocols/freshness-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/receipt-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/boundary-safety.md 2>/dev/null || true`
!`cat Shipyard/.protocols/conflict-resolution.md 2>/dev/null || true`
!`cat Shipyard/.protocols/grounding-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/security-defaults.md 2>/dev/null || true`
!`cat Shipyard/.protocols/compliance-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/architecture-boundaries.md 2>/dev/null || true`
!`cat Shipyard/.protocols/observability-contract.md 2>/dev/null || true`
!`cat .shipyard.yaml 2>/dev/null || echo "No config — using defaults"`
!`cat Shipyard/.orchestrator/codebase-context.md 2>/dev/null || true`

**Fallback (if protocols not loaded):** Use AskUserQuestion with options (never open-ended), "Chat about this" last, recommended first. Work continuously. Print progress constantly. Validate inputs before starting — classify missing as Critical (stop), Degraded (warn, continue partial), or Optional (skip silently). Use parallel tool calls for independent reads. Use smart_outline before full Read.

## Brownfield Awareness

If `Shipyard/.orchestrator/codebase-context.md` exists and mode is `brownfield`:
- **READ existing architecture first** — understand current patterns, tech stack, API structure
- **Design around existing code** — new architecture extends the system, doesn't replace it
- **Document existing patterns in ADRs** — capture what's already decided
- **API contracts must be backward-compatible** — new endpoints, not breaking changes
- **Don't redesign what works** — focus architecture on the NEW features/requirements

## Engagement Mode

!`cat Shipyard/.orchestrator/settings.md 2>/dev/null || echo "No settings — using Standard"`

Read `Shipyard/.orchestrator/settings.md` at startup. Adapt discovery depth:

| Mode | Discovery Approach |
|------|-------------------|
| **Express** | Auto-derive from BRD. Ask only if critical info missing. Conservative defaults. |
| **Standard** | 5-7 questions across 2 rounds. Scale sizing + constraints. Fitness-derived architecture. |
| **Thorough** | 12-15 questions across 4 structured rounds. Full capacity planning. Trade-off analysis. Architecture alternatives. |
| **Meticulous** | Everything in Thorough + individual ADR approval, tech stack walkthrough, capacity modeling with cost estimates. |

### Always-Resolved Defaults (every mode, never Thorough-gated)

Regardless of engagement mode — including Express — these three artifacts are ALWAYS produced. They are DERIVED from the scale, data-type, and customer-segment answers (or, in Express, auto-derived from BRD signals + conservative defaults). They are never gated behind Thorough/Meticulous-only rounds, because frontend/qa/sre/devops/software-engineer skills READ them and will hardcode wrong values if they are absent:

| Always-resolved artifact | How it is resolved even in Express | Owner contract |
|--------------------------|-------------------------------------|----------------|
| **Performance budget** — `docs/architecture/performance-budget.yaml` | Map the chosen scale + data-pattern to the default budget table in Phase 4 (e.g. small/balanced-CRUD → p95 500ms, LCP 2500ms, bundle 200KB). If no scale signal, use the small/balanced row. | solution-architect EMITS; frontend/qa/sre/devops READ — never hardcode 500ms/200KB. |
| **Compliance scope** — `Compliance & Controls` subsection + scoped framework set | Run the deterministic product-signals → frameworks map from `compliance-protocol.md` against BRD/security PII signals. No signal → record `out of scope: <framework> — no <signal>` (an explicit empty scope is still a resolved scope). | solution-architect designs CONTROLS into the design; compliance-officer maps/verifies. |
| **Feature-flag provider** — flag client + registry contract | Always resolve an OpenFeature-based provider with an env/config fallback and per-flag safe defaults (`libs/shared/feature-flags/`, `config/feature-flags.yaml`). In Express, default to the env/config provider with no external service. | software-engineer OWNS the client; architect records the provider choice + fallback in an ADR. |

Log on resolution: `✓ Defaults resolved — perf-budget {row}, compliance {frameworks|none}, flag-provider {provider}`.

## Progress Output

Follow `Shipyard/.protocols/visual-identity.md`. Print structured progress throughout execution.

**Skill header** (print on start):
```
━━━ Solution Architect ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Phase progress** (print during execution):
```
  [1/5] Constraint Discovery
    ✓ Scale: {users}, {CCU}, {constraints}
    ⧖ analyzing compliance requirements...
    ○ fitness function

  [2/5] Architecture Design
    ✓ Pattern: {pattern}, {N} ADRs
    ⧖ generating system diagrams...
    ○ user review

  [3/5] API Contracts
    ✓ {N} OpenAPI specs, {M} endpoints
    ⧖ defining error schemas...
    ○ versioning strategy

  [4/5] Data Model
    ✓ ERD: {N} entities, {M} migrations
    ⧖ writing migration files...
    ○ audit trail schema

  [5/5] Scaffold
    ✓ Project structure generated
    ⧖ writing Dockerfiles...
    ○ docker-compose
```

**Completion summary** (print on finish — MUST include concrete numbers):
```
✓ Solution Architect    {pattern}, {N} ADRs, {M} endpoints, scaffold generated    ⏱ Xm Ys
```

## Overview

Full architecture pipeline: from business requirements to a scaffolded, production-ready codebase. The architecture is DERIVED from project constraints (scale, team, budget, compliance) — not picked from a template. There is no one-size-fits-all architecture.

Generates architecture deliverables at the project root (`api/`, `schemas/`, `docs/architecture/`, project scaffold) with workspace artifacts in `Shipyard/solution-architect/`.

## Config Paths

Read `.shipyard.yaml` at startup. Use these overrides if defined:
- `paths.api_contracts` — default: `api/`
- `paths.adrs` — default: `docs/architecture/architecture-decision-records/`
- `paths.architecture_docs` — default: `docs/architecture/`
- `paths.erd` — default: `schemas/erd.md`
- `paths.migrations` — default: `schemas/migrations/`
- `paths.tech_stack` — default: `docs/architecture/tech-stack.md`

Deliverables go to the **project root** (`api/`, `schemas/`, `docs/architecture/`). Workspace artifacts go to `Shipyard/solution-architect/`.

## When to Use

- Designing a new SaaS product or platform
- Planning microservices or service-oriented architecture
- Selecting tech stacks for production systems
- Creating API contracts and data models
- Scaffolding multi-cloud, production-ready projects
- Architecture review or modernization of existing systems

## Process Flow

```dot
digraph sa {
    rankdir=TB;
    "Triggered" [shape=doublecircle];
    "Phase 1: Discovery" [shape=box];
    "Phase 2: Architecture Design" [shape=box];
    "Phase 3: Tech Stack" [shape=box];
    "Phase 4: API Contracts" [shape=box];
    "Phase 5: Data Models" [shape=box];
    "Phase 6: Scaffold" [shape=box];
    "User Review" [shape=diamond];
    "Suite Complete" [shape=doublecircle];

    "Triggered" -> "Phase 1: Discovery";
    "Phase 1: Discovery" -> "Phase 2: Architecture Design";
    "Phase 2: Architecture Design" -> "User Review";
    "User Review" -> "Phase 2: Architecture Design" [label="revise"];
    "User Review" -> "Phase 3: Tech Stack" [label="approved"];
    "Phase 3: Tech Stack" -> "Phase 4: API Contracts";
    "Phase 4: API Contracts" -> "Phase 5: Data Models";
    "Phase 5: Data Models" -> "Phase 6: Scaffold";
    "Phase 6: Scaffold" -> "Suite Complete";
}
```

## Phase 1: Discovery & Scale Assessment

The architecture must fit the project's actual constraints. This phase gathers those constraints — at a depth matching the engagement mode.

### Step 1: Read Existing Context

Before asking ANY questions, read in parallel:
1. `Shipyard/polymath/handoff/context-package.md` — may contain scale, constraints, decisions
2. `Shipyard/product-manager/BRD/brd.md` — user stories, acceptance criteria, business rules
3. `Shipyard/.orchestrator/codebase-context.md` — brownfield context

**Reduce questions to cover ONLY gaps not addressed in existing context.** If polymath or PM already established scale targets, do not re-ask.

### Step 2: Scale & Fitness Interview

Adapt depth to engagement mode. Use AskUserQuestion with structured options (never open-ended).

#### Express Mode

Skip interview entirely. Auto-derive from BRD signals:
- User count hints from user stories -> default to "small" (< 1K users) if no signals
- Tech mentions in BRD or polymath context -> use those, else conservative defaults
- Default: modular monolith, managed services, single region, single DB
- Log: `✓ Express mode — auto-deriving architecture from BRD`

If a critical constraint is completely missing (e.g., BRD mentions "enterprise customers" but no scale number), ask ONE clarifying question maximum.

#### Standard Mode (2 rounds)

**Round 1 — Scale & Users:**

```python
AskUserQuestion(questions=[{
  "question": "I need to understand your scale to design the right architecture.\n\n"
    "These 3 questions determine whether you need a simple monolith or a distributed system.",
  "header": "Scale & Users",
  "options": [
    {"label": "Small scale — < 1K users, MVP or internal tool", "description": "Simple architecture, minimal infra, fast to build"},
    {"label": "Medium scale — 1K-100K users, startup/growth", "description": "Needs to scale but not from day 1. Service extraction plan."},
    {"label": "Large scale — 100K+ users, high availability", "description": "Distributed architecture, multi-region, serious infrastructure"},
    {"label": "Not sure — help me estimate", "description": "I'll ask a few questions to figure this out"},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": false
}])
```

Follow up with:

```python
AskUserQuestion(questions=[{
  "question": "What's the primary data pattern?",
  "header": "Data Characteristics",
  "options": [
    {"label": "Read-heavy — dashboards, content, catalogs", "description": "Cache-first, read replicas, CDN"},
    {"label": "Write-heavy — logging, IoT, transactions", "description": "Queue-based, event sourcing, eventual consistency"},
    {"label": "Balanced — typical CRUD SaaS", "description": "Standard request/response, relational DB"},
    {"label": "Real-time — chat, collaboration, live updates", "description": "WebSocket/SSE, pub/sub, in-memory state"},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": false
}])
```

**Round 2 — Constraints:**

```python
AskUserQuestion(questions=[{
  "question": "Who will build and maintain this system?",
  "header": "Team & Budget",
  "options": [
    {"label": "Solo or pair — keep it simple", "description": "Monolith, managed services, minimal ops"},
    {"label": "Small team (3-5) — some specialization", "description": "Can handle moderate complexity"},
    {"label": "Medium team (6-15) — dedicated roles", "description": "Can support microservices if needed"},
    {"label": "Large team (15+) — multiple squads", "description": "Service ownership model, independent deploys"},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": false
}])
```

```python
AskUserQuestion(questions=[{
  "question": "Any hard constraints? Select every regulatory regime that applies — the six deterministic compliance signals can co-occur (e.g. GDPR + CCPA + SOC2).",
  "header": "Compliance & Deployment",
  "options": [
    {"label": "No special requirements", "description": "Standard web app, no regulatory burden"},
    {"label": "GDPR — EU user data", "description": "Data residency, right to deletion, consent management"},
    {"label": "CCPA / CPRA — California consumers", "description": "Do-not-sell/share opt-out, data-category lookback, consumer access requests"},
    {"label": "SOC2 / ISO 27001 — enterprise customers", "description": "Audit trails, access controls, security policies"},
    {"label": "HIPAA — health data", "description": "BAA required, encryption everywhere, dedicated tenancy"},
    {"label": "PCI DSS — payment data", "description": "Tokenization, network segmentation, quarterly scans"},
    {"label": "FedRAMP — US federal customers", "description": "Authorization boundary, NIST 800-53 baseline, continuous monitoring"},
    {"label": "Other (specify)", "description": "Select to describe additional requirements"},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": true
}])
```

#### Thorough Mode (4 rounds)

Everything in Standard, PLUS two additional rounds:

**Round 3 — Technical Requirements:**

```python
AskUserQuestion(questions=[{
  "question": "Let's get precise about performance and availability requirements.",
  "header": "Performance & Availability",
  "options": [
    {"label": "Standard SaaS — 99.9% uptime, < 500ms API response", "description": "8.7 hours downtime/year. Typical for most web apps."},
    {"label": "High availability — 99.99% uptime, < 200ms response", "description": "52 minutes downtime/year. Requires multi-AZ, automated failover."},
    {"label": "Mission critical — 99.999% uptime, < 100ms response", "description": "5 minutes downtime/year. Requires multi-region, chaos engineering."},
    {"label": "Internal tool — best effort, availability not critical", "description": "Simplest architecture, no redundancy required."},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": false
}])
```

```python
AskUserQuestion(questions=[{
  "question": "Where are your users?",
  "header": "Geographic Distribution",
  "options": [
    {"label": "Single country", "description": "One region deployment, simplest"},
    {"label": "Single continent", "description": "One region with CDN for static assets"},
    {"label": "Global — users everywhere", "description": "Multi-region, edge CDN, data replication strategy"},
    {"label": "Not sure yet", "description": "I'll design for single-region with a multi-region migration path"},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": false
}])
```

```python
AskUserQuestion(questions=[{
  "question": "Expected peak concurrent users (CCU)?",
  "header": "Peak Load",
  "options": [
    {"label": "< 100 CCU", "description": "Single instance can handle this"},
    {"label": "100-1K CCU", "description": "Horizontal scaling, load balancer needed"},
    {"label": "1K-10K CCU", "description": "Auto-scaling, connection pooling, caching layer"},
    {"label": "10K+ CCU", "description": "Distributed architecture, queue-buffered writes, edge computing"},
    {"label": "Help me estimate", "description": "Typically 5-10% of total users are concurrent at peak"},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": false
}])
```

**Round 4 — Strategic:**

```python
AskUserQuestion(questions=[{
  "question": "How do you see this system evolving?",
  "header": "Growth & Extensibility",
  "options": [
    {"label": "Steady linear growth", "description": "Predictable scaling, plan for 10x over 2 years"},
    {"label": "Hockey stick — potential viral growth", "description": "Must handle 100x spikes, auto-scaling critical"},
    {"label": "Seasonal — predictable traffic spikes", "description": "Scale-to-zero between peaks, burst capacity"},
    {"label": "Platform play — third parties will build on this", "description": "Public API, webhooks, rate limiting, developer portal"},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": false
}])
```

```python
AskUserQuestion(questions=[{
  "question": "Monthly infrastructure budget ceiling?",
  "header": "Budget",
  "options": [
    {"label": "Minimal — under $500/mo", "description": "Serverless, managed DBs, free tiers. Optimize for cost."},
    {"label": "Moderate — $500 to $5K/mo", "description": "Managed K8s, dedicated DBs, standard monitoring."},
    {"label": "Significant — $5K+/mo", "description": "Dedicated infra, custom observability, multi-region."},
    {"label": "Not a constraint", "description": "Optimize for performance and reliability, not cost."},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": false
}])
```

```python
AskUserQuestion(questions=[{
  "question": "Cloud strategy?",
  "header": "Vendor & Portability",
  "options": [
    {"label": "All-in on AWS (cheapest, most managed services)", "description": "Use AWS-native services. Fast to build, harder to migrate."},
    {"label": "All-in on GCP (best for data/ML workloads)", "description": "Use GCP-native services. Strong managed K8s."},
    {"label": "All-in on Azure (best for enterprise/Microsoft shops)", "description": "Use Azure-native services. AD integration."},
    {"label": "Cloud-agnostic (most portable, higher upfront cost)", "description": "Terraform abstractions, avoid proprietary services."},
    {"label": "Not sure — recommend based on my project", "description": "I'll recommend based on your requirements"},
    {"label": "Chat about this", "description": "Free-form input"}
  ],
  "multiSelect": false
}])
```

#### Meticulous Mode

Everything in Thorough, PLUS:
- After the fitness function produces an architecture, present **2-3 alternative architectures** with explicit trade-off tables (cost vs complexity vs scalability vs team fit) before the user chooses
- **Individual ADR approval**: present each ADR separately. User reviews and approves each decision.
- **Capacity modeling**: estimate infrastructure cost at current scale AND 10x projected scale
- **Tech stack walkthrough**: for each major tech choice, present 2-3 alternatives with rationale

### Step 3: Architecture Fitness Function

After gathering inputs, DERIVE the architecture from constraints. The architecture is a FUNCTION of the inputs — not a template.

**Architecture Pattern:**

| Scale | Team | -> Pattern |
|-------|------|------------|
| < 1K users | 1-3 people | **Monolith** or **Modular Monolith**. Single deploy, single DB. Docker Compose for local dev. |
| 1K-100K users | 3-15 people | **Modular Monolith** with documented service boundaries. Extract services ONLY when team or scale demands. Include service extraction plan in ADR. |
| 100K+ users | 15+ people | **Microservices**. Service mesh, distributed data, event-driven communication. Each team owns 1-3 services. |
| Any scale | Solo developer | Whatever is simplest. Serverless or monolith. Managed everything. Minimize operational burden. |

**Infrastructure Sizing:**

| Budget | -> Infrastructure Strategy |
|--------|---------------------------|
| < $500/mo | Serverless-first (Lambda/Cloud Run), managed DB (RDS free tier/PlanetScale), no K8s, CloudWatch/basic monitoring |
| $500-5K/mo | Managed K8s (EKS/GKE) or ECS, managed DB with replicas, Redis cache, standard monitoring (Grafana/Datadog) |
| > $5K/mo | Dedicated infrastructure, self-hosted options viable, custom observability stack, multi-region possible |

**Data Architecture:**

| Data Pattern | -> Strategy |
|-------------|-------------|
| Read-heavy (>80% reads) | Cache-first (Redis), read replicas, CDN for static, materialized views |
| Write-heavy | Event sourcing or CQRS, queue-buffered writes (SQS/Kafka), eventual consistency |
| Real-time | WebSocket/SSE infrastructure, pub/sub (Redis Pub/Sub or Kafka), in-memory state |
| Balanced CRUD | Standard relational DB, connection pooling, query optimization |

**Compliance Impact** (ILLUSTRATIVE ONLY — directional architecture cues, NOT the authoritative map):

> This table sketches the *shape* of the architectural change each regime tends to demand, to steer the fitness function. It is **not** the source of truth and intentionally omits specifics. The single source of truth for which frameworks are in scope and which controls are mandatory is the deterministic **product-signals → frameworks** map in `Shipyard/.protocols/compliance-protocol.md`, materialized in the Phase 2 **Compliance & Controls** subsection (which designs the concrete controls in). Any specific scan cadence, breach-notification window, control id, article, or §-citation is **NOT** stated here and MUST be verified LIVE per `freshness-protocol.md` in that subsection — never from memory (the same BINDING freshness rule the Compliance & Controls subsection carries). compliance-officer later maps/verifies those controls to evidence.

| Requirement | -> Architecture cue (illustrative) |
|------------|------------------------|
| GDPR | Data residency controls, right-to-deletion pipeline, consent management, PII encryption |
| CCPA / CPRA | Do-not-sell/share opt-out plumbing, data-category lookback support, consumer access/deletion requests |
| SOC2 / ISO 27001 | Audit trail on all mutations, RBAC, centralized logging, access review automation |
| HIPAA | Dedicated tenancy, encryption at rest + transit, BAA with all vendors, audit logging, no shared infrastructure |
| PCI DSS | Tokenize card data (use Stripe/Adyen), network segmentation, periodic vulnerability scanning, no raw card storage |
| FedRAMP | Defined authorization boundary, NIST 800-53-aligned control baseline, continuous monitoring, US-region/data-handling boundaries |

**Availability Impact:**

| SLA | -> Architecture Changes |
|-----|------------------------|
| 99% (3.7 days/yr) | Single instance OK, basic health checks |
| 99.9% (8.7 hrs/yr) | Multi-AZ, load balancer, automated restarts, basic monitoring |
| 99.99% (52 min/yr) | Multi-AZ with automated failover, zero-downtime deploys, chaos engineering, comprehensive monitoring |
| 99.999% (5 min/yr) | Multi-region active-active, global load balancing, circuit breakers everywhere, dedicated SRE |

**Growth Model Impact:**

| Growth | -> Architecture Changes |
|--------|------------------------|
| Linear/steady | Plan for 10x. Vertical scaling first, horizontal when needed. |
| Hockey stick | Horizontal scaling from day 1. Stateless services. Auto-scaling groups. Queue-buffered writes. Feature flags for load shedding. |
| Seasonal | Scale-to-zero capable (serverless/spot instances). Pre-warming automation. Burst capacity planning. |
| Platform/API | API gateway, rate limiting, webhook system, developer portal, backwards-compatible versioning from day 1. |

**Present the derived architecture:** "Based on your constraints [summary], here's what fits and why..."

For **Thorough/Meticulous** modes, also present 1-2 alternative architectures:
- **Conservative alternative**: simpler, faster to build, may need rework at scale
- **Ambitious alternative**: handles more future growth, higher upfront complexity and cost

Each alternative includes a trade-off summary: build time, operational complexity, monthly cost estimate, scaling ceiling, team fit.

## Phase 2: Architecture Design

Generate architecture documents in `docs/architecture/` (or `paths.architecture_docs` from config):

### architecture-decision-records/
One ADR per major decision using this template:
```markdown
# ADR-NNN: [Title]
**Status:** Accepted | Superseded | Deprecated
**Context:** Why this decision is needed
**Decision:** What we chose and why
**Consequences:** Trade-offs accepted
**Alternatives Considered:** What we rejected and why
```

Required ADRs:
- Architecture pattern (monolith, microservices, modular monolith, event-driven)
- **Architecture-style & layering ADR (REQUIRED, per `architecture-boundaries.md`)** — see below
- Communication patterns (sync REST/gRPC, async messaging, CQRS)
- Data strategy (shared DB, DB-per-service, event sourcing)
- Auth architecture (JWT, OAuth2, session-based)
- Multi-tenancy strategy (row-level, schema-level, DB-level)
- Feature-flag provider ADR (OpenFeature provider + env/config fallback + per-flag safe defaults, per the always-resolved defaults above)

#### Architecture-Style & Layering ADR (REQUIRED — emit `ADR-NNN-architecture-style.md`)

Emit an ADR that documents the Clean/Hexagonal layering and the **dependency-direction rule** per `Shipyard/.protocols/architecture-boundaries.md`. It is the design-time source of truth for the boundary that software-engineer enforces MECHANICALLY (`make arch`, exit non-zero on violation) — the architect declares the law; the engineer wires the fitness function. The ADR MUST state:

- The layer stack innermost→outermost: **domain** (entities/value-objects/business rules, zero framework/IO imports) → **application** (use-cases + PORT interfaces) → **infrastructure/adapters** (frameworks, DB drivers, HTTP clients, ORMs, SDKs).
- **The one law:** source-code dependencies (imports) point INWARD only; a framework/ORM/HTTP/DB import in the domain is a HIGH-severity, build-blocking violation.
- **Ports owned inside, adapters bound at the composition root** — use-cases receive ports via constructor/parameter injection; only `main`/bootstrap/DI module names concrete adapters.
- A pointer to the per-language fitness function software-engineer will emit (`.dependency-cruiser.js` / ArchUnit / `.importlinter` / `deptrac.yaml` / `.go-arch-lint.yml`) and the `make arch` CI gate. Note explicitly: **the architect does not implement the lint; it specifies the rule the lint must encode.**

#### Compliance & Controls (REQUIRED subsection — design controls in, do not just name regulations)

Consume `Shipyard/.protocols/compliance-protocol.md`. Run the deterministic **product-signals → frameworks** map against the BRD, the security-engineer PII inventory (if present), and any `compliance:` block in `.shipyard.yaml`. This subsection is ALWAYS produced (see Always-Resolved Defaults) — when no signal scopes a framework, record `out of scope: <framework> — no <signal>` so the empty scope is auditable.

When a signal indicates regulated data, the architect DESIGNS the required CONTROLS into the system design (not advice — concrete architecture) and records them in a control table:

| Control area | Designed-in mechanism (record the concrete design decision) |
|--------------|--------------------------------------------------------------|
| Audit logging | Append-only audit trail on all mutations (who/what/when/before-after); tamper-evident store; which entities are audited |
| Encryption at rest | KMS-backed envelope encryption for PII/PHI columns + storage; key rotation policy; which fields |
| Encryption in transit | TLS 1.2+ everywhere incl. service-to-service; mTLS where the framework requires dedicated tenancy |
| RBAC / authorization | Role model + per-object (default-deny) authz design feeding `security-defaults.md`; tenant + object-id checks at the data layer |
| Retention & deletion | Retention windows per data class; right-to-erasure / right-to-delete pipeline (GDPR/CCPA); soft-delete vs hard-delete policy |
| Data residency | Region pinning + replication boundaries for EU/regulated data; where data may and may not flow |
| Consent | Consent capture + lawful-basis recording (GDPR Arts. 5–11) where personal data is processed |

- **Freshness rule (BINDING):** any specific control id, article number, §-citation, or statutory clock (e.g. GDPR 72-hour breach notice, HIPAA breach notice window) is verified LIVE against the official source this session per `compliance-protocol.md` — NEVER written from memory. If it cannot be verified live, mark it `not verified`; do not fabricate.
- Each designed control becomes an Implementing-artifact target the compliance-officer will later map to evidence (`path:line`). The architect's job is to ensure the design HAS a place for each mandatory control.

### system-diagrams/
Create Mermaid diagrams in markdown files:
- **C4 Context** — system boundaries and external actors
- **C4 Container** — services, databases, message brokers, CDN
- **Sequence diagrams** — for critical user flows (auth, payment, data pipeline)
- **Infrastructure topology** — cloud resources and networking

### Design Principles
Apply and document these production patterns:
- **12/15-Factor App methodology** — explicit design intent, documented factor-by-factor in `design-principles.md`. Config strictly from the environment (no config in code), strict dev/prod parity, stateless processes, port binding, disposability/graceful shutdown, logs as event streams to **stdout** (per `observability-contract.md` — the app never owns log files/rotation). Carry the 15-factor extensions: **API-first**, **telemetry** (RED metrics + traces + structured logs per the observability contract), and **authentication/authorization as a first-class concern** (per `security-defaults.md`).
- Defense in depth (security layers) — aligns with `security-defaults.md` (input validation at the boundary, parameterized queries, output encoding, SSRF allowlist, secrets from env/secret-manager, per-object default-deny authz, security headers + strict CORS + secure cookies)
- Clean/Hexagonal layering with inward-only dependencies (see the Architecture-Style & Layering ADR; mechanically enforced by software-engineer)
- Circuit breaker, retry, timeout patterns
- Idempotency for all write operations (realized as the reusable `IdempotencyKey` header contract in Phase 4)
- Eventual consistency where appropriate
- Zero-trust networking

### Phase 2 Quality Bar (gate — do not proceed to Phase 3 until all true)

- [ ] Architecture-style & layering ADR emitted, declaring the inward-only dependency-direction law + the `make arch` gate software-engineer will enforce.
- [ ] Feature-flag provider ADR emitted (OpenFeature provider + env/config fallback + per-flag safe defaults).
- [ ] `Compliance & Controls` subsection produced with a resolved scope (frameworks scoped IN, or explicit `out of scope — no <signal>`); any cited control id/article/clock is `[verified]` live or marked `not verified`.
- [ ] 12/15-factor design intent documented factor-by-factor in `design-principles.md`.
- [ ] **`security-defaults checklist passes`** — the design leaves a concrete place for every secure-by-default control (boundary validation, parameterized data access, per-object default-deny authz, secrets from env/secret-manager, security headers/CORS/cookies) so the BUILD agents can ship it without retrofit.

**Present architecture to user via AskUserQuestion for approval before proceeding.**

## Phase 3: Tech Stack Selection

Generate `docs/architecture/tech-stack.md` (or `paths.tech_stack` from config):

| Layer | Selection | Rationale |
|-------|-----------|-----------|
| Language(s) | Based on team/requirements | Performance, ecosystem, hiring |
| Framework | Based on language choice | Maturity, community, features |
| Database(s) | Based on data patterns | ACID vs BASE, query patterns |
| Cache | Redis/Memcached | Access patterns, consistency needs |
| Message Broker | Kafka/RabbitMQ/SQS/Pub-Sub | Throughput, ordering, durability |
| API Gateway | Kong/AWS API GW/GCP API GW | Rate limiting, auth, routing |
| Auth | Keycloak/Auth0/Cognito/Firebase Auth | SSO, MFA, compliance |
| Search | Elasticsearch/OpenSearch | Full-text, analytics, scale |
| Object Storage | S3/GCS/Azure Blob | Cost, lifecycle, CDN integration |
| CDN | CloudFront/Cloud CDN/Azure CDN | Edge locations, cost |

Selection criteria: production maturity, multi-cloud portability, team expertise, cost at scale.

## Phase 4: API Contract Design

Generate API contracts at `api/` (or `paths.api_contracts` from config) at the project root:

- **OpenAPI 3.1 specs** for REST APIs — complete with request/response schemas, auth, error codes
- **gRPC proto files** if inter-service communication is gRPC
- **AsyncAPI specs** for event-driven interfaces
- **API versioning strategy** documented (URL path vs header)

The architect OWNS the cross-skill API contracts below. software-engineer (runtime mapping), technical-writer (error table/docs), and code-reviewer (consume + verify) READ these — they are defined ONCE here as reusable OpenAPI components and `$ref`'d everywhere.

### Canonical error contract — RFC 9457 `Problem` (application/problem+json)

**Replace the bespoke `{code, message, details, trace_id}` envelope.** The canonical error contract is RFC 9457 `application/problem+json`. Define a single reusable component schema named **`Problem`** in `api/openapi/components.yaml` (or the shared `components` block) and `$ref` it from EVERY error response (4xx/5xx). The architect OWNS this schema.

```yaml
components:
  schemas:
    Problem:
      type: object
      description: RFC 9457 problem detail. The canonical error body for every 4xx/5xx response.
      required: [type, title, status]
      properties:
        type:     { type: string, format: uri-reference, default: "about:blank",
                    description: "URI reference identifying the problem type (stable per error code)." }
        title:    { type: string, description: "Short, human-readable summary; stable per type." }
        status:   { type: integer, format: int32, minimum: 100, maximum: 599 }
        detail:   { type: string, description: "Human-readable explanation specific to this occurrence." }
        instance: { type: string, format: uri-reference, description: "URI reference identifying this occurrence." }
        # standard extensions (cross-skill contract):
        trace_id: { type: string, description: "Correlation id; matches the observability-contract trace_id." }
        errors:
          type: array
          description: "Field-level validation errors."
          items:
            type: object
            properties:
              field:   { type: string, description: "Field name OR JSON Pointer (e.g. /items/0/qty)." }
              pointer: { type: string }
              detail:  { type: string }
```

Rules:
- Every error response sets **`Content-Type: application/problem+json`** and `$ref`s `#/components/schemas/Problem` — no inline error bodies, no second error shape anywhere in the spec.
- `trace_id` is the SAME correlation id as the observability contract's `trace_id` (read from the live span). Do not invent a parallel id.
- **Error catalog is the source of truth for the values.** `Problem.type`/`title`/`status` are populated at runtime from a single error-catalog module (`libs/shared/errors/catalog.*`) with entries `{ code, http_status, title, message_template, remediation, docs_anchor }`. BOTH the runtime mapper (app error → `Problem`) and the technical-writer's docs error table READ this one catalog. The architect specifies the catalog's existence + shape in an ADR / scaffold stub; software-engineer implements the mapping.

### Reusable `IdempotencyKey` header — REQUIRED on all unsafe POST/PATCH

Declare a reusable header parameter and require it on every non-idempotent mutation:

```yaml
components:
  parameters:
    IdempotencyKey:
      name: Idempotency-Key
      in: header
      required: true
      schema: { type: string, format: uuid }
      description: >
        Client-generated key. Replaying the same key with the SAME request returns the original
        result (replay). Reusing a key with a DIFFERENT request body returns 409 Conflict; a malformed
        key returns 422. Servers persist key→result for a documented retention window.
```

- Every unsafe `POST`/`PATCH` (and any non-idempotent `PUT`/`DELETE`) `$ref`s `parameters/IdempotencyKey` and documents `409` (key reuse with mismatched body) and `422` (malformed key) responses — both `$ref` `Problem`.
- This is the spec-level realization of the "idempotency for all write operations" design principle.

### Reusable `CursorPage<T>` pagination — REQUIRED on every list endpoint

Every list/collection endpoint returns the cursor-page envelope (cursor-based for production; `offset` only for admin/internal):

```yaml
components:
  schemas:
    PageInfo:
      type: object
      required: [has_more, limit]
      properties:
        next_cursor: { type: string, nullable: true, description: "Opaque cursor for the next page; null at the end." }
        has_more:    { type: boolean }
        limit:       { type: integer, minimum: 1 }
    # CursorPage<T> is composed per resource: data[] of T + page_info.
    # e.g. UserPage: { allOf: [ { properties: { data: { type: array, items: { $ref: '#/components/schemas/User' } },
    #                                            page_info: { $ref: '#/components/schemas/PageInfo' } } } ] }
```

- Shape is fixed: `data[]` (the items) + `page_info { next_cursor, has_more, limit }`. Every list endpoint `$ref`s `PageInfo` and supplies a typed `data[]`.

### OpenAPI Governance — validate + lint, BLOCK handoff until clean

After writing `api/openapi/*.yaml`, the spec is NOT handed off until it is **valid AND clean**:

1. **Structural validation** — run an OpenAPI 3.1 validator (e.g. `redocly lint` / `swagger-cli validate` / `openapi-spec-validator`). Spec must parse and be schema-valid.
2. **Spectral ruleset lint** — author/emit a default ruleset at **`api/.spectral.yaml`** (a new artifact this skill OWNS) and run `spectral lint api/openapi/*.yaml`. The default ruleset MUST assert at minimum:
   - extends `spectral:oas`;
   - every operation has an `operationId`, `summary`, and `tags`;
   - every `4xx`/`5xx` response `$ref`s `#/components/schemas/Problem` and uses `application/problem+json`;
   - every unsafe `POST`/`PATCH` references `parameters/IdempotencyKey`;
   - every list/array-returning operation uses the `PageInfo`/cursor-page envelope;
   - no inline error schemas; security scheme declared; no `$ref` to undefined components.
3. **BLOCKING gate:** any validator error or Spectral error blocks the phase. Handoff to software-engineer/technical-writer happens only on validator exit 0 AND `spectral lint` with zero errors (warnings recorded). Cite the actual tool output — never assert "the spec is clean" without an observed exit 0.

### Performance Budget Artifact — `docs/architecture/performance-budget.yaml` (single source of truth)

Emit `docs/architecture/performance-budget.yaml` per the shared PERFORMANCE BUDGET contract. This is the ONE place perf targets live; frontend/qa/sre/devops READ it and MUST NOT hardcode 500ms/200KB. It is ALWAYS emitted (see Always-Resolved Defaults) — even in Express/Standard mode resolve a sensible default from the chosen scale + data-type.

Shape:
```yaml
# docs/architecture/performance-budget.yaml
api:
  "GET /users/{id}":      { p95_ms: 300, p99_ms: 800, throughput_rps: 200, error_rate_pct: 0.5 }
  "POST /orders":         { p95_ms: 500, p99_ms: 1200, throughput_rps: 100, error_rate_pct: 1.0 }
web_vitals:
  lcp_ms: 2500
  inp_ms: 200
  cls: 0.1
bundle:
  main:   { max_kb: 200 }
  vendor: { max_kb: 350 }
```

**Default-resolution table** (apply when the user gives no explicit numbers — derive from scale + data-pattern; route-level rows default to the per-tier API row):

| Scale / data-type | api p95 / p99 (ms) | throughput (rps) | error_rate (%) | web_vitals (lcp/inp/cls) | bundle main (KB) |
|-------------------|--------------------|--------------------|------------------|--------------------------|-------------------|
| Small / balanced-CRUD (default) | 500 / 1200 | 50 | 1.0 | 2500 / 200 / 0.1 | 200 |
| Medium / read-heavy | 300 / 800 | 200 | 0.5 | 2000 / 200 / 0.1 | 200 |
| Medium / write-heavy | 500 / 1500 | 150 | 1.0 | 2500 / 200 / 0.1 | 200 |
| Large / high-availability | 200 / 500 | 1000 | 0.1 | 1800 / 150 / 0.1 | 180 |
| Real-time | 150 / 400 | 500 | 0.5 | 2000 / 100 / 0.1 | 200 |

These align with the latency/availability rows in the Phase 1 fitness function and the `http_request_duration_seconds` instrument in `observability-contract.md` (note the budget is in **ms** for human-readability; the runtime histogram is in **seconds**).

Standards enforced:
- **Canonical error body is RFC 9457 `Problem`** (above) — no `{code, message, details, trace_id}` envelope.
- Pagination via the reusable `CursorPage<T>` / `PageInfo` envelope (`cursor-based` for production, `offset` only for admin).
- Idempotency via the reusable `IdempotencyKey` header on all unsafe writes.
- Rate limiting headers (`X-RateLimit-*`)
- Request ID propagation (`X-Request-ID`) — echoed into the log `request_id` field per the observability contract.

### Phase 4 Quality Bar (gate — do not hand off until all true)

- [ ] Reusable `Problem` schema defined ONCE; every 4xx/5xx response `$ref`s it and serves `application/problem+json`; zero inline error bodies.
- [ ] Error-catalog source-of-truth (`libs/shared/errors/catalog.*` shape) specified for runtime + docs to read.
- [ ] `IdempotencyKey` header declared once and `$ref`'d on every unsafe POST/PATCH, with 409/422 responses.
- [ ] `PageInfo`/cursor-page envelope declared once and used by every list endpoint.
- [ ] `api/.spectral.yaml` default ruleset emitted; OpenAPI validator AND `spectral lint` both run with **zero errors** (observed exit 0) before handoff.
- [ ] `docs/architecture/performance-budget.yaml` emitted with a resolved budget (explicit numbers or default-table row); no hardcoded perf targets elsewhere.

## Phase 5: Data Model Design

Generate data models at `schemas/` at the project root:

- **ERD diagrams** in Mermaid (at `paths.erd` from config, default `schemas/erd.md`)
- **SQL migration files** (numbered, idempotent) (at `paths.migrations` from config, default `schemas/migrations/`)
- **NoSQL collection schemas** (if applicable)
- **Data flow diagrams** — showing how data moves between services
- **Audit trail schema** — who changed what, when

Standards enforced:
- Soft deletes with `deleted_at` timestamps
- UUID primary keys (not auto-increment) for distributed systems
- Created/updated timestamps on all entities
- Tenant isolation at the data layer
- PII field identification and encryption strategy

## Phase 6: Project Scaffolding

Scaffold the project root structure directly. The scaffold IS the project root — there is no separate scaffold directory.

```
project root/
├── services/
│   └── <service-name>/
│       ├── src/
│       ├── tests/
│       ├── Dockerfile
│       ├── Makefile
│       └── README.md
├── libs/
│   └── shared/          # Shared types, utils, clients
├── docker-compose.yml   # Local dev environment
├── Makefile             # Root-level commands
└── README.md            # Getting started guide
```

Each service includes:
- Health check endpoint (`/healthz`, `/readyz`)
- Structured logging (JSON, correlation IDs)
- Graceful shutdown handling
- Configuration from environment variables
- Basic test structure (unit, integration)
- Dockerfile (multi-stage, non-root user, minimal base image)

## Output Structure

### Project Root Output (Deliverables)

```
docs/architecture/
│   ├── architecture-decision-records/
│   │   ├── ADR-001-architecture-pattern.md
│   │   └── ...
│   ├── system-diagrams/
│   │   ├── c4-context.md
│   │   ├── c4-container.md
│   │   └── sequence-*.md
│   ├── tech-stack.md
│   ├── design-principles.md
│   └── performance-budget.yaml      # single source of truth — frontend/qa/sre/devops read this
api/
│   ├── openapi/
│   │   ├── *.yaml
│   │   └── components.yaml           # reusable Problem / IdempotencyKey / PageInfo components
│   ├── .spectral.yaml                # default lint ruleset (validate+lint gate)
│   ├── grpc/
│   │   └── *.proto
│   └── asyncapi/
│       └── *.yaml
schemas/
│   ├── erd.md
│   ├── migrations/
│   │   └── *.sql
│   └── data-flow.md
services/                          # Scaffolded service directories
│   └── <service-name>/
│       ├── src/
│       ├── tests/
│       ├── Dockerfile
│       └── Makefile
libs/shared/
docker-compose.yml
Makefile
README.md
```

### Workspace Output (`Shipyard/solution-architect/`)

```
Shipyard/solution-architect/
├── working-notes.md
└── analysis/
    └── *.md
```

## Cloud-Specific Patterns

### AWS
- ECS/EKS for orchestration, RDS/Aurora for relational, DynamoDB for key-value
- SQS/SNS for messaging, CloudWatch for monitoring, Secrets Manager
- VPC with public/private subnets, NAT Gateway, ALB

### GCP
- GKE/Cloud Run for orchestration, Cloud SQL/Spanner for relational, Firestore for document
- Pub/Sub for messaging, Cloud Monitoring, Secret Manager
- VPC with private service access, Cloud Load Balancing

### Azure
- AKS/Container Apps for orchestration, Azure SQL/Cosmos DB for data
- Service Bus for messaging, Azure Monitor, Key Vault
- VNet with subnets, Application Gateway, Front Door

### Multi-Cloud Abstractions
- Use Terraform modules with provider-agnostic interfaces
- Abstract cloud-specific SDKs behind service interfaces
- Document cloud provider mapping in tech-stack.md

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Picking architecture before knowing constraints | Run the fitness function FIRST. Scale, team, budget determine the pattern. |
| Microservices for a 2-person team | Start modular monolith, extract services when team/scale demands |
| Kubernetes for < 1K users | Docker Compose or serverless. K8s operational cost > benefit at small scale. |
| Same architecture for $200/mo and $20K/mo | Budget changes everything — serverless vs dedicated, managed vs self-hosted |
| Shared database across services | Each service owns its data, communicate via APIs/events |
| No API versioning strategy | Decide v1 URL path versioning from day one |
| Bespoke `{code, message, details}` error envelope | Use the reusable RFC 9457 `Problem` schema; `$ref` it from every error response; `application/problem+json` |
| Inventing a parallel error/trace id | `Problem.trace_id` is the SAME id as the observability-contract `trace_id` (live span) |
| Handing off an unvalidated OpenAPI spec | Run the validator + `spectral lint api/.spectral.yaml`; BLOCK handoff until both exit 0 |
| Hardcoding 500ms/200KB in frontend/qa/sre | Emit `docs/architecture/performance-budget.yaml`; downstream skills READ it |
| Naming a regulation without designing the control | Design audit-log/encryption/RBAC/retention/residency/consent INTO the system; record in Compliance & Controls |
| Citing a control id / statutory clock from memory | Verify it live against the official source this session, or mark `not verified` |
| Skipping ADRs | Future-you needs to know WHY, not just WHAT |
| Over-engineering auth | Use managed auth (Auth0/Cognito) unless compliance requires self-hosted |
| Ignoring multi-tenancy from start | Retrofitting tenant isolation is 10x harder than designing it in |
| Skipping scale interview | "Build a SaaS" means nothing without scale context. 100 users vs 10M users is a completely different system. |
| Ignoring engagement mode | Express: auto-derive. Standard: 2 rounds. Thorough: 4 rounds. Meticulous: full walkthrough. Read settings.md. |
| Designing for 10M users when there are 100 | Design for current + 10x. Not 1000x. Over-engineering kills velocity. |
| Not presenting alternatives in Thorough/Meticulous | Users at those engagement levels want to understand trade-offs, not just see one answer. |
