# Phase 3: Cross-Cutting Concerns

## Objective

Implement shared middleware and infrastructure code in `libs/shared/` and wire into each service. This phase covers authentication, tenant resolution, error handling, structured logging, rate limiting, caching, retry/circuit-breaker patterns, feature flags, and graceful degradation.

## 3.1 — Authentication Middleware

Based on the auth ADR from the architect:

```
Request arrives
  → Extract token (Bearer header / cookie)
  → Validate token (JWT signature, expiry, issuer, audience)
  → Extract claims (user_id, tenant_id, roles, permissions)
  → Attach to request context
  → Pass to next middleware
  → On failure: 401 with standard error format
```

Implementation requirements:
- JWKS key caching with background refresh (not per-request fetch)
- Token introspection fallback for opaque tokens
- Role-based access control (RBAC) decorator/annotation for handlers
- Permission-based fine-grained access where needed
- Service-to-service auth (mTLS or service account tokens)

## 3.2 — Tenant Resolution Middleware

```
Request arrives (after auth)
  → Extract tenant identifier (from JWT claim / subdomain / header / path)
  → Validate tenant exists and is active
  → Load tenant configuration (feature flags, limits, plan tier)
  → Attach tenant context to request
  → All downstream queries automatically scoped to tenant
  → On failure: 403 with "invalid tenant" error
```

## 3.3 — Error Handling (RFC 9457 problem+json + Error Catalog)

The global error handler maps every app error to **RFC 9457 `application/problem+json`** — there is no bespoke `{code,message,details}` envelope. Response `Content-Type: application/problem+json`; body:

```json
{
  "type": "https://errors.example.com/resource-not-found",
  "title": "Resource not found",
  "status": 404,
  "detail": "User with ID '123' not found",
  "instance": "/api/v1/users/123",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "errors": [
    { "pointer": "/userId", "detail": "no user with this id in tenant" }
  ]
}
```

- `type` is a URI reference, `title`/`status`/`detail`/`instance` per RFC 9457; `trace_id` (string) and `errors[]` (array of `{ field|pointer, detail }`) are the standard extensions agreed across skills.
- The body schema is the reusable OpenAPI component **`Problem`** (owned by solution-architect). Every error response in `api/openapi/*.yaml` `$ref`s it; the runtime serializes to exactly that shape.

### Generate the Error Catalog (single source of truth)

EMIT one source-of-truth module — `libs/shared/errors/catalog.{ts,py,go,...}` — whose entries are:

```
{ code, http_status, title, message_template, remediation, docs_anchor }
```

- **Both** the runtime error handler AND the docs error table read from this catalog — never two hand-maintained copies. The runtime maps a domain/app error → its catalog entry → a `Problem` body (`type` derived from `code`/`docs_anchor`, `title`/`status` from the entry, `detail` from `message_template`).
- `trace_id` is read from the **live span context** (not generated ad hoc), so logs↔traces↔problem responses correlate.

Baseline entries (extend per domain):
| Domain Error | `code` | `http_status` |
|-------------|--------|---------------|
| ValidationFailed | `VALIDATION_ERROR` | 400 |
| Unauthorized | `UNAUTHORIZED` | 401 |
| Forbidden | `FORBIDDEN` | 403 |
| NotFound | `RESOURCE_NOT_FOUND` | 404 |
| Conflict | `CONFLICT` | 409 |
| RateLimited | `RATE_LIMITED` | 429 |
| InternalError | `INTERNAL_ERROR` | 500 |
| ServiceUnavailable | `SERVICE_UNAVAILABLE` | 503 |

- Never expose stack traces in production (only in development) — `detail` stays user-safe; full error + stack logged server-side at ERROR with `trace_id`.
- Always include `trace_id` for support correlation; map field-level failures into `errors[]`.

## 3.4 — Structured Logging

