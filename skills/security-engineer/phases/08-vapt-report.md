# Phase 8: VAPT Report

## Objective

Aggregate every finding from the full engagement -- Phases 1-6 (threat model, code audit, auth, data, supply-chain analysis, and remediation planning) and Phase 7 (live VAPT execution evidence) -- into a single professional, client-deliverable penetration test report at `Shipyard/security-engineer/report/vapt-report.md`. The report assembles the seven industry-standard sections: Engagement Scope & Rules of Engagement, Methodology, Executive Summary, a CVSS-backed Risk Rating Matrix, Per-Finding Writeups with the full standards tag block and retest status, Confirmed vs Needs-Verification buckets, and an Appendix. This phase produces no new testing -- it assembles, scores, and presents evidence already captured. Honor `grounding-protocol.md` (no fabricated CVE/CVSS; tag every claim) and `security-testing-protocol.md` (CVSS discipline; Confirmed vs Needs-Verification separation).

## Context Bridge

Read ALL prior phase outputs as the source material -- do not re-analyze or re-test, only aggregate and present:

- `Shipyard/security-engineer/threat-model/` (Phase 1 -- attack surface, STRIDE)
- `Shipyard/security-engineer/code-audit/` (Phase 2 -- OWASP Web/API/LLM findings with `file:line`)
- `Shipyard/security-engineer/auth-review/` (Phase 3)
- `Shipyard/security-engineer/data-security/` (Phase 4)
- `Shipyard/security-engineer/supply-chain/` (Phase 5 -- SBOM, dependency CVEs)
- `Shipyard/security-engineer/remediation/` (Phase 6 -- finding inventory, fixes, timeline)
- `Shipyard/security-engineer/vapt/` (Phase 7 -- executed results, captured request/response evidence + PoCs, PASS/FAIL/INCONCLUSIVE matrix, `authorization-receipt.json`)

The static findings tell you WHAT was suspected; the Phase 7 execution evidence tells you what was CONFIRMED. A static finding without an execution reproduction stays in the Needs-Verification bucket and never carries Critical/High as if confirmed.

## Inputs

- Phase 7 VAPT execution -- `Shipyard/security-engineer/vapt/results.md`, `vapt/evidence/<scenario>.md`, `vapt/scan-output/*.sarif`, `vapt/authorization-receipt.json`
- Phase 6 remediation plan -- `Shipyard/security-engineer/remediation/` (unified finding IDs, prioritization, fixes)
- Phases 1-5 reports -- the per-phase output directories listed above
- Authorization receipt -- `Shipyard/.orchestrator/receipts/` (authorization reference, scope allowlist, RoE, testing window)
- Standards references -- the `## Standards References` section of `skills/security-engineer/SKILL.md` (OWASP Web 2025 / API 2023 / LLM 2025 ids, ASVS 5.0.0 levels, WSTG v4.2 ids, CVSS 4.0 policy)

## Workflow

### Step 1: Assemble Engagement Scope & Rules of Engagement (Section 1)

Open `vapt/authorization-receipt.json` and the authorization receipt in `Shipyard/.orchestrator/receipts/`. Reproduce verbatim, not from memory:

- Authorized target allowlist (hosts / domains / IPs / API base URLs that were in scope)
- Out-of-scope assets explicitly excluded
- Testing window (start/end of the authorized period)
- Authorization reference (the receipt id) and the authorizing party
- Rules of engagement constraints honored (no DoS, no destructive payloads, no production data, local/authorized-staging only)

If the authorization receipt is missing or unverifiable, state that explicitly and mark the engagement scope `[unverified]` -- do not invent an allowlist.

### Step 2: Write the Methodology (Section 2)

Document the methodology actually followed and the standards basis. State the recon -> enum -> scan -> exploit/PoC -> retest progression. List the tools that were actually run (link the Appendix for exact versions + invocations -- do not restate full invocations here). State the standards basis using the verified ids/versions exactly as written in the SKILL.md `## Standards References` section:

- OWASP Top 10 -- 2025 edition (Web)
- OWASP API Security Top 10 -- 2023 edition
- OWASP Top 10 for LLM Applications -- 2025 (v2.0) (only if LLM/ML code was in scope)
- OWASP ASVS 5.0.0 (state the target Level: L1 / L2 / L3)
- OWASP WSTG v4.2
- CVSS 4.0 (with 3.1 retained where an advisory provides it)

Do not "correct" any of these ids/versions from memory -- they are the verified source of truth.

### Step 3: Write the Executive Summary (Section 3)

Produce a stakeholder-readable summary (no jargon, no `file:line`):

- Overall risk posture in plain business language
- Counts by severity (Critical / High / Medium / Low / Informational)
- Top risks expressed as business impact (what an attacker could do, to whom, at what cost)
- A one-line confirmed-vs-suspected framing (e.g. "N findings confirmed by live reproduction; M leads require further verification")

Severity counts here MUST reconcile exactly with the Risk Rating Matrix (Step 4). Re-derive counts from the actual finding list; never round from memory.

### Step 4: Build the Risk Rating Matrix (Section 4, CVSS-backed)

Tabulate every finding with severity DERIVED FROM the CVSS 4.0 base score (compute from the vector showing each metric, or retrieve and cite the official advisory score). Provide the 3.1 score alongside where the advisory supplies it. Pair the base score with EPSS and CISA KEV context where known -- never rate on base score alone, and never compare scores across CVSS versions.

| Finding ID | Title | Severity | CVSS 4.0 | CVSS 3.1 | EPSS / KEV | Confirmed? |
|------------|-------|----------|----------|----------|------------|------------|

