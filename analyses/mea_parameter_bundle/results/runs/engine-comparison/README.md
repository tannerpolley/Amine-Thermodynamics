# MEA Engine comparison

Fixed parameters and state packets were used throughout. The measurements describe these Engine and evaluator versions; they do not establish predictive use.
The original controller setup failures remain as 14 `setup_failure` rows and are excluded from the three valid cold-sweep pairs.

## Provenance

| Measurement rows | Engine commit | Wheel SHA-256 | Evaluator git blob | Parameter file SHA-256 | State packet JSON SHA-256 |
|---|---|---|---|---|---|
| G b66 addendum | 443a9da492fd5ac7724525945d108c6a2a854d51 | b66c7b962541a586f5ec50043a5e8b4e62cf52e24eaec02ef33f43e558762a58 | ac6298f85a33f0a4d09dd71f17a3a343195392b2 | 868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be | 86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448 |
| G 3eb502ab, cold runs 4–5 | 83ac1126d8824dd2f1465c194be73c19ebc0cdb5 | 3eb502abf74c4bb9f48fcafbbe2f271e7bba7a70152ed2d998f10c4606741252 | 69104fcc0fd67977f67773611eae9e9574fdb28e | 868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be | 86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448 |
| G 3eb502ab, cold run 6 and selected checks | 83ac1126d8824dd2f1465c194be73c19ebc0cdb5 | 3eb502abf74c4bb9f48fcafbbe2f271e7bba7a70152ed2d998f10c4606741252 | ac6298f85a33f0a4d09dd71f17a3a343195392b2 | 868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be | 86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448 |
| S superseded | 8438ce5f94a547189c91c4ec180a7782d60879d6 | 40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805 | 25a270bc94c5306dc19b2a2e542891d3357483f9 | 568f7a5f6379acebacea584d707d5a3222db1022a85a4092b52553248e48524d | 86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448 |

- State packet JSON SHA-256: 86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448; compressed file SHA-256: e9d3ea9903fec9b5239dddcfe5bb8449e9f1a1aff488f0900cc9a91479ba48ba.
- The superseded parameter file from 8f8e4a2^ matches the current adopted file on all 110 shared numeric coefficients. Its seven extra same-sign ion-pair kij=1 entries are omitted by the current file, which explicitly excludes same-sign pairs.
- Each run used OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1, a fresh empty evaluator cache, and sequential workers. The full uptime snapshot is retained in host_load on every measurement row.
- Greenfield rows on wheel 3eb502ab include evaluator recovery attempts. The b66 rows add only the five-state value check and derivative check; no new speed measurements were taken.

## Summary

### 79-state solved-pressure replay

Medians use only valid alternating pairs S4/G4, S5/G5, and S6/G6. Median recovery attempts per sweep is the median of each run's total attempts beyond its first attempt.

| Engine | Median total wall (s) | Median per-run median state wall (s) | Cold-start-only evaluated / 79 | Final evaluated / 79 | Median states recovered by evaluator | Median recovery attempts per sweep |
|---|---:|---:|---:|---:|---:|---:|
| S | 892 | 9.46 | 66/79 | 66/79 | 0 | 0 |
| G (3eb502ab) | 211 | 1.55 | 76/79 | 79/79 | 3 | 3 |

Median of per-pair total S/G ratios: 4.21x. Per-pair ratios and ratios on the 63 states S evaluated in all three runs:

| Pair | S total (s) | G total (s) | Total S/G | Shared-state S/G |
|---:|---:|---:|---:|---:|
| 4 | 892 | 378 | 2.36 | 1.94 |
| 5 | 1228 | 150 | 8.18 | 6.66 |
| 6 | 887 | 211 | 4.21 | 3.64 |

Median shared-state S/G ratio: 3.64x. G was faster in every pair by at least 1.9x on those shared states.
S totals include about 242 s median time on the 6 bubble-Newton failures. G totals include its 3 evaluator recovery attempts per run.
Cold-sweep start load averages ranged from 7.41 to 47.3; full snapshots remain in `host_load`.

### Failures and evaluator retries

G's `cold-packet-start` failed on `vle_obs_0128`, `vle_obs_0145`, `vle_obs_0227` and evaluated 76/79 in every run. The newer MEA evaluator then tried `speciated-liquid-start`, recovered 3 states in every run, and evaluated 79/79 in every run. The S evaluator uses `anchors=[]` and records only the initial attempt, so G's final count reflects both the Engine and newer evaluator.

