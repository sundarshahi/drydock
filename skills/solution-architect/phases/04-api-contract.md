# Phase 4 — API Contract Design

Generate API contracts at `api/` (or `paths.api_contracts` from config) at the project root:

- **OpenAPI 3.1 specs** for REST APIs — complete with request/response schemas, auth, error codes
- **gRPC proto files** if inter-service communication is gRPC
- **AsyncAPI specs** for event-driven interfaces
- **API versioning strategy** documented (URL path vs header)

The architect OWNS the cross-skill API contracts below. software-engineer (runtime mapping), technical-writer (error table/docs), and code-reviewer (consume + verify) READ these — they are defined ONCE here as reusable OpenAPI components and `$ref`'d everywhere.

## Canonical error contract — RFC 9457 `Problem` (application/problem+json)

**Replace the bespoke `{code, message, details, trace_id}` envelope.** The canonical error contract is RFC 9457 `application/problem+json`. Define a single reusable component schema named **`Problem`** in `api/openapi/components.yaml` (or the shared `components` block) and `$ref` it from EVERY error response (4xx/5xx). The architect OWNS this schema.

```yaml
components:
  schemas:
    Problem:
      type: object
      description: RFC 9457 problem detail. The canonical error body for every 4xx/5xx response.
      required: [type, title, status]
      properties:
        type:     { type: string, format: uri-reference, default: "about:blank",
                    description: "URI reference identifying the problem type (stable per error code)." }
        title:    { type: string, description: "Short, human-readable summary; stable per type." }
        status:   { type: integer, format: int32, minimum: 100, maximum: 599 }
        detail:   { type: string, description: "Human-readable explanation specific to this occurrence." }
        instance: { type: string, format: uri-reference, description: "URI reference identifying this occurrence." }
        # standard extensions (cross-skill contract):
        trace_id: { type: string, description: "Correlation id; matches the observability-contract trace_id." }
        errors:
          type: array
          description: "Field-level validation errors."
          items:
            type: object
            properties:
              field:   { type: string, description: "Field name OR JSON Pointer (e.g. /items/0/qty)." }
              pointer: { type: string }
              detail:  { type: string }
```

Rules:
- Every error response sets **`Content-Type: application/problem+json`** and `$ref`s `#/components/schemas/Problem` — no inline error bodies, no second error shape anywhere in the spec.
- `trace_id` is the SAME correlation id as the observability contract's `trace_id` (read from the live span). Do not invent a parallel id.
- **Error catalog is the source of truth for the values.** `Problem.type`/`title`/`status` are populated at runtime from a single error-catalog module (`libs/shared/errors/catalog.*`) with entries `{ code, http_status, title, message_template, remediation, docs_anchor }`. BOTH the runtime mapper (app error → `Problem`) and the technical-writer's docs error table READ this one catalog. The architect specifies the catalog's existence + shape in an ADR / scaffold stub; software-engineer implements the mapping.

## Reusable `IdempotencyKey` header — REQUIRED on all unsafe POST/PATCH

Declare a reusable header parameter and require it on every non-idempotent mutation:

```yaml
components:
  parameters:
    IdempotencyKey:
      name: Idempotency-Key
      in: header
      required: true
      schema: { type: string, format: uuid }
      description: >
        Client-generated key. Replaying the same key with the SAME request returns the original
        result (replay). Reusing a key with a DIFFERENT request body returns 409 Conflict; a malformed
        key returns 422. Servers persist key→result for a documented retention window.
```

- Every unsafe `POST`/`PATCH` (and any non-idempotent `PUT`/`DELETE`) `$ref`s `parameters/IdempotencyKey` and documents `409` (key reuse with mismatched body) and `422` (malformed key) responses — both `$ref` `Problem`.
- This is the spec-level realization of the "idempotency for all write operations" design principle.

## Reusable `CursorPage<T>` pagination — REQUIRED on every list endpoint

Every list/collection endpoint returns the cursor-page envelope (cursor-based for production; `offset` only for admin/internal):

```yaml
components:
  schemas:
    PageInfo:
      type: object
      required: [has_more, limit]
      properties:
        next_cursor: { type: string, nullable: true, description: "Opaque cursor for the next page; null at the end." }
        has_more:    { type: boolean }
        limit:       { type: integer, minimum: 1 }
    # CursorPage<T> is composed per resource: data[] of T + page_info.
    # e.g. UserPage: { allOf: [ { properties: { data: { type: array, items: { $ref: '#/components/schemas/User' } },
    #                                            page_info: { $ref: '#/components/schemas/PageInfo' } } } ] }
```

- Shape is fixed: `data[]` (the items) + `page_info { next_cursor, has_more, limit }`. Every list endpoint `$ref`s `PageInfo` and supplies a typed `data[]`.

## OpenAPI Governance — validate + lint, BLOCK handoff until clean

