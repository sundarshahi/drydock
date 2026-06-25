# Phase 4: Data Pipeline Architecture

## Objective

Design and implement the data pipeline layer — ETL/ELT architecture, data warehouse/lake design, real-time vs batch processing, data quality monitoring, event streaming, and analytics dashboards. Produce deployable schemas, pipeline definitions, and monitoring configs.

## Context Bridge

Read Phase 1 audit from `analysis/system-audit.md` for data flow maps and analytics gaps. Read Phase 3 metrics schema from `experiments/framework/metrics-schema.md` for events the pipeline must ingest.

## Security Defaults (this phase generates ingestion/ETL code — obey `security-defaults.md`)

- **Parameterized queries ONLY** in every dbt model, ETL transform, and warehouse query — zero string-concatenated SQL with event/user input.
- **No secrets in pipeline configs.** Warehouse/broker/connector credentials come from env/secret-manager; commit `.env.example` key names only; never log connection strings or tokens.
- **PII handling:** anonymize/pseudonymize PII at ingestion (before it lands in raw), enforce it as a Critical data-quality check; the LLM-usage mart and experiment-metrics mart carry no raw prompts/responses containing PII or secrets, and **LLM-derived/model-output columns are treated as untrusted** — validated/typed, never interpolated into SQL or rendered raw in a dashboard.
- **SSRF allowlist** any connector/webhook whose source URL is user/config-influenced.
- **Data poisoning defenses (LLM04).** Track provenance/lineage for every dataset that feeds training or fine-tuning; constrain ingestion sources to an **allowlist**; **validate and anomaly-detect** ingested/training data (schema, range, label/distribution outliers); and **integrity-check datasets** (checksum/signature) before any training or fine-tuning run. Data arriving from a third-party feed is an untrusted upstream payload — cross-ref `security-defaults.md` "Treat third-party / upstream API responses as untrusted".

## Workflow

### Step 1: Event Schema Design

Define the canonical event schema with base fields (event_id, event_name, timestamp, source, user_id, session_id, properties, context) and domain-specific extensions. Every event must include validation rules: non-null checks on required fields, enum constraints, and range validation.

Produce `data-pipeline/event-schema/` with base event YAML and domain event definitions.

### Step 2: Pipeline Architecture Selection

Evaluate architecture patterns against system needs:

| Pattern | Best For | Stack Options | Latency |
|---------|----------|---------------|---------|
| **Batch ETL** | Daily/hourly analytics, cost reports | Airflow + dbt + warehouse | Hours |
| **Micro-batch** | Near-real-time dashboards | Spark Streaming, Flink | Minutes |
| **Event Streaming** | Real-time features, live dashboards | Kafka/Redpanda + consumers | Seconds |
| **ELT (recommended)** | Warehouse-first, flexible transforms | Fivetran/Airbyte + dbt | Hours |

Produce `data-pipeline/architecture.md` with chosen pattern, data flow diagram (source -> ingestion -> transformation -> storage -> serving), tech stack per layer, and SLAs per pipeline (freshness, completeness).

### Step 3: Data Warehouse/Lake Design

Design three-layer storage: **raw** (immutable event log), **staging** (cleaned, validated, deduplicated), **marts** (business-ready aggregations). Include LLM usage daily mart (date, feature, model, calls, tokens, cost, latency percentiles, error rate, cache hit rate) and experiment metrics daily mart.

Produce `data-pipeline/warehouse/` with schema SQL, dbt models, and data dictionary.

### Step 4: Data Quality Monitoring

Implement quality checks at every pipeline stage with three severity levels:

- **Critical (pipeline halts):** Non-null on required fields, primary key uniqueness, data freshness within SLA, **source on the ingestion allowlist**, and **dataset integrity check (checksum/signature) for any data destined for training/fine-tuning** (LLM04)
- **Warning (alert, continue):** Value range validation, row count within expected bounds, **label/feature-distribution anomaly detection** (poisoning signal)
- **Info (log only):** Distribution shift detection, schema evolution tracking, **provenance/lineage record written** for the batch