S had 7 persistent `numerical_convergence_failure` cases with diagnostic `reactive_finite_phase_certificate_failed`: `vle_obs_0130`, `vle_obs_0135`, `vle_obs_0149`, `vle_obs_0190`, `vle_obs_0198`, `vle_obs_0205`, `vle_obs_0221`.
S had 6 persistent `numerical_convergence_failure` cases with diagnostic `bubble Newton iteration limit reached`: `vle_obs_0227`, `vle_obs_0228`, `vle_obs_0229`, `vle_obs_0230`, `vle_obs_0231`, `vle_obs_0232`.
S run 5 had 3 additional 60 s `evaluation_timeout` cases: `vle_obs_0121`, `vle_obs_0122`, `vle_obs_0124`; its one-minute load average was 47.31. It had 16 failures total, including 13 numerical cases.

### pCO2 accuracy by source, all evaluated states

Predictions use the per-state median across valid runs. AARD (%) is the mean absolute relative error times 100; mean ln ratio reports bias, and RMS ln ratio reports the log error spread.

| Engine | Source | States | AARD (%) | Mean ln ratio (bias) | RMS ln ratio |
|---|---|---:|---:|---:|---:|
| S | Hilliard2008 | 28 | 64.03 | 0.3285 | 0.5582 |
| S | Jou1995 | 38 | 57.83 | -0.01952 | 0.6297 |
| G, all evaluable states | Hilliard2008 | 31 | 67.34 | 0.3407 | 0.5759 |
| G, all evaluable states | Jou1995 | 48 | 56.73 | 0.04607 | 0.6016 |

### pCO2 accuracy on the 66 states evaluated by both Engines

| Engine | Source | Shared states | AARD (%) | Mean ln ratio (bias) | RMS ln ratio |
|---|---|---:|---:|---:|---:|
| S | Hilliard2008 | 28 | 64.03 | 0.3285 | 0.5582 |
| S | Jou1995 | 38 | 57.83 | -0.01952 | 0.6297 |
| G, shared states | Hilliard2008 | 28 | 63.9 | 0.3273 | 0.5575 |
| G, shared states | Jou1995 | 38 | 57.81 | -0.01915 | 0.6294 |

On shared states, G's AARD differs from S by 0.13 points for Hilliard2008 and 0.02 points for Jou1995. The larger all-state Hilliard2008 AARD for G comes from its 3 extra evaluable Hilliard states.
Across 66 paired pressure states, median |ln(G/S)| is 0.00112 and maximum is 0.00907 on `vle_obs_0233`.

### Representative states

Three alternating repeats each on the original 3eb502ab wheel:

| State | Engine | Evaluation counts | Median wall (s) | Median iterations |
|---|---|---|---:|---:|
| `Bottinger2008_state_050` | S | `evaluated:3` | 1.91 | — |
| `Bottinger2008_state_050` | G (3eb502ab) | `evaluated:3` | 0.2 | 77 |
| `Bottinger2008_state_058` | S | `evaluated:3` | 2.05 | — |
| `Bottinger2008_state_058` | G (3eb502ab) | `evaluated:3` | 0.159 | 16 |
| `vle_obs_0130` | S | `non_evaluable:3` | 2.26 | — |
| `vle_obs_0130` | G (3eb502ab) | `evaluated:3` | 6.16 | 95 |
| `vle_obs_0206` | S | `evaluated:3` | 5.75 | — |
| `vle_obs_0206` | G (3eb502ab) | `evaluated:3` | 1.85 | 43 |
| `vle_obs_0232` | S | `non_evaluable:3` | 35.3 | — |
| `vle_obs_0232` | G (3eb502ab) | `evaluated:3` | 0.456 | 5 |

Absolute mole-fraction errors for measured species on the two fixed-pressure states:

| Engine | Source / species | Mean absolute error | RMS error |
|---|---|---:|---:|
| S | Bottinger2008/HCO3- | 0.003783 | 0.004188 |
| S | Bottinger2008/MEA + MEAH+ | 0.0076 | 0.00796 |
| S | Bottinger2008/MEACOO- | 0.008433 | 0.009813 |
| G (3eb502ab) | Bottinger2008/HCO3- | 0.003783 | 0.004188 |
| G (3eb502ab) | Bottinger2008/MEA + MEAH+ | 0.0076 | 0.00796 |
| G (3eb502ab) | Bottinger2008/MEACOO- | 0.008433 | 0.009813 |

The b66 cache-cold pass evaluated 5 representative states and matched 21 outputs to the median of three 3eb502ab repeats; maximum relative difference: 0. No timing rows from that pass are retained.

### Derivatives

| Direction family | S | G (3eb502ab) | G (443a9da4) |
|---|---|---|---|
| temperature | `unavailable` | `unavailable` | `available` |
| pressure | `unavailable` | `available` | `available` |
| eos parameter | `available` | `unavailable` | `unavailable` |
| reaction coefficient | `available` | `unavailable` | `unavailable` |

