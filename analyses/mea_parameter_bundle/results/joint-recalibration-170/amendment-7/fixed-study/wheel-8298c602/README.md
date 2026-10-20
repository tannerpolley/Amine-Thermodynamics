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

## After adoption (main `d68be19`): qualified

Rerun on the adopted code (same wheel, `tmp/a7/venv`). The old-wheel records are
`amendment-6/selected-checks/phase-diagnosis/a4-family/`,
`amendment-6/selected-checks/phase-family/` and the A6 Held cold replay. Each
`comparison.json` and `replay-comparison.json` under `after-adoption/` retains the point-by-point comparison.

| Check | Old wheel 21e761c3 | Wheel 8298c602 |
|---|---|---|
| A4 control family (passed / unresolved / failed) | 0 / 73 / 0 | **73 / 0 / 0** (69 two-phase, 4 single-liquid); no descent, no failed trial optimizer |
| A6 selected family | 0 / 61 / 12 | **61 / 0 / 12**; the same 29 resolved descents at points 21, 24, 27, 33, 36, 45, 54, 62, 63, 70–72, max \|Δ tpd/RT\| 1.1 × 10⁻¹³ |
| Final Gibbs objective, max \|change\| | | 2.5 × 10⁻¹⁰ (A4), 1.7 × 10⁻¹⁰ (A6) |
| A6 307-row replay | cost 148.2377314835 | cost 148.2377314835; all rows available; max relative prediction change 2.1 × 10⁻¹³ |

No new descent appears and no equation changed. The design's qualification
stops do not fire. The classification changes are the Engine #660 relabelling and
trace-support repairs: unresolved points now pass with `no_resolved_descent`
trials. This is numerical verification on these vectors and points. Charged:
q4 34.45 / 34.22, q5 33.54 / 33.49, q6 15.01 / 14.98. With the four failed attempts
the qualification stage used 120.73 / 120.02 of its 342 / 963.14.
