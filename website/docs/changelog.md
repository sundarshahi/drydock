---
sidebar_position: 8
title: "Changelog"
description: "Notable changes to Drydock, newest first."
---

# Changelog

Notable changes to [Drydock](https://github.com/sundarshahi/drydock), the open-source plugin for Claude Code. Newest first.

:::info Current version
**2.5.0** — a team of 19 specialized agents coordinated by one orchestrator, running a six-phase pipeline (DEFINE → BUILD → HARDEN → SHIP → LAUNCH → SUSTAIN) with three human approval gates.
:::

For the full per-commit history, see [`CHANGELOG.md`](https://github.com/sundarshahi/drydock/blob/main/CHANGELOG.md) in the repo. See also [How it works](/docs/concepts/how-it-works).

## 2.5.0 — 2026-06-25

Extends the team past engineering into the full product cycle. Drydock already shipped production-ready *software* well; it now also designs the UX and takes the product to market. Four new agents bring the roster from **15 to 19** and add a new **LAUNCH** phase after SHIP.

### Added

- **UX Designer** (`ux-designer`, DEFINE → BUILD) — the missing engineering-adjacent role. Owns user research, information architecture, interaction design, and the design-system **specification** (tokens, type scale, WCAG-AA color, component specs, states, motion) that the frontend-engineer implements.
- **Growth Marketer** (`growth-marketer`, LAUNCH) — positioning, messaging, go-to-market and launch plan, marketing-site copy and SEO briefs, funnels and analytics, and growth experiments.
- **Sales Strategist** (`sales-strategist`, LAUNCH) — pricing and packaging, sales collateral, sales process and qualification, enablement, and proposals. Turns security and compliance evidence into a buyer-facing trust pack (legal artifacts flagged "requires legal review").
- **Customer Success** (`customer-success`, LAUNCH → SUSTAIN) — onboarding and activation, support operations, retention and churn, and a voice-of-customer loop back to the product-manager.
- **New LAUNCH phase** — runs after SHIP and Gate 3, dispatching the three go-to-market agents in parallel; customer-success carries into SUSTAIN. The full pipeline is now DEFINE → BUILD → HARDEN → SHIP → **LAUNCH** → SUSTAIN.
- **Two new execution modes** — **Design (UX)** routing to the ux-designer, and **Launch (GTM)** with a go-to-market plan gate. Brings the total from 12 to **14 modes**.

### Changed

- The orchestrator is wired for all four agents: request classification, gate tables, phase-execution table, internal parallelism, dispatch list, context bridging, workspace directories, and partial execution. Counts updated everywhere (15 → 19 agents, 12 → 14 modes).
- **Pipeline dispatchers now match the roster.** DEFINE dispatches the UX Designer in parallel with the architect once Gate 1 passes (when the frontend feature is enabled), and the DEFINE → BUILD handoff verifies its receipt. BUILD makes the design-system spec the source of truth the frontend implements, rather than inventing tokens. This closes the gap where the orchestrator advertised these tasks but the dispatchers never ran them.
- Authority and boundary rules enforce non-overlap: the ux-designer owns the design *spec* (frontend implements it), the growth-marketer owns positioning (sales consumes it), and customer-success routes feedback to the product-manager (it doesn't change requirements).
- Structural evaluations updated to the new ground truth. All 19 skills stay within the 500-line progressive-disclosure budget.

## 2.4.0 — 2026-06-25

Frontend production-grade upgrade. The `frontend-engineer` skill was already strong (atomic components, WCAG 2.1 AA, React Query, OpenAPI-typed clients, RFC 9457 errors, observability, performance budgets, feature flags); this closes the remaining gaps and makes the **framework choice product-driven** instead of a blanket Next.js default.

### Added

- **Product-driven framework selection.** A decision matrix replaces the default: the architect's tech stack wins, brownfield matches the existing stack, otherwise the framework is chosen by product archetype.

  | Product archetype | Framework |
  | --- | --- |
  | Content / marketing, SEO-critical | Astro |
  | Full-stack SaaS | Next.js App Router |
  | Internal tool / admin SPA | React + Vite |
  | Form-heavy | Remix / React Router v7 |

  The design system, accessibility, observability, security, i18n, and testing standards are framework-stable; only routing, rendering, and data loading vary.
- **Internationalization (i18n)** end to end — provider, message catalogs, `Intl` formatting, and RTL support; a no-hardcoded-strings rule on every component; locale routing with `hreflang`; and a pseudo-locale plus RTL render check in testing. Single-locale projects still externalize strings, so adding a second locale is a config change.
- **Image and web-performance optimization** — an optimized `Image` primitive (explicit dimensions for zero CLS, lazy loading, AVIF/WebP, required `alt`), optimized font loading, and a performance pass (route-level code splitting, parallel data loading, Suspense streaming, LCP prioritization, bundle hygiene) feeding the existing Core Web Vitals and size-budget gate.
- **SEO and discoverability** — per-route metadata, canonical URLs, Open Graph, and schema.org JSON-LD, plus generated `sitemap.xml` and `robots.txt` for public routes; behind-auth routes are marked `noindex`.
- **Production-grade form system** — react-hook-form with a Zod resolver (reusing the OpenAPI-generated schemas), multi-step and wizard forms, field arrays, async and server-error mapping, an accessible error summary, autosave, and an unsaved-changes guard.

### Changed

- **Functional verification is now executed, not reasoned.** The interaction trace was a mental walk-through; it is now an executed Playwright smoke test that builds and boots the app and asserts each top-5 flow reaches its correct final state.

  :::note
  A failing flow is a Critical defect that blocks the next phase, and the smoke spec seeds the qa-engineer's full E2E suite. If the app can't be booted in-environment, the spec is produced and handed to QA as a required gate, recorded as deferred rather than skipped.
  :::

## 2.3.0 — 2026-06-25

Production-grade security hardening. The HARDEN (audit) phase already covered the OWASP Top 10, API, and LLM standards thoroughly; this release closes the **BUILD ↔ AUDIT asymmetry** — control families the audit checks for are now written into the secure-by-default BUILD contract, so builder agents ship them in the first draft instead of relying on HARDEN to retrofit. Grounded in a gap analysis against OWASP ASVS 5.0, API Security Top 10 (2023), LLM Top 10 (2025), OWASP Top 10 CI/CD Security Risks, and SLSA v1.2.

### Added

- **Seven new secure-by-default sections**, each ASVS-tagged and asserted in the BUILD quality bar:
  - **Strong cryptography** — Argon2id/scrypt/bcrypt credential hashing, AES-GCM/ChaCha20-Poly1305 authenticated encryption, a CSPRNG for all tokens and ids, TLS 1.2+.
  - **Authentication and credential handling** — throttling and lockout, an MFA hook, a breach-screened password policy, safe recovery, no user enumeration.
  - **Session and token lifecycle** — CSPRNG session ids, regeneration on privilege change, idle and absolute timeouts, server-side revoke, JWT algorithm allowlist rejecting `alg=none`.
  - **Resource-consumption and anti-automation limits** — body, page, depth, and upload caps, timeouts, per-tenant quotas (API4/API6).
  - **Property-level authorization / mass assignment** — bind allowlisted fields, enforce `role`/`tenant`/`owner` server-side, DTO-shaped responses (API3/BOPLA).
  - **Treat upstream responses as untrusted** — schema-validate, size and timeout caps, verify webhooks (API10).
  - **Security event logging** (A09 / ASVS V16).
- **Backend BUILD phases wired to assert the new defaults**, each adding the control to its local validation loop and quality bar.
- **Frontend browser hardening** — Subresource Integrity on external scripts, `__Host-`/`__Secure-` cookie prefixes, Cross-Origin policies (COOP/CORP/COEP), Trusted Types, HSTS `preload`, and `Cache-Control: no-store` on sensitive responses, all asserted in the E2E security-header test.
- **Security-event logging contract** — a distinct stdout security-event stream keyed by a stable `event` field (`auth.success/failure`, `authz.denied`, `input.rejected`, and more) with fixed field names, a no-secrets/PII rule, and a hand-off to SIEM and alerting.
- **CI/CD and supply-chain hardening** — dependency-confusion controls, poisoned-pipeline-execution guardrails, CI/CD identity and access, runner isolation, audit-to-SIEM, and SLSA v1.2 source-track integrity (signed commits, no force-push). The CI template gains a Terraform/checkov IaC gate, and the production deploy now signs the SBOM and verifies the attestation as a blocking gate.
- **AI/LLM build-side controls** — model and dataset provenance with signature verification as a promotion gate, vector-store per-tenant isolation, data-poisoning defenses, RAG grounding, and runtime token/cost limits (LLM03, LLM04, LLM08, LLM09, LLM10).
- **Audit trail for the secret-guard hook** — every block and every explicit bypass is appended as one JSON line to the project's audit log (best-effort; it never fails the hook).

### Changed

- The session-guard hook anchors detection to the Claude project directory instead of the process working directory, and the hook config verifies each script is a regular file before invoking it. The secret-guard documents its intentional fail-open trust model: a broken guard never wedges a session.

### Fixed

- **Open-redirect guidance** — the auth-callback pattern now requires validating `callbackUrl` as a same-origin or allowlisted relative path before redirecting, rejecting absolute and cross-origin URLs.
- **OWASP Top 10 2025 labeled as Release Candidate 1** (published 6 Nov 2025, not yet ratified; 2021 remains the last finalized edition). The category mappings are unchanged; reports are labeled accordingly.

## 2.2.1 — 2026-06-25

Patch fix for a skill-load failure on permission-checked setups (for example, the VS Code extension and managed installs).

### Fixed

- **Protocol loaders no longer hard-fail the permission check.** Every worker skill loaded shared protocols with a compound shell line joined by `||`. Claude Code decomposes compound commands at `||` and requires each sub-command to be allow-listed, so skill expansion failed with *"This Bash command contains multiple operations… require approval"* — most visibly on the orchestrator, the one skill with no `allowed-tools`.

  :::tip Resolution
  Loaders are now single commands that call two bundled helpers, which do the path fallback internally and always exit 0. Every skill declares narrow `allowed-tools` grants for those helpers, so loaders run with no prompt and no user-side settings, marketplace installs included. The helpers reject absolute paths, parent traversal, and non-slug protocol names.
  :::

### Changed

- A loader-shape test now guards the single-command convention: it fails on any loader containing a compound operator (the exact regression fixed here), checks every protocol reference resolves to a real file, and exercises both helpers across all fallback scenarios and their traversal guards.