| Engine / wheel | Direction | Unit | Native status | Native derivative | Central finite difference | Relative error |
|---|---|---|---|---:|---:|---:|
| S | kij | mole fraction per coordinate | `available` | -9.3286e-06 | -9.3286e-06 | 2.454e-07 |
| G (3eb502ab) | pressure | mole fraction per coordinate | `Available` | 6.4298e-11 | 6.4298e-11 | 1.206e-07 |
| G (3eb502ab) | kij | mole fraction per kij | `ReferenceUnavailable` | — | -9.3287e-06 | — |
| G (443a9da4) | temperature | 1 | `Available` | 0.00017228 | 0.00017228 | 1.098e-07 |
| G (443a9da4) | pressure | 1 | `Available` | 6.4298e-11 | 6.4298e-11 | 1.206e-07 |
| G (443a9da4) | kij | mole fraction per kij | `ReferenceUnavailable` | — | -9.3287e-06 | — |

On b66, the measured solved-state temperature action includes the Engine #84 R1–R5 reference-temperature chain; its central finite-difference relative error is 1.098e-07.
The retained G 3eb502ab derivative run 2 failed with `MAXITER_EXCEEDED` after 200 iterations on the central kij solve. Its failed worker row remains in `measurements.csv` and is not treated as a derivative value.
The superseded wheel has native R4/R5 coefficient-sensitivity evidence in retained `sensitivity-check.csv`.

### Adopted fit objective

| Engine / wheel | Result | Evidence or reason |
|---|---|---|
| S superseded | `could_evaluate` | No timing taken. `full-validation-targets.csv` retains 113 evaluated heat rows from the superseded wheel 40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805; `file_sha256`=10977052cf96e1325caca994a2bc840db57bee1b3528e2b03b2e13bc845e40f3. |
| G 3eb502ab | `not_measurable` | No timing taken: the adopted objective includes absorption-heat rows, and the current Greenfield path lacks the required reference-enthalpy actions (Engine #84). |
| G b66 | `not_measured` | The MEA heat scripts have not been rebuilt on Engine #84/#138. |

No objective timing was taken. Retained `full-validation-targets.csv` contains evaluated heat rows for the superseded 40fba7cf wheel. On wheel 3eb502ab, the adopted objective could not be measured because Engine #84 reference-enthalpy actions were unavailable. On b66, the Engine actions are present, but the MEA heat scripts have not been rebuilt on Engine #84/#138.

## Reproduction

Finalization reads `measurements.csv` only; it does not invoke either Engine or modify measurement rows. It deterministically regenerates `summary.csv` and this README:

```bash
python3.13 analyses/mea_parameter_bundle/scripts/compare_engines.py --finalize-only
```

Set `RUNROOT`, `GREENFIELD_3EB_WHEEL`, and `GREENFIELD_B66_WHEEL` to scratch and pinned wheel paths, then prepare the workers:

```bash
UV_PROJECT_ENVIRONMENT="$RUNROOT/superseded-venv" uv sync --locked --group test --python 3.13
uv pip install --python "$RUNROOT/superseded-venv/bin/python" --reinstall --no-deps analyses/mea_parameter_bundle/data/input/engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl
uv pip install --python "$RUNROOT/superseded-venv/bin/python" pint==0.26.1
UV_PROJECT_ENVIRONMENT="$RUNROOT/greenfield-venv" uv sync --locked --group test --python 3.13
uv pip install --python "$RUNROOT/greenfield-venv/bin/python" --reinstall --no-deps "$GREENFIELD_3EB_WHEEL"
python3.13 analyses/mea_parameter_bundle/scripts/compare_engines.py --superseded-python "$RUNROOT/superseded-venv/bin/python" --greenfield-python "$RUNROOT/greenfield-venv/bin/python" --greenfield-wheel "$GREENFIELD_3EB_WHEEL"
uv pip install --python "$RUNROOT/greenfield-venv/bin/python" --reinstall --no-deps "$GREENFIELD_B66_WHEEL"
python3.13 analyses/mea_parameter_bundle/scripts/compare_engines.py --scenario addendum --append --greenfield-python "$RUNROOT/greenfield-venv/bin/python" --greenfield-wheel "$GREENFIELD_B66_WHEEL"
python3.13 analyses/mea_parameter_bundle/scripts/compare_engines.py --finalize-only
```

Use wheel 3eb502ab for the original comparison and b66 for the five-state addendum. The addendum records values and derivative checks without timing rows. A fresh comparison refuses to overwrite this folder: run it from a checkout without `results/runs/engine-comparison/`; valid cold runs are taken from the data (cold-sweep runs without `setup_failure` rows), and G rows record the git blob of the `shared_evaluation.py` actually imported.
