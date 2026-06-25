# Security Defaults — Secure-by-Default BUILD Contract (OWASP ASVS 5.0 L2 / Proactive Controls)

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

## Strong cryptography: hashing, encryption, randomness  (ASVS V11 / OPC C8)

- **Hash credentials with a memory-hard KDF** — Argon2id (preferred), scrypt, or bcrypt, each with a per-user salt and a tuned cost factor. NEVER store passwords in plaintext or reversible encryption; NEVER use fast/raw hashes (MD5, SHA-1, unsalted SHA-256) for credentials.
- **Encrypt sensitive data with authenticated encryption** — AES-256-GCM or ChaCha20-Poly1305. No ECB, no unauthenticated modes, no hand-rolled crypto. Use a fresh random nonce/IV per message; never reuse an IV under the same key.
- **Generate every security-bearing value from a CSPRNG** — session ids, reset/verification tokens, API keys, OTPs, and salts come from `crypto.randomBytes` / `secrets.token_urlsafe` / `crypto/rand`. NEVER `Math.random()` / `random.random()` / `rand()`.
- **TLS in transit on every hop** — enforce TLS 1.2+ (prefer 1.3), including service-to-service; no plaintext fallback. Key material is read from the secret manager, is rotatable, and is never logged.
- Pick algorithms that are current at build time (cross-reference `freshness-protocol.md`); do not pin to one a later audit will flag as deprecated.

---

## Authentication & credential-handling defaults  (ASVS V6 / OPC C6)

- **Throttle and lock out credential endpoints** — login, password-reset, OTP/MFA-verify, and token endpoints get per-account AND per-IP rate limiting plus progressive backoff/lockout to defeat credential stuffing and brute force (wire to the resource-consumption limits below).
- **Make MFA possible** — provide a second-factor hook (TOTP/WebAuthn) for privileged or account-sensitive flows; never design auth that structurally precludes it.
- **Score password strength, don't dictate composition** — enforce a minimum length and screen against known-breached/common passwords; do not impose arbitrary composition or forced-rotation rules (NIST 800-63B).
- **Safe account recovery** — reset/verification tokens are CSPRNG-generated, single-use, and short-TTL, delivered out-of-band; reset never reveals whether an account exists; invalidate existing sessions on password change.
- **No user enumeration** — login, reset, and registration return uniform responses and timing for "no such user" vs "wrong credential".

---

## Session & self-contained-token lifecycle  (ASVS V7 / V9 / OPC C6)

- **Session IDs from a CSPRNG with sufficient entropy**, carried in `HttpOnly`+`Secure`+`SameSite` cookies (see headers section). **Regenerate the session id on login and on any privilege/role change** (anti-fixation).
- **Expire and revoke** — enforce both idle and absolute timeouts; invalidate the session server-side on logout, password change, and privilege change. A logout that only clears the client is not a logout.
- **JWT / self-contained tokens** — verify the signature against an **explicit algorithm allowlist (reject `alg=none`; never honor a caller-chosen alg)**; validate `exp`/`nbf`/`iss`/`aud`; keep access-token TTL short and pair it with a revocable refresh token. No secrets or PII in claims (a JWT is base64, not encrypted).
- Never place session ids or tokens in URLs/query strings — they leak via logs and the `Referer` header.

---

## Resource-consumption & anti-automation limits  (API4:2023 / API6:2023)

- **Bound every request** — cap request body size, JSON depth/array length, file-upload size/count, and page size (enforce a max `limit`; reject unbounded list queries). Set server-side timeouts on inbound requests and on every outbound/DB call.
- **Bound expensive operations** — depth/complexity/cost limits on GraphQL and any nested/recursive query; pagination is mandatory on list endpoints; apply per-tenant quotas/cost ceilings where a request can fan out or spend money.
- **Anti-automation on sensitive business flows** — signup, login, password reset, checkout/purchase, invite, and comment flows get anti-automation (rate/velocity limits; CAPTCHA or proof-of-work where abuse is likely) beyond plain per-IP throttling.
- Rate-limit responses are `429` with `Retry-After`; the limiter **fails closed** (deny when its backend is unavailable, never bypass).

---

## Property-level authorization (mass assignment / BOPLA)  (API3:2023 / ASVS V4 / OPC C7)