Every log line is JSON with mandatory fields:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "info",
  "service": "user-service",
  "trace_id": "abc-123",
  "span_id": "def-456",
  "tenant_id": "tenant-789",
  "user_id": "user-012",
  "method": "POST",
  "path": "/api/v1/users",
  "status": 201,
  "duration_ms": 45,
  "message": "User created successfully"
}
```

Log levels:
- `error` — Unexpected failures requiring investigation
- `warn` — Expected failures (validation errors, rate limits, not-found)
- `info` — Request/response lifecycle, business events
- `debug` — Detailed execution flow (disabled in production)

Field names follow `observability-contract.md` exactly. `trace_id`/`span_id` are read from the **live span context** — never generated ad hoc; if there is no active span, omit them rather than fabricate.

### Stdout-only logging (12-Factor XI — HARD RULE)

Logs are written to **stdout/stderr ONLY**. The app never owns log files, rotation, or external sinks — **no file transports, no log-rotation, no `LOG_FILE`** config. The platform (collector/sidecar) captures stdout and ships it. Configure the logger to emit one JSON object per line to stdout and nothing else.

### Statelessness (12-Factor VI — HARD RULE)

Processes are **stateless and share-nothing**. No session, upload, temp, or cache state may live **in-process memory or on local disk** between requests — back it with Redis / an object store / the database. **No sticky sessions** (any instance must serve any request). Local disk is scratch only; anything that must survive a restart or be seen by a sibling instance goes to a backing service.

### PII-safe log redaction (HARD RULE)

Wire a **redaction layer into the logger itself** with a default deny-list so secrets/PII never reach stdout:

```
deny-list (redact to "***" or hash): authorization, cookie, set-cookie, password,
  token, access_token, refresh_token, secret, api_key, ssn, credit_card,
  card_number, cvv, and the request/response BODY by default
```

- TS/Node: **pino `redact`** paths. Python: a **structlog processor** that drops/masks denied keys. JVM: **logback** masking converter / pattern. Equivalent for other stacks.
- **Never log a full request/response body at `info`.** If a body must be logged for debugging, redact denied fields first and gate it behind `debug`.
- Logging a secret is a contract AND a security violation (`security-defaults.md`, `observability-contract.md`).

### Security event logging (HARD RULE)

Emit a **distinct, structured security event** for every security-relevant action so they are alertable and auditable — not buried in request logs (cross-ref `security-defaults.md` "Security event logging" + `observability-contract.md`). Emit one for at least:

- authentication **success** and **failure**, and **logout**
- **403** access-control denials (per-OBJECT/BOLA + role denials)
- **privilege / role change** (grant, revoke, role assignment)
- **password / MFA change** (and credential reset/recovery)
- **boundary validation rejections** (input rejected at the trust boundary)

Each event carries the observability-contract field names — `user_id`, `tenant_id`, `ip`, `action`, `target`, `result`, `trace_id` — plus a **stable `event`/`category` field** so alerting rules can match on a constant, not a free-text message. **Never log secrets/PII** — the redaction deny-list above applies to security events too (log a user/object id, never the credential or the protected payload).

## 3.5 — Rate limiting & resource-consumption limits

Rate is only one axis. Cap **every** unbounded consumer of compute/memory/IO so a single caller can't exhaust the service (cross-ref `security-defaults.md` "Resource-consumption & anti-automation limits"). Implement request rate at two levels:

1. **Global rate limiting** (per IP) — Sliding window, configurable RPM per endpoint
2. **Tenant rate limiting** (per tenant) — Based on plan tier from tenant config

```
Request arrives
  → Check global rate limit (Redis INCR + EXPIRE)
  → Check tenant rate limit (Redis INCR + EXPIRE, keyed by tenant_id)
  → If exceeded: 429 with Retry-After header
  → Set response headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
  → Pass to next middleware
