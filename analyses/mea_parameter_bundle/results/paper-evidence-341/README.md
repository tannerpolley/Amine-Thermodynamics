# F2 paper evidence (#341)

The research notebook’s “Paper evidence on F2” section owns interpretation and displayed tables. This directory owns the numerical files; earlier studies keep their own original records.

From the issue branch at base `673bceb`, with the locked uv environment and pinned wheel available, run each action once in order:

```bash
agent-heavy env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src uv run --no-sync python -u analyses/mea_parameter_bundle/scripts/paper_evidence_341.py replay
```

Repeat that command with `evidence`, `uncertainty`, `comparison`, `weights`, `shared`, `checks`, `stability` and finally `inventory` as the action. Run each as a background shell and wait for completion. `uncertainty` reuses #307’s method; its conditional fit and inward profiles are diagnostics and do not adopt new parameters. `comparison` reuses both #339 table producers with F2 rebound as “this work”; the historical F0 rounded-AARD assertion is inapplicable, while all source-row identity and parameter-hash checks remain. Published-model calculations stay frozen. Source ranges are recorded separately from runtime calculation ranges.

The wheel is verified by its archive hash and installed module bytes. Workers derive their counts from `AGENT_HEAVY_CORES`; numerical-library threads are one. Stability reads the committed MEA registry and never discovers trials from the tree. Every new native resolved descent must be appended before accepting a later result.

The retained paper-evidence package includes the producer outputs and diagnostics. Repeated runtime caches and duplicate producer bindings are temporary; the row tables and diagnostic summaries own the calculation evidence. Presentation reads retained values and does not run the thermodynamic model. Manuscript promotion is a separate owner decision under #337; no manuscript inputs are changed.
