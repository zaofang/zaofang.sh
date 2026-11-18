# zaofang.sh

The Zaofang home page. One source, `content.toml`, renders to `dist/index.html` for browsers and `dist/index.txt` for terminals:

```sh
curl zaofang.sh
```

This is the interim page. The fuller ZAOFANG(7) manual version is in commit 32769e7.

## Build

The lockup and colour tokens are read from a clone of zaofang/brand, never copied in.

```sh
uv run build.py --brand ../brand
sh build.sh                       # clones zaofang/brand to a temp dir first
```

## Deploy

Cloudflare Workers static assets, deployed by `.github/workflows/site.yml` on push to main (and every 6 hours, to pick up brand changes). The `production` environment holds `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. `wrangler.jsonc` binds the custom domain zaofang.sh.

`worker.js` sends `index.txt` to curl, wget, HTTPie, xh and fetch at `/`, HTML to everyone else, and redirects plain http to https.

## Edit

Change `content.toml` for words, `page.html` for layout.
