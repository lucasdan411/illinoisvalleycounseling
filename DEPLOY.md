# Deploy notes (Illinois Valley Counseling)

## Cloudflare Pages

- **Project name:** `illinois-valley-counseling`
- **Live hosts:** `illinoisvalleycounseling.com`, `illinois-valley-counseling.pages.dev` (also `go.illinoisvalleycounseling.com`)
- **GitHub repo / branch (source of truth):** `lucasdan411/illinoisvalleycounseling` / `gh-pages`
- **Publish directory:** contents of `website/` (the practice site)

### Important: Direct Upload, not Git-connected

As of 2026-09-29 the Pages project has **no Git source** (`source: {}`). Pushing to `gh-pages` updates GitHub Pages / the repo, but **does not** automatically rebuild Cloudflare Pages.

To update production after commits:

```bash
wrangler pages deploy website \
  --project-name=illinois-valley-counseling \
  --branch=gh-pages \
  --commit-hash="$(git rev-parse HEAD)"
```

Optional later improvement: connect the GitHub repo in the Cloudflare dashboard (Root directory = `website`, production branch = `gh-pages`) so pushes auto-deploy. Do not change DNS or custom domains unless asked.

The repository root contains pitch videos, strategy docs, and older assets. Those must **not** be the Pages publish root. Serving from repo root previously showed the pitch instead of the practice homepage. Root `index.html` is a noindex stub that points at the apex site.

## Soft 404s

`website/404.html` is required so unknown paths return HTTP 404 instead of Cloudflare's SPA fallback (homepage with 200). Verified after deploy: random paths return 404 with the custom page.

## Custom domains / DNS / Worker

- Apex: `illinoisvalleycounseling.com`
- `www` should continue redirecting to apex (do not change DNS/custom domains unless asked)
- Leave the Worker named `illinoisvalleycounseling` alone unless explicitly asked to change routing
