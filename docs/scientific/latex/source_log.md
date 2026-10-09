# Source log: manuscript version 1

## Bibliography

`references.bib` holds only the entries cited in the manuscript. It is copied one way from
the central Zotero export `~/Zotero/exports/references.bib` (Better BibTeX), with local
`file` fields dropped. The copy is never edited by hand. To regenerate it after a build:

```bash
python scripts/cited_bibliography.py > references.bib
```

The three hand-kept files `manuscript_references.bib`, `project_sources.bib` and
`official_sources.bib` were removed, as the owner decided on 2026-09-30 (#68).

On 2026-09-30 the Zotero record `Figiel2026Correction` (item `UDSKTAF2`) was corrected with a
version-checked PATCH request to the Zotero local server (`http://127.0.0.1:23119/api/users/0/items/UDSKTAF2`) that the owner approved. The authors changed from
Adam Figiel / Yuan Yu to Paul Figiel, Gangqiang Yu and Christoph Held, and volume 65 and page
7782 were added. The source is the correction PDF (attachment `QS7QHR5L`), p. 7782. The export
was then refreshed with `cse-zotero bibliography-export --apply`.

## Cited sources and their use

| Key | Use and locator |
| --- | --- |
| `matinFacileMethodDetermination2012` | Titration speciation method. Experimental Section and Method Description, pp. 6614–6616; Eqs. 18–19b. The authors report bicarbonate above Jakobsen's NMR values (Fig. 2, p. 6616) and an order-of-magnitude difference from NMR bicarbonate (Fig. 3 and its discussion, p. 6617). Figures are labeled 21 °C. |
| `Bottinger2008` | Online ¹H/¹³C NMR. MEA + MEAH⁺ is observed only as a sum (§3). Pitzer model constants fitted iteratively (§5); VLE comparison (§6). |
| `Jakobsen2005` | NMR bicarbonate and carbonate at 20/40 °C, used for the carbonate-share comparison. |
| `Figiel2025` | SSM+DS Born term, Eqs. 5–10, pp. 9407–9409. Parameter estimation: Born diameters fitted to solvation Gibbs energies at infinite dilution, k_ij to mean ionic activity coefficients at 298.15 K (Model Parameters, pp. 9411–9412). Mixed-solvent predictions, Figs. 6–9. |
| `Figiel2026Correction` | Corrected Eq. 7 (missing bracket; ε_ion in the second term), p. 7782. |
| `Akula2023a` | Electrolyte NRTL for MEA. Joint pressure/heat objective, Eq. 34 (ω_p = 1, ω_h = 0.2). NMR speciation and Cp outside the fit (§4.2). Read from the Zotero PDF `RVYVQKSF/IIYKTEG7`. |
| `Held2014` | Ion parameters from densities and osmotic coefficients; dispersion between unlike-charged ions only. |
| `Uyan2015`, `Wangler2018` | MDEA ePC-SAFT with explicit ions. Prediction from pure-component and binary parameters, one sense of "predictive" that this work does not use. |
| `Baygi2015`, `Najafloo2018` | PC-SAFT and SAFT-HR for loaded MEA, with separate chemical equilibrium. |
| `Gross2001`, `Gross2002`, `Cameretti2005`, `Bulow2020`, `Rueben2024`, `Schick2023` | Lineage of the equation of state and of the permittivity/Born terms. |
| `archerDielectricConstantWater1990` | Water relative permittivity. The manuscript uses the Engine's polynomial approximation (eq. `eq:water-permittivity`), not the full Archer–Wang equation, so no equation or table locator is cited. Zotero item `BWBDFZ6J` (PDF `VII3CVVA`); title, authors, year and DOI 10.1063/1.555853 checked against the item. |
| `Jou1995`, `Hilliard2008`, `Aronu2011`, `idrisSpeciationMEACO2Adducts2014`, `Mamun2005`, `Xu2011` | Pressure observations. Hilliard App. D.4 and Xu Table 1 supply the measured molality and temperature used in calculation. |
| `Amundsen2009` | Loaded-density limitation; Table 3, p. 3097; uncertainty scope pp. 3099–3100. |

Writer A's methods, equation-of-state and table files may add keys; `scripts/cited_bibliography.py`
fails if any cited key is absent from the export.

## Numerical evidence (2026-10-08 numbers pass)

The investigator authorized manuscript use of notebook commit `398c1d3` in this implementation task, subject to #170's reviewed claim limits: calibration for fitted pressure, species, heat and four density states; conditional predictions outside the fit with prior access disclosed; numerical verification rather than physical validation.

The manuscript consumes the adopted heat-augmented record `66ff7715958e9d22e77bd129faf7f67822204e3285b50993bf3f67d72c3b9778`. Engine commit `026b30311b959f1a5db4feef4c15e243f7044a5f`, immutable wheel `94b55dfcf72f21b43010c7125d71f103f41fd56f7a6b6fe0774903eef71cc72a`. The fitting-stage provenance snapshot is `7ad8156`; public deposit/tag remains pending. Numerical files were merged from evidence branch `398c1d3` without conflicts and remain unchanged.

Paths below are relative to `analyses/mea_parameter_bundle/results/heat-final-170/`.

| Manuscript quantity | Retained file |
| --- | --- |
| All 128 old/new entries and paragraph locators | `awaiting-rerun-numbers.csv`; disposition in `docs/scientific/latex/builds/numbers-pass-170.csv` |
| Six heat fits: 149 base or 167 pool targets, costs, AARDs and coordinates | `fit-comparison.csv`; `fit-summary.json`; each selected native-fit file |
| Source/observable AARDs | `evaluation/targets.csv`, restricted to each native-fit target-ID set |
| Conditional errors, correlations and bound gradients | `conditional-uncertainty.json`; `conditional-standard-errors.csv` |
| Outside-fit AARDs and mean log ratios | `evaluation/scores.csv` |
| Carbonate comparison | `evaluation/jakobsen-carbonate-share.csv` |
| Four density-translation calibration states at 0.100 MPa | `corrected-densities.csv`, restricted to 30 wt%, 50/70 °C, loading 0.3/0.4 |
| Uncorrected density comparisons at 101325 Pa, explicitly separate | `evaluation/density.csv` |
| Vinjarapu fitted and Arcis predicted heats; matched no-heat comparison | `heat-comparison.csv`; `figure-data/heat.csv` |
| Separately named Hilliard/Jou packet and canonical pressure cohorts | `high-temperature-comparison.csv` |
| Heat-capacity spot checks | `heat-capacity-comparison.csv` |
| 1,374 current and 375 no-heat equilibrium states, replay/balance residuals | `evaluation/replay-checks.json`; `evaluation/execution.json` |

The 83 pressure/species states and 141 targets remain the #152 corrected basis. Eight Vinjarapu observations bring each base fit to 149; 18 Matin pool values bring F4/F5 to 167. Historical source corrections and fixed reaction shifts retain their existing cited records and are not re-estimated here.

The unavailable ion-free ionic reference prevents the decomposition. Its numerical checks, hypotheses, offsets, activity/speciation interpretations, figure and table are removed. The supported Born claim is the tested refit comparison, 13.81% against 80.25% fitted-pressure AARD. The Matin pool does not reverse the Born ordering. The slope's 107.96 ± 22.93 K uncertainty is conditional, and the heat/high-temperature-pressure change is a trade-off of the parameterization, without a uniquely diagnosed chemistry cause.

## Heat sources read for this pass

The worktree lacks its ignored literature shelf. The existing Zotero PDFs were read directly without changing Zotero or refreshing the bibliography: Vinjarapu (2024), attachment `CE8AP5BM`, Sections 1.1.1, 2.2 and 3.1, Table 4; Arcis (2011), attachment `UAIPQMND`, Section 2.4 and Table 5. These support the integral-heat definition, conditions and observation roles. Prior literature positioning is retained from the approved restructuring; no new literature ranking or molecular mechanism is asserted.

## Presentation and build

`scripts/render_manuscript_figures.py` reads the current retained tables and writes pressure, speciation, pool-effect and heat-of-absorption figures under `figures/generated/`. Model values are discrete markers at measured states; pressures are in kPa, species in mole fraction, and heat in kJ/mol CO2. Rendering evaluates no model. `scripts/final_rerun_tables.py` writes result tables from the same current evidence.

The manuscript build remains `scripts/build_manuscript.sh`; the supplement uses `latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds supplement.tex` from the LaTeX directory. Both run through `agent-heavy --max 3G --timeout 10m`. Final build counts, warnings and visual checks are recorded in `builds/numbers-pass-170.md`.

The data statement remains pending a public deposit or immutable manuscript tag. Independent manuscript evidence/prose review and owner publication remain open.
