---
sidebar_position: 6
title: "Go-to-market"
description: "Growth Marketer, Sales Strategist, and Customer Success: the agents that launch the product."
---

# Go-to-market

The LAUNCH phase takes a production-ready product to market. Three agents run here, and they form a strict chain: the **Growth Marketer** writes the narrative, the **Sales Strategist** turns that narrative plus your hardened security and compliance evidence into a way to close revenue, and **Customer Success** keeps the customers you win and routes what they say back into the product.

LAUNCH runs **after SHIP and only after Gate 3 (production-readiness) passes** — Drydock does not launch software that isn't production-ready. All three agents are dispatched together as one parallel wave (T14, T15, T16).

:::info Where these agents run
All three are isolated subagents (`agents/*.md`), part of Drydock's team of 19 specialized agents coordinated by one orchestrator. For the full roster and how subagents differ from the in-context planning skills, see [/docs/concepts/how-it-works](/docs/concepts/how-it-works).
:::

## At a glance

| Agent | Phase | Owns (sole authority) | Consumes | Primary deliverables |
|-------|-------|-----------------------|----------|----------------------|
| Growth Marketer | LAUNCH | Positioning, messaging, launch plan, marketing-site copy, funnel/analytics, growth experiments | BRD, the shipped product | `docs/marketing/` |
| Sales Strategist | LAUNCH | Pricing & packaging, sales collateral, sales process, the buyer-facing trust pack, proposal templates | Growth-marketer positioning, security-engineer + compliance-officer evidence | `docs/sales/` |
| Customer Success | LAUNCH → SUSTAIN | Onboarding & activation, support operations, retention & churn, voice-of-customer loop | BRD personas, technical-writer `docs/`, growth analytics | `docs/customer-success/` |

## Growth Marketer

The Growth Marketer takes a product engineering has SHIPPED and brings it to market. It defines who the product is for and why they should care, plans and sequences the launch, writes the marketing-site and lifecycle copy, instruments the acquisition → activation → retention funnel, and stands up a growth-experiment program against a single north-star metric.

**What it produces** (deliverables under `docs/marketing/`):

| Artifact | Path |
|----------|------|
| Positioning & messaging | `docs/marketing/positioning.md` |
| Launch plan (sequence, calendar, assets, waitlist) | `docs/marketing/launch-plan.md` |
| Landing-page copy + SEO content briefs | `docs/marketing/website/`, `docs/marketing/content/` |
| Lifecycle / email copy | `docs/marketing/lifecycle/` |
| Funnel + analytics + experiment plan | `docs/marketing/analytics-plan.md` |
| Growth-metrics scorecard | `docs/marketing/growth-metrics.md` |

It runs five phases — Positioning, Launch Plan, Website & Content, Funnels & Analytics, Growth Metrics. Positioning runs first because everything downstream keys off it; the Launch Plan and Website & Content phases then run in parallel.

**Boundaries.** The Growth Marketer **owns positioning** — the value proposition, messaging hierarchy, and category framing are its sole authority. It hands the landing-page copy and SEO briefs to the frontend-engineer and technical-writer to implement, and hands its positioning to the Sales Strategist. It does **not** author pricing, packaging, or the sales process (that is the Sales Strategist), and it does **not** author requirements (the product-manager owns the BRD).

:::warning Every claim is grounded
The Growth Marketer never recalls a competitor feature, a Product Hunt rule, or a "typical conversion rate" from memory. Every market, competitor, channel, and benchmark claim is verified with a live WebSearch (cited URL + retrieval date), and every product capability it claims traces to something that actually shipped.
:::

## Sales Strategist

The Sales Strategist turns the shipped product and its go-to-market narrative into a repeatable, sellable motion. It owns the buyer-facing sell-side: pricing & packaging, sales collateral, the sales process and qualification framework, objection-handling enablement, and proposal/quote/SOW templates.

**What it produces** (deliverables under `docs/sales/`):

| Artifact | Path |
|----------|------|
| Pricing & packaging | `docs/sales/pricing.md` |
| Sales collateral (one-pager, deck outline, demo script, ROI calculator, case-study) | `docs/sales/collateral/` |
| Sales process (ICP, qualification, pipeline, CRM, outbound, discovery) | `docs/sales/process/` |
| Enablement (objection handling, battlecards, FAQ) | `docs/sales/enablement/` |
| Buyer-facing trust pack | `docs/sales/trust/` |
| Proposal / quote / SOW / order-form / MSA templates | `docs/sales/proposals/` |

