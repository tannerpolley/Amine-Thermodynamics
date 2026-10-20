# A7 adopted working record and retained paper evidence

The owner adopted the A7 second restricted endpoint as the repository's
selected working record on 20 October 2026 under
[#196](https://github.com/tannerpolley/Amine-Thermodynamics/issues/196), following
[#170 acceptance](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6298116916).
The selected file is byte-identical to
`../joint-recalibration-170/amendment-7/restricted-2/fit/usable-budget-endpoint.json`,
document version 2, SHA-256
`e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e`.
No version bump, fit, Engine differentiation or additional model calculation
was used to produce this package. The separate default-path reproduction is
the only new Engine evaluation for adoption.

This is the owner's working-record choice, not physical validation. The
manuscript remains on the retained heat F1 inputs pending Stage 3; A7 has not
been promoted for manuscript or absorber/stripper use. Delivered review of
this adoption remains with the orchestrator.

## Numerical reproduction

`default-replay/summary.json` reports 153 distinct identities, all finite and
available, with worst relative difference **8.392969848994369e-16**, below
1e-10. `comparison.json` preserves every value, identity and conversion unit;
`predictions.json` preserves availability and numerical diagnostics;
`input-hashes.json` binds the selected record, endpoint, specification, inputs,
wheel and check script. Hashes refer to raw file bytes, including compressed
packet bytes.

The fresh process called `shared_evaluation.parameter_mapping()` without a
path, then `fit_observations.rows_for(spec, mapping, 'base')` and `replay` for
the common 149. Packet pressures are Pa and species values are mole fractions;
Vinjarapu assessment kJ/mol values are multiplied by 1000 for comparison with
Engine J/mol. The four declared Hilliard Cp rows call the existing `cp_check`
producer at their analytical feeds, pressures and 1e-6 unloaded proxy. The
helper Cp is multiplied by helper-feed mass divided by parameter-document
feed mass, as in the retained assessment, to obtain kJ/(kg K). The metric is
`abs(new-reference)/max(abs(new),abs(reference),1e-300)`.

The replay used Engine merged commit
`8298c6029ebb8b467929badc4a223c580ec591ab`, wheel SHA-256
`8897a0caab9f2508ed642f42c8b5226957fbe7035ed7bfdad71e4166798785b3`,
numpy 2.5.4 and scipy 1.18.1, through the owner-specified A7 interpreter.
`default-replay/command-time.json` records **10.99 wall-s / 10.84 CPU-s**.
The wall time exceeded the 5 s estimate; no missing-quantity allowance was used.

## Package contents and reconciliation

`scripts/reduce_a7_evidence.py` is the single reduction owner. It reads retained
A7 values and uses `calibration-misfit/refit.py:identifiability` for covariance;
it executes no Engine solve or differentiation. `input-hashes.json` binds each
input by raw-file SHA-256, including the endpoint, fit specification, native
result, chemistry-coordinate record, starting metadata and phase-family rows.
Copied CSV and JSON files retain their bytes. Selected CSV views preserve
their source field strings; derived objective statistics use full-precision
retained values. Objective costs are summed with `math.fsum`.

| File | Values and basis |
|---|---|
| `fitted-rows.csv` | All 307 replay rows joined by identity to native quantity declarations; observed, predicted, scale, weight, residual, weighted residual and cost |
| `fit-summary.json` | Group and common-149 subgroup costs/AARDs, 12 iterations, six bound indices, 16 named scientific-coordinate values, Engine and gate score |
| `state-targets.csv`, `state-summary.json` | All 462 state-target rows and original cohort summaries, state identities and availability |
| `states-excluded.json`, `states-unavailable.json` | Original exclusions and availability accounting; three canonical states above 393.15 K remain inadmissible |
| `pressure-figure-data.csv`, `species-figure-data.csv` | 79 packet pressures and 131 packet species rows; retained `heat-final-170` field meanings, Pa and mole fractions |
| `canonical-pressure.csv`, `wagner-pressure.csv`, `transfer.csv` | 159 canonical, 23 Wagner and 70 transfer pressures from the same state table |
| `pool-figure-data.csv` | All 19 report-only Matin bicarbonate/carbonate pools; none enters the objective |
| `heat.csv` | All 22 Vinjarapu/Arcis rows, joined to `heat-rows.json` by record ID, with `uH_J_per_mol_CO2`, role, units and source row |
| `density.csv`, `cp.csv`, `carbonate-share.csv` | All 210 densities, four Cp states and ten carbonate shares, copied without rounding or a volume translation |
| `high-temperature-comparison.csv` | Original 100–120 °C cohort statistics after complete membership and AARD reconciliation against the state rows |
| `phase-family.csv` | 73 A7 and 73 A6 classifications, resolved-descent counts and state coordinates, from the retained reductions and point records |
| `conditional-uncertainty.json`, `conditional-standard-errors.csv`, `conditional-correlations.csv` | Named coordinate map, signed transformations, ties, free spectrum/rank, variance factor, errors and correlations |
| `summary.json`, `verification.json` | Unchanged retained assessment and its numerical checks; their historical task-completion wording describes the original assessment |
| `predecessor-f1.json` | Pointers and hashes for F1 parameters, original result tables/Engine record and the bounded 8298c602 transfer check |
| `consumer-inventory.json` | Source hashes for the inspected default-consuming commands and historical guards; none was run or modified |

The eight disjoint objective groups reconcile to **307 rows** and total cost
**148.90525398237165**, agreeing with the retained gate score and native result
within 1e-10 relative. Each replay cost also reconciles with
`0.5 * weight * residual**2`. The common-149 subgroups partition its rows and
are not additional objective contributions.

| Group | Rows | Cost |
|---|---:|---:|
| Common 149 | 149 | 23.86596394718697 |
| Seven restored species | 7 | 2.450296383185741 |
| Jakobsen amount ratios | 6 | 13.117059154169253 |
| Loaded densities | 47 | 0.5657514833247265 |
| CO₂-free densities | 5 | 11.611171058081595 |
| Cai | 50 | 91.9077547440675 |
| Kiepe | 39 | 0.0006790194987316589 |
| Cp | 4 | 5.386578192857118 |

Common-149 pressure/species/heat costs are
5.983407588690508 / 16.669083897497224 / 1.2134724609992413.
Pressure/species AARDs are 11.860789024706285% / 7.103578681500922%.
The state reduction checks all 462 distinct `(kind, identity, target)` entries,
every cohort's full membership and AARD before producing comparison views.
Canonical and packet views overlap; their rows are not independent additions.

## Conditional uncertainty

The retained 307-by-16 weighted optimizer Jacobian is mapped in declaration
order into named scientific coordinates. Column slopes are the declared
scales, with the negative source-to-native sign for R5 A. R5 A is reported
before its enthalpy shift; its origin and bounds subtract the inherited R5
shift divided by `R ln(10)`. Total R2/R5 enthalpy-shift values and bounds add
the inherited shifts. The serialized R5 A is checked against unshifted A plus
the total shift divided by `R ln(10)`. Packing and Debye–Hückel ties are checked
against the named endpoint fields. The 20-entry native physical vector is
never zipped to the 16 declarations.

Optimizer-bound indices **[1, 3, 5, 7, 8, 11]** are fixed. The ten free columns
have **rank 10** using the campaign relative singular-value cutoff **1e-14**
on the scientific-coordinate weighted Jacobian. Their spectrum is retained;
no regularization is used. The variance factor is
**1.0027289830464732 = rᵀr/(307−10)**, with 297 degrees of freedom.
The existing covariance owner calculates standard errors and correlations;
all returned values are finite. Bound coordinates have no symmetric error.

These errors condition on the residual weights, fixed inputs, active bounds
and local linearization. They do not establish independent-error measurement
uncertainty, parameter uniqueness or prediction intervals. AARDs across a
mixed objective group are arithmetic relative-error summaries; property
comparisons use the named property subgroups and their original units.

## Preserved history and limits

The three 353.15 K loaded-density failures remain failures accepted with
disclosure: Amundsen state 081 (−2.2832s), Hartono α 0.29 (−2.0550s) and α 0.39
(−2.4317s). Amundsen's exact high-temperature/loading source-uncertainty
boundary remains unresolved (source pp. 3099–3100, per-row locators retained).
Density residual scales are not uniformly measured uncertainties. Five
Amundsen loading-0.4 source-conflict rows remain excluded from the objective
and gate. Non-fitted comparisons preserve their source-state basis and
data-access history.

The phase evidence is the finite 73-point family at 313.15–333.15 K and
loading 1e-5–0.5, not a stability certificate. Both restricted fits are single
local fits from one start. The bounds were sampled, not certified. Neither
these comparisons nor the conditional errors extend process-use qualification.

F1 stays predecessor evidence with original parameter, Engine and source-state
identities. The 8298c602 transfer check establishes agreement within 2.9e-12
relative for its named 152 F1 quantities only; it does not qualify all retained
F1 results on the current wheel. Historical guards and outputs remain intact:
best-in-slot campaign, Born-permittivity study, direct-enthalpy calorimetry,
temperature reanchor 140, concentration transfer 137,
`figure-calculation-record.json`, `compare_engines.py`,
`calibration-misfit/candidate.py`, `density-current-record-123`, `cp-unloaded-161`
and the selected-path case in `model-d/born-form-diagnosis`. No handoff zip was
created. Future calculations by the eleven unpinned commands listed in
`consumer-inventory.json` use A7; retained outputs are not rerun or relabeled.

## Presentation, checks and compute

The two existing notebook renderers now consume this package and assert identity
against the accepted A7 endpoint. Current figures and table provenance go to
`figures/a7_regression_overview/output/`; F1 figures remain at their original
paths. The renderers format values only and execute no model. Notebook
navigation metadata changes only the two renamed current-result headings so
its sidebar links and required validation agree with the A7 presentation.

Repository tests pass: **76 tests and 17 subtests**. The A7 interpreter lacks
pytest, so the authorized `uv sync --locked` and worktree `.venv/bin/python -m
pytest tests -q -p no:cacheprovider` path was used. Test output and measured
timing are in `checks/`.

`analyses/manuscript.py validate analyses` passes. The full
`analyses/render.sh --profile presentation` command stops on the historical
`reactive_epcsaft_parameter_evidence` readiness-summary checksum mismatch.
The orchestrator identified it as pre-existing on main since `aa20f49`
(2026-10-18): current hash `118a22a2…`, expected `802dae17…`, unrelated to #196,
and authorized the direct MEA notebook render through the native question tool.
The failed command output is retained at `checks/notebook-render-output.txt`.
No historical checksum or result was changed.

The authorized fallback passes:
`cd analyses && quarto render mea_parameter_bundle/notebook.qmd --to html --profile presentation`,
using the owner-specified Quarto environment. Its output is
`analyses/_site/mea_parameter_bundle/notebook.html`;
`checks/notebook-direct-render-output.txt` preserves the result. The always-on
preview service was not started, stopped or restarted. Historical figure,
heat, thermal and notebook certification records remain unchanged. Strict
certification, `refresh_results.py`, absorber packaging and bundle Snakemake
were not run. Manuscript freshness checks concern retained LaTeX inputs and
do not establish A7 adoption.

All numerical check calls, including the first reduction and its final
scientific-coordinate spectrum update, are charged to
`../joint-recalibration-170/amendment-4/compute-ledger.json` with their retained
GNU timing files and outputs. The adoption adds **40 rounded-up wall-s /
38.74 CPU-s**, leaving **3,267 wall-s / 68,340.04 CPU-s**. No missing-quantity
allowance was used. Rendering and reporting are outside the ledger's compute
definition.

The executable changes replace F1 assumptions in the existing table and
figure renderers, add one explicit default-path reproduction and one retained
value reduction, and update the active test pin. Campaign code is unchanged.
Against base `5d5735c`, the corrected change adds 395 lines in executable files, including blanks and comments: replay 73, reduction 213, parameter renderer 66, and figure renderer 43. This is below the approved 500-line ceiling. The filtered nonblank, non-comment count is 367 and is supplementary. Tests add one line separately; deletions do not offset additions.
The change-accounting results and file checks are retained in `checks/`.
