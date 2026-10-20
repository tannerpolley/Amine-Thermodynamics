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

## A7 prerequisite presentation and R2/R5 inheritance (2026-10-20, #197)

This section records retained inputs for the prerequisite Build. It does not
update the historical F1 narrative above or begin the manuscript Write stage.
The selected A7 document is
`analyses/mea_parameter_bundle/results/selected-current-best-parameters.json`,
SHA-256 `e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e`.
It is byte-identical to
`analyses/mea_parameter_bundle/results/joint-recalibration-170/amendment-7/restricted-2/fit/usable-budget-endpoint.json`.
The A7 calculation Engine is merged commit
`8298c6029ebb8b467929badc4a223c580ec591ab`, wheel SHA-256
`8897a0caab9f2508ed642f42c8b5226957fbe7035ed7bfdad71e4166798785b3`.
Presentation reads retained values only; no fit, covariance calculation or
Engine evaluation is part of this Build.

Paths starting with `J/` below mean
`analyses/mea_parameter_bundle/results/joint-recalibration-170/`.

### Reaction sources and earlier adjustments

The source owner is
`data/reference/MEA/manifests/chemical_reaction_source_contract.json`,
`reactions` R2/R5 and `common_source_standard_state`. R2 uses Austgen (1991),
Table V, with source coefficients 231.465, −12092.1 K, −36.7816 and zero in
`ln K = a + b/T + c ln T + d T`. Its source-to-common molality offset is
+4.016534992299479. R5 uses Bates and Pinching (1951), equation 7, p.349:
`−log10 K = 2677.91/T + 0.3869 + 0.0004277 T`; its source-to-common offset
is zero. These are the retained, previously adjudicated source declarations;
this presentation Build does not claim a new reading of the papers.

Both `J/amendment-4/matched-larger-dV/control-start-parameters.json` and
`J/amendment-6/inputs/revision-3/held-start.json` serialize R2 a =
235.4815349923, b = −12092.1 K and the source R5 coefficients. Their fit
specifications declare zero inherited R2/R5 enthalpy shifts:
`J/amendment-4/matched-larger-dV/control/stage6-spec.json`,
`information_starts`, and
`J/amendment-6/joint-mea-water/held/fit-spec.json`, `information_starts`.
Thus the older `sources` citations to the September Born/permittivity and
reaction-temperature studies are historical ancestry, not evidence that
those studies' numerical adjustments remain in these starts. In particular,
the old F1 fixed R2 shift is not added to A7.

The earlier fitted adjustments retained in
`J/amendment-4/matched-larger-dV/control/chemistry-coordinates.json` are total
R2/R5 shifts +2719.454475528878 / +2950.799195553639 J/mol and unshifted
R5 A = 2472.3956785580126 K. Its declaration is
`J/amendment-4/matched-larger-dV/control/stage6-spec.json`; objective rows,
scales and data use are those recorded there, including the common pressure,
species and Vinjarapu heat rows and binary/supporting observations.

The A6 totals in
`J/amendment-6/joint-mea-water/held/fit/chemistry-coordinates.json` are
+3417.3298047595786 / +10000 J/mol, with unshifted R5 A = 2400 K.
Its declaration is `J/amendment-6/joint-mea-water/held/fit-spec.json`;
it includes the joint MEA–water Cai observations and removes the five
Amundsen source-conflict rows. These are calibration inputs, not independent
validation of either reaction law.

### A7 start and final totals

`J/amendment-7/design-probes/path-0p125/provenance.json` records the fraction
0.125 interpolation between the retained A4 control and A6 selected records,
including their exact paths and hashes. The R2/R5 starting shifts are the
same interpolation of the preceding totals, +2806.6888916827156 /
+3831.9492961094343 J/mol. The serialized coefficients are retained in
`J/amendment-7/design-probes/path-0p125/fixed-parameters.json` and the
restricted fit start `J/amendment-7/inputs/restricted-start.json`.
`J/amendment-7/restricted/fit-spec.json`, `information_starts`, explicitly
records these inherited shifts; this is not an inferred reset to zero.

