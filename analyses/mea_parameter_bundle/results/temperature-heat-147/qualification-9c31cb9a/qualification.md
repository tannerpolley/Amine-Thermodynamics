# Engine 9c31cb9a qualification: two checks pass; completion awaits a code-budget decision

The historical replay and frozen-law mapping pass on the pinned wheel. No numerical
failure occurred. Calorimetric qualification is incomplete: the retained driver
does not implement the phase/feed admission, independent enthalpy, anchor,
conditioning or heat-Jacobian checks. Completing these checks is estimated to
require 80–110 further readable lines, beyond the task's about-60-new-line stop
threshold and potentially beyond the 94 lines remaining. This estimate is not a
completed implementation or an approved increase. The parent's budget decision
is pending; no calorimetric calculation has run.

Evidence type: **numerical verification only**. The replay uses the historical
adopted vector, chemistry, 84 states and 142 targets at 293.15–333.15 K, with
independent empty caches. Frozen Phase A source laws and inputs remain unchanged.

| Check | Outcome and retained numbers |
|---|---|
| 1. Historical replay | Pass. Pressure cost 8.143453130514477, species 24.848444130706277, total 32.99189726122075. Differences from the unchanged benchmark are −3.730349362740526e−13, 0 and −3.765876499528531e−13. Maximum prediction/allowance ratio is 1.7684921378575326e−5. Maximum pressure relative difference is 1.7684921378575326e−13; all species differences are zero. |
| 2. Frozen-law mapping | Pass. Twelve R2/R4/R5 direct ln K values at 293.15, 313.15, 333.15 and 353.15 K give maximum absolute difference 7.815970093361102e−14, below 5e−13. Stored/native polynomial RT² derivatives differ by zero. Reference pressures are R2 101325 Pa and R4/R5 100000 Pa. |
| 3. Vinjarapu 0→0.11, then 0→0.45 | Unrun. Neither Δh value exists on this wheel. Exact-zero endpoints, available total H, feed balance/root and phase admission are unqualified here. |
| 4. Independent total H, neutral-anchor shift and conditioning | Unrun. No conditioning ratio or anchor-invariance result exists. |
| 5. Exact heat Jacobian against h/2h centered re-solves | Unrun. Fine/coarse maximum error ratios are unavailable. |
| 6. Convergence and conservation | Training portion passes: maximum material error 2.0605739337042905e−13 mol, charge error 3.7951851945411784e−14 mol and stationarity 3.979039320256561e−13. All 84 requested tolerances are met. Calorimetric endpoints are unrun. |
| §6.1 phase boundary/feed admission | Unrun. No bubble separation, regular pure-CO2 root or local phase admission is claimed. |

`old-replay-states.json` retains returned states and diagnostics;
`old-replay-targets.csv` retains every comparison; `old-replay-checks.csv` and
`training-residuals.json` retain conservation checks assembled from those states
and the unchanged packet. The latter checks require no new Engine solve.
`native-law-mapping.csv` retains both ln K and RT² derivative values and source
pressures. The derivative check compares polynomial coefficients; it does not
qualify a solved-state temperature action. Phase A representation grids and
continuations retain their previous admitted limits.

The wheel archive SHA-256 is
`b83c42502235e8915cd07b0eabf24398c7f54a884d41ca914273ddd0f1703667`, from source
commit `9c31cb9a89b6fb42fd386ca44de2331601b4751c`. The fresh separate clone's own
setup restored its fingerprint-matched shared cache; no fresh C++ compilation
is claimed. Wheel fingerprint:
`b0c619cbf23f94b51f636a2139374fa364fdd3393f8234ee78a0e4936a0b86e2`.
Build fingerprint:
`6e53a1c224bbd5df9f64c123629136fafb1ab796f2e8efb686399c9594c345c8`.
Toolchain fingerprint:
`f6db693e21e289603ae71c78242a17b102f1e324061021d5dca361f47a0bfef7`.

The noneditable install is in the new private `.venv-9c31cb9a`; actual module
origin is recorded in the results and `wheel-identity.json`. The Engine's
verification confirms all 14 wheel RECORD hashes, and the retained driver
confirms all 18 hashed installed RECORD entries. Installation metadata was not
rewritten. The first preparation import lacked NumPy; its full log is retained.
Declared dependencies were installed before any numerical check. The clone
remains clean, and the protected old venv and source checkouts were not used.

All heavy jobs used `agent-heavy --timeout 30m --max 8G`. Build jobs were one;
replay used 12 processes under the actual 12-CPU affinity, with OMP, OpenBLAS
and MKL threads all one. Replay wall time was 5.901135103 s and summed worker
time 53.588810458 s. Its enclosing invocation took 205.12 s including the
serialization wait. Mapping's enclosing invocation took 49.79 s including its
wait, with user/system CPU times 0.31/0.11 s; native ln K calls were not timed
separately. Charging the whole mapping invocation conservatively gives
103.378810458 s of new budget use, about 163.38 s including the earlier roughly
60 s, against the unchanged 50,400 s ceiling. Preparation wall time, including
its wait, was 576.82 s; it is a wheel prerequisite, not a numerical study job.

The retained historical driver is unchanged. The new 25-line runner selects
the successor pin, new outputs/caches, actual build-job count, installed RECORD
verification, module origins and the 175 s state budget. Numerical criteria,
starts, chemistry and historical benchmarks are unchanged. Accounting from
`76ea465fe1ede72257a809d04fc986489c5267f3` gives **331 + 25 = 356 used; 94 of 450
remaining**, with no tests added. The protected pre-existing untracked diagnosis
is excluded from this task's additions and remains untracked.

Local commits `ff50239` and `effa030` retain wheel identity and the runner.
Independent delivered review remains with the parent. No fit, loaded solve
above 333.15 K, #152/#160 input substitution, notebook, manuscript, remote
publication or parameter adoption occurred. The two completed checks establish
replay and mapping agreement only; calorimetric capability and physical
agreement remain unresolved.
