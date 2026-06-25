# Security Defaults — Secure-by-Default BUILD Contract (OWASP ASVS L2 / Proactive Controls)

**Core principle: Every BUILD agent ships secure-by-default code at write time — you do not wait for the HARDEN audit to add validation, authz, or output encoding. The audit confirms; it does not retrofit the basics.**

These are non-negotiable defaults for any code that touches external input, data stores, outbound calls, auth, or rendering. Each rule maps to OWASP ASVS L2 and the OWASP Proactive Controls (OPC) and is written so a reviewer can verify pass/fail by reading the diff. A BUILD phase is not complete until the **BUILD Quality Bar line** below asserts these pass. (Runtime request validation is owned here; the existing `input-validation.md` covers SKILL-ARTIFACT dependency validation only — cross-reference, do not duplicate.)

---

## Validate ALL external input at the trust boundary  (ASVS V5.1 / OPC C5)

- Validate every input crossing the trust boundary: request body, query string, path params, headers/cookies, file uploads, and event/webhook payloads. Untrusted until proven valid.
- **Fail closed.** Reject on validation failure; never coerce-and-continue. Default to deny when a field is absent, malformed, or out of range.
- **Allowlist, not denylist.** Constrain by type, length, range, format, and enum membership (e.g. Zod/Pydantic/JSON-Schema). Validate the parsed value against an explicit schema before use — do not regex-blacklist "bad" strings.
- Validate at the server boundary regardless of any client-side checks. Client validation is UX, never a control.
- For uploads: verify content-type + magic bytes, cap size, generate a server-side filename, store outside the web root. Never trust the supplied filename or extension.
- Canonicalize before validating (decode once, normalize Unicode/path) so `../`, double-encoding, and homoglyphs cannot bypass the check.

---

## Parameterized queries / prepared statements ONLY  (ASVS V5.3 / OPC C3)

- All SQL/NoSQL goes through parameterized queries, prepared statements, or a vetted query builder/ORM with bound params. **Zero** string-concatenated or template-interpolated queries containing user input.
- This includes `LIKE`, `IN (...)`, and dynamic sort/limit — bind values; for identifiers (table/column/direction) map user input through a fixed allowlist, never interpolate it raw.
- NoSQL: reject operator injection — never pass a raw request object as a query filter (e.g. `{ user: req.body.user }` lets `{$ne:null}` through); coerce to expected scalar types first.
- No shell/OS command built from user input; use argument arrays / exec-with-args, never `sh -c "... ${input}"`.

---

## Context-aware output encoding & safe templating  (ASVS V5.2 / OPC C4)

- Encode output for its exact sink: HTML body, HTML attribute, JS, URL, and CSS each need their own encoding. Rely on the framework's auto-escaping; do not hand-roll concatenated HTML.
- **No unsanitized HTML injection.** No React `dangerouslySetInnerHTML`, Angular `bypassSecurityTrust*`, Vue `v-html`, or `innerHTML` with user data unless the value passes a vetted sanitizer (DOMPurify with a strict allowlist) first.
- Use parameterized/auto-escaping templates; never disable the engine's escaping globally. Keep user data out of executable contexts (`<script>`, `on*=` handlers, `javascript:` URLs).
- Set/serve a Content-Security-Policy that blocks inline script (no `unsafe-inline`/`unsafe-eval`) as defense-in-depth.

---

## SSRF allowlist on user-controlled outbound URLs  (ASVS V5.2.6 / OPC C5)

- Any outbound request whose URL, host, or port is influenced by user input goes through an explicit destination allowlist (scheme + host + port). Reject everything not on it.
- Block internal/loopback/link-local/metadata ranges by default: `127.0.0.0/8`, `::1`, `10/8`, `172.16/12`, `192.168/16`, `169.254.169.254`, `*.internal`. Resolve the hostname and validate the **resolved IP** (defeat DNS-rebind), not just the string.
- Disable or cap redirect following; re-validate the target host after each redirect. Never let a redirect walk you off the allowlist.

---

## Secrets only from env / secret manager  (ASVS V6.4 / OPC C8)

- Read every credential, token, API key, and connection string from environment variables or a secret manager (Vault, AWS/GCP/Azure secret stores, Wrangler secrets). **Never** hardcode a secret in source, config committed to git, or a client bundle.
- **Never log secrets.** Redact tokens/passwords/keys from logs, error messages, and traces; keep them out of URLs (query strings get logged). Scrub before emitting.
- Commit a `.env.example` with key names only (no values). Fail fast at startup if a required secret is missing — do not run with an empty default.

---

## Default-DENY per-OBJECT authorization (BOLA / IDOR)  (ASVS V4.2 / OPC C7)

