# Phase 1: UI/UX Analysis

## Objective

Read BRD user stories and solution architect artifacts from the project root. Confirm framework, state management, and styling choices with the user. Produce a structured analysis in `drydock/frontend-engineer/docs/` (workspace artifacts).

## Phase 0: Framework Selection — product-driven

**Pick the framework that best fits THIS product. Never default to one framework blindly.** Decide in this order (first match wins), then confirm per autonomy level.

**1. Architect's choice wins.** If `docs/architecture/tech-stack.md` names a frontend framework, USE IT — the architect already chose for the whole system. Do not re-litigate.

**2. Brownfield matches existing.** If `drydock/.orchestrator/codebase-context.md` mode is `brownfield`, MATCH the existing framework (React/Vue/Svelte/Angular). Never introduce a second framework into an existing app.

**3. Greenfield → choose by product archetype (read it from the BRD):**

| Product archetype | Best fit | Why |
|-------------------|----------|-----|
| **Content / marketing-led** — landing, blog, docs, brochure; SEO-critical; mostly static; low app interactivity | **Astro** (React islands for interactive bits) | Ships ~zero JS by default → best Core Web Vitals + SEO; reuses the SAME React component library as islands |
| **Full-stack SaaS** — auth'd app + public marketing, server data, SEO needed, mixed server/client rendering | **Next.js (App Router + RSC)** | SSR/ISR + RSC, one framework for marketing + app, largest ecosystem. The default for product SaaS. |
| **Internal tool / admin / pure SPA behind auth** — no SEO, highly interactive, fast iteration | **React + Vite** (TanStack Router + Query) | No SSR overhead, fastest dev loop, smallest toolchain; SEO is irrelevant behind a login |
| **Form/mutation-heavy, web-standards, nested data** | **React Router v7 (Remix)** | Loader/action model, progressive enhancement, excellent form/mutation ergonomics |
| Team/architect already on **Vue / Svelte** | **Nuxt 3 / SvelteKit** | Match team expertise; the design-token + component discipline below still applies |

Tie-breaker for an unspecified product SaaS: **Next.js App Router**.

**Framework-stable vs framework-specific.** The design system, tokens, accessibility, component discipline, observability, security defaults, **i18n**, and testing standards in the phases below are **framework-stable — they apply no matter what you pick.** The framework choice mainly determines **routing, rendering/SSR, and data-loading** (Phase 4). React-family choices (Next/Vite/Remix, and Astro via islands) all reuse the same `components/ui` primitives; only the routing/data layer differs. Record the choice + the archetype that drove it in `drydock/frontend-engineer/docs/framework-decision.md`.

### State Management Options

| Stack | Best For | Why |
|-------|----------|-----|
| **React Query + Zustand (recommended)** | Next.js SaaS with REST/GraphQL APIs | Server state separated from client state, minimal boilerplate, excellent devtools |
| **Redux Toolkit + RTK Query** | Complex client-side state, offline-first, time-travel debugging | Mature, predictable, large team familiarity |
| **Pinia** | Vue/Nuxt applications | Official Vue store, TypeScript-native, devtools integration |
| **Svelte stores + TanStack Query** | SvelteKit applications | Native reactivity, minimal overhead |

### Styling Options

| Approach | Recommendation |
|----------|---------------|
| **Tailwind CSS + CSS variables** | Recommended — design tokens map to CSS custom properties, utility-first with design system constraints |
| **CSS Modules + design tokens** | Good for teams that prefer scoped CSS without utility classes |
| **Styled Components / Emotion** | Runtime CSS-in-JS, declining in favor of zero-runtime solutions |
| **Vanilla Extract** | Zero-runtime, type-safe styles, excellent for design systems |

**Autonomy level determines selection behavior:**
- **Autopilot**: Auto-select via the product-archetype matrix above (**not** a blanket Next.js default) — read the BRD archetype, pick the framework, and report `Framework: {choice} (chosen for {archetype})` plus state/styling defaults. Do NOT ask.
- **Copilot**: If `tech-stack.md` or brownfield resolves it, use that silently. Otherwise surface the top recommendation (with the matrix rationale) + alternatives via AskUserQuestion.
- **Checkpoint/Manual**: Present the matrix recommendation + alternatives via AskUserQuestion and confirm.

## 1.1 User Flow Mapping

Create `drydock/frontend-engineer/docs/user-flows.md`:

