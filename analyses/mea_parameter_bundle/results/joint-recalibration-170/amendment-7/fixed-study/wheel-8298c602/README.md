# Strict-gate qualification attempts on wheel 8298c602

**Interface failure, not a phase result.** Four calls on the merged #660 wheel
(`main-8298c602`, SHA-256 `8897a0ca…85b3`) returned no thermodynamic result:

| Call (`../../step-ledger.json`) | Exit | Wall-s / CPU-s | What failed |
|---|---:|---:|---|
| q1-a4-control-family, first | 1 | 0.35 / 0.30 | `RuntimeError: installed Engine wheel does not match the pinned SHA-256`, raised on import by `calibration-misfit/probe.py:27`: the study's explicit wheel binding then ran after `import final_evidence`. Its output file was overwritten by the second q1 call; the message is quoted from that call's terminal output. |
| q1-a4-control-family | 0 | 12.46 / 12.36 | `a4-control/`: all 73 points `failed` with `TypeError: object of type 'float' has no len()` before any stability test |
| q2-a6-selected-family | 0 | 13.00 / 12.95 | `a6-selected/`: the same failure at all 73 points |
| q3-a6-selected-replay | 1 | 11.92 / 11.72 | `fit_observations.py:261` `previous.pressure[0]`: `TypeError: 'float' object is not subscriptable` |

Cause: Engine #609 leg 2 (`b11d69d6`), present in every merged wheel that contains
#660, returns `EquilibriumResult.temperature` and `.pressure` as numbers instead
of one-element lists. The owner chose repo-wide adoption
([#170 comment 6297147461](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6297147461));
see `analyses/mea_parameter_bundle/results/engine-8298c602-adoption/`. The
`a4-control/` and `a6-selected/` point records are retained as these failed
attempts and are not compared. Requalification after adoption uses new labels.
All four calls are charged (37.73 wall-s / 37.33 CPU-s) to the qualification allocation.
