# DEFINE Phase — Dispatcher

This phase manages tasks T1 (Product Manager) and T2 (Solution Architect). Sequential execution with Gate 1 and Gate 2.

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

Read `.shipyard.yaml` for path overrides:
- `paths.brd` → BRD output location (default: `Shipyard/product-manager/BRD/`)
- `paths.api_contracts` → API contract location (default: `api/openapi/*.yaml`)
- `paths.adrs` → ADR location (default: `docs/architecture/architecture-decision-records/`)
- `paths.architecture_docs` → Architecture docs (default: `docs/architecture/`)

## T1: Product Manager — BRD

Mark task in progress and invoke as Skill (needs user interaction for CEO interview):

```python
TaskUpdate(taskId=t1_id, status="in_progress")
Skill(skill="product-manager")
```

The product-manager skill will:
1. Research domain via WebSearch
2. Conduct CEO interview (3-5 questions via AskUserQuestion with multiSelect), **including the compliance-discovery questions** (data classes handled — PHI/cardholder/EU-personal-data/etc., target markets, customer type) that produce the product signals the compliance-officer scopes from
3. Write BRD to `Shipyard/product-manager/BRD/`
4. Outputs: `brd.md`, `research-notes.md`, `constraints.md`, and a `compliance-signals.md` (the compliance-discovery answers) — this is a **mandatory input the solution-architect reads for compliance scoping** and the compliance-officer (T6c, HARDEN) reads for framework scoping

**On completion:** The product-manager writes a receipt to `.orchestrator/receipts/T1-product-manager.json`, then:
```python
TaskUpdate(taskId=t1_id, status="completed")
```

### Gate 1 — BRD Approval

**Before opening gate:** Read `Shipyard/.orchestrator/receipts/T1-product-manager.json`. Verify all `artifacts` exist on disk. Use receipt `metrics` for gate display numbers.

Present Gate 1 using the orchestrator's gate pattern. On approval, unblock T2.

If user selects "I have changes" → iterate on BRD, re-present Gate 1.
If user selects "Show BRD details" → display BRD, re-present Gate 1.

## T2: Solution Architect — Architecture

```python
TaskUpdate(taskId=t2_id, status="in_progress")
Skill(skill="solution-architect")
```

The solution-architect skill will:
1. Read BRD from `Shipyard/product-manager/BRD/`, **including `compliance-signals.md`** — the PM compliance-discovery answers flow into the architect's compliance scoping (which frameworks the design must accommodate, data-residency/encryption/audit-log architecture), recorded so the compliance-officer (T6c) consumes a consistent scope
2. Design architecture: ADRs, tech stack, system design (honoring `architecture-boundaries.md` — inward dependencies, port→adapter wiring — so BUILD inherits an enforceable boundary)
3. Design API contracts (OpenAPI 3.1), data model (ERD), migrations
4. Generate project scaffold
5. Write deliverables to **project root**: `api/`, `schemas/`, `docs/architecture/`
6. Write workspace artifacts to `Shipyard/solution-architect/` (including the compliance-scoping note)

**On completion:** The solution-architect writes a receipt to `.orchestrator/receipts/T2-solution-architect.json`, then:
```python
TaskUpdate(taskId=t2_id, status="completed")
```

### Gate 2 — Architecture Approval

**Before opening gate:** Read `Shipyard/.orchestrator/receipts/T2-solution-architect.json`. Verify all `artifacts` exist on disk. Use receipt `metrics` for gate display numbers.

Present Gate 2 using the orchestrator's gate pattern. On approval, proceed to BUILD phase.

## Handoff to BUILD

After Gate 2 approval:
1. **Verify receipts:** Read `Shipyard/.orchestrator/receipts/T1-product-manager.json` and `T2-solution-architect.json`. Verify all listed artifacts exist on disk.
2. **Re-anchor:** Re-read from disk before transitioning:
   - `Shipyard/product-manager/BRD/brd.md`
   - `Shipyard/solution-architect/system-design.md`
   - `docs/architecture/adr/*.md` (list files)
   - `api/openapi/*.yaml` (list files)
   - `.orchestrator/settings.md`
3. Verify architecture outputs exist at project root (`api/`, `schemas/`, `docs/architecture/`)
4. Log decisions to `Shipyard/.orchestrator/decisions-log.md`
5. Read `phases/build.md` and begin BUILD phase — use freshly-read artifacts when creating agent task prompts

**Sequence note — security-requirements before BUILD writes code:** In BUILD Wave A the Security Engineer (T6a) runs the STRIDE threat model alongside the build agents, and it MUST emit `Shipyard/security-engineer/security-requirements.md` (the per-threat control list) EARLY — before T3a/T3b begin writing implementation. BUILD agents read this file as a **mandatory input** (see `phases/build.md` Re-Anchor), so the STRIDE step is sequenced to land first; if it is not yet available when a build agent starts, the build agent blocks on it rather than coding without the security requirements.

## Failure Handling

- If PM cannot gather enough requirements → escalate to user
- If Architect finds contradictions in BRD → flag to user, do not silently resolve
- Each skill self-debugs before escalating
