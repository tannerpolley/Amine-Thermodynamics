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
fit iteration 4.3–7.8 times slower (5.7 times on the means) than the same objective without them.

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

Stopping tolerance is a minor part. Replaying each retained cost history
under Ceres's function-tolerance rule (stop when an accepted step lowers the
cost by at most ftol relative), with the fits' ftol 1e-10 as the baseline:

| Fit | Accepted / rejected | Steps under 0.01 % | Time after within 0.1 % of final | ftol 1e-4 would stop at |
|---|---|---|---|---|
| Route 2 converge-1 (time limit) | 62 / 19 | 26 | 0 s | 552 of 1,206 s, cost +2.92 % |
| Route 2b larger-dV (converged) | 56 / 26 | 22 | 164 s (14 %) | 574 of 1,196 s, cost +1.66 % |
| Route 2b smaller-dV (time limit) | 45 / 8 | 19 | 180 s (15 %) | 560 of 1,214 s, cost +0.88 % |

The small steps sit on plateaus 0.9–2.9 % above the final cost; the longest stretches with under
0.1 % total cost drop last 338–543 s, and they end in real drops. In the larger-dV fit
the 56 accepted steps took 1,140 s and the 26 rejected trials 56 s.

**Superseded (2026-10-17):** this replay treated a function-tolerance stop as the end of
the fit. The Engine fit (`fit.cpp`, active-set loop) instead runs rounds: each round is a
Ceres solve with some coordinates held at bounds, and a held coordinate whose gradient
points back into the box is released only after a round's Ceres solve converges. A
tolerance stop therefore ends a round, not the fit. The measured effect of the tolerance
and the plateau cause are in "After Engine #595" below.

Measured compute in the program to date is about 6,790 s: the 484 s before
Route 1 entry, 5,716 s of retained call timings in amendments 2–4 (one per call,
command-time duplicates removed), and about 590 s for these probes. The six long
reactive fits are 5,284 s of it. The rest of the 19,605.51 s ledger is the fixed
conservative charges for preparation, review and reporting.

## After Engine #595 (2026-10-16/17)

Wheel `main-21e761c3` (sha256 `d2f61e3a…0357`) contains Engine #595. Same
objective and start as above, plus the #191 CO₂/MEA `no_cross_association`
item in a probe copy (84ca269d ignores that key). Numbers are in
[after-595.json](after-595.json); probes were `tmp/fit-time-21e761c3/`.

**Same objective.** At the start, 203 of 205 rows give bitwise-equal values and
exact derivatives on 84ca269d and 21e761c3. The two 318.15 K Hilliard Cp rows
differ by at most 3.1e-12, scaled by each row's largest derivative. Serial
evaluation of all rows: 48.6 → 17.1 CPU-s (host load about 4).

**Iteration time, 32 workers** (same host load, 5–10, back to back):

| | 84ca269d | 21e761c3 |
|---|---|---|
| Without the four Cp rows | 2.14–2.32 s | 2.14–2.15 s |
| With the Cp rows | 19.2–19.5 s | 3.43–3.50 s |

With the Cp rows the new iteration is 1.62 times the one without them; #595's
per-row criterion (about 2 CPU-s) is met, its alternative 1.5× iteration
criterion is not.

**Whole fit.** The Route 2b larger-dV continuation replays identically: the
same 82-iteration accept/reject sequence, final cost within 2.9e-13 relative,
optimizer within 8e-9 scaled units, the same seven active bounds. Wall time
is **246 s** against 1,266 s (CPU 3,337 s against 7,616 s), at host load 14–22.

**Plateau cause.** The two crawls (iterations 46–59 and 75–82) are linear
convergence of a round's Ceres solve: each accepted step lowers the cost by
about 0.4× (first crawl) and 0.18× (last) of the previous step's decrease,
down to 2.5e-10 and 3.4e-10 relative. A fit stopped at iteration 59 retraces
the full replay bit for bit and shows the state there:

- The free coordinates' gradients are 1.1e-7–2.5e-5 in magnitude.
- Two held coordinates have gradients pointing back into the box. Carbamate
  Born diameter (index 8): held at 2.0 Å, g = −0.024; it ends at its 5.0 Å
  upper bound. Carbamate ε/k (index 15): held at 1,000 K, g = +0.0087; it ends
  free near 672 K.
- Protonated-MEA ε/k (index 14) is free at about 764 K and ends at its
  950 K upper bound.

The first crawl is therefore the round polishing the free coordinates to the
1e-10 function tolerance while the descent that matters waits for the
release; the release at the round boundary is inferred from the Engine's rule,
the held gradients at iteration 59 and the endpoint, not traced (a trace forces
one worker, `fit.cpp:486`). The last crawl is the final round converging to
the same tolerance. A coordinate crossing from one bound to the other is the
model-form question of amendments 3–4, not a fit-speed defect.

**Tolerance, measured.** The same fit with function tolerance 1e-6 instead of
1e-10 follows the identical path to iteration 50, ends that round nine
iterations earlier, releases the same coordinates and continues the same descent:

| | ftol 1e-10 | ftol 1e-6 |
|---|---|---|
| Iterations / Jacobian evaluations | 82 / 59 | 68 / 45 |
| Wall | 246 s | 189 s |
| Final cost | 36.785655 | 36.785669 (+3.7e-7 relative) |
| Active bounds | 7 | the same 7 |
| Largest optimizer change | — | 0.10 scaled units (carbamate ε/k, about 1 K) |

Linearized over the nine free coordinates (residual variance 0.375), the 1e-6
endpoint lies 0.011 conditional standard errors from the 1e-10 endpoint. The
remaining 45 Jacobian evaluations, against F1's 12, come from 16 coordinates of
which seven end on bounds; each new bound contact or release restarts a round
with a fresh trust region, which is where the 25 rejected trials (about 21 s) fall.

This is numerical evidence about cost and convergence, not a physical result.
Single runs on a shared host; times scale with load.

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
