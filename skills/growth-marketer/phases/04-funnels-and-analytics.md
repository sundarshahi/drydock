# Phase 4: Funnels & Analytics

## Objective

Make growth measurable. Define the acquisition funnel, a stable product-analytics **event taxonomy** for signup → activation → retention, an instrumentation plan (PostHog / GA4 or equivalent), an attribution model, and an A/B + growth-experiment backlog. The event taxonomy obeys the naming discipline in `observability-contract.md` — you specify the events; software-engineer/frontend-engineer EMIT them in code. Write working notes to `drydock/growth-marketer/analytics/`; the deliverable is `docs/marketing/analytics-plan.md`.

## Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| Observability contract | `drydock/.protocols/observability-contract.md` | The naming law your events follow — snake_case, base unit in name, low/bounded cardinality, no PII in properties, no per-feature renaming |
| Landing/lifecycle | `docs/marketing/website/`, `docs/marketing/lifecycle/` | The conversion surfaces + events the funnel must measure |
| Launch plan | `docs/marketing/launch-plan.md` | Channels (for attribution) and the waitlist capture event |
| Positioning | `docs/marketing/positioning.md` | Segments — funnels and reports are per segment, not blended |
| Shipped product | `frontend/`, `services/` | The real flows where events fire (so the taxonomy is instrumentable, not aspirational) |

## Steps

1. **Map the acquisition funnel per segment.** Define the stages from first touch to retained user: e.g. **visit → signup → activation → retention → referral/revenue**. For each priority segment (Phase 1), state what each stage MEANS for them (e.g. "activation = connected first data source"). A blended funnel hides segment truth — keep them separate where they diverge. **Deliverable:** a funnel diagram/table per segment.

2. **Define the product-analytics event taxonomy (under the observability contract).** Specify each event the funnel needs. The naming law from `observability-contract.md` applies — events and their properties are a CONTRACT that emitters and analytics must agree on; do NOT coin ad-hoc names like `btn_click_v2`. For each event record:

   | Field | Rule |
   |-------|------|
   | `event` name | `snake_case`, action-object, stable (`signup_completed`, `source_connected`, `activation_reached`); no synonyms, no per-feature renaming |
   | When it fires | The exact user action / server state, traceable to a real flow in code |
   | Properties | Bounded, low-cardinality, `snake_case` (`plan`, `segment`, `source_type`); base unit in name where numeric |
   | Cardinality / PII rule | NEVER put raw email, user id as a label, token, or unbounded value in a property — same redaction + cardinality discipline as the log/metric contract |
   | Funnel stage | Which funnel step this event marks |
   | Emitter | frontend-engineer (browser) or software-engineer (server) — they instrument it |

   Define the **activation event** explicitly — the single event that marks "user reached first value". This is the spine of the activation KPI (Phase 5).

3. **Write the instrumentation plan.** Choose the tool class (PostHog, GA4, Amplitude, or equivalent) and specify: where each event is emitted (client vs server — prefer server for revenue/activation truth), the identity model (anonymous → identified on signup, alias on the waitlist→signup join), the property schema, and a QA/validation step (events fire once, in order, with correct properties). State that the events join to the same `trace_id`/`service`/`route` discipline where they cross into backend telemetry — you do not invent a parallel vocabulary that contradicts the observability contract. This plan is the hand-off spec the engineers implement against.

4. **Define attribution.** Specify the attribution model (e.g. first-touch for channel learning + last-touch for conversion, or a simple position-based split) and the UTM/source taxonomy that feeds it (bounded `utm_source`/`utm_medium`/`utm_campaign` values mapped to the Phase 2 channels). State how the waitlist and referral sources are attributed. Keep source values bounded — an unbounded campaign string breaks both attribution and cardinality.

5. **Build the experiment backlog.** Produce a prioritized A/B + growth-experiment backlog. Each experiment row:

   | Field | Content |
   |-------|---------|
   | Hypothesis | "If we change X, then [metric] improves because [reason]" |
   | Funnel stage | Where it acts (acquisition / activation / retention) |
   | Primary metric | The single event-derived metric it moves (from the taxonomy) |
   | MDE + guardrail | Minimum detectable effect; the metric that must NOT regress |
   | Decision rule | Ship / kill / iterate threshold |
   | Effort / priority | ICE or PIE score |

   Prioritize by impact × confidence × ease. No experiment ships without a hypothesis, a primary metric, and a decision rule.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Per-segment acquisition funnel | `docs/marketing/analytics-plan.md` (funnel section) |
| Event taxonomy (contract-compliant) | `docs/marketing/analytics-plan.md` (event-taxonomy section) + `drydock/growth-marketer/analytics/events.md` |
| Instrumentation plan (tool, identity, QA) | `docs/marketing/analytics-plan.md` (instrumentation section) |
| Attribution model + UTM taxonomy | `docs/marketing/analytics-plan.md` (attribution section) |
| Experiment backlog (prioritized) | `docs/marketing/analytics-plan.md` (experiments section) |

## Validation Loop

Before moving on:
- The funnel is defined per priority segment, with each stage's meaning stated.
- Every event name follows `observability-contract.md` discipline — `snake_case`, stable, bounded/low-cardinality properties, NO PII or unbounded values; no ad-hoc renames.
- A single explicit **activation event** is defined and traceable to a real product flow.
- The instrumentation plan names the tool, the client/server split, the identity/alias model, and a QA validation step; emitters (frontend/software-engineer) are assigned per event.
- Attribution names a model and a bounded UTM/source taxonomy mapped to the Phase 2 channels.
- Every experiment has a hypothesis, a primary event-derived metric, an MDE + guardrail, and a decision rule.

## Quality Bar

The plan is instrumentable as written: an engineer can read the event taxonomy and emit exactly those events, with those properties, at those points — and the names won't collide with or contradict the observability contract. Funnels are per segment so the activation truth isn't blended away; the activation event is one specific, real moment of first value. Attribution and UTMs are bounded (no cardinality blow-up). The experiment backlog is decisions-ready — every row is a falsifiable hypothesis with a primary metric and a kill/ship rule. Every benchmark or tool-capability claim is live-cited; tag claims and close with a calibration summary.
