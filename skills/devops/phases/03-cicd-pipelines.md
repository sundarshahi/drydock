# Phase 3 — CI/CD Pipelines

Generate CI/CD pipelines at `.github/workflows/` (or `paths.ci_cd` from config) and `scripts/`. **GitHub Actions templates first** — FILL IN from `skills/devops/templates/`, do not free-write the YAML.

### Pipeline Templates (copy from `skills/devops/templates/`, replace `<PLACEHOLDER>`)
```
.github/workflows/
├── ci.yml              # lint-pipelines, lint, typecheck, test+coverage, make arch, SAST, Trivy
├── pr-checks.yml       # patch-coverage, frontend-perf (lhci+size-limit), stale-flags, docs-examples
├── cd-staging.yml      # OIDC deploy on merge; qa suite via workflow_call; k6 baseline gate
├── cd-production.yml   # SLSA provenance + cosign + syft SBOM + verify GATE + immutable digest
├── scheduled.yml       # dependency updates + cron housekeeping; calls qa's mutation-nightly.yml via workflow_call (does NOT define its own mutation gate)
├── (mutation-nightly.yml owned by qa — the single nightly mutation gate; never duplicated here)
└── (test.yml owned by qa — REUSED via workflow_call, never clobbered)

.github/dependabot.yml      # ALL ecosystems + github-actions (keeps pinned SHAs fresh)
infrastructure/kubernetes/<svc>/rollout.yaml   # from templates/rollout-canary.yaml

.gitlab-ci.yml              # (only if architecture mandates GitLab — GH Actions is the default)

scripts/
├── build.sh
├── deploy.sh               # supports --snapshot-config + immutable --image <digest>
├── smoke-test.sh
├── setup-branch-protection.sh   # gh api: required job names + PR review + prod environment
└── reconcile-sbom.sh       # cross-check release SBOM vs security-engineer/supply-chain/sbom.json
```
> **No `rollback.sh`.** Rollback is the Argo Rollouts canary auto-abort (see `templates/rollout-canary.yaml`) restoring the prior immutable release id — replace any orphan `rollback.sh` with the progressive-delivery analysis.

### Lint mandate (BLOCKING — record results in the T7 receipt)

Every workflow, Dockerfile, and IaC module is linted and the pipeline FAILS on any error:

| Target | Tool | Wired in |
|--------|------|----------|
| Workflows | `actionlint` | `ci.yml` + `pr-checks.yml` `lint-pipelines` job |
| Dockerfiles | `hadolint` (`--failure-threshold error`) | same |
| Terraform | `tflint` + `terraform validate` | `ci.yml` `lint-pipelines` job |

The T7 receipt `metrics` records `{actionlint_errors, hadolint_errors, tflint_errors, terraform_validate}` — a non-zero error count is a failed task.

### Cloud auth + action hardening (HIGH)

- **Keyless OIDC only.** `permissions: id-token: write` + the provider's OIDC; assume a role. NO long-lived `AWS_ACCESS_KEY_ID` / `GCP_SA_KEY` secrets. The OIDC trust is a checked-in Terraform module under `infrastructure/security/iam/` (this skill emits it).
- **Pin every third-party action to a full 40-char commit SHA** (`uses: owner/repo@<sha> # vX.Y.Z`). A bare `@v4` is a supply-chain hole.
- **`.github/dependabot.yml`** — enable ALL ecosystems present + the `github-actions` ecosystem (bumps the pinned SHAs via PR).
- **`scripts/setup-branch-protection.sh`** — uses `gh api` to require the EXACT job names (`lint`, `test`, `arch`, `sast`, `patch-coverage`, `frontend-perf`, `stale-flags`, `docs-examples`, `lint-pipelines`) + PR review + a `production` GitHub Environment with required reviewers.

### CI Pipeline Stages
1. **Checkout & cache** — Restore dependency caches
2. **Install** — Dependencies with lockfile verification
3. **Lint** — Code style, formatting (fail-fast)
4. **Type check** — Static analysis (if applicable)
5. **Unit tests** — Parallel execution, coverage reporting
6. **Integration tests** — Against test containers (testcontainers)
7. **Security scan** — SAST (Semgrep/CodeQL), dependency audit (Snyk/Trivy)
8. **Build** — Docker image with content-hash tagging
9. **Push** — To ECR/GCR/ACR with immutable tags