```

**Beyond request rate, every service inherits these resource caps as middleware/config defaults:**
- **Request body-size cap** — reject oversized payloads at the edge (e.g. `413`) before parsing.
- **Mandatory pagination max** — list/collection queries enforce a hard max page size; **reject unbounded list queries** (no `limit` → apply a default, an over-max `limit` → clamp or `400`).
- **JSON depth & array caps** — bound nesting depth and array/element counts on inbound JSON so a hostile body can't blow up the parser.
- **File-upload caps** — per-file size, total request size, and max file count; enforce before buffering.
- **GraphQL / nested-query limits** — query depth + complexity/cost limits (and pagination on connections) so a single nested query can't fan out unboundedly.
- **Server-side timeouts everywhere** — a bounded timeout on the inbound request AND on **every** outbound HTTP / DB / cache / broker call (no unbounded waits; pairs with the per-call timeouts in 3.7).

**Fail closed:** when the limiter's backend (Redis) is unavailable the limiter **denies** rather than fails open — a degraded counter store must not become an unlimited-traffic bypass. Every limit breach returns **`429` with a `Retry-After` header** (size/upload breaches use the appropriate `4xx`).

## 3.6 — Caching Layer

Implement cache-aside pattern in repositories:

```
Read path:
  → Check cache (Redis) by key
  → Cache HIT: return cached entity, log cache hit
  → Cache MISS: query database, store in cache with TTL, return entity

Write path:
  → Write to database
  → Invalidate cache (delete key, not update — avoids race conditions)
  → Emit cache invalidation event (for multi-instance consistency)
```

Cache key convention: `{service}:{entity}:{tenant_id}:{entity_id}` (e.g., `user-service:user:tenant-123:user-456`)

## 3.7 — Retry and Circuit Breaker

For all external calls (HTTP, database, cache, message broker):

**Retry policy:**
- Max retries: 3
- Backoff: Exponential with jitter (100ms, 200ms, 400ms + random 0-100ms)
- Retry on: Network errors, 502, 503, 504, connection timeouts
- Do NOT retry on: 400, 401, 403, 404, 409 (client errors are not transient)

**Circuit breaker:**
- Closed (normal) -> Open (failing) after 5 consecutive failures or >50% error rate in 60s window
- Open -> Half-Open after 30s cooldown
- Half-Open -> Closed after 3 consecutive successes
- Open state returns 503 immediately (fail fast, don't pile up timeouts)

Use existing libraries: resilience4j (Java), polly (.NET), cockatiel (Node.js), go-resilience (Go), tenacity (Python).

## 3.8 — Feature Flags (OpenFeature — GENERATE)

EMIT a provider-agnostic feature-flag client at **`libs/shared/feature-flags/`** built on **OpenFeature** — this is a generation mandate, not an abstraction sketch. Owned by software-engineer; frontend-engineer adds a client hook on top of it; data-scientist EXTENDS it for ML experiments.

```
interface FeatureFlagClient {
  isEnabled(flagKey: string, ctx: { tenantId, userId, environment }): boolean   // boolean flag
  getVariant(flagKey: string, ctx): string                                       // multivariate, returns default on miss
}
```

Scaffold requirements:
- **OpenFeature SDK** with a swappable provider (LaunchDarkly / Unleash / ConfigCat / cloud) — provider-agnostic; the app code never imports a specific vendor SDK directly.
- **ALWAYS-present env/config fallback provider** so flags resolve even with zero external dependencies (`FEATURE_X=true/false` / `config/feature-flags.yaml`).
- **Local cache + streaming** updates from the provider (low-latency reads; live toggles without redeploy).
- **Per-flag SAFE DEFAULT returned fail-static on provider error** — a provider outage NEVER throws and NEVER flips behavior; the registered default for that flag is returned. Ship a **provider-down test** proving each flag resolves to its safe default when the provider is unreachable.

### Checked-in flag registry

EMIT **`config/feature-flags.yaml`** — the source-of-truth registry, a list of:

```yaml
- key: new_billing
  type: boolean
  owner: payments-team
  default: false        # SAFE DEFAULT — returned fail-static on provider error
  created: 2026-06-25
  removal_by: 2026-12-31 # stale-flag expiry; flags are temporary by default
