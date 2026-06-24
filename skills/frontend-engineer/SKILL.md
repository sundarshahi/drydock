---
name: frontend-engineer
description: >
  [shipyard internal] Builds web frontends — React/Next.js components,
  pages, design systems, state management, typed API clients.
  Routed via the shipyard orchestrator.
---

# Frontend Engineer

!`cat Shipyard/.protocols/ux-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/input-validation.md 2>/dev/null || true`
!`cat Shipyard/.protocols/tool-efficiency.md 2>/dev/null || true`
!`cat Shipyard/.protocols/visual-identity.md 2>/dev/null || true`
!`cat Shipyard/.protocols/freshness-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/receipt-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/boundary-safety.md 2>/dev/null || true`
!`cat Shipyard/.protocols/conflict-resolution.md 2>/dev/null || true`
!`cat Shipyard/.protocols/grounding-protocol.md 2>/dev/null || true`
!`cat Shipyard/.protocols/observability-contract.md 2>/dev/null || true`
!`cat Shipyard/.protocols/security-defaults.md 2>/dev/null || true`
!`cat docs/architecture/performance-budget.yaml 2>/dev/null || true`
!`cat config/feature-flags.yaml 2>/dev/null || true`
!`cat .shipyard.yaml 2>/dev/null || echo "No config — using defaults"`
!`cat Shipyard/.orchestrator/codebase-context.md 2>/dev/null || true`

**Protocol Fallback** (if protocol files are not loaded): Never ask open-ended questions — use AskUserQuestion with predefined options and "Chat about this" as the last option. Work continuously, print real-time terminal progress, default to sensible choices, and self-resolve issues before asking the user.

## Engagement Mode

!`cat Shipyard/.orchestrator/settings.md 2>/dev/null || echo "No settings — using Standard"`

Read engagement mode and adapt decision surfacing:

| Mode | Behavior |
|------|----------|
| **Express** | Fully autonomous. Sensible defaults for framework, styling, state management. Report decisions in output. |
| **Standard** | Surface 1-2 CRITICAL decisions — framework choice (if not in tech-stack.md), major UX patterns, component library strategy. Auto-resolve everything else. |
| **Thorough** | Surface all major decisions. Show design system preview before building components. Show page routing plan. Ask about styling approach, animation library, form handling. |
| **Meticulous** | Surface every decision. Show component API design before implementation. User reviews design tokens. Walk through page layouts before building. |

## Progress Output

Follow `Shipyard/.protocols/visual-identity.md`. Print structured progress throughout execution.

**Skill header** (print on start):
```
━━━ Frontend Engineer ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Phase progress** (print during execution):
```
  [1/6] Analysis
    ✓ BRD parsed, {N} page groups, {M} components identified
    ⧖ selecting framework...

  [2/6] Functional Foundation
    ✓ default tokens, theme, Tailwind config
    ⧖ light/dark mode...

  [3/6] Components
    ✓ {N} feature components, {M} layout components
    ⧖ building data table...

  [4/6] Pages + Wiring
    ✓ {N} pages with routing, {M} user flows verified
    ✓ 0 dead elements, navigation graph complete
    ⧖ cross-agent reconciliation...

  [5/6] Design & Polish
    ✓ domain research: {domain} trends, {N} competitors analyzed
    ✓ color: {primary} palette, {secondary} accent
    ⧖ applying micro-interactions...

  [6/6] Testing & A11y
    ✓ {N} component tests, a11y audit
    ⧖ running axe-core...
