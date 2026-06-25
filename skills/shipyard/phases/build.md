# BUILD Phase — Dispatcher

This phase manages tasks T3a (Backend), T3b (Frontend), and T4 (DevOps Containerization). Features PARALLEL #1 and #2.

## Visual Output

Print pipeline dashboard with BUILD ● active on phase start. Then print Wave A announcement:
```
┌─ WAVE A: BUILD + ANALYSIS ────────────── {N} agents ─┐
│                                                        │
│  T3a  Software Engineer    {services from architecture}│
│  T3b  Frontend Engineer    {pages from BRD}            │
│  T4a  DevOps               Dockerfiles + CI skeleton   │
│  T5a  QA Engineer          test plan from BRD          │
│  T6a  Security Engineer    STRIDE threat model         │
│  T6b  Code Reviewer        conformance checklist       │
│  T9a  SRE                  SLO definitions             │
│                                                        │
│  All agents launched. Working autonomously...          │
└────────────────────────────────────────────────────────┘
```

When Wave A completes, print the checkmark cascade:
```
┌─ WAVE A COMPLETE ─────────────────────── ⏱ {time} ─┐
│                                                      │
│  ✓ Software Engineer    {N} services, {M} endpoints  │
│  ✓ Frontend Engineer    {N} pages, {M} components    │
│  ✓ DevOps               {N} Dockerfiles, 1 compose   │
│  ✓ QA Engineer          {N} test cases planned       │
│  ✓ Security Engineer    STRIDE: {N} threats          │
│  ✓ Code Reviewer        {N} checkpoints defined      │
│  ✓ SRE                  {N} SLOs, {M} alerts         │
│                                                      │
│  {N}/{N} complete                                    │
│  → Starting Wave B ({M} agents against written code) │
└──────────────────────────────────────────────────────┘
```

Then print Wave B announcement and completion similarly. Each agent's completion line MUST include concrete numbers.

## Re-Anchor

Before creating any agent tasks, re-read key artifacts from disk:
- `Shipyard/product-manager/BRD/brd.md`
- `Shipyard/solution-architect/system-design.md`
- `docs/architecture/adr/*.md` (Glob to list, Read key ADRs)
- `api/openapi/*.yaml` (Glob to list)
- `Shipyard/security-engineer/security-requirements.md` — the EARLY STRIDE-derived security-requirements artifact emitted by T6a in DEFINE/Wave A. This is a **mandatory BUILD input**: every BUILD agent prompt below MUST instruct the agent to read it and treat its controls (authn/authz, input-validation, output-encoding, secrets handling per threat) as acceptance criteria, not optional advice.
- `.orchestrator/receipts/T1-*.json`, `.orchestrator/receipts/T2-*.json`

Use this freshly-read data when writing agent task prompts below — not your compressed memory of DEFINE phase.

## Pre-Flight

Read `.shipyard.yaml` to determine:
- `features.frontend` → if false, skip T3b
- `project.architecture` → monolith vs microservices (affects containerization)
- `paths.services`, `paths.frontend`, `paths.shared_libs` → output locations

## Worktree Pre-Flight

Before launching parallel agents, check if worktree isolation is available:

```python
# Check for clean git state (worktrees require committed state)
result = Bash("git status --porcelain 2>/dev/null | head -5")
if result.strip():
  # Dirty repo — ask user
  AskUserQuestion(questions=[{
    "question": "Parallel agents work best with worktree isolation, but you have uncommitted changes.",
    "header": "Worktree Isolation",
    "options": [
      {"label": "Auto-commit and use worktrees (Recommended)", "description": "Commit current state, isolate each agent in its own worktree"},
      {"label": "Skip worktrees — run in shared directory", "description": "Agents share the working directory (risk of file conflicts)"},
      {"label": "Chat about this", "description": "Free-form input"}
    ],
    "multiSelect": False
  }])
  # If auto-commit: git add -A && git commit -m "shipyard: pre-BUILD checkpoint"
  # If skip: set use_worktrees = False
else:
  use_worktrees = True
```

