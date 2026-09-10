# Analysis Workflows

This directory contains source-controlled scientific analysis, validation, and figure workflows. Runtime package code belongs under `src/MEA`; reusable literature and parameter inputs belong under `data/reference`; analysis-specific generated snapshots stay with the analysis that owns them.

## Hosted analysis site

The repository-level Quarto site is the only hosted analysis surface. Its
configuration and index are [`_quarto.yml`](_quarto.yml) and
[`index.qmd`](index.qmd); build [`_site/`](_site/) with:

```bash
bash analyses/render.sh
```

The site-level format and explicit workflow sidebar are inherited by every
rendered report. Individual analysis directories keep their
source records and retained results; they do not publish separate sites.

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

`toybox/` retains compact rejection receipts from retired exploratory
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
parameter notebook. The notebook is rendered through the root Quarto site and
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