- **Bind only allowlisted fields on writes.** Never spread a raw request object into a model/ORM create or update (`new User(req.body)`, `Object.assign(entity, req.body)`, `Model(**request.json)`). Map an explicit allowlist of client-settable fields; ignore everything else.
- **Server-controlled fields are never client-settable** — `role`, `is_admin`, `tenant_id`, `owner_id`, `balance`, `verified`, pricing, and status are set server-side from session/trusted state, never from the payload.
- **Allowlist the response shape too** — serialize via an explicit DTO/view; never return whole DB rows (excessive data exposure). Strip internal/sensitive fields (password hash, tokens, internal flags).

---

## Treat third-party / upstream API responses as untrusted  (API10:2023 / OPC C5)

- Apply the same boundary rules to data you *receive* from third-party/integrated APIs as to user input: validate against a schema, constrain types/sizes, and encode before it reaches any sink (DB, DOM, shell, file path).
- Set timeouts, size caps, and retry/circuit-breaker limits on outbound calls; never block indefinitely on a slow upstream. Route any redirect through the SSRF allowlist (see SSRF section).
- Never `eval`/deserialize an untrusted upstream payload into executable objects; verify webhooks (signature + replay/nonce protection) before acting on them.

---

## Security event logging  (A09 / ASVS V16 / OPC C9)

- **Emit a structured security event** (distinct from request logs) for: authentication success/failure, logout, password/MFA change, access-control denials (`403`), privilege/role change, and input-validation rejections at the boundary. Include `user_id`, `tenant_id`, source IP, action, target, result, and `trace_id` — the exact field names from `observability-contract.md`.
- **Never log secrets or full PII** in these events (the redaction deny-list still applies); log identifiers, not credentials.
- Make security events queryable via a stable `event`/`category` field so detection and alerting can fire on them — never bury an auth failure inside a generic `info` line.

---

## BUILD Quality Bar line

Every BUILD phase MUST end by asserting, in its completion receipt/summary:

> **`security-defaults checklist passes`** — input validated at the boundary (fail-closed, allowlist); queries parameterized; output context-encoded (no unsanitized HTML); SSRF allowlist on user-controlled outbound; secrets from env/secret-manager and never logged; per-object default-deny authz (no BOLA/IDOR); property-level authz (no mass assignment, DTO-shaped responses); security headers + strict CORS + secure cookies; deps pinned + lockfile committed + SCA clean; LLM output treated as untrusted + tool-calls gated; strong crypto (KDF-hashed credentials, authenticated encryption, CSPRNG tokens, TLS 1.2+); auth throttled + lockout + safe recovery; session/JWT lifecycle (regenerate on privilege change, server-side revoke, alg-allowlist); resource-consumption + anti-automation limits (body/page/depth caps, timeouts); third-party responses treated as untrusted; security events logged (authn/authz/denials).

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
| `md5(password)` / storing the password in plaintext | Argon2id/scrypt/bcrypt + per-user salt; never raw/fast hashes for credentials |
| `Math.random()` for a reset token / session id | CSPRNG — `crypto.randomBytes` / `secrets.token_urlsafe` / `crypto/rand` |
| `jwt.verify(token)` accepting any alg (or `alg:none`) | Verify against an explicit alg allowlist; validate `exp`/`iss`/`aud` |
| `new User(req.body)` / `Object.assign(entity, req.body)` | Bind an allowlist of client-settable fields; set `role`/`tenant_id`/`owner_id` server-side |
| Returning the raw DB row to the client | Serialize via an explicit DTO; strip password hash, tokens, internal flags |
| `findAll()` with no pagination / no body-size cap | Mandatory max page size + body/depth/upload caps + request & outbound timeouts |
| Logout that only clears the client cookie | Invalidate the session server-side; regenerate the id on privilege change |
| Trusting a webhook / third-party JSON as-is | Validate the schema, verify the signature, cap size + timeout before acting |
| Auth failure swallowed in a generic `info` log | Emit a structured security event (authn/authz/denial) with `user_id`/`trace_id` |

---

## Key Principle

**Secure defaults are written into the first draft, not bolted on after the audit. If a handler reads input, hits a store, calls outbound, decides access, or renders output, the matching default above is already in the diff — and the BUILD phase asserts `security-defaults checklist passes` before it closes.**
