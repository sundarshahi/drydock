# Phase 1 — Discovery & Scale Assessment

The architecture must fit the project's actual constraints. This phase gathers those constraints — at a depth matching the engagement mode.

## Step 1: Read Existing Context

Before asking ANY questions, read in parallel:
1. `Shipyard/polymath/handoff/context-package.md` — may contain scale, constraints, decisions
2. `Shipyard/product-manager/BRD/brd.md` — user stories, acceptance criteria, business rules
3. `Shipyard/.orchestrator/codebase-context.md` — brownfield context

**Reduce questions to cover ONLY gaps not addressed in existing context.** If polymath or PM already established scale targets, do not re-ask.

## Step 2: Scale & Fitness Interview

Adapt depth to engagement mode. Use AskUserQuestion with structured options (never open-ended).

### Express Mode

Skip interview entirely. Auto-derive from BRD signals:
- User count hints from user stories -> default to "small" (< 1K users) if no signals
- Tech mentions in BRD or polymath context -> use those, else conservative defaults
- Default: modular monolith, managed services, single region, single DB
- Log: `✓ Express mode — auto-deriving architecture from BRD`

If a critical constraint is completely missing (e.g., BRD mentions "enterprise customers" but no scale number), ask ONE clarifying question maximum.

### Standard Mode (2 rounds)

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

### Thorough Mode (4 rounds)

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

### Meticulous Mode

Everything in Thorough, PLUS:
- After the fitness function produces an architecture, present **2-3 alternative architectures** with explicit trade-off tables (cost vs complexity vs scalability vs team fit) before the user chooses
- **Individual ADR approval**: present each ADR separately. User reviews and approves each decision.
- **Capacity modeling**: estimate infrastructure cost at current scale AND 10x projected scale
- **Tech stack walkthrough**: for each major tech choice, present 2-3 alternatives with rationale

## Step 3: Architecture Fitness Function

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
