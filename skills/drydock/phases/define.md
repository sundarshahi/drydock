# DEFINE Phase — Dispatcher

This phase manages tasks T1 (Product Manager), T2 (Solution Architect), and T2b (UX Designer). T1 → Gate 1 → T2 + T2b (parallel) → Gate 2. T1 and T2 are sequential, gated; T2b (UX) launches alongside T2 once the BRD is approved — it depends on the BRD, not the architecture.

## Visual Output

Print pipeline dashboard with DEFINE ● active on phase start:
```
  → Starting DEFINE phase
```

Each skill (PM, Architect) prints its own `━━━ [Skill Name] ━━━` header and `[1/N]` phase progress per visual-identity protocol.

Print gate ceremony before each gate (see orchestrator Gate 1 and Gate 2 templates).

On phase completion, print transition:
```
  → DEFINE complete, starting BUILD phase
```

## Pre-Flight

Read `.drydock.yaml` for path overrides:
- `paths.brd` → BRD output location (default: `drydock/product-manager/BRD/`)
- `paths.api_contracts` → API contract location (default: `api/openapi/*.yaml`)
- `paths.adrs` → ADR location (default: `docs/architecture/architecture-decision-records/`)
- `paths.architecture_docs` → Architecture docs (default: `docs/architecture/`)
- `paths.design` → UX design-system spec location (default: `docs/design/`) — used by T2b dispatch, the receipt verify, and the re-anchor below; ux-designer honors the same override

When `paths.design` is set, use it (not the literal `docs/design/`) in the T2b dispatch prompt, the receipt-artifact verification, and the DEFINE→BUILD re-anchor.

## T1: Product Manager — BRD

Mark task in progress and invoke as Skill (needs user interaction for CEO interview):

```python
TaskUpdate(taskId=t1_id, status="in_progress")
Skill(skill="product-manager")
```

The product-manager skill will:
1. Research domain via WebSearch
2. Conduct CEO interview (3-5 questions via AskUserQuestion with multiSelect), **including the compliance-discovery questions** (data classes handled — PHI/cardholder/EU-personal-data/etc., target markets, customer type) that produce the product signals the compliance-officer scopes from
3. Write BRD to `drydock/product-manager/BRD/`
4. Outputs: `brd.md`, `research-notes.md`, `constraints.md`, and a `compliance-signals.md` (the compliance-discovery answers) — this is a **mandatory input the solution-architect reads for compliance scoping** and the compliance-officer (T6e, HARDEN) reads for framework scoping

**On completion:** The product-manager writes a receipt to `.orchestrator/receipts/T1-product-manager.json`, then:
```python
TaskUpdate(taskId=t1_id, status="completed")
```

### Gate 1 — BRD Approval

**Before opening gate:** Read `drydock/.orchestrator/receipts/T1-product-manager.json`. Verify all `artifacts` exist on disk. Use receipt `metrics` for gate display numbers.

Present Gate 1 using the orchestrator's gate pattern. On approval, unblock T2.

If user selects "I have changes" → iterate on BRD, re-present Gate 1.
If user selects "Show BRD details" → display BRD, re-present Gate 1.

## T2b: UX Designer — Design-System Spec (parallel with T2)

**Conditional — skip if `.drydock.yaml` has `features.frontend: false`** (no UI to design). When skipped, `TaskUpdate(taskId=t2b_id, status="completed")` and move on.

Once Gate 1 passes, the UX Designer needs only the approved BRD, so it runs **alongside the architect (T2)**. The Solution Architect runs in-context (it interviews the user); the UX Designer runs **backgrounded in its own worktree per its definition** (`agents/ux-designer.md`), so launch it first, then start T2 — the two overlap.

```python
TaskUpdate(taskId=t2b_id, status="in_progress")
```

Delegate to the `ux-designer` subagent (carry task context only — the agent declares background/isolation and invokes its own skill):

