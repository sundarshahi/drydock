# Phase 1: Pricing & Packaging

## Objective

Choose a pricing model, package the product into tiers with explicit feature gates, justify every price point against LIVE-verified comparables, ground the prices in unit economics (CAC/LTV/margin and the COGS floor), and hand a billing/subscription requirements spec to software-engineer. This phase sets the numbers every later phase reuses — collateral ROI (Phase 2) and proposal pricing tables (Phase 5) read from here, so it runs first and its outputs are canonical. Pricing is the sales-strategist's SOLE authority; no other skill sets price points.

## Inputs

- **Market narrative** — `drydock/growth-marketer/` (ICP, value proposition, segment). Pricing must reflect the value story the marketing owns; it does not invent a different one.
- **Product + business model** — the shipped feature set + `drydock/product-manager/BRD/` (segment: SMB self-serve vs enterprise; declared business model: subscription/usage/freemium/enterprise).
- **COGS / unit cost** — `drydock/data-scientist/analysis/cost-model.md` if present (the per-unit/per-seat marginal cost that floors the margin). If absent, estimate conservatively from infra and flag the assumption.
- **Config** — any `pricing:` / `sales:` block in `.drydock.yaml` (declared model, currency, target ACV, comparables allowlist).

## Workflow

### Step 1: Select the Pricing Model

Evaluate the four canonical models against the product's value metric (the unit that grows with the value a customer gets). Choose ONE primary model; a secondary may layer on (e.g. tier + usage overage). Record the decision with rationale.

| Model | Value metric | Best fit | Watch-outs |
|-------|--------------|----------|------------|
| **Per-seat** | active users | collaboration/productivity tools where value scales with team size | penalizes adoption; seat-sharing leakage; weak for non-human/automation usage |
| **Usage-based** | API calls / GB / events / compute | infra/API/AI products where consumption ≈ value | revenue unpredictability for both sides; bill-shock risk; needs metering |
| **Tiered (feature/quota)** | packaged tier | most B2B SaaS — predictable, easy to buy | mis-gated tiers strand value or cannibalize upsell |
| **Value-based** | a business outcome (e.g. % of revenue processed, $ saved) | products with a directly measurable customer outcome | hard to meter and defend; needs a clean attribution model |

Pick the value metric FIRST (what should the customer pay more as they get more of?), then the model that prices that metric. State why the rejected models were rejected.

### Step 2: Package into Tiers + Feature Gates

Design 3-4 tiers (the canonical Good / Better / Best, optionally a free or trial entry and a custom Enterprise). For each tier define:

- **Target buyer** (which ICP segment / firmographic band)
- **Included value metric quota** (seats, usage units, etc.)
- **Feature gates** — the exact features that unlock at this tier. Gates MUST reference features that actually exist in the shipped product (cross-check the BRD / feature list) and must follow a coherent gating logic (scale gates, security/admin gates, support/SLA gates).

```markdown
| Tier | Target buyer | Value-metric quota | Key feature gates | Price |
|------|--------------|--------------------|--------------------|-------|
| Free / Trial | evaluator | <quota> | core only | $0 |
| Starter | SMB self-serve | <quota> | + integrations | $/mo |
| Pro | mid-market | <quota> | + SSO, roles, audit log | $/mo |
| Enterprise | enterprise | custom | + SAML/SCIM, DPA, dedicated support, SLA | Custom |
```

**Gating discipline:** put security/compliance features (SSO/SAML, SCIM, audit logs, DPA, data residency) at the tier the enterprise buyer lands on — these connect directly to the Phase 4 trust pack and are common deal-makers. Never gate a feature the product does not ship.

### Step 3: Justify Price Points Against LIVE Comparables

Price points are NOT guessed. For each tier, anchor the number against real market comparables verified THIS session — pricing is Tier-1 volatile per `freshness-protocol.md`; never state a competitor's price from memory.

