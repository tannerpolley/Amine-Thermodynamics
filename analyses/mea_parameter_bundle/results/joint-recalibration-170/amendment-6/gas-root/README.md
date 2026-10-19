# Amendment-6 gas-root scratch probe

The revision-3 **tied start** returns **pass**: both native root requests
return one root at 58010.42820851521 mol/m³, denser than the newly solved
liquid. The physical solve and all seven dilution points complete.
**Numerical qualification only: this start is not the selected vector, these
outputs are not selected-vector gate evidence, and they are not physical
validation.** No fit was run. Independent delivered review remains with the
parent task.

`probe.py.txt` is a disclosed one-off calculation excluded from the campaign
ceiling by the [owner decision, item 2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6278338236),
under the [scope decision, item 4](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6276283139).
Campaign script additions/removals are zero. The executable scratch text,
invocations, outputs, timings and hashes are retained here.

## Calculation and gate

One hash-checked candidate is evaluated at exactly **318.15 K,
3699.0803800848512 Pa, loading 0.25557798094241313 mol CO₂/mol MEA**.
`final_evidence.flash_problem` supplies the original feed: 9.7292821 mol MEA,
76.9751925 mol water and loading × 9.7292821 mol CO₂. Chemistry/reference
preparation uses `heat_evidence_170.request(mapping,313.15,.11)`, exactly as
in the phase-family dispatch; the flash receives the exact test T/P/loading.

The probe requests both native vapor/liquid roots at the normalized ionic
gas-witness composition, solves a new two-phase physical state cold at
1e-10 row tolerance, evaluates both old packing-coordinate witnesses and
scans densities **1e-6, 1e-3, .01, .1, 1.4, 10, 100 mol/m³**. The historical
vanished vapor amount is clamped to zero as in the screen. Source-density
contributions and packing-coordinate Gibbs evaluations remain separate.
Engine owns every EOS and Gibbs evaluation. Bulk Born uses the screen's
`c_dielectric=0` diagnostic; full minus bulk gives shell Born. The solved
model retains its original coefficients.

A native stable ionic root on the declared dilute support **fails**,
regardless of Gibbs ordering; this includes a lower-Gibbs stable ionic gas
root there. Incomplete root searches or physical solves are **unresolved**.
Passing requires both native requests to find the same sole stable root,
denser than the new physical liquid, completed witnesses/scan, positive
pressure-density derivatives, raw physical residual ≤1e-10 and nonnegative
reduced-Hessian minimum. Additional roots without a dilute-root witness
remain unresolved. No absolute gas/liquid density cutoff is invented.
The dilution check retains decreasing |ε−1| and |bulk Born| toward the dilute
endpoint, without adding an endpoint threshold. A finite shell is disclosed.

## Retained quantities

Each invocation writes one incremental `gas-root.json`; partial numbers
survive failure or interruption. No prescribed item is omitted in the final
qualification.

| Design item | JSON fields |
|---|---|
| State, feed, candidate/wheel identity, reactions/reference | Top-level state/identity fields, `engine`, `candidate_reaction_system`, `neutral_reference` |
| Both old witness evaluations, full coordinates, Gibbs and raw row/closure evidence | `witnesses.{gas,physical}.source`, `.evaluation`, `.charge_closure` |
| Original source-density contributions plus pressure-density derivative | `witnesses.*.source_density_contributions` |
| Both root requests, counts, densities, pressure/derivative, residuals, iterations/evaluations and stopping reasons | `root_requests` |
| New physical coordinates, amounts, compositions, densities, packing, pressure, raw/classified residuals, closures, multipliers, local-minimum evidence, work/messages and contributions | `physical_solve` |
| Native Gibbs re-evaluation and witness differences | `physical_solve.closure`, `.native_objective_re_evaluation_difference_over_RT`, `witnesses.*.witness_minus_physical_G_over_RT` |
| All seven densities, ε→1, bulk Born→0 and finite shell | `density_scan`, `dilution` |
| Bound, stopping point, missing/nonfinite values and gate decision | `timing`, `stage`, `error`/`traceback` when applicable, `nonfinite_diagnostics`, `classification`, `reason` |

