# Reaction-temperature study — recentered candidate adopted as exploratory incumbent

2026-09-03. The original screening record below used the earlier selected
bundle. The subsequent exploratory adoption is recorded in
`adoption-record.json`; the active values are in
`../selected-current-best-parameters.json`. Historical baseline results below
are not a replay of that later selection. The full candidate replay included
R1/R3 shifts omitted from the selected JSON; see `interpretation_correction`
in the adoption record. Its scores must not be attributed to the exact selected
vector. Future adoption must persist every scored shift or constrain omitted
shifts to zero before replay.

## Corrected scientific origin

The retained Engine wheel is
`40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805`;
the historical baseline parameter file was
`00049473d53c7e8088ef3e2dbbc6a1bab058f6dc4de963ee98936b4cd9bda25e`.
R1–R3 use the existing common-molality source conversion; R4/R5 origins come
from that selected parameter file, not from the state packet. The corrected
sparse baseline reproduces the retained selected-bundle heat predictions to
`1.1641532182693481e-9 kJ/mol CO2` maximum absolute difference.

## Design and sparse result

At the 313.15 K pivot, every ln K is preserved. For R1–R4,
`delta A = delta h/(R T_p)` and `delta B = -delta h/R`; for R5,
`delta a = delta h/(R ln 10)` and `delta b = -delta h/(R T_p ln 10)`.
The typed Engine reaction derivatives therefore receive the specified constant
reaction-enthalpy shift without changing the pivot equilibrium.

Eleven scenarios were evaluated: baseline and ±2.5 kJ/mol for R1–R5. Each
scenario requested 41 scalar targets (6 pressure, 29 speciation, 6 heat).
Thirty were common-evaluable across all scenarios: 2 pressure, 22 speciation,
and 6 heat. The remaining 11 rows are retained with their failure status, not
assigned artificial residuals. In particular, the common screen has no 120 C
pressure leverage and loses the selected Matin individual-MEA/MEAH+ state;
this limits identification despite the requested family/source coverage.

The objective gives equal weight to the three families, then equal weight to
source/temperature/species groups within a family and equal rows within each
group. Each family is scaled by its correspondingly weighted baseline RMS.
The first two SVD directions were retained; their coordinates were bounded to
±5 kJ/mol for the local linear least-squares proposal. This is a local search
bound, not a physical parameter-admissibility claim.

The proposed shifts, ordered R1–R5, are
`[-0.00055656, -4.27244586, -0.07336611, -3.58470585, 4.34634415] kJ/mol`.
The exact sparse weighted norm was `0.78042113`, versus `0.77852951` predicted
and `1.0` at baseline. No recenter was used. Sparse heat RMSE was
`12.21363818 kJ/mol CO2` over six intervals.

## Full-domain replay and stopping decision

The corrected candidate was replayed once over the full pressure/speciation
catalog and 40/80 C heat. The 120 C heat sequence was stopped after the pressure
replay exposed inadequate evaluability; no holdout result is inferred.

| Common evaluated cohort | Count | Baseline RMSE | Candidate RMSE |
|---|---:|---:|---:|
| Pressure, log10(predicted/observed) | 139 | 0.33435338 | 0.26720716 |
| Speciation, log10(predicted/observed) | 125 | 0.37018445 | 0.36639891 |
| Heat, 40/80 C, kJ/mol CO2 | 86 | 19.01939631 | 14.16330344 |

These paired-cohort improvements do not establish acceptance. Pressure
evaluability was only 139/161, including 18/39 at 120 C, compared with 161/161
in the retained baseline replay. The bounded candidate routing is not identical
to the baseline's stronger cross-temperature recovery, so this is an unresolved
solver-coverage limitation, not proof of physical inadmissibility. The candidate
is **not accepted**, and the requested complete 120 C heat holdout remains
unresolved. No second candidate, additional recenter, or promotion was attempted.

## Reproduction and retained evidence

Use the repository's pinned environment and cap BLAS/OpenMP threads to one.
The driver is `../../scripts/run_reaction_temperature_fit.py` and supports
`--self-check`, the default screen, `--candidate`, `--full`, `--groups`, and
`--summarize-partial`. Scenario and completed group caches avoid repeating
finished exact work. The run used at most three CPU cores. All task-owned
processes were stopped at closeout.

The self-check verifies selected reaction origins, pivot preservation, and
constant reaction-enthalpy shifts at 20/40/80/120 C. The retained
`full-validation-targets.csv` provides row-level replay evidence; screen and
candidate records retain their bounded shifts, weights, coverage, and
incomplete-holdout status. Full-validation aggregate metrics are computed only
on evaluated rows and must not be compared against a different cohort.

