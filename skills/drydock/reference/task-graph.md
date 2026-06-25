# Task Dependency Graph — Per-Phase Parallel Execution

## Task Dependency Graph — Per-Phase Parallel Execution

The pipeline runs phase by phase — **DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN** — sequential and gated. **Within each phase, independent tasks run in parallel**; the orchestrator reads the architecture output (number of services, pages, modules) and spawns one Agent per work unit.

**Task IDs here match the phase dispatchers and the receipt filenames exactly** (`T3a-software-engineer.json`, `T6a-security-engineer.json`, …). These are the IDs the orchestrator wires with `TaskCreate`/`TaskUpdate`, so the graph and the dispatchers stay in lock-step. The flat per-phase scheme is the source of truth; the dispatchers in `phases/*.md` own the delegation detail.

### Task list by phase

| Phase | Dispatcher | Tasks (run in parallel within the phase) |
|-------|-----------|------------------------------------------|
| DEFINE | `phases/define.md` | T1 (product-manager) → Gate 1 → **T2 (solution-architect) ∥ T2b (ux-designer)** → Gate 2 |
| BUILD | `phases/build.md` | **T3a (software-engineer) ∥ T3b (frontend-engineer) ∥ T4 (devops — containerization)** |
| HARDEN | `phases/harden.md` | **T5 (qa-engineer) ∥ T6a (security-engineer) ∥ T6b (code-reviewer) ∥ T6e (compliance-officer)** |
| SHIP | `phases/ship.md` | **T7 (devops — IaC + CI/CD) ∥ T8 (remediation)**, then **T9 (sre) ∥ T10 (data-scientist, conditional)** → Gate 3 |
| LAUNCH | `phases/launch.md` | **T14 (growth-marketer) ∥ T15 (sales-strategist) ∥ T16 (customer-success)** |
| SUSTAIN | `phases/sustain.md` | **T11 (technical-writer) ∥ T12 (skill-maker)**, then T13 (compound learning + assembly) |

> The same agent can run in more than one phase under the same ID. **security-engineer (T6a)** emits `security-requirements.md` early (sequenced at the start of BUILD as a mandatory BUILD input — see `phases/define.md` handoff note) and runs its full code audit in HARDEN; **devops** runs containerization in BUILD (T4) and IaC + CI/CD in SHIP (T7).

### Visual flow

```
T1: product-manager (BRD)
    ↓ [GATE 1]
┌── DEFINE: design + architecture (parallel — both need only the BRD) ──┐
│  T2:  solution-architect (Architecture) ── in-context (interviews user)│
│  T2b: ux-designer (design-system spec) ─── backgrounded; skip if no UI │
│       hands the spec in `docs/design/` to frontend-engineer (T3b)      │
└────────────────────────────────────────────────────────────────────────┘
    ↓ [GATE 2]
┌── BUILD: write the system (parallel) ──────────────────────────────────┐
│  T3a: software-engineer ── spawns N agents (1 per service)             │
│  T3b: frontend-engineer ── spawns N agents (1 per page group)          │
│  T4:  devops ──────────── Dockerfiles + containerization (after backend)│
└────────────────────────────────────────────────────────────────────────┘
    ↓ (code written)
┌── HARDEN: audit + test against the code (parallel) ────────────────────┐
│  T5:  qa-engineer ──────── implement tests (spawns N: unit/integ/e2e/perf)│
│  T6a: security-engineer ── code audit + dep scan (spawns N phases)      │
│  T6b: code-reviewer ────── adversarial review (spawns N: arch/quality/perf)│
│  T6e: compliance-officer ─ control mapping (consumes the T6a audit)     │
└────────────────────────────────────────────────────────────────────────┘
    ↓
T7: devops (IaC + CI/CD) ──────────┐
T8: remediation (HARDEN fixes) ────┘ PARALLEL
    ↓
T9:  sre (readiness + SLO + chaos + capacity) ─┐
T10: data-scientist (conditional) ─────────────┘ PARALLEL
    ↓ [GATE 3 — production readiness]
┌── LAUNCH: go-to-market (parallel, after Gate 3) ───────────────────────┐
│  T14: growth-marketer  — positioning + launch plan + site copy/SEO     │
│  T15: sales-strategist — pricing + collateral + trust pack             │
│                          (consumes T14 positioning + T6a/T6e evidence)  │
│  T16: customer-success — onboarding + support + retention              │
│                          (consumes T14; help center refined in SUSTAIN) │
└────────────────────────────────────────────────────────────────────────┘
    ↓
T11: technical-writer (spawns N: API ref / dev guide / ops guide) ──┐
T12: skill-maker ──────────────────────────────────────────────────┘ PARALLEL
    ↓
T13: Compound Learning + Assembly   (customer-success carries into SUSTAIN)
```

