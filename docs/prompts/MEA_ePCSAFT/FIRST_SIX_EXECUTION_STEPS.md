# Prompt: First Six MEA-Thermodynamics Execution Steps

Execute these tasks in order. Keep the work PR-ready and bounded.

## Step 1 — Fix reproducibility and dependency hygiene

Inspect:

- `pyproject.toml`
- `uv.lock`
- `README.md`
- `HANDOFF.md`
- `docs/latex`
- current ePC-SAFT import path logic.

Tasks:

- Identify local absolute Windows paths used in publication-facing files.
- Do not break the user’s local development setup.
- Move local overrides into development-only notes if needed.
- Add a roadmap note for portable dependency resolution.

Acceptance:

- A clean-checkout dependency strategy is documented.
- Manuscript-facing documents do not depend on `C:\Users\...`.

## Step 2 — Inventory and extract high-priority data

Inspect:

- `docs/papers/md`
- `data/reference/MEA`
- `data/reference/MEA/ChEq`
- `data/reference/MEA/VLE`
- manifest templates under `data/reference/MEA/manifests`.

Required searches:

```powershell
rg -n -i "Wong|Raman|protonated MEA|carbamate|bicarbonate|carbonate|molecular CO2|30 wt|60 bar" docs/papers/md data/reference/MEA
rg -n -i "Amundsen|density|viscosity|loaded MEA|CO2-loaded|aqueous MEA" docs/papers/md data/reference/MEA
rg -n -i "dielectric|relative permittivity|permittivity|MEA water|monoethanolamine water|Hsieh|Floriano|Nascimento" docs/papers/md data/reference/MEA
```

Tasks:

- Update `docs/roadmaps/mea_data_curation_plan.md`.
- Treat Wong 2015 and Amundsen 2009 as repo-local/expected extraction tasks.
- Treat MEA–H2O dielectric constants as local-literature extraction tasks.
- Create target folders/manifests if missing.
- Do not invent data.

Acceptance:

- Data status is explicit.
- Extraction tasks have target paths and required columns.

## Step 3 — Full-row Tier-A MEAH+/MEACOO- fit plan

Inspect:

- `data/reference/MEA/ChEq/Combined_ChEq.csv`
- `data/reference/MEA/ion_parameter_regression_sources.csv`
- `analyses/epcsaft_ionic_regression/results/ion_parameter_regression`
- `src/MEA/epcsaft_ionic/ion_parameter_regression.py`

Tasks:

- Document current selected-row promoted fit boundary.
- Plan full-row Tier-A fit.
- Include Wong Raman as validation first after extraction.
- Keep Böttinger as combined MEA+MEAH+, not direct MEAH+.

Acceptance:

- Roadmap states current fit boundary.
- Full-row next action is concrete.
- Required fit artifacts are listed.

## Step 4 — Regenerate pressure parity from the same parameter artifact

Inspect:

- `analyses/epcsaft_ionic_regression/results/pressure`
- `analyses/epcsaft_ionic_regression/results/global_regression`
- `analyses/epcsaft_ionic_regression/results/ion_parameter_regression`

Tasks:

- Identify whether current pressure parity uses the same promoted ionic parameter artifact as speciation.
- If not, add script/task requirements.
- Mark placeholder pressure figures as not publication-ready.

Acceptance:

- The roadmap names the exact parameter artifact for pressure/speciation figures.
- The final manuscript requirement says all final figures must use one parameter artifact.

## Step 5 — Stage pressure-coupled global regression behind ePC-SAFT dependencies

Inspect the ePC-SAFT dependency issues/PRs if accessible.

Expected dependencies:

- Task C / #86: generic implicit solved-state sensitivity framework.
- Task F / #89: generic speciation solver using ePC-SAFT activities.
- Task G / #90: generic VLE/fugacity-equilibrium solver.
- Task K / #94: generic regression row schema and native optimizer backend.
- Task L / #95: literature benchmark suite.

Tasks:

- Update `docs/roadmaps/epcsaft_dependency_matrix.md`.
- Do not request MEA-specific public APIs.
- Define Phase 1/2/3 gates around actual package availability.

Acceptance:

- Phase 1 does not depend on unavailable package features.
- Phase 2 depends on activity/speciation and fugacity equilibrium support.
- Phase 3 depends on generic regression backend support.

## Step 6 — Align manuscript claim with achieved evidence

Inspect:

- `docs/latex/main.tex`
- `docs/latex/sections/*.tex`
- abstract/conclusion/data availability if present.

Tasks:

- Do not rewrite all prose.
- Add a roadmap note with staged claim boundaries:
  - Phase 1: Smith–Missen reproduction baseline.
  - Phase 2: activity-based true-species ePC-SAFT evaluation.
  - Phase 3: coupled pressure/speciation regression.
- Add prohibited-claim checks.

Acceptance:

- No roadmap language overclaims a final predictive regression before artifacts exist.
- Final manuscript claim is evidence-gated.
