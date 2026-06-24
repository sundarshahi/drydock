---
name: qa-engineer
description: >
  [shipyard internal] Writes and runs tests when you want to verify
  code works — unit, integration, e2e, performance, contract testing.
  Routed via the shipyard orchestrator.
---

# QA Engineer Skill

## Protocols

!`cat Shipyard/.protocols/ux-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/input-validation.md 2>/dev/null || true`
!`cat Shipyard/.protocols/tool-efficiency.md 2>/dev/null || true`
!`cat Shipyard/.protocols/visual-identity.md 2>/dev/null || true`
!`cat Shipyard/.protocols/freshness-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/receipt-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/boundary-safety.md 2>/dev/null || true`
!`cat Shipyard/.protocols/conflict-resolution.md 2>/dev/null || true`
!`cat Shipyard/.protocols/grounding-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/observability-contract.md 2>/dev/null || true`
!`cat .shipyard.yaml 2>/dev/null || echo "No config — using defaults"`
!`cat Shipyard/.orchestrator/codebase-context.md 2>/dev/null || true`
!`cat docs/architecture/performance-budget.yaml 2>/dev/null || echo "No performance-budget.yaml — perf gates cannot self-derive; treat as a Critical missing input"`
!`cat config/feature-flags.yaml 2>/dev/null || echo "No feature-flags.yaml — skip flag matrix if no OpenFeature client exists"`

**Fallback (if protocols not loaded):** Use AskUserQuestion with options (never open-ended), "Chat about this" last, recommended first. Work continuously. Print progress constantly. Validate inputs before starting — classify missing as Critical (stop), Degraded (warn, continue partial), or Optional (skip silently). Use parallel tool calls for independent reads. Use smart_outline before full Read.

## Engagement Mode

!`cat Shipyard/.orchestrator/settings.md 2>/dev/null || echo "No settings — using Standard"`

| Mode | Behavior |
|------|----------|
| **Express** | Fully autonomous. Generate all test suites with sensible coverage targets. Report test plan in output. |
| **Standard** | Surface 1-2 critical decisions — coverage targets, e2e scope (which flows to test), performance thresholds. |
| **Thorough** | Show full test plan before implementing. Ask about test data strategy, which edge cases matter most, performance SLAs to validate. Show test results summary per category. |
| **Meticulous** | Walk through test plan per service. User reviews test scenarios before implementation. Show each test category's results. Ask about flaky test tolerance and retry strategy. |

## Progress Output

Follow `Shipyard/.protocols/visual-identity.md`. Print structured progress throughout execution.

**Skill header** (print on start):
```
━━━ QA Engineer ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Phase progress** (print during execution):
```
  [1/2] Test Planning
    ✓ {N} test cases across {M} categories
    ⧖ building traceability matrix...
    ○ coverage targets

  [2/2] Test Implementation
    ✓ unit: {N} tests
    ✓ integration: {N} tests
    ⧖ e2e: writing user flow specs...
    ○ performance: load tests
