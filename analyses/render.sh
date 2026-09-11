#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
quarto render --no-clean --to html --no-execute
