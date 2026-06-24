# Grounding Protocol — Evidence-First Generation & Anti-Hallucination

**Core principle: Memory is not evidence. If you did not Read it, run it, or retrieve it this session, you may not state it as fact.**

LLMs confidently produce invented file paths, fabricated `file:line` references, non-existent APIs and packages, made-up CVE identifiers, and hallucinated CVSS scores — all in syntactically perfect, assertive prose. This protocol forces every factual or code claim to be backed by a concrete artifact observed this session, and rewards honest abstention over confident fabrication.

---

## Evidence-First Rule

- Never assert a fact about the codebase, an API, a config value, a version, a dependency, or a vulnerability from training knowledge alone.
- Every factual or code claim carries a concrete artifact pointer: `file:line` (e.g. `auth.py:42`), an exact command + its actual output, or a source URL + quoted span. **No pointer = not a fact.**
- **Read before you describe:** open the actual file and quote the relevant lines before describing what a function/route/middleware does. Do not infer behavior from a filename or convention.
- **Verify external symbols against ground truth** before writing a call to any external API/package/function — confirm it exists in retrieved docs or the project manifest/lockfile. Package/API hallucinations are syntactically valid but cause runtime + supply-chain failures.
- **Verify volatile facts live** (model IDs, pricing, versions, deprecations, advisories) — cross-reference `freshness-protocol.md`; never recall.
- **Re-derive numbers** (counts, metrics, line numbers, scores) from an actual count or tool output; never round from memory. State the source of each number.
- **Trace, do not assume, reachability/control flow:** follow the actual call chain. "Config says auth required" is not evidence the guard is applied to every route.

---

## Claim ↔ Evidence Separation (structural rule)

- Write findings/claims in two fields: **CLAIM** and **EVIDENCE**. EVIDENCE must be a concrete artifact reference (`path:line`, exact `command` + output excerpt, or URL + quoted span) that, when opened, literally states the claim.
- A claim with an empty or vague EVIDENCE field is invalid — cut it, or downgrade it to `[unverified]`.
- Use a two-column or two-field layout so empty evidence is visually obvious to a reviewer.

| CLAIM | EVIDENCE |
|-------|----------|
| The `/admin` route requires an authenticated admin | `routes/admin.py:14` — `@require_role("admin")` decorator on the handler |
| The build pins Node 22 | `Dockerfile:1` — `FROM node:22-alpine` |
| Dependency `left-pad` is at 1.3.0 | `package-lock.json:88` — `"version": "1.3.0"` |

---

## Confidence Tags (evidence-based, NOT feeling-based)

Assign by the evidence you actually hold, never by gut confidence:

| Tag | Objective definition (assign by evidence held, never by gut confidence) |
|-----|--------------------------------------------------------------------------|
| `[verified]` | You directly observed the supporting artifact this session — Read the file, ran the command, retrieved + quoted the source. |
| `[inferred]` | Logically derived from verified facts but not directly observed. You MUST state the inference chain (verified premises → step → conclusion). |
| `[unverified]` | Plausible but you could not retrieve evidence. |

- Tag every factual/code claim with exactly one marker. **Untagged factual claims are treated as `[unverified]` by default.**
- Avoid decisive language ("always", "guaranteed", "definitely") on anything not `[verified]`. Match linguistic certainty to evidence strength.
- Promote or demote tags only on a change in evidence, never "on reflection".
- End every report with a **calibration summary**: counts by tag (e.g. `18 [verified], 4 [inferred], 2 [unverified]`).
- Why tags, not feelings: LLM self-reported verbal confidence is poorly calibrated and mimics assertive training phrasing. That is exactly why each tag is defined by an objective evidence test — what artifact you observed — and never by how sure you feel.

---

## Abstention (cite-or-abstain)

