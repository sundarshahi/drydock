# Phase 2: Code Security Audit

## Objective

Systematically audit the entire codebase against the **OWASP Top 10:2025 (Release Candidate 1, published 6 Nov 2025 — not yet ratified; 2021 remains the last finalized list)**, plus the **OWASP API Security Top 10 (2023)** and — when LLM/ML usage is present — the **OWASP Top 10 for LLM Applications (2025)**. Drydock deliberately audits against the 2025 RC1 categories (ahead of ratification) so reports are forward-compatible; the A01..A10:2025 mappings below are correct against RC1. security-engineer is the SOLE AUTHORITY on OWASP code review -- no other skill performs OWASP analysis. Every finding must reference specific files, lines, and code patterns, and carry the per-finding standards tag block (see SKILL.md "Standards References"). Generate all outputs in `drydock/security-engineer/code-audit/`.

> **OWASP 2025 relabel:** the Web steps below were authored against the 2021 list (the last finalized edition); their ids are mapped to **OWASP Top 10:2025 RC1** inline. RC1 was published 6 Nov 2025 and is **not yet ratified**, so the category set may still shift before the final release — Drydock intentionally audits against RC1 now. Key 2021→2025 changes: SSRF (old A10) is folded into **A01:2025** Broken Access Control; "Vulnerable & Outdated Components" (old A06) is expanded into **A03:2025** Software Supply Chain Failures; Security Misconfiguration moved up to **A02:2025**; and a NEW **A10:2025 Mishandling of Exceptional Conditions** (fail-open states, insecure error/exception handling) is added — see Step 10b. The per-vulnerability test guidance is unchanged; only category ids are remapped.

## Context Bridge

Read Phase 1 outputs from `drydock/security-engineer/threat-model/` before beginning. The STRIDE analysis and attack surface map tell you WHERE to focus. Start with endpoints and code paths that scored Critical or High in the threat matrix.

## Inputs

