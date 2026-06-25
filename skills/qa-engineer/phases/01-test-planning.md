# Phase 1 — Test Planning

**Goal:** Produce a traceability matrix linking every BRD acceptance criterion to concrete test cases, categorized by test type.

**Inputs to read:**
- BRD / PRD acceptance criteria (every GIVEN/WHEN/THEN or equivalent)
- `api/` API contracts (OpenAPI specs, AsyncAPI specs)
- `schemas/` data models and `docs/architecture/` sequence diagrams
- `services/` service structure (list all services, handlers, repos)
- `frontend/` component and page structure (if frontend exists; otherwise skip frontend inputs)

**Actions:**
1. Extract every acceptance criterion and assign a unique ID (AC-001, AC-002, ...).
2. For each criterion, determine which test types are required (unit, integration, contract, e2e, performance).
3. Identify all services, modules, and components that need test coverage.
4. Identify all external dependencies that require mocking or test containers.
5. Identify critical user flows for E2E coverage.
6. Identify performance-sensitive endpoints for load testing; read `docs/architecture/performance-budget.yaml` so k6 thresholds derive from it (never hardcode 500ms).
7. Define coverage thresholds per service (lines, branches, functions) AND the patch-coverage threshold (~80%) — these become the FAILING gate in Phase 7, not a passive JSON file.
8. Identify **critical modules** (money/billing, authz predicates, validators, parsers, serializers, domain invariants) that require mutation testing + property/fuzz tests (Test Quality Gates).
9. If `config/feature-flags.yaml` exists, list every flag key for the feature-flag test matrix (on/off + provider-down safe default).

**Output:** Write `Shipyard/qa-engineer/test-plan.md` with the following sections:
- **Scope** — What is being tested, what is explicitly out of scope
- **Test Strategy** — Test pyramid approach, which test types cover which risk areas
- **Traceability Matrix** — Table mapping AC-ID to test case IDs, test type, and priority
- **Environment Requirements** — Containers, external services, env vars needed
- **Coverage Targets** — Per-service and global coverage gates
- **Risk Register** — Areas with high complexity or insufficient testability
