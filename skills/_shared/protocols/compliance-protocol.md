# Compliance Protocol — Per-Product Regulatory Scoping, Control Catalog & Evidence Contract

**Core principle: Compliance is scoped from product signals, mapped to a pinned framework catalog, and proven by an evidence map — but EVERY specific control ID, article number, and requirement text is verified live against the official source this session, never recalled from memory.**

This is the cross-agent contract for regulatory compliance. It is the one domain no other skill owns: security-engineer audits PII/encryption, devops owns infra, solution-architect owns design — none of them scopes frameworks, maps mandatory controls, or produces statutory evidence. The compliance-officer is the authority on per-framework scoping and the control-evidence map; it CONSUMES the security-engineer's PII inventory and encryption audit and does NOT redo them. Consuming skills: **compliance-officer, security-engineer, solution-architect, product-manager**.

---

## Deterministic Product-Signals → Frameworks Map

Read data classification (security-engineer PII inventory), the product/BRD, and any `compliance:` block in `.shipyard.yaml`. Apply this map deterministically — a present signal SCOPES IN its framework. Multiple signals stack (a B2B health SaaS with EU users scopes HIPAA + SOC 2 + GDPR). When a signal is ambiguous, scope it IN and flag for confirmation; never silently drop.

| Product signal (evidence required) | Framework scoped IN | Edition pinned this protocol |
|------------------------------------|---------------------|------------------------------|
| PHI / health data / treatment-payment-operations data | **HIPAA** (Security + Privacy + Breach Notification Rules) | 45 CFR Parts 160 & 164 |
| Cardholder data / PAN / stores-processes-transmits payment cards | **PCI-DSS** | **v4.0.1** (current; v3.2.1 retired Mar 2024) |
| EU/EEA personal data, or EU users/establishment, or monitoring EU subjects | **GDPR** | Regulation (EU) 2016/679 |
| California consumers at the statutory threshold (revenue / volume / data-sales) | **CCPA/CPRA** | Cal. Civ. Code §1798.100 et seq. (CPRA amendments in force) |
| Enterprise B2B SaaS / customer trust / vendor-security questionnaires | **SOC 2** (Type I, then Type II) and/or **ISO 27001** | SOC 2 (AICPA TSC 2017, rev. 2022) · ISO/IEC 27001:2022 |
| US federal agency customer / sells to federal government | **FedRAMP** | FedRAMP Rev 5 (NIST SP 800-53 Rev 5 baselines) |

- **Type I before Type II:** SOC 2 Type I attests design at a point in time; Type II attests operating effectiveness over a window (commonly 3–12 months). Scope Type I first, then Type II.
- **No signal → no framework.** Do not scope a framework with zero supporting signal — over-scoping creates phantom blocking gates. Record "out of scope: <framework> — no <signal>" so the decision is auditable.

---

## Per-Framework Requirement Catalog (STABLE families — pinned; IDs verified live)

List the control FAMILIES / article groups / TSC categories below. These groupings are stable and citable. The EXACT control id, article number, criterion number, and requirement text inside each family is **NOT recalled here** — verify it live (see Runtime-Freshness Rule). Pin the edition; verify the contents.

### SOC 2 — AICPA Trust Services Criteria (2017, rev. 2022)
- **Common Criteria (CC, security — always in scope):** CC1 Control Environment · CC2 Communication & Information · CC3 Risk Assessment · CC4 Monitoring · CC5 Control Activities · CC6 Logical & Physical Access · CC7 System Operations · CC8 Change Management · CC9 Risk Mitigation.
- **Additional categories (in scope only if committed to):** Availability (A) · Confidentiality (C) · Processing Integrity (PI) · Privacy (P).
- Pull the exact point-of-focus and criterion number live from the current TSC.

