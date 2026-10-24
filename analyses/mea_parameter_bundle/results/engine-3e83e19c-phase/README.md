# Phase-study regeneration on Engine 3e83e19c (#208)

**Changed, returned to the owner before #211 use.** All requested numerical stages have retained results. The phase-search counts, classifications, exclusions and confirmed/unconfirmed outcomes reproduce, and the reported record has no resolved descent at any of its 133 admitted states. The comparison replay has residual/cost/error changes above its reproduction limit, and the extension's most-negative-first reduction changes representative assignments at four states. Independent delivered review and the owner's disposition remain open. These results have not been promoted for manuscript use.

## Outcome and comparison

The reported parameter document is `e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e`. The adopted comparison document is `968ed8c035e23011687edfa502d31a935545abadfca87b6261a498e0b14569a4`. Both are bound explicitly, with separate runtime-mapping hashes, in each fresh family and its split-parent records. The adopted comparison endpoint was not changed or fitted again.

| Quantity or outcome | Old → new | Comparison disposition |
|---|---|---|
| Original descent states, comparison / reported | 12/73 → 12/73; 0/73 → 0/73 | Every state/trial classification agrees; 657 returned trials per fit |
| Original reported classifications | 69 liquid–vapor + four single-liquid → same | No unresolved state |
| Extension admitted / excluded, each fit | 60/81 + 21/81 → same | Excluded states: 6/6/9 by temperature; 189 unavailable trial slots per fit |
| Extension returned trials, each fit | 189/189/162 → same | 540 total, all completed; no numerical-unavailable or unresolved state |
| Extension comparison descending trials | 22/19/0 → same | 21 descent states; reported record has none |
| Combined descent states, comparison / reported | 33/133 → 33/133; 0/133 → 0/133 | Finite-search result only |
| Extension distinct confirmations | 27 attempts, 23 confirmed at 17 states → same | Twelve trial-to-representative links change at indices 49, 56, 57 and 58 |
| Supplement required seeds | Six resolved-descent seeds → same | Five successful splits; state 21 `positive-neutral-base` remains unsuccessful |
| Comparison replay | 307 available predictions → same | All predictions within `1e-10`; some residuals/costs/errors exceed that limit |

[old-new-comparison.csv](old-new-comparison.csv) retains matched identities, old/new values, absolute differences, units, relative differences, numerical reproduction limits and the separation of unsuccessful-solve diagnostics. [comparison-summary.json](comparison-summary.json) reduces its groups. Missing or duplicate identities are rejected; parameter-document changes are recorded separately from scientific identities.

The pressure limit is `1e-8`, the successful-split limit is `1e-6`, and the replay limit is `1e-10`, using `abs(new-old)/max(abs(old),abs(new),1e-300)` and #208's exact-zero rule. These are numerical reproduction labels; they are not physical uncertainty bounds.

| Successful quantity | Largest relative difference and identity | Old → new; absolute difference |
|---|---|---|
| All 51 P* values | `6.787717402727284e-14`; original reference, 313.15 K, loading 0.25557798094241313 | 5212.2594091423425 → 5212.259409142696 Pa; `3.537934389896691e-10` Pa |
| All imposed pressures, including the key state | `6.805166547721441e-14`; original index 38, fraction 0.80 of that reference | 4169.807527313874 → 4169.807527314158 Pa; `2.837623469531536e-10` Pa |
| Extension confirmed split Gibbs difference | `2.592671141527928e-7`; index 41, 373.15 K, `positive-neutral-base` | −0.10883542018369406 → −0.10883544840114669 J; `2.821745262449049e-8` J |
| Extension split amount | `5.822865431920618e-8`; same state, additional liquid | 0.2056506850503224 → 0.20565069702508576 mol; `1.1974763347577522e-8` mol |
| Supplement Gibbs difference against parent | `1.4307055360271402e-10`; state 63, `near-pure-2` | −2.11051284378118 → −2.1105128440831322 in G/(RT) on the feed basis; `3.019522409886122e-10` |
| Supplement supported composition | `8.110772449383072e-9`; state 21, `near-pure-2`, additional-liquid carbonate | `2.0185376045335374e-6` → `2.0185375881616382e-6` mol/mol; `1.637189919089432e-14` mol/mol |
| Replay prediction | `4.750890942682765e-11`; `Jakobsen2005_state_011::HCO3- + CO3^2-` | 0.008313864966748104 → 0.008313864966353121 mol/mol; `3.9498265769211116e-13` mol/mol |

All 27 extension P* values are bitwise equal to run 2. The original 24 historical P* values are recovered from the retained 0.50-pressure rows using their declared factor. Index 0 remains the literal 5918.5286 Pa; it is `8.13574115454685e-6` Pa below the recomputed corresponding 0.80-pressure state. No rounding rule replaces that literal.

## Owner-return reasons

