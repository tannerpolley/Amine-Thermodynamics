# Why the amendment-2 reactive fits take about 1,270 s (#170)

Diagnosed 2026-10-16 on wheel `main-84ca269d` (sha256 `98a140a0…38d83a`), at
the Route 2b larger-dV start (`route2b/larger-dV/start-parameters.json`,
sha256 `aee26a2d…c2d202`; spec `continuation-fit-spec.json`, sha256
`0d27e844…a076c8`): 205 rows, 16 coordinates, density weight 0, BLAS/OpenMP
threads 1. Host load average during the probes was 35–47 on 32 cores (other
agents), so the absolute times are inflated; the comparisons ran back to back
at the same load.

## Result

The four Hilliard (2008) `equilibrium_isobaric_heat_capacity` rows set the
fit's critical path. Their exact parameter derivatives make each 32-worker
fit iteration about 5–7 times slower than the same objective without them.

| Measurement | Value |
|---|---|
| Serial derivative evaluation, all 205 rows | 84.2 CPU-s, 91.6 s wall |
| Added serial derivative cost per Cp row (318.15/353.15 K, loading 0/0.358) | 27.6, 28.0, 31.5, 33.6 CPU-s |
| Largest added cost of any other row (Vinjarapu 2024 addition enthalpy) | 1.26 CPU-s |
| Four Cp rows evaluated together | 57.6 CPU-s (about half the separate sum) |
| Four Cp values without derivatives | 2.5 CPU-s, so derivatives cost about 50× the values |
| One Cp row called twice | 30.9 then 33.9 CPU-s: no reuse between calls |
| Two fit iterations, 32 workers, without the Cp rows (201 rows) | 4.2 and 6.7 s per iteration; 18.8 s wall, 141 CPU-s |
| The same with the Cp rows (205 rows) | 32.6 and 29.1 s per iteration; 91.1 s wall, 445 CPU-s |

`row-cost.csv` lists the added serial derivative CPU of every row, measured as
the time of [anchor, row] minus the anchor alone (anchor `vle_obs_0119-pco2`,
0.34 CPU-s); small negative values are timing noise. By quantity: Cp 4 rows
120.7 CPU-s; partial pressure 46 rows 21.2; phase mole fraction 94 rows 12.3;
addition enthalpy 8 rows 8.1; all others under 1.1.

## Second factor: iteration count

The retained Route 2b larger-dV continuation took 82 iterations: 59 Jacobian
evaluations at about 20 s each and 25 rejected trials at about 2 s each. Its
cost reached within 1 % of the final value at iteration 67; iterations 44–59
and 74–82 changed the cost by less than 0.01 % each, about 500 s. The
Engine's frozen F1 fit needs 12 Jacobian evaluations. This crawl coincides
with the seven active bounds already reported for Route 2b; that causal link
is not tested here.

## Third factor: host contention

Our own F1 timing fit (wheel `36485a88`, `results/fit-timing-36485a88*`)
converged in 46 s wall on a quiet host and 658 s under load, with the same 14
iterations. Shared-host load therefore multiplies wall time by more than the
lost core share.

## Disposition and limits

This is numerical evidence about cost, not a physical result. The probes were
disposable (`tmp/fit-time-diagnosis/`) and changed no retained
implementation. The Cp derivative cost belongs to the Engine's exact
derivative path for solved reacting equilibria and is reported there. The
fix to the iteration count is the model-form work already in amendments 3–4.
Projected fit times without the Cp bottleneck are not claimed until measured
on a fixed wheel.

Accounting: conservative charge 1,200 CPU-s and 1,800 s active wall, bringing
the program to 53,037.61 CPU-s of 144,000 and 19,605.51 s of 21,600 s, with
the 1,950.38 s check reserve still held. Owner decision 2026-10-16: the
campaign code ceiling is raised from 900 to 1,000 lines; the active-wall cap
is not raised to absorb slow fits.