> Read the approved BRD at `drydock/product-manager/BRD/` (user stories, personas, constraints). Produce the UX deliverables — UX research synthesis, information architecture, the **design-system specification** (design tokens, type scale, WCAG-AA color, component specs with all states, motion), interaction/flow specs, and the usability/accessibility checklist. Write deliverables to `docs/design/` and workspace artifacts to `drydock/ux-designer/`. The design-system spec is a **mandatory input for frontend-engineer (T3b) in BUILD** — frontend implements this spec, it does not re-author it. When complete, write a receipt to `drydock/.orchestrator/receipts/T2b-ux-designer.json` and mark its task complete.

If a frontend already exists (brownfield), it produces a UX audit + improvement spec instead of greenfield IA.

**On completion:** the receipt lands at `.orchestrator/receipts/T2b-ux-designer.json` and the task is marked complete. If T2b is still running when Gate 2 is reached, that is fine — its spec only needs to land before BUILD's frontend work (T3b) starts; if T3b is reached before the spec exists, T3b blocks on it rather than building without the design system.

## T2: Solution Architect — Architecture

```python
TaskUpdate(taskId=t2_id, status="in_progress")
Skill(skill="solution-architect")
```

The solution-architect skill will:
1. Read BRD from `drydock/product-manager/BRD/`, **including `compliance-signals.md`** — the PM compliance-discovery answers flow into the architect's compliance scoping (which frameworks the design must accommodate, data-residency/encryption/audit-log architecture), recorded so the compliance-officer (T6e) consumes a consistent scope
2. Design architecture: ADRs, tech stack, system design (honoring `architecture-boundaries.md` — inward dependencies, port→adapter wiring — so BUILD inherits an enforceable boundary)
3. Design API contracts (OpenAPI 3.1), data model (ERD), migrations
4. Generate project scaffold
5. Write deliverables to **project root**: `api/`, `schemas/`, `docs/architecture/`
6. Write workspace artifacts to `drydock/solution-architect/` (including the compliance-scoping note)

**On completion:** The solution-architect writes a receipt to `.orchestrator/receipts/T2-solution-architect.json`, then:
```python
TaskUpdate(taskId=t2_id, status="completed")
```

### Gate 2 — Architecture Approval

**Before opening gate:** Read `drydock/.orchestrator/receipts/T2-solution-architect.json`. Verify all `artifacts` exist on disk. Use receipt `metrics` for gate display numbers.

Present Gate 2 using the orchestrator's gate pattern. On approval, proceed to BUILD phase.

## Handoff to BUILD

After Gate 2 approval:
1. **Verify receipts:** Read `drydock/.orchestrator/receipts/T1-product-manager.json`, `T2-solution-architect.json`, and (unless frontend is disabled) `T2b-ux-designer.json`. Verify all listed artifacts exist on disk. If T2b is still in progress, let it finish before starting BUILD's frontend work (T3b) — T3b consumes the design-system spec.
2. **Re-anchor:** Re-read from disk before transitioning:
   - `drydock/product-manager/BRD/brd.md`
   - `drydock/solution-architect/system-design.md`
   - `docs/architecture/adr/*.md` (list files)
   - `api/openapi/*.yaml` (list files)
   - `docs/design/` (design-system spec — list files; frontend implements this)
   - `.orchestrator/settings.md`
3. Verify architecture outputs exist at project root (`api/`, `schemas/`, `docs/architecture/`)
4. Log decisions to `drydock/.orchestrator/decisions-log.md`
5. Read `phases/build.md` and begin BUILD phase — use freshly-read artifacts when creating agent task prompts

**Sequence note — security-requirements before BUILD writes code:** At the start of BUILD the Security Engineer (T6a) runs the STRIDE threat model alongside the build agents, and it MUST emit `drydock/security-engineer/security-requirements.md` (the per-threat control list) EARLY — before T3a/T3b begin writing implementation. BUILD agents read this file as a **mandatory input** (see `phases/build.md` Re-Anchor), so the STRIDE step is sequenced to land first; if it is not yet available when a build agent starts, the build agent blocks on it rather than coding without the security requirements. (T6a then runs its full code audit in HARDEN — same agent, same ID, two sequenced activities.)

## Failure Handling

- If PM cannot gather enough requirements → escalate to user
- If Architect finds contradictions in BRD → flag to user, do not silently resolve
- Each skill self-debugs before escalating