- `Severity` is the human-readable rollup of the CVSS 4.0 base score, not a hand-picked label.
- `Confirmed?` = Yes only if there is a reachable code path + a live reproduction from Phase 7. Otherwise it belongs in Needs-Verification (Step 6) and cannot show Critical/High here.
- Leave a CVSS cell `not verified` rather than inventing a score. A Needs-Verification finding shows no CVE/CVSS as if confirmed.

### Step 5: Write Per-Finding Writeups (Section 5)

For EVERY finding, produce a writeup. Each MUST carry the full standards tag block. Use the verified id formats from SKILL.md `## Standards References`; where a precise WSTG or ASVS id cannot be retrieved, mark it `[unverified]` and do not invent one.

```markdown
## [SEVERITY] SEC-XXX: Finding Title

**Affected asset:** <host / URL / service / `file:line`>
**Status:** Confirmed (reproduced) | Needs-Verification (lead only)

### Standards Tags
- CVSS: <4.0 vector> -> <base score>  (and 3.1 vector+score if available)
- CWE: CWE-<n>
- OWASP: <A0x:2025 | APIx:2023 | LLMx:2025>
- WSTG: WSTG-v42-<CAT>-<nn>
- ASVS: v5.0.0-<chapter>.<section>.<req> (Level <1|2|3>)

### Reproduction
<the literal request/input -> the path it travels -> the observable effect>

### Evidence
<request/response excerpt and/or source->sink `file:line`, citing the Phase 7
 evidence file or static report it came from>

### Remediation
<fix guidance; recommend ONLY real, retrieved fixed versions/packages --
 if no fixed version exists, say so>

### Retest Status
Fixed | Still Vulnerable | Risk Accepted | Not Retested
```

Requirements for every writeup:
- The standards tag block is mandatory and complete. A missing tag is left `[unverified]`, never invented.
- CVSS is either a vector you computed (each metric shown) or an official advisory score you retrieved and cited -- never a recalled or "≈" number.
- CVE identifiers may appear ONLY if retrieved this session from an authoritative source (NVD/MITRE/GHSA/vendor) AND matched to the actual dependency+version in the manifest/lockfile.
- Remediation references real, retrieved fixed versions/packages only -- never an invented "fixed in x.y.z".
- Retest status is present on EVERY Critical and High finding (Fixed / Still Vulnerable / Risk Accepted / Not Retested).
- Critical/High requires a live reproduction from Phase 7; a finding with no reproduction is downgraded and labeled unconfirmed.

### Step 6: Separate Confirmed vs Needs-Verification (Section 6)

Sort every finding into two clearly labeled buckets:

- **Confirmed** -- reachable code path + live reproduction + cited evidence. These may carry their full CVSS/CVE and Critical/High severity.
- **Needs-Verification** -- a lead only (e.g. an unverified scanner candidate, a static suspicion with no traced path). A Needs-Verification item NEVER carries Critical/High and NEVER presents a CVE/CVSS as if confirmed. State why it could not be confirmed (retrieval failure, unreachable path, input not user-controlled, no testing window for it).

### Step 7: Assemble the Appendix (Section 7)

- References to raw SARIF / scanner output (`vapt/scan-output/*.sarif`) -- by path, not pasted in full.
- Tool versions and the exact invocations used (the verbatim invocations from Phase 7's tool table).
- **Calibration summary** -- counts by confidence tag across the whole report (e.g. `18 [verified], 4 [inferred], 2 [unverified]`), per `grounding-protocol.md`.
- The [UNVERIFIED] flags carried from the standards basis (e.g. WSTG non-INFO ids, ASVS requirement ids pulled at use time; the CVSS 4.0-vs-3.1 base-score-trend debate -- do not assert a direction).

## Output Deliverables

Write the report to `Shipyard/security-engineer/report/`:

| File | Contents |
|------|----------|
| `report/vapt-report.md` | Professional VAPT report: (1) Engagement Scope & RoE, (2) Methodology + standards basis, (3) Executive Summary, (4) CVSS-backed Risk Rating Matrix, (5) Per-Finding Writeups with full standards tag block + retest status, (6) Confirmed vs Needs-Verification buckets, (7) Appendix with tool versions/invocations + calibration summary |

## Validation

Before delivering the report, verify:
- [ ] Every finding carries the full standards tag block (CVSS 4.0 vector+score, CWE id, OWASP id, WSTG id, ASVS req+level)
- [ ] No fabricated CVE/CVSS -- each score is retrieved-and-cited or computed-from-vector; no recalled or "≈" values
- [ ] Severity for every finding is derived from the CVSS 4.0 base score, not hand-picked
- [ ] Retest status (Fixed / Still Vulnerable / Risk Accepted / Not Retested) is present on every Critical and High finding
- [ ] Confirmed and Needs-Verification buckets are separated; no Needs-Verification item carries Critical/High or a CVE/CVSS as confirmed
- [ ] Engagement scope, allowlist, window, and authorization reference match the receipt verbatim (not from memory)
- [ ] Executive Summary severity counts reconcile exactly with the Risk Rating Matrix
- [ ] Calibration summary (counts by `[verified]` / `[inferred]` / `[unverified]`) is included in the Appendix

## Quality Bar

A VAPT report is a legal-grade, client-facing deliverable -- its credibility dies on a single fabricated CVE or hand-waved CVSS. Every Critical and High finding must trace to a reachable code path, a live reproduction, and cited evidence; a scanner hit with no traced path is a lead in the Needs-Verification bucket, not a Critical in the matrix. Every score is computed from a shown vector or retrieved from a cited advisory -- never recalled, never approximated. Where a WSTG id, ASVS requirement, CVE, or CVSS cannot be verified this session, leave it `not verified` -- honest abstention is correct and recoverable; a confident fabrication is the worst outcome. The report a reader trusts is one where every claim, when opened, literally says what the report says it says.
