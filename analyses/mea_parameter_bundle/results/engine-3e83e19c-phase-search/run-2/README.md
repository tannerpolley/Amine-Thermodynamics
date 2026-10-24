# MEA finite phase search on Engine 3e83e19c

**The reported record resolves no descent at all 162 states. The comparison resolves descents at 54 of 162 states, comprising 143 descending trials.** Both fits complete every state and all 1458 scheduled trials. There is no unavailable pressure, unresolved trial or incomplete state, and no reported-fit falsifier. The uniform distinct-composition reduction produces 91 representative confirmation attempts for the comparison: 51 confirmed paths across 32 states and 40 unsuccessful attempts with retained numerical diagnostics. The reported fit has no descending trial to confirm.

These are finite-search numerical-verification results and model predictions. They do not establish global stability or physically validate liquid–liquid splitting. Independent delivered review and investigator promotion for manuscript use remain open; #215 owns parameter adoption.

## Correction of the selected-record dependency

The first census at commit `62cc2bd30fea8e43400bc47fc9235e924a9c9009` read `results/selected-current-best-parameters.json` seven times during one request. The claim in its original README and notebook that this file was not an input was incorrect. Its original [README](first-run-README.md), [provenance](../provenance.json), numerical records and hashes remain available. The current census is under `run-2/`; the original numerical files were not overwritten.

The old reads supplied correlation kind/source metadata, the coefficient comparison used to label selected versus candidate input, and the candidate temperature domains for R2, R4 and R5 (293.15–393.15 K). Reaction IDs are obtained from each request's equilibrium-constant metadata or R1–R5 row order; stoichiometry comes from its reaction matrix. R1 and R3 use the established source-correlation owner and 273.15–498.15 K interval. None of those equations or references changed.

The R2 and R5 coefficients differ between the old selected record and both #212 endpoints, but the first census already supplied each endpoint's own coefficient values. No calculation-entering value was replaced by an old-record value: the metadata and domains taken from the old record are identical in all three records. The [reaction inputs](reaction-input-diagnosis.json) retain all coefficients, metadata, domains and emitted Engine reaction records. Reaction enthalpy shifts are encoded in the endpoint coefficients by `fit_campaign.py:614` and `fit_campaign.py:621`; neither request normalization nor `verify_reference_calorics.record()` loads such shifts from the selected record.

`shared_evaluation.corrected_request()`, `_engine_reaction_records()`, `_reaction_specifications()`, `_parameter_domain()` and `_selected_reactions()` now accept the supplied mapping. `heat_evidence_170.request()` forwards it. Only calls without a mapping use the selected record. Explicit records keep the candidate label; passing a record does not adopt it for manuscript use. Equations, solver settings, trial starts, ceilings and admission checks are unchanged.

The [read-guard proof](dependency-proof.json) raises on every attempted open of the selected path. Both reported and comparison requests complete with zero open attempts and are exactly equal to the first calculation's requests. A changed temperature domain in a disposable copy reaches the Engine declaration. Requests and direct reaction helpers called without a mapping are unchanged, including the source-only reaction case. All 12 installed Engine files equal their pinned-wheel bytes.

The [comparison with the first census](comparison-with-first-run.json) checks all 469 raw reference, parent-state and representative-confirmation records. All thermodynamic values, solver diagnostics and classifications are exactly equal after excluding execution duration, output location and the parent-file hash that includes duration. The trial, count, outcome, state, point and confirmation tables are byte-identical. `phase-family.csv` differs only in its relative source paths; `reference-pressures.csv` differs only in timing. No numerical tolerance was needed for these equalities.

## Read-only check of #212 and #213

Both earlier issues used these helpers and therefore read the old selected record. This is a dependency defect, with no changed calculation input found for their retained fixed calculations. No fit or evaluation from either issue was rerun or changed. [The retained comparison](earlier-dependency.json) uses their reported/comparison display records and #213 start/endpoint. Substituting each record for the default selected record leaves every emitted Engine correlation, reaction stoichiometry, standard-state reference and temperature domain exactly equal. Only selected/candidate metadata changes in that disposable substitution. #213 start and endpoint have identical reaction coefficients.

