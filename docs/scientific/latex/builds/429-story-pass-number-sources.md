# Issue 429 story pass: sources of added and changed numbers

No calculation was run and no retained record was edited by the Writer. Every number below was read from a retained record. Paths are relative to the repository root; `MEA/` abbreviates `analyses/mea_parameter_bundle/results/`.

Numbers marked **checked** are rebuilt from their record by `docs/scientific/latex/scripts/dea_displays.py` and compared with the prose as an exact string; the run fails if the prose and the record disagree. Numbers in generated tables are written by `dea_displays.py` or `final_rerun_tables.py` and are compared byte for byte in `--check` mode. Unmarked numbers were read from the record by the Writer and are not machine-checked.

## AMP pair (abstract, introduction, Section 4.2, conclusions, highlights)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| Objective, slope fitted / fixed | 61.29, 62.07 (61.3, 62.1) | `analyses/amp_transfer/results/` free-fit `fit-summary.json` (`fits[selected].cost`) and model `confirmation.json` (`selected_cost`) | checked |
| Fitted total-pressure AARD, slope fitted / fixed | 10.3, 10.5 % on 47 | AMP comparison record, `pressure_deviations_by_range['loaded-pressure']` | checked |
| Slope and its standard error; distance of −150 K | −219 K, 81 K, 0.86 SE | free-fit `fit-summary.json:parameter_table['AMPH-water-slope']` | checked |
| Confirmed splits; searches | 73; 666 | AMP split classification `counts.confirmed`; `confirmation.json:full_search.states` | checked |
| k(AMPH⁺–water) at 353 and 393 K | −0.178, −0.115 | free-fit `AMPH-water-k` and slope, reference 313.15 K | checked |
| Worked split: Gibbs decrease, error, state (a grid state) | 0.0188 mol, 2.8e-9, 30 wt %, 393.15 K, 0.700 mol/mol, 1.212 MPa; mole fractions 0.100 / 0.028 | State and Gibbs decrease: `analyses/mea_parameter_bundle/results/reference-states-428/amp.json` (`row_key` = grid state, `feed_mol`, `P_Pa` 1212490.95, `Gibbs_difference_over_RT_mol` −0.0188141, `phases`). Numerical error 2.8e-9: `numerical_error_over_RT_mol` 2.807e-9 of the same grid state in `analyses/amp_transfer/results/retransfer-412-f2-05e94210/main/phase-classification-1.json.gz`; the `uncertainty` field of `amp.json` (1.83e-10) is the error of the plane value, a different quantity (fix round 1) | not checked |
| Split domain | 26.8–30.0 wt %, loadings 0.40–0.97, six at measured states | AMP split classification states (values already in the supplement) | not checked |

## Controlled MDEA transfer (abstract, Section 4.3, Table 8, conclusions, highlights)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| k values | 0.7650, 0.1325, 1.0 | `analyses/mdea_mea_workflow/results/shared-bicarbonate-417/profile.json.gz` | checked |
| MEA objective rise; allowance | 1.023, 0.024; 1.3987 | same; `MEA/paper-evidence-341/uncertainty/profiles.json` (largest `delta_cost`) | checked |
| Fitted Kuranov total P (66) | 20.1 → 11.2 % (20.09, 11.18, 20.18) | `shared-bicarbonate-417/mdea-comparison.json.gz:Kuranov.original` | checked; table generated |
| Total pressures outside the objective (54: Kamps 28, Kuranov 413 K 11, Sedighi 15) | 38.7 → 33.0 % (38.75, 32.99, 38.65) | same, per-source `original` AARD of `corrected-Kamps`, `Kuranov-413K`, `Sedighi`, count-weighted; the five sets reproduce `all pressures not fitted` (175, 25.83 %) within 1e-9 | checked (fix round 1); table generated |
| CO₂ partial pressures outside the objective (121: Ermatchkov 101, Xiao 20) | 20.1 → 33.6 % (20.07, 33.62, 20.05) | same, `Ermatchkov`, `Xiao`, count-weighted | checked, including the preprint abstract and the cover letter (fix round 1); table generated |
| At the upper value, every displayed deviation changes by less than 0.1 points | 0.088, 0.099, 0.018 | same | asserted (fix round 1) |
| Unfinished searches; confirmed splits | 1099 → 1245; 0 → 2 | `shared-bicarbonate-417/mdea-search-readback.json`; MDEA `summary-row.json` | checked |
| Correlations of the interaction | 0.960, −0.974 | `MEA/paper-evidence-341/uncertainty/covariance.json` (unchanged) | checked |

