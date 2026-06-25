# Phase 5 — Monitoring & Observability

Generate `infrastructure/monitoring/` (or `paths.monitoring` from config):

```
monitoring/
├── prometheus/
│   ├── prometheus.yml
│   ├── alerts/
│   │   ├── availability.yml
│   │   ├── latency.yml
│   │   ├── saturation.yml
│   │   └── errors.yml
│   └── recording-rules.yml
├── grafana/
│   ├── dashboards/
│   │   ├── overview.json
│   │   ├── per-service.json
│   │   ├── infrastructure.json
│   │   └── business-metrics.json
│   └── datasources.yml
├── logging/
│   ├── fluentbit.conf          # Log collection and forwarding
│   └── log-format.md           # Structured logging standard
├── tracing/
│   └── otel-collector.yaml     # OpenTelemetry Collector config
└── alerting/
    ├── pagerduty.yml
    ├── slack.yml
    └── escalation-policy.md
```

**Note:** SLO thresholds (SLI/SLO/SLA definitions) are defined by SRE (see sre skill output). DevOps provides the monitoring infrastructure; SRE defines the service level objectives.

**Note:** Operational runbooks are written by SRE. See SRE output at `docs/runbooks/`. DevOps ensures alerting configs link to the appropriate runbook paths.

### Scrape Config + Generated Dashboards/Alerts (observability-contract — EXACT names only)

**A dashboard that queries a name nothing emits renders "No data" — that is the bug this closes.** Scrape `GET /metrics` (Prometheus `ServiceMonitor` / scrape job); every Grafana panel and Prometheus alert references ONLY names declared in `observability-contract.md`. Grep the generated dashboards/alerts for any name absent from the contract before shipping.

| Signal | EXACT instrument (from `observability-contract.md`) | Panel / alert query |
|--------|------|------|
| **Traffic** | `http_requests_total{method,route,status_class}` | `sum(rate(http_requests_total[1m]))` by `route` |
| **Errors** | `http_requests_total{status_class="5xx"}` | `5xx / total` error ratio + burn-rate (SRE thresholds) |
| **Latency** | `http_request_duration_seconds_bucket` (exemplars) | `histogram_quantile(0.99, ...)` p50/p95/p99 heatmap with exemplar click-through to the trace |
| **Saturation (concurrency)** | `http_requests_in_flight{method,route}` | in-flight gauge panel |
| **Saturation (pools)** | `*_pool_connections_in_use` / `_max` / `_idle`, `*_pool_wait_seconds`, `*_pool_acquire_errors_total` | utilization % = in_use/max; wait > 0 → starvation |
| **Broker** | `broker_messages_*_total`, `broker_consumer_lag` | throughput + backlog |

- **Never invent a metric name.** No synonyms, no per-service renaming. `route` is the templated path; never label by raw URL/id/email/token.
- **ADD the observability-contract loader** (done — `!`cat Shipyard/.protocols/observability-contract.md ...``).

### Observability Standards
- **Structured logging** — JSON to **stdout only**; fields per `observability-contract.md`: `timestamp, level, message, service, env, trace_id, span_id, request_id` (+ `error.type`/`error.stack` on error). `trace_id`/`span_id` come from the LIVE span — devops ships stdout, never owns log files.
- **Distributed tracing** — OpenTelemetry, W3C Trace Context (`traceparent`+`baggage`); `http_request_duration_seconds` observations attach trace **exemplars** so a latency bucket clicks through to the slow trace. `service.name`/`deployment.environment` strings match metric/log/span.
- **Metrics** — RED (Rate, Errors, Duration) per service, USE (Utilization, Saturation, Errors) for pools — the exact instruments above.
- **SLO-based alerting** — Alert on error-budget burn rate, not raw thresholds (SLO definitions + burn-rate numbers provided by SRE; devops wires the query).
- **Runbook links** — Every alert links to a runbook (`docs/runbooks/`, maintained by SRE).
