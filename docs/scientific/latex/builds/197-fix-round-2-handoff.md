# Issue 197 correction round 2

The two required science corrections, the optional logarithmic-average clarification, and story N1–N9 are applied. The parent owns confirming review and delivery. No push, mainline integration, GitHub comment, model calculation or parameter estimation was performed. The Quarto preview service and system browser were untouched.

Exact old/new excerpts with source locations are in `197-fix-round-2-excerpts.md`. `197-fix-round-2-numeric-check.json` compares the presentation with `ae15c4d`: every number in 380 table rows (including headers) across 21 generated files is unchanged after minus-sign normalization. No retained input changed in this round. Exact N2 adds a repeated 47; N1 adds Section S5; exact N8 adds the existing cost 148.9, Table 3, and counts 79/47, and removes state indices 0/41. These are the required non-formatting numeric-token differences, not value changes.

Science 2 overrides story N7's unscaled residual wording. N8 uses the reviewer's appended Table S2 text. The optional science phrase was inserted as “so, on logarithmic average, the model …”; the report supplied no complete replacement sentence. The native scope question returned “All N9 records” in Don't Ask mode: Neumann plus the nine formula titles were corrected through Zotero/Better BibTeX, rather than limiting the work to two records. Only those ten title overrides changed; the 54 citation keys and other semantic fields are unchanged. Exporter trailing commas are formatting. The source log gives the keys and export route.

The starting branch already contains issue #201 files from its mainline base. They were not used or edited: manuscript phase claims remain 313.15–333.15 K. No phase-extension result entered the manuscript.

Source commit: `05195cb`; exact excerpts and numeric evidence: `30bae41`; starting-point merge: `edd44a6`. Both PDFs use SOURCE_DATE_EPOCH `1792734244` from `30bae41`. Main build: `UV_PROJECT_ENVIRONMENT=/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv UV_NO_SYNC=1 nice -n 10 bash scripts/build_manuscript.sh`. Supplement: `SOURCE_DATE_EPOCH=1792734244 FORCE_SOURCE_DATE=1 nice -n 10 latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds supplement.tex` from the LaTeX directory.

- `main.pdf`: 22 pages; SHA-256 `9d933bac29124caaa4d82f2982dee19549fd2ecde8e341c56770e5bca827a814`.
- `supplement.pdf`: 14 pages; SHA-256 `cd46c55c3dd9a1934bef6c5d7a892b57a2b3920b7805691dba800213c8151c1e`.

Rendered abstract: 247 whitespace-delimited words after joining line-end hyphenation. ChemRxiv abstract: 240 words. Highlights: [82, 77, 72, 73, 79] characters. Companion claims remain synchronized.

Freshness: `Manuscript PDF is current`. CSE prose: `Prose check passed for plugin-wide and scoped rules.` Both builds and `git diff --check` exit 0. All 21 tables reproduce exactly without writes; the cited bibliography reproduces exactly using newly built auxiliary files. Build logs and `197-fix-round-2-build-checks.json` retain the check evidence.

Automated visual QA: main `fail`, 66 findings (61 tight-leading warnings, two math/graphic warnings, three overlap errors); supplement `review`, 68 warnings (57 tight-leading, 11 landscape-edge). The three errors are the pre-existing log-ratio superscript on main p.7 and rotated Figure 1 labels on p.11. All 36 pages were inspected as PNGs; the reported overlaps are visually separate. Corrected spans have no new clipping or unintended overlap. One existing supplement underfull paragraph warning remains; no undefined references, missing citations, overfull boxes or font substitutions occur. This manual disposition does not turn the automated result into a pass.