Store the worktree decision in `Shipyard/.orchestrator/settings.md` by appending:
```
Worktrees: [enabled|disabled]
```

## PARALLEL #1: T3a + T3b

Spawn backend and frontend agents simultaneously as background Agents.
When `use_worktrees` is True, add `isolation="worktree"` to each Agent call. Each agent gets its own isolated copy of the repo — no file race conditions.

```python
# T3a: Backend Engineering
TaskUpdate(taskId=t3a_id, status="in_progress")
Agent(
  prompt="""You are the Backend Engineer.
Use the Skill tool to invoke 'shipyard:software-engineer' to load your complete methodology and follow it.
Read architecture from: api/, schemas/, docs/architecture/
Read protocols from: Shipyard/.protocols/ (security-defaults.md, observability-contract.md, and architecture-boundaries.md are MANDATORY — write secure-by-default code, emit the contract's canonical metric/log/span names, and keep domain imports pointing inward at write time; do not defer these to the HARDEN audit).
MANDATORY input: read Shipyard/security-engineer/security-requirements.md (the EARLY STRIDE threat-model output) and implement its per-threat controls as acceptance criteria.
Read .shipyard.yaml for paths and preferences.
Write services to project root: services/, libs/shared/
Write workspace artifacts to: Shipyard/software-engineer/
TDD enforced: write test → watch fail → implement → watch pass → refactor.
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T3a-software-engineer.json with task, agent, phase, status, artifacts, metrics, effort, verification. The receipt's verification block MUST assert "security-defaults checklist passes" (the BUILD Quality Bar line from security-defaults.md) with per-rule pass/fail evidence. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Remove this line if use_worktrees is False
)

# T3b: Frontend Engineering (skip if features.frontend is false)
TaskUpdate(taskId=t3b_id, status="in_progress")
Agent(
  prompt="""You are the Frontend Engineer.
Read API contracts from: api/
Read BRD user stories from: Shipyard/product-manager/BRD/
Read protocols from: Shipyard/.protocols/ (security-defaults.md and observability-contract.md are MANDATORY — apply output-encoding/XSS-safe rendering and secrets handling at write time, and emit the contract's canonical client metric/log names).
MANDATORY input: read Shipyard/security-engineer/security-requirements.md (the EARLY STRIDE threat-model output) and implement its per-threat controls as acceptance criteria.
Read .shipyard.yaml for framework and styling preferences.

Use the Skill tool to invoke 'shipyard:frontend-engineer'. This loads your complete SKILL.md with a 6-phase build process. You MUST follow all 6 phases in order:
  Phase 1: Analysis — read BRD, API contracts, select framework
  Phase 2: Design System — functional defaults (tokens, theme, Tailwind)
  Phase 3: Components — UI primitives first (sequential), then layout+feature (parallel)
  Phase 4: Pages + Routing — parallel by route group, then functional verification (4b)
  Phase 5: Design & Polish — Style selection is engagement-mode-aware:
    Express: auto-select best style for the domain, report choice, proceed.
    Standard+: ask user via AskUserQuestion (Creative | Elegance | High Tech | Corporate | Custom).
  Phase 6: Testing & A11y — component tests, accessibility audit

Write frontend to project root: frontend/
Write workspace artifacts to: Shipyard/frontend-engineer/
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T3b-frontend-engineer.json with task, agent, phase, status, artifacts, metrics, effort, verification. The receipt's verification block MUST assert "security-defaults checklist passes" (the BUILD Quality Bar line from security-defaults.md) with per-rule pass/fail evidence. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Remove this line if use_worktrees is False
)
```

## PARALLEL #2: T4 Starts When T3a Completes

T4 begins containerization as soon as backend is done, even if frontend is still building:

