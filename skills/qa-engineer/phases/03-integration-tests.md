# Phase 3 — Integration Tests

**Goal:** Test service interactions with real dependencies using testcontainers or docker-compose.

**Inputs to read:**
- `services/` database migrations, schemas, connection configs
- `docs/architecture/` infrastructure requirements (which DBs, caches, brokers)
- The test plan from Phase 1

**Rules:**
1. Write `tests/integration/docker-compose.test.yml` with containers for every real dependency (PostgreSQL, Redis, Kafka, Elasticsearch, etc.). Pin exact image versions.
2. Write `tests/integration/setup.ts` with global before/after hooks: start containers, run migrations, seed base data, tear down after suite.
3. Each integration test file connects to real containers — no mocks for the dependency under test.
4. Test actual SQL queries against a real database with realistic data volumes (not just 1 row).
5. Test cache read/write/eviction with a real Redis instance.
6. Test message publishing and consumption with a real broker.
7. Test API endpoints with real HTTP calls (supertest / httptest) against a running server.
8. Each test must clean up its own data. Use transactions with rollback, or truncate tables in afterEach.
9. Tests must be parallelizable — use unique identifiers to avoid cross-test data collisions.
10. Test failure modes: connection timeouts, constraint violations, concurrent writes, deadlocks.

**Output:** Write test files to `tests/integration/<service>/`.

Write `docker-compose.test.yml` and `setup.ts` to `tests/integration/`.