1. Twelve descending-trial links change their representative assignment at extension indices 49, 56, 57 and 58. Most-negative-first selection uses the fresh trials; it was not forced to preserve an old seed. There are still 27 distinct attempts, 23 confirmations and 17 confirmed states, with no confirmed/unconfirmed link changing.
2. Of 3,070 compared replay fields (ten per target), 170 residual, weighted-residual or cost values exceed `1e-10`. All observed values, scales, weights, forms, availability and tolerance outcomes agree. All 307 predictions are within the limit. The largest relative cost change is `5.678966273406134e-9` for `Hartono2014_density_80C_alpha0.19`: `7.690633216480888e-6` → `7.690633172806042e-6`, absolute `4.36748466575319e-14` (dimensionless).
3. Two score fields exceed the replay limit: CO₂-free density errors `AMU-DENS-009` (`1.321703471847886e-10` relative) and `AMU-DENS-016` (`3.0225071657898196e-10`). The latter changes from −0.02595326122491315 to −0.025953261217068757 kg/m³, absolute `7.844391802791506e-12` kg/m³.
4. Thirteen of the 47 loaded-density errors exceed the replay limit. The largest is the Hartono row above: 0.05785471105468787 → 0.05785471089041039 kg/m³, relative `2.8394832073821936e-9`, absolute `1.6427748050773516e-10` kg/m³. `error_over_s` is the unweighted replay residual.

Total replay cost changes from 148.23773148349386 to 148.23773148351188. New C149 is 24.923085270733207; Cai cost 91.8114657754144; pressure AARD 12.47366935635063%; species AARD 7.145138025313051%; Vinjarapu RMSE 1.821530054692655 kJ/mol CO₂. All 47 loaded densities remain within two declared scales; the largest absolute error/scale is 1.9764146339510436. The largest CO₂-free density absolute error is 0.5709262280848861 kg/m³. [score.json](original-73/A6/score.json) retains these and every component error. Arcis heats remain supplied by #207's [displays/summary.json](../engine-3e83e19c-refits/displays/summary.json).

Unsuccessful-solve Gibbs values are retained as diagnostics, including state 21's `positive-neutral-base` result, whose new parent-relative G/(RT) is `4.764478944707662e-7`. Its apparent sign or magnitude is not split evidence. No numerical retry, new solver, changed trial design, changed admission, parameter substitution or refit followed the reproduction differences.

## Reference declaration and execution

The case-7 pressure model is distinct from both fitted records. Its original parameter document, complete runtime mapping and reaction declaration are under [reference-pressure/inputs](reference-pressure/inputs/reference-runtime.json), with original byte hashes in [input-checks.json](input-checks.json). [declaration.json](reference-pressure/declaration.json) binds the construction to Engine `build/issue-350/seed_family.cpp`, SHA-256 `f7bebb0888aff98c56db093be5058ad9db8228356f1991efacab1994fd7dd33b`. Engine source was read only; it was not compiled or imported.

All three anchors qualify at `1e-8`. There are 24 cold original references, 17 cold extension predecessors, and 27 final extension references. The cold 353.15 K files also supply that temperature's final references; the continued references consume only the exact cold predecessors required in #208, with each seed's byte hash retained. `Free()` replaces the ignored historical phase-amount guess. Numerical admission is retained separately from the 1–10,000,000 Pa search interval. Every reference/predecessor is numerically admitted; seven final extension pressures exceed 10 MPa and exclude every dependent state. No old-Engine seed was consumed and no second association translation was applied.

The numerical owner remains `final_evidence.py` (including its corrected vapor-support projection), the retained run-2 `reference()`, `study.py.txt` screen/score, current extension reduction/confirmation, and the supplement's `probes.py.txt` split calculation. [phase_regeneration_208.py](../../scripts/phase_regeneration_208.py) supplies explicit input/output bindings and the missing reductions/comparisons. It does not copy whole numerical drivers. Historical result directories are unchanged.

The original-screen supervisor encountered `ProcessLookupError` while reading a just-exited child in `/proc`. Both independent screens finished all 73 points and 657 trials per fit. Their logs and GNU child timings are retained. The current extension supervisor now treats that vanished process like `FileNotFoundError`; numerical routines and budgets are unchanged. The `original-retained` command performs only reduction and the required fresh confirmations, without repeating a screen. No solve was killed and no state or extension-stage ceiling was reached.

All numerical calls used the main checkout's verified interpreter:

```text
/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I
```

The installed wheel is Engine `3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`. No local worktree environment was installed. MA57 is the loaded linear solver; epcsaft 0.2.0.dev0, numpy 2.4.4 and scipy 1.17.1 are installed. Numerical libraries use one thread per process. The cold-reference pool is sized as `min(os.cpu_count(), MemAvailable_kib//1000000)`; search and confirmation concurrency preserves the ordered chains.