- #212: `association_volume_refit_chain.py:123` saves the explicit fixed records and `:124` calls the retained `score()` function. `results/joint-recalibration-170/amendment-7/fixed-study/study.py.txt:200` loads them, `:201` builds the 307 rows with `fit_observations.stage6_rows()`, and `:203` replays them. `fit_observations.py:94`, `:101`, `:72` and `:29` normalize those requests through the shared helper. The loaded-density and carbon-free-density construction also reaches it at `fit_observations.py:246`, `:249` and `shared_evaluation.py:274`. The Arcis display at `engine_3e83e19c_refits.py:127` calls both `heat_evidence_170.request()` and `fit_observations.heat_items()` with each mapping.
- #213 (inspected read-only at merged commit `4e5e5f599c0a14253cae00fbbc7e87a34eee0de9`): `density_free_213.py:41` builds the base rows, `:42` replays them, and `:47` builds Arcis items through the same request and heat helpers before `:48` replays them. Its five free coordinates change interactions, leaving reaction laws and domains fixed at the #212 candidate. `fit_campaign.py:518`–`:524` defines the reaction coordinates; `:614`–`:625` writes the fitted laws and their enthalpy-shift record. New R2/R5 coefficients, including the shifts, were already consumed. This inspection verifies input equality, not a new numerical evaluation or a new physical validation.

## Records, basis and method

The [study README](README.md), [provenance](provenance.json) and [checked values](validation.json) retain the complete calculation. Every model and split uses Engine commit `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, wheel SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`. The installed Engine files were checked byte for byte against the wheel before calculation; no Engine source checkout was imported.

