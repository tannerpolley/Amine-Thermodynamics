# Issue 197 reframe: displayed-number sources

The property-calibration basis is unchanged. Fix round 1 incorporates the retained phase extension and replacement split calculations brought in by main commit `d5c9bd1` (#201/#203), explicitly promoted for manuscript use by the owner in `tmp/reframe-197/fix-round-1-brief.md`, adjustments A2–A5. No scientific result was recomputed or edited by the writer. The extension is numerical verification at declared states, not physical validation or a certificate of global stability. This record supplements the earlier audits. `197-reframe-fix1-numeric-check.json` records 63 checks, 82 hashed inputs and the numerical rows of all 24 generated table files; `197-reframe-numeric-check.json` retains the preceding rewrite audit.

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
| removed in fix round 1: pressure at loading 0.69, 313.15 K (kPa) | 159 | `model-curves/pressure.csv` | Exact row coordinates listed in the JSON audit |
| removed in fix round 1: pressure at loading 0.69, 393.15 K (MPa) | 2.848 | `model-curves/pressure.csv` | Exact row coordinates listed in the JSON audit |
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
| first part of the finite phase search | {"states_each": 73, "comparison_descent_states": 12, "reported_descent_states": 0, "T_K": [313.15, 333.15], "loading": [1e-05, 0.5]} | `phase-family.csv` | matched records and indices; counts resolved_trials > 0 |
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

- Pressure at 100–120 °C: 24.35% over 54 observations; Wagner: 22.20% and 9.25% near 353 and 392 K. These remain in `high-temperature-comparison.csv`, `state-summary.json` and generated `supplement_outside_fit.tex`; Section 4.2 states the populations (the supplement is reordered in fix round 1).
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

The added/removed literal-number inventory is in `prose_numeric_changes` in the JSON audit. Process numbers cut from the main text remain in the supplement, including the reference fit, acceptance margins, 5.49-to-5.35 Å history, single-start counts, pressure levels, repeated phase state, optimizer tolerances, conditional errors and cost shares. Development labels and file identities stay outside both PDFs, except the two Engine commit prefixes explicitly required by adjustment A5 in Data and Code Availability. `references.bib` is byte-identical to the baseline. Earlier audit records remain available for unchanged equations, source conversions and fixed coefficients.


## Fix round 1: added and changed displayed quantities

Paths in this section are relative to `analyses/mea_parameter_bundle/results/` unless otherwise stated. Values already above retain their sources; supplementary-section and table numbers change with first-citation ordering.

| Quantity | Displayed value | Retained source and selector |
|---|---|---|
| complete density domain | 210 observations; 293.15–393.15 K; 20–100 wt% MEA | `a7-paper-evidence/density.csv`, all rows; minimum and maximum `mea_mass_fraction` are 0.2 and 1.0. This corrects the former 20–60 wt% inventory label, without changing data. |
| all six pressure-source deviations | Hilliard 9.42% (31); Ma'mun 18.54% (19); Jou 19.37% (48); Idris 21.05% (10); Xu 27.46% (15); Aronu 29.76% (36) | `a7-paper-evidence/canonical-pressure.csv`, grouped by `source`; sum of counts 159; arithmetic mean of absolute relative deviations. |
| source disagreement near 313 K | Aronu 2.86 kPa at loading 0.489; Hilliard 1.10 kPa at 0.491; model 1.17 kPa at Aronu's state | `canonical-pressure.csv` under `a7-paper-evidence/`: `vle_obs_0048-pco2` has measured 2857.7 Pa and calculated 1166.51525598756 Pa; Hilliard row with measured 1100 Pa is at its reported 313.028 K. Displayed loadings round the retained analytical loadings. |
| Hilliard/Jou comparison | within 24% near 40 °C and loading 0.46–0.52 | Same CSV, the two sources at reported temperatures within 0.5 K of 313.15 K and analytical loading between 0.46 and 0.52; maximum absolute relative error is below 24%. |
| non-fitted Böttinger species at 353.15 K, 31 wt% | five states; amine-sum errors within 1.3% through loading 0.25, then −6.4%/−14.5% at 0.34/0.40; carbamate +9%/+26% at the last two | `a7-paper-evidence/species-figure-data.csv`, unique target identities `Bottinger2008_state_063` through `_067`; the audit stores each target and rounded error. |
| Matin titration species | protonated MEA 7.76% AARD; carbamate 8.10%; free MEA 16–35% low above loading 0.4 | Same species CSV, unique target identity, `source=Matin2012`; free-MEA errors at high loading span −35.1522% to −15.9994%. |
| minor species maxima moved into Figure 3 caption | carbonate 1.8×10⁻⁵; dissolved CO₂ 9.7×10⁻⁴ | `model-curves/species.csv`, maximum available `value` for `quantity=CO3^2-` or `CO2` across all four plotted isotherms; dissolved-CO₂ unrounded maximum 0.0009712087. |
| bound comparison made explicit | diameter 4.16→5.35 Å; water interaction +0.027→−0.5 at 313.15 K; narrowed ranges [5.35,5.8] Å and [−0.5,−0.161]; density counts 47/47→44/47 | Fixed-parameter files named above; `joint-recalibration-170/amendment-7/restricted-2/fit/usable-budget-endpoint.json` coordinate declarations, `fitted-rows.csv`, `density.csv`, and generated bound-comparison tables. These are retained values, now explicitly connected in the phase section. |
| extension grid | 353.15, 373.15 and 393.15 K; nine loadings 10⁻⁵, 0.05, 0.1, 0.2, 0.256, 0.3, 0.4, 0.5, 0.6; three pressure fractions 0.50,0.80,0.95 | `phase-extension-201/run-3/reference-pressure/reference-pressures.csv`; the exact special loading is 0.25557798, rounded to 0.256 in prose and to 0.2556 in the confirmation table. |
| extension counts for each fit | 81 declared; excluded 6/6/9 by temperature, total 21 because P* >10 MPa; admitted 21/21/18, total 60; trial counts 189/189/162, total 540; all converged and none unresolved | `phase-extension-201/run-3/counts-by-temperature.csv` and `outcomes-by-temperature.csv`. Exclusions are declared-state exclusions, not failed searches. |
| extension comparison-fit descents | 41 trials at 21 states: 22 trials/12 states at 353.15 K; 19/9 at 373.15 K; 0/0 at 393.15 K | Same outcomes CSV, `record=A6`. Reported fit `record=A7` has zero resolved descents at all 60 admitted states. |
| combined search | 73+60=133 searched states, 313.15–393.15 K; comparison instabilities 12+21=33; reported instabilities 0 | `phase-extension-201/run-3/phase-family-combined.csv`, count admitted rows and rows with `resolved_trials>0` by record; one nearly repeated original state is counted but not drawn. Figure 6 additionally draws all 21 excluded states as crosses. |
| extension split confirmations | 23/27 attempts confirm two liquids at 17/21 tested instability states | `phase-extension-201/run-3/split-confirmations.csv`, deduplicate by split `path`; repeated trial seeds sharing a solve are one attempt. The generated table gives every state pressure, loading and count. |
| frozen extension reference pressures | all 27 values, in kPa in Table S18 | `phase-extension-201/run-3/reference-pressure/reference-pressures.csv`, `fraction=1`; divide `pressure_Pa` by 1000. References were computed with fitting Engine 8298c602 and reused unchanged. All table rows and input hash are in the numeric audit. |
| replacement state 63 water-rich split | succeeds; ΔG/RT = −2.1105128438 (table −2.1105); liquid L density 27919 mol/m³, labels exchanged relative to uniform start | `engine-3e83e19c-adoption/A6-supplement-splits/split-seeded-63.json`, seed `near-pure-2`; complete phase amounts, densities and water fractions are generator-derived. |
| replacement state 21 uniform split | fails; ΔG/RT relative to original +4.76×10⁻⁷ and relative to single liquid −15.7739335 (table −15.774) | `engine-3e83e19c-adoption/A6-supplement-splits/split-seeded-21.json`, seed `positive-neutral-base`; failed-solve diagnostics are explicitly distinguished from confirmed splits. |
| objective enumeration | 307=47+101+6+8+52+50+39+4 | `a7-paper-evidence/fitted-rows.csv`, disjoint observable groups; quantities and counts already retained in the generated data inventory. |

The new split inputs also include `split-seeded-70.json` from the same adoption directory. Their retained Engine identity is `adoption-check.json:summary.accepted_split_changes.retained_engine`, checked against `checks.json:candidate_wheel`: merged Engine commit `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, immutable wheel SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`. The adoption checks retain bit-for-bit property and 73-state classification reproduction. Parameters, conditional standard errors and correlations keep Engine 8298c602 provenance; the new Engine computes the extension and separately seeded splits. This identity is stated once in the manuscript and referenced from methods and supplement.

The newly introduced literature wording uses existing references only: Böttinger 2008, Table 3 (carbamate versus bicarbonate in loaded MEA); Neumann 2022, Section 4.2, p. 8 (homogeneous-liquid density comparisons); Najafloo 2018, Sections 3.1–3.3 and 4 (pure-component fitting in methods versus ternary fitted ranges in the conclusion). These passages were read for this fix round. No bibliography or Zotero source was changed. The literature phase-assessment sentence is unchanged.
