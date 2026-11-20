# Analysis Workflows

This directory contains source-controlled scientific analysis, validation, and figure workflows. Runtime package code belongs under `src/MEA`; reusable literature and parameter inputs belong under `data/reference`; analysis-specific generated snapshots stay with the analysis that owns them.

## Snakemake adoption

The confirmed decisions for all 11 top-level analyses and their nested work
are recorded in [scientific context](../docs/scientific/CONTEXT.md#local-snakemake-workflow-adoption).
Ten analysis-local presentation workflows are installed by
[issue #133](https://github.com/tannerpolley/Amine-Thermodynamics/issues/133).
The `mea_parameter_bundle/` workflow remains held until its scientific results
are reconciled; all eleven adoption decisions remain in force.

From an installed analysis directory, run:

```bash
PATH="$HOME/.cache/cse-quarto-demo/.venv/bin:$PATH" snakemake --cores 1 --dry-run present
PATH="$HOME/.cache/cse-quarto-demo/.venv/bin:$PATH" snakemake --cores 1 present
```

The dedicated presentation interpreter supplies Snakemake 9.27.0. Reproduce
that approved dependency with `uv pip install --python
~/.cache/cse-quarto-demo/.venv/bin/python 'snakemake==9.27.0'`. Renderers use
`~/.local/bin/uv run --no-sync` in the project environment, preserving its installed Engine
and dependency lock. Each workflow plans one `present` job, verifies retained
inputs before rendering, and checks them again afterward. It has no numerical
calculation entry.

Each `retained-results.sha256` selects the existing input set from base commit
`2a01cdc4b4d5a62eea2fa2e1556c40128c548a9d`; existing producing identities and
source records remain authoritative. The matched species comparison also
checks its existing source and output hash inventories before its renderers
rewrite them. Historical eNRTL and film create small Markdown includes from
their retained JSON. Missing or modified inputs stop presentation; recover the
identified retained version rather than rewriting hashes or running a retired
generator. This file checking establishes presentation integrity, not a new
calculation or physical validation.

[Issue #90](https://github.com/tannerpolley/Amine-Thermodynamics/issues/90) still
owns the required source-data calculation, coherent result delivery and notebook
refresh experiments. Presentation installation does not complete
its calculation, unchanged-run or dependency-rebuild requirements.

From the repository root, check refusal and preservation in a disposable copy:

```bash
PATH="$HOME/.cache/cse-quarto-demo/.venv/bin:$PATH" python3 tests/check_presentation_retained_inputs.py
```

## Root Quarto analysis website

`analyses/` is one root Quarto analysis website managed by the CSE
`manuscript.py`. [`index.qmd`](index.qmd) is its home page. `_quarto.yml` holds
the shared HTML settings. `_cse-manuscript.json` records the published pages
and their sidebar groups. The sidebar links to pages, and each page has its own
table of contents.

From the repository root, set `CSE_PLUGIN` to the installed plugin directory
when installing or updating the tooling. Use `include` to register a report,
`render.sh` to render the site, and `refresh` to update one report and the home
page.

```bash
python3 "$CSE_PLUGIN/assets/visualize/project/quarto/manuscript.py" init analyses/
python3 analyses/manuscript.py include analyses/ analyses/ideal_reaction_equilibrium/index.qmd \
  --title "Ideal reaction-equilibrium reference" --group "Reference and comparison"
bash analyses/render.sh
python3 analyses/manuscript.py refresh analyses/ analyses/mea_parameter_bundle/notebook.qmd
```

Omit `--group` to list a report at the top level. `render.sh` renders HTML by
default with document execution disabled. Open `analyses/_site/index.html` for
the home page. A registered `case/result.qmd` renders to
`analyses/_site/case/result.html`. If the report directory has a Snakefile,
`refresh` first runs its `present` rule. For strict bundle certification, see
the [bundle README](mea_parameter_bundle/README.md).

```text
analyses/
  toybox/
    ionic_parameter_fit_playground/
  paper_validation/
    2015_baygi/
  six_species_solubility_reference/
  neutral_pcsaft_pressure_reference/
  ideal_reaction_equilibrium/
  speciation_evidence_harmonization/
  historical_fixed_parameter_epcsaft_evaluation/
  reactive_epcsaft_parameter_evidence/
  enrtl_six_species_ideal_comparison/
  mea_parameter_bundle/
  film_chemistry_work_package_a/
```

`toybox/` retains compact rejection records from retired exploratory
calculations. These results are excluded from parameter promotion, manuscript
inputs, and predictive-model claims.

`paper_validation/` is reserved for paper-matching reproduction work: figures,
tables, and parameters should be recreated to match the cited paper table or figure as
directly as possible. The other analysis names describe their scientific role,
not a project stage. Historical fixed-parameter evidence remains explicitly
separate from future reactive ePC-SAFT parameter evidence.

`mea_parameter_bundle/` is the update-in-place research notebook for the
nine-species parameter bundle. It owns the active MEA mapping, retained
calculations, figures, fit statistics, cross-analysis interpretation, and next
experiments. `enrtl_six_species_ideal_comparison/` retains the complete matched
six-/nine-species calculation packet, source notebook, UQ tables, and figures;
its packet-specific results are summarized, rather than duplicated, in the live
parameter notebook. The notebook is rendered through the root Quarto website and
is not a certified numerical publication; the strict result-freshness check
currently refuses the retained generation.

`film_chemistry_work_package_a/` checks source-qualified film reaction and
transport inputs. It does not supply an accepted thermodynamic parameter set.
The role of each analysis, historical evidence to preserve, and unresolved
ownership findings are recorded in the
[repository audit](../docs/scientific/REPOSITORY_AUDIT_2026-09-08.md).

Each executable analysis should remain self-contained:

```text
analyses/<short-id>/
  README.md
  analysis.yaml
  data/
    processed/
  figures/
    <figure_id>/
      input/
      output/
      scripts/
  results/
  scripts/
```

Only create optional folders when the analysis needs them. Curated Matplotlib plot bundles keep the plotted CSV snapshot, `.mpl.yaml` sidecar, PNG preview, SVG figure, and PDF together in the owning figure or result folder. Disposable run output belongs under ignored `results/runs/`.

Generated results and render products are marked with GitHub Linguist
attributes; generated SVGs are tracked as binary-style diffs. Review executable
changes separately with:

```bash
git diff --stat <base>...HEAD -- src/ tests/ scripts/ ':(glob)analyses/**/scripts/**'
```
