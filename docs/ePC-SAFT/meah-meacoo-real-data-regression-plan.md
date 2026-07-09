# MEAH+ and MEACOO- Real-Data Regression Plan

## Purpose

This document defines the data and proof standard for replacing seed values for `MEAH+` and `MEACOO-` with fitted ePC-SAFT parameters.

The regression must not pass if fitted values simply equal the initial guesses. A passing result requires source-backed experimental targets, changed or intentionally fixed parameters, a residual/statistics table, and regression plots.

## Current Problem

The active ionic dataset contains plausible-looking values, but they are still seed/regression-smoke values:

```text
data/reference/epcsaft_datasets/MEA_CO2_H2O_ionic_fit/pure/any_solvent.csv
MEAH+:   m=1, s=3.563,  e=228.71, d_born=3.563
MEACOO-: m=1, s=3.5605, e=533.11, d_born=3.5605
```

The current saved parameter-regression summary is not proof of final fitted ion parameters:

```text
analyses/phase3/ionic_epcsaft_regression/results/parameter_regression/ionic_parameter_regression_summary.json
target_counts: vle=3, speciation=3
optimizer.success: false
optimizer.nfev: 1
```

## Data Already In The Repo

Machine-readable source manifest:

```text
data/reference/MEA/ion_parameter_regression_sources.csv
```

Local speciation inventory:

```text
data/reference/MEA/ChEq/Combined_ChEq.csv
rows: 74
MEACOO- rows: 74
direct MEAH+ rows: 35
MEA+MEAH+ combined rows: 74
sources: Bottinger=39, Matin=19, Jakobsen=16
```

Direct local sources:

| source | local path | MEAH+ | MEACOO- | role |
|---|---|---:|---:|---|
| Matin 2012 | `data/reference/MEA/ChEq/Matin_2012_ChEq.csv` | 19 | 19 | primary direct speciation target |
| Jakobsen 2005 | `data/reference/MEA/ChEq/Jakobsen_2005_ChEq.csv` | 24 | 24 | independent NMR speciation target; 16 rows are the 30 wt% subset used in `Combined_ChEq.csv` |
| Böttinger 2008 | `data/reference/MEA/ChEq/Bottinger_2007_ChEq.csv` | 0 direct, 68 combined MEA+MEAH+ | 68 | MEACOO- target and MEAH+ indirect constraint |

Do not claim Böttinger directly identifies `MEAH+`; it reports the rapidly exchanging amine/protonated-amine pool together.

## Source-Backed Candidate Data

### Tier A: Use Immediately

1. Matin et al. 2012, `Matin2012`, DOI `10.1021/ie300230k`.

Use for direct `MEAH+` and `MEACOO-` composition residuals at 30 wt% MEA. The source describes a titration/loading method for CO2-loaded 30 wt% MEA and reports species concentrations including free amine, carbamate, and protonated amine.

2. Jakobsen et al. 2005, `Jakobsen2005`, DOI `10.1021/ie048813+`.

Use for independent NMR `MEAH+` and `MEACOO-` residuals at 20 and 40 C. The standalone source file includes 15 wt% and 30 wt% MEA rows; the 30 wt% subset is the portion already carried into `Combined_ChEq.csv`. Treat reported uncertainty as about 5-10%.

3. Böttinger et al. 2008, `Bottinger2008`, DOI `10.1016/j.fluid.2007.09.017`.

Use for `MEACOO-`, `HCO3-`, dissolved `CO2`, and combined `MEA + MEAH+` residuals. Do not use it as a direct `MEAH+` residual.

### Tier B: Import Or Digitize Before Final Claim

1. Wong et al. 2015, `Wong2015`, DOI `10.1016/j.ijggc.2015.05.016`.

This is the strongest missing high-pressure speciation extension. It reports in situ Raman quantification of protonated MEA, carbamate, bicarbonate, carbonate, and molecular CO2 for 30 wt% MEA at 303.15, 313.15, and 323.15 K over 1-60 bar. Import tables or digitize figures before calling the final fit broad.

2. Amundsen et al. 2009, `Amundsen2009a`, DOI `10.1021/je900188m`.

Use density/viscosity of CO2-loaded MEA+water as mixture-property constraints after the speciation mapping is working. This helps prevent unrealistic ion sizes/energies, but it is not direct MEAH+/MEACOO- data.

3. Barzagli et al. 2009, `Barzagli2009`, DOI `10.1039/B814670E`.

Use as a dilute external validation set for MEA carbamate/protonated amine trends. It is not a primary 30 wt% fit target.

### Tier C: MEAH+ Transferability Only

1. Kaljusmaa et al. 2026, `Kaljusmaa2026`, DOI `10.1021/acs.jpcb.5c07863`.

This source provides density, viscosity, conductivity, and NMR data for ethanolammonium acetate/hexanoate plus water. It is useful for checking `MEAH+` cation transferability only if acetate/hexanoate anion parameters are fixed or jointly identifiable. It is not evidence for `MEACOO-`.

## What Counts As A Real Fit

### Fitted Parameters

The minimum fitted parameter report must list:

```text
MEAH+:
  s
  e
  d_born
MEACOO-:
  s
  e
  d_born
Selected interactions:
  MEAH+--MEACOO- k_ij
  MEAH+--HCO3- k_ij if used
  CO2--MEACOO- k_ij only if direct/defensible mixed target is included
```

Do not fit `m` for these ions unless there is a defensible reason. The current package benchmark fixes ionic `m=1`, which is reasonable unless a package-side ePC-SAFT convention says otherwise.

### Required Residual Terms

A valid first objective must include:

