# Issue 197 reframe: displayed-number sources

The numerical basis is unchanged from the retained study. The rewrite changes presentation, populations described in prose and the generated data-table summary. This record supplements the earlier revision and correction audits; it does not replace the underlying results. `197-reframe-numeric-check.json` contains 41 arithmetic or population checks, all 73 paragraph identifiers, all 23 generated table files with their numerical rows and source hashes, and the added/removed prose-number inventory.

Unless written as a repository-relative path, filenames below are under `analyses/mea_parameter_bundle/results/a7-paper-evidence/`; `model-curves/` is its sibling. The JSON audit gives row identities and full selectors.

## Values introduced or made explicit in the rewrite

| Quantity | Displayed value | Retained source | Population or basis |
|---|---|---|---|
| fitted pressure AARD (%) | 11.86 | `fit-summary.json:groups:common149 pressure` | 47 fitted pressure observations |
| fitted species AARD (%) | 7.1 | `fit-summary.json:groups:common149 species` | 94 fitted species observations |
| six-source pressure AARD (%) | 20.55 | `canonical-pressure.csv` | all 159 rows, including 47 fitted |
| Hilliard2008 pressure AARD (%) | 9.42 | `canonical-pressure.csv` | 31 row identities listed in the JSON audit |
| Jou1995 pressure AARD (%) | 19.37 | `canonical-pressure.csv` | 48 row identities listed in the JSON audit |
| Aronu2011 pressure AARD (%) | 29.76 | `canonical-pressure.csv` | 36 row identities listed in the JSON audit |
| Aronu 40 C high-loading error, least negative (%) | -46 | `canonical-pressure.csv` | 7 row identities listed in the JSON audit |
| Aronu 40 C high-loading error, most negative (%) | -70 | `canonical-pressure.csv` | 7 row identities listed in the JSON audit |
| pressure at loading 0.69, 313.15 K (kPa) | 159 | `model-curves/pressure.csv` | Exact row coordinates listed in the JSON audit |
| pressure at loading 0.69, 393.15 K (MPa) | 2.848 | `model-curves/pressure.csv` | Exact row coordinates listed in the JSON audit |
| MEA + MEAH+ AARD (%) | 2.32 | `species-figure-data.csv`; `fitted-rows.csv` | 25 row identities listed in the JSON audit |
| Matin bicarbonate + carbonate AARD (%) | 67.48 | `pool-figure-data.csv` | 19 row identities listed in the JSON audit |
| carbonate mole-fraction maximum | at or below 1.8e-5 | `model-curves/species.csv` | all available carbonate values across four isotherms; 353.15 K uses 31 wt% |
| Vinjarapu fitted heat RMSE (kJ/mol) | 1.83 | `heat.csv` | 8 row identities listed in the JSON audit |
| Arcis mean calculated-minus-measured, 510000 Pa (kJ/mol) | 10.21 | `heat.csv` | 8 row identities listed in the JSON audit |
| Arcis mean calculated-minus-measured, 1030000 Pa (kJ/mol) | 3.14 | `heat.csv` | 6 row identities listed in the JSON audit |
| calculated pressure effect on integral heat, 322.5 K (kJ/mol) | about 0.19 | `model-curves/heat.csv` | matched analytical loading, 1.03 MPa minus 0.51 MPa |
| fitted loaded density AARD (%) | 0.18 | `fit-summary.json:groups:loaded density` | 47 fitted loaded densities |
| Han loaded mean signed density error, 353.15 K (%) | -0.43 | `density.csv` | 5 row identities listed in the JSON audit |
| Han loaded mean signed density error, 373.15 K (%) | -0.72 | `density.csv` | 5 row identities listed in the JSON audit |
| Han loaded mean signed density error, 393.15 K (%) | -1.2 | `density.csv` | 5 row identities listed in the JSON audit |
| Han worst density error_kg_m3 | -20.02 | `density.csv` | Han2012_density_120C_alpha0.56 |
| Han worst density observed_kg_m3 | 1057.6 | `density.csv` | Han2012_density_120C_alpha0.56 |
| Han worst density predicted_kg_m3 | 1037.58 | `density.csv` | Han2012_density_120C_alpha0.56 |
| three fitted density misses | [{"id": "Amundsen2009_state_081", "loading": "0.3", "T_K": "353.15", "error_kg_m3": "-5.51709875321626", "error_over_s": "-2.283238811680242", "error_percent": "-0.530388266988681"}, {"id": "Hartono2014_density_80C_alpha0.29", "loading": "0.29", "T_K": "353.15", "error_kg_m3": "-4.161510655263783", "error_over_s": "-2.0549667656950366", "error_percent": "-0.40128738093649063"}, {"id": "Hartono2014_density_80C_alpha0.39", "loading": "0.39", "T_K": "353.15", "error_kg_m3": "-4.406529347786545", "error_over_s": "-2.4317113439017946", "error_percent": "-0.41761717159355405"}] | `density.csv`; `fitted-rows.csv` | fitted loaded density, absolute error/s > 2 |
| Cai temperature RMSE | 1.79 | `fitted-rows.csv` | 25 row identities listed in the JSON audit |
| Cai mole_fraction RMSE | 0.0204 | `fitted-rows.csv` | 25 row identities listed in the JSON audit |
| Aronu 15 wt% pressure AARD (%) | 29.5 | `transfer.csv`; `data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv` | 33 row identities listed in the JSON audit |
| Aronu 45 wt% pressure AARD (%) | 56.0 | `transfer.csv`; `data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv` | 37 row identities listed in the JSON audit |
| finite phase search | {"states_each": 73, "comparison_descent_states": 12, "reported_descent_states": 0, "T_K": [313.15, 333.15], "loading": [1e-05, 0.5]} | `phase-family.csv` | matched records and indices; counts resolved_trials > 0 |
| heat-capacity error (%) Hilliard2008_Cp_318.15_0.0 | 5.53 | `cp.csv` | Hilliard2008_Cp_318.15_0.0 |
| heat-capacity error (%) Hilliard2008_Cp_318.15_0.358 | 2.57 | `cp.csv` | Hilliard2008_Cp_318.15_0.358 |
| heat-capacity error (%) Hilliard2008_Cp_353.15_0.0 | 1.15 | `cp.csv` | Hilliard2008_Cp_353.15_0.0 |
| heat-capacity error (%) Hilliard2008_Cp_353.15_0.358 | -2.13 | `cp.csv` | Hilliard2008_Cp_353.15_0.358 |
| after-adoption/a6-selected MEAH+ segment diameter (angstrom) | 4.16 | `analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-7/fixed-study/wheel-8298c602/after-adoption/a6-selected/fixed-parameters.json` | component/protonated-monoethanolamine/segment_diameter |
| after-adoption/a6-selected MEAH+-water interaction at 313.15 K | 0.027 | `analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-7/fixed-study/wheel-8298c602/after-adoption/a6-selected/fixed-parameters.json` | pair/protonated-monoethanolamine/water/k_ij |
| restricted-2-endpoint MEAH+ segment diameter (angstrom) | 5.35 | `analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-7/fixed-study/wheel-8298c602/restricted-2-endpoint/fixed-parameters.json` | component/protonated-monoethanolamine/segment_diameter |
| restricted-2-endpoint MEAH+-water interaction at 313.15 K | -0.5 | `analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-7/fixed-study/wheel-8298c602/restricted-2-endpoint/fixed-parameters.json` | pair/protonated-monoethanolamine/water/k_ij |
| increase in total fitting cost (%) | 0.45 | `analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-7/fixed-study/wheel-8298c602/after-adoption/a6-selected/score.json`; `analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-7/fixed-study/wheel-8298c602/restricted-2-endpoint/score.json` | same 307-quantity objective, reported/comparison - 1 |
| fitted species temperature domain (K) | [293.15, 333.15] | `state-targets.csv`; `fitted-rows.csv` | all fitted rows of the stated property; generated main-text data table |
| fitted loaded-density temperature domain (K) | [293.15, 353.15] | `density.csv`; `fitted-rows.csv` | all fitted rows of the stated property; generated main-text data table |

