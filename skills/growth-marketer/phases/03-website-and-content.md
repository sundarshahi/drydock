# Phase 3: Website & Content

## Objective

Write the marketing-site COPY and the SEO content STRATEGY, and produce the email/nurture copy. You author what the page and articles SAY and what each SEO page must rank for — you do not write the production page or the long-form article; you hand briefs to **frontend-engineer** (builds the landing page) and **technical-writer** (writes long-form/SEO docs). Deliver landing-page copy (hero, value props, social proof, CTA), an SEO content strategy with keyword/topic briefs, and lifecycle/nurture email copy. Write working notes under `drydock/growth-marketer/`; deliverables go to `docs/marketing/website/`, `docs/marketing/content/`, and `docs/marketing/lifecycle/`.

## Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| Positioning | `docs/marketing/positioning.md` | Core promise, pillars, proof points, message-to-persona map — the copy reuses these verbatim where possible |
| Shipped product | `frontend/`, `services/`, `README.md` | Real screenshots/flows/feature names to claim; never invent UI or capability |
| Launch plan | `docs/marketing/launch-plan.md` | Content calendar items that become SEO briefs; waitlist capture the page must support |
| Live web | WebSearch | Keyword demand, search intent, SERP competitors, current SEO guidance — verify live |

## Steps

1. **Write the landing-page copy block.** Produce `docs/marketing/website/landing-page.md` as a structured copy doc the frontend engineer builds from — copy only, no code:
   - **Hero** — headline (core promise in the buyer's words), subhead (the differentiated benefit + reason to believe), and ONE dominant primary CTA. Optional secondary CTA only if it serves a different intent (e.g. "See it work" vs "Start free").
   - **Value-prop sections** — one section per pillar (from Phase 1), benefit-led headline + supporting line + the proof point (a real shipped feature). Map each section to the segment it serves.
   - **Social proof** — the FRAME and placeholders for logos / testimonials / metrics. Do NOT fabricate testimonials, customer names, or metrics — use `<!-- TODO: real testimonial from <source> -->` placeholders the team fills with genuine proof.
   - **Objection handling / FAQ** — preempt the top objections from the message-to-persona map.
   - **Closing CTA** — restate the primary CTA.
   - **Conversion event note** — name the primary conversion action on the page (signup / waitlist / demo) so Phase 4 instruments it and frontend wires it.

2. **Annotate the build handoff.** At the top of the landing-page copy, state: this is COPY for frontend-engineer to implement; the analytics events the page must emit are defined in Phase 4 and follow `observability-contract.md`; performance/accessibility are owned by frontend-engineer. You own the words and the CTA hierarchy, not the markup.

3. **Build the SEO content strategy (live keyword/intent research).** Research demand and intent with WebSearch — keyword themes, search intent (informational / commercial / transactional), and who currently ranks. SEO guidance is volatile (`freshness-protocol.md`); cite sources + dates. Group findings into topic clusters: one pillar page per cluster + supporting articles. Map each cluster to a Phase 1 segment + buying stage. **Deliverable:** `docs/marketing/content/seo-strategy.md` — the cluster map with intent and priority.

4. **Write one content brief per target page (hand to technical-writer/frontend).** Each brief in `docs/marketing/content/briefs/` is the spec the implementing skill writes the article from — you do NOT write the article body:

   | Brief field | Content |
   |-------------|---------|
   | Working title | Draft H1 |
   | Primary keyword / topic | The term + its intent (informational/commercial/transactional) |
   | Search intent + audience | Which segment + buying stage |
   | Outline | H2/H3 structure the writer fills |
   | Internal links | Which landing/pillar pages to link |
   | Primary CTA | The conversion action for this page |
   | Owner | technical-writer (long-form) or frontend-engineer (page) |
   | Source evidence | The cited demand/intent data backing this brief |

   State clearly these briefs are handed off — technical-writer owns the prose, you own the strategy + brief.

5. **Write the lifecycle / nurture email copy.** Produce `docs/marketing/lifecycle/` copy for the core sequences tied to the funnel (Phase 4): waitlist nurture (signup → launch), onboarding/activation (signup → first value), and a re-engagement nudge. Each email: trigger event, goal, subject line(s), body copy, single CTA, and the funnel stage it serves. Trigger events reference the Phase 4 event taxonomy — not ad-hoc names.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Landing-page copy (hero, value props, social proof, CTA) | `docs/marketing/website/landing-page.md` |
| SEO content strategy (cluster map) | `docs/marketing/content/seo-strategy.md` |
| Per-page SEO content briefs | `docs/marketing/content/briefs/<slug>.md` |
| Lifecycle / nurture email copy | `docs/marketing/lifecycle/*.md` |

## Validation Loop

Before moving on:
- The landing page has exactly ONE dominant primary CTA; each value-prop section maps to a pillar + segment.
- Every capability/claim in copy traces to a shipped feature; no fabricated testimonials, logos, or metrics (placeholders only).
- The copy doc is annotated as a frontend-engineer build handoff; the page's conversion event is named for Phase 4.
- SEO strategy clusters each carry an intent, a segment, and a priority, backed by cited demand data.
- Every content brief has a primary keyword + intent, an outline, a CTA, and a named owner (technical-writer/frontend) — you are not writing the article body.
- Lifecycle emails each name a trigger event from the Phase 4 taxonomy, a single CTA, and a funnel stage.

## Quality Bar

The page reads like the positioning sounds: the hero is the core promise in the buyer's language, every section earns its place against a pillar, and there is one obvious thing to do. SEO is a clustered strategy with intent-mapped briefs an implementer can write from — not "blog more". Nothing is fabricated: real features, real proof or honest placeholders, live-cited keyword data. The deliverables are clean handoffs — frontend-engineer can build the page and technical-writer can write the articles without guessing intent. Tag claims and close with a calibration summary.