### GDPR — Regulation (EU) 2016/679 (article GROUPS)
- **Principles & lawfulness:** Arts. 5–11 (principles, lawful basis, consent, special-category data).
- **Data-subject rights:** Arts. 12–23 (transparency, access, rectification, erasure, portability, objection).
- **Controller/processor obligations:** Arts. 24–43 (DPbD&D Art. 25, records Art. 30, security Art. 32, DPA Art. 28).
- **Breach:** Arts. 33–34 (supervisory-authority + data-subject notification).
- **DPIA & DPO:** Arts. 35–39.
- **International transfers:** Arts. 44–49.
- Verify the exact article number + clause text live; do not assert "Art. 17" from memory.

### HIPAA — 45 CFR Parts 160 & 164 (rule + safeguard groups)
- **Security Rule (Part 164 Subpart C):** Administrative · Physical · Technical safeguards (each split into Required vs Addressable implementation specifications).
- **Privacy Rule (Part 164 Subpart E):** uses & disclosures, minimum necessary, individual rights.
- **Breach Notification Rule (Part 164 Subpart D):** individual, HHS, and media notice.
- Verify the exact §164.xxx citation and Required/Addressable status live.

### PCI-DSS v4.0.1 — the 12 requirements (6 control objectives)
- Build/maintain secure network (Req 1–2) · Protect account data (Req 3–4) · Vulnerability mgmt (Req 5–6) · Strong access control (Req 7–9) · Monitor & test networks (Req 10–11) · Information-security policy (Req 12).
- Note SAQ type vs full ROC, and the customized vs defined-approach option. Verify the exact sub-requirement number and "applicable after 31 Mar 2025" future-dated items live.

### CCPA/CPRA — Cal. Civ. Code §1798.100 et seq. (obligation groups)
- Notice at collection · Right to know/access · Right to delete · Right to correct · Right to opt-out of sale/sharing ("Do Not Sell or Share") · Limit use of sensitive personal information · Non-discrimination · Service-provider/contractor contract terms.
- Verify the exact §1798.xxx citation and current threshold figures live (thresholds are adjusted).

### ISO/IEC 27001:2022 — STUB (Annex A control themes)
- ISMS clauses 4–10 + **Annex A** four themes: Organizational (A.5), People (A.6), Physical (A.7), Technological (A.8). 93 controls. Verify exact A.x.y control numbers live against ISO 27001:2022 / 27002:2022.

### FedRAMP — STUB (NIST SP 800-53 Rev 5 control families)
- Baselines: Low / Moderate / High (+ Tailored/LI-SaaS). Control families AC, AU, CA, CM, CP, IA, IR, … per 800-53 Rev 5. Verify exact control ids + baseline membership live against the current FedRAMP baseline and OSCAL package.

---

## Runtime-Freshness Rule (BINDING — mirrors security-testing-protocol.md & grounding-protocol.md)

Regulatory text is volatile and is the single most hallucination-prone surface in this domain: a confidently wrong "GDPR Art. 17" or "PCI Req 8.3.6" or "§164.312(a)(2)(iv)" passes a glance and fails an audit. Therefore:

- **NEVER state a specific control id, article number, criterion, §-citation, threshold figure, or requirement sentence from memory.** Verify it live against the official source THIS session before writing it into any catalog row, matrix, SSP, or finding.
- **Official sources only (cite URL + verbatim quoted span + retrieval date):** AICPA TSC, eur-lex.europa.eu (GDPR), ecfr.gov / hhs.gov (HIPAA), pcisecuritystandards.org (PCI-DSS SAQ/ROC), leginfo.legislature.ca.gov + oag.ca.gov (CCPA/CPRA), iso.org (27001), fedramp.gov + NIST CSRC (800-53/OSCAL). A blog, vendor checklist, or prior-session memory is NOT authoritative.
- **Tag each compliance claim** `[verified]` / `[inferred]` / `[unverified]` exactly as in `grounding-protocol.md`. An un-verified control id is `[unverified]` and may NOT drive a BLOCKING gate decision.
- **Tier-3 volatility** per `freshness-protocol.md` (compliance frameworks update): re-verify editions, thresholds, and future-dated requirements (e.g., PCI items effective after a date) every session.
- **Abstain, do not fabricate:** if a control id cannot be verified live, leave it `not verified` in the catalog/template and say so — never invent a plausible-looking id to fill the schema.

