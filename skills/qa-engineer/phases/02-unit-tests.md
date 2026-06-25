# Phase 2 — Unit Tests

**Goal:** Test each service's business logic, handlers, and repositories in isolation with full mocking of external dependencies.

**Inputs to read:**
- `services/` source code for each service
- The test plan from Phase 1

**Rules:**
1. One test file per source file. Mirror the source directory structure under `tests/unit/<service>/`.
2. Mock ALL external dependencies: databases, caches, message brokers, HTTP clients, other services.
3. Use dependency injection or module mocking — never patch globals.
4. Test the happy path, error paths, edge cases, and boundary values for every public function.
5. For handlers/controllers: test request parsing, validation error responses, correct status codes, response body shape.
6. For services/domain logic: test business rule enforcement, state transitions, calculation correctness.
7. For repositories: test query construction, parameter binding, result mapping (with mocked DB driver).
8. For validators: test every validation rule, including null, empty, boundary, and malformed inputs.
9. Every test must have a descriptive name that reads as a specification: `it("should return 404 when order does not exist for the given user")`.
10. Use factories from `tests/fixtures/factories/` for test data — never inline large object literals.
11. Assert on specific values, not just truthiness. Prefer `toEqual` over `toBeTruthy`.
12. Test error types and messages, not just that an error was thrown.

**Output:** Write test files to `tests/unit/<service>/`.

Also write factories to `tests/fixtures/factories/` as you discover entity shapes.
