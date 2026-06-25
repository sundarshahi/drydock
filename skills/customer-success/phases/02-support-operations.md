# Phase 2: Support Operations

## Objective

Stand up a support operation that resolves issues fast and deflects the resolvable ones to self-serve. Build the help-center information architecture **on top of the existing technical-writer docs** (source, do not rewrite), define the ticket workflow and tiers, set concrete SLAs with escalation paths, write canned responses, and choose a channel strategy with a self-serve deflection plan. This phase organizes and operationalizes — it never forks the documentation.

## Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| Documentation (SOURCE) | `docs/` (getting-started, guides, api-reference, error-codes, FAQs) | The content the help center is built FROM |
| Onboarding journey | `drydock/customer-success/onboarding/journey-map.md` | Friction points → predictable ticket categories |
| Product | `services/`, `frontend/` | Error surfaces, known failure modes → canned responses & runbooks |
| BRD personas + segment | `drydock/product-manager/BRD/` | Customer segments → tiering, B2B vs B2C channel needs |
| Existing support content | project / existing macros | Reuse, note gaps |

If `docs/` is missing, WARN and proceed: build the help-center IA with `<!-- TODO: needs technical-writer doc -->` placeholders for each node — do NOT write the doc prose yourself (technical-writer is the documentation authority per `conflict-resolution.md`).

## Workflow

### Step 1: Build the Help-Center IA From the Docs

The help center is an information architecture OVER the existing `docs/` — a customer-facing organization and index, not new content. Map each help-center node to its source doc path.

| Help-center section | Source `docs/` path | Audience | Notes |
|---------------------|---------------------|----------|-------|
| Getting Started | `docs/getting-started/quickstart.md`, `installation.md` | New user | Mirror the onboarding first-value path |
| How-to Guides | `docs/guides/` | Active user | Task-oriented |
| API & Integrations | `docs/api-reference/`, `docs/integrations/` | Developer | Link, do not restate |
| Troubleshooting & Errors | `docs/api-reference/error-codes.md` | All | Each error → its remediation (already in the generated table) |
| FAQ | synthesized from ticket categories (Step 3) | All | Highest-volume questions first |

