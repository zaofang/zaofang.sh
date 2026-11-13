"""Fetch the inputs pinned in sources.lock into .sources/, or bump the pinned repos to HEAD."""

import argparse
import hashlib
import re
import subprocess
import tomllib
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
LOCK = HERE / "sources.lock"
OUT = HERE / ".sources"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def repo(name: str, url: str, commit: str) -> None:
    d = OUT / name
    if (d / ".git").exists() and git("-C", str(d), "rev-parse", "HEAD") == commit:
        return
    d.mkdir(parents=True, exist_ok=True)
    git("init", "-q", str(d))
    git("-C", str(d), "fetch", "-q", "--depth", "1", url, commit)
    git("-C", str(d), "checkout", "-q", "--force", "FETCH_HEAD")


def font(family: str, base: str, files: dict[str, str]) -> None:
    for name, sha in files.items():
        p = OUT / "fonts" / family / name
        if not (p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == sha):
            data = urllib.request.urlopen(base + name).read()
            if hashlib.sha256(data).hexdigest() != sha:
                raise SystemExit(f"{base}{name}: sha256 does not match sources.lock")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)


def bump(lock: dict) -> None:
    s = LOCK.read_text()
    for name, r in lock["repos"].items():
        head = git("ls-remote", r["url"], "HEAD").split()[0]
        s = re.sub(rf'(\[repos\.{name}\][^\[]*?commit = ")\w+', rf"\g<1>{head}", s)
        print(f"{name} {r['commit'][:7]} -> {head[:7]}")
    LOCK.write_text(s)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bump", action="store_true", help="move pinned repos to their remote HEAD")
    lock = tomllib.loads(LOCK.read_text())
    if ap.parse_args().bump:
        bump(lock)
        lock = tomllib.loads(LOCK.read_text())
    for name, r in lock["repos"].items():
        repo(name, r["url"], r["commit"])
    for family, f in lock["fonts"].items():
        font(family, f.pop("base"), f)


if __name__ == "__main__":
    main()
