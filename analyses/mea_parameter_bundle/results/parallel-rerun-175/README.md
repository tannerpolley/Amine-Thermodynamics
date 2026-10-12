# Issue 175: F1–F6 heat campaign on Engine e9b1aed5

All 12 native fits converged using 16 Engine workers per fit, sequentially,
with OMP, OpenBLAS and MKL each limited to one thread. None matched the retained
Engine 026b3031 result bitwise. The numerical outputs remain comparison evidence;
this campaign does not adopt parameters or establish physical validation.

The sum of the 12 fit command wall times is **1293.108 s (21.55 min)**;
native `regression.fit` calls alone sum to **1192.162 s (19.87 min)**.
Peak memory was not measured. Timing is an observed comparison on a shared
machine, not a controlled isolation of worker scaling.

| Fit | Targets | New command wall (s) | Retained command wall (s) | Iterations new / old | Bitwise equal | Max absolute coordinate change | Relative final-cost change | Max absolute weighted-residual change |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| F1-A | 149 | 73.713 | 621.45 | 9 / 5 | no | 4.01771099e-05 | 3.78222589e-08 | 8.73322237e-07 |
| F1-B | 149 | 107.955 | 1138.83 | 15 / 13 | no | 1.91107356e-05 | 3.78226606e-08 | 3.7342865e-07 |
| F2-A | 149 | 113.129 | 1167.84 | 16 / 16 | no | 2.8652312e-05 | 3.04072565e-07 | 5.60997603e-07 |
| F2-B | 149 | 123.980 | 1337.90 | 16 / 16 | no | 2.86546548e-05 | 3.04072695e-07 | 5.60993244e-07 |
| F3-A | 149 | 181.277 | 1973.08 | 26 / 26 | no | 2.58416217e-05 | 2.05787653e-07 | 7.20604176e-07 |
| F3-B | 149 | 147.665 | 1638.69 | 19 / 19 | no | 2.58427308e-05 | 2.05787761e-07 | 7.20607936e-07 |
| F4-A | 167 | 90.175 | 976.18 | 8 / 8 | no | 3.13228533e-05 | 3.5130878e-08 | 1.59499641e-07 |
| F4-B | 167 | 111.491 | 1295.32 | 10 / 19 | no | 3.13241365e-05 | 3.51498208e-08 | 1.59496283e-07 |
| F5-A | 167 | 67.691 | 683.24 | 5 / 5 | no | 2.90017265e-05 | 2.87353308e-07 | 5.78025012e-07 |
| F5-B | 167 | 81.939 | 877.08 | 7 / 7 | no | 2.90017564e-05 | 2.87353191e-07 | 5.78025601e-07 |
| F6-A | 149 | 100.986 | 1138.66 | 12 / 14 | no | 2.45311004e-05 | 6.60352251e-08 | 1.93090395e-06 |
| F6-B | 149 | 93.105 | 926.80 | 12 / 11 | no | 2.46207475e-05 | 6.60336021e-08 | 1.45554859e-07 |

## Basis and comparison

