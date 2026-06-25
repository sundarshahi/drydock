# Strategic Gates

### Strategic Gates (3 total)

**Gate 1 — Requirements Approval (BRD)** (after T1):

Print the pipeline dashboard (DEFINE ● active), then the gate ceremony:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⬥ GATE 1 — Requirements Approval                  ⏱ {elapsed}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  User Stories       {N} with acceptance criteria
  Stakeholders       {N} roles identified
  Constraints        {key constraints summary}
  Scope              {brief scope summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Receipt verification before gate:**
Read `drydock/.orchestrator/receipts/T1-product-manager.json`. Verify all `artifacts` exist on disk. If receipt missing or artifacts missing, investigate before opening gate. Use receipt `metrics` for the numbers displayed above.

Then ask:
```python
AskUserQuestion(questions=[{
  "question": "BRD complete: [X] user stories, [Y] acceptance criteria. Approve?",
  "header": "Gate 1: Requirements",
  "options": [
    {"label": "Approve — start architecture (Recommended)", "description": "BRD locked, proceed to Solution Architect"},
    {"label": "Show BRD details", "description": "Display the full BRD before deciding"},
    {"label": "I have changes", "description": "Request modifications to requirements"},
    {"label": "Chat about this", "description": "Free-form input about the BRD"}
  ],
  "multiSelect": false
}])
```

**Gate 2 — Architecture Approval** (after T2):

Print the pipeline dashboard (DEFINE ✓ complete), then the gate ceremony:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⬥ GATE 2 — Architecture Approval                  ⏱ {elapsed}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Pattern      {architecture pattern}
  Stack        {language} · {framework} · {database} · {cache}
  Services     {N} bounded contexts
  API          {N} endpoints across {M} specs
  ADRs         {N} architecture decision records
  Data         {N} entities, {M} migrations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Receipt verification before gate:**
Read `drydock/.orchestrator/receipts/T2-solution-architect.json`. Verify all `artifacts` exist on disk (ADRs, API specs, system design). If receipt missing or artifacts missing, investigate before opening gate. Use receipt `metrics` for the numbers displayed above.

Then ask:
```python
AskUserQuestion(questions=[{
  "question": "Architecture complete: [tech stack summary]. Approve to start building?",
  "header": "Gate 2: Architecture",
  "options": [
    {"label": "Approve — start building (Recommended)", "description": "Architecture locked, begin autonomous BUILD phase"},
    {"label": "Show architecture details", "description": "Walk through ADRs, diagrams, and API spec"},
    {"label": "Rework architecture", "description": "Send concerns back to Architect for revision"},
    {"label": "Chat about this", "description": "Free-form input about the architecture"}
  ],
  "multiSelect": false
}])
```

**Rework loop (Gate 2):**

If user selects "Rework architecture":
1. Ask what concerns they have (AskUserQuestion with common architecture concerns + free-form)
2. Track rework cycle: read `drydock/.orchestrator/rework-log.md`, increment Gate 2 rework count
3. If rework count < 2: Re-invoke Solution Architect with the user's concerns as additional constraints. The architect re-reads its own previous output, applies the feedback, and produces updated artifacts.
4. If rework count >= 2: Escalate — "Architecture has been revised twice. Approve current state or discuss further?"
5. After rework: re-verify receipts, re-present Gate 2

Print rework indicator in the gate ceremony:
```
  ⬥ GATE 2 — Architecture Approval (Rework {N}/2)        ⏱ {elapsed}
```

Write each rework cycle to `drydock/.orchestrator/rework-log.md`:
```markdown
## Gate 2 — Rework {N}
Concerns: {user's feedback}
Changes: {what the architect modified}
```

**Gate 3 — Production Readiness** (after T9):

Print the pipeline dashboard (DEFINE ✓, BUILD ✓, HARDEN ✓, SHIP ✓ complete), then the gate ceremony:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⬥ GATE 3 — Production Readiness                   ⏱ {elapsed}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Services     {N} built, all compiling
  Tests        {tests_passing} passing, {tests_failing} failing
  Coverage     {coverage_lines}% lines · {coverage_branches}% branches · mutation {mutation_score}% · patch {patch_coverage}%
  Performance  CWV {lcp}/{inp}/{cls} · p95 {p95}ms vs budget (performance-budget.yaml) — {within|REGRESSION}
  Security     {N} findings → {M} Critical, {K} High remaining
  Compliance   {present}/{total} mandatory controls present ({missing} missing) · frameworks: {list}
  Architecture {boundary_violations} boundary violations
  Infra        {N} Dockerfiles, {M} Terraform modules
  CI/CD        {N} workflows configured
  SRE          {N} SLOs, {M} alerts, {K} runbooks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Receipt verification before gate — RE-DERIVE, don't trust self-reports:**

Do NOT take the agents' self-reported `metrics` at face value. Independently re-derive the gate metrics from the build's ground-truth artifacts:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/drydock/scripts/verify-gate.py" 2>/dev/null \
  || python3 "${CLAUDE_SKILL_DIR}/scripts/verify-gate.py"
```
It reads ALL receipts, verifies each receipt's claimed `artifacts` exist on disk, and re-derives **tests** (from JUnit XML) and **coverage** (from Istanbul `coverage-summary.json` / Cobertura `coverage.xml` / `lcov.info`), returning JSON:
- `tests` / `coverage` each carry `{claimed_*, derived_*, source, status}` where `status` is `verified` (derived matches the receipt), `mismatch` (derived CONTRADICTS the receipt), or `unverified` (no parseable artifact found).
- `artifacts.missing` — claimed artifacts absent from disk.
- `discrepancies` — human-readable list; `trustworthy` — false if any mismatch or missing artifact.

Apply it as follows:
- Use the **derived** value as the gate input wherever `status == verified` or `mismatch` (ground truth wins over the receipt).
- A `mismatch` (a receipt that overstates pass count or coverage) is itself a **BLOCKING breach** — the build is not production-ready until the code is fixed so the artifacts agree, or an override receipt is logged. Surface the discrepancy verbatim.
- Where `status == unverified` (no JUnit/coverage artifact emitted), fall back to the receipt's self-reported value but render it tagged `[unverified]` in the gate summary so the user knows it wasn't independently confirmed.
- Still verify, from the receipts, the fields the script does not re-derive — `metrics.mutation_score`, `metrics.patch_coverage`, `metrics.contract_can_i_deploy`, `metrics.perf_baseline_regression`, and the compliance controls-present/missing status from the top-level `compliance` object (`compliance.controls_present`, `compliance.controls_missing`).
- For Critical/High findings: verify the remediation chain is complete (finding receipt + remediation receipt + verification receipt).
- If `verify-gate.py` reports `trustworthy: false`, any receipt is missing, or any Critical finding lacks a verification receipt → flag to the user before opening the gate.

**Production-readiness gate evaluation (BLOCKING):**
Evaluate against the RE-DERIVED metrics from `verify-gate.py` first, then the receipt-only fields above (there is NO separate `gate_metrics` object). A build may only be offered "production ready" when ALL of these are green:
- **Tests** — re-derived `tests.derived_failing == 0` and `tests.derived_passing > 0`, and `tests.status != "mismatch"` (a self-report that contradicts the JUnit artifact is a breach)
- **Coverage** — re-derived `coverage.derived_lines` (and `metrics.coverage_branches`/`metrics.patch_coverage` for changed lines) meet the project threshold with `coverage.status != "mismatch"`; `metrics.mutation_score` meets the mutation threshold (mutation + property tests are default-on)
- **Performance** — `metrics.perf_baseline_regression == false` and `metrics.contract_can_i_deploy == true`; Core Web Vitals and p95 are within `performance-budget.yaml`
- **Compliance** — every mandatory control for each in-scope framework is present (`compliance.controls_missing` is empty / count == 0)
- **Architecture boundary** — no boundary violations (per `architecture-boundaries.md`)

If ANY of these breaches, the "Ship it — production ready" option is BLOCKED **unless** a logged `accepted with justification` override receipt exists for that specific breach at `drydock/.orchestrator/overrides/<gate>-<id>.json`. The override receipt schema:
```json
{
  "gate": "coverage | perf | compliance | architecture | tests",
  "id": "<short slug of the breached check>",
  "status": "accepted with justification",
  "justification": "<user-provided reason>",
  "metrics_at_override": { "...": "the failing metric values" },
  "accepted_by": "<user>",
  "timestamp": "<ISO 8601>"
}
```
When a gate is breached, do NOT silently offer "Ship it". Instead present the breach and offer either "Rework — fix issues first" or "Accept with justification" (which writes the override receipt to `drydock/.orchestrator/overrides/<gate>-<id>.json` and only then unblocks "Ship it" for that breach). Each independent breach requires its own override receipt.

Then ask:
```python
AskUserQuestion(questions=[{
  "question": "All phases complete. [summary]. Ship it?",
  "header": "Gate 3: Production Readiness",
  "options": [
    # "Ship it" is offered as Recommended ONLY when tests/coverage/perf/compliance/architecture are all green
    # (or every breach already has a logged override receipt). If any gate is breached, OMIT this option until
    # the breach is reworked or accepted with justification.
    {"label": "Ship it — production ready (Recommended)", "description": "Finalize assembly and deploy"},
    {"label": "Show full report", "description": "Display complete pipeline summary"},
    {"label": "Rework — fix issues first", "description": "Run remediation cycle, then re-verify"},
    {"label": "Accept with justification", "description": "Log an 'accepted with justification' override receipt for a breached gate (tests/coverage/perf/compliance/architecture), then allow shipping that breach"},
    {"label": "Chat about this", "description": "Free-form input about production readiness"}
  ],
  "multiSelect": false
}])
```

If the user selects **"Accept with justification"**, ask which breached gate(s) they are accepting and capture a justification, then write an override receipt to `drydock/.orchestrator/overrides/<gate>-<id>.json` (schema above) for each. Only after the override receipt(s) exist may "Ship it — production ready" be offered for those breaches.

**Rework loop (Gate 3):**

If user selects "Rework — fix issues first":
1. Track rework cycle in `drydock/.orchestrator/rework-log.md`, increment Gate 3 rework count
2. If rework count < 2:
   a. Create a new remediation task targeting the remaining Critical/High findings
   b. After remediation completes, re-run verification (original finding agents re-scan affected files)
   c. Re-verify all receipts and remediation chains
   d. Re-present Gate 3 with updated metrics
3. If rework count >= 2: Escalate — "Pipeline has been through 2 remediation cycles. {N} findings remain. Ship with known issues or discuss further?"
4. Show rework indicator: `⬥ GATE 3 — Production Readiness (Rework {N}/2)`

The rework loop is self-healing: instead of stopping the pipeline on rejection, it feeds the user's concerns back into the relevant agents, re-verifies, and re-presents the gate. Max 2 cycles prevents infinite loops.
