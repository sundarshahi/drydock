# DevOps Reference Templates — FILL IN, do not free-write

These are **parameterized, lint-clean reference pipelines**. The devops agent COPIES a
template into the project and replaces every `<PLACEHOLDER>` token — it does NOT author a
workflow from scratch. Free-writing YAML is how `actionlint`/`hadolint` errors, unpinned
actions, and missing `permissions:` blocks slip in. Start from the template; keep it green.

| Template | Copy to | Purpose |
|----------|---------|---------|
| `ci.yml` | `.github/workflows/ci.yml` | Build, lint, typecheck, test+coverage, container build, IaC lint, SAST |
| `pr-checks.yml` | `.github/workflows/pr-checks.yml` | PR-only gates: patch-coverage, frontend perf (lhci + size-limit), stale-flag, docs-examples, lint-the-pipelines |
| `cd-staging.yml` | `.github/workflows/cd-staging.yml` | Auto-deploy to staging on merge to default branch + smoke + k6 baseline compare |
| `cd-production.yml` | `.github/workflows/cd-production.yml` | Tag-triggered supply-chain-hardened release: SLSA provenance, cosign sign, syft SBOM, verify-attestation GATE, immutable digest deploy, progressive rollout |
| `rollout-canary.yaml` | `infrastructure/kubernetes/<service>/rollout.yaml` | Argo Rollouts `Rollout` + `AnalysisTemplate` querying the observability-contract metrics; canary FAIL → auto-abort/rollback |

## Hard rules (every copy MUST satisfy — recorded in the T7 receipt)

1. **Lint the pipelines and FAIL on any error.** `actionlint` on every workflow, `hadolint`
   on every Dockerfile, `tflint` + `terraform validate` on every IaC module. A lint error
   blocks the merge. Record `{actionlint, hadolint, tflint, terraform_validate}` pass/fail
   counts in the receipt `metrics`.
2. **Pin every third-party action to a full 40-char commit SHA** (`uses: owner/repo@<sha> #
   vX.Y.Z`). A bare tag (`@v4`) is a supply-chain hole — Dependabot (`github-actions`
   ecosystem) bumps the SHA via PR. First-party `actions/*` may use a tag pinned by
   Dependabot but prefer SHA.
3. **Cloud auth is keyless OIDC.** `permissions: id-token: write`; assume a role via the
   provider's OIDC. NO long-lived `AWS_ACCESS_KEY_ID`/`GCP_SA_KEY` secrets. The OIDC trust is
   a checked-in Terraform module under `infrastructure/security/iam/`.
4. **Every metric / log field / span attr referenced in a dashboard, alert, AnalysisTemplate
   or k6 check is an EXACT name from `observability-contract.md`** — `http_requests_total`,
   `http_request_duration_seconds`, `http_requests_in_flight`, `*_pool_*`. Never invent a
   name no code emits.
5. **Read thresholds from `docs/architecture/performance-budget.yaml`** — never hardcode
   500ms / 200KB. lhci, size-limit, and the k6 baseline compare all read the budget.
6. **No `|| true`, no `continue-on-error: true` on a gate.** A gate that cannot fail is not a
   gate. Coverage, patch-coverage, arch-boundary (`make arch`), perf, supply-chain-verify,
   and stale-flag jobs exit non-zero on breach.

## Placeholder convention

`<UPPER_SNAKE>` = fill in. Common tokens:
`<SERVICE>`, `<IMAGE>` (`ghcr.io/<org>/<service>`), `<AWS_ACCOUNT_ID>`, `<OIDC_ROLE_ARN>`,
`<AWS_REGION>`, `<CLUSTER>`, `<NAMESPACE>`, `<RUNTIME>` (node/python/go/jvm),
`<COVERAGE_MIN>` (from `.shipyard.yaml`/architecture, default 80), `<DEFAULT_BRANCH>`.
