# Phase 1: Production Readiness Review

## Objective

Systematically evaluate every service for production survivability. This is not a rubber stamp — it is an adversarial review. Every checklist item that fails gets documented with severity and specific evidence.

## Inputs

- `infrastructure/kubernetes/` — pod specs, probes, resource limits
- `infrastructure/terraform/` — infrastructure sizing, redundancy
- Application source code — connection pooling, retry logic, timeout configs
- Architecture docs — dependency map, data stores, external integrations

## Workflow

### Step 1: Read Kubernetes Manifests

Extract from all Kubernetes manifests:
- Readiness probes, liveness probes, startup probes
- Resource requests and limits
- PodDisruptionBudgets
- Topology spread constraints
- Graceful shutdown configuration (preStop hooks, terminationGracePeriodSeconds)

### Step 2: Read Application Configuration

Analyze application configs for:
- Connection pool sizes (database, HTTP clients, Redis)
- Timeout values (connect, read, write, idle)
- Retry policies (max retries, backoff strategy, jitter)
- Circuit breaker thresholds

### Step 3: Read Infrastructure Configs

Analyze Terraform/infrastructure configs for:
- Multi-AZ deployment
- Load balancer health checks
- Auto-scaling policies
- Backup schedules
- Encryption at rest and in transit

### Step 4: Generate Production Readiness Checklist

Write `production-readiness/checklist.md` using this structure:

```markdown
# Production Readiness Checklist

## Service: <service-name>
Review Date: <date>
Reviewer: SRE Skill (automated)

### Health Checks
- [ ] Readiness probe configured with appropriate path and thresholds
- [ ] Liveness probe configured (distinct from readiness)
- [ ] Startup probe configured for slow-starting services
- [ ] Health check endpoints verify downstream dependencies
- [ ] Health checks do NOT perform expensive operations

### Graceful Shutdown
- [ ] preStop hook configured with sleep or drain logic
- [ ] terminationGracePeriodSeconds > preStop + drain time
- [ ] Application handles SIGTERM and drains in-flight requests
- [ ] Long-running connections (WebSocket, gRPC streams) are drained

### Connection Management
- [ ] Database connection pool sized correctly (not default)
- [ ] HTTP client connection pools configured with limits
- [ ] Idle connection timeout set to prevent stale connections
- [ ] Connection pool metrics exposed

### Timeout Tuning
- [ ] Upstream timeout > downstream timeout (no orphaned requests)
- [ ] Connect timeout distinct from read timeout
- [ ] Global request timeout configured at ingress/gateway
- [ ] Timeout values documented and justified

### Retry Configuration
- [ ] Retries configured with exponential backoff
- [ ] Jitter applied to prevent thundering herd
- [ ] Retry budget capped (e.g., max 10% additional load)
- [ ] Non-idempotent operations are NOT retried
- [ ] Circuit breaker wraps retry logic

### Resource Limits
- [ ] CPU request and limit set (limit >= 2x request for bursty services)
- [ ] Memory request and limit set (limit == request for predictable OOM behavior)
- [ ] Ephemeral storage limits set
- [ ] PodDisruptionBudget configured (minAvailable or maxUnavailable)

### Data Safety
- [ ] Backup schedule configured and verified
- [ ] Point-in-time recovery tested
- [ ] Data encryption at rest enabled
- [ ] Data encryption in transit enforced (mTLS or TLS)

### Dependency Resilience
- [ ] All external dependencies have circuit breakers
- [ ] Fallback behavior defined for each dependency failure
- [ ] Dependency health is NOT part of liveness probe
- [ ] Timeout on every outbound call
```

### Step 4b: 12/15-Factor Compliance

Walk ALL 15 factors of the (12-Factor + the 3 cloud-native additions: API-first, Telemetry, Auth) methodology for EVERY service. This is not prose — it is a pass/fail table where each verdict CITES the proving artifact (file + line, config key, or env var). A factor with no cited evidence is a FAIL, not a pass.

Write `production-readiness/factor-compliance.md`:

```markdown
# 12/15-Factor Compliance — <service-name>

| # | Factor | Verdict | Proving artifact (cite file/line, key, or env) |
|---|--------|---------|------------------------------------------------|
| 1 | Codebase — one repo tracked in VCS, many deploys | PASS | `.git`, `infrastructure/kubernetes/<svc>/` per-env overlays |
| 2 | Dependencies — explicitly declared & isolated | PASS | `package.json`/`go.mod`/`pyproject.toml` + lockfile; no system-wide deps in Dockerfile |
| 3 | Config — in the environment, not code | FAIL | hardcoded DB host in `src/config.ts:14` — must read from env |
| 4 | Backing services — attached resources via URL/creds | PASS | `DATABASE_URL`, `REDIS_URL`, `OTEL_EXPORTER_OTLP_ENDPOINT` from env |
| 5 | Build, release, run — strictly separated | PASS | immutable image tag per release; `.github/workflows/` build≠deploy |
| 6 | Processes — stateless, share-nothing | PASS | session in Redis (`USER_SESSIONS`), no in-proc sticky state |
| 7 | Port binding — self-contained, binds a port | PASS | binds `PORT` env (see Startup/Disposability below) |
| 8 | Concurrency — scale out via the process model | PASS | HPA `minReplicas`/`maxReplicas` (Phase 5 scaling-configs) |
| 9 | Disposability — fast startup, graceful shutdown | PASS | SIGTERM drain + preStop (see Graceful Shutdown section) |
| 10 | Dev/prod parity — keep environments similar | PASS | same image dev→prod; managed Postgres both sides |
| 11 | Logs — event streams to stdout | PASS | structured JSON to **stdout only** per `observability-contract.md` (no app-owned log files) |
| 12 | Admin processes — one-off as separate processes | FAIL | migrations run in entrypoint — must be a separate Job (see Startup/Disposability) |
| 13 | API-first — contract before implementation | PASS | OpenAPI at `api/openapi.yaml` (solution-architect), `Problem` schema for errors |
| 14 | Telemetry — metrics, logs, traces emitted | PASS | RED + USE instruments + W3C trace propagation per `observability-contract.md` |
| 15 | Authentication & authorization — security as a concern | PASS | mTLS in transit + authz middleware (cite `security-defaults.md` controls) |

## Failures requiring remediation
<List every FAIL with severity + the remediation pointer. A FAIL blocks `production-ready`
unless logged in Shipyard/sre/gate/overrides.log as accepted-with-justification.>
```

