# MEA Engine comparison

This fixed-input comparison reports elapsed time, states evaluated, prediction errors, and derivative values. It does not qualify predictive use.
The first controller attempt failed before any Engine calculation because Python resolved each venv symlink to the base interpreter. Those rows remain labeled `setup_failure` and are excluded from all medians.

## Provenance

| Engine rows | Engine commit | Wheel SHA-256 | Evaluator git blob | Parameter file SHA-256 |
|---|---|---|---|---|
| S | `8438ce5f94a547189c91c4ec180a7782d60879d6` | `40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805` | `25a270bc94c5306dc19b2a2e542891d3357483f9` | `568f7a5f6379acebacea584d707d5a3222db1022a85a4092b52553248e48524d` |
| G cold runs 4–5 | `83ac1126d8824dd2f1465c194be73c19ebc0cdb5` | `3eb502abf74c4bb9f48fcafbbe2f271e7bba7a70152ed2d998f10c4606741252` | `69104fcc0fd67977f67773611eae9e9574fdb28e` | `868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be` |
| G cold run 6 and selected states | `83ac1126d8824dd2f1465c194be73c19ebc0cdb5` | `3eb502abf74c4bb9f48fcafbbe2f271e7bba7a70152ed2d998f10c4606741252` | `ac6298f85a33f0a4d09dd71f17a3a343195392b2` | `868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be` |
| G addendum state and derivative checks | `443a9da492fd5ac7724525945d108c6a2a854d51` | `b66c7b962541a586f5ec50043a5e8b4e62cf52e24eaec02ef33f43e558762a58` | `ac6298f85a33f0a4d09dd71f17a3a343195392b2` | `868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be` |

- For the original G rows, the producer set the evaluator’s stored wheel SHA and Engine commit in memory to `3eb502abf74c4bb9f48fcafbbe2f271e7bba7a70152ed2d998f10c4606741252` and `83ac1126d8824dd2f1465c194be73c19ebc0cdb5`. For addendum rows, the same evaluator source was loaded with the b66 SHA and `443a9da492fd5ac7724525945d108c6a2a854d51` set in memory.
- All original and addendum rows use state packet JSON SHA-256 `86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448`; compressed file SHA-256: `e9d3ea9903fec9b5239dddcfe5bb8449e9f1a1aff488f0900cc9a91479ba48ba`.
- The old parameter file is from `8f8e4a2^` and matches the adopted current file on all 110 common coefficients. It retains seven same-sign ion-pair `kij=1` entries that the current file omits while explicitly excluding same-sign pairs; this preserves the fitted model’s exclusion rule.
- Python 3.13.14; each scratch venv used `uv sync --locked --group test`. The superseded wheel also needed Pint 0.26.1. Both venvs and every evaluator cache were under `/tmp`.
- Each run used `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`. Workers ran sequentially. The raw `uptime` text is retained in `host_load` on every measurement row.
- Each Engine/run used a new empty state cache. Valid cold runs were `S4,G4,S5,G5,S6,G6`; original representative-state runs alternate S and G three times per state. The addendum used one additional cache-cold G pass.
- Valid cold run indices retained: `4,5,6`. Setup-failure rows retained: `14`.

## Summary

### 79-state solved-pressure replay

Medians use only valid cold run indices 4–6. Non-evaluable states count as failures; their attempt and solver diagnostics remain in `measurements.csv`.

| Engine | Median total wall (s) | Median per-state median (s) | Evaluated states / 79 | Non-evaluable / 79 | Median recovery attempts | S/G wall ratio |
|---|---:|---:|---:|---:|---:|---:|
| S | 892.4 | 9.461 | 66/79 | 13/79 | 0 | — |
| G (3eb502ab) | 210.7 | 1.548 | 79/79 | 0/79 | 3 | 4.236 |

### pCO₂ accuracy by source

The table uses per-state median predictions from valid cold runs. Mean and RMS are over `ln(predicted/observed)`; AARD is `100 × mean(|predicted/observed − 1|)`.

| Engine | Source | Evaluated states | Mean ln ratio | RMS ln ratio | AARD (%) |
|---|---|---:|---:|---:|---:|
| S | Hilliard2008 | 28 | 0.3285 | 0.5582 | 64.03 |
| S | Jou1995 | 38 | -0.01952 | 0.6297 | 57.83 |
| G | Hilliard2008 | 31 | 0.3407 | 0.5759 | 67.34 |
| G | Jou1995 | 48 | 0.04607 | 0.6016 | 56.73 |

