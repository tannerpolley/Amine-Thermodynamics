# Manuscript handoff: DEA refit with F2 carbamate inputs (#413)

For the Writer after owner confirmation. No file under `docs/scientific/latex`
was changed by #413. The old values are from `analyses/dea_transfer/results/retransfer-398/`.
The new values are from `analyses/dea_transfer/results/refit-413/`. Every table
value below was produced by running `scripts/dea_displays.py` with the reader
changes in step 1 in a scratch checkout. The regenerated outputs were diffed
against the current files. Before that change, a scratch run at `f30977a32`
regenerated every display identically.

## 1. Reader changes in `scripts/dea_displays.py`

- Line 18: `BASE = 'analyses/dea_transfer/results/refit-413/'`.
- Lines 121, 135 and 583: the model label `'05e94210'` becomes `'F2-carbamate'`.
  In `refit-413`, the CSV model labels are `F2-carbamate` (this fit) and `F0-carbamate` (the #398 fit, replayed).
- Lines 393–398 and 410: read fit `F2` instead of `F0` for the DEA carbamate.
  Add `f2 = {... if r['fit'] == 'F2'}` and use `f2` in the two asserts and in `origins`.
  Keep `f0` for the AMP lines (430, 609); AMP belongs to #412.
- Line 393 comment and line 439 origin label: `\ce{MEACOO-}, 16-parameter calibration`
  for the DEA dispersion energy becomes the MEA-model wording the Writer chooses.
  Line 431 (AMP) stays unless #412 changes it.
- The table note `b` at line 413, "Dispersion energy of \ce{MEACOO-} in the
  16-parameter calibration and its diameter scaled to DEA", needs the same
  wording change. Note `g` (AMP) belongs to #412.

Then run `dea_displays.py`, followed by `dea_displays.py --check`.

## 2. Generated tables and figure (regenerate; values for checking)

| File | Quantity | Old (#398, F0 carbamate) | New (#413, F2 carbamate) |
| --- | --- | ---: | ---: |
| `tables/amine-summary.tex` | DEA fitted pressure AARD (30), both columns | 28.46 | 28.51 |
| `tables/amine-summary.tex` | DEA not-fitted pressure AARD (67) | 54.19 | 53.92 |
| `tables/transfer-fitted.tex` | $k_{\mathrm{DEACOO^-,w}}$ (SE) | −0.039 (0.054) | −0.048 (0.054) |
| `tables/transfer-fitted.tex` | R4 $A_4$ (SE) | 5.869 (0.615) | 5.883 (0.618) |
| `tables/transfer-fitted.tex` | R4 $\delta h$ SE (J/mol) | 1346 | 1344 |
| `tables/transfer-species.tex` | \ce{DEACOO-} $\sigma$, $u/k_B$, $d^{\mathrm{Born}}$ | 6.1672, 183.0006, 6.1672 | 6.1997, 179.8579, 6.1997 |
| `tables/supplement-transfer-parameters.tex` | $k_{\mathrm{DEAH^+,w}}$ | −0.188256471177024 | −0.18834282671276725 |
| same | $k_{\mathrm{DEACOO^-,w}}$ | −0.03854869916071153 | −0.0477314406219579 |
| same | R4 $A_4$ | 5.86941067321772 | 5.883485367291507 |
| same | R4 $B_4$ (K) | −2660.2065169161024 | −2661.435714463442 |
| same | \ce{DEACOO-} Born, Debye–Hückel and segment diameter (Å) | 6.167209298821595 | 6.199663980008535 |
| same | \ce{DEACOO-} packing diameter (Å) | 5.427144182963003 | 5.4557043024075105 |
| same | \ce{DEACOO-} $u/k_B$ (K) | 183.00063128808972 | 179.85787428794876 |
| `tables/supplement-transfer-bounds.tex` | R4 $A_4$ bounds | 4.189, 10.189 | 4.192, 10.192 |
| same | R4 $\delta h$ bounds (J/mol) | −18021, 21979 | −18032, 21968 |
| `tables/supplement-transfer-data.tex` | AARD / bias (%): Lawson fitted | 28.46 / −0.66 | 28.51 / −0.65 |
| same | Carson fitted | 0.95 / −0.12 | 0.94 / −0.12 |
| same | Lawson 394.26 K | 23.12 / −23.12 | 22.95 / −22.95 |
| same | Seo and Hong | 84.95 / 83.09 | 85.36 / 83.59 |
| same | Lal | 47.94 / −31.63 | 47.41 / −30.30 |
| same | Weiland (density) | 0.63 / −0.38 | 0.70 / −0.47 |
| same | Lawson 50–54.5 wt% | 37.79 / −20.77 | 38.73 / −20.03 |
| same | Böttinger DEA + DEAH⁺ | 7.46 / −7.30 | 7.48 / −7.33 |
| same | Böttinger carbamate | 59.21 / 58.35 | 59.20 / 58.34 |
| same | Böttinger bicarbonate | 33.08 / −33.08 | 33.21 / −33.21 |
| `tables/supplement-dea-ranges.tex` | R5 in/out AARD: Lawson | 46.91 / 22.85 | 46.97 / 22.89 |
| same | Carson (out) | 0.95 | 0.94 |
| same | Lawson 394.26 K (out) | 23.12 | 22.95 |
| same | Seo and Hong in/out | 31.13 / 109.41 | 31.98 / 109.62 |
| same | Lal in/out | 56.30 / 42.68 | 55.79 / 42.13 |
| same | Weiland (out) | 0.63 | 0.70 |
| same | Lawson 50–54.5 wt% (in, out, R4 in) | 28.96, 43.67, 31.27 | 29.39, 44.96, 32.83 |
| same | Böttinger rows | changes of at most 0.14 points | see regenerated table |
| `figures/generated/dea-current-measured-model.pdf` | model curves | #398 | regenerated from `refit-413/curve-data.json` |
| `tables/number-sources.json` | source hashes | `retransfer-398/*` | `refit-413/*` |

Unchanged in the generated displays: Cai (40.82 %), Horstmann (+1,313 J/mol mean
signed error; binary, no reactions), the cation–water SE (0.0035), the R4 $A_4$ /
$k_{\mathrm{DEACOO^-,w}}$ correlation (0.974), the stability counts
(1,271 states, 1 unavailable, 0 splits) and the 4 fitted parameters with 0 on a bound.

## 3. Hand-written text

| File:line | Old | New | Source |
| --- | --- | --- | --- |
| `supplement.tex:204` | `\SI{183.0006}{\kelvin}, is that of \ce{MEACOO-} in the 16-parameter calibration of the main text` | `\SI{179.8579}{\kelvin}`, that of \ce{MEACOO-} in the MEA model (fit F2); wording is the Writer's | `refit-413/parameter-values.csv`; MEA `reduced-refit/parameter-details.csv` F2 |
| `supplement.tex:204` | `the \ce{MEACOO-} diameter of that calibration, \SI{5.3200}{\angstrom}, multiplied by 1.1593` | `\SI{5.3480}{\angstrom}`, MEA-model diameter; factor 1.1593 unchanged | same |
| `sections/transfer_results.tex:74` | `15.4--84.9\,\%` | `15.4--85.4\,\%` (largest not-fitted set: Seo and Hong, 85.36 %) | `refit-413/group-deviations.csv` |
| `sections/conclusion.tex:9` | `15.4--84.9\,\%` | `15.4--85.4\,\%` | same |

Checked and unchanged: `main.tex:95` and the highlights (DEA fitted pressures 28.5 %),
`transfer_results.tex:11` (Cai 40.8 %), `transfer_results.tex:14` (correlation 0.974),
and the supplement's 1.1593 size ratio. `transfer_results.tex:123` and
`supplement.tex:206` refer to the 16-parameter calibration for shared parameters
and for AMP. #413 does not change them, but after #412 the Writer should check
whether any amine still uses F0.

The `stated` assertion list in `dea_displays.py` (lines 624–631) will fail until
`transfer_results.tex`, `conclusion.tex` and `supplement.tex` carry the new strings above.
