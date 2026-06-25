# Phase 1: Onboarding & Activation

## Objective

Get every new customer to **first value** as fast as possible. Define what "value" means per BRD persona, map the journey from signup to that first valuable outcome, set a concrete time-to-value (TTV) target grounded against a researched benchmark, and specify the in-app guidance (checklists, empty states), welcome/setup sequence, and activation milestones that drive a user there. This phase produces a journey map (workspace) and an onboarding deliverable (docs); it does NOT change the product or rewrite docs.

## Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| Personas + scope | `drydock/product-manager/BRD/` | Each persona, their goal, the product's success metrics — what "value" is for them |
| Product (frontend/setup) | `frontend/`, `services/` | The actual signup → setup → first-action flow; where friction lives |
| Existing docs | `docs/getting-started/` | Quickstart / setup content to LINK from onboarding (do not rewrite) |
| Activation analytics | `drydock/growth-marketer/` | Signup→activation funnel + drop-off points, if present |

If the BRD is missing, STOP — you cannot define first-value without personas (per SKILL Input Classification, this is Critical).

## Workflow

### Step 1: Define First Value Per Persona

For each persona in the BRD, define the single **first valuable outcome** — the moment the user gets the core benefit, not account creation. Express it as a measurable in-product event so it can be instrumented.

| Persona (from BRD) | First value (the "aha") | Measurable activation event | Why it matters to them |
|--------------------|-------------------------|-----------------------------|------------------------|
| e.g. Solo developer | First successful API call returns data | `api.first_success` within session 1 | Proves the product works for their use case |
| ... | ... | ... | ... |

Rule: "signed up" is NOT activation. Activation is the first event that delivers the persona's stated goal. If a persona has no measurable first-value event in the product, flag it as a product/instrumentation gap (raise to product-manager / solution-architect — do not invent the feature).

### Step 2: Set the Time-to-Value Target (grounded)

Set a concrete TTV target (e.g. "median user reaches first value within 24h; in-session for self-serve personas"). Ground the target against a researched benchmark — WebSearch current TTV / activation-rate norms for the relevant model (self-serve PLG vs. sales-assisted, B2B vs. B2C) and cite source + date. Do NOT state a benchmark from memory (`freshness-protocol.md`). Record both the target and the benchmark it is calibrated against.

### Step 3: Map the Onboarding Journey

For each persona, map the journey from entry to first value and beyond, stage by stage. For every stage record: the user's goal, what the product shows, the friction risk, and the intervention that reduces it.

| Stage | User goal | In-product surface | Friction risk | Intervention |
|-------|-----------|--------------------|----------------|--------------|
| Signup | Create account | Signup form | Form length, email verify delay | Social/SSO, magic link |
| Setup | Configure to their case | Setup wizard / empty state | Blank-slate paralysis | Templates, sample data, checklist |
| First action | Do the core thing | Primary surface | Doesn't know where to start | Guided tour, tooltip, "do this first" CTA |
| First value | Get the outcome | Result view | Outcome unclear | Success state + "what's next" |
| Habit | Return + expand | Dashboard | No reason to come back | Day-2/7 nudges, second-value prompt |

Keep a **friction log** in the journey map: each friction point, its evidence (analytics drop-off or a product observation `path`), and the proposed mitigation.

### Step 4: Define Activation Milestones

Define an ordered set of milestones from signup to a "set-up-for-success" account (the leading indicator of retention). Each milestone is a measurable event with a target completion rate and the nudge that drives it.

| # | Milestone | Measurable event | Target completion | Nudge if not done |
|---|-----------|------------------|-------------------|-------------------|
| 1 | Account verified | `account.verified` | 90% | Resend + reminder email |
| 2 | First value reached | persona activation event | 60% in TTV window | In-app checklist + day-1 email |
| 3 | Core habit formed | N core actions / week | 40% | Day-7 nudge, use-case tip |

### Step 5: Specify In-App Guidance (Checklists & Empty States)

Specify (do not build) the in-app guidance that drives milestones:
- **Setup checklist** — the ordered, dismissible task list shown to new accounts; each item maps to a milestone event; show progress.
- **Empty states** — for each key surface, the empty-state copy + primary CTA that points at the next milestone (turn blank slates into guided first steps).
- **Tooltips / product tour** — the minimal guided tour for the first session (3-5 steps max; over-touring is friction).
- **Sample data / templates** — where a blank account blocks first value, specify the seed data or templates that let a user reach value before configuring.

Write these as a spec (surface, trigger, copy, CTA, milestone it advances) — the implementation is owned by frontend-engineer; you own the design of the activation guidance.

### Step 6: Write the Welcome / Setup Sequence

Specify the lifecycle message sequence that supports activation (channel-appropriate: email/in-app):

| Trigger | Timing | Channel | Goal | Content |
|---------|--------|---------|------|---------|
| Signup | t+0 | Email + in-app | Orient + first step | Welcome, the ONE thing to do first, link to quickstart in `docs/getting-started/` |
| No activation | t+1 day | Email | Remove friction | Use-case tip, link to the relevant existing doc/help-center article |
| Activated | t+1 day | In-app | Reinforce + expand | Celebrate, point to second value |
| No return | t+7 days | Email | Re-engage | "Here's what you're missing" + path back to value |

Link to the EXISTING getting-started docs; do not rewrite them (technical-writer is the documentation authority).

## Output Deliverables

| Artifact | Path |
|----------|------|
| Onboarding journey map + activation milestones + friction log + TTV target | `drydock/customer-success/onboarding/journey-map.md` |
| Onboarding deliverable: first-value per persona, welcome sequence, in-app checklist + empty-state spec | `docs/customer-success/onboarding.md` |

## Validation Loop

Before moving to Phase 2:
- Every BRD persona has a first-value definition expressed as a measurable in-product event
- The TTV target is a concrete number, grounded against a WebSearch'd benchmark (source + date recorded)
- Activation milestones are ordered, each a measurable event with a target rate and a nudge
- In-app guidance (checklist, empty states, tour, seed data) is specified as a spec, not built, and each item maps to a milestone
- The welcome sequence links to existing `docs/` content rather than duplicating it
- Friction log entries each cite evidence (analytics drop-off or a product observation), not assertion

## Quality Bar

- Activation means first VALUE, never "signed up" — and it is measurable.
- The TTV target is calibrated against a researched benchmark, not asserted.
- Every milestone, checklist item, and lifecycle message traces to a persona goal and an activation event.
- Onboarding references the single-source docs; product/instrumentation gaps are raised to product-manager / solution-architect, never invented here.
