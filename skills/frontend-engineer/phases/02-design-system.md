# Phase 2: Functional Design Foundation

## Objective

Establish the **minimum viable design system** so components can be built and wired. This is NOT the final design — this is defaults that work. The real design research and polish happens in Phase 5 after everything is functional.

Do NOT spend time on color theory, trend research, or visual polish here. Use sensible defaults. Get to working components fast.

## 2.1 Design Tokens (Defaults)

Create `frontend/app/styles/tokens/`:

```
tokens/
├── colors.ts          # Neutral palette + one primary color (blue default)
├── typography.ts      # System font stack, modular scale
├── spacing.ts         # 4px base unit scale
├── breakpoints.ts     # Standard responsive breakpoints
├── shadows.ts         # 3-level elevation (sm, md, lg)
├── radii.ts           # 3-level border radius (sm, md, lg)
├── z-index.ts         # Z-index scale
├── motion.ts          # Fast/normal/slow durations
└── index.ts           # Unified export
```

Token standards (functional defaults — will be refined in Phase 5):
- **Colors** — Neutral gray scale (50-950). One primary color (blue). Semantic: `success` (green), `warning` (amber), `danger` (red). WCAG AA contrast ratios.
- **Typography** — System font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', ...`). Modular scale (1.25). Heading levels h1-h6. Line height: 1.5 body, 1.2 headings.
- **Spacing** — 4px base: `0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64`.
- **Breakpoints** — `sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`, `2xl: 1536px`.
- **Motion** — `fast: 150ms`, `normal: 300ms`, `slow: 500ms`. Respect `prefers-reduced-motion`.

## 2.2 Theme Configuration (Minimal)

Create `frontend/app/styles/theme/`:

```
theme/
├── theme-provider.tsx     # React context for theme switching
├── light-theme.ts         # Light mode (default neutral palette)
├── dark-theme.ts          # Dark mode (inverted neutral palette)
├── theme.css              # CSS custom properties from tokens
└── global.css             # Reset, base styles, font loading
```

Requirements:
- Light and dark mode with system preference detection
- Theme toggle with localStorage persistence
- CSS custom properties bridge tokens to components
- No FOUC on theme load

## 2.3 Tailwind Configuration (if Tailwind selected)

Create `frontend/tailwind.config.ts`:
- Extend with default design tokens
- Standard color palette
- Typography plugin
- Animation utilities
- Container queries

**Keep it simple. These tokens will be upgraded in Phase 5 (Design & Polish) with researched colors, typography, and visual identity.**

## 2.4 Security Foundation (EMIT — secure-by-default per `security-defaults.md`)

Security defaults are written into the first draft, not bolted on after the audit. Establish them now, at the foundation, so every component and page inherits them.

**CSP + security headers.** EMIT framework-level security headers via `next.config.*` `headers()` (or middleware / framework equivalent):
- `Content-Security-Policy` that blocks inline script — **no `unsafe-inline`, no `unsafe-eval`** (use nonces/hashes for any required inline). Defense-in-depth against XSS.
- `Strict-Transport-Security` (HSTS), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` (or CSP `frame-ancestors`), `Referrer-Policy: strict-origin-when-cross-origin`, a restrictive `Permissions-Policy`.

**Sanitization wrapper.** EMIT `frontend/app/lib/sanitize.ts` — a DOMPurify wrapper with a strict allowlist. **No raw `dangerouslySetInnerHTML`** anywhere: any HTML injection must pass through this sanitizer first. Add an ESLint rule (`react/no-danger`) so unsanitized usage fails CI; render untrusted strings as text by default.

**Other secure defaults (carry forward):**
- No secrets in the client bundle — only `NEXT_PUBLIC_*` config values are exposed; credentials/tokens stay server-side (cross-ref `security-defaults.md`).
- Auth/session cookies are `HttpOnly` + `Secure` + `SameSite=Lax|Strict`; no auth tokens or PII in `localStorage` (enforced in Phase 4 auth).

## Validation Loop

Before moving to Phase 3:
- All tokens defined and exported
- Light/dark themes render
- Theme toggle works
- Tailwind config extends with tokens
- CSP + security headers emitted (no `unsafe-inline`/`unsafe-eval`); `lib/sanitize.ts` (DOMPurify) present; `react/no-danger` ESLint rule on

**Do NOT present design system for approval here — it's defaults. Move to components.**

## Quality Bar

- Every color meets WCAG 2.1 AA contrast
- Typography scale is consistent
- Spacing scale covers layout needs
- No hardcoded visual values
- This is a FUNCTIONAL foundation, not the final design
- **`security-defaults checklist passes`** — CSP/security headers served (no `unsafe-inline`/`unsafe-eval`), DOMPurify sanitizer in place with no unsanitized `dangerouslySetInnerHTML`, no secrets in the client bundle, secure-cookie defaults established for Phase 4 auth
