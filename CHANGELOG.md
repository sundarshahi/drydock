# Changelog

All notable changes to **Drydock**.

## [Unreleased]

### Renamed
- **Plugin renamed `shipyard` → `drydock`** ahead of the community-marketplace
  submission (the name `shipyard` was already taken by a different plugin). This
  changes the install name (`drydock`), the skill namespace (`drydock:<skill>`),
  the `/drydock` command, the runtime workspace directory (`drydock/`), and the
  project config file (`.drydock.yaml`). The GitHub repository itself stays at
  `sundarshahi/drydock`. Verified by the eval suite, `validate --strict`, and a
  live routing smoke test (`route='drydock:drydock'`, zero plugin errors).
- **Engagement modes renamed to "Autonomy Levels"** — the four levels
  `Express / Standard / Thorough / Meticulous` are now
  `Autopilot / Copilot / Checkpoint / Manual`, and the concept "engagement mode"
  is now "autonomy level" (how many decisions the pipeline surfaces to the user).
  Applied consistently across all 15 agents and the shared protocols; the default
  is **Copilot**. Naming only — the behavioral spectrum (Autopilot = fully
  autonomous → Manual = reviews every decision) is unchanged.

### Docs
- **Documentation hardened for the marketplace submission.** `DEV_PROTOCOL.md`
  corrected: agent/protocol counts fixed (15 agents, 14 shared protocols), version
  examples aligned to the `2.x` line, the competitive-analysis tables rewritten as
  capability-focused language (no named third-party products), and stale
  original-project references removed. `SECURITY.md` supported-versions table
  aligned to `2.1.x`. `README.md` "Autonomy Levels" section rewritten with clearer
  selection guidance. `VISION.md` rephrased for clarity — goal-first framing, the
  three gates named consistently (Requirements / Architecture / Production
  Readiness), and the autonomy-level terminology applied; all eleven principles and
  their hard rules are preserved.
- **README rewritten for first-time readers** — a plain-language intro, a
  quick-start with a concrete example, and a clearer pipeline diagram (the three
  gates shown as explicit approval points, parallel phases marked). `SECURITY.md`
  scope corrected to the actual executable surface — both hooks (`secret-guard.sh`,
  `session-guard.sh`) plus the bundled `bootstrap-workspace.sh` / `verify-gate.py`
  / `aggregate-cost.py` scripts. `CONTRIBUTING.md` CI description updated to the
  current `claude plugin validate . --strict` + deterministic-evals workflows.

### Changed
- **`product-manager` is now self-contained** — it no longer invokes the external
  `superpowers:writing-plans` skill; when an implementation outline is needed it
  writes a lightweight inline task breakdown (detailed planning is owned downstream
  by the orchestrator and Solution Architect). Removes a hard dependency on a
  third-party plugin.

### Fixed
- **Case-sensitive-filesystem bug in the workspace directory name.** When the
  runtime workspace was lowercased to `drydock/`, several path references were
  left as `Drydock/` — the `session-guard` hook's `SUITE_DIR`, the default
  workspace and prune-set in `aggregate-cost.py` / `verify-gate.py`, and the
  deterministic eval fixtures. On a case-insensitive filesystem (macOS) these
  still resolved, but on a case-sensitive one (Linux/CI) they pointed at a
  non-existent `Drydock/`, so the session-guard never fired and the helper
  scripts defaulted to the wrong directory. All workspace path references are now
  lowercase `drydock/`, matching what `bootstrap-workspace.sh` creates. This also
  fixes the deterministic eval suite, which was green on macOS but failing in CI.
- **Progressive-disclosure refactor** — the four oversized `SKILL.md` files were
  slimmed below the 500-line budget by deferring per-phase detail to on-demand
  `phases/` and `reference/` files (loaders + frontmatter stay in `SKILL.md`):
  `drydock` 1212→451 (5 new `phases/`+`reference/` files), `solution-architect`
  826→240 (6 phases), `qa-engineer` 670→376 (7 phases), `devops` 667→273 (6
  phases). Each slimmed `SKILL.md` gains a Phase/Reference Index and Dispatch
  Protocol, mirroring `software-engineer`. Lossless: no instruction was dropped,
  only relocated. Verified by the eval suite (loaders/frontmatter intact) and a
  live routing smoke test (orchestrator still loads with zero plugin errors and
  classifies correctly).

### Added
- **Gate-metric re-derivation** — the production-readiness gate no longer trusts
  the agents' self-reported receipt metrics. `skills/drydock/scripts/verify-gate.py`
  independently re-derives **tests** (from JUnit XML) and **coverage** (from
  Istanbul/Cobertura/lcov) from the build's ground-truth artifacts, verifies every
  claimed artifact exists, and flags any receipt whose numbers contradict the
  artifacts. `phases/gates.md` now gates on the derived values: a `mismatch`
  (overstated pass count / coverage) or a missing artifact is a BLOCKING breach;
  metrics with no parseable artifact fall back to the receipt tagged `[unverified]`.
