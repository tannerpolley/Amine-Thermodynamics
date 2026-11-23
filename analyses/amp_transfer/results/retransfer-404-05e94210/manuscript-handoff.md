# AMP manuscript handoff for issue 404

This list compares the active manuscript at `origin/main` commit `55cc85416` with the AMP result for review. Apply after the owner's confirmation. Locations below are relative to `docs/scientific/latex`. Evidence paths are relative to the repository root. Historical build records and the source log describe earlier snapshots. The current manuscript's AMP values come from the #344 record.

## Main and supplement tables

### Table 6, `tables/transfer-species.tex`

| Display cell | Old | New | Source |
|---|---:|---:|---|
| AMPH⁺ segment and Born diameters (Å) | 5.7730 | 5.7699 | analyses/amp_transfer/results/retransfer-404-05e94210/main/parameters.json |
| Carbamate segment and Born diameters (Å) | 6.5000 | 6.4705 | analyses/amp_transfer/results/retransfer-404-05e94210/main/parameters.json |
| Carbamate dispersion energy divided by Boltzmann constant (K) | 207.2169 | 183.0006 | analyses/amp_transfer/results/retransfer-404-05e94210/main/parameters.json |

AMPCOO⁻ source cell and note. “This work” → identify the fixed dispersion energy as the MEA carbamate value from the reported 16-parameter calibration. Identify the diameter as fitted, with the MEA carbamate diameter from the 11-parameter calibration as its lower bound. The bounds table already displays that bound. The source CSV and coefficient identities are recorded in `checks.json`.

### Table 7, `tables/transfer-fitted.tex`

Old numbers are in analyses/amp_transfer/results/retransfer-344-05e94210/campaign/start-0/retreat-comparison.json. New values, standard errors and bounds are in analyses/amp_transfer/results/retransfer-404-05e94210/main/fit-summary.json and analyses/amp_transfer/results/retransfer-404-05e94210/penalty-0/parameter-table.json. Values below are rounded as in Table 7.

| Coordinate | Main value, old → new | Conditional SE, old → new | Alternative value, old → new |
|---|---:|---:|---:|
| AMP–water intercept | -0.1304 → -0.1301 | 0.0062 → 0.0062 | -0.1295 → -0.1293 |
| AMP–water slope (K) | -55.108 → -54.316 | 16.255 → 16.343 | -52.048 → -51.526 |
| AMPH⁺–water intercept | -0.2564 → -0.2561 | 0.0215 → 0.0232 | -0.2769 → -0.2775 |
| AMPH⁺–water slope (K) | -215.473 → -214.681 | 82.692 → 87.987 | -221.368 → -222.430 |
| AMPH⁺–CO₂ interaction | 0.7584 → 0.7565 | 0.0760 → 0.0760 | 0.7599 → 0.7580 |
| AMPH⁺ segment diameter (Å) | 5.7730 → 5.7699 | 0.6563 → 0.7145 | 5.7768 → 5.7590 |
| Carbamate segment diameter (Å) | 6.5000 (upper bound) → 6.4705 | — → 1.6648 | 6.0045 → 5.9830 |
| R4 constant | 11.1145 → 11.5617 | 0.2457 → 4.5702 | 9.8707 → 10.1231 |
| R4 enthalpy increment (J/mol) | -5000.0 (lower bound) → -5000.0 (lower bound) | — → — | -5000.0 (lower bound) → -5000.0 (lower bound) |

Remove the upper-bound mark from the fitted carbamate diameter and supply its conditional standard error. The R4 enthalpy lower-bound marks still apply. The alternative remains interpolated.

### Table 8, `tables/amine-summary.tex` (Table 7 in the earlier build)

Pressure statistics come from analyses/amp_transfer/results/retransfer-404-05e94210/same-row-deviations.csv. Bound marks come from the fitted-parameter records above. Search counts come from analyses/amp_transfer/results/retransfer-404-05e94210/main/fit-summary.json, analyses/amp_transfer/results/retransfer-404-05e94210/main/phase-classification-0.json.gz and analyses/amp_transfer/results/retransfer-404-05e94210/penalty-0/alternative-checks.json.

