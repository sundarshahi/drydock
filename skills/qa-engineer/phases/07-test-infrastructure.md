# Phase 7 — Test Infrastructure

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
