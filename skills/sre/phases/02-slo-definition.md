# Phase 2: SLO Refinement

## Objective

Transform DevOps monitoring into business-aligned SLOs with actionable error budgets. SRE is the SOLE AUTHORITY on SLO definitions — DevOps implements the thresholds SRE defines, but does not set them.

## Context Bridge

Read Phase 1 findings from `production-readiness/findings.md` to understand known reliability risks before defining SLO targets.

## Contracts You MUST Read First (do not invent names or numbers)

- **`Shipyard/.protocols/observability-contract.md`** — the ONLY metric/log/span names you may query. RED metrics: `http_requests_total{method,route,status_class}` (error rate = `status_class="5xx"` over total — **NOT** `status=~"5.."`), `http_request_duration_seconds` (histogram in **seconds**, with exemplars, exposes `_bucket`/`_sum`/`_count`), `http_requests_in_flight{method,route}`. USE metrics: `<resource>_pool_connections_in_use|_max|_idle`, `<resource>_pool_wait_seconds`, `<resource>_pool_acquire_errors_total`, `broker_consumer_lag{destination,group}`. Every alert expr, recording rule, and dashboard panel below uses these names verbatim. A name absent from the contract is a bug the Production-Ready Gate fails on.
- **`docs/architecture/performance-budget.yaml`** — the ONLY source of latency/throughput/error-rate targets. SLO latency thresholds READ the route's `p99_ms`/`p95_ms` from this file. **Never hardcode 500ms.** If the file is missing, fall back to the observability-contract default buckets and record the assumption in `error-budget-policy.md`.

## Inputs

- `Shipyard/.protocols/observability-contract.md` — canonical metric names (authoritative)
- `docs/architecture/performance-budget.yaml` — latency/throughput/error-rate targets (authoritative)
- `infrastructure/monitoring/` — existing Prometheus rules, Grafana dashboards
- `Shipyard/product-manager/` or requirements — availability promises, user expectations
- Architecture docs — request flow, critical paths, dependency chains
- Phase 1 findings — known reliability risks

## Workflow

### Step 1: Identify SLIs

For each service, identify SLIs using these categories:

- **Availability:** proportion of successful requests (HTTP 5xx exclusion, gRPC status codes)
- **Latency:** proportion of requests faster than threshold (p50, p95, p99)
- **Throughput:** requests per second within acceptable range
- **Correctness:** proportion of responses returning correct data (for data pipelines)
- **Freshness:** proportion of data updated within acceptable staleness window

### Step 2: Generate SLI Definitions

Write `slo/sli-definitions.yaml` with this structure:

```yaml
# Metric names are EXACTLY those in observability-contract.md.
# Error = status_class="5xx" (the contract label is status_class, NOT status).
# Latency `le` is derived from performance-budget.yaml p99_ms / 1000 (seconds) —
# it MUST equal a standard contract bucket boundary; never hardcode a value.
slis:
  - name: api-availability
    service: api-gateway
    type: availability
    description: Proportion of HTTP requests that do not return 5xx
    good_event: http_requests_total{status_class!="5xx"}
    valid_event: http_requests_total
    measurement_window: 28d

  - name: api-latency-p99
    service: api-gateway
    type: latency
    description: Proportion of HTTP requests served within the budgeted p99
    # le READ from performance-budget.yaml: "POST /orders".p99_ms (1200) → 1.2 (seconds)
    good_event: http_request_duration_seconds_bucket{le="1.2"}
    valid_event: http_request_duration_seconds_count
    threshold_source: performance-budget.yaml#api."POST /orders".p99_ms
    measurement_window: 28d

slos:
  - name: api-availability-slo
    sli: api-availability
    # error budget = 1 - target; cross-check against performance-budget error_rate_pct
    target: 99.9
    window: 28d
    consequences: |
      If error budget exhausted: freeze deployments,
      redirect engineering effort to reliability work.

  - name: api-latency-slo
    sli: api-latency-p99
    target: 99.0
    window: 28d
    consequences: |
      If error budget below 25%: require performance review
      for all new features before deployment.
```

> The `le` bucket value MUST be `p99_ms / 1000` of the matching route in `performance-budget.yaml` AND a declared standard bucket boundary (`0.005…10`). If the budget's p99 is not a standard boundary, ADD that boundary to the histogram (coordinate with software-engineer per the contract) — never silently round. `scripts/check-slo-vs-budget.sh` (Production-Ready Gate) fails the build if the threshold drifts from the budget.