## Table 10, pressures not fitted (fix round 1)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| MDEA: total P; p(CO₂) | 38.75 (54); 20.07 (121) | reported MDEA model, `analyses/mdea_mea_workflow/results/bounded-binary-411/data-rows.json` (role `not fitted`, unit Pa, by group); equal to the k₀ column of Table 8 | table generated; pooled rows reproduce `summary-row.json` (25.83, 175) |
| AMP: total P; p(CO₂) | 26.18 (63: Hartono 2021 18, Tong 40 loaded, Tong 5 CO₂-free); 47.02 (51, Kundu) | `analyses/amp_transfer/results/retransfer-412-f2-05e94210/slope-150/data-rows.json`, same selection | table generated; pooled rows reproduce the retained AMP summary (35.50, 114) |
| MEA and DEA pressures not fitted | labeled p(CO₂); values unchanged | Tables 5 and S8 | label only |

## MDEA phase behavior (Section 4.4, Table 10, conclusions, supplement)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| Fixed pressure | 262.862 MPa (262.9) | `analyses/mdea_mea_workflow/results/phase-search-421/fixed-pressure.json:P_Pa` | checked |
| Gibbs decrease; numerical error | 1.394e-3 (1.39417e-3); 7.6e-10 (7.60e-10) mol | same, `attempts[0]` | checked |
| Moles in the denser liquid; densities | 4.4 % (4.387 %); 22214, 25053 mol/m³ | same, `attempts[0].amounts_mol`, `densities_mol_m3` | checked (shares) |
| State of the earlier split | 363.15 K, 78.62 wt %, 1.368 mol/mol, 1.05 × bubble pressure | same, `T_K`, `feed` (unchanged prose values) | not checked |
| Assigned pressures at the 27 states | 0.100–4.190 MPa | `phase-search-421/` 27-state record | not checked |
| The 27 states: 23 loaded, 4 CO₂-free densities at 0.100 MPa | 23, four, 0.100 MPa | `phase-search-421/measured-phase.json` (`feed_mol` CO₂ = 0, `pressure_Pa`) | not checked; read in fix round 1 |
| Gap onset brackets | 423.150–423.156 K at 1.466 MPa; 423.13750–423.14375 at 1.121; 423.16250–423.16875 at 1.811 | `phase-search-421/` onset record | not checked |
| Objective without / with bound | 479.4, 564.5 | bounded-binary-411 records (unchanged) | checked |

## DEA pair (Section 4.5, Table 9)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| Excess enthalpy AARD (14) | 152 → 17.1 % | `analyses/dea_transfer/results/reactive-refit-425/comparisons.json:tableS10['Horstmann heat']` | checked; table generated |
| Horstmann pressures (42) | 0.8 → 9.5 % | same, `Horstmann VLE` | checked |
| Cai pressures (7) | 51.49 → 48.55 % | same, `Cai VLE` | table generated |
| Fitted Lawson p(CO₂) (30) | 28.5 → 23.1 % | same, `Lawson` | checked |
| p(CO₂) outside the fit (67) | 53.9 → 62.9 % | same, `table7.loaded_outside_reactive_fit` | checked |
| Fitted integral heats (50) | 0.9 → 1.9 % | same, `Carson` | checked |