| Quantity | Main, old → new | Alternative, old → new |
|---|---:|---:|
| Fitted coordinates | 9 → 9 | 9 → 9 |
| Active bounds | 2 → 1 | 1 → 1 |
| Loaded fitted pressure AARD (%, 47 rows) | 10.36 → 10.35 | 20.04 → 20.20 |
| All fitted pressure AARD (%, 73 rows) | 7.08 → 7.07 | 13.29 → 13.39 |
| Other pressure AARD (%, 114 rows) | 34.20 → 34.22 | 59.05 → 59.51 |
| Full searches completed / attempted | 666/666 → 666/666 | 666/666 → 666/666 |
| Unavailable entries | 0 → 0 | 0 → 0 |
| Confirmed two-liquid splits | 74 → 73 | 0 → 0 |

### Table S5, `tables/supplement-transfer-parameters.tex`

These are the exact changed numbers from the parameter documents. Use the tied diameter values from the document for each diameter column.

| Parameter document key | Old | New | Unit |
|---|---:|---:|---|
| `aminomethylpropanol/water/k_ij` | -0.13040209477661865 | -0.13010976132052726 | dimensionless |
| `aminomethylpropanol/water/k_ij_reciprocal_temperature_slope` | -55.107522561628976 | -54.3159071695958 | kelvin |
| `carbamate-anion/born_diameter` | 6.5 | 6.4704647197605425 | angstrom |
| `carbamate-anion/debye_huckel_diameter` | 6.5 | 6.4704647197605425 | angstrom |
| `carbamate-anion/dispersion_energy_over_k` | 207.21694618033155 | 183.00063128808972 | kelvin |
| `carbamate-anion/packing_diameter` | 5.72 | 5.694008953389277 | angstrom |
| `carbamate-anion/segment_diameter` | 6.5 | 6.4704647197605425 | angstrom |
| `carbamate-anion/water/k_ij` | -0.0036580495327475336 | -0.013004788810687472 | dimensionless |
| `carbamate-hydrolysis/a` | 11.114485568393897 | 11.5616747761141 | dimensionless |
| `carbon-dioxide/protonated-aminomethylpropanol/k_ij` | 0.7584044537152828 | 0.75651013952477 | dimensionless |
| `protonated-aminomethylpropanol/born_diameter` | 5.772984096882795 | 5.769915428775273 | angstrom |
| `protonated-aminomethylpropanol/debye_huckel_diameter` | 5.772984096882795 | 5.769915428775273 | angstrom |
| `protonated-aminomethylpropanol/packing_diameter` | 5.0802260052568595 | 5.07752557732224 | angstrom |
| `protonated-aminomethylpropanol/segment_diameter` | 5.772984096882795 | 5.769915428775273 | angstrom |
| `protonated-aminomethylpropanol/water/k_ij` | -0.2563521659787007 | -0.25613191165718885 | dimensionless |
| `protonated-aminomethylpropanol/water/k_ij_reciprocal_temperature_slope` | -215.47263600801818 | -214.6805119041768 | kelvin |

Old main document `analyses/amp_transfer/results/retransfer-344-05e94210/campaign/start-0/unpenalized/stage-0/parameters.json`. New main document `analyses/amp_transfer/results/retransfer-404-05e94210/main/parameters.json`. The completed main R4 law supplies the new $A_4$ above. Its $B_4$ stays at −1944.8382247863697 K, also the value at both alternatives. In the S5 Source column for AMPCOO⁻ dispersion energy and AMPCOO⁻–water interaction, replace “Fixed” with “16-parameter MEA calibration (F0)”. The [F0 CSV and SHA-256](checks.json) support both source entries. The alternative section of S5 uses the following exact estimates from analyses/amp_transfer/results/retransfer-344-05e94210/campaign/start-0/retreat-comparison.json and analyses/amp_transfer/results/retransfer-404-05e94210/penalty-0/parameter-table.json. The completed new alternative R4 law is in analyses/amp_transfer/results/retransfer-404-05e94210/penalty-0/alternative-parameters.json.

| Alternative coordinate | Old | New |
|---|---:|---:|
| AMP–water intercept | -0.12952811611887585 | -0.12934100269795387 |
| AMP–water slope (K) | -52.04795882281316 | -51.52602425474883 |
| AMPH⁺–water intercept | -0.27691493020509045 | -0.27753500803194153 |
| AMPH⁺–water slope (K) | -221.3683357945177 | -222.4301902856557 |
| AMPH⁺–CO₂ interaction | 0.7599095565516938 | 0.7579743828934802 |
| AMPH⁺ segment diameter (Å) | 5.7768062843958585 | 5.7589723299863875 |
| Carbamate segment diameter (Å) | 6.004530487610873 | 5.9829779851817 |
| R4 constant | 9.870666948610754 | 10.123066601799017 |
| R4 enthalpy increment (J/mol) | -5000.0 | -5000.0 |

