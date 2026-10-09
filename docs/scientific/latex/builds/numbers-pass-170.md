# FPE numbers pass: build and accounting (2026-10-08)

Done locally on `t3code/fpe-manuscript-restructuring-approved-acfbca97`. Merge commit `0c969b9` integrates evidence branch `398c1d3` into restructuring `22d03fe` without conflicts. Retained results and notebook are byte-identical to the evidence branch; no model calculation was run.

## All 128 entries

`numbers-pass-170.csv` records each original row, paragraph locators and disposition: **53 updated, 46 verified unchanged, 29 removed**. Of the removals, 28 belong to the unavailable decomposition (including its unchanged methodological counts/thresholds), and one is the obsolete public-deposit commit assertion, replaced by pending delivery. Source/basis/historical counts remain unchanged where the reviewed table says they are unchanged. Translated F1 density values refer to the four calibration states at 0.100 MPa; the supplement explicitly separates uncorrected EOS density calculations at 101325 Pa.

Removed: Born activity-sum decrease, activity/speciation cancellation, intermediate-loading mechanism, 0.08 offset fraction, H1–H3 conclusions, N1–N9 decomposition checks, decomposition figure and table, and the Matin-pool reversal claim. Narrowed: Born-off result to the tested model/bounds/objective/two starts; pressure comparability between Born forms; slope uncertainty to conditional precision; heat/pressure change to this parameterization without a unique chemistry cause. Density is calibration, and provenance is labeled as the fitting stage.

## Outputs

| File | Pages | SHA-256 |
| --- | ---: | --- |
| `main.pdf` | 20 | `f62e50b64a97ccd124a456defb69932885834d9b9ba4ab2de9c0a25bd0e1d2bb` |
| `supplement.pdf` | 16 | `3de08958fbcb594d8070503012dac7d8f52893669c4ec2a3ab880109f134856a` |

Main input SHA-256 from the freshness check: `9cbf8d3e2ee64c06f204594f14bb80d19489a8e03a7b11613c22b4d5e42c28cd`.

Abstract: **223 whitespace-delimited words in the synchronized submission text; 224 after extracting the rendered PDF and joining line-break hyphenation**. Both are below 250. TeXcount on the isolated TeX abstract reports 211 because its default rules omit some macro content. Highlight lengths: **80, 70, 79, 77, 77** characters, including spaces; all are at most 85.

Both builds ran through `agent-heavy --max 3G --timeout 10m`: `scripts/build_manuscript.sh` for the main file and `latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds supplement.tex` from the LaTeX directory. Final logs contain no undefined citation/reference, duplicate label, overfull box or LaTeX error. The manuscript freshness check passes. The initial supplement alignment error was corrected in the table generator; the redundant start-difference column was removed to fit the six-fit table, with its maximum retained in Section S5. Float barriers keep the Methods tables and the translated-density table within their section boundaries.

## Figures and visual inspection

Pressure, speciation and pool figures were regenerated, and the integral-heat figure was added, using the existing renderer and current retained values. Observations and model values are markers at measured states, with pressure in kPa, species as mole fraction and heat in kJ/mol CO2. The heat figure shows fitted Vinjarapu, predicted Arcis and the matched no-heat F1.

| Figure | SHA-256 |
| --- | --- |
| `heat-of-absorption.pdf` | `9938a0f81ba4fd70cd8bfe57c58ae13dfe3fad1a8af5bf90ae15a37ac61a5a35` |
| `pool-effect.pdf` | `01d131a5920338681840cd5ba678b78b11e83eb37c0f55d865c1b7ebacf84463` |
| `pressure.pdf` | `4cadcf12967c559fbcb6c98eaf1589e93febba8ca69d6ce773681029c3518385` |
| `speciation.pdf` | `bbce5d16e8fce8d19559ead2f1566c0ee77a5af1bcf4da2f06a6db6376a5614d` |

Every page was inspected in color at 110 dpi, including the landscape inventory. Grayscale page contact sheets and all four figure pages were inspected. Changed pages were re-inspected after layout corrections. No clipping or unintended overlap was found.

The conservative geometry reports are retained in `visual-qa/main/report.json` and `visual-qa/supplement/report.json`; their raw results are **fail** and **review**, respectively. Manual disposition: the two main-page-8 text-overlap errors are bounding-box overlap of mathematical superscripts/subscripts in the residual denominator and AARD expression, without glyph collision. Text/graphic warnings concern fraction rules and heat-figure legend markers; the remaining main warnings concern tight but clear template spacing. Supplement page-edge warnings arise from rotated landscape-page coordinates, with ordinary spacing warnings elsewhere. None denotes an observed layout defect. These raw findings are retained rather than reported as an automated pass.

## Focused checks and limits

All six fit target counts and pressure/species/heat cost sums agree with retained values. Rounded source/observable AARDs reproduce each fit's pressure/species family AARD within 0.0051 percentage points. Plot assertions verify all 18 pool rows, and the translated-density table verifies exactly four calibration states. Paragraph identifiers are unique within their source files; removed labels and claims are absent. The CSE prose checker passes. No new persistent tests were added for presentation edits.

Change accounting against merge `0c969b9`: two executable presentation files, **93 added / 96 removed lines**. No Engine or scientific result files changed. The only numerical evidence remains the reviewed calibration, conditional predictions and numerical verification. This pass does not establish physical validation, concentration transfer, high-temperature qualification or absorber/stripper suitability.

## Owner follow-up

No scientific input decision remains for this implementation. Independent final manuscript evidence/prose review remains pending, followed by the public deposit or immutable manuscript tag, source archive, preprint update and journal submission. The data statement remains marked pending. No push, PR, tag, release or submission was performed; the bibliography snapshot is unchanged.
