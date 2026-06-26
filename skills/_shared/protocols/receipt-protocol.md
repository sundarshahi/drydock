# Receipt Protocol — Verifiable Gate Enforcement

**Core principle: Every completed task must have proof it actually ran. No receipt = not done.**

---

## Receipt Schema

Every agent writes a JSON receipt as its LAST action before `TaskUpdate(status="completed")`.

**File path:** `drydock/.orchestrator/receipts/{task_id}-{agent_name}.json`

**Required fields:**

```json
{
  "task": "T6b",
  "agent": "code-reviewer",
  "phase": "HARDEN",
  "status": "complete",
  "artifacts": [
    "drydock/code-reviewer/review-report.md",
    "drydock/code-reviewer/findings/critical.md",
    "drydock/code-reviewer/metrics/complexity.json"
  ],
  "metrics": {
    "findings_critical": 2,
    "findings_high": 5,
    "findings_medium": 12,
    "findings_low": 8,
    "tests_passing": 412,
    "tests_failing": 0,
    "coverage_lines": 87.4,
    "coverage_branches": 81.2,
    "mutation_score": 76.0,
    "patch_coverage": 92.5,
    "contract_can_i_deploy": true,
    "perf_baseline_regression": false
  },
  "compliance": {
    "frameworks_in_scope": ["SOC2", "GDPR"],
    "controls_required": 24,
    "controls_present": 24,
    "controls_missing": []
  },
  "effort": {
    "files_read": 47,
    "files_written": 6,
    "tool_calls": 83
  },
  "verification": "all 4 review phases executed, review-report.md written with executive summary"
}
```

**Field rules:**

| Field | Type | Rule |
|-------|------|------|
| `task` | string | Task ID from the orchestrator (T1, T2, T3a, etc.) |
| `agent` | string | Skill name (product-manager, software-engineer, etc.) |
| `phase` | string | Pipeline phase (DEFINE, BUILD, HARDEN, SHIP, LAUNCH, SUSTAIN) |
| `status` | string | Always `"complete"` — only write receipt on success |
| `artifacts` | string[] | Every file the agent created or modified. Each path MUST exist on disk at time of writing. |
| `metrics` | object | Key-value pairs with concrete numbers. At least one metric required. No empty objects. This object ALSO carries the machine-readable gate evidence the orchestrator VERIFIES rather than trusts — emit every gate field the task can measure directly inside `metrics`: `tests_passing` (int), `tests_failing` (int), `coverage_lines` (float %), `coverage_branches` (float %), `mutation_score` (float %), `patch_coverage` (float %), `contract_can_i_deploy` (bool), `perf_baseline_regression` (bool — true = regressed past budget). These gate fields are required on any task that runs tests, contracts, or perf checks. |
| `compliance` | object | Compliance gate evidence: `frameworks_in_scope` (string[]), `controls_required` (int), `controls_present` (int), `controls_missing` (string[] — control IDs with no evidence). Required on compliance-officer tasks and any task asserting a compliance control. An empty `controls_missing` array means all required controls are present. |
| `effort` | object | Tracking: `files_read` (int), `files_written` (int), `tool_calls` (int). Count your actual tool invocations during this task. |
| `verification` | string | One-line summary of what the agent checked to confirm its work is correct. |

---

## When to Write

Write the receipt as your ABSOLUTE LAST action, after all files are written and verified:

```
1. Do all your work (write files, run tests, generate reports)
2. Verify your outputs exist and are valid
3. Write receipt JSON to .orchestrator/receipts/
4. THEN call TaskUpdate(status="completed")
```

Never write the receipt before the work is done. Never skip the receipt.

---

## Remediation Chain

For findings that require remediation, the chain is:

1. **Finding receipt** — the agent that found the issue (security-engineer, code-reviewer, qa-engineer) writes its normal completion receipt listing findings
2. **Remediation receipt** — the remediation agent writes a receipt listing which findings were fixed and which files were modified
3. **Verification receipt** — the ORIGINAL finding agent re-scans and writes a verification receipt: `{task_id}-{agent_name}-verification.json`

All three must exist for a Critical/High finding to be considered resolved. The orchestrator checks this chain before Gate 3.

**Verification receipt schema:**

```json
{
  "task": "T6a-verify",
  "agent": "security-engineer",
  "phase": "SHIP",
  "status": "complete",
  "artifacts": [],
  "metrics": {
    "original_critical": 3,
    "remaining_critical": 0,
    "original_high": 5,
    "remaining_high": 1
  },
  "verification": "re-scanned all previously flagged files, 0 Critical remaining, 1 High accepted with justification"
}
```

---

## Orchestrator Verification

At every phase transition and before every gate, the orchestrator:

1. **Lists expected receipts** for the completed phase
2. **Reads each receipt** from `.orchestrator/receipts/`
3. **Verifies artifacts exist** — for each path in `receipt.artifacts`, confirm the file exists on disk
4. **If receipt missing** — the task did not complete properly. Investigate before proceeding.
5. **If artifacts missing** — the agent claimed to produce files it didn't. Investigate before proceeding.
6. **Extracts metrics** for gate ceremony display — users see verified data, not agent claims
7. **Reads the gate fields inside `metrics` and the top-level `compliance` object** to enforce gates from data, not prose. `production-ready` is BLOCKED when `metrics.tests_failing > 0`, `metrics.coverage_lines`/`metrics.coverage_branches`/`metrics.mutation_score`/`metrics.patch_coverage` are below budget, `metrics.perf_baseline_regression` is true, `metrics.contract_can_i_deploy` is false, `compliance.controls_missing` is non-empty, or an architecture-boundary violation is present — UNLESS a logged "accepted with justification" override receipt exists for that specific gate at `drydock/.orchestrator/overrides/<gate>-<id>.json`.

---

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| Writing receipt before work is done | Receipt is the LAST action, after all files verified |
| Empty `artifacts` array when files were created | List every file the agent produced |
| `"metrics": {}` | At least one concrete number in metrics |
| `"verification": "done"` | Describe what was actually verified |
| Skipping receipt because "it's a small task" | Every task gets a receipt, regardless of size |
| Writing receipt but not checking artifacts exist | Verify each artifact path before writing receipt |
| `"effort": {}` or missing effort field | Count files_read, files_written, tool_calls from your actual work |
