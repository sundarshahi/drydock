# Phase 4: Enablement & Trust

## Objective

Arm the rep to win contested deals and clear buyer due diligence: an objection-handling matrix, competitive battlecards, a sales FAQ, and — the differentiator — a buyer-facing **security/compliance trust pack** assembled ENTIRELY from the security-engineer and compliance-officer evidence already on disk. Every trust-pack claim is a restatement of an artifact a previous agent wrote, traced in an evidence map. Sales never re-runs a scan, re-scopes a framework, or asserts a posture the evidence does not support. The trust pack turns the team's HARDEN-phase work into a sales asset.

## Inputs

- **Security evidence (CONSUMED — never re-derived)** — `drydock/security-engineer/`:
  - `data-security/pii-inventory.md`, `data-security/encryption-audit.md` (what data, how protected)
  - `supply-chain/` (SBOM, dependency/license audit)
  - `report/vapt-report.md` (pen-test / VAPT findings, retest status)
- **Compliance evidence (CONSUMED — never re-derived)** — `drydock/compliance-officer/`:
  - `scoping/frameworks.md` (which frameworks are IN scope, with editions)
  - `evidence/control-evidence-map.md` (control → artifact → status)
  - `docs/ssp.md`, `docs/dpia.md`, `docs/breach-runbook.md` (statutory docs)
- **Market narrative + competitors** — `drydock/growth-marketer/` (positioning, named competitors, differentiators) for battlecards.
- **Product + pricing** — for FAQ answers (capabilities, tiers).

If the security-engineer / compliance-officer artifacts are ABSENT, the trust pack degrades: every claim it would have made becomes "control in progress" / "audit not yet complete", explicitly flagged. Do NOT fill the gap with a posture from memory.

## Workflow

### Step 1: Objection-Handling Matrix

Catalog the objections this product will face and a grounded response for each. Use the **Feel-Felt-Found / acknowledge-reframe-evidence** pattern, and ground every rebuttal in a real artifact (a product capability, the ROI model, or the trust evidence).

```markdown
| Objection | Category | Response (acknowledge → reframe → evidence) | Proof source |
|-----------|----------|----------------------------------------------|--------------|
| "Too expensive" | price | reframe to value/ROI | `roi-calculator.md` |
| "We use <competitor>" | competition | differentiator reframe | battlecard + narrative |
| "Is our data safe?" | security | restate the security posture | trust pack (Step 4) |
| "Are you SOC 2 / GDPR compliant?" | compliance | restate the ACTUAL scoped posture | `compliance-posture.md` |
| "No time to switch" | status quo | migration story + cost of inaction | demo + ROI |
```

Responses must never overclaim — a security/compliance objection is answered ONLY with what the evidence supports.

### Step 2: Competitive Battlecards

One card per named competitor (names come from the growth-marketer narrative, not invented). Each card:

- **Their positioning** (as the market sees it — from the narrative, neutral).
- **Where we win / where they win** (honest; a battlecard that claims we win everything is useless).
- **Landmines** — questions that expose the competitor's gap (especially the trust/compliance gap if it is a real differentiator).
- **Pricing posture** — any public competitor pricing is WebSearch-verified live (Tier-1 volatile per `freshness-protocol.md`), cited with URL + date; never recalled.
- **Trap-setting** — how to frame the evaluation criteria around our strengths.

### Step 3: Sales FAQ

The recurring buyer questions and grounded answers, grouped: product/capabilities (from product), pricing/packaging (from Phase 1), implementation/onboarding (hand-off to customer-success), and security/compliance (pointer into the trust pack). Every answer cites its source; no answer is invented.

### Step 4: Build the Security/Compliance Trust Pack (the differentiator)

This is the core deliverable. Build a buyer-readable pack from the evidence on disk, and maintain an evidence map proving every claim is backed.

**4a. Security overview** (`docs/sales/trust/security-overview.md`) — restate, in buyer language:
- **Data protection** — encryption at rest / in transit, from `encryption-audit.md`. State only what the audit verified.
- **Data handling** — what PII is collected and how it is protected, from `pii-inventory.md`.
- **Application security** — the pen-test / VAPT posture from `report/vapt-report.md`: scope, that testing was performed, and current finding/retest status. Summarize severity counts; do NOT publish raw exploit detail to buyers.
- **Supply-chain integrity** — SBOM availability and dependency/license hygiene from `supply-chain/`.
- **Access control / operational security** — RBAC, audit logging, etc., as evidenced in the control-evidence map.

