# Phase 2 Activity ePC-SAFT

This analysis owns the Phase 2 true-species activity-based ePC-SAFT workflow for MEA-CO2-H2O.

Current status: native ePC-SAFT activity-equilibrium model run succeeded with residual-gated claims. The repository has the species basis, reaction-constant basis manifest, source-value verification ledger, package dependency status, one Phase 2 parameter artifact, native solver diagnostics, equilibrium rows, pressure/speciation metrics, target-role validation, and smooth solver-success-only speciation curves. The model-run status is `model_ran_success`; validation/claim permission remains controlled by `phase2_residual_acceptance_audit.csv`.

The liquid basis contains CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-,
H3O+, and OH-; only CO2, H2O, and MEA are volatile. The fixed R1-R5 reaction
constants and their source checks live in `data/reference/MEA/manifests/`, and
the generated problem definition records the balances, activity convention,
solver route, and exact parameter artifact. This Phase 2 evaluation is not a
finalized joint-regression result.

## Commands

```bash
uv run python analyses/phase2/activity_epcsaft/scripts/generate_data.py
uv run python analyses/phase2/activity_epcsaft/scripts/render_figures.py
```

Render commands read canonical generated tables from `results/` and must not rerun solver calculations. Figure-owned source manifests live under `figures/speciation/input/`; figure output contains only plotted-data subsets, PNGs, SVGs, PDFs, and `.mpl.yaml` lineage sidecars.