Numerical verification for [issue #175](https://github.com/tannerpolley/Amine-Thermodynamics/issues/175).
`run.py` reuses `d1_density_cp_160.fit_worker`, the command recorded in the
retained `resources.txt` files, with `p5conv-fit.py` and `heat_160.py`.
`heat_evidence_170.py` owns the retained summary and subsequent assessments;
those assessments were not rerun. Budgets remain **40 iterations / 2250 s**.
Starts, bounds, scales, observations, weights and tolerances are unchanged.
All 12 start mappings, coordinate identities and ordered target lists match
retained records. F4/F5 retain **167 targets**, including 18 pooled-species
values; the other fits have 149. All include the same eight Vinjarapu heats.

The wheel SHA-256 was verified before launching:

- New Engine `e9b1aed5`: `e691b5a9a2fe41e9115d83c914c912a928ed671f1b82ea001c90e6edf8e3d97b`.
- Retained Engine `026b3031`: `94b55dfcf72f21b43010c7125d71f103f41fd56f7a6b6fe0774903eef71cc72a`.

`engine.json` records the private ignored environment and installed versions.
Engine imports resolve inside that environment, with no source-checkout import.
Old command wall times come from each retained `resources.txt`, including the
first-wave runs. F4-B's new time uses its child-wrapper timer and excludes
small process-launch overhead. Retained F1-A took 621.45 s, outside the task's
approximate 683–1973 s range.

`comparison.csv` contains both command and native-fit timers. Equality packs
decoded numbers as IEEE-754 binary64, including signed zero, for coordinates,
initial/final/iteration costs, predictions, weighted residuals and both Jacobians.
Every fit's `differences.json` records changed indices, old/new decimal and exact
hexadecimal values, signed differences and differing history lengths. The old
records expose weighted residuals; new unweighted residuals are also retained.
No tolerance replaces equality. `max_relative_delta_cost` compares initial and
final costs; `final_cost_relative_delta` compares final costs only.
Coordinate maxima mix four dimensionless interactions and one slope in kelvin;
the overall maximum, **4.01771099e-5**, is the F1-A slope change in kelvin.

## Exceptions and limits

The initial setup attempt failed for all starts at an import-time old-wheel
pin check, before any native fit. Its logs and exceptions are in `setup-attempt/`.
The pin order was corrected and each command received one retry. No numerical
fit was repeated.

F1-A and F1-B then converged, but the unchanged driver assertion against the
retained heat-160 cost failed: `AssertionError: F1 heat equivalence failed`.
Their command return codes are 1, and the exact tracebacks remain in their
`exception.json` files. Their native outputs and diagnostic parameter mappings
had already been produced and are retained as `native-fit.json` and
`parameters.json`; they were not treated as passing the equivalence gate.
Their final-cost increases are 1.21245619e-6 and 1.21246907e-6, respectively
(relative changes 3.78222589e-8 and 3.78226606e-8). All other fit commands returned 0.

The first launcher's comparison assumed equal iteration-history lengths and
stopped after converged F4-B (10 iterations versus 19). The comparison was
corrected to retain length differences, and only the unrun F5/F6 commands were
started. `execution-before-resume.json` and `campaign.txt` preserve this event.
The total in `execution.json` adds the execution segments and F4-B's child timer;
it excludes the pause to repair the comparison. The reported sum of fit command
times has no dependency on that pause or on environment installation time.

`input-checks.json` compares all recorded inputs using the repository's hash
convention: decompressed bytes for `.json.gz`. Both state packets, observation,
reaction, heat-input and numerical-helper hashes match. The changed files are
the adopted selected parameter record, `shared_evaluation.py`'s default wheel
pin (c91dfff), and the later decomposition-reporting part of
`d1_density_cp_160.py` (7ad8156). The fit function is unchanged; every generated
full start mapping and target list matches its reference. An earlier compressed
versus decompressed hash comparison was corrected before retention.

**Evidence type: numerical verification.** The largest relative final-cost
change is 3.04072695e-7 (F2-B), and the largest weighted-residual change is
1.93090395e-6 (F6-A). The differences include initial costs, so they are not
limited to different final stopping iterations. This comparison changes both
the wheel version and worker count; it cannot attribute the differences to
parallelism or test the Engine's same-wheel worker-count equality claim.
No new single-worker control, parameter adoption, physical validation, manuscript,
notebook, selected-record, permittivity or default-environment change was made.

## Reproduction and files

Create the ignored environment with `uv venv --python 3.13 tmp/venv-e9b1aed5`;
use `uv pip install --python tmp/venv-e9b1aed5/bin/python` for the new wheel,
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.9 and pandas 2.3.3 (lock versions),
then install this repository with the same command plus `--no-deps .`.
The default environment was not synchronized or modified. The campaign command was:

```bash
uv run --no-project --python tmp/venv-e9b1aed5/bin/python analyses/mea_parameter_bundle/results/parallel-rerun-175/run.py 2>&1 | tee analyses/mea_parameter_bundle/results/parallel-rerun-175/campaign.txt
```

The final runner refuses to overwrite an existing campaign. During recovery,
the launcher skipped completed directories; its final code restores the guard.
`finalize.py` compares retained outputs without fitting. Per-fit JSON files,
`comparison.csv`, `summary.json`, `engine.json` and `execution.json` own the
results; `file-hashes.json` records their identities. Investigator records and
`heat-final-170` are unchanged.
