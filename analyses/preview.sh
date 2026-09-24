#!/usr/bin/env bash
set -euo pipefail

# Entry point of the installed mea-parameter-bundle-preview.service; the CSE
# manuscript preview owns the serving behavior.
cd "$(dirname "$0")"
exec python3 manuscript.py preview . \
  --host "${MEA_ANALYSES_HOST:-127.0.0.1}" \
  --port "${MEA_ANALYSES_PORT:-8770}"
