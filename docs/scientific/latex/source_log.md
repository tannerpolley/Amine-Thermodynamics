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

## Numerical evidence

Every result number in the manuscript and supplement comes from the corrected141 final rerun
(#154), which the owner promoted for manuscript use at `79256a0` on 2026-10-02 (#68), and from the
#152 source corrections. Paths below are relative to `analyses/mea_parameter_bundle/results/final-rerun/` (**R**). The claims concern
calibration, numerical verification and comparisons outside the fit; no physical validation is
claimed.

| Manuscript value | Retained file |
| --- | --- |
| F1 record SHA-256 `ae92bac5…f1aa`; wheel `28181e72…a97402f2` | R`selected-record.json`; R`README.md` |
| Costs, fitted AARDs, coordinates, active bounds and start agreement of F1–F6 | R`fit-summary.json` |
| Fitted-target AARD by source and observable | R`fit-aard-by-source-species.csv`; R`f6-aard-by-source-species.csv` |
| Conditional standard errors, correlations, outward bound gradients | R`conditional-standard-errors.csv`; R`conditional-correlations.csv`; R`conditional-uncertainty.json` |
| Outside-fit AARD and mean ln by group and source (80 °C, Wagner, 100–120 °C, pooled, transfer, Matin pool) | R`evaluation/scores.csv`; R`evaluation/not-evaluated.json` |
| Jakobsen carbonate share; loaded density | R`evaluation/jakobsen-carbonate-share.csv`; R`evaluation/density.csv` |
| Replay residuals and the 1,374 evaluated states | R`evaluation/replay-checks.json`; R`evaluation/execution.json` |
| Pressure decomposition, H1/H2/C statistics, offset fractions and checks N1–N9 | R`activity-contributions/checks.json`; R`activity-contributions/born-off-pressure-decomposition.csv` |
| Pool-effect costs (141 base and 18 pool targets) | R`figure-data/pool-effect-costs.csv` |
| Corrected data: 83 states, 141 targets (47 pressure, 94 species); Xu rows 22–24 not evaluated | `analyses/mea_parameter_bundle/results/source-corrections-152/README.md`; issue #152 |
| Wagner composition and temperature ranges | `analyses/mea_parameter_bundle/results/temperature-reanchor-140/never-accessed-vle-admission.csv` |
| Fixed R2/R5 shifts (−8.2019, +8.4185 kJ/mol): 33 estimation targets (Jou `vle_obs_0206`, `0211` at 80 °C; `0227`, `0228`, `0232` at 120 °C; 22 species; 6 Kim–Svendsen 2007 heats); adoption replay with Xu 2011 held out | F1 record reaction coefficients; `analyses/mea_parameter_bundle/results/reaction-temperature-fit/README.md` (“Revised screen, recenter, full replay, and adoption”), `adoption-receipt.json`, `full-validation-targets.csv` |
| R5 \(A_5\) lowered by 80 K | Fixed-parameter variant `r5am80` in `analyses/mea_parameter_bundle/scripts/run_born_permittivity_study.py`; `analyses/mea_parameter_bundle/results/born-permittivity-study/current-fast-common-comparison.csv`; `analyses/evidence-map.qmd` (R4/R5 row) |
| CO2 dispersion energy 173.44 K selected against 30 wt% pressures at 40–120 °C and species at 20–80 °C | `analyses/mea_parameter_bundle/results/best-in-slot-campaign/final-full-validation-evaluations.csv` (scenario `local-p0.15-db-350-eps+0.025`) |
| ε_MEA = 32 has no retained source (retired `any_solvent.csv`, column `dielc`); water permittivity is the Engine's approximation of the Archer–Wang permittivity (`archerDielectricConstantWater1990`) | F1 record provenance of `component/monoethanolamine/relative_permittivity` and of the water permittivity correlation |
| Reason the two Böttinger 40 °C states and Matin state 016 are not fitted | `analyses/mea_parameter_bundle/calibration-misfit/compare.py` (`EXCLUDED`, commit `e274898`); `data/reference/MEA/manifests/speciation_target_membership.csv` (Matin state 016) |
| Jakobsen 40 °C, loading 0.21 point excluded as out of line | `analyses/mea_parameter_bundle/calibration-misfit/README.md` (carbonate share) |

The result tables (`tables/residual_summary.tex`, `tables/binary_interaction_parameters.tex`
and `tables/supplement_*.tex` except the data inventory) are generated from these files by
`python scripts/final_rerun_tables.py`; their values are not edited by hand.

## Figures

All four figures are drawn by `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py`
from R`figure-data/`, whose CSV hashes the script checks against R`figure-data/input-hashes.json`.
Model values are discrete evaluations at the measured states and are drawn as markers.

| Manuscript figure | File | SHA-256 | Data |
| --- | --- | --- | --- |
| Pressure against loading (`fig:pressure`) | `figures/generated/pressure.pdf` | `ef99f2d42c5f9274b6274f2fa4fcd055a754f633334b31e3f5a9f2b8ecbea705` | R`figure-data/pressure.csv` |
| Speciation (`fig:speciation`) | `figures/generated/speciation.pdf` | `eec5ec497c8755a9862fb907e99e5fef8b430a7cb667d56004e2e0394571b29b` | R`figure-data/speciation.csv`, R`figure-data/pool-effect.csv` (fitted flags) |
| Born-off decomposition (`fig:born-off`) | `figures/generated/born-off-mechanism.pdf` | `ff430c99fb3c88eb66594e9aaa0a0304cc020baf787b2af4e294081db1393a6e` | R`figure-data/born-off-mechanism.csv`, R`figure-data/pressure.csv` |
| Titration pool effect (`fig:pool-effect`) | `figures/generated/pool-effect.pdf` | `b64377cebb5dfd5bb18383f10712b11596b1a972a6b300ffe3e2258f89a26f57` | R`figure-data/pool-effect.csv`, R`figure-data/pool-effect-costs.csv` |

## Supplement data inventory

`tables/supplement_data_inventory.tex` (34 entries, label `tab:s4-data-inventory`) is generated
from the #152-corrected source-status inventory `data/reference/MEA/manifests/source_status_manifest.csv`; its values are not edited by hand. Regenerate from
`docs/scientific/latex/`:

```bash
python scripts/supplement_data_inventory.py ../../../data/reference/MEA/manifests/source_status_manifest.csv ~/Zotero/exports/references.bib
```

The corrected inventory records the Matin 2012 method as checked against the article and its
numerical values as unchecked against the unavailable supporting tables; the generator maps that
evidence level, and curation notes such as pending or unverified fields, to plain statements. Seven reference labels have no export key and keep an explicit
unavailable-key marker.

- Source-status inventory CSV: `455ed105c408a444e793307856be29eaa5c208ca4251734b9dcecddf95de0bd1`
- Generator: `0880b78373b9e8ffd3b02b8cf9b86403c7ceec50cd42f2ebe94fdf3d2a9adfc7`
- Generated table: `c32ba940160eda83e4c764df7d5a078e518ab81191e6aeac6a10c6fd32feea42`
