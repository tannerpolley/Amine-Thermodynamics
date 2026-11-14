# Bounded stability diagnosis for Part I

The 13 missing parents are numerical closure failures in the declared reacting
liquid–vapor solve, rather than missing input or a failed liquid/bubble
calculation. All have successful liquid and bubble solves. Their initial and
bubble-seeded attempts converge to a nonzero defining-row residual, despite
native `solver_status=SUCCESS`. The classified maximum is
4.07245e-5–8.50955e-5, against the producer's `EQUILIBRIUM_ROW_RESIDUAL=1e-10`.
This is not a rounding-floor or detected rank-deficiency termination: index
108 has rank 20, nullity zero, and estimated floor 6.13823e-18.
Its dominant compiled row is `Chemical`, phase 0, component index 1
(monoethanolamine); its raw residual is about 45097.34484 and classified
residual 7.76186471e-5. Raw and classified residuals have different
normalizations and must not be compared as the same quantity.

Recovery used the two closest successful two-phase parents (temperature,
loading and log-pressure distance), passed as exact coordinate starts to
`solve_equilibrium_starts`, with two attempts, 400 iterations per attempt,
and 800 total. All 26 attempts reach the same residuals to the displayed
precision: **0/13 recovered; 13 unresolved**. Index 108 is 313.15 K,
loading 0.4 mol/mol, 3276.642223 Pa; its successful bubble pressure is
6926.027603 Pa. This identifies an initialization-insensitive nonroot
attractor in the shared closure driver. The reason the driver cannot escape
that attractor is unresolved; these results establish neither absence of a
physical two-phase solution nor a physical instability. Altering the generic
closure/scaling algorithm belongs to Engine, beyond these read-only probes.

Of the 262 unsuccessful liquid trials, 149 have no optimizer message and
are explicit condensed-domain exclusions; 113 have a stalled optimizer.
**All 113 also carry the same condensed-domain exclusion**, so the two
message classes are not independent physical causes. The stalled end points
have log-packing coordinates corresponding to packing fractions
1.44929e-5–0.00430792, with residuals 0.000320986–0.000973352. The native
post-optimization check rejects their charged compositions outside the liquid
side of the pressure-density roots. Density-independent permittivity is
restricted to the condensed side by the existing Engine admission rule.
This explains why these points cannot supply admitted tangent-plane values;
a stalled optimizer alone would not establish that explanation.

Recovery first supplied the admitted central liquid composition and packing
as liquid trial guesses to the same stability producer (149 state attempts).
That recovered no matching stalled trial. Inspection of pinned Engine commit
`391dfe5d`, `engine/native/equilibrium/phase_stability.cpp:597–649`, explains
why: optimized searches construct their own native seeds; custom composition
and packing are consumed only for direct supplied-point evaluation. Thus this
attempt does not test a changed optimizer start. No local trial optimizer was
implemented. Fifteen central-state restorations in this first probe failed;
those states have no new optimized-trial evidence.

The second recovery passed the 113 stalled compositions, without a packing
guess, to direct supplied-point evaluation, asking the native liquid-root
selector to reclose density. At 81 states, **110/110 tested compositions were
excluded by the condensed-domain rule before an optimizer ran**. Central
restoration failed at indices 47 and 98, leaving three compositions untested
by this recovery. Thus **0/113 original optimizers recovered; 113 remain
unresolved** (110 have a repeated direct domain exclusion; three retain the
original exclusion only). Direct domain exclusion does not show that all
other compositions are outside the domain, or that an interior trial minimum
cannot exist. The unresolved generic limitation is that the trial driver can
leave the admitted condensed domain and the public search offers no custom
optimized start or domain-constrained recovery. No no-descent result follows.

The original 25/162 descent states, 13 missing parents, zero complete
no-descent states and all supplied-trial evidence remain unchanged. These
probes are numerical diagnosis, not physical validation or a new census.

## Engine request for owner routing

Please diagnose nonroot closure and condensed-domain trial recovery on merged
Engine `391dfe5d64ede5036bf160bc6ae037ad5e14af32`, wheel SHA-256
`0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b`.
Use MEA parameter record `polley-2026-explicit-defaults.json`, SHA-256
`be66f6cf9df77201a632d73a3c3e341f66ce7fc77b69c3d657288f4c1899a76b`.
Declaration: #255 `final_evidence.flash_problem`, nine reacting liquid
species and three neutral vapor species, feed 9.7292821 mol MEA,
76.9751925 mol water and loading times 9.7292821 mol CO2; unchanged reactions,
reference and row tolerance 1e-10. Exact state and prior starts are in
`part1/published/census-raw.json.gz`; the probe outputs are in
`stability-diagnosis/recovery-results.json.gz`.

Parent reproducer: index 108, T=313.15 K, P=3276.642223163914 Pa,
loading=0.4. Consume a fully closed, admissible parent and defining-row,
rank, floor, phase amount, composition and density diagnostics; current
residual is 7.76186471e-5 despite a successful 6926.027603 Pa bubble solve.
Acceptance: recover the declared parent with raw and classified residuals
within the existing 1e-10 admission, positive mechanical derivatives and
admissible phase amounts, or demonstrate why no admissible parent exists;
do not relax tolerance or count nonconvergence as stability.

Trial reproducer: index 19, `positive-neutral-base` liquid trial, exact
composition and raw coordinates retained in `supplied-19.json` inside the
gzip. Consume an optimized, condensed-domain-admitted tangent-plane value,
its closure residuals, density-side evidence, donor and descent diagnostics.
Current residual is 0.0009733521053, packing fraction about 1.45137e-5,
and the final charged point is domain-excluded. Acceptance: retain the
existing permittivity domain, permit a genuinely condensed optimized recovery
and report all residuals against 1e-10, or return an explicit unresolved
search with the exhausted recovery and domain reason. Preserve every existing
resolved descent; a direct evaluated point is not a successful optimizer.
Extend diagnosis to the listed 13 parents and 113 stalled trials before
claiming class-wide recovery.

## Execution and retained evidence

Disposable probes `/tmp/issue339_diagnose.py` and
`/tmp/issue339_trial_recovery.py` imported `same_data_part1` then
`phase_diagnosis_255`, verified the pinned wheel, and used the existing
#255 `flash_problem`, phase serialization and stability producers. No Engine
source or persistent numerical method was edited. Their SHA-256 hashes are
in `summary.json`. Commands, from the task worktree:

```bash
agent-heavy uv run --no-project --python /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python python /tmp/issue339_diagnose.py
agent-heavy uv run --no-project --python /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python python /tmp/issue339_trial_recovery.py
```

Both ran as background shells, with process pools sized by
`AGENT_HEAVY_CORES` and single-threaded numerical libraries inherited from
`stable_refit_255`. `recovery-results.json.gz` preserves each output under its
original JSON filename, including initial restoration failures, every parent
attempt, supplied-point exclusions and compiled parent-row identities.
`summary.json` gives counts without replacing the raw evidence. Probes are
not retained implementation and add no executable lines.
