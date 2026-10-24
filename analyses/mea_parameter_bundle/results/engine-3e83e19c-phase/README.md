# Issue 208: numerical regeneration not started

The one-wheel reproduction question remains unanswered. This attempt stopped
before executable changes because the complete adaptation is forecast to exceed
the accepted ceiling of 160 gross added executable lines against `a7c1240`.
The measured executable change is **zero added and zero removed lines**. The
forecast is about 300 lines; the proposed ceiling is **320 lines**, subject to
owner approval. This is an estimate from the inspected responsibilities, not a
measurement of an implemented solution or proof of a minimum line count.

No Engine model was constructed, and no reference solve, phase search, split
confirmation or replay ran. There are no new pressure, phase or replay values
here. No comparison has passed or failed its reproduction limit. Historical
numerical results remain unchanged. These files must not supply #211's tables,
figures or physical claims.

## Verified inputs and source evidence

Build is the starting stage because the current issue settles the model,
calculation sequence, numerical admission checks and reproduction limits.
The complete current body of
[#208](https://github.com/tannerpolley/Amine-Thermodynamics/issues/208), its comment,
and `/tmp/issue-208-readiness.md` were read. The checked-out base is
`a7c124075df34e4d95595ef176156672b434da8d`.

[Input checks](input-checks.json) retain the issue-body identity, inspected
producer hashes, validation timing and the following independently checked
byte identities:

| Input | SHA-256 |
|---|---|
| Engine `3e83e19c` wheel | `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804` |
| Reported parameter document | `e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e` |
| Adopted comparison parameter document | `968ed8c035e23011687edfa502d31a935545abadfca87b6261a498e0b14569a4` |
| Case-7 runtime mapping | `8b15c3a862495842b31c10aa0cedc3d1217342da408b1c0d104e950b479b3d67` |
| Case-7 original parameter document | `2ea3b41485a98d2cf49add620b87bb05fc5a275cdd132c1cdbb0cfc5f07f2ca4` |
| Case-7 reaction declaration | `2058458ca473bbc7b3deef77c67a9bb5124011c0bd5d28ba3a24da5d9c0e22a4` |
| Engine `build/issue-350/seed_family.cpp` | `f7bebb0888aff98c56db093be5058ad9db8228356f1991efacab1994fd7dd33b` |

The installed Engine module and `direct_url.json` in the main checkout's
environment identify that retained wheel. The worktree has no local environment
or wheel copy; no installation or dependency change was made. Engine source
lines 53–80 and 234–244 were read only. They agree with the issue's feed,
reaction constants, temperatures, loadings, three pressure factors, cold
7398.16 Pa pressure guess, row tolerance and literal index-0 pressure.

The reference model remains distinct from both fitted records. Its original
parameter document, runtime mapping and reaction declaration remain available
under `../phase-extension-201/run-2/inputs/`; no second topology translation was
made. Their values have not been rerun on this attempt.

## Code-budget return

The following estimates cover readable adaptations and reuse existing numerical
owners; they do not allocate lines for a copied driver, new solver or test suite.
The issue remains the authoritative method. This breakdown explains the requested
ceiling change without changing any scientific requirement.

| Responsibility | Estimated gross additions | Existing code reused; missing responsibility |
|---|---:|---|
| Reference calls and grids | 75 | Reuse run-2 `reference()` and admission checks. Add explicit cold/continued predecessor selection, consumed-seed hashes, original references, anchors, grid ordering and the literal key pressure. |
| Original and extension search calls | 45 | Reuse `study.py.txt` screen/score and current extension search/confirmation. Redirect output, records, family paths and hashes; replace frozen-input copying and historical-family appending. |
| Supplement split inputs | 30 | Reuse `probes.py.txt` calculations. Bind the new comparison model and all parent/liquid/trial records, require the two specified seed identities and retain unavailable-seed outcomes. |
| Retained reductions and export | 35 | Reuse existing extension reductions and CSV writer. Add outcomes by temperature, fresh combined families and the 47-row metadata join from replay predictions. |
| Old/new comparison | 80 | Reuse #203 numerical-leaf traversal and relative-difference calculation. Add identity/duplicate checks, separate pressure/split/replay limits, exact-zero handling, absolute differences with units and successful-versus-diagnostic split treatment. |
| Execution and provenance | 35 | Reuse existing bounded calls, stage supervisor and timing. Record commands, producer/input/runtime hashes, packages, solver and final-output hashes. |
| Total forecast | 300 | Proposed ceiling 320; retain the same base and counting scope. |

Inspected alternatives do not remove the missing responsibilities:

- Run-2 `reference()` at lines 115–131 chooses the nearest successful historical
  seed from `OUT.parent/reference-pressure` and uses the rejected `Free(value)`
  amount guess. Redirecting that directory alone would change the required
  cold-predecessor sequence. The issue requires explicit new predecessors.
- `study.py.txt` lines 225–227 hardcode the old family path and hash. Screen mode
  provides the required fixed mapping for score mode, but needs fresh grid and
  output bindings. Its unrelated parameter-vector modes need not be copied.
- Current `phase_extension_201.py` lines 197–216 copy/check the historical
  reference files. Lines 237–238 append the historical original family. Its
  unchanged search, split and reduction functions remain the numerical owners;
  its `main()` cannot run unchanged. It does not emit the required outcomes file.
- `probes.py.txt` lines 12–17 bind both the historical model and old state loader.
  Its lines 31–36 choose seeds by trial order/composition distance, while this
  task requires preserving the named seed identities and detecting their loss.
- #203's `adopt.py.txt` comparison loop covers different families and includes
  specifically accepted historical split differences. Its default numerical
  gate uses `1e-10`, and its supplement override is not this issue's admission
  decision. Reuse its traversal; do not rerun its full comparison mode or reuse
  those accepted-change exemptions for #208.

The CSE Build reference requires pausing when an overrun is foreseeable,
before reaching the ceiling. No partial numerical runner was added to spend
the remaining allowance or to bypass counting through a temporary script.
No approval of a higher ceiling is claimed.

## Comparison coverage and limits

The historical original-family records were inspected directly: A6 has 12
descent states out of 73; A7 has none, with 69 liquid–vapor and four single-liquid
classifications. Each record contains 657 returned original-family trials.
The run-3 extension files retain 60 admitted states per fit, 540 returned trials,
6/6/9 pressure exclusions by temperature, 22/19/0 descending comparison-fit
trials, and 27 distinct confirmation attempts, of which 23 confirm at 17 states.
The old A6 replay has 307 predictions and 47 loaded-density observations.
These are historical counts, not new-wheel regeneration results.

| Required comparison | New evidence | Largest delta and identity |
|---|---|---|
| 24 original and 27 extension reference pressures, imposed pressures and literal key pressure | Not calculated | Unavailable |
| State/trial outcomes and extension confirmations | Not calculated | Unavailable |
| Supplement split Gibbs differences, amounts, densities and supported compositions | Not calculated | Unavailable |
| 307 replay predictions/costs, reductions and 47 density errors | Not calculated | Unavailable |

Numerical wall and CPU time are both zero because execution did not start.
No predecessor or anchor was tested; no new failure or descent was observed.
That absence supplies no evidence of stability. The intended study can provide
finite-search numerical verification only, not a global stability certificate
or physical validation. Independent delivered review returning Supported remains
outstanding.

## Notebook check and hand-back to issue 211

From `analyses/`, `nice -n 10 python3 manuscript.py validate .` returned `valid`
with exit code 0. GNU time measured 9.51 s wall, 8.32 s user and 2.56 s system
time (10.88 CPU-s). The existing notebook was not changed: Analyze has no new
method-specific numerical result for Summarize. No render or preview-service
operation was performed.

This README and `input-checks.json` are retained from the attempt;
`output-sha256.txt` records their final byte hashes (excluding its own hash).
After the budget decision and successful completion of the calculations, #211
will need these issue-specified paths relative to this directory; **none exists
yet**:

- `reference-pressure/` for the reference declaration, anchors, cold predecessors
  and 24 original plus 27 final extension reference pressures;
- `original-73/A6/` and `original-73/A7/` for fresh family evidence and mappings;
  `original-73/A6/full-replay.json`, `original-73/A6/score.json` and
  `original-73/A6/loaded-density-errors.csv` for the comparison replay;
- `extension-81/inputs/states.json`, `extension-81/states.csv`,
  `extension-81/family-points.txt`,
  `extension-81/reference-pressure/reference-pressures.csv`,
  `extension-81/phase-family.csv`, `extension-81/trials.csv`,
  `extension-81/counts-by-temperature.csv`,
  `extension-81/outcomes-by-temperature.csv` and
  `extension-81/split-confirmations.csv`, with both fits' raw point/split files;
- `A6-supplement-splits/` for fresh states 21, 63 and 70;
- `phase-family-combined.csv` for all 308 declared fit-state rows, and an old/new
  comparison table covering every displayed value.

The #207 Arcis heat source remains
`../engine-3e83e19c-refits/displays/summary.json`. This return authorizes no
manuscript input switch, refit, changed comparison endpoint or numerical retry.
