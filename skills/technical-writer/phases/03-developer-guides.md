# Phase 3: Developer Guides

## Objective

Enable a new developer to go from zero to productive. Write task-oriented guides that answer "how do I..." questions — quickstart, local development, contributing, testing, architecture overview, environment variables reference, and deployment. Every guide is grounded in actual project artifacts, not generic advice.

## 3.1 — Mandatory Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| DevOps artifacts | `infrastructure/`, `docker-compose.yml` | Docker configs, environment setup |
| CI/CD pipelines | `.github/workflows/` | Build steps, test commands, deploy process |
| Source structure | `services/`, `frontend/`, `libs/` | Module layout, build files, package managers |
| Architecture docs | `docs/architecture/` | ADRs, service map, tech stack |
| Test artifacts | `tests/`, `Shipyard/qa-engineer/test-plan.md` | Test strategy, coverage requirements |
| Linter configs | `.eslintrc*`, `.prettierrc*`, `ruff.toml`, etc. | Code style rules, enforced conventions |
| Git workflow | `.github/PULL_REQUEST_TEMPLATE.md`, branch strategy | PR process, commit conventions |
| Env example | `.env.example` | All environment variables with defaults |
| Content inventory | `Shipyard/technical-writer/content-inventory.md` | Phase 1 priorities |

## 3.2 — Quickstart Guide

Generate `docs/getting-started/quickstart.md`:

0. **Recommended first run — Dev Container** — Lead with the `.devcontainer` path (the `.devcontainer/` is emitted by **devops**, not this skill). State: "Open in VS Code → *Reopen in Container*, or `devcontainer up`, and the environment is provisioned for you." This is the fastest, most reproducible onboarding. Only if a contributor opts out do they follow the manual steps below.
1. **Prerequisites** (manual path) — List runtime, Docker, and tools with exact version numbers and install links (3 items max)
2. **Clone and install** — Exact commands from clone to dependency install
3. **Configure environment** — Copy `.env.example`, document which values must be changed
4. **Start infrastructure** — `docker compose up -d` or equivalent
5. **Run migrations and seed** — Exact migration and seed commands
6. **Start the application** — Exact start command with expected output
7. **Verify it works** — A curl command with expected response (health check)
8. **Environment variables table** — Required vars with name, required flag, default, description
9. **Next steps** — Links to local development guide, architecture overview, contributing guide

The quickstart MUST achieve a working local environment in under 10 minutes. Move deep configuration to separate pages.

**Runnable examples:** every fenced command block here must be self-contained and copy-pasteable (no `...`, no invented service names) — the devops-owned `docs-examples` CI job extracts and executes these blocks against the `.devcontainer`/CI image and fails on a non-zero exit. Your job is to make the examples real; devops owns the extraction job.

## 3.3 — Local Development Setup

Generate `docs/getting-started/local-development.md`:

1. **IDE setup** — Recommended IDE, required extensions/plugins, workspace settings
2. **Hot reloading** — How to enable live reload for each service
3. **Debugging** — launch.json / debugger configuration with step-by-step setup
4. **Running tests locally** — Commands for unit, integration, and e2e tests
5. **Working with Docker** — Rebuilding containers, viewing logs, accessing service shells
6. **Common development tasks** — Creating migrations, adding endpoints, adding a new service
7. **Troubleshooting** — Table of common issues with symptoms and fixes

## 3.4 — Contributing Guide

Generate `docs/guides/contributing.md`:

1. **Git branching strategy** — Branch naming, base branches, feature vs hotfix flow
2. **Commit message format** — Convention (Conventional Commits or project-specific)
3. **Pull request process** — PR template, required reviewers, CI checks that must pass
4. **Code review expectations** — What reviewers look for, turnaround time expectations
5. **Getting help** — Slack channels, office hours, documentation links

## 3.5 — Testing Guide

Generate `docs/guides/testing-guide.md`:

1. **Testing philosophy** — Testing strategy extracted from `Shipyard/qa-engineer/test-plan.md`
2. **Running tests** — Exact commands for each test type (unit, integration, e2e) with expected output
3. **Writing a new test** — Template and example for each test type
4. **Coverage requirements** — Minimum thresholds and how to check coverage locally
5. **Test data management** — Fixtures, factories, seeding, database cleanup
6. **CI test pipeline** — Which tests run on PR, which run nightly, failure handling

