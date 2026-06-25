# Phase 5: ML Infrastructure

## Objective

Design production ML infrastructure — model serving (batch and real-time), model versioning and registry, monitoring (drift detection, performance degradation), retraining pipelines, GPU/compute optimization, and deployment patterns.

## Context Bridge

Read Phase 1 audit from `analysis/system-audit.md` for ML model inventory. Read Phase 4 pipeline from `data-pipeline/architecture.md` for data flow integration points.

## Security Defaults (this phase generates model-serving code — obey `security-defaults.md`)

- **Model output is untrusted.** Serving responses and shadow-comparison logs are validated/typed before any downstream sink; never `eval`/exec a prediction or interpolate it raw into SQL/DOM/shell. Inference inputs are validated at the trust boundary (allowlist, fail-closed).
- **Per-object authz on serving endpoints.** A real-time inference/feature-store request authorizes the caller for that specific object server-side from the session/token — never trust a `user_id`/`tenant_id` in the request body (no BOLA/IDOR on feature lookups).
- **No secrets in serving/retraining configs.** Registry, GPU, and warehouse credentials from env/secret-manager; never logged. Security headers + strict CORS + secure cookies on any HTTP serving surface.
- **Gate model-triggered tool-calls and SSRF-allowlist** any model/user-influenced outbound (e.g. an LLM-serving endpoint that calls tools or fetches retrieval sources); keep the prompt-injection trust boundary for any LLM in the serving path.
- **Model & dataset supply chain / provenance (LLM03).** The registry records source, version, and checksum/signature for every model and training dataset; verify provenance against that record before promotion. Scan model artifacts for unsafe deserialization (reject untrusted `pickle`; prefer `safetensors`) and pin artifact versions/digests — never load a `latest`/unpinned model. Cross-ref `security-defaults.md` "Treat third-party / upstream API responses as untrusted" (never deserialize an untrusted payload into executable objects).
- **Vector store & RAG security (LLM08).** Enforce per-tenant access control / namespace isolation on the vector DB; authorize every retrieval against the caller server-side (no cross-tenant leakage). Validate documents before embedding and guard against embedding poisoning. Cross-ref `security-defaults.md` "Property-level authorization (mass assignment / BOPLA)" and the per-object default-deny authz above.

## Workflow

### Step 1: Model Registry & Versioning

Design a registry tracking every model from training to production. Schema includes: model_id, version (semver), framework, task type, status (staging/canary/production/archived), artifact paths, lineage (training data version, parent model), and serving config (endpoint, latency SLA, throughput RPS).

**Supply chain & provenance (LLM03):** the registry also records, for every model AND training/fine-tuning dataset, its **source, version, and checksum/signature (artifact digest)**. Verify provenance against this record before any promotion — a model whose digest does not match its registry entry is blocked. Scan model artifacts for unsafe deserialization: reject untrusted `pickle`/`joblib`/`torch.load` blobs and **prefer `safetensors`** for weights. **Pin every model/dataset artifact to a version + digest** in serving and retraining configs; never load `latest` or an unpinned URI. This mirrors `security-defaults.md` "Treat third-party / upstream API responses as untrusted" — an externally pulled model is an untrusted upstream payload.

Define promotion workflow: staging -> canary (5% traffic, 24h) -> production. Rollback: automatic revert if canary metrics degrade beyond thresholds. **Provenance verification is a hard promotion gate** (digest/signature match) — it runs before the eval/canary gates.

Produce `ml-infrastructure/model-registry.md`.

### Step 2: Model Serving Architecture

Select serving pattern based on inference requirements:

| Pattern | Best For | Latency | Stack |
|---------|----------|---------|-------|
| **REST API** | Real-time, low-medium traffic | < 100ms | FastAPI + Triton / TorchServe |
| **gRPC** | High throughput, internal services | < 50ms | Triton / TF Serving |
| **Batch** | Offline scoring, recommendation refresh | Hours | Spark / Ray / Airflow |
| **Streaming** | Event-driven scoring | < 500ms | Kafka consumer + model |

Include shadow deployment pattern: run new model version alongside production, log prediction comparisons for offline analysis, shadow failures never affect primary responses.

**Vector store & RAG security (LLM08)** — when the serving path includes retrieval-augmented generation or any vector DB:

- **Per-tenant isolation:** every collection/index is namespaced per tenant; a retrieval query is scoped to the caller's namespace and can never read another tenant's vectors. Default-deny — no shared "global" index that leaks across tenants.
- **Authorize every retrieval against the caller** server-side from the session/token (per-object authz — same rule as serving endpoints above); never trust a tenant/namespace id from the request body to pick the index.
- **Validate documents before embedding** (schema, size, source allowlist) and guard against **embedding poisoning** — an attacker who can write to the corpus must not be able to steer retrieval. Only ingest from provenance-tracked, allowlisted sources (cross-ref Phase 4 "Data poisoning defenses").
- **Treat retrieved chunks as untrusted content** in the prompt-injection trust boundary: retrieved text is data, never instructions (cross-ref Phase 2 and `security-defaults.md` "LLM / AI security defaults").

