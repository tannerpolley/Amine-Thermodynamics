# Saturation-capped Merkley heat: pinned Engine capability check

Issue #222, owner comment 6480448810 (2026-10-28), base `6714b76`.
Engine request: https://github.com/tannerpolley/ePC-SAFT/issues/906.
The owner selected native Engine implementation, with no downstream optimizer.
No refit or outside-fit statistic has been computed in this continuation.

`phase-density-threshold.json` declares packing fraction 0.10 before any new
refit endpoint is calculated or read. The diagnosis reports gas-like trials
up to 0.0250923 and dense liquid probes at 0.40–0.46. Gas evolution does not
fail the gate. The stage-2 phase search now declares carbon-free supports at zero loading,
classifies every resolved descending trial by its final packing fraction
independently of the trial kind, and checks each #904 state on the ion-free
liquid and vapor faces. Other unresolved trials and ambiguous densities block
a clean gate. No generic Engine equation or fitting mechanic was added.

## Capability result

The installed Engine files are byte-identical to the pinned wheel at
`3e83e19c`, SHA-256
`0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`.
`merkley-fit-capability.json` retains the constructor signatures, native
observation fields and kinds, the free-feed refusal, loading scans and direct
heat predictions. The installed `regression.py` lines 555–605 declare fixed
endpoint feeds and fixed `feed_amount`. Its `fit` at lines 718–790 accepts a
fixed sequence of native observations and exposes no callback to reconstruct
them for each parameter vector. There is no native saturation-capped heat
observation among the exposed kinds. A free feed amount fails native mapping.

The owner-requested endpoint is min(source loading point, model saturation
loading). The model saturation loading changes with parameters. Replacing the
endpoint only once before native fitting would fit a different objective;
replacing it only after fitting would leave the calibration unchanged.
The derivative must include movement of the saturation endpoint when the cap
is active. The pinned native declaration cannot express that dependence.

## Direct numerical check at declared starts

These numbers are at the item-(l) A1 and B1 starts, not selected or refitted
endpoints. All eight saturation scans have exactly one admitted sign change
on the previously approved 0.05–1.50 loading grid; all eight heat predictions
are available. The source loading points are 1.009, 0.941, 0.587 and 0.360,
respectively. No start-state row is truncated.

| Start | Temperature (K) | MDEA wt% | Model saturation loading (mol/mol) | Integral heat (kJ/mol CO2) |
|---|---:|---:|---:|---:|
| A1 | 333.15 | 20 | 1.138007712 | -49.830172 |
| A1 | 333.15 | 40 | 1.129177580 | -55.985265 |
| A1 | 388.71 | 20 | 0.587069972 | -61.809702 |
| A1 | 388.71 | 40 | 0.504117668 | -75.206615 |
| B1 | 333.15 | 20 | 1.221783401 | -56.564713 |
| B1 | 333.15 | 40 | 1.253007455 | -70.075711 |
| B1 | 388.71 | 20 | 0.730848309 | -67.821075 |
| B1 | 388.71 | 40 | 0.737751645 | -81.489712 |

The cap being inactive at starts does not remove its dependence during fitting.
The prior diagnosis already documents active caps at earlier fit endpoints;
those older endpoints are not reused as the requested refits.

The source definition was checked in Merkley 1987, Results, printed pp.439–441,
against Zotero PDF ED7IMI2E (hash recorded in the retained source inventory):
the reported heat is a through-origin slope of cumulative heat against loading
below saturation. The new endpoint rule is the owner's modeling decision.
These start calculations verify numerical evaluation only; they establish no
physical validation or transfer verdict. Loading-point digitization has the
retained ±0.02 mol/mol uncertainty.

## Completed phase-search verification

`phase-checks/` retains 754 state records per historical A1/B1 endpoint,
including fitted, comparison and saturation states. This is a check of the new
phase classifier on the old vectors, not selection or assessment of a refit.
Counts are state records, including repeated physical states for different
observables; #904 trial counts happen to equal affected state counts here.

| Historical endpoint | Dense splits | Gas evolution states | #904 trials / same-state ion-free checks | Other unresolved | Ambiguous density |
|---|---:|---:|---:|---:|---:|
| A1 | 0 | 42 | 35 / 35 | 0 | 0 |
| B1 | 0 | 40 | 31 / 31 | 0 | 0 |

Carbon-free supports were declared at 153 records per endpoint (including the
unloaded binary states). No zero-loading unresolved trial remains. Gas states
and all #904 messages, their original reports and the ion-free checks are
retained per state. A focused classification check also verifies that a dense
trial fails regardless of its declared kind, a gas-density trial is separated,
and a non-#904 unresolved trial is not ignored. Empty searches cannot pass.

## Both-branch direct acceptance reference

These four additional cases keep the A1 start and vary only a declared test
cap. They exercise both sides of min without changing the source observations
or fitting data. Actual source-cap calculations remain in the eight-row table
above. `both_branch_acceptance_reference` in the capability JSON retains every
scan, root, cap, selected branch and heat.

| T (K) | MDEA wt% | Test cap (mol/mol) | Selected endpoint (mol/mol) | Branch | Integral heat (kJ/mol CO2) |
|---|---:|---:|---:|---|---:|
| 333.15 | 20 | 0.50 | 0.500000000 | source cap | -56.856024 |
| 333.15 | 20 | 1.25 | 1.138007712 | saturation cap | -46.990617 |
| 388.71 | 40 | 0.25 | 0.250000000 | source cap | -78.820538 |
| 388.71 | 40 | 0.75 | 0.504117668 | saturation cap | -69.643705 |

All four scans have one admitted sign change and all four heat predictions
are available. These are numerical references from the pinned wheel, not
physical validation. Fitted-coordinate derivatives of this complete capped
observable remain unavailable until Engine #906; no local derivative or
optimizer substitutes for them.

## Resume after Engine delivery

1. Obtain the wheel built from merged Engine main for #906. Retain its exact
   commit and SHA-256 and qualify the installed immutable wheel; never import
   an Engine checkout.
2. Use the new native capped addition-enthalpy declaration for the four fitted
   Merkley states. At each declared A1 reference state and both min branches,
   compare its value to the retained direct saturation-plus-heat reference
   within replay tolerance 1e-8. Verify native fitted-coordinate derivatives
   against central differences of the fully recomputed observable within
   1e-5 relative; preserve the 1e-10 equilibrium residual tolerance. Record the
   branch/switch convention and any unavailable or nonunique saturation root.
3. Only after qualification, refit A1, A3, B1 and B3 under the unchanged #222
   freeze. Use the implemented density gate at all declared states, retain
   every endpoint and active bound, then write each variant's lowest-cost
   passing endpoint selection before any outside-fit statistic. Resume the
   full assessment and bicarbonate/control follow-up already authorized in
   #222. Corrected Kamps remains excluded from the two-point criterion.

The Engine request owns the generic observable and exact derivative. The old
fixed-endpoint Merkley fitting path has not been relabeled as implementing
#906; it must be replaced when that capability exists. No refits, endpoint
selection, transfer verdicts or follow-up were run. Independent delivery
review remains pending. No MDEA outcome falsifies the MEA bicarbonate value.

Reproduce from this issue worktree with:

```bash
agent-heavy nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/check_merkley_saturation_fit.py
agent-heavy nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/check_density_phase_gate.py
```

Both checks use at most 16 worker processes and one BLAS thread per process.
All writes stay in this issue worktree. The manuscript and Engine source are
untouched. The two phase-search JSON files exceed 5 MB and are retained as
level-9 gzip with raw and compressed hashes in `../compressed-evidence.json`.
Other newly retained files are below 5 MB.
