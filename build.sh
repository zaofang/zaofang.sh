#!/bin/sh
# Site build: fetch the inputs pinned in sources.lock, then render dist/.
set -eu
uv run fetch.py
uv run build.py
