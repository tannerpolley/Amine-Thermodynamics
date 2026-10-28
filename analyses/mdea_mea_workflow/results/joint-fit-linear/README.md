# Linear MDEA–water joint fit

A1 converged at cost 400.448016085 with four arbitrary bounds active. Stage 2 returns to Design before outside-fit evaluation. The [notebook](../../notebook.qmd) owns interpretation and limits; [summary.json](summary.json) and [endpoints.csv](endpoints.csv) retain the current disposition. Earlier reciprocal-law results remain historical.

Reproduction uses the isolated main-venv interpreter with `nice -n 10` and one BLAS thread per process:

```python
import runpy
runpy.run_path('analyses/mdea_mea_workflow/scripts/fit_mdea.py', run_name='__main__')
runpy.run_path('analyses/mdea_mea_workflow/scripts/check_mdea_endpoint.py', run_name='__main__')
```

The fit owner now reads item-(l) starts and calorics, uses the two retained `temperature_law_coefficient` coordinates, and writes this directory. The endpoint-check owner maps those coefficients into the retained document and stores explicit numerical prediction fields. No equations or objective rows changed. The former reciprocal-coordinate declarations in those two current execution owners were replaced; historical result files were preserved. Callers are the two commands above; historical diagnosis commands are not authorized reproduction of the current linear-law study.

The A4 larger-budget retry was not executed: the pinned Engine fixes the relevant limits. The owner selected exclusion without retry while away. See [capability evidence](../item-l/A4-retry-capability.json), [qualified-start gate](../item-l/gate-status.json), [runtime](runtime.json), and [frozen inputs](frozen-inputs.json). No shared parameter was released.

The initial derivative-check command requested a nonexistent residual field and stopped before producing a check. The corrected command compares native physical predictions with native optimizer-gradient columns. All four comparisons pass; [linear-derivatives.json](linear-derivatives.json) retains step sizes, quantities and errors. Replay was repeated once to replace the former string representation of Prediction objects with explicit numeric fields; the maximum error is unchanged. This repetition did not refit or repeat the A4 trial.

Weak-direction profiles, remaining starts, complete phase/balance checks, outside-fit comparisons, Wangler sensitivity and follow-up refits were not run after the mandatory bound stop. No MDEA outcome falsifies the MEA bicarbonate value. Independent delivered review remains open; no manuscript promotion occurred.

Presentation-only refresh failed because `snakemake` is absent from PATH; [notebook-refresh.txt](notebook-refresh.txt) retains the error. Notebook source and section index are current; HTML remains stale.

The change-accounting report measures 33 executable lines added and 19 removed in the two existing execution owners relative to `2b6cd44`; no new executable file was added. No issue-specific code ceiling was supplied, so this handoff does not claim budget approval.
