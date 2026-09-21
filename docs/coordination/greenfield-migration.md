# Greenfield migration consumer specification — MEA-Thermodynamics

Status: **input contract prepared; qualification and parameter adoption remain
pending**.

This document is the MEA input-preparation handoff for Engine issues #84, #85,
#87, #89, #90 and #61. It records the current application consumer contract,
the source and parameter limits that are visible in the repositories, and the
smallest useful first replay. It does not adopt the exploratory MEA parameter
candidate, qualify an Engine wheel, change application source, or authorize a
numerical-kernel implementation.

## Inspection boundary and snapshot identity

The current application repository was inspected read-only at
`/home/tnnrpolley21/Workspaces/Engineering/MEA-Thermodynamics`, HEAD
`3b2071197e801401162f24ff7d0aa99518369c26` on `main`. The independent draft
clone was inspected at
`/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-greenfield/downstream/MEA-Thermodynamics`.
Only this document in the draft clone is changed by this handoff. The draft
clone contains older copied analysis inputs; it is not silently treated as the
current application snapshot.

The current application evaluator and its retained input identities are:

| item | current path | SHA-256 or identity | role |
|---|---|---|---|
| evaluator | `analyses/mea_parameter_bundle/scripts/shared_evaluation.py` | `6e5e081700207f6e358ef2b034ad70d3c1d6b5f816681f03fc402a3df5c8a371` | retained state construction, bounded recovery, output capture and failure receipt; old API consumer |
| state packet archive | `analyses/mea_parameter_bundle/data/input/state-packet.json.gz` | `e9d3ea9903fec9b5239dddcfe5bb8449e9f1a1aff488f0900cc9a91479ba48ba` | current compact input packet |
| decompressed state packet | same archive, decompressed | `86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448` | byte identity for a replay |
| selected parameter candidate | `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json` | `568f7a5f6379acebacea584d707d5a3222db1022a85a4092b52553248e48524d` | exploratory incumbent, `document_id=mea-co2-h2o-nine-species-estimation-candidate-v1`, version 2 |
| source parameter snapshot | `analyses/mea_parameter_bundle/data/input/parameters.json` | `58793d354f393944ca0f5fd1640a11645417ddfe6331b955de728f86f0e0b195` | separate source/input record; not the evaluator's selected-parameter path |
| Engine wheel | `analyses/mea_parameter_bundle/data/input/engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl` | `40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805` | retained non-editable wheel used by the analysis records |
| Engine commit recorded by analysis | — | `8438ce5f94a547189c91c4ec180a7782d60879d6` | provenance only; it is not current Engine acceptance evidence |
| reaction source contract | `data/reference/MEA/manifests/chemical_reaction_source_contract.json` | `39db0d7ef972dc7eb41328bdf2ec3f67f62c33fc2bf0fdc7bab471ade9aefb55` | source standard state, reaction rows and conversion metadata |
| thermal reference | `analyses/mea_parameter_bundle/results/calorimetry/current-selected-reference-thermochemistry.json` | `a24a6b3c8b506fc659fc1bbd8a470b55919ba93da23eea27ffdf882645706185` | current exploratory reaction-consistent thermal reference |
| calorimetry partition | `analyses/mea_parameter_bundle/data/input/calorimetry-observation-partition.csv` | `175e55ff7e238ee19957da9b028e0d957bd99b35aa5ec4145926a055542725d3` | calibration, holdout and source-lineage partition |
| density observations | `data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv` | `9047efb0281bff93d1769b12a3df50420d0b01ddd44ffd5041749ec0fb1fe622` | supporting density source rows |

The draft clone still has plain `state-packet.json` with SHA-256
`41017bcf727a486a8f3feb280e19c111a15c5dda5a3cca4e8c7dc5b051168fef`, the
older selected-parameter file with SHA-256
`a9186c93759f2e2c02a6c913350ad06a244fff3f82503820c9962b3df8dd40d9`, and an
older evaluator with SHA-256
`6bc94e6c628aa212ccc4a6cce32226eed42aadaca6d06692e6c9be6984b6e32d`. Those
copied files remain untouched because this preparation slice is documentation
only. A future replay must use and record the current identities above, or
explicitly state that it is reproducing the older draft snapshot.

The retained evaluator is not runnable unchanged against merged Engine
`f909bb21a93171c38465adba8777cd3b0bc6c53d` or wheel
`9f73aeb466c54eff80c89a8776c90d49cb9c9c2d130f0eb15bf0311c1f76e606`. It calls
the retired `equilibrium.general_reactive_equilibrium_problem_from_mapping`
and `equilibrium.solve(..., active_parameters=...)` surfaces. A finite #61
adapter is therefore required before the first replay: map the retained
requests to current `Problem`/`Phase`/`Amounts`/`Reaction(correlation)`,
call `solve_equilibrium`, and call `solved_state_actions` for the supported
state/EOS actions. The adapter must preserve current result statuses and
failure diagnostics. For heat, map the current phase
`TotalEnthalpy` observable (J/mol) times phase amount (mol) to extensive
endpoint `H` (J). No adapter or replay was implemented in this preparation.

## Application target and declared topology

The target operating range for MEA and the absorber is the full **315--360 K**
range. Retained calibration inputs extend below and above that range and are
useful for source and continuation diagnosis, but a result outside 315--360 K
must be labelled as supporting or extrapolative. A published fit interval is
an applicability input to assess, not an automatic rejection gate. The
application must disclose extrapolation and its effect on each consumed
prediction; it must not call extrapolated results source-validated.

The first contract keeps the existing nine liquid species, five reactions and
neutral-only vapor support. Phase discovery is deferred. The selected
parameter file is an exploratory candidate and remains an input fingerprint,
not an accepted MEA model.

