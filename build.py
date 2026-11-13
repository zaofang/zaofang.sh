"""Render ZAOFANG(7) from content.toml as dist/index.html and dist/index.txt.

Marks and colours come from sibling clones: <src>/brand, <src>/yan, <src>/mandate.
"""

import argparse
import html
import json
import re
import shutil
import textwrap
from string import Template
import tomllib
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
WIDTH, INDENT = 72, 7


def svg(path: Path, fills: dict[str, str | None]) -> str:
    s = path.read_text()
    s = re.sub(r"<\?xml.*?\?>|<metadata>.*?</metadata>|<title>.*?</title>", "", s, flags=re.S)
    s = re.sub(r'\s(?:width|height)="[\d.]+"', "", s, count=2)
    s = re.sub(r'<rect[^>]*/>', "", s, count=1) if path.name == "typeon.svg" else s
    for hex_, var in fills.items():
        if var is None:
            continue
        if not re.search(f'fill="{hex_}"', s, flags=re.I):
            raise SystemExit(f"{path}: expected fill {hex_}; the mark changed, update build.py")
        s = re.sub(f'fill="{hex_}"', f'style="fill:var({var})"', s, flags=re.I)
    return s.strip()


def load(src: Path) -> dict:
    zf_fills = {"#F0E7D5": "--zf-text", "#F0A445": "--zf-accent", "#13242A": "--zf-on-accent"}
    md = json.loads((src / "mandate/assets/brand/tokens.json").read_text())
    yn = json.loads((src / "yan/site/brand/tokens.json").read_text())
    return {
        "tokens": (src / "brand/tokens/tokens.css").read_text(),
        "favicon": (src / "brand/logo/favicon.svg"),
        "lockup": svg(src / "brand/logo/lockup-on-dark.svg", zf_fills),
        "typeon": svg(src / "brand/motion/typeon.svg", zf_fills | {"#13242A": None}),  # ground rect is dropped
        "yan": svg(src / "yan/site/brand/lockup.svg", {}),
        "mandate": svg(src / "mandate/assets/brand/lockup-on-dark.svg",
                       {md["dark"]["ming"]: "--md-ming", md["dark"]["word"]: "--md-word"}),
        "plates": {
            t: {"--yn-bg": yn[t]["bg"], "--yn-text": yn[t]["text"], "--yn-tone": yn[t]["accent"],
                "--md-bg": md[t]["bg"], "--md-ming": md[t]["ming"], "--md-word": md[t]["word"]}
            for t in ("dark", "light")
        },
    }


def para(text: str) -> list[str]:
    return textwrap.wrap(text, WIDTH - INDENT, initial_indent=" " * INDENT, subsequent_indent=" " * INDENT)


def head(left: str, mid: str) -> str:
    gap = WIDTH - 2 * len(left) - len(mid)
    return left + " " * (gap // 2) + mid + " " * (gap - gap // 2) + left


def text(c: dict, today: str) -> str:
    out = [head("ZAOFANG(7)", "Workshop Manual"), "", "NAME", *para(c["name"]), "", "SYNOPSIS"]
    out += [" " * INDENT + s for s in c["synopsis"]]
    out += ["", "DESCRIPTION"]
    for p in c["description"]:
        out += [*para(p), ""]
    out += ["PROJECTS"]
    col = max(len(p["id"]) for p in c["projects"]) + 5
    for p in c["projects"]:
        lead = " " * INDENT + f"{p['id']}(1)".ljust(col)
        out += textwrap.wrap(f"{p['summary']} {p['url']}", WIDTH, initial_indent=lead, subsequent_indent=" " * len(lead))
    out += ["", "SEE ALSO", *[" " * INDENT + u for u in c["see_also"]], ""]
    foot = f"zaofang {today}"
    out.append(foot + " " * (WIDTH - len(foot) - len("ZAOFANG(7)")) + "ZAOFANG(7)")
    return "\n".join(out) + "\n"


def link(url: str) -> str:
    return f'<a href="{url}">{html.escape(url.removeprefix("https://"))}</a>'


def page(c: dict, a: dict, today: str) -> str:
    e = html.escape
    plates = {t: ";".join(f"{k}:{v}" for k, v in d.items()) for t, d in a["plates"].items()}
    marks = {"yan": f'<span class="plate yn">{a["yan"]}</span>', "mandate": f'<span class="plate md">{a["mandate"]}</span>'}
    projects = "".join(
        f'<div class="proj"><a href="{p["url"]}" aria-label="{p["id"]}">{marks[p["id"]]}</a><div>'
        f'<p class="pname">{p["id"]}<span>(1)</span></p><p>{e(p["summary"])}</p>'
        f'<p class="pfacts">{e(p["status"])} · {link(p["url"])}</p></div></div>'
        for p in c["projects"]
    )
    name, _, rest = c["name"].partition(" - ")
    return Template((HERE / "page.html").read_text()).substitute(
        tokens=a["tokens"], plates_dark=plates["dark"], plates_light=plates["light"],
        lockup=a["lockup"], typeon=a["typeon"], name=e(name), name_rest=e(rest),
        synopsis=e("\n".join(c["synopsis"])),
        description="".join(f"<p>{e(p)}</p>" for p in c["description"]),
        projects=projects, see_also=", ".join(link(u) for u in c["see_also"]), today=today,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=HERE.parent, help="directory holding brand/, yan/, mandate/ clones")
    ap.add_argument("--out", type=Path, default=HERE / "dist")
    args = ap.parse_args()
    c = tomllib.loads((HERE / "content.toml").read_text())
    a = load(args.src)
    today = date.today().isoformat()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "index.html").write_text(page(c, a, today))
    (args.out / "index.txt").write_text(text(c, today))
    shutil.copy(a["favicon"], args.out / "favicon.svg")


if __name__ == "__main__":
    main()
