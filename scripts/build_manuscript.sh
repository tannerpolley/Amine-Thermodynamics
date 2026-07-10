#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
latex_dir="$repo_root/docs/latex"
SOURCE_DATE_EPOCH="$(git -C "$repo_root" log -1 --format=%ct)"
export SOURCE_DATE_EPOCH
export FORCE_SOURCE_DATE=1

if ! command -v latexmk >/dev/null 2>&1; then
    echo "latexmk is required to build the manuscript." >&2
    exit 1
fi

cd "$latex_dir"
latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds main.tex

cd "$repo_root"
uv run python scripts/check_manuscript_freshness.py --write-receipt
