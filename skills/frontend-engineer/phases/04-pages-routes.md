# Phase 4: Pages, Routes & API Client Layer

## Objective

Build actual pages with routing, state management, data fetching, and auth guards. Generate typed API clients from OpenAPI specifications. This phase ties together the design system and component library into a working application with full data flow.

## 4.1 Route Structure

Generate routes based on the Page Inventory from Phase 1:

```
pages/                          # Next.js App Router (or equivalent)
├── (auth)/                     # Auth layout group
│   ├── login/page.tsx
│   ├── signup/page.tsx
│   ├── forgot-password/page.tsx
│   └── reset-password/page.tsx
├── (dashboard)/                # Dashboard layout group
│   ├── layout.tsx              # DashboardLayout with sidebar
│   ├── page.tsx                # Dashboard home
│   ├── [resource]/             # Dynamic CRUD routes
│   │   ├── page.tsx            # List view
│   │   ├── [id]/page.tsx       # Detail view
│   │   ├── [id]/edit/page.tsx  # Edit view
│   │   └── new/page.tsx        # Create view
│   ├── settings/
│   │   ├── page.tsx            # General settings
│   │   ├── profile/page.tsx
│   │   ├── billing/page.tsx
│   │   └── team/page.tsx
│   └── admin/                  # Admin-only routes
│       ├── users/page.tsx
│       └── analytics/page.tsx
├── (marketing)/                # Public pages
│   ├── page.tsx                # Landing page
│   ├── pricing/page.tsx
│   └── docs/page.tsx
├── error.tsx                   # Global error boundary
├── not-found.tsx               # 404 page
├── loading.tsx                 # Global loading state
└── layout.tsx                  # Root layout (providers, fonts, metadata)
```

## 4.2 State Management Setup

Create `frontend/app/stores/`:

```
stores/
├── auth-store.ts              # Auth state: user, tokens, login/logout
├── ui-store.ts                # UI state: sidebar open, theme, modals
├── notification-store.ts      # Toast/notification queue
└── index.ts                   # Store initialization
```

For React Query + Zustand (recommended):
- **Zustand** for client-only state (UI state, theme, sidebar toggle, form drafts)
- **React Query** for all server state (API data, caching, optimistic updates, refetch)
- Query keys follow convention: `[resource, action, params]` e.g., `['users', 'list', { page: 1 }]`
- Mutations with optimistic updates for better UX
- Stale time: 5 minutes default, 30 seconds for frequently changing data
- Global error handler for 401 -> redirect to login

## 4.3 Auth Implementation

Create `frontend/app/hooks/use-auth.ts` and auth utilities:

```
hooks/
├── use-auth.ts                # Login, logout, signup, user state
├── use-permissions.ts         # Role-based permission checks
├── use-require-auth.ts        # Redirect if unauthenticated
├── use-debounce.ts            # Debounce input values
├── use-media-query.ts         # Responsive breakpoint detection
├── use-local-storage.ts       # Persistent local storage state
├── use-clipboard.ts           # Copy to clipboard
├── use-pagination.ts          # Pagination state management
├── use-infinite-scroll.ts     # Infinite scroll with intersection observer
├── use-form.ts                # Form state with validation (or integrate react-hook-form)
└── use-keyboard-shortcut.ts   # Global keyboard shortcut registration
```

Auth flow implementation:
- JWT access/refresh token handling with automatic refresh
- Secure token storage (httpOnly cookies for SSR, in-memory for SPA)
- Auth middleware/guard on protected routes (Next.js middleware or route guards)
- OAuth integration stubs for configured providers
- Session expiry detection with re-auth prompt
- Role-based route protection with redirect to unauthorized page

## 4.4 Page Standards

Every page MUST implement:
- **Loading state** — Skeleton screens matching final layout (not generic spinners)
- **Error state** — Contextual error message with retry action
- **Empty state** — Helpful message with primary action CTA
- **SEO metadata** — Title, description, Open Graph, canonical URL
- **Responsive design** — Mobile-first, tested at all breakpoints
- **Breadcrumbs** — Contextual navigation trail
- **Page transitions** — Smooth transitions between routes (optional, respect reduced-motion)

