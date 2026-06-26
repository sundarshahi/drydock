---
sidebar_position: 2
title: "Guardrails"
description: "Receipts, re-anchoring, adversarial review, and the production-readiness gate: how Drydock stays grounded."
---

# Guardrails

Autonomous coding pipelines fail in predictable ways. Agents claim work is done when files are missing. Context compresses over a multi-hour run and the spec drifts. Code looks syntactically perfect but quietly removes a safety check. A generator confidently emits a model ID or package version that hasn't existed for a year.

Drydock treats these as engineering problems with engineering solutions, not as things a smarter prompt will eventually fix. The guardrails below are the mechanisms — enforced by shared protocols and by the orchestrator — that make the pipeline's output trustworthy. They are the difference between a system that *claims* it works and one that *proves* it.

:::info Where these live
The mechanisms on this page are implemented in the shared protocol stack (`skills/_shared/protocols/`) loaded by every agent, and enforced by the orchestrator at each phase transition. See [How it works](/docs/concepts/how-it-works) for the pipeline they sit inside.
:::

## The trust model in one sentence

> Real over claimed: numbers, not adjectives; verified artifacts, not agent assertions; receipts, not promises.

Every guardrail below is an expression of that rule.

## Receipts: proof of completion, not a status report

Every agent writes a JSON **receipt** as its absolute last action — after all files are written and verified, and before it marks its task complete. The receipt is the agent's proof that the work actually ran.

A receipt lists every artifact the agent produced (each path must exist on disk at the moment of writing), concrete metrics (at least one real number — no empty objects), and a one-line description of what was verified. Tasks that run tests, contracts, or performance checks must also emit machine-readable gate fields inside `metrics` — `tests_passing`, `tests_failing`, `coverage_lines`, `coverage_branches`, `mutation_score`, `patch_coverage`, `contract_can_i_deploy`, `perf_baseline_regression`.

```json
{
  "task": "T6b",
  "agent": "code-reviewer",
  "phase": "HARDEN",
  "status": "complete",
  "artifacts": ["drydock/code-reviewer/review-report.md"],
  "metrics": { "findings_critical": 2, "tests_passing": 412, "tests_failing": 0, "coverage_lines": 87.4 },
  "effort": { "files_read": 47, "files_written": 6, "tool_calls": 83 },
  "verification": "all 4 review phases executed, review-report.md written with executive summary"
}
```

At every phase transition and before every gate, the orchestrator does not take the receipt on faith. It:

1. Lists the receipts it expects for the completed phase.
2. Reads each one from `.orchestrator/receipts/`.
3. Confirms every path in `artifacts` actually exists on disk.

| Symptom | What the receipt check catches |
|---|---|
| Agent says "done" but the file was never written | An artifact path with no file on disk — the orchestrator investigates instead of proceeding |
| Receipt never appears | The task did not complete properly |
| Empty `metrics` or vague `verification: "done"` | Rejected as an anti-pattern — every receipt carries concrete numbers |

:::warning No receipt = not done
A gate will not open without verified artifacts behind it. This is the core of the differentiator most multi-agent systems lack: a verifiable proof chain instead of LLM self-reporting.
:::

The `effort` fields (`files_read`, `files_written`, `tool_calls`) also feed the cost dashboard, aggregated across all agents at pipeline end by `skills/drydock/scripts/aggregate-cost.py`.

## Re-anchoring: re-read the spec from disk

In a long autonomous run, context compresses. As it does, the agent's memory of the original requirements degrades — a paraphrase of a paraphrase. The result is **context drift**: the BUILD phase quietly diverges from what the DEFINE phase actually decided.

The fix is structural, not hopeful. The orchestrator **re-anchors** at every phase transition: it re-reads the canonical artifacts — the BRD, the architecture docs, the API contracts — directly **from disk** rather than trusting its compressed in-context recollection. The artifacts are the single source of truth; memory is not.

:::note Why from disk
Memory is not evidence. The on-disk artifact is what every agent aligned on, so re-reading it is what keeps fifteen subagents pulling toward the same target hours into a run. Re-anchoring is the temporal counterpart to receipts: receipts verify *output*, re-anchoring verifies the *input* each phase builds from.
:::

## The grounding protocol: memory is not evidence

Receipts and re-anchoring keep the *pipeline* honest. The **grounding protocol** keeps each *claim* honest. Its rule: if you did not Read it, run it, or retrieve it this session, you may not state it as fact.

LLMs produce invented file paths, fabricated `file:line` references, non-existent APIs, made-up CVE IDs, and hallucinated CVSS scores — all in confident, assertive prose. The grounding protocol forces every factual or code claim to carry a concrete pointer and rewards honest abstention over fabrication:

- **Evidence pointers.** Every claim cites `file:line`, an exact command plus its output, or a source URL plus a quoted span. No pointer = not a fact.
- **Confidence tags by evidence, not feeling.** `[verified]` (directly observed this session), `[inferred]` (derived from verified facts, with the chain stated), or `[unverified]` (plausible, no evidence). Untagged factual claims default to `[unverified]`.
- **Cite-or-abstain.** If a claim can't be backed, the agent writes `Unverified: <claim> — could not confirm because <reason>` rather than inventing a value to fill a schema field.
- **Chain-of-verification.** Before finalizing, the agent re-opens each artifact and answers an open question about it ("what does line 42 actually return?"), then deletes any claim the artifact doesn't support.

