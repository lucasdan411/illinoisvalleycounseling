# Deploy notes (Illinois Valley Counseling)

## Cloudflare Pages

- **Project name:** `illinois-valley-counseling`
- **GitHub repo / branch:** `lucasdan411/illinoisvalleycounseling` / `gh-pages`
- **Root directory (required):** `website`
- **Build command:** leave empty (static HTML)
- **Build output directory:** `/` (or blank; content is already the publish root inside `website/`)

The repository root contains pitch videos, strategy docs, and older assets. Those must **not** be the Pages publish root. Serving from repo root previously showed the pitch instead of the practice homepage.

## Soft 404s

Cloudflare Pages serves `404.html` for missing paths when that file exists at the publish root. `website/404.html` is included so unknown URLs return a real 404 instead of the homepage (SPA fallback).

If soft-404s persist after deploy, confirm in the Cloudflare dashboard that the project Root directory is still `website` and that a fresh deployment picked up `404.html`.

## Custom domains / DNS / Worker

- Apex: `illinoisvalleycounseling.com`
- `www` should continue redirecting to apex (do not change DNS/custom domains unless asked)
- Leave the Worker named `illinoisvalleycounseling` alone unless explicitly asked to change routing
