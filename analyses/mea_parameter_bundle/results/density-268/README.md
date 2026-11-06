# Higher-temperature MEA density comparison

Issue [268](https://tnnrpolley21-ms-7c95.taila72856.ts.net:3000/tannerpolley/Amine-Thermodynamics/issues/268).
The [research notebook](../../notebook.qmd#higher-temperature-density-probes-issue-268)
owns interpretation, data roles, uncertainty and the recommendation for #255
stage 2. `summary.json` and `density-summary.json` retain the reduced numbers;
all JSON results identify the executing wheel. No parameter set is adopted.
Independent readiness returned Ready. Delivered review is pending.

The two local fits converge and have no detected descent or incomplete state
on the retained 162-state search, but preserve only 17/47 and 34/47 fitted
loaded-density checks. They meet 13/20 and 10/20 higher-temperature Han loaded
expanded-uncertainty comparisons, respectively. This is a tested density
tradeoff, not a proof that no feasible parameter set exists.

## Reproduction

The repository lock still identifies the original immutable wheel. With that
wheel available at its locked path, `uv sync --frozen` prepares the environment.
The following first command reproduces the original mixed-domain R5 refusal;
the original successful baseline and refusal are retained in
`original-wheel-final/`. Never overwrite that retained evidence.

```bash
agent-heavy uv run --no-sync python analyses/mea_parameter_bundle/scripts/density_268.py baseline final
```

The owner then authorized the merged e6dae5c7 wheel only for this worktree.
Install the exact wheel identified in `density_268.py:WHEELS` with `uv pip
install --python .venv/bin/python --no-deps <wheel>`. Its SHA-256 must equal
`83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6`.
Keep `--no-sync`: an implicit synchronization reinstalls the old locked wheel.
`verify()` checks the wheel and every installed Engine file before execution.
The script sets the diagnostic module's wheel identity in that process only;
it changes no repository-wide pin or other process.

For each `final` and `wide` start, run `baseline`, `compare`, `sensitivity`,
`fit`, then `phase` with the same command prefix above. The new-wheel full
307-row baseline and native chart checks are mandatory before fitting. A
retained `fit.json` is consumed without repeating optimization, so interrupted
endpoint export/replay can resume. The native controls and original declarations
remain in the fit input and report; the time limit is the retained 600 s per fit.
Then run `extend-255` without a start argument. That command reads five retained
#255 mappings and scores only the 25 new higher-temperature Han cells; it does
not repeat any original 307-row replay or stability search.

```bash
uv run --no-sync python analyses/mea_parameter_bundle/scripts/density_268.py present
```

`present` reads retained values only. It writes the comparison figure, source
and sensitivity reductions, qualification checks and input hashes. The Quarto
notebook also reads retained values; it runs no model. The bundle's Snakemake
workflow remains held under #133. Raw phase evidence is compressed by state;
its summary distinguishes detected descent from incomplete searches. Uncertainty
scales, coordinate units and source locators remain attached to every row.
The old #255 evidence retains its original wheel identity in `reused-255/`.

The converged native fits are retained rather than repeated when endpoint
export/replay resumes. Both endpoint replays agree with the native predictions.

The approved code ceiling is 450 gross executable additions against `30db72a`,
zero separate tests. `change-accounting.json` records 374 executable additions;
assertions in the study command protect the 307-row qualification, chart/start
identity, native-fit initial cost, endpoint replay and retained row counts.

## Retained 255 vectors

The additional higher-temperature density values and original fixed-vector
summaries are retained together for
[final size at the wider-bound value](reused-255/final-size-wide.json),
[wider-bound size at 5.35 Å](reused-255/wide-size-5.35.json),
[wider-bound water interaction −0.175](reused-255/wide-water--0.175.json),
[wider-bound Born diameter 4.5 Å](reused-255/wide-born-4.5.json), and
[wider-bound ion-pair interaction −0.5](reused-255/wide-pair--0.5.json).
