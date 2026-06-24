# Phase 2: Control Matrix

## Objective

For every in-scope framework, emit a per-framework control matrix listing the mandatory controls — built from the STABLE family skeleton in the pinned catalog, with every specific control id, article number, criterion, and §-citation **verified LIVE against the official source this session**. No control id is recalled from memory. Generate outputs in `Shipyard/compliance-officer/control-matrix/`.

## Context Bridge

Read Phase 1 scoping (`Shipyard/compliance-officer/scoping/frameworks.md`) — the in-scope framework set + pinned editions. Build a matrix only for in-scope frameworks. The catalog SKELETON (control families / article groups / TSC categories) is in `Shipyard/.protocols/compliance-protocol.md`; this phase fills it with live-verified ids.

## Runtime-Freshness Rule (BINDING — do not skip)

Per `Shipyard/.protocols/compliance-protocol.md`, `Shipyard/.protocols/freshness-protocol.md`, and `Shipyard/.protocols/grounding-protocol.md`:

- **NEVER write a control id, article number, criterion, §-citation, or requirement sentence from memory.** Verify each LIVE this session before it enters the matrix.
- Use WebSearch/WebFetch against **official sources only**, and cite URL + verbatim quoted span + retrieval date for each:
  - SOC 2 TSC → AICPA
  - GDPR → eur-lex.europa.eu
  - HIPAA → ecfr.gov / hhs.gov
  - PCI-DSS v4.0.1 → pcisecuritystandards.org
  - CCPA/CPRA → leginfo.legislature.ca.gov / oag.ca.gov
  - ISO 27001:2022 → iso.org
  - FedRAMP / 800-53 Rev 5 → fedramp.gov / NIST CSRC
- Tag each control row `[verified]` (id confirmed live + quoted), `[inferred]`, or `[unverified]`. An `[unverified]` id may NOT later drive a BLOCKING gate.
- If an id cannot be verified live, leave it `not verified` and say so — never invent a plausible id to fill the matrix.

## Workflow

### Step 1: Load the Family Skeleton per In-Scope Framework

From the protocol catalog, take the stable groupings for each in-scope framework, e.g.:
- **SOC 2** — Common Criteria CC1–CC9 (+ Availability / Confidentiality / Processing Integrity / Privacy if committed).
- **GDPR** — article groups: principles & lawfulness (5–11), data-subject rights (12–23), controller/processor obligations (24–43), breach (33–34), DPIA & DPO (35–39), transfers (44–49).
- **HIPAA** — Security Rule Administrative / Physical / Technical safeguards (Required vs Addressable); Privacy Rule; Breach Notification Rule.
- **PCI-DSS v4.0.1** — the 12 requirements under the 6 objectives.
- **CCPA/CPRA** — notice, know/access, delete, correct, opt-out of sale/sharing, limit sensitive PI, non-discrimination, service-provider terms.
- **ISO 27001:2022** (stub) — ISMS clauses 4–10 + Annex A themes A.5/A.6/A.7/A.8.
- **FedRAMP** (stub) — 800-53 Rev 5 families for the selected baseline.

### Step 2: Verify Each Control Id Live

For each family, retrieve the current official text and extract the EXACT control id + a one-line requirement. Quote the source span. Mark Required vs Addressable (HIPAA), mandatory vs scope-dependent (PCI SAQ type), and committed-category membership (SOC 2 extra categories).

### Step 3: Build the Per-Framework Matrix

One file per framework. Columns:

| Column | Meaning |
|--------|---------|
| Control id | LIVE-verified id (e.g. SOC2 `CC6.1`, GDPR `Art. 32`, HIPAA `§164.312(a)(1)`, PCI `Req 3.x`) |
| Family / group | The stable grouping from the catalog |
| Requirement (1 line) | Quoted/paraphrased from the live official text |
| Mandatory? | Mandatory / Addressable / Scope-dependent |
| Source | Official URL + retrieval date |
| Tag | `[verified]` / `[inferred]` / `[unverified]` |
| Maps-to (placeholder) | left for Phase 3 to fill with implementing artifact |

### Step 4: Mark Mandatory vs Discretionary

Flag which controls are MANDATORY for in-scope frameworks — these drive the Phase 5 BLOCKING gate. HIPAA Addressable items, SOC 2 optional categories, and out-of-baseline FedRAMP controls are noted but are not auto-blocking unless committed/applicable.

### Step 5: Calibration Summary

End each matrix file with counts by tag (e.g. `42 [verified], 0 [inferred], 3 [unverified]`) per `grounding-protocol.md`. Any `[unverified]` id is listed with the reason live verification failed.

## Output Deliverables

Write to `Shipyard/compliance-officer/control-matrix/`:

| File | Contents |
|------|----------|
| `<framework>.md` (one per in-scope framework, e.g. `soc2.md`, `gdpr.md`, `hipaa.md`, `pci-dss.md`, `ccpa-cpra.md`) | The per-framework control matrix with live-verified ids, sources, tags, mandatory flags |
| `matrix-summary.md` | Cross-framework rollup: total controls, mandatory count, verified vs unverified, per-framework counts |

## Validation

Before proceeding to Phase 3, verify:
- [ ] A matrix exists for every in-scope framework (and only in-scope frameworks)
- [ ] Every control id carries an official source URL + retrieval date + quoted span
- [ ] No control id was written from memory (every row is `[verified]` or explicitly `[unverified]` with reason)
- [ ] Mandatory vs Addressable/Scope-dependent is marked per control
- [ ] Each matrix ends with a calibration summary (counts by tag)

## Quality Bar

A control matrix populated from memory is the failure mode this phase exists to prevent — a confidently wrong "PCI Req 8.3.6" or "GDPR Art. 17" passes a glance and fails an audit. Every id must trace to a live official source quoted this session. A matrix with zero `[verified]` tags and no citations is not a matrix — it is a hallucination with a table around it. If live verification is impossible for an id, the honest `not verified` is the correct output.
