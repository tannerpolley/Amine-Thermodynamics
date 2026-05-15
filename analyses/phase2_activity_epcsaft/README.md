# Phase 2 Activity ePC-SAFT

This analysis owns the Phase 2 true-species activity-based ePC-SAFT workflow for MEA-CO2-H2O.

Current status: problem-definition, convention-audit, promoted activity-constant fixed inputs, and required-output status scaffold. The repository now has the species basis, reaction-constant basis manifest, R1-R5 Austgen Table V unsymmetric mole-fraction activity rows, package dependency status, one Phase 2 parameter artifact, and a generated table stating which issue #5 outputs are ready versus blocked. Activity-based speciation and VLE outputs remain blocked on upstream ePC-SAFT issue #115.

## Commands

```powershell
uv run python analyses\phase2_activity_epcsaft\scripts\generate_data.py
```

Future render commands should read generated CSV tables from `data/processed/` and must not rerun solver calculations.