- **Scripts over prose** — two deterministic orchestrator procedures that were
  described in prose are now bundled scripts the orchestrator runs directly:
  `skills/drydock/scripts/bootstrap-workspace.sh` (scaffold `drydock/` +
  deploy all shared protocols, with `${CLAUDE_PLUGIN_ROOT}` → `${CLAUDE_SKILL_DIR}`
  → script-relative source resolution) and `skills/drydock/scripts/aggregate-cost.py`
  (sum effort/cost metrics across receipts, dedup artifacts, tolerate malformed
  receipts). The full-build setup, non-Full-Build mode bootstrap, and final-summary
  docs now call these instead of re-deriving them each run.

### Testing
- **Gate re-derivation eval** — `test_gate_verification.py` drives `verify-gate.py`
  against fixtures: it CONFIRMS a truthful receipt (`verified`, `trustworthy`),
  CATCHES a lying one (tests/coverage `mismatch`, missing artifact flagged,
  `trustworthy: false`), and reports `unverified` when no artifact exists.
- **Bundled-script eval** — `test_drydock_scripts.py` runs both helper scripts
  against throwaway fixtures and asserts their behavior (protocols deployed,
  metrics aggregated/deduplicated), so a script regression fails CI for free.
- **SKILL.md size budget** — new deterministic test `test_skill_size.py` fails
  any `skills/*/SKILL.md` over 500 lines, locking in the progressive-disclosure
  win (`phases/`/`reference/` detail files are exempt).
- **Eval harness added** — a two-tier evaluation suite under `evals/`.
  - **Deterministic tier (free, gates every PR)** — pure-Python structural
    invariants over the repo, run by `evals/run_deterministic.py` and wired into
    CI via [`.github/workflows/evals.yml`](.github/workflows/evals.yml) (also
    `make evals`). No API key and no Claude CLI. Guards: loader-resolution shape
    (the belt-and-suspenders protocol fallback chain), dead-tool regression
    (`TeamCreate`/`TeamDelete`/`smart_outline`/`smart_search`/`smart_unfold`
    never reappear as live calls), agent/skill cross-reference (the 11
    `agents/*.md` map 1:1 to worker skills; the 4 main-context skills have no
    agent file), manifest integrity (`plugin.json`/`marketplace.json` version
    agreement), and YAML frontmatter validity.
  - **Behavioral tier (local-only)** — non-deterministic routing checks driven
    by `claude -p` (`make evals-behavioral`). Uses your local Claude Code login
    and spends usage; intentionally **NOT** in CI (no API key, `temperature=1.0`
    is non-deterministic).
- No plugin behavior change: dev tooling only, so `plugin.json` /
  `marketplace.json` remain at `2.1.0`.

## [2.1.0] — 2026-06-25

Dispatch-port + correctness release. The orchestration is now built entirely on documented Claude Code primitives — **not** breaking; these are internal dispatch and correctness fixes with no change to the public contract or generated-artifact behavior.

### Changed
- **Ported orchestration to documented primitives** — the 15 agents are now real `agents/` subagent definitions (auto-discovered, with isolation/background frontmatter) dispatched as genuine isolated subagents via the real `Task*` tools.
- **Removed nonexistent tooling** — dropped references to the made-up `TeamCreate`/`TeamDelete` and `smart_outline`/`smart_search`/`smart_unfold` tools that were never real Claude Code tools; the real `Task*` tools are retained.
- **First-run protocol loader fixed** — the first-run-empty bug in the protocol loader is fixed with a belt-and-suspenders `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` path resolution.
- **Scoped allowed-tools** — each worker subagent now declares a scoped `allowed-tools` set instead of inheriting the full toolset.
- **skill-maker corrected** — updated to SOTA skill-authoring rules.

### Fixed
- **Hooks hardened** — `SessionStart`/`PreToolUse` hook commands no longer guess a non-versioned `~/.claude/plugins/cache` path; when `${CLAUDE_PLUGIN_ROOT}` is unset they fail loudly to stderr and exit 0 so the session is never blocked.

### Removed
- **Dead config** — deleted the orphaned `skills/drydock/hooks/activation-rules.json` (referenced a `UserPromptSubmit` hook wired to nothing).

### CI
- **Strict validation** — CI installs the Claude Code CLI (`npm install -g @anthropic-ai/claude-code`) and runs `claude plugin validate . --strict`, failing the job on any error or warning (no more warning swallow, and no more hard-fail when the CLI is simply absent on the runner). It also verifies `skills/*/SKILL.md` + `agents/*.md` frontmatter with a real YAML parse (name present; description present and ≤1024 chars).
- **Marketplace description added** — `.claude-plugin/marketplace.json` now carries a top-level `description`, which `--strict` requires (the previous warning was promoted to an error under strict mode).

## [2.0.0] — 2026-06-25

Enterprise-grade hardening release. Drydock now treats production-readiness as evidence-backed and enforceable: artifacts are generated (not described) and blocking gates verify them.

