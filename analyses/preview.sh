#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
exec quarto preview \
  --port "${MEA_ANALYSES_PORT:-8770}" \
  --host "${MEA_ANALYSES_HOST:-127.0.0.1}" \
  --no-browser \
  --no-navigate \
  --timeout "${MEA_ANALYSES_TIMEOUT:-0}" \
  --render html \
  --no-clean
