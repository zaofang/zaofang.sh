#!/bin/sh
# Cloudflare Pages build: fetch the marks and tokens, then render dist/.
set -eu
src=$(mktemp -d)
for repo in brand yan mandate; do
  git clone --quiet --depth 1 "https://github.com/zaofang/$repo" "$src/$repo"
done
python3 build.py --src "$src"
