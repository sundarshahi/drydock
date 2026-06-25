# Phase 4: Evidence & Docs

## Objective

Produce the statutory compliance documents an auditor or regulator expects — System Security Plan (SSP), GDPR Data Protection Impact Assessment (DPIA), and a breach/incident runbook encoding statutory notification clocks — and assemble the control-evidence map that ties every mandatory control to its proof. Every control statement is grounded in a real implementing artifact and live-verified requirement text. Generate outputs in `Shipyard/compliance-officer/docs/` and `Shipyard/compliance-officer/evidence/`.

## Context Bridge

Read:
- Phase 2 matrices (`Shipyard/compliance-officer/control-matrix/`) — live-verified control ids + requirement text.
- Phase 3 implementation check (`Shipyard/compliance-officer/implementation/controls-check.md`) — status + implementing artifacts.
- security-engineer outputs (PII inventory, encryption audit) — CONSUMED for data descriptions, not redone.
- solution-architect architecture (system boundary, data flows, residency).

## Runtime-Freshness Rule (BINDING)

Per `Shipyard/.protocols/compliance-protocol.md`: any statutory clock, article number, or requirement sentence written into these documents is verified LIVE against the official source this session (eur-lex for GDPR Arts. 33–34; ecfr.gov/hhs.gov for HIPAA §164.404 / Breach Notification Rule), cited with URL + quote + date. NEVER write a statutory deadline or control statement from memory. If you cannot verify a clock live, mark it `not verified` rather than asserting a number.

## Workflow

### Step 1: System Security Plan (SSP)

Assemble an SSP (the structure auditors expect; FedRAMP/SOC 2 readiness uses this form):
- **System description** — purpose, components/services, data types (from security-engineer PII inventory), users/roles.
- **Authorization boundary** — what is in scope, external services/processors, trust boundaries (from solution-architect).
- **Data classification** — sensitivity tiers (CONSUMED from security-engineer; cite, do not redo).
- **Control implementation statements** — for each mandatory control: the live-verified requirement (Phase 2) + HOW it is implemented, citing the Phase 3 implementing artifact `path:line`. A control with no artifact is documented as a gap, never as fabricated prose.

### Step 2: GDPR DPIA (when EU personal data is in scope)

Produce a DPIA per GDPR Art. 35 (verify the article + the "high risk" triggering criteria live):
- **Processing description** — nature, scope, context, purposes; categories of data subjects + personal data (from PII inventory).
- **Necessity & proportionality** — lawful basis (Art. 6, verified live), data minimization, retention.
- **Risk assessment** — risks to data-subject rights/freedoms; likelihood + severity.
- **Mitigations** — controls reducing each risk, each mapped to a Phase 3 artifact.
- **Residual risk + sign-off placeholder** — and whether prior consultation with the supervisory authority is indicated.

If EU personal data is NOT in scope, record "DPIA not required — no EU personal-data signal" instead of producing an empty template.

### Step 3: Breach / Incident Runbook with Statutory Clocks

Produce an incident/breach runbook that ENCODES the statutory notification clocks as hard deadlines, not advice (verify each clock's exact wording live):

| Trigger | Statutory clock (verify exact wording live) | Source to verify |
|---------|---------------------------------------------|------------------|
| Personal-data breach (GDPR) | Notify the supervisory authority **within 72 hours** of becoming aware (Art. 33); notify data subjects without undue delay if high risk (Art. 34) | eur-lex Arts. 33–34 |
| PHI breach (HIPAA) | Notify affected individuals **without unreasonable delay and no later than 60 days** from discovery; notify HHS; media notice if ≥500 in a state/jurisdiction (verify §164.404–408) | ecfr.gov / hhs.gov Breach Notification Rule |

The runbook includes: detection → triage/assessment → containment → the notification decision tree with the clocks → who notifies whom → record-keeping. Tie detection hooks to the Phase 3 breach-detection control. Mark any clock you could not verify live as `not verified`.

### Step 4: Control-Evidence Map

Assemble the proof contract from `Shipyard/.protocols/compliance-protocol.md`. One row per mandatory control:

| Control | Implementing artifact | Owning agent | Evidence location | Status |
|---------|----------------------|--------------|-------------------|--------|
| `<framework id>` (live-verified) | `path:line` | security-engineer / devops / solution-architect / software-engineer | artifact / receipt / test / log sample | Met / Partial / Missing / N/A / Accepted |

- Owning agent is the producer of the artifact — compliance-officer maps, it does not own implementation.
- A `Met` row with an empty Implementing-artifact field is invalid — downgrade to `Missing`.
- This map is the direct input to the Phase 5 gate.

### Step 5: Copy Deliverables (optional, config-aware)

If `.shipyard.yaml` defines a docs path, also copy SSP/DPIA/runbook to `docs/compliance/`. Otherwise leave them in the workspace. Never overwrite existing user docs without the brownfield rules in `Shipyard/.orchestrator/codebase-context.md`.

## Output Deliverables

Write to `Shipyard/compliance-officer/docs/` and `Shipyard/compliance-officer/evidence/`:

| File | Contents |
|------|----------|
| `docs/ssp.md` | System Security Plan — system description, boundary, data classification, per-control implementation statements |
| `docs/dpia.md` | GDPR DPIA (or a recorded "not required" note when EU data is out of scope) |
| `docs/breach-runbook.md` | Incident/breach runbook with the GDPR 72h + HIPAA 60-day clocks encoded as deadlines |
| `evidence/control-evidence-map.md` | control → implementing artifact → owning agent → evidence location → status |

## Validation

Before proceeding to Phase 5, verify:
- [ ] SSP control implementation statements each cite a Phase 3 artifact or are marked as a gap (none fabricated)
- [ ] DPIA exists when EU personal data is in scope (or a "not required" note when it is not)
- [ ] Breach runbook encodes the GDPR 72h and HIPAA 60-day clocks, each verified live with a citation
- [ ] Control-evidence map has a row for every mandatory control with a non-empty status
- [ ] Every statutory clock / article number is `[verified]` with URL + quote + date

## Quality Bar

A compliance document that asserts controls in confident prose with no artifact behind it is exactly the audit-failure this domain exists to prevent. Every implementation statement points at real code/infra; every statutory clock is the live-verified number, cited; every Missing control is documented as a gap, not papered over. The breach runbook is operational — a responder can follow the decision tree and hit the 72h / 60-day deadlines — not a restatement of the law.
