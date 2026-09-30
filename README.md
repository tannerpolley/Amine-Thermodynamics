# MEA Thermodynamics

MEA-CO2-H2O thermodynamics workflows organized around importable package code in `src/MEA`, reusable reference data in `data/reference`, and durable analysis workspaces in `analyses/<category>/<analysis_id>`.

## Canonical Commands

```bash
uv sync --locked --group test
uv run ruff check src scripts analyses tests
uv run python scripts/doctor.py
uv run python scripts/validate_project.py quick
uv run python scripts/validate_project.py confidence
bash scripts/build_manuscript.sh
uv run python scripts/check_manuscript_freshness.py
```

Use each analysis README for its supported calculation or render command.
Several historical analyses retain rendering only; the parameter notebook has
its own bounded refresh and render-only commands.

Historical calculated tables and figures remain evidence only. New generic
ePC-SAFT methods are built and debugged first in the Engine repository. After
upstream acceptance, this repository may reproduce the pinned method directly
against MEA-owned inputs and an accepted immutable packet.

The lockfile pins the legacy `pcsaft.flashTQ` baseline to an immutable Git
revision and declares its Cython/NumPy build requirements. It does not install
the notebook's `epcsaft` runtime. That analysis requires its explicitly retained
immutable wheel; see [the parameter-bundle README](analyses/mea_parameter_bundle/README.md).
The historical Engine lock under `data/reference/MEA/manifests/` identifies a
different calculation and must not be substituted for the notebook wheel.

Package imports remain `import MEA...`; source lives under `src/MEA`.
Old file-path commands such as `uv run python MEA/run_plot_exports.py` are intentionally not preserved.

## Layout

- `src/MEA/`: importable model, data-loading, ePC-SAFT, and plotting support code.
- `data/reference/MEA/`: reusable MEA VLE and chemical-equilibrium reference tables.
- `analyses/paper_validation/2015_baygi/`: Baygi 2015 figure, parameter-table, and neutral parity reproduction.
- `analyses/six_species_solubility_reference/`: retained six-species pressure and speciation reference calculation.
- `analyses/neutral_pcsaft_pressure_reference/`: neutral PC-SAFT pressure reference tables and figures.
- `analyses/ideal_reaction_equilibrium/`: ideal reaction-equilibrium manuscript evidence.
- `analyses/speciation_evidence_harmonization/`: basis-separated experimental speciation source evidence.
- `analyses/historical_fixed_parameter_epcsaft_evaluation/`: historical true-species fixed-parameter ePC-SAFT evidence.
- `analyses/reactive_epcsaft_parameter_evidence/`: Issue #70 refusal evidence, bounded historical diagnostics, and dormant parameter-evaluation methods.
- `analyses/mea_parameter_bundle/`: exploratory incumbent, parameter-first working HTML notebook, and retained comparisons; numerical publication remains incomplete.
- `analyses/enrtl_six_species_ideal_comparison/`: packet-specific species reduction and sensitivity comparisons.
- `analyses/film_chemistry_work_package_a/`: bounded film-input source and consistency checks; no accepted thermodynamic packet.
- `docs/scientific/latex/`: writable manuscript source mirrored from the separate Overleaf Git checkout.
- `scripts/`: root doctor, validation, and plot orchestration entrypoints.

Removed diagnostic workflows remain recoverable from Git history and archival tags; they are not part of active `main` validation.

## License and Citation

Repository software and original project documentation are available under the
[MIT License](LICENSE). Third-party experimental data and source material retain
their original terms and provenance; the repository license does not relicense
those works. Cite the exact version used through [CITATION.cff](CITATION.cff).

Each analysis owns its canonical generated tables under `results/`. Figure output folders contain only the exact plotted CSV subset and render bundle; every `.mpl.yaml` sidecar records the repository-relative plotted-data path and SHA-256 digest. Disposable run output belongs under ignored `analyses/**/results/runs/`.

Tracked JSON is limited to 100 KiB and 3,000 lines. Larger scientific tables
must use CSV, structured parameter sets must use the split CSV/TOML bundle
format, and raw fit requests/results must remain in ignored `results/runs/`.
`scripts/validate_project.py` enforces both limits without exceptions.

## Key Evidence Paths

- `analyses/reactive_epcsaft_parameter_evidence/results/issue_70/predictive_mea_parameter_decision.json`
- `analyses/six_species_solubility_reference/results/pressure/legacy_pcsaft_jou_recomputed_fit.png`
- `analyses/six_species_solubility_reference/results/pressure/legacy_pcsaft_jou_recomputed_fit.svg`
- `analyses/six_species_solubility_reference/results/speciation/speciation.png`
- `analyses/neutral_pcsaft_pressure_reference/results/pressure/epcsaft_neutral_pcsaft_parity.png`
- `analyses/reactive_epcsaft_parameter_evidence/results/issue_70/comparison_evidence_table.csv`
- `analyses/reactive_epcsaft_parameter_evidence/co2_water_induced_association/results/summary.json`
- `analyses/paper_validation/2015_baygi/results/neutral_parity/baygi_neutral_epcsaft_pcsaft_pressure_parity.png`

## Manuscript

The article draft source lives under `docs/scientific/latex/`. It is a normal folder in this repo, not a submodule. Set `MEA_OVERLEAF_MIRROR` to the absolute path of the independent Overleaf-connected mirror checkout.

Build and hash-verify the local manuscript with:

```bash
bash scripts/build_manuscript.sh
uv run python scripts/check_manuscript_freshness.py
```

The build is written only to `docs/scientific/latex/builds/`. The tracked `manuscript_references.bib`, `project_sources.bib`, and `official_sources.bib` files make citations reproducible in a clean clone; a full personal-library `references.bib` export remains ignored.

Sync the local manuscript source back to the Overleaf mirror with:

```bash
bash docs/scientific/latex/scripts/sync_to_overleaf_mirror.sh
```

## Model Boundaries

There is no accepted MEA ePC-SAFT parameter set. The exploratory incumbent and
its comparison history live under `analyses/mea_parameter_bundle/results/`;
Engine Issue #80 owns the acceptance campaign. This repository retains source evidence,
the Issue #70 supported-negative decision, and reproduction/rendering conventions
for an accepted immutable packet; historical calculated results are not live
parameter authority.

The [scientific roadmap](docs/scientific/PREDICTIVE_MEA_PROGRAM.md) separates
source qualification, estimation, numerical coverage, independent validation,
and manuscript/absorber use. The [8 September audit](docs/scientific/REPOSITORY_AUDIT_2026-09-08.md)
records current inconsistencies and conditional removal candidates. This
checkout still has evaluator v3; the reviewed v4 start-volume correction and
ionic comparison are reported in MEA Issues #85/#86 in another checkout.
Reconcile that work before starting new local numerical comparisons.
