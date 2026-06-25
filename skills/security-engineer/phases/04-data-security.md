# Phase 4: Data Security

## Objective

Inventory every piece of sensitive data in the system and verify encryption at rest and in transit. security-engineer is the SOLE AUTHORITY on the PII inventory, data classification, and the encryption AUDIT at the application layer. It does NOT own regulatory framework scoping or requirement→control mapping — the **compliance-officer** owns GDPR/CCPA/SOC2/etc. scoping, the mandatory-control matrix, and the control-evidence map (per `Shipyard/.protocols/conflict-resolution.md` + `Shipyard/.protocols/compliance-protocol.md`). This phase produces the PII inventory plus a **non-authoritative compliance posture note** that compliance-officer CONSUMES; it does not render the compliance verdict. Generate all outputs in `Shipyard/security-engineer/data-security/`.

## Context Bridge

Read Phase 3 outputs from `Shipyard/security-engineer/auth-review/`. Token management findings feed directly into data security -- tokens are sensitive data. Also reference Phase 2 code audit findings for A04:2025 (Cryptographic Failures) as the starting point for encryption analysis.

## Inputs

- Phase 2 code audit -- `Shipyard/security-engineer/code-audit/` (A04:2025 cryptographic findings)
- Phase 3 auth review -- `Shipyard/security-engineer/auth-review/`
- Data schemas -- `schemas/` (ERD, migrations, data models)
- Implementation code -- data access layers, ORM models, API response serializers
- Infrastructure configs -- database encryption settings, backup configs
- Architecture docs -- data flow diagrams, storage architecture

## Workflow

### Step 1: Build PII Inventory

Catalog EVERY PII and sensitive data field across ALL storage and transit locations. PII is not limited to database columns -- check all of the following:

- **Database columns** -- every table and column containing personal data
- **Cache stores** -- Redis, Memcached, in-memory caches holding user data
- **Message queues** -- Kafka topics, RabbitMQ queues, SQS messages containing PII
- **Log files** -- application logs, access logs, error tracking (Sentry, Datadog)
- **Browser storage** -- localStorage, sessionStorage, cookies containing user data
- **File storage** -- S3 buckets, local file uploads, temp directories
- **API responses** -- fields returned to clients that contain PII
- **Third-party services** -- analytics, error tracking, email providers receiving PII

For each PII field, document:

| Column | Description |
|--------|-------------|
| Data Field | Name of the field (e.g., email, phone, SSN) |
| Service | Which service owns this data |
| Storage | Where it is stored (DB, cache, logs, etc.) |
| Classification | Public / Internal / Confidential / Restricted |
| Encrypted at Rest | Yes/No, algorithm used |
| Encrypted in Transit | Yes/No, TLS version |
| Logged | Is this field appearing in logs? (should be No for PII) |
| In API Responses | Is it returned unnecessarily? |
| Retention | How long is it kept? |
| Legal Basis | Why the system collects it (contractual, consent, legitimate interest) |

### Step 2: Audit Encryption Implementation

Review all encryption in the system:

**At rest:**
- Database encryption (TDE, column-level, application-level)
- File storage encryption (S3 SSE, disk encryption)
- Backup encryption (algorithm, key management)
- Cache encryption (Redis TLS, encrypted at rest)

**In transit:**
- TLS version and cipher suites (reject TLS 1.0/1.1, weak ciphers)
- Internal service communication encryption (mTLS, service mesh TLS)
- Certificate management and expiration monitoring

**Application-level:**
- Field-level encryption for highly sensitive data (SSN, credit card)
- Key derivation functions for passwords
- Encryption library versions (reject outdated libraries)

**Flag violations:**
- Deprecated algorithms: DES, 3DES, RC4, MD5 for integrity, SHA1 for signing
- ECB mode usage (use CBC/GCM instead)
- Hardcoded encryption keys or initialization vectors
- Missing HMAC on encrypted data (require encrypt-then-MAC)
- Custom cryptography implementations (must use vetted libraries)
- Keys stored alongside encrypted data

### Step 3: Validate Key Management

Document the complete key management lifecycle:

- Where are encryption keys stored? (HSM, KMS, secrets manager, environment variable, config file, hardcoded)
- Who has access to keys? (service accounts, developers, CI/CD)
- How are keys rotated? (automated schedule, manual, never)
- Is there a key hierarchy? (master key -> data encryption keys)
- What happens if a key is compromised? (re-encryption procedure)
- Are old keys retained for decrypting historical data?

### Step 4: Audit Data Retention

Document and validate data lifecycle:

- **Active data** -- retention period in primary storage
- **Archived data** -- archive location, access controls, encryption
- **Deleted data** -- soft delete vs hard delete, purge timeline
- **Logs** -- retention periods by type (access, application, security, audit)
- **Backups** -- retention, encryption, geographic location
- **Third-party data** -- what is shared with third parties, their retention policies

Verify enforcement:
- Are automated purge jobs implemented?
- Are purge jobs tested and monitored?
- Do purge jobs handle cascading deletes correctly?
- Are audit logs exempted from purge (required for compliance)?

### Step 5: Compliance Posture Note (NON-authoritative — hand-off to compliance-officer)

This step does NOT render a compliance verdict and does NOT scope frameworks or map requirements to controls — **compliance-officer owns that** (framework scoping, the mandatory-control matrix, the control-evidence map, and the blocking compliance gate). What this phase produces is a *posture note*: the data-handling facts the compliance-officer needs, plus an OBSERVED implementation status for each privacy-relevant capability the PII inventory and encryption audit already surfaced. Mark each capability Present / Partial / Absent / Not Applicable based on what the code actually does — leave the requirement→article mapping and the pass/fail call to compliance-officer.