- Every single-object read/update/delete checks that the authenticated principal owns or may access **that specific object** — ownership/tenant + object id — before acting. A tenant/`WHERE org_id=` filter alone is NOT sufficient for object-level access.
- Authorize server-side from the session/token identity; never trust a `user_id`/`role`/`tenant_id` supplied in the request body, query, or header to decide access.
- Default deny: the handler must explicitly grant. Missing or unrecognized authz path = 403/404, not implicit allow. Prefer 404 over 403 where existence itself is sensitive.
- Enforce at the data-access layer (scoped query: `WHERE id=? AND owner_id=:session_user`) so a forgotten controller check cannot leak the row. Apply the same check to nested/related objects and bulk operations.

---

## Security headers, strict CORS, secure cookies  (ASVS V3 / V13 / OPC C7)

- Apply a security-header middleware (helmet or equivalent): HSTS, `X-Content-Type-Options: nosniff`, `X-Frame-Options`/frame-ancestors, Referrer-Policy, and a CSP.
- **CORS is an explicit origin allowlist.** Never reflect arbitrary `Origin`; never combine `Access-Control-Allow-Origin: *` with `Allow-Credentials: true`. Reject `null` and wildcard origins for credentialed requests.
- Session/auth cookies are `HttpOnly` + `Secure` + `SameSite=Lax` (or `Strict`). No secrets/PII in `localStorage`. Enforce CSRF protection (token or `SameSite`) on state-changing requests.

---

## Dependency pinning, lockfile, post-add SCA  (ASVS V14.2 / OPC C2)

- Pin dependencies and commit the lockfile (`package-lock.json`/`pnpm-lock.yaml`/`poetry.lock`/`Cargo.lock`/`go.sum`). No floating `latest`/`*` ranges for production deps.
- **After adding or bumping any dependency, run SCA** (`osv-scanner`, `npm audit`, `pip-audit`) and resolve High/Critical before the BUILD phase completes; record the result.
- Verify a new package exists in the registry and is the intended name (typosquat/slopsquat check) before adding — cross-reference `grounding-protocol.md` (no hallucinated packages). Use `--ignore-scripts` when installing in untrusted contexts.

---

## LLM / AI security defaults  (OWASP LLM Top 10: LLM01 / LLM02 / LLM06)

- **Treat model output as untrusted input.** Validate, encode, and never `eval`/exec it or render it as raw HTML. Output flowing to a sink (SQL, shell, DOM, file path) passes the same boundary rules as any user input.
- **No secrets, keys, or full PII in prompts** or system context; assume prompt content can leak. Keep credentials in the tool/runtime, not the prompt.
- **Gate tool/function calls** the model can trigger: allowlist the callable tools, validate arguments against a schema, enforce least privilege, and require confirmation for irreversible/destructive actions. The model does not get ambient authority.
- **Guard against prompt injection:** keep a trust boundary between system instructions and untrusted content (retrieved docs, web pages, user text); do not let fetched content silently rewrite instructions or exfiltrate context.

---

## BUILD Quality Bar line

Every BUILD phase MUST end by asserting, in its completion receipt/summary:

> **`security-defaults checklist passes`** — input validated at the boundary (fail-closed, allowlist); queries parameterized; output context-encoded (no unsanitized HTML); SSRF allowlist on user-controlled outbound; secrets from env/secret-manager and never logged; per-object default-deny authz (no BOLA/IDOR); security headers + strict CORS + secure cookies; deps pinned + lockfile committed + SCA clean; LLM output treated as untrusted + tool-calls gated.

A BUILD phase that cannot assert this line is **not complete**. Any consciously deferred item is logged explicitly as a HARDEN hand-off with reason — never silently skipped.

---

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| `db.query("SELECT * FROM u WHERE id=" + req.params.id)` | `db.query("SELECT * FROM u WHERE id=$1", [id])` with parameter binding |
| `WHERE org_id = :tenant` and returning the row | `WHERE id = :id AND owner_id = :session_user` — object-level check |
| `dangerouslySetInnerHTML={{__html: comment}}` | `DOMPurify.sanitize(comment)` with a strict allowlist, or render as text |
| `fetch(req.query.url)` for a user-supplied URL | Allowlist scheme+host+port, validate the resolved IP, cap redirects |
| `const KEY = "sk-live-..."` in source | `const KEY = process.env.API_KEY` from a secret manager; `.env.example` keys only |
| `Allow-Origin: *` with `Allow-Credentials: true` | Explicit origin allowlist; reject wildcard + credentials together |
| Validating only in the browser | Server-side schema validation at the trust boundary, fail-closed |
| `exec(\`SELECT \${model_output}\`)` on LLM output | Treat model output as untrusted; bind params; gate tool-calls |

---

## Key Principle

**Secure defaults are written into the first draft, not bolted on after the audit. If a handler reads input, hits a store, calls outbound, decides access, or renders output, the matching default above is already in the diff — and the BUILD phase asserts `security-defaults checklist passes` before it closes.**
