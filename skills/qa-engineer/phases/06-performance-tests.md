# Phase 6 — Performance Tests

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
