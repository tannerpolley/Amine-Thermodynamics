#!/usr/bin/env bash
# Write builds/fpe-latex-source.zip: the main manuscript as a flat LaTeX source that Editorial Manager can compile.
# EM cannot process archives with subfolders or two files sharing a base name (Aries EM LaTeX guide, 2025),
# so sections, tables and the bibliography are expanded into one .tex. Run after scripts/build_manuscript.sh.
set -euo pipefail
latex=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
cd "$latex"
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT

latexpand --expand-bbl builds/main.bbl main.tex | sed \
    -e 's#\\externaldocument\[supp-\]{builds/supplement}#\\externaldocument[supp-]{fpe-supplement}#' \
    -e '/\\graphicspath/d' -e '/\\bibliographystyle/d' > "$stage/fpe-manuscript.tex"
sed 's#\\RequirePackage{styles/cas-common}#\\RequirePackage{cas-common}#' styles/cas-sc.cls > "$stage/cas-sc.cls"
cp styles/cas-common.sty "$stage/"
cp builds/supplement.aux "$stage/fpe-supplement.aux"  # supplement labels for xr ("Table S3")
sed -n 's#^INPUT \(\./\)\?figures/generated/##p' builds/main.fls | sort -u | while read -r figure; do
    cp "figures/generated/$figure" "$stage/"
done

files=$(cd "$stage" && ls)
duplicates=$(printf '%s\n' $files | sed 's/\.[^.]*$//' | sort | uniq -d)
[[ -z "$duplicates" ]] || { echo "Files share a base name, which EM rejects: $duplicates" >&2; exit 1; }

# The flat source must reproduce the reviewed build word for word.
(cd "$stage" && for pass in 1 2 3; do pdflatex -interaction=nonstopmode -halt-on-error fpe-manuscript.tex >/dev/null; done)
if ! diff -q <(pdftotext -q builds/main.pdf -) <(pdftotext -q "$stage/fpe-manuscript.pdf" -) >/dev/null; then
    echo 'The flat source does not reproduce builds/main.pdf; rebuild with scripts/build_manuscript.sh first.' >&2
    exit 1
fi

rm -f builds/fpe-latex-source.zip
(cd "$stage" && touch -d "@$(git -C "$latex" log -1 --format=%ct)" $files && zip -q -X "$latex/builds/fpe-latex-source.zip" $files)
printf 'Wrote builds/fpe-latex-source.zip, %s files, sha256 %s\n' "$(printf '%s\n' $files | wc -l)" \
    "$(sha256sum builds/fpe-latex-source.zip | cut -d' ' -f1)"