It runs five sequential phases — Pricing & Packaging, Sales Collateral, Sales Process, Enablement & Trust, Proposals — after a Phase 0 reconnaissance pass that reads the prior pipeline outputs.

**Boundaries.** The Sales Strategist **consumes the positioning** the Growth Marketer produced and restates it verbatim as the single source of truth for every deck, one-pager, and battlecard. If the sales narrative and the marketing narrative ever disagree, **the marketing narrative wins** and sales flags the gap — it never forks a competing story. It turns the **security-engineer + compliance-officer evidence into a buyer-facing trust pack**: a buyer-readable restatement of the PII inventory, encryption audit, SBOM, pen-test results, framework scoping, and control-evidence map. Every trust-pack claim cites the source evidence artifact (`path:line`); a claim with no evidence pointer is "in progress", never "compliant".

:::note Two hard boundaries
1. **Positioning is the Growth Marketer's.** Sales translates the narrative into deal collateral; it never re-authors it.
2. **Nothing sales generates is binding.** Every legal artifact — MSA, SOW, order form, terms — ships as a template marked `REQUIRES LEGAL REVIEW — not binding as generated` and is logged in a legal-review register. Sales never represents a generated contract as enforceable.
:::

The Sales Strategist also hands billing/subscription requirements to the software-engineer as a spec (it does not implement billing) and hands the closed account off to Customer Success for the post-sale motion.

## Customer Success

Customer Success owns the post-launch relationship. It gets new customers to first value fast (onboarding & activation), runs a support operation that resolves and deflects efficiently (help center, ticket tiers, SLAs), keeps customers (health scores, churn intervention, renewal & expansion, NPS/CSAT), and closes the loop by synthesizing what customers say into prioritized signal for the product-manager.

**What it produces** (deliverables under `docs/customer-success/`):

| Artifact | Path |
|----------|------|
| Welcome/setup sequence + activation checklists | `docs/customer-success/onboarding.md` |
| Support runbook (tiers, SLAs, escalation) | `docs/customer-success/support-runbook.md` |
| Retention playbooks (churn, renewal, expansion, NPS/CSAT, QBR) | `docs/customer-success/retention-playbook.md` |
| Customer changelog / release comms | `docs/customer-success/release-comms.md` |

It runs four sequential phases — Onboarding & Activation, Support Operations, Retention & Churn, Voice of Customer.

:::tip This agent carries into SUSTAIN
Customer Success is the one go-to-market agent that does not stop at LAUNCH. It runs from LAUNCH into [SUSTAIN](/docs/concepts/how-it-works) — live onboarding, support, retention, and the ongoing voice-of-customer loop. Its receipt records the `SUSTAIN` phase for this reason.
:::

**Boundaries.** Customer Success **sources** the help center from the technical-writer's `docs/` — it organizes existing docs into a help-center IA and files gaps as doc requests; it never rewrites or forks the prose, because the technical-writer is the sole documentation authority.

:::note A soft input at LAUNCH
The technical-writer task (T11) runs in SUSTAIN, so `docs/` may be sparse when LAUNCH fires. Customer Success bootstraps the help center from the best-available docs (API specs, READMEs) and refines it once the technical-writer's docs land.
:::

The feedback loop is a **hand-off, not an override**: Customer Success synthesizes customer feedback into themes with evidence (volume, segment, revenue-at-risk) and **routes prioritized requests to the product-manager**, who decides scope. It files a structured request; it never writes a BRD, changes acceptance criteria, or commits a roadmap.

## How the chain fits together

```text
growth-marketer ──positioning──▶ sales-strategist ──closed account──▶ customer-success
       │                              ▲                                      │
       │                   security-engineer +                              │
       │                   compliance-officer ── evidence ──▶ trust pack    │
       │                                                                     ▼
       └──────────── analytics ───────────────────────────────────▶  product-manager
                                                                    (feedback loop)
```

- **Growth owns the narrative.** Positioning and messaging are authored once, here.
- **Sales consumes it** and combines it with hardened evidence into a buyer-facing trust pack; on any conflict, marketing wins.
- **Customer Success keeps the customer** and feeds prioritized feedback back to the product-manager — the only agent that crosses from LAUNCH into SUSTAIN.

For the full pipeline (DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN) and the three approval gates, see [/docs/concepts/how-it-works](/docs/concepts/how-it-works).