| Fit | Inherited R2 / R5 shift (J/mol) | Final total R2 / R5 shift (J/mol) | Final unshifted R5 A (K) |
| --- | ---: | ---: | ---: |
| First restricted A7 | +2806.6888916827156 / +3831.9492961094343 | −1811.8989223397166 / +10000 | 2848.5159752166187 |
| Second restricted A7, accepted | −1811.8989223397166 / +10000 | −1387.404676576437 / +10000 | 2831.6809640586557 |

The first final row comes from
`J/amendment-7/restricted/fit/chemistry-coordinates.json`.
The second start is recorded in
`J/amendment-7/restricted-2/fit-spec.json`, `information_starts`; its parameter
file is `J/amendment-7/inputs/restricted-2-start.json` and it inherits the
first endpoint. The second final row comes from
`J/amendment-7/restricted-2/fit/chemistry-coordinates.json`.
Both fits retain the declared 307-row objective and previously accessed
comparison/acceptance cohorts; the bounds are owner-selected restrictions.
The first fit does not have a full Arcis assessment; its cell is unavailable.

The scientific coordinates are distinct from serialized coefficients.
`analyses/mea_parameter_bundle/results/a7-paper-evidence/fit-summary.json`,
`coordinates` 9–11, reports unshifted R5 A and total R2/R5 shifts. The selected
JSON's R2/R5 `reaction_correlations` already contain their shifts and are used
directly by the reaction table. The retained mapping explanation is in
`analyses/mea_parameter_bundle/results/a7-paper-evidence/README.md`,
“Conditional uncertainty,” and its producer is
`analyses/mea_parameter_bundle/scripts/reduce_a7_evidence.py`, `uncertainty`.
It uses the pivot-preserving R2/R5 transformation; the R5 serialized A equals
unshifted A plus the total R5 shift divided by R ln(10). Neither generator
reapplies the shifts. The inheritance question is resolved by these retained
starts, declarations and chemistry-coordinate records, without a refit.

### F1 density pressure amendment

**orchestrator amendment 2026-10-20: pressure basis disclosed, not matched**.
The orchestrator authorized comparison at each record's retained pressure,
with temperature, loading and unloaded-solvent mass fraction matched exactly.
All 68 F1 rows match A7 on those three keys. F1 native densities come only
from `analyses/mea_parameter_bundle/results/heat-final-170/corrected-densities.csv`,
`eos_density_kg_m3`; the translated column is not used. The corresponding
`density-states.json`, `solved_state.phases[].pressure_pa`, establishes
101325 Pa for all 68 F1 rows, while all A7 Amundsen rows use 100000 Pa.
The 1325 Pa difference is disclosed in the generated table. The historical
100000 Pa description above is superseded for this F1 density file.
Neither retained density record contains a pressure-density derivative, so no
implied density change or bound is claimed. No F1 row is excluded; the 142 A7
rows outside this comparison are listed in the generated provenance comments.

F1 preserves parameter SHA-256
`66ff7715958e9d22e77bd129faf7f67822204e3285b50993bf3f67d72c3b9778`
and original Engine wheel SHA-256
`94b55dfcf72f21b43010c7125d71f103f41fd56f7a6b6fe0774903eef71cc72a`.
The 152-quantity transfer check named in
`analyses/mea_parameter_bundle/results/a7-paper-evidence/predecessor-f1.json`
does not qualify every retained F1 result on the A7 wheel. F1 phase results
are omitted from the generated manuscript and supplement inputs.

A6 density and Arcis assessment values retain parameter SHA-256 `ceefc95cd051fb291e0c08675c4cb6f159bf10dca0116ef1251ba78c243f79c7`, Engine commit `21e761c318c2ac5b555a245365c844d38a93e4cb`, and wheel SHA-256 `d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357`. The paired A6/A7 phase-family classifications were evaluated on Engine `8298c6029ebb8b467929badc4a223c580ec591ab`.
