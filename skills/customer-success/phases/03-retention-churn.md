# Phase 3: Retention & Churn

## Objective

Keep customers and grow their value. Build a **customer health score** from measurable signals, define churn-risk signals each paired with an intervention play, write the renewal and expansion playbooks, stand up an NPS/CSAT program, and produce a QBR template for high-value accounts. Every signal maps to a real product/usage event; every benchmark is grounded with WebSearch. This phase measures and intervenes — it does not change the product.

## Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| Activation milestones | `drydock/customer-success/onboarding/journey-map.md` | Leading indicators of retention — feed the health score |
| Usage/retention analytics | `drydock/growth-marketer/` | Cohort retention, usage frequency, feature adoption — the raw signals |
| Product | `services/`, `frontend/` | Which events are actually instrumented (a signal needs a measurable event) |
| BRD segment + model | `drydock/product-manager/BRD/` | Revenue model (subscription/usage/seat), segments → renewal/expansion + QBR scope |
| Support data | `docs/customer-success/support-runbook.md` | Ticket volume/sentiment as a health input |

## Workflow

### Step 1: Build the Customer Health Score

Compose a weighted score over measurable signals. Each signal must map to a real, instrumented event — no measurable input means it is not a signal (raise an instrumentation gap to solution-architect/software-engineer rather than inventing it). Weights sum to 100.

| Signal | Measurable input (event/metric) | Weight | Healthy / At-risk threshold |
|--------|---------------------------------|--------|------------------------------|
| Product adoption | core-action frequency / active days | e.g. 30 | ≥ N actions/week / 0 in 14 days |
| Breadth of use | # key features used | e.g. 15 | ≥ 3 features / 1 feature |
| Activation depth | activation milestones reached | e.g. 15 | all / stalled before first value |
| Engagement trend | usage WoW direction | e.g. 15 | rising/flat / declining 3 wks |
| Support sentiment | ticket volume + CSAT | e.g. 10 | low+positive / spike or negative |
| Relationship (B2B) | exec sponsor active, QBR attended | e.g. 10 | engaged / gone dark |
| Commercial | seats used vs. licensed, payment health | e.g. 5 | growing / shrinking, failed payment |

Define **score bands** with names and actions:

| Band | Score | Meaning | Default action |
|------|-------|---------|----------------|
| Healthy | 80-100 | Thriving | Expansion play candidate |
| Neutral | 50-79 | Stable, watch | Nudge toward next value |
| At-risk | 25-49 | Churn signals present | Trigger intervention play |
| Critical | 0-24 | Likely to churn | Human outreach now |

State the **refresh cadence** (e.g. recompute daily; alert on band transition). Document the score as a reproducible formula, not a vibe.

### Step 2: Define Churn-Risk Signals + Interventions

For each churn-risk signal, pair it with a concrete intervention play (trigger → action → owner → success measure). A signal with no paired play is incomplete.

| Churn signal | Detection (event) | Intervention play | Owner | Success measure |
|--------------|-------------------|-------------------|-------|------------------|
| Usage drop-off | 0 core actions in 14 days | Re-engagement sequence + "what's blocking you" outreach | Tier 1 / CSM | Returns to active in 14 days |
| Failed onboarding | stalled before first value | Guided setup offer + relevant help article | CSM | Reaches first value |
| Negative sentiment | CSAT ↓ or ticket spike | Escalate to specialist + apology + fix ETA | Tier 2 | CSAT recovers |
| Sponsor churn (B2B) | champion left / went dark | Multithread to new contacts | CSM | New active sponsor |
| Payment failure | dunning event | Dunning sequence + retry | Billing | Recovered |

Set a **save-rate target** for at-risk interventions, grounded against a researched benchmark (WebSearch current churn/save-rate norms for the model; cite source + date — not from memory).

### Step 3: Renewal Playbook

Define the renewal motion for subscription/contract customers, working back from the renewal date.

| Window | Action | Owner | Goal |
|--------|--------|-------|------|
| T-90 days | Health review + value recap (usage delivered) | CSM | Surface risk early |
| T-60 | Renewal conversation, address blockers | CSM | Confirm intent |
| T-30 | Commercials + paperwork | CSM / sales | Close renewal |
| T-0 | Renew or run save play | CSM | Retain |
| Post | Confirm + set next-period goals | CSM | Set up expansion |

Calibrate the renewal-rate / gross-retention target against a researched benchmark for the segment and model (WebSearch; cite). Tie health-band transitions into the renewal forecast (Critical accounts = renewal risk).

### Step 4: Expansion Playbook

Define how Healthy accounts grow (upsell/cross-sell/seat expansion), gated on health so you never push expansion at an at-risk account.

| Expansion trigger | Signal | Play | Owner |
|-------------------|--------|------|-------|
| Approaching usage/seat limit | usage ≥ X% of plan | Proactive upgrade offer | CSM / sales |
| Adopting advanced features | feature depth rising | Cross-sell adjacent module | CSM |
| Multi-team adoption | new teams active | Org-wide expansion / volume tier | CSM / sales |

Net revenue retention (NRR) is the north-star outcome of retention + expansion minus churn — calibrate an NRR target against a researched benchmark (WebSearch; cite). Expansion plays only fire on Healthy-band accounts.

### Step 5: NPS / CSAT Program

Stand up the satisfaction-measurement program:
- **CSAT** — post-resolution (per ticket) and post-onboarding; 1-5 scale; trigger and timing defined.
- **NPS** — relationship survey on a cadence (e.g. quarterly), segmented by cohort; 0-10 scale.
- **Closing the loop** — every detractor (NPS ≤ 6) and low CSAT triggers an outreach play; passives/promoters route to expansion/advocacy. Feed verbatims into the Phase 4 VoC taxonomy.
- Benchmark NPS/CSAT targets against researched norms for the category (WebSearch; cite). Do not assert a "good NPS" number from memory.

### Step 6: QBR Template (High-Value Accounts)

Produce a Quarterly Business Review template for high-value / strategic accounts (segment threshold from the BRD/commercial model). The template covers: value delivered (usage + outcomes vs. their goals), health-score trend, open issues + roadmap items they care about (sourced from Phase 4 VoC requests, NOT promises — PM owns the roadmap), expansion opportunities, and next-quarter success plan. The QBR is a relationship + value-realization instrument, not a sales pitch.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Health-score model (signals, weights, bands, cadence) | `drydock/customer-success/retention/health-score.md` |
| Retention playbooks: churn interventions, renewal, expansion, NPS/CSAT program, QBR template | `docs/customer-success/retention-playbook.md` |

## Validation Loop

Before moving to Phase 4:
- Every health-score signal maps to a measurable, instrumented event with a weight and a band threshold; weights sum to 100; refresh cadence stated
- Every churn-risk signal is paired with an intervention play (trigger → action → owner → success measure); the save-rate target is grounded
- Renewal + expansion playbooks have time-boxed steps and owners; expansion gated on Healthy band
- Renewal-rate / NRR / NPS / CSAT targets are calibrated against WebSearch'd benchmarks (source + date), not memory
- The QBR template surfaces VoC requests as items PM owns, not as roadmap promises
- Any signal lacking a measurable input is raised as an instrumentation gap, not invented

## Quality Bar

- The health score is a reproducible weighted formula over real events with named bands and a cadence — not a subjective rating.
- Every churn signal has a matched intervention; no detection without a response.
- Retention targets (renewal, NRR, NPS, CSAT, save-rate) are each grounded against a researched benchmark, never asserted from memory.
- Expansion never fires on an at-risk account, and the QBR realizes value without promising scope the product-manager has not committed.