From the task worktree root, each numerical command was launched with `/usr/bin/time`, `nice -n 10`, the interpreter above and `analyses/mea_parameter_bundle/scripts/phase_regeneration_208.py`, with mode `references` (the default), `original-73`, `extension-81`, `original-retained`, `score` or `supplement`. The commands themselves remained the background shells with `tee`; their `*-command.log`, per-child command logs and `calls.json` are retained. `provenance` and `compare` only bind/read retained results and construct comparisons; they do not solve or replay again.

| Command | Measured wall / s | Measured CPU / s |
|---|---:|---:|
| References and grids | 4.68 | 8.94 |
| Original supervisor, exited with process-read error | 17.74 | 3.89, excluding still-running screens |
| Original comparison screen | 38.15 | 38.03 |
| Original reported screen | 36.60 | 36.48 |
| Original retained reduction and new confirmations | 11.73 | 20.96 |
| Extension screen, reductions and confirmations | 45.76 | 213.69 |
| 307-row replay and 47-row export | 13.23 | 13.17 |
| Supplement splits | 5.98 | 5.96 |

These command wall times overlap and are not summed into a fictitious serial wall time. The charged numerical CPU total is 341.12 s from the rounded GNU measurements, without double-counting the original screens. Extension screen and confirmation supervisor measurements are 33.6523/194.2878 and 8.0822/15.3926 wall/CPU seconds, respectively, against 600/1800 per stage. The original confirmations use 18 distinct attempts, 15 confirmed; the extension uses 27, 23 confirmed. The independent design review's wall estimate was not a measured end-to-end command.

[provenance.json](provenance.json) and each fit's provenance retain the interpreter, packages, wheel, parameter-byte and runtime-mapping hashes, grid/state hashes and producer hashes. The reference records retain consumed seed hashes and the effective reference-function hash. The retained adapter specifies the exact source transformations for screen, score and supplement. Final file hashes are in [output-sha256.txt](output-sha256.txt).

## Notebook, changed surface and hand-back

The phase-extension discussion in [joint-recalibration/index.qmd](../../joint-recalibration/index.qmd#phase-extension-201) now describes the fresh states, outputs, limits and owner-return reasons. Validation and the HTML render are recorded in `notebook-validation.json`; all rendered output is under `/tmp`, with `--no-execute`. The Quarto preview service and port 8770 were not accessed. No browser or subagent was used.

The accepted base is `a7c1240`; the approved ceiling is 320 gross added executable lines, [owner amendment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/208#issuecomment-6378132112). The final implementation has 315 lines in `phase_regeneration_208.py` plus two changed executable lines in `phase_extension_201.py`: **317 gross additions, two removals**. No tests or new dependencies were added. The numerical checks are the anchors, required predecessor/admission checks and the complete retained old/new comparisons. The [change-accounting report](change-accounting.json) records the final source surface; its own JSON and the final hash inventory are reporting outputs.

After the owner-return disposition and independent Supported review, #211 will consume these exact paths relative to this directory:

- `reference-pressure/inputs/{engine-case7-parameters.json,reference-runtime.json,engine-case7-reactions.json}` and `reference-pressure/declaration.json` for S8's separate reference model and parameter values; `reference-pressure/{anchor-*,cold-*,original-*,extension-*}.json` for admission and consumed seeds;
- `original-73/{A6,A7}/point-*.json`, `fixed-parameters.json`, `provenance.json`, `reduction.json` and the original family's `states.csv`, `family-points.txt`, `reference-pressure/reference-pressures.csv`, `phase-family.csv`, `trials.csv`, `split-confirmations.csv` and raw split files;
- `original-73/A6/full-replay.json`, `original-73/A6/score.json`, `original-73/A6/loaded-density-errors.csv` and `original-73/A6/loaded-density-provenance.json`;
- `extension-81/inputs/states.json`, `extension-81/states.csv`, `extension-81/family-points.txt`, `extension-81/reference-pressure/reference-pressures.csv`, `extension-81/phase-family.csv`, `extension-81/trials.csv`, `extension-81/counts-by-temperature.csv`, `extension-81/outcomes-by-temperature.csv`, `extension-81/split-confirmations.csv`, `extension-81/{A6,A7}/point-*.json` and raw `split-seeded-*.json` records;
- `A6-supplement-splits/split-seeded-{21,63,70}.json`, with fresh parent bindings, phase amounts/densities/supported compositions, both Gibbs differences and complete unsuccessful-attempt diagnostics;
- `phase-family-combined.csv` (308 fresh rows), `old-new-comparison.csv`, `comparison-summary.json` and this disposition.

#211 owns manuscript generator switches, captions, tables, figures and prose. No manuscript files were edited. This result supports numerical reproduction and the stated finite-search outcomes only; excluded and unresolved work cannot be called no descent, parameter/measurement/model uncertainty is not propagated, and confirmed model splits do not establish physical liquid separation or process performance.
