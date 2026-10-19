# Revision 3 declarations: prepared, no fits

Authority: `tmp/joint-design/amendment-6-paper-candidate.md` §0b at Ready
`352bda1`, merged in `8d9e315`. The implementation stopped before completing
the phase producer because the remaining code was forecast to exceed the
250-line addition ceiling. See `../../build/ledger.json` and its README.
These declarations do not establish a fitted candidate or a density-gate pass.

- `stage2b-spec.json` uses the exact Hartono-target endpoint as reference.
  It declares the two MEA–water coordinates, A/B constant-k starts with b=0,
  one slope insertion, and `stage2b-rows.json`: 50 unchanged Cai rows and
  five exact-carbon-zero Amundsen densities, scale 0.5 kg/m³ and weight 10.
  Its wall/CPU budgets are 300/13,440 s; native/nonfit bounds are 60 s.
- `density-source-rows.json` preserves the 20 Amundsen and 32 adopted Hartono
  source cells, printed loadings, source hashes, uncertainty declarations,
  and Hartono x3/alternative-loading fields. `density-scales.json` freezes
  each source/T secant pair, slope, density uncertainty, loading contribution,
  and combined scale. It contains no calculated model densities.
- `joint-added-rows.json` appends the five CO₂-free rows once to the existing
  52 added rows, retaining the 39 Kiepe rows. The two information declarations
  replace the old loaded block with 52 loaded rows and retain four Cp rows.
  Both construct 262 rows with positive weights; the reacting subset is 223.
- `tied-start-pending-stage2b.json` and `held-start-pending-stage2b.json` are
  **templates awaiting stage 2b**, retaining A4's MEA–water k and a newly
  inserted b=0. The Held document changes all six DH diameters to σ; its
  information coordinates change both fitted target factors and serialized
  DH ties to 1. Packing stays at 0.88σ. The tied form retains DH=0.88σ.
- `*-information-pending-stage2b.json` has one start, information λ=[1],
  loaded IDs explicitly frozen, and per-loaded-row weight 1/52.
  `*-fit-pending-stage2b.json` adds one fit case and an intentionally unresolved
  fresh-release hash. Native controls are 180 iterations, function 1e−6,
  parameter 1e−10 and gradient 1e−8. Fit/nonfit CPU allowances are 6,000/500 s,
  and wall allowances 600/180 s, with 32 workers and the pinned merged wheel.
- `source-identities.json` records Hartono adoption `b998d038`, merge
  `e2a2a05`, design readiness/merge, the immutable reference and source hashes.
  `density-selection-183.csv` is the exact historical selection table. Its
  old model-error columns are historical inputs and are not new predictions.

Before any joint information or fitting launch, complete stage 2b and its
required checks. Substitute only its selected MEA–water k and b into each
joint start, retaining all other values, then recompute the start and input
hashes. Refresh the launch budget and program-prior fields from the charged
ledger. Generate a fresh release bound to those exact inputs and replace the
pending release hash. No fitted neutral values have been invented here.
The remaining Build work and qualification must also complete before execution.

Stage 2b still requires the same-wheel constant-k Cai reference and the
specified endpoint density/Cai trade-off check during execution. No such cost
or fitted density is claimed by these declarations.
