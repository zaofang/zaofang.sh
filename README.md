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

Cloudflare Pages, connected to this repository:

| Setting | Value |
|---|---|
| Build command | `sh build.sh` |
| Output directory | `dist` |
| Environment variable | `PYTHON_VERSION=3.13` |

`functions/_middleware.js` sends `index.txt` to curl, wget, HTTPie and xh at `/`, and HTML to everyone else.

## Edit

Change `content.toml` for words, `page.html` for layout.
