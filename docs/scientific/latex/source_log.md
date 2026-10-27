## Second mechanical correction round (2026-10-22)

The confirming science and story reports for `ae15c4d` were applied under issue #197. The science definition of the row-scaled residuals used to decide convergence overrides story N7's unscaled-equation wording. The appended Table S2 correction replaces the earlier N8 text. Table changes were regenerated from `scripts/final_rerun_tables.py`; the Figure 2 change is in the caption source.

For N9, the native scope question returned “All N9 records” in Don't Ask mode. The correction therefore covers the ten explicitly listed title records: Neumann's Helmholtz capitalization plus nine H2O/H2S titles, rather than the brief's two-record limit. Only their Better BibTeX `tex.title=` overrides were changed, after inspecting the exact old/new preview. Zotero keys: `MIWSMGMV`, `RVYVQKSF`, `NL4W5CA6`, `E322TKPZ`, `MMI98GID`, `9GBQCJNU`, `VDRXENRB`, `P9HDI8CX`, `UC2KB9PU`, `ZILDPWWE`. The authorized canonical export was regenerated with `cse-zotero bibliography-export --apply`, verified to omit attachment paths, then the cited subset was regenerated with `scripts/cited_bibliography.py` using the preceding build's unchanged citation set. All 54 keys and every non-title bibliography field are semantically unchanged; the exporter adds trailing field commas.

This round changes presentation only. No model calculation or parameter estimation was run. The phase-search claims remain limited to 313.15–333.15 K; the issue #201 files already present on the starting branch were not used or changed. The parent owns confirming review and delivery.

## Review correction round (2026-10-22)

The science review of `703fb86` and the reader review were applied under issue #197's explicit fix-round authority. Science correction 7 overrides story R5: only restricted-bound marker shapes identify single-liquid versus liquid--vapor states. Science correction 8 and story R3 agree on Table S1; the story replacement supplies the complete grammatical sentence. No other scientific conflict was found.

All table edits pass through `scripts/final_rerun_tables.py`; figure edits pass through `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py`. Removing the duplicated inventory renumbers caloric inputs to Section S8, complete inputs to Section S9, ideal calorics to Table S13 and component inputs to Table S14. References follow those changes. The water exponential coefficients keep their values and now use symbols defined in the supplement equation. No #201 result is included.