After writing `api/openapi/*.yaml`, the spec is NOT handed off until it is **valid AND clean**:

1. **Structural validation** — run an OpenAPI 3.1 validator (e.g. `redocly lint` / `swagger-cli validate` / `openapi-spec-validator`). Spec must parse and be schema-valid.
2. **Spectral ruleset lint** — author/emit a default ruleset at **`api/.spectral.yaml`** (a new artifact this skill OWNS) and run `spectral lint api/openapi/*.yaml`. The default ruleset MUST assert at minimum:
   - extends `spectral:oas`;
   - every operation has an `operationId`, `summary`, and `tags`;
   - every `4xx`/`5xx` response `$ref`s `#/components/schemas/Problem` and uses `application/problem+json`;
   - every unsafe `POST`/`PATCH` references `parameters/IdempotencyKey`;
   - every list/array-returning operation uses the `PageInfo`/cursor-page envelope;
   - no inline error schemas; security scheme declared; no `$ref` to undefined components.
3. **BLOCKING gate:** any validator error or Spectral error blocks the phase. Handoff to software-engineer/technical-writer happens only on validator exit 0 AND `spectral lint` with zero errors (warnings recorded). Cite the actual tool output — never assert "the spec is clean" without an observed exit 0.

## Performance Budget Artifact — `docs/architecture/performance-budget.yaml` (single source of truth)

Emit `docs/architecture/performance-budget.yaml` per the shared PERFORMANCE BUDGET contract. This is the ONE place perf targets live; frontend/qa/sre/devops READ it and MUST NOT hardcode 500ms/200KB. It is ALWAYS emitted (see Always-Resolved Defaults) — even in Express/Standard mode resolve a sensible default from the chosen scale + data-type.

Shape:
```yaml
# docs/architecture/performance-budget.yaml
api:
  "GET /users/{id}":      { p95_ms: 300, p99_ms: 800, throughput_rps: 200, error_rate_pct: 0.5 }
  "POST /orders":         { p95_ms: 500, p99_ms: 1200, throughput_rps: 100, error_rate_pct: 1.0 }
web_vitals:
  lcp_ms: 2500
  inp_ms: 200
  cls: 0.1
bundle:
  main:   { max_kb: 200 }
  vendor: { max_kb: 350 }
```

**Default-resolution table** (apply when the user gives no explicit numbers — derive from scale + data-pattern; route-level rows default to the per-tier API row):

| Scale / data-type | api p95 / p99 (ms) | throughput (rps) | error_rate (%) | web_vitals (lcp/inp/cls) | bundle main (KB) |
|-------------------|--------------------|--------------------|------------------|--------------------------|-------------------|
| Small / balanced-CRUD (default) | 500 / 1200 | 50 | 1.0 | 2500 / 200 / 0.1 | 200 |
| Medium / read-heavy | 300 / 800 | 200 | 0.5 | 2000 / 200 / 0.1 | 200 |
| Medium / write-heavy | 500 / 1500 | 150 | 1.0 | 2500 / 200 / 0.1 | 200 |
| Large / high-availability | 200 / 500 | 1000 | 0.1 | 1800 / 150 / 0.1 | 180 |
| Real-time | 150 / 400 | 500 | 0.5 | 2000 / 100 / 0.1 | 200 |

These align with the latency/availability rows in the Phase 1 fitness function and the `http_request_duration_seconds` instrument in `observability-contract.md` (note the budget is in **ms** for human-readability; the runtime histogram is in **seconds**).

Standards enforced:
- **Canonical error body is RFC 9457 `Problem`** (above) — no `{code, message, details, trace_id}` envelope.
- Pagination via the reusable `CursorPage<T>` / `PageInfo` envelope (`cursor-based` for production, `offset` only for admin).
- Idempotency via the reusable `IdempotencyKey` header on all unsafe writes.
- Rate limiting headers (`X-RateLimit-*`)
- Request ID propagation (`X-Request-ID`) — echoed into the log `request_id` field per the observability contract.

## Phase 4 Quality Bar (gate — do not hand off until all true)

- [ ] Reusable `Problem` schema defined ONCE; every 4xx/5xx response `$ref`s it and serves `application/problem+json`; zero inline error bodies.
- [ ] Error-catalog source-of-truth (`libs/shared/errors/catalog.*` shape) specified for runtime + docs to read.
- [ ] `IdempotencyKey` header declared once and `$ref`'d on every unsafe POST/PATCH, with 409/422 responses.
- [ ] `PageInfo`/cursor-page envelope declared once and used by every list endpoint.
- [ ] `api/.spectral.yaml` default ruleset emitted; OpenAPI validator AND `spectral lint` both run with **zero errors** (observed exit 0) before handoff.
- [ ] `docs/architecture/performance-budget.yaml` emitted with a resolved budget (explicit numbers or default-table row); no hardcoded perf targets elsewhere.