| index | Engine component id | application symbol | charge |
|---:|---|---|---:|
| 0 | `carbon-dioxide` | CO2 | 0 |
| 1 | `monoethanolamine` | MEA | 0 |
| 2 | `water` | H2O | 0 |
| 3 | `protonated-monoethanolamine` | MEAH+ | +1 |
| 4 | `carbamate-anion` | MEACOO- | -1 |
| 5 | `bicarbonate-anion` | HCO3- | -1 |
| 6 | `carbonate-anion` | CO3-- | -2 |
| 7 | `hydronium-cation` | H3O+ | +1 |
| 8 | `hydroxide-anion` | OH- | -1 |

Products are positive in the fixed reaction matrix. The rows are:

| reaction | equation | matrix row in the species order above |
|---|---|---|
| R1 | `2 H2O <=> H3O+ + OH-` | `[0,0,-2,0,0,0,0,1,1]` |
| R2 | `CO2 + 2 H2O <=> HCO3- + H3O+` | `[-1,0,-2,0,0,1,0,1,0]` |
| R3 | `HCO3- + H2O <=> CO3-- + H3O+` | `[0,0,-1,0,0,-1,1,1,0]` |
| R4 | `MEACOO- + H2O <=> HCO3- + MEA` | `[0,1,-1,0,-1,1,0,0,0]` |
| R5 | `MEAH+ + H2O <=> MEA + H3O+` | `[0,1,-1,-1,0,0,0,1,0]` |

The current packet names the liquid reference standard
`aqueous-molality-infinite-dilution-water-v1`: water is the solvent, standard
molality is 1 mol/kg and `M_water=0.01801528 kg/mol`. For a finite liquid
composition, the molality is
`m_i = x_i/(x_water*M_water)`. The relation
`m_i/m° = x_i/(M_water*m°)` is only the infinite-dilution
`x_water -> 1` standard-scale relation; it is not a general finite-composition
conversion.

The source facts are row-specific. R1--R3 use Austgen's unsymmetric
mole-fraction convention with pure H2O/MEA standard components and infinitely
dilute molecular and ionic solutes at the system `T,P`. R4/R5 use aqueous
molality sources with source/reference pressure `p°=100000 Pa`. The packet's
unit-vector water solvent and fixed 100000 Pa liquid sentinel are input
assumptions, not a shared source convention. Its historical trial-pressure
provider contraction remains unqualified. The declared ion pairs, source
conventions and any provider transfer must remain in the reaction receipt;
#84 owns the exact thermodynamically consistent conversion.

## Reaction and thermal reference contract

R1--R3 are retained from Austgen 1991 Table V with the source's unsymmetric
mole-fraction convention, pure H2O/MEA standard components and infinitely
dilute solutes at system `T,P`. The stored offsets are R1
`+8.0330699846`, R2 `+4.0165349923` and R3 `+4.0165349923`; they are a
prepared infinite-dilution scale transformation, not an accepted finite-state
conversion. The source range is 273.15--498.15 K. #84 owns the exact conversion
from these source definitions to the current provider basis.

R4 is the selected Tong 2012 Table 5 / Aroua 1999 form
`ln K = 2.151 - 1545.3/T`, with source range 293.15--323.15 K and
`p°=100000 Pa`. R5 is the selected Bates and Pinching 1951 Eq. 7 form
`-log10 K = 2677.91/T + 0.3869 + 0.0004277*T`, with source range
273.15--323.15 K and `p°=100000 Pa`. The recorded trial-pressure provider
contraction for R4/R5 is historical evidence and remains unqualified. The
common all-five source intersection is therefore 293.15--323.15 K. The
315--360 K application target requires R4 and R5 to be extrapolated by as much
as 36.85 K. That extrapolation is a disclosed model limitation, not an
automatic rejection and not source validation.

The current reaction-temperature fit changes R2/R4/R5 values in the selected
candidate and is exploratory. Its reaction-coordinate transformations are
application-owned candidate metadata: at pivot `T_p=313.15 K`, R1--R4 use
`Delta a = Delta h/(R*T_p)` and `Delta b = -Delta h/R`; R5 uses
`Delta a_k = Delta h/(R*ln(10))` and
`Delta b = -Delta h/(R*T_p*ln(10))`. The current receipt also reports that
the full replay scored R1/R3 shifts while the selected document omitted those
shifts. These coordinates need a conditional #61 reaction-fit design; they are
not current Engine EOS active-parameter actions. No reaction vector is accepted
until #61 reconciles that history and the source-centered values with a fresh
application decision.

The thermal reference payload is
`mea-anchored-reaction-consistent-reference-thermochemistry-v2`: 293.15--393.15
K, reference temperature 353.15 K, 2.5 K grid, degree-8 Engine-form
polynomials, anchor pressure 101325 Pa, and a hydronium gauge equal to the
water reference enthalpy (zero-enthalpy proton). Its retained maximum
van't Hoff residual is `0.00012996 J/mol` against a `0.001 J/mol` identity
tolerance. CO2 has a physical ideal-gas Cp/formation-enthalpy anchor from the
NIST Shomate/CODATA record. Hilliard and Weiland provide physical solution-Cp
observations on their stated mass bases. The current selected record labelled
`liquid_correlation_minus_eos_residual` is an **effective model-input record**:
it makes the modeled pure-liquid Cp match a retained solution correlation by
subtracting the Engine residual contribution. It is not a physical ideal-gas
Cp and it is not a freely selectable enthalpy or entropy gauge.

