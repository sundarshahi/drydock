# Phase 1: Positioning

## Objective

Decide who this product is for and why they should pick it over the alternatives. Produce the ICP and segments, the value proposition and messaging hierarchy, a category frame, an evidenced differentiation analysis against real competitors, a single positioning statement, and a message-to-persona map. Everything downstream (launch, copy, funnels, metrics) keys off this phase — so it is grounded in the BRD, in what actually shipped, and in live competitor research, never in invention. Write working notes to `drydock/growth-marketer/positioning/` and `drydock/growth-marketer/research/`; the polished deliverable is `docs/marketing/positioning.md`.

## Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| BRD | `drydock/product-manager/BRD/` | Problem statement, ICP signals, user personas, success metrics, compliance/segment scope, out-of-scope |
| Shipped product | `frontend/`, `services/`, `README.md`, `CHANGELOG.md` | The REAL feature set and flows you are allowed to claim — no fabricated capabilities |
| Codebase context | `drydock/.orchestrator/codebase-context.md` | Stack, greenfield/brownfield, existing brand/marketing assets |
| Live web | WebSearch / WebFetch | Competitors, category language, alternatives, review-site sentiment — always live, cite URL + date |

If the BRD is missing, this is a **Critical** gap — stop and request it; you cannot position a product whose problem and ICP are undefined. If the shipped product can't be read, degrade: position only on BRD-promised value and tag every capability claim `[inferred]` pending verification.

## Steps

1. **Extract ICP signals from the BRD (don't reinvent personas).** Pull the problem, the personas, the success metrics, and the segment/compliance scope the product-manager already resolved. The product-manager owns the BRD; you CONSUME it (`conflict-resolution.md`). Record each ICP attribute with its BRD source (`BRD/brd.md:NN`). **Deliverable:** `drydock/growth-marketer/positioning/icp.md` — firmographic/demographic + behavioral + psychographic attributes, each cited.

2. **Define 2-4 segments and rank them.** Split the ICP into a small set of addressable segments (e.g. by role, company size, use case, or trigger). For each: the job-to-be-done, the trigger that makes them buy now, the current alternative they use, and the pain with it. Rank by reachability × pain × willingness-to-pay and pick the **beachhead** segment. **Deliverable:** a segment table with a marked beachhead.

3. **Research the competitive set LIVE (WebSearch — never recall).** Identify the real alternatives: direct competitors, adjacent tools, and the status-quo "do nothing / spreadsheet" option. For each direct competitor research the actual positioning, headline claim, target segment, and 2-3 capabilities — from their own site + a review source. Follow `freshness-protocol.md` (channel/market facts are volatile) and `grounding-protocol.md` (every claim cites a URL + retrieval date; tag `[verified]`/`[unverified]`). **Deliverable:** `drydock/growth-marketer/research/competitors.md` — a cited competitor matrix (≥3 competitors).

4. **Build the differentiation analysis.** Against the researched set, find the axes where this product is genuinely different AND the beachhead segment cares. Separate true differentiators (we have it, they don't, segment values it) from table stakes (everyone has it) from gaps (they have it, we don't — be honest; this feeds the launch + roadmap conversation). Every "we have X" traces to shipped code/README. **Deliverable:** a differentiation table (differentiator / table-stake / gap, each evidenced).

5. **Frame the category.** Decide whether you enter an existing category (and win on a wedge) or frame a new sub-category. State the frame in one line plus the "from → to" shift it creates for the buyer. Ground category language in how the market actually talks (research, step 3), not invented jargon.

6. **Write the value proposition + messaging hierarchy.** A three-level hierarchy: (1) the single **core promise** (one sentence — the dominant benefit for the beachhead), (2) **3-5 pillars** (benefit-led, each backed by a shipped capability as proof), (3) **proof points** per pillar (a real feature, metric, integration, or claim — each grounded). Benefits lead, features prove. **Deliverable:** `docs/marketing/positioning.md` messaging-hierarchy section.

7. **Write the positioning statement.** Use a known frame (e.g. *For [beachhead segment] who [trigger/need], [product] is the [category] that [core differentiated benefit], unlike [primary alternative], because [evidenced reason to believe].*). One paragraph, every bracket filled from steps 1-6, the differentiator and reason-to-believe cited.

8. **Map message to persona.** For each segment/persona: their primary pain, the pillar that resonates most, the headline message in their language, the objection to preempt, and the proof point that lands. This is the table the launch copy, landing page, and sales collateral all read from. **Deliverable:** a message-to-persona map in `docs/marketing/positioning.md`.

9. **Set the handoff note.** State explicitly that `docs/marketing/positioning.md` is the single source of messaging truth that **sales-strategist** consumes for collateral and that **frontend-engineer/technical-writer** consume for copy/SEO — and that pricing/packaging/sales-process are out of your scope (sales-strategist owns them).

## Output Deliverables

| Artifact | Path |
|----------|------|
| ICP definition (cited) | `drydock/growth-marketer/positioning/icp.md` |
| Segment table + beachhead | `drydock/growth-marketer/positioning/segments.md` |
| Competitor matrix (cited, live) | `drydock/growth-marketer/research/competitors.md` |
| Positioning & messaging (deliverable) | `docs/marketing/positioning.md` |

## Validation Loop

Before moving on:
- ICP and segments each trace to a BRD line or researched evidence — no wholesale-invented personas.
- ≥3 direct competitors researched THIS session, each with a cited URL + retrieval date; claims tagged `[verified]`/`[unverified]`.
- Every "we have / we do X" in the messaging traces to shipped code/README/changelog — zero fabricated capabilities.
- The positioning statement fills every bracket and names a real primary alternative.
- The message-to-persona map covers every segment and preempts an objection per persona.
- In Checkpoint/Manual, the user has co-signed the beachhead + positioning statement before Phase 2.

## Quality Bar

Positioning is a decision, not an adjective. "We're the modern, easy way to do X" is not positioning — "For revenue-ops leads at 50-500-person B2B SaaS who lose hours reconciling usage data, [product] is the usage-metering layer that reconciles in real time, unlike spreadsheets + Stripe metering, because it reads the same event stream billing does (`services/metering`)" is. Every differentiator is evidenced against a researched competitor and a shipped capability; every market claim carries a cited, dated source; and the messaging hierarchy leads with benefits and proves with real features. End the deliverable with a calibration summary (counts by `[verified]`/`[inferred]`/`[unverified]`).
