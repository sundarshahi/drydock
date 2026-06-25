# Observability Contract — Shared Metric, Log & Span Names Across Emit / Scrape / Alert

**Core principle: One name, three agents. A metric name, log field, or span attribute is a CONTRACT. software-engineer/frontend-engineer EMIT exactly these names, devops scrapes/dashboards exactly these names, sre alerts on exactly these names. A dashboard or alert may only query a name this contract declares, and emitted code may only use names this contract declares. Drift on either side is a bug — the loop must close so dashboards light up on first run.**

Today SRE alert rules and Grafana panels query `http_requests_total` and `http_request_duration_seconds_bucket` while generated code emits nothing, so panels render "No data". This contract is the single source of truth that ends that mismatch: it fixes the exact instrument names, label sets, log fields, and span attributes the three roles must agree on.

---

## Canonical RED Metrics (Rate / Errors / Duration) — EMIT these EXACTLY

Every HTTP service emits these three instruments. Names, types, and labels are fixed — no synonyms, no per-service renaming.

| Instrument | Type | Unit | Labels (exact) | Notes |
|------------|------|------|----------------|-------|
| `http_requests_total` | Counter | `1` | `method`, `route`, `status_class` | **Rate** + **Errors**. `route` is the templated path (`/users/{id}`), NEVER the raw URL (no high-cardinality IDs). `status_class` ∈ `1xx,2xx,3xx,4xx,5xx`. Error rate = `5xx / total`. |
| `http_request_duration_seconds` | Histogram | `s` | `method`, `route`, `status_class` | **Duration**. Seconds, never milliseconds. Standard buckets below. Exemplars REQUIRED (link to live span/trace). Prometheus exposes `_bucket`/`_sum`/`_count`. |
| `http_requests_in_flight` | Gauge | `1` | `method`, `route` | Concurrency. Increment at request start, decrement in a `finally`/deferred path so errors still decrement. |

- **Standard latency buckets (seconds), use verbatim:** `0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10`. Do not invent custom buckets unless a documented SLO needs a boundary — then ADD, never replace.
- **Label cardinality is a hard rule.** `route` MUST be the matched template. Never label by raw path, user id, email, token, or unbounded query param. A label whose value set is unbounded is a contract violation.
- **`status_class`, not raw `status`.** Bucket the 3-digit code to its class for the standard label; if exact codes are needed, add a separate low-traffic `status` only where justified.
- **Naming rules (Prometheus/OTel):** `snake_case`; counters end `_total`; base unit in the name (`_seconds`, `_bytes`); no `_total` on gauges/histograms.

---

## USE Metrics for Resource Pools (Utilization / Saturation / Errors) — EMIT for db / redis / broker

Connection pools and queues are the usual saturation source. `<resource>` ∈ `db`, `redis`, `broker` (or the concrete driver, e.g. `pg`).

| Instrument | Type | Labels | Meaning |
|------------|------|--------|---------|
| `<resource>_pool_connections_in_use` | Gauge | `pool` | Active/checked-out connections (Utilization). |
| `<resource>_pool_connections_max` | Gauge | `pool` | Configured pool ceiling. Utilization % = in_use / max. |
| `<resource>_pool_connections_idle` | Gauge | `pool` | Idle/available connections. |
| `<resource>_pool_wait_seconds` | Histogram | `pool` | Time a caller waited to acquire a connection (Saturation; waiting > 0 means starvation). |
| `<resource>_pool_acquire_errors_total` | Counter | `pool` | Acquire timeouts / exhaustion (pool Errors). |
| `broker_messages_published_total` / `broker_messages_consumed_total` | Counter | `destination`, `result` | Messaging throughput; `result` ∈ `ack,nack,error`. |
| `broker_consumer_lag` | Gauge | `destination`, `group` | Unprocessed backlog (queue saturation). |

---

## Structured Log JSON Schema — EMIT to stdout ONLY

Logs are JSON, one object per line, written to **stdout only** (the platform ships stdout; the app never owns log files, rotation, or external sinks).

| Field | Required | Type / format | Source |
|-------|----------|---------------|--------|
| `timestamp` | yes | ISO 8601 UTC w/ ms (`2026-06-24T12:00:00.123Z`) | clock at emit |
| `level` | yes | `debug,info,warn,error,fatal` | call site |
| `message` | yes | human-readable, no interpolated PII | call site |
| `service` | yes | matches span `service.name` & metric job | env / resource |
| `env` | yes | `dev,staging,prod` — matches `deployment.environment` | env |
| `trace_id` | yes when in a request | 32-hex, **from the LIVE span context**, never generated ad hoc | active span |
| `span_id` | yes when in a request | 16-hex, from the live span context | active span |
| `request_id` | yes | inbound `X-Request-Id` or a generated UUID echoed in the response header | middleware |
| `error.type` / `error.stack` | on error | exception class + stack | catch site |

- **`trace_id`/`span_id` MUST be read from the active span context**, not invented — this is what makes logs↔traces correlate in the backend. No live span → omit the fields, do not fabricate.
- **PII-safe rules:** never log passwords, tokens, API keys, full card numbers, raw auth headers, or request bodies with personal data. Redact to `***` or hash. Logging a secret is a contract + security violation (see `security-testing-protocol.md`).
- Keys are `snake_case` / OTel dotted (`error.type`); no nested free-form blobs that break field-based queries.