## Existing values retained with their earlier evidence

- Pressure at 100–120 °C: 24.35% over 54 observations; Wagner: 22.20% and 9.25% near 353 and 392 K. These remain in `high-temperature-comparison.csv`, `state-summary.json` and generated `supplement_outside_fit.tex`; Section 4.2 states the populations.
- The three fitted density misses, carbon-free maximum error, 44/47 versus 47/47 within twice the assigned density scale, R5 departure of 0.49 pK and 50.5 versus 63.4 kJ/mol, and the 16 parameters/six active bounds retain their exact evidence in the earlier number audits and generated table input comments.
- Carbonate-share mean 0.0731 and range 0.00633–0.267 use the ten diluted-sample comparisons in `carbonate-share.csv` and the earlier audit. They differ from the six fitted amount ratios.
- Arcis measured pairs at loadings 0.181/0.183 and 0.391/0.405, with heats −92.6/−85.9 and −94.4/−85.5 kJ/mol, remain source Table 5, pp. 3355–3356, and `heat.csv`. They are nearby-loading comparisons.
- Existing fixed coefficients, numerical tolerances, bound-history probes, trial counts and objective weights move with their explanations to the supplement. Nineteen unchanged or moved table-file comparisons are recorded in `197-reframe-build-checks.json`; generated table input comments bind all 23 files to retained inputs. No retained scientific results were edited.

## Population and rounding corrections

- The MEA + MEAH+ 2.32% deviation covers 25 compared observations, 20 fitted. The 20 fitted observations alone do not give 2.32%.
- Han mean signed errors use five loaded 30 wt% observations at each temperature, excluding zero loading: −0.43%, −0.72% and −1.20% at 353.15, 373.15 and 393.15 K.
- Heat-capacity errors round to +5.53%, +2.57%, +1.15% and −2.13%; the last retained value is −2.134707%.
- The main data table derives the fitted species range 293.15–333.15 K and fitted loaded-density range 293.15–353.15 K from retained rows. Comparison curves extending beyond those ranges do not extend the fitted data domain.
- The Amundsen fitted density miss is at loading 0.3. The main non-fitted Amundsen comparison statement specifies 30 wt% MEA.

## Literature numbers

Section 4.7 and Table 4 retain explicit source locators: Zhang 2011, Section 3.3 and Tables 9–11 (13.5–35.5% fitted pressure deviations); Najafloo 2018, Table 5 (34.71%, 691 comparisons); Baygi 2015, Table 5 (36.42%, 691 comparisons). Table 4 retains the other previously checked literature numbers and their locators. The sources use different data, roles and domains; these values establish a published range, not equal or better accuracy. Zhang assesses differential heat; the present work assesses integral heat. Only existing bibliography entries are cited.

## Deliberate cuts and source identity

The added/removed literal-number inventory is in `prose_numeric_changes` in the JSON audit. Process numbers cut from the main text remain in the supplement, including the reference fit, acceptance margins, 5.49-to-5.35 Å history, single-start counts, pressure levels, repeated phase state, optimizer tolerances, conditional errors and cost shares. Development labels and file identities stay outside both PDFs. `references.bib` is byte-identical to the baseline. Earlier audit records remain available for unchanged equations, source conversions and fixed coefficients.
