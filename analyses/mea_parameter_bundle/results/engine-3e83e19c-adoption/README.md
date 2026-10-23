# Engine 3e83e19c adoption (#203)

Engine `3e83e19c` reproduces every current-result value the manuscript reports **bitwise**
(largest relative difference 0): the reference fit's 152 predictions, both 307-row replays,
712 selected-assessment rows and 452 reductions, 2,019 model-curve values, and the
state-by-state classification of both 73-state phase families. The only changed values are
two seeded split attempts of the comparison fit (A6, `ceefc95c…`) in supplement Table S10.
The orchestrator accepted both as disclosed numerical changes
([#203 comment 6361213910](https://github.com/tannerpolley/Amine-Thermodynamics/issues/203#issuecomment-6361213910)),
and the `3e83e19c` split values are now the retained values. With that decision the step-3
check passes, and the pin moved to `3e83e19c` in commit `86f0384`.

This is numerical verification of fixed-parameter calculations. It adds no physical validation.

## Comparison results

The relative difference is δ = |new − old| / max(|old|, |new|, 10⁻³⁰⁰), with gate δ ≤ 10⁻¹⁰
(10⁻⁶ for the supplement splits). Old values are the retained Engine `8298c602` results;
the supplement splits were computed on Engine `21e761c3`. Every compared old and new value is in
[adoption-check.json](adoption-check.json); the reference-fit rows are in [comparison.json](comparison.json).

| Check (issue step 3) | Compared values | Failed | Largest δ |
|---|---:|---:|---:|
| (a) Reference fit `7b0b4bb5…b4b84308`: 47 pressures, 94 species, 8 heats, 3 heat capacities | 152 | 0 | 0 (all bitwise equal) |
| (b) Reported parameters `e234e860…`: 307-row replay predictions and costs, total cost, `score.json` statistics | 630 | 0 | 0 |
| (b) Comparison fit `ceefc95c…`: the same | 630 | 0 | 0 |
| (c) Selected assessment: 210 densities, 22 heats, 10 carbonate shares, 4 heat capacities (8 values), 462 state targets | 712 | 0 | 0 |
| (c) Selected-assessment reductions: density, heat, carbonate and state statistics (AARD, RMSE, bias, counts, costs) | 452 | 0 | 0 |
| (d) 73-state families, both fits: classification, final success and every trial's kind, start, optimizer success, evidence and resolved descent | 146 states | 0 | identical |
| (d) Supplement seeded splits at A6 states 21, 63 and 70 | 129 | 0 (28 accepted changes) | 3.9 × 10⁻¹⁰ outside the accepted attempts |
| (e) #202 model curves: every available value in the five CSV files | 2,019 | 0 | 0 |

Totals are unchanged: replay cost 148.90525398237165 (reported parameters) and
148.23773148349386 (comparison fit); phase families 0/73 failed for the reported parameters
(69 two-phase, 4 single-liquid) and 12/73 failed for the comparison fit (61 two-phase).

### Accepted split changes

The 28 changed rows belong to two attempts. `adoption-check.json` keeps their old and new
values, marks them `accepted`, and records the decision under `summary.accepted_split_changes`.

| State, start | Engine 21e761c3 (supplement) | Engine 8298c602 (previous pin) | Engine 3e83e19c (retained) |
|---|---|---|---|
| 21, uniform (`positive-neutral-base`) | failed; ΔG/RT vs original −1.5415 × 10⁻⁵; vs single liquid −15.7739494 | failed; −1.5442 × 10⁻⁵; −15.7739494 | failed; +4.76 × 10⁻⁷; −15.7739335 |
| 63, water-rich (`near-pure-2`) | failed; −1.3990 × 10⁻⁴ | failed; −4.150 × 10⁻⁵ | converged: ΔG/RT −2.1105128438, two liquids (17.777 and 68.928 mol) |

The 63 water-rich solve now reaches the same two-liquid state as the 63 uniform start (ΔG/RT
−2.110512843788456 against −2.11051284378118), so the two seeded starts agree. Its phase
labels are swapped relative to the uniform start: here `L` is the 27,919 mol/m³ liquid and
`L2` the 49,836 mol/m³ liquid. Its message records the
`amount chart physical_mol; retry after start_amount` path, consistent with the
physical-mole recovery change `221c8e94`; no single commit was isolated. The state-21 uniform
values belong to a failed solve and carry no physical meaning. The four successful splits
(21 water-rich, 63 uniform, 70 both) are bitwise equal on `8298c602` and `3e83e19c`, and within
3.9 × 10⁻¹⁰ of the `21e761c3` values. The `8298c602` column comes from the same split command
run from an extracted `d578555` tree with the main checkout's pinned environment
([A6-supplement-splits-on-8298c602](A6-supplement-splits-on-8298c602/)).

These rows are the comparison fit's split confirmations. They change no number for the
reported parameters, no classification, and no fitted or compared quantity. Table S10 is
regenerated from [A6-supplement-splits](A6-supplement-splits/) under #197.

## Engine changes between 8298c602 and 3e83e19c

The two commits are 296 commits apart. The #203 readiness review read the diffs and found no
change to the equations, species or phase supports, reaction conventions or observation
operators these MEA declarations select:

- `29fc334e` adds a reaction-activity readout (readout only).
- `d11523d7` changes the separate `IdealMoleFraction` path; MEA uses `Mixture`.
- `3ee82b92` changes the `ComponentMixing` permittivity branch; the reported parameters declare
  `solvent-density-temperature` and the frozen case-7 reference declares `solvent-only`.

Numerical-method changes, disclosed under the issue's stop rule:

- `05d0ffae`: stability-polish step limit of ln 101, the Engine #811 fix.
- `b2c7367b`: association Newton damping.
- `221c8e94`: physical-mole recovery.
- `e15e2f06` / `76a5fbc9`: energy-action caching and its invalidation.
- `12f200ef`: refuses a phase-amount `Free(value)` guess that the old interface ignored.

## Code and record changes

- **Pin** (`86f0384`): `ENGINE_WHEEL_SHA256` and `ENGINE_COMMIT` in `scripts/shared_evaluation.py`
  (two lines), the relative wheel path and hash in `pyproject.toml` and `uv.lock`, and
  `working_engine_wheel_sha256` in `analysis.yaml`.
- **Interface adaptation, `scripts/phase_extension_201.py`** (`123a9ae`): the #201 reference-pressure
  generator set `problem.phases[0].amount = Free(<seeded amount>)`, which `12f200ef` refuses. On
  `8298c602` that guess was ignored. Run 3 does not regenerate reference pressures: it copies
  run 2's states, family points and reference evidence and checks their hashes. The generator was
  therefore removed rather than rewritten; its run-2 form is retained as
  `../phase-extension-201/run-2/phase_extension_201.py.txt`. Classifier, trials, chains and
  stage ceilings are unchanged.
- **No other adaptation was needed.** Every step-3 producer ran unchanged on this wheel.
- **Not changed:** `../phase-extension-201/diagnosis/probes.py` (lines 83 and 159) also passes
  phase-amount guesses; it is a retained run-2 diagnosis record on `8298c602` and is not rerun.
  `analyses/mdea_kuranov_refit` (#126) declares its own `8298c602` wheel in `score.py` and refuses
  any other wheel; re-pinning belongs to #126.

## Retained with original Engine provenance, not recomputed

- The conditional standard errors and correlations of both fits: local fit diagnostics of the
  original fits.
- The historical predecessor records (earlier records, fits and adoptions in this analysis).

## Method

[adopt.py.txt](adopt.py.txt) runs each retained producer with only its output path redirected
(and, for the reference fit, its input document): the `8298c602` adoption `evaluate.py.txt`,
`amendment-7/fixed-study/study.py.txt` (`screen`, `score`), `amendment-6/selected-checks/phase-diagnosis/probes.py.txt`
(`split 21 63 70`), `amendment-7/selected-assessment/assess.py.txt` and `reduce.py.txt`, and
`model_curves.main`. Its `compare` mode reads the retained files only. After the acceptance it
was rerun with the two accepted attempts marked; no producer was rerun.
The reference-fit document was recovered from commit `eb0d1d6` into
[inputs/reference-fit-parameters.json](inputs/reference-fit-parameters.json) and its SHA-256 checked.
Three assessment inputs (`observation-groups.json`, `state-inputs.json`, `density-inputs.json`) were
byte-identical to the retained amendment-7 files and were removed; model-curve worker caches were removed.

## Wheel and installation

- Built from the ignored clone `upstream/ePC-SAFT` after syncing `main` to `origin/main` and checking
  out `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, with `tools/build-engine.sh --wheel` and
  `EPCSAFT_BUILD_JOBS=8` (17 GB free of 31 GB). There is no release asset for this commit.
- Relative path:
  `build/engine-wheels/main-3e83e19ccc771b51d8ebc038931ab25192f4c5b5/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl`,
  with its `.sha256` file beside it.
- SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`
  (`sha256sum --check --strict` passes); linear solver MA57; numpy 2.4.4, scipy 1.17.1.
- `uv lock` changed only the `epcsaft` source and hash; `uv sync --frozen` exits 0 and
  `shared_evaluation.verify_wheel()` passes.

Fresh checkout: build the wheel from that commit into that directory as above, then `uv sync --frozen`.

## Checks

[checks.json](checks.json) records every command and exit.

- Pytest on the new pin: **95 passed, 4 failed** (15.0 s). The four failures
  (`test_campaign_routing.py` two, `test_shared_evaluation.py` two) fail with identical messages on
  Engine `8298c602` at base `d578555`, so this adoption did not cause them.
- Compute for step 3: 15 calls, 238 wall-s and 632 CPU-s at niceness 10, one numerical-library
  thread per process and process pools sized at one worker per available gigabyte. The largest
  resident memory was 112,468 KiB for one process.
- Change accounting for the whole issue against base `d578555`: **154 gross added executable lines**
  of the approved 160. They are `adopt.py.txt` 129, `scripts/phase_extension_201.py` 23 (71 removed)
  and `scripts/shared_evaluation.py` 2. The run-3 files `phase_extension_201.py.txt` and
  `final_evidence.py.txt` are byte copies of the committed producers and add no code. No test was added.