## Stage 0--2 driver repair, parity, and benchmark (2026-09-03, later)

The driver now uses one shared recovery policy (the retained baseline replay's
ordering: same-temperature anchor, cold packet start, cross-temperature
anchors, remaining anchors) for every family, deduplicates identical prepared
starts, caches each exact solve atomically under ignored `results/runs/`,
verifies the installed wheel in every mode, caps BLAS/OpenMP threads, and
records per-attempt wall time. Xu 2011 pressure rows are an independent
holdout and Kim et al. 2014 rows are excluded from fitting.

`parity-record.json` / `parity-targets.csv`: 17/17 states reproduce the
retained baseline to a maximum relative difference of 1.5e-10, including three
120 C pressure states recovered through cross-temperature anchors.
Detailed scenario caches and invalid trial runs are intentionally not retained
in the mergeable tree; the records and selected target tables above are the
reviewable evidence, and rerunning the driver recreates the omitted detail.


## Revised screen, recenter, full replay, and adoption (2026-09-03, evening)

Cohort changes: the three 120 C screen pressure rows are Jou 1995 states
(vle_obs_0227, 0228, 0232) and evaluate in every scenario under the shared
recovery policy; Xu 2011 pressure rows are an independent holdout and never
enter the objective; the fitted heat rows are six Kim--Svendsen 2007 calibration
intervals (Kim et al. 2014 is model-selection comparison only). The screen
retained 33 common targets (5 pressure at 80/120 C, 22 speciation, 6 heat).
Column norms per kJ/mol: R1 1.6e-5, R2 0.050, R3 0.0033, R4 0.034, R5 0.051;
singular values 7.5e-2, 2.6e-2, 3.8e-3, 6.9e-6, 7.0e-8. The bounded proposal
again sat on both +/-5 kJ/mol bounds, so the single permitted recenter was an
exact check of the unbounded two-direction solution:

| Proposal | R2 | R4 | R5 | exact weighted norm |
|---|---:|---:|---:|---:|
| bounded | -4.41 | -3.16 | +4.53 | 0.7530 |
| unbounded (adopted) | -8.20 | -4.81 | +8.42 | 0.6559 |

R1 and R3 shifts are below 0.3 kJ/mol and are carried only through the
retained directions. `sensitivity-check-record.json` shows native Engine
R4/R5 sensitivities agree with the finite-difference columns to at most 0.2 %
over 45 pressure/speciation rows.

Full replay under the same recovery policy as the retained baseline
(`full-validation-record.json`, `full-validation-targets.csv`), paired on
identical evaluated rows (`adoption-record.json`):

| Cohort | n | Incumbent RMSE | Candidate RMSE |
|---|---:|---:|---:|
| Pressure calibration, log10 | 143 | 0.3344 | 0.2366 |
| Pressure holdout Xu 2011, log10 | 18 | 0.3096 | 0.1901 |
| Speciation, log10 | 125 | 0.3702 | 0.3670 |
| Heat 40/80 C calibration, kJ/mol CO2 | 66 | 20.01 | 11.84 |
| Heat 120 C holdout, kJ/mol CO2 | 20 | 39.30 | 31.15 |
| Heat Kim 2014 comparison, kJ/mol CO2 | 27 | 16.84 | 10.71 |

Evaluability is 161/161 pressure, 129/131 speciation targets (incumbent 125),
and 113/113 heat intervals. Every 120 C pressure state evaluated. All adoption
rules passed (evaluability not below the incumbent, both held-out blocks
improved, no cohort degraded, interior solution), so
`results/selected-current-best-parameters.json` now carries the shifted R2,
R4, and R5 correlations (sha256 `568f7a5f...8524d` after storage-only JSON
compaction); the previous record
(`00049473...da25e`) is superseded and listed in
`results/parameter-record-history.csv`. Holdout use is logged in
`results/holdout-evaluations.csv`; both blocks have now been scored once.

Limitations that remain: the 120 C heat holdout still under-predicts by
18.8 kJ/mol on average; the shifts exceed typical source uncertainty for R2
and R5 and therefore compensate other temperature-dependent model deficiencies
(Born/permittivity temperature response) rather than correcting the source
enthalpies alone; speciation is essentially unchanged; this is an exploratory
incumbent under the repository's claim boundary, not an accepted packet.
