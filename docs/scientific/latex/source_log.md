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

The #152 inventory originally recorded the Matin numerical values as unchecked. Issue #159 subsequently verified all 95 cells against Table S.1. The FPE revision corrects only that verification wording in the manuscript table; it does not regenerate or change the numerical inventory. Regeneration from the older inventory would restore the superseded wording until its source record is reconciled by the data owner. Seven reference labels have no export key and keep an explicit
unavailable-key marker.

- Source-status inventory CSV: `455ed105c408a444e793307856be29eaa5c208ca4251734b9dcecddf95de0bd1`
- Generator: `0880b78373b9e8ffd3b02b8cf9b86403c7ceec50cd42f2ebe94fdf3d2a9adfc7`
- Baseline generated table: `c32ba940160eda83e4c764df7d5a078e518ab81191e6aeac6a10c6fd32feea42`

## FPE text revision, 2026-10-08 (#170)

The owner authorized text restructuring, the two named Zotero acquisitions and bibliography refresh. This revision preserves the numerical results of the previously promoted #154 manuscript snapshot; it does not promote the #160 notebook or incorporate the pending final rerun or heat fit.

- Zotero collection: `8RZP275E` (`mea-thermodynamics`). Exact-DOI and author searches found no duplicates before acquisition.
- Added `YYLHCSG9`, `avlundApplicationAssociationModels2011`, DOI [10.1016/j.fluid.2011.02.005](https://doi.org/10.1016/j.fluid.2011.02.005): Avlund, Eriksen, Kontogeorgis and Michelsen, *Fluid Phase Equilibria* 306 (2011), 31–37.
- Added `QBX24HPH`, `macdowellDynamicModellingAnalysis2013`, DOI [10.1016/j.ijggc.2012.10.013](https://doi.org/10.1016/j.ijggc.2012.10.013): Mac Dowell, Samsatli and Shah, *International Journal of Greenhouse Gas Control* 12 (2013), 247–258. Acquired as requested; not cited because no process-model claim was added.
- Both records are in the approved collection and their title, authors, venue, date, volume and pages match the DOI metadata returned by Crossref. Acquisition stopped before full-text attachment at the Elsevier access check (Avlund) and subsequent publisher cooldown (Mac Dowell).
- The approved canonical Better BibTeX export was previewed and refreshed through Companion; it contains 587 entries without local attachment fields. The manuscript snapshot is regenerated by the existing cited-bibliography script after both auxiliary files contain the revised citations.

Sources actually read for positioning:

| Source and current Zotero identity | Passages read and citation boundary |
| --- | --- |
| Chremos 2016, `CP4EWGIM` / PDF `CB9CSV5I` | Sections 2.1–2.3, 3.6 and 4; species from association fractions, reactive parameters fitted to solubility, species not fitted. |
| Perdomo 2023, `V5E9HBSY` / Markdown `AYPT2IA4` | Sections 2.1–2.3, 4.3.1–4.3.3 and 5, plus Figures 13–14. Current Markdown SHA-256 matches the indexed shelf copy (`459d6498…b249`). Species predictions use association fractions; the primary-alkanolamine interactions use MEA VLE at two isotherms. |
| Lloret 2017, `NXYH6NLG` / PDF `M9UK6V4P` | Sections 2, 3, 4.6–4.7 and 5; reactive association sites fitted to ternary data, concentration transfer assessed. No explicit-ion or fitted-speciation claim added. |
| Najafloo & Zarei 2018, shelf parent `7MICDGGJ` / Markdown `7GCRH2RE` | Sections 2, 3.1–3.3 and 4. Current Markdown SHA-256 matches the indexed shelf copy (`f28f1111…4ef`). Ideal reaction activities, pure-MEA calibration and binary-interaction choices. No accuracy ranking across incompatible observations. |
| Avlund 2011, `YYLHCSG9` | Publisher Introduction and Conclusion preview, and author-institution metadata at DTU. The citation states only the binary MEA–water/hydrocarbon system scope. Full methods and parameter tables remain unread because no PDF was acquired. Publisher preview: [Avlund 2011](https://www.sciencedirect.com/science/article/pii/S037838121100063X). |

The Born and solvent-permittivity equations were compared read-only with Engine main `026b30311b959f1a5db4feef4c15e243f7044a5f`, `engine/docs/equations.md` (`born_outer_shell_diameter`, `born_radial_charging_work`, `born_residual_helmholtz`, `salt_free_solvent_permittivity`) and the selected parameter record's `model_families` / `model_coefficients`: solvent-only bulk mixing, `c_shell = c_dielectric = 1` and fixed ion-region permittivity 8. No equation or result was recalculated. The other fixed inputs in this draft still require the final #160 evidence update.

Observation ranges are counted from `final-rerun/fit-targets.csv` (F1, start A) joined by target identity to `figure-data/pressure.csv` and `figure-data/speciation.csv`. Pressure rows with `kind = packet` identify the fitted pressure states; the same targets also appear among canonical comparisons and must not be counted twice. Counts are 47 pressure states and 94 species targets at 36 species states. The canonical, Wagner and concentration-transfer groups contain 159, 23 and 70 evaluated pressure states. Ranges use observed pressures (Pa converted to kPa) and retained loading, rounded only for display. These are observations and membership counts, not new model results.

Matin verification follows #159: 19 rows × 5 columns (loading plus four species), all 95 values checked against Table S.1 with source rounding. Linked supporting PDF `AWH3TDZ9` belongs to `X5FACKMR`. The owner instructed that the source's 21 °C be treated as equivalent to 20 °C. No input data were changed.

The calibration chronology and exact solution residuals moved to Supplementary Section S6, and calculation paths and hashes to S7. The data statement remains explicitly pending a public deposit or immutable tag. Main and supplement result values, generated numerical tables, figures, submission metrics and the existing caloric limitations await the single final evidence update. This build is a text-review draft, not a submission-ready #160 result snapshot.

Text-build checks: the rebuilt source baseline had 19 main pages and 15 supplement pages; the revised PDFs have 19 and 16. The abstract has 223 words by TeXcount and 231 whitespace-separated tokens in the rendered PDF, both within the 220–240 target. The project bibliography has 72 entries (four added cited records); existing records differ only in the central export's removal of terminal commas. The five highlight lengths are 79, 73, 83, 74 and 77 characters. Final main and supplement logs contain no undefined citations/references, overfull boxes or font substitutions. The banned-language check and Git whitespace check pass. Builds use the existing `cas-sc` / `article` pdfLaTeX configuration and `latexmk`, each heavy job under `agent-heavy --max 3G --timeout 10m`.

The binary-interaction table's prose pointer now identifies Supplementary Section S7. This changes no parameter value. During the final evidence update, the table generator must retain this pointer instead of restoring its older Data and Code Availability wording; likewise the data-inventory generator must retain the #159 verification disclosure. The current task changes manuscript prose only, leaving both numerical generators and all result files unchanged.

Visual checks: all final color pages and the four main figure pages in grayscale were inspected. The automated main report flags two text-overlap errors in mathematical notation (the species residual denominator on page 7 and the AARD sum on page 10); both are false positives on manual inspection. Four equation-rule warnings and tight-clearance warnings reveal no clipping. The supplement has warnings only, chiefly the landscape inventory margins, with no clipped table cells. Reports, rendered pages and the manual disposition are retained under `builds/visual-qa/`. The existing color distinctions in the speciation figure are weaker in grayscale; figure regeneration remains with the final evidence update.

The inventory table after the #159 prose correction has SHA-256 `3db67246a391d32ff4a135dc678405ed2e141409fd341d6dfc4a54436e43b5bc`; the baseline generator output hash above identifies its earlier verification wording.
