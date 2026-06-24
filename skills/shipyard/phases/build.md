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
Read protocols from: Shipyard/.protocols/
Read .shipyard.yaml for paths and preferences.
Write services to project root: services/, libs/shared/
Write workspace artifacts to: Shipyard/software-engineer/
TDD enforced: write test → watch fail → implement → watch pass → refactor.
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T3a-software-engineer.json with task, agent, phase, status, artifacts, metrics, effort, verification. Then mark your task as completed.""",
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
Read protocols from: Shipyard/.protocols/
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
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T3b-frontend-engineer.json with task, agent, phase, status, artifacts, metrics, effort, verification. Then mark your task as completed.""",
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

## Completion

When all BUILD tasks complete:
1. **Merge worktree branches** (if worktrees enabled) — see Worktree Merge-Back above.
2. **Verify receipts:** Read all BUILD receipts from `.orchestrator/receipts/` (T3a, T3b, T4). Verify all listed artifacts exist on disk.
3. **Re-anchor:** Re-read from disk before transitioning to HARDEN:
   - Directory listing of `services/`, `frontend/`, `libs/shared/` (what was actually built)
   - `Shipyard/solution-architect/system-design.md` (architecture reference for HARDEN agents)
3. Verify all services compile and start
4. Verify docker-compose brings up the full stack
5. Log BUILD completion to workspace
6. Read `phases/harden.md` and begin HARDEN phase — use freshly-read data for agent prompts

## Failure Handling

- Build failure after 3 retries → escalate to user via AskUserQuestion
- Frontend fails but backend succeeds → continue backend-only pipeline
- Agents self-debug: read errors, fix, retry before escalating