## 4.5 API Client Layer

Auto-generate typed API clients from OpenAPI specifications in `frontend/app/services/`.

### Client Generation

Read `api/openapi/*.yaml` and generate:

```
services/
├── api-client.ts              # Base HTTP client (axios/fetch wrapper)
├── interceptors.ts            # Request/response interceptors (auth, error, logging)
├── generated/                 # Auto-generated from OpenAPI specs
│   ├── types.ts               # Request/response TypeScript types
│   ├── schemas.ts             # Zod validation schemas (generated from OpenAPI)
│   └── endpoints.ts           # Endpoint URL constants
├── auth-service.ts            # Auth API calls (login, signup, refresh, logout)
├── user-service.ts            # User CRUD operations
├── [resource]-service.ts      # Per-resource service files (from OpenAPI paths)
├── query-keys.ts              # React Query key factory
├── queries/                   # React Query hooks per resource
│   ├── use-users.ts           # useUsers, useUser, useCreateUser, useUpdateUser, useDeleteUser
│   └── use-[resource].ts      # Generated per API resource
└── index.ts                   # Barrel export
```

### HTTP Client Standards

Base client (`api-client.ts`) MUST include:
- **Base URL** from environment variable (`NEXT_PUBLIC_API_URL`)
- **Request interceptors** — Attach auth token, set `Content-Type`, add `X-Request-ID`, and **inject the W3C `traceparent` header** from the active browser span (see 4.6 Frontend Observability) so the browser→backend trace is unbroken per `observability-contract.md`
- **Response interceptors** — Handle 401 (refresh token), 403 (redirect to unauthorized), 429 (retry with backoff), 500 (error boundary); parse error bodies as **RFC 9457 `application/problem+json`** (see Error Handling Strategy below)
- **Timeout** — 30 second default, configurable per request
- **Retry logic** — Exponential backoff for 5xx errors (max 3 retries), no retry on 4xx
- **Request deduplication** — Cancel duplicate in-flight requests
- **AbortController** — Cancel requests on component unmount

### React Query Integration

Generated query hooks MUST follow:

```typescript
// Pattern for every resource
export function useUsers(params?: ListParams) {
  return useQuery({
    queryKey: queryKeys.users.list(params),
    queryFn: () => userService.list(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: queryKeys.users.detail(id),
    queryFn: () => userService.get(id),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: userService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    },
  });
}

export function useUpdateUser(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UpdateUserInput) => userService.update(id, data),
    onMutate: async (data) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: queryKeys.users.detail(id) });
      const previous = queryClient.getQueryData(queryKeys.users.detail(id));
      queryClient.setQueryData(queryKeys.users.detail(id), (old) => ({ ...old, ...data }));
      return { previous };
    },
    onError: (err, data, context) => {
      queryClient.setQueryData(queryKeys.users.detail(id), context?.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    },
  });
}
```

### Runtime Validation

- Validate all API responses at runtime using Zod schemas generated from OpenAPI specs
- Log validation errors to monitoring (do not crash the UI)
- Type-narrow response data after validation for full type safety
- Validate request payloads before sending to catch errors early

### Error Handling Strategy (RFC 9457 + shared error catalog)

The backend returns errors as **RFC 9457 `application/problem+json`** (`$ref` to the `Problem` OpenAPI component owned by solution-architect). The frontend parses that exact shape — it does NOT invent a frontend-only error type — and resolves user-facing copy from the **single source-of-truth error catalog** (`libs/shared/errors/catalog.*`), the same module the backend runtime and the docs error table read from. Do not re-declare titles/messages inline.