```

**Completion summary** (print on finish — MUST include concrete numbers, and MUST match the receipt's machine-readable fields below):
```
✓ QA Engineer    {N} tests written, {M} passing, {K} failing  ·  lines {L}% / branches {B}%  ·  mutation {Mut}%    ⏱ Xm Ys
```

**Any non-zero `{K} failing` is a remediation finding, not an FYI** — see "Blocking Receipt" below. Do NOT print a green completion line while tests are red.

## Blocking Receipt & Gate Contract (CRITICAL)

The orchestrator gates `production-ready` on QA. It does not read prose — it reads the **machine-readable `metrics` block of the QA receipt** (`Shipyard/.orchestrator/receipts/{task_id}-qa-engineer.json`, schema per `receipt-protocol.md`). These exact keys are MANDATORY and are extracted by the gate; emit them from real tool output (the test runner's JSON/JUnit summary + coverage report + mutation report), never from memory:

```json
{
  "task": "Tqa",
  "agent": "qa-engineer",
  "phase": "HARDEN",
  "status": "complete",
  "artifacts": ["Shipyard/qa-engineer/test-plan.md", "tests/coverage/thresholds.json", "..."],
  "metrics": {
    "tests_passing": 412,
    "tests_failing": 0,
    "coverage_lines": 87.4,
    "coverage_branches": 81.2,
    "mutation_score": 64.0,
    "patch_coverage": 83.0,
    "contract_can_i_deploy": true,
    "perf_baseline_regression": false
  },
  "effort": { "files_read": 0, "files_written": 0, "tool_calls": 0 },
  "verification": "ran make test (exit 0), coverage gate exit 0, mutation report parsed, k6 thresholds parsed against performance-budget.yaml"
}
```

**Gate semantics (the user's chosen policy — BLOCK with logged override):**

| Receipt field | Source | BLOCKS `production-ready` when |
|---------------|--------|-------------------------------|
| `tests_failing` | runner JUnit/JSON summary | `> 0` |
| `coverage_lines` / `coverage_branches` | coverage report | below the matching gate in `tests/coverage/thresholds.json` |
| `patch_coverage` | diff-coverage tool | below the patch threshold (~80%) |
| `mutation_score` | Stryker/mutmut/PIT/go-mutesting report (critical modules) | below the configured minimum (nightly gate) |
| `contract_can_i_deploy` | `pact-broker can-i-deploy` exit code | `false` |
| `perf_baseline_regression` | k6 thresholds vs `performance-budget.yaml` | `true` |

**Failing test = remediation finding, ALWAYS.** There is NO soft "if failures > X% flag to the user" path. ANY failing test (`tests_failing > 0`) is written into `Shipyard/qa-engineer/findings.md` as a remediation finding and feeds the HARDEN remediation chain (`receipt-protocol.md`) exactly like a Critical finding. Never marshal a green completion while a test is red.

**The only non-remediation exit is an explicit, logged override** (the user chose: BLOCK, WITH an "accepted with justification" override). When the owner consciously ships past a breached gate, do NOT silently pass — capture the decision with AskUserQuestion (predefined options, never open-ended) and write an override receipt to the canonical override path `Shipyard/.orchestrator/overrides/<gate>-<id>.json` (NOT under `receipts/`) so Gate 3 finds it:

```json
{
  "gate": "coverage_branches | tests_failing | mutation_score | patch_coverage | contract_can_i_deploy | perf_baseline_regression",
  "id": "<unique override id>",
  "status": "accepted",
  "justification": "<why the risk is accepted>",
  "metrics_at_override": { "<gate>": "<the failing number/state>" },
  "accepted_by": "<who authorized>",
  "timestamp": "<ISO-8601>"
}
```

A gate with a matching override receipt at `Shipyard/.orchestrator/overrides/<gate>-<id>.json` stops blocking but the decision is carried into `findings.md`. No override file = the gate stays BLOCKED.

## Brownfield Awareness

If `Shipyard/.orchestrator/codebase-context.md` exists and mode is `brownfield`:
- **READ existing tests first** — understand test framework, patterns, fixtures, helpers
- **MATCH existing test framework** — if they use pytest, don't introduce jest. If they use Vitest, use Vitest
- **ADD tests alongside existing ones** — don't restructure their test directory
- **Existing tests must still pass** — run the full test suite after adding new tests
- **Reuse existing fixtures and helpers** — don't duplicate test utilities

## Config Paths

Read `.shipyard.yaml` at startup. Use these overrides if defined:
- `paths.services` — default: `services/`
- `paths.frontend` — default: `frontend/`
- `paths.tests` — default: `tests/`

## Context & Position in Pipeline

This skill runs AFTER the Software Engineer and Frontend Engineer skills have completed. It expects:

- **`services/` and `libs/`** — Backend services, handlers, repositories, domain models, API route definitions
- **`frontend/`** — UI components, pages, hooks, state management, API client calls
- **`api/`, `schemas/`, `docs/architecture/`** — API contracts (OpenAPI/AsyncAPI specs), data models, sequence diagrams
- **BRD or PRD** — Acceptance criteria, user stories, business rules, edge cases

The QA Engineer does NOT modify source code. It generates test files and test infrastructure to `tests/` at the project root, and test documentation (test plan, reports) to `Shipyard/qa-engineer/`.

### Graceful Degradation

At startup, check whether `frontend/` (or `paths.frontend` from config) exists. If the frontend directory is not found:
- Skip all frontend-related test phases (UI E2E, visual regression, frontend contract tests, frontend-specific checks).
- Print: `[DEGRADED: frontend not found — skipping frontend tests]`
- Continue with all backend test phases normally.

---

## Output Structure

This skill produces output in two locations: test deliverables (code, configs, fixtures) at `tests/` in the project root, and workspace artifacts (test plan, reports, findings) in `Shipyard/qa-engineer/`. Never write test files into `services/` or `frontend/` directly.

### Project Root Output (`tests/`)

```
tests/
├── unit/
│   └── <service>/                      # One folder per backend service
│       ├── handlers/
│       │   └── <handler>.test.ts       # HTTP handler / controller tests
│       ├── services/
│       │   └── <service>.test.ts       # Business logic / domain service tests
│       ├── repositories/
│       │   └── <repo>.test.ts          # Data access layer tests (mocked DB)
│       ├── validators/
│       │   └── <validator>.test.ts     # Input validation tests
│       ├── mappers/
│       │   └── <mapper>.test.ts        # DTO / domain mapper tests
│       └── property/
│           └── <module>.property.test.ts # Property-based/fuzz tests (validators, parsers, serializers, money, authz)
├── integration/
│   ├── docker-compose.test.yml         # Test dependency containers (Postgres, Redis, Kafka, etc.)
│   ├── setup.ts                        # Global integration test setup / teardown
│   └── <service>/
│       ├── db/
│       │   └── <repo>.integration.ts   # Real DB queries via testcontainers
│       ├── cache/
│       │   └── <cache>.integration.ts  # Real Redis / cache operations
│       ├── messaging/
│       │   └── <queue>.integration.ts  # Real message broker publish / consume
│       └── api/
│           └── <endpoint>.integration.ts  # HTTP-level integration (supertest / httptest)
├── contract/
│   ├── pacts/
│   │   ├── consumer/
│   │   │   └── <consumer>-<provider>.pact.ts  # Consumer-driven contract tests
│   │   └── provider/
│   │       └── <provider>.verify.ts           # Provider verification tests
│   ├── schema/
│   │   ├── <api>.schema.test.ts               # OpenAPI schema validation tests
│   │   └── problem.contract.test.ts           # RFC 9457 Problem error-body contract (against the reusable Problem $ref)
│   └── pact-broker.config.ts                  # Pact Broker connection + can-i-deploy config
├── e2e/
│   ├── api/
│   │   ├── flows/
│   │   │   └── <user-flow>.e2e.ts     # Multi-step API workflow tests
│   │   ├── smoke.e2e.ts               # Critical-path smoke tests
│   │   └── setup.ts                   # API E2E auth helpers, base URLs
│   └── ui/
│       ├── pages/                     # Page Object Models
│       │   └── <page>.page.ts
│       ├── flows/
│       │   └── <user-flow>.spec.ts    # Playwright / Cypress user flow specs
│       ├── visual/
│       │   └── <component>.visual.ts  # Visual regression snapshot tests
│       └── playwright.config.ts       # Or cypress.config.ts
├── performance/
│   ├── load-tests/
│   │   └── <scenario>.k6.js           # k6 load test scripts (sustained load)
│   ├── stress-tests/
│   │   └── <scenario>.k6.js           # k6 stress test scripts (breaking point)
│   ├── spike-tests/
│   │   └── <scenario>.k6.js           # k6 spike test scripts (sudden burst)
│   ├── baselines/
│   │   └── <scenario>.baseline.json   # Expected p50/p95/p99 latency, throughput
│   ├── compare-baseline.js            # Runner devops invokes via `node tests/performance/compare-baseline.js` — reads baselines/<scenario>.baseline.json + budget, exits non-zero on regression
│   └── thresholds.js                  # k6 thresholds DERIVED FROM docs/architecture/performance-budget.yaml (never hardcoded)
├── fixtures/
│   ├── factories/
│   │   └── <entity>.factory.ts        # Test data factories (fishery / factory-girl pattern)
│   ├── seed-data/
│   │   ├── <entity>.seed.json         # Static seed data for integration / E2E
│   │   └── seed-runner.ts             # Script to load seed data into test DBs
│   └── mocks/
│       ├── <external-api>.mock.ts     # External API mock servers (MSW / nock)
│       └── <service>.stub.ts          # Internal service stubs
├── flags/
│   └── <flag>.matrix.test.ts          # On/off + provider-down safe-default matrix, parameterized over config/feature-flags.yaml
├── mutation/
│   └── stryker.config.json            # (or mutmut/PIT/go-mutesting config) — scoped to critical modules, gating min score
└── coverage/
    └── thresholds.json                # Single source for coverage numbers — WIRED into the runner (vitest/jest threshold, pytest --cov-fail-under, JaCoCo rule, go-cover gate) so `make test` exits non-zero on breach; includes patch threshold