## 3.6 — Architecture Overview

Generate `docs/architecture/overview.md`:

1. **System diagram** — Mermaid diagram showing all services and their connections
2. **Service responsibilities** — One paragraph per service explaining what it does and why
3. **Data flow** — Step-by-step data flow for the 3-5 most common operations
4. **Technology stack** — Table with technology, version, and rationale for each choice
5. **Key constraints** — Architectural trade-offs and why they were made

Synthesize from ADRs and architecture docs. Write for a developer who has no prior context.

## 3.7 — Environment Variables Reference

Generate `docs/getting-started/installation.md` (includes env var reference):

1. **Installation instructions** — Platform-specific setup for macOS, Linux, Windows/WSL
2. **Version requirements** — Exact versions for all tools with compatibility notes
3. **Environment variables** — Grouped by category (database, cache, auth, external services, observability)

Each variable documented with: name, type, required/optional, default value, description, example value. Group by category — never dump 50 variables in a flat list.

## 3.8 — Deployment Guide

Generate `docs/operations/deployment.md`:

1. **Pipeline overview** — Describe CI/CD stages from commit to production
2. **Environments table** — URL, branch, auto-deploy flag, approval requirements
3. **Standard deployment** — Step-by-step from PR merge to production rollout
4. **Emergency deployment** — Manual process when CI is unavailable
5. **Rollback procedure** — Commands for rolling back to previous and specific versions
6. **Feature flags** — How to toggle features without deployment. Document the OpenFeature client at `libs/shared/feature-flags/` and the checked-in registry `config/feature-flags.yaml` (each flag: `{ key, type, owner, default, created, removal_by }`). List flags FROM the registry — do not invent flag keys. Note the `removal_by` date so stale flags get cleaned up.
7. **Database migrations** — How migrations run during deployment, rollback procedures

Do NOT hardcode performance numbers (deploy gates, latency/size budgets) in this guide — reference `docs/architecture/performance-budget.yaml` as the source. The budget-ref lint fails on a hardcoded `500ms`/`200KB`.

## 3.9 — Coding Conventions

Generate `docs/guides/coding-conventions.md`:

1. **Naming conventions** — Extracted from linter configs and existing code patterns
2. **File organization** — Directory structure conventions per service. State the **inward-only dependency law** from `architecture-boundaries.md` and that `make arch` (the fitness gate) fails on an outward dependency — document what IS enforced, not aspiration.
3. **Error handling patterns** — Errors map to RFC 9457 `application/problem+json` via the error-catalog module `libs/shared/errors/catalog.*` (the single source the docs error table also reads). Show how a domain error → catalog entry → `Problem` body; do NOT document a bespoke `{code,message,details}` envelope.
4. **Logging conventions** — Structured JSON to **stdout only**, with the exact fields from `observability-contract.md` (`timestamp, level, message, service, env, trace_id, span_id, request_id`, `error.type`/`error.stack` on error). `trace_id`/`span_id` come from the **live span context**, never fabricated. PII/secrets are never logged. Metric/log/span names referenced here MUST be the contract names (`http_requests_total`, `http_request_duration_seconds`, `http_requests_in_flight`, `*_pool_*`) — no invented names.
5. **Code examples** — "Good" examples from the actual codebase (not invented patterns)

## 3.10 — Monitoring Guide

Generate `docs/operations/monitoring.md`:

1. **Golden signals** — Document the RED metrics by their EXACT contract names: `http_requests_total` (rate + errors via `status_class`), `http_request_duration_seconds` (latency histogram, in **seconds**, with **exemplars** that link a slow bucket to its trace), `http_requests_in_flight` (concurrency). For resource pools, the USE metrics `*_pool_connections_in_use/_max/_idle`, `*_pool_wait_seconds`, `*_pool_acquire_errors_total`.
2. **Logs↔traces correlation** — Explain that `trace_id` joins a structured log line, its span, and the problem+json error body; how to pivot from a log to a trace.
3. **Where to look** — Link to actual Grafana dashboards/alerts (owned by devops/sre); this page is a summary + index, not a second copy.

**Hard rule:** reference ONLY metric/log/span names declared in `observability-contract.md`. Naming a metric no code emits (e.g. `request_latency_ms`) makes a reader build a "No data" dashboard — the metric-name lint greps this page against the contract and FAILS on any unlisted name. Do not hardcode SLO/latency numbers here either; cite `docs/architecture/performance-budget.yaml`.

