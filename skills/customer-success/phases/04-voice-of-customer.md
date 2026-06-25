# Phase 4: Voice of Customer

## Objective

Turn raw customer input into prioritized, evidenced signal — and close the loop. Define the feedback-capture taxonomy, synthesize feedback into themes with evidence, route the prioritized requests to the **product-manager** (who decides scope — you do not), and produce the customer-facing changelog / release-communication template that tells customers what shipped. This phase is the hand-off that makes the whole success operation compound: support volume, churn signals, NPS verbatims, and feature asks all flow up as structured product signal.

## Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| Support data | `docs/customer-success/support-runbook.md`, `drydock/customer-success/support/` | Ticket categories + volume — the largest feedback source |
| NPS/CSAT verbatims | `docs/customer-success/retention-playbook.md` (program) | Detractor reasons, satisfaction drivers |
| Churn signals | `drydock/customer-success/retention/health-score.md` | Why at-risk accounts disengage |
| BRD | `drydock/product-manager/BRD/` | Personas + scope to attribute requests against |
| Release notes / changelog | `docs/` (technical-writer changelog automation) | Source for the customer-facing changelog (translate, do not re-author) |

## Workflow

### Step 1: Define the Feedback Capture Taxonomy

Define one consistent taxonomy so every piece of feedback — from any channel — is captured the same way and can be aggregated. Channels feeding in: support tickets, NPS/CSAT verbatims, churn-interview notes, in-app feedback, sales-lost reasons.

| Field | Values | Why |
|-------|--------|-----|
| Type | bug \| feature-request \| usability \| docs-gap \| pricing \| praise | Routes to the right owner |
| Theme | (emergent — clustered in Step 2) | Aggregation key |
| Persona | from BRD | Whose pain (weights priority) |
| Segment | self-serve \| SMB \| enterprise | Revenue weighting |
| Severity / frequency | how blocking, how often | Priority inputs |
| Source channel | ticket \| NPS \| churn \| in-app \| sales | Traceability |
| Evidence | ticket ids / quote / count | Grounds the request |

Route each Type to its owner up front: **docs-gap → technical-writer** (you file the request, you do not write the doc), **bug → software-engineer via support tier ladder**, **feature-request / usability / pricing → product-manager** (synthesized below). Praise → advocacy/marketing.

### Step 2: Synthesize Feedback Into Themes

Cluster the captured feedback into themes (do not forward 200 raw tickets — synthesize). Each theme aggregates its underlying items and carries the evidence that makes it actionable.

| Theme | Type | Volume (count) | Segments affected | Revenue-at-risk / -upside | Representative quotes | Linked items |
|-------|------|----------------|-------------------|---------------------------|-----------------------|--------------|
| e.g. "Bulk export missing" | feature-request | 47 tickets + 6 NPS | SMB, enterprise | 3 at-risk renewals | "...can't get my data out..." | T-102, T-188 |
| ... | ... | ... | ... | ... | ... | ... |

Quantify everything: a theme without volume, segment, and revenue context is an anecdote, not a signal. Tie themes back to churn (Phase 3) and CSAT detractors where they overlap — a theme that also drives churn is higher signal.

### Step 3: Prioritize and File PM Requests (the loop)

This is the hand-off. Rank themes by a transparent priority model (e.g. volume × segment-revenue-weight × severity, with churn-linkage as a multiplier), then file the top themes as **structured requests to the product-manager**. You SURFACE and SYNTHESIZE; the **product-manager decides scope** — you never write a BRD, set acceptance criteria, or commit a roadmap date.

Each filed request contains: the theme, the evidence (volume/segment/revenue/quotes), the personas affected, the churn/retention linkage, and a recommended priority — explicitly framed as a recommendation, not a decision.

```
## PM Request: <theme>
- Type: feature-request | usability | pricing
- Evidence: <N> tickets, <M> NPS mentions, <K> at-risk accounts ($<value> ARR)
- Personas affected: <from BRD>
- Churn/retention linkage: <e.g. cited in 3 churn interviews>
- Recommended priority: <High/Med/Low — RECOMMENDATION; PM decides scope>
- Decision: <left for product-manager>
```

Write these to `pm-requests.md`. The loop's success metric is throughput, not authorship: requests are filed with evidence; the PM's verdict (accepted/deferred/declined) is recorded back as the loop's close. If a request is later shipped, it feeds Step 5 (tell the customers who asked).

### Step 4: Route Non-PM Feedback

Not all feedback goes to the PM — route by Type so nothing dead-ends:
- **docs-gap** → file a technical-writer doc request (cite the help-center node that's missing). You do not write the doc.
- **bug** → route through the support tier ladder to software-engineer / sre (incidents) per `conflict-resolution.md`.
- **praise / advocacy** → flag promoters for case studies / references (hand to growth-marketer).

### Step 5: Customer Changelog / Release Comms

Translate engineering release notes into customer-facing communication. The changelog is GENERATED upstream by technical-writer's changelog automation — you do not re-author it; you translate "what changed" into "what this means for you" for customers, and you **close the loop** by notifying customers whose feedback drove a shipped change.

Produce:
- **Customer changelog template** — per release: the customer-benefit framing (not commit messages), grouped by New / Improved / Fixed, linked to the relevant help-center article.
- **Release-comms template** — the in-app + email announcement for material releases: headline benefit, who it helps, link to docs, and a "you asked for this" callout tying it back to the originating VoC theme/requesters.
- **Loop-closure rule** — when a PM request (Step 3) ships, notify the customers/segments who raised it. Closing the loop visibly is the single biggest driver of repeat, high-quality feedback.

Keep customer comms benefit-led and link to the single-source docs; do not restate the technical changelog.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Feedback taxonomy + synthesized themes (with evidence) | `drydock/customer-success/voc/feedback-taxonomy.md` |
| Prioritized PM requests (recommendations; PM decides scope) | `drydock/customer-success/voc/pm-requests.md` |
| Customer changelog + release-comms templates + loop-closure rule | `docs/customer-success/release-comms.md` |

## Validation Loop

Before completing the suite:
- The taxonomy captures every channel consistently and routes each Type to its owner
- Themes are synthesized (not raw forwarded) and each carries volume + segment + revenue-at-risk + representative quotes
- Top themes are filed as structured PM requests framed as RECOMMENDATIONS — no BRD authored, no acceptance criteria set, no roadmap dates committed
- Non-PM feedback is routed (docs-gap → technical-writer, bug → software-engineer/sre, praise → growth-marketer); nothing dead-ends
- The customer changelog translates (not re-authors) the upstream automated changelog and links to single-source docs
- The loop-closure rule notifies the customers who raised any shipped request

## Quality Bar

- Every prioritized request carries quantified evidence (volume, segment, revenue) — anecdotes are not signal.
- The loop ends in a product-manager DECISION, never a scope change authored here; you recommend, PM decides.
- Customer comms are benefit-led, link to the single-source docs, and visibly close the loop with the customers who asked.
- Feedback is synthesized into a handful of evidenced themes, not dumped as raw tickets — the synthesis is the value you add.
