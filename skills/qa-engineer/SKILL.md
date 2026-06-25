---
name: qa-engineer
description: >
  [drydock internal] Writes and runs tests when you want to verify
  code works — unit, integration, e2e, performance, contract testing.
  Routed via the drydock orchestrator.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task, Skill, WebSearch, WebFetch, Bash(bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" *), Bash(bash "${CLAUDE_SKILL_DIR}/../_shared/load-file.sh" *)
---

# QA Engineer Skill

## Protocols

!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" ux-protocol`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" input-validation`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" tool-efficiency`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" visual-identity`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" freshness-protocol`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" receipt-protocol`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" boundary-safety`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" conflict-resolution`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" grounding-protocol`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-protocol.sh" observability-contract`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-file.sh" .drydock.yaml`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-file.sh" drydock/.orchestrator/codebase-context.md`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-file.sh" docs/architecture/performance-budget.yaml`
!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-file.sh" config/feature-flags.yaml`

**Fallback (if protocols not loaded):** Use AskUserQuestion with options (never open-ended), "Chat about this" last, recommended first. Work continuously. Print progress constantly. Validate inputs before starting — classify missing as Critical (stop), Degraded (warn, continue partial), or Optional (skip silently). Use parallel tool calls for independent reads. Use Grep to find the relevant lines, then Read with offset/limit.

## Autonomy Level

!`bash "${CLAUDE_SKILL_DIR}/../_shared/load-file.sh" drydock/.orchestrator/settings.md`

| Level | Behavior |
|------|----------|
| **Autopilot** | Fully autonomous. Generate all test suites with sensible coverage targets. Report test plan in output. |
| **Copilot** | Surface 1-2 critical decisions — coverage targets, e2e scope (which flows to test), performance thresholds. |
| **Checkpoint** | Show full test plan before implementing. Ask about test data strategy, which edge cases matter most, performance SLAs to validate. Show test results summary per category. |
| **Manual** | Walk through test plan per service. User reviews test scenarios before implementation. Show each test category's results. Ask about flaky test tolerance and retry strategy. |

## Progress Output

Follow `drydock/.protocols/visual-identity.md`. Print structured progress throughout execution.

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

The orchestrator gates `production-ready` on QA. It does not read prose — it reads the **machine-readable `metrics` block of the QA receipt** (`drydock/.orchestrator/receipts/{task_id}-qa-engineer.json`, schema per `receipt-protocol.md`). These exact keys are MANDATORY and are extracted by the gate; emit them from real tool output (the test runner's JSON/JUnit summary + coverage report + mutation report), never from memory:

```json
{
  "task": "Tqa",
  "agent": "qa-engineer",
  "phase": "HARDEN",
  "status": "complete",
  "artifacts": ["drydock/qa-engineer/test-plan.md", "tests/coverage/thresholds.json", "..."],
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

**Failing test = remediation finding, ALWAYS.** There is NO soft "if failures > X% flag to the user" path. ANY failing test (`tests_failing > 0`) is written into `drydock/qa-engineer/findings.md` as a remediation finding and feeds the HARDEN remediation chain (`receipt-protocol.md`) exactly like a Critical finding. Never marshal a green completion while a test is red.

**The only non-remediation exit is an explicit, logged override** (the user chose: BLOCK, WITH an "accepted with justification" override). When the owner consciously ships past a breached gate, do NOT silently pass — capture the decision with AskUserQuestion (predefined options, never open-ended) and write an override receipt to the canonical override path `drydock/.orchestrator/overrides/<gate>-<id>.json` (NOT under `receipts/`) so Gate 3 finds it:

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

A gate with a matching override receipt at `drydock/.orchestrator/overrides/<gate>-<id>.json` stops blocking but the decision is carried into `findings.md`. No override file = the gate stays BLOCKED.

## Brownfield Awareness

If `drydock/.orchestrator/codebase-context.md` exists and mode is `brownfield`:
- **READ existing tests first** — understand test framework, patterns, fixtures, helpers
- **MATCH existing test framework** — if they use pytest, don't introduce jest. If they use Vitest, use Vitest
- **ADD tests alongside existing ones** — don't restructure their test directory
- **Existing tests must still pass** — run the full test suite after adding new tests
- **Reuse existing fixtures and helpers** — don't duplicate test utilities

## Config Paths

Read `.drydock.yaml` at startup. Use these overrides if defined:
- `paths.services` — default: `services/`
- `paths.frontend` — default: `frontend/`
- `paths.tests` — default: `tests/`

## Context & Position in Pipeline

This skill runs AFTER the Software Engineer and Frontend Engineer skills have completed. It expects:

- **`services/` and `libs/`** — Backend services, handlers, repositories, domain models, API route definitions
- **`frontend/`** — UI components, pages, hooks, state management, API client calls
- **`api/`, `schemas/`, `docs/architecture/`** — API contracts (OpenAPI/AsyncAPI specs), data models, sequence diagrams
- **BRD or PRD** — Acceptance criteria, user stories, business rules, edge cases

The QA Engineer does NOT modify source code. It generates test files and test infrastructure to `tests/` at the project root, and test documentation (test plan, reports) to `drydock/qa-engineer/`.

### Graceful Degradation

At startup, check whether `frontend/` (or `paths.frontend` from config) exists. If the frontend directory is not found:
- Skip all frontend-related test phases (UI E2E, visual regression, frontend contract tests, frontend-specific checks).
- Print: `[DEGRADED: frontend not found — skipping frontend tests]`
- Continue with all backend test phases normally.

---

## Output Structure

This skill produces output in two locations: test deliverables (code, configs, fixtures) at `tests/` in the project root, and workspace artifacts (test plan, reports, findings) in `drydock/qa-engineer/`. Never write test files into `services/` or `frontend/` directly.

**Project root (`tests/`)** — top-level dirs and their purpose:
- `unit/<service>/` — handlers, services, repositories, validators, mappers, plus `property/` (property-based/fuzz tests for validators, parsers, serializers, money, authz).
- `integration/` — `docker-compose.test.yml` (pinned dependency containers), `setup.ts` (global setup/teardown), and per-service `db/`, `cache/`, `messaging/`, `api/` real-dependency tests.
- `contract/` — `pacts/consumer/` + `pacts/provider/`, `schema/` OpenAPI + `problem.contract.test.ts` (RFC 9457 Problem `$ref`), `pact-broker.config.ts` (connection + can-i-deploy).
- `e2e/` — `api/` (flows, `smoke.e2e.ts`, setup) and `ui/` (Page Object Models in `pages/`, `flows/`, `visual/`, `playwright.config.ts`/`cypress.config.ts`).
- `performance/` — `load-tests/`, `stress-tests/`, `spike-tests/` (k6 scripts), `baselines/<scenario>.baseline.json`, `compare-baseline.js` (devops invokes `node tests/performance/compare-baseline.js`), `thresholds.js` (DERIVED from `docs/architecture/performance-budget.yaml`).
- `fixtures/` — `factories/` (fishery/factory-girl), `seed-data/` (`*.seed.json` + `seed-runner.ts`), `mocks/` (MSW/nock mock servers + service stubs).
- `flags/<flag>.matrix.test.ts` — on/off + provider-down safe-default matrix, parameterized over `config/feature-flags.yaml`.
- `mutation/stryker.config.json` (or mutmut/PIT/go-mutesting) — scoped to critical modules, gating min score.
- `coverage/thresholds.json` — single source for coverage numbers, WIRED into the runner so `make test` exits non-zero on breach; includes patch threshold.

**Workspace (`drydock/qa-engineer/`)** — `test-plan.md` (master plan + traceability matrix), `coverage-report.md`, `findings.md` (QA findings and remediation).

---

## Phases

Execute each phase sequentially. Do NOT skip phases. Each phase builds on the outputs of the previous one.

### Parallel Execution Strategy

After Phase 1 (Test Planning), Phases 2-6 run in parallel — each test type is independent. After the test plan is written, spawn all test types simultaneously with **bounded foreground fan-out** — up to **3 concurrent** `general-purpose` sub-tasks (Agent tool), batching in groups of 3 if there are more than 3. Do NOT pass isolation/background/mode at call time (not documented Agent-tool parameters; this subagent is already isolated). Sub-task prompts:

> - Write unit tests following Phase 2 (`phases/02-unit-tests.md`) rules. Read `drydock/qa-engineer/test-plan.md` for traceability. Write to `tests/unit/`.
> - Write integration tests following Phase 3 (`phases/03-integration-tests.md`) rules. Read `drydock/qa-engineer/test-plan.md`. Write to `tests/integration/`.
> - Write contract tests following Phase 4 (`phases/04-contract-tests.md`) rules. Read `drydock/qa-engineer/test-plan.md`. Write to `tests/contract/`.
> - Write E2E tests following Phase 5 (`phases/05-e2e-tests.md`) rules. Read `drydock/qa-engineer/test-plan.md`. Write to `tests/e2e/`.
> - Write performance tests following Phase 6 (`phases/06-performance-tests.md`) rules. Read `drydock/qa-engineer/test-plan.md`. Write to `tests/performance/`.

Since there are 5 sub-tasks and the cap is 3 concurrent, run them in batches of 3 (e.g., unit + integration + contract, then E2E + performance). Wait for all 5 agents to complete, then run Phase 7 (Test Infrastructure) sequentially — it needs all test files to configure CI. **Why this works:** each test type reads source code independently and writes to its own directory. No conflicts. The test plan from Phase 1 provides shared context.

**Execution order:** 1. Phase 1 (sequential, foundational) → 2. Phases 2-6 (PARALLEL) → 3. Phase 7 (sequential, needs all test files).

## Phase Index

| Phase | File | When to Load | Purpose |
|-------|------|-------------|---------|
| 1 | phases/01-test-planning.md | Always first (sequential) | Traceability matrix: BRD acceptance criteria → test cases by type; coverage targets; critical modules; perf budget; flag keys |
| 2 | phases/02-unit-tests.md | After Phase 1 (parallel) | Isolated unit tests for handlers, services, repositories, validators with full mocking; factories |
| 3 | phases/03-integration-tests.md | After Phase 1 (parallel) | Real-dependency tests via testcontainers/docker-compose; DB, cache, broker, HTTP |
| 4 | phases/04-contract-tests.md | After Phase 1 (parallel) | Pact consumer/provider + OpenAPI schema validation; RFC 9457 Problem; can-i-deploy gate |
| 5 | phases/05-e2e-tests.md | After Phase 1 (parallel) | Critical user flows end-to-end; cross-boundary journeys; smoke suite; UI Page Objects |
| 6 | phases/06-performance-tests.md | After Phase 1 (parallel) | k6 load/stress/spike scripts; thresholds from perf budget; baselines + compare-baseline.js |
| 7 | phases/07-test-infrastructure.md | After Phases 2-6 (sequential) | CI workflows, coverage/patch gates wired into runner + Makefile, mutation nightly, flaky/retry policy |

## Dispatch Protocol

Read the relevant phase file before starting that phase. Never read all phases at once — each is loaded on demand to minimize token usage.

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

- [ ] `drydock/qa-engineer/test-plan.md` has a traceability matrix covering every BRD acceptance criterion
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