### Step 3: Generate Error Budget Policy

Write `slo/error-budget-policy.md` defining:
- Error budget calculation method (1 - SLO target = budget)
- Budget consumption thresholds and corresponding actions
- Who has authority to freeze deployments
- How budget resets (rolling window vs. calendar)
- Exception process for emergency deployments during budget freeze

### Step 4: Generate Burn-Rate Alerts

Write `slo/burn-rate-alerts.yaml` using multi-window, multi-burn-rate alerting (Google SRE workbook method):

All `expr` use `status_class="5xx"` (the contract label) — NOT `status=~"5.."`. Saturation alerts use the USE pool/concurrency instruments verbatim. `promtool check rules` must pass (Production-Ready Gate).

```yaml
groups:
  - name: slo-burn-rate
    rules:
      # Fast burn — 2% budget consumed in 1 hour (page).
      # error ratio uses status_class="5xx" per observability-contract.md.
      - alert: SLOHighBurnRate_Critical
        expr: |
          (
            sum(rate(http_requests_total{status_class="5xx"}[1h]))
            / sum(rate(http_requests_total[1h]))
          ) > (14.4 * (1 - 0.999))
          and
          (
            sum(rate(http_requests_total{status_class="5xx"}[5m]))
            / sum(rate(http_requests_total[5m]))
          ) > (14.4 * (1 - 0.999))
        for: 2m
        labels:
          severity: critical
          slo: api-availability
        annotations:
          summary: "High SLO burn rate — 2% error budget consumed in 1h"
          runbook: "../runbooks/api/high-error-rate.md"

      # Slow burn — 5% budget consumed in 6 hours (ticket)
      - alert: SLOHighBurnRate_Warning
        expr: |
          (
            sum(rate(http_requests_total{status_class="5xx"}[6h]))
            / sum(rate(http_requests_total[6h]))
          ) > (6 * (1 - 0.999))
          and
          (
            sum(rate(http_requests_total{status_class="5xx"}[30m]))
            / sum(rate(http_requests_total[30m]))
          ) > (6 * (1 - 0.999))
        for: 5m
        labels:
          severity: warning
          slo: api-availability
        annotations:
          summary: "Elevated SLO burn rate — 5% error budget consumed in 6h"
          runbook: "../runbooks/api/high-error-rate.md"

  - name: latency-slo
    rules:
      # Latency SLO breach — p99 over the budgeted threshold (le from performance-budget.yaml).
      - alert: LatencySLOBreach
        expr: |
          histogram_quantile(0.99,
            sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
          ) > 1.2   # p99_ms 1200 / 1000 — READ from performance-budget.yaml, not hardcoded
        for: 10m
        labels:
          severity: warning
          slo: api-latency-p99
        annotations:
          summary: "p99 latency over budget"
          runbook: "../runbooks/api/high-latency.md"

  - name: saturation-use
    rules:
      # Concurrency saturation (USE) — in-flight requests climbing.
      - alert: HighInFlightSaturation
        expr: sum(http_requests_in_flight) > 200
        for: 5m
        labels: { severity: warning, slo: api-availability }
        annotations:
          summary: "Request concurrency saturating"
          runbook: "../runbooks/api/high-latency.md"

      # Connection pool exhaustion (USE) — utilization + acquire errors.
      - alert: DBPoolExhaustion
        expr: |
          (
            sum by (pool) (db_pool_connections_in_use)
            / sum by (pool) (db_pool_connections_max)
          ) > 0.9
          or sum by (pool) (rate(db_pool_acquire_errors_total[5m])) > 0
        for: 5m
        labels: { severity: critical, slo: api-availability }
        annotations:
          summary: "DB connection pool near/at exhaustion"
          runbook: "../runbooks/api/dependency-down.md"

      # Broker backlog (USE) — consumer lag growing.
      - alert: BrokerConsumerLagHigh
        expr: max by (destination, group) (broker_consumer_lag) > 1000
        for: 5m
        labels: { severity: warning, slo: api-availability }
        annotations:
          summary: "Broker consumer lag exceeds backlog budget"
          runbook: "../runbooks/api/dependency-down.md"
```

### Step 4b: Generate the Canary Burn-Rate Query (consumed by devops)