- You are rewarded for honest abstention and penalized for confident fabrication. If you cannot back a claim with `file:line`, command output, or a cited source, do not state it. Write: `Unverified: <claim> — could not confirm because <reason>.`
- **Abstain on retrieval failure** (Read fails, command errors, file missing, search empty) — mark dependent claims `[unverified]`; do not fill the gap from memory.
- **Abstain on self-inconsistency** (two independent reasoning passes disagree) — report the disagreement rather than picking one.
- Scope abstention to the specific unverifiable claim; deliver everything you DID verify, clearly separated.
- **Never fabricate to satisfy a format/schema:** leave a required field (CVE ID, CVSS, repro step, citation) explicitly empty or `not verified` rather than inventing a value.
- Surface assumptions as `[inferred]` so they are checkable, not presented as established fact.

---

## Citation Discipline

- Every finding/claim cites evidence inline: claim → `path:line` | `` `command` `` + output excerpt | URL + quoted span.
- Cite the **precise span**, not the document ("auth.py:42", not "somewhere in auth.py").
- The cited evidence must literally support the claim — faithfulness is not the same as correctness; a citation that does not actually say what you claim is still a hallucination.
- Never cite a source you did not open this session. Fabricated or broken citations (invented titles, non-existent docs) are a primary hallucination tell.
- For web claims, include URL + verbatim quoted snippet + retrieval date (volatile facts).

---

## Chain-of-Verification before asserting (CoVe, 4 steps)

```
Before finalizing any report, code change, or finding:
  1. List every concrete factual or code claim you made.
  2. For each, write an OPEN verification question
     ("What does line 42 of auth.py actually return?"
      NOT "Does line 42 return null?").  ← yes/no questions cause false agreement.
  3. Re-open the actual file / re-run the command and answer each from the artifact, not memory.
  4. Revise or delete any claim the artifact does not support.
```

**Self-consistency for high-stakes judgments** (severity rating, "this is exploitable", root-cause): reason it through two independent ways — e.g. trace the data-flow forward, then trace it backward from the sink. Agree → `[verified]`; disagree → report the disagreement, mark `[unverified]`, or gather more evidence. Do not average the two.

**Adversarial self-critique pass:** after drafting, switch to a skeptical-reviewer role and find (a) the single claim most likely hallucinated, (b) the weakest-evidenced claim, and (c) any place you answered from memory. Re-verify or remove those three.

---

## Security-Specific No-Fabrication

(Mirrors the rules formalized fully in `security-testing-protocol.md`; this is a short cross-reference.)

- **NEVER invent CVE identifiers.** A CVE may only be cited if retrieved THIS session from an authoritative source (NVD / MITRE / GitHub Advisory / vendor) AND it matches the actual dependency + version in the manifest/lockfile.
- **NEVER fabricate CVSS scores or vectors.** Retrieve the official score (cite it) or compute it from the vector, showing each metric. A hallucinated CVSS score is a known forensic marker of AI-fabricated security content.
- Every vulnerability finding references real, reachable code (source / tainted-input `file:line` → sink → data-flow path). No traced path → `[unverified]` / potential, not Critical / High.
- **Cross-reference:** full security grounding (authorization, scope, evidence-backed findings, CVSS discipline) lives in `security-testing-protocol.md`.

---

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| "The `login` route checks the JWT" (from the name) | Open the route handler, quote the guard line, cite `auth/routes.py:88` |
| Citing `CVE-2024-XXXXX` recalled from memory | WebSearch NVD/GHSA this session, confirm it maps to the installed version, quote it |
| Inventing a "fixed version 3.2.1" to recommend | Retrieve the real fixed version from the advisory/registry; if none exists, say so |
| Stating a CVSS base score "≈9.1" | Compute from the vector showing each metric, or retrieve + cite the official score |
| Filling a required CVE/CVSS field to satisfy the report schema | Leave it `not verified`; abstention is correct |
| Averaging two conflicting line counts | Re-read both, state the conflict, resolve via the authoritative source |

---

## Key Principle

**A confident fabrication is the worst outcome; an honest "I could not verify X" is recoverable and rewarded. Tag by the evidence you hold, cite the exact span, and abstain when you cannot.**
