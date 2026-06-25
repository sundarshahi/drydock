# Phase 2: Launch Plan

## Objective

Turn the positioning into a sequenced, dated go-to-market launch. Produce the channel strategy, a T-minus → T-plus launch timeline (waitlist, owned channels, Product Hunt / Hacker News / communities, PR), a content calendar, an asset checklist with owners, and a pre-launch waitlist mechanic. The plan is concrete enough to execute — channel mechanics are researched live, not recalled. Write working notes to `drydock/growth-marketer/launch/`; the deliverable is `docs/marketing/launch-plan.md`.

## Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| Positioning | `docs/marketing/positioning.md` | Beachhead segment, core promise, pillars, message-to-persona map (the copy every asset reuses) |
| Segment table | `drydock/growth-marketer/positioning/segments.md` | Where each segment actually congregates (channel fit) |
| BRD | `drydock/product-manager/BRD/` | Launch constraints, compliance/segment scope, any GA/beta gating |
| Live web | WebSearch / WebFetch | Current channel mechanics + rules (Product Hunt launch rules, HN guidelines, subreddit/community policies, PR timing) — volatile, verify live |

## Steps

1. **Select channels by segment fit.** For each priority segment from Phase 1, identify the 2-3 channels where they actually are (communities, search, marketplaces, social, PR, partnerships). Classify each channel as **owned** (site, list, docs), **earned** (PR, communities, Product Hunt/HN), or **paid** (ads — only if justified). Score by reach × fit × cost × effort and pick the launch channel set. Do NOT spray every channel. **Deliverable:** a channel-strategy table in `drydock/growth-marketer/launch/channels.md`.

2. **Verify channel mechanics LIVE.** Before you sequence a channel, WebSearch its current rules (e.g. Product Hunt's launch-day/hunter/timing rules, Hacker News "Show HN" guidelines, each community's self-promotion policy, embargo norms for PR). Channel rules are Tier-1 volatile (`freshness-protocol.md`) — cite the URL + retrieval date for each, tag `[verified]`. Never state a launch rule from memory.

3. **Design the pre-launch waitlist.** Define the waitlist mechanic: the landing capture (hands to Phase 3 copy + Phase 4 instrumentation), the incentive (early access / launch-day perk / referral position), the referral loop if any, and the nurture cadence from signup to launch day. State the single conversion event the waitlist optimizes for. **Deliverable:** a waitlist plan with the capture → nurture → activation flow.

4. **Sequence the launch on a T-minus timeline.** Build a dated sequence with the waitlist warming up first, owned channels seeding, then the spike day(s), then sustain. Example skeleton (adapt to the product):

   | When | Action | Channel | Owner | Asset needed |
   |------|--------|---------|-------|--------------|
   | T-21d | Open waitlist + teaser | Owned (site, list) | growth-marketer | Waitlist landing copy (Phase 3) |
   | T-14d | Seed communities, line up hunter/commenters | Earned (communities) | growth-marketer | Community posts, demo GIF |
   | T-7d | Brief PR / newsletters under embargo | Earned (PR) | growth-marketer | Press kit, embargo note |
   | T-1d | Final assets staged, waitlist "launching tomorrow" email | Owned | growth-marketer | Launch email |
   | T-0 | Product Hunt + Show HN + launch posts go live; engage all day | Earned | growth-marketer | PH listing, Show HN post, social thread |
   | T+1→T+7d | Recap, thank-you, sustain content, capture testimonials | Owned/Earned | growth-marketer | Recap post, testimonials |

   Each row names the channel, owner, and required asset. The timeline is the spine of the deliverable.

5. **Build the content calendar.** Map content to the timeline: pre-launch teasers, the launch-day asset set, and the sustain cadence (e.g. a weekly cadence for N weeks). Each item: format, channel, message pillar it serves (from Phase 1), the CTA, and the publish date. Cross-reference Phase 3 — long-form/SEO pieces in this calendar become the topic briefs handed to technical-writer/frontend-engineer.

6. **Compile the asset checklist with owners.** Every asset the timeline + calendar require, in one checklist, each with: format, owner (you author copy; frontend-engineer/technical-writer/design implement), source pillar, status, and due date relative to T-0. Mark which assets are blocking for T-0.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Channel strategy (scored) | `drydock/growth-marketer/launch/channels.md` |
| Launch plan: sequence + timeline + calendar + assets + waitlist (deliverable) | `docs/marketing/launch-plan.md` |
| Cited channel-mechanics research | `drydock/growth-marketer/research/channels.md` |

## Validation Loop

Before moving on:
- Every channel in the plan maps to a priority segment (no spray-and-pray).
- Every channel rule cited (Product Hunt/HN/community/PR) is from a live WebSearch with URL + retrieval date — none recalled.
- The timeline is dated on a T-minus → T-plus axis with a channel, owner, and required asset per row.
- The waitlist has a defined capture event (handed to Phase 4 instrumentation), incentive, and nurture cadence.
- The asset checklist names an owner and due date per asset and marks the T-0 blockers.
- Assets you author are copy/briefs; build/implementation is owned by frontend-engineer/technical-writer/design — the checklist reflects that split.

## Quality Bar

A launch plan is a runbook, not a wish. "We'll launch on Product Hunt and post on socials" fails; "T-0 06:01 PT PH listing live (hunter X confirmed, current PH rules verified `producthunt.com/...` 2026-06-25), Show HN at T-0 09:00 PT per HN guidelines, waitlist 'we're live' email to N subscribers, founder engaging every comment until T+1" passes. The sequence compounds (waitlist → owned → earned spike → sustain), every channel mechanic is live-verified and cited, and every required asset has an owner and a date. Tag claims `[verified]`/`[unverified]` and close with a calibration summary.