---

## Control-Evidence Map (the proof contract)

Every mandatory control, once verified live, maps to a row proving it is actually implemented — claims without an artifact pointer are not evidence (`grounding-protocol.md`):

| Field | Rule |
|-------|------|
| **Control** | Framework + live-verified id + one-line requirement (e.g. `SOC2 CC6.1 — logical access restricted`). Id must be `[verified]`. |
| **Implementing artifact** | The concrete file/config that satisfies it — `path:line` (e.g. `services/auth/rbac.ts:30`, `infrastructure/kms.tf:12`). No path = not implemented. |
| **Owning agent** | Who produced the artifact: security-engineer / devops / solution-architect / software-engineer. compliance-officer does NOT implement controls — it maps and verifies them. |
| **Evidence location** | Where the proof lives for an auditor: the artifact, a receipt, a test, a log sample, a screenshot path. |
| **Status** | `Met` (verified artifact exists) · `Partial` (artifact incomplete) · `Missing` (no artifact — a BLOCKING gap if the control is mandatory) · `N/A` (out of scope, with reason) · `Accepted` (missing but justified + override receipt). |

A control marked `Met` with an empty Implementing-artifact field is invalid — downgrade to `Missing`.

---

## Compliance Gate Rule

- A **mandatory** in-scope control with status `Missing` is a **BLOCKING** finding. It feeds the HARDEN remediation chain (`conflict-resolution.md`: findings → tasks → fix → re-verify) exactly like a Critical security finding.
- A block may be cleared two ways only: (1) an implementing artifact is added and re-verified to `Met`; or (2) an explicit **"accepted with justification"** override recorded as a receipt (who accepted, why, residual risk, expiry). Silent skips are forbidden.
- Statutory clocks are non-negotiable design inputs, not advice: GDPR breach notification to the supervisory authority **within 72 hours** of awareness (Art. 33); HIPAA breach notice to individuals **without unreasonable delay and no later than 60 days** (verify the exact §164.404 wording live). The incident runbook MUST encode these clocks.

---

## Authority Boundary (no double-work)

- **security-engineer** remains the SOLE authority on PII inventory, data classification, and the encryption/crypto AUDIT. compliance-officer READS those outputs (`Shipyard/security-engineer/data-security/`) and maps them to controls — it does NOT re-run the PII scan or re-audit encryption.
- **solution-architect** owns data-residency and architecture decisions; compliance-officer flags a residency/control GAP as a finding, it does not change the architecture.
- **devops** owns infra controls (KMS, IAM, logging pipelines); compliance-officer points the evidence map at devops artifacts.
- **product-manager** owns the product scope that drives the signals map; compliance-officer reads it, confirms ambiguous signals, and does not redefine requirements.

---

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| "GDPR Art. 17 requires erasure" (from memory) | Open eur-lex this session, quote the article text, cite URL + date, tag `[verified]` |
| Citing `PCI Req 8.3.6` recalled from training | Retrieve PCI-DSS v4.0.1 live, confirm the sub-requirement number, quote it |
| Scoping SOC 2 because "enterprises like it" with no signal | Scope only on a present signal; record out-of-scope frameworks with the missing signal |
| Re-running a PII scan inside the compliance skill | Read security-engineer's PII inventory; map it — do not redo it |
| Marking a control `Met` with no file pointer | `Met` requires an Implementing-artifact `path:line`; else `Missing` |
| Silently passing a missing mandatory control | BLOCKING finding → remediation, or an "accepted with justification" override receipt |
| Inventing a control id to fill the SSP template | Leave it `not verified`; abstention is correct |

---

## Key Principle

**Scope deterministically from signals, map to pinned framework families, prove with an evidence map — and verify every specific id, article, and clause live against the official source this session. A confident hallucinated control id is the worst outcome; an honest "could not verify live" is recoverable.**
