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
