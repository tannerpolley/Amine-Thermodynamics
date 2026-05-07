# MEA-Thermodynamics Handoff

Date: 2026-05-07

This repo was consolidated so `main` is now the active ePC-SAFT/legacy MEA workflow branch. The old main state was preserved separately as `legacy/main-legacy`.

## Branch State

- Active branch: `main`
- Legacy branch: `legacy/main-legacy`
- Remote branches expected:
  - `origin/main`
  - `origin/legacy/main-legacy`
- Stale local/remote Codex branches were removed.
- The normal local checkout is `C:\Users\Tanner\Documents\git\MEA-Thermodynamics` and should be on clean `main`.

## Major Changes Already Done

- Converted the project to uv:
  - `pyproject.toml`
  - `uv.lock`
  - `.python-version`
  - no Conda workflow should be required for active commands.
- Separated legacy workflows:
  - `MEA/six_species/`: canonical six-species legacy speciation and Jou CO2 pressure workflow.
  - `MEA/nine_species/`: diagnostic nine-species legacy workflow.
  - `MEA/common/`: shared paths, data loading, reporting, and plot helpers.
- Archived old root scripts and obsolete entrypoints under `archive/`.
- Added active ePC-SAFT workflows:
  - `MEA/epcsaft_neutral/`: neutral EOS parity workflow.
  - `MEA/epcsaft_ionic/`: full ionic MEA-CO2-H2O diagnostic/regression workflow.
- Added tests:
  - `tests/test_epcsaft_ionic.py`
- Updated the main runner:
  - `MEA/run_plot_exports.py`

## Important ePC-SAFT Package Context

The ePC-SAFT package was coordinated through:

https://github.com/tannerpolley/ePC-SAFT/discussions/26

Downstream MEA validation drove package-side PRs that added/fixed native reactive electrolyte bubble pressure:

- PR #27: native electrolyte bubble pressure path.
- PR #28: fixed misleading aggregate success status.
- PR #29: added explicit phase-handoff tolerances.

Latest package commit validated from this repo:

```text
f957ac970e51c873914287ea2a8cc778eda0df78
```

Install command used:

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
uv pip install --reinstall "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@f957ac970e51c873914287ea2a8cc778eda0df78"
```

Use `uv run --no-sync ...` after this direct install if you do not want uv to resync back to a local path dependency.

## Current Validation Results

Focused ionic tests:

```powershell
uv run --no-sync python -m unittest tests.test_epcsaft_ionic -v
```

Result:

```text
2 passed
```

Full ionic export:

```powershell
uv run --no-sync python -m MEA.epcsaft_ionic.plot_results
```

Result:

```text
Pressure successes: 161/161
Speciation activity successes: 74/74
Raw pressure median |log10(model/data)|: 0.36235972825694707
Raw pressure max |log10(model/data)|: 0.9726416719381225
```

Generated artifacts:

```text
out/epcsaft/ionic_regression/ionic_pressure_comparison.csv
out/epcsaft/ionic_regression/ionic_speciation_activity_residuals.csv
out/epcsaft/ionic_regression/ionic_evaluation_summary.json
out/plots/MEA/epcsaft_ionic/pressure/ionic_epcsaft_co2_pressure.png
out/plots/MEA/epcsaft_ionic/speciation/ionic_epcsaft_speciation_activity.png
```

## Recommended Verification Commands

From the repo root:

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
uv sync
uv run python -m compileall MEA tests
uv run python -m MEA.six_species.plot_speciation
uv run python -m MEA.six_species.plot_pressure
uv run python -m MEA.nine_species.plot_speciation_diagnostic
uv run python -m MEA.nine_species.plot_pressure_diagnostic
uv run python -m unittest tests.test_epcsaft_ionic -v
uv run --no-sync python -m MEA.epcsaft_ionic.plot_results
```

## Remaining Work

- Runtime capability blocker is resolved for ionic pressure/speciation export.
- Remaining work is model-quality/regression work:
  - improve CO2 partial-pressure fit beyond median abs log10 error near `0.36`;
  - improve trace-species speciation fit, especially CO2, H3O+, and OH- metrics;
  - decide and document which parameters are fixed from literature versus regressed;
  - avoid arbitrary `k_ij` fitting without direct binary data;
  - fit or source `d_born` parameters from dielectric/relative-permittivity evidence where possible.
- The ionic parameter set is still provisional and should not be treated as a final thermodynamic model.

## Coordination Notes

The user-level skill formerly named `coordinator` was renamed to `coordination`.

Use `$coordination` for cross-repo agent loops. The key lesson from this thread:

- Each thread should create and own its own watcher automation using `destination="thread"`.
- Do not rely on another thread creating a heartbeat for this thread via raw `targetThreadId`; it can fail with `Heartbeat thread not found`.
- Use the GitHub Discussion as the durable handoff, and pass ownership with `Next actor: upstream`, `Next actor: downstream`, or `Next actor: none`.

## Legacy Branch

`legacy/main-legacy` contains the old main state plus committed LaTeX paper sources under `docs/latex/`.

Commit on legacy branch:

```text
be00d6c add legacy latex paper sources
```

That branch is pushed to `origin/legacy/main-legacy`.
