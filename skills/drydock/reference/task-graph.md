# Task Dependency Graph — Two-Wave Parallel Execution

## Task Dependency Graph — Two-Wave Parallel Execution

Dynamic task generation with two-wave parallelism at its core (Wave A: build + analysis; Wave B: execution against code). The orchestrator reads the architecture output (number of services, pages, modules) and generates tasks accordingly — one Agent per work unit. Two smaller parallel groups bracket the core: in DEFINE, the UX Designer (T2b) runs alongside the architect (T2); after Gate 3, the LAUNCH wave (T14–T16) runs the three go-to-market agents in parallel.

### Wave Announcements

**When launching a wave**, print a Tier 2 box listing all agents and their tasks:
```
┌─ WAVE A ──────────────────────────────────── {N} agents ─┐
│                                                           │
│  T3a  Software Engineer    {service list from architecture}│
│  T3b  Frontend Engineer    {page groups from BRD}         │
│  T4a  DevOps               Dockerfiles + CI skeleton      │
│  T5a  QA Engineer          test plan from BRD             │
│  T6a  Security Engineer    STRIDE threat model            │
│  T6b  Code Reviewer        conformance checklist          │
│  T9a  SRE                  SLO definitions                │
│                                                           │
│  All agents launched. Working autonomously...             │
└───────────────────────────────────────────────────────────┘
```

**When a wave completes**, print the checkmark cascade — the peak visual moment:
```
┌─ WAVE A COMPLETE ─────────────────────────── ⏱ {time} ─┐
│                                                          │
│  ✓ Software Engineer    {N} services, {M} endpoints      │
│  ✓ Frontend Engineer    {N} page groups, {M} components  │
│  ✓ DevOps               {N} Dockerfiles, 1 compose       │
│  ✓ QA Engineer          test plan: {N} test cases        │
│  ✓ Security Engineer    STRIDE: {N} threats identified   │
│  ✓ Code Reviewer        checklist: {N} checkpoints       │
│  ✓ SRE                  {N} SLOs, {M} alert rules        │
│                                                          │
│  {N}/{N} complete                                        │
│  → Starting Wave B ({M} agents against written code)     │
└──────────────────────────────────────────────────────────┘
```

Every agent completion line MUST include concrete numbers. No `✓ QA Engineer — complete`. The numbers prove the system did real work.

### Transition Announcements

Between phases and waves, print a concise `→` transition line:
```
  → Starting DEFINE phase
  → Starting BUILD phase (Wave A: {N} agents)
  → Wave A complete, starting Wave B ({N} agents against written code)
  → HARDEN complete, {N} Critical findings → entering remediation
  → All phases complete, presenting final summary
```

**Maximum parallelism mode (default):**