The reported record is [#212's second restricted endpoint](../../engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json), byte SHA-256 `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`. The comparison is [#212's refitted A6 endpoint](../../engine-3e83e19c-refit-chain/a6/run/fit/usable-budget-endpoint.json), byte SHA-256 `efb2a9abe3787410734394f5ee32e6eade42d7cb6f5ad23445a357423690b2f3`. Both use MEA association volume 0.036305439. Parameter bytes, runtime mappings, state lists and producers have separate hashes. The selected working-record file is not read by this corrected request construction; the first census had the dependency described below.

The feed is 9.7292821 mol MEA, 76.9751925 mol water and $9.7292821\alpha$ mol CO₂. Charged species remain liquid-only. For each of the 54 temperature–loading pairs, `diagnose()` independently starts a fixed-pressure liquid solve at 101325 Pa, then uses its composition and packing guesses for a free-pressure bubble solve with zero vapor amount. Both solves are retained. All 54 references pass the requested tolerance, finite-pressure and 1 Pa–10 MPa window checks, liquid-positive/vapor-zero amounts, raw residuals at most $10^{-10}$, nonnegative reduced-Hessian minimum and positive pressure–density derivatives. Reference pressures range from **6412.308582651815 Pa to 1768948.0817829045 Pa**, with largest absolute raw residual **3.9745984281580604 × 10⁻¹³**. The [54-row reference table](reference-pressures.csv) links each pair to its numerical diagnostics.

The grid uses temperatures 313.15, 318.15, 333.15, 353.15, 373.15 and 393.15 K; loadings $10^{-5}$, 0.05, 0.1, 0.2, 0.256, 0.3, 0.4, 0.5 and 0.6 mol CO₂/mol MEA; and pressure fractions 0.50, 0.80 and 0.95. Loading is outermost, followed by temperature and pressure fraction; indices run 0–161 without duplicated states. Both fits consume identical state and point-file hashes. All 162 states fall inside the 1 Pa–10 MPa candidate interval; 152 fall inside the 10–300000 Pa diagnostic interval. The observed-total-pressure indicator is defined for 81 states at 353.15–393.15 K (17 inside, 64 outside) and is null for the 81 lower-temperature states. It is not an admission check. The [state table](states.csv) retains every domain column.

Twelve concurrent same-temperature chains each search 27 ordered states, using `phase_family(..., continue_bubble=True)`, four liquid starts and five vapor starts. Existing recovery calls retain two attempts, at most 400 iterations per attempt and 800 per call. Reference construction and screening share 600 s wall / 3600 s CPU; confirmation starts a fresh budget with the same ceilings. Each reference, state and representative confirmation is limited to the smaller of 300 s and remaining stage wall time. No ceiling was reached, no numerical attempt was added and no process was terminated. Each process uses one numerical-library thread and runs at niceness 10.

## State and trial counts

A completed state has all nine returned successful trial optimizers and complete numerical evidence. A resolved descent still counts as completed evidence: the native `failed` classification denotes the descent, not a failed numerical calculation. Both fits return all 1458 trials and complete 162 states, with zero unresolved or unavailable states. The [324-row state reduction](phase-family.csv), [2916 trial slots](trials.csv), [counts](counts-by-temperature.csv) and [outcomes](outcomes-by-temperature.csv) preserve those distinctions. Tables directly answer these categorical questions; no continuous relationship is inferred between grid states.

| Fit | Temperature / K | States | Descent states | Descending trials | Completed | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| reported | 313.15 | 27 | 0 | 0 | 27 | 0 |
| reported | 318.15 | 27 | 0 | 0 | 27 | 0 |
| reported | 333.15 | 27 | 0 | 0 | 27 | 0 |
| reported | 353.15 | 27 | 0 | 0 | 27 | 0 |
| reported | 373.15 | 27 | 0 | 0 | 27 | 0 |
| reported | 393.15 | 27 | 0 | 0 | 27 | 0 |
| comparison | 313.15 | 27 | 10 | 27 | 27 | 0 |
| comparison | 318.15 | 27 | 10 | 24 | 27 | 0 |
| comparison | 333.15 | 27 | 9 | 23 | 27 | 0 |
| comparison | 353.15 | 27 | 9 | 26 | 27 | 0 |
| comparison | 373.15 | 27 | 9 | 25 | 27 | 0 |
| comparison | 393.15 | 27 | 7 | 18 | 27 | 0 |

## Uniform split confirmations

Descending trials are ordered by most negative split Gibbs change, then grouped within each state by phase kind, support and maximum composition difference at most $10^{-6}$. One representative per group receives one attempt with 400 iterations. Confirmation requires success, requested tolerance met, negative $\Delta G/(RT)$, raw residuals at most $10^{-10}$, positive reduced-Hessian minimum, positive amounts and positive pressure–density derivatives. Distinct confirmation paths are counted once.

| Temperature / K | Attempts | Confirmed paths | States with a confirmation |
|---:|---:|---:|---:|
| 313.15 | 15 | 7 | 6 |
| 318.15 | 15 | 4 | 3 |
| 333.15 | 15 | 7 | 5 |
| 353.15 | 17 | 9 | 5 |
| 373.15 | 17 | 15 | 8 |
| 393.15 | 12 | 9 | 5 |

All confirmations belong to the comparison fit. The 51 confirmed paths have $\Delta G$ from −7569.920533932512 to −0.7926816549017589 J on the stated feed basis. The [91-row split table](split-confirmations.csv) retains fit, state, temperature, loading, pressure, seed, success, admission, both Gibbs changes, and every confirmed phase's identity, support, amount (mol), molar density (mol/m³) and supported-species mole fractions. The 40 unsuccessful attempts retain their causes and raw results, with phase-quantity cells empty. Their diagnostics include vanished phases, coincident phases and a nonpositive reduced Hessian; no extra confirmation attempt is made. Failure to confirm does not erase a resolved descending trial.

## Numerical checks, timing and limits

The largest raw residual is $3.353761712787673\times10^{-12}$ for parent states and $3.467448550509289\times10^{-12}$ for confirmed splits, below $10^{-10}$. Retained checks cover state order, domain columns, complete trial identities, parameter/state hashes, composition grouping, split phase values and unchanged execution-time producer hashes. Every reference, screening state and confirmation returns within its bound; the longest item is 3.271364313 s.

Reference construction uses 6.551251094 s wall / 38.979783620 s CPU. The shared reference-plus-screening stage ends at 28.412972003 s wall / 244.768486133 s CPU; these cumulative values already include reference construction. Confirmation uses a fresh 19.893877184 s wall / 95.250929557 s CPU. Total measured calculation and reduction time is 49.210244071 s wall / 340.921808888 s CPU. The [stage calls](calls.json) and [total timing](timing.json) retain the measured values. The supervisor ran in transient user unit `issue214-phase-r2.service`; it completed normally using `systemd-run --wait --pipe`. The first launch stopped before numerical dispatch because the worktree lacked its retained-wheel storage link; [the command record](unit-command.json) retains that cause and the local correction.

The search is finite at specified states. The 81 states above 333.15 K extrapolate beyond the pressure-fit temperature range. Native numerical error estimates determine resolved descent; parameter, measurement and model-form uncertainty are not propagated. Neither absent descents nor confirmed model splits establish physical liquid separation, concentration transfer or absorber/stripper performance. Historical results retain their own records and are not acceptance targets for this new design. The selected parameter record, manuscript and generators remain unchanged. The notebook is validated and rendered only under `/tmp`; no preview service is controlled. The independent delivered review is still required.

Implementation: [phase_search_214.py](../../../scripts/phase_search_214.py), 144 gross added executable lines, plus 15 in [shared_evaluation.py](../../../scripts/shared_evaluation.py) and one in [heat_evidence_170.py](../../../scripts/heat_evidence_170.py), totaling **160/160** against base `0ee470579d3eaaad84c549db258a5fc2668a840b`. The 18 removed shared lines are replaced by supplied-mapping handling. No persistent test was added. [Change accounting](change-accounting.json) measures the complete issue change. The numerical Engine and `final_evidence` functions are unchanged.

The [working notebook](../../../joint-recalibration/index.qmd#phase-extension-201) is the presentation owner. The corrected result awaits independent delivered review and investigator promotion for manuscript use.