Produce `ml-infrastructure/serving/` with architecture docs, deployment configs, health checks, and (if RAG) vector-store namespace/authz config.

### Step 3: Model Monitoring

Implement three monitoring dimensions:

**a. Data drift detection:** Input feature distribution shifts via PSI (Population Stability Index) and KS test. PSI thresholds: < 0.1 stable, 0.1-0.25 investigate, > 0.25 action required.

**b. Model performance:** Prediction quality metrics (accuracy, precision, recall, RMSE), latency p50/p95/p99, throughput, error rates, confidence score distribution shifts.

**c. Operational health:** Memory/CPU per model instance, queue depth, cold start latency.

Produce `ml-infrastructure/monitoring/` with drift detection configs, alerting rules, and dashboards.

### Step 4: Retraining Pipelines

Design automated retraining with safeguards:

- **Triggers:** Scheduled (weekly/monthly), drift-triggered (PSI > threshold), performance-triggered (metric below SLO)
- **Pipeline:** Data validation -> Feature engineering -> Training -> Evaluation -> Registry upload
- **Promotion gates:** Automated eval on holdout set, shadow deployment comparison, canary rollout
- **Rollback:** Automatic revert if canary metrics degrade

Produce `ml-infrastructure/retraining/` with pipeline definitions, trigger configs, and promotion gates.

### Step 5: GPU/Compute Optimization

Evaluate optimization techniques:

| Technique | Impact | Complexity |
|-----------|--------|------------|
| **Model quantization** (INT8/FP16) | 2-4x speedup, 50-75% memory reduction | Medium |
| **Batched inference** | Higher throughput, lower per-request cost | Low |
| **Model distillation** | Smaller model, similar accuracy | High |
| **Spot instances** | 60-80% training cost reduction | Low |
| **Auto-scaling** | Match capacity to demand | Medium |
| **ONNX conversion** | Framework-agnostic optimized runtime | Medium |

Produce `ml-infrastructure/compute-optimization.md` with current vs optimized cost comparison.

## Output Files

- `ml-infrastructure/model-registry.md`
- `ml-infrastructure/serving/` (architecture, deployment configs, health checks)
- `ml-infrastructure/monitoring/` (drift detection, performance alerts, dashboards)
- `ml-infrastructure/feature-store/` (feature definitions — if applicable)
- `ml-infrastructure/retraining/` (pipeline definitions, triggers, promotion gates)
- `ml-infrastructure/compute-optimization.md`

## Validation

Before proceeding to Phase 6, verify:
- [ ] Model registry covers versioning, lineage, and promotion workflow
- [ ] Registry records source + version + checksum/signature for every model AND dataset; provenance verified as a hard promotion gate (LLM03)
- [ ] Model artifacts scanned for unsafe deserialization (no untrusted pickle; safetensors preferred); artifacts pinned to version + digest (no `latest`)
- [ ] Serving architecture matches latency and throughput requirements
- [ ] Shadow deployment pattern implemented for safe rollout
- [ ] If RAG/vector store: per-tenant namespace isolation, per-retrieval caller authz, document validation before embedding, embedding-poisoning guard (LLM08)
- [ ] Drift detection covers input features and prediction distributions
- [ ] Monitoring includes data drift, model performance, and operational health
- [ ] Retraining pipeline has automated triggers and promotion gates
- [ ] Compute optimization opportunities quantified with cost impact
- [ ] `security-defaults checklist passes` — model output treated as untrusted, inference inputs validated fail-closed, per-object default-deny authz on serving/feature/retrieval endpoints, secrets from env/secret-manager, model-triggered tool-calls gated + SSRF allowlist, model/dataset provenance verified (source+version+digest, no unsafe deserialization), vector-store per-tenant isolation

> **GATE: Present ML infrastructure design. Wait for user approval before proceeding.**

## Quality Bar

Every model in production must have monitoring, drift detection, a rollback procedure, **a verified provenance record (source + version + digest)**, and `security-defaults checklist passes`. "The model is deployed" is not acceptable — "Model rec-engine-v3.1.0 (safetensors, digest sha256:… verified against registry) serves at p99 < 85ms, PSI monitored hourly with retraining at PSI > 0.25, canary validates on 5% traffic for 24h before full rollout; RAG retrieval is namespace-isolated per tenant" is acceptable. A deferred security item is logged as an explicit HARDEN hand-off, never silently skipped.