For any help-center node with no source doc, record a **gap request** (what's missing, which persona needs it) and route it to technical-writer — do not author the prose. Keep the mapping in `help-center-map.md` so the help center stays a thin index over the single source.

### Step 2: Define the Ticket Workflow

Define the lifecycle a ticket moves through and the states it can occupy:

```
New -> Triaged (categorized + prioritized) -> In Progress -> Pending Customer
  -> Resolved -> Closed   (Reopened path from Resolved on customer reply)
                -> Escalated (to next tier / to engineering) when criteria met
```

For each state, record: who owns it, the entry criteria, and the exit criteria. Define the **priority rubric** (P1/P2/P3/P4) by customer impact (outage/data-loss vs. degraded vs. question), independent of tier.

| Priority | Definition | Example |
|----------|------------|---------|
| P1 — Critical | Service down / data loss / security | Cannot log in (all users), data exposure |
| P2 — High | Major feature broken, no workaround | Core workflow failing for one account |
| P3 — Normal | Minor issue, workaround exists | UI glitch, slow page |
| P4 — Low | Question / how-to / feature ask | "How do I export?" |

### Step 3: Define Support Tiers

Define the tier ladder and what each tier owns. Tiers are about ESCALATION DEPTH, not priority.

| Tier | Owns | Handles | Escalates when |
|------|------|---------|----------------|
| Tier 0 — Self-serve | Help center, FAQ, in-app help | Deflected before a ticket exists | User can't find the answer |
| Tier 1 — Frontline | First response, common issues, macros | P3/P4, known issues | Needs product/account internals |
| Tier 2 — Product specialist | Deep product issues, config, account data | Escalated P2/P3, complex how-to | Reproducible bug / needs code |
| Tier 3 — Engineering | Bugs, incidents | Escalated P1/P2 bugs | (Hand to sre/software-engineer per `conflict-resolution.md`) |

Note: Tier 3 hands incidents to **sre** (incident management / runbooks) and bugs to **software-engineer** — you route, they fix. You do not own the incident process; you own the customer-facing support process that feeds into it.

### Step 4: Set SLAs + Escalation Paths (concrete)

Define first-response and resolution targets per priority per tier — concrete numbers, not "respond quickly". Calibrate the targets against a researched industry benchmark (WebSearch current support-SLA conventions for the segment; cite source + date — never from memory).

| Priority | First-response target | Resolution target | Escalation on breach |
|----------|----------------------|-------------------|----------------------|
| P1 | e.g. 15 min (24/7) | e.g. 4 h | Auto-page on-call + Tier 3 + notify account owner |
| P2 | e.g. 1 h (business h) | e.g. 1 business day | Escalate Tier 1 → Tier 2 at 50% of target |
| P3 | e.g. 8 business h | e.g. 3 business days | Escalate at target |
| P4 | e.g. 1 business day | best-effort / deflect | Convert to FAQ if recurring |

For each SLA, define the **escalation path that fires on breach** (who gets paged/notified, at what threshold) and any segment-based differentiation (e.g. enterprise tier gets tighter targets). Tie P1 escalation to the sre on-call path rather than redefining incident response.

### Step 5: Write Canned Responses (Macros)

Write reusable macros keyed to the highest-volume ticket categories (derived from the onboarding friction log + product error surfaces). Each macro: a trigger/category, the response template (with placeholders), and the linked help-center article. Macros must point to the single-source docs, not restate them.

| Category | Trigger | Macro (template) | Links to |
|----------|---------|------------------|----------|
| Login / auth | "can't log in" | Reset steps + SSO note | help-center → getting-started |
| Billing | "charged twice" | Acknowledge + escalation note | billing runbook |
| API error | known error code | Remediation from `error-codes.md` | the generated error table |

### Step 6: Channel Strategy + Self-Serve Deflection

Choose the support channels appropriate to the segment (from BRD), and design the deflection plan that pushes resolvable volume to self-serve BEFORE a ticket is created.

- **Channels** — pick from in-app/email/chat/community/phone based on segment (B2C self-serve leans in-app + help center; enterprise adds dedicated channels). State why each is in/out.
- **Deflection** — in-app help search, contextual help-center links at error surfaces, suggested articles before submit, and a community/FAQ for recurring questions. Set a **deflection-rate target**, grounded against a researched benchmark (WebSearch; cite). Wire the recurring-question feedback so high-volume categories become FAQ/doc requests (technical-writer) rather than perpetual tickets.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Help-center IA mapping each node → `docs/` source + gap requests | `drydock/customer-success/support/help-center-map.md` |
| Support runbook: workflow, tiers, SLA matrix, escalation paths, channel strategy, deflection plan | `docs/customer-success/support-runbook.md` |
| Canned responses / macros | `drydock/customer-success/support/canned-responses.md` |

## Validation Loop

Before moving to Phase 3:
- Every help-center node maps to a `docs/` source path; nodes with no source are filed as technical-writer gap requests (no prose authored here)
- The ticket workflow has owners + entry/exit criteria per state, and a priority rubric independent of tier
- Tiers define ownership + escalation criteria; Tier 3 routes to sre (incidents) / software-engineer (bugs)
- The SLA matrix is concrete (first-response + resolution per priority) with an escalation path firing on breach; targets grounded against a WebSearch'd benchmark
- Macros link to the single-source docs rather than restating them
- The channel strategy is justified per segment and the deflection plan has a grounded target

## Quality Bar

- The help center is a thin, mapped index over the single-source `docs/` — never a fork or rewrite.
- SLAs are concrete numbers per priority with an escalation that actually fires on breach, calibrated to a researched benchmark.
- Tiering separates escalation depth from priority, and routes bugs/incidents to their owning agents.
- The deflection plan converts recurring tickets into FAQ/doc requests, lowering future volume — with a grounded deflection target, not a guess.