```
T1: product-manager (BRD)
    ↓ [GATE 1]
┌────────────── DEFINE: design + architecture (parallel, both need only the BRD) ──┐
│  T2:  solution-architect (Architecture) ── in-context (interviews user)          │
│  T2b: ux-designer (design-system spec) ─── backgrounded; skip if no frontend     │
│       hands the spec in `docs/design/` to frontend-engineer (T3b) in BUILD       │
└──────────────────────────────────────────────────────────────────────────────────┘
    ↓ [GATE 2]
    ↓ parallelism preference
┌────────────── WAVE A: BUILD + ANALYSIS (all parallel) ──────────────┐
│                                                                      │
│  BUILD (needs architecture):                                         │
│    T3a: software-engineer ──── spawns N agents (1 per service)       │
│    T3b: frontend-engineer ──── spawns N agents (1 per page group)    │
│                                                                      │
│  ANALYSIS (needs architecture only, starts alongside build):         │
│    T4a: devops — Dockerfiles + CI skeleton                           │
│    T5a: qa-engineer — test plan + test scaffolds                     │
│    T6a: security-engineer — STRIDE threat model                      │
│    T6b: code-reviewer — arch conformance + review checklist          │
│    T9a: sre — SLO definitions + alert rules                         │
│                                                                      │
│  Up to 7+ concurrent agents in Wave A                                │
└──────────────────────────────────────────────────────────────────────┘
    ↓ (wait for T3a + T3b code to be written)
┌────────────── WAVE B: EXECUTION against code (all parallel) ────────┐
│                                                                      │
│    T4b: devops — build + push containers                             │
│    T5b: qa-engineer — implement tests (spawns N: unit/integ/e2e/perf)│
│    T6c: security-engineer — code audit + dep scan (spawns N phases)  │
│    T6d: code-reviewer — actual review (spawns N: arch/quality/perf)  │
│    T6e: compliance-officer — control mapping (after T6c audit)        │
│                                                                      │
│  Up to 4 concurrent agents, each spawning 3-4 internal agents        │
└──────────────────────────────────────────────────────────────────────┘
    ↓
T7: devops (IaC + CI/CD) ──────────┐
T8: remediation (HARDEN fixes) ────┘ PARALLEL
    ↓
T9b: sre (chaos + capacity) ──────┐
T10: data-scientist (conditional) ─┘ PARALLEL
    ↓ [GATE 3 — production readiness]
┌────────────── LAUNCH: go-to-market (parallel, after Gate 3) ────────┐
│  T14: growth-marketer  — positioning + launch plan + site copy/SEO  │
│  T15: sales-strategist — pricing + collateral + trust pack          │
│                          (consumes T14 positioning + T6c/T6e evidence)│
│  T16: customer-success — onboarding + support + retention           │
│                          (consumes T14; help center refined in SUSTAIN)│
└──────────────────────────────────────────────────────────────────────┘
    ↓
T11: technical-writer (spawns N: API ref / dev guide / ops guide) ──┐
T12: skill-maker ──────────────────────────────────────────────────┘ PARALLEL
    ↓
T13: Compound Learning + Assembly   (customer-success carries into SUSTAIN)
```

> **Phase order note.** The canonical pipeline is DEFINE → BUILD → HARDEN → SHIP → **LAUNCH** → SUSTAIN. LAUNCH (T14–T16) runs after Gate 3; SUSTAIN (T11–T13) follows. customer-success (T16) bootstraps its help center from the best-available docs (API specs, READMEs) at LAUNCH and refines it once the technical-writer docs (T11) land in SUSTAIN — that doc dependency is soft, so it does not block LAUNCH.

**Standard mode:** Collapses waves — Wave A runs build only, Wave B runs all harden sequentially. No internal skill parallelism.

**Sequential mode:** One task at a time. The full task list (T1, T2, T2b, T3a/T3b, T4a/T4b, T5a/T5b, T6a–T6e, T7–T13, T14–T16) run serially in pipeline order.

### Task Dependencies (Maximum Parallelism)

Create tasks with TaskCreate, then set dependencies with TaskUpdate using the returned IDs.

**Wave A tasks** — the BUILD/ANALYSIS rows (T3a–T9a) all depend on T2 (architecture) and have no dependencies on each other. The DEFINE rows (T1, T2, T2b) are listed here for completeness with their own blockers — note **T2b depends on T1 (the BRD), not T2**, and runs in parallel with the architect:

| Task | Blocked By | Notes |
|------|-----------|-------|
| T1 | — | First task, no blockers |
| T2 | T1 | Needs BRD |
| T2b | T1 | UX Designer — design-system spec; runs parallel with T2 (needs only the BRD). Conditional: skip if `features.frontend: false`. Hands `docs/design/` spec to T3b |
| T3a | T2 | Backend — spawns 1 Agent per service from architecture |
| T3b | T2, T2b | Frontend — spawns 1 Agent per page group from BRD; implements the T2b design-system spec if present |
| T4a | T2 | DevOps analysis — Dockerfiles + CI skeleton |
| T5a | T2 | QA test plan — from BRD + architecture |
| T6a | T2 | Security threat model — STRIDE from architecture |
| T6b | T2 | Review prep — arch conformance checklist |
| T9a | T2 | SRE — SLO definitions from architecture + monitoring |

**Wave B tasks** — depend on T3a/T3b (code) + their Wave A analysis:

