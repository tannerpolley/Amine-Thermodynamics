# Composition transfer on the 70 untouched Aronu 2011 rows (#108)

This folder holds one prediction run, finished 2026-09-24 16:12. It predicts pCO2 for the Aronu 2011
rows at 15 and 45 wt% MEA. No fit or model selection used these rows. The partition was frozen in
`d7d187e` (`aronu-2011-untouched-vle-rows.txt`, SHA-256 `eaaaa6f9…cea1`, the #108 audit hash). The
row IDs in `transfer-states.csv` equal that partition for both records.

## Result: 15 wt% transfer fails

ln(pred/obs), one row per measured point, failures kept:

| MEA wt% | record | solved | AARD | mean ln | RMS ln |
|---|---|---:|---:|---:|---:|
| 15 | refit C | 33/33 | 87.8 % | +0.535 | 0.656 |
| 15 | pre-refit | 33/33 | 90.6 % | +0.541 | 0.675 |
| 45 | refit C | 36/37 | 23.3 % | −0.180 | 0.351 |
| 45 | pre-refit | 32/37 | 32.7 % | −0.268 | 0.512 |

By temperature (refit C; AARD / mean ln / n):

| MEA wt% | 40 °C | 60 °C | 80 °C |
|---|---|---|---|
| 15 | 77 % / +0.39 / 14 | 81 % / +0.56 / 13 | 126 % / +0.82 / 6 |
| 45 | 26 % / −0.14 / 14 | 23 % / −0.25 / 11 | 20 % / −0.16 / 11 |

- **15 wt%:** both records over-predict pCO2 by a factor of about 1.7 on average (exp 0.535). The bias
  grows with temperature. Refit C barely changes it.
- **45 wt%:** refit C under-predicts by about 16 % on average. Its AARD is 23 %, against 27 % for
  refit C on the 36 Aronu rows at 30 wt%, which no fit used (`../calibration-misfit/README.md`).
- **Failures:** each failure is an Ipopt `LOCAL_INFEASIBILITY` return unless marked otherwise.
  - Refit C: `vle_obs_0072` (45 wt%, 40 °C, loading 0.195).
  - Pre-refit: `0075` and `0077` (40 °C); `0086` and `0090` (60 °C); `0088` (60 °C), which hit the
    90 s budget.
- **Solved rows:** every solved row meets the requested tolerance with no balance error. The maximum
  stationarity residual is 2.3e-13.

## What was evaluated

- **Refit C:** parameter SHA-256 `4c1bff04…9e5159`, written by
  `../calibration-misfit/candidate.py refit-C-converged.json`. The CSV label `adopted-refit-C` is the
  command-line label of the run. Refit C was the candidate for adoption at the time; it has not been
  adopted (owner decision 2026-09-28: refit on the current Engine first).
- **Pre-refit:** the exploratory incumbent, `868a5018…fcb7be`.
- **Engine:** wheel `b66c7b96…` (SHA-256 `b66c7b962541a586f5ec50043a5e8b4e62cf52e24eaec02ef33f43e558762a58`),
  Engine `443a9da4`, parameter packet v3. This is the old pin, not the current Engine.
- **Scripts:** `transfer.py` `dab504a8…`, `../calibration-misfit/probe.py` `33bbd805…`. Each CSV row
  carries all hashes.

Each state is the 30 wt% packet pCO2 request at the same temperature and nearest loading. The CO2
feed is set to the row loading and water is rescaled to the row's MEA mass fraction.

## Claim limit

This is composition transfer at fixed chemistry. Temperatures (40–80 °C) lie inside the calibrated
range, and no species or reactions are new. It is not temperature validation or new-species
validation. The source is one laboratory, Aronu 2011.

This run is the one-time look at these rows. Any later model scored on them is a second look, not an
untouched test.

## Reproduce

```sh
OMP_NUM_THREADS=1 python transfer.py adopted-refit-C=REFIT_C.json pre-refit=PRE_REFIT.json
```

Solver caches go to `../results/runs/composition-transfer/` (ignored). The run log is
`transfer.log` there.