### Table S9, `tables/supplement-transfer-data.tex` (Table S7 in the earlier build)

All cells below come from analyses/amp_transfer/results/retransfer-404-05e94210/same-row-deviations.csv. AARD and signed bias are percent. The observed conditions, roles and denominators match by identity.

| Set | Rows | AARD, old → new | Signed bias, old → new |
|---|---:|---:|---:|
| Hartono binary bubble pressure | 26 | 1.14 → 1.14 | 1.10 → 1.10 |
| Hartono binary vapor AMP mole fraction | 26 | 3.68 → 3.71 | 2.01 → 2.03 |
| Supplemental Hartono total pressure | 18 | 28.13 → 28.12 | -28.13 → -28.12 |
| Kundu CO₂ partial pressure | 51 | 44.07 → 44.06 | 38.17 → 38.09 |
| Fitted Hartono total pressure | 47 | 10.36 → 10.35 | -1.21 → -1.22 |
| Ciftja carbamate fraction per analytical AMP | 57 | 27.44 → 26.23 | 4.89 → 2.92 |
| Loaded Tong total pressure | 40 | 28.16 → 28.23 | -12.19 → -12.12 |
| CO₂-free Tong bubble pressure | 5 | 3.65 → 3.67 | 2.47 → 2.48 |
| Alternative, Supplemental Hartono total pressure | 18 | 24.42 → 24.35 | -24.42 → -24.35 |
| Alternative, Kundu CO₂ partial pressure | 51 | 94.19 → 95.04 | 92.90 → 93.76 |
| Alternative, Fitted Hartono total pressure | 47 | 20.04 → 20.20 | 13.90 → 14.12 |
| Alternative, Loaded Tong total pressure | 40 | 36.74 → 37.01 | 3.68 → 4.05 |

### Table S20, `tables/supplement-amp-ranges.tex`, and adjacent supplement prose

Range values and their denominators come from analyses/amp_transfer/results/retransfer-404-05e94210/same-row-deviations.csv. Apply the main rows to S20 and the alternative rows to the adjacent two sentences. The Tong R4 and R5 partitions are identical.

| Point | Set | Range | Calculated / relative defined | AARD (%, old → new) |
|---|---|---|---:|---:|
| Main | Supplemental Hartono total pressure | R5 outside | 18/18 | 28.13 → 28.12 |
| Main | Supplemental Hartono total pressure | R4 inside | 11/11 | 26.42 → 26.41 |
| Main | Supplemental Hartono total pressure | R4 outside | 7/7 | 30.82 → 30.82 |
| Main | Kundu CO₂ partial pressure | R5 inside | 51/51 | 44.07 → 44.06 |
| Main | Kundu CO₂ partial pressure | R4 inside | 11/11 | 17.88 → 17.93 |
| Main | Kundu CO₂ partial pressure | R4 outside | 40/40 | 51.27 → 51.24 |
| Main | Fitted Hartono total pressure | R5 inside | 47/47 | 10.36 → 10.35 |
| Main | Fitted Hartono total pressure | R4 inside | 32/32 | 11.14 → 11.14 |
| Main | Fitted Hartono total pressure | R4 outside | 15/15 | 8.71 → 8.67 |
| Main | Ciftja carbamate fraction per analytical AMP | R5 inside | 57/57 | 27.44 → 26.23 |
| Main | Ciftja carbamate fraction per analytical AMP | R4 inside | 16/16 | 23.57 → 26.16 |
| Main | Ciftja carbamate fraction per analytical AMP | R4 outside | 41/41 | 28.95 → 26.25 |
| Main | Loaded Tong total pressure | R5 inside | 17/17 | 29.17 → 29.33 |
| Main | Loaded Tong total pressure | R5 outside | 23/23 | 27.42 → 27.42 |
| Main | Loaded Tong total pressure | R4 inside | 17/17 | 29.17 → 29.33 |
| Main | Loaded Tong total pressure | R4 outside | 23/23 | 27.42 → 27.42 |
| Alternative | Supplemental Hartono total pressure | R5 outside | 18/18 | 24.42 → 24.35 |
| Alternative | Supplemental Hartono total pressure | R4 inside | 11/11 | 21.55 → 21.47 |
| Alternative | Supplemental Hartono total pressure | R4 outside | 7/7 | 28.92 → 28.87 |
| Alternative | Kundu CO₂ partial pressure | R5 inside | 51/51 | 94.19 → 95.04 |
| Alternative | Kundu CO₂ partial pressure | R4 inside | 11/11 | 30.91 → 31.30 |
| Alternative | Kundu CO₂ partial pressure | R4 outside | 40/40 | 111.59 → 112.57 |
| Alternative | Fitted Hartono total pressure | R5 inside | 47/47 | 20.04 → 20.20 |
| Alternative | Fitted Hartono total pressure | R4 inside | 32/32 | 19.78 → 19.92 |
| Alternative | Fitted Hartono total pressure | R4 outside | 15/15 | 20.60 → 20.81 |
| Alternative | Loaded Tong total pressure | R4 inside | 17/17 | 52.99 → 53.66 |
| Alternative | Loaded Tong total pressure | R4 outside | 23/23 | 24.73 → 24.70 |