## 3.11 — Governance & DX Files

Generate the repository governance and developer-experience files (respect Brownfield Awareness — never overwrite an existing one; extend instead):

| File | Content |
|------|---------|
| `README.md` (root, GENERATED) | Value prop (one paragraph), status **badges** (CI, coverage, license, docs), a quickstart that leads with the `.devcontainer` first-run path, and a **link tree** to `docs/` sections (getting-started, architecture, api-reference, guides, operations). Keep it generated from project metadata + the doc sitemap so links stay valid. |
| `CONTRIBUTING.md` | Branch/PR/commit conventions (Conventional Commits if changelog automation uses release-please), how to run tests + the docs gates locally, link to CODE_OF_CONDUCT. |
| `CODE_OF_CONDUCT.md` | Contributor Covenant; fill the contact from project metadata. |
| `SECURITY.md` | Supported versions, private vulnerability-reporting channel, response SLA. Align with `security-defaults.md`. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Checklist: tests, docs updated, changeset added, gates green. |
| `.github/ISSUE_TEMPLATE/` | `bug_report.yml`, `feature_request.yml`, `config.yml` (structured forms). |
| `.github/CODEOWNERS` | Map paths → owning teams (docs → technical-writer/maintainers, `api/` → backend, `libs/shared/errors/` → backend, etc.). |
| Changelog automation | **release-please** (`release-please-config.json` + `.release-please-manifest.json`) OR **Changesets** (`.changeset/config.json`). CHANGELOG.md becomes **bot-driven** — document the workflow; do not hand-edit the changelog. |

These are real governance artifacts, not prose: the PR template enforces the changeset/docs checklist, CODEOWNERS enforces review routing, and the changelog automation is wired into the release workflow (a manual CHANGELOG edit without a changeset fails the release check).

## Output Deliverables

| Artifact | Path |
|----------|------|
| Quickstart guide | `docs/getting-started/quickstart.md` |
| Local development guide | `docs/getting-started/local-development.md` |
| Installation and env vars | `docs/getting-started/installation.md` |
| Contributing guide | `docs/guides/contributing.md` |
| Testing guide | `docs/guides/testing-guide.md` |
| Coding conventions | `docs/guides/coding-conventions.md` |
| Architecture overview | `docs/architecture/overview.md` |
| Service map | `docs/architecture/service-map.md` |
| ADR summaries | `docs/architecture/decisions/<NNN-title>.md` |
| Deployment guide | `docs/operations/deployment.md` |
| Monitoring guide | `docs/operations/monitoring.md` |
| Root README (GENERATED) | `README.md` |
| Contributing guide | `CONTRIBUTING.md` |
| Code of Conduct | `CODE_OF_CONDUCT.md` |
| Security policy | `SECURITY.md` |
| PR template | `.github/PULL_REQUEST_TEMPLATE.md` |
| Issue templates | `.github/ISSUE_TEMPLATE/*` |
| Code owners | `.github/CODEOWNERS` |
| Changelog automation config | `release-please-config.json` + `.release-please-manifest.json` OR `.changeset/config.json` |

## Validation Loop

Before moving to Phase 4:
- Quickstart leads with the `.devcontainer` first-run path and still achieves a working environment in under 10 minutes (mentally walk through every step)
- Every environment variable is documented with name, type, required/optional, default, description
- Every test command actually works (verify against project build files)
- Architecture overview matches the actual system, not an aspirational design
- Monitoring guide names ONLY `observability-contract.md` metrics/log fields/span attrs (metric-name lint clean); no hardcoded budget numbers (cite `performance-budget.yaml`)
- Coding-conventions error/logging sections reference the error-catalog + RFC 9457 `Problem` + stdout JSON log fields, not invented patterns
- Feature-flag docs list flags from `config/feature-flags.yaml`; none invented
- Governance/DX files generated and not overwriting existing ones (Brownfield); changelog is bot-driven
- All fenced runnable examples are self-contained so the devops `docs-examples` job passes
- All guides end with "Next steps" linking to related pages
- No fabricated content — every statement traces to a source artifact

## Quality Bar

- A new developer can onboard using only these guides and no human help
- Every code example is complete and copy-pasteable
- ADR summaries are plain language, not copy-pasted from raw ADR format
- Coding conventions reference actual linter configs, not invented rules
