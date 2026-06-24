# Phase 4: Docusaurus Scaffold

## Objective

Set up a production-ready Docusaurus documentation site that organizes all docs written in Phases 1-3, with sidebar navigation, search, versioning, and a deployment pipeline. This phase is conditional — execute only if `features.documentation_site` is true or if the user confirms they want a documentation site.

## 4.1 — Mandatory Inputs

| Input | Path | What to Extract |
|-------|------|-----------------|
| All documentation | `docs/` | Pages to organize into sidebar categories |
| Project metadata | `package.json` or `README.md` | Project name, description, repository URL |
| Branding assets | `frontend/public/` or project root | Favicon, logo, brand colors (use defaults if absent) |
| Content inventory | `Shipyard/technical-writer/content-inventory.md` | Sitemap from Phase 1 |

## 4.2 — Docusaurus Project Setup

Generate the scaffold in `docs/docusaurus/`:

1. **`package.json`** — Docusaurus 3.x dependencies:
   - `@docusaurus/core`, `@docusaurus/preset-classic`, `@docusaurus/theme-search-algolia`
   - React 18, `clsx`, `prism-react-renderer`
   - Scripts: `start`, `build`, `serve`, `clear`
   - Engine requirement: Node >= 18

2. **`babel.config.js`** — Standard Docusaurus Babel config:
   ```javascript
   module.exports = { presets: [require.resolve('@docusaurus/core/lib/babel/preset')] };
   ```

3. **`src/css/custom.css`** — Brand colors extracted from project assets or sensible defaults:
   - Primary color, dark variant, darker variant, light variant, lighter variant
   - Font family override if project uses a custom font

4. **`src/pages/index.js`** — Landing page with:
   - Project name and tagline
   - "Get Started" button linking to quickstart
   - Feature highlights (3-4 cards: API Reference, Developer Guides, Operations)

## 4.3 — Docusaurus Configuration

Generate `docs/docusaurus/docusaurus.config.js`:

1. **Site metadata** — Title, tagline, favicon, URL, base URL, organization, project name
2. **Docs preset** — Sidebar path, edit URL pointing to repository, `showLastUpdateTime: true`, `showLastUpdateAuthor: true`
3. **Blog disabled** — `blog: false` (documentation site, not a blog)
4. **Navbar** — Project name, Docs link, API Reference link, GitHub link
5. **Footer** — Docs links (Quickstart, API Reference), Community links (GitHub, Discord placeholder)
6. **Algolia search** — Configuration with placeholder app ID and API key (annotated with setup instructions)
7. **Broken links** — `onBrokenLinks: 'throw'`, `onBrokenMarkdownLinks: 'warn'`
8. **Versioning** — Current version labeled as "Next" at path "next"

## 4.4 — Sidebar Configuration

Generate `docs/docusaurus/sidebars.js` matching the documentation sitemap from Phase 1:

```javascript
const sidebars = {
  docs: [
    {
      type: 'category', label: 'Getting Started', collapsed: false,
      items: ['getting-started/quickstart', 'getting-started/installation', 'getting-started/local-development'],
    },
    {
      type: 'category', label: 'Architecture',
      items: ['architecture/overview', 'architecture/service-map',
        { type: 'category', label: 'Design Decisions', items: [/* populated from docs/architecture/decisions/ */] },
      ],
    },
    {
      type: 'category', label: 'API Reference',
      items: ['api-reference/authentication',
        { type: 'category', label: 'Endpoints', items: [/* populated from docs/api-reference/endpoints/ */] },
        'api-reference/error-codes', 'api-reference/rate-limiting', 'api-reference/webhooks',
      ],
    },
    {
      type: 'category', label: 'Guides',
      items: ['guides/coding-conventions', 'guides/testing-guide', 'guides/contributing'],
    },
    {
      type: 'category', label: 'Operations',
      items: ['operations/deployment', 'operations/monitoring', 'operations/incident-response', 'operations/runbook-index'],
    },
    {
      type: 'category', label: 'Integrations',
      items: ['integrations/sdk-quickstart', 'integrations/webhook-guide'],
    },
  ],
};
```

Categories must match the actual documentation files produced in Phases 2-3. Remove sidebar entries for docs that were not generated (e.g., if no webhooks exist, remove the webhooks entry).

## 4.5 — Search Configuration

Configure search in one of two modes:

1. **Algolia DocSearch** (recommended for public docs):
   - Add placeholder `appId`, `apiKey`, `indexName` to `docusaurus.config.js`
   - Add a `<!-- TODO: Apply for Algolia DocSearch at https://docsearch.algolia.com/ -->` comment
   - Enable `contextualSearch: true` for versioned docs

2. **Local search** (for private/internal docs):
   - Add `@cmfcmf/docusaurus-search-local` as alternative
   - Configure language, index blog (false), index docs (true)

Document the chosen approach in `Shipyard/technical-writer/writing-notes.md`.

## 4.6 — Deployment Configuration

Generate deployment config for the documentation site:

