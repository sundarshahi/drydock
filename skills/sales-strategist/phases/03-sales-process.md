# Phase 3: Sales Process

## Objective

Define the repeatable motion that moves a lead to a closed deal: a specific ICP, a qualification framework (MEDDIC or BANT), pipeline stages with explicit entry/exit criteria, the CRM schema (fields + stages) that operationalizes them, outbound sequence templates (email/LinkedIn), and a discovery-call script. The process is grounded in the growth-marketer's ICP narrative and the segment signals from the BRD — sales operationalizes the ICP into a qualification and pipeline machine; it does not redefine the market segment.

## Inputs

- **ICP narrative + segment** — `drydock/growth-marketer/` (target market, persona, messaging) and `drydock/product-manager/BRD/` (customer segment: SMB self-serve vs enterprise sales-led — this decides MEDDIC vs BANT and the whole motion).
- **Pricing & tiers** — `docs/sales/pricing.md` (the entry tier and ACV band shape the motion: self-serve PLG vs sales-assisted vs enterprise).
- **Collateral** — `docs/sales/collateral/` (the demo script and one-pager that attach to pipeline stages).

## Workflow

### Step 1: Define the ICP (specific, not "everyone")

Translate the growth-marketer ICP narrative into a crisp, qualify-against-able profile. Specify:

- **Firmographics** — industry/vertical, company-size band (employees / revenue), geography, tech-stack signals.
- **Behavioral / trigger signals** — the buying triggers that say "now" (a funding round, a new regulation, a hire of role X, a competitor switch, hitting a usage threshold).
- **The buyer + the champion** — the economic buyer (who signs), the champion (who advocates internally), and the typical blockers (security, procurement, finance).
- **Anti-ICP / disqualifiers** — who to walk away from fast (too small to afford the COGS floor, wrong segment, no trigger). Disqualification speed is a feature.

### Step 2: Choose the Qualification Framework (MEDDIC vs BANT)

Pick by deal complexity (the BRD segment + ACV band decide):

- **BANT** (Budget, Authority, Need, Timeline) — lighter; fits SMB / transactional / self-serve-assisted deals.
- **MEDDIC** (Metrics, Economic buyer, Decision criteria, Decision process, Identify pain, Champion) — fits mid-market/enterprise deals with multiple stakeholders and a procurement process.

For the chosen framework, write a per-criterion **exit question** the rep must be able to answer before advancing — qualification is a checklist, not a vibe.

```markdown
| MEDDIC criterion | What it answers | Exit question (must be answerable to advance) |
|------------------|-----------------|------------------------------------------------|
| Metrics | the quantified value | "What number does the buyer need to move, by how much?" |
| Economic buyer | who signs | "Who controls the budget and have we met them?" |
| Decision criteria | how they'll choose | "What are their must-haves vs nice-to-haves?" |
| Decision process | the steps to a signature | "What are the procurement + security review steps and timeline?" |
| Identify pain | the compelling event | "What breaks if they do nothing?" |
| Champion | the internal seller | "Who sells for us when we're not in the room?" |
```

### Step 3: Pipeline Stages with Entry/Exit Criteria

Define 5-7 stages. Every stage has an explicit entry criterion (what makes a deal land here) and an exit criterion (what must be true to advance) — a stage without exit criteria is sandbagging. Tie the relevant collateral to each stage.

```markdown
| Stage | Entry criterion | Exit criterion (to advance) | Attached collateral |
|-------|-----------------|------------------------------|----------------------|
| 1. Lead | matches ICP signal | meeting booked | one-pager |
| 2. Discovery | meeting booked | pain + metrics + economic buyer identified | discovery script |
| 3. Demo / Eval | qualified pain | value beats landed; next step agreed | demo script, ROI calc |
| 4. Proposal | mutual fit confirmed | proposal sent + reviewed | proposal template (Phase 5) |
| 5. Security review | enterprise + data sensitivity | trust pack delivered, questionnaire cleared | trust pack (Phase 4) |
| 6. Negotiation / Legal | proposal accepted in principle | terms agreed (legal review flagged) | order form (Phase 5) |
| 7. Closed-Won | signed | hand off to customer-success | onboarding hand-off |
```

The security-review stage exists specifically because the Phase 4 trust pack is a differentiator — make it an explicit stage for enterprise deals.

### Step 4: CRM Setup (fields + stages)

Operationalize the above into a CRM schema (provider-agnostic; do not pin a CRM). Specify:

- **Stages** — the pipeline stages from Step 3 as CRM deal stages, each with its exit criterion as the "required to advance" rule.
- **Required fields** per object: Lead/Contact (source, ICP-fit score, persona), Deal/Opportunity (stage, ACV/tier, value metric, qualification fields from Step 2, compelling-event date, next step + date), Account (segment, security-review status).
- **Hygiene rules** — every open deal has a next-step + date; stale-deal SLA; closed-lost reason captured (for the growth-marketer/product feedback loop).

### Step 5: Outbound Sequence Templates (email / LinkedIn)

Multi-touch sequences that restate the marketing narrative's hook — never a fabricated claim, never spam. Provide:

- A **cold-outbound** sequence (e.g. 5-7 touches over ~2-3 weeks: email → LinkedIn → email → break-up), each touch with a purpose and a personalization slot tied to an ICP trigger signal.
- A **trigger-based** sequence (fired by a buying signal from Step 1).
- Each template uses merge fields, leads with the buyer's pain (from the narrative), and has ONE clear CTA. Note relevant deliverability/consent basics (e.g. honor opt-out; respect CAN-SPAM/GDPR-marketing-consent where the compliance scope applies) — verify any specific legal requirement, don't recall it.

### Step 6: Discovery-Call Script

A script that powers Step 2 qualification. Structure: rapport → agenda-set → pain discovery (open questions mapping to the qualification criteria) → quantify the pain (feeds the ROI calculator) → identify the buying process and stakeholders → mutual next step. Provide the actual question list, grouped by qualification criterion, so a rep can run it and fill the CRM fields directly.

## Output Deliverables

Write to `docs/sales/process/`:

| File | Contents |
|------|----------|
| `icp.md` | Firmographics, trigger signals, buyer/champion, anti-ICP |
| `qualification.md` | Chosen framework (MEDDIC/BANT) with per-criterion exit questions |
| `pipeline-stages.md` | Stages with entry/exit criteria + attached collateral |
| `crm-setup.md` | Provider-agnostic CRM stages, required fields, hygiene rules |
| `outbound-sequences.md` | Email/LinkedIn sequence templates with personalization slots |
| `discovery-script.md` | Discovery question list grouped by qualification criterion |

## Validation Loop

Before moving to Phase 4:
- [ ] ICP is specific (firmographic + behavioral signals + anti-ICP) — not "any company"
- [ ] Qualification framework chosen to match the segment; every criterion has an exit question
- [ ] Every pipeline stage has BOTH an entry and an exit criterion
- [ ] CRM fields capture every qualification criterion + a next-step + closed-lost reason
- [ ] An explicit security-review stage exists for enterprise deals (wires to Phase 4)
- [ ] Outbound templates restate the marketing narrative; one CTA each; opt-out/consent noted

## Quality Bar

A new rep can run this process end-to-end without guessing. The ICP disqualifies bad-fit leads as fast as it qualifies good ones. No deal can advance a stage without satisfying a written exit criterion (no happy-ears forecasting). The qualification fields and discovery questions line up 1:1 with the CRM schema, so running the discovery call populates the pipeline automatically. Outbound is grounded in the marketing narrative and respects consent — never invented claims, never spray-and-pray.
