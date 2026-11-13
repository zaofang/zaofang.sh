#!/bin/sh
# Cloudflare Pages build: fetch the lockup and tokens, then render dist/.
set -eu
brand=$(mktemp -d)/brand
git clone --quiet --depth 1 https://github.com/zaofang/brand "$brand"
python3 build.py --brand "$brand"