> **Phase order note.** LAUNCH (T14–T16) runs after Gate 3; SUSTAIN (T11–T13) follows. customer-success (T16) bootstraps its help center from the best-available docs (API specs, READMEs) at LAUNCH and refines it once the technical-writer docs (T11) land in SUSTAIN — that doc dependency is soft, so it does not block LAUNCH.

### Phase Announcements

**When launching a phase**, print a Tier 2 box listing all agents and their tasks (BUILD shown):
```
┌─ BUILD ───────────────────────────────────── {N} agents ─┐
│                                                           │
│  T3a  Software Engineer    {service list from architecture}│
│  T3b  Frontend Engineer    {page groups from BRD}         │
│  T4   DevOps               Dockerfiles + containerization │
│                                                           │
│  All agents launched. Working autonomously...             │
└───────────────────────────────────────────────────────────┘
```

**When a phase completes**, print the checkmark cascade — the peak visual moment (HARDEN shown):
```
┌─ HARDEN COMPLETE ─────────────────────────── ⏱ {time} ─┐
│                                                          │
│  ✓ QA Engineer          {N} tests, {M} passing          │
│  ✓ Security Engineer    {N} findings ({M} Critical/High) │
│  ✓ Code Reviewer        {N} findings ({M} Critical/High) │
│  ✓ Compliance Officer   {N} controls ({M} missing)       │
│                                                          │
│  {N}/{N} complete                                        │
│  → Starting SHIP phase                                   │
└──────────────────────────────────────────────────────────┘
```

Every agent completion line MUST include concrete numbers. No `✓ QA Engineer — complete`. The numbers prove the system did real work.

### Transition Announcements

Between phases, print a concise `→` transition line:
```
  → Starting DEFINE phase
  → Starting BUILD phase ({N} agents)
  → BUILD complete, starting HARDEN ({N} agents against written code)
  → HARDEN complete, {N} Critical findings → entering remediation
  → All phases complete, presenting final summary
```

### Parallelism modes

