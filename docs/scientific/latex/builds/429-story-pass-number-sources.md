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

## Text pass 4 (round-3 calculations and the #433 split diagnosis)

No calculation was run and no retained record was edited. `R3/` abbreviates `analyses/round_3/results/`; `S433` is `analyses/mea_parameter_bundle/results/split-diagnosis-433/README.md`. **checked** means `dea_displays.py` rebuilds the string from the record (new block "Round-3 calculations") and the run fails if the prose differs.

| Quantity | Displayed | Where | Retained source | Check |
|---|---|---|---|---|
| AMP fits at equal absolute pressure: confirmed splits | 14 of 15 (first fit), none (second) | §4.2, S7.3 | `R3/q1.json` (`attempts[*].confirmed` per fit); the producer asserts 15 rows, 14 and 0 | checked |
| Same: first-fit smallest TPD at confirmed states; second-fit TPD | −9.9e-4 to −3.7e-3; within 1.2e-13 of zero except the worked state | S7.3 | `R3/q1.json` (`minimum_trial.quantities.tpd_over_rt`); the producer asserts the 1.2e-13 bound | checked |
| Worked state: second fit's bubble pressure; vapor-side descent | 1.238 MPa; −0.0199 at 383 mol/m³ | §4.2, S7.3 | `S433` (fixed-pressure sweep paragraph: 1.238250 MPa, −0.01988932, 383.23 mol/m³, 33-point isotherm) | not checked |
| AMP total pressures at 373–393 K, one liquid: AARD (bias = −AARD) | Hartono 18: 28.10 / 28.35 %; Tong 25: 25.30 / 25.47 % (main text 28.1, 25.3, 28.3, 25.5) | §4.2, S7.3 | `R3/q2.json:scores` (`free`, `fixed`); the producer asserts bias = −AARD for all four | checked |
| Resolved descents of the first fit at the measured pressure | 7 Hartono, 7 Tong | S7.3 | `R3/q2.json:scores[*].fixed_pressure_outcomes` | not checked |
| Hartono row 9 (373 K, 0.58 mol/mol): measured P; parent TPD; local two-liquid bubble P | 0.4065 MPa; −1.84e-3; 0.2525 MPa | §4.2, S7.3 | `R3/q2.json` row `hartono-2021:55`; `analyses/round_3/manuscript-handoff.md` Q2 (−0.001840; 252,535.6 Pa) | not checked |
| Tong row 9 (373.2 K, 0.455 mol/mol, 0.2915 MPa): liquid amounts; ΔG/RT; error | 11.410 and 1.138 mol; 5.57e-4 mol; 3.1e-9 | S7.3 | handoff Q2 (11.41035, 1.13818, 0.000556998, 3.13e-09); row `tong-2012:28` | not checked |
| Two-liquid bubble pressures; readback misses; vanished phase | 0.2525, 0.3384, 0.4451, 0.3291 MPa; four Tong states 0.159–0.238 MPa miss the 1e-10 readback; Tong row 13 (0.9835 MPa) unavailable | S7.3 | handoff Q2 table | not checked; **misses reported as misses** |
| Worked AMP split: recalculation, chemical potentials, Hessian eigenvalue | within 1.2e-13 mol (record 1.14e-13); 3.9e-14 RT; −0.083 | S7.3 | `S433` "Independent verification" | not checked |
| Curvature terms along the liquid–liquid line (first fit); AMP model total | −0.369, −0.228, −0.218 vs +0.343, +0.211, +0.236; total −0.024; +0.030 | S7.3 | `S433` "AMP energy and curvature" | not checked |
| Slope-only control (−219.25 → −150 K) | total curvature +3.4e-4; pair 0.0190 mol above the single liquid | S7.3 | `S433` (+0.000344; +0.01896829) | not checked |
| Exact Figiel Eq. 9 average | 0.018814 → 0.018693 mol; 0.64 % | §5.4, S7.3 | `S433` "Formulation test" (−0.01869319273) | not checked |
| Born removed | pair 0.364 mol below the single liquid; amounts unresolved | S7.3 | `S433` (−0.36375749) | not checked |
| Controlled MDEA splits at k = 0.1325 | 288.71 K, 1.121 MPa, 0.5635 mol/mol; 373.15 K, 203.1 MPa (203.127), 1.3 mol/mol; water 9.9218 and 1.7988 mol; ΔG/RT 1.94e-3 and 2.49e-4 (S7: 1.937e-3, 2.495e-4) | abstract, §4.3, S7.1 | `R3/q3.json` (`reference`); the producer asserts that the 0.7650 and 1.0 rows have no resolved descent and no confirmed attempt | checked (ΔG and the abstract wording) |
| Same, 0.7650 and 1.0: attempt outcomes | coalesced, vanished or iteration budget exhausted | §4.3, S7.1 | `R3/q3.json` (`attempts[*].message`) | asserted |
| Cold MDEA split, k alone 0.1325 → 0.7650 | pair 0.391 mol above the single liquid | S7.1 | `S433` "MDEA" (+0.39080) | not checked |
| 262.862 MPa MDEA split: x(CO₂) in the two liquids; x(MDEAH⁺); curvature terms | 0.262, 0.736; < 1.08e-4; dispersion −0.564, Born −0.419, Debye–Hückel +0.207, total −0.244 | S7.1 | `S433` MDEA table and text | not checked |
| Reaction reference pressure | R1–R3 at system P (bubble P in a bubble calculation), R4–R5 at 0.1 MPa | Section 2 (text after the activity equation), nomenclature, S3 | handoff Q4; #432 readiness | text |
| S15 common-molality R1 / R3: ln K, Γ | −31.175402, −23.536538; −576.92284, −942.62762 | Table S15 (generated) | `R3/q4.json:S15_common_basis`; `final_rerun_tables.py --reference-states` asserts ln K + Γ equals the retained #428 value within 1e-9 and now writes `tables/mea_reference_state.tex` (the #428 file is unchanged) | table generated |
| R1–R3 at 0.1 MPa instead: p(CO₂) shifts; heat | +0.00187 and +15.03 Pa at 1.559 and 73206 Pa; −81.553 → −81.603 kJ/mol | S3 | `R3/q4.json` (`rows[*].pCO2_change`, `prior_prediction_Pa`, `heat`, `heat_change`) | checked |
| S14 certificate | chemical-potential residual 1.8e-13 (tolerance 1e-10); reaction 7.5e-13; electrochemical 1.1e-13; smallest TPD of 5 starts +0.0307; four vapor-connected +0.0382 at 383.4 mol/m³ | S3 | `R3/q6.json:split.diagnostics`; handoff Q6 | +0.0307, +0.0382: checked; residuals not checked |
| Search recall of the comparison fit | 93 of 93 recovered; 0 new among 573; pressure matches at 609; 57 without archived pressure | S7.1 (AMP) | `R3/q7-summary.json` | checked; **57 keys reported as not compared** |
| DEA tie | 8.082968228315, 8.082968228355; tolerance 1e-10; second solution k −0.18834289, −0.04772959 vs −0.18834283, −0.04773144; 28.51 % (30 Lawson), 0.94 % (50 Carson); 1270 searches finish, no split; outside-fit deviations not retained | Section 3 (initial parameter sets), S7.2 | `R3/q8.json:dea`; `analyses/dea_transfer/results/refit-413/selection.json` (`chosen` = start-0, `ties`) | costs and 28.51: checked |
| Kuranov 82 | 66 + 4 fitted; 11 at 413 K + 1 at 393.16 K, 1.205 MPa not fitted; 22.1 vs 19.1 % | §5.3 | `R3/q8.json:kuranov` | checked |
| Water fit conditions | 20 temperatures 298.15–393.15 K (psat, saturated ρ), 23 heat capacities | S1.2 | `R3/q8.json:water.fitted_rows` (a constant written by `analyses/round_3/records.py`, not computed from fit rows) | not checked |
| Water deviations (record `lambda-0.1-A`, equal to F2 in all five coordinates) | 0.075, 0.036, 0.037, 0.44 % (max 0.17, 0.098, 0.095, 1.49); staggered 0.070, 0.034, 0.035, 0.42 %; 0.101325 MPa controls 0.038, 0.78 % | S1.2 | `R3/q8.json:water.metrics` | not checked |
| Carbonate pool split, 8 Jakobsen states at 313.15 K | calculated 5.9e-6 to 0.039; measured 0.016 to 0.57 | S2.2 | `R3/q5.json`; handoff Q5 table | not checked |
| MEA pH (R2, common molality) | 9.84 → 7.92 (loading 0.05 → 0.50); 0.64–0.81 below Hessen Fig. 6 (197 points, 313.15 K); 0.42–0.82 below Matin Fig. 1 (6 points, 294.15 K); 10.63 (R1) vs 8.89 (R2) at 0.30 | S2.2 | `R3/q5.json`, `R3/ph-digitization.json`; handoff Q5 | not checked (digitized read-off bounds) |

