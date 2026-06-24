# HARDEN Phase — Dispatcher

This phase manages tasks T5 (QA), T6a (Security), T6b (Code Review), and T6e (Compliance). All four run in parallel (PARALLEL #3 and #4).

## Authority Boundaries — CRITICAL

Enforce these boundaries strictly:
- **security-engineer** is SOLE authority on OWASP Top 10, STRIDE, PII, encryption
- **code-reviewer** does architecture conformance, code quality, performance — does NOT perform security review
- **code-reviewer** is READ-ONLY — produces findings and patch files, does NOT modify source code
- **compliance-officer** is SOLE authority on per-framework regulatory scoping and the control-evidence map (HIPAA/PCI-DSS/GDPR/SOC 2/etc.) — it CONSUMES the security-engineer's PII inventory + encryption audit and does NOT redo them, and does NOT perform the OWASP/STRIDE audit
- See `Shipyard/.protocols/conflict-resolution.md` for full authority table and `Shipyard/.protocols/compliance-protocol.md` for the compliance scoping/evidence contract

## Re-Anchor

Before creating HARDEN agent tasks, re-read key artifacts from disk:
- `Shipyard/solution-architect/system-design.md`
- `docs/architecture/adr/*.md` (Glob to list)
- Directory listing of `services/`, `frontend/`, `libs/shared/` (what BUILD actually produced)
- `Shipyard/.orchestrator/receipts/T3a-*.json`, `T3b-*.json` (BUILD receipts — what was built, metrics)

Use this freshly-read data when writing agent task prompts below.

## PARALLEL #3 + #4: T5 + T6a + T6b + T6e

All four start together:

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
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/T5-qa-engineer.json with task, agent, phase, status, artifacts, metrics, effort, verification. The receipt's `metrics` object MUST include these gate fields, every value taken from REAL tool output (test runner, coverage tool, mutation tool, contract check, perf runner) — never estimated or recalled: `tests_passing` (int), `tests_failing` (int), `coverage_lines` (float %), `coverage_branches` (float %), `mutation_score` (float %), `patch_coverage` (float %), `perf_baseline_regression` (bool — true if node tests/performance/compare-baseline.js shows a p95/error-rate regression past budget), `contract_can_i_deploy` (bool). These mirror Gate 3's required keys; the orchestrator reads them as `metrics.*` to enforce production-readiness, so a missing or fabricated field blocks the gate. Then mark your task as completed.""",
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

# T6e: Compliance (SOLE authority on regulatory scoping + control-evidence map)
TaskUpdate(taskId=t6e_id, status="in_progress")
Agent(
  prompt="""You are the Compliance Officer — SOLE authority on per-framework regulatory scoping and the control-evidence map.
Use the Skill tool to invoke 'shipyard:compliance-officer' to load your complete methodology and follow it.
You do NOT perform the OWASP/STRIDE audit (security-engineer owns it) and you do NOT redo the PII inventory or encryption audit — you CONSUME them.
Read protocols from: Shipyard/.protocols/ — load and honor Shipyard/.protocols/compliance-protocol.md and Shipyard/.protocols/grounding-protocol.md.
Read product signals: Shipyard/product-manager/BRD/ (compliance-discovery answers), .shipyard.yaml `compliance:` block, Shipyard/solution-architect/ (compliance scoping).
Read security-engineer outputs: Shipyard/security-engineer/ (PII inventory + encryption audit) — consume, do not redo.
Read implementation: services/, frontend/, infrastructure/.
Scope frameworks deterministically from product signals (HIPAA/PCI-DSS/GDPR/CCPA/SOC 2/ISO 27001/FedRAMP per the protocol's map); VERIFY every control ID / article number / requirement text live against the official source this session — never recall from memory; tag every claim [verified]/[inferred]/[unverified].
Produce the control-evidence map: for each scoped mandatory control, mark present / missing with file:line or artifact evidence.
Write findings + control-evidence map to: Shipyard/compliance-officer/.
A missing MANDATORY control is a BLOCKING finding (feeds T8 remediation) — do not soft-flag it.
When complete, write a receipt JSON to Shipyard/.orchestrator/receipts/Tcomp-compliance-officer.json with task, agent, phase, status, artifacts, metrics (including the controls-present/controls-missing status), effort, verification. Then mark your task as completed.""",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True,
  isolation="worktree"  # Omit if Worktrees: disabled
)
```

## Visual Output

Print pipeline dashboard with HARDEN ● active on phase start. Then print wave announcement:
```
┌─ HARDEN ─────────────────────────────── 4 agents ─┐
│                                                     │
│  T5   QA Engineer          implementing tests       │
│  T6a  Security Engineer    code audit + dep scan    │
│  T6b  Code Reviewer        arch + quality review    │
│  T6e  Compliance Officer   framework scope + evidence│
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
1. **Verify receipts:** Read `.orchestrator/receipts/T5-qa-engineer.json`, `T6a-security-engineer.json`, `T6b-code-reviewer.json`, `Tcomp-compliance-officer.json`. Verify all listed artifacts exist on disk.
2. **Read the gate/metric fields from receipts** (not memory) when collecting findings:
   - From T5 (and any contract/perf receipts): `tests_passing`, `tests_failing`, `coverage_lines`, `coverage_branches`, `mutation_score`, `patch_coverage`, `contract_can_i_deploy`, `perf_baseline_regression`.
   - From Tcomp: the compliance controls-present / controls-missing status.
3. Collect all findings from T5, T6a, T6b, T6e workspace folders.

### UNIFIED BLOCKING GATES — all feed T8 remediation, mirroring security Critical/High

Security Critical/High findings have always flowed into T8 remediation. Apply the SAME treatment to every gate below — each condition is a **BLOCKING finding** that produces a remediation task, not a soft "flag to the user":

| Source | BLOCKING condition (→ T8 remediation task) |
|--------|---------------------------------------------|
| **Security (T6a)** | Any Critical or High OWASP/STRIDE finding |
| **Tests (T5)** | `tests_failing > 0` — **any** failing test is a remediation task (replaces the old "QA failures > 20% → flag to user" rule; there is no percentage tolerance) |
| **Coverage (T5)** | `coverage_lines` or `coverage_branches` below the configured threshold; `patch_coverage` below threshold |
| **Performance (T5/perf)** | `perf_baseline_regression` shows p95 latency or error-rate regression beyond the configured tolerance (per `observability-contract.md` RED metrics) |
| **Compliance (T6e)** | Any MISSING mandatory control in the Tcomp control-evidence map |
| **Architecture (T6b)** | Any HIGH-severity architecture-boundary violation (inward-dependency / domain-purity breach per `architecture-boundaries.md`) |

Process:
4. Deduplicate findings by file:line — keep highest severity rating.
5. Treat all BLOCKING conditions above as the blocking set (Critical/High security findings UNION any failing test, sub-threshold coverage, perf regression, missing mandatory compliance control, and HIGH architecture-boundary violation).
6. If the blocking set is non-empty → T8 (Remediation in SHIP phase) receives the full blocking-finding list. The pipeline does not reach Gate 3 "production-ready" while any blocking finding is open (a blocking finding may only be cleared by remediation, or by a logged "accepted with justification" override receipt).
7. Medium/Low severity, non-mandatory compliance gaps, and coverage above threshold → documented but do not block.
8. Print the checkmark cascade, then findings summary:
```
┌─ HARDEN COMPLETE ─────────────────────── ⏱ {time} ─┐
│                                                      │
│  ✓ QA Engineer          {N} tests, {M} passing       │
│  ✓ Security Engineer    {N} findings ({M} Crit/High) │
│  ✓ Code Reviewer        {N} findings ({M} Crit/High) │
│  ✓ Compliance Officer   {N} scoped, {M} controls missing│
│                                                      │
│  4/4 complete                                        │
└──────────────────────────────────────────────────────┘

━━━ Findings ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Critical   {N}    {top finding description}
                    {second finding if applicable}
  High       {N}    {summary}
  Medium     {N}    —
  Low        {N}    —
  ─────────────
  Blocking gates:
    Tests failing      {tests_failing}
    Coverage           {coverage_lines}% lines / {coverage_branches}% branches (threshold {T}%)
    Perf regression    {perf_baseline_regression}
    Compliance missing {M} mandatory controls
    Arch boundary HIGH {N} violations
  ─────────────
  Total      {N}    deduplicated by file:line

  → {N} BLOCKING items entering remediation (security Crit/High + failing tests + sub-threshold coverage + perf regression + missing mandatory controls + HIGH arch-boundary)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Handoff to SHIP

**Re-anchor:** Before transitioning, re-read from disk:
- `Shipyard/security-engineer/findings/` (what was found)
- `Shipyard/code-reviewer/findings/critical.md`, `high.md` (including HIGH architecture-boundary violations)
- `Shipyard/qa-engineer/` test results (failing tests, coverage, perf regression)
- `Shipyard/compliance-officer/` control-evidence map (missing mandatory controls)
- All HARDEN receipts from `.orchestrator/receipts/` (T5, T6a, T6b, Tcomp) — including their gate/metric fields

Read `phases/ship.md` and begin SHIP phase — use freshly-read findings data for remediation agent prompt.
