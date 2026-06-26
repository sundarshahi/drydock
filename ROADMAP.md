# Roadmap

*Where Drydock is going, and why.*

This is a **direction document, not a contract.** It captures the work we believe will make Drydock sharper, cheaper, and more grounded — organized by version horizon, not by date. Items move, merge, and drop as we learn. Each one carries a status; nothing here is promised until it ships in [CHANGELOG.md](CHANGELOG.md).

If you want to push one of these forward, open an issue or PR — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Where we are — v2.5.0

The pipeline works end to end: a plain-English idea flows through **DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN**, driven by 19 specialized agents, three approval gates, and a receipt-verified handoff between every phase. Security is on by default. The docs site is live. The plugin is published to the marketplace.

Two things are already right and shape everything below:

- **Receipts are the contract.** Agents hand off compact JSON proofs, not whole artifacts. This is both the trust mechanism *and* the core token optimization. Every roadmap item must keep receipts as the source of truth.
- **The evals harness exists** (`evals/`, run in CI via `.github/workflows/evals.yml`). It is the guardrail that lets us cut tokens and compress prompts *safely* — measure, don't guess.

---

## Design tenets for what comes next

These govern how we evolve, the same way the eleven principles govern how agents behave.

1. **Grounding over invention.** When an agent can read the real system, it should — a live source beats a re-anchored assumption.
2. **Graceful degradation.** Every new external dependency (MCP server, language server, telemetry source) must be optional. Absent the integration, the agent falls back to today's behavior. Drydock never *requires* a connection to function.
3. **Measure, then cut.** No token or prompt change ships without passing the evals. The reliability floor is non-negotiable; shorter prose that follows worse is a regression.
4. **Receipts stay the spine.** New capabilities produce or consume receipts. We do not route trust around them.

---

## Themes

### 1. Grounding via MCP

**Problem:** Today every agent *reasons about* systems it cannot *see*. The product manager writes a BRD without the real backlog; the architect assumes a schema; the SRE infers SLOs. The output is sound but ungrounded.

**Approach — two directions:**

- **Consume MCP.** Let agents read real systems, mapped onto the existing roster:

  | Agent | MCP source | What changes |
  |---|---|---|
  | product-manager | Linear / Jira / Notion | BRD derived from the real backlog |
  | solution-architect | Postgres / cloud provider | reads actual schema & infra |
  | frontend / ux-designer | Figma | design tokens from the real file |
  | security-engineer | Snyk / SAST / dependency scanners | findings from real scans |
  | sre / devops | Sentry / Datadog / GitHub Actions | SLOs and incidents from real telemetry |

- **Expose Drydock as an MCP server.** Make capabilities callable from outside the session — "return the production-readiness scorecard," "validate this BRD against Gate 1," "report current task-graph state." Drydock becomes composable into other agents and CI, not just an interactive plugin.

**Leverage:** Highest of all themes — this is the difference between plausible output and grounded output, and it reinforces the re-anchoring protocol (re-anchor against a live source, not a stale spec).

**Status:** Proposed. Start with one consume integration (GitHub or Sentry) behind capability detection, per tenet 2.

---

### 2. Code intelligence via LSP-over-MCP

**Problem:** The engineering and review agents (`software-engineer`, `code-reviewer`, `qa-engineer`) understand code by reading whole files and inferring types — token-heavy and imprecise.

**Approach:** There is no native LSP path for subagents, so the practical delivery is to wrap a language server as an MCP server. The engineering-agent slice then gets:

- **Precise references** — "find every caller of this signature" returns a few lines instead of many files read.
- **Diagnostics as receipts** — compiler errors and warnings ingested structurally, more reliable than parsing build logs.
- **Exact types on hover** instead of inference from surrounding code.

**Leverage:** Doubles as a token win — it is the code-aware corner of both the MCP theme and the efficiency theme.

**Status:** Proposed. Sequenced *after* the MCP spine exists, since it rides on it.

---

### 3. Token & cost efficiency

**Problem:** A 19-agent pipeline is token-hungry by nature. The always-on skill core is ~55k words before any phase file loads. We pay for every re-anchor and every receipt round-trip. There is real slack to reclaim — without touching quality, if we measure.

**Approach — four levers, ranked by leverage-per-effort:**

1. **Per-agent model tiering.** Subagents support a `model:` frontmatter field; today none is set, so every agent runs at one tier. Put mechanical agents (technical-writer, changelog, scaffolding, receipt formatting) on a cheaper tier; reserve the top tier for the gates, architecture, security, and code review. Roughly one line per agent, near-zero quality risk.
2. **Prompt compression against evals.** Compress the highest-frequency always-on files (the `drydock` orchestrator, `code-reviewer`, `qa-engineer` SKILL.md) toward terse imperative form. Re-run the evals after each cut; stop at the reliability floor. Measured, not vibes.
3. **Lazy-load depth.** Phase files already defer ~98k words. Push more detail out of always-on SKILL.md into phase files so the core stays lean.
4. **Re-anchor tuning.** Make re-anchoring content-hash-aware — "spec unchanged since last anchor → skip the re-read." A tunable reliability/token dial, defaulting to today's safe behavior.

Plus the instrument that proves it worked:

5. **Per-phase cost/token telemetry.** Emit spend so users see where budget goes — and so the compression work above is provably worth it.

**Leverage:** Tiering is the cheapest meaningful cost cut available. The rest compounds.

**Status:** Proposed. Tiering can land first; compression should wait until the evals are stable enough to anchor the floor.

---

### 4. Pipeline ergonomics

**Problem:** The full pipeline is the right default for a real product, but it is heavy for a small change, and long runs have no clean re-entry point.

**Approach:**

- **Express / lite mode.** A reduced pipeline (fewer agents, gates collapsed or skipped) for small, well-scoped tasks. Likely the most-requested missing capability.
- **Resume-from-gate.** Receipts already make a pipeline resumable; this exposes the entry point — re-enter at the last cleared gate instead of restarting.

**Status:** Proposed.

---

## Sequencing

A suggested order, optimizing for risk and dependency rather than ambition:

1. **Per-agent model tiering** — cheapest, lowest-risk, immediate cost cut.
2. **MCP spine** — one consume integration as proof, behind capability detection.
3. **LSP-over-MCP** — the engineering-agent slice, once the spine exists.
4. **Prompt compression** — last among the efficiency work, when the evals are stable.

Ergonomics items (express mode, resume-from-gate) are independent and can slot in wherever there's appetite.

---

## Non-goals

To keep scope honest, Drydock is **not** heading toward:

- **A required cloud backend.** It stays a local-first Claude Code plugin. External integrations are always optional (tenet 2).
- **A general agent framework.** Drydock is an opinionated idea-to-launch product team, not a toolkit for building arbitrary agents.
- **Replacing the strategist.** The gates stay. More autonomy never means removing the human approval points that matter.

---

## Tracking

This document is the high-level map; granular work lives in [GitHub issues](https://github.com/sundarshahi/drydock/issues). When an item here breaks down into concrete tasks, it gets an issue; when it ships, it moves to [CHANGELOG.md](CHANGELOG.md) and leaves this file.