```typescript
// RFC 9457 problem+json — the wire shape (matches the shared `Problem` component)
type Problem = {
  type: string;        // URI reference identifying the problem type
  title: string;       // short, human-readable summary
  status: number;      // HTTP status code
  detail?: string;     // human-readable explanation specific to this occurrence
  instance?: string;   // URI reference for this specific occurrence
  trace_id?: string;   // standard extension — joins to the backend trace
  errors?: Array<{ field?: string; pointer?: string; detail: string }>; // field-level
};

// Parse ONLY when Content-Type is application/problem+json; fall back to a synthetic
// Problem for network/timeout failures so the UI always has a stable shape.
function parseProblem(res: Response, body: unknown): Problem { /* ... */ }

// User-facing copy comes from the SHARED catalog, keyed by the catalog `code`
// (NOT hardcoded here). The catalog entry supplies title / message_template /
// remediation / docs_anchor; map Problem.type or an errors[] code onto it.
import { errorCatalog } from '@/libs/shared/errors/catalog';
function messageForProblem(p: Problem): string {
  return errorCatalog.resolve(p)?.message ?? p.detail ?? p.title;
}
```

- Surface `trace_id` in the error UI (e.g. a "Reference: <trace_id>" line) so support can join the user's report to the backend trace.
- Render `errors[]` against the matching form fields (`field`/`pointer`) for inline validation feedback.
- Report the failure to the global error reporter (4.6) with `trace_id` attached so it correlates with the backend.

### 4.6 Frontend Observability (EMIT — names per `observability-contract.md`)

Browser telemetry is a CONTRACT, not a nicety: the frontend STARTS the trace and emits the same metric/log/span names the backend, devops dashboards, and sre alerts agree on. Implement in `frontend/app/lib/observability/`:

**Web Vitals → OTLP / analytics endpoint.** Use the `web-vitals` library to capture **LCP, INP, CLS** (plus FCP, TTFB) and POST them to the OTLP/analytics collector (`NEXT_PUBLIC_OTEL_EXPORTER_OTLP_ENDPOINT` / analytics beacon URL — never hard-code a host). These feed the `web_vitals` budget in `docs/architecture/performance-budget.yaml` and the RUM panels. Attach the page `route` (templated, never a raw URL with IDs — cardinality bound) and `trace_id` from the active span.

```
observability/
├── web-vitals.ts        # onLCP/onINP/onCLS → beacon to OTLP/analytics endpoint
├── error-reporter.ts    # window.onerror + unhandledrejection → structured JSON log
├── error-boundary.tsx   # global React error boundary → error-reporter
├── tracing.ts           # browser tracer; startSpan, current traceparent getter
└── index.ts
```

- **Browser RED metrics.** Emit `http_requests_total` and `http_request_duration_seconds` from the API client with labels `method`, `route` (templated), `status_class` — EXACT names from the contract, so the RUM/dashboard panels light up. Duration in **seconds**, standard buckets.
- **Global error reporter.** Register `window.onerror` and `window.addEventListener('unhandledrejection', ...)` plus a top-level React **error boundary** that wraps the root layout (in addition to per-route `error.tsx`). Each report is a structured JSON object with the contract log fields — `timestamp`, `level: "error"`, `message`, `service`, `env`, `trace_id`/`span_id` from the live span, `error.type`/`error.stack` — and is PII-safe (no tokens, no request bodies with personal data).
- **W3C trace propagation.** The browser tracer starts a span per navigation/interaction and the API client request interceptor injects the current `traceparent` (and `baggage`) header on every fetch/XHR, so backend spans join the browser-initiated trace. Resource attributes `service.name`, `service.version`, `deployment.environment` match the backend strings exactly.
- **Export endpoint** is read from env (`NEXT_PUBLIC_OTEL_EXPORTER_OTLP_ENDPOINT`), honoring `OTEL_SERVICE_NAME` / `OTEL_RESOURCE_ATTRIBUTES` — never a hard-coded collector host.

### 4.7 OpenFeature Client Flag Hook (consume shared `libs/shared/feature-flags/`)

Add a client hook `frontend/app/hooks/use-flag.ts` over the **shared OpenFeature client** (`libs/shared/feature-flags/`, owned by software-engineer) and registry `config/feature-flags.yaml`. The frontend does NOT create its own flag system — it adds an SSR/edge-safe hook.

