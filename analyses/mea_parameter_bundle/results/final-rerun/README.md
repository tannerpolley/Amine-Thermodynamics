# Issue 154: stopped, incomplete final rerun

This directory is **not the completed final evidence suite**. Ten optimizer runs
(F1–F5, two starts each) converged; the two F6 jobs stopped in input verification,
before anchors, native state evaluation, or `regression.fit`. No optimizer was
retried, no extra start was added, and no parameter record was adopted.

## Retained fitted values

`fit-summary.json` retains both starts, pressure/species costs, fitted coordinates,
active bounds and relative start-cost differences. `fit-targets.csv` retains all
native predictions and weighted residuals; `fit-aard-by-source-species.csv`
retains source/species AARDs with positive-observation/prediction denominators.
F1–F3 have 141 targets (47 pressure, 94 species); F4–F5 have 159 (47 pressure,
112 species), at 83 states. All native observation results were Available and
retained residuals/predictions were finite. These native results have **not**
been checked by the required independent replay or per-state checks.

| Problem | Lower-cost start | Pressure cost | Species cost | Total cost | Pressure AARD (%) | Species AARD (%) |
|---|---|---:|---:|---:|---:|---:|
| F1 | B | 8.43870162159786 | 24.59507262194432 | 33.03377424354218 | 13.977583010175842 | 8.258162617784622 |
| F2 | A | 11.241011515792477 | 22.90068620944915 | 34.14169772524163 | 17.364961003879095 | 8.160018130610943 |
| F3 | B | 61.61215032903855 | 35.02645860398223 | 96.63860893302073 | 53.597958692102424 | 10.787050573779593 |
| F4 | B | 10.30952516308719 | 37.317322797966796 | 47.62684796105397 | 14.792794515196933 | 14.096855627345548 |
| F5 | A | 11.621033638074117 | 28.077576236466182 | 39.698609874540296 | 17.46098689214804 | 10.17060304247853 |
| F6 | — | not fitted | not fitted | not fitted | not evaluated | not evaluated |

All five fitted problems meet relative cost agreement 1e-6; the largest observed
relative difference is 7.203e-13. The lower complete cost is reported, without
post-hoc Born-form reselection. This agreement does not establish identification.

## Conditional uncertainty

`conditional-uncertainty.json`, `conditional-standard-errors.csv` and
`conditional-correlations.csv` reuse `calibration-misfit/refit.py::identifiability`
on the native optimizer Jacobian, converted to physical units with coordinate
scales 0.01 (interactions) and 10 K (slope). F1 has four interior coordinates;
F2 has three. Their interior Jacobians have full column rank. Variance factors
are 0.482244879467769 and 0.49480721340929895, respectively, using 141 minus the
actual number of interior coordinates. Active coordinates have no symmetric
interval. Pressure ln-ratio scale is 0.3; species scale is 0.1*x_obs+0.001.
Independent residuals are assumed; species derived from one titration are not
independent. These standard errors are conditional and indicative only, and
remain dependent on the unperformed replay checks.

## Stop and diagnosis

Both F6 jobs stopped at `low-temperature-fit.py::verify_inputs`, at the assertion
that each continuation mole fraction equals its normalized feed fraction within
1e-15. The final-rerun binding supplied corrected packet requests directly,
instead of reproducing the existing #140 training-input initialization.
`temperature-reanchor-140/phase-a.py` explicitly replaces historical
continuation by feed-only guesses when writing fitting inputs (lines 216–228).
All 83 supplied requests violate that F6 initialization invariant.

`diagnosis.json` retains the mismatching identities and maximum absolute
composition differences. A construction-only probe reused the existing
`assessment.py::feed_start` and recovered the composition and pressure-initial
invariants without changing reaction_system, analytical feed, observed targets
or temperature. The probe called no solver or optimizer and did not change the
retained inputs. This is an implementation input-binding error, not a numerical
or physical result for F6. No retry was made under the owner's stop instruction.
The next owner should authorize corrected F6 binding and how to complete the
remaining two optimizer runs without violating the single-pool/concurrent-run
requirement or repeating the ten completed optimizations.

The #152 accepted-wave coordinator requested for outside-fit evaluation was not
found in this worktree or its tracked files. Its retained outputs are present,
including corrected observations and evaluated populations. No replacement
coordinator was created, and old results were not substituted. The existing
shared evaluation owner is present. Its missing named caller must be supplied
or its reuse explicitly clarified before outside-fit calculations.

## Compute, checks and provenance

The calculation used one process pool of 12 workers, sized to CPU affinity,
with OMP_NUM_THREADS, OPENBLAS_NUM_THREADS and MKL_NUM_THREADS all 1. No nested
pool was used. Each job retained its 2400 s outer timeout and unchanged native
2250 s/40-iteration controls. Pool wall time was 478.01425133400335 s; the
longest completed optimizer job was F3-B at 477.11323463699955 s.

The Engine wheel was SHA-256 verified before fitting:
`28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2`.
Imports resolved to this worktree's `.venv/lib/python3.13/site-packages/epcsaft`,
not an Engine source checkout. Corrected packet content SHA-256 is
`02b9b331abe5911c4c3d5050c3f0cdfadbbb3d2dd98a618c751e96c2ade90fc7`.
Original starts and fixed configuration inputs remain unchanged. F6's existing
hash verification was rebound to `input-hashes.json` for the corrected training
input and current #152 evaluator/probe/compare files; historical #140 input pins
were not overwritten. No selected-record guard or pin was changed.

The four edited/new Python files compiled successfully; corrected fit bindings
constructed 83-state/141-target and 83-state/159-target observation lists before
dispatch. No new admission, preregistration, guard, wheel, or scientific method
was introduced. Gross executable additions against `f68e16f` are advisory and
recorded in `change-accounting.json`.

## Not done and claim boundaries

Not done: F6's two optimizer runs; outside-fit scores for F1/F2/F6; replay and
independent stationarity, element/charge-balance and domain checks; #151 activity
decomposition and N1–N9; four main-text figure data sets; replacing
`selected-current-best-parameters.json`; notebook section, render and delivered
review. The selected record remains the original `9055458d…` record. No push,
PR, issue write or manuscript edit was made.

No Born mechanism, physical necessity, transfer or extrapolation conclusion is
established by this incomplete suite. The intended calibrated domain is 30 wt%
MEA, pressure fitted at 40–60 °C and species at 20–60 °C. Matin inputs remain
source-unverified legacy inputs. The 80 °C and higher-temperature data also
informed reaction shifts and are not independent temperature predictions;
Wagner is the only set not used earlier. Any eventual Born-off conclusion is
limited to the tested bounded refits. Ion values are effective parameters, and
loaded density must be reported as a limit from the eventual evaluation.
F6 versus F1 must assess extrapolated model behaviour over the matched
293.15–393.15 K domain and the combined change of reaction laws, CO2 epsilon/k
and refitted interactions—not the reaction-law effect alone. Xu rows 22–24
remain outside that domain, not evaluated.
