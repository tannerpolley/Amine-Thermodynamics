# MEA finite phase search on Engine 3e83e19c

**The reported record resolves no descent at all 162 states. The comparison resolves descents at 54 of 162 states, comprising 143 descending trials.** Both fits complete every state and all 1458 scheduled trials. There is no unavailable pressure, unresolved trial or incomplete state, and no reported-fit falsifier. The uniform distinct-composition reduction produces 91 representative confirmation attempts for the comparison: 51 confirmed paths across 32 states and 40 unsuccessful attempts with retained numerical diagnostics. The reported fit has no descending trial to confirm.

These are finite-search numerical-verification results and model predictions. They do not establish global stability or physically validate liquid–liquid splitting. Independent delivered review and investigator promotion for manuscript use remain open; #215 owns parameter adoption.

## Records, basis and method

The [study README](README.md), [provenance](provenance.json) and [checked values](validation.json) retain the complete calculation. Every model and split uses Engine commit `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, wheel SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`. The installed Engine files were checked byte for byte against the wheel before calculation; no Engine source checkout was imported.

The reported record is [#212's second restricted endpoint](../engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json), byte SHA-256 `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`. The comparison is [#212's refitted A6 endpoint](../engine-3e83e19c-refit-chain/a6/run/fit/usable-budget-endpoint.json), byte SHA-256 `efb2a9abe3787410734394f5ee32e6eade42d7cb6f5ad23445a357423690b2f3`. Both use MEA association volume 0.036305439. Parameter bytes, runtime mappings, state lists and producers have separate hashes. The selected working-record file is not an input to this study.

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

The largest raw residual is $3.353761712787673\times10^{-12}$ for parent states and $3.467448550509289\times10^{-12}$ for confirmed splits, below $10^{-10}$. Retained checks cover state order, domain columns, complete trial identities, parameter/state hashes, composition grouping, split phase values and unchanged execution-time producer hashes. Every reference, screening state and confirmation returns within its bound; the longest item is 3.4400457800002187 s.

Reference construction uses 6.601900243 s wall / 39.093675594 s CPU. The shared reference-plus-screening stage ends at 28.259955173 s wall / 242.617018607 s CPU; these cumulative values already include reference construction. Confirmation uses a fresh 20.507284521 s wall / 99.688767694 s CPU. Total measured calculation and reduction time is 49.674454699 s wall / 343.210246179 s CPU. The [stage calls](calls.json) and [total timing](timing.json) retain the measured values. The supervisor ran in transient user unit `issue214-phase.service`; it completed normally and the wait used `systemctl --user is-active`.

The search is finite at specified states. The 81 states above 333.15 K extrapolate beyond the pressure-fit temperature range. Native numerical error estimates determine resolved descent; parameter, measurement and model-form uncertainty are not propagated. Neither absent descents nor confirmed model splits establish physical liquid separation, concentration transfer or absorber/stripper performance. Historical results retain their own records and are not acceptance targets for this new design. The selected parameter record, manuscript and generators remain unchanged. The notebook is validated and rendered only under `/tmp`; no preview service is controlled. The independent delivered review is still required.

Implementation: [phase_search_214.py](../../scripts/phase_search_214.py), 144 gross added executable lines against base `0ee470579d3eaaad84c549db258a5fc2668a840b`; no persistent tests. The script reuses the phase extension’s supervisor, reducer and confirmation owners through narrow source adaptation, and leaves the numerical Engine and `final_evidence` functions unchanged. See [change accounting](change-accounting.json).

The [working notebook](../../joint-recalibration/index.qmd#phase-extension-201) is the presentation owner. This result is not independently reviewed or promoted for manuscript use.
