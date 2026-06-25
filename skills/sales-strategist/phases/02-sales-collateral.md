# Phase 2: Sales Collateral

## Objective

Produce the deal-facing assets a rep uses to move a prospect from interest to decision: a one-pager, a pitch-deck outline, a demo script tied to the top product flows, an ROI/value calculator, and a case-study template. Every asset RESTATES the growth-marketer narrative (the source of truth for positioning/messaging) and references only product capabilities that actually ship. Sales translates the narrative into a selling motion; it never authors a new positioning.

## Inputs

- **Market narrative** — `drydock/growth-marketer/` (positioning, messaging pillars, value proposition, proof points, ICP). This is CONSUMED verbatim; quote it, do not re-invent it. On any conflict, the marketing narrative wins and you raise a finding.
- **Pricing** — `docs/sales/pricing.md` + `drydock/sales-strategist/pricing/pricing-rationale.md` (the "ask" and the value-to-price story).
- **Product + flows** — the shipped product and `drydock/product-manager/BRD/` (the real top user flows the demo will walk, the features the value drivers come from).

## Workflow

### Step 1: One-Pager (leave-behind)

A single page a champion can forward internally. Structure:

- **Headline** — the marketing one-liner (from growth-marketer, verbatim).
- **The problem** — the pain, in the buyer's words (from the narrative).
- **The solution** — what the product does, 3 bullets, each mapping to a real capability.
- **Proof** — metrics/logos/quotes that EXIST (from growth-marketer proof points or product-manager outcomes); if none exist yet, use a labeled placeholder `<!-- proof: pending real reference -->`, never a fabricated stat.
- **Differentiators** — including the security/compliance trust angle (forward-reference Phase 4).
- **The ask / next step** — book a demo / start a trial, with the pricing entry point.

### Step 2: Pitch-Deck Outline (problem → solution → proof → ask)

Outline the slides (this is an outline, not designed slides). Canonical arc:

```markdown
1. Title / one-liner            (the marketing hook)
2. The problem                  (buyer pain, quantified where the narrative quantifies it)
3. Why now                      (market shift / urgency from the narrative)
4. The solution                 (product overview — real capabilities)
5. How it works                 (the top product flow, 3 steps)
6. Proof                        (case study / metrics / logos — real only)
7. Differentiation              (incl. the security/compliance trust differentiator)
8. Pricing & packaging          (the tiers from Phase 1 — value-framed, not just numbers)
9. The ask                      (clear next step + mutual action plan)
```

Each slide gets a one-line speaker note and a "source" pointer (which narrative/product/pricing artifact the content comes from). No slide asserts a claim without a source.

### Step 3: Demo Script Tied to the Top Product Flows

The demo proves the solution slide. Tie each beat to a REAL flow that exists in the shipped product — verify the flow before scripting it (open the product / BRD; do not script a flow from assumption).

```markdown
| Beat | Buyer pain addressed | Product flow (real) | What the rep shows | "Aha" moment |
|------|----------------------|---------------------|---------------------|--------------|
| 1 | <pain> | <flow name in product> | <action> | <value landed> |
```

Cover: the setup ("here's the world before"), 2-3 value beats on the top flows, the differentiator beat (often the trust/security flow), and the close ("here's what changes for you"). Include a discovery-driven branch note ("if the prospect cares about X, lead with beat N").

### Step 4: ROI / Value Calculator

A calculator the rep fills in WITH the prospect — never a hardcoded fabricated number. Define:

- **Value drivers** — the 2-4 levers this product moves (time saved, error reduction, revenue lift, cost avoided), each grounded in a real product capability.
- **Inputs** — the buyer's own numbers (team size, current cost, volume, current rate). The model is `value = f(buyer_inputs, product_effect)`.
- **Assumptions** — every product-effect assumption (e.g. "30% faster") is labeled as an assumption the buyer can adjust, with the rationale; if you cite a benchmark for the effect size, WebSearch-verify it.
- **Output** — annual value vs the price from Phase 1 → payback / ROI multiple.

```markdown
ROI = (annual_value_created − annual_price) / annual_price
annual_value_created = Σ (driver_i_effect × buyer_input_i)
```

State that all figures are estimates from the buyer's inputs, not guarantees.

### Step 5: Case-Study Template

A reusable template (not a fabricated case study). Sections: customer profile, the problem, why they chose us, the solution deployed, **quantified results** (with a `<!-- metric: provided by customer -->` placeholder until a real customer supplies them), and a pull-quote slot. The template makes clear results are filled from REAL customer data, never invented.

## Output Deliverables

Write to `docs/sales/collateral/`:

| File | Contents |
|------|----------|
| `one-pager.md` | The leave-behind, sourced from the narrative + real proof |
| `pitch-deck-outline.md` | Slide-by-slide outline with speaker notes + source pointers |
| `demo-script.md` | Beat table tied to real product flows + discovery branches |
| `roi-calculator.md` | Value-driver model, inputs, labeled assumptions, ROI formula |
| `case-study-template.md` | Reusable template with placeholders for real customer data |

## Validation Loop

Before moving to Phase 3:
- [ ] Every collateral claim restates the growth-marketer narrative (cited) — no forked positioning
- [ ] Every demo beat maps to a flow that ACTUALLY exists in the shipped product (verified)
- [ ] The ROI calculator uses buyer inputs + labeled assumptions — zero hardcoded fabricated outcomes
- [ ] No fabricated proof points/metrics/logos; placeholders used where real proof is pending
- [ ] Pricing references reuse the Phase 1 numbers verbatim (no drift)

## Quality Bar

Collateral that invents a story or a stat destroys trust in the whole deal. Every claim traces to the marketing narrative, a real product capability, or the buyer's own numbers. A reviewer can point at any sentence in the one-pager or any deck slide and find its source pointer. The demo script can be run against the actual product without the rep hitting a flow that doesn't exist. The ROI model is honest math on the buyer's inputs, with every assumption visible and adjustable.
