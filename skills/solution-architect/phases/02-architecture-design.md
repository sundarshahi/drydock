# Phase 2 — Architecture Design

Generate architecture documents in `docs/architecture/` (or `paths.architecture_docs` from config):

## architecture-decision-records/
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

### Architecture-Style & Layering ADR (REQUIRED — emit `ADR-NNN-architecture-style.md`)

Emit an ADR that documents the Clean/Hexagonal layering and the **dependency-direction rule** per `Shipyard/.protocols/architecture-boundaries.md`. It is the design-time source of truth for the boundary that software-engineer enforces MECHANICALLY (`make arch`, exit non-zero on violation) — the architect declares the law; the engineer wires the fitness function. The ADR MUST state:

- The layer stack innermost→outermost: **domain** (entities/value-objects/business rules, zero framework/IO imports) → **application** (use-cases + PORT interfaces) → **infrastructure/adapters** (frameworks, DB drivers, HTTP clients, ORMs, SDKs).
- **The one law:** source-code dependencies (imports) point INWARD only; a framework/ORM/HTTP/DB import in the domain is a HIGH-severity, build-blocking violation.
- **Ports owned inside, adapters bound at the composition root** — use-cases receive ports via constructor/parameter injection; only `main`/bootstrap/DI module names concrete adapters.
- A pointer to the per-language fitness function software-engineer will emit (`.dependency-cruiser.js` / ArchUnit / `.importlinter` / `deptrac.yaml` / `.go-arch-lint.yml`) and the `make arch` CI gate. Note explicitly: **the architect does not implement the lint; it specifies the rule the lint must encode.**

### Compliance & Controls (REQUIRED subsection — design controls in, do not just name regulations)

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

## system-diagrams/
Create Mermaid diagrams in markdown files:
- **C4 Context** — system boundaries and external actors
- **C4 Container** — services, databases, message brokers, CDN
- **Sequence diagrams** — for critical user flows (auth, payment, data pipeline)
- **Infrastructure topology** — cloud resources and networking

## Design Principles
Apply and document these production patterns:
- **12/15-Factor App methodology** — explicit design intent, documented factor-by-factor in `design-principles.md`. Config strictly from the environment (no config in code), strict dev/prod parity, stateless processes, port binding, disposability/graceful shutdown, logs as event streams to **stdout** (per `observability-contract.md` — the app never owns log files/rotation). Carry the 15-factor extensions: **API-first**, **telemetry** (RED metrics + traces + structured logs per the observability contract), and **authentication/authorization as a first-class concern** (per `security-defaults.md`).
- Defense in depth (security layers) — aligns with `security-defaults.md` (input validation at the boundary, parameterized queries, output encoding, SSRF allowlist, secrets from env/secret-manager, per-object default-deny authz, security headers + strict CORS + secure cookies)
- Clean/Hexagonal layering with inward-only dependencies (see the Architecture-Style & Layering ADR; mechanically enforced by software-engineer)
- Circuit breaker, retry, timeout patterns
- Idempotency for all write operations (realized as the reusable `IdempotencyKey` header contract in Phase 4)
- Eventual consistency where appropriate
- Zero-trust networking

## Phase 2 Quality Bar (gate — do not proceed to Phase 3 until all true)

- [ ] Architecture-style & layering ADR emitted, declaring the inward-only dependency-direction law + the `make arch` gate software-engineer will enforce.
- [ ] Feature-flag provider ADR emitted (OpenFeature provider + env/config fallback + per-flag safe defaults).
- [ ] `Compliance & Controls` subsection produced with a resolved scope (frameworks scoped IN, or explicit `out of scope — no <signal>`); any cited control id/article/clock is `[verified]` live or marked `not verified`.
- [ ] 12/15-factor design intent documented factor-by-factor in `design-principles.md`.
- [ ] **`security-defaults checklist passes`** — the design leaves a concrete place for every secure-by-default control (boundary validation, parameterized data access, per-object default-deny authz, secrets from env/secret-manager, security headers/CORS/cookies) so the BUILD agents can ship it without retrofit.

**Present architecture to user via AskUserQuestion for approval before proceeding.**
