# zaofang.sh

The Zaofang home page. One source, `content.toml`, renders to `dist/index.html` for browsers and `dist/index.txt` for terminals:

```sh
curl zaofang.sh
```

This is the interim page. The fuller ZAOFANG(7) manual version is in commit 32769e7.

## Build

```sh
sh build.sh             # uv run fetch.py && uv run build.py
uv run fetch.py --bump  # move the pinned repos to their HEAD; commit sources.lock
```

`sources.lock` pins the zaofang/brand commit (lockup, tokens, favicon) and the google/fonts commit and sha256 of DM Mono. `fetch.py` fetches exactly those into `.sources/`; nothing is copied into this repository. Brand changes reach the site only through a `sources.lock` bump.

The build subsets DM Mono to the characters on the page and serves it from `/fonts/` with its licence. It fails if `index.html` is over 14 KB gzipped.

## Deploy

Cloudflare Workers static assets, deployed by `.github/workflows/site.yml` on push to main. The `production` environment holds `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. `wrangler.jsonc` binds the custom domain zaofang.sh.

At `/`, `worker.js` sends `index.txt` when the `Accept` header prefers `text/plain` to `text/html`. When neither is preferred, as with curl's `*/*`, it sends text to curl, wget, HTTPie, xh and fetch by user agent, and HTML to everyone else. Terminals get the text over plain http; browsers, and every other path, are redirected to https.

## Edit

Change `content.toml` for words, `page.html` for layout.
