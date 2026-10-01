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
| `Jou1995`, `Hilliard2008`, `Aronu2011`, `idrisSpeciationMEACO2Adducts2014`, `Mamun2005`, `Xu2011` | Pressure observations. Hilliard2008 is also the source of the Cp values in the earlier-record deficit. |
| `Amundsen2009` | Selected-record density limitation; Amundsen Table 3 and unloaded control in Table 1. |

Writer A's methods, equation-of-state and table files may add keys; `scripts/cited_bibliography.py`
fails if any cited key is absent from the export.

## Numerical evidence

The manuscript uses owner-promoted evidence at `e80ef4e` for the base record and Born/source-method
comparison, `cc508d1` for the temperature finding, `83ab62b` for interaction and Born-input
sensitivity, and `5dd82bc7` for the selected-record density limitation. The claims concern
calibration, numerical verification and tests outside the present fit; no physical validation is
claimed. Paths below are relative to the repository root, under
`analyses/mea_parameter_bundle/` (**B**).

| Manuscript value | Retained file |
| --- | --- |
| Selected record, SHA-256 `9055458d…cb241`; wheel `28181e72…a97402f2` | B`results/selected-current-best-parameters.json`; B`results/promotion-107-identity.json` |
| 142-target costs 32.991897/34.584032; 160-target re-scores 53.769479/43.623963; 88-target costs 10.471772/16.850037 | B`model-d/born-form-diagnosis/p5conv-costs.csv` |
| Historical 160-target costs 47.625767/40.201537 and group decomposition (7.424230; 11.341018; −1.777157; −2.139631; pool 6.023860) | B`model-d/born-form-diagnosis/key-objective-evaluations.csv`; notebook “Historical full-objective costs” |
| Fitted pressure 13.526616/17.312216 % (48); fitted species 8.284851/8.233650 % (94); 80 °C packet pressure 9.239806/11.208814 % (11); 80 °C species 11.154216/7.359391 % (11); Matin pool 59.813492/35.117599 %, signed −58.838358/−34.299307 %; carbonate ratios 0.423322–1.325562 / 1.207799–3.189248 | B`model-d/assessment-p5a-11-summary.json`, B`model-d/assessment-p5a-00-summary.json` (packet calculation; unaffected by the loading correction) |
| Canonical pressure after the loading correction: 104 rows 20.581177/20.778397 %; 21 rows at 80 °C 20.270257/20.914492 %; the 11 Jou targets 9.239806/11.208814 %; 57 rows at 100–120 °C 26.436267/26.477470 %; per-source values; transfer 75.946385/46.149817 % and 71.495617/46.991021 %; mean ln values | B`model-d/assessment-p5a-loadfix-summary.json`; B`model-d/assessment-p5a-loadfix-comparison.csv`; B`model-d/assessment-p5a-11-loadfix-comparison-scores.csv`; B`model-d/assessment-p5a-00-loadfix-comparison-scores.csv`; B`model-d/assessment-p5a-11-loadfix-transfer-scores.csv` |
| Singular values 1.55013, 1.13411, 0.89865, 0.69831, 0.12531; HCO₃⁻–water gradient −12.4674 | B`results/promotion-107-identification.json` |
| Unavailable probes `vle_obs_0119` (1,0) and `vle_obs_0193` (ε_ion = 2) | B`model-d/born-form-diagnosis/engine-handoff/`; notebook “Unavailable solves and limits” |
| Selected-record density: +13.17/+17.80 % at 50 °C and +12.99/+17.39 % at 70 °C (loadings 0.3/0.4); unloaded control −0.423 % | B`results/density-current-record-123/density.csv` at `5dd82bc7` (issue #123) |
| Historical earlier-record Cp (−9.8 to −14.6 %) | Issue #124, record `868a5018`, wheel `48a639e7…` |
| Inherited R2/R5 reaction shifts estimated partly on 80 °C data (`vle_obs_0206`, `vle_obs_0211`) | Ancestry commit `c369705`; B`results/reaction-temperature-fit/README.md` |

### Canonical loading correction

The canonical request builder (`B/calibration-misfit/probe.py`, old line 60) assigned the nominal
CO₂ loading to neutral CO₂ without subtracting the ionic CO₂ seed. As a result, every one of the
161 canonical and 70 transfer states was 1.0 × 10⁻⁴ mol CO₂/mol MEA too high. The fix is commit
`d8c4cd1` on `work/canonical-loading-offset`, merged before the `manuscript-v1` tag. All
canonical values in the manuscript come from the corrected calculation. After the fix, the 11 Jou
targets at 80 °C give 9.239806 % in both the packet and the canonical calculations; the pre-fix
canonical value was 9.421005 %.

The 57-row 100–120 °C value was recomputed read-only from
B`model-d/assessment-p5a-11-loadfix-canonical.jsonl`, using the scorer's own selection
(`calibration-misfit/compare.py`: rounded °C outside 40–80, first target). It gives 57 rows and
26.43626673522353 % (Original Born: 26.47747014124176 %), identical to the scorer output.

The pressure figure (`pressure.pdf`) was regenerated on 2026-09-30 after replacing the duplicate
request builder with `probe.pressure_observations`. All 161 corrected canonical rows and 78
overlapping packet rows agree with the corrected assessment within the requested 1e-8 relative
tolerance; the per-row comparison and hashes are retained in the figure provenance. The writer
owns replacement of the caption's pre-correction disclosure.

## Figures

| Manuscript figure | Copied file | SHA-256 | Provenance |
| --- | --- | --- | --- |
| Pressure against loading (`fig:pressure`) | `figures/generated/pressure.pdf` | `98ef591000a8d77a96eaad6291cfe5a5bab19394c3064762c8608dc8ee741522` | B`figures/regression_overview/output/provenance.json` |
| Speciation (`fig:speciation`) | `figures/generated/speciation.pdf` | `20d325c76cb08efa3690c9621ecee303f9e3e01df5e18bcae04ddc50f13e8b52` | same |
| Historical cost decomposition (`fig:born-cost-groups`) | `figures/generated/born-cost-by-group-and-species.png` | `2a3bd7afe4fb72a928a3d00027c2bd46b4ee16087e990832038ed67da579451e` | B`model-d/born-form-diagnosis/born-comparison-figure-sources.json` |
| Ranking by target set (`fig:born-ranking`) | `figures/generated/born-p5-ranking-reversal.png` | `2a633b632365893665266b02a129ce7b9c1345348e26d419769476aa4d6bb1e9` | same (`p5conv-costs.csv` hash `472765ae…`) |
| Born-input sensitivity (`fig:born-input-sensitivity`) | `figures/generated/born-input-sensitivity.png` | `1cd3d038f909f8776b38b349512f5a3c6e75946bc04da3d8f6aa8546f46c82c5` | B`model-d/sensitivity-current/figure-inputs.json` at `83ab62b` |

## Supplement data inventory generation (2026-09-30)

The notes in this section are historical build records. The current inventory input is
`source_status_manifest.csv` at main-checkout commit `a349f1a` on
`work/mea-30wt-data-inventory`; on 2026-10-01 regenerating from it reproduced
`tables/supplement_data_inventory.tex` byte for byte. Final publication checks are the
builds reported with the `manuscript-v1` tag, not the preview checks below.

The 34-entry selection and eight columns follow part B of the independent source
inventory review (thread `mea68-supplement-review-1`, timeline position 56).
The corrected manifest is from main-checkout commit
`fdb30b62865b8decf878bc266039353aef9ce718`, on
`work/mea-30wt-data-inventory`. Barzagli's journal locator was checked on Zotero
PDF `VZPDXBT5`, p. 1; the nine legacy extraction labels were reconciled without
changing observation admission. `uv run python scripts/validate_mea_data_library.py`
passed. This table transcribes retained source inventory evidence; it adds no
measurement extraction, model calculation, or physical validation.

Regenerate from `docs/scientific/latex/`:

```bash
python scripts/supplement_data_inventory.py /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/data/reference/MEA/manifests/source_status_manifest.csv /home/tnnrpolley21/Zotero/exports/references.bib
```

The generator reads all coverage, method, basis, count, extraction and caveat fields
from that CSV. It removes extraction/checking workflow receipts from the caveat
cell while retaining source limitations. Long compact source tokens receive
line-break opportunities; no numeric values are rewritten. Reference labels
`Won16c` and `Sob16b` expand to Wong 2016 and Sobrino 2016; their names are
recorded in the retained Wong source file and source-search log, respectively.
Citation keys are matched by DOI against the central Zotero export. Hilliard's
dissertation has no DOI and is matched by title to its supplied export key.
Missing export keys: Park2002, Dugas2009, Arcis2011, Han2012, Concepcion2023,
Karunarathne2020, Sob16b. These rows retain reference labels and DOIs with an
explicit unavailable-key marker. The bibliography export was not edited.

`tables/supplement_data_inventory.tex` contains exactly 34 entries and three
salt-containing markers, with label `tab:s4-data-inventory`. The caption retains
all review disclosures. The table requires `longtable`, `pdflscape`, `array`,
`booktabs`, `xurl` and the manuscript citation package. No other TeX source was
edited by this task; inclusion and preamble assembly remain with the manuscript
writer.

A temporary A4 wrapper with 25 mm margins, LuaLaTeX and natbib compiled using
`timeout 120 env OMP_NUM_THREADS=2 latexmk -norc -lualatex -interaction=nonstopmode -halt-on-error`.
It produced 11 landscape table pages and two bibliography pages, with no
overfull boxes, undefined citations, or missing glyphs. All 11 table pages were
visually inspected; rows and repeated headers fit without clipping.
The CSE `latex_visual_qa.py --profile article --contact-sheet` check completed
text, vector and raster checks. Its 590 warnings are exclusively
`text_near_page_edge`: the detector uses portrait page coordinates for the
rotated landscape content. Inspection of the rendered pages confirms the table
fits the landscape margins. Disposition: keep; scientific logic: exact
transcription of retained inventory fields, subject to their stated caveats.
Preview evidence is retained in `builds/supplement_data_inventory_preview.pdf`,
`builds/supplement_data_inventory_preview.log` and
`builds/supplement_data_inventory_preview_qa.json`.

Generation input/output SHA-256:

- Corrected source manifest: `aa6d9ad4d3b4f6ea2c664c7c57870c6522745cbdbba2969bdaa52a001cf2cfc2`
- Zotero bibliography export: `fdcd9eb08a586485b9deec626613828c29ab1fb68d61d125b4034fd6faf661f9`
- Generator: `647f88486c6dde655cfbf399501ba01e41102e10c2c44b10b229b277b57b2c99`
- Generated table: `7ea50628d71233a882085f3878b68494be46c05ad4415d0760ce0ee147e7fea1`
- Preview PDF: `ce574771466d4129e62815168e78c17c953ff87cf77fd193804b729e7e5db7ff`

### Supplement table formatting correction (2026-09-30)

The generator now preserves source wording and whitespace, including underscores;
it does not insert arbitrary breaks inside words. URLs and reference DOIs use
`\url` with the existing `xurl` package. Break opportunities in long identifiers
and file tokens occur only at `/`, `_`, `.` or `-`; list punctuation permits a
line break between items without inserting or removing a space. The explicit
7 pt table font, column widths and 2 pt cell padding accommodate the manifest's
unspaced prose strings without rewriting them.

Rebuilt the actual supplement using the owner's updated preamble:

```bash
python scripts/supplement_data_inventory.py /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/data/reference/MEA/manifests/source_status_manifest.csv
timeout 600 env OMP_NUM_THREADS=2 latexmk -pdf -interaction=nonstopmode supplement.tex
```

The final `builds/supplement.log` has zero overfull boxes and zero undefined
citations or references. Five generated cells were compared with the manifest
after decoding LaTeX markup: Arcis quantity/method, Arcis observation count basis,
Weiland1998 composition, Amundsen2009 composition, and Jayarathna2013 locator.
All five retain exact wording; the comparison is retained in
`builds/supplement_data_inventory_wording_check.json`. The original Arcis
strings `vibratingtubebinarydensity` and `across15/30 mass%` are already compact
in the manifest; no spaces were invented to repair them.

The seven unavailable-key markers remain unchanged. No bibliography, supplement
preamble or other manuscript text was edited by this correction. No commit was
made. This is a rendering and source-wording check, not new extraction, fitting
admission, or physical validation. The actual supplement replaces the earlier
standalone preview as the rendering evidence.

Corrected artifact SHA-256:

- Generator: `2f515a3b73a50822d5baecf7b2f966b2e906017db47c883d33a316d3c7126059`
- Table: `fb5ea5b154875727dbd77b2958507cc8487484a49baea05f5174021eff2a06b3`
- Actual supplement PDF: `fb886ae299873f80512e6e74f84dc18ef4dc7784b047ebb88782ccb54593d2d8`

The affected rendered pages (5, 10, 11 and 12) were inspected: URLs and
source strings fit their cells. The full-document automated visual report is
retained in `builds/supplement_inventory_qa/report.json`. It flags one
`text_overlap` on page 1 in the existing Born-diameter annotation, outside the
generated inventory table; that source was left unchanged. Landscape page-edge
warnings arise from the detector's portrait coordinates. No table overlap error
was reported. This is not a claim that the whole supplement passed automated
visual acceptance.
