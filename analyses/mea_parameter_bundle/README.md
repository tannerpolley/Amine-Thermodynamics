# MEA Parameter Bundle Notebook

This directory is the canonical, update-in-place research notebook for the
single nine-species MEA ePC-SAFT parameter bundle. Keep
`notebook.tex` and `results/notebook.pdf` synchronized with the present
evidence, results, interpretation, and next experiments;
do not accumulate candidate-specific notebook copies or parallel status notes.

The current document owns the active MEA bundle. Its molecular
starting vector comes from ePC-SAFT Issues #80 and #119 and closed, unmerged PR
#134; a full 123-state comparison then selected Uyan solvent-only dielectric
mixing over the former ion-specific baseline and Schick component mixing. A
bounded direct-Engine campaign subsequently selected the displayed R4 and
carbon-dioxide dispersion-energy values. The notebook is the live MEA
authority for that parameter set and its recorded results.

The retained state packet contains raw Austgen R1--R3 values in records already
labeled with the common aqueous-molality standard state. The replay applies the
audited source-to-common shifts before constructing each Engine problem. The
uncorrected packet remains immutable input evidence; the correction and its
numerical consequences are documented in the notebook and calculation receipt.

`data/input/parameters.json` and `data/input/state-packet.json` are immutable
local snapshots from ePC-SAFT commit
`38e91823b6d4f26c1d549f07aaef24a089d8e16d`. Generate the retained numerical
tables with the exact retained Engine wheel, then render with the MEA
environment. The state packet intentionally excludes the source fit request's
parameter declaration; this replay binds the separately hashed notebook vector.
Nested continuation values are converted to finite warm starts, after which
their continuation identity and state are cleared before every solve. Every
successful result is checked against the notebook parameter fingerprint.

```bash
uv venv /tmp/mea-parameter-bundle-engine
uv pip install --python /tmp/mea-parameter-bundle-engine/bin/python \
  data/input/engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl
/tmp/mea-parameter-bundle-engine/bin/python \
  scripts/compare_permittivity_formulations.py
/tmp/mea-parameter-bundle-engine/bin/python scripts/generate_figure_data.py
uv run python scripts/render_figures.py
```

The generation receipt under `results/` anchors the retained pre-campaign
speciation grid; the selected pressure replay, current failure table, and fit
tables are sourced from the identified full-validation campaign. The main
speciation figure shows every retained 20 C, 30 wt%
principal-species and MEA-plus-MEAH+ observation from Bottinger, Jakobsen, and
Matin; matching 40, 60, and 80 C figures are retained as notebook appendices.
Exact reported zeros remain in the retained observation snapshot but are
omitted from the plots. Each broken logarithmic axis starts its expanded panel
30% below the lowest positive HCO3- observation
or model value, ends 3% above the displayed maximum, and compresses the range
from 1e-10 to that HCO3- cutoff. The retained speciation line snapshots are the
pre-campaign 46-state direct Engine grids and are labeled as qualitative
context in the notebook; they were not recomputed for the bounded selection.
Pressure lines are shape-preserving render-time interpolations of the selected
bundle's reactive Engine evaluations at the active-v1 observation coordinates. The pressure view includes
Aronu, Hilliard, Idris, Jou, Mamun, and Xu; experimental points remain visible
when a corresponding Engine state is non-evaluable. Complete target-level
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
pivot--slope, refinement, full-validation, and boundary results are retained
under `results/best-in-slot-campaign/`.
`permittivity-formulation-comparison.json` and its state/target CSVs retain the
full ion-specific/Schick/Uyan comparison. The selected live mapping is
`results/selected-current-best-parameters.json`. The renderer turns every
successfully evaluated target into the pressure/speciation parity figure
without rerunning the Engine.

Render from this directory with:

```bash
latexmk -lualatex -interaction=nonstopmode -halt-on-error \
  -outdir=results notebook.tex
```

The durable output is `results/notebook.pdf`. LaTeX intermediates are ignored
by the repository.

Build the deterministic absorption-agent handoff with:

```bash
uv run python scripts/build_absorption_handoff.py
```

The resulting `results/handoff/mea-reactive-epcsaft-parameter-bundle.zip` contains
the selected parameter mapping, reaction definition, pinned Engine wheel,
fit results, figure, notebook, file hashes, and an
executable verifier. Its stable name is overwritten when the selected bundle
changes.

`references.bib` is a byte-for-byte snapshot of the configured Zotero Better
BibTeX library export at `$HOME/Zotero/exports/references.bib`. Copy that live
master here after Zotero updates; the notebook prints only cited entries.
