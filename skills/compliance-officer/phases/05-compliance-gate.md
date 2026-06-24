# Phase 5: Compliance Gate

## Objective

Render the compliance verdict. Verify that every MANDATORY in-scope control is present (status `Met` with a verified artifact). A mandatory control that is `Missing` is a **BLOCKING** finding that feeds the HARDEN remediation chain — exactly like a Critical security finding. The only ways to clear a block are: remediate to `Met`, or record an explicit **"accepted with justification"** override receipt. Generate outputs in `Shipyard/compliance-officer/gate/`, then write the skill receipt.

## Context Bridge

Read:
- `Shipyard/compliance-officer/evidence/control-evidence-map.md` (Phase 4) — the per-control status map.
- `Shipyard/compliance-officer/implementation/gaps.md` (Phase 3) — Partial/Missing findings + owning agents.
- `Shipyard/compliance-officer/control-matrix/` (Phase 2) — which controls are mandatory and their `[verified]`/`[unverified]` tags.

## Workflow

### Step 1: Verify Verification Integrity

A control may only drive a BLOCKING decision if its id is `[verified]` (confirmed live this session). Per `Shipyard/.protocols/compliance-protocol.md`, an `[unverified]` control id may NOT block — list it separately as "verify before gating" rather than blocking on an id that might be hallucinated. Confirm every mandatory control in the evidence map carries a `[verified]` id and a non-empty status.

### Step 2: Classify Each Mandatory Control

| Status | Gate effect |
|--------|-------------|
| **Met** (verified artifact) | Pass |
| **Partial** | BLOCKING (treat as not-yet-met) unless accepted with justification |
| **Missing** | **BLOCKING** finding |
| **N/A** (out of scope, reasoned) | Pass (recorded) |
| **Accepted** (missing but justified, override receipt exists) | Pass (with residual-risk note) |

A `Met` with an empty implementing-artifact field is invalid — downgrade to `Missing` and block.

### Step 3: Emit BLOCKING Findings → HARDEN Remediation

For every Missing/Partial mandatory control, emit a finding into the remediation chain (`Shipyard/.protocols/conflict-resolution.md`: findings → tasks → fix → re-verify). Each finding records:
- Control id (live-verified) + framework + the requirement.
- What is missing / incomplete.
- The owning agent who must implement it (security-engineer / devops / solution-architect / software-engineer — compliance-officer does NOT implement).
- The suggested implementing artifact + acceptance criteria for re-verification.

The orchestrator routes these like Critical/High findings; after fixes, re-run Phase 3 on the affected controls and re-verify to `Met` before the gate can pass.

### Step 4: Accepted-With-Justification Override (the only other exit)

When the user/owner consciously accepts a Missing mandatory control instead of remediating, record an explicit override — silent skips are forbidden. Use AskUserQuestion (predefined options, never open-ended) to capture the decision, then write an override receipt:

`Shipyard/.orchestrator/receipts/Tcomp-compliance-officer-accept-<controlid>.json`

```json
{
  "task": "Tcomp-accept",
  "agent": "compliance-officer",
  "phase": "HARDEN",
  "status": "complete",
  "artifacts": ["Shipyard/compliance-officer/gate/compliance-gate.md"],
  "metrics": { "control_accepted": 1 },
  "acceptance": {
    "control_id": "<live-verified id>",
    "framework": "<framework>",
    "accepted_by": "<who authorized>",
    "justification": "<why the risk is accepted>",
    "residual_risk": "<the exposure that remains>",
    "expiry": "<re-review date>"
  },
  "effort": { "files_read": 0, "files_written": 0, "tool_calls": 0 },
  "verification": "missing mandatory control consciously accepted with documented justification, residual risk, and expiry; not silently skipped"
}
```

An accepted control moves to status `Accepted` in the evidence map and stops blocking — but the residual risk and expiry are carried into the gate report.

### Step 5: Render the Gate Verdict

The gate is **PASS** only when every mandatory in-scope control is `Met`, `N/A`, or `Accepted`. Any Missing/Partial mandatory control with no override = **BLOCKED**. Write the verdict with counts and the blocking list.

### Step 6: Write the Skill Receipt (LAST action)

After all gate files exist and are verified on disk, write the completion receipt per `Shipyard/.protocols/receipt-protocol.md` to:

`Shipyard/.orchestrator/receipts/Tcomp-compliance-officer.json`

Populate the **TOP-LEVEL `compliance` object** — this is the gate evidence the orchestrator reads:

```json
"compliance": {
  "frameworks_in_scope": ["<slug>", "..."],
  "controls_required": 0,
  "controls_present": 0,
  "controls_missing": []
}
```

- `frameworks_in_scope` — `string[]` of the scoped framework slugs (Phase 1). NOT an int, and NOT inside `metrics`.
- `controls_required` / `controls_present` — ints: mandatory in-scope controls, and those at status `Met`/`N/A`/`Accepted`.
- `controls_missing` — `string[]` of the **live-verified ids** of every still-missing mandatory control (Missing/Partial with no override), MINUS any control id cleared by an accept-with-justification override receipt. This list is **EMPTY only when the verdict is PASS**; whenever it is non-empty the orchestrator BLOCKS production-ready. Never list an `[unverified]` id here (those are "verify before gating", not blockers).

Then populate `metrics` with the remaining real counts (`controls_total`, `controls_met`, `controls_accepted`, `control_ids_live_verified`) and `effort` with your actual `files_read`/`files_written`/`tool_calls`. Every path in `artifacts` MUST exist on disk. This is the ABSOLUTE LAST action before reporting completion.

## Output Deliverables

Write to `Shipyard/compliance-officer/gate/`:

| File | Contents |
|------|----------|
| `compliance-gate.md` | Verdict (PASS / BLOCKED), per-framework Met/Partial/Missing/Accepted counts, the BLOCKING list, and any accepted overrides with residual risk + expiry |
| `remediation-handoff.md` | The Missing/Partial mandatory controls formatted as remediation findings (control, gap, owning agent, acceptance criteria) |

Plus, in `Shipyard/.orchestrator/receipts/`: the completion receipt `Tcomp-compliance-officer.json` and any `Tcomp-compliance-officer-accept-<controlid>.json` override receipts.

## Validation

Before completing, verify:
- [ ] Every mandatory control has a final status; none left blank
- [ ] Every BLOCKED item is in `remediation-handoff.md` with an owning agent + acceptance criteria
- [ ] Every Accepted item has a matching override receipt with justification, residual risk, and expiry
- [ ] No `[unverified]` control id was used to block (those are listed as "verify before gating")
- [ ] The completion receipt exists and every artifact path in it resolves on disk

## Quality Bar

The gate is a real gate, not a summary. A Missing mandatory control either gets fixed (re-verified to `Met`) or gets a signed, justified, expiring acceptance — never a silent pass and never an invented "looks fine". The verdict is reproducible from the evidence map: an auditor reading the gate report can see exactly which control blocked, who owns the fix, or who accepted the risk and why. And the receipt is the proof the gate ran — no receipt, the gate did not happen.
