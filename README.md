# zaofang.sh

ZAOFANG(7), the Zaofang home page. One source, `content.toml`, renders to `dist/index.html` for browsers and `dist/index.txt` for terminals:

```sh
curl zaofang.sh
```

## Build

Marks and colours are read from clones of zaofang/brand, zaofang/yan and zaofang/mandate, never copied in.

```sh
uv run build.py --src ..   # expects ../brand, ../yan, ../mandate
sh build.sh                # clones them to a temp dir first
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

Change `content.toml` for words, `page.html` for layout. The page follows the Zaofang brand (Lamplight tokens, Newsreader, Geist, DM Mono); projects keep their own identities.
