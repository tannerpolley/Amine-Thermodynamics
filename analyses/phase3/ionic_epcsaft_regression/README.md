# Full Ionic ePC-SAFT Regression

Canonical commands:

```bash
uv run python analyses/phase3/ionic_epcsaft_regression/scripts/generate_data.py
uv run python analyses/phase3/ionic_epcsaft_regression/scripts/render_figures.py
```

Curated artifacts live under `results/<plot_set>/` with plotted CSV snapshots, `.mpl.yaml` style sidecars, PNG previews, SVG figures, and PDF LaTeX artifacts.
Disposable solver/run output belongs under ignored `results/runs/`.

## Downstream SciPy regression experiment

The bounded application-level experiment can be reproduced with:

```bash
uv run python analyses/phase3/ionic_epcsaft_regression/scripts/run_scipy_regression_experiment.py --max-nfev 12
```

It fits one shared effective segment diameter for `MEAH+` and `MEACOO-`.
The shared constraint is deliberate: the admitted bulk density data cannot
separate cation and anion diameter contributions. Dispersion energies, Born
diameters, reaction constants, and binary interactions remain fixed.

The density/speciation-only fit converged to a shared diameter of
5.334530692 Å and was stable across three near-best starts. Relative density
RMSE fell from 13.75% to 2.49% in training and from 12.79% to 2.40% in reserved
validation. The candidate failed the pressure qualification: training median
absolute pressure error increased from 0.432 to 0.869 log10 units and reserved
validation increased from 0.542 to 0.730, with one failed state in each role.
The experiment therefore does not supply parameters for the manuscript or a
promoted parameter dataset. Its numerical outputs are retained under
`results/scipy_regression_experiment/`.