- Phase 1 threat model -- `drydock/security-engineer/threat-model/`
- Implementation code -- `services/`, `frontend/` (controllers, middleware, data access layers, utilities)
- API specs -- `api/` (OpenAPI, gRPC proto) for expected behavior comparison
- Test suites -- `tests/` for coverage gap analysis
- Dependency manifests -- `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, `pom.xml`

## Workflow

### Step 1: A01:2025 -- Broken Access Control (SSRF now folded in here — also run Step 10)

- Review every route/endpoint for authorization checks
- Search for IDOR vulnerabilities (direct object references without ownership validation)
- Check for missing function-level access control (admin endpoints accessible to regular users)
- Verify CORS configuration is restrictive (reject `Access-Control-Allow-Origin: *`)
- Check for path traversal in file operations (`../` sequences in user-supplied paths)
- Review WebSocket and GraphQL authorization

### Step 2: A04:2025 -- Cryptographic Failures

- Identify sensitive data transmitted without TLS enforcement
- Check password hashing (require bcrypt/scrypt/argon2 -- reject MD5/SHA1/SHA256 without KDF)
- Review encryption key management -- hardcoded keys, weak algorithms, missing rotation
- Check for sensitive data in URLs, logs, or error messages
- Verify cryptographically secure random number generation (not `Math.random()` or `random.random()` for tokens)

### Step 3: A05:2025 -- Injection (XSS included)

Audit EVERY database call, system call, and template render:
- **SQL injection** -- parameterized queries vs string concatenation
- **NoSQL injection** -- MongoDB query operator injection via user input
- **Command injection** -- `exec`, `system`, `spawn`, `os.popen` with user-controlled arguments
- **LDAP injection** -- if directory services are used
- **Template injection** -- server-side template engines processing user input
- **ORM injection** -- unsafe ORM methods that bypass parameterization
- **Header injection** -- CRLF in HTTP headers constructed from user input

### Step 4: A06:2025 -- Insecure Design

- Review business logic for race conditions (TOCTOU in payments, inventory, counters)
- Check for missing rate limiting on sensitive operations (login, password reset, OTP verification)
- Verify multi-step workflows cannot be bypassed (skipping payment, reordering steps)
- Review error handling for information leakage (stack traces, internal paths, version info)
- Check for insecure defaults in configuration

### Step 5: A02:2025 -- Security Misconfiguration

- Review framework security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options)
- Check for debug mode enabled in production configs
- Verify default credentials are not present
- Review CORS policy strictness
- Check for unnecessary HTTP methods (TRACE, permissive OPTIONS)
- Review error pages for information disclosure

### Step 6: A03:2025 -- Software Supply Chain Failures (expands 2021's "Vulnerable and Outdated Components")

- Cross-reference with Phase 5 (Supply Chain) for detailed dependency analysis
- Flag components with known CVEs currently in use
- Check for unmaintained or deprecated packages in direct dependencies

### Step 7: A07:2025 -- Authentication Failures

- Cross-reference with Phase 3 (Auth Review) for detailed analysis
- Check for credential stuffing protection (rate limiting, CAPTCHA)
- Verify MFA implementation if present
- Review session fixation and session ID entropy

### Step 8: A08:2025 -- Software or Data Integrity Failures

- Check CI/CD pipeline for unsigned artifacts
- Review deserialization of untrusted data (Java `ObjectInputStream`, Python `pickle`, PHP `unserialize`, Node.js `node-serialize`)
- Verify integrity of third-party code (SRI hashes for CDN-hosted scripts)
- Check for auto-update mechanisms without signature verification

### Step 9: A09:2025 -- Security Logging & Alerting Failures

- Verify authentication events are logged (login, logout, failed attempts)
- Check that authorization failures are logged with context (user_id, resource, action)
- Review log format for required security fields (user_id, ip, action, timestamp, result)
- Verify sensitive data is NOT logged (passwords, tokens, PII, credit card numbers)
- Check for tamper-proof log storage
- Review alerting on security-relevant events

### Step 10: A01:2025 -- Server-Side Request Forgery (SSRF) — folded into Broken Access Control in 2025

- Identify all code paths that make HTTP requests based on user input
- Check for URL validation and allowlisting
- Review cloud metadata endpoint access restrictions (169.254.169.254)
- Check for DNS rebinding protections
- Verify internal service URLs cannot be reached via user-controlled parameters

### Step 10b: A10:2025 -- Mishandling of Exceptional Conditions (NEW in 2025)

Audit how the system behaves when things go wrong — weaknesses previously filed under "poor code quality" now have a dedicated 2025 category:
- **Fail-open security controls** — does an auth/authz check that throws an exception default to ALLOW instead of DENY? Every guard must fail closed.
- **Improper error/exception handling** — unhandled exceptions, empty catch blocks that swallow security-relevant failures, `try/except: pass`.
- **Logic errors under abnormal conditions** — null/empty/oversized/negative/concurrent inputs that bypass validation or leave inconsistent state.
- **Information leakage via errors** — stack traces, internal paths, SQL errors, framework versions returned to the client (cross-check Steps 2 and 5).
- **DoS via unhandled conditions** — exceptions on malformed input that crash a worker or exhaust resources.
- Verify exceptional paths re-enforce the same security controls as the happy path.

### Step 11: Map Injection Points

Enumerate every input entry point in the system:
- HTTP request parameters (query, body, headers, cookies)
- File upload handlers
- WebSocket message handlers
- Message queue consumers
- GraphQL resolvers accepting user arguments
- CLI/admin command arguments
- Environment variables consumed from external sources

For each entry point, document: current sanitization applied, missing sanitization needed, expected vs accepted data types, maximum length enforcement.

### Step 12: Generate Per-Service Findings

For each service, compile findings using this structure:

```markdown
# Security Findings: <Service Name>

## Summary
- Critical: N | High: N | Medium: N | Low: N | Info: N

## Findings

