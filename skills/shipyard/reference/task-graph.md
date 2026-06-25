# Task Dependency Graph — Two-Wave Parallel Execution

## Task Dependency Graph — Two-Wave Parallel Execution

Dynamic task generation with two-wave parallelism. The orchestrator reads the architecture output (number of services, pages, modules) and generates tasks accordingly — one Agent per work unit.

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
T2: solution-architect (Architecture)
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
    ↓ [GATE 3]
T11: technical-writer (spawns N: API ref / dev guide / ops guide) ──┐
T12: skill-maker ──────────────────────────────────────────────────┘ PARALLEL
    ↓
T13: Compound Learning + Assembly
```

**Standard mode:** Collapses waves — Wave A runs build only, Wave B runs all harden sequentially. No internal skill parallelism.

**Sequential mode:** One task at a time. Original 13-task serial execution.

### Task Dependencies (Maximum Parallelism)

Create tasks with TaskCreate, then set dependencies with TaskUpdate using the returned IDs.

**Wave A tasks** — all depend on T2 (architecture), no dependencies on each other:

| Task | Blocked By | Notes |
|------|-----------|-------|
| T1 | — | First task, no blockers |
| T2 | T1 | Needs BRD |
| T3a | T2 | Backend — spawns 1 Agent per service from architecture |
| T3b | T2 | Frontend — spawns 1 Agent per page group from BRD |
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

### Dynamic Task Generation

After Gate 2 (architecture approved), the orchestrator reads the architecture output to determine work units:

1. **Count services** — Read `docs/architecture/` service list or `api/` specs. For each service, create a subtask under T3a.
2. **Count pages** — Read BRD user stories. Group into page clusters (auth, dashboard, settings, etc.). For each group, create a subtask under T3b.
3. **Generate Wave A TaskList** — All T3a subtasks + T3b subtasks + T4a + T5a + T6a + T6b + T9a. No cross-dependencies.
4. **On Wave A completion** — Generate Wave B TaskList with dependencies on Wave A outputs.

Each subtask is dispatched as a natural-language delegation to the matching subagent. For a backend service subtask:

> Delegate to the `software-engineer` subagent (`agents/software-engineer.md` — runs backgrounded in its own worktree per its definition). Task context: implement the `{service_name}` service. Read the architecture at `docs/architecture/` and the API contract at `api/openapi/{service}.yaml`; write output to `services/{service_name}/`. When done, write receipt `Shipyard/.orchestrator/receipts/T3a-software-engineer.json` and mark its task complete.

The subagent may parallelize internally up to 3 concurrent FOREGROUND sub-tasks for genuinely independent work (e.g. multiple services). Do not pass `isolation`/`background`/`mode` — those live in the subagent's frontmatter.

### Conditional Tasks

- **T3b (Frontend):** Skip if `.shipyard.yaml` has `features.frontend: false`
- **T10 (Data Scientist):** Auto-detect by scanning for `openai`, `anthropic`, `langchain`, `transformers`, `torch`, `tensorflow` imports. If not detected and `features.ai_ml: false`, mark as completed immediately.