Contributions retain amount, composition, density, EOS pressure, its difference
from imposed pressure, ε, hard-chain, dispersion, association, polar,
Debye–Hückel, bulk/shell Born and residual A/RT. Native objects are explicitly
serialized; unsupported objects are rejected instead of stringified.

## Qualification and limits

Input: `../inputs/revision-3/tied-start.json`, SHA-256
`aabe31750b71bc13a20188a5bc589a8a2182ba994a8005a2d1f3c48c54f4d403`.
Exactly **three** Engine-backed invocations completed, all **pass**, with GNU
wall times **4.97, 5.80, 5.08 s**. Attempts 1/2 retain their executed probe
texts; attempt 3 matches the final probe. Attempt 2 adds explicit charge
reporting and preserves the basic physical result before further evaluation;
attempt 3 checks that the sole ionic root exceeds the solved liquid density.
All retained thermodynamic numbers are identical between attempts.

The final physical liquid/vapor densities are 29240.137146619792 and
1.3990539161205706 mol/m³, with maximum raw residual 1.1368683772161603e-13
and total charge 9.714428544548898e-15 mol of elementary charge. Gas/physical
witness G/RT minus new physical G/RT are +2860.709956528466 and
+28.05819454522134. At 1e-6 mol/m³, ε−1 is 1.035124208570437e-9, extensive
bulk Born/RT is −3.1493324274075534e-6 and shell Born/RT remains
−818.3912644412122, on the retained 86.70447547705399 mol basis.
[Qualification summary](qualification/summary.json) contains every scan
value, work/time, Gibbs comparison and source identity; each raw JSON keeps
all diagnostics. [Offline checks](qualification/offline-checks.json) cover
failure classification, serialization and hash rejection without more Engine
calls. `SHA256SUMS` and `change-accounting.json` record retained-file hashes
and changed lines; executable `.py.txt` scratch is disclosed separately from
the campaign ceiling, regardless of its accounting-file category.

The two old witnesses have large residuals and are **not new converged
states**. No converged ionic gas state exists to receive a new Gibbs value
here. These finite supports do not prove global phase stability. No
uncertainty interval, experimental validation, selected-vector conclusion,
notebook promotion or manuscript change is claimed. The local literature
shelf is absent; no new literature-backed judgment is made.

## Sources and execution

Authority: `tmp/joint-design/amendment-6-paper-candidate.md`, §0b, the
function/serialization table around lines 350–372, and §4's gas-root gate.
Historical source: `git show 5ebcb37:analyses/mea_parameter_bundle/results/permittivity-screen-172/permittivity_probe.py`,
functions `contribution`/`falsifier`, and that screen's README discussion of
source-density versus packing-coordinate evaluations. `inputs/` contains
byte-identical witness JSON files and `engine-decomposition.csv` from that
commit, checked by hash. No Engine equation is copied. Build base: `242d788`.

Run from this worktree's root with a **new** output directory:

```bash
nice -n 10 env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /usr/bin/time -f '{"whole_command_user_s":%U,"whole_command_system_s":%S,"wall_s":%e}' \
  -o /tmp/gas-root-time.json \
  /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/tmp/a6/venv/bin/python \
  analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-6/gas-root/probe.py.txt \
  <parameter-document> <sha256> <output-dir>
```

`fit_campaign.bounded_call` owns process termination at the 300-second
whole-probe wall allowance, including imports and all calculations. Its
existing termination/kill cleanup can take additional time. Numerical
libraries use one thread. Installed package bytes match the retained Engine
main wheel `21e761c318c2ac5b555a245365c844d38a93e4cb`, SHA-256
`d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357`.
An Engine source checkout is rejected before import. The pinned environment
and running-fit worktree were not modified.