**Do NOT state regulatory article numbers, §-citations, or statutory clocks from memory.** Per `Shipyard/.protocols/freshness-protocol.md` + `grounding-protocol.md`, any specific article/clock MUST be verified LIVE against the official source this session (cite the eur-lex / official-register URL + the quoted span + the access date, tag `[verified]`); otherwise leave the article cell blank and tag the row `[unverified]`. The deterministic requirement→control map lives in `compliance-protocol.md`, not here.

**Privacy-capability posture (observed from PII inventory + encryption audit):**

| Privacy capability | Article (verify live per freshness-protocol; cite eur-lex URL + quote + date, tag `[verified]`) | Observed status | Implementation (`path:line`) | Gap / note for compliance-officer |
|--------------------|--------------------------------------------------------------------------------------------------|-----------------|------------------------------|-----------------------------------|
| Lawful basis recorded for processing | _(verify live)_ | | | |
| Consent capture + management | _(verify live)_ | | | |
| Right to access / data export | _(verify live)_ | | | |
| Right to rectification | _(verify live)_ | | | |
| Right to erasure / deletion pipeline | _(verify live)_ | | | |
| Data portability (machine-readable export) | _(verify live)_ | | | |
| Breach-notification readiness (logging/alerting wired) | _(verify live)_ | | | |
| Privacy-by-design / data minimization in schema | _(verify live)_ | | | |
| Cross-border transfer / residency boundary | _(verify live)_ | | | |

**CCPA/CPRA-relevant facts to hand off (observed, not adjudicated):**
- Whether a "Do Not Sell / Share My Personal Information" opt-out mechanism exists in the code.
- Whether financial-incentive / data-collection disclosures are surfaced to users.
- Whether the system can produce a lookback of collected data categories (and over what window the code supports).
- Whether household-level / per-subject access requests are supportable from the data model.

Write these to `compliance-posture-note.md` and flag it explicitly as **non-authoritative input for compliance-officer** — the authoritative scoping, mapping, and verdict are produced by compliance-officer.

### Step 6: Verify Secrets Management

Audit how the codebase handles secrets:

- Search for hardcoded secrets (API keys, passwords, tokens in source code)
- Verify `.env` files are in `.gitignore`
- Check git history for accidentally committed secrets
- Review secrets manager integration (Vault, AWS Secrets Manager, etc.)
- Verify secret rotation automation
- Check CI/CD pipeline for exposed secrets in logs or artifacts

### Step 7: Cross-Check Logger Redaction Deny-List Against Data Classification

The `software-engineer` wires a PII redaction deny-list **into the logger itself** (see `skills/software-engineer/phases/03-cross-cutting.md` "PII-safe log redaction" and the PII-safe rules in `Shipyard/.protocols/observability-contract.md`). That deny-list is only correct if it covers **every field the data classification marks as PII/Confidential/Restricted**. Verify the two agree — a classified field absent from the deny-list is a leak waiting to happen.

For each field in the PII inventory (Step 1) with `Classification` ∈ {Confidential, Restricted} or `Logged = should be No`:
- Confirm the field name (and its common aliases/serialized keys) appears in the logger deny-list (pino `redact` paths / structlog processor / logback masking — whichever the codebase uses).
- Confirm the baseline secret/PII keys are present: `authorization, cookie, set-cookie, password, token, access_token, refresh_token, secret, api_key, ssn, credit_card, card_number, cvv`, plus request/response BODY redacted by default.
- Any classified field NOT covered by the deny-list is an **A09:2025 (Security Logging & Alerting Failures)** + **A04:2025** finding — file it with the missing field name and the exact deny-list path that must be added. Owner for the fix: software-engineer (logger config); this phase produces the gap list, not the logger change.

Record the result as a coverage table (`Classified field` · `In deny-list?` · `Logger path` · `Finding ID if missing`) in `encryption-audit.md` (or a dedicated `log-redaction-coverage.md`). This ties the data-classification doc to observability-contract PII-safe logging so a classified field can never reach stdout unredacted.

## Output Deliverables

Write all outputs to `Shipyard/security-engineer/data-security/`:

| File | Contents |
|------|----------|
| `pii-inventory.md` | Complete catalog of every PII field across all storage locations |
| `encryption-audit.md` | Encryption review for at-rest, in-transit, and application-level |
| `data-retention-policy.md` | Retention analysis with enforcement verification |
| `compliance-posture-note.md` | NON-authoritative privacy-capability posture + CCPA/CPRA facts for compliance-officer to consume (no framework scoping or requirement→control mapping — that is compliance-officer's authority; any article cited must be `[verified]` live) |

## Validation

Before proceeding to Phase 5, verify:
- [ ] PII inventory covers ALL storage locations (not just database columns)
- [ ] Every encryption implementation has been reviewed (not just "TLS is enabled")
- [ ] Key management lifecycle is fully documented
- [ ] Compliance posture note records observed privacy-capability status as NON-authoritative input for compliance-officer; no framework scoping or requirement→control verdict is rendered here, and every cited article/clock is `[verified]` live (blank + `[unverified]` otherwise — never from memory)
- [ ] Secrets management audit found no hardcoded credentials
- [ ] Every Confidential/Restricted PII field is covered by the logger redaction deny-list (Step 7) — gaps filed as A09:2025/A04:2025 findings for software-engineer to fix in the logger config

## Quality Bar

A data security audit that only checks database columns for PII is incomplete. PII leaks into logs, caches, error tracking services, analytics pipelines, browser localStorage, and third-party integrations. The audit must trace data through EVERY layer. Similarly, "encryption is enabled" is not an assessment -- specify the algorithm, key length, mode of operation, and whether the implementation follows current best practices.
