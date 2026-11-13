"""Render zaofang.sh from content.toml as dist/index.html and dist/index.txt.

The lockup and colour tokens come from zaofang/brand, the font from google/fonts, both as pinned in
sources.lock and fetched by fetch.py.
"""

import argparse
import gzip
import hashlib
import html
import re
import shutil
import tomllib
from datetime import date
from pathlib import Path
from string import Template

from fontTools import subset

HERE = Path(__file__).parent
SOURCES = HERE / ".sources"
BUDGET = 14 * 1024  # gzipped HTML that fits the first round trip
FILLS = {"#F0E7D5": "--zf-text", "#F0A445": "--zf-accent", "#13242A": "--zf-on-accent"}


def lockup(path: Path) -> str:
    s = path.read_text()
    s = re.sub(r"<\?xml.*?\?>|<metadata>.*?</metadata>|<title>.*?</title>", "", s, flags=re.S)
    s = re.sub(r'\s(?:width|height)="[\d.]+"', "", s, count=2)
    for hex_, var in FILLS.items():
        if not re.search(f'fill="{hex_}"', s, flags=re.I):
            raise SystemExit(f"{path}: expected fill {hex_}; the mark changed, update build.py")
        s = re.sub(f'fill="{hex_}"', f'style="fill:var({var})"', s, flags=re.I)
    return s.strip()


def text(c: dict, year: str) -> str:
    col = max(len(p["id"]) for p in c["projects"]) + 3
    out = ["zaofang (造坊)", "", *c["lines"], ""]
    for p in c["projects"]:
        out += [p["id"].ljust(col) + p["summary"] + ", " + p["status"], " " * col + p["url"]]
    return "\n".join([*out, "", c["github"], year]) + "\n"


def font(src: Path, chars: str, out: Path) -> str:
    """Subset src to chars as woff2 in out; return its content-addressed file name."""
    opts = subset.Options(flavor="woff2", layout_features=[], name_IDs=[0, 1, 2, 3, 4, 5, 6], hinting=False)
    f = subset.load_font(src, opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=chars)
    sub.subset(f)
    tmp = out / "font.woff2"
    subset.save_font(f, tmp, opts)
    name = f"{src.stem.lower()}.{hashlib.sha256(tmp.read_bytes()).hexdigest()[:10]}.woff2"
    tmp.rename(out / name)
    return name


def page(c: dict, brand: Path, year: str, font: str) -> str:
    e = html.escape
    rows = "".join(
        f'<tr><td><a href="{p["url"]}">{e(p["id"])}</a></td><td class="d m">{e(p["summary"])}</td>'
        f'<td class="m">{e(p["status"])} <span aria-hidden="true">↗</span></td></tr>'
        for p in c["projects"]
    )
    lines = f'{e(c["lines"][0])}<br><span class="m">{"<br>".join(e(x) for x in c["lines"][1:])}</span>'
    return Template((HERE / "page.html").read_text()).substitute(
        tokens=(brand / "tokens/tokens.css").read_text(),
        lockup=lockup(brand / "logo/lockup-on-dark.svg"),
        font=font, lines=lines, rows=rows, github=c["github"], github_label=e(c["github"].removeprefix("https://")), year=year,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", type=Path, default=SOURCES / "brand", help="checkout of zaofang/brand")
    ap.add_argument("--out", type=Path, default=HERE / "dist")
    args = ap.parse_args()
    c = tomllib.loads((HERE / "content.toml").read_text())
    year = str(date.today().year)
    shutil.rmtree(args.out, ignore_errors=True)
    fonts = args.out / "fonts"
    fonts.mkdir(parents=True)
    txt = text(c, year)
    mono = SOURCES / "fonts/dm-mono"
    index = page(c, args.brand, year, font(mono / "DMMono-Regular.ttf", txt, fonts))
    shutil.copy(mono / "OFL.txt", fonts / "OFL.txt")
    (args.out / "index.html").write_text(index)
    (args.out / "index.txt").write_text(txt)
    (args.out / "_headers").write_text("/fonts/*.woff2\n  Cache-Control: public, max-age=31536000, immutable\n")
    shutil.copy(args.brand / "logo/favicon.svg", args.out / "favicon.svg")
    size = len(gzip.compress(index.encode(), 9))
    print(f"index.html {size} B gzipped, budget {BUDGET} B")
    if size > BUDGET:
        raise SystemExit("index.html is over the size budget")


if __name__ == "__main__":
    main()