**Rules:**
- A `PASS` MUST cite a concrete artifact. "Looks fine" is a FAIL.
- Factor 11 (logs) and 14 (telemetry) verdicts MUST be consistent with `observability-contract.md` — logs to stdout only, RED+USE instruments emitted, W3C propagation. If code emits a metric name not in the contract, that is a telemetry FAIL.
- Factor 13 (API-first) cites the solution-architect OpenAPI + the RFC 9457 `Problem` schema; if errors are an ad-hoc envelope, FAIL.
- Every FAIL feeds `scripts/check-factor-compliance.sh` (Production-Ready Gate). The gate exits non-zero on any FAIL not accepted-with-justification.

### Step 4c: Startup & Disposability Block

Add a `## Startup & Disposability` section to `production-readiness/checklist.md` per service. This makes Factors 7 and 9 mechanically verifiable against the Kubernetes manifests and app boot path:

```markdown
## Startup & Disposability — <service-name>

### Port binding & readiness
- [ ] Process binds the `PORT` env var (no hardcoded port) and listens on `0.0.0.0`
- [ ] Reports readiness within the boot budget — readiness probe `initialDelaySeconds` + `failureThreshold × periodSeconds` ≥ measured p99 cold-boot time (cite the measured boot time)
- [ ] **No blocking remote calls before the listener is up** — DB/cache/broker dials happen AFTER bind or lazily; the readiness probe (not the liveness probe) reflects dependency health, so a slow dependency delays traffic without killing the pod
- [ ] Readiness probe flips to ready ONLY after warm-up (pool primed, caches loaded) completes

### Disposability (fast, clean shutdown)
- [ ] Handles SIGTERM: stop accepting new requests, drain in-flight within `terminationGracePeriodSeconds`
- [ ] `preStop` sleep ≥ ingress propagation delay so the LB stops routing before the process exits
- [ ] In-flight request drain + long-lived connection (WebSocket/gRPC stream) drain implemented
- [ ] Crash-only design: process can be killed at any instant without corrupting state (idempotent writes, no in-proc-only buffers)

### Admin / migrations as one-off processes (Factor 12)
- [ ] Schema migrations run as a SEPARATE one-off process (k8s `Job` / init container / `make migrate`), NEVER inside the request-serving entrypoint
- [ ] One-off process uses the same image + config as the app (dev/prod parity)
- [ ] Startup probe is tuned to REAL boot time so slow-but-healthy starts are not killed (`startupProbe.failureThreshold × periodSeconds` ≥ worst-case boot)
```

Each unchecked box becomes a finding in Step 5 with the offending manifest/code path cited.

### Step 5: Generate Findings

Write `production-readiness/findings.md` documenting every checklist item that fails, with:
- Severity (Critical / High / Medium / Low)
- Specific evidence from the configs
- Which service is affected
- What the current value is vs. what it should be

### Step 6: Generate Remediation Plan

Write `production-readiness/remediation.md` with concrete fix instructions for every finding:
- Exact config changes
- Code snippets
- Kubernetes manifest patches
- Prioritized by severity

## Validation

Before proceeding to Phase 2, verify:
- [ ] Every service in the architecture has been reviewed
- [ ] Every checklist section has been evaluated (no blanks)
- [ ] `factor-compliance.md` exists for every service with all 15 factors verdicted and EACH pass citing a proving artifact
- [ ] Startup & Disposability section present per service (PORT bind, readiness-within-budget, no blocking remote calls before listening, migrations as a one-off process, startup-probe tuned to real boot)
- [ ] All Critical findings have remediation instructions
- [ ] Findings are linked to specific files and line numbers where possible
- [ ] Any factor FAIL is either remediated or logged in `Shipyard/sre/gate/overrides.log` (accepted-with-justification) — otherwise it BLOCKS `production-ready`

## Quality Bar

A production readiness review is NOT complete if it just says "looks good." Every checklist item must have a concrete pass/fail with evidence. Vague assessments ("timeout seems reasonable") are not acceptable — state the actual value and whether it meets the criterion.
