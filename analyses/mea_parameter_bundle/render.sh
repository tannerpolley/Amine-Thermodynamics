#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
if [[ "${1:-}" != "notebook.qmd" || "$#" -gt 2 || ( "$#" == 2 && "$2" != "--working-copy" ) ]]; then
  echo "Usage: bash render.sh notebook.qmd [--working-copy]" >&2
  exit 2
fi
working_copy="${2:-}"
if [[ -z "$working_copy" ]]; then
  render_inputs="$(uv run python scripts/result_freshness.py --fingerprint)"
fi

runtime_root="$(mktemp -d "${TMPDIR:-/tmp}/cse-quarto.XXXXXX")"
trap 'rm -rf "$runtime_root"' EXIT

export TEXMFVAR="$runtime_root/tex"
export TEXMFCACHE="$TEXMFVAR"
export QUARTO_CACHE_DIR="$runtime_root/quarto"
export DENO_DIR="$runtime_root/deno"
export XDG_CACHE_HOME="$runtime_root/xdg"

for directory in "$TEXMFVAR" "$QUARTO_CACHE_DIR" "$DENO_DIR" "$XDG_CACHE_HOME"; do
  mkdir -p "$directory"
  [[ -w "$directory" ]] || {
    echo "CSE Quarto render failed: runtime directory is not writable: $directory" >&2
    exit 1
  }
done

# Keep --no-execute last: neither mode can run document code.  The project
# render list builds the overview and each study page as one synchronized site.
pages=(notebook neutral-mea-water/index ionic-speciation-fit/index \
    co2-r4-calibration/index reaction-temperature-fit/index \
    born-permittivity/index calorimetry/index \
    coupling-and-identification/index association-topology/index \
    historical-designs/index)
legacy_pages=(neutral-mea-water ionic-speciation-fit co2-r4-calibration \
    reaction-temperature-fit born-permittivity calorimetry \
    coupling-and-identification association-topology historical-designs)
# Stale page-navigation HTML can be recursively embedded by Pandoc.
for page in "${pages[@]}" "${legacy_pages[@]}"; do rm -f -- "$page.html"; done
rm -rf -- _site
quarto render --no-execute

# Keep the user-facing local entry point beside the Quarto sources. The site
# build is the source of truth; these copied HTML files make the existing
# file://notebook.html bookmark and sibling-page links work without a server.
for page in "${pages[@]}"; do
  mkdir -p -- "$(dirname -- "$page.html")"
  cp "_site/$page.html" "$page.html"
done
rm -r -- _site
if [[ -z "$working_copy" ]]; then
  uv run python scripts/result_freshness.py --stamp-notebook --expected-fingerprint "$render_inputs"
else
  echo "Working HTML rendered; numerical publication was not certified."
fi
