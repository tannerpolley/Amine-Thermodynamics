# Historical Fixed-Parameter ePC-SAFT Evaluation

This analysis owns the historical true-species activity-based ePC-SAFT evidence for MEA-CO2-H2O.

Retained historical status: native ePC-SAFT activity-equilibrium model run succeeded with residual-gated claims. The repository has the species basis, reaction-constant basis manifest, source-value verification ledger, package dependency status, one historical fixed-parameter ePC-SAFT evaluation parameter artifact, native solver diagnostics, equilibrium rows, pressure/speciation metrics, target-role validation, and smooth solver-success-only speciation curves. The model-run status is `model_ran_success`; validation/claim permission remains controlled by `historical_activity_evaluation_residual_acceptance_audit.csv`.

The liquid basis contains CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-,
H3O+, and OH-; only CO2, H2O, and MEA are volatile. The fixed R1-R5 reaction
constants and their source checks live in `data/reference/MEA/manifests/`, and
the generated problem definition records the balances, activity convention,
solver route, and exact parameter artifact. This historical evaluation is not a
finalized joint-regression result.

## Render retained results

```bash
uv run python analyses/historical_fixed_parameter_epcsaft_evaluation/scripts/render_figures.py
```

Render commands read canonical generated tables from `results/` and must not rerun solver calculations. Figure-owned source manifests live under `figures/speciation/input/`; figure output contains only plotted-data subsets, PNGs, SVGs, PDFs, and `.mpl.yaml` lineage sidecars.

The historical numerical generator was retired. These commands render retained
tables only; they do not regenerate or adopt an ePC-SAFT parameter set. If a
required table is missing, recover its exact retained version rather than
following a renderer hint to the deleted generator.