**Data poisoning defenses (LLM04):** these checks are also the poisoning gate. Every dataset that will train or fine-tune a model carries a **provenance/lineage record** (source, batch id, ingestion time, checksum), comes only from an **allowlisted source**, and is **integrity-verified before training**. Anomaly detection on labels/feature distributions flags tampering before it reaches the model. The training/fine-tuning step (Phase 5) consumes only datasets that passed these gates.

Produce `data-pipeline/quality/` with check definitions, alerting thresholds, and quality dashboard spec.

### Step 5: Analytics Dashboards

Design dashboards per stakeholder group:

| Dashboard | Audience | Key Metrics | Refresh |
|-----------|----------|-------------|---------|
| **LLM Operations** | Engineering | Token usage, cost/call, latency p50/p95/p99, error rate, cache hits | Real-time |
| **Experiment Monitor** | Data Science | Variant metrics, sample size progress, significance status | Hourly |
| **Cost Overview** | Leadership | Monthly spend, cost per feature, budget burn rate | Daily |
| **Data Quality** | Platform | Freshness SLA, null rates, schema violations, pipeline failures | Real-time |

Produce `data-pipeline/dashboards/` with dashboard specs (Grafana JSON, Superset configs, or Metabase queries).

### Step 6: Event Streaming (if applicable)

For real-time requirements: Kafka/Redpanda topic design (partitioning, retention, schema registry), consumer group architecture (delivery semantics), dead letter queues, backpressure handling, and consumer lag monitoring.

Produce `data-pipeline/streaming/` with topic schemas and consumer configurations.

## Output Files

- `data-pipeline/architecture.md`
- `data-pipeline/event-schema/` (base + domain events)
- `data-pipeline/warehouse/` (schema SQL, dbt models, data dictionary)
- `data-pipeline/etl/` (pipeline definitions, transformation logic)
- `data-pipeline/quality/` (check definitions, alerting config)
- `data-pipeline/dashboards/` (dashboard specs per audience)
- `data-pipeline/streaming/` (topic schemas, consumer configs — if applicable)

## Validation

Before proceeding to Phase 5, verify:
- [ ] Event schema covers all analytics and experiment events with validation rules
- [ ] Pipeline architecture documented with data flow diagram and SLAs
- [ ] Warehouse schema includes raw, staging, and marts layers
- [ ] Data quality checks at every pipeline stage (non-null, freshness, uniqueness, range, volume)
- [ ] Data poisoning defenses (LLM04): provenance/lineage tracked, ingestion sources allowlisted, anomaly detection on training data, dataset integrity-checked before training/fine-tuning
- [ ] Dashboard specs cover all key stakeholder groups
- [ ] All SQL compatible with target warehouse (confirmed with user) and parameterized (no concatenated user/event input)
- [ ] Pipeline error handling includes dead letter queues and alerting
- [ ] `security-defaults checklist passes` — parameterized queries only, secrets from env/secret-manager (never logged), PII anonymized at ingestion, model-output columns treated as untrusted, SSRF allowlist on connector URLs, training-data provenance tracked + sources allowlisted + integrity-checked (LLM04)

> **GATE: Present data pipeline architecture. Wait for user approval before proceeding.**

## Quality Bar

Every pipeline must have SLAs for freshness and completeness, and `security-defaults checklist passes`. "The data is updated regularly" is not acceptable — "The LLM usage mart refreshes every 2 hours with a freshness SLA of 3 hours, completeness target of 99.5%, and an automated alert if any quality check fails" is acceptable. Any dataset feeding training/fine-tuning additionally carries a provenance record, an allowlisted source, and a pre-training integrity check (LLM04). A deferred security item is logged as an explicit HARDEN hand-off, never silently skipped.
