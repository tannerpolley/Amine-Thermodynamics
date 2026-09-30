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
| `Amundsen2009` | Loaded-solution densities in the earlier-record deficit. |

Writer A's methods, equation-of-state and table files may add keys; `scripts/cited_bibliography.py`
fails if any cited key is absent from the export.

## Numerical evidence

The investigator promoted notebook commit `e80ef4e` for manuscript-v1 use. The promoted use
covers scoped pressure prediction and the Born/source-method comparison, subject to the limits
C7–C11 in the #68 design. Paths below are relative to the repository root, under
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
| Earlier-record density (+12.5 to +16.8 %) and Cp (−9.8 to −14.6 %) | Issues #123 and #124, record `868a5018`, wheel `48a639e7…` |
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

The pressure figure (`pressure.pdf`) was rendered before the correction by a separate request builder
(`scripts/generate_figure_data.py:356`). Its caption discloses this, as the owner decided.

## Figures

| Manuscript figure | Copied file | SHA-256 | Provenance |
| --- | --- | --- | --- |
| Pressure against loading (`fig:pressure`) | `figures/generated/pressure.pdf` | `29bec55d4eb02400a32bdee3ef04c2d4a68b1076bcabab29f70f4848af81d45f` | B`figures/regression_overview/output/provenance.json` |
| Speciation (`fig:speciation`) | `figures/generated/speciation.pdf` | `ed501b51165a043d782c6e1cb2e8438fa7f2a291a2370bc234229bc0e3db50a6` | same |
| Historical cost decomposition (`fig:born-cost-groups`) | `figures/generated/born-cost-by-group-and-species.png` | `2a3bd7afe4fb72a928a3d00027c2bd46b4ee16087e990832038ed67da579451e` | B`model-d/born-form-diagnosis/born-comparison-figure-sources.json` |
| Ranking by target set (`fig:born-ranking`) | `figures/generated/born-p5-ranking-reversal.png` | `2a633b632365893665266b02a129ce7b9c1345348e26d419769476aa4d6bb1e9` | same (`p5conv-costs.csv` hash `472765ae…`) |
