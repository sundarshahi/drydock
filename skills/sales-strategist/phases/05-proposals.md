# Phase 5: Proposals

## Objective

Produce the documents that turn a qualified, trust-cleared deal into a signature: a proposal template, a quote template, a Statement of Work (SOW) template, an order-form template, and an MSA/terms outline. Every pricing figure reuses the Phase 1 numbers verbatim, and **every legal artifact is a TEMPLATE marked `REQUIRES LEGAL REVIEW — not binding as generated`**, logged in a legal-review register. Sales templates and flags legal documents; it never authors binding contract language or represents a generated document as enforceable. Legal counsel (out of band) owns the binding language.

## Inputs

- **Pricing & packaging** — `docs/sales/pricing.md` + `drydock/sales-strategist/pricing/pricing-rationale.md` (the tiers, price points, and discount guardrails the proposal/quote/order-form tables reuse — no re-derivation, no drift).
- **Trust pack** — `docs/sales/trust/` (the security/compliance posture a SOW/MSA references for DPA, subprocessors, breach-notification, and security commitments).
- **Process** — `docs/sales/process/` (the qualification + close stage these documents attach to).
- **Compliance scope** — `drydock/compliance-officer/scoping/frameworks.md` (whether a DPA / BAA / data-residency commitment must be referenced — and flagged for legal, since the binding form is counsel's).

## Workflow

### Step 1: Proposal Template

A buyer-facing proposal a rep customizes per deal. Sections: executive summary (the buyer's pain + outcome, from the narrative/discovery), proposed solution (tier + scope), the value/ROI summary (from the Phase 2 calculator with the buyer's inputs), pricing (the exact Phase 1 tier table), implementation/onboarding outline (hand-off to customer-success), security/compliance summary (a pointer to the trust pack), timeline, and the next step / acceptance. Merge fields for everything deal-specific. The proposal is sales collateral, not a contract — but if it contains any commitment language, flag it for legal.

### Step 2: Quote Template

The itemized price quote. Fields: line items (tier, add-ons, usage estimate), quantity (seats / usage units), unit price (from Phase 1, verbatim), term (monthly/annual), discount (within the Phase 1 discount guardrails — a discount that breaks the COGS floor from Phase 1 is flagged, not granted silently), subtotal/total, currency, valid-until date, and the tax-handling note. The quote reuses the pricing source of truth — it never restates a price that disagrees with `docs/sales/pricing.md`.

### Step 3: Statement of Work (SOW) Template — LEGAL REVIEW REQUIRED

A template for deals with services/implementation scope. Sections: scope of services, deliverables, milestones/timeline, acceptance criteria, assumptions/exclusions, fees & payment schedule, and a change-control process. Because a SOW creates obligations, the template carries the prominent flag and a `<!-- LEGAL: review scope, liability, acceptance, and change-control clauses -->` marker on the obligation-bearing sections.

### Step 4: Order-Form Template — LEGAL REVIEW REQUIRED

The transactional document that, when signed, orders the product under the MSA. Fields: customer/legal entity, the ordered tier/quantities/price (from the quote), subscription term, start date, auto-renewal terms, payment terms, and the MSA incorporation-by-reference line. The order form is binding-by-design, so it carries the most prominent `REQUIRES LEGAL REVIEW` flag — sales fills the commercial fields; counsel owns the legal terms.

### Step 5: MSA / Terms Outline — LEGAL REVIEW REQUIRED (outline only)

An OUTLINE of the Master Service Agreement clauses a B2B SaaS deal needs — NOT drafted binding language. List the clause headings and a one-line intent each, so counsel can draft from a complete checklist:

```markdown
| Clause | Intent (one line) | Why it matters | Legal owns |
|--------|-------------------|----------------|------------|
| Definitions | terms used | clarity | ✓ |
| License / Subscription grant | what's granted | scope of use | ✓ |
| Fees & payment | commercial terms | revenue | ✓ (commercial from quote) |
| Term & termination | duration / exit | renewal/churn | ✓ |
| Data protection / DPA | per compliance scope | GDPR/privacy | ✓ (ref trust pack) |
| Security commitments | per trust pack | buyer assurance | ✓ (ref trust pack) |
| Confidentiality | NDA terms | protection | ✓ |
| Warranties & disclaimers | what's promised | risk | ✓ |
| Limitation of liability | liability cap | risk | ✓ |
| Indemnification | who covers what | risk | ✓ |
| SLA / support | uptime/support tier | from pricing tier | ✓ |
| Governing law / disputes | jurisdiction | enforceability | ✓ |
```

Where the compliance scope (Phase 4 / compliance-officer) requires a DPA, BAA, or data-residency commitment, NOTE it as a required attachment and flag for legal — do not draft the binding form.

### Step 6: Legal-Review Register

Maintain the register that proves nothing binding ships unflagged. Every legal artifact, its review status (`pending-legal`), and the specific clauses/sections flagged for counsel.

```markdown
| Artifact | Type | Status | Clauses flagged for legal |
|----------|------|--------|----------------------------|
| sow-template.md | SOW | pending-legal | scope, acceptance, liability |
| order-form-template.md | order form | pending-legal | auto-renewal, payment, MSA incorporation |
| msa-terms-outline.md | MSA outline | pending-legal | all (outline only — counsel drafts) |
```

## Output Deliverables

| Artifact | Path | Legal flag |
|----------|------|-----------|
| Proposal template | `docs/sales/proposals/proposal-template.md` | flag if commitment language present |
| Quote template | `docs/sales/proposals/quote-template.md` | commercial — pricing source-of-truth |
| SOW template | `docs/sales/proposals/sow-template.md` | `REQUIRES LEGAL REVIEW` |
| Order-form template | `docs/sales/proposals/order-form-template.md` | `REQUIRES LEGAL REVIEW` |
| MSA / terms outline | `docs/sales/proposals/msa-terms-outline.md` | `REQUIRES LEGAL REVIEW` (outline only) |
| Legal-review register | `drydock/sales-strategist/proposals/legal-review-register.md` | tracks all flags |

## Validation Loop

Before completing:
- [ ] Every pricing figure in every template matches `docs/sales/pricing.md` verbatim (no drift)
- [ ] No discount in the quote template breaks the Phase 1 COGS floor / guardrails without a flag
- [ ] SOW, order-form, and MSA outline each carry `REQUIRES LEGAL REVIEW — not binding as generated`
- [ ] The MSA artifact is an OUTLINE (clause headings + intent), not drafted binding language
- [ ] Every legal artifact appears in the legal-review register with `pending-legal` status
- [ ] DPA/BAA/residency requirements from the compliance scope are noted as required attachments, flagged for legal
- [ ] `legal_templates_flagged_for_review == legal_templates_total` (receipt metric)

## Quality Bar

These templates accelerate a close without creating legal exposure. Pricing is internally consistent to the cent with Phase 1 — a quote never contradicts the pricing page. The MSA is a clause checklist for counsel, never a fabricated contract; the SOW and order form are clearly marked non-binding templates; and the legal-review register makes it impossible to ship a binding-looking document without a flag. A rep can assemble a complete, professional deal packet from these, and legal can pick it up knowing exactly what needs their drafting. Nothing the sales-strategist generates is ever represented as an enforceable contract.
