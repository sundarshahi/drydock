# HARDEN Phase — Dispatcher

This phase manages tasks T5 (QA), T6a (Security), T6b (Code Review). All three run in parallel (PARALLEL #3 and #4).

## Authority Boundaries — CRITICAL

Enforce these boundaries strictly:
- **security-engineer** is SOLE authority on OWASP Top 10, STRIDE, PII, encryption
- **code-reviewer** does architecture conformance, code quality, performance — does NOT perform security review
- **code-reviewer** is READ-ONLY — produces findings and patch files, does NOT modify source code
- See `Shipyard/.protocols/conflict-resolution.md` for full authority table

## Re-Anchor

Before creating HARDEN agent tasks, re-read key artifacts from disk:
- `Shipyard/solution-architect/system-design.md`
- `docs/architecture/adr/*.md` (Glob to list)
- Directory listing of `services/`, `frontend/`, `libs/shared/` (what BUILD actually produced)
- `Shipyard/.orchestrator/receipts/T3a-*.json`, `T3b-*.json` (BUILD receipts — what was built, metrics)

Use this freshly-read data when writing agent task prompts below.

## PARALLEL #3 + #4: T5 + T6a + T6b

All three start together:

Read `Shipyard/.orchestrator/settings.md` to check if `Worktrees: enabled`. If enabled, add `isolation="worktree"` to each Agent call below.

```python
# T5: QA Testing
TaskUpdate(taskId=t5_id, status="in_progress")
Agent(
  prompt="""You are the QA Engineer.
Use the Skill tool to invoke 'shipyard:qa-engineer' to load your complete methodology and follow it.
Read implementation: services/, frontend/ (if exists), api/
Read protocols from: Shipyard/.protocols/
Read .shipyard.yaml for paths.tests and paths.services.
Write tests to project root: tests/
Write workspace artifacts to: Shipyard/qa-engineer/
Run integration, e2e, and performance tests.
Distinguish test bugs (fix immediately) from implementation bugs (log as findings).
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T5-qa-engineer.json with task, agent, phase, status, artifacts, metrics, effort, verification. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Omit if Worktrees: disabled
)

# T6a: Security Audit (SOLE OWASP AUTHORITY)
TaskUpdate(taskId=t6a_id, status="in_progress")
Agent(
  prompt="""You are the Security Engineer — SOLE authority on OWASP, STRIDE, PII, encryption.
Use the Skill tool to invoke 'shipyard:security-engineer' to load your complete methodology and follow it.
No other skill performs security review. This is YOUR exclusive domain.
Read all implementation code: services/, frontend/, infrastructure/
Read protocols from: Shipyard/.protocols/
Perform STRIDE threat modeling + OWASP Top 10 (2025) audit + dependency scan.
Load and honor Shipyard/.protocols/grounding-protocol.md and Shipyard/.protocols/security-testing-protocol.md.
This is HARDEN (static) mode: run security phases 1-6 ONLY. Do NOT run phases 07-vapt-execution or 08-vapt-report here — live/active testing requires the explicit authorization gate enforced by the orchestrator's Pentest (VAPT) mode (it sets vapt_authorized after the gate).
Every finding must carry file:line evidence and the standards tag block (CVSS/CWE/OWASP 2025/WSTG/ASVS); no fabricated CVE/CVSS; tag every claim [verified]/[inferred]/[unverified].
Write findings to: Shipyard/security-engineer/
Auto-fix Critical/High issues with regression tests.
Document Medium/Low for remediation plan.
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T6a-security-engineer.json with task, agent, phase, status, artifacts, metrics, effort, verification. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Omit if Worktrees: disabled
)

# T6b: Code Review (NO OWASP — architecture + quality only)
TaskUpdate(taskId=t6b_id, status="in_progress")
Agent(
  prompt="""You are the Code Reviewer — architecture conformance and code quality ONLY.
Use the Skill tool to invoke 'shipyard:code-reviewer' to load your complete methodology and follow it.
DO NOT perform OWASP, STRIDE, or any security review — security-engineer is sole authority.
Cross-reference: "See security-engineer findings for security context."
Read architecture: docs/architecture/, api/
Read implementation: services/, frontend/
Read protocols from: Shipyard/.protocols/
Review: SOLID/DRY/KISS, performance, N+1 queries, resource leaks, test quality.
Write findings to: Shipyard/code-reviewer/
READ-ONLY: produce findings only, do NOT modify source code.
ADVERSARIAL STANCE: Your job is to find where this code breaks, not confirm it works. Assume every function has an edge case, every endpoint accepts bad input, every concurrent operation has a race condition. Hunt for the bugs the author can't see.
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T6b-code-reviewer.json with task, agent, phase, status, artifacts, metrics, effort, verification. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Omit if Worktrees: disabled
)
```

## Visual Output

Print pipeline dashboard with HARDEN ● active on phase start. Then print wave announcement:
```
┌─ HARDEN ─────────────────────────────── 3 agents ─┐
│                                                     │
│  T5   QA Engineer          implementing tests       │
│  T6a  Security Engineer    code audit + dep scan    │
│  T6b  Code Reviewer        arch + quality review    │
│                                                     │
│  All agents launched. Working autonomously...       │
└─────────────────────────────────────────────────────┘
```

## Worktree Merge-Back

If worktrees were used, merge each HARDEN agent's branch back after the wave completes:

```python
for branch in harden_worktree_branches:
  Bash(f"git merge --no-ff {branch} -m 'shipyard: merge {branch}'")
  Bash(f"git branch -d {branch}")
# If merge conflicts: git merge --abort, escalate to user
```

## Post-HARDEN: Receipt Verification & Remediation Preparation

After all HARDEN tasks complete:
1. **Verify receipts:** Read `.orchestrator/receipts/T5-qa-engineer.json`, `T6a-security-engineer.json`, `T6b-code-reviewer.json`. Verify all listed artifacts exist on disk.
2. Collect all findings from T5, T6a, T6b workspace folders
2. Deduplicate by file:line — keep highest severity rating
3. Filter Critical/High severity findings
4. If any Critical/High exist → T8 (Remediation in SHIP phase) receives the findings list
5. Medium/Low → documented but do not block pipeline
6. Print the checkmark cascade, then findings summary:
```
┌─ HARDEN COMPLETE ─────────────────────── ⏱ {time} ─┐
│                                                      │
│  ✓ QA Engineer          {N} tests, {M} passing       │
│  ✓ Security Engineer    {N} findings ({M} Crit/High) │
│  ✓ Code Reviewer        {N} findings ({M} Crit/High) │
│                                                      │
│  3/3 complete                                        │
└──────────────────────────────────────────────────────┘

━━━ Findings ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Critical   {N}    {top finding description}
                    {second finding if applicable}
  High       {N}    {summary}
  Medium     {N}    —
  Low        {N}    —
  ─────────────
  Total      {N}    deduplicated by file:line

  → {N} Critical/High items entering remediation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Handoff to SHIP

**Re-anchor:** Before transitioning, re-read from disk:
- `Shipyard/security-engineer/findings/` (what was found)
- `Shipyard/code-reviewer/findings/critical.md`, `high.md`
- `Shipyard/qa-engineer/` test results
- All HARDEN receipts from `.orchestrator/receipts/`

Read `phases/ship.md` and begin SHIP phase — use freshly-read findings data for remediation agent prompt.
