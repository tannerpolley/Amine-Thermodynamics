# Engine 9c31cb9a qualification: stopped at the independent feed-query construction

The native 0→0.11 finite-addition calculation returns **−68169.42621173232
J/mol CO2** on the pinned wheel at 313.15 K and 1734000 Pa. Both independently
solved fixed-pressure endpoints return total enthalpy. Qualification then stops
at the first failure: the driver tries a C++ observation enum that is absent
from the Python binding. No independent feed-state calculation occurred.
The 0→0.45 observation and all subsequent checks remain unrun.

Evidence type: **numerical verification only**. The negative native value is
exothermic under the frozen model and declared one-liquid endpoints. Independent
feed/root and local phase admission are unresolved, so the result does not
complete calorimetric qualification or establish physical validation.

| Check | Outcome and retained numbers |
|---|---|
| 1. Historical replay | Pass, retained unchanged: 84 states/142 targets. Pressure cost 8.143453130514477, species 24.848444130706277, total 32.99189726122075. Cost differences −3.730349362740526e−13, 0 and −3.765876499528531e−13. Maximum prediction/allowance ratio 1.7684921378575326e−5; pressure relative difference 1.7684921378575326e−13; species differences zero. |
| 2. Frozen-law mapping | Pass, retained unchanged: 12 R2/R4/R5 values at 293.15/313.15/333.15/353.15 K; maximum absolute ln K difference 7.815970093361102e−14. Stored/native polynomial RT² derivative differences zero. Reference pressures R2 101325 Pa, R4/R5 100000 Pa. |
| 3. Vinjarapu 0→0.11 | Incomplete: native heat −68169.42621173232 J/mol CO2 is available; initial H −2313691.8924407274 J, final H −2364483.718759536 J. Exactly zero initial carbon and zero componentwise feed-balance differences are retained. The same five reaction objects and neutral-reference values are checked. Independent feed-query construction fails as quoted below. |
| 3. Vinjarapu 0→0.45 | Unrun after the earlier failure; no new Δh value exists. |
| 4. Independent assembly, +10 kJ/mol neutral-anchor shift, conditioning | Unrun. Endpoint H values exist, but no independent feed H, assembled comparison, shifted result or conditioning test exists. |
| 5. Exact heat Jacobian, h/2h centered re-solves | Unrun. Fine/coarse maximum error ratios unavailable. |
| 6. Convergence and conservation | Formal check 6 is unrun. Training checks retained from replay pass: material 2.0605739337042905e−13 mol, charge 3.7951851945411784e−14 mol, raw stationarity 3.979039320256561e−13. Returned 0→0.11 endpoints meet requested tolerance; packet-balance errors at most 1.951563910473908e−16 mol, charge 4.96507676858133e−16 mol and raw equation rows 1.2789769243681803e−13. |
| §6.1 phase boundary/feed root | Unrun. No independent root density, derivative, root count or bubble separation was calculated. |

The exact first failure is:

```text
AttributeError: type object 'epcsaft._core.ObservationKind' has no attribute 'FeedEnthalpy'
```

It occurs at `item.kind = reg.ObservationKind.FeedEnthalpy`, before
`model.state(...)` or the independent feed prediction. `feed-0.11.json`
retains the exception, zero feed-balance differences, wheel identity and actual
module origin. `remaining-qualification.json` retains all four subprocess calls,
times, return codes and full child traceback; `qualification-failure.json`
retains the exact stopping point and diagnosis. No later calculation, changed
tolerance, seed, epsilon, guess, chemistry or alternative feed query was used.

Read-only diagnosis uses the pinned clone at `9c31cb9a`. The internal kind is
present in `engine/native/regression/observations.hpp:19` and is used inside the
native addition calculation in `observations.cpp:291`. The Python enum in
`engine/native/bindings/regression_bindings.cpp:18–34` omits it, consistently
with `engine/src/epcsaft/_core.pyi:833–848` and the observed exception. The driver
incorrectly assumed that internal kind was exposed. This is an implementation
error; it demonstrates neither a feed EOS defect nor physical-model failure.
Selecting a supported public independent feed query is the correction boundary.
The stop instruction precludes testing a replacement in this run.

`calorimetry-0.11.json` retains the native heat, input basis and convergence:
classified residual 5.045085355955182e−14, 12 iterations and 22 evaluations.
`state-0.11-0.json` and `state-0.11-1.json` retain independent total H, full
amounts/compositions, raw/classified equations and source-reference diagnostics.
The initial four carbon-bearing species have literal zero mole fractions.
Basis is 1 mol MEA, 7.911062165006594 mol water, unloaded MEA mass fraction 0.3,
and pure CO2 dose 0→0.11 mol. Physical parameter hash is `7e9e3f02723700f8b6577681173249c0e7bd2c8c2a098f38a4e0a7e4611852d5`;
physical calorics hash is `c94d504e68c6dc6e85d3d950cc51422499846729b1a06994b362040be991924a`.

Wheel archive SHA-256:
`b83c42502235e8915cd07b0eabf24398c7f54a884d41ca914273ddd0f1703667`.
Source commit: `9c31cb9a89b6fb42fd386ca44de2331601b4751c`.
Wheel fingerprint: `b0c619cbf23f94b51f636a2139374fa364fdd3393f8234ee78a0e4936a0b86e2`.
Build fingerprint: `6e53a1c224bbd5df9f64c123629136fafb1ab796f2e8efb686399c9594c345c8`.
Toolchain fingerprint: `f6db693e21e289603ae71c78242a17b102f1e324061021d5dca361f47a0bfef7`.
The Engine preparation restored a fingerprint-matched cached wheel in the fresh
separate clone. The noneditable private `.venv-9c31cb9a` has all 14 wheel RECORD
hashes and all 18 hashed installed RECORD entries verified. Metadata was not
rewritten; actual installed module origins are retained in every result.

All heavy jobs used `agent-heavy --timeout 30m --max 8G`; OMP/OpenBLAS/MKL threads
were one. This continuation was serial, with a 175 s timeout plus 5 s kill grace
for every observation/state query. The four subprocesses took 0.701901991,
0.548934818, 0.590324929 and 0.354105625 s: summed wall **2.195267363 s**.
The native heat prediction itself took **0.334117079 s**. The enclosing invocation
took 162.93 s including queue time; user/system CPU times were 2.14/0.34 s.
The conservative cumulative budget charge is about **165.574 s of 50,400 s**.
Earlier replay wall/summed-worker times remain 5.901135103/53.588810458 s;
its pool had 12 single-threaded workers under 12-CPU affinity.

The owner approved 110 further gross executable lines after baseline `df8ab59`
(356 used), with phase ceiling 466 and fits/assessment excluded. The extension
adds **110 lines** and removes one; the removal receives no credit. Charged
accounting is **356 + 110 = 466 used, zero remaining**. The base-to-final-tree CSE
report measures 465 surviving executable additions; the one-line difference is
explicitly retained in the no-removal-credit accounting. No tests were added.
The preserved first two checks used the earlier producer at `effa030`; continuation
producer is `e7ff4b4`, SHA-256 `e6298f03e107dfe9a177ae6a4dc24fb006c4ad82cf9b9910aef494a1187d4c10`.

Earlier qualification records and the protected untracked zero-carbon diagnosis
remain unchanged. No fit, assessment, loaded solve above 333.15 K, input
substitution, notebook, manuscript, remote publication or parameter adoption
occurred. Independent delivered review and any corrected continuation remain
with the parent.