---

## Required Span Attributes & Propagation — EMIT on every span

Follow OpenTelemetry semantic conventions. Resource attributes are set once per process; span attributes per operation.

| Scope | Attribute | Example | Required |
|-------|-----------|---------|----------|
| Resource | `service.name` | `checkout-api` | yes |
| Resource | `deployment.environment` | `prod` | yes |
| Resource | `service.version` | `1.4.2` | yes |
| HTTP server span | `http.request.method` | `GET` | yes |
| HTTP server span | `http.route` | `/users/{id}` (templated — matches metric `route`) | yes |
| HTTP server span | `http.response.status_code` | `200` | yes |
| HTTP server span | `url.path`, `server.address` | `/users/42` | yes |
| DB client span | `db.system`, `db.namespace`, `db.operation.name` | `postgresql`, `orders`, `SELECT` | yes for DB calls |
| Messaging span | `messaging.system`, `messaging.destination.name`, `messaging.operation` | `kafka`, `orders.events`, `publish`/`receive` | yes for broker calls |

- **Propagation: W3C Trace Context** (`traceparent` + `tracestate`) on every inbound/outbound HTTP and broker hop, plus **W3C `baggage`** for cross-service request context. Frontend (frontend-engineer) starts the trace and sends `traceparent` on fetch/XHR so the browser→backend trace is unbroken.
- **Exemplar linkage:** every `http_request_duration_seconds` observation attaches an exemplar carrying the current `trace_id`, so a latency-histogram bucket in Grafana clicks straight through to the slow trace. Same `http.route` value is used by metric, span, and log — that is the join key.

---

## OTLP Export Expectations

- **Exporter endpoint:** read `OTEL_EXPORTER_OTLP_ENDPOINT` (e.g. `http://otel-collector:4317`); never hard-code a collector host. Honor `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_SERVICE_NAME`, `OTEL_RESOURCE_ATTRIBUTES`.
- **Signals over OTLP:** traces + metrics export via OTLP to the collector; logs go to **stdout** (collected by the platform), not pushed direct from the app.
- **Resource attributes on every export:** `service.name`, `service.version`, `deployment.environment` — identical strings to the log `service`/`env` fields and span resource, or correlation breaks.
- **Prometheus scrape:** the collector (or app `/metrics`) exposes the RED + USE instruments above; devops scrape configs and sre alert rules reference ONLY names declared in this contract.

---

## Who Emits / Who Consumes (the three+ agents agree here)

| Signal | EMITTER (owns the name in code) | SCRAPE / DASHBOARD (devops) | ALERT / SLO (sre) |
|--------|--------------------------------|-----------------------------|-------------------|
| `http_requests_total` | software-engineer (backend), frontend-engineer (browser/RUM) | Grafana rate + error-rate panels | error-budget burn, error-ratio alerts |
| `http_request_duration_seconds` | software-engineer, frontend-engineer | latency heatmap / p50·p95·p99 + exemplars | latency SLO (p99 threshold) |
| `http_requests_in_flight` | software-engineer | concurrency panel | saturation alert |
| `*_pool_connections_*`, `*_pool_wait_seconds` | software-engineer | pool utilization panel | saturation / exhaustion alert |
| Structured JSON logs (stdout) | software-engineer, frontend-engineer | devops ships stdout to log backend | sre correlates logs↔traces via `trace_id` |
| Spans + W3C propagation | software-engineer (start/continue), frontend-engineer (start at browser) | devops wires collector/backend + Grafana trace view | sre uses traces for RCA via exemplars |

- **Authority (matches `conflict-resolution.md`):** software-engineer/frontend-engineer own the emitted names; **devops** owns dashboards + scrape config and implements thresholds; **sre** defines SLO thresholds + alert logic. None renames a signal unilaterally — a name change is a contract change agreed by all three.

---

## Reviewer Checklist (verify before any service ships)

- [ ] All three RED instruments emitted with EXACT names, types, labels, and the standard buckets; latency in **seconds**.
- [ ] `route`/`http.route` is templated everywhere — no raw IDs/emails/tokens in any label (cardinality bound).
- [ ] Resource pools (db/redis/broker present) emit the USE instruments.
- [ ] Logs are JSON to **stdout only**, every required field present; `trace_id`/`span_id` come from the **live span**; no PII/secrets.
- [ ] Spans carry required semconv attributes; W3C `traceparent` + `baggage` propagate inbound→outbound; frontend starts the trace.
- [ ] Histogram observations attach trace **exemplars**; `service.name`/`deployment.environment` strings match across metric, log, and span.
- [ ] Export honors `OTEL_EXPORTER_OTLP_ENDPOINT` + resource attributes; metrics scrapeable by Prometheus.
- [ ] Every sre alert rule + Grafana panel queries ONLY names declared here — grep dashboards/alerts for any name absent from this file (closes the `http_requests_total`-with-no-emitter gap).

---

## Key Principle

**A dashboard that queries a name nothing emits is broken, and code that emits a name nothing dashboards is wasted. This contract is the join: same metric names, same log fields, same span attributes, same `route`/`service`/`env` strings across all three roles — so the very first run lights the dashboards up and the alerts have data to fire on.**
