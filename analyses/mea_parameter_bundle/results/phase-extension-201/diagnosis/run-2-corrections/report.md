# Caller correction and diagnosis at 393.15 K

Both index-6 parents now converge and complete their nine-trial searches, with
zero resolved descents. Same-temperature parent continuation does not correct
the A7 trial failures at indices 25, 42 and 51. The corrected extension contains
zero detected A7 descents in 540 returned trials of 729 scheduled slots:
54/81 completed states, 6/81 unresolved and 21/81 excluded by pressure admission.
It remains incomplete finite-search numerical evidence, without global
stability or physical-validation claims. Delivered review of this correction
and investigator promotion remain pending.

## Conditions and numerical boundary

The Ready revision-2 design has SHA-256
`fb771344530184e34fe80c884cbd552780472db9d8abab8c217adc9945992b49`.
The feed is 9.7292821 mol analytical MEA, 76.9751925 mol water and
`loading * 9.7292821` mol CO2. Liquid supports all nine model species;
vapor supports neutral CO2, MEA and water. Temperatures are K, pressures Pa,
phase amounts mol, and densities mol/m³. All probes use 393.15 K.
The row tolerance stays at `1e-10`; trial starts, Engine optimizer settings,
iteration limits, reference pressures and admission rules are unchanged.

A6 parameter-byte SHA-256 is
`ceefc95cd051fb291e0c08675c4cb6f159bf10dca0116ef1251ba78c243f79c7`;
A7 is `e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e`.
Engine is merged commit `8298c6029ebb8b467929badc4a223c580ec591ab`, immutable
wheel SHA-256 `8897a0caab9f2508ed642f42c8b5226957fbe7035ed7bfdad71e4166798785b3`.
Every probe verifies that wheel and records parameter, parent, seed and producer
hashes, installed package path, versions, niceness and numerical thread settings.
The inherited branch was fast-forwarded to `0b37cba` before editing.

## Probes 1–2: index 6, loading 1e-5, 86,666.50099025687 Pa

`bubble_recover` previously passed nine vapor mole fractions, including six
zero ionic entries, to a three-component declared support. The pinned Engine
requires the composition width to equal that support's width
(`engine/native/equilibrium/gibbs_minimizer.cpp:1725–1733` at the commit above).
The correction maps each phase's model-order composition through its declared
support. This also preserves the support ordering. It leaves the two declared
liquid fractions 0.5 and 0.9, their amounts, packing fractions, two-attempt
limit, 400 iterations per attempt and 800 total unchanged.

| Probe | Fit | Recovery iterations | Maximum raw parent residual | Reported reduced-Hessian minimum | Liquid / vapor amount, mol | Search |
|---|---|---:|---:|---:|---|---|
| 1 | A6 | 90 | 2.84217094304e-14 | 4.21557890267e-12 | 3.85062909754 / 82.8538455879 | 9/9 successful, 0 descents |
| 2 | A7 | 23 | 2.78532752418e-12 | 3.89469868119e-11 | 3.89021229719 / 82.8142634305 | 9/9 successful, 0 descents |

Both cold parent attempts still exhaust their original limits. The corrected
0.5 start converges, and the Engine selects it without attempting the second
declared start. Both accepted parents meet the unchanged checks, including
positive amounts and pressure-density derivatives. Full compositions, residuals,
density diagnostics and searches are in `p01-index6-A6.json` and
`p02-index6-A7.json`, under `row`. Neither returns a descent, so neither needs
a seeded confirmation. The original 17/27 successful representative A6
confirmations remain unchanged, covering 13/21 descending states.

## Probes 3–8: reproduce, then attempt parent continuation

For each reproduction, the original single-liquid solve returns coordinates
exactly equal to the retained parent; an assertion records that equality before
the unchanged nine-trial search. Each continuation starts the parent from the
composition, packing and liquid amount of the successful same-temperature
neighbour named below. The target feed, temperature and pressure remain fixed.
Every parent converges and every probe returns nine trials with zero resolved
descents; exactly the liquid `near-pure-0` optimizer fails in each search.

| Index | Loading | Pressure, Pa | Reproduction | Continuation and source | Failed trial after continuation |
|---|---:|---:|---|---|---|
| 25 | 0.1 | 2090794.0240735733 | Probe 3: stalled, 2.372130093496704e-6 | Probe 6, index 24 | stalled, 2.3721300935317215e-6 |
| 42 | 0.25557798094241313 | 3300912.557525805 | Probe 4: row residual 4.042584254710358e-16; Hessian check fails | Probe 7, index 43 | row residual 2.0212921273551795e-15; Hessian check still fails |
| 51 | 0.3 | 3908890.0218429407 | Probe 5: stalled, 1.7073970118474764e-6 | Probe 8, index 52 | stalled, 1.7073970130726587e-6 |

At 25 and 51, every failing classified row is chemical stationarity for an
ion: protonated MEA, carbamate, bicarbonate, carbonate, hydronium or hydroxide.
Carbonate gives the largest residual. The unweighted carbonate chemical-row
residuals are 237.212978181 and 170.739656814; the corresponding classified
residuals are the stalled values above. Five ionic log mole fractions are
near `log(1e-8) = -18.420680744`; protonated MEA is near `4e-8` in mole fraction.
Pressure, normalization, material-balance and charge diagnostics are below
the requested row tolerance. The numerical floors, 5.79e-14 and 1.98e-13,
are far below the stalled residuals. Full row identities and both raw and
classified values are retained in the probe JSON and `failing-chemical-rows.csv`.

