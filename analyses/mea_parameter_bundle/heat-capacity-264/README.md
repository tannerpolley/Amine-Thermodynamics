# MEA heat-capacity evidence for issue 264

The [bundle notebook](../notebook.qmd#broader-mea-heat-capacity-comparison) interprets the retained measurements, decomposition and bounded refits. The canonical design is [issue 264, design comment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/264#issuecomment-6699109299), amended by [the design amendment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/264#issuecomment-6699223997) and independently reviewed Ready. These probes do not adopt parameters.

`sources.csv` preserves the measured values, source locators, composition basis, uncertainty interpretation and pressure assumption. `source-provenance.json` identifies the live Zotero PDFs and their hashes. `qualification.json` checks all 307 original observations with their original water record; subsequent calculations use the corrected water record from issue 260. Every numerical JSON carries the probe wheel SHA-256. `decomposition.json` and the probe decomposition files use kJ/(kg loaded solution K), except the explicitly labeled finite-difference checks in J/(mol phase K).

`probe-*-fit.json` retains native optimization, failure and covariance evidence; `probe-*-parameters.json` retains each unadopted endpoint; `probe-*-replay.json` records independent prediction replays, group costs and deterioration checks. The original 307-row objective has no integral-heat rows: the 22 retained integral heats are additional comparison controls, excluded from the probe objective. `*-stability.json` retains all 60 state/trial searches. Dense descent, gas descent and unresolved searches have distinct meanings. Hilliard pressure is unreported; 101325 Pa is the calculation convention, including for the gas-descent interpretation.

Run from this worktree with the merged e6dae5c7 Engine wheel installed only in its environment (SHA-256 `83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6`):

```bash
agent-heavy env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python analyses/mea_parameter_bundle/heat-capacity-264/calculate.py qualify
agent-heavy env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python analyses/mea_parameter_bundle/heat-capacity-264/calculate.py baseline
agent-heavy env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python analyses/mea_parameter_bundle/heat-capacity-264/calculate.py stability
agent-heavy env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python analyses/mea_parameter_bundle/heat-capacity-264/calculate.py A
agent-heavy env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python analyses/mea_parameter_bundle/heat-capacity-264/calculate.py B
.venv/bin/python analyses/mea_parameter_bundle/heat-capacity-264/present.py
```

`A-replay` and `B-replay` explicitly rebuild assessment, decomposition and phase evidence from the corresponding retained fit and parameter files, without refitting. They were added after a NumPy Boolean serialization error interrupted A's assessment; its converged native fit was preserved. The source-to-problem mapping uses shallow copies because native reaction-law objects cannot be pickled by Python's deep-copy routine. Neither correction changes the thermodynamic model or the optimizer.

`present.py` reads retained results only. Its figure uses discrete model points at measurement coordinates; it does not imply a continuous curve or create additional observations. Hilliard error bars show the stated ±2% accuracy, not a confidence interval. `cp-by-temperature-loading-source.csv` reports heat-capacity AARD and mass-specific RMSE by the requested groupings; `group-costs.csv` preserves every group's cost share and separates the fit objective from comparison controls. Mixed-quantity groups have quantity-specific RMSE in the native replay records, rather than combining kelvin with mole fractions.