Not used from the round-3 handoff: the MDEA unbounded per-dataset deviations and the AMP relative-objective statistics (Q8), the transplanted-ion comparison (Q8), the per-ion activity decomposition (Q5) and the Böttinger 046 and 100 kPa control rows of Q4.

## Revision pass (adopted #435 models)

No calculation was run by the Writer. `H435` is `analyses/mea_parameter_bundle/results/salt-anchored-435/manuscript-handoff.md` (its rows name the retained record and key of each value); `R5` is `analyses/round_5/manuscript-handoff.md`. **checked** means the exact prose string is rebuilt from the record by `dea_displays.py`; **table** means the value is written into a generated table and compared byte for byte in `--check` mode; **read** means the Writer read it from the handoff row and no string check covers the prose. This section supersedes the rows above wherever they describe the fits made with the MEA-fitted shared set as the reported models.

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| MEA fitted p(CO₂), 47 | 11.3 % (11.35) | H435, deviations by observable | checked (abstract, Sections 1, 4.1.2, 6) |
| MEA not-fitted p(CO₂), 112; with MEA-fitted set | 27.8 %; 24.9 % | H435; `paper-evidence-341` scores | checked |
| MEA objective, both shared sets | 152.96; 150.76 | H435, objectives | checked |
| MEA responsive observations, degrees of freedom, variance factor | 268, 259, 1.18113896 | H435, variance row | checked |
| MEA bound refits, largest change | 0.75 | `MEA/F4` `uncertainty/profiles.json` | checked; Table S21 |
| MEA pressure standard errors | 5.9–17.0 % | H435 | checked |
| Ma'mun pressures near 393 K, three calibrations | 19.4, 33.5, 38.4 % | H435 matched comparisons | checked |
| Carbonate share: AARD, geometric-mean ratio, MEA-fitted set | 89.9 %, 0.070, 0.032 | H435; `carbonate-share.csv` | checked |
| Cai contributions and share | 39.750 + 51.795, 59.9 % of 152.96 | H435 contributions | checked; Table S13 |
| Temperature bands, MEA | 27.25 % (69), 29.66 % (66); 1.2 and 0.4 %; 5.8, 10.0, 13.4 % | H435 band rows | checked; Table S8 |
| Salt fit: laws, AARD, bounds | 0.1707 + 0.003931 K⁻¹; −0.9706 + 0.001963 K⁻¹; 0.16 %, 5.1 %; two values on −1 | H435 salt calibration; `carbonate-ions-282/README.md` | read |
| DEA fitted p(CO₂), 30; with MEA-fitted set | 36.6 %; 28.5 % | H435 | checked |
| DEA not fitted, 67 | 58.5 % | H435 | checked; Table 8 |
| DEA R4 change and enthalpy increment | −1.438 ± 0.729 (factor 0.237); −11969 ± 1628 J/mol | H435 fitted parameters | checked; Table 7 |
| DEA correlation; unfinished searches | 0.970; 1269 of 1271 | H435 | read; checked |
| DEA binary fits | 152 → 17.1 %; 0.8 → 9.5 %; 28.5 → 23.1 %; 53.9 → 62.9 %; 0.9 → 1.9 %; −0.0870, −32.25 K | #425 records through Table S14 | table (S14); text read |
| MDEA fitted total pressures, 66; with MEA-fitted set | 10.1 %; 20.1 % | H435 | checked |
| MDEA above 368 K, 29 | AARD 12.5, bias 11.3 % | H435 | checked |
| MDEA Ermatchkov p(CO₂), 101; with MEA-fitted set; published set I | 38.4 %; 17.9 %; 16.8 % | H435; Table 9 | checked |
| MDEA Kuranov 413 K, 11; 82 Kuranov pressures | 3.1 %; 8.8 % (8.75) | H435 | checked |
| MDEA other fitted properties | 0.1–13.9 % | H435 | checked |
| MDEA objective shares | loaded pressures 1 %, CO₂-free densities 84 % | H435 contributions | checked; Table S13 |
| MDEA starts | 537.659, 539.870, 537.659 | H435 | table (S23) |
| MDEA variance factors, correlation | 3.95337207, 3.91024580; 0.953 | H435 | checked |
| MDEA searches | 11,824; 1,248 unfinished (1,024 / 146 / 71 / 7); 75 descents at 26 states | H435 phase-search rows | checked (146, 71, 7 read) |
| MDEA unfinished by kind of state | 1,026 grid, 222 measured of 1,564 | `mdea_mea_workflow/results/salt-anchored-435/campaign/search-outcome.json.gz`, `tally.unavailable` keys | checked |
| MDEA instabilities at measured states | 25 states (4 + 13 + 5 + 3), gas-like trial phase, two-liquid attempt at 17, none confirmed | same record, `classifications` | checked (25, 17); breakdown read |
| MDEA confirmed split | 383.15 K, 78.6 wt %, loading 1.368, 121.309 MPa, 4.233 × 10⁻⁵ mol against 9.2 × 10⁻¹⁰ | H435 | read; count asserted |
| MDEA bound and onset | −0.0671; 423.150–423.156 K at 1.466 MPa | `campaign/binary-onset.json` | read |
| AMP loaded total pressures, 105 | 10.9 % (12.06 / 6.99 / 11.35 by set) | H435 | checked; Table S29 |
| AMP Kundu, 51; Tong 45 pooled | 15.6 %; 10.5 % | `amp_transfer/results/salt-anchored-435/matched-deviations-free.json` | checked (pooled value computed in the check) |
| AMP slope | −52.0 ± 63 K | H435 | checked; Table 7 |
| AMP R4 change | +0.389 ± 0.230 (factor 1.475) | H435 | checked |
| AMP −150 K sensitivity | 77.6428 (+1.33), 1.55 standard errors, 11.10 %, 74.01 against 73.60 | H435 | checked |
| AMP searches | 666, none; 7301 supplied compositions | H435 | checked (666) |
| First AMP fit | −219.25 ± 80.99 K; 61.2853; 10.3 %; 73 + 20 of 666; 28.1 and 25.3 % | `round_5` original fits; #432 records | checked |
| AMP fit to all pressures, MEA-fitted set | −181 K; 6.7 % on 18 | H435 comparison column | checked (6.7); slope read |
| Cation–water interaction with temperature | −0.178 → −0.115 (first fit); −0.202 → −0.187 (AMP model) | fitted laws | checked (AMP model); first fit read |
| AMP slope profile | −365 to −134 K; −283 to −77 K; reference changes 1.58, 1.36 | R5 section A | read |
| AMP bubble pressures at the worked feed; split at 2.037 MPa | 1.155, 1.238, 1.907, 1.940, 1.886, 1.794 MPa; 0.0185 mol | R5 section A; H435 worked-state rows | read; Table S30 |
| Lowest Hessian eigenvalues | 0.122, 0.137, 0.408, 0.439 | R5 section D | read |
| Reference-pressure test | +0.00198 and +4.84 Pa on 1.562 and 87,678 Pa; −81.795 → −81.850 kJ/mol | `MEA/F4` `q4.json` | checked |
| Reference-convention recalculation of splits | 0.01882 against 0.01881; 1.89 × 10⁻³ against 1.94 × 10⁻³; 203.1 MPa not confirmed | R5 section B | read |
| Variance factors of DEA and AMP | 0.28770616 (76), 0.73731307 (207) | H435 variance rows | read |
| Hong comparison | 24.77 / 24.97 / 50.93; 26.27 / 23.40 / 53.83; 22.92 and 52.34 | H435 Hong rows | checked; Table S31 |
| Hilliard heat-capacity roles | 4 fitted / 47 not fitted | `round_5/results/records/Hilliard-Cp.json` | table (S7), asserted |
| Published AMP benchmarks | 15.4, 8.0; 17.3, 9.3 % | Yi et al. 2024 Table 4; Hartono et al. 2020 Table 13, as transcribed in the round-5 literature note | read |
| Shares of the objectives | 98 % (DEA), 96 % (AMP) | H435 contributions | checked; Table S13 |

