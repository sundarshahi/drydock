# Phase 5: Growth Metrics

## Objective

Tie the whole GTM to one number and a small set of KPIs with real targets. Produce the AARRR + **north-star metric** definition, acquisition/activation/retention/referral/revenue KPIs each with a numeric target and a cited benchmark, a reporting cadence, and an experiment scorecard. This is the dashboard the team runs on after launch — derived from the Phase 4 event taxonomy, so every KPI is computable from instrumented events. Write working notes to `drydock/growth-marketer/analytics/`; the deliverable is `docs/marketing/growth-metrics.md`. The completion receipt is written here as the LAST action of the skill.

## Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| Analytics plan | `docs/marketing/analytics-plan.md` | The event taxonomy + funnel — every KPI must be computable from these events |
| Positioning | `docs/marketing/positioning.md` | Segments — KPIs and targets are reported per segment where they diverge |
| BRD | `drydock/product-manager/BRD/` | The product-manager's success metrics — your north-star must align with, not contradict, them |
| Launch plan | `docs/marketing/launch-plan.md` | Launch-window targets (waitlist size, launch-day signups) for the first reporting period |
| Live web | WebSearch | Category benchmarks (conversion, activation, retention) to set defensible targets — verify live, cite |

## Steps

1. **Pick the north-star metric.** ONE metric that measures delivered customer value and that growth across the funnel rolls up to (e.g. weekly activated accounts, weekly value-events delivered) — never a vanity count (signups, pageviews). It must be computable from a Phase 4 event and must align with the BRD's success metrics (if it conflicts with the product-manager's stated success metric, flag the gap — you don't override the BRD). State the north-star, its exact event-derived formula, and why it proxies value. **Deliverable:** the north-star definition in `docs/marketing/growth-metrics.md`.

2. **Lay out the AARRR frame.** For each stage — **Acquisition, Activation, Retention, Referral, Revenue** — define the 1-2 KPIs that matter and how each is computed from the event taxonomy:

   | Stage | KPI | Event-derived formula | Segment cut |
   |-------|-----|----------------------|-------------|
   | Acquisition | Visit→signup rate; CAC by channel | `signup_completed / visits`, by `utm_source` | per channel |
   | Activation | Activation rate; time-to-activate | `activation_reached / signup_completed`; median Δt | per segment |
   | Retention | WAU/MAU; week-N retention curve | active accounts over rolling window | per segment |
   | Referral | Referral rate / k-factor | invites sent × accept rate | overall |
   | Revenue | Conversion to paid; expansion | paid events / activated (if monetized) | per plan |

   Every formula references real events from Phase 4 — no metric that can't be computed from instrumented data.

3. **Set numeric targets with cited benchmarks.** For each KPI, set a target for the launch window AND a 90-day target. Ground each target in a live-researched category benchmark (`freshness-protocol.md` — conversion/activation/retention benchmarks are volatile; cite URL + date) OR the BRD's stated success metric — never a number pulled from memory. State the baseline (or "no baseline yet — first launch" honestly) so the target is interpretable. Mark stretch vs commit.

4. **Define the reporting cadence.** Specify what's reviewed and when: a daily launch-window pulse (signups, north-star, top channel), a weekly growth review (full AARRR + active experiments), and a monthly trend (retention curves, CAC trend, north-star trajectory). For each cadence: the audience, the surface (dashboard from Phase 4 tooling), and the decision it drives. State who owns the dashboard build (frontend/devops wire the tool; you define the metrics).

5. **Build the experiment scorecard.** A living scorecard for the Phase 4 experiment backlog: per experiment — hypothesis, primary metric + target MDE, status (queued / running / shipped / killed), result (lift + confidence), and the decision taken. Add a roll-up: experiments run, win rate, cumulative lift on the north-star. This is how the program proves it's compounding, not guessing.

6. **Write the completion receipt (LAST action).** Per `receipt-protocol.md`, after every deliverable exists on disk, write `drydock/.orchestrator/receipts/<task>-growth-marketer.json` with:
   - `artifacts` — every file produced across all five phases (each path must exist on disk).
   - `metrics` — concrete numbers: `segments`, `competitors_researched`, `channels`, `launch_assets`, `seo_briefs`, `funnel_events`, `experiments`, `kpis_with_targets`, `north_star_defined` (bool).
   - `effort` — your actual `files_read`, `files_written`, `tool_calls`.
   - `verification` — one line on what you checked (e.g. "every KPI computes from a Phase 4 event; all targets cite a benchmark or the BRD; no fabricated capabilities").
   Then mark the task complete. No receipt = the work didn't happen.

## Output Deliverables

| Artifact | Path |
|----------|------|
| North-star + AARRR KPIs with targets + cadence + scorecard | `docs/marketing/growth-metrics.md` |
| Benchmark research (cited) | `drydock/growth-marketer/research/benchmarks.md` |
| Completion receipt | `drydock/.orchestrator/receipts/<task>-growth-marketer.json` |

## Validation Loop

Before completing:
- Exactly ONE north-star metric, measuring delivered value (not a vanity count), computable from a Phase 4 event, and aligned with the BRD (conflicts flagged, not overridden).
- Every AARRR KPI has an event-derived formula referencing the Phase 4 taxonomy — nothing uncomputable.
- Every target has a number for the launch window AND 90 days, each grounded in a cited benchmark or the BRD success metric — none recalled from memory.
- The reporting cadence names audience, surface, and the decision each review drives.
- The experiment scorecard ties to the Phase 4 backlog and rolls up win rate + cumulative north-star lift.
- The completion receipt exists, every artifact path resolves on disk, and `metrics` carries concrete numbers.

## Quality Bar

The output is a scoreboard the team can run launch on Monday morning. There is one north-star everyone optimizes, each KPI is a real formula over instrumented events (not a number nobody can compute), and every target is defensible — a cited benchmark or the BRD's success metric, with the baseline stated. The cadence drives decisions, not just charts, and the experiment scorecard shows the program compounding. Every benchmark claim is `[verified]` with a cited, dated source; unverifiable targets are flagged, not invented. Close the deliverable with a calibration summary, and the receipt is the proof the whole GTM actually ran.