## R4 on the starting-law basis (Section 4.5, Table 7, Tables S5 and S20, supplement)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| DEA Δln K₄ at 313.15 K; ratio | −1.309 ± 0.618; 0.270 | `analyses/dea_transfer/results/r4-shift-426/table6.json`, `shift.csv` | checked |
| DEA enthalpy increment | −11968 ± 1344 J/mol; bounds −30000…+10000 | same | checked |
| AMP Δln K₄ at 313.15 K; ratio | +1.233 ± 0.265; 3.433 | `analyses/amp_transfer/results/r4-shift-426/table6.json`, `shift.csv` | checked |
| AMP enthalpy increment | −5000 J/mol, on its lower bound | same | checked |
| Shifts at 298.15, 313.15, 393.15 K | DEA 1.078, 1.309, 2.244 (SE 0.640, 0.618, 0.532); AMP 1.330, 1.233, 0.843 | both `shift.csv` | checked |
| Source ranges | DEA 303–331 K; AMP 313.15–373.15 K | `r4-shift-426/source-rows.json` | not checked |

## Standard errors on responsive observations (methods, Tables 4, 7, S-tables, supplement)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| MEA responsive observations; degrees of freedom | 268; 258 | `MEA/objective-weights-420/MEA/information.json.gz` | checked |
| MEA variance factor before / after; multiplier | 1.01523840; 1.16869941 (1.169); 1.0729 (+7.3 %) | same | checked |
| MDEA observations; degrees of freedom | 278; 272 | `MEA/objective-weights-420/MDEA/information.json.gz` | checked |
| MDEA variance factor before / after; multiplier | 4.10533597; 4.15061398; 1.0055 (+0.5 %) | same | checked |
| Every printed MEA and MDEA standard error | tables | conditional SE × multiplier, in both producers | tables generated |
| Carbamate–water SE; carbamate energy SE | 0.5464; 63.79 K | MEA standard errors × 1.0729 | checked |
| Relative SE of the 47 fitted p(CO₂) | 6.0–16.9 % (5.98–16.9) | `MEA/objective-weights-420/MEA/prediction-bands.csv` (`stage_SE`/`value`) | checked |

## Cai weights (methods, supplement S2.3)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| Cai contributions; share | 39.824, 51.807; 60.8 % (60.78 %) of 150.76 | `MEA/objective-weights-420/MEA/contributions.csv` | checked |
| Objective on alternative weights, reported / refit | 62.797; 62.656 | `MEA/objective-weights-420/tables.md`, `alternative/` | not checked |
| p(CO₂) AARD after the refit | 11.64 → 11.61 %; 24.89 → 24.98 % (112); 25.03 → 25.50 % (Wagner) | `MEA/objective-weights-420/alternative/` paired comparisons, `tables.md` | not checked |
| Objectives of the two MEA starts | 150.763, 150.767 | `MEA/reduced-refit/F2/` start records | not checked |

## Carbonate share and electrostatic choices (Section 4.1.2, Section 5.4, Table S9, supplement)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| Geometric-mean ratio, MEA model; range at the ten states | 0.032 (0.0317); 0.004–0.182 | `MEA/shared-ion-electrostatics-423/…/P0/carbonate-share.json` | checked (mean) |
| Range over the tested changes; largest | 0.016–0.040; 0.0402 | per-case `carbonate-share.json` | checked; table generated |
| Refit with MEA solvation factor 1.5 | objective −1.096; ratio 0.020 (0.0197) | `refit-comparison.json`; `M3-refit/carbonate-share.json` | checked |
| Objective rise, CO₂ factor 1.5; MEA factor 1.5 | 0.57 (0.569); 15.0 (15.037) | `arm-replay-costs.json` | checked |
| Second permittivity pair | +0.110 fixed, +0.108 refitted; coefficients 0.73099 L/mol, 1019.08 K and 0.24645 L/mol, 2436.44 K; +0.19, 0.71, 1.28 % | `arm-replay-costs.json`, `refit-comparison.json`, permittivity record of the same study | not checked |
| Volume-equivalent Born diameter replays | DEA 28.5 → 28.1 %; MDEA 20.1 → 17.7 % | `…/diethanolamine` and `…/methyldiethanolamine` `control` and `volume-equivalent` `data-rows.json.gz` | checked |
| Segment and volume-equivalent diameters | 2.948, 3.655 Å; 5.108, 5.641 Å | reported DEA and MDEA parameter records (σ, m) | checked |