- Map every BRD user story to a page or component
- Identify all distinct user flows (signup, onboarding, core CRUD, settings, admin)
- Document navigation hierarchy (top-level routes, nested routes, modals)
- Identify shared layouts (auth layout, dashboard layout, public marketing layout)
- Map role-based access per page (which roles see which pages/sections)

## 1.2 Page Inventory

Create `drydock/frontend-engineer/docs/page-inventory.md`:

```markdown
| Page | Route | Layout | Auth Required | Roles | Key Components | API Endpoints |
|------|-------|--------|---------------|-------|----------------|---------------|
| Login | /login | AuthLayout | No | All | LoginForm, OAuthButtons | POST /auth/login |
| Dashboard | /dashboard | DashboardLayout | Yes | user, admin | StatsCards, RecentActivity, QuickActions | GET /dashboard/stats |
| ... | ... | ... | ... | ... | ... | ... |
```

## 1.3 Component Inventory

Create `drydock/frontend-engineer/docs/component-inventory.md`:

- Catalog every unique UI element from user stories
- Classify by atomic design level (atom, molecule, organism)
- Identify shared vs feature-specific components
- Note interactive states (loading, error, empty, success)
- Document responsive behavior requirements per component

## 1.4 API Surface Mapping

Cross-reference BRD user stories with OpenAPI specs:
- Map each page to the API endpoints it consumes
- Identify real-time requirements (WebSocket, SSE, polling)
- Note optimistic update opportunities
- Document file upload flows and their endpoints
- Identify pagination patterns per list endpoint

## 1.5 Localization & SEO Requirements (scope the work early)

Decide these in analysis so Phases 2–4 build the right foundation rather than retrofitting:

- **Localization (i18n).** From the BRD, determine: single-locale or multi-locale? which locales? any **RTL** language (Arabic/Hebrew)? locale-specific number/date/currency formatting? Record in `drydock/frontend-engineer/docs/i18n-decision.md`.
  - **Multi-locale →** full i18n in Phase 2 (provider + message catalogs + locale routing).
  - **Single-locale →** still **externalize all user-facing strings** into one message catalog and use `Intl` for number/date/currency, so a second locale is a config change, not a rewrite. Never hardcode display strings in components.
- **SEO surfaces.** Identify which routes are public/indexable (marketing, blog, docs, pricing, public profiles) vs behind-auth (no SEO). Public routes get full metadata + Open Graph + canonical + JSON-LD structured data + sitemap/robots (Phase 4). Behind-auth routes are `noindex`. Record the indexable route list.

## Input Dependencies

This skill reads from two upstream sources:

### From Project Root
- `api/openapi/*.yaml` — OpenAPI 3.1 specs for typed client generation
- `docs/architecture/tech-stack.md` — Framework, language, auth provider decisions
- `docs/architecture/system-diagrams/` — C4 container diagrams for understanding service boundaries
- `docs/architecture/architecture-decision-records/` — ADRs for auth strategy, API patterns, multi-tenancy
- `schemas/erd.md` — Entity relationships for understanding data shapes
- `docs/design/` — UX-designer spec **if present** (IA/sitemap, navigation, user flows, wireframes, and the design-system spec). When present it is the **source of truth**: IMPLEMENT it — do not re-derive IA/flows from the BRD or re-author the design system (Phase 2 implements its tokens/components). Falls back to the BRD only when absent.

### From BRD
- User stories with acceptance criteria
- User flow diagrams (signup, onboarding, core workflows, admin) — from `docs/design/` when the UX spec exists, otherwise derived from the BRD
- Information architecture and navigation structure — from `docs/design/` when the UX spec exists, otherwise derived from the BRD
- Role-based access requirements (admin, user, viewer, etc.)
- Branding guidelines (if provided)

## Validation Loop

Before moving to Phase 2:
- Framework chosen **by product archetype** (or architect/brownfield), recorded in `framework-decision.md` with the rationale; state management + styling resolved
- Localization scope decided (single vs multi-locale, RTL?) and SEO/indexable-route list captured (`i18n-decision.md`)
- User flows mapped to pages and components
- Page inventory complete with routes, layouts, auth requirements, and API endpoints
- Component inventory classified by atomic design level
- API surface mapped per page

**Present analysis summary to user for quick review (no formal approval gate — informational).**

## Quality Bar

- Every BRD user story is mapped to at least one page or component
- Every page has its API endpoints identified
- Role-based access documented per page
- Shared layouts identified and catalogued
