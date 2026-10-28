# Saturation-capped Merkley heat: pinned Engine capability check

Issue #222, owner comment 6480448810 (2026-10-28), base `6714b76`.
No refit or outside-fit statistic has been computed in this continuation.

`phase-density-threshold.json` declares packing fraction 0.10 before any new
refit endpoint is calculated or read. The diagnosis reports gas-like trials
up to 0.0250923 and dense liquid probes at 0.40–0.46. Gas evolution does not
fail the gate. Carbon-free trial supports and the #904 ion-free check remain
required when execution resumes.

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

## Required decision and remaining work

Recommended: request a native saturation-capped addition-enthalpy observation
and its parameter derivative from the Engine owner, then qualify a merged
immutable wheel before refitting. Preserve the source loading cap, fixed
pressure, zero-loading initial state, heat scale and weights. At each vector,
retain the model saturation loading, selected endpoint, truncation and branch;
refuse absent or nonunique saturation solutions and verify derivatives on
both sides of an active cap. The exact cap switch needs an explicit derivative
convention. Generic fitting mechanics remain in Engine.

An alternative requires explicit owner authority for a downstream fitting
exception using the pinned wheel's direct calculations. No such optimizer or
numerical derivative has been added here. The scientific objective is retained.

For both variants, all requested refits, endpoint selection, gate counts,
Ermatchkov verdicts, other comparisons, Wangler delta, bicarbonate/control
follow-up and endpoint identifiability remain pending. Earlier diagnostic
AARDs are not substituted for new results. Independent delivery review remains
pending. No MDEA outcome falsifies the MEA bicarbonate value.

Reproduce from this issue worktree with:

```bash
agent-heavy nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/check_merkley_saturation_fit.py
```

The check uses at most 16 worker processes, one BLAS thread per process, and
writes only inside this worktree. The manuscript and Engine source are untouched.
All new retained files are below 5 MB; no compression-registry entry is needed.