```

### Workspace Output (`Shipyard/qa-engineer/`)

```
Shipyard/qa-engineer/
├── test-plan.md                        # Master test plan with traceability matrix
├── coverage-report.md                  # Coverage analysis and findings
└── findings.md                         # QA findings and recommendations
```

---

## Phases

Execute each phase sequentially. Do NOT skip phases. Each phase builds on the outputs of the previous one.

### Parallel Execution Strategy

After Phase 1 (Test Planning), Phases 2-6 run in parallel — each test type is independent:

```python
# After test plan is written, spawn all test types simultaneously:
Agent(prompt="Write unit tests following Phase 2 rules. Read test-plan.md for traceability. Write to tests/unit/.", ...)
Agent(prompt="Write integration tests following Phase 3 rules. Read test-plan.md. Write to tests/integration/.", ...)
Agent(prompt="Write contract tests following Phase 4 rules. Read test-plan.md. Write to tests/contract/.", ...)
Agent(prompt="Write E2E tests following Phase 5 rules. Read test-plan.md. Write to tests/e2e/.", ...)
Agent(prompt="Write performance tests following Phase 6 rules. Read test-plan.md. Write to tests/performance/.", ...)
```

Wait for all 5 agents to complete, then run Phase 7 (Test Infrastructure) sequentially — it needs all test files to configure CI.

**Why this works:** Each test type reads source code independently and writes to its own directory. No conflicts. The test plan from Phase 1 provides shared context.

**Execution order:**
1. Phase 1: Test Planning (sequential — foundational)
2. Phases 2-6: Unit + Integration + Contract + E2E + Performance (PARALLEL)
3. Phase 7: Test Infrastructure (sequential — needs all test files)

---

### Phase 1 — Test Planning

**Goal:** Produce a traceability matrix linking every BRD acceptance criterion to concrete test cases, categorized by test type.

**Inputs to read:**
- BRD / PRD acceptance criteria (every GIVEN/WHEN/THEN or equivalent)
- `api/` API contracts (OpenAPI specs, AsyncAPI specs)
- `schemas/` data models and `docs/architecture/` sequence diagrams
- `services/` service structure (list all services, handlers, repos)
- `frontend/` component and page structure (if frontend exists; otherwise skip frontend inputs)

**Actions:**
1. Extract every acceptance criterion and assign a unique ID (AC-001, AC-002, ...).
2. For each criterion, determine which test types are required (unit, integration, contract, e2e, performance).
3. Identify all services, modules, and components that need test coverage.
4. Identify all external dependencies that require mocking or test containers.
5. Identify critical user flows for E2E coverage.
6. Identify performance-sensitive endpoints for load testing; read `docs/architecture/performance-budget.yaml` so k6 thresholds derive from it (never hardcode 500ms).
7. Define coverage thresholds per service (lines, branches, functions) AND the patch-coverage threshold (~80%) — these become the FAILING gate in Phase 7, not a passive JSON file.
8. Identify **critical modules** (money/billing, authz predicates, validators, parsers, serializers, domain invariants) that require mutation testing + property/fuzz tests (Test Quality Gates).
9. If `config/feature-flags.yaml` exists, list every flag key for the feature-flag test matrix (on/off + provider-down safe default).

**Output:** Write `Shipyard/qa-engineer/test-plan.md` with the following sections:
- **Scope** — What is being tested, what is explicitly out of scope
- **Test Strategy** — Test pyramid approach, which test types cover which risk areas
- **Traceability Matrix** — Table mapping AC-ID to test case IDs, test type, and priority
- **Environment Requirements** — Containers, external services, env vars needed
- **Coverage Targets** — Per-service and global coverage gates
- **Risk Register** — Areas with high complexity or insufficient testability

---

### Phase 2 — Unit Tests

**Goal:** Test each service's business logic, handlers, and repositories in isolation with full mocking of external dependencies.

**Inputs to read:**
- `services/` source code for each service
- The test plan from Phase 1

**Rules:**
1. One test file per source file. Mirror the source directory structure under `tests/unit/<service>/`.
2. Mock ALL external dependencies: databases, caches, message brokers, HTTP clients, other services.
3. Use dependency injection or module mocking — never patch globals.
4. Test the happy path, error paths, edge cases, and boundary values for every public function.
5. For handlers/controllers: test request parsing, validation error responses, correct status codes, response body shape.
6. For services/domain logic: test business rule enforcement, state transitions, calculation correctness.
7. For repositories: test query construction, parameter binding, result mapping (with mocked DB driver).
8. For validators: test every validation rule, including null, empty, boundary, and malformed inputs.
9. Every test must have a descriptive name that reads as a specification: `it("should return 404 when order does not exist for the given user")`.
10. Use factories from `tests/fixtures/factories/` for test data — never inline large object literals.
11. Assert on specific values, not just truthiness. Prefer `toEqual` over `toBeTruthy`.
12. Test error types and messages, not just that an error was thrown.

**Output:** Write test files to `tests/unit/<service>/`.

Also write factories to `tests/fixtures/factories/` as you discover entity shapes.

---

### Phase 3 — Integration Tests

**Goal:** Test service interactions with real dependencies using testcontainers or docker-compose.

**Inputs to read:**
- `services/` database migrations, schemas, connection configs
- `docs/architecture/` infrastructure requirements (which DBs, caches, brokers)
- The test plan from Phase 1

**Rules:**
1. Write `tests/integration/docker-compose.test.yml` with containers for every real dependency (PostgreSQL, Redis, Kafka, Elasticsearch, etc.). Pin exact image versions.
2. Write `tests/integration/setup.ts` with global before/after hooks: start containers, run migrations, seed base data, tear down after suite.
3. Each integration test file connects to real containers — no mocks for the dependency under test.
4. Test actual SQL queries against a real database with realistic data volumes (not just 1 row).
5. Test cache read/write/eviction with a real Redis instance.
6. Test message publishing and consumption with a real broker.
7. Test API endpoints with real HTTP calls (supertest / httptest) against a running server.
8. Each test must clean up its own data. Use transactions with rollback, or truncate tables in afterEach.
9. Tests must be parallelizable — use unique identifiers to avoid cross-test data collisions.
10. Test failure modes: connection timeouts, constraint violations, concurrent writes, deadlocks.

**Output:** Write test files to `tests/integration/<service>/`.

Write `docker-compose.test.yml` and `setup.ts` to `tests/integration/`.

---

### Phase 4 — Contract Tests

**Goal:** Verify API consumers and providers agree on request/response schemas and that implementations conform to OpenAPI specifications.

**Inputs to read:**
- `api/` OpenAPI specs and AsyncAPI specs
- `services/` API route definitions, request/response DTOs
- `frontend/` API client calls and expected response shapes (if frontend exists; otherwise skip consumer-side frontend contracts)

**Rules:**
1. For each API consumer (frontend, other services), write a Pact consumer test that defines the expected interactions.
2. For each API provider, write a Pact provider verification test that replays consumer expectations against the real provider.
3. Write schema validation tests that load the OpenAPI spec and validate every endpoint's actual response against the schema.
4. Test backward compatibility: if there are versioned APIs, verify old consumers still work with new providers.
5. For async APIs (events, messages), write contract tests for message schemas using AsyncAPI specs.
6. Configure Pact Broker connection in `pact-broker.config.ts` (even if the broker URL is a placeholder). Wire the **`pact-broker can-i-deploy` deployment gate** into the contract CI stage — see "Contract Deployment Gate" — and surface it as `contract_can_i_deploy` in the receipt.
7. Contract tests must fail if a required field is removed, a type changes, or a new required field is added without consumer agreement.
8. **Error-response contract (RFC 9457):** every 4xx/5xx interaction asserts the body is `application/problem+json` matching the reusable `Problem` schema (owned by solution-architect) — `{ type, title, status, detail, instance }` plus extensions `trace_id` and `errors[]`. Validate against the OpenAPI `Problem` `$ref`, and assert the `type`/error code comes from the error-catalog module (the single source for runtime + docs) — not an ad-hoc string. A bare `{ code, message }` envelope is a contract failure.

**Output:** Write contract tests to `tests/contract/`.

---

### Phase 5 — E2E Tests

**Goal:** Test critical user flows end-to-end through the full stack.

**Inputs to read:**
- BRD / PRD user stories and acceptance criteria (especially the critical path)
- `frontend/` pages and navigation flow (if frontend exists; otherwise API-only E2E)
- `services/` API endpoints
- The test plan from Phase 1 (critical user flows identified)

**Rules:**
1. Identify the 5-10 most critical user flows (signup, login, core CRUD, payment, etc.).
2. For API E2E: chain multiple API calls that represent a complete user journey. Use real auth tokens. Validate side effects (DB state, emails sent, events published).
3. For UI E2E (skip if frontend not found): use Page Object Model pattern. Each page gets a class in `tests/e2e/ui/pages/`.
4. UI tests must use resilient selectors: `data-testid` attributes, ARIA roles — never CSS classes or DOM structure.
5. Write a smoke test suite (`smoke.e2e.ts`) that covers the absolute minimum "is the app alive" checks. This runs on every deploy.
6. E2E tests must be idempotent — running them twice produces the same result.
7. Include setup/teardown that creates test users, seeds required data, and cleans up after.
8. Add explicit waits for async operations — never use arbitrary `sleep()` calls.
9. For visual regression (skip if frontend not found): capture screenshots of key pages and compare against baselines.
10. Configure test timeouts generously (30s+ per test) — E2E is slow by nature.
11. **Cross-boundary journey testing** (boundary-safety protocol pattern 5): For every multi-system flow (auth, payment, email, webhook), write at least one E2E test that traces the COMPLETE journey from user action to final state. Auth test must verify: unauthenticated user visits protected page → redirected to login → authenticates → redirected back to original page → sees authenticated content. Payment test must verify: user clicks pay → payment provider processes → callback fires → order status updates → user sees confirmation. Do NOT just test individual hops — test the full chain.
12. **Framework navigation correctness**: Verify that no `<Link>` or client-side `navigate()` targets API routes, external URLs, or auth endpoints. These must use raw `<a href>` or `window.location` for full HTTP requests.

**Output:** Write E2E tests and page objects to `tests/e2e/`. Write Playwright or Cypress config.

---

### Phase 6 — Performance Tests

**Goal:** Establish performance baselines and create load/stress test scripts for performance-sensitive endpoints.

**Inputs to read:**
- `docs/architecture/` NFRs (latency targets, throughput requirements, SLOs)
- `services/` API endpoints (especially high-traffic ones)
- The test plan from Phase 1 (performance-sensitive areas)

**Rules:**
1. Write k6 scripts (JavaScript). Each script targets a specific scenario (e.g., "user browsing products", "checkout flow under load").
2. Load tests: simulate sustained normal traffic. Define realistic ramp-up patterns (e.g., 0 -> 100 VUs over 2 min, hold 10 min, ramp down).
3. Stress tests: find the breaking point. Ramp VUs aggressively until error rate exceeds 5% or p99 exceeds SLO.
4. Spike tests: simulate sudden traffic bursts (0 -> 500 VUs in 10 seconds).
5. **Define thresholds by READING `docs/architecture/performance-budget.yaml` — never hardcode `< 500`.** Encode them in `tests/performance/thresholds.js` derived from the budget (see "Performance & Feature-Flag Tests"). Tag metrics by the templated `route` so they join to the `http_request_duration_seconds` / `http_requests_total` instruments in `observability-contract.md`.
6. Write baseline JSON files (`tests/performance/baselines/<scenario>.baseline.json`) that record expected performance under normal load. **Also EMIT the comparison runner `tests/performance/compare-baseline.js`** — the exact script devops invokes as `node tests/performance/compare-baseline.js`. It reads every `tests/performance/baselines/<scenario>.baseline.json` and the budget, compares the latest k6 run, and **exits non-zero on regression** → sets `perf_baseline_regression: true` in the receipt. devops calls this script verbatim; do not rename it or split it into a per-scenario `baseline.json`.
7. Use realistic test data — not the same request repeated. Parameterize with CSV data files or k6 SharedArray. Use only synthetic, PII-free data (Test-Data Lifecycle rules).
8. Include authentication in test scripts (token generation, session management).
9. Test both read-heavy and write-heavy endpoints separately.
10. Add custom metrics for business-critical operations — but for HTTP RED metrics use the contract names (`http_requests_total`, `http_request_duration_seconds`, `http_requests_in_flight`); never invent a metric name no service emits.

**Output:** Write k6 scripts to `tests/performance/`. Write baseline files to `tests/performance/baselines/<scenario>.baseline.json` and the comparison runner to `tests/performance/compare-baseline.js`.

---

### Phase 7 — Test Infrastructure

**Goal:** Configure CI test execution, coverage enforcement, and test reliability tooling.

**Inputs to read:**
- All test files generated in Phases 2-6
- Coverage thresholds from the test plan
- Project CI/CD system (GitHub Actions, GitLab CI, etc.)

**Actions:**
1. **Coverage is a FAILING gate, not a passive JSON file.** Write `tests/coverage/thresholds.json` as the single source of the numbers:
   ```json
   {
     "global": { "lines": 80, "branches": 75, "functions": 80, "statements": 80 },
     "services": {
       "<service-name>": { "lines": 85, "branches": 80, "functions": 85, "statements": 85 }
     },
     "patch": { "lines": 80 }
   }
   ```
   Then **WIRE it into the runner so `make test` exits non-zero on breach** — a JSON file nothing reads does NOT count. Per language, derive the runner config from these numbers (do not hardcode a second copy of the thresholds — generate from `thresholds.json` or keep the runner config the single source and have CI assert they match):
   - **Vitest/Jest:** `coverage.thresholds` (global + per-glob `100`-style entries) in `vitest.config.ts` / `jest.config.js` — runner exits non-zero below threshold. `make test` runs `vitest run --coverage` / `jest --coverage --coverageThreshold` with **no `|| true`**.
   - **pytest:** `--cov-fail-under=<lines>` (and `fail_under` in `[tool.coverage.report]` of `pyproject.toml`); branch coverage via `--cov-branch`.
   - **JaCoCo (JVM):** a `jacocoCoverageVerification` rule (`LINE`/`BRANCH` `minimum`) bound to `check` — Gradle/Maven fails the build below the limit.
   - **Go:** a `go test ./... -coverprofile` step plus a gate script that parses `go tool cover -func` total and `exit 1` below the threshold.
   - The `make test` target MUST propagate the runner's non-zero exit (no `|| true`, no `continue-on-error`). CI invokes `make test` as a required step.
   - **EMIT the `coverage-check` and `patch-coverage` Makefile targets** (CANON #8 — qa owns them). Append them to the **root `Makefile`** (software-engineer generates the base Makefile in phase 05; do NOT create a second Makefile). The devops CI gates invoke `make coverage-check` and `make patch-coverage` verbatim, so both targets MUST exist and MUST exit non-zero on breach — **no `|| true`, no `continue-on-error`**:
     ```makefile
     # appended by qa-engineer — coverage gates wired to tests/coverage/thresholds.json
     coverage-check:
     	# runs the coverage runner (vitest/jest threshold | pytest --cov-fail-under | JaCoCo rule | go-cover gate)
     	# against tests/coverage/thresholds.json; exits non-zero below the matching gate
     	$(COVERAGE_CMD)

     patch-coverage:
     	# diff-scoped gate (diff-cover / Codecov patch / vitest --changed) at thresholds.json:patch.lines (~80%)
     	# exits non-zero when new/changed lines fall below the patch threshold
     	$(PATCH_COVERAGE_CMD)
     ```
   - **Patch-coverage required PR check:** the `make patch-coverage` target (above) wraps the diff-scoped coverage gate (`diff-cover` / Codecov/Coveralls patch status / `vitest --changed`); wire it as a **required GitHub status check at ~80%** (`thresholds.json:patch.lines`) — it fails the PR when new/changed lines fall below the patch threshold. NO `|| true`, NO `continue-on-error: true`.
2. Write `.github/workflows/test.yml` (GitHub Actions templates first, per the chosen default) with:
   - **Unit test stage** — runs first, fast, no containers. `make test` — fails (non-zero) on coverage threshold breach (item above). NO `|| true`.
   - **Patch-coverage check** — required PR status at ~80% on changed lines (item above).
   - **Integration test stage** — starts docker-compose dependencies (pinned image **digests**, item 4 below), runs integration suite, tears down.
   - **Contract test stage** — runs Pact tests, publishes pacts to the broker, AND runs the **`pact-broker can-i-deploy` deployment gate** (item 4 below) — its non-zero exit blocks deploy.
   - **E2E test stage** — deploys to test environment, runs smoke + full E2E suite.
   - **Performance test stage** — runs k6 against staging; the script's own thresholds (read from `performance-budget.yaml`, Phase 6) fail the stage on baseline regression. NO `|| true`.
   - **Mutation test stage (NIGHTLY, gating)** — `mutation-nightly.yml` on a `schedule:` cron; runs Stryker/mutmut/PIT/go-mutesting on critical modules and **fails below the configured minimum score** (Test Quality Gates section). Nightly (not per-PR) because mutation runs are slow; the failing run is still a gate, not advisory.
   - **Randomized test order** — run the unit/integration suites with randomized order (`--shuffle` / `-p randomly` / `-shuffle=on`) so order-dependence fails CI, not prod.
   - Parallel execution: split unit and integration tests across multiple CI runners by service.
   - Test result artifacts: JUnit XML reports, coverage + patch-coverage reports, mutation reports, k6 JSON results — the receipt's machine-readable fields are parsed from these.
   - Flaky test detection: track test pass/fail history, quarantine tests with >5% flake rate. A quarantined test is a remediation finding, not a silent skip.
   - Retry policy: retry failed E2E tests up to 2 times before marking as failed. **Unit/integration tests are NOT retried** — a non-deterministic unit test is a determinism finding (Test Determinism section), not something to paper over with retries.
3. Write seed data runner to `tests/fixtures/seed-data/seed-runner.ts`.
4. Write external API mock configurations to `tests/fixtures/mocks/`.

**Output:** Write CI config to `.github/workflows/test.yml` and `.github/workflows/mutation-nightly.yml`, append the `coverage-check` and `patch-coverage` targets to the root `Makefile`, and write coverage thresholds and test infrastructure to `tests/`.

---

## Test Quality Gates

Line coverage proves a line *ran*, not that a test would *catch a bug on it*. These gates measure whether the tests have teeth. Both are **default-on** per the chosen policy (critical modules); they are FAILING gates wired into CI, not advisory reports.

### Mutation Testing (NIGHTLY gating job)

Mutation testing seeds faults (flip `<` to `<=`, drop a `return`, negate a boolean) and fails the suite if the tests still pass — a surviving mutant is an untested behavior. Run it **scoped to critical modules** (money/billing, authz predicates, validators, parsers/serializers, domain invariants — not the whole tree, which is too slow) on the **nightly `mutation-nightly.yml` schedule cron**, with a minimum score that **exits non-zero on breach**:

| Stack | Tool | Config | Gate |
|-------|------|--------|------|
| TS/JS | **Stryker** | `stryker.config.json` — `mutate` globs the critical modules; `thresholds.break` set | `stryker run` exits non-zero below `thresholds.break` |
| Python | **mutmut** (or `cosmic-ray`) | `setup.cfg`/`pyproject.toml` `[mutmut]` `paths_to_mutate` = critical modules | wrapper parses `mutmut results` score, `exit 1` below min |
| JVM | **PIT** | `pitest` `targetClasses` = critical packages; `mutationThreshold` | Maven/Gradle fails below `mutationThreshold` |
| Go | **go-mutesting** | scope to critical packages | wrapper parses score, `exit 1` below min |

Record the score as `mutation_score` in the receipt. The minimum (e.g. 60% overall, higher for money/authz) lives next to the tool config so it is one source.

### Property-Based & Fuzz Testing (mandatory, default-on)

Example-based tests check the cases you thought of; property-based tests generate thousands of inputs and assert an **invariant** (`parse(serialize(x)) == x`, `total == sum(line_items)`, `authorize(user, res)` is monotone in permissions, money never goes negative). These are **mandatory** for the high-risk surfaces below — a critical module without a property test is a finding:

| Surface | Invariants to assert | Tool by stack |
|---------|----------------------|----------------|
| **Validators** | accepts iff schema-valid; rejects malformed/boundary/null; never throws on attacker input | fast-check / Hypothesis / jqwik / proptest |
| **Parsers** | round-trip `parse∘serialize == id`; never panics; bounded output | fast-check / Hypothesis / jqwik / proptest + **native fuzzing** |
| **Serializers** | round-trip both directions; stable ordering; escapes injection chars | same |
| **Money / billing** | associativity/commutativity of sums; no negative balances; rounding within tolerance; currency never mixed | same |
| **Authz predicates** | deny-by-default; monotone in granted permissions; no privilege escalation across tenants | same |

- **Native fuzzing** is required for byte-level parsers/deserializers and any untrusted-input boundary: `go test -fuzz`, `cargo fuzz`/`libFuzzer`, Jazzer (JVM), Atheris (Python), `jest-fuzz`/fast-check for JS. Seed the corpus from real + crashing inputs; failing inputs are committed as regression cases.
- Property/fuzz tests obey the determinism rules below — **seed the generator** (`fast-check` `seed`, Hypothesis `derandomize`/`@seed`) and print the seed on failure so a counterexample reproduces. A flaky property test is a determinism finding.
- These run in the normal unit stage (fast, bounded runs) and gate via the coverage + mutation jobs; the deep fuzz campaigns run in the nightly job alongside mutation.

---

## Contract Deployment Gate, Determinism & Test Data

### Pact `can-i-deploy` deployment gate (item: Contract)

Pact consumer/provider verification (Phase 4) proves the contracts *match*; `can-i-deploy` proves it is *safe to release this version*. Add a **deployment gate** in the contract CI stage:

```bash
pact-broker can-i-deploy \
  --pacticipant "$SERVICE" --version "$GIT_SHA" \
  --to-environment production --retry-while-unknown 6 --retry-interval 10