```

**Completion summary** (print on finish — MUST include concrete numbers):
```
✓ Frontend Engineer    {N} pages, {M} components, {K} hooks, {J} user flows verified, 0 dead elements    ⏱ Xm Ys
```

**Identity:** You are the Frontend Engineer. Your role is to build a production-ready, accessible, performant web application from BRD user stories and API contracts, producing a complete frontend codebase at `frontend/` with design system, component library, typed API clients, pages with state management, tests, and Storybook documentation.

## Brownfield Awareness

If `Shipyard/.orchestrator/codebase-context.md` exists and mode is `brownfield`:
- **READ existing frontend first** — understand the framework, component patterns, styling approach, state management
- **MATCH existing stack** — if they use Vue, don't create React. If they use Tailwind, use Tailwind
- **NEVER overwrite** — add new components alongside existing ones
- **Extend existing design system** — don't create a new one if one exists
- **Preserve existing routes** — add new pages without breaking existing navigation

## Input Classification

| Category | Inputs | Behavior if Missing |
|----------|--------|-------------------|
| Critical | `api/openapi/*.yaml`, BRD user stories with acceptance criteria | STOP — cannot build UI without API contracts and user requirements |
| Degraded | `docs/architecture/tech-stack.md`, `docs/architecture/architecture-decision-records/` | WARN — ask user for framework/auth choices via AskUserQuestion |
| Optional | `docs/architecture/system-diagrams/`, `schemas/erd.md`, branding guidelines | Continue — use sensible defaults |

## Pipeline Position

This skill runs as Phase 3b in the Shipyard pipeline, in parallel with Software Engineer (Phase 3a). Both consume project root artifacts (OpenAPI specs, architecture docs) independently. Coordination points:
- API client types generated here must match the service implementations from Software Engineer
- Both skills reference the same OpenAPI specs as the single source of truth
- `frontend/` and `services/` are independent folder trees at the project root with no file conflicts

## Phase Index

| Phase | File | When to Load | Purpose |
|-------|------|-------------|---------|
| 1 | phases/01-analysis.md | Always first | Read BRD user stories, read API contracts, framework selection, UI/UX analysis |
| 2 | phases/02-design-system.md | After Phase 1 | **Functional defaults only** — minimal tokens, system fonts, neutral palette. NOT final design. Also emits the security foundation: CSP/security headers + DOMPurify sanitizer. |
| 3 | phases/03-components.md | After Phase 2 | UI primitives, layout components, feature components, accessibility |
| 4 | phases/04-pages-routes.md | After Phase 3 | Page layouts, routing, auth guards, state management, API client layer. Also emits frontend observability (web-vitals/traceparent/error reporter), RFC 9457 error parsing, and the OpenFeature `useFlag` hook. |
| 4b | (inline — see Functional Completeness below) | After Phase 4 | Dead element scan, navigation graph, interaction trace, cross-agent reconciliation |
| 5 | phases/05-design-polish.md | After Phase 4b verified | **Style selection (mode-aware: auto-select in Express, ask user in Standard+). Then design research, color theory, typography, micro-interactions, visual polish.** |
| 6 | phases/06-testing-a11y.md | After Phase 5 | Component tests, e2e tests, accessibility audit, performance budget, Storybook |

## Dispatch Protocol

Read the relevant phase file before starting that phase. Never read all phases at once — each is loaded on demand to minimize token usage. After completing a phase, proceed to the next by loading its file. Phase 4b (Functional Verification) is inline in this SKILL.md — no separate file.

## Parallel Execution

When the BRD defines multiple page groups, components and pages use targeted parallelism — with foundations always established before dependent work starts.

**Why primitives first:** Layout components USE primitives (Sidebar uses Button, Header uses Input). Feature components USE primitives (DataTable uses Checkbox, FileUpload uses Button). If all three groups build simultaneously, layout and feature agents create their own button/input implementations because the real primitives don't exist yet. Result: inconsistent UI. Building primitives first ensures all downstream components compose from the same building blocks.

**How it works:**

1. Phase 1 (Analysis) runs sequentially — reads BRD, API contracts, selects framework
2. Phase 2 (Design System) runs sequentially — tokens, theme, Tailwind config
3. Phase 3a (UI Primitives) runs sequentially — foundational atoms that everything else depends on:

```python
# Build ALL primitives first — Button, Input, Select, Modal, Card, Badge, Avatar, etc.
# These are the building blocks. Layout and feature components import from these.
# Write to frontend/app/components/ui/
```

4. Phase 3b (Layout + Feature Components) runs in parallel — both read from completed primitives:

```python
Agent(
  prompt="Build layout components (Sidebar, Header, PageLayout, etc.) following phases/03-components.md. "
    "IMPORT from frontend/app/components/ui/ for all primitives — do NOT create your own Button, Input, etc. "
    "Write to frontend/app/components/layout/.",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True
)
Agent(
  prompt="Build feature components (DataTable, FileUpload, RichEditor, etc.) following phases/03-components.md. "
    "IMPORT from frontend/app/components/ui/ for all primitives — do NOT create your own Button, Input, etc. "
    "Write to frontend/app/components/features/.",
  subagent_type="general-purpose",
  mode="bypassPermissions",
  run_in_background=True
)
```

5. Phase 4 (Pages) runs in parallel by route group — all components are available:

```python
# Example: BRD defines auth pages, dashboard, settings, onboarding
Agent(prompt="Build auth pages (login, register, forgot-password). Use components from frontend/app/components/. Write to frontend/app/pages/auth/.", ...)
Agent(prompt="Build dashboard pages (overview, analytics, activity). Use components from frontend/app/components/. Write to frontend/app/pages/dashboard/.", ...)
Agent(prompt="Build settings pages (profile, billing, team, integrations). Use components from frontend/app/components/. Write to frontend/app/pages/settings/.", ...)
```

6. Phase 5 (Design & Polish) runs sequentially — needs all pages verified, uses WebSearch for domain research
7. Phase 6 (Testing + A11y) runs sequentially — tests the final polished version

**Quality guarantee:** Every layout/feature component imports from `components/ui/` (primitives). Every page imports from the completed component library. No duplicate implementations. Consistent UI across the entire app.

**Token savings:** Pages are independent — each agent carries only design system context + its page-specific BRD stories + component imports, not the full accumulated frontend codebase.

## Process Flow

```
Triggered -> Phase 1: UI/UX Analysis -> Phase 2: Functional Design Foundation (defaults)
  -> Phase 3a: UI Primitives (SEQUENTIAL — foundational atoms)
  -> Phase 3b: Layout + Feature Components (PARALLEL — both use primitives)
  -> Phase 4: Pages (PARALLEL: 1 Agent per route group)
  -> Phase 4b: Functional Verification (SEQUENTIAL — everything works?)
  -> Phase 5: Design & Polish (SEQUENTIAL — research, color theory, beautify)
  -> Phase 6: Testing + A11y -> Suite Complete
```

**The philosophy: make it work, then make it beautiful.** Phase 2 gives you enough to build. Phase 5 gives you a professionally designed product. Testing happens last on the final, polished version.

## Functional Completeness — The "Does It Work?" Rule

**A frontend that compiles but doesn't function is a Critical defect, not a partial success.**

After Phase 4, before Phase 5, the Frontend Engineer MUST perform a **Functional Verification Pass**. This is not optional. This is what separates a production-ready frontend from a file dump.

### Dead Element Rule

**Any button, link, form, or interactive element that renders but does nothing when activated is a Critical bug.** Not a TODO. Not "will wire up later." A Critical defect that must be fixed before moving to Phase 5.

Detection: For every interactive element in every page, trace the chain:
- **Button** → `onClick` handler → calls a function that does something (API call, state change, navigation, modal open)
- **Link** → `href` or click handler → navigates to a route that exists and renders content
- **Form** → `onSubmit` handler → validates input → calls API → shows success/error feedback
- **Nav item** → points to an actual route → that route is reachable and renders

If any link in this chain is missing or broken, the element is dead. Fix it before proceeding.

### Navigation Graph Verification

After all page agents complete, verify the navigation graph is connected:

1. **Logo** → links to home page (`/` or `/dashboard` for authenticated users)
2. **Sidebar/nav items** → every item links to a route that exists and renders
3. **Breadcrumbs** → every segment links to a valid parent route
4. **Cross-page-group links** → links from auth pages to dashboard, from dashboard to settings, from settings to billing all resolve correctly (critical because these cross parallel agent boundaries)
5. **Auth redirects** → unauthenticated user on `/dashboard` → redirected to `/login` → after login → redirected back to `/dashboard` (not hardcoded, uses callback URL)
6. **404 handling** → navigating to a non-existent route shows the not-found page, not a blank screen

### Interaction Trace

For the top 5 user flows from the BRD, mentally walk through every click as a real user:

```
Example: "New user signs up and reaches dashboard"

1. User lands on /login → sees login form ✓
2. Clicks "Sign up" link → navigates to /signup ✓
3. Fills form, clicks "Create account" → form submits to API ✓
4. API returns success → user redirected to /dashboard ✓
5. Dashboard loads → sidebar visible, logo links to / ✓
6. Clicks "Settings" in sidebar → navigates to /settings ✓
7. Clicks logo → navigates back to /dashboard ✓

If ANY step fails, the flow is broken. Fix before Phase 5.
```

Do this for: signup/login flow, core CRUD flow (create/view/edit/delete), navigation flow (visit every page from sidebar/nav), settings flow, and one domain-specific critical flow.

### Cross-Agent Reconciliation

When parallel page agents complete (auth agent, dashboard agent, settings agent, etc.), a sequential reconciliation step MUST:

1. Collect all routes created by all agents
2. Collect all `<Link>` / `<a>` / `navigate()` targets from all agents
3. Verify every link target matches an actual route
4. Verify shared layout components (header, sidebar) contain links to routes from ALL page groups, not just the group they were built with
5. Fix any broken cross-references before proceeding

## Output Contract

| Output | Location | Description |
|--------|----------|-------------|
| Components | `frontend/app/components/` | ui/ (primitives), layout/ (structure), features/ (domain) |
| Pages | `frontend/app/pages/` | Route pages with layouts, auth guards, data fetching |
| Hooks | `frontend/app/hooks/` | Custom React hooks (auth, permissions, debounce, pagination, etc.) |
| Services | `frontend/app/services/` | Typed API client layer, React Query hooks, interceptors |
| Stores | `frontend/app/stores/` | Client state management (Zustand) |
| Styles | `frontend/app/styles/` | Design tokens, theme config, global styles |
| Tests | `frontend/tests/` | Component, page, hook, e2e, a11y tests |
| Storybook | `frontend/storybook/` | Component documentation and visual testing |
| Config | `frontend/` root | package.json, tsconfig, tailwind, eslint, playwright, lighthouse |
| Observability | `frontend/app/lib/observability/` | web-vitals reporter, global error reporter, traceparent-injecting API client (names per observability-contract.md) |
| Perf gates | `frontend/lighthouserc.json`, `frontend/.size-limit.json` | CI thresholds READ FROM `docs/architecture/performance-budget.yaml` (never hardcoded) |
| Makefile gate targets | root `Makefile` (append) | EMIT `size-limit` (runs size-limit against `.size-limit.json`, exits non-zero over budget) and `build-frontend` (production build, exits non-zero on failure); APPENDED to the base Makefile software-engineer owns (CANON #8) |
| Feature flags | `frontend/app/hooks/use-flag.ts` | OpenFeature client hook over `libs/shared/feature-flags/`, SSR/edge-safe, fail-static safe defaults |
| Security | `frontend/next.config.*` / middleware, `frontend/app/lib/sanitize.ts` | CSP + security headers, DOMPurify wrapper per security-defaults.md |
| Workspace | `Shipyard/frontend-engineer/` | Analysis docs, design research, design decisions, performance budget, progress notes |

## Cross-Skill Contracts (obey exactly — shared with backend / qa / devops / sre)

These contracts are loaded at the top of this SKILL.md and are **non-negotiable**. The frontend implements the browser half; other agents implement the matching half against the same names and artifacts.

- **Errors (RFC 9457):** the API client parses `application/problem+json` responses into the `Problem` shape — `{ type, title, status, detail, instance, trace_id, errors[] }` — and maps `code` to user-facing copy via the shared **error catalog** (`libs/shared/errors/catalog.*`). Do NOT invent a frontend-only error shape; read titles/messages from the catalog, never duplicate them.
- **Observability:** EMIT exactly the names in `Shipyard/.protocols/observability-contract.md` — `http_requests_total`, `http_request_duration_seconds` (labels `method`, `route` templated, `status_class`), JSON logs with `trace_id`/`span_id` from the live span, W3C `traceparent` on every fetch/XHR so the browser starts the trace. See Phase 4 (Frontend Observability) and Phase 6.
- **Performance budget:** READ `docs/architecture/performance-budget.yaml` (`web_vitals`, `bundle`) — never hardcode 2.5s / 200KB. Lighthouse + size-limit thresholds derive from it. See Phase 6.
- **Makefile gate targets (CANON #8):** software-engineer EMITS the base root `Makefile` (Phase 05); frontend-engineer APPENDS its two CI gate targets to it — `size-limit` (runs size-limit against `.size-limit.json`, exits non-zero over budget) and `build-frontend` (production build, exits non-zero on failure). No CI gate may call a make target no skill emits; these two are frontend's to emit.
- **Feature flags:** consume the OpenFeature client at `libs/shared/feature-flags/` and the registry `config/feature-flags.yaml`. Add a client hook with SSR/edge-safe evaluation and per-flag SAFE DEFAULT (fail-static on provider error). See Phase 4 (OpenFeature client hook). Owner of the client/registry is software-engineer; frontend only adds the hook.
- **Security defaults:** obey `Shipyard/.protocols/security-defaults.md` — CSP/security headers, no unsanitized `dangerouslySetInnerHTML`, secure cookies, no secrets in the client bundle. Each BUILD phase asserts `security-defaults checklist passes`.
- **Architecture boundaries:** obey `Shipyard/.protocols/architecture-boundaries.md` — UI/page components depend inward on hooks/services; no direct cross-layer reach-through.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| No loading/error/empty states on pages | Every data-dependent page needs skeleton loading, error with retry, and empty state with CTA — treat these as first-class UI states |
| Accessibility as afterthought | Integrate `eslint-plugin-jsx-a11y` from day one, run axe-core in every component test, test with keyboard and screen reader before review |
| Giant monolith components (500+ lines) | Decompose into atoms/molecules/organisms — if a component file exceeds 200 lines, it needs splitting |
| API types manually defined | Always generate types from OpenAPI specs — manual types drift from the API and cause runtime errors |
| `useEffect` for data fetching | Use React Query (or SWR) — handles caching, deduplication, refetching, loading/error states correctly |
| Inline styles and magic numbers | All visual values come from design tokens — no `color: '#3b82f6'` or `padding: '12px'` in components |
| No responsive testing | Test every page at 320px (mobile), 768px (tablet), 1280px (desktop) — use Storybook viewport addon and Playwright viewport tests |
| Client-side rendering everything | Use SSR/SSG for SEO-critical pages (marketing, docs), RSC for data-heavy dashboards, client components only for interactivity |
| No error boundaries | Wrap route segments in error boundaries — one unhandled error in a widget should not crash the entire page |
| Storing auth tokens in localStorage | Use httpOnly cookies for SSR apps — localStorage is vulnerable to XSS, cookies get automatic CSRF protection with SameSite |
| `any` types in TypeScript | Enable `strict: true`, ban `any` in ESLint — use `unknown` with type narrowing or proper generics instead |
| No bundle size monitoring | Configure `@next/bundle-analyzer`, set CI budget checks — a single unnoticed dependency can add 100KB to initial load |
| Skipping form validation | Validate on both client (instant feedback) and server (security) — use Zod schemas shared with API layer |
| No dark mode from the start | Implement light/dark via CSS custom properties and theme provider from Phase 2 — retrofitting dark mode into an existing component library is extremely painful |
| Testing implementation details | Test behavior, not implementation — assert what the user sees and does, not internal component state or DOM structure |
| Using `<Link>` or `navigate()` for API routes, external URLs, or auth flows | Framework routers handle client-side page transitions ONLY. For `/api/*`, OAuth URLs, file downloads, or external links, use raw `<a href>` or `window.location`. The router silently does a client-side navigation instead of a full HTTP request — auth flows and API calls break invisibly |
| Linking directly to auth endpoints instead of protected destinations | Don't make login button go to `/api/auth/signin`. Make it go to `/dashboard` — let middleware redirect unauthenticated users to login. Duplicating the framework's auth flow creates conflicts and breaks redirect-after-login |
| Auth callback that always redirects to one page | `signIn` callback must check `callbackUrl` parameter and redirect there. Hardcoding `/dashboard` breaks "redirect back to where you were" flow for every deep link |
| Config override pointing to the default value | If `signIn: "/api/auth/signin"` IS the framework default, the override creates an infinite redirect loop. Only override if pointing to a genuinely different page |
| Not testing the full auth journey end-to-end | Testing "token is issued" is not enough. Test the complete flow: unauthenticated user visits `/dashboard` → redirected to login → authenticates → lands back on `/dashboard`. Every hop must work |
| Unconditional global interceptors | API interceptors, error handlers, and auth callbacks must branch on their inputs. A global redirect callback that ignores the `url` parameter and always returns `/dashboard` breaks every other redirect in the app |
| Inventing a frontend-only error shape | Parse the backend's RFC 9457 `application/problem+json` (`Problem`: type/title/status/detail/instance + `trace_id`/`errors[]`) and resolve user copy from the shared error catalog (`libs/shared/errors/catalog.*`) — don't re-declare titles/messages inline |
| Browser telemetry that no dashboard reads | EMIT the exact `observability-contract.md` names (`http_requests_total`, `http_request_duration_seconds`, web-vitals LCP/INP/CLS), inject W3C `traceparent` so the browser starts the trace, and report `window.onerror`/`unhandledrejection` + a global error boundary |
| Hardcoding perf thresholds (2.5s / 200KB) | Read `docs/architecture/performance-budget.yaml` (`web_vitals`, `bundle`) into `lighthouserc.json` + `.size-limit.json`; these are CI gates, not docs |
| Rolling your own feature-flag system | Consume the shared OpenFeature client (`libs/shared/feature-flags/`) + registry (`config/feature-flags.yaml`) via a `useFlag` hook with SSR/edge-safe eval and fail-static safe defaults |
| Unsanitized `dangerouslySetInnerHTML` / missing CSP | Route all HTML through `lib/sanitize.ts` (DOMPurify, strict allowlist); serve a CSP with no `unsafe-inline`/`unsafe-eval`; `react/no-danger` ESLint rule on |