| Task | Blocked By | Notes |
|------|-----------|-------|
| T4b | T3a, T4a | Build containers — needs code + Dockerfiles |
| T5b | T3a, T3b, T5a | Implement tests — needs code + test plan |
| T6c | T3a, T3b, T6a | Code audit — needs code + threat model |
| T6d | T3a, T3b, T6b | Code review — needs code + checklist |
| T6e | T6c | Compliance mapping — needs the security audit; maps controls to in-scope frameworks (HARDEN-phase parallel agent, dispatch in `phases/harden.md`) |

**Post-wave tasks:**

| Task | Blocked By | Notes |
|------|-----------|-------|
| T7 | T5b, T6c, T6d | IaC + CI/CD — needs HARDEN output |
| T8 | T5b, T6c, T6d | Remediation — needs HARDEN findings |
| T9b | T7, T8, T9a | SRE execution — needs infra + SLO defs |
| T10 | T7, T8 | Conditional on AI/ML usage |
| T11 | T9b | Docs — needs all prior output |
| T12 | T9b | Skills — needs all prior output |
| T13 | T11, T12 | Final step |

**LAUNCH tasks** — go-to-market, run in parallel after Gate 3 (production-ready). Dispatch in `phases/launch.md`. Standalone **Launch (GTM)** mode requires an already-shipped/described product:

| Task | Blocked By | Notes |
|------|-----------|-------|
| T14 | Gate 3 | Growth Marketer — positioning, launch plan, site copy + SEO briefs, funnels. Needs BRD + shipped product |
| T15 | T14, T6c, T6e | Sales Strategist — pricing, collateral, sales process; turns T14 positioning + the security (T6c) / compliance (T6e) evidence into a buyer trust pack |
| T16 | T14 | Customer Success — onboarding, support ops, retention; consumes T14 analytics. Help-center docs (T11) are a soft input refined in SUSTAIN; carries into SUSTAIN |

### Dynamic Task Generation

After Gate 1 (BRD approved), the UX Designer (T2b) launches alongside the architect (T2) — both need only the BRD. After Gate 2 (architecture approved), the orchestrator reads the architecture output to determine work units:

1. **Count services** — Read `docs/architecture/` service list or `api/` specs. For each service, create a subtask under T3a.
2. **Count pages** — Read BRD user stories. Group into page clusters (auth, dashboard, settings, etc.). For each group, create a subtask under T3b.
3. **Generate Wave A TaskList** — All T3a subtasks + T3b subtasks + T4a + T5a + T6a + T6b + T9a. No cross-dependencies.
4. **On Wave A completion** — Generate Wave B TaskList with dependencies on Wave A outputs.
5. **On Gate 3 pass (LAUNCH)** — Generate the LAUNCH TaskList: T14 + T15 + T16, dispatched in parallel per `phases/launch.md`.

Each subtask is dispatched as a natural-language delegation to the matching subagent. For a backend service subtask:

> Delegate to the `software-engineer` subagent (`agents/software-engineer.md` — runs backgrounded in its own worktree per its definition). Task context: implement the `{service_name}` service. Read the architecture at `docs/architecture/` and the API contract at `api/openapi/{service}.yaml`; write output to `services/{service_name}/`. When done, write receipt `drydock/.orchestrator/receipts/T3a-software-engineer.json` and mark its task complete.

The subagent may parallelize internally up to 3 concurrent FOREGROUND sub-tasks for genuinely independent work (e.g. multiple services). Do not pass `isolation`/`background`/`mode` — those live in the subagent's frontmatter.

### Conditional Tasks

- **T2b (UX Designer) and T3b (Frontend):** Skip both if `.drydock.yaml` has `features.frontend: false` — no UI to design or build.
- **T10 (Data Scientist):** Auto-detect by scanning for `openai`, `anthropic`, `langchain`, `transformers`, `torch`, `tensorflow` imports. If not detected and `features.ai_ml: false`, mark as completed immediately.
- **T14–T16 (LAUNCH):** Run in a Full Build after Gate 3, or standalone via **Launch (GTM)** mode. The standalone mode requires an already-shipped/described product and presents a GTM-plan gate first.

