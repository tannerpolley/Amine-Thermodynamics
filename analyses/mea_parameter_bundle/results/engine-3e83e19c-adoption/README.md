# Engine 3e83e19c adoption check (#203 step 3): stopped at the supplement split comparison

**Outcome: adoption failed under the issue's stop rule.** Engine `3e83e19c` reproduces every
fixed-state prediction, replay, assessment reduction, model-curve value and phase classification
**bitwise** (largest relative difference 0). The one failure is in the seeded split solves reported
in supplement Table S10 (`tab:supplement-split-states`): the water-rich (`near-pure-2`) start at
A6 state 63 failed on the earlier Engines and now converges. Its reported Gibbs change moves from
−1.399 × 10⁻⁴ to −2.1105, and the table row would change from "no / failed split" to "yes".
The issue requires a stop and report when a supplement split quantity changes by more than 10⁻⁶.
The pin stays at Engine `8298c602`; the 353–393 K extension (step 5) was not run.

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
| (d) Supplement seeded splits at A6 states 21, 63 and 70 | 129 | **28** | ∞ |
| (e) #202 model curves: every available value in the five CSV files | 2,019 | 0 | 0 |

Totals are unchanged: replay cost 148.90525398237165 (reported parameters) and
148.23773148349386 (comparison fit); phase families 0/73 failed for the reported parameters
(69 two-phase, 4 single-liquid) and 12/73 failed for the comparison fit (61 two-phase).

### Failing rows: supplement seeded splits

| State, start | Engine 21e761c3 (supplement) | Engine 8298c602 (current pin) | Engine 3e83e19c |
|---|---|---|---|
| 21, uniform (`positive-neutral-base`) | failed; ΔG/RT vs original −1.5415 × 10⁻⁵; vs single liquid −15.7739494 | failed; −1.5442 × 10⁻⁵; −15.7739494 | failed; **+4.76 × 10⁻⁷**; **−15.7739335** (δ 1.007 × 10⁻⁶) |
| 63, water-rich (`near-pure-2`) | failed; −1.3990 × 10⁻⁴ | failed; −4.150 × 10⁻⁵ | **converged**: ΔG/RT −2.1105128438, two liquids (17.777 and 68.928 mol) |

The 63 water-rich solve now reaches the same two-liquid state as the 63 uniform start (ΔG/RT
−2.110512843788456 against −2.11051284378118). Its message records the new
`amount chart physical_mol; retry after start_amount` path, consistent with the disclosed
physical-mole recovery change `221c8e94`; no single commit was isolated. The four successful
supplement splits (21 water-rich, 63 uniform, 70 both) are bitwise equal on `8298c602` and
`3e83e19c`, and within 3.9 × 10⁻¹⁰ of the `21e761c3` values.

The `8298c602` column comes from the same split command run from an extracted `d578555` tree
with the main checkout's pinned environment ([A6-supplement-splits-on-8298c602](A6-supplement-splits-on-8298c602/)).
It shows that the 63 water-rich failure was already numerically different on the current pin
(−4.150 × 10⁻⁵ against the printed −1.399 × 10⁻⁴), while it still failed, as in the supplement.
Only `3e83e19c` turns a reported failed split into a converged one.

## What the owner must decide

The change is numerical: an unsuccessful seeded split attempt now succeeds and agrees with the
existing successful split at the same state. No equation, support, reaction or observation
operator changed. Two paths follow from the issue's rules:

1. Accept this numerical change as disclosed and authorize an update of Table S10's state-63
   water-rich row (and the state-21 uniform failed-split values) with the `3e83e19c` results;
   then rerun step 3 with that row's new values as the reference and continue to steps 4–6.
2. Keep the pin at `8298c602` and state the 353–393 K gap as a limitation.

## Method

[adopt.py.txt](adopt.py.txt) runs each retained producer with only its output path redirected
(and, for the reference fit, its input document): the `8298c602` adoption `evaluate.py.txt`,
`amendment-7/fixed-study/study.py.txt` (`screen`, `score`), `amendment-6/selected-checks/phase-diagnosis/probes.py.txt`
(`split 21 63 70`), `amendment-7/selected-assessment/assess.py.txt` and `reduce.py.txt`, and
`model_curves.main`. The reference-fit document was recovered from commit `eb0d1d6` into
[inputs/reference-fit-parameters.json](inputs/reference-fit-parameters.json) and its SHA-256 checked.
Three assessment inputs (`observation-groups.json`, `state-inputs.json`, `density-inputs.json`) were
byte-identical to the retained amendment-7 files and were removed; model-curve worker caches were removed.

Retained with original Engine provenance and not recomputed: the conditional standard errors and
correlations (local fit diagnostics of the original fits) and the historical predecessor records.

## Candidate wheel and environment

- Built from the ignored clone `upstream/ePC-SAFT` after syncing `main` to `origin/main` and checking
  out `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, with `tools/build-engine.sh --wheel` and
  `EPCSAFT_BUILD_JOBS=8` (17 GB free of 31 GB).
- `build/engine-wheels/main-3e83e19ccc771b51d8ebc038931ab25192f4c5b5/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl`,
  SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`; linear solver MA57;
  numpy 2.4.4, scipy 1.17.1.
- Qualified through uncommitted edits to `shared_evaluation.py`, `pyproject.toml` and `uv.lock`
  (`uv lock` changed only the `epcsaft` source and hash; `uv sync --frozen`). After the failure the
  edits were discarded and the environment returned to the `8298c602` wheel.

## Compute

[checks.json](checks.json) records every command, exit and GNU-time record: 15 calls, 238 wall-s
and 632 CPU-s in total, at niceness 10, one numerical-library thread per process and process pools
sized at one worker per available gigabyte. The largest resident memory was 112,468 KiB for one process.
