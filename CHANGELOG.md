# Changelog

All notable changes to **Shipyard**.

## [Unreleased]

### Testing
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
- **Dead config** — deleted the orphaned `skills/shipyard/hooks/activation-rules.json` (referenced a `UserPromptSubmit` hook wired to nothing).

### CI
- **Strict validation** — CI installs the Claude Code CLI (`npm install -g @anthropic-ai/claude-code`) and runs `claude plugin validate . --strict`, failing the job on any error or warning (no more warning swallow, and no more hard-fail when the CLI is simply absent on the runner). It also verifies `skills/*/SKILL.md` + `agents/*.md` frontmatter with a real YAML parse (name present; description present and ≤1024 chars).
- **Marketplace description added** — `.claude-plugin/marketplace.json` now carries a top-level `description`, which `--strict` requires (the previous warning was promoted to an error under strict mode).

## [2.0.0] — 2026-06-25

Enterprise-grade hardening release. Shipyard now treats production-readiness as evidence-backed and enforceable: artifacts are generated (not described) and blocking gates verify them.

### Added
- **Four new shared protocols**, deployed to `Shipyard/.protocols/` at orchestrator bootstrap and loaded by the worker skills: `security-defaults.md` (security-by-default baseline), `observability-contract.md` (OTel traces/metrics/logs + RED/USE), `architecture-boundaries.md` (Clean Architecture / dependency-rule enforcement), and `compliance-protocol.md` (per-product regulatory mapping). These join `grounding-protocol.md` and `security-testing-protocol.md`.
- **Compliance Officer skill** (`shipyard:compliance-officer`) — the 15th agent. Scopes per-product regulatory frameworks (SOC 2, GDPR, HIPAA, PCI-DSS v4.0.1, CCPA/CPRA, ISO 27001, FedRAMP), maps mandatory controls to implementing artifacts, verifies controls exist in generated code/infra, and emits statutory evidence (SSP, DPIA, breach runbook) behind a blocking compliance gate.
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
- **Pentest (VAPT) execution mode** — new orchestrator mode with a mandatory authorization-gate prompt before any active testing, plus `/shipyard pentest` and `/shipyard vapt` commands. HARDEN mode remains static-only so the gate cannot be bypassed.

### Changed
- **OWASP coverage** — Security Engineer audits against OWASP Top 10 2025, API Security Top 10 (2023), and the LLM Top 10 (2025), with a Standards References section and a per-finding standards tag block (CVSS 4.0 / CWE / OWASP / WSTG v4.2 / ASVS 5.0.0). Verified against official sources.
- **Plugin metadata** — version 1.1.0; description and keywords advertise VAPT + OWASP coverage and anti-hallucination guardrails.

## [1.0.0] — 2026-06-24

Baseline release — project branding, workspace layout, and configuration established.