Removed with their text: the 14-of-15 equal-pressure comparison, the archived-pressure repeat counts (609 and 57), the pressure-ratio range 0.1731–0.9807 and the details of the 262.862 MPa two-liquid calculation.

## Round 7 adoption display rebind

The adopted declarations are the original #435 MEA fit, broadened DEA, pressure-weighted salt MDEA and corrected-input free-slope AMP. Corrected-input fixed-slope AMP and the full-weight expanded MEA fit are sensitivities. The [owner decisions on issue 429](https://github.com/tannerpolley/Amine-Thermodynamics/issues/429) select the endpoints. The [quantity-keyed handoff](../../../../analyses/round_7/manuscript-handoff.json) and its [notebook](../../../../analyses/round_7/notebook.qmd) identify the retained scientific records. The table below abbreviates paths beneath `analyses/round_7/results/` and omits their JSON or compressed JSON suffix.

| Generated display | Retained values and locator |
|---|---|
| `supplement-mea-pressure-sensitivity.tex` | `E/{incumbent,F4}/replay:summary.pressure` for legacy 47, added 112, hot 54 and 66, aggregate and source scores. The 12 unfitted Wagner rows are `hot_wagner`. The two nominal 120 °C source subsets use `pressure_population` joined by row identity to `rows`. The Wagner-only scores are 28.07%/−28.07% and 10.40%/−7.90%. Pooled hot-66 scores are 29.66%/−24.39% and 21.04%/−2.45%. |
| `supplement-mea-off-window.tex` | `E/{incumbent,F4}/off-window:rows` via the keyed handoff. The 70 Aronu observations and 14 Jou observations comprise the 84. The six refused Jou comparisons stay in the denominators for attempted rows and are excluded from the relative errors. |
| `supplement-mea-window-objective.tex` | `E MEA {incumbent,F4} {original,expanded} objective`. On the original 307 rows, 152.96 → 165.71. On the expanded 419 rows, see the generated table. |
| `transfer-species.tex`, `transfer-fitted.tex`, `supplement-transfer-parameters.tex`, `supplement-transfer-bounds.tex` | `F/selection`, `C/salt/selection`, and `AMP/free/selection:selected[2]` give the adopted declarations and bounds. DEA and AMP conditional standard errors come from `assessment:uncertainty`. MDEA active bounds come from `C/salt/refit:objective.rms.active_bounds`, with no retained coefficient SEs. The two #435 `hydrolysis/shift.json:source_law` entries supply the starting basis for the reported R4 shifts. Corrected AMP inputs are independently identified in `AMP/free/assessment:identity.carbamate`. |
| `calibration-data.tex`, `supplement-transfer-data.tex`, `supplement-{dea,mdea,amp}-ranges.tex` | `F/assessment:expanded_design,deviations`, `C/salt/refit:rows`, and `AMP/free/assessment:rows,deviations`. Counts and availability come from the retained rows. The comparison column matches available rows with defined relative errors by observation identity and unit against the original #435 receiver fits. |
| `amine-summary.tex` | Same receiver assessment rows, plus `F/search-outcome`, `C/salt/search-outcome` and `AMP/free/native-outcome:tally,confirmed`. Original #435 receiver searches provide the comparison rows. MEA retains its #435 reported row and MEA-fitted shared-set comparison. |
| `published-models.tex` | The MDEA original-weight and pressure-weighted results use `C/salt/{incumbent,refit}:rows`. AARD uses the available Kamps predictions and shows their count. K82 stays unfilled for the adopted model because row 72 is absent from the reweighted endpoint record. The matched original salt value is in the #435 `kuranov-matched-pressure:grouped.K82.salt_anchored`. `H/kuranov-82nd` identifies the unmatched row. |
| `supplement-dea-expanded.tex`, `supplement-dea-binary.tex` | Expanded objective from `F/incumbent-expanded:cost` and `F/selection:selected[0]`. Seo–Hong and Horstmann from `F/assessment:expanded_design` and the corresponding handoff keys. Conditional methane maximums come from `F/{methane,methane-refit}:rows` via the handoff. The historical constant/temperature-dependent binary comparison still uses #425 `comparisons.json` on its original set. |
| `supplement-mdea-weighting.tex` | `C/salt/{incumbent,refit}:objective` compares both weightings at each endpoint. Both loaded total-pressure AARDs come from the same 66 Kuranov rows of the same records. |
| AMP sensitivity and common-pressure displays in `supplement-amp-ranges.tex` | `AMP/{free,fixed}/selection:selected[0]`, both assessments and both native and supplied outcomes. The older common absolute-pressure calculations remain with their original #435 endpoints and the historical shared-set fits. |
| `supplement-liquid-splits.tex`, `supplement-mdea-fixed-pressure.tex` | `F/search-outcome:classifications,confirmed` identifies the four measured-state DEA splits. `C/salt/search-outcome:classifications,confirmed` identifies the 204.054 MPa grid split. `A/reference:comparisons` gives original-weight 121.309 MPa tracking confirmation and the unresolved 100 kPa reference case. `C/salt/{original,rms}-fixed-pressures` provides the separate targeted comparisons at 121.309 and 262.862 MPa. |
| `supplement-transfer-scales.tex`, `supplement-objective-contributions.tex`, `supplement-fit-starts.tex` | MDEA scales and contributions use `C/salt/refit:objective.rms.rows`. The reweighting is as declared in `analyses/round_7/calculations.py:MDEAWeights.bind`. DEA and AMP contributions sum half the squared retained `report.weighted_residuals` after checking the fit prediction order against the fitted assessment rows. Start table uses `F/fit-{0,1}`, `AMP/{free,fixed}/fit-{0,1}` and `C/salt/attempts/fit-{0,1,2}`. |
| `dea-current-measured-model.pdf`, `dea-integral-heat-concentrations.pdf`, `loaded-pressure-residuals.pdf`, `mdea-current-measured-model.pdf`, `amp-current-measured-model.pdf` | Same adopted assessment rows. The DEA figures show predictions at the observations, since round 7 lacks an adopted continuous curve record. The MDEA pressure residuals retain 53 of the 54 outside-fit total-pressure observations because one prediction was refused. |
| `mdea-gap-onset.pdf` | MDEA–water laws in `C/salt/selection:selected[2]` and the #435 original salt endpoint, plotted against the retained #411 CO₂-free onset brackets. The historical AMP split figure and worked reference-state tables retain their own original case identities. |

