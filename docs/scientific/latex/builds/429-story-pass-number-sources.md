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
| Worked split: Gibbs decrease, error, state | 0.0188 mol, 2.8e-9, 30 wt %, 393.15 K, 0.700 mol/mol, 1.212 MPa; mole fractions 0.100 / 0.028 | `analyses/amp_transfer/results/refit-306/summary.json` and the supplement's worked-split table (unchanged values, moved into the main text) | not checked |
| Split domain | 26.8–30.0 wt %, loadings 0.40–0.97, six at measured states | AMP split classification states (values already in the supplement) | not checked |

## Controlled MDEA transfer (abstract, Section 4.3, Table 8, conclusions, highlights)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| k values | 0.7650, 0.1325, 1.0 | `analyses/mdea_mea_workflow/results/shared-bicarbonate-417/profile.json.gz` | checked |
| MEA objective rise; allowance | 1.023, 0.024; 1.3987 | same; `MEA/paper-evidence-341/uncertainty/profiles.json` (largest `delta_cost`) | checked |
| Fitted Kuranov total P (66) | 20.1 → 11.2 % (20.09, 11.18, 20.18) | `shared-bicarbonate-417/mdea-comparison.json.gz:Kuranov.original` | checked; table generated |
| Pressures outside the objective (175) | 25.8 → 33.4 % | same, `all pressures not fitted` | checked |
| Unfinished searches; confirmed splits | 1099 → 1245; 0 → 2 | `shared-bicarbonate-417/mdea-search-readback.json`; MDEA `summary-row.json` | checked |
| Correlations of the interaction | 0.960, −0.974 | `MEA/paper-evidence-341/uncertainty/covariance.json` (unchanged) | checked |

## MDEA phase behavior (Section 4.4, Table 10, conclusions, supplement)

| Quantity | Displayed | Retained source | Check |
|---|---|---|---|
| Fixed pressure | 262.862 MPa (262.9) | `analyses/mdea_mea_workflow/results/phase-search-421/fixed-pressure.json:P_Pa` | checked |
| Gibbs decrease; numerical error | 1.394e-3 (1.39417e-3); 7.6e-10 (7.60e-10) mol | same, `attempts[0]` | checked |
| Moles in the denser liquid; densities | 4.4 % (4.387 %); 22214, 25053 mol/m³ | same, `attempts[0].amounts_mol`, `densities_mol_m3` | checked (shares) |
| State of the earlier split | 363.15 K, 78.62 wt %, 1.368 mol/mol, 1.05 × bubble pressure | same, `T_K`, `feed` (unchanged prose values) | not checked |
| Assigned pressures at the 27 states | 0.100–4.190 MPa | `phase-search-421/` 27-state record | not checked |
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
| Fitted MEA p(CO₂) temperature range | 313–333 K | `MEA/paper-evidence-341/paper-evidence/fitted-rows.csv` (Table 2 shows 313.00–333.15) | table generated |
| Cai temperatures at or above 370 K | 22 of 25, up to 431.85 K | same | table note generated |
| Horstmann isotherm | 365.15 K, 42 pressures | `reactive-refit-425/comparisons.json` | table generated |