### CD Pipeline Stages (staging — `cd-staging.yml`)
1. **qa suite via `workflow_call`** — reuse qa's `test.yml` (compose, don't clobber)
2. **Build + push immutable digest** via OIDC; tag by digest, never `latest`
3. **Deploy to staging** — automatic on default-branch merge
4. **Smoke tests** — health + critical-path verification
5. **Perf-baseline GATE (POST-MERGE)** — `node tests/performance/compare-baseline.js` (k6 p95/p99 vs the committed `tests/performance/baselines/<scenario>.baseline.json`, fail beyond +10%, also reads `performance-budget.yaml`) — runs after the staging deploy and BLOCKS staging->prod promotion (via the `production` GitHub Environment); NOT a required PR check.

### CD Pipeline Stages (production — `cd-production.yml`, supply-chain hardened, HIGH)
1. **Build + push by DIGEST** (immutable; release id == version tag)
2. **SLSA v1.0 provenance** — `actions/attest-build-provenance` (or slsa-github-generator), keyed to the digest
3. **Keyless cosign sign** — Sigstore Fulcio cert + Rekor transparency log (no key material)
4. **syft SBOM** — SPDX, attached to the GitHub Release; **reconcile** with `Shipyard/security-engineer/supply-chain/sbom.json` via `reconcile-sbom.sh`
5. **PRE-DEPLOY VERIFY GATE** — `gh attestation verify` + `cosign verify` against the digest; an unverifiable artifact **BLOCKS the deploy**
6. **Required-reviewer approval** — `production` GitHub Environment
7. **Progressive rollout** — Argo Rollouts canary on the verified digest; analysis FAIL → auto-abort/rollback
8. **Post-deploy verification** — automated smoke + synthetic monitoring on the contract metrics

> **Conflict resolution:** security-engineer AUDITS the supply chain (sole authority on app-dependency analysis); **devops IMPLEMENTS** provenance + signing at the image/infra layer and reconciles its release SBOM against the security-engineer audit.

### Deployment Strategies (progressive delivery, HIGH)
Argo Rollouts `Rollout` (or Flagger `Canary`) from `templates/rollout-canary.yaml`, with an `AnalysisTemplate` that CONSUMES SRE's `Shipyard/sre/slo/burn-rate-query.yaml` — copying its `burn_rate_query` / `latency_query` (the **exact `observability-contract` names**) and its thresholds verbatim:
- **burn-rate** = SRE's `burn_rate_query` (multi-window 5xx burn on the canary subset), with `failureCondition: result[0] > 14.4` (SRE's `fail_when`)
- **p99 latency** = SRE's `latency_query` = `histogram_quantile(0.99, http_request_duration_seconds_bucket{canary="true"})`, with `failureCondition: result[0] > 1.2` seconds (SRE's `latency_fail_when`, derived from `performance-budget.yaml`)

**Contract: canary analysis FAIL → automatic abort + rollback** to the prior immutable release id. SRE OWNS the burn-rate / latency queries AND thresholds in `burn-rate-query.yaml`; devops only WIRES them into the AnalysisTemplate `failureCondition` (no raw `<ERROR_RATE_MAX>`/5xx-ratio `successCondition`, no re-derived threshold). Traffic shift: 10% → 25% → 50% → 100% with analysis at each step. Blue-Green and Rolling remain available for stateless / stateful-ordered services respectively; all three restore a specific prior immutable release on failure (no mutable rollback).

### Immutable releases (LOW)
Each deploy is an immutable versioned release = image **DIGEST** + a resolved **config snapshot** (`deploy.sh --snapshot-config`). Rollback restores a specific prior release id (digest + config snapshot), never a re-mutated tag.