## Reference states and worked calculations (supplement)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| Tables S14 and S15 | generated | `MEA/reference-states-428/amp_reference_state.tex`, `mea_reference_state.tex` | `final_rerun_tables.py --reference-states --check` |
| Error estimates and tangent-plane distance | 1.8267e-10, 1.7544e-10, −3.697e-3 | `MEA/reference-states-428/amp.json` | not checked |
| MEA heat and heat capacity at 313.15 K, 1.734 MPa, 0.31 mol/mol | −81.553 kJ/mol; 84.628 J/(mol K); 4e-7 | `MEA/reference-states-428/mea.json` | not checked |
| Source pressures | 1.734 MPa (R1–R3), 0.1 MPa (R4–R5, P°) | `MEA/reference-states-428/tables.md` | not checked |
| Pressure insensitivity of speciation AARD | 7.2137 / 7.2136 %; 11.1441 / 11.1435 % | `MEA/reference-states-428/s12.json` | not checked |

## Published comparisons (Section 5.3, Table 11, supplement)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| Hong et al., their own fit | 1.53 % AARD | Hong et al. §3.2, Table 3, as given by the post-draft numbers check; not re-read by the Writer (no local copy) | not checked |
| Kundu et al. statistic | AAD label with a signed formula; 56 observations | Kundu et al. Table 10 and its footnote, as given by the post-draft numbers check; not re-read by the Writer | not checked |
| MDEA model on the 82 Kuranov pressures | 19.5 % (19.53); 70 fitted, 4 CO₂-free | `analyses/mdea_mea_workflow/results/kuranov-published-422/statistics.json:present.K82` | checked |
| Published values on those 82 | Uyan 22.9, Wangler 19.7, Raeispour 10.9 | `kuranov-published-422/` records | table generated |
| Zhang and Chen | 6.8 % (82 Kuranov), 17.7 % (101 Ermatchkov) | their Table 14, read in `literature/zhangThermodynamicModelingCO22011--2KHILX2X.md`; constants in `dea_displays.py` | table generated |
| Ermatchkov comparison | 17.9 against 16.8 % | MDEA published-comparison record (unchanged) | checked |
| Hong comparison | 24.8, 22.6 %; 132; 131; 32 fitted | Hong comparison record, `adopted_fitted` | checked (first four) |

## Table 2 (data in each objective)

Generated by `dea_displays.py` from `MEA/paper-evidence-341/paper-evidence/{fitted-rows,state-targets,density,heat,cp}.csv` and the DEA, MDEA and AMP data-row records; the producer asserts 307, 80, 281 and 156 objective observations and 14 Arcis heats.

## Other counts

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| MEA searches | 2646 = 2484 + 162 | MEA stability record (unchanged counts, summed) | checked |
| Table 2 temperatures: Jakobsen ratios; CO₂-free densities | 293.15–313.15 K; 298.15–353.15 K | `MEA/paper-evidence-341/objective-declarations.json` (`row.T_K`) | table generated (fix round 1) |
| Section 5.2 denominators | 15 heat capacities, 26 densities, 15 loaded Han densities | `MEA/stripper-temperature-409/band-table.csv` (`n`, cohort `all` and `Han2012 loaded`) | checked (fix round 1) |
| Fitted MEA p(CO₂) temperature range | 313–333 K | `MEA/paper-evidence-341/paper-evidence/fitted-rows.csv` (Table 2 shows 313.00–333.15) | table generated |
| Cai temperatures at or above 370 K | 22 of 25, up to 431.85 K | same | table note generated |
| Horstmann isotherm | 365.15 K, 42 pressures | `reactive-refit-425/comparisons.json` | table generated |

