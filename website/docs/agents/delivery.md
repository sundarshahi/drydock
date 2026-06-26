---
sidebar_position: 5
title: "Delivery & operations"
description: "DevOps, SRE, Data Scientist, Technical Writer, and Skill Maker: the agents that ship and sustain."
---

# Delivery & operations

The final stretch of the [Drydock](https://github.com/sundarshahi/drydock) pipeline takes verified code and turns it into a deployable, observable, documented, production-survivable system. Five agents own this work across the **SHIP** and **SUSTAIN** phases:

| Agent | Phase | Produces |
|-------|-------|----------|
| **DevOps** | SHIP | Containers, CI/CD pipelines, infrastructure-as-code, monitoring infra |
| **SRE** | SHIP | SLOs, error budgets, runbooks, chaos scenarios, capacity models |
| **Data Scientist** | SHIP (conditional) | LLM/ML optimization, experiments, data pipelines, cost models |
| **Technical Writer** | SUSTAIN | API reference, developer guides, the Docusaurus site, governance files |
| **Skill Maker** | any | Reusable Claude Code skills and plugins |

All five run as isolated subagents (`agents/*.md`), routed through the `drydock` orchestrator. They sit downstream of the planning and build agents — see [how the pipeline fits together](/docs/concepts/how-it-works).

:::info Where these agents sit in the pipeline
Drydock runs `DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN`, with three human approval gates (requirements, architecture, production-readiness). DevOps, Data Scientist, and SRE execute in **SHIP** — where SRE also runs the Gate 3 production-readiness review at the end of the phase; the Technical Writer documents in **SUSTAIN**.
:::

## DevOps — SHIP

**What it produces.** A complete deployment surface: per-service multi-stage Dockerfiles, GitHub Actions workflows (`ci.yml`, `pr-checks.yml`, `cd-staging.yml`, `cd-production.yml`), Terraform modules under `infrastructure/terraform/`, Kubernetes base + overlays, and the monitoring/observability stack (Prometheus, Grafana, logging, tracing, alerting). Deliverables land at the project root; planning notes go in `drydock/devops/`.

**How it hardens.** Every standard ships as a **generated artifact wired into a job that exits non-zero on breach** — never prose. Pipelines are filled in from `skills/devops/templates/` (lint-clean references), not free-written. Blocking gates include lint (`actionlint`, `hadolint`, `tflint`), coverage and patch-coverage, arch-boundary (`make arch`), frontend/backend perf budgets, supply-chain verification (`cosign verify` + `gh attestation verify`), and stale-flag checks. Production deploys go by immutable digest with SLSA provenance and a signed SBOM; rollback is the Argo Rollouts canary auto-abort, not a script.

**Boundaries.**

:::warning DevOps does not define SLOs
SLOs, error budgets, and burn-rate queries belong to **SRE**. DevOps provides the monitoring infrastructure and *copies* SRE's burn-rate query and threshold into the canary `AnalysisTemplate` — it never re-derives them. Operational runbooks belong to SRE at `docs/runbooks/`; DevOps only links alerts to those runbook paths.
:::

- **DevOps implements**, SRE governs reliability targets.
- **security-engineer** is the sole authority on app-dependency supply-chain analysis; DevOps owns image provenance and signing at the infra layer.
- **solution-architect** owns the RFC 9457 `Problem` schema and the performance budget (`docs/architecture/performance-budget.yaml`); DevOps reads them — it never hardcodes `500ms`/`200KB`.
- All metric/log/span names come from `observability-contract.md`; dashboards reference only names that code emits.

## SRE — SHIP

**What it produces.** The reliability layer for a deployed system: a production-readiness checklist with 12/15-Factor compliance, SLI/SLO definitions with error budgets, multi-window burn-rate alerts, chaos scenarios with steady-state hypotheses, incident runbooks and escalation policies, and capacity models. Deliverables go to `docs/runbooks/<service>/`, the `production-ready` gate, and analysis lands in `drydock/sre/`.

**The production-ready gate.** SRE emits `make production-ready` plus `.github/workflows/production-ready.yml` — a **blocking gate** that exits non-zero on metric-name drift, invalid alert rules, an SLO-vs-budget mismatch, an unjustified factor failure, a missing kill-switch key, or failing tests/coverage/arch-boundary. Overrides are allowed only as a logged `accepted-with-justification` entry; no silent skips. This gate backs **Gate 3 (production-readiness)**.

**Boundaries.**

:::tip SRE is the sole SLO authority
SRE has **sole authority** over SLO definitions, error budgets, runbooks, and capacity planning. DevOps does not define SLOs — it implements the thresholds SRE defines. SRE writes the SRE-owned `drydock/sre/slo/burn-rate-query.yaml` that DevOps's canary `AnalysisTemplate` consumes: SRE owns the threshold and the query, DevOps wires it into the rollout.
:::

| Concern | DevOps owns | SRE owns |
|---------|-------------|----------|
| Monitoring | Prometheus/Grafana install, base dashboards | SLI instrumentation, SLO burn-rate alerts, error budgets |
| Alerting | Infra alerts (disk, CPU, memory) | Service-level alerts tied to SLOs, on-call routing |
| Incident response | Provides the tooling | Owns the process (classification, war rooms, postmortems) |
| Disaster recovery | Backup infrastructure | RTO/RPO validation, failover testing |

Like DevOps, SRE reads latency targets from `performance-budget.yaml` and metric names from `observability-contract.md` — never inventing either.

## Data Scientist — SHIP (conditional)

:::note Conditional on AI/ML usage
The Data Scientist runs only when the system has AI/ML/LLM usage. Its Phase 1 audit detects integration points; if none are found, the agent is not engaged. ML-infrastructure phases activate only when custom ML models exist.
:::

**What it produces.** Optimization and rigor for AI-powered systems: LLM prompt/token optimization with semantic caching and fallback chains, A/B experiment frameworks with power analysis, analytics/ETL data pipelines, ML serving and model-registry infrastructure, and cost models projected at 2x/5x/10x scale. Artifacts go to `drydock/data-scientist/`. After the Phase 1 audit, the system is classified (LLM-Powered App, ML-Enhanced Product, Data-Intensive Platform, or Hybrid) to select which phases run.

**Security posture.** Every prompt template, serving endpoint, cache, pipeline, and experiment harness is BUILD-phase code subject to `security-defaults.md`. Model output is treated as untrusted; no secrets or PII enter prompts, caches, or traces; model-triggered tool calls are gated and allowlisted; and the prompt-injection trust boundary is enforced. The relevant OWASP LLM Top 10 controls (LLM03/04/08/09/10) are asserted in their owning phase.

**Boundaries.** A/B experiment guardrails trip the **shared** feature-flag auto-rollback (`libs/shared/feature-flags/`) — the Data Scientist defines thresholds but does not reimplement bucketing, ring rollout, or rollback. It hands infra requirements (Redis, Kafka, warehouse) and alert thresholds to DevOps, data-flow diagrams to solution-architect, and ROI summaries to the product-manager.

## Technical Writer — SUSTAIN

**What it produces.** The documentation surface that lets a new developer onboard in hours and an API consumer integrate in minutes: an API reference generated from OpenAPI, developer guides (quickstart, local dev, contributing, testing), operations summaries, a runnable API collection, a Docusaurus site, and governance files (README, CONTRIBUTING, SECURITY, CODEOWNERS, issue/PR templates). Deliverables land under `docs/`; writing notes go to `drydock/technical-writer/`.

**Single-source-of-truth law.** Documentation that restates a value owned elsewhere drifts and lies, so where a machine-readable source exists, the page is **generated from it by a checked-in script wired into CI**:

| Doc surface | Generated from |
|-------------|----------------|
| Error-code table + `problem+json` format | `libs/shared/errors/catalog.*` |
| API endpoint/schema reference + collection | `api/openapi/*.yaml` |
| Monitoring metric/log/span names | `observability-contract.md` |
| Performance numbers | `docs/architecture/performance-budget.yaml` |
| Feature-flag list | `config/feature-flags.yaml` |

A hand-edited generated doc fails the `docs:gen-check` CI job. Other gates cover broken links (`onBrokenLinks: 'throw'`), OpenAPI validation, metric-name lint, and budget-ref lint.

**Boundaries.** The Technical Writer **never invents information** — every statement traces to a prior-phase artifact, and missing facts get a `<!-- TODO: Source not found -->` placeholder. Operations docs summarize and index the canonical SRE runbooks rather than duplicating them. The `.devcontainer/` quickstart and the `docs-examples` CI job are owned by **DevOps**; the writer's job is to make every fenced example real and copy-pasteable so that job passes.

## Skill Maker — reusable tooling

**What it produces.** End-to-end skill and plugin creation: it interviews the user, writes a `SKILL.md` (with frontmatter `name`/`description` in third person, optional `disable-model-invocation` and `allowed-tools`), generates an evals set (≥3 positive and ≥3 negative trigger/behaviour cases), packages the result as a Claude Code plugin, validates it with `claude plugin validate`, creates a GitHub repo, and registers it in the user's marketplace.

**Boundaries.** Skill Maker is not tied to a single pipeline phase — it is invoked when a user wants to turn a repeatable workflow into a shareable tool ("make a skill", "build a plugin"), not for editing existing skills. All identity values (`<owner>`, `<marketplace-repo>`, repo paths) are **resolved at runtime in Phase 0** — never hardcoded. Generated skills keep the `SKILL.md` body under ~500 lines using progressive disclosure, and push fragile or deterministic steps into bundled `scripts/`.

## Install Drydock

Inside Claude Code:

```text
/plugin marketplace add sundarshahi/drydock
/plugin install drydock@drydock
```

Drydock is an open-source plugin (version 2.5.0) — a team of 19 specialized agents coordinated by one orchestrator, with 14 execution modes from Full Build down to single-agent runs.

## Next steps

- [How it works](/docs/concepts/how-it-works) — the full pipeline, phases, and approval gates
- [Build & harden agents](/docs/agents/engineering) — the agents that produce the code these five ship and sustain