# non-zero exit = a consumer/provider this version must talk to has NOT verified → BLOCK deploy
```

Surface its result as `contract_can_i_deploy` in the receipt; `false` blocks `production-ready`. No `|| true`. The broker URL/token come from env/CI secrets, configured once in `pact-broker.config.ts`.

### Test Determinism (rules — flaky tests are findings, not retries)

A test that fails 1-in-50 erodes trust in the whole suite. Every test the QA Engineer writes MUST be deterministic:

- **Frozen clock** — inject a fixed clock / use fake timers (`vi.useFakeTimers`, `freezegun`, `Clock.fixed`, a `Clock` port). Never read wall-clock in an assertion.
- **Seeded RNG** — seed every generator (test data factories, property-test generators, shuffles); print the seed so failures reproduce.
- **No `sleep()`** — replace arbitrary sleeps with explicit wait-for-condition polling (element/visibility, API response, DB state). Sleeps are banned in unit/integration; E2E uses framework auto-waiting.
- **Pinned image DIGESTS** — testcontainers and `docker-compose.test.yml` pin images by **`@sha256:` digest**, not floating tags (`postgres:16` drifts; `postgres@sha256:…` does not). Reproducible across machines and time.
- **Hermetic network** — no test hits the public internet. External APIs are stubbed (MSW/nock/WireMock) or run as a pinned-digest container. A test that needs `api.stripe.com` is non-hermetic and must be rewritten.
- **Randomized order** — run suites with randomized order in CI (`--shuffle` / `pytest-randomly` / `go test -shuffle=on`) so hidden ordering coupling fails the build, not production.

A test that violates these is a **determinism finding** written to `findings.md` — fix the test, do NOT mask it with a retry (retries are E2E-only, Phase 7).

### Test-Data Lifecycle

- **Schema-per-worker isolation** — each parallel test worker gets its own database schema/namespace (`test_w<worker_id>`), created in setup and dropped in teardown. No shared mutable schema → no cross-worker collisions, full parallelism.
- **Synthetic, PII-free data only** — factories and seed data generate synthetic values (Faker with a seeded locale); NEVER copy production data, real emails, real card numbers, or real PII into tests. This aligns with the observability-contract PII rules and `security-testing-protocol.md`. Card-like fields use documented test PANs only.
- Each test owns its data (transaction rollback or scoped truncate in teardown); reference rows by business identifiers, never auto-increment IDs.

---

## Performance & Feature-Flag Tests (gates, not docs)

### k6 thresholds READ FROM the performance budget (never hardcoded)

`tests/performance/thresholds.js` and each k6 scenario MUST derive their pass/fail thresholds from **`docs/architecture/performance-budget.yaml`** (owned by solution-architect; frontend/qa/sre/devops all read the same numbers). **Do NOT hardcode 500ms.** Read the budget at test-build time and encode k6 thresholds that map directly onto the contract's runtime instruments:

```javascript
// tests/performance/thresholds.js — generated from docs/architecture/performance-budget.yaml
// budget["POST /orders"] = { p95_ms: 500, p99_ms: 1200, throughput_rps: 100, error_rate_pct: 1.0 }
export const thresholds = {
  // http_req_duration is k6's measure of http_request_duration_seconds (contract instrument)
  'http_req_duration{route:POST /orders}': ['p(95)<500', 'p(99)<1200'], // ms, from budget
  'http_req_failed{route:POST /orders}':   ['rate<0.01'],               // = error_rate_pct/100
  'http_reqs':                             ['rate>=100'],               // throughput_rps
};
```

- Tag k6 metrics by the **templated `route`** (e.g. `/orders`, `POST /orders`) — the SAME `route` string used by `http_requests_total` / `http_request_duration_seconds` in `observability-contract.md`, so a load-test breach and a production dashboard point at the same dimension. Never tag by raw URL with IDs.
- **Baseline-regression encoded as a threshold:** the emitted runner `tests/performance/compare-baseline.js` (invoked by devops as `node tests/performance/compare-baseline.js`) compares the run against `tests/performance/baselines/<scenario>.baseline.json`; a regression beyond the budget fails the run (non-zero exit) → `perf_baseline_regression: true` in the receipt → blocks `production-ready`. When the budget file is missing, treat perf gating as a Critical missing input (do not invent 500ms).

### Feature-flag test matrix (from `config/feature-flags.yaml`)

Every flag in **`config/feature-flags.yaml`** (the OpenFeature registry: `{ key, type, owner, default, created, removal_by }`, client at `libs/shared/feature-flags/`) gets a test matrix so a toggle can't ship a broken state:

1. **On / Off state matrix** — for each flag key, run the affected behavior with the flag forced **on** and forced **off**; both states must pass. Parameterize the suite over the registry so a newly-added flag is automatically covered (a flag with no on/off test is a finding).
2. **Safe-default-when-provider-down** — simulate the OpenFeature provider being unreachable and assert each flag resolves to its registry **`default`** (fail-static), and the behavior matches the off/safe path — mirroring software-engineer's provider-down test. The provider outage must NOT throw and NOT flip behavior.
3. **Stale-flag check** — assert no flag is past its `removal_by` date (or surface it as a finding) so temporary flags don't become permanent.

---

## Common Mistakes

| # | Mistake | Why It Fails | What to Do Instead |
|---|---------|-------------|-------------------|
| 1 | Writing tests inside `services/` or `frontend/` source directories | Pollutes source directories; violates pipeline separation | Always write tests to `tests/` at project root exclusively |
| 2 | Testing implementation details instead of behavior | Tests break on every refactor, providing no safety net | Test public interfaces, inputs, and outputs — not private methods or internal state |
| 3 | Using `any` type or skipping type assertions in test mocks | Mocks drift from real interfaces silently; tests pass but code is broken | Type mocks against the real interface; use `jest.Mocked<typeof RealService>` or equivalent |
| 4 | Sharing mutable state between tests | Tests pass in isolation but fail when run together; order-dependent results | Reset state in beforeEach; use factory functions that return fresh instances |
| 5 | Hardcoding connection strings, ports, or URLs in test files | Tests break in CI, on other machines, or when container ports change | Use environment variables with sensible defaults; read from docker-compose labels |
| 6 | Writing integration tests that mock the dependency under test | You are just writing unit tests with extra steps; real bugs slip through | If testing DB queries, use a real database. If testing cache, use real Redis. Mock only the things NOT under test |
| 7 | E2E tests that depend on specific database IDs or auto-increment values | Tests break when seed data changes or when run against a non-empty database | Create test data as part of test setup; reference by unique business identifiers, not DB IDs |
| 8 | Performance test scripts with a single hardcoded request | Does not simulate real traffic patterns; results are misleading | Parameterize requests with varied data; simulate realistic user think-time with `sleep(Math.random() * 3)` |
| 9 | Coverage thresholds set to 100% | Encourages meaningless tests written just to hit the number; blocks legitimate PRs | Set realistic thresholds (80-85% lines, 75-80% branches); focus on critical path coverage |
| 10 | Ignoring test execution time | Slow test suites get skipped by developers; CI feedback loops become painful | Parallelize tests by service; keep unit suite under 60 seconds; keep integration suite under 5 minutes |
| 11 | Not testing error paths and failure modes | Happy-path-only tests miss the bugs that actually cause production incidents | For every success test, write at least one failure test: invalid input, timeout, auth failure, conflict |
| 12 | Writing E2E tests with `sleep()` for async waits | Flaky on slow CI runners; wastes time on fast ones | Use explicit wait-for conditions: poll for element visibility, API response, or DB state change |
| 13 | Contract tests that only check status codes | Schema changes, missing fields, and type mismatches go undetected | Validate full response body shape, field types, required fields, and enum values against the contract |
| 14 | No seed data strategy — each test creates its own world from scratch | Integration and E2E suites become extremely slow; redundant setup logic everywhere | Build a shared seed-data layer with factories and a seed runner; tests add only their unique data on top |
| 15 | Generating test files without reading the actual implementation first | Tests reference nonexistent functions, wrong parameter names, or incorrect module paths | Always read the source file before writing its test file; match imports, function signatures, and error types exactly |
| 16 | Auth E2E tests that only check "token returned" | Misses redirect bugs, callback misconfig, and infinite loops that only appear in the full browser flow | Test the complete journey: visit protected page → redirect to login → authenticate → land on original page with authenticated state |
| 17 | Not testing cross-system flows end-to-end | Payment tests that check "Stripe returns success" but never check "order status is updated and user sees confirmation" miss the integration point bugs | For every multi-system flow (auth, payment, webhook), trace from user action to final visible state |
| 18 | `thresholds.json` as a passive doc nothing reads | Coverage "gate" never fails a build; numbers drift and rot | Wire it into the runner (vitest/jest threshold, pytest `--cov-fail-under`, JaCoCo rule, go-cover gate) so `make test` exits non-zero on breach; no `\|\| true` |
| 19 | Hardcoding k6 thresholds (`p(95)<500`) | Diverges from the single perf source; budget changes don't reach the gate | Read `docs/architecture/performance-budget.yaml` into `tests/performance/thresholds.js`; tag by templated `route` to join the observability instruments |
| 20 | Retrying a flaky unit/integration test to make CI green | Hides a real determinism bug (clock/RNG/order/network) that will surface in prod | Fix the test (frozen clock, seeded RNG, hermetic network, randomized order) and log it as a determinism finding; retries are E2E-only |
| 21 | Trusting line coverage as proof of test quality | A line can run with zero assertions on its behavior | Add mutation testing (nightly, gating, critical modules) + property/fuzz tests on validators/parsers/serializers/money/authz |
| 22 | Writing the receipt metrics from memory or rounding "looks passing" | The orchestrator gates `production-ready` on these exact numbers; fabricated metrics ship broken code | Parse `tests_passing`/`tests_failing`/`coverage_*`/`mutation_score` from real runner/coverage/mutation output; ANY failing test is a remediation finding |
| 23 | Floating image tags in testcontainers / compose | `postgres:16` drifts; a test passes today and fails next month for no code change | Pin by `@sha256:` digest for reproducible, hermetic integration tests |
| 24 | Copying production data (real emails/PII/PANs) into fixtures | Privacy/compliance violation and brittle tests | Generate synthetic, PII-free data with seeded Faker; schema-per-worker isolation; documented test PANs only |

---

## Execution Checklist

Before marking the skill as complete, verify:

- [ ] `Shipyard/qa-engineer/test-plan.md` has a traceability matrix covering every BRD acceptance criterion
- [ ] Every service in `services/` has corresponding unit tests in `tests/unit/`
- [ ] Every repository/data-access module has integration tests with real database containers
- [ ] Every API endpoint has at least one contract test validating its schema
- [ ] The top 5-10 critical user flows have E2E tests
- [ ] At least 3 performance-sensitive endpoints have k6 load test scripts with baselines at `tests/performance/baselines/<scenario>.baseline.json`; thresholds READ FROM `docs/architecture/performance-budget.yaml` (no hardcoded 500ms), tagged by templated `route`; the emitted runner `tests/performance/compare-baseline.js` (devops invokes `node tests/performance/compare-baseline.js`) fails the run on baseline regression
- [ ] `tests/integration/docker-compose.test.yml` + testcontainers pin images by **`@sha256:` digest** (not floating tags)
- [ ] `tests/coverage/thresholds.json` is WIRED into the runner (vitest/jest threshold, pytest `--cov-fail-under`, JaCoCo rule, go-cover gate) so `make test` exits non-zero on breach — verified by observing a non-zero exit, no `|| true`
- [ ] `coverage-check` and `patch-coverage` targets are appended to the root `Makefile` (no second Makefile) and exit non-zero on breach so the devops `make coverage-check` / `make patch-coverage` CI gates resolve
- [ ] Patch-coverage (~80%) is a REQUIRED PR status check (via `make patch-coverage`) with no `|| true` / `continue-on-error`
- [ ] Mutation testing scoped to critical modules runs on the NIGHTLY gating job and fails below the minimum score; `mutation_score` recorded in the receipt
- [ ] Every validator/parser/serializer/money/authz module has property-based tests (+ native fuzzing for byte-level parsers); generators are seeded and print the seed on failure
- [ ] `pact-broker can-i-deploy` deployment gate wired in the contract stage; `contract_can_i_deploy` in the receipt
- [ ] 4xx/5xx contract tests assert RFC 9457 `application/problem+json` against the reusable `Problem` schema; `type` comes from the error-catalog
- [ ] Feature-flag matrix (on/off + provider-down safe default) parameterized over `config/feature-flags.yaml`
- [ ] Test determinism enforced: frozen clock, seeded RNG, no `sleep()` in unit/integration, hermetic network, randomized order in CI; flaky tests logged as findings (not masked by retries)
- [ ] Test data is schema-per-worker isolated and synthetic/PII-free (no production data)
- [ ] `.github/workflows/test.yml` + `.github/workflows/mutation-nightly.yml` orchestrate all stages with parallelization and artifact collection
- [ ] All test factories are in `tests/fixtures/factories/` and reused across test types
- [ ] No test file has hardcoded secrets, credentials, or environment-specific values
- [ ] All tests can run independently and in any order
- [ ] QA receipt emits machine-readable `tests_passing`, `tests_failing`, `coverage_lines`, `coverage_branches`, `mutation_score` (+ `patch_coverage`, `contract_can_i_deploy`, `perf_baseline_regression`) from real tool output
- [ ] ANY failing test is written to `findings.md` as a remediation finding; the only non-remediation exit is a logged "accepted with justification" override receipt