SRE OWNS the SLO threshold and the burn-rate query; **devops's canary AnalysisTemplate (Argo Rollouts / Flagger) CONSUMES it**. Emit `slo/burn-rate-query.yaml` as the single contract devops reads — so the canary aborts on the SAME burn-rate math the SLO alerts use, querying the SAME contract metric names. Do NOT let devops re-derive a separate threshold.

```yaml
# Shipyard/sre/slo/burn-rate-query.yaml — SRE owns; devops's AnalysisTemplate reads.
slo: api-availability
target: 0.999            # SRE-owned SLO threshold
# Canary fast-burn guard: short-window 5xx burn rate over the canary subset.
# Metric names EXACTLY per observability-contract.md (status_class label).
burn_rate_query: |
  (
    sum(rate(http_requests_total{status_class="5xx", canary="true"}[2m]))
    / sum(rate(http_requests_total{canary="true"}[2m]))
  ) / (1 - 0.999)
fail_when: "> 14.4"     # >14.4x burn over 2m → abort the rollout
latency_query: |
  histogram_quantile(0.99,
    sum by (le) (rate(http_request_duration_seconds_bucket{canary="true"}[2m]))
  )
latency_fail_when: "> 1.2"   # p99 seconds — READ from performance-budget.yaml
# devops maps fail_when/latency_fail_when into AnalysisTemplate failureCondition.
```

> devops references this file from its canary `AnalysisTemplate` (see devops skill). If the canary queried a different metric name or a different threshold, the rollout would gate on data that disagrees with the SLO alerts — this file closes that loop. SRE changes the threshold here; devops never edits it.

### Step 5: Generate SLO Dashboard

Write `slo/slo-dashboard.json` as a Grafana dashboard JSON. EVERY panel query references ONLY contract metric names (`http_requests_total{status_class=...}`, `http_request_duration_seconds_bucket` with exemplars enabled, `http_requests_in_flight`, `*_pool_*`, `broker_consumer_lag`). Panels:
- SLO status panel (current attainment vs. target) — `http_requests_total{status_class="5xx"}` ratio
- Error budget remaining (percentage and time-based)
- Burn rate over time (same multi-window math as the alerts)
- Latency p50/p95/p99 from `http_request_duration_seconds_bucket` with **exemplars enabled** (click a slow bucket → the trace via the exemplar `trace_id`)
- Saturation: `http_requests_in_flight` + pool utilization (`db_pool_connections_in_use / db_pool_connections_max`)
- Budget consumption trend (projected exhaustion date)
- Per-service SLI breakdown

> Before handoff, grep every `expr`/`target.expr` in `slo-dashboard.json` and `burn-rate-alerts.yaml` for any token that is NOT in `observability-contract.md`. A panel that queries a name nothing emits renders "No data" — the Production-Ready Gate (`scripts/check-observability-names.sh`) fails on it.

## Validation

Before proceeding to Phase 3, verify:
- [ ] Every user-facing endpoint has at least one SLO (availability + latency)
- [ ] Every alert expr, recording rule, and dashboard panel queries ONLY names declared in `observability-contract.md` — error uses `status_class="5xx"`, NOT `status=~"5.."` (grep proves zero unknown names)
- [ ] Latency `le` thresholds READ from `performance-budget.yaml` (a standard bucket boundary) — no hardcoded 500ms
- [ ] SLO targets are realistic (not 99.99% for every service)
- [ ] Error budget policy specifies concrete enforcement actions
- [ ] Burn-rate alerts use multi-window approach (not just threshold-based); `promtool check rules` passes
- [ ] USE saturation alerts emitted for in-flight + pool exhaustion + broker lag (using the contract USE instruments)
- [ ] `burn-rate-query.yaml` emitted with the SRE-owned threshold + query that devops's canary AnalysisTemplate consumes
- [ ] Dashboard includes budget projection (exhaustion date) and exemplar-enabled latency panels

## Quality Bar

SLOs must be based on user-observable impact, not internal metrics. Internal services get lower targets than user-facing services. Every SLO must have a documented consequence for budget exhaustion — SLOs without enforcement are aspirational fiction. And an alert that queries a metric no code emits is worse than no alert: it renders "No data" and silently never fires. Close the loop — every query name lives in `observability-contract.md`, every latency target lives in `performance-budget.yaml`.
