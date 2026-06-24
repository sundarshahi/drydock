# SHIP Phase — Dispatcher

This phase manages tasks T7 (DevOps IaC), T8 (Remediation), T9 (SRE), T10 (Data Scientist). Features PARALLEL #5 and #6.

## Visual Output

Print pipeline dashboard with SHIP ● active on phase start, then:

```
  → Starting SHIP phase
```

On PARALLEL #5 completion:
```
┌─ SHIP: Infra + Remediation COMPLETE ────── ⏱ {time} ─┐
│                                                        │
│  ✓ DevOps         {N} Terraform modules, {M} workflows │
│  ✓ Remediation    {N} Critical/{M} High fixed          │
│                                                        │
│  → Starting SRE + Data Scientist                       │
└────────────────────────────────────────────────────────┘
```

On PARALLEL #6 completion:
```
┌─ SHIP COMPLETE ───────────────────────────── ⏱ {time} ─┐
│                                                          │
│  ✓ SRE              {N} SLOs, {M} alerts, {K} runbooks  │
│  ✓ Data Scientist    {N} optimizations (or skipped)      │
│                                                          │
│  → Presenting Gate 3: Production Readiness               │
└──────────────────────────────────────────────────────────┘
```

## Authority Boundaries

- **devops** owns infrastructure provisioning, CI/CD, monitoring setup — does NOT define SLOs
- **sre** owns SLO/SLI definitions, error budgets, runbooks, chaos engineering — does NOT provision infrastructure
- See `Shipyard/.protocols/conflict-resolution.md`

## Re-Anchor

Before creating SHIP agent tasks, re-read key artifacts from disk:
- `Shipyard/security-engineer/findings/` (findings for remediation)
- `Shipyard/code-reviewer/findings/critical.md`, `high.md`
- `Shipyard/solution-architect/system-design.md` (architecture for infra)
- Directory listing of `services/`, `infrastructure/` (what exists)
- All HARDEN receipts from `.orchestrator/receipts/`

Use this freshly-read data when writing agent task prompts below.

## PARALLEL #5: T7 + T8

Read `Shipyard/.orchestrator/settings.md` to check if `Worktrees: enabled`. If enabled, add `isolation="worktree"` to each Agent call below.

```python
# T7: DevOps IaC + CI/CD
TaskUpdate(taskId=t7_id, status="in_progress")
Agent(
  prompt="""You are the DevOps Engineer — IaC and CI/CD.
Use the Skill tool to invoke 'shipyard:devops' to load your complete methodology and follow it.
Read architecture: docs/architecture/
Read implementation: services/, frontend/
Read .shipyard.yaml for paths and preferences.
Read protocols from: Shipyard/.protocols/
Generate: Terraform/Pulumi, K8s manifests (if microservices), CI/CD pipelines, monitoring dashboards.
Write to project root: infrastructure/, .github/workflows/
Write workspace artifacts to: Shipyard/devops/
DO NOT define SLOs — add placeholder: "SLO thresholds defined by SRE."
DO NOT write runbooks — SRE writes runbooks to docs/runbooks/.
Validate: terraform validate, pipeline syntax lint.
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T7-devops.json with task, agent, phase, status, artifacts, metrics, effort, verification. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Omit if Worktrees: disabled
)

# T8: Remediation (fix HARDEN findings)
TaskUpdate(taskId=t8_id, status="in_progress")
Agent(
  prompt="""You are the Remediation Engineer.
Read HARDEN findings from workspace: Shipyard/security-engineer/, code-reviewer/, qa-engineer/
Focus on Critical and High severity findings only.
For each finding:
  1. Read the affected file
  2. Apply the fix
  3. Run affected tests to verify no regressions
  4. Re-scan the affected code
If findings persist after 2 fix-rescan cycles → document and escalate.
Medium/Low findings: document but do not block.
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T8-remediation.json with task, agent, phase, status, artifacts (files modified), metrics (findings_fixed, findings_remaining), effort, verification. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Omit if Worktrees: disabled
)
```

## PARALLEL #6: T9 + T10 (after T7 + T8 complete)

```python
# T9: SRE — Production Readiness (SOLE SLO AUTHORITY)
TaskUpdate(taskId=t9_id, status="in_progress")
Agent(
  prompt="""You are the SRE — SOLE authority on SLO definitions, error budgets, runbooks, capacity planning.
Use the Skill tool to invoke 'shipyard:sre' to load your complete methodology and follow it.
Read all prior outputs: architecture, implementation, infrastructure, HARDEN findings.
Read protocols from: Shipyard/.protocols/
Perform production readiness review (checklist).
Define SLIs/SLOs per service, error budgets, burn-rate alerts.
Design chaos engineering scenarios and game-day playbook.
Write runbooks to project root: docs/runbooks/
Write workspace artifacts to: Shipyard/sre/
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T9-sre.json with task, agent, phase, status, artifacts, metrics, effort, verification. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Omit if Worktrees: disabled
)

# T10: Data Scientist (conditional — auto-detect LLM/ML usage)
# Scan imports for: openai, anthropic, langchain, transformers, torch, tensorflow
# If detected OR features.ai_ml is true:
TaskUpdate(taskId=t10_id, status="in_progress")
Agent(
  prompt="""You are the Data Scientist.
Use the Skill tool to invoke 'shipyard:data-scientist' to load your complete methodology and follow it.
Read implementation for LLM/ML usage patterns (imports, API calls, prompts).
Read protocols from: Shipyard/.protocols/
Optimize: prompt engineering, token usage, semantic caching, fallback chains.
Design: A/B testing infrastructure, experiment framework, data pipeline.
Write workspace artifacts to: Shipyard/data-scientist/
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T10-data-scientist.json with task, agent, phase, status, artifacts, metrics, effort, verification. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Omit if Worktrees: disabled
)
# If NOT detected AND features.ai_ml is false:
#   TaskUpdate(taskId=t10_id, status="completed")  # Skip
```

## Worktree Merge-Back

If worktrees were used, merge each SHIP agent's branch back after each parallel pair completes:

```python
# After PARALLEL #5 (T7 + T8):
for branch in ship_p5_worktree_branches:
  Bash(f"git merge --no-ff {branch} -m 'shipyard: merge {branch}'")
  Bash(f"git branch -d {branch}")

# After PARALLEL #6 (T9 + T10):
for branch in ship_p6_worktree_branches:
  Bash(f"git merge --no-ff {branch} -m 'shipyard: merge {branch}'")
  Bash(f"git branch -d {branch}")
# If merge conflicts: git merge --abort, escalate to user
```

## Receipt Verification Before Gate 3

After T9 (and T10 if applicable) completes:
1. **Verify all SHIP receipts:** Read `.orchestrator/receipts/T7-devops.json`, `T8-remediation.json`, `T9-sre.json`, `T10-data-scientist.json` (if applicable). Verify all listed artifacts exist.
2. **Verify remediation chain:** For each Critical/High finding from HARDEN, check that a remediation receipt AND a verification receipt exist. If any Critical finding lacks verification, flag before Gate 3.
3. **Aggregate metrics** from all receipts for Gate 3 display — use verified receipt data, not memory.

## Gate 3 — Production Readiness

After verification, present Gate 3 using the orchestrator's gate pattern.

On approval → read `phases/sustain.md` and begin SUSTAIN phase.
On "Fix issues first" → create additional remediation tasks.