The accuracy and representative-state medians above use G wheel `3eb502ab`; the b66 addendum checks values only and adds no accuracy summary.

Maximum paired `|ln(G/S)|` for pCO₂: **0.009068** on `vle_obs_0233` across 66 commonly evaluated states.

### Representative states

Three alternating repeats each: Böttinger 050 and 058 at fixed pressure; VLE 0130, 0206, and 0232 at 40, 80, and 120 °C.

| State | Engine | Evaluated status counts | Median wall (s) | Median iterations |
|---|---|---|---:|---:|
| Bottinger2008_state_050 | S | evaluated:3 | 1.907 | — |
| Bottinger2008_state_050 | G | evaluated:3 | 0.1996 | 77 |
| Bottinger2008_state_058 | S | evaluated:3 | 2.053 | — |
| Bottinger2008_state_058 | G | evaluated:3 | 0.1591 | 16 |
| vle_obs_0130 | S | non_evaluable:3 | 2.263 | — |
| vle_obs_0130 | G | evaluated:3 | 6.157 | 95 |
| vle_obs_0206 | S | evaluated:3 | 5.751 | — |
| vle_obs_0206 | G | evaluated:3 | 1.854 | 43 |
| vle_obs_0232 | S | non_evaluable:3 | 35.34 | — |
| vle_obs_0232 | G | evaluated:3 | 0.4556 | 5 |

Absolute mole-fraction errors for measured species on the two fixed-pressure states:

| Engine | Source / species | Mean absolute error | RMS error |
|---|---|---:|---:|
| S | Bottinger2008/HCO3- | 0.003783 | 0.004188 |
| S | Bottinger2008/MEA + MEAH+ | 0.0076 | 0.00796 |
| S | Bottinger2008/MEACOO- | 0.008433 | 0.009813 |
| G | Bottinger2008/HCO3- | 0.003783 | 0.004188 |
| G | Bottinger2008/MEA + MEAH+ | 0.0076 | 0.00796 |
| G | Bottinger2008/MEACOO- | 0.008433 | 0.009813 |

### Derivatives