```typescript
// SSR/edge-safe: evaluates on the server during RSC/SSR AND hydrates on the client.
// fail-static: on provider error/unreachable, return the per-flag SAFE DEFAULT
// (from config/feature-flags.yaml `default`) — never throw, never block render.
export function useFlag<T>(key: string, defaultValue: T): T { /* OpenFeature client */ }
```

- **Always-present fallback.** Provider-agnostic; if the provider is down, return the registry's per-flag `default` (fail-static). A flag check never crashes the page or causes hydration mismatch.
- **SSR/edge safety.** Evaluate with a stable context on server and client so the rendered value matches across the SSR/CSR boundary (no flicker, no hydration error). Edge runtime must use the edge-safe provider entrypoint.
- **Registry-driven.** Only consume keys declared in `config/feature-flags.yaml` (`{ key, type, owner, default, created, removal_by }`). Do not invent ad-hoc flag keys.

## Validation Loop

Before moving to Phase 5:
- All routes render with correct layouts
- Auth guards redirect unauthenticated users
- Role-based route protection works correctly
- API client generates typed requests and validates responses
- React Query hooks handle loading, error, and success states
- Optimistic updates work for mutation operations
- State management stores are wired and functional
- All pages implement loading/error/empty states
- API client parses RFC 9457 `application/problem+json` and resolves copy from the shared error catalog (`trace_id` surfaced)
- API client injects W3C `traceparent` on every request; web-vitals + global error reporter wired (4.6)
- `useFlag` hook evaluates SSR/edge-safe with fail-static safe defaults from `config/feature-flags.yaml` (4.7)

**Then run the Functional Verification Pass (see main SKILL.md):**

- [ ] **Dead element scan:** Every button has an onClick that does something. Every link goes to a route that exists. Every form has an onSubmit that calls an API. Zero dead interactive elements.
- [ ] **Navigation graph:** Logo links to home. Every sidebar/nav item links to a real route. Breadcrumbs resolve. Cross-page-group links work (auth→dashboard, dashboard→settings, etc.).
- [ ] **Interaction trace:** Walk through the top 5 user flows click-by-click. Sign up → dashboard → create something → view it → edit it → navigate to settings → return. Every step must work.
- [ ] **Cross-agent reconciliation:** If pages were built by parallel agents, verify all cross-references resolve. Shared layout (header, sidebar) includes routes from ALL page groups.
- [ ] **Auth redirect chain:** Unauthenticated visit to protected page → login → authenticate → return to original page (not hardcoded dashboard).

**Only proceed to Phase 5 after ALL functional verification checks pass.**

**Page review (autonomy-level-aware):** Autopilot — proceed to Phase 5, report page count and flow verification results. Copilot — present key metrics. Checkpoint/Manual — present key pages via AskUserQuestion for approval.

## Quality Bar

- Every page has loading, error, and empty states
- API types are auto-generated, not hand-written
- Auth flow handles token refresh seamlessly
- All pages have SEO metadata
- Mobile-first responsive design at all breakpoints
- No `useEffect` for data fetching (React Query used instead)
- **Zero dead interactive elements** — every button, link, and form does something when clicked
- **Navigation is complete** — every page reachable from at least one nav element, logo links to home
- **Top 5 user flows verified** — walked through click-by-click, every step works end-to-end
- **Errors are RFC 9457** — `application/problem+json` parsed, copy from shared error catalog, `trace_id` surfaced
- **Browser trace started** — `traceparent` injected on every API call; web-vitals + global error boundary/reporter emit contract names
- **Flags fail-static** — `useFlag` SSR/edge-safe, returns registry safe default on provider error
- **`security-defaults checklist passes`** — no secrets in the client bundle, secure cookies (`HttpOnly`+`Secure`+`SameSite`), no auth tokens in `localStorage`, no unsanitized `dangerouslySetInnerHTML`, input validated at the boundary (client validation is UX only)
