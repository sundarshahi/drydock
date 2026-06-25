# Phase 5 — E2E Tests

**Goal:** Test critical user flows end-to-end through the full stack.

**Inputs to read:**
- BRD / PRD user stories and acceptance criteria (especially the critical path)
- `frontend/` pages and navigation flow (if frontend exists; otherwise API-only E2E)
- `services/` API endpoints
- The test plan from Phase 1 (critical user flows identified)

**Rules:**
1. Identify the 5-10 most critical user flows (signup, login, core CRUD, payment, etc.).
2. For API E2E: chain multiple API calls that represent a complete user journey. Use real auth tokens. Validate side effects (DB state, emails sent, events published).
3. For UI E2E (skip if frontend not found): use Page Object Model pattern. Each page gets a class in `tests/e2e/ui/pages/`.
4. UI tests must use resilient selectors: `data-testid` attributes, ARIA roles — never CSS classes or DOM structure.
5. Write a smoke test suite (`smoke.e2e.ts`) that covers the absolute minimum "is the app alive" checks. This runs on every deploy.
6. E2E tests must be idempotent — running them twice produces the same result.
7. Include setup/teardown that creates test users, seeds required data, and cleans up after.
8. Add explicit waits for async operations — never use arbitrary `sleep()` calls.
9. For visual regression (skip if frontend not found): capture screenshots of key pages and compare against baselines.
10. Configure test timeouts generously (30s+ per test) — E2E is slow by nature.
11. **Cross-boundary journey testing** (boundary-safety protocol pattern 5): For every multi-system flow (auth, payment, email, webhook), write at least one E2E test that traces the COMPLETE journey from user action to final state. Auth test must verify: unauthenticated user visits protected page → redirected to login → authenticates → redirected back to original page → sees authenticated content. Payment test must verify: user clicks pay → payment provider processes → callback fires → order status updates → user sees confirmation. Do NOT just test individual hops — test the full chain.
12. **Framework navigation correctness**: Verify that no `<Link>` or client-side `navigate()` targets API routes, external URLs, or auth endpoints. These must use raw `<a href>` or `window.location` for full HTTP requests.

**Output:** Write E2E tests and page objects to `tests/e2e/`. Write Playwright or Cypress config.
