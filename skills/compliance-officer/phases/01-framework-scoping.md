# Phase 1: Framework Scoping

## Objective

Determine WHICH regulatory frameworks apply to this product, deterministically, from product signals. Produce an auditable scoping decision log — every framework is scoped IN with an evidenced signal, or scoped OUT with the specific missing signal. The compliance-officer is the authority on per-product framework scoping; no other skill makes this determination. Generate outputs in `drydock/compliance-officer/scoping/`.

## Context Bridge

Read Phase 0 (Reconnaissance) outputs and, critically, the security-engineer's data-security outputs. You should already know the data classification, PII inventory, product scope, and customer types. The data classification is the PRIMARY signal source — do not re-derive it; consume it (`drydock/.protocols/compliance-protocol.md`, Authority Boundary). If Phase 0 was not run, perform reconnaissance inline before proceeding.

## Inputs

- **Data classification + PII inventory** — `drydock/security-engineer/data-security/pii-inventory.md`, `gdpr-compliance.md` (CONSUMED, not redone)
- **Product scope** — `product-manager/BRD/` (target markets, customer types, data the product collects)
- **Declared targets** — `compliance:` block in `.drydock.yaml` (if present: explicit framework list, target markets)
- **Implementation code** — `services/`, `frontend/` (data fields, payment integrations, regional deployment hints)
- **Architecture** — `docs/architecture/` (data residency, regions, external processors)

If a Critical input is missing, STOP and request it (you cannot scope frameworks without data classification, and cannot verify controls later without code).

## Workflow

### Step 1: Extract Product Signals (each backed by evidence)

For each signal, record the concrete evidence (`path:line`, a PII field, a BRD statement) or mark it absent. No evidence = signal absent.

| Signal | Evidence to look for |
|--------|---------------------|
| PHI / health data | health/treatment/diagnosis fields in PII inventory; healthcare integrations |
| Cardholder data / PAN | card-number/CVV/PAN fields; payment processor code; whether the system stores/processes/transmits card data |
| EU/EEA personal data | EU users, EU establishment, EU-region deployment, or monitoring of EU subjects |
| California consumers at threshold | CA users + the statutory threshold signals (revenue / data volume / data-sales business model) |
| Enterprise B2B / trust attestation | B2B SaaS selling to enterprises; vendor-security-questionnaire / SOC-trust demand in BRD |
| US federal customer | sells to / hosts data for a US federal agency |

### Step 2: Apply the Deterministic Signals → Frameworks Map

Apply the map from `drydock/.protocols/compliance-protocol.md` exactly. A present signal SCOPES IN its framework. Signals STACK — record every framework each present signal scopes in.

| Present signal | Framework scoped IN |
|----------------|---------------------|
| PHI / health data | **HIPAA** |
| Cardholder data / PAN | **PCI-DSS v4.0.1** |
| EU/EEA personal data or EU users | **GDPR** |
| California consumers at threshold | **CCPA/CPRA** |
| Enterprise B2B SaaS / SOC trust | **SOC 2** (Type I → then Type II) and/or **ISO 27001:2022** |
| US federal customer | **FedRAMP** |

- **SOC 2 sequencing:** scope Type I (design at a point in time) first, then Type II (operating effectiveness over a window). Record both as a sequence, not a choice.
- **Ambiguous signal:** scope IN and flag for confirmation — never silently drop a possible obligation.

### Step 3: Resolve Ambiguity by Autonomy Level

- **Autopilot:** infer all signals from artifacts; report assumptions; proceed.
- **Copilot:** confirm only signals not derivable from artifacts (1 AskUserQuestion, batched options).
- **Checkpoint/Manual:** confirm the scoped set, target markets, and certification stage (SOC 2 Type I vs II; FedRAMP Low/Moderate/High baseline) via AskUserQuestion (1-2 calls max, predefined options + "Chat about this" last).

Never ask open-ended questions — follow `drydock/.protocols/ux-protocol.md`.

### Step 4: Pin Editions

For every in-scope framework, record the pinned edition from the protocol catalog (PCI-DSS **v4.0.1**, ISO/IEC **27001:2022**, GDPR Regulation (EU) 2016/679, SOC 2 TSC 2017 rev. 2022, FedRAMP Rev 5, HIPAA 45 CFR 160/164, CCPA/CPRA Cal. Civ. Code §1798.100). Editions are Tier-3 volatile — note that exact requirement contents are verified live in Phase 2, not here.

### Step 5: Write the Scoping Decision Log

Produce a decision log that an auditor can trace. Out-of-scope frameworks are recorded WITH their missing signal — silent omission is not allowed.

| Framework | Edition (pinned) | In scope? | Signal / evidence | Decision rationale |
|-----------|------------------|-----------|-------------------|--------------------|
| GDPR | 2016/679 | Yes | EU users — `pii-inventory.md` region=EU | EU personal data processed |
| HIPAA | 45 CFR 160/164 | No | no PHI fields found | no health-data signal present |
| ... | ... | ... | ... | ... |

## Output Deliverables

Write to `drydock/compliance-officer/scoping/`:

| File | Contents |
|------|----------|
| `frameworks.md` | The scoping decision log (in-scope + out-of-scope with missing-signal reasons), pinned editions, SOC 2 Type sequencing, confirmed certification stage |
| `signals.md` | Each product signal with its concrete evidence pointer (or marked absent) |

## Validation

Before proceeding to Phase 2, verify:
- [ ] Every product signal is recorded with evidence or explicitly marked absent
- [ ] Every framework appears in the log as In-scope (with signal) or Out-of-scope (with missing signal)
- [ ] No framework is scoped IN without a present, evidenced signal
- [ ] Editions are pinned for every in-scope framework
- [ ] SOC 2 (if in scope) records Type I → Type II sequencing

## Quality Bar

Scoping is NOT a guess. "We're probably SOC 2" is not a decision — "SOC 2 scoped IN; signal: B2B enterprise sales per `BRD/customers.md:12`; Type I first, then Type II" is. Every in-scope framework traces to an evidenced signal, and every out-of-scope framework records the specific signal that was absent. Do not pin requirement text here — only editions; the actual control ids and requirement text are verified live in Phase 2.

**In Checkpoint/Manual level, present the scoping decision to the user before proceeding to Phase 2.**