## Round-3 text pass

No calculation was run and no retained record was edited. Numbers added or moved in this pass:

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| Abstract, AMP: fitted total-pressure AARD of the two fits; confirmed splits | 10.3, 10.5 %; 73 | as in the AMP pair rows above | checked |
| Abstract, AMP: highest temperature of the fitted loaded-solution pressures | 353 K | `analyses/amp_transfer/declarations.toml` (`hartono-2021-calibration` filter `T` ≤ 353.5 K; Table 2 shows 313.00–353.00 K) | table generated (Table 2) |
| Abstract and highlight 4, MDEA: fitted Kuranov total P; outside-fit CO₂ partial pressures | 20.1 → 11.2 %; 20.1 → 33.6 % | as in the controlled MDEA rows above | checked (main.tex, highlights, preprint abstract, cover letter) |
| Table 7 footnote c: R4 change at 313.15 K | −1.309 ± 0.618 (DEA), +1.233 ± 0.265 (AMP) | `analyses/{dea,amp}_transfer/results/r4-shift-426/table6.json` (`delta_ln_K4`, `SE_ln_K4`) | table generated |
| Table S5: DEA R4 enthalpy increment on the starting-law basis | −11968.40567100886 J/mol | `analyses/dea_transfer/results/r4-shift-426/table6.json` (`delta_h_J_mol`); the producer asserts the record row it replaces is 0 | table generated |
| Section 3.1: DEA and MDEA fitted pressures above their R5 ranges | 23 of 30; 29 of 66 | already in Section 5.2 and Table S22/S23 (`analyses/dea_transfer/part-ii-346.qmd`; MDEA `mstats['Kuranov']['MDEA-dissociation']`) | 29: checked; 23: not checked |
| Section 3.1: DEA isotherm left out; R2 domain end | 394 K; 393.15 K | `analyses/dea_transfer/historical-f0.qmd` ("The seven Lawson rows at 394.26 K lie above the 393.15 K end of the shared R2 law") | not checked |
| Section 3.1: AMP R5 range | 293–353 K | Table 1 (Hamborg and Versteeg, 293.12–353.22 K); `analyses/amp_transfer/source-admission.md` | table generated (Table 1) |
| Section 4.4: measured MDEA states with a converged two-phase calculation; states shown only by an earlier trial | 16 of 27; 23 and four | `analyses/mdea_mea_workflow/results/phase-search-421/measured-phase.json` (`attempts[*].requested_tolerance_met and distinct`; `native_branch == 'none'`) | checked (new) |
| Section 5.5: MEA ion-diameter correlation | −0.998 | Table S18 (`MEA/paper-evidence-341/uncertainty/covariance.json`) | table generated |
| Section 5.3: Uyan 22.9 % and its recalculation 34.4 % | 22.9, 34.4 | Table 11 and note c; Section S9 | table generated |
| Section 4.1.4: Aronu extended UNIQUAC, all CO₂ partial pressures | 24.3 % | Aronu et al. 2011, abstract and Section 4.2 (Zotero AYEZBMRS) | literature, read |
| Section 4.2: Tong quasi-chemical AMP correlation, loading AAD | 1.9 % | Tong et al. 2012, Section 3.4, p. 46 (Zotero 5FB2UHQZ) | literature, read |
| Section 5.3 and S10: Hong pressure AARD | 1.53 % | Hong et al. 2027, Section 3.2 and Table 3 (Zotero 5MFM84GS) | literature, read |

Removed from the main text: the 262.862 MPa state, its Gibbs decrease, numerical error and dense-phase share (kept in Section S7.1), the Table 10 fixed-pressure row, the abstract objective values, MEA and DEA deviations and 666 searches, and the Section 5.1 sentence repeating the Table 10 deviations. The Hong deviations on 132 observations and the 131 failing states remain in Section S10 and Table S25.
