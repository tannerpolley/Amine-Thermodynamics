# Stability-constrained MEA refit for issue 255 (stage 3): candidate evidence, not adopted

**Result.** Both starts reach one stable optimum inside the original wide bounds: the final set and the wide-bound fit. It has no resolved liquid-phase descent at any of 1903 enforced, 576 offset or 162 census states. It passes every acceptance rule against the final set, and its 307-row cost is **148.510546**, against **148.883260** for the final set replayed on the same inputs and wheel. The candidate is not the final set: the MEAH⁺ segment diameter leaves the narrowed #170/#212 bound (5.35 → 4.905 Å), and the bicarbonate–water interaction moves to its upper bound (0.727 → 1.0). MDEA shares that interaction and the R2 law; transferring both roughly doubles the MDEA pressure error, which adoption must resolve. Nothing here is adopted: `selected-current-best-parameters.json`, the Engine pin and the manuscript are unchanged.

The evidence is calibration and numerical verification. The stability requirement is a finite search at declared states, not a global stability certificate, and the downstream comparisons are fixed-parameter predictions, not independent validation.

## Method and inputs

The accepted design is in [design-probe/design.md](design-probe/design.md), published as the #255 stage-2 comment.
- **Engine.** `main` at `bc7794731e94be961d16028d3f4880c6718a93ad` (#1059 stability requirement, PR #1074), wheel SHA-256 `8b9609d4c8908d9397833988158f525c92dd28e3bcf7333f4c3b33c48db99069`. It is installed only in this worktree; the repository pin stays at `0d08dff9…`. Every JSON result records the wheel.
- **Objective.** The 307 a6 rows, roles, weights and scales; 16 coordinates with the a6 wide bounds; enthalpy-shift totals within ±10 000 J/mol.
- **Stability requirement.** Rows of `epcsaft.regression.stability` on an all-liquid parent at $P=c\,P^*_\text{bubble}$, with c = 1.05 and 3.0. The grid is 15/25/35/45 wt% MEA, 313.15–393.15 K, and loadings 10⁻⁵ and 0.025–0.6, plus the 108 census nodes at 30 wt%: 1908 states. The 5 states unavailable at either start are excluded, leaving 1903 enforced; they are re-evaluated at every endpoint and any descent there fails the candidate. At the primary, the four 25 wt% CO₂-free states at 313.15 and 323.15 K (both pressure ratios) stay unavailable, and the 45 wt%, 383.15 K, α = 0.3, c = 1.05 state is available with no descent.
- **Penalty schedule.** Exterior-penalty stages at s = 10⁻², then 3×10⁻³ (design §Primary fit). Every run ends with the design's retreat: on the straight segment from the stable anchor to the stage endpoint, scan t = 1, 0.99, … to the first admissible t, then bisect; the result is an admissible point near the endpoint, not the farthest one, because admissibility is not monotone in t. Variants with a stable start run only the 3×10⁻³ stage. Both primaries stopped after the s = 10⁻² stage under the design's stop rule (no descent at the endpoint), so only `stage-0/` exists for them.
- **Held-out checks.** 576 offset states (20/30/40 wt%, c = 1.5) and the stage-1 162-state liquid + vapor census.

The script is [`stable_refit_255.py`](../../scripts/stable_refit_255.py): `qualify | old-wheel-replay | fit <run> | assess <run> | select | extras <run>`. The downstream script is [`candidate_evidence_255.py`](../../scripts/candidate_evidence_255.py): `final | all | compare | present`. Both run from the repository root with the worktree `.venv` under `agent-heavy`.

**Qualification** ([summary](qualification/summary.json)). The new wheel reproduces the final and wide sets on identical inputs within 5.1×10⁻¹² (final) and 7.2×10⁻¹² (wide) per row, with relative cost differences of 2×10⁻¹³ and 6×10⁻¹⁴. This was run through `old-wheel-replay` with the 0d08dff9 wheel. Relative to the stage-1 replay, only the 4 heat-capacity rows move (4–9×10⁻⁴ relative), from the #260 water ideal-gas record (0e216fe). The final-set cost on current inputs is therefore 148.883260 (historical: 148.878939). Census: final set 0/162 descent, wide set 54/162 (matching stage 1), all complete.

## Runs

| Run | Start | 307-row cost | Retreat t | Iterations | Enforced / offset / census descent | Acceptance |
|---|---|---:|---:|---:|---|---|
| final set (reference) | — | 148.883260 | — | — | 0 / 0 / 0 | — |
| final start | final set | 148.510614 | 1 | 19 | 0 / 0 / 0 | pass |
| **wide start (primary)** | wide fit `efb2a9ab…` | **148.510546** | 1 | 90 | 0 / 0 / 0 | pass |
| (a) R2 held (#262) | final set | 148.520998 | 1 | 22 | 0 / 0 / 0 | pass |
| (b) joint chemistry + R4 shift + 10 Böttinger rows (#263) | primary | 148.263082 | 0.98182 | 34 | 0 / 0 / 0 | pass |
| (c) #261 data roles (sensitivity only) | primary | 148.688351 | 1 | 14 | 0 / 0 / 0 | pass |

Both primary starts agree within 0.023 optimizer scales on every coordinate ([final](final/assessment.json), [wide](wide/assessment.json)). [primary.json](primary.json) applies the lower-cost rule and selects the wide-start endpoint: outcome A. Neither endpoint is near the final set:

| Coordinate | Final set | Primary | Change / optimizer scale |
|---|---:|---:|---:|
| MEAH⁺ segment diameter / Å | 5.35 | 4.90455 | −4.45 |
| MEAH⁺ dispersion energy / K | 177.893 | 199.707 | +2.18 |
| carbamate segment diameter / Å | 4.86611 | 5.32 | +4.54 |
| carbamate dispersion energy / K | 207.217 | 183.001 | −2.42 |
| bicarbonate–water k | 0.72706 | 1.0 (upper bound) | +27.3 |
| carbamate–water k | −0.00366 | −0.01300 | −0.93 |
| MEAH⁺–water k slope / K | −41.620 | −35.314 | +0.63 |
| R5 aₖ / K | 3354.10 | 3293.61 | −0.76 |
| R2 total enthalpy shift / J mol⁻¹ | −1363.93 | −620.83 | |

Six coordinates end on bounds: MEAH⁺–water k (−0.5), bicarbonate–water k (1.0), carbamate–MEAH⁺ k (−1), both Born diameters (5 Å) and the R5 total shift (+10 000 J/mol).

**Where the stability requirement was binding.** The final-start fit ends with stability cost 0 ([final/stage-0/fit.json](final/stage-0/fit.json)); its four retained stability transitions are trial-minimizer changes at two states that stay without a witness, so no resolved descent was met along the path. From the final set, the requirement was therefore not binding: what held the cost at 148.883 was the narrowed #170/#212 bounds (the MEAH⁺ segment diameter sat at its 5.35 Å bound). About 0.004 of the 0.373 cost gain comes from the input change instead: the final set's own fit, on the stage-1 inputs, cost 148.879, and #260 later changed 4 heat-capacity rows. Lifting them gives a lower-cost local optimum that happens to be stable. From the wide start (unconstrained 148.2156, 1207 descent states), the penalty moved the fit out of the unstable basin to the same optimum. Relative to that unstable optimum, stability costs +0.295 in the 307-row cost. The outcome-A test uses the current-input reference 148.883260 with the relative margin 10⁻⁶; the near-final test uses one optimizer scale per coordinate (enthalpy-shift coordinates are not part of it).

The final-start fit has no `workers` field: it used `os.cpu_count()` = 32. A first wide-start attempt was stopped after 4.5 h of memory thrash caused by concurrent builds ([log](logs/fit-wide-attempt-1-stopped-under-memory-thrash.log)). The retained wide run sizes its workers from free memory (32 at launch). Worker count does not change the calculation.

## Acceptance against the final set (same wheel and inputs)

| Group | n | Final set AARD % (within 2s) | Primary | Rule |
|---|---:|---:|---:|---|
| fitted CO₂ partial pressure | 47 | 11.863 | 11.788 | rise ≤ 2 points |
| Kiepe pressure | 39 | 2.667 | 2.667 | rise ≤ 2 points |
| fitted phase mole fraction | 94 | 7.103 | 7.114 | rise ≤ 2 points |
| restored species | 7 | 9.002 | 8.963 | rise ≤ 2 points |
| Jakobsen ratio | 6 | 17.514 | 17.036 | rise ≤ 2 points |
| loaded density | 47 | 0.177 (44) | 0.162 (46) | count kept; AARD/RMSE ×0.916/×0.902 |
| CO₂-free density | 5 | 0.028 (5) | 0.028 (5) | ×1.015/×1.015 |
| fitted heat of absorption | 8 | 1.877 (8) | 1.899 (8) | ×1.011/×1.001 |
| heat capacity | 4 | 2.846 (3) | 2.771 (3) | ×0.974/×0.979 |
| Cai MEA–water VLE (reported only) | 50 | 1.480 (36) | 1.480 (36) | — |

Variant (b) is the only run that raises a pressure group materially (+0.674 points, fitted pressures), and it is the only run with all 47 loaded densities within 2s. R5 keeps its original total-shift bounds (owner, 2026-11-08); the final set and the primary sit at the +10 000 J/mol bound, so (b) cannot follow #263's small upward R5 move (+156 J/mol).

For variant (c), the design scores criterion 2 on its 57 fitted pressure rows, which replace the 47: 13.474 % for the final set and 13.707 % for (c), +0.23 points, which passes ([extras](pressure-roles-261/extras.json)). `assess` scores the 307 standard rows for every run, so the table entry for (c) uses the standard 47 pressures (+0.29 points).

**Variant extras.**
- [joint-chemistry/extras.json](joint-chemistry/extras.json): the 353 K carbamate excess (largest Böttinger 063–067 relative error) is 26.33 % for the final set, reproducing #263's baseline; 25.89 % for the primary; and **24.94 %** for variant (b). The R5 law against Hamborg's law at his temperatures (compared, not fitted; #263 used it in the same convention) has an RMS ln K difference of 1.184, 0.761 and 0.881 respectively.
- [pressure-roles-261/extras.json](pressure-roles-261/extras.json) gives AARD for each set (final / primary / variant c):

  | Rows | Final set | Primary | Variant (c) |
  |---|---:|---:|---:|
  | standard 47 fitted pressures | 11.86 % | 11.79 % | 12.15 % |
  | #261's 57 candidate rows | 13.47 % | 13.42 % | 13.71 % |
  | 106 Aronu concentration rows | 38.85 % | 36.17 % | 34.91 % |
  | 89 rows above 333.15 K | 20.04 % | 19.78 % | 19.64 % |

  Variant (c) runs on [spec-261/](spec-261/study.toml), #261's study re-pinned to the current caloric record (path prefixes and two hashes only).

## Downstream rerun on the primary candidate (candidate evidence)

The producers listed here were rerun twice on the new wheel, once on the final set ([evidence/final/](evidence/final/)) and once on the candidate ([evidence/candidate/](evidence/candidate/)). Not rerun: the #212 conditional uncertainty, the #214 phase-family export (both recomputations belong to adoption), and `generate_figure_data.py` (below). The producers are the A7 selected-assessment producer and point-data reduction, the model curves, Kim 2007, the #268 density comparison, the #264 heat capacity and the #267 MDEA transfer. Retained producers are copied with path, record and hash substitutions only ([producers/](evidence/candidate/producers/)).

The final-set rerun reproduces the retained values:
- the 462 state targets, 210 densities, 22 heats and 10 carbonate shares within 10⁻¹²;
- the 4 Cp rows within 2.2×10⁻⁵, which is the #260 record;
- all 31 curve references, with curves within 2.1×10⁻¹²;
- Kim within 2×10⁻⁹;
- the #264 and #268 group metrics exactly;
- the MDEA heats within 2×10⁻¹³ relative.

[evidence/comparison.csv](evidence/comparison.csv) lists all 345 same-input differences. The main ones (final set → candidate):

| Quantity | Final set | Candidate |
|---|---:|---:|
| canonical pressures (159), AARD | 20.55 % | 20.27 % |
| packet pressures (79), AARD | 15.46 % | 15.00 % |
| 15 wt% transfer (33): AARD; mean ln(calc/obs) | 29.49 %; −0.205 | 33.89 %; −0.002 |
| 45 wt% transfer (37): AARD; mean ln(calc/obs) | 56.04 %; +0.149 | 44.53 %; −0.051 |
| Wagner near 353 K (11), AARD | 22.19 % | 23.72 % |
| carbonate share, mean calc/obs (10 rows) | 0.073 | 0.021 |
| Kim 2007 semi-differential (53), RMSE | 6.12 kJ/mol | 6.30 kJ/mol |
| Han loaded density above 353 K (20), mean error | −8.84 kg/m³ | −6.02 kg/m³ |
| Han loaded density to 353 K (30), mean error; RMSE | −2.70; 3.23 kg/m³ | −0.26; 5.15 kg/m³ (α = 0.56 rows rise ≈ +10) |
| #264 broad Cp (51), AARD | 2.443 % | 2.391 % |
| Hilliard Cp, CO₂-free 318.15 K | +5.53 % | +5.43 % |
| Arcis heats (14), RMSE | 8.12 kJ/mol | 8.09 kJ/mol |
| MDEA Xiao pressure (20), AARD, A3 / B1: k only; k and R2 | 20.4 / 28.3 % | 53.2 / 58.9 %; **52.9 / 58.6 %** |
| MDEA Ermatchkov pressure (88), AARD, A3 / B1: k only; k and R2 | 26.2 / 19.1 % | 51.1 / 40.7 %; **52.5 / 42.0 %** |
| MDEA heat, A3 333.15 K, 60 wt%, 1.121 MPa: k only; k and R2 | −76.27 kJ/mol | −83.49; −82.81 kJ/mol |
| MDEA heat, B1 388.71 K: k only; k and R2 | −64.13 kJ/mol | −82.28; −82.47 kJ/mol |
| MDEA heat, B1 333.15 K, 60 wt%, 1.121 MPa | unavailable (Engine #1073) | unavailable (Engine #1073) |

Pressure curves change by at most 7.2 % and density curves by at most 10.8 kg/m³ (1.0 %). Integral heat changes by at most 0.13 kJ/mol. Species mole fractions change by less than 3×10⁻⁴ absolute; relative changes reach 30 % for MEAH⁺ and 75 % for carbonate on small values (carbonate below 1.3×10⁻⁵) ([figure](evidence/candidate-comparison.png), [plotted values](evidence/candidate-comparison-plotted-values.csv)). MDEA shares two things with the MEA record: the bicarbonate–water k, in its parameter documents, and the R2 law (CO₂ + 2 H₂O ⇌ HCO₃⁻ + H₃O⁺), frozen in `analyses/mdea_mea_workflow/inputs/probe-reaction-reference.json`. The rerun asserts that this frozen law equals the final set's completed R2 law, then substitutes the candidate's ([r2-laws.json](evidence/mdea-transfer/r2-laws.json)). The k-and-R2 case is the adoption consequence; the k-only case isolates the interaction, which carries almost all of the change. MDEA's own reactions and other components are unchanged.

## Canonical VLE hash (#248)

[canonical-vle-hash-check.json](canonical-vle-hash-check.json) compares the old `a4f9e3c0…` CSV (6d3137c) with the current `d5cd6ea0…` (177df00, #152). Of 327 rows, 119 changed, mostly in metadata. Among the columns `generate_figure_data.py` reads:
- `vle_obs_0149` (Hilliard 2008, 59.945 °C, α 0.565) joined the active view;
- four Xu 2011 rows changed rounded temperature: 0271 and 0272 from 100 to 101 °C, 0287 from 120 to 121 °C, and 0288 from 120 to 121.8 °C (122 °C after the producer's rounding).

No fitted row changed. The paper-evidence observation groups are byte-identical to A7's, because they come from the frozen packet. `generate_figure_data.py` is re-pinned to `d5cd6ea0…`. It is not run for the candidate, because it asserts the adopted incumbent and writes the tracked notebook figure outputs. The paper reads the paper-evidence package and model curves, which are rerun here.

## What adoption would change

- **Parameter record.** `results/selected-current-best-parameters.json` and `analyses/solvent_specification_mea/inputs/endpoint.json` would change from `00e77608…` to the candidate bytes [evidence/candidate-parameters.json](evidence/candidate-parameters.json) (`f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97`, the same mapping as [wide/candidate.json](wide/candidate.json)). Their hash pins would follow: `MEA.toml`, `pressure-transfer-261/study.toml`, `tests/test_source_corrections_152.py`, `check_a7_selected.py` and `parameter-record-history.csv`.
- **Engine pin.** `0d08dff9…` → `8b9609d4…` in `pyproject.toml`/`uv.lock` and `shared_evaluation.ENGINE_WHEEL_SHA256`, from Engine `bc779473`.
- **Displays.** Every input listed in the [paper-evidence inventory](../engine-3e83e19c-paper-evidence/README.md#displayed-input-inventory) would be regenerated: parameter, interaction and reaction tables; fitted-row statistics; figure point data; model curves; heat, density, Cp and carbonate tables. Conditional uncertainty and the phase-family export would need recomputation. The notebook renderers would follow: `render_parameter_tables.py`, `render_regression_overview.py`, `analysis.yaml` and `notebook.qmd`. Manuscript numbers would change too (#259).
- **MDEA.** The MDEA application shares bicarbonate–water k = 0.727 and the frozen final-set R2 law. Adoption must decide whether MDEA follows the MEA values, with the pressure degradation above, or these are decoupled. This is a scientific decision for the owner, outside this issue's scope.

## Limits

The stability evidence is a finite Full search at declared states. Liquid-parent states test liquid–liquid stability; the below-bubble liquid + vapor topology is checked only by the census. The endpoints are local optima from two starts, and six coordinates are on bounds. Acceptance rules come from the repository's limitation studies, not from published practice. The 15/45 wt% transfer AARD, the 353 K carbamate excess, the 318 K Cp offset and the carbonate share are not closed by this refit. The MDEA heat at B1, 333.15 K stays unavailable under Engine #1073.

## Execution record

[logs/](logs/) keeps every attempt:
- `fit-final-attempt-1-reduction-crash.log`: after the first final-start fit, the endpoint comparison paired the 307 data values with predictions that also held the appended stability rows (`zip() argument 2 is longer`). The stability predictions are now reported separately; the fit was rerun.
- `fit-wide-attempt-1-stopped-under-memory-thrash.log`: stopped after 4.5 h of swap thrash from concurrent builds; restarted with workers sized from free memory.
- `fit-joint-chemistry-attempt-1-invalid-setup.log`: the Engine refused the setup (R5 tied declarations and starts disagreed) because the Böttinger rows were built from the specification's stored record instead of the run's start record; the driver then failed reading reactions from the refused fit's empty chart (`zip() argument 2 is shorter`). Fixed in `bottinger_targets`, and the driver now reads reactions only from a chart with physical values.
- `fit-pressure-roles-261-attempt-1-hash-pin.log`: #261's study pinned the pre-#260 caloric record; replaced by the re-pinned [spec-261/](spec-261/study.toml).

## Files not retained

[.gitignore](.gitignore) excludes regenerable solve caches (`curve-runs/`, `selected-assessment/evaluation/`), resume checkpoints (`stage-*/fit-native.json`, which the retained `fit.json` duplicates), and `selected-assessment/{observation-groups,state-inputs}.json`. The last two are byte-identical to the retained `joint-recalibration-170/amendment-7/selected-assessment` copies and are rewritten by the producer's inventory step.