- **Maximum parallelism (default):** every independent unit gets its own agent — T3a spawns one per service, T3b one per page group, and each HARDEN/SHIP/LAUNCH/SUSTAIN agent spawns its own internal sub-agents (see the orchestrator's internal-parallelism table).
- **Standard:** one agent per task within a phase; no internal sub-agent fan-out.
- **Sequential:** one task at a time, in pipeline order — T1, T2, T2b, T3a, T3b, T4, T5, T6a, T6b, T6e, T7, T8, T9, T10, T14, T15, T16, T11, T12, T13.

### Task Dependencies

Create tasks with `TaskCreate`, then set dependencies with `TaskUpdate` using the returned IDs.

**DEFINE:**

| Task | Blocked By | Notes |
|------|-----------|-------|
| T1 | — | Product Manager — first task, no blockers |
| T2 | T1 | Architect — needs the BRD |
| T2b | T1 | UX Designer — design-system spec; runs **parallel with T2** (needs only the BRD, not the architecture). Conditional: skip if `features.frontend: false`. Hands `docs/design/` spec to T3b |

**BUILD** — needs the architecture (and the design spec for the frontend):

| Task | Blocked By | Notes |
|------|-----------|-------|
| T3a | T2 | Backend — spawns 1 Agent per service from the architecture |
| T3b | T2, T2b | Frontend — spawns 1 Agent per page group from the BRD; implements the T2b design-system spec if present |
| T4 | T3a | DevOps — Dockerfiles + containerization; starts once the backend is written |

**HARDEN** — runs against the written code:

| Task | Blocked By | Notes |
|------|-----------|-------|
| T5 | T3a, T3b | QA — implement + run tests (spawns N: unit/integration/e2e/perf) |
| T6a | T3a, T3b | Security — code audit + dep scan; SOLE OWASP authority. (Also emits `security-requirements.md` early as a BUILD input — see `phases/define.md`.) |
| T6b | T3a, T3b | Code review — adversarial arch/quality/perf review |
| T6e | T6a | Compliance — maps controls to in-scope frameworks; consumes the security audit (dispatch in `phases/harden.md`; receipt `Tcomp-compliance-officer.json`) |

**SHIP** — needs HARDEN output:

| Task | Blocked By | Notes |
|------|-----------|-------|
| T7 | T5, T6a, T6b | IaC + CI/CD — needs harden output |
| T8 | T5, T6a, T6b, T6e | Remediation — fixes HARDEN findings (incl. missing compliance controls) |
| T9 | T7, T8 | SRE — production readiness, SLOs, chaos + capacity |
| T10 | T7, T8 | Data Scientist — conditional on AI/ML usage |

**LAUNCH** — go-to-market, parallel after Gate 3 (production-ready). Standalone **Launch (GTM)** mode requires an already-shipped/described product:

| Task | Blocked By | Notes |
|------|-----------|-------|
| T14 | Gate 3 | Growth Marketer — positioning, launch plan, site copy + SEO briefs, funnels. Needs BRD + shipped product |
| T15 | T14, T6a, T6e | Sales Strategist — pricing, collateral, sales process; turns T14 positioning + the security (T6a) / compliance (T6e) evidence into a buyer trust pack |
| T16 | T14 | Customer Success — onboarding, support ops, retention; consumes T14 analytics. Help-center docs (T11) are a soft input refined in SUSTAIN; carries into SUSTAIN |

**SUSTAIN:**

| Task | Blocked By | Notes |
|------|-----------|-------|
| T11 | T9 | Docs — needs all prior output |
| T12 | T9 | Project-specific skills — needs all prior output |
| T13 | T11, T12 | Compound learning + final assembly |

### Dynamic Task Generation

After Gate 1 (BRD approved), the UX Designer (T2b) launches alongside the architect (T2) — both need only the BRD. After Gate 2 (architecture approved), the orchestrator reads the architecture output to determine work units:

1. **Count services** — Read `docs/architecture/` service list or `api/` specs. For each service, create a subtask under T3a.
2. **Count pages** — Read BRD user stories. Group into page clusters (auth, dashboard, settings, etc.). For each group, create a subtask under T3b.
3. **Generate the BUILD TaskList** — all T3a subtasks + all T3b subtasks + T4, no cross-dependencies among T3a/T3b.
4. **On BUILD completion** — generate the HARDEN TaskList (T5 + T6a + T6b + T6e) with dependencies on the written code.
5. **On Gate 3 pass (LAUNCH)** — generate the LAUNCH TaskList: T14 + T15 + T16, dispatched in parallel per `phases/launch.md`.

Each subtask is dispatched as a natural-language delegation to the matching subagent. For a backend service subtask:

> Delegate to the `software-engineer` subagent (`agents/software-engineer.md` — runs backgrounded in its own worktree per its definition). Task context: implement the `{service_name}` service. Read the architecture at `docs/architecture/` and the API contract at `api/openapi/{service}.yaml`; write output to `services/{service_name}/`. When done, write receipt `drydock/.orchestrator/receipts/T3a-software-engineer.json` and mark its task complete.

The subagent may parallelize internally up to 3 concurrent FOREGROUND sub-tasks for genuinely independent work (e.g. multiple services). Do not pass `isolation`/`background`/`mode` — those live in the subagent's frontmatter.

### Conditional Tasks

- **T2b (UX Designer) and T3b (Frontend):** Skip both if `.drydock.yaml` has `features.frontend: false` — no UI to design or build.
- **T10 (Data Scientist):** Auto-detect by scanning for `openai`, `anthropic`, `langchain`, `transformers`, `torch`, `tensorflow` imports. If not detected and `features.ai_ml: false`, mark as completed immediately.
- **T14–T16 (LAUNCH):** Run in a Full Build after Gate 3, or standalone via **Launch (GTM)** mode. The standalone mode requires an already-shipped/described product and presents a GTM-plan gate first.