Reports end with a calibration summary — counts by tag — so a reviewer can see at a glance how much of a finding rests on evidence versus inference.

## The freshness protocol: verify volatile data before implementing

Training data goes stale. Model IDs, API pricing, SDK versions, security advisories, and config syntax change on the order of days to months. A generator that emits a remembered package name invites a real failure: attackers register hallucinated package names with malicious code.

The freshness protocol sorts volatile data into tiers and tells each agent when to stop and verify with a live web search before writing:

| Tier | Examples | Action |
|---|---|---|
| 1 — Critical (days–weeks) | LLM model IDs, API pricing, active CVEs, SDK breaking changes | Must WebSearch before using |
| 2 — High (weeks–months) | Package versions, framework APIs, Docker base tags, cloud SKUs | WebSearch when writing config or dependencies |
| 3 — Medium (months–quarters) | Browser APIs, crypto recommendations, compliance updates | WebSearch if uncertain |
| 4 — Stable (years) | Language syntax, protocols, SQL, algorithms, git | Trust training data |

The pattern is **search, then implement**: identify what needs verifying, search for the current value, cite what was found, then write the verified data. A ten-second search is near-free; shipping a deprecated API or vulnerable dependency is not.

## Adversarial code review

Most review tooling is a neutral observer. Drydock's Code Reviewer is an adversary: it assumes the code is **wrong until proven right** and actively tries to break it. Surface-level correctness — code that compiles and looks right but hides an off-by-one, a hallucinated method, or a quietly removed safety check — is exactly the failure mode a neutral reviewer misses.

The review scales with the autonomy level, from critical-issues-only up to hostile break scenarios. It pairs with the **Dead Element Rule** (any button, link, or form that renders but does nothing is a Critical bug, not a TODO) and with the QA Engineer running actual tests, so "looks done" is never mistaken for "is done."

## The production-readiness gate re-derives metrics from real artifacts

Drydock has three human approval gates — Requirements (Gate 1), Architecture (Gate 2), and Production Readiness (Gate 3). The third is the strictest, and it does not trust receipt metrics on faith.

`skills/drydock/scripts/verify-gate.py` independently **re-derives** the numbers from ground-truth artifacts: test results from JUnit XML, coverage from Istanbul / Cobertura / lcov. If a receipt's reported numbers contradict what the artifacts actually say, the gate flags it.

The gate enforces from data, not prose. `production-ready` is **blocked** when any of the following hold:

- `tests_failing > 0`
- `coverage_lines`, `coverage_branches`, `mutation_score`, or `patch_coverage` is below budget
- `perf_baseline_regression` is `true`
- `contract_can_i_deploy` is `false`
- `compliance.controls_missing` is non-empty
- an architecture-boundary violation is present

The only way past a blocked gate is an explicit, logged override receipt ("accepted with justification") for that specific gate at `.orchestrator/overrides/<gate>-<id>.json`. Acceptance is a recorded decision, never a silent skip.

:::tip The verification hierarchy
Every task gets Level 1 (agent self-check) and Level 2 (orchestrator reads the receipt and confirms artifacts exist). Critical findings add Level 3 (cross-agent review). Phase transitions add Level 4 (a gate ceremony showing concrete, re-derived metrics). Users see verified data, not agent claims.
:::

## Boundary safety

The bugs that survive review tend to live at system boundaries — client to server, app to external API, one integrated system to another — where a framework abstraction silently does the wrong thing. Boundary Safety codifies six structural, framework-agnostic patterns distilled from real production failures that every agent checks for:

| # | Pattern | One-liner |
|---|---|---|
| 1 | Abstractions break at boundaries | Use platform primitives when crossing domains (raw `<a href>`, `fetch`, redirect) |
| 2 | Don't duplicate framework control flow | Wire the UI to the destination; let middleware handle the rest |
| 3 | Self-referencing config = infinite loop | An override must point to something different from the default |
| 4 | Global interceptors must branch | Never return a hardcoded value from a global hook |
| 5 | Test full journeys, not just hops | Verify the user's final state, not intermediate 200s |
| 6 | Identity must match across systems | Verify identity-format compatibility at every integration point |

These catch the silent failures unit and integration tests miss: a `<Link>` pointing at an API route, a NextAuth override that redirects into itself, an auth callback that ignores the original destination, or git commits whose email format the CI provider rejects.

## How the guardrails reinforce each other

No single mechanism is sufficient; together they close the loop the ecosystem leaves open.

| Failure mode | Guardrail |
|---|---|
| Agent claims work is done but files are missing | Receipts + artifact-existence check |
| Context drift in long runs | Re-anchoring from disk at every phase transition |
| Confident hallucination of paths, APIs, CVEs | Grounding protocol — evidence pointers, confidence tags, abstention |
| Stale model IDs, deprecated APIs, hallucinated packages | Freshness protocol — verify before implementing |
| Surface-level correctness hiding subtle bugs | Adversarial review + Dead Element Rule + real test runs |
| Inflated or invented gate metrics | Production-readiness gate re-derives numbers from JUnit/coverage artifacts |
| Silent failures at system boundaries | Boundary Safety — six structural patterns |

The result is a pipeline whose output you can trust precisely because it never asks you to take its word for it.

:::note Related
[How it works](/docs/concepts/how-it-works) — the DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN pipeline and the three gates these guardrails protect.
:::