Both reproductions and continuation attempts retain
`trial preparation failed: invalid composition`. The Engine carries optimizer
preparation errors into refinement and can record rejected Newton candidates
(`gibbs_minimizer.cpp:930,1054–1067,1222–1228`). The returned trial composition
is its retained admissible point; the invalid rejected coordinates are not
returned. The message therefore does not identify which rejected coordinate
was invalid, and does not show that the retained physical composition itself
is invalid. Positive evaluated tangent-plane distances of about 2.3511 and
2.6933 do not complete these failed optimizations.

At index 42 the stationarity rows converge, but the equilibrated Hessian
minimum is -1.0581048500379191 against rounding band 4.9747098120274285e-14.
Continuation returns -1.0581048500379198 against 4.9747098120275282e-14.
This is a failed minimum check, far outside rounding. The positive evaluated
tangent-plane distance, about 2.7993, does not waive it. The native curvature
gate is `gibbs_minimizer.cpp:1313–1328`; the `convergence.stop` field describes
stationarity and must not override the unsuccessful optimizer result.

Ranked explanations for 25 and 51 are trace-composition row conditioning or
refinement near the optimizer's composition bounds, followed by a rejected
step or stopping-rule limitation. Parent initialization alone is not sufficient
in the tested continuation. For 42, a stationary trial that is not a local
minimum is directly supported; parent continuation does not change that outcome.
Neither diagnosis establishes absence of an admissible minimum elsewhere.
Indices 10, 11 and 22 retain the earlier diagnosis and were not re-probed.

**Proposal for Design and the Engine owner:** inspect the rejected candidate
coordinates and chemical-row scaling/refinement for 25 and 51, and investigate
how the existing optimizer reaches a minimum rather than this negative-curvature
stationary point at 42. The MEA declaration and exact cases above provide the
reference cases; completion requires the original 1e-10 row tolerance, all
existing feasibility checks and the native positive-curvature check. Any change
to optimizer mechanics, trial starts, tolerances or iteration limits needs its
own design/ownership decision. No such correction was applied or claimed here.
This proposal was not posted remotely.

## Corrected reductions and provenance

`phase-family.csv`, per-fit `reduction.json` and `summary.json`, `trials.csv`,
`counts-by-temperature.csv`, `outcomes-by-temperature.csv` and
`phase-family-combined.csv` are a corrected view. They use run-2 evidence
everywhere except the separately retained index-6 rows. The unchanged
`phase_extension_201.reduce` constructs all 162 state rows and 1,458 scheduled
slots; source paths are then resolved to their actual retained files. Paths
in `source_path` and `reference_path` are relative to the bundle's `results/`;
`source_field = row` identifies a wrapped correction result, while a blank
source field identifies an original point document. Probe timings are separate
in `budget.json`. The two new searches add nine returned slots each, remove
one missing-parent state per fit and add one completed two-phase state per fit.
No continuation probe replaces an original state. The old 73-state family
retains both indices 0 and 41 and appears before extension indices 73–153.

`split-confirmations.csv` retains all 41 descending-trial links and points to
the existing run-2 confirmations. All 285 run-2 files and the original 155
run-1 files remain byte-identical; `verification.json` records the checks.
The notebook presents categorical results; plotting would add no information
about these incomplete optimizations. There is no new physical validation,
parameter uncertainty estimate, fitted parameter change or manuscript edit.

## Commands, allocation and code accounting

The exact eight worker commands, captured process IDs, elapsed and CPU times,
exit outcomes and kill information are in `budget.json`; their logs are retained.
They run through `probes.py --run-2`. For example, the reproduction of index 25
used `trials p03-retained-A7-25 --index 25`, and its correction attempt used
`trials p06-continued-A7-25 --index 25 --seed` followed by the run-2 A7
`point-24.json` path. Every output name is new; existing probe names are rejected.
The shared ledger enforces 600 wall-s and 1,800 CPU-s for this set, retaining
the earlier diagnosis allocation separately. Each command also has the existing
150-second probe deadline. Only its captured process group can be terminated.

The whole eight-command run, including supervisors and unsuccessful probes,
used **40.21 wall-s and 39.88 CPU-s**, maximum resident memory **94,840 KiB**
(`command-time.json`). The summed worker ledger is smaller because it excludes
supervisor overhead; the whole-command numbers are used for allocation.
All work ran with `nice -n 10` and OMP, OpenBLAS, MKL, BLIS and NumExpr thread
counts set to one before numerical imports. No process was killed or timed out.

Against base `2738fce`, the study implementation adds **300 gross executable
lines**: 284 in `phase_extension_201.py`, 16 in `final_evidence.py` (nine removed).
The retained diagnosis script adds **195 lines**. These meet their separate
300-line and 250-line ceilings, respectively: **495 executable additions total**.
The prior 299-line statement omitted the inherited diagnosis code. The separate
test addition pins the support-width/order defect and preserves amounts,
packing fractions and work limits. Prose and generated results are counted
separately by `change-accounting.json`.

The existing caller owns recovery; no replacement solver or extra recovery
path was introduced. `family_job` remains its caller. The superseded expression
that supplied the full vapor vector is removed. Checks and rendered notebook
evidence are retained in `checks.log` and `verification.json`.