```

Feature flags must be used for: new feature rollouts (percentage-based), tenant-specific features (plan-tier gating), kill switches for degraded mode, and A/B test integration points.

**EMIT the `make flags-check` gate (CANON #8 — software-engineer owns this target).** Since software-engineer owns `config/feature-flags.yaml`, it EMITS the `flags-check` Makefile target (appended to the base Makefile in Phase 05) that validates the registry: well-formed schema, every flag carries a SAFE DEFAULT, and no flag is past its `removal_by` (stale-flag expiry). It exits non-zero on any violation and is wired as a required, non-skippable CI step.

### 3.8.1 — Progressive-rollout primitives (generic machinery, here so every build gets it)

House the generic rollout machinery IN this flag layer so every service gets sticky progressive rollout for free (data-scientist EXTENDS the same primitives for ML experiments — do not fork them):

- **Deterministic hash bucketing** — `bucket = hash("{flagKey}:{stableId}") % 100` (colon delimiter, camelCase `flagKey` and `stableId`); the same `stableId` (user/tenant) always lands in the same bucket, so a user does not flip-flop across requests (sticky assignment). data-scientist's experiment framework consumes this EXACT bucketing input — do not fork a second scheme.
- **Percentage / ring rollout** — advance a flag through cohorts (e.g. internal → 1% → 10% → 50% → 100%, or ring 0..N) using the bucket; rollout state lives in the registry/provider.
- **Guardrail auto-rollback** — bind a flag to guardrail metrics (error rate, latency, the RED instruments from `observability-contract.md`); if a guardrail breaches its threshold during a rollout, auto-revert the flag to its safe default and emit a degradation log.
- **Experiment registry** — record `{ flagKey, variants, allocation, stableId basis, guardrails, start/stop }` so assignments are reproducible and auditable; this is the seam data-scientist extends for ML A/Bs.

## 3.9 — Graceful Degradation

Every external dependency must have a fallback:

| Dependency | Degraded Behavior |
|-----------|-------------------|
| Cache (Redis) down | Bypass cache, serve from database (higher latency, still functional) |
| Message broker down | Queue events locally (in-memory or disk), replay when reconnected |
| External API down | Return cached/default response, log degradation, alert |
| Read replica down | Route reads to primary (higher load, still functional) |
| Feature flag service down | Fall back to cached flags or env-var defaults |
| Auth service down | Accept cached JWT validation (short window), reject new tokens |

Log all degradation events at WARN level with `degraded_dependency` field.

## 3.10 — Telemetry Bootstrap (CRITICAL — GENERATE)

A dashboard that queries a name nothing emits is broken. EMIT a generated **`libs/shared/observability/`** module with per-language OpenTelemetry init, imported as the **FIRST line of the service entrypoint** (before any framework/app import, so auto-instrumentation can patch libraries). Use the EXACT instrument/label/field/attribute names from `observability-contract.md` — no synonyms.

**OpenTelemetry init (`libs/shared/observability/`) sets up, per language:**
- `TracerProvider` + `MeterProvider` + **OTLP exporter** (read `OTEL_EXPORTER_OTLP_ENDPOINT`; honor `OTEL_EXPORTER_OTLP_HEADERS`/`OTEL_SERVICE_NAME`/`OTEL_RESOURCE_ATTRIBUTES` — never hard-code a collector host).
- **Resource attributes** on every export: `service.name`, `service.version`, `deployment.environment` — identical strings to the log `service`/`env` fields and span resource.
- **W3C propagators**: `tracecontext` (`traceparent` + `tracestate`) + `baggage`, installed globally so inbound→outbound HTTP/broker hops keep one unbroken trace (frontend starts it).
- **Auto-instrumentation** for HTTP server/client, DB, cache, and broker clients.

**RED middleware (emit on every HTTP request), EXACT names + labels + buckets:**
- `http_requests_total` — Counter, labels `method, route, status_class` (`route` = templated path, never raw URL).
- `http_request_duration_seconds` — Histogram (seconds, standard buckets `0.005…10`), labels `method, route, status_class`, **with exemplars carrying the `trace_id` from the active span**.
- `http_requests_in_flight` — Gauge, labels `method, route`; increment at start, decrement in a `finally`/deferred path so errors still decrement.
- Plus **USE pool metrics** for db/redis/broker (`<resource>_pool_connections_in_use|max|idle`, `<resource>_pool_wait_seconds`, `<resource>_pool_acquire_errors_total`).

**Exposure & correlation:**
- Metrics exposed at **`GET /metrics`** (Prometheus scrape) — or via the collector — using only contract names.
- Log `trace_id`/`span_id` are derived from the **LIVE span context** (3.4), so logs↔traces↔problem responses join on the same `trace_id`/`route`/`service`.

**Verification-loop item (EMIT a concrete gate — parallel to `make arch`):** "No data = failing gate" must be a *runnable* check, not prose. EMIT a `make smoke-telemetry` target (backed by `scripts/verify-telemetry.sh`) that: boots the stack (`docker-compose up -d`), waits for health, hits a real endpoint, scrapes `GET /metrics`, and **asserts non-zero `http_requests_total` AND the presence of the RED instruments** (`http_requests_total`, `http_request_duration_seconds`, `http_requests_in_flight`) — exiting **non-zero** if any are absent or zero. Wire it as a required, non-skippable CI step (no `|| true` / `continue-on-error`), exactly like `make arch`. A "No data" panel on first run then fails the build by exit code, not by reviewer attention.

## 3.11 — Security Defaults in BUILD (HARD — `security-defaults.md`)

Secure-by-default code is written into the first draft, not bolted on after the audit. Wire these into shared middleware so every service inherits them:

- **Security-header middleware** (helmet or per-stack equivalent): HSTS, `X-Content-Type-Options: nosniff`, `X-Frame-Options`/`frame-ancestors`, `Referrer-Policy`, and a CSP that blocks inline script (no `unsafe-inline`/`unsafe-eval`).
- **Strict CORS allowlist** — an explicit origin allowlist; **reject `*`** and `null`; NEVER combine `Access-Control-Allow-Origin: *` with `Allow-Credentials: true`.
- **Secure cookies** — auth/session cookies are `HttpOnly` + `Secure` + `SameSite=Lax` (or `Strict`); no secrets/PII in `localStorage`; CSRF protection (token or SameSite) on state-changing requests.
- **Per-OBJECT authorization (BOLA/IDOR)** — every single-object read/update/delete checks that the authenticated principal may access **that specific object** (ownership/tenant + object id), enforced at the data-access layer (`WHERE id=? AND owner_id=:session_user`). A tenant `WHERE org_id=` filter alone is NOT sufficient. Authorize from the session/token identity, never a request-supplied `user_id`/`tenant_id`. Default deny → 403/404 (prefer 404 where existence is sensitive). Apply to nested/related objects and bulk operations too.
- **Cryptography** (cross-ref `security-defaults.md` "Strong cryptography: hashing, encryption, randomness") — hash credentials with a **memory-hard KDF** (Argon2id, scrypt, or bcrypt) with a per-credential salt — never a bare SHA/MD5. Use **authenticated encryption** (AES-GCM / ChaCha20-Poly1305) for data at rest — never ECB/unauthenticated modes. Generate all tokens, ids, and nonces from a **CSPRNG** (never `Math.random`/`rand()`). Enforce **TLS 1.2+ on every hop** (inbound and outbound, service-to-service included).
- **Authentication & session lifecycle** (cross-ref `security-defaults.md` "Authentication & credential-handling defaults" + "Session & self-contained-token lifecycle") — credential endpoints (login, reset, token) **throttle + lock out** on repeated failure, expose an **MFA hook**, use **safe account recovery**, and give **no user-enumeration signal** (uniform response/timing for unknown vs known accounts). **Regenerate the session id on privilege change** (login / role elevation); enforce **idle + absolute session timeout**; support **server-side logout / token revocation**. For JWT/self-contained tokens: pin an **algorithm allowlist that rejects `alg=none`** (and alg-confusion) and validate `exp` / `iss` / `aud` on every request.
- **Property-level authorization / mass assignment** (cross-ref `security-defaults.md` "Property-level authorization (mass assignment / BOPLA)") — bind only an **allowlist of client-settable fields**; never spread `req.body` into a model/entity. Set `role` / `tenant` / `owner` and other privileged fields **server-side** from the session, never from the payload. Return **DTO-shaped responses** (an explicit allowlist of fields), never raw rows/entities.

See `security-defaults.md` for the full checklist; the BUILD phase asserts `security-defaults checklist passes` before it closes.

## Validation Loop

Before moving to Phase 4:
- All middleware compiles and passes lint
- Auth middleware correctly validates JWTs and extracts claims
- Tenant resolution correctly scopes all downstream operations
- Error handler maps all app errors to RFC 9457 problem+json via the error-catalog module
- Logging produces valid JSON to stdout with all mandatory fields; redaction deny-list active; distinct security events emitted for authn success/failure, logout, 403 denials, privilege/role change, password/MFA change, and validation rejections
- Rate limiting enforces request-rate limits and returns correct headers; resource caps active (body-size cap, mandatory pagination max — unbounded list rejected, JSON depth/array caps, upload size/count caps, GraphQL depth/complexity limits, inbound + outbound/DB timeouts); limiter **fails closed** (denies when Redis is down) and returns `429` + `Retry-After`
- Cache layer handles HIT, MISS, and invalidation correctly
- Circuit breaker opens after failures and recovers after cooldown
- Feature flag client returns correct values AND each flag falls back to its safe default when the provider is down
- **Telemetry: `docker-compose up`, hit an endpoint → a trace appears in Jaeger AND `/metrics` is populated with the RED instruments**

## Quality Bar

- Zero `any` types in middleware code
- All middleware is independently unit testable
- Integration test demonstrates full middleware chain
- Degradation fallbacks verified with dependency-down tests
- Errors are RFC 9457 problem+json (`application/problem+json`) `$ref`'ing the shared `Problem` schema; runtime + docs both read the generated error-catalog module
- Logs to stdout/stderr ONLY (no file transports/rotation/`LOG_FILE`); processes stateless (no in-process/local-disk session/upload/temp state, no sticky sessions)
- PII redaction deny-list wired into the logger; no full request body logged at `info`
- Security events emitted (distinct, structured, alertable) for authn success/failure, logout, 403 denials, privilege/role change, password/MFA change, and boundary validation rejections — with `user_id`/`tenant_id`/`ip`/`action`/`target`/`result`/`trace_id` + a stable `event`/`category`; no secrets/PII
- Resource-consumption limits active: request body-size cap, mandatory pagination max (unbounded list rejected), JSON depth/array caps, file-upload size/count caps, GraphQL depth/complexity limits, inbound + outbound/DB timeouts; limiter fails closed (denies when Redis down) and returns `429` + `Retry-After`
- Observability init is the FIRST entrypoint import; RED + USE instruments emitted with EXACT contract names/labels/buckets; duration histogram carries trace exemplars; `/metrics` exposed
- Feature-flag client built on OpenFeature with an always-present env/config fallback + per-flag fail-static safe default (provider-down test green); `config/feature-flags.yaml` registry committed
- Security middleware present: security headers, strict CORS allowlist (no `*`), HttpOnly+Secure+SameSite cookies, per-OBJECT default-deny authz (BOLA/IDOR)
- Cryptography defaults: credentials hashed with Argon2id/scrypt/bcrypt + salt; authenticated encryption (AES-GCM/ChaCha20-Poly1305) at rest; CSPRNG for all tokens/ids; TLS 1.2+ every hop
- Authentication & session lifecycle: credential endpoints throttle+lock out, MFA hook, safe recovery, no user enumeration; session id regenerated on privilege change; idle+absolute timeout; server-side logout/revoke; JWT alg-allowlist rejecting `alg=none` + `exp`/`iss`/`aud` validated
- Property-level authz (mass assignment): allowlisted client-settable fields only (no `req.body` spread); role/tenant/owner set server-side; DTO-shaped responses
- **security-defaults checklist passes**
