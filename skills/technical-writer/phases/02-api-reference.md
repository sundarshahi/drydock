# Phase 2: API Reference

## Objective

Generate comprehensive API documentation from OpenAPI/AsyncAPI specs and source code so that an API consumer can integrate without reading source code or asking questions. Every endpoint, authentication method, error code, and webhook event is documented with working examples.

## 2.1 — Mandatory Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| OpenAPI specs | `api/openapi/*.yaml` | Endpoints, schemas, auth requirements |
| AsyncAPI specs | `api/asyncapi/*.yaml` | Webhook events, payload schemas |
| Auth middleware | `services/*/src/middleware/auth*` | Authentication methods, token formats |
| **Error catalog module** | `libs/shared/errors/catalog.*` | **Single source for the error-code table** — entries `{ code, http_status, title, message_template, remediation, docs_anchor }` (the SAME module the runtime error handler reads) |
| `Problem` schema | `api/openapi/components.yaml` | Reusable RFC 9457 `Problem` component (owned by solution-architect) referenced by every error response |
| Rate limit config | `services/*/src/middleware/rate-limit*` | Rate tiers, limit values |
| Content inventory | `Shipyard/technical-writer/content-inventory.md` | Phase 1 gap analysis results |

## 2.2 — Authentication Documentation

Generate `docs/api-reference/authentication.md`:

1. **Overview** — One paragraph: what auth method is used, how to obtain credentials
2. **Getting credentials** — Step-by-step instructions for obtaining API keys or tokens
3. **Using credentials** — Header authentication (recommended) and query parameter authentication (with security warning)
4. **Authentication errors** — Table with status code, error code, description, and resolution
5. **Code examples** — Working examples in Python, JavaScript, and Go (minimum three languages)
6. **Token refresh flow** — If using OAuth2/JWT, document the refresh cycle

Every code example must be complete and copy-pasteable. No pseudo-code, no `...` ellipsis in runnable blocks.

## 2.3 — Endpoint Reference

Generate `docs/api-reference/endpoints/<resource-name>.md` — one file per API resource.

Each endpoint page follows this template:

```
# <Resource Name>

## List <Resources>
`GET /v1/<resources>`

<One-sentence description>

### Authentication
Required. Scope: `<resource>:read`

### Query Parameters
| Parameter | Type | Required | Default | Description |

### Response (200)
```json
{ ... complete example ... }
```

### Error Responses
| Status | Code | Description |

### cURL Example
```bash
curl -X GET ... complete command ...
```
```

For each endpoint document: method, path, auth scope, all parameters (path, query, body), request body schema, response schema with example, all error responses, and a working cURL example.

## 2.4 — Error Codes Reference (GENERATED from the error-catalog — single source of truth)

`docs/api-reference/error-codes.md` is **GENERATED, never hand-typed.** The runtime error handler and this docs table read the SAME module — `libs/shared/errors/catalog.*` — so they cannot drift. Hand-editing the generated table is a defect that `docs:gen-check` fails on.

### 2.4.1 — Document the RFC 9457 problem+json format (top of the page)