### [SEVERITY] Finding Title
- **Category:** OWASP `<A0x:2025 | APIx:2023 | LLMx:2025>`
- **Location:** `file:line`
- **Confidence:** [verified] (reproduced) | [inferred] (reasoned from verified facts) | [unverified] (lead only — never rated Critical/High)
- **Description:** What the vulnerability is
- **Proof of Concept:** Concrete input → vulnerable sink → observed effect
- **Remediation:** Specific code fix or pattern to apply
- **Standards:** CVSS `<4.0 vector> → <score>` · CWE-<n> · WSTG-v42-<CAT>-<nn> · ASVS v5.0.0-<chapter>.<section>.<req> (L<1|2|3>)
- **References:** real retrieved advisory/doc links only — never invent a CVE id (see grounding-protocol)
```

Every finding MUST reference a specific file and line number. Generic findings ("check for SQL injection") are not acceptable.

### Step 13: OWASP API Security Top 10 (2023)

For any service exposing an HTTP / GraphQL / gRPC API, evaluate all 10 — each finding needs a `file:line` evidence pointer:
- `API1:2023` Broken Object Level Authorization (BOLA) — object id in the request not validated against caller ownership (IDOR). Check every resource endpoint.
- `API2:2023` Broken Authentication — weak tokens, credential stuffing, JWT flaws.
- `API3:2023` Broken Object Property Level Authorization (BOPLA) — mass assignment + excessive data exposure at the property level.
- `API4:2023` Unrestricted Resource Consumption — missing rate/size/cost limits (DoS, bill spikes).
- `API5:2023` Broken Function Level Authorization (BFLA) — privileged functions callable by regular users.
- `API6:2023` Unrestricted Access to Sensitive Business Flows — no anti-automation on signup/purchase/comment flows.
- `API7:2023` Server-Side Request Forgery — user-supplied URL fetched without validation.
- `API8:2023` Security Misconfiguration — insecure defaults, missing headers, permissive CORS/TLS.
- `API9:2023` Improper Inventory Management — undocumented/old/shadow API versions and endpoints.
- `API10:2023` Unsafe Consumption of APIs — over-trusting third-party/integrated API responses.

### Step 14: OWASP Top 10 for LLM Applications (2025) — CONDITIONAL

Run ONLY if LLM/ML usage is detected (scan for `openai`, `anthropic`, `langchain`, `transformers`, `torch`, `tensorflow` imports — the same signal the orchestrator uses to auto-enable the data-scientist; see drydock/SKILL.md "Conditional Tasks"). Each finding needs a `file:line` evidence pointer:
- `LLM01:2025` Prompt Injection — direct jailbreaks and indirect injection via retrieved/processed content.
- `LLM02:2025` Sensitive Information Disclosure — model leaks PII/secrets/training data; check output filtering.
- `LLM03:2025` Supply Chain — model/dataset/plugin provenance and integrity.
- `LLM04:2025` Data and Model Poisoning — manipulated training/fine-tune/embedding data.
- `LLM05:2025` Improper Output Handling — LLM output reaching a sink unsanitized (downstream XSS/SSRF/SQLi/RCE).
- `LLM06:2025` Excessive Agency — tool/permission/autonomy scope; high-impact actions without a human in the loop.
- `LLM07:2025` System Prompt Leakage — secrets/instructions embedded in the system prompt; confirm none live there.
- `LLM08:2025` Vector and Embedding Weaknesses — RAG/vector-DB access controls, embedding poisoning, cross-tenant leakage.
- `LLM09:2025` Misinformation — unvalidated/over-relied model output presented as fact.
- `LLM10:2025` Unbounded Consumption — token/cost/compute exhaustion, model extraction.

If no LLM/ML usage is detected, record "N/A — no LLM/ML usage found" and skip.

## Output Deliverables

Write all outputs to `drydock/security-engineer/code-audit/`:

| File | Contents |
|------|----------|
| `owasp-top10-report.md` | Full OWASP Top 10:2025 RC1 analysis with findings per category. Label the report "OWASP Top 10:2025 RC1" and note RC1 (6 Nov 2025) is not yet ratified (2021 is the last finalized list) |
| `api-top10-report.md` | OWASP API Security Top 10 (2023) findings, per API service |
| `llm-top10-report.md` | OWASP LLM Top 10 (2025) findings — only if LLM/ML usage detected |
| `findings-by-service/<service>.md` | Per-service findings with severity summary |
| `injection-points.md` | Comprehensive map of every input entry point |

## Validation

Before proceeding to Phase 3, verify:
- [ ] All 10 OWASP Top 10:2025 RC1 Web categories evaluated (A01–A10:2025), including A10:2025 Mishandling of Exceptional Conditions (Step 10b) — report labeled "OWASP Top 10:2025 RC1" with the not-yet-ratified note (2021 is the last finalized list)
- [ ] OWASP API Security Top 10 (2023) evaluated for every API service (Step 13)
- [ ] OWASP LLM Top 10 (2025) evaluated IF LLM/ML usage detected, else marked N/A (Step 14)
- [ ] Every finding has a specific file:line location and the standards tag block (CVSS/CWE/OWASP/WSTG/ASVS)
- [ ] No fabricated CVE/CVSS — each id retrieved this session or computed from the CVSS vector (grounding-protocol)
- [ ] Every finding has a concrete remediation (not just "fix this")
- [ ] Per-service findings include severity summary counts
- [ ] Injection points map covers all input vectors (not just HTTP parameters)

## Quality Bar

This is a code audit, not a checklist exercise. Every finding must include the vulnerable code snippet, an explanation of how it can be exploited, and the specific fix. "Possible SQL injection in user service" is not a finding. "String concatenation in user-service/src/db/queries.js:87 allows SQL injection via the `sort` parameter -- replace with parameterized query using `$1` placeholder" is a finding.