In the range-table caption, “measured temperature ranges of the equilibrium constants” → “source temperature ranges of the equilibrium constants”. The R4 limits are from model-derived estimates and R5 is measured. The same distinction applies to the S9 note and the scope sentence introducing the range tables.

## Prose and figure changes by LaTeX source

The short links below identify the new source for each replacement. The old wording and displayed values refer to the manuscript at `55cc85416`.

| Location | Old | New wording or information for the Writer | Source |
|---|---|---|---|
| `main.tex`, abstract, loaded-pressure sentence | 10.4% (AMP) to 28.5% (DEA) | 10.4–28.5% at the current display precision | [Same-row deviations](same-row-deviations.csv) |
| `main.tex`, abstract, AMP phase sentence | At least 74 calculated splits, all above the measured dissociation range, and 20.0% deviation for the alternative | At least 73 confirmed calculated splits, all above the measured R5 range. The alternative gives 20.2% AARD on the same 47 fitted loaded pressures and zero descents in finite searches with the 7,879-trial bank. | [Coexistence checks](main/phase-classification-0.json.gz), [pressure deviations](same-row-deviations.csv), [alternative checks](penalty-0/alternative-checks.json) |
| `sections/introduction.tex`, final paragraph | At least 74 splits for AMP | At least 73 confirmed splits for AMP. The R5 qualifier still applies. | [Coexistence checks](main/phase-classification-0.json.gz) |
| `sections/data_methods.tex`, AMP reporting choice | The converged fit without the penalty is reported as the AMP model. The interpolated set selected by the penalty procedure has no detected instability and is reported beside it. | Keep this reporting choice. Specify that the alternative completed the full and compressed checks with zero descents using the 7,879-trial bank. State that its upper interpolation neighbor was rejected for an unavailable solve. | [Alternative checks](penalty-0/alternative-checks.json), [bracket](penalty-0/finding.json) |
| `sections/transfer_results.tex`, fitted-parameter paragraph | Two of nine parameters are on bounds. The carbamate diameter moves inside its bounds at the alternative. | One of nine is on a bound, the R4 enthalpy increment. The main carbamate diameter is 6.47 Å with a conditional SE of 1.66 Å. The alternative diameter is 5.98 Å. Both diameters are interior. | [Fit estimates](main/fit-summary.json), [alternative estimates](penalty-0/parameter-table.json) |
| `sections/transfer_results.tex`, phase results | 90 descents, 74 confirmed and 16 with no solution. Confirmed splits at 373.00–393.20 K. The alternative has no detected instability in any search. | 92 liquid-directed descents, 73 confirmed and 19 unresolved coexistence calculations. Confirmed splits at 363.15–393.20 K. All 666 entries completed. All confirmed splits remain above the measured R5 range and the highest fitted loaded-pressure temperature of 353 K. The alternative gave zero descents in the finite checks with the 7,879-trial bank. | [Coexistence checks](main/phase-classification-0.json.gz), [fit summary](main/fit-summary.json), [alternative checks](penalty-0/alternative-checks.json) |
| `sections/transfer_results.tex`, Figure 7 caption and `figures/generated/amp-splits.pdf` | 74 confirmed and 16 with no solution, plotted from #344 locations | 73 confirmed and 19 unresolved. Project the new temperature and loading coordinates onto the plot. Multiple stocks and pressures can project onto the same location. Retain the fitted-temperature band and R5 upper limit. | [Old state coordinates](../retransfer-344-05e94210/descent-diagnosis/descent-states.csv), [new state coordinates](main/phase-classification-0.json.gz) |
| `sections/transfer_results.tex`, Figure 10 and `figures/generated/amp-current-measured-model.pdf` | #344 homogeneous model curves | Replot the AMP pressure curves at the same curve identities, measured points, stock, temperature and range marks. The existing caption describes these same data and marks. | [Old curve values](../retransfer-344-05e94210/curve-data.json), [new curve values](main/curve-data.json), [paired observation predictions](main/data-rows.json) |
| `sections/transfer_results.tex`, other properties | Carbamate fractions have greater deviation than fitted pressures and a small bias | The relationship still holds. Carbamate fraction AARD 27.44% → 26.23%, signed bias +4.89% → +2.92%, on 57 rows. The fitted-pressure comparison is 7.08% → 7.07% on 73 rows. | [Same-row deviations](same-row-deviations.csv) |
| `sections/transfer_results.tex`, four-amine comparison | At least 74 confirmed AMP splits, and the alternative deviates about twice as much from fitted pressures | At least 73 confirmed AMP splits. Make the comparison explicitly about the fitted **loaded** pressures, with 10.35% and 20.20% AARD on 47 rows. The rounded four-amine range of about 10–28% and the ranking among the three transfers still hold. | [Same-row deviations](same-row-deviations.csv), [coexistence checks](main/phase-classification-0.json.gz) |
| `sections/conclusion.tex`, transfer errors and phase conclusion | AMP fitted loaded pressures 10.4%, at least 74 splits, alternative 20.0%. The comparison-pressure range is 15.4–84.9%. | Keep 10.4% and 15.4–84.9% at the current display precision. Report at least 73 splits and 20.2% AARD on the fitted loaded pressures for the alternative. | [Same-row deviations](same-row-deviations.csv), [coexistence checks](main/phase-classification-0.json.gz) |
| `submission/highlights.txt`, lines 3–4 | 10.4–28.5% and at least 74 for AMP | 10.4–28.5% and at least 73 for AMP | [Same-row deviations](same-row-deviations.csv), [coexistence checks](main/phase-classification-0.json.gz) |
| `supplement.tex`, fixed AMP inputs near “The dispersion energy of AMPH⁺ is that of AMP” | The AMPH⁺ energy origin is stated. The carbamate transfer origin is absent there. | Keep the AMPH⁺ sentence. Add the AMPCOO⁻ energy 183.00063128808972 K and AMPCOO⁻–water interaction −0.013004788810687472 as fixed values from the reported 16-parameter MEA calibration. Explain that the interaction's conditional uncertainty in MEA is large (SE 0.1444). The diameter was fitted with the 11-parameter MEA carbamate diameter as its lower bound. | [F0/F2 source and checks](checks.json) |
| `supplement.tex`, R4/R5 alternative differences after S20 | The values currently printed in the two sentences | Replace all eight R4 and the three repeated R5 numerical values using the alternative rows in the range table above. The last sentence on the two Tong partitions still holds. | [Same-row deviations](same-row-deviations.csv) |

