# Phase 4 — Contract Tests

**Goal:** Verify API consumers and providers agree on request/response schemas and that implementations conform to OpenAPI specifications.

**Inputs to read:**
- `api/` OpenAPI specs and AsyncAPI specs
- `services/` API route definitions, request/response DTOs
- `frontend/` API client calls and expected response shapes (if frontend exists; otherwise skip consumer-side frontend contracts)

**Rules:**
1. For each API consumer (frontend, other services), write a Pact consumer test that defines the expected interactions.
2. For each API provider, write a Pact provider verification test that replays consumer expectations against the real provider.
3. Write schema validation tests that load the OpenAPI spec and validate every endpoint's actual response against the schema.
4. Test backward compatibility: if there are versioned APIs, verify old consumers still work with new providers.
5. For async APIs (events, messages), write contract tests for message schemas using AsyncAPI specs.
6. Configure Pact Broker connection in `pact-broker.config.ts` (even if the broker URL is a placeholder). Wire the **`pact-broker can-i-deploy` deployment gate** into the contract CI stage — see "Contract Deployment Gate" — and surface it as `contract_can_i_deploy` in the receipt.
7. Contract tests must fail if a required field is removed, a type changes, or a new required field is added without consumer agreement.
8. **Error-response contract (RFC 9457):** every 4xx/5xx interaction asserts the body is `application/problem+json` matching the reusable `Problem` schema (owned by solution-architect) — `{ type, title, status, detail, instance }` plus extensions `trace_id` and `errors[]`. Validate against the OpenAPI `Problem` `$ref`, and assert the `type`/error code comes from the error-catalog module (the single source for runtime + docs) — not an ad-hoc string. A bare `{ code, message }` envelope is a contract failure.

**Output:** Write contract tests to `tests/contract/`.
