---
sidebar_position: 3
title: "Engineering"
description: "Software Engineer and Frontend Engineer: the agents that write the system."
---

# Engineering

The engineering agents turn the approved architecture into working code. They run in the **BUILD** phase, after Gate 2 (architecture) has been approved, and they implement the contracts the [Solution Architect](/docs/concepts/how-it-works) produced — they do not redesign them.

Two agents share this phase and run in parallel:

| Agent | Builds | Reads | Writes |
|-------|--------|-------|--------|
| **Software Engineer** | Backend services, APIs, business logic | `api/`, `schemas/`, `docs/architecture/` | `services/`, `libs/`, `scripts/` |
| **Frontend Engineer** | Production web frontend | `api/openapi/*.yaml`, BRD user stories | `frontend/` |

:::info Phase position
Both agents run as isolated subagents in the BUILD phase. The Software Engineer is Phase 3a; the Frontend Engineer is Phase 3b. They consume the same OpenAPI specs as the single source of truth and write to independent folder trees (`services/` and `frontend/`) with no file conflicts.
:::

## Software Engineer

The Software Engineer reads the Solution Architect's output (`api/`, `schemas/`, `docs/architecture/`) and generates fully working, production-ready service code: business logic, API handlers, data access layers, middleware, and integration patterns. It implements the API contracts faithfully and does **not** change them.

### What it needs to start

| Category | Inputs | If missing |
|----------|--------|-----------|
| Critical | OpenAPI/gRPC contracts, `schemas/erd.md`, `tech-stack.md` | Stops — can't implement without contracts, data models, and stack |
| Degraded | ADRs, SQL migrations | Warns — proceeds with sensible defaults, flags assumptions |
| Optional | AsyncAPI specs, existing `services/` scaffold | Continues — generates from scratch if absent |

### Internal parallelism

The Software Engineer runs five phases. Phase 2 (Service Implementation) splits into two steps so that parallel work stays consistent:

1. **Phase 2a — Shared Foundations** runs sequentially and establishes `libs/shared/`: common types/DTOs from OpenAPI schemas, the error response format and error classes, logging middleware with correlation IDs, an auth middleware template, a base repository pattern, health checks, a config loader, and shared test utilities.
2. **Phase 2b — Service Implementation** parallelizes per service with **bounded foreground fan-out**: up to **3 concurrent** sub-tasks, batched in groups of three when there are more services. Every service agent reads `libs/shared/` first and reuses those patterns rather than inventing its own.

:::note Why foundations first
Without shared patterns, parallel service agents each invent their own error handling, logging, auth middleware, and types — leaving Phase 3 to reconcile N inconsistent implementations. Building foundations first means every service composes from the same building blocks. If only one service exists, parallel dispatch is skipped and Phase 2 runs as a single pass.
:::

Phases 3 (cross-cutting verification), 4 (integration), and 5 (local dev) run sequentially after fan-out completes — Phase 3 verifies all services use the shared patterns consistently before they're wired together.

### Key practices

- **TDD per endpoint** — Phase 2 follows clean architecture layers (handlers → services → repositories) with a test written for each endpoint. Handlers validate and delegate (under ~30 lines); all logic lives in the service layer; services call repositories and never import DB clients directly.
- **Security by default** — auth uses the JWKS/OAuth2 middleware pattern with battle-tested libraries (never hand-parsed JWTs). Every repository query includes `tenant_id`, and integration tests verify cross-tenant data is invisible. Every write accepts an `Idempotency-Key`. Sensitive fields are wired into a logger redaction deny-list, and logs go to stdout/stderr only.
- **12-Factor discipline** — config comes from validated env vars; processes are stateless (no local-disk or in-memory session state); errors use RFC 9457 `application/problem+json` referencing the shared `Problem` schema.
- **Observability as a first import** — OpenTelemetry init from `libs/shared/observability/` is the entrypoint's first import, with RED/USE instruments and `/metrics` using the exact names in the observability contract.

### Outputs

| Output | Location |
|--------|----------|
| Service implementations (handlers, services, repositories, models, middleware) | `services/<name>/src/` |
| Service tests (unit, integration, fixtures) | `services/<name>/tests/` |
| Shared libraries | `libs/shared/` |
| Dev scripts (seed, setup, migrate) | `scripts/` |
| Local dev stack | `docker-compose.dev.yml` |
| Environment template | `.env.example` |
| Root dev commands | `Makefile` |
| Workspace artifacts (plan, progress, logs) | `drydock/software-engineer/` |

:::tip Cloud targets
The skill supports AWS (SDK v3, LocalStack), GCP (emulators), Azure (Azurite), and multi-cloud abstractions via provider interfaces selected by `CLOUD_PROVIDER` config.
:::

## Frontend Engineer

