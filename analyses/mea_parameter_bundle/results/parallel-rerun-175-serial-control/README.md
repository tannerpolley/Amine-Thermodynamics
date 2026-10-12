# Issue 175 control: F1-A with one Engine worker on the same wheel

**Outcome:** F1-A run with one worker on Engine `e9b1aed5` (wheel SHA-256
`e691b5a9a2fe41e9115d83c914c912a928ed671f1b82ea001c90e6edf8e3d97b`) is
**bitwise identical** to the 16-worker run in `../parallel-rerun-175/F1-A/`.
Identical means equal IEEE-754 binary64 values in `F1-A-results.json` (fitted
cost, coordinates, per-family costs), `F1-A-diagnostic-parameters.json`,
`start-parameters.json` and every residual in `fit-execution.json`. The small
differences from the retained `026b3031` campaign (≤ 4.0e-5 K slope, ≤ 3.0e-7
relative cost) therefore come from the wheel change, not from parallel workers.

| Run | Native fit wall time (s) |
|---|---:|
| Retained, Engine 026b3031, 1 worker (command wall) | 621.45 |
| e9b1aed5, 1 worker | 406.02 |
| e9b1aed5, 16 workers | 65.01 |

`run.py` is `../parallel-rerun-175/run.py` with `WORKERS = 1` and the reference
switched to the 16-worker run. The unchanged F1 heat-equivalence assertion
fails exactly as it does in the 16-worker run (`exception.json`), after all
outputs are written. Peak resident memory was 120 MB (`/usr/bin/time -v`,
parent process). Evidence type: numerical verification; one fit, so it does
not prove determinism for every fit or worker count.
