# Phase 6: Testing & Accessibility

## Objective

Establish comprehensive testing coverage and accessibility compliance on the **final, polished** frontend. This runs AFTER Phase 5 (Design & Polish), so visual regression baselines capture the actual production design, not placeholder defaults.

## Context Bridge

Read Phase 3 component inventory from `drydock/frontend-engineer/docs/component-inventory.md`. Read Phase 4 pages from `frontend/app/pages/` for route coverage. Read Phase 5 design decisions from `drydock/frontend-engineer/docs/design-decisions.md` for visual regression context.

## Workflow

### Step 1: Component Testing

Set up component tests with the project's framework (Vitest + @testing-library/react recommended for React/Next.js). Test every component across all states:

- **UI primitives:** All variants (primary, secondary, destructive), interactive states (hover, focus, disabled, loading), edge cases (long text, empty)
- **Feature components:** Mocked API data via MSW — loading skeleton, success, error with retry, empty state with CTA
- **Custom hooks:** @testing-library/react-hooks with renderHook
- **A11y per component:** `jest-axe` assertion in every component test

Coverage target: 80% branch coverage on component files, 100% for hooks and utilities.

Produce tests in `frontend/tests/components/` mirroring the component directory structure.

### Step 2: End-to-End Testing (Playwright)

Configure Playwright with projects for Desktop Chrome, Firefox, Safari (WebKit), Mobile Chrome (Pixel 5), and Mobile Safari (iPhone 13). Enable trace-on-first-retry and screenshot-only-on-failure.

Write E2E tests for every critical user flow from Phase 1: authentication (signup, login, logout, session expiry), onboarding, core CRUD operations, navigation and deep linking, admin operations. Use role-based test fixtures for multi-role flows.

Produce E2E tests in `frontend/tests/e2e/` and `frontend/playwright.config.ts`.

### Step 3: Accessibility Audit

**Automated (axe-core):**
- `jest-axe` in every component test (Step 1)
- `@axe-core/playwright` full-page audits on every route in E2E
- Target: **WCAG 2.1 AA** with zero critical violations
- `eslint-plugin-jsx-a11y` at error level in ESLint — CI fails on violation

**Manual checklist:**
- Keyboard: every interactive element reachable via Tab, activatable via Enter/Space
- Focus: trapped in modals, returned to trigger on close
- Screen reader: all images have alt text, all inputs have labels, live regions for dynamic updates
- Color contrast: 4.5:1 normal text, 3:1 large text
- Motion: `prefers-reduced-motion` respected

Produce `drydock/frontend-engineer/docs/a11y-audit.md`.

### Step 4: Performance Budget (Core Web Vitals) — thresholds READ FROM the shared budget artifact

**Do NOT hardcode 2.5s / 200KB.** The single source of truth is `docs/architecture/performance-budget.yaml` (owned/emitted by solution-architect):

```yaml
web_vitals: { lcp_ms, inp_ms, cls }
bundle:     { <entry>: max_kb }
api:        <route>: { p95_ms, p99_ms, throughput_rps, error_rate_pct }
```

EMIT the two CI gate configs whose thresholds are **derived from that file**, not typed in by hand:

- **`frontend/lighthouserc.json`** — Lighthouse CI assertions for LCP / INP / CLS read from `web_vitals` (`lcp_ms`, `inp_ms`, `cls`), plus minScore assertions (performance, accessibility 0.95, best-practices). If the file is absent, fall back to documented defaults (LCP 2500ms, INP 200ms, CLS 0.1) and record the fallback — but prefer the artifact.
- **`frontend/.size-limit.json`** (size-limit) and/or a `bundlesize` config — per-entry `max_kb` read from the `bundle` section, one limit per entrypoint. Wire `@next/bundle-analyzer` for diagnosis.

Because these are generated from the YAML, a budget change in `docs/architecture/performance-budget.yaml` flows straight into the CI gates — frontend, QA, SRE, and DevOps all read the same numbers. **These are enforced as CI gates that block merge on regression; DevOps wires the job** (Lighthouse CI + `size-limit --json` steps). Frontend owns emitting the configs; do not also hardcode the thresholds in test files.

The web-vitals captured at runtime (Phase 4.6) report to the same `web_vitals` keys, so the field RUM data and the CI budget speak the same units.

Produce `frontend/lighthouserc.json`, `frontend/.size-limit.json`, and `drydock/frontend-engineer/docs/performance-budget.md` (documenting which thresholds came from the artifact).

### Step 5: Visual Regression Testing

Capture baseline screenshots per component and page across viewports using Playwright `toHaveScreenshot()` or Chromatic. Pixel diff tolerance: 0.1%. CI blocks merge on unexpected visual diff.

Produce visual regression configs in `frontend/tests/visual/`.

### Step 6: Cross-Browser Testing Strategy