### Performance-budget CI (HIGH)
Wired across `pr-checks.yml` (frontend) and `cd-staging.yml` (backend) — all thresholds READ FROM `docs/architecture/performance-budget.yaml`, never hardcoded:
- **`frontend-perf` job (pr-checks, required check)** — `lhci autorun` against `frontend/lighthouserc.json` + a `size-limit`/`bundlesize` step that FAILS on breach. `lighthouserc.json` assertions and `.size-limit.json` `limit` values are generated FROM the budget's `web_vitals` / `bundle` keys.
- **`perf-baseline` job (cd-staging, POST-MERGE promotion gate)** — `tests/performance/compare-baseline.js` runs k6, compares `http_request_duration_seconds` p95/p99 against the committed per-scenario `tests/performance/baselines/<scenario>.baseline.json` AND the budget; **fails beyond +10%**. The runner `compare-baseline.js` and the `baselines/<scenario>.baseline.json` files are EMITTED by qa-engineer; devops only INVOKES `node tests/performance/compare-baseline.js`. This gate runs on `cd-staging` (default-branch merge) and BLOCKS staging->prod promotion via the `production` GitHub Environment — it is NOT a required PR check.

### Test / coverage gates (HIGH)
- **Coverage gate** in `ci.yml` `test` job — `make coverage-check COVERAGE_MIN=<n>` (threshold from architecture/`.shipyard.yaml`), **no `|| true`**.
- **Patch-coverage required check** in `pr-checks.yml` — `make patch-coverage`; NEW/changed lines must meet the threshold (`diff-cover`).
- **Nightly mutation gate** — there is ONE mutation workflow, qa-engineer's `mutation-nightly.yml` (qa owns the mutation tool config + the cron). devops does NOT emit a second mutation workflow. If devops's `scheduled.yml` needs the nightly mutation run on its cron, it invokes qa's gate via `workflow_call` (`uses: ./.github/workflows/mutation-nightly.yml`); otherwise devops makes NO mutation claim. Mutation + property tests are default-on for critical modules — owned and surfaced by qa.

### Stale-flag CI (HIGH)
`stale-flags` job in `pr-checks.yml` — `make flags-check` reads `config/feature-flags.yaml` and FAILS/warns when a flag is past its `removal_by` date OR a flag key appears in code but is unregistered in the registry (`{key,type,owner,default,created,removal_by}`).

### Developer experience (MEDIUM)
- **`.devcontainer/devcontainer.json`** — zero-install Codespaces; `postCreateCommand` runs `make setup` so a contributor gets a working toolchain with no local install.
- **`docs-examples` CI job** (in `pr-checks.yml`) — extracts fenced code blocks from `docs/**` and RUNS them (executable docs), plus `markdownlint` + `Vale` prose lint. Stale/broken examples fail the PR. devops EMITS the `docs-examples` Makefile target (see Makefile-target ownership below).

### Makefile-target ownership (CI gates call ONLY targets some skill emits)

software-engineer generates the base root `Makefile` (phase 05); each gate target is APPENDED by its owner skill. devops only WIRES these targets into CI workflows — it does NOT redefine targets it does not own. No CI job may `make <target>` a target no skill emits.

| Make target | Emitted by (owner) | devops role |
|-------------|--------------------|-------------|
| `coverage-check`, `patch-coverage` | qa | wires into `ci.yml` / `pr-checks.yml` |
| `flags-check` | software-engineer | wires into `pr-checks.yml` (`stale-flags`) |
| `arch` | software-engineer (base Makefile / architecture-boundaries) | wires into `ci.yml` (`arch`) |
| `size-limit`, `build-frontend` | frontend | wires into `pr-checks.yml` (`frontend-perf`) |
| `docs-examples` | **devops (EMITS)** | devops appends this target to the root Makefile AND wires it into `pr-checks.yml` |

devops's ONLY emitted CI-gate Makefile target is `docs-examples`. Every other `make <target>` in a devops workflow (`make coverage-check`, `patch-coverage`, `flags-check`, `size-limit`, `build-frontend`, `arch`) is emitted by its owner skill (qa / software-engineer / frontend); devops merely invokes it. `make setup` / `make test` / `make lint` / `make typecheck` come from the base Makefile (software-engineer).

### `production-ready` gate decision (override-able, logged)
`production-ready` is BLOCKED while any of {tests, coverage, perf, compliance, arch-boundary} fails. A breach may be cleared only by a logged **"accepted with justification" override** — an entry in `Shipyard/devops/override.yaml` ` { gate, breach, justification, approver, date }` surfaced at the gate ceremony. An unjustified breach stays blocking.
