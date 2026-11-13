"""Render zaofang.sh from content.toml as dist/index.html and dist/index.txt.

The lockup and colour tokens come from a clone of zaofang/brand.
"""

import argparse
import html
import re
import shutil
import tomllib
from datetime import date
from pathlib import Path
from string import Template

HERE = Path(__file__).parent
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


def page(c: dict, brand: Path, year: str) -> str:
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
        lines=lines, rows=rows, github=c["github"], github_label=e(c["github"].removeprefix("https://")), year=year,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", type=Path, default=HERE.parent / "brand", help="clone of zaofang/brand")
    ap.add_argument("--out", type=Path, default=HERE / "dist")
    args = ap.parse_args()
    c = tomllib.loads((HERE / "content.toml").read_text())
    year = str(date.today().year)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "index.html").write_text(page(c, args.brand, year))
    (args.out / "index.txt").write_text(text(c, year))
    shutil.copy(args.brand / "logo/favicon.svg", args.out / "favicon.svg")


if __name__ == "__main__":
    main()