For story R15, Zotero metadata were previewed and corrected for 33 cited records: 31 Better BibTeX raw title overrides protect chemistry and proper nouns, Bates's title reads “from 0 to 50 °C”, and Chase's place field no longer contains “-1”. The raw overrides use `tex.title=`, following the [Better BibTeX extra-field documentation](https://retorque.re/zotero-better-bibtex/exporting/extra-fields/). The canonical path-sanitized export was regenerated and verified, then `scripts/cited_bibliography.py` copied the cited entries. The project bibliography was not hand-edited. Extra trailing commas reflect the exporter, and other bibliographic fields were checked for drift.

`builds/197-fix-round-numeric-check.json` records the before/after numeric comparison against `703fb86`. The retained parameter and results files are unchanged. Generator guards again reconcile the exact 307 quantities and phase pairs. This is a correction of reviewed presentation, without a fit, model calculation or new scientific claim. The parent owns the confirming review and delivery.

# Manuscript sources and numerical provenance (#197)

## Current revision (2026-10-22)

The current draft implements the merged referee plan with retained results only. The investigator promotion and scientific parameter identities below are unchanged. The historical entries below document the preceding draft; statements about unchanged presentation generators, historical inventory or six-fit tables are superseded by this revision.

- Names: original-bound fit (A6), restricted-bound fit (A7), reference fit (F1). The paired 73-state phase evidence remains limited to 313.15–333.15 K. No results from issue #201 are used.
- R5 verified directly against Bates and Pinching, Zotero parent `TAE3BGEB`, PDF `A9H4U73D`, Eq. 10 and Table 2, printed p.351; and Böttinger PDF `TJCRKTFQ`, Table 5, printed p.138. The source equation is pK = 2677.91/T + 0.3869 + 0.0004277 T. At 298.15 K source/fitted pK are 9.4961729056/10.0958410589 (difference +0.5996681533); at 313.15 K they are 9.0723590834/9.5634047933 (difference +0.4910457099). At 313.15 K dissociation enthalpy from R ln(10)(A − C T²) is 50.46497796/63.40888580 kJ/mol. The serialized coefficients already contain the +10 kJ/mol total shift. The unshifted reciprocal-temperature coefficient also changes; the departure is not the shift alone. Table 2 reports temperature-specific experimental deviations, not a uniform ±0.0014 pK uncertainty. The source declaration is preserved unchanged, including its obsolete Eq. 7 locator; only presentation is corrected.
- Literature additions checked in the actual sources: Zhang PDF `M3QDCZM7`, Tables 9–11 (species deviation 35.7%, not 5.7%); Baygi Table 5 and Table 3; Nasrifar Table 2 and Eq. 12; Najafloo Table 5; Akula PDF `IIYKTEG7`, Section 4.2; Lloret PDF `M9UK6V4P`, Section 4.7; Téllez-Arredondo PDF `562Y8VTS`, Tables 5 and 8 (electrolyte cubic two-state association, not ePC-SAFT); Neumann PDF `G3U3WRF8`, Section 4.2; Hessen PDF `PMT4R63N`, Sections 3–4 and Table 2; Aronu PDF `W2NNU9H6`, Sections 3–5, Tables 7–10, including its appended correction. Parameter counts are stated only where established.
- The phase algorithm and numerical-error formulas were read from Engine commit `8298c6029ebb8b467929badc4a223c580ec591ab`, `engine/native/equilibrium/phase_stability.cpp`, and its documented algorithms. This was a read-only source inspection; no Engine calculation ran. Fixed reference pressures are defined from the retained state grid with ratios 0.50/0.80/0.95; the historical calculation that first produced those reference pressures is not traced. The manuscript identifies them as design inputs and supplies their exact states, rather than claiming they are current bubble pressures.
- New table inputs: density scales and source differences from `J/amendment-6/inputs/without-amundsen-0p4/density-scales.json` and `J/amendment-6/density-sweep-1b/summary.json`; neutral calorics from `data/reference/MEA/thermal/physical-ideal-gas-calorics.json`; original bounds from `J/amendment-6/joint-mea-water/held/fit-spec.json`. Pure-water fitting details come from `J/stage3/qualification/water-spec.json`, its assessment and `results/water-124/lambda-0.1-A/assessment.json`. Permittivity branch ambiguity and fitting observations come from the retained stage-5 estimates. The exact data are preserved.
- The 210 density observations and 73 paired phase states are supplied as CSV in the staged deposit. The supplement prints source summaries, confirmed splits and a 10 by 10 lower-triangular correlation matrix. The obsolete inventory and six-fit history are removed. All table changes pass through `scripts/final_rerun_tables.py`; all figure changes through `render_manuscript_figures.py`.
- Availability follows the authorized Zenodo plan: DOI added at submission and restricted Engine wheel access for referees. No DOI is invented and nothing is published. The staged deposit README contains hashes, software identities and reproduction commands.
- The local bibliography is refreshed only through the existing approved script and existing central export, after both auxiliary files exist. Existing-entry metadata are copied unchanged; capitalization corrections requiring central metadata changes are deferred. No Zotero mutation or central export refresh is performed.
- Numeric changes and executable additions are recorded in `builds/197-revision-numeric-check.json` and its Markdown explanation. The parent conducts the independent scientific and reader reviews after delivery.

## Preceding-draft evidence record (2026-10-20)

The investigator promoted notebook commit `8f40c125e5945ac785cc0ad1889fc79bea2096c9` and the accepted A7 endpoint `e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e` for the joint-calibration and finite-phase-test manuscript, subject to the density failures, finite state domain, single-start/local-fit, conditional-error and prior-data-access limits in issue #197.

## Numerical sources and identities

`E/` means `analyses/mea_parameter_bundle/results/a7-paper-evidence/`; `J/` means `analyses/mea_parameter_bundle/results/joint-recalibration-170/`. The selected parameter JSON is `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json`, byte-identical to `J/amendment-7/restricted-2/fit/usable-budget-endpoint.json`. Its SHA-256 is `e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e`.

A7 uses Engine commit `8298c6029ebb8b467929badc4a223c580ec591ab`, wheel SHA-256 `8897a0caab9f2508ed642f42c8b5226957fbe7035ed7bfdad71e4166798785b3`. The paired phase-family classification comparison uses this same Engine for A6 and A7. A6 density, Arcis and separate split-confirmation results retain their original Engine identities below. F1 retains its original wheel; no historical result is relabeled as an A7-wheel calculation.

The fourteen generated numerical tables come from `docs/scientific/latex/scripts/final_rerun_tables.py`; five A7 figure pairs and `figures/generated/provenance.json` come from `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py`. The delivered r2 review supported these inputs. Write did not edit their files, generators or retained evidence, and ran no Engine calculation. The obsolete pool-effect figure is not included.

| Displayed quantity | Retained source and field |
| --- | --- |
| 16 coordinates, bounds, ties, signed transformations and values | `E/fit-summary.json`, `coordinates`; `E/conditional-standard-errors.csv`, scientific coordinate rows |
| 307 rows; total cost 148.905254; common149 cost 23.865964; 47/94/8 common subgroups | `E/README.md`, objective reconciliation; `E/fit-summary.json`, `cost`, `groups` |
| Pressure/species AARD 11.86/7.10% (11.8608/7.1036% in results) | `E/fit-summary.json`, `groups.common149 pressure/species.AARD_percent` |
| Eight group operators, scales, weights; loaded 1/47, CO2-free 0.5 kg/m3 and weight 10, Cai 1 K/0.01, Kiepe 1/39 | `E/fitted-rows.csv`, `form`, `scale`, `weight`, `declaration`; generated `tables/objective_groups.tex` |
| Cai native-unit RMSE/bias and approximate 62% cost share | Generated `tables/residual_summary.tex`, Cai rows; `E/fit-summary.json`, Cai cost 91.9077547440675 and total 148.90525398237165; cost share rounded to integer percent as required in #197 |
| Kiepe cost approximately 0.0007 | `E/fit-summary.json`, `groups.Kiepe.cost` |
| 44/47 densities; all three named failures; 0.40–0.53% low | `E/density.csv`, IDs Amundsen2009_state_081 and Hartono2014_density_80C_alpha0.29/0.39, errors/scales; `J/amendment-7/restricted/README.md`, second-restricted-fit limits |
| All 210 density rows; all 103 Amundsen rows at A7 100000 Pa; other pressures remain row-specific | `E/density.csv`, all records, `source` and `P_Pa`; Han2012 high-temperature rows include 700000 Pa, so the Amundsen convention is not generalized |
| All ten carbonate shares, mass fraction 0.27142748, mean ratio 0.07305 and range 0.00633–0.26703 | `E/carbonate-share.csv`, all ten records; `E/summary.json`, `carbonate_share` |
| All 19 Matin pools, AARD 67.4808%, log ratio −1.26582 | `E/pool-figure-data.csv`; `E/state-summary.json`, Matin pool cohort |
| Vinjarapu 1.83486, Arcis 8.11440 RMSE and +7.18190 bias; pressure-separated RMSE 10.3310/3.36566 kJ/mol CO2 | `E/heat.csv`; `E/summary.json`, `heat`, pressure groups; generated residual table |
| Four Cp errors +5.534/+2.567/+1.150/−2.135%; 318.15/353.15 K, nominal loadings 0/0.358, 101325 Pa and 7 mol/kg | `E/cp.csv`; notebook `Density and heat capacity`; generated residual table |
| Canonical 159-pressure AARD 20.5537%; Wagner 22.2026/9.2542%; transfer 29.5070/56.0168% and signed log ratios | `E/state-summary.json`, named cohorts; generated `tables/supplement_outside_fit.tex` for objective-excluded rows; full canonical statistic is not the 112-row excluded subset |
| Canonical/packet high-temperature 24.3499/27.5380%, 54/20 rows | `E/high-temperature-comparison.csv`, first two data rows |
| 73 paired phase states, 657 trials, A6 12 descent points, A7 zero; 69 two-phase/four single-liquid A7 states | `E/phase-family.csv`; `J/amendment-7/restricted/README.md`, second endpoint; generated phase table |
| MEAH size probes 5.49/5.45/5.40/5.35 Å and 44/44/22/7 of 47; first/accepted worst 2.70/2.43s | `J/amendment-7/restricted/README.md`, size probe and second fit; `J/amendment-7/fixed-study/wheel-8298c602/size-probe/` |
| Hartono x3 own-basis 44/47 and cross-basis 40/47 | `J/amendment-7/restricted/README.md`, Hartono x3 sensitivity; `J/amendment-7/restricted-2-x3/` |
| Ten free/rank ten, six at bounds, 297 degrees of freedom, variance factor 1.002729 | `E/README.md`, conditional uncertainty; `E/conditional-uncertainty.json` |
| Bicarbonate-water 0.7253 ± 1.2671; R2 −1.4 ± 5.3 kJ/mol; MEAH-water −41.93 ± 60.29 K (also rounded −42 ± 60 K) | `E/conditional-standard-errors.csv`, corresponding coordinate rows |
| 375 states; residual bound 2.2e-12 and detailed residuals | `E/verification.json`, `state_numerical_checks` |
| 153-identity replay; 8.39e-16 relative difference | `E/default-replay/summary.json`, distinct count and worst relative difference |
| F1 comparable common149 metrics, untranslated 68-row density baseline and pressure difference | Generated `tables/supplement_predecessor.tex`; `E/predecessor-f1.json`; `heat-final-170/corrected-densities.csv`, only `eos_density_kg_m3`; release README, Density comparison amendment |
| Predecessor F1–F6 numbers | Unchanged `heat-final-170/fit-comparison.csv`, `with heat` rows; generated `tables/supplement_fits.tex`; no F1 phase result is used |

A working sentence/cell list with precise source line locators is retained in `builds/197-displayed-number-sources.md`. It lists generated table cells by their generated source line, whose provenance comments identify raw inputs and hashes; prose rounding is stated beside its source. Chemical subscripts, equation numbers, bibliography years and software hashes are identities rather than measured values.

## Literature read and source checks

The main checkout's ignored `literature/README.md` and `index.csv` were read. Indexed raw-source SHA-256 and Markdown-output SHA-256 values were checked on their distinct declared bases against the current Zotero files and reading copies; no drift was found. The reading shelf itself was not edited. Source PDFs were read where no local Markdown was available, without Zotero writes or conversion services.

| Source | Passages used and source identity |
| --- | --- |
| Zhang2011 | Zotero parent `MMAGNPIH`, PDF `M3QDCZM7`; §§2.1–2.4, 3.1–3.3, Tables 6, 9 and 10, pp. 68–74. Liquid electrolyte NRTL and PC-SAFT vapor; binary and ternary multi-property fitted roles. No independent prediction or accuracy ranking is inferred from the word “predicted” in the paper. |
| Nasrifar2010 | Parent `CBRPAXQG`, Markdown `FVFWT3P9`, PDF `3G4FGGY4`; §§3–4, 6–7, Tables 2–3. Ideal reaction activities, effective water containing ions, pure/binary parameter use and loaded-solubility comparisons. |
| Najafloo2018 | Parent `7MICDGGJ`, Markdown `7GCRH2RE`; §§2, 3.1–3.3 and 4, Tables 1–5. Methods use pure-MEA calibration, imported CO2–water interaction and zero other binary coefficients, whereas the conclusion describes broader ternary data use. That ambiguity is preserved; it is not resolved by inference. |
| Lloret 2017 | Parent `NXYH6NLG`, PDF `M9UK6V4P`; §§4.4–4.7 and 5, Table 5, Eq. 26, Figs. 9–11, pp. 527–531. Reactive association is fitted to ternary data; heat is estimated from the pressure–temperature derivative, with stated underestimation and no calculated temperature dependence; concentration transfer is a separate test. |
| Yang2024 | Parent `LQMTYLCE`, PDF `PELWE2BT`; §2.1, Eqs. 1a, 2a and 2b, PDF p.4. Supports only the Schreckenberg functional form and solvent-number averages. A7 coefficient values, branch choice and qualifications come from its own selected record and retained stage-5 evidence, not from this paper. |
| Böttinger2008 and Jakobsen2005 | Current hash-verified Markdown; Böttinger §3 and §§5–6, Table 3, pp. 134–142; Jakobsen calibration experiments, pp. 9895–9896 and Tables A1–A2. Aggregate NMR observations, chemical-shift separation and fitted reaction constants. |
| Baygi2015 | Hash-verified Markdown `ICDS2PAA`; §3 parameter estimation, Eq. 6, Tables 2–3, and ternary ideal-speciation methods/results. Existing literature-table row retained on that support. |
| Akula2023a | Parent `RVYVQKSF`, PDF `IIYKTEG7`; Eq. 34 and §4.2: joint pressure/heat objective, speciation and Cp outside fitting. |
| Uyan2015, Wangler2018, Cleeton2020 | Hash-verified Markdown `9C7EACSK`, `RIUUBS2B`, `IEBNHBR2`; parameter-estimation and results passages, including Uyan solvent/ion treatment, Wangler Eq. 33 and water–MDEA–HCl osmotic data, Cleeton binary-parameter construction and competitive acid-gas results. The rows retain their own fitted/predicted roles, not a common assessment domain. |
| Figiel2025 and 2026 correction | Hash-verified main Markdown `2M74BKJG`, Model Parameters and Eqs. 5–12; correction PDF `QS7QHR5L`, p.7782, corrected Eq. 7. Born equation checked against the correction. Scope is ions in the paper's single/mixed solvents; transfer to loaded MEA is a model assumption. |
| Perdomo 2023 | Hash-verified Markdown; §§2.2–2.3 and 4.3.3, Tables 6–7, Figs. 13–14. Primary alkanolamine–CO2 parameters fitted at the stated two MEA isotherms; species are association-derived comparisons. |
| Chremos 2016 | Parent `CP4EWGIM`, PDF `CB9CSV5I`; §3.6, Figs. 11–12, pp. 290–292. Existing SAFT-gamma square-well row checked against reactive association fitting and speciation comparisons. No shelf copy was available, so the live Zotero PDF was used. |
| Bülow2021a | Hash-verified Markdown; ePC-SAFT model and pure/binary parameter sections, Tables 1–3. Born inclusion and reduced binary-parameter use in its specified MDEA blends. |
| Vinjarapu and Arcis | Vinjarapu PDF `CE8AP5BM`, §§1.1.1, 2.2, 3.1 and Table 4; Arcis PDF `UAIPQMND`, §2.4 and Table 5. Integral finite-addition heat, source conditions and declared heat intervals; no isolated heat-fitting effect is claimed. |

The other unchanged literature-table rows retain their existing source support; published accuracy statistics are not ranked. Exact numerical transcriptions in generated tables remain bound to the selected parameter document and declared source observations. The retained-inventory inconsistency is disclosed in S8: its Hilliard “not extracted” note and F1-only Amundsen pressure convention are superseded by immediately preceding A7 corrections, while the generated inventory and its generator remain unchanged.

## Bibliography

The owner-approved local refresh uses only `python scripts/cited_bibliography.py > references.bib` from this directory after main and supplement builds have written their `.aux` files. It reads the existing `~/Zotero/exports/references.bib`; no central export or Zotero record is modified. The snapshot is never hand-edited. Yang2024 is added only for the equations actually read. The final diff adds `Yang2024` and removes `Held2008` and `archerDielectricConstantWater1990`, following the rewritten citations. All other entry text is unchanged: no existing-entry field drift and no local `file` fields.

## A7 release and review state

The A7 DOI remains pending. Local staging is `tmp/joint-design/a7-data-release/`, with README, SHA256SUMS, file roles, exact identities and reproduction commands. The existing F1 DOI `10.5281/zenodo.23323107` and tag `manuscript-fpe-v1` are historical; neither is presented as the A7 release. This writing task authorizes no publication, Overleaf sync, push or submission. The two manuscript reviews and owner review remain open after this Writer handoff. Historical readiness ticks do not certify the rewrite.

## R2/R5 inheritance and F1 density pressure basis

### Reaction sources and earlier adjustments

The source owner is
`data/reference/MEA/manifests/chemical_reaction_source_contract.json`,
`reactions` R2/R5 and `common_source_standard_state`. R2 uses Austgen (1991),
Table V, with source coefficients 231.465, −12092.1 K, −36.7816 and zero in
`ln K = a + b/T + c ln T + d T`. Its source-to-common molality offset is
+4.016534992299479. R5 uses Bates and Pinching (1951), Eq. 10 and Table 2, p.351:
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

## Issue 197 reframe, 23 October 2026

The owner-approved reframe and writer brief promote the notebook at `59c8d9067ffe62733707775a7e6a5e20e46740c6` (included in base `d578555`) for the equilibrium-property manuscript, subject to its fitted/comparison roles, unresolved property discrepancies and finite 313.15–333.15 K phase domain. This continues the adoption and manuscript-use authority recorded in #196 and adds the #202 fixed-parameter curves explicitly authorized for this rewrite. No new model evaluation or parameter estimation was performed.

The accepted plan is [the 23 October reframe comment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/197#issuecomment-6359283213). Its complete checklist, current displayed-number evidence, build commands, hashes and page inspection are retained under `builds/197-reframe-*`. The bibliography snapshot is unchanged. The local literature shelf is in the main checkout rather than this worktree; relevant indexed companions were compared with their current Zotero-storage files. Zhang (2011) Tables 9–11 and Neumann (2022) Section 4.2 were also read directly from their existing local PDFs. No Zotero or bibliography write was made.

The 2.32% amine-sum deviation covers 25 comparisons, including 20 fitted observations; the fitted-only value is 1.72%. The Han mean density errors in the rewrite refer to five loaded 30 wt% observations at each temperature, excluding the zero-loading value. All 67 Han observations remain outside the objective. Binary dashed lines denote the vapor branch; dashed species/density curves denote single-liquid states imposed below their own bubble pressure. These distinct meanings are stated in the captions.

## Issue 211 one-wheel numbers, 26 October 2026

The owner, acting as investigator, promoted the results of #212–#215 for manuscript use on 2026-10-26 ([#211 comment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/211)): the adopted record `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`, the package `analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/`, the density-free limits and the 162-state phase search, subject to their stated limits: calibration statistics and finite-search numerical verification, not physical validation, global stability or process qualification.

Every generated table and figure now reads these files through `analyses/mea_parameter_bundle/scripts/a7_presentation.py`, which checks each bound input against the package's `inventory.json` or `input-hashes.json`. Prose numbers were recomputed from the same files; the ones that changed are:

| Displayed value | Source |
| --- | --- |
| Per-source pressure AARD 9.43/18.57/19.36% (Hilliard, Ma'mun, Jou) | `canonical-pressure.csv`, grouped by `source` |
| Wagner 22.19/9.27%; 15 wt% log bias −0.205; Matin pools 67.46%, −1.265 | `state-summary.json`, named cohorts |
| Matin carbamate 8.09%; carbonate-share mean 0.0727, range 0.00629–0.266 | `species-figure-data.csv`; `carbonate-share.csv` |
| Vinjarapu RMSE 1.84 kJ/mol (1.83501); Arcis 1.03 MPa bias +3.15 | `summary.json`, `heat` |
| Hartono 0.39 error −4.40 kg/m³; Han maximum −20.01, 1037.59 calculated | `density.csv` |
| Comparison-fit MEAH⁺–water $k_{ij}$ +0.026 | `comparison-parameters.json` |
| Residual checks 2.16e-12 / 8.60e-13 / 2.11e-13 | `verification.json`, `state_numerical_checks` |
| Loaded-density cost 0.565; Cai 91.87 of 148.88 | `fit-summary.json`, `groups` |
| Bicarbonate–water 0.727; MEAH⁺–water slope −41.6 K | `conditional-standard-errors.csv` |
| Eight iterations, function tolerance | `../engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/native.json` |
| MEA association volume 0.036305439, least squares to Baygi's model at 21 temperatures | `../engine-3e83e19c-association-volume/README.md` |
| Constant-interaction Cai $k_{ij}$ −0.084399862, cost 91.29 | `../engine-3e83e19c-refit-chain/stage2/run/selection.json`; `refit-display-summary.json` |
| Phase grid, reference pressures, counts and 51 confirmed splits | `../engine-3e83e19c-phase-search/run-2/` |
| Parameters printed to eight significant figures give the `tab:residual-summary` statistics at printed precision; largest relative prediction change 2.8e-6 (7: 1.9e-5, 6: 2.0e-4, 4: 4.2e-2) | `../engine-3e83e19c-paper-evidence/parameter-rounding/summary.json`, `replay-*.csv`; full-precision replay equal to `full-replay.json` in all 307 rows |

The eight-significant-figure sentence in the parameter-fitting subsection of the data and parameter-estimation section is restored from `parameter_rounding_sensitivity.py`, rebound to record `00e77608…`, the restricted-2 specification and the retained replay; the earlier-record result `results/parameter-rounding/` (`e234e860…`) is unchanged.

## Issue 211 Part 2 story pass, 26 October 2026

The owner-approved merged edit plan of 26 October 2026, based on `ac073b8`, authorizes A–H and O-C, O-D, O-L and O-W. This pass changes the planned prose, its cross-references and the generated presentation only. The investigator promotion recorded above for #212–#215 supplies the evidence and claim limits: fitted/comparison statistics and finite-search numerical verification, without physical phase validation or process qualification. No model calculation, parameter estimation, source-library edit or bibliography refresh was made.

### Changed spans

Paths below are relative to this directory unless otherwise stated. Existing paragraph identifiers are retained, including the moved `results-scope-01` and reordered `results-phase-01`/`results-phase-02`.

| Plan item | Changed span and outcome |
| --- | --- |
| A | `main.tex`, `abstract-01`: added the 0.51 MPa Arcis discrepancy and specified loaded densities; `sections/conclusion.tex`, `conclusion-01`: replaced the opening claim and added the complete discrepancy sentence; `conclusion-02`: replaced the future-work sentence. Done. |
| B | `sections/mea_system_modeling_results.tex`, `results-scope-01`: removed the two repeated formulation sentences, replaced the domain claim with assessment and extrapolation limits, and moved the whole block after the literature table as subsection 4.7. Added the 162-state sentence with a phase-section reference. Done. |
| C | `sections/data_methods.tex`, `methods-03`: stated the development role of the 112 non-fitted six-source pressures and distinguished comparison from acceptance limits; retained the citations and replaced the blind-test sentence. `abstract-01` and the generated present-work row state the same development role. Done. |
| D | `abstract-01` and `conclusion-01`: changed the published-range comparison to the 159-pressure statistic after checking Table 6. Done. |
| E | `results-phase-02` and `supplement.tex`, `supplement-phase-confirmation-01`: replaced the experimental-counterpart statements with the approved sentence about Neumann's homogeneous-liquid comparisons; retained its Section 4.2 citation. Schick's distinct experimental observation remains. Done. |
| F | `conclusion-02`: specified three of the 47 fitted loaded densities outside twice the assigned scale; `supplement-acceptance-01`: added the approved sentence explaining that the loaded-density requirement records the three misses. Done. |
| G | `results-phase-01`: replaced the local-optimum claim with the approved local bounded least-squares limitation. Done. |
| H | `submission/chemrxiv.md`: synchronized the final abstract; `submission/cover_letter.md`: synchronized pressure, heat, density and phase results, limits and development roles; `submission/highlights.txt`: replaced highlight 5. Replaced the prohibited calculation-command wording in the ChemRxiv availability paragraph. Done. |
| O-C1 | `sections/introduction.tex`, `introduction-04`: replaced the contribution and relative-contribution sentences; `abstract-01`: added the approved contribution sentence and used the explicitly permitted shorter separate-fit sentence. Done. |
| O-C2 | Moved the first sentence of `results-phase-03`, with all citations, into `introduction-04` immediately before its final sentence. Done. |
| O-C3 | Moved the tangent-plane criterion, equation `eq:tpd` and explanation to the end of Methods as `methods-phase-01`; inserted the Methods/S8 reference and reordered subsection 4.5 to grid, wider-bound result, restriction and cost, and the closing observation. Done. |
| O-C4 | `results-phase-01`: added the active-bound/density trade-off and replaced the 47/47-to-44/47 sentence; `results-phase-02`: added the confirmed split compositions; `methods-heat-03`: appended the density/phase/reaction parameter connection. Done. |
| O-D1 | New `results-scope-02`: inserted the approved R5 offset, six-of-16 active bounds, compensation and interpretation limits. Done after checking the adopted record. |
| O-D2 | New `results-scope-03`: combined high-temperature evidence and the R4/R5 source limits; abstract ending now refers to absorber and stripper temperatures. Adapted the quoted density clause to identify Han's loaded 30 wt% observations and the mean errors at 373.15–393.15 K; 0.7–1.2% describes those means, rather than every density. |
| O-D3 | `abstract-01` and `conclusion-01`: inserted the approved pressure ranges and the shared species subset range, combining the abstract development-role edit from C. Done. |
| O-D4 | `abstract-01`: added the density denominator, 44 values within twice the assigned scale and three accepted misses at 353.15 K. Done. |
| O-L1 | `scripts/final_rerun_tables.py`, present-work row: now computes and prints fitted pressure, shared species count/deviation, integral-heat RMSE and loaded-density count/deviation from retained evidence; the comparison note gives the 112 development observations. `results-literature-01`: inserted the approved Zhang/Neumann comparison immediately after the original data-role sentence. Done; the generated table uses the size adjustment described below. |
| O-L2 | Same generator, literature-table caption: inserted the approved parameter-count qualification. Done; the additional caption and row text required a table-size adjustment. |
| O-L3 | `introduction-03`: inserted the approved Uyan and Wangler sentences with existing bibliography keys. Done. |
| O-L4 | `introduction-01`: replaced sentence 2 with the approved driving-force, species, energy-balance and density sentences. Done. |
| O-L5 | `introduction-02`: replaced the Helmholtz-energy contrast sentence. Done. |
| O-W1 | Renamed displayed fit text in Methods, Results, Conclusion, supplement, table captions/headers and figure captions/panel titles to wider-bound fit. Internal filenames, labels, record keys and variables are unchanged. The phase paragraph now calls the S10 limits acceptance limits. Done. |
| O-W2 | Deleted the repeated domain recap, the separate-fit conclusion recap, the closing validation clause in `results-phase-03` and the final Figure 9 caption sentence. One finite-search qualification remains in subsection 4.5 and one in the conclusion. Done. |

### Verified numbers and sources

All evidence paths in this table are under `analyses/mea_parameter_bundle/results/`. These are reductions or checks of promoted retained values, not new analyses.

| Quantity checked | Value and retained source |
| --- | --- |
| Fitted pressure | 47 observations; AARD 11.8625628140%, printed 11.86%; `engine-3e83e19c-paper-evidence/fit-summary.json`, `groups.common149 pressure`. Matching `canonical-pressure.csv` targets span 313.00–333.15 K. |
| Complete pressure comparison | 159 observations; AARD 20.5521214768%, printed 20.55%; `state-summary.json`, `scores.canonical`, and `canonical-pressure.csv`, spanning 313.00–393.15 K. Subtracting the fitted 47 gives 112 non-fitted observations. |
| Shared fitted species | 94 fractions; AARD 7.10284218155%, printed 7.10%; `fit-summary.json`, `groups.common149 species`. Matching targets in `species-figure-data.csv` span 293.15–333.15 K. |
| Fitted heat | Eight Vinjarapu integral heats at 313.15 K; RMSE 1.83500986475 kJ/mol, printed 1.84; `summary.json`, `heat.Vinjarapu2024`, and `heat.csv`. The former submission abstract's 1.83 is stale. |
| Fitted loaded density | 47 observations; AARD 0.176969446814%, printed 0.18%; `density.csv` restricted by `engine-3e83e19c-refit-chain/restricted-2/attempt-3/spec.json`, `loaded_density_ids`. Exactly 44 within twice the assigned scale. All three misses are low at 353.15 K: Amundsen loading 0.3 and Hartono loadings 0.29/0.39. The wider-bound fit has 47/47 within twice the scale (`comparison-score.json`). |
| Concentration transfer | 33 observations at 15 wt%: 29.4878365654%, printed 29.5%; 37 at 45 wt%: 56.0373635609%, printed 56.0%; `state-summary.json`, `scores.transfer 15 wt%` and `scores.transfer 45 wt%`. The current abstract and plan agree. |
| Published pressure range | Table 6 reports related-model CO2 pressure deviations from 12.5% to 112% (and 11.7% for total pressure); the present 20.55% lies within either range. These statistics use different data sets and roles. Zhang Table 9 directly confirms 13.5–35.5% for fitted sources and Table 11 confirms the additional-source range. |
| High-temperature pressure | 54 six-source observations at 100–120 °C: 24.3476287870%, printed 24.35%; `high-temperature-comparison.csv`, `canonical 100-120 C`. |
| CO2–water maximum low pressure | −11.3361183453%, printed −11.3%, target `kiepe-393.17-07`, at the isotherm displayed as 393.2 K; `fitted-rows.csv`, `group=Kiepe`. |
| Han loaded-density means | Five loaded 30 wt% observations at each temperature: −0.721870800161% at 373.15 K and −1.19629859624% at 393.15 K, printed 0.7–1.2% low; `density.csv`, `source=Han2012`, `mea_mass_fraction=0.3`, positive loading. The corresponding 353.15 K mean is −0.433194052296%. |
| R5 and active bounds | Adopted R5 coefficients give an offset of +0.491307769667 pK at 313.15 K from the source coefficients 2677.91, 0.3869 and 0.0004277; `reported-parameters.json` and `source-only/chemical_reaction_source_contract.json`. Six active coordinates among 16, `fit-summary.json`, `active_bounds`. R4/R5 source upper temperatures are both 323.15 K; the R5 enthalpy shift is at +10 kJ/mol. |
| Phase grid | 162 states per fit, six temperatures 313.15–393.15 K, nine loadings from 1e-5 to 0.6 and three pressure fractions; `engine-3e83e19c-phase-search/run-2/phase-family.csv`, `counts-by-temperature.csv`, and `reference-pressures.csv`. The wider-bound fit has 54 resolved-descent states and the reported fit zero; nine trials per state give 1458 optimizations per fit. |
| Confirmed two-liquid compositions | 51 confirmed paths at 32 of 54 descent states; water-poor liquid water fraction 0.402875114547–0.739470616430, printed 0.40–0.74; water-rich 0.675096586314–0.974908506943, printed 0.68–0.97; `split-confirmations.csv`, confirmed rows, sorting the two liquid water fractions for each path. |
| Fitting-cost change | Reported 148.878939345574 versus wider-bound 148.211507590408; increase 0.450323841932%, printed 0.45%; `reported-score.json` and `comparison-score.json`. |
| Observation and parameter totals | 307 fitted quantities, 16 coordinates, six active bounds; checked against `fit-summary.json`, `fitted-rows.csv` and `conditional-standard-errors.csv` by the shared presentation checks. |

The literature reading shelf is in the main checkout. Uyan (2015), Sections 4.1–4.3, Wangler (2018), Sections 6.1–6.3, and Böttinger (2008), the equilibrium-constant fitting discussion and Table 5, were read from their indexed companions; each companion matches both its indexed SHA-256 and current Zotero-storage bytes. Zhang (2011), Section 3.3 and Tables 9–11, and Neumann (2022), Sections 4.1–4.2, were read directly from existing Zotero PDFs because those papers are absent from the shelf index. Their attachment keys and SHA-256 values are `M3QDCZM7`, `c37e7370c765257b4c47d60b22b0ed136b7e97b3ef867ff2613d69c572785760`, and `G3U3WRF8`, `3480911860e23b29e2460868a06aa7a3ef3f20f261bd05379ca878906a53eaf1`, respectively. The source-library files and committed bibliography remain unchanged.

### Generation and checks

Table and figure strings were edited only in `scripts/final_rerun_tables.py` and `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py`. Tables were regenerated with the main checkout's `.venv/bin/python -I`; figures with that interpreter and the specified figure script. Only four table bodies changed: the literature comparison, wider-bound parameter table, acceptance-limit table and phase-count/split tables in `supplement_phase_family.tex`; all other table differences update the generator, shared-check and supplement input hashes. The phase-family PDF/PNG and figure provenance were regenerated. All numerical results remain unchanged.

`a7_presentation.py` retains every original evidence hash, inventory, count and numerical equality check. Its original unchanged-literature/nomenclature comparison against inventoried commit `771410a94f7729915bfe6457bfe7a5a0746f1611` remains in force. The approved present-work generator row and literature-caption line now have exact SHA-256 checks as well. A temporary in-memory check confirmed that an unapproved literature coefficient, nomenclature definition, present-work row or caption modification each raises an assertion, while the approved generator passes. No persistent test or new calculation script was added.

`main.tex` imports prefixed supplement labels through `xr`, so the new references resolve to the actual Table S4 (`tab:supplement-data-roles`) and Section S8 (`sec:s-phase`); the Methods and phase-section references use their existing main-text labels. Three paragraph identifiers were added: `methods-phase-01`, `results-scope-02` and `results-scope-03`. The assembled main text has 50 unique paragraph identifiers.

The first main build found that the enlarged Table 6 exceeded the page height by 31.32335 pt. The generator now selects `footnotesize` for that table only, preserving every approved word and number. The final table fits and remains legible. This is the only layout adaptation. The supplied ban-list directory was stale; the existing file read was `/home/tnnrpolley21/Workspaces/Agentic-Coding/plugins/cse/cse-plugin/plugin/BANNED.md`. The plugin-wide and scoped prose checker passes. No abstract word limit was found in the repository or submission files; the final synchronized plain-text abstract has 296 whitespace-separated words. Highlight lengths are 78, 79, 83, 81 and 76 characters, all within 85.

Both final builds used, from this directory:

```bash
SOURCE_DATE_EPOCH=1792750003 FORCE_SOURCE_DATE=1 nice -n 10 latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds supplement.tex
SOURCE_DATE_EPOCH=1792750003 FORCE_SOURCE_DATE=1 nice -n 10 latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds main.tex
```

The supplement was built first to supply its cross-reference values. Final outputs are `builds/main.pdf`, 21 pages, SHA-256 `4bfdb4a1dcf427cc72aab1c10e9170297525d5418a700db64297286ea7a384a4`, and `builds/supplement.pdf`, 23 pages, SHA-256 `1dce0e80a8a9154738faa4dac210be2fca50885640d1fbc436abb719316a2254`. Neither final log has overfull boxes, oversized floats, undefined references/citations or missing/substituted fonts. BibTeX uses the unchanged committed snapshot.

All 44 pages were rendered in color and grayscale at 110 dpi under `/tmp/issue-211-part2-pages/{main,supplement}/pages/{color,grayscale}/page-NN.png`; `page-images.txt` lists all 88 paths. Each document also has `contact-sheet.png` and `report.json`. The automated visual checks report 178 main and 52 supplement warnings, rather than an automatic pass: tight text clearances, mathematical/plot text reported against vector graphics, and rotated landscape-table text reported near the page edge. Inspection of the complete contact sheets and full-size revised pages found no clipping or unintended text/graphic collisions; the landscape table remains within its rotated page. The final PDF preserves the finite-search and property-specific limits. These presentation checks are not an independent scientific review.

The manuscript freshness command checked the 67 retained manuscript inputs against the final main PDF and updated the recorded build hashes. The required `git add -u` followed; the subsequent freshness check and staged whitespace check both pass. Delivery for this implementor is a local issue-branch commit; merging, pushing and the independent manuscript review are outside this pass.
