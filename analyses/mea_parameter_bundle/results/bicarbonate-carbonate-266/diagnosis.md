# Probe reporting and reaction-law replay

The first numerical batch reproduced all 307 fitted observations at total
weighted least-squares cost 148.87893934557388. All 153 comparison predictions
were available. It completed twelve sensitivity evaluations, then stopped
after the first native fitting call while preparing the application report:

```text
SolventSpecification.fit -> fitted_reactions(result.chart)
for q, value in zip(source_coordinates, chart.physical[len(chart.active):], strict=True):
ValueError: zip() argument 2 is shorter than argument 1
```

The native fit termination and parameters were not retained. This establishes
no physical result for the probe and does not identify the native termination
cause. The application previously attempted reaction export even for an
unusable native result. The correction preserves that result's diagnostics
and withholds fitted-law and parameter export when `result.usable` is false.
Whether the first native fit was unusable remains unknown because its result
was lost; the owner-authorized recovery is recorded below.

Inspection also found that direct reaction-coordinate changes were omitted
from the study's sensitivity replay: only `chart.reaction_laws` was transported.
The retained R2/R3 physical values changed by ±0.1, but their replayed predictions
were identical to baseline. The existing `fitted_reactions` owner also maps
direct reaction coefficients; the study now consumes that complete mapping
and compares every fresh sensitivity prediction with its independent native
coordinate evaluation before retaining the result. The initial R2/R3 replay
values must not be interpreted as zero physical sensitivity.

Neither correction changes the objective, source scales, numerical method,
bounds, solver tolerances or parameter adoption. The corrected twelve-case sensitivity replay passed its comparison with native
coordinate predictions. The subsequent fit-repeat decision is recorded below.

The owner then authorized one identical recovery repeat. The repeat retained
`fit1-native.json` and `fit1.json` before stopping: native termination is
`invalid_setup`, with message `reaction coordinate R2: tied declarations or
starts disagree`, `usable=false`, zero iterations, zero residual evaluations
and zero Jacobian evaluations. Physical and optimizer endpoint vectors are
empty. Native initial/final cost fields are both zero because no objective
evaluation ran; they are not calculated costs. No endpoint is assessable.

The first log reached application export; the repeat instead preserved the
native refusal before deliberately stopping. No native trajectory or
termination comparison with the first run is possible because the first
captured output contains neither. No further old-wheel fit repeat was attempted.

Declaration inspection finds that the aqueous and amended R2 polynomials
have equal coefficients, standard state and other reaction fields, with
different upper temperature bounds (393.15 and 436.85 K). The retained
`diagnose-start.json` shows six zero inferred optimizer values for each
declaration separately and rejection of their combination. Explicit native
evaluation of the zero vector gives 326 available predictions and finite
derivatives, without optimization. This isolates admission of the tied
declarations from evaluation of the physical starting state.

Read-only inspection of Engine commit
`3e83e19ccc771b51d8ebc038931ab25192f4c5b5` identifies the refusal:
`engine/native/regression/coordinates.cpp:105` checks `same_reaction` while
inferring tied reaction starts. The comparison in
`engine/native/equilibrium/problem.hpp` (lines 124–136) includes both temperature
bounds. `engine/native/regression/fit.cpp` (lines 1409–1411) applies explicit starts
and then calls the same fit implementation, which again infers the start.
An explicit optimizer start therefore does not remove this admission check.
No Engine source was changed or imported.

The orchestrator identified this as Engine issue 962, fixed in merged commit
`e6dae5c7`, and authorized its immutable wheel for this worktree environment:
SHA-256 `83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6`.
The repository pin remains unchanged. The owner requires a fresh 307-row
replay at relative tolerance 1e-8, with an absolute residual allowance of
1e-8 below unit residual magnitude, plus tied-R2 admission with both original
domains. Probe 1 on this wheel is the authorized repeat's first execution
with actual evaluations; the old-wheel attempt evaluated no objective rows.
Its results use the `fit1-executed` prefix, preserving `fit1-native.json` and
`diagnose-start.json` as the old-wheel refusal evidence. Probe 2 remains
authorized under the accepted design after the qualification gates pass.