1. WebSearch each named comparable's current public pricing page (respect any `.drydock.yaml` comparables allowlist).
2. Record a comparables table: competitor, tier, value metric, list price, source URL, date accessed, tag `[verified]`.
3. Position this product's price relative to comparables with an explicit strategy (penetration / parity / premium) and the reason (e.g. "premium +15% vs X, justified by the SOC 2 + audit-log differentiator").

```markdown
| Comparable | Tier | Value metric | List price | Source URL | Accessed | Verified |
|-----------|------|--------------|-----------|-----------|----------|----------|
| Acme | Pro | per-seat | $X/seat/mo | https://... | 2026-06-25 | [verified] |
```

If a comparable's pricing is "contact sales" (no public number), record that explicitly — do not fabricate a number.

### Step 4: Ground in Unit Economics

A price point that does not clear the unit-cost floor is a defect. Compute and record the unit-economics inputs:

- **COGS floor / gross margin** — price minus marginal cost per unit (from the cost-model, or a flagged estimate). Target gross margin band stated; any tier priced below its COGS floor is flagged BLOCKING.
- **CAC inputs** — the assumed cost to acquire a customer in this segment (sales-led vs self-serve changes this by an order of magnitude). State the assumption; do not assert a benchmark from memory — if you cite an industry CAC/LTV benchmark, WebSearch it.
- **LTV inputs** — expected lifetime = ARPA ÷ churn assumption; flag the LTV:CAC ratio target (commonly ~3:1 for a healthy B2B motion — verify if asserting it).
- **Payback period** — months of gross margin to recover CAC.

State every assumption explicitly. These are INPUTS for the team to validate, not asserted truths.

### Step 5: Hand Billing/Subscription Requirements to software-engineer

Pricing implies billing work that sales SPECIFIES but does not implement (software-engineer owns billing code). Write the requirements spec:

- **Plans & entitlements** — each tier's plan id, included quotas, and the entitlement checks the app must enforce.
- **Metering** — for any usage component: what event is metered, the aggregation window, and the overage rule.
- **Lifecycle** — proration on upgrade/downgrade, trial→paid conversion, mid-cycle plan changes, cancellation/refund policy.
- **Invoicing** — billing frequency, currency(ies), tax handling hook, dunning/failed-payment retry policy.
- **Provider hint** — note candidate billing providers but leave the choice to software-engineer/solution-architect; do not pin one.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Pricing decision log (model, tiers, comparables table, unit economics) | `drydock/sales-strategist/pricing/pricing-rationale.md` |
| Public-facing pricing & packaging | `docs/sales/pricing.md` |
| Billing/subscription requirements (hand-off to software-engineer) | `drydock/sales-strategist/pricing/billing-requirements.md` |

## Validation Loop

Before moving to Phase 2:
- [ ] One pricing model chosen with a written rationale and the rejected models' reasons
- [ ] Every tier has a target buyer, a value-metric quota, and feature gates that reference REAL shipped features
- [ ] Every price point cites ≥1 comparable verified live this session (URL + date), OR records that the comparable is "contact sales"
- [ ] Every tier clears its COGS floor; any below-floor tier is flagged BLOCKING, not shipped silently
- [ ] CAC/LTV/margin inputs are stated as assumptions (benchmarks WebSearch-verified, not recalled)
- [ ] Billing requirements spec written and ready for software-engineer

## Quality Bar

Pricing is a defended decision, not a number. "Pro is $49/seat" is not a decision — "Pro is $49/seat: parity with Acme Pro ($48, verified 2026-06-25), +SSO/audit-log gates that comparable charges Enterprise for; gross margin 82% over the $8.80 COGS floor; LTV:CAC modeled at 3.4:1 on a self-serve CAC assumption of $X" is. Every comparable is live-verified with a URL and date; every tier clears its unit-cost floor; and the billing hand-off is concrete enough for software-engineer to build against without re-deriving the pricing logic.