Zhang, Que and Chen (2011), DOI
[10.1016/j.fluid.2011.08.025](https://doi.org/10.1016/j.fluid.2011.08.025),
Zotero `MMAGNPIH/M3QDCZM7`, Table 3 (printed p. 68 / PDF p. 2), supplies a
candidate MEA ideal-gas heat-capacity correlation for `283 < T < 1000 K`:
`Cp_ig [J/(mol K)] = 13.207 + 0.28158*T - 0.0001513*T^2 +
3.1287e-8*T^3`, with `T` in K. The paper attributes these coefficients to
the Aspen Databank; the table reports no uncertainty. This is a physical
ideal-gas model-input candidate, neither a new experiment nor an adopted
thermal record. The same page's Table 2 ionic columns are infinite-dilution
aqueous properties, not gas heat capacities, and must not be mixed into this
candidate.

The physical ideal/reference Cp and the source-to-provider enthalpy/entropy
reference shifts belong to #84. Residual-model inadequacy belongs to #61. A
reference gauge must not be changed to hide a residual-model error, and no
thermal record is an accepted parameter packet.

The small, source-observed Hilliard case verified in Zotero
`DNQUPRMT/PDFLB7LUETY`, Appendix G.2, printed p. 937 / PDF p. 994, is 7 mol
MEA per kg water at loading 0.358 mol CO2/mol MEA: Cp is 3.3675 kJ/kg/K at
45 C and 3.4707 kJ/kg/K at 80 C. The same appendix reports unloaded 45 C Cp
3.7195 kJ/kg/K. The composition is reported per kg water, while Cp is reported
per kg loaded solution per K; retain those bases separately. These values are
physical observations, not the model predictions in Table 13.6-1 p. 494.
The independent Weiland 1997 source `66XLM3LX/PDF27V9SYLA`, Table 3 p. 1004,
reports only 25 C, 30 wt% MEA solution Cp at loadings 0, 0.1, 0.2, 0.3, 0.4
and 0.5 as 3.734, 3.656, 3.570, 3.457, 3.418 and 3.359 J/g/K,
respectively, with +/-1% repeatability. Those are source observations on the
reported solution mass basis; they do not establish the 315--360 K range.

Calorimeter assumptions remain explicit: finite vapor inventory is zero and
the incoming CO2 has ideal/reference gauge-zero residual enthalpy. Freeze the
positive heat-release convention for a loading pair `a -> b` as
`q_CO2 = [Delta n_CO2*h_CO2,feed^ref - (H_b - H_a)]/Delta n_CO2`, where
`h_CO2,feed^ref` is that incoming ideal/reference feed enthalpy and
`H_a/H_b` are extensive endpoint enthalpies. Do not substitute an arbitrary
vapor partial enthalpy. These are application pairing/reference choices, not
generic Engine defaults.

## Retained packet and operating conventions

The current compact packet has 123 equilibrium observations and 210 included
targets: 79 true-species vapor partial-pressure targets, 106 true-species
liquid mole-fraction targets and 25 linear aggregate targets. All packet target
roles are `calibration`. The source lineages are Jou 1995 (48 pCO2 rows),
Hilliard 2008 (31 pCO2 rows), Böttinger 2008 (55 speciation targets) and Matin
2012 (76 speciation targets). The packet temperatures are 293.15, 313.15,
333.15, 353.15, 373.15 and 393.15 K.

The packet constructs finite amounts in mol. A representative feed has
`[CO2, MEA, H2O] = [loading*MEA, 0.99998, 7.910947365207347] mol`; the ionic
components carry small positive seed amounts (for example 1e-5 mol, with
the retained vector preserving the exact charge/balance seed). Conserved
totals are derived from the stoichiometric balance matrix, not treated as
independent measurements. The strict interior amount floor is 1e-12 mol.
The small ionic seeds, normalized feed and all-liquid pressure sentinel are
assumed numerical/input conventions and must not be presented as measured
ionic concentrations.

Source loading is mol CO2 per mol MEA unless a row says otherwise. MEA
composition is a mass fraction (30 wt% is stored as 0.30). Temperature is K
inside the Engine; source Celsius values are converted explicitly. Pressure is
Pa inside the Engine; source kPa/bar values are converted and retained as
context. Mole fractions and aggregate results are dimensionless. A solved
VLE pressure is a total system pressure; `co2-partial-pressure` is a vapor
phase partial pressure and must never be compared with total pressure.

The all-liquid speciation request uses fixed `P=101325 Pa` as a packet
sentinel. VLE requests solve pressure in `[1, 10000000] Pa` with retained
initial and continuation starts. The phase declarations are:

- `mea-nine-species-liquid`, finite, all nine components, liquid;
- `mea-neutral-incipient-vapor`, incipient, vapor, support exactly
  `[carbon-dioxide, monoethanolamine, water]`;
- reaction phases point to the liquid. No ionic vapor species are inferred.

## Exact representative cases

These cases freeze the first preparation/replay inputs. They are not results
or qualification predictions.

### Liquid speciation and aggregate basis

`Bottinger2008_state_050` is the explicit basis check:

- source: `data/reference/MEA/observations/liquid_speciation/Bottinger_2007_ChEq.csv`, source row 50;
- source state: 0.487 mol CO2/mol MEA, 30 wt% MEA, 313.15 K (40 C), source pressure blank;
- packet state: CO2 feed 0.4869 mol, MEA 0.99998 mol, water
  7.910947365207347 mol, retained ionic seed floors, fixed 101325 Pa;
- conserved totals: `[2.487, 1.0]` for the retained balance rows;
- outputs: MEA+MEAH+ aggregate `0.0646`, MEACOO- `0.0511`, HCO3-
  `0.0052`, all dimensionless mole-fraction quantities;
- aggregate map: `[0,1,0,1,0,0,0,0,0]` in the nine-species order;
- target covariance identity: `speciation|Bottinger2008|w=0.3|T=40`;
- all three targets are calibration rows with scaled-difference residuals and
  packet scale 0.01.

Böttinger's fast proton transfer means MEA and MEAH+ are observed as an
aggregate. CO2, MEA, MEAH+, CO3--, H3O+ and OH- are balance-inferred in the
source membership record rather than independent observations. MEACOO- and
HCO3- are eligible true-species observations. This 313.15 K state is a
chemistry/basis contract case just below the 315 K target boundary. The exact
application-range speciation row is `Bottinger2008_state_058`, source row 58,
333.15 K (60 C), 30 wt% MEA and loading 0.415 mol/mol. Its packet feed is
`[0.4149, 0.99998, 7.910947365207347, 0.00001, 0.00001, 0.00008,
0.00001, 0.00011, 0.00001]` mol, with conserved totals `[2.415, 1.0]` and
fixed 101325 Pa. The retained outputs are MEA+MEAH+ `0.0687`, MEACOO-
`0.0417` and HCO3- `0.0042`, all dimensionless mole fractions, with the same
aggregate coefficient vector `[0,1,0,1,0,0,0,0,0]`. It is a current packet
calibration row and an application-range case; the grouped cross-validation
manifest marks this 333.15 K curve as a non-scoring domain extension pending
the R4/R5 source-range extension. It must not be called source-validated.

The source inventory classification is corrected here for Matin 2012: the
source measures titration inputs and derives species concentrations from
alkalinity, base, CO2 loading and density. The current packet's `direct`
measurement label is therefore treated as `derived_from_titration` for this
handoff, with the original packet identity retained. These rows are not direct
species observations and are not scored as such.

### Reactive VLE and partial pressure

`vle_obs_0206` is an in-domain pressure/partial-pressure case:

- source: Jou 1995 `Jou_1995_VLE.csv`, source row 35, active row `vle_0097`;
- source state: 353.15 K (80 C), MEA mass fraction 0.30, loading 0.118
  mol/mol, source total pressure 250 kPa, source CO2 pressure 0.0992 kPa;
- packet feed: CO2 0.1179 mol, MEA 0.99998 mol, water
  7.910947365207347 mol and the retained ionic seeds;
- pressure: solved in `[1, 10000000] Pa`, initial 100000 Pa, retained start
  `43106.57112947591 Pa`;
- phases: finite all-nine liquid plus incipient neutral vapor;
- outputs: `system-pressure` (Pa), `vapor-y-co2`, `vapor-y-mea`,
  `vapor-y-water` (dimensionless) and `co2-partial-pressure` (Pa);
- target: `co2-partial-pressure = 99.2 Pa`, direct calibration, `log_ratio`
  residual, scale 0.05.

The source total pressure is contextual metadata. The packet solves pressure at
fixed temperature and loading, so the target is the CO2 partial pressure. This
case is also a useful #89/#90 diagnostic because a numerical pressure-root
failure does not establish physical nonexistence.

The Jou source was visually checked in Zotero `XIY346VI/PDFVF5GM23T`,
pp. 140--141. Its apparatus uses N2 as a carrier for total-pressure control
and GC N2/CO2 composition, with a 0.1% full-scale pressure gauge over 0--10 or
0--35 MPa and temperature uncertainty +/-0.1 C. The current packet vapor phase
supports only neutral CO2/MEA/H2O, so mapping this low-pCO2 source to a
neutral-only bubble at a different total pressure requires an explicit
pressure/carrier transfer assumption. Preserve the neutral-only support, but
do not call this an identical-state validation of the N2-containing source.

The Hilliard comparator `vle_obs_0130` is source row 24 of
`Hilliard_2008_VLE.csv`, active row `vle_0029`: 313.15 K (40 C), 30 wt% MEA,
loading 0.35 mol/mol, source pCO2 0.0721 kPa (72.1 Pa) and source total
pressure 6.75 kPa. Its source basis is calibration-derived partial pressure
from calibrated gas composition and total pressure; the current packet stores
it as a direct `true-species-vapor-partial-pressure` calibration target. It
uses the same neutral vapor support, but the source numeric uncertainty and
covariance remain unspecified.

### Exact source row, basis and role inventory

The current packet labels its included rows `calibration`; the canonical
manifests also retain grouped training/reserved-validation lineage. Both roles
are recorded below so a later fit cannot silently turn a selected holdout into
independent validation.

| source | exact row/state and physical inputs | source basis and observed quantity | current packet role | canonical/selection role |
|---|---|---|---|---|
| Jou 1995 | `vle_obs_0206`, `Jou_1995_VLE.csv` row 35, active row `vle_0097`; 353.15 K, 30 wt%, loading 0.118, source total P 250 kPa | `calibration_derived_partial_pressure`; pCO2 0.0992 kPa from total pressure and calibrated gas composition; current target is 99.2 Pa `true-species-vapor-partial-pressure` | calibration, direct target classification | grouped manifest reserves the Jou w=0.3/T=80 group for validation; the current packet's calibration use is therefore a lineage conflict to disclose, not an identical-state validation claim |
| Hilliard 2008 | `vle_obs_0130`, `Hilliard_2008_VLE.csv` row 24, active row `vle_0029`; 313.15 K, 30 wt%, loading 0.35, source total P 6.75 kPa | `calibration_derived_partial_pressure`; pCO2 0.0721 kPa (72.1 Pa), derived from calibrated FTIR/IR gas composition and measured total pressure | calibration, direct target classification | active grouped training row; source numeric uncertainty and covariance not transcribed |
| Xu 2011 | pressure holdout IDs `vle_obs_0265`--`vle_obs_0272` (source rows 1--8, nominal 100 C) and `vle_obs_0279`--`vle_obs_0288` (source rows 15--24, nominal 120 C), all 30 wt% MEA; source temperatures and loadings remain row-specific | `total_pressure_derived` from measured total pressure corrected by source Eq. (1) for N2 and calculated solvent vapor; pCO2 targets are reported in kPa and converted explicitly | not in the current packet; 18 rows were evaluated in the reaction-selection holdout | reserved validation by source/composition/temperature group; already accessed during candidate selection, so no longer untouched validation |
| Jakobsen 2005 | `Jakobsen2005_state_017`, `Jakobsen_2005_ChEq.csv` row 17; 313.15 K (40 C), 30 wt%, loading 0.11; retained values MEA 0.0985, MEAH+ 0.0065, aggregate 0.105, MEACOO- 0.0103, HCO3- 0.0001, CO3-- 0.0001 | true-species liquid mole fractions plus the MEA+MEAH+ linear aggregate; CO2/H3O+/OH- are balance-inferred; source covariance not reported | not in the current packet | canonical eligible but grouped `reserved_validation`; direct positive species/aggregate observations, held out as a complete source/composition/temperature curve |
| Böttinger 2008 | `Bottinger2008_state_050`, source row 50, 313.15 K/30 wt%/loading 0.487, and exact application-range `Bottinger2008_state_058`, source row 58, 333.15 K/30 wt%/loading 0.415 | true-species liquid mole fractions for MEACOO-/HCO3- and MEA+MEAH+ linear aggregate; CO2, MEA, MEAH+, CO3--, H3O+, OH- balance-inferred; covariance not reported | both are calibration targets in the current packet; state 050 values .0646/.0511/.0052 and state 058 values .0687/.0417/.0042 | state 050 is active grouped training; state 058 is grouped training metadata but marked non-scoring domain extension pending R4/R5 extension |

This inventory is the source/basis/role contract for #60 and #82. It does not
add a source-acquisition prerequisite: the relevant PDFs are retained in
Zotero storage and their locators are recorded where needed.

### Paired caloric difference

Use the 353.15 K (80 C) Kim and Svendsen 2007 Table 2 run 1 pair
`kim2007_t80_r1_0.047 -> kim2007_t80_r1_0.090`:

- 30 wt% MEA, source loadings 0.047 and 0.090 mol/mol;
- preceding row 0.047 is the initial endpoint and 0.090 is the paired target;
- target endpoint reports 90.904 kJ/mol CO2, with source semantics
  “temperature-differential; loading-semi-differential” and reported relative
  uncertainty 2.2%;
- the first table row has an assumed start loading 0.003. The known printed
  first-row/integration inconsistency is retained and excluded from the pair
  definition rather than repaired silently;
- the future #61 adapter maps the current phase `TotalEnthalpy` observable
  (J/mol) times phase amount (mol) to each endpoint's extensive `H` (J), then
  applies the positive heat-release convention above and reports J/mol CO2
  (also in kJ/mol CO2). This mapping is not implemented in this preparation.

The historical exploratory candidate predicted 85.4111 kJ/mol CO2 at the
0.090 endpoint, a residual of -5.4929 kJ/mol CO2 for this pair. That value is
retained context only; this preparation did not replay it. The 120 C heat
holdout remains underpredicted (candidate RMSE 31.1513 versus baseline
39.3029 kJ/mol CO2) and was already accessed during reaction selection, so it
is diagnostic evidence rather than untouched validation.

### Supporting density closure

The supporting physical-density case is Amundsen 2009 Table 3, lines 70--81:

- 353.15 K (80 C), MEA mass fraction 0.30 on the unloaded-solution basis,
  loading 0.3 mol/mol;
- measured density 1.0402 g/cm3, combined absolute uncertainty
  +/-0.002 g/cm3, temperature uncertainty 0.03 K, MEA mass-fraction relative
  uncertainty 0.5%, loading relative uncertainty 2%;
- pressure is blank in the retained row and must remain missing/unreported;
- source scope is 25--80 C, 20/30/40 wt% MEA and loading 0--0.5. The stated
  use is density/viscosity for column capacity, pressure drop and mass transfer.

This row is not in the equilibrium packet. It is a supporting density/property
case for #89 and #85, not a reason to infer pressure or add transport physics.
The analogous ionic density records are not direct MEA electrolyte evidence.

## Consumed Engine outputs, actions and coordinate transformations

The following are the actual application consumers. The derivative order used
by the current code is first order. No second derivative or generic Hessian is
required by this slice.

| consumer | physical inputs and coordinates | consumed outputs | consumed action and status contract |
|---|---|---|---|
| reactive VLE | `T` K; solved `P` Pa; finite nine-species feed amounts mol; balance totals; declared phase supports; reaction constants after source-to-provider conversion | total pressure Pa; neutral-vapor mole fractions; CO2 partial pressure Pa; phase composition and evidence | #61 adapter to current `solve_equilibrium`; bounded pressure/root recovery; value rows for packet targets; `solved_state_actions` state-input blocks when requested by an anchor/recovery replay. Keep root/branch status and partial values. |
| liquid speciation | fixed `T` K and `P` Pa; finite feed amounts mol; nine-component molar masses; reaction/balance rows | true liquid mole fractions dimensionless; linear aggregates from stored coefficient vectors | value rows for current packet; no unrecorded finite-difference substitute for a missing native action. Aggregate mapping and source basis stay application-owned. |
| continuation/density | finite phase amounts mol, molar volume m3/mol, balance totals, continuation identity, model/reaction fingerprints | phase pressure Pa, molar density mol/m3, molar volume m3/mol, packing fraction, composition, phase amounts, chemical-potential-over-RT and evidence/status | continuation state and property actions seed bounded recovery and cache identity. Nonpositive, inconsistent or failed density is a failed attempt. Global search remains unestablished if not run. |
| paired heat | fixed endpoint `T/P`, finite composition and amounts, reference/formation enthalpy payload, paired loading endpoints | phase `TotalEnthalpy` (J/mol), phase amount (mol), extensive endpoint `H` (J), paired heat J/mol CO2 | current `solved_state_actions` value/status for the phase observable plus the #61 adapter's amount multiplication and finite pairing. No reaction/reference active-parameter derivative is currently available; do not finite-difference silently. |
| reaction-coordinate fit | candidate reaction coefficient identities and order; application-transformed values; T/P/feed coordinates | fixed-candidate output rows; any future reaction-coefficient Jacobian columns | retained fit receipts use old reaction actions. Current `SolvedStateActionDirection.active_parameters` covers EOS model actives only; #61 owns a conditional reaction-fit design and adoption decision. |

The retained old-wheel application evidence consumes values, recovery evidence,
density and reaction-fit output Jacobians. The current Engine can provide EOS
model-parameter and state-input actions through `solved_state_actions`, but
the adapter is still absent and the application does not consume a general
state-input derivative tensor for every packet row or second-order actions.
The six built-in regression observation forms therefore do not by themselves
establish CO2 partial-pressure rows, paired caloric differences, or reaction
coefficient fitting.

Every promoted active-parameter row must preserve caller parameter order,
output identity, unit and phase. A missing Jacobian block, changed coordinate,
nonfinite row or status mismatch is a hard derivative failure. Retain finite
central outputs when a derivative action fails, but mark the derivative result
unavailable; do not use it as a qualified fit row.

### Reaction-coefficient action status

The retained `reaction:R4:correlation:a` and
`reaction:R4:correlation:b_k` values, their R5 pair and the centered
finite-difference agreement are **old-wheel evidence** from the retained
evaluator. They are not current f909/wheel-9f73 reaction-action evidence.
The current `SolvedStateActionDirection.active_parameters` contains only EOS
model actives declared on the `Mixture`; `ReactionLogPolynomial` coefficients
passed through `Reaction(correlation)` have no current reaction-coefficient
action slot. No current R4/R5 or R1--R3 reaction action is therefore available.

A fixed candidate reaction value can remain a prepared value input for a future
replay after the adapter maps it, but any further reaction-coordinate fit
requires a conditional #61 design and adoption decision. #84's generic
reference chain and #85's EOS-family inventory must not silently absorb that
reaction-fitting extension. Do not substitute finite differences for the
missing consumed action or waive the action requirement.

For provenance, the old receipt's R4 central perturbation was +/-2.5 kJ/mol,
with `Delta a = +/-0.9601816624838422` and
`Delta b_k = -/+300.68088760681513 K`; its retained finite ladder was
`Delta h = +/-[0.625, 1.25, 2.5, 5.0] kJ/mol`. The old-wheel criterion was
a maximum native-versus-centered finite-difference relative deviation of 1% on
evaluated, positive, non-floor rows. At `vle_obs_0206`, it reported
`0.017420114262867055` versus `0.017417808364391107` per kJ/mol in
`dlog10(pCO2)/d(Delta h)`, relative deviation
`0.00013238740648115324`; across 24 R4 rows, the maximum was
`0.0017369951310693928` and the median `0.0002437437844653066`. These are
diagnostic old-wheel evidence, not current qualification.

### Finite replay and resource budget

The proposed replay is not runnable unchanged: it first needs the finite #61
adapter described above. The fixed nine-species/five-reaction candidate values
and neutral-vapor topology can be prepared through that adapter, but the
retained R4 reaction-action receipt remains old-wheel evidence and is not a
current action check. A current reaction-coefficient action is unavailable
until #61 settles its conditional design and adoption boundary.

The first replay is limited to the following cases: `Bottinger2008_state_058`
for the exact in-range liquid basis, `vle_obs_0130` for Hilliard pCO2,
`vle_obs_0206` for Jou pCO2 and the N2/carrier-transfer diagnostic, the two
endpoints of the Kim/Svendsen 353.15 K pair, and the Amundsen 353.15 K density
row as supporting evidence. The R4 action check is run on the two VLE cases
and the in-range speciation case only **if #61 first provides a current
reaction-action path**; otherwise retain the typed unavailable status and old
receipt as provenance. This is a bounded consumer trace, not a packet
campaign.

For each equilibrium state, retain at most four unique recovery starts:
nearest same-temperature anchor, cold packet start, nearest cross-temperature
anchor and one additional retained cross-temperature continuation anchor;
duplicate start signatures are skipped. Use the existing hard 60 s child-solver timeout and 900 s per-state
wall budget, including all recovery attempts and cache work. The thermal pair
has two such endpoint budgets. Record each attempt, elapsed time, status and
partial outputs; a budget exhaustion is a typed numerical failure. No broader
parameter or temperature campaign is authorized by this contract.

## Source and input inventory

| class | retained quantities and evidence | present limitation |
|---|---|---|
| measured/direct | Jou/Hilliard pCO2 rows; Böttinger NMR MEA+MEAH aggregate, MEACOO- and HCO3- rows; Matin titration inputs; Kim/Svendsen direct calorimetry; Amundsen density; Hilliard/Weiland solution-Cp observations | pCO2 uncertainty/covariance is unspecified; Böttinger has aggregate/proton-transfer basis; Matin species are derived from measured titration quantities; Amundsen pressure is blank; solution-Cp source values have their own stated mass bases |
| derived | finite molality from `x_i/(x_water*M_water)`; retained R1--R3 infinite-dilution scale offsets; reaction balance totals; aggregate coefficient maps; normalized finite feed and ionic seed vector; calorimetry endpoint pairing; reaction-consistent thermal reference polynomial | finite source-to-provider conversion and reference identities remain a #84 boundary; derived values are not independent measurements |
| assumed | ionic seed floors; fixed 101325 Pa all-liquid sentinel; retained pressure starts and recovery order; neutral-only vapor; zero finite vapor inventory and ideal incoming CO2 reference enthalpy; hydronium gauge; historical trial-pressure provider contraction | source p° and system-`T,P` conventions are source facts; packet assumptions can affect consumed predictions and must be disclosed or falsified separately |
| fitted/candidate | exploratory candidate residual EOS, association, Born/Debye-Huckel, packing, solvation, permittivity, interaction and reaction-coordinate values | candidate is `candidate_extrapolation`; no accepted MEA parameter packet exists |
| missing/unqualified | direct MEAH+/activity evidence, exact-salt ionic density, a verified MEA-water static relative-permittivity table over temperature/composition/loading, VLE uncertainty/covariance and density pressure metadata | do not fill with zeros, defaults or analog transfer; source PDFs are retained in Zotero storage, so missing local Markdown is not a source-acquisition gap |

The local literature README's missing-Markdown entries do not mean that the
sources are absent. Hilliard is retained as Zotero
`Zotero/storage/PDFLB7LUETY/`, Jou as `Zotero/storage/PDFVF5GM23T/`, and the
other source PDFs use their retained Zotero attachment keys. Any new source
claim should use those retained PDFs first and record a printed-page/PDF-page
locator. No source acquisition or covariance transcription is a prerequisite
for this input handoff.

Selection, calibration and validation lineages must stay separate. The current
packet is calibration only. The Xu 2011 pressure rows and Kim/Svendsen 120 C
heat rows were accessed during reaction selection and are therefore no longer
untouched independent validation, even though their retained holdout receipts
are useful limitations. Source-reserved rows and non-30-wt% composition rows
remain candidates for a later, explicitly designed validation split.

## Proposed physical criteria and numerical falsifiers

The following are **proposed owner-review criteria**, not acceptance claims.
They distinguish physical prediction from numerical convergence and use the
retained source precision and actual engineering use. The pCO2 screen uses a
factor-of-two envelope because partial pressure drives absorber loading and
the source covariance is unspecified; the exploratory pressure calibration
RMSE of 0.2366 dex is retained as context, not as a pass gate. The speciation
limits reflect the reported three-to-four-decimal mole-fraction resolution and
the fact that aggregate/minor-ion quantities affect reaction loading, while
inferred species are excluded. The heat limits are approximately 10--15% of
the 90--150 kJ/mol CO2 source scale and expose transfer error: the exploratory
candidate's retained calibration RMSE is 11.8447 kJ/mol CO2 and its accessed
120 C holdout RMSE is 31.1513 kJ/mol CO2. These thresholds are engineering
screens and require review; source measurement uncertainties are metadata and
are not silently promoted to model-error limits.

| observable | proposed physical screen | required qualification caveat |
|---|---|---|
| CO2 vapor partial pressure | median absolute `log10(p_pred/p_obs) <= 0.20` dex; at least 90% of eligible rows within 0.30 dex (about a factor of two); source/temperature group bias within 0.15 dex | retain source pressure context and missing uncertainty; do not score rows whose phase/basis contract is unresolved |
| speciation | for positive aggregate rows, median absolute error <=0.01 mole fraction and median absolute log10 ratio <=0.20; for positive minor-ion rows, absolute error <=0.005 and report a separate log ratio; inferred constituents are not independently scored | use source observation basis and detection limits; MEA+MEAH aggregate is the Böttinger observable |
| density | relative density error <=1.6% for the column-use screen, matching Amundsen's stated satisfactory baseline deviation for column use; report the source +/-0.0005 g/cm3 unloaded and +/-0.002 g/cm3 loaded values as informative measurement metadata | those 0.05% and 0.2% relative measurement uncertainties are not automatic model gates; pressure is missing in the Amundsen loaded records, so preserve the state limitation |
| paired heat | calibration median absolute error <=10 kJ/mol CO2; later holdout median absolute error <=15 kJ/mol CO2; no target-range systematic bias over 10 kJ/mol CO2 | 2.2% source uncertainty is metadata, not a blanket replacement for an observable-specific criterion; the 120 C holdout remains a diagnostic limitation |

Numerical falsifiers are separate:

- finite, positive requested state and output values; material and charge
  balances, reaction affinities, phase support and local mechanical checks
  within the caller's existing numerical tolerances;
- independent cold, warm and continuation starts agree on the declared branch
  when the same root is obtained: a provisional pCO2 relative spread of
  `1e-4` and composition absolute spread of `1e-6` are useful diagnostic
  thresholds, not physical error limits;
- if roots or branches differ materially, retain a typed ambiguous-branch or
  missed-root record and route it to #89/#90. A failed attempt is not evidence
  of physical nonexistence;
- every promoted EOS active parameter has a native Jacobian row with status
  `evaluated`, correct identity/order and finite units. Reaction-coefficient
  action remains typed unavailable until the conditional #61 design; the
  centered `Delta h` ladder above is old-wheel evidence only and must not be
  substituted for that action;
- verify the thermal reaction identity using the retained reference payload;
  the current maximum van't Hoff residual `0.00012996 J/mol < 0.001 J/mol` is
  retained evidence for the identity only, not a heat-prediction acceptance.

No new numerical tolerance should be promoted into an Engine implementation
without a reviewed diagnosis showing which consumer fails and why the existing
contract cannot express it.

## Finite Engine handoffs and demonstrated gaps

The following are the smallest concrete handoffs from this application slice:

| owner issue | demonstrated gap or bounded input | stopping condition |
|---|---|---|
| #85 active EOS families | The retained fixed-candidate/old-wheel evidence exercises `SegmentCount`, segment-diameter constant (`SigmaConstant`), `DispersionEnergyOverK`, `Kij`, `AssociationEnergyOverK` and `AssociationVolume`. `Lij` exists as a generic active coordinate but no MEA consumer or candidate slot demonstrates that it is required. The candidate also carries fixed segment-diameter(T), a reciprocal-temperature `k_ij` slope, Born/Debye-Huckel/packing diameters, solvation factors, relative-permittivity law and ion suppression; these are not automatically active regression coordinates. Reaction-correlation coefficients are not EOS families and remain outside this inventory. | publish the finite EOS family/order actually needed by the first MEA replay; return a reviewed no-code result if existing families suffice |
| #84 source/reference chains | Own the finite molality and infinite-dilution source-to-provider conversion, row-specific system-`T,P` versus source `p°` handling, thermal K(T)/Delta H relation, reference formation enthalpy and hydronium gauge. Do not replace the source contract with a scalar K-only input or silently absorb reaction fitting. | source rows, equations, units and reference identities are reviewable and reproducible at the exact target T |
| #87 trace/action accuracy | Trace pCO2 and true-species/aggregate rows, nonunit scales, partial-result retention, status/failure meaning, current EOS active-parameter row Jacobians and the missing paired-heat/reference derivative action. | a caller-level trace shows each consumed row/action/status and a typed failure; no silent finite-difference or dropped failure remains |
| #89 density and pressure roots | Reproduce pressure-root/branch behavior on `vle_obs_0206`, including the solved bounds and retained start, and on any high-loading examples. Distinguish a missed root from a legitimately ambiguous branch. Reuse the existing density owner and retain the Amundsen pressure-missing limitation. | reviewed reproduction classifies each failure/branch and states whether an implementation change is authorized |
| #90 initialization/continuation | Reproduce the known equilibrium-temperature start sensitivity using the evaluator's same-temperature, cold, cross-temperature and continuation anchors. | bounded start/continuation diagnosis identifies a reproducible failure class or establishes that no Engine change is required for the selected cases |
| #61 MEA application adoption | Provide the finite adapter from the retained evaluator to current Engine APIs; decide whether any application-owned reaction recalibration is adopted. Reconcile selected exploratory R2/R4/R5 shifts with source-centered correlations and the omitted R1/R3 fit records. Any reaction-coefficient action/fit remains conditional on this design. | explicit adapter/status mapping and candidate/reference decision with calibration, transfer and limitation language; no silent parameter promotion |

There is no demonstrated need here for PH/PS/UV, phase discovery, transport,
finite-rate chemistry, a broad optimization-domain campaign, or new physics.
The absorber and MEA can consume the declared neutral-vapor and thermal
contracts without adding those capabilities.

## First replay and dependency boundary

After #61 supplies the finite adapter, the parent authorizes the bounded replay
and a current wheel is installed, the first reviewable evidence block is:

1. `Bottinger2008_state_050` for species order, balance, aggregate map and
   source basis, with `Bottinger2008_state_058` as the exact 333.15 K
   application-range speciation row;
2. `vle_obs_0130` and `vle_obs_0206` for solved pressure, neutral vapor
   support, CO2 partial pressure, source-basis/carrier-transfer assumptions and
   pressure-root diagnostics. Fixed candidate reaction values may be mapped;
   the retained R4 action receipt is old-wheel provenance, not a current action;
3. the Kim/Svendsen 353.15 K pair for endpoint enthalpy and finite heat
   pairing; and
4. the Amundsen 353.15 K loaded-density row as a supporting property check,
   with pressure explicitly missing.

The record must include exact wheel, packet, parameter, reaction and thermal
hashes; all requested outputs with phase/unit/basis; balances and charge;
root/branch status; partial values and failure diagnostics; and native
derivative identities/statuses. It must not claim numerical or physical
qualification until the proposed physical criteria are reviewed and the
source-basis/carrier assumptions are stated in the receipt.

The dependency boundary is deliberately narrow:

- generic #87/#89/#90 diagnosis can proceed before a settled MEA parameter
  adoption decision;
- #84 consumes the source/reference definitions in this document;
- #85 receives the finite family inventory and may close with no code;
- #61 owns the evaluator adapter, application candidate selection,
  reaction-coordinate adoption and any conditional reaction-action design;
- MEA input preparation and qualification are independent of lithium;
- absorber physical qualification consumes accepted MEA thermodynamics, while
  absorber interface preparation can proceed earlier.

## Current status gaps

- The exact finite source-to-provider conversion remains with #84; the
  infinite-dilution R1--R3 offsets and the historical R4/R5 trial-pressure
  contraction are not accepted finite-state mappings.
- The retained evaluator cannot run against current f909/wheel-9f73 without the
  finite #61 adapter and current status/enthalpy mapping.
- Current solved-state actions expose EOS model actives, not reaction
  correlation coefficients; reaction fitting remains a conditional #61 design
  and adoption decision.
- Zhang's MEA ideal-gas Cp correlation is a source-backed candidate with
  unreported uncertainty; it is not an experiment or adopted thermal input.
- No replay, qualification or parameter adoption has been performed.

## Decisions still required

Only these material decisions remain after the source inspection:

1. Review and accept, revise or reject the proposed observable-specific
   physical screens before new acceptance predictions.
2. Have #84 define and qualify the generic reference/action boundary for the
   row-specific source conventions.
3. Have #61 provide/approve the finite adapter and choose the
   reaction-coordinate candidate/reference treatment; any reaction action
   remains conditional on that design.
4. Have #85/#87 state the exact EOS active-parameter family/order and the
   separate heat derivative action or an owner-approved heat-fit deferral.

Matin's direct-to-derived classification is resolved by this handoff as
evidence, not left as an owner question. Missing pCO2 covariance, unspecified
source gauge precision and blank Amundsen pressure remain disclosed limitations
without creating acquisition prerequisites.

No predictive qualification, Engine build/install, slow campaign, application
transfer, merge or source-code edit was performed in this preparation slice.