The paragraph comparing Tong, Kundu and supplemental Hartono with the alternative still has the same direction of change. Its alternative AARDs are shown in S9 above. The caption of Figure 10 still uses the same loaded observations and R4/R5 markings. Table 2 reaction definitions and source intervals, Tables 3–5 MEA quantities, the pure-AMP data and prefit, S10 objectives and S16 bounds were checked as input invariants. The 23 hot Tong rows are still included. S17 and the reported MEA calibration remain the same comparison records. AMP publication comparisons still have no scalar comparison on the identical rows. The MEA-only submission drafts and old build reports contain no #404 AMP result to replace.

### Supplement phase and penalty paragraphs

| Location | Old | New | Source |
|---|---|---|---|
| `supplement.tex`, search classification | 90 liquid-directed descents, all 90 outside R5 and 64 outside R4 | 92 liquid-directed descents, all 92 outside R5 and 65 outside R4. The confirmed split stock range is 26.8–30.0 wt%. The selected main confirmed range is 363.15–393.20 K and 0.4–0.966 mol CO₂/mol AMP. | [Old classification](../retransfer-344-05e94210/descent-diagnosis/summary.json), [new classification](main/phase-classification-0.json.gz) |
| Same paragraph, largest Gibbs decrease | 1.215 MPa and densities 44,685 and 31,704 mol/m³. The #344 record gives a decrease of 0.01673355584 mol in total G/(RT). | 1.215 MPa (1.215282456 MPa before rounding). Densities 44,631 and 31,743 mol/m³. The decrease is 0.01618322237 mol with numerical estimate 2.79 × 10⁻⁹ mol. Conditions remain 393.15 K, 30.0 wt% AMP and loading 0.700 mol/mol. | [Old classification](../retransfer-344-05e94210/descent-diagnosis/summary.json), [new classification](main/phase-classification-0.json.gz) |
| `supplement.tex`, unpenalized start selection | Costs agree within the optimizer tolerance and the lower cost is 61.70 | Both converge. Their reloaded costs are 61.42269696437 and 61.42269701978. The relative difference is about 9.0 × 10⁻¹⁰ against a 10⁻¹⁰ tolerance. Select start 0. The carbamate diameter coordinates differ by 0.00020036 Å. | [Fit summary](main/fit-summary.json), [coordinate differences](checks.json) |
| Same paragraph, 3.5 Å sensitivity | Each loaded-pressure AARD moves by less than 0.001 percentage points | That statement still holds. Add that the best sensitivity cost was 61.42269697052 and its search gave 92 descents, 73 confirmed and 19 unresolved. The 3.5 Å calculation comprised the fit and search. | [Sensitivity fit](sensitivity-3.5/fit-summary.json), [same-row deviations](same-row-deviations.csv) |
| Same paragraph, penalty stage descents | 38 and 17 after the 0.01 and 0.003 stages | 39 and 17 in the full searches. The 862-entry compressed checks returned 42 and 17 descents. The nine-coordinate fitted costs are 61.52917403 and 61.59360343 apart from penalty costs 0.02702698 and 0.01824427. | [Stage details](penalty-0/finding.json) |
| Same paragraph, anchor eligibility | The AMP paragraph gives the selected fraction and omits the eligibility check for each start. | State that the first anchor passed all 666 entries with zero descents, while the other completed all 666 with 572 descents and was ineligible. Only the first start continued through the penalty stages. | [Start 0](penalty-0/anchor-eligibility.json), [start 1](penalty-1/anchor-eligibility.json) |
| `supplement.tex`, interpolation procedure and AMP fraction | Generic wording describes a coarse 0.01 line scan before bisection. AMP fraction 0.5699, with one search unfinished at the next set. | Specify that the AMP calculation bisected from the two ends with the same final width limit. The selected fraction is 0.5585556030273438 and upper neighbor 0.558563232421875. At the upper neighbor 861/862 completed and zero descended. At 30.0 wt%, 313.15 K, loading 0.6 and 1.05 times the bubble pressure, a solve stalled at residual 1.18037446048 × 10⁻¹⁰ against the 10⁻¹⁰ row limit. The bound on the selected fraction reflects solver availability in this bracket. | [Bracket](penalty-0/finding.json), [unavailable search details](penalty-0/unavailable-searches.json.gz) |
| Same paragraph, accepted point | Zero detected instabilities in 666 full and 862 compressed searches, fitted cost 124.73. Fitted loaded pressure contribution from 59.04 to 122.13. | Zero descents in the 666 full and 862 compressed entries with the 7,879-trial bank, including the supplied-trial rechecks. The compressed supplied-trial recheck reused the final passing sweep. The initial bank had 7,301 trials and the retained main bank later grew to 10,771. Fitted cost 126.86. Fitted loaded pressure contribution rises from 58.89 to 123.61. | [Alternative checks](penalty-0/alternative-checks.json), [main bank](main-new-witnesses.json.gz), [alternate group costs](penalty-0/group-costs.json), [main group costs](main/fit-summary.json) |

The source selection for AMP in `scripts/dea_displays.py` still points at #344. When applying the handoff, update the AMP readers and the numerical assertions together, then regenerate the AMP rows of Tables 6–8, S5, S9 and S20, both figures and `tables/number-sources.json`. `scripts/final_rerun_tables.py` reads the shared declarations and AMP reaction-range reference for Table 2. Check its number-source output and reference links when regenerating. The reaction equations, source intervals and numerical ranges in Table 2 are unchanged. No manuscript build or generated LaTeX was changed by issue 404.