Both display checks compare regenerated files to their committed equivalents. `tables/number-sources.json` records the display inputs and SHA-256 hashes. The MEA sensitivity tables carry their round-7 input hashes in the generated LaTeX headers. The round-7 handoff check independently recomputes its 1,022 quantities from retained records. The Writer's [prose gaps](436-rebind-prose-gaps.md) capture strings tied to superseded endpoints. The TeX changes outside generated tables are the supplement's display inputs. The source has no generated result-number macro file to update.

The expanded MEA heat-of-absorption comparison requested in the owner comment has no matching round-7 retained hot caloric series to bind. The historical caloric displays and their own evidence stay with the original MEA fit. The K82 published comparison, old MDEA coefficient SEs and above-423 K gap-onset brackets also lack corresponding adopted-endpoint readbacks. The corrected AMP endpoints have no keyed common-pressure worked-state replay at 2.037 MPa. No Engine calculation or replay was run for this rebind.

## Round-7 endpoint replays for the displays

The replay records are in `analyses/round_7/results/display-replays/`. They use Engine `05e94210` and the SHA-256 recorded in each file. The generators read the retained records, and the round-7 notebook handoff checks their values and provenance.

| Quantity | Result | Record and display |
|---|---|---|
| DEA pressure isotherms | 275 of 275 points converged on 11 isotherms, from 5.12 Pa to 1.976 MPa over the sampled loadings. | `dea-pressure-curves.json.gz:rows` supplies the lines in panels (a–c) of `dea-current-measured-model.pdf`. The plotted lines connect calculated values. Panel (d) shows measured-state heat predictions. |
| MDEA conditional standard errors | In coefficient order after the active bound, the errors are 3.434e-5 K⁻¹, 0.02656, 0.08567, 4.255 K, 0.5162, 0.03405 Å and 152.44 K. | `mdea-standard-errors.json.gz:responsive_standard_error` supplies `transfer-fitted.tex`. The analytic residual Jacobian is weighted once and converted to physical coordinates. Covariance holds the 423 K intercept fixed and scales inverse information by the responsive residual variance, 0.12842032 from 278 rows and 271 degrees of freedom. The three pure-water Kim rows are excluded from the variance estimate, as in #435. |
| MDEA binary onset | 423.14375–423.15000 K at 1.121 MPa, 423.15625–423.16250 K at 1.466 MPa and 423.16875–423.17500 K at 1.811 MPa. | `mdea-binary-onset.json.gz:pressures` supplies the new onset table in `supplement-amp-ranges.tex`. The #435 method brackets agreement of the Gibbs hull and tangent-plane distance on both composition grids. |
| Kuranov Table 2 | Row 72 is 1.165620 MPa calculated versus 1.205300 MPa measured, a −3.29% deviation. The matched K82 total-pressure AARD is 4.16% on all 82 rows. | `kuranov-row-72.json.gz:prediction` joins the 81 rows of `C/salt/refit.json.gz` by source row for `published-models.tex`. |
| Corrected-input AMP at common pressure | At 393.15 K, 0.700 mol/mol and 2.037241 MPa, both finite searches found no resolved descent. The seeded phases coalesced for both and the fixed-slope retry also lost a phase. Bubble pressures are 1.892512 and 1.801649 MPa for free and fixed slope. | `amp-common-pressure.json.gz:outcomes` supplies the two new rows in `supplement-amp-ranges.tex`. |
| Expanded-fit MEA heat sensitivity | At 393.15 K and 1.734 MPa, the expanded fit predicts 68.10–91.73 kJ/mol for the seven Kim intervals, versus 70.55–90.52 for the reported fit and 79.74–100.77 measured. The five Vinjarapu integrals give 91.29–91.59, versus 90.11–90.38 reported and 94–98 measured. All 12 hot rows were available. Three cool Kim rows above the loading ceiling remain in the record. | `mea-heat-sensitivity.json.gz:replay.rows` and `salt-anchored-435/MEA/F4/heat-replay.json:rows` supply the calorimetry comparison in `supplement-mea-pressure-sensitivity.tex`. |