### Added
- **Four new shared protocols**, deployed to `drydock/.protocols/` at orchestrator bootstrap and loaded by the worker skills: `security-defaults.md` (security-by-default baseline), `observability-contract.md` (OTel traces/metrics/logs + RED/USE), `architecture-boundaries.md` (Clean Architecture / dependency-rule enforcement), and `compliance-protocol.md` (per-product regulatory mapping). These join `grounding-protocol.md` and `security-testing-protocol.md`.
- **Compliance Officer skill** (`drydock:compliance-officer`) — the 15th agent. Scopes per-product regulatory frameworks (SOC 2, GDPR, HIPAA, PCI-DSS v4.0.1, CCPA/CPRA, ISO 27001, FedRAMP), maps mandatory controls to implementing artifacts, verifies controls exist in generated code/infra, and emits statutory evidence (SSP, DPIA, breach runbook) behind a blocking compliance gate.
- **Compliance execution mode** — new orchestrator mode (now 12 total), invocable for regulated builds and as a gate input to production-readiness.
- **Real secret-guard hook** — `hooks/secret-guard.sh`, wired as a `PreToolUse` hook in `hooks/hooks.json`. Blocks committing/writing secret files and scans staged diffs for credentials.
- **Generated observability** — OpenTelemetry traces/metrics/logs scaffolding plus RED (Rate/Errors/Duration) and USE (Utilization/Saturation/Errors) metric sets, produced as real artifacts.
- **OpenFeature feature flags** — standardized flag provider with an env-var fallback.
- **OpenAPI governance** — API-first contract linting and spec-as-source enforcement.
- **Supply-chain hardening** — GitHub Actions CI templates (lint-clean by default), SLSA provenance, and cosign artifact signing.
- **Unified blocking gate metrics** — downstream skills now emit `tests_passing`, `tests_failing`, `coverage_lines`, `coverage_branches`, `mutation_score`, `patch_coverage`, `contract_can_i_deploy`, `perf_baseline_regression`, and a compliance controls-present/missing status.

### Changed
- **Unified blocking production-readiness gate** — `production-ready` is now BLOCKED on failing tests, coverage, performance budget, compliance controls, or architecture-boundary violations. An explicit, logged "accepted with justification" override receipt is the only escape hatch.
- **Mutation + property tests default-on** — QA emits mutation score and property-based coverage as first-class gate metrics.
- **CI/CD defaults to GitHub Actions templates** for the generated pipeline and supply-chain steps.
- **Plugin metadata** — version 2.0.0; description, keywords, author email, homepage, and repository updated to advertise the 15-agent enterprise roster.

### Breaking
- **Default error format is now RFC 9457 `application/problem+json`.** Services and clients that assumed the prior ad-hoc error envelope must migrate to the problem+json shape. This is potentially breaking for existing integrations.

## [1.1.0] — 2026-06-24

### Added
- **Grounding & Anti-Hallucination protocol** — new shared protocol `grounding-protocol.md`, loaded by all 14 agents. Evidence-first generation: every factual/code claim cites `file:line`, command output, or a retrieved source; claim↔evidence separation; `[verified]`/`[inferred]`/`[unverified]` confidence tags; cite-or-abstain; a 4-step chain-of-verification; and security-specific no-fabrication (never invent CVE ids or CVSS scores).
- **Security Testing Authorization & Safety protocol** — new shared protocol `security-testing-protocol.md`, loaded by the Security Engineer. Mandatory authorization + scope gate before any active testing; local/authorized-staging targets only; no DoS/destructive payloads/production data; responsible disclosure; evidence-backed findings; CVSS discipline (4.0 primary, 3.1 ingested, paired with EPSS/CISA KEV).
- **Real VAPT execution** — two new Security Engineer phases. `07-vapt-execution.md` runs gated DAST/pen-testing (recon→enum→scan→exploit/PoC→retest) with a 24-tool integration table (semgrep, CodeQL, trivy, grype, osv-scanner, gitleaks, trufflehog, checkov, OWASP ZAP, nuclei, nikto, sqlmap, wapiti, ffuf, schemathesis, RESTler…), each with verified invocations and safe-by-default usage; all active/DAST tools are gated behind the authorization step. `08-vapt-report.md` assembles a professional CVSS-backed pentest report. The Security Engineer now runs 8 phases.
- **Pentest (VAPT) execution mode** — new orchestrator mode with a mandatory authorization-gate prompt before any active testing, plus `/drydock pentest` and `/drydock vapt` commands. HARDEN mode remains static-only so the gate cannot be bypassed.

### Changed
- **OWASP coverage** — Security Engineer audits against OWASP Top 10 2025, API Security Top 10 (2023), and the LLM Top 10 (2025), with a Standards References section and a per-finding standards tag block (CVSS 4.0 / CWE / OWASP / WSTG v4.2 / ASVS 5.0.0). Verified against official sources.
- **Plugin metadata** — version 1.1.0; description and keywords advertise VAPT + OWASP coverage and anti-hallucination guardrails.

## [1.0.0] — 2026-06-24

Baseline release — project branding, workspace layout, and configuration established.