The Frontend Engineer builds a production-ready, accessible, performant, internationalized, and SEO-ready web application from BRD user stories and API contracts. It chooses the framework that best fits the product rather than defaulting — Astro for content/marketing, Next.js App Router for full-stack SaaS, React + Vite for internal-tool SPAs, or Remix for form-heavy apps (or it matches the architect's `tech-stack.md` / the existing brownfield stack).

### The design-system spec it consumes

The Frontend Engineer does not invent a final visual design up front. Phase 2 emits a **functional design foundation** — minimal tokens, system fonts, a neutral palette — plus the security foundation (CSP/headers + DOMPurify), the i18n foundation (provider, externalized strings, RTL), and the font/performance foundation. This is deliberately *not* the final design.

It also reads two specs as inputs at startup:

- **`docs/architecture/performance-budget.yaml`** — the `web_vitals` and `bundle` budgets feed `lighthouserc.json` and `.size-limit.json` as CI gates. Thresholds are never hardcoded.
- **`config/feature-flags.yaml`** — the shared OpenFeature flag registry, consumed via a `useFlag` hook.

:::tip Make it work, then make it beautiful
Phase 2 gives just enough to build. Phase 5 (Design & Polish) delivers the professionally designed product through domain research, color theory, typography, and micro-interactions. Testing runs last, against the final polished version.
:::

### Internal parallelism

The Frontend Engineer runs six phases. Parallelism is gated on foundations being built first:

1. **Phase 3a — UI Primitives** runs sequentially, building all foundational atoms (Button, Input, Select, Modal, Card, etc.) into `frontend/app/components/ui/`.
2. **Phase 3b — Layout + Feature Components** parallelizes with **bounded foreground fan-out** (up to **3 concurrent** sub-tasks). Layout and feature agents import primitives from `components/ui/` instead of creating their own.
3. **Phase 4 — Pages** parallelizes by route group with the same fan-out (≤3 concurrent, batched), one agent per group (auth, dashboard, settings).

:::note Why primitives first
Layout and feature components *use* primitives. If all groups build at once, the real primitives don't exist yet and agents create duplicate, inconsistent buttons and inputs. Building primitives first means every downstream component composes from the same atoms.
:::

### Functional completeness — the "does it work?" rule

After Phase 4 and before Phase 5, the Frontend Engineer runs a mandatory **Functional Verification Pass**:

- **Dead element rule** — any button, link, form, or interactive element that renders but does nothing when activated is a Critical defect, not a TODO. Every interactive element is traced to a working handler.
- **Navigation graph verification** — logo, nav items, breadcrumbs, cross-page-group links, auth redirects, and 404 handling are all confirmed to resolve.
- **Executed interaction trace** — the top-5 BRD flows are written as `frontend/tests/e2e/smoke.spec.ts` and **run** (Playwright against the built app), asserting the correct final state. A failing flow blocks Phase 5. If the app can't be booted in the environment, the smoke spec is still produced, handed to the QA Engineer as a required gate, and recorded as *deferred* (not skipped).
- **Cross-agent reconciliation** — a sequential step collects every route and link target from all parallel page agents and fixes broken cross-references.

:::warning Reasoning is not proof
"I reasoned the flow works" is not acceptable evidence. The interaction trace is an executed test asserting final state (URL + visible content), not a mental walk-through.
:::

### Key practices

- **TDD and behavior testing** — component, page, hook, e2e, and a11y tests; tests assert what the user sees and does, not internal component state.
- **Security by default** — the frontend obeys the shared security defaults: CSP with no `unsafe-inline`/`unsafe-eval` plus Trusted Types, SRI hashes on external scripts, `__Host-`/`__Secure-` cookie prefixes, `Cache-Control: no-store` on sensitive responses, all HTML routed through a DOMPurify wrapper, validated same-origin redirects (no open redirect), and no secrets in the client bundle.
- **Contract fidelity** — API client types are generated from OpenAPI specs; errors are parsed from RFC 9457 `application/problem+json` and mapped to copy via the shared error catalog; telemetry emits the exact observability-contract names and injects W3C `traceparent` on every request.
- **Accessibility, i18n, and SEO from day one** — `eslint-plugin-jsx-a11y` and axe-core throughout; all user-facing strings externalized with `Intl` formatting and RTL support; indexable routes get unique metadata, canonical, Open Graph, and JSON-LD, with auth routes set `noindex`.

### Outputs

| Output | Location |
|--------|----------|
| Components (ui / layout / features) | `frontend/app/components/` |
| Pages with routing, auth guards, data fetching | `frontend/app/pages/` |
| Hooks, typed API services, client stores | `frontend/app/hooks/`, `services/`, `stores/` |
| Design tokens, theme, global styles | `frontend/app/styles/` |
| i18n message catalogs | `frontend/app/messages/` |
| SEO (sitemap, robots, metadata, JSON-LD) | `frontend/app/sitemap.*`, `robots.*` |
| Tests (incl. executed `e2e/smoke.spec.ts`) | `frontend/tests/` |
| Storybook component docs | `frontend/storybook/` |
| Observability (web-vitals, error reporter, traceparent client) | `frontend/app/lib/observability/` |
| Perf gates | `frontend/lighthouserc.json`, `frontend/.size-limit.json` |
| Workspace artifacts | `drydock/frontend-engineer/` |

The Frontend Engineer also appends two CI gate targets — `size-limit` and `build-frontend` — to the root `Makefile` that the Software Engineer owns.

## What comes next

The code these agents produce flows into the **HARDEN** phase, where the QA Engineer extends `smoke.spec.ts` into a full E2E suite and security and reliability are verified before Gate 3 (production-readiness). See [How it works](/docs/concepts/how-it-works) for the full DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN pipeline.
