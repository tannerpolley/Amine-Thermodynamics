# Baygi 2015: neutral parity and a like-for-like pCO2 comparison

Reproduction workflow for the Baygi and Pahlavanzadeh 2015 parameter tables and neutral ePC-SAFT parity
(`render_figures.py`, unchanged), extended on 2026-09-29 with a pCO2 comparison of the Baygi model against our
refit C_src on our 161 canonical 30 wt % rows (Refs #68, #10). Nothing here adopts a parameter set or changes a
selected record.

## Commands

```bash
uv run python analyses/paper_validation/2015_baygi/scripts/render_figures.py              # neutral parity (retained tables)
uv run python analyses/paper_validation/2015_baygi/scripts/digitize_curves.py             # three published figures -> data/digitized
uv run python analyses/paper_validation/2015_baygi/scripts/compute_pco2_comparison.py     # about 4 min, one process
uv run python analyses/paper_validation/2015_baygi/scripts/check_pure_mea_saturation.py   # Table 2 convention check
uv run python analyses/paper_validation/2015_baygi/scripts/render_pco2_comparison.py      # figures
```

`evaluate_c_src_grid.py` needs the pinned Engine wheel `f66d972c…` (the `MEA-Thermodynamics-calibration-misfit`
environment had it; the main checkout's environment does not) and takes 25 s. The other scripts need `pcsaft`,
which that environment lacks.

## Baygi model as implemented

`scripts/baygi_model.py`:

1. **Chemistry:** the repo's ideal Smith-Missen solver (`MEA.smith_missen.ideal_speciation`), activity = mole
   fraction for all nine species, R1-R5 of Table 4, MEA 30 wt % unloaded, loading from Eqs. 14-16.
2. **Phase equilibrium:** PC-SAFT on the pseudo-ternary CO2, MEA (3B), water (4C) liquid, bubble pressure at the
   row temperature; p_CO2 = P y_CO2. Table 2 parameters; k_ij(MEA-water) = -0.0520; k_ij(CO2-water) = k_ij(CO2-MEA) = 0.
3. **Bubble pressure:** `pcsaft.flashTQ`, and where it fails (above a few MPa) a pressure scan and root find on
   ln sum(x_i K_i). The two agree to 1e-9 (relative) on the rows where both work.

Locators (Zotero B8EJJPCJ, PDF attachment JWH69DKG, sha256 `7e8e7757…2365`; Markdown `literature/Baygi2015--ICDS2PAA.md`;
PDF page numbers, not journal pages):

| item | PDF page | checked |
|---|---|---|
| Table 2, pure parameters (MEA 3B/4C/2B, water 4C/2B, CO2) | 4 | Markdown = PDF = `data/processed/baygi_table2_pure_parameters.csv` |
| Table 3, k_ij(MEA 3B, water 4C) = -0.0520 | 4 | Markdown = PDF; also the Fig. 6 caption (p. 7) and section 3.3 (p. 9) |
| Section 3.3 (no regression; CO2-water and CO2-MEA k_ij = 0; a_i = x_i; ion pairs neglected) | 9-10 | read in both |
| Fig. 1 (only molecules enter PC-SAFT; ions only in Smith-Missen) | 2 | image read |
| Table 4, R1-R5 constants | 8 | Markdown = PDF, one difference (below) |
| Eqs. 14-18, mass balances, ln K form, molality conversion | 10 | Markdown = PDF |
| Table 5, published AARD | 8 | Markdown = PDF; footnote b: AAD % = 100/np sum abs(p_exp - p_cal)/p_exp |
| Fig. 9, Fig. 11 | 9 | images from the sibling packet `ePC-SAFT-project/analyses/reproduction/2015-baygi/figures/figure-09, figure-11/source` |

## Choices where the paper is ambiguous

1. **Ions in the PC-SAFT step (the main one).** Fig. 1 keeps ions out of the EOS but does not say what happens to
   their moles. The paper follows Nasrifar and Tafazzol 2010 for a_i = x_i; that paper (PDF page 8, the paragraph on an
   "effective water mole fraction", read in the Zotero PDF `3G4FGGY4`) keeps the molecular CO2 and MEA moles and
   lumps the ionic moles with water. **Used:** that (`ions="water"`: x = x_CO2, x_MEA, 1 - x_CO2 - x_MEA of the true
   speciation). **Sensitivity kept:** dropping the ions and renormalising the three molecules (`ions="drop"`).
   The lumped form is closer to Baygi's own Fig. 11 line at every loading (median |ln| 0.03 against 0.05 below
   loading 0.3, 0.06 against 0.13 below 0.6). That is a reason to prefer it, not a fit: nothing was adjusted, and both
   are in every table.
2. **R1 sign.** Table 4 prints C = +22.4773 for R1 in both the Markdown and the PDF. Edwards 1978 and the repo solver
   use -22.4773. With +22.4773 the ionic product is absurd (ln K about +216 at 298 K), so the sign is read as a
   misprint. The repo's constant table `ideal_reaction_equilibrium/results/ideal_reference_reaction_constant_table.csv`
   already carries -22.4773.
3. **R4 basis.** The Table 4 footnote (mole-fraction conversion) sits on the R4 row, so the printed R4 constants are
   used as mole-fraction constants (no second conversion by Eq. 18). The repo's ideal reference records the same reading.
4. **Eq. 15** prints `-[HCO3-]` in the carbon balance in both sources. The carbon balance used is the physical one,
   with `+[HCO3-]` (as the repo solver has it); the printed sign would count bicarbonate as negative carbon.
5. **Temperatures.** Baygi's 313 K and 393 K are evaluated at 313.15 K and 393.15 K, our 40 and 120 degC rows.
6. **R4 range.** R4 is defined for 293-323 K and R5 for 273-323 K; both are extrapolated to 120 degC, as the paper does
   for its 393 K curve.

## Reproduction check (before using the model)

Baygi Table 5 AARD, `data/processed/baygi_table5_reproduction.csv`:

| source | rows | Baygi published | this reproduction | Baygi Fig. 11 digitized line |
|---|---|---:|---:|---:|
| Ma'mun 2005 | the same 19 rows | 21.03 % (n = 19) | **21.25 %** (ions dropped: 24.10 %) | 19.70 % |
| Jou 1995 | we hold 74 rows to loading 0.689; Baygi used 100 of 124 rows to 1.324 | 43.16 % (n = 100) | 120.6 % (72 solved, two 0 degC rows not) | 115.3 % on the 18 rows at 313 and 393 K |

- **Ma'mun 2005 reproduces within 0.2 AARD points** (3.1 with ions dropped).
- **Jou 1995 is not a like-for-like row set, so 43.16 % can not be checked directly.** Our Jou rows sit at loading
  0.35-0.69, where Baygi's own Fig. 11 line is about a factor 3 above the Jou points. The digitized published line
  scores 115 % AARD on the 18 rows we hold at 313 and 393 K, and this reproduction scores 116 % on the same rows.
  Baygi's 100 rows extend to loading 1.3 and 24 rows were dropped, which is how 43 % is possible; that cannot be
  tested without those rows.
- **Model against the published line** (`baygi_fig11_check`, `baygi_fig11_recomputed_curves.csv`), ln(recomputed / digitized):
  median |ln| 0.03 to loading 0.3, 0.06 to 0.6, 0.14 to 1.0; maximum 0.21 to 0.6 and 0.88 at 1.0 (393 K). The
  digitizing error is about 0.07. The recomputed line rises above the published line at loading above 0.6 (the ratio
  reaches 1.5 at 313 K and 2.4 at 393 K by loading 1.0). Our rows stop at loading 0.69, and the row-level statistics below
  are unaffected beyond that.
- **Pure MEA saturation pressure** (`baygi_pure_mea_psat_check.csv`): with the Table 2 rows, `pcsaft` gives 3.4 / 6.0 / 5.9 %
  AAD against the Eq. 9 / Table 1 correlation for 2B / 3B / 4C, against 0.62 / 1.75 / 0.24 % published in Table 2. The
  Engine wheel gives identical saturation pressures (sibling `results/baygi-pure-saturation.csv`), so this is not an
  association-scheme convention error in `pcsaft`. It is an unresolved difference between Table 2's stated AAD and the
  Table 1 correlation as transcribed. The pCO2 reproduction does not depend on it.

Verdict: the reproduction matches Table 5 for Ma'mun 2005 and the published Fig. 11 line to the digitizing error at
loadings up to 0.3, within about 0.1 in ln up to 0.6. It stops matching above loading 0.6 (a growing overprediction),
outside the range of our rows. Jou and the other Table 5 sources cannot be checked on our row sets.

## Comparison on our 161 canonical rows

Rows: 161 active 30 wt % rows of `Canonical_VLE_Observations.csv`, 40-120 degC. Ours is refit C_src (variant
`source-R4-C-f66-v5`, parameters `refit-C-parameters.json` `8b6f30ea…`, Engine wheel `f66d972c…`, not adopted), read
from `calibration-misfit/refit-C-states.csv` and not recomputed (retained values are in Pa). The overall row of the
table (34.78 % AARD, +0.067, 0.388) equals the retained `refit-C-scores.csv`. Each cell: AARD / mean ln(pred/obs) /
RMS ln. Baygi = ions lumped with water; the ions-dropped variant is in `baygi_pco2_statistics.csv`.

| scope | n | Baygi 2015 | ours, C_src |
|---|---:|---|---|
| all rows | 161 | 81 % / +0.29 / 0.70 | 35 % / +0.07 / 0.39 |
| 40-80 degC | 104 | 84 % / +0.32 / 0.71 | 38 % / +0.10 / 0.41 |

By source, all rows, then 40-80 degC (the 100 and 120 degC sources Xu 2011 and Ma'mun 2005 fall out):

| source | n (all) | Baygi 2015, all | ours, all | n (40-80) | Baygi 2015, 40-80 | ours, 40-80 |
|---|---:|---|---|---:|---|---|
| Aronu 2011 | 36 | 40 % / -0.01 / 0.55 | 26 % / -0.10 / 0.37 | 36 | same | same |
| Hilliard 2008 | 30 | 98 % / +0.48 / 0.73 | 45 % / +0.29 / 0.41 | 30 | same | same |
| Idris 2014 | 10 | 67 % / +0.48 / 0.53 | 49 % / +0.37 / 0.43 | 10 | same | same |
| Jou 1995 | 48 | 126 % / +0.45 / 0.90 | 40 % / +0.08 / 0.42 | 28 | 132 % / +0.50 / 0.92 | 43 % / +0.05 / 0.46 |
| Xu 2011 | 18 | 85 % / +0.49 / 0.67 | 32 % / +0.13 / 0.34 | 0 | | |
| Ma'mun 2005 | 19 | 21 % / -0.10 / 0.30 | 19 % / -0.20 / 0.29 | 0 | | |

By temperature (the same rows; 40-80 degC are the first three):

| degC | n | Baygi 2015 | ours, C_src |
|---:|---:|---|---|
| 40 | 59 | 83 % / +0.45 / 0.65 | 42 % / +0.20 / 0.43 |
| 60 | 24 | 97 % / +0.34 / 0.76 | 35 % / +0.10 / 0.37 |
| 80 | 21 | 74 % / -0.10 / 0.83 | 30 % / -0.20 / 0.42 |
| 100 | 18 | 115 % / +0.45 / 0.85 | 35 % / +0.06 / 0.37 |
| 120 | 39 | 57 % / +0.16 / 0.55 | 26 % / -0.01 / 0.32 |

- **Reading.** Baygi's untuned prediction over-predicts pCO2 in the 0.35-0.65 loading band at every temperature
  (a factor 3-5 on the Jou rows) and under-predicts below loading 0.15 at 80-120 degC; our C_src has half the
  RMS ln. Baygi is comparable with ours only on Ma'mun 2005 (120 degC, loading 0.16-0.42; 21 % against 19 %).
- **Limits.** The comparison is a prediction against the data for Baygi (no fit to these rows) but not for ours: C_src was
  fitted to Hilliard 2008 and Jou 1995 (except 80 degC) pCO2 and to speciation; Aronu, Idris, Xu and Ma'mun were not fitted.
  Baygi's 30 wt % chemistry, parameters and k_ij were set from other data. AARD weights over-predictions more than
  under-predictions, so the mean ln column is the bias check.
- **Neither model is validated** here for absorber use; this is a numerical comparison of two predictions.

Per-row values: `data/processed/baygi_pco2_row_comparison.csv` (temperature, loading, source, observed, Baygi model,
Baygi ions-dropped variant, ours). All 161 rows solved for both models.

## Digitized model curves

`data/digitized/` holds, per figure, `<id>_model_curves.csv` (series, temperature, loading, pCO2, pixel position,
per-point error estimate), `<id>_model_curves.json` (source image and sha256, crop, axis calibration, tick check,
method, error summary) and `<id>_model_curves_qa.png` (traced points on the source image, calibration frame in blue).

| figure | source | series | median est. error in ln pCO2 |
|---|---|---|---:|
| Baygi Fig. 11, 30 wt % | PNG copied from the sibling packet, 851 x 803 px | 313 K, 393 K | 0.067 |
| Baygi Fig. 9, 15.3 wt % | PNG copied from the sibling packet, 846 x 768 px | 313.15-413.15 K, six lines | 0.053 |
| Nasrifar Fig. 12a, 15.3 wt % | Zotero PDF `3G4FGGY4` page 7, 1-bit 1200 ppi image, sha256 in the JSON | 313.15, 373.15, 413.15 K | 0.014 |

- **Method:** black-ink connected components inside the plot frame, legend excluded; the stroke centre per pixel column.
  For Nasrifar, whose markers are black, a 13 px disk opening removes the 10 px marker outlines and keeps the 16-24 px
  curve strokes, and samples more than 0.06 decade from a running median are dropped. The bundled `cse:digitize` helper
  needs OpenCV, which the environment lacks; this is the same column-centre trace in PIL and numpy.
- **Calibration:** two known points per axis (the frame lines carry 0 / 1.2 and 1e-6 / 1e6 for Fig. 11, 0 / 0.8 and
  1e-5 / 1e4 for Fig. 9, 0 / 1 and 1e-4 / 1e4 for Fig. 12a). For the two Matlab figures the tick marks fall on round values
  within a median 0.3-0.6 px, an independent check. That check does not apply to the Excel-style Nasrifar axes, which rest on the frame lines alone.
- **Error estimate:** 1.5 px per pixel coordinate propagated through the local slope, so steep segments carry more. It
  excludes error in the published figure itself and the conversion of an image to numbers.
- **Second lane:** the recomputed Baygi model against the digitized Fig. 11 line (above). There is no second digitizer.
- **Nasrifar 313.15 K at 15.3 wt %:** the digitized line lies well below Baygi's Fig. 9 line at loading 0.3-0.5 and above it
  from about 0.5 (see the figure). Nasrifar's curve starts at loading 0.2 for 313.15 K and 0.06 for 413.15 K, as published.

## Figures (`results/pco2_comparison/`)

| figure | content |
|---|---|
| `baygi_ours_30wt_pco2` | (a) 30 wt %, 40 degC (313 K) and 120 degC (393 K): measured points by source, ours C_src as a curve, recomputed Baygi, digitized Baygi Fig. 11. Rows at 60-100 degC are in the tables, not the figure. |
| `baygi_nasrifar_15wt_pco2` | (b) 15.3 wt %: digitized Baygi Fig. 9 and Nasrifar Fig. 12a lines at 40, 60, 80 degC. Ours as points at the 33 Aronu 2011 15 wt % states of `composition-transfer/second-look-source-R4-states.csv` (the same C_src record), next to the measured Aronu points. Jones 1959 is not held here. |
| `baygi_fig11_check` | recomputed Baygi against digitized Fig. 11, and their ln ratio |
| `baygi_fig11_recomputed_on_paper_figure.png` | recomputed points drawn on Baygi's own Fig. 11 image |

Each has `_plot_data.csv`, `.mpl.yaml`, PNG, SVG and PDF (the overlay is a PNG only). **Our curves in (a)** are
C_src evaluated on a 0.05-0.70 loading grid at 40 and 120 degC (54 states, 25 s, one process, `ours_c_src_loading_grid.csv`);
three canonical rows replayed through the same path reproduce the retained predictions exactly. **Our curve is points in (b)**
because the composition-transfer states are only at the Aronu loadings. The 15 wt % of those rows is not the 15.3 wt % of the
published lines (2 % relative difference in MEA mass fraction).

## Where things are

Inputs are `data/input_baygi_2015.md`, the reproduced Baygi tables and comparison tables in `data/processed/`, digitized
curves in `data/digitized/`, and the exact plotted-data bundles in `results/neutral_parity/` and `results/pco2_comparison/`.
The historical numerical generator was retired; `render_figures.py` renders retained tables only.