```text
log10(model_x_MEACOO- / data_x_MEACOO-)
log10(model_x_MEAH+ / data_x_MEAH+) for Matin and Jakobsen rows
log10((model_x_MEA + model_x_MEAH+) / data_x_MEA_plus_MEAH+) for Böttinger rows
log10(model_pCO2 / data_pCO2) for VLE rows
regularization to literature/seed values with low weight, not high enough to freeze the fit
```

Optional but recommended after the first fit:

```text
density residuals from Amundsen 2009
Raman high-pressure speciation residuals from Wong 2015
dilute validation residuals from Barzagli 2009
```

## Required Plots And Statistics

Create a new curated result folder:

```text
analyses/phase3/ionic_epcsaft_regression/results/ion_parameter_regression/
```

Required files:

```text
ion_parameter_fit_summary.json
ion_parameter_fit_values.csv
ion_parameter_fit_statistics.csv
ion_parameter_speciation_fit_data.csv
ion_parameter_pressure_fit_data.csv
meah_meacoo_speciation_parity.mpl.yaml
meah_meacoo_speciation_parity.png
meah_meacoo_speciation_parity.svg
ion_parameter_pressure_parity.mpl.yaml
ion_parameter_pressure_parity.png
ion_parameter_pressure_parity.svg
```

Required statistics:

```text
initial vs final residual norm
initial vs final RMSE by target family
initial vs final MAE by target family
initial vs final median absolute log10 error by species
R2 or parity-slope/intercept for MEAH+ and MEACOO- speciation
parameter confidence/identifiability notes, at minimum whether each fitted parameter is at a bound
number of rows used per source
number of failures and fixed residual penalties
```

Required plots:

```text
1. MEAH+ and MEACOO- model-vs-data parity plot, colored by source.
2. MEAH+ and MEACOO- vs CO2 loading curves for at least 20 C / ambient Matin/Jakobsen rows.
3. CO2 partial pressure parity or pressure-vs-loading plot using the same fitted parameter set.
4. Optional density/viscosity parity if Amundsen data is imported.
```

The plot captions and JSON summary must say which rows were used for fitting and which were held out for validation.

## Current Candidate Fit

The current promoted artifact folder is:

```text
analyses/phase3/ionic_epcsaft_regression/results/ion_parameter_regression/
```

It is a real-data Tier A speciation fit, not a final full VLE-approved parameter set. It uses eight evenly selected local Tier A rows from Matin, Jakobsen, and Böttinger to prove the workflow and produce non-seed fitted values.

Current promoted result:

```text
optimizer.success: true
optimizer.message: `xtol` termination condition is satisfied.
optimizer.nfev: 13
target_row_count: 8
initial_residual_norm: 0.271444549584188
final_residual_norm: 0.26765769640830644
overall median |log10(model/data)|: 0.1010484260531472 -> 0.09884572828236765
MEAH+ median |log10(model/data)|: 0.0581945677496939 -> 0.05633896500746165
MEACOO- median |log10(model/data)|: 0.04248908563659662 -> 0.034888546312248254
MEAH+ R2 log10: 0.6553265859383761 -> 0.6653433193502851
MEACOO- R2 log10: 0.8876738274090447 -> 0.9050466408808331
```

Current fitted values:

```text
MEAH+__s = 3.48508556586
MEAH+__e = 232.687201645
MEAH+__d_born = 3.53322927146
MEACOO-__s = 3.53543525721
MEACOO-__e = 453.265244384
MEACOO-__d_born = 3.54107030822
k_ij__MEAH+__MEACOO- = -0.00201813457644
```

Why this does not close the full scientific goal yet:

```text
The pressure parity artifact in this folder is a placeholder; full VLE pressure must be regenerated after promoting a final ion fit.
No Wong 2015 Raman or Amundsen 2009 density data has been imported yet.
```

## Commands The Next Agent Should Add

Preferred final interface:

```bash
uv run python analyses/phase3/ionic_epcsaft_regression/scripts/generate_ion_parameter_data.py
uv run python analyses/phase3/ionic_epcsaft_regression/scripts/fit_ion_parameters.py --fit-tier tier_a --max-nfev 80 --promote
uv run python analyses/phase3/ionic_epcsaft_regression/scripts/render_ion_parameter_figures.py
uv run python -m MEA.epcsaft_ionic.approval_check
```

The `--promote` flag is important. Smoke runs should write to:

```text
analyses/phase3/ionic_epcsaft_regression/results/runs/<label>/
```

Curated final artifacts should be promoted only after the statistics and plots pass.

## Failure Conditions

Fail the goal if any of these are true:

```text
MEAH+ and MEACOO- fitted values equal the initial values without a fixed-parameter explanation.
The summary does not list the exact experimental rows used.
The plots compare only pressure and never show MEAH+/MEACOO- model-vs-data speciation.
The fit uses Böttinger data as direct MEAH+ data.
The fit uses ethanolammonium acetate/hexanoate data as MEACOO- evidence.
Any fitted ion parameter hits a bound and the report does not call it out.
The regression improves pressure only by destroying speciation residuals.
```

## Package-Side Need

The upstream ePC-SAFT package now exposes `evaluate_reactive_electrolyte_bubble_residuals(...)`, which is closer to the needed fixed-shape objective helper. The MEA-side implementation should use this package helper where possible instead of reimplementing failure-shaping and continuation logic.

If performance is still too slow, the next package request is not "add MEA data"; it is:

```text
make the coupled reactive-electrolyte residual evaluator fast enough and warm-startable enough to run an 18 VLE / 18 speciation / 80 nfev fit without manual interruption.
```