| Browser | Versions | Method | Priority |
|---------|----------|--------|----------|
| Chrome | Latest 2 | Playwright CI | P0 |
| Firefox | Latest 2 | Playwright CI | P0 |
| Safari | Latest 2 | Playwright WebKit | P0 |
| Edge | Latest 2 | Covered by Chromium | P1 |
| Mobile Chrome | Latest | Playwright emulation | P0 |
| Mobile Safari | Latest | Playwright emulation | P0 |

Produce `drydock/frontend-engineer/docs/browser-support.md`.

### Step 7: Observability & Security Verification

Verify the contracts established in Phase 2 (security) and Phase 4.6 (observability) actually hold on the final build:

- **Observability names match the contract.** Web-vitals (LCP/INP/CLS) report to the OTLP/analytics endpoint; the API client emits `http_requests_total` / `http_request_duration_seconds` with labels `method`, `route` (templated), `status_class`; `traceparent` is injected on every request; the global error boundary + `window.onerror`/`unhandledrejection` reporter emit the structured JSON log fields (`trace_id`/`span_id` from the live span). Grep the code for any emitted name absent from `observability-contract.md` — drift is a bug.
- **Security headers present.** Assert CSP is served with no `unsafe-inline`/`unsafe-eval`, HSTS/`nosniff`/frame-ancestors set, and no raw `dangerouslySetInnerHTML` (all HTML passes `lib/sanitize.ts`). Also assert: every external/CDN `<script>` carries an SRI `integrity` attribute (or is self-hosted); `Cross-Origin-Opener-Policy` and `Cross-Origin-Resource-Policy: same-origin` are present; the Trusted Types CSP directive (`require-trusted-types-for 'script'`) is present where the framework supports it; the session cookie carries a `__Host-`/`__Secure-` prefix; and an authenticated/sensitive route responds with `Cache-Control: no-store`. The E2E suite can assert the response headers and cookie attributes on a sample route.
- **No secrets in the client bundle.** Confirm only `NEXT_PUBLIC_*` config is exposed; no tokens/keys in the built JS.

## Output Files

- `frontend/tests/components/` (component tests with a11y)
- `frontend/tests/e2e/` (Playwright E2E tests)
- `frontend/tests/visual/` (visual regression)
- `frontend/playwright.config.ts`
- `frontend/lighthouserc.json` (LCP/INP/CLS thresholds read from `docs/architecture/performance-budget.yaml`)
- `frontend/.size-limit.json` (per-entry `max_kb` read from the budget `bundle` section)
- `drydock/frontend-engineer/docs/a11y-audit.md`
- `drydock/frontend-engineer/docs/performance-budget.md`
- `drydock/frontend-engineer/docs/browser-support.md`

## Validation Loop

Before concluding the frontend skill:
- [ ] Every UI primitive has component tests covering all variants, states, and a11y
- [ ] Every critical user flow has an E2E test
- [ ] WCAG 2.1 AA with zero critical violations
- [ ] Performance budget thresholds READ FROM `docs/architecture/performance-budget.yaml` (not hardcoded) and enforced as CI gates (Lighthouse CI + size-limit); DevOps wires the job
- [ ] Visual regression baselines captured
- [ ] Cross-browser matrix tested (Chrome, Firefox, Safari, mobile)
- [ ] Observability verified: web-vitals → OTLP/analytics, `traceparent` injected, global error boundary/reporter, contract names only (Step 7)
- [ ] `security-defaults checklist passes`: CSP + security headers, no unsanitized `dangerouslySetInnerHTML`, no secrets in the bundle, secure cookies
- [ ] Browser-hardening asserted on the final build: SRI `integrity` on external scripts (or self-hosted), COOP/CORP `same-origin` present, Trusted Types CSP directive present (where applicable), session cookie carries a `__Host-`/`__Secure-` prefix, and an authenticated/sensitive route returns `Cache-Control: no-store`

**Present testing summary with coverage report, a11y audit results, and performance scores to user.**

## Quality Bar

Every component must have at least one accessibility test. "Tests pass" is not acceptable -- "94 component tests (87% branch coverage), 12 E2E flows, zero WCAG 2.1 AA violations, LCP 1.8s (budget 2.5s from performance-budget.yaml), CLS 0.04 (budget 0.1), bundle 156 KB gzip (budget 200 KB from performance-budget.yaml), web-vitals+traceparent emitting contract names, security-defaults checklist passes" is acceptable.

- **Perf budget is a CI gate, not a doc** — `lighthouserc.json` + `.size-limit.json` thresholds derive from `docs/architecture/performance-budget.yaml`; the build fails on regression (DevOps wires the job). State the budget source, not a hardcoded number.
- **`security-defaults checklist passes`** — CSP/security headers served (incl. Trusted Types directive where supported, COOP/CORP `same-origin`, HSTS preload), SRI `integrity`+`crossorigin` on external scripts (or self-hosted), `__Host-`/`__Secure-` prefixed cookies, `Cache-Control: no-store` on sensitive routes, no unsanitized `dangerouslySetInnerHTML`, no secrets in the client bundle, secure cookies, input validated server-side (client validation is UX only).
