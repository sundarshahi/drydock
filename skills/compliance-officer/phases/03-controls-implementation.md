# Phase 3: Controls Implementation Check

## Objective

For every mandatory control in the Phase 2 matrix, verify the control ACTUALLY EXISTS in the generated code/infrastructure — by reading the implementing artifact, not by assuming. Map each control to a concrete `path:line` and a status (Met / Partial / Missing). This phase CONSUMES the outputs of security-engineer, solution-architect, and devops; it does not re-audit or implement. Generate outputs in `Shipyard/compliance-officer/implementation/`.

## Context Bridge

Read the Phase 2 matrices (`Shipyard/compliance-officer/control-matrix/`) and the upstream artifacts you map onto:
- `Shipyard/security-engineer/data-security/` — PII inventory, encryption audit, GDPR/CCPA mapping (CONSUMED — the SOLE authority on PII + encryption; do not redo).
- `Shipyard/security-engineer/auth-review/` — auth flows, RBAC findings.
- `docs/architecture/` — data residency, regions, data flows (solution-architect).
- `infrastructure/`, `.github/workflows/` — KMS, IAM, logging pipelines, retention jobs (devops).
- `services/`, `frontend/` — application controls (consent, retention, PII handling).

## Authority Boundary (do not double-work)

Per `Shipyard/.protocols/conflict-resolution.md` + `Shipyard/.protocols/compliance-protocol.md`:
- Encryption/crypto and PII findings come FROM security-engineer — cite their artifact, do not re-audit.
- Data-residency decisions come FROM solution-architect — flag a gap as a finding, do not change architecture.
- Infra controls come FROM devops — point the evidence at their files, do not re-provision.
- Where a control needs an artifact that does not exist, raise a finding for the owning agent — do not implement it yourself.

## Workflow

### Step 1: Verify the Required Control Surfaces Exist

For each mandatory control, find and READ the implementing artifact. The control areas to verify across frameworks:

| Control area | What to verify (read the artifact, cite `path:line`) | Typical owner / source |
|--------------|------------------------------------------------------|------------------------|
| **Audit logging** | Security-relevant events logged (auth, access, admin, data changes); tamper-resistance; retention; PII-redaction in logs | devops (pipeline) + software-engineer (emit) |
| **Encryption at rest** | DB/file/backup encryption present; algorithm/key-mgmt | **CONSUME** security-engineer encryption audit |
| **Encryption in transit** | TLS version + cipher posture; mTLS for internal | **CONSUME** security-engineer encryption audit |
| **RBAC / access control** | Role/permission model enforced server-side; least privilege; default-deny | **CONSUME** security-engineer auth-review + read code |
| **Data retention** | Retention periods defined + automated purge jobs that run | software-engineer + devops |
| **Consent** | Consent capture/withdrawal for processing (GDPR/CCPA); granularity; record of consent | software-engineer + frontend-engineer |
| **Data residency** | Storage/processing regions match obligations (e.g. EU data in-region) | **CONSUME** solution-architect architecture |
| **PII handling** | Minimization, masking, access scoping, deletion paths | **CONSUME** security-engineer PII inventory |
| **Breach detection/response hooks** | Alerting + incident triggers present (feeds Phase 4 runbook) | devops + sre |

For each: open the actual file, quote the line, and record what the artifact literally does — do not infer from a filename (`grounding-protocol.md`: read before you describe).

### Step 2: Assign a Status per Control

| Status | Criterion |
|--------|-----------|
| **Met** | A verified implementing artifact exists (`path:line`) that satisfies the control |
| **Partial** | An artifact exists but does not fully satisfy the control (note the gap) |
| **Missing** | No implementing artifact found — a BLOCKING gap if the control is mandatory (Phase 5) |
| **N/A** | Out of scope for this product, with a recorded reason |

A control marked `Met` with no `path:line` is invalid — downgrade to `Missing`. Status must be backed by reading the code, not by an assertion.

### Step 3: Cross-Reference, Do Not Re-Audit

When a control's evidence is a security-engineer or devops artifact, cite it (`See Shipyard/security-engineer/data-security/encryption-audit.md:NN`). Do not produce a competing audit — that violates the authority hierarchy. If the upstream artifact is missing or inconclusive, mark the control `Partial`/`Missing` and raise a finding for the owning agent rather than auditing it yourself.

### Step 4: Record Gaps as Findings

For each `Missing`/`Partial` mandatory control, write a finding: control id, what's missing, the owning agent who must implement it, and the suggested artifact. These flow into Phase 5's gate and the HARDEN remediation chain.

## Output Deliverables

Write to `Shipyard/compliance-officer/implementation/`:

| File | Contents |
|------|----------|
| `controls-check.md` | Per-control table: control id → implementing artifact `path:line` → status (Met/Partial/Missing/N/A) → owning agent → notes |
| `gaps.md` | Every Partial/Missing mandatory control as a finding (control, gap, owning agent, suggested artifact) |

## Validation

Before proceeding to Phase 4, verify:
- [ ] Every mandatory control from Phase 2 has a status
- [ ] Every `Met` control cites an implementing artifact `path:line`
- [ ] Encryption/PII statuses cite security-engineer artifacts (not a re-audit)
- [ ] Residency statuses cite solution-architect artifacts (no architecture changes made)
- [ ] Every Partial/Missing mandatory control appears in `gaps.md` with an owning agent

## Quality Bar

"Audit logging exists" is not verification — `services/api/middleware/audit.ts:18 logs actor+action+resource+timestamp on every mutating route` is. Every status must be backed by an artifact actually read this session. The deliverable proves implementation by pointing at code/infra, never by restating the requirement. And it stays in its lane: encryption and PII verdicts come from security-engineer's audit — this phase maps them to controls, it does not re-derive them.
