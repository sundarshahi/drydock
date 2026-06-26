# Drydock docs site

The documentation site for [Drydock](https://github.com/sundarshahi/drydock), built with [Docusaurus](https://docusaurus.io). Content lives in `docs/`; the landing page is `src/pages/index.tsx`.

## Local development

```bash
cd website
npm install
npm start          # dev server with hot reload at http://localhost:3000
npm run build      # production build into ./build (run this before deploying)
npm run serve      # preview the production build locally
```

## Deploy — Cloudflare Pages (recommended)

The site is configured for `https://drydock.sundarshahithakuri.com.np` (see `url` in `docusaurus.config.ts`). To deploy via Cloudflare Pages connected to this GitHub repo:

1. **Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git** → pick `sundarshahi/drydock`.
2. **Build settings:**
   - Framework preset: **Docusaurus** (or "None")
   - **Root directory:** `website`
   - **Build command:** `npm run build`
   - **Build output directory:** `build` (i.e. `website/build`)
   - Node version: `20` or newer (set `NODE_VERSION=20` as an env var if needed).
3. **Custom domain:** Pages → your project → **Custom domains → Set up a custom domain** → `drydock.sundarshahithakuri.com.np`. Since the apex domain is already on Cloudflare, it adds the `CNAME` record automatically.

Every push to `main` then rebuilds and deploys; pull requests get preview URLs.

> If you change the production URL, update `url` (and `baseUrl` if it's served from a subpath) in `docusaurus.config.ts`.
