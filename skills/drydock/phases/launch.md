# LAUNCH Phase — Dispatcher

The go-to-market phase. Runs **after SHIP and after Gate 3 (production-readiness) passes** — you do not launch software that isn't production-ready. Manages tasks T14 (Growth/Marketing), T15 (Sales), T16 (Customer Success). All three run in parallel (PARALLEL #8).

> **Scope gate (LAUNCH mode only).** When invoked as the standalone **Launch (GTM)** mode (not inside a Full Build), present the GTM plan for confirmation first (target market, channels, pricing direction) via `AskUserQuestion` — GTM choices are strategic and user-owned. Inside a Full Build, LAUNCH proceeds automatically once Gate 3 is green.

## Authority Boundaries — CRITICAL

Enforce strictly (see `drydock/.protocols/conflict-resolution.md`):
- **growth-marketer** owns positioning, messaging, and the launch plan — the narrative and demand generation.
- **sales-strategist** owns pricing & packaging, sales collateral, and sales process — it CONSUMES growth-marketer's positioning, does NOT re-author it, and turns the **security-engineer + compliance-officer evidence** into a buyer-facing trust pack.
- **customer-success** owns onboarding, support ops, and retention — it sources the help center from **technical-writer** docs and routes prioritized feedback to **product-manager** (does not change requirements).
- None of these author product requirements (product-manager) or write product code (software/frontend-engineer).

## Re-Anchor

Before creating LAUNCH tasks, re-read from disk:
- `drydock/product-manager/BRD/brd.md` (what the product is + who it's for)
- `drydock/solution-architect/system-design.md` and the shipped surface (`services/`, `frontend/` listing)
- `drydock/security-engineer/findings/` + `drydock/compliance-officer/` control-evidence map (for the sales trust pack)
- `drydock/technical-writer/` docs **if present** (for the help center) — this is a **soft input**: in the canonical order technical-writer (T11) runs in SUSTAIN, so `docs/` may be empty at LAUNCH. customer-success bootstraps the help center from best-available docs (API specs, READMEs) and refines it once T11 lands.
- `.orchestrator/receipts/` SHIP receipts (T7–T10) — confirm production-ready before launching

## PARALLEL #8: T14 + T15 + T16

All three start together. Read `drydock/.orchestrator/settings.md` for `Worktrees: enabled`; each subagent runs backgrounded in its own worktree per its definition (`agents/growth-marketer.md`, `agents/sales-strategist.md`, `agents/customer-success.md`), merged back after the wave.

```
TaskUpdate(taskId=t14_id, status="in_progress")
TaskUpdate(taskId=t15_id, status="in_progress")
TaskUpdate(taskId=t16_id, status="in_progress")
```

Delegate to their subagents to run CONCURRENTLY (each backgrounded + isolated per its definition):

- **`growth-marketer`** (T14 — Marketing & Growth) — Read the BRD + shipped product. Produce positioning, messaging, the launch plan, landing-page copy + SEO briefs (handed to frontend-engineer/technical-writer), and the funnel/analytics + growth-experiment plan. Write deliverables to `docs/marketing/`, workspace artifacts to `drydock/growth-marketer/`. Ground all market/competitor claims via WebSearch (freshness). When complete, write a receipt to `drydock/.orchestrator/receipts/T14-growth-marketer.json` and mark its task complete.
- **`sales-strategist`** (T15 — Sales) — Consume growth-marketer positioning (start may stagger slightly to read it) + product + security/compliance evidence. Produce pricing & packaging, sales collateral (one-pager, deck outline, demo script), sales process (qualification, pipeline, CRM, outbound), the enablement + security/compliance **trust pack**, and proposal/SOW templates (mark legal artifacts as requiring legal review). Deliverables to `docs/sales/`, workspace to `drydock/sales-strategist/`. Receipt to `T15-sales-strategist.json`; mark complete.
- **`customer-success`** (T16 — Customer Success/Support) — Consume best-available docs (API specs/READMEs, plus technical-writer docs **if already present** — soft input, refined once T11 lands in SUSTAIN) + product + growth-marketer analytics. Produce the onboarding/activation journey, support operations (help center, ticket workflow, SLAs), retention/churn playbooks, and the voice-of-customer loop to product-manager. Deliverables to `docs/customer-success/`, workspace to `drydock/customer-success/`. Receipt to `T16-customer-success.json`; mark complete.

Each subagent may parallelize internally up to 3 concurrent FOREGROUND sub-tasks for genuinely independent work.

## Visual Output

Print the pipeline dashboard with LAUNCH ● active, then the wave announcement:
```
┌─ LAUNCH ───────────────────────────────── 3 agents ─┐
│                                                      │
│  T14  Growth Marketer    positioning + launch plan   │
│  T15  Sales Strategist   pricing + collateral + trust│
│  T16  Customer Success   onboarding + support + retain│
│                                                      │
│  All agents launched. Working autonomously...        │
└──────────────────────────────────────────────────────┘
```

## Worktree Merge-Back

If worktrees were used, merge each LAUNCH subagent's branch back after the wave (see HARDEN merge-back pattern). On conflict: `git merge --abort`, escalate to user.

## Post-LAUNCH: Receipts & Completion

After all three complete:
1. **Verify receipts:** Read `T14-`, `T15-`, `T16-` receipts; confirm listed deliverables exist on disk.
2. Print the completion cascade:
```
┌─ LAUNCH COMPLETE ──────────────────────── ⏱ {time} ─┐
│  ✓ Growth Marketer    {N} channels, {M}-step launch  │
│  ✓ Sales Strategist   {T} tiers, {C} collateral pieces│
│  ✓ Customer Success   onboarding + {K} support flows  │
│  3/3 complete                                         │
└───────────────────────────────────────────────────────┘
```

## Handoff to SUSTAIN

LAUNCH sets up the go-to-market; **customer-success** continues into SUSTAIN (live onboarding, support, retention, and the voice-of-customer loop). Re-anchor on the LAUNCH deliverables, then read `phases/sustain.md` and continue.
