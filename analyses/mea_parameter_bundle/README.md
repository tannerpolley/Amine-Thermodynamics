# MEA Parameter Bundle Notebook

This directory is the canonical, update-in-place research notebook for the
single nine-species MEA ePC-SAFT parameter bundle. The rendered view is a small
Quarto site: [`notebook.qmd`](notebook.qmd) is the parent overview with the
selected parameter tables and the main pressure, speciation and heat figures;
each child analysis folder contains one `index.qmd` report and its
`analysis.yaml` identity. Keep the overview and child reports synchronized with
the retained evidence. Link to detailed records rather than creating
candidate-specific notebook copies or parallel status notes.

## Presentation map

The repository-level site at `analyses/` is the hosted entry point. Render it
with `bash ../render.sh` from this directory or `bash analyses/render.sh` from
the repository root; open `analyses/_site/index.html` (or the root preview at
<http://127.0.0.1:8770/>). The bundle pages below remain the source-owned
children of that site.

For the bundle's strict freshness gate and local snapshots, render the complete
overview plus study pages with:

```bash
bash render.sh notebook.qmd
```

For an automatically refreshing local view of the complete site while editing,
start the repository-level Quarto preview instead:

```bash
bash ../preview.sh
```

Open <http://127.0.0.1:8770/>. The preview watches the QMD, CSS, and included
files, rebuilds changed pages, and never executes the scientific model. It stays
available until stopped; systemd restarts it if the process fails. The
checked-in systemd unit at
`systemd/mea-parameter-bundle-preview.service` provides the same preview as a
user service; install it with:

```bash
install -D systemd/mea-parameter-bundle-preview.service \
  "$HOME/.config/systemd/user/mea-parameter-bundle-preview.service"
systemctl --user daemon-reload
systemctl --user enable --now mea-parameter-bundle-preview.service
```

The copied `notebook.html` remains the offline fallback. It is a rendered
snapshot and does not update until `render.sh` is run.

The render wrappers always pass `--no-execute`; Quarto reads retained tables,
figures and receipts but never runs the thermodynamic model. The hosted root
site uses an explicit native Quarto sidebar, so its links, groups, and order
are deliberate and stable rather than inferred from filesystem names. The
parent/child tree is recorded in [`analysis.yaml`](analysis.yaml): neutral
MEA–water,
ionic/speciation, CO₂–R4, reaction-temperature, Born/permittivity, calorimetry,
coupling and identification, association topology, and historical designs. The
historical page preserves the July designs as discarded-strategy context, with
exact Git retrievals, rather than presenting them as the current plan.

## Claude experiment checkpoint — 3 September 2026

**Historical checkout checkpoint (audit update, 8 September):** the instructions
below describe this branch's v3 starting point, not the next unrun experiment.
MEA Issues #83–#86 now report completed F/S/ionic diagnostics and a reviewed v4
start-volume correction in `codex/reaction-partition-fs-study`. This checkout
still has the v3 evaluator hash shown below. Do not repeat those studies or
start a broad refresh here before reconciling that owner-held work. The
[repository audit](../../docs/scientific/REPOSITORY_AUDIT_2026-09-08.md) and
[scientific roadmap](../../docs/scientific/PREDICTIVE_MEA_PROGRAM.md) distinguish
reported results from locally retained evidence. The selected JSON is unchanged.

The bounded formation/partition experiment does **not** require a full figure,
calorimetry, HTML, or ZIP refresh first. Those publication checks protect
published comparisons; they are not prerequisites for new direct Engine
calculations. Use the commit containing this section as the fixed input/code
checkpoint, and keep its shared evaluator unchanged while the experiment runs.
This is an experiment starting point, not acceptance of the parameter model.

The reviewed Claude plan uses 12 baseline states at 30 mass% MEA and 40/80 °C:
Böttinger speciation states 042, 045, 049, 050, 063, 065, 066, 067 and pressure
rows `vle_obs_0186`, `vle_obs_0142`, `vle_obs_0206`, `vle_obs_0211`.
No Xu 2011 or 120 °C observations enter this screen. The coordinates are
`F = ln K2 - ln K5 - 0.5 ln K4` and `S = -ln K4`:

- F offset d: R2 `a += d`.
- S offset d: R2 `a -= d/2`, R4 `a -= d`.
- Keep EOS parameters, R5, and every slope coefficient fixed. These are ln K
  intercept offsets, **not** the earlier reaction-enthalpy shifts.
- Native derivatives use `ActiveParameterSet` in declared R2-a/R4-a order;
  then check offsets ±0.1. Twelve baseline plus 48 offset evaluations give a
  60-state ceiling, not a promise that every state finishes in the time limit.

Reuse `shared_evaluation.corrected_request`, `prepared_problem`, and the bounded
`_solve_in_child(..., active_parameters=active)` path demonstrated in
`run_reaction_temperature_fit.run_sensitivity_check`. Native row Jacobians are
in `SolveSnapshot.rows`; `evaluate_state` retains ordinary predictions and
warm starts but is **not** a cached-Jacobian interface. Do not run the old
`--sensitivity-check` command for this new experiment: it compares historical
R4/R5 enthalpy columns, not F/S. Retain new Jacobians, their ordered identities,
offset results, timings, and failures in the experiment's own results directory.

Use one worker, one logical CPU, single BLAS/OpenMP threads, 60 seconds maximum
per native state, and 900 seconds for the whole experiment. Apply the existing
`refresh_results.run_stage` process boundary to the experiment command and
pass its remaining deadline to each child. Checkpoint each completed state;
do not retry automatically or overwrite the selected JSON or historical fit.
Report paired residuals, coverage/failures, direction similarity, and one
sensitivity figure. No fitting or adoption is part of this screen.

Verified checkpoint inputs (SHA-256):

| Input | SHA-256 |
|:--|:--|
| `results/selected-current-best-parameters.json` | `a9186c93759f2e2c02a6c913350ad06a244fff3f82503820c9962b3df8dd40d9` |
| `scripts/shared_evaluation.py` | `6bc94e6c628aa212ccc4a6cce32226eed42aadaca6d06692e6c9be6984b6e32d` |
| `scripts/run_reaction_temperature_fit.py` | `cc83e4291e5d7603acf7b03be72bdacc6f1d557db9a9449e213688c29d4cf5bd` |
| `data/input/state-packet.json` | `86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448` |
| `data/input/engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl` | `40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805` |

Before running in a new checkout, install that retained wheel explicitly; do
not substitute a newer sibling Engine build. With that environment prepared,
from the repository root:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 45s uv run --no-sync python analyses/mea_parameter_bundle/scripts/run_reaction_temperature_fit.py --self-check
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 90s uv run --no-sync pytest analyses/mea_parameter_bundle/tests -q
```

At this checkpoint, the self-check and all 76 repository/analysis tests pass
(9.32 seconds for the tests on one CPU). A direct bounded native solve of
`Bottinger2008_state_050` returned all three requested outputs with both
R2-a/R4-a derivatives in 0.49 seconds. This confirms the derivative path, not
the runtime or successful coverage of the unrun 60-state experiment.
The earlier adoption writer still omits scored R1/R3 shifts; do not invoke
`--adopt`. Repair and re-review that writer before any future adoption. The
unfinished publication and this known adoption limitation do not block the
fixed-EOS F/S screen. Old v2 caches cannot be relabeled as current v3 results.

## Retained parameter evidence

The selected JSON owns the exploratory incumbent; the notebook describes its
retained evidence and does not establish an accepted MEA parameter set. Its molecular
starting vector comes from ePC-SAFT Issues #80 and #119 and closed, unmerged PR
#134; a full 123-state comparison then selected solvent-only mass-fraction
mixing over the former ion-specific baseline and all-component mixing. The
selected rule uses the normalized salt-free-solvent average in Ascani and
Held's Equation 13 with water and MEA as the explicit solvent pool. A
bounded direct-Engine campaign subsequently selected the displayed R4 and
carbon-dioxide dispersion-energy values. The current fixed-parameter
Born--permittivity study retains solvent-only mass-fraction dielectric mixing.
The subsequent reaction-temperature selection is recorded in
`results/reaction-temperature-fit/adoption-receipt.json`; read the current
R2/R4/R5 coefficients from `results/selected-current-best-parameters.json`,
not from the earlier study's fitted values.
The active mapping omits redundant formulation switches: positive unique ion
Born diameters together with a non-unit neutral solvation factor automatically
activate corrected SSM+DS, while a zero Born diameter inherits that ion's
Debye--Hückel diameter and recovers original Born. The notebook summarizes that parameter record and its recorded results.

The retained compact state packet contains deduplicated requests and raw Austgen R1--R3 values in records already
labeled with the common aqueous-molality standard state. The replay applies the
audited source-to-common shifts before constructing each Engine problem. The
uncorrected packet remains immutable input evidence; the correction and its
numerical consequences are documented in the notebook and calculation receipt.

The calorimetry preparation step reads the canonical MEA observation table and
materializes only the declared paired-state campaign rows. It retains 66
Kim--Svendsen 40/80 C calibration observations, 20 Kim--Svendsen 120 C
temperature-holdout observations, and 27 Kim et al. 2014 Table A1-1
model-selection comparison observations. It also records each preceding
endpoint within the same source, temperature, concentration, and run. Generate
and verify that view with:

```bash
uv run python scripts/prepare_calorimetry_partition.py
```

The selected input is `data/input/calorimetry-observation-partition.csv`; its
source hash, selected-view hash, row counts, pairing rule, assumed initial
loading, and first-row exclusion sensitivity are recorded under
`results/calorimetry/`. The selected bundle is now compared with all 113
retained observations using direct paired-state total enthalpy generated by
`scripts/evaluate_direct_absorption_heat.py`. The calculation uses one
reaction-consistent conserved gauge, Engine residual enthalpy, and an explicit
zero-vapor/ideal-CO2-feed reconstruction. The older Gibbs--Helmholtz
pressure-slope result remains a historical secondary diagnostic; its summary
records the input curve hash but does not establish the current parameter identity.

`data/input/parameters.json` and the compact `data/input/state-packet.json` are immutable
local snapshots from ePC-SAFT commit
`38e91823b6d4f26c1d549f07aaef24a089d8e16d`. The retained Engine wheel includes
the fast Born/permittivity implementation and solved-pressure reactive
enthalpy at commit `8438ce5f94a547189c91c4ec180a7782d60879d6`; its
SHA-256 is
`40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805`.
Generate numerical tables with that exact wheel, then render with the MEA
environment. The state packet intentionally excludes the source fit request's
parameter declaration; this replay binds the separately hashed notebook vector.
Nested continuation values are converted to finite warm starts, after which
their continuation identity and state are cleared before every solve. Cache reuse requires matching source, evaluator, EOS parameter, reaction,
thermal-reference, and request identities. The recorded model identity
distinguishes selected and candidate evaluations.

Use the repository's pinned uv environment. From this analysis directory:

```bash
uv run python scripts/refresh_results.py
```

This is the normal update command. It runs figure data, calorimetry, thermal
checks, figure rendering, Quarto, and handoff packaging sequentially. It uses
one logical CPU, single-threaded BLAS/OpenMP, lower scheduling priority, a
2 GiB per-process solver address-space limit and a 2 GiB native V8 heap cap
for Quarto (neither is an aggregate RAM quota), and a
15-minute hard wall deadline for the entire refresh. `--wall-seconds` and
`--memory-mib` explicitly override those limits; they are never increased
automatically. A timeout stops the owned process group and preserves completed
state caches. Cache reuse also requires an unchanged evaluator source hash;
edits to the evaluator invalidate the earlier caches, even within one version.
A state that crosses the invocation deadline is not retained. Another refresh
cannot run concurrently. Re-running resumes
matching cached states; it does not silently reuse values from another model,
parameter vector, reaction mapping, or thermal reference.
Standalone numerical campaign commands use the same one-CPU, 2 GiB,
15-minute process boundary; they are not an unbounded alternative.

`scripts/shared_evaluation.py` owns request preparation, the pinned wheel,
cached equilibrium evaluation, recovery, and failure diagnostics. Figure,
heat, and parameter-study callers use it rather than private solve loops.
Numerical tolerances and model equations are unchanged. Rendering alone never
launches the Engine. Hash checks reject stale inputs, changed result tables,
or figures not yet regenerated for the current selection. Historical results
remain evidence of their original input vectors, not current predictions.

The older permittivity comparison is an explicit experiment, not an update
step: `compare_permittivity_formulations.py --parameters PATH` writes only
under `results/historical/permittivity-comparison/` and cannot replace the selected bundle.
Render a newly generated comparison with
`render_figures.py --permittivity-comparison results/historical/permittivity-comparison`;
it is not part of the current refresh.

The generation receipt under `results/` anchors the selected pressure replay,
current failure table, and fit tables. The pressure
replay preserves certified continuation states across nearby loadings and,
when needed, neighboring temperatures while retaining the original independent
start as a fallback. The main
speciation figure shows every retained 20 C, 30 wt%
principal-species and MEA-plus-MEAH+ observation from Bottinger, Jakobsen, and
Matin; matching 40, 60, and 80 C figures remain linked supporting views.
Exact reported zeros remain in the retained observation snapshot but are
omitted from the plots. Each broken logarithmic axis starts its expanded panel
30% below the lowest positive HCO3- observation
or model value, ends 3% above the displayed maximum, and compresses the range
from 1e-10 to that HCO3- cutoff. The plotted line tables are local render
products regenerated from the selected extended-Born and reaction-adjusted
parameter mapping when the figures are refreshed.
Pressure lines are shape-preserving render-time interpolations of the selected
bundle's reactive Engine evaluations at the active-v1 observation coordinates. The pressure view includes
Aronu, Hilliard, Idris, Jou, Mamun, and Xu. Current coverage and failed states
are recorded in the generation receipt; the earlier vector evaluated all 161 states.
Complete target-level
residuals and grouped overall, temperature, source, species, and
temperature--source statistics are retained in
`results/current-best-fit-residuals.csv` and
`results/current-best-fit-statistics.csv`.
`parameter-start-comparison.csv` and `parameter-sensitivity-screen.csv` retain
the bounded diagnosis used by the notebook to select the current parameter
start and reject unsupported parameter substitutions.
`quick-endpoint-perturbation-screen.csv` and its receipt retain the earlier
representative-state full bubble-point endpoint diagnostic and the single
SciPy reaction-root consistency check. The complete superseding sensitivity,
full-validation summary and selected row-level results are retained under
`results/best-in-slot-campaign/`; rerunnable trial grids and caches stay local.
`results/born-permittivity-study/` supersedes the narrower dielectric
comparison for structure selection. It retains the study summary, paired
common-row comparisons, and selected sensitivity tables; full trial matrices
and failure dumps are reproducible and stay local. Molecular CO2 pool exclusion
means exclusion from both SSM $f_{mix}$ and the salt-free neutral-permittivity
pool while CO2 remains a reacting EOS component. The selected live mapping
remains `results/selected-current-best-parameters.json`.

Render from this directory with:

```bash
bash render.sh notebook.qmd
```

The overview and child reports render under the root site's `_site/` directory.
The site copies displayed figures and assets into that output; evidence links
still require the repository. The overview is the user-facing entry point and
the sidebar links to every child report.
The wrapper checks result freshness and always passes `--no-execute`, so
rendering cannot rerun the model. A successful build hashes the source and HTML;
manual prose remains investigator-reviewed, not inferred from a timestamp.
The former LaTeX/PDF notebook is retired; historical prose and selected
evidence remain in Git, while rerunnable detail tables and plot sidecars stay
out of the mergeable tree.

## Related species-reduction and sensitivity analysis

`../enrtl_six_species_ideal_comparison/` retains the complete six-/nine-species
comparison, including its Quarto source, self-contained HTML and PDF notebooks,
calculation scripts, exact packet receipts, row-level tables, UQ checkpoints,
and figure bundles. This notebook summarizes the conclusions that affect the
active bundle and records which results can be used in the manuscript. The
companion notebook remains the detailed calculation record so its results are
not copied into parallel status files.

The latest shared-driver refresh stopped at pressure state 87/161 after 900
seconds. The retained figures, HTML, and thermal checks are not a current
synchronized publication. The corrected `notebook.qmd` can still be rendered
for day-to-day discussion with `bash render.sh notebook.qmd --working-copy`.
That render includes a visible warning, uses the retained figures as labeled,
and does not stamp numerical publication or authorize packaging. It replaces
the previously stale HTML without rerunning the model. The old thermal
validation files still contain invalid retired three-knot comparison rows.
The default render and handoff packaging continue to require a successful
numerical refresh. Display colors mark supported values (green), working values
whose evidence should be reviewed for green (blue, including fixed/derived
choices), and values needing targeted testing or regression (yellow). Test
first; regress only if observations can constrain the parameter. Color changes
do not change parameter values or their recorded scientific qualifications.
The current yellow targets are only the R2/R4 intercepts in the F/S experiment;
retained transfer values remain blue unless a specific test justifies reopening
them. The working-note callout is part of the Quarto source, preserving the
normal page margins and table-of-contents sidebar in both render modes.

Build the deterministic absorption-agent handoff locally when needed with:

```bash
uv run python scripts/build_absorption_handoff.py
```

The generated ZIP is intentionally local and is not a checked-in result. The
packager verifies the selected mapping and current source hashes before writing
it.
