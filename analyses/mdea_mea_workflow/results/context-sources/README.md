# Additional MDEA context, issue 225

Xiao Table 4 supplies 20 equilibrium pressure/loading states. Frozen A3 and B1
CO2 partial-pressure AARDs are 20.397551% and 28.276415%, respectively.
All 20 bubble-state density gates pass at each endpoint: no dense, gas,
ambiguous or unresolved states. The 24.2% Ermatchkov verdict is unchanged.

The notebook context section owns interpretation and limitations.
`data/reference/MDEA/context-sources.json` owns source identities, hashes,
locators, units, bases, uncertainties and transcription identities.
`unscored-states.json` retains all 16 Zhang conditions and four Derks rows for
each endpoint, including their unscored reasons. Zhang is extrapolation;
its eight SI transient rows are not equilibrium observations.

From this issue worktree, use the separate `.venv` with Python 3.13 and the
immutable Engine wheel named in `runtime.json`, plus numpy, scipy, pandas and
matplotlib. The script verifies the installed Engine files against the wheel.

```bash
agent-heavy nice -n 10 .venv/bin/python -I analyses/mdea_mea_workflow/scripts/score_context.py
nice -n 10 .venv/bin/python -I analyses/mdea_mea_workflow/scripts/plot_context.py
```

The phase declaration and threshold reuse #222 `stage2.py`: full-species
liquid and neutral vapor trials at each scored bubble state; packing fraction
0.10, ambiguity interval (0.05, 0.35), gas evolution counted separately.
No searches are claimed for unscored states. All row failures would be retained;
a complete AARD is withheld if any row prediction is unavailable.

The figure reads retained predictions only. Source standard uncertainty bars
represent pressure and loading only, not model uncertainty. To render without
changing managed site membership, run from `analyses/`:

```bash
agent-heavy nice -n 10 quarto render mdea_mea_workflow/notebook.qmd --to html --no-execute
```

The normal manuscript refresh command was not used because its sync step can
write the explicitly excluded `_cse-manuscript.json`. Direct HTML rendering
succeeded. No site service was started or restarted. Independent delivered
review and manuscript promotion remain open. No fit, Zotero mutation, merge,
push or manuscript change was performed.