The page opens by documenting the canonical error body. Every 4xx/5xx response is `Content-Type: application/problem+json` with the reusable OpenAPI **`Problem`** schema (owned by solution-architect, `$ref`'d from every error response). Show the exact shape:

```json
{
  "type": "https://errors.example.com/validation-error",
  "title": "Request validation failed",
  "status": 400,
  "detail": "body.email must be a valid email address",
  "instance": "/v1/users",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "errors": [ { "pointer": "/email", "detail": "must be a valid email address" } ]
}
```

Document each field: `type` (URI reference, also the link to this code's docs anchor), `title`/`status`/`detail`/`instance` per RFC 9457, and the standard extensions `trace_id` (string, read from the live span — lets a consumer quote it in a support request) and `errors[]` (array of `{ field|pointer, detail }`). State explicitly there is NO bespoke `{code,message,details}` envelope anywhere in the API.

### 2.4.2 — Generate the code table from the catalog

EMIT `scripts/gen-error-docs.*` (a checked-in generator, run in CI) that imports the error-catalog module and renders the table. For each catalog entry `{ code, http_status, title, message_template, remediation, docs_anchor }` it emits one row, and for each `docs_anchor` it emits a linkable section so `type` URIs resolve:

```markdown
| HTTP Status | Error Code | Title | Resolution | Reference |
|-------------|-----------|-------|------------|-----------|
| 400 | `VALIDATION_ERROR` | Request validation failed | Check the request body against the schema | [#validation-error](#validation-error) |
| 401 | `AUTH_MISSING` | No authentication provided | Include a `Bearer` token in the `Authorization` header | [#auth-missing](#auth-missing) |
```

- The table is rendered from catalog entries — do NOT invent codes or statuses that the catalog does not contain, and do NOT omit ones it does.
- Each `code` links to its `docs_anchor` section (which expands `message_template` + `remediation`), and the `Problem.type` URI for that code points at the same anchor — so a consumer who gets a `type` URL lands on the right docs section.
- Group rendered rows by category: authentication, validation, resource, rate limiting, server.

### 2.4.3 — Wire the gate

`scripts/gen-error-docs.*` runs in `docs-build.yml`; the job then `git diff --exit-code docs/api-reference/error-codes.md`. If a human hand-edited the table (drift), or the catalog changed without regenerating, the **build FAILS**. This is the single-source-of-truth enforcement — not a convention.

## 2.5 — Rate Limiting Documentation

Generate `docs/api-reference/rate-limiting.md`:

1. **Rate limit tiers** — Table showing limits by plan/API key type
2. **Rate limit headers** — Document `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
3. **Handling 429 responses** — Exponential backoff strategy with code examples in Python and JavaScript
4. **Requesting increases** — Process for requesting higher rate limits

## 2.6 — Webhook Documentation

Generate `docs/api-reference/webhooks.md` (if AsyncAPI specs or webhook implementation exists):

1. **Available events** — Table of all webhook events with descriptions
2. **Payload format** — JSON example for each event type
3. **Signature verification** — Code examples for verifying webhook signatures in Python, JavaScript, and Go
4. **Retry policy** — How failed deliveries are retried (intervals, max attempts)
5. **Testing locally** — Step-by-step instructions using ngrok or localtunnel
6. **Best practices** — Respond with 200 quickly, process asynchronously, handle duplicate deliveries

## 2.7 — Auto-Generated Reference

Generate artifacts in `docs/api-reference/generated/`:

1. Copy the OpenAPI spec as `openapi.json` for consumers to download
2. Generate `openapi.html` using Redoc standalone HTML (single-file, works without a server)
3. This serves as a machine-readable fallback that works independently of the Docusaurus site

## 2.8 — Runnable API Collection (GENERATED from OpenAPI)

EMIT a runnable API collection so a consumer can fire real requests in minutes — **derived from the OpenAPI spec, not hand-written** (a drifted collection sends wrong requests). Choose ONE format:

- **Bruno collection** — `docs/api-collection/<api>.bru` files (git-friendly, no cloud account), OR
- **`.http` file** — `docs/api-collection/<api>.http` (VS Code REST Client / JetBrains HTTP client).

EMIT `scripts/gen-api-collection.*` (checked-in, run in CI) that reads `api/openapi/*.yaml` and emits one request per operation, including: method + templated path, required headers (auth), a representative request body from the schema example, and an `{{baseUrl}}`/`{{token}}` variable block. Wire it into `docs-build.yml` with `git diff --exit-code docs/api-collection/` so a drifted or hand-edited collection FAILS the build (same gate family as the error table). Do not invent endpoints, params, or auth schemes the spec does not define.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Authentication guide | `docs/api-reference/authentication.md` |
| Endpoint pages | `docs/api-reference/endpoints/<resource>.md` (one per resource) |
| Error codes reference (GENERATED) | `docs/api-reference/error-codes.md` |
| Error-docs generator | `scripts/gen-error-docs.*` |
| Rate limiting guide | `docs/api-reference/rate-limiting.md` |
| Webhooks guide | `docs/api-reference/webhooks.md` |
| OpenAPI JSON | `docs/api-reference/generated/openapi.json` |
| Redoc HTML | `docs/api-reference/generated/openapi.html` |
| Runnable API collection (GENERATED) | `docs/api-collection/<api>.bru` or `<api>.http` |
| API-collection generator | `scripts/gen-api-collection.*` |

## Validation Loop

Before moving to Phase 3:
- Every endpoint in the OpenAPI spec has a corresponding documentation page
- Authentication guide has working code examples in at least 3 languages
- `docs/api-reference/error-codes.md` is regenerated by `scripts/gen-error-docs.*` and matches the catalog (`docs:gen-check` / `git diff --exit-code` clean) — never hand-edited
- Error page documents RFC 9457 `application/problem+json` with `{type,title,status,detail,instance}` + `trace_id`/`errors[]`, and every code links to its `docs_anchor`
- Runnable API collection regenerated by `scripts/gen-api-collection.*` and clean under `git diff --exit-code`
- All code examples are complete (no `...` or placeholders in runnable code) so the devops `docs-examples` job can run them
- Webhook documentation covers all events in AsyncAPI spec (if applicable)
- `<!-- TODO -->` comments are inserted where source artifacts are missing (never fabricate)

## Quality Bar

- API consumer can integrate using only these docs (no source code needed)
- Every code example includes expected output or response
- Error table has resolution steps, not just descriptions
- Rate limiting section includes backoff code, not just prose
