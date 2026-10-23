# Issue 197 review correction round

All eight required science corrections and story R1–R16 are applied. The phase-test scope remains 313.15–333.15 K and loading 10⁻⁵–0.5. No retained result, selected parameter, fit or issue #201 result was changed or added. The parent owns the confirming review and merge. No push, integration into main or GitHub comment was made.

| Review item | Disposition |
|---|---|
| Science 1: Neumann fitting role | Applied verbatim in the table generator: three reaction laws refitted; binary and ternary data inform the reducing parameter. |
| Science 2: Jakobsen temperatures | Applied: 293.15/313.15 K. |
| Science 3: Kiepe endpoints | Applied: 313.20–393.17 K. |
| Science 4: six-source range | Applied: 313.00–393.15 K. |
| Science 5: ionic caloric functions | Applied verbatim: six functions, five reaction constraints, minimum-norm charge-reference convention. |
| Science 6: Téllez-Arredondo limits | Applied verbatim: Table 2/Figure 8 reach 393.15 K; Section 4.3.3 says 366.68 K. |
| Science 7: Figure 1 annotation | Applied verbatim; science overrides story R5. Shapes identify phase classification only for the restricted-bound fit. |
| Science 8: density cross-reference | Applied Table S1; compatible story R3 grammar also applied. The following sentence is capitalized. |
| Story R1: abstract | Applied verbatim; identifies the predicted second liquid phase before the phase-range limit. |
| Story R2: one fit name | Applied throughout the named prose, captions, supplement and submission aids. |
| Story R3: damaged density sentence | Applied verbatim with Table S1. |
| Story R4: caption generator and typography | Applied capitalization, Vapor, Debye–Hückel, Born and reference-density names through the generator. |
| Story R5: duplicate state and Figure 1 caption | Applied duplicate-state wording and plotted 72-state grid. Shape clause follows science 7. |
| Story R6: results opening and remaining instabilities | Applied verbatim, including the three lower-temperature states and Table S10. |
| Story R7: scientific question and finite-search meaning | Applied verbatim. |
| Story R8: definitions, lingo and R5 notation | Applied. The 375 states are identified from the retained state-targets file; R5 coefficients carry A5/B5/C5 notation. |
| Story R9: results wording | Applied, including removal of the overlapping high-temperature pressure statistic and source-specific bias statement supported by Table S3. |
| Story R10: transfer wording | Applied concentration and permittivity wording; material transfer remains in the phase method. |
| Story R11: figure labels and fill convention | Applied in the figure generator: linear Wagner axes, filled/open deviation markers, density-error label and Arcis selection check. |
| Story R12: main tables | Applied through the generator: readable rows, nondegenerate ranges, true minus signs and source-conversion notation. |
| Story R13: supplement | Applied: duplicate inventory removed; readable labels; caloric, water-law, association and permittivity names corrected. |
| Story R14: availability | Applied verbatim; duplicate submission sentence removed. |
| Story R15: bibliography | Applied through Zotero metadata and the approved export/cited-entry generator; no project-snapshot hand edit. |
| Story R16: highlight | Applied verbatim; all five highlights are within 85 characters. |

Science 7 versus story R5 is the only conflict. Science wins, as instructed. Science 8 and story R3 are compatible: both cite Table S1; story R3 repairs the grammar. Removing the duplicate inventory renumbers Sections S9/S10 to S8/S9 and Tables S14/S15/S16 to S13/S14/S15. Main-text and generated-table references follow the new numbering. The water exponential coefficients retain their values and use symbols defined in the supplement equation.

## Build and checks

Source commits precede the build: `7a7c890` (corrections) and `0a3e24f` (numeric comparison). Both PDFs use SOURCE_DATE_EPOCH 1792731498 from `0a3e24f`. Build commands:

```bash
UV_PROJECT_ENVIRONMENT=/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv UV_NO_SYNC=1 nice -n 10 bash scripts/build_manuscript.sh
SOURCE_DATE_EPOCH=1792731498 FORCE_SOURCE_DATE=1 nice -n 10 latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds supplement.tex
```

The existing main-checkout Python environment supplies Matplotlib. No package was installed or model calculation run. No browser or Quarto preview service was opened, started, stopped or restarted.

| Output | Pages | SHA-256 |
|---|---:|---|
| main.pdf | 22 | 9c765cff6ba65a1368ef151616fd6beb1b58043d7a80a47edccd5d2ff1e806ed |
| supplement.pdf | 14 | 7cbeb90fed6713a426a2eb55474aa227fb70bdd07a3c407261cb0fbbb3399228 |

The rendered abstract has **248 whitespace-delimited words**, after joining line-end hyphenation. The synchronized ChemRxiv abstract has 241 words; separate percentage/unit/punctuation tokens in the PDF extraction explain the difference. Highlight character counts are **82, 77, 72, 73, 79**. Cover-letter claims, ChemRxiv and highlights are synchronized.

The numeric comparison against `703fb86` has **14 files with numeric changes, zero unresolved additions, and 298 unchanged numerical table rows checked** outside the two review-corrected domain/attribution tables. The retained result and data directories have no diff. Full details are in `197-fix-round-numeric-check.json` and its Markdown explanation. Generator guards passed for all 307 quantities, selected parameter identity, property reductions and 73 paired states. Focused checks passed for degenerate ranges, distinct Aronu concentrations, R5 labels and minus signs.

The bibliography has 54 unchanged citation keys, 32 corrected title fields and one removed Chase address field; no other semantic field changes or local attachment paths. The source workflow corrected 33 Zotero records and regenerated the canonical export before the cited subset. The source log records the route and Better BibTeX documentation.

- Main and supplement latexmk builds: exit 0; no undefined references/citations, missing citations, overfull boxes or font substitutions. One supplement underfull box (lines 77–81) does not clip or obscure content.
- Manuscript freshness: `Manuscript PDF is current: docs/scientific/latex/builds/main.pdf (9c765cff6ba65a1368ef151616fd6beb1b58043d7a80a47edccd5d2ff1e806ed)`.
- CSE prose checker: `Prose check passed for plugin-wide and scoped rules.`
- `git diff --check`: exit 0.
- Automated visual QA reports main **fail**, 202 bounding-box findings (196 tight-leading warnings, three math/rule warnings and three overlap errors); supplement **review**, 99 findings (88 tight-leading and 11 landscape-edge warnings). The overlap errors are the log-ratio superscript on main page 7 and the two multiline rotated Figure 1 labels on page 11. These are visually separate. Math/rule warnings on pages 3–4 concern intentional fractions/brackets; supplement edge warnings concern the landscape correlation page 8. All 36 pages were rendered to PNG and viewed at 130 dpi; no actual overlap, clipping or unreadable changed labels was found. `197-fix-round-build-checks.json` retains the complete findings and disposition.

PDFs and render/check logs remain locally under `builds/` and `tmp/fix-197/`. `submission_metadata.yml` contains the new main PDF hash; the tracked `builds/verification-receipt.json` is staged with `git add -u`. Parent confirmation and authorized integration remain open.
