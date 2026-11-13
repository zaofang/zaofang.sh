# zaofang.sh

The Zaofang home page. One source, `content.toml`, renders to `dist/index.html` for browsers and `dist/index.txt` for terminals:

```sh
curl zaofang.sh
```

This is the interim page. The fuller ZAOFANG(7) manual version is in commit 32769e7.

## Build

```sh
uv run fetch.py         # inputs pinned in sources.lock, into .sources/
uv run build.py         # dist/
uv run fetch.py --bump  # move the pinned repos to their HEAD; commit sources.lock
```

`sources.lock` pins the zaofang/brand commit (lockup, tokens, favicon) and the google/fonts commit and sha256 of DM Mono. Nothing is copied into this repository. The build subsets DM Mono to the characters on the page and self-hosts it under `/fonts/` with its licence. The build fails if `index.html` is over 14 KB gzipped.

## Serve

A Cloudflare Worker (`worker.js`) in front of static assets (`dist/`), deployed by `.github/workflows/site.yml` on every push to main.

At `/` it sends `index.txt` when the `Accept` header prefers `text/plain` to `text/html`. When neither is preferred, as with curl's `*/*`, it sends text to curl, wget, HTTPie and xh by user agent, and HTML to everyone else. Terminals get the text over plain http; browsers, and every other path, are redirected to https.

### Cloudflare setup

1. My Profile, API Tokens, Create Custom Token, named for this repository only. Permissions: Account, Workers Scripts, Edit; Account, Account Settings, Read; Zone, Workers Routes, Edit. Resources: this account, and the zaofang.sh zone only. Do not use the "Edit Cloudflare Workers" template; it also grants account-wide R2 and KV edit.
2. This repository, Settings, Environments: create `production`, set deployment branches to `main` only, and add the secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` there, not as repository secrets. Only the deploy job, on main, can read them.
3. Remove zaofang.sh from the custom domains of the old Pages project `zaofang-sh`, then delete that project.
4. zaofang.sh zone, SSL/TLS, Edge Certificates: turn off Always Use HTTPS. The Worker redirects browsers itself.
5. Run the workflow on main. `wrangler deploy` attaches the custom domain zaofang.sh.

## Edit

Change `content.toml` for words, `page.html` for layout.