| Derivative family | S | G (3eb502ab) | G (443a9da4) |
|---|---|---|---|
| temperature | unavailable | unavailable | available |
| pressure | unavailable | available | available |
| eos parameter | available | unavailable | unavailable (`ReferenceUnavailable`) |
| reaction coefficient | available | unavailable | unavailable (#61) |
| reaction reference temperature | unavailable | unavailable | available (#84; exercised by the source-referenced temperature action) |

Native CO₂–H₂O kij action on `Bottinger2008_state_050`:

| Engine | Value |
|---|---:|
| S | -9.329e-06 |
| G (3eb502ab) | — |

Central finite difference on `Bottinger2008_state_050`:

| Engine | Value |
|---|---:|
| S | -9.329e-06 |
| G (3eb502ab) | -9.329e-06 |

Relative error on `Bottinger2008_state_050`:

| Engine | Value |
|---|---:|
| S | 2.454e-07 |
| G (3eb502ab) | — |

The G CO₂–H₂O kij action returned `ReferenceUnavailable` on this source-reference MEA problem, so it has no native-versus-finite-difference error. The old Engine’s kij action was available and its finite-difference relative error is shown above.

Greenfield pressure direction on the same state:

| Engine | Native pressure derivative | Central finite difference | Relative error |
|---|---:|---:|---:|
| S | — | — | — |
| G (3eb502ab) | 6.43e-11 | 6.43e-11 | 1.206e-07 |

On this MEA source-reference problem, the 3eb502ab wheel reported temperature and EOS-parameter directions as unavailable and pressure as available. With b66, temperature and pressure are available; CO₂–H₂O kij still returns `ReferenceUnavailable`. The b66 temperature action includes the R1–R5 reference-temperature chain added by Engine #84. Reaction-coefficient directions remain unavailable under Engine #61. The superseded wheel has native R4/R5 coefficient sensitivity evidence in the retained `sensitivity-check.csv`.

### Engine 443a9da4 addendum

One cache-cold pass on the same five representative states evaluated all five states. The 21 output predictions (speciation for Bottinger 050/058 and pressure plus vapor composition for VLE 0130/0206/0232) match the median of the three retained 3eb502ab predictions exactly: maximum relative difference **0**. No timing rows from this pass are retained or compared.

At `Bottinger2008_state_050`, the observable is liquid MEACOO⁻ mole fraction. Native actions and central finite differences are:

| Direction | Native derivative | Central finite difference | Relative error |
|---|---:|---:|---:|
| temperature (mole fraction/K) | 1.722780126e-04 | 1.722780315e-04 (0.02 K step) | 1.098e-07 |
| pressure (mole fraction/Pa) | 6.429815005e-11 | 6.429814230e-11 (100 Pa step) | 1.206e-07 |
| CO₂–H₂O kij (mole fraction/kij) | unavailable (`ReferenceUnavailable`) | -9.328707702e-06 (1e-4 step) | not applicable |
| reaction coefficient | unavailable (Engine #61) | not measured | not applicable |

For b66, the temperature and pressure actions were available and passed the centered re-solve comparison above. The CO₂–H₂O kij direction remains unavailable on this source-referenced state, despite a finite-difference estimate. No reaction-coefficient direction is exposed by Engine #61. The new #84 reference-temperature action is available through the temperature direction for the R1–R5 source-referenced reactions. The existing heat and fitting scripts still have not been rebuilt on the new reference-temperature and total-enthalpy callables.

The addendum uses the same current parameter file (`868a5018…fcb7be`) and state packet as the original comparison. Its one-pass state rows and derivative rows are appended in `measurements.csv`; `summary.csv` has ten appended rows for the equality check and derivative availability/errors. The addendum venv was recreated under `/tmp/mea-engine-comparison-addendum/greenfield-venv` with Python 3.13.14 and the locked test group, then the b66 wheel was installed with `--reinstall --no-deps`. The temporary runner loaded the existing comparison helpers and set the wheel pin in memory; it did not edit the producer or Engine repository. Each row retains the run-start `uptime` snapshot and UTC timestamp.

### Adopted fit objective

No new objective timing was taken. The superseded side could evaluate the pressure/speciation/heat target families: retained `full-validation-targets.csv` contains evaluated heat rows for the 40fba7cf wheel. This is prior capability evidence, not a timing for this comparison. Greenfield is recorded as not measurable because its adopted objective includes absorption-heat rows blocked by Engine #84.

## Reproduction and limits

Worker Python paths: `S=/tmp/mea-engine-comparison-20260923/superseded-venv/bin/python`, `G=/tmp/mea-engine-comparison-20260923/greenfield-venv/bin/python`.

```bash
python3.13 analyses/mea_parameter_bundle/scripts/compare_engines.py --superseded-python /tmp/mea-engine-comparison-20260923/superseded-venv/bin/python --greenfield-python /tmp/mea-engine-comparison-20260923/greenfield-venv/bin/python
```

The b66 addendum used a new Python 3.13.14 environment and the temporary runner `/tmp/mea-engine-comparison-addendum/run_addendum.py`:

```bash
UV_PROJECT_ENVIRONMENT=/tmp/mea-engine-comparison-addendum/greenfield-venv uv sync --locked --group test --python 3.13
uv pip install --python /tmp/mea-engine-comparison-addendum/greenfield-venv/bin/python --reinstall --no-deps /home/tnnrpolley21/.cache/epcsaft/wheels/b66c7b962541a586f5ec50043a5e8b4e62cf52e24eaec02ef33f43e558762a58/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl
/tmp/mea-engine-comparison-addendum/greenfield-venv/bin/python /tmp/mea-engine-comparison-addendum/run_addendum.py
```

Scratch root: `/tmp`. The long-format measurements are in `measurements.csv`; medians and aggregate statistics are in `summary.csv`.
- The setup failures came from resolving the venv `bin/python` symlink before launching workers; the corrected commands preserve the venv path.
- Superseded runs 4–6 had numerical-convergence failures; those states were excluded only from prediction accuracy and evaluated-state counts. All per-attempt outcomes remain in the long-format table.
- Cold-run start load averages (1 min) ranged from 7.41 to 47.31. Result timings vary with the host load snapshots retained in `host_load`; only three valid alternating cold pairs were requested.