**4b. Compliance posture** (`docs/sales/trust/compliance-posture.md`) — restate the compliance-officer's ACTUAL scope and status, never aspirational:
- For each in-scope framework (from `scoping/frameworks.md`): the framework + edition, and the HONEST status. Distinguish precisely: "audit complete / report available under NDA" vs "Type II audit in progress, controls evidenced" vs "controls implemented, audit not yet started". Overstating ("SOC 2 certified" when it's in progress) is a deal-killing liability — restate the compliance-officer's status verbatim.
- Statutory posture (GDPR DPA available, breach-notification process per the breach runbook with its 72h/60-day clocks) — pointing at the real `dpia.md` / `breach-runbook.md`.
- Out-of-scope frameworks: state plainly when something is not in scope rather than implying coverage.

**4c. Security questionnaire answers** (`docs/sales/trust/security-questionnaire-answers.md`) — a pre-filled answer bank for the standard buyer questionnaires (SIG / CAIQ / VSA-style) so deals don't stall in procurement. Each answer maps to a control-evidence-map entry; questions with no evidence are answered "in progress / roadmap", never bluffed.

**4d. Subprocessors** (`docs/sales/trust/subprocessors.md`) — the third-party processors a buyer's DPA review requires, sourced from the architecture/compliance artifacts; flag as `confirm-with-compliance` if not fully enumerated in the evidence.

**4e. Evidence map** (`drydock/sales-strategist/trust/evidence-map.md`) — the audit trail: every buyer-facing claim → the source artifact + `path:line` it restates → status. This is what makes `trust_claims_unbacked == 0` checkable.

```markdown
| Buyer-facing claim | Source artifact | path:line | Status |
|--------------------|-----------------|-----------|--------|
| "Data encrypted at rest (AES-256)" | encryption-audit.md | :42 | evidenced |
| "SOC 2 Type II in progress" | scoping/frameworks.md | :15 | in-progress |
| "Pen test completed Q2, 0 criticals open" | vapt-report.md | :88 | evidenced |
```

## Output Deliverables

| Artifact | Path |
|----------|------|
| Objection-handling matrix | `docs/sales/enablement/objection-handling.md` |
| Competitive battlecards | `docs/sales/enablement/battlecards.md` |
| Sales FAQ | `docs/sales/enablement/faq.md` |
| Security overview (buyer-facing) | `docs/sales/trust/security-overview.md` |
| Compliance posture (buyer-facing) | `docs/sales/trust/compliance-posture.md` |
| Security questionnaire answer bank | `docs/sales/trust/security-questionnaire-answers.md` |
| Subprocessor list | `docs/sales/trust/subprocessors.md` |
| Trust-pack evidence map | `drydock/sales-strategist/trust/evidence-map.md` |

## Validation Loop

Before moving to Phase 5:
- [ ] Every objection rebuttal grounds in a real artifact (no invented counters)
- [ ] Battlecards name only real competitors (from the narrative); any competitor pricing is WebSearch-verified with URL + date
- [ ] Every trust-pack claim appears in the evidence map with a source `path:line` — `trust_claims_unbacked == 0`
- [ ] Compliance posture restates the compliance-officer's ACTUAL status (no "certified" where it's "in progress")
- [ ] Where security/compliance evidence is absent, the claim is "in progress" — never backfilled from memory
- [ ] Raw exploit detail from the VAPT report is NOT published to buyers (severity summary only)

## Quality Bar

The trust pack is a differentiator only if it is true. A buyer's security team will check it against reality — every claim must survive that. 100% of buyer-facing security/compliance statements trace to a security-engineer or compliance-officer artifact in the evidence map; the compliance posture never overstates scope or certification status; and the questionnaire answer bank lets a deal clear procurement without the rep improvising a compliance claim. Battlecards are honest (we lose some), objections are answered with evidence, and the whole pack reads as a restatement of the team's hardened work — never a sales fiction.