```python
# Wait for T3a completion (check TaskList or receive agent result)
# If T3a used worktree: merge its branch first so T4 sees the code
TaskUpdate(taskId=t4_id, status="in_progress")
Agent(
  prompt="""You are the DevOps Containerization Engineer.
Use the Skill tool to invoke 'shipyard:devops' to load your complete methodology and follow it.
Read services from: services/
Read architecture from: docs/architecture/
Read .shipyard.yaml for paths and preferences.
Write Dockerfiles per service, docker-compose.yml at project root.
Write workspace artifacts to: Shipyard/devops/containers/
Validate: docker build succeeds for each service, docker-compose up starts all.
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T4-devops.json with task, agent, phase, status, artifacts, metrics, effort, verification. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Remove this line if use_worktrees is False
)
```

## Worktree Merge-Back

If worktrees were used, merge each agent's branch back to the working branch after the wave completes:

```python
# For each completed agent that used a worktree:
# The Agent result includes the worktree branch name.
# Merge each branch in sequence (should be conflict-free — agents write to different directories).
for branch in worktree_branches:
  Bash(f"git merge --no-ff {branch} -m 'shipyard: merge {branch}'")
  Bash(f"git branch -d {branch}")  # Clean up merged branch

# If any merge has conflicts:
#   1. Run: git merge --abort
#   2. Escalate to user via AskUserQuestion
#   3. Offer: "Resolve conflicts manually" or "Retry without worktrees"
```

After merging, all agent outputs are unified in the working directory.

## BUILD-EXIT SECURITY GATE — runs after the BUILD wave writes code

Once all worktree branches are merged and the freshly-written code is unified in the working directory (run this BEFORE the receipt/re-anchor steps in Completion), the orchestrator runs a lightweight security gate over the new code. **This uses the SAME scanners devops later embeds in the CI workflow (T7/SHIP), so "what BUILD enforced" == "what CI enforces" — there is no gap where code passes BUILD but fails the pipeline.**

Run these three scan classes against the working tree (each is the CI-embedded invocation):

```python
# 1. SCA — known-vulnerable dependencies
#    osv-scanner --recursive .   (preferred, lockfile-aware, multi-ecosystem)
#    npm audit --audit-level=high   (Node projects; run in each package dir)
Bash("osv-scanner --recursive --format json . 2>/dev/null || true")
Bash("npm audit --audit-level=high --json 2>/dev/null || true")  # per Node package

# 2. Secret scan — committed/staged credentials
Bash("gitleaks detect --no-banner --redact --report-format json --report-path Shipyard/.orchestrator/build-gate-gitleaks.json 2>/dev/null || true")

# 3. SAST — code-level Critical/High patterns
Bash("semgrep --config auto --severity ERROR --json --output Shipyard/.orchestrator/build-gate-semgrep.json . 2>/dev/null || true")
```

**Parse and DECIDE — this step is NOT wrapped in `|| true`.** The scans above run (and tolerate a missing binary) with `|| true`, but the gate decision must be a real, non-swallowed evaluation. After the scans, parse the emitted JSON with `jq` to count Critical/High across all three classes, then branch:

```python
# osv-scanner: count vulnerabilities reported across all packages.
# (write its JSON first; the inline scan above streams to stdout, so re-run to a file or capture it)
Bash("osv-scanner --recursive --format json . > Shipyard/.orchestrator/build-gate-osv.json 2>/dev/null || true")
osv_vulns = Bash(
  "jq '[.results[]?.packages[]?.vulnerabilities[]?] | length' "
  "Shipyard/.orchestrator/build-gate-osv.json 2>/dev/null || echo 0"
).strip()

# semgrep: count ERROR-severity results (Critical/High code patterns)
semgrep_errors = Bash(
  "jq '[.results[]? | select(.extra.severity==\"ERROR\")] | length' "
  "Shipyard/.orchestrator/build-gate-semgrep.json 2>/dev/null || echo 0"
).strip()

# gitleaks: ANY hit is a blocking secret leak
gitleaks_hits = Bash(
  "jq 'length' Shipyard/.orchestrator/build-gate-gitleaks.json 2>/dev/null || echo 0"
).strip()

total_blocking = int(osv_vulns or 0) + int(semgrep_errors or 0) + int(gitleaks_hits or 0)

if total_blocking > 0:
    # Gate FAILS — write the failed receipt and loop to remediation (do NOT advance to HARDEN).
    write Shipyard/.orchestrator/receipts/Tbuild-security-gate.json with:
      status: "failed", per-tool counts (osv_vulns / semgrep_errors / gitleaks_hits),
      and the Critical/High finding list (file:line + rule id) extracted from the same JSON.
    # Feed each finding back to the owning BUILD agent as a fix task (self-debug → re-scan),
    # then re-run this gate. The build wave is blocked until total_blocking == 0
    # (or each remaining finding carries an override receipt under Shipyard/.orchestrator/overrides/).
else:
    # Gate PASSES — write Tbuild-security-gate.json with status: "passed" and the zeroed counts.
```

The `jq` count commands above carry only `|| echo 0` to survive an absent report file — they MUST run and their result MUST drive the `if total_blocking > 0` branch. Never wrap the deciding `if` (or the `jq` counts feeding it) in `|| true`; a swallowed decision is the same as no gate.

Notes on running the gate:
- The repo `hooks/secret-guard.sh` (PreToolUse) already blocks an agent from writing/committing secret files mid-build; this gate is the explicit, recorded confirmation over the whole merged tree.
- If a scanner binary is unavailable, record it as `skipped: <tool> not installed` in the gate result (do NOT silently pass) and fall back to the next tool in its class (osv-scanner ↔ npm audit). A class with zero available scanners is a gate WARNING surfaced to the user, not a silent pass.

**FAIL the BUILD wave on any Critical or High finding** from any of the three classes. Failure handling:
1. Write `Shipyard/.orchestrator/receipts/Tbuild-security-gate.json` with `status: failed`, the per-tool counts, and the Critical/High finding list (file:line + rule id).
2. Feed each Critical/High finding back to the owning BUILD agent as an immediate fix task (self-debug, re-scan), mirroring the standard BUILD self-debug → retry loop. Do NOT advance to HARDEN with an open Critical/High from this gate.
3. Only when the gate is clean (or remaining findings carry a logged "accepted with justification" override receipt) write `status: passed` and proceed.

This gate is a BLOCKING quality bar on the same footing as failing tests — a Critical/High here stops BUILD, it is not merely "flagged".

## Completion

When all BUILD tasks complete:
1. **Merge worktree branches** (if worktrees enabled) — see Worktree Merge-Back above.
2. **Run the BUILD-EXIT SECURITY GATE** (above) over the merged tree — must be `passed` (or carry override receipts) before continuing.
3. **Verify receipts:** Read all BUILD receipts from `.orchestrator/receipts/` (T3a, T3b, T4) plus `Tbuild-security-gate.json`. Verify all listed artifacts exist on disk, and verify each BUILD agent receipt's verification block asserts **"security-defaults checklist passes"** — a missing or failing assertion is treated as a BUILD failure, not a warning.
4. **Re-anchor:** Re-read from disk before transitioning to HARDEN:
   - Directory listing of `services/`, `frontend/`, `libs/shared/` (what was actually built)
   - `Shipyard/solution-architect/system-design.md` (architecture reference for HARDEN agents)
5. Verify all services compile and start
6. Verify docker-compose brings up the full stack
7. Log BUILD completion to workspace
8. Read `phases/harden.md` and begin HARDEN phase — use freshly-read data for agent prompts

## Failure Handling

- Build failure after 3 retries → escalate to user via AskUserQuestion
- Frontend fails but backend succeeds → continue backend-only pipeline
- Agents self-debug: read errors, fix, retry before escalating