## Fixed 100 kPa reaction references (#440)

The #429 owner decision selects the #440 models on wheel
`c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb`.
All five selections are start A. The fitted objectives are 152.932402 for
MEA, 15.588667 for DEA, 15.609314 for provisional MDEA, 74.928158 for reported
free-slope AMP and 76.226564 for the fixed-slope AMP sensitivity. The exact
values and parameter fingerprints are in `selected_starts` and
`quantities[<design> selected objective]` in the [#440 handoff](../../../../analyses/fixed_reaction_reference/manuscript-handoff.json).
Paths in the following table are relative to
`analyses/fixed_reaction_reference/results/`.

| Display | Record and field |
|---|---|
| Main MEA species, interaction, fitted parameters, and full-precision supplement | `MEA/A.json.gz:endpoint.parameters, endpoint.coordinates, diagnostics.uncertainty`. Keep the independently fitted sodium-salt law. |
| Main receiver species and parameters, supplement parameters and bounds, AMP fixed-slope parameters and variance table | `{DEA,MDEA,AMP_free,AMP_fixed}/A.json.gz:endpoint, diagnostics, replay.rows`. Hold active bounds fixed. Scale the retained conditional standard errors by the square root of the responsive-row to all-row variance ratio. The residual variance factors are 1.18093995, 0.22924510, 0.11519787, 0.72394356 and 0.72944080 over 259, 136, 271, 207 and 209 degrees of freedom, respectively, in the order above. The 39 Kiepe pressures and three pure-water Kim pressures enter the objective and are omitted from the variance estimate under #420. |
| Main deviations, source and range tables, and amine summary | `E/MEA/replay.json.gz:rows,pressure_population,hot_wagner`, `MEA/off-window.json.gz:rows`, `display-replays/wagner.json.gz:rows`, `DEA/property-comparisons/selected.json.gz:rows`, `MDEA/properties.json.gz:rows` and `AMP_{free,fixed}/properties.json.gz:rows`. Loaded-fit AARDs are 11.34% MEA, 42.75% DEA, 4.39% MDEA and 10.82% AMP on 47, 90, 66 and 105 rows. |
| Objective totals, contributions, scales and starts | Each selected `A.json.gz:replay.rows.cost`, original declared scales and weights, and handoff `fit_attempts`, `<design> start distances` and `<design> admitted-start distances`. MDEA admitted two of 64 draws and its selected endpoint remains provisional. AMP fixed C and LHS-53 retain the second basin at 2741.260320. Blank numeric fields in a failed start denote unavailable values. |
| DEA confirmations and unresolved feed, MDEA finite and targeted screens, AMP screens and measured controls | `DEA/screen/selected/declared/summary.json.gz` gives four confirmed feeds, 32/41/42/43, and feed 31 unresolved. `MDEA/screen/selected/declared/summary.json.gz` gives 10,509 completed of 11,824 attempts, 80 descent attempts and no confirmation. Handoff keys `MDEA A phase 204-MPa` and `MDEA A phase 263-MPa` report unresolved. In `AMP_{free,fixed}/screen/selected/{native,supplied}/summary.json.gz` all 666 states complete without a descent for each fitting case and protocol. `C4 AMP_{free,fixed} selected experimental phase counts` report four unresolved and two without descent for free slope, three and three for fixed slope. The 2.037241 MPa worked-state controls are separate. |
| C1 consistency and the worked caloric example | `C1/*.json.gz` and handoff `C1 selected-*`, `C1 fixed-at-old-*` and daughter-inventory sum keys give signed discrepancies and numerical estimates for both identities. `display-replays/caloric-and-species.json.gz:reference_state` retains the heat, heat capacity and all fixed-reference checks. Use the existing basis offsets to present the R1 and R3 constants and fugacity terms on a common molality basis. The independently replayed bubble implementation values are in `display-replays/bubble-checks.json.gz:rows`. |
| Matched comparisons and published values | `MDEA <source> <unit> matched {AARD_percent,bias_percent}`, `C5 C7 corrected-Kamps matched AARD_percent`, `C7 corrected-Kamps additional row comparison:113`, `C7 Kuranov row-matched 82 AARD`, `MEA pressure Mamun2005 AARD_percent`, `MEA/hong-matched.json.gz` and the comparison identities of the Hong tables. The selected MDEA Kamps AARD is 11.93% on the common 27 and 14.76% on all 28. The added row stays outside the common-27 comparison. |
| MEA off-window, full-weight expansion and temperature bands | `MEA/off-window.json.gz`, `E/MEA/replay.json.gz`, `MEA/heat-comparison.json.gz` and `display-replays/{mea-comparisons,caloric-and-species,wagner}.json.gz`. The expanded fit is a historical tracking-reference sensitivity from #436. The band table reports historical AARD only where the population agrees. |
| Curves and point figures | The five MEA curve records `MEA/curves/{pressure,species,heat,density,mea-water}.json.gz` contain 2,211 available points and 47.10 s summed replay time. DEA uses the 275 isotherm points in `DEA/property-comparisons/selected.json.gz:curves` (24.49 s including the observation replay). MDEA and AMP measured-state figures use selected row predictions. The MDEA curve batches already retained by #440 took 19.80 s. AMP curve timings are not isolated in the receiver timer. The plotted MDEA–water law comes from `MDEA/A.json.gz:endpoint.parameters`, and the onset brackets come from the 73.50 s replay at `display-replays/mdea-binary-onset.json.gz`. The pressure-uncertainty figure propagates the selected weighted log-residual derivatives and responsive-row covariance to the 47 fitted pressures. |
| DEA methane and AMP worked-feed pressure | `display-replays/dea-methane.json.gz` retains the 30 Lawson states and the conditional maximum 0.317 MPa shift. `display-replays/AMP_{free,fixed}-bubble.json.gz` gives 1.883232 and 1.790874 MPa at the historical worked feed, respectively. |
| Salt osmotic residuals and historical AMP split plot | `salt.json.gz:differences` gives exactly zero maximum relative prediction change and zero relative AARD change for NaCl, NaHCO3, Na2CO3 and mixed salts, with six mixed state refusals preserved. The residual figure stays byte-identical. The AMP splits plotted are those of the named historical first fit. |

The [prose gaps](440-rebind-prose-gaps.md) locate the Writer changes. The
tracking-only bound profiles, calibration-restriction sequence, DEA binary
comparison, phase controls and four-case MDEA weight comparison retain their
historical interpretation. No new fit was run. The graphical abstract is
byte-identical to main.