1. **GitHub Pages** (default, GitHub Actions first) — Generate `.github/workflows/docs-build.yml`. It carries BOTH the site build and the **blocking docs gates** (each step exits non-zero on breach):
   - Trigger on push to main and PR to main (paths: `docs/**`, `api/**`, `libs/shared/errors/**`, `config/feature-flags.yaml`)
   - `docs:gen-check` — re-run `scripts/gen-error-docs.*` and `scripts/gen-api-collection.*`, then `git diff --exit-code docs/api-reference/error-codes.md docs/api-collection/`. A drifted/hand-edited generated doc FAILS the build (single-source-of-truth enforcement).
   - OpenAPI spec validation step using `swagger-editor-validate` on `api/openapi/*.yaml`.
   - metric-name lint — grep `docs/operations/monitoring.md` for any metric/log/span token absent from `observability-contract.md`; fail on a hit.
   - budget-ref lint — fail if perf docs hardcode a number rather than referencing `docs/architecture/performance-budget.yaml`.
   - `npm ci` + `npm run build` with `onBrokenLinks: 'throw'` (broken-link gate, incl. every error `docs_anchor`).
   - Reference (do NOT redefine) the **devops-owned `docs-examples` job** that extracts and runs fenced examples — note in a comment that this skill guarantees the examples are real/self-contained and devops owns execution.
   - Deploy job: upload pages artifact, deploy to GitHub Pages — gated on all the above passing.
   - **'production-ready' is BLOCKED** if any gate above fails; the only bypass is a logged **'accepted with justification'** override (per `receipt-protocol.md`), never a silent skip.

2. **Vercel** (alternative) — Generate `docs/docusaurus/vercel.json`:
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "build",
     "installCommand": "npm ci",
     "framework": "docusaurus-2"
   }
   ```

3. **Netlify** (alternative) — Generate `docs/docusaurus/netlify.toml`:
   ```toml
   [build]
     command = "npm run build"
     publish = "build"
   [build.environment]
     NODE_VERSION = "20"
   ```

**Deployment choice (mode-aware):** Express — default to GitHub Pages, proceed. Standard+ — present deployment options via AskUserQuestion (default: GitHub Pages).

## 4.7 — Versioning Setup

Configure documentation versioning for API-versioned projects:

1. Set `current` version label in `docusaurus.config.js` as "Next" (development)
2. Document the versioning workflow in `Shipyard/technical-writer/writing-notes.md`:
   - Run `npm run docusaurus docs:version X.Y` to cut a version
   - Cut a docs version for each major API version
   - Default to latest stable, keep previous versions accessible
   - Archive versions older than N-2 major releases

## 4.8 — CHANGELOG (automation-driven, not hand-maintained)

The changelog is **bot-driven** (Governance & DX, Phase 3.11). Wire automation, do not ask humans to hand-edit:

- **release-please** (default) — `release-please-config.json` + `.release-please-manifest.json`, plus a `release-please` GitHub Actions workflow that opens/updates a release PR and writes `CHANGELOG.md` from Conventional Commits. OR **Changesets** — `.changeset/config.json` + a `changesets/action` workflow; contributors add a changeset file per change (the PR template enforces this).
- The generated `CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) sections (Added, Changed, Deprecated, Removed, Fixed, Security) — but the bot owns the entries.
- Add a header comment stating "Generated by <release-please|Changesets> — do not edit by hand; add a changeset / use Conventional Commits." A manual edit without a changeset fails the release check.

## Output Deliverables

| Artifact | Path |
|----------|------|
| Docusaurus config | `docs/docusaurus/docusaurus.config.js` |
| Sidebar config | `docs/docusaurus/sidebars.js` |
| Package manifest | `docs/docusaurus/package.json` |
| Babel config | `docs/docusaurus/babel.config.js` |
| Custom CSS | `docs/docusaurus/src/css/custom.css` |
| Landing page | `docs/docusaurus/src/pages/index.js` |
| CI pipeline (build + docs gates) | `.github/workflows/docs-build.yml` |
| Changelog (automation-driven) | `CHANGELOG.md` + `release-please-config.json`/`.release-please-manifest.json` OR `.changeset/config.json` |
| Deployment config | `docs/docusaurus/vercel.json` or `netlify.toml` (per user choice) |
| Writing notes (updated) | `Shipyard/technical-writer/writing-notes.md` |

## Validation Loop

Before marking the Technical Writer skill as complete:
- `npm run build` in `docs/docusaurus/` produces zero errors
- Sidebar navigation matches the actual documentation files (no broken links)
- Every documentation page is reachable from the sidebar
- Landing page renders with correct project name and working links
- CI pipeline YAML is valid; `docs:gen-check`, OpenAPI validation, metric-name lint, budget-ref lint, and broken-link gate are all present and exit non-zero on breach
- The pipeline references (not redefines) the devops-owned `docs-examples` job
- 'production-ready' block on failing docs gates is wired, with a logged 'accepted with justification' override path
- CHANGELOG.md is automation-driven (release-please / Changesets), not hand-edited
- Versioning configuration is documented in writing notes

## Quality Bar

- Documentation site builds cleanly with `onBrokenLinks: 'throw'`
- Sidebar categories match the 6 documentation sections (getting-started, architecture, api-reference, guides, operations, integrations)
- Search is configured (Algolia or local) — not silently omitted
- Deployment config targets at least one platform with working commands
- No hardcoded project-specific values that should be template variables
