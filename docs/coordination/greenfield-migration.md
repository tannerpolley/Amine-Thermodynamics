# Greenfield migration consumer specification — MEA-Thermodynamics

Status: **notebook incumbent adopted for the authorized #61 working delivery;
bounded final-wheel replay complete; predictive qualification remains pending**.

This document is the MEA input-preparation handoff for Engine issues #84, #85,
#87, #89, #90 and #61. It records the current application consumer inputs and outputs,
the source and parameter limits that are visible in the repositories, and the
smallest useful first replay. The owner adopted the exact notebook incumbent
for this working delivery; this records an application input decision and does
not qualify its predictive error or the Engine wheel. The adapter carries the
remaining reference/action limitations as typed results.

## Inspection boundary and snapshot identity

The current application repository was inspected read-only at
`/home/tnnrpolley21/Workspaces/Engineering/MEA-Thermodynamics`, HEAD
`3b2071197e801401162f24ff7d0aa99518369c26` on `main`. The independent draft
clone was inspected at
`/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-greenfield/downstream/MEA-Thermodynamics`.
The draft clone contains older copied analysis inputs; it is not silently
treated as the current application snapshot. This worktree now carries the
bounded adapter and focused checks described below; the main local application
checkout remains untouched.

The current application evaluator and its retained input identities are:

| item | current path | SHA-256 or identity | role |
|---|---|---|---|
| evaluator | `analyses/mea_parameter_bundle/scripts/shared_evaluation.py` | `8dfe427517918639b8514d2ba267d27b5672d5df9a8aabc6cbf240eb5953a5e2` | final-wheel state construction, bounded recovery, output/action capture and typed failure record |
| state packet archive | `analyses/mea_parameter_bundle/data/input/state-packet.json.gz` | `e9d3ea9903fec9b5239dddcfe5bb8449e9f1a1aff488f0900cc9a91479ba48ba` | current compact input packet |
| decompressed state packet | same archive, decompressed | `86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448` | byte identity for a replay |
| selected parameter record | `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json` | `568f7a5f6379acebacea584d707d5a3222db1022a85a4092b52553248e48524d` | owner-adopted working input, `document_id=mea-co2-h2o-nine-species-estimation-candidate-v1`, version 2; predictive error remains a result |
| source parameter snapshot | `analyses/mea_parameter_bundle/data/input/parameters.json` | `58793d354f393944ca0f5fd1640a11645417ddfe6331b955de728f86f0e0b195` | separate source/input record; not the evaluator's selected-parameter path |
| Engine wheel | `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-greenfield/build/environment-wheel/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl` | `c87846663349640ab115cb09f9b880caea71be973dfe685dc9bd0f8bf7b11072` | final non-editable wheel pinned by this adapter |
| Engine runtime source | — | `3f5d9ac87a70aebbefbbecef47fcb8ba39f56e6c` | final runtime source; build fingerprint `78937d2876bd90feaebbd7c28ae5ad6a7d1c6323fda9d3dab3440338e84dc202` |
| reaction source record | `data/reference/MEA/manifests/chemical_reaction_source_contract.json` | `39db0d7ef972dc7eb41328bdf2ec3f67f62c33fc2bf0fdc7bab471ade9aefb55` | source standard state, reaction rows and conversion metadata |
| thermal reference | `analyses/mea_parameter_bundle/results/calorimetry/current-selected-reference-thermochemistry.json` | `a24a6b3c8b506fc659fc1bbd8a470b55919ba93da23eea27ffdf882645706185` | current exploratory reaction-consistent thermal reference |
| calorimetry partition | `analyses/mea_parameter_bundle/data/input/calorimetry-observation-partition.csv` | `175e55ff7e238ee19957da9b028e0d957bd99b35aa5ec4145926a055542725d3` | calibration, holdout and source-lineage partition |
| density observations | `data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv` | `9047efb0281bff93d1769b12a3df50420d0b01ddd44ffd5041749ec0fb1fe622` | supporting density source rows |

The draft clone still has plain `state-packet.json` with SHA-256
`41017bcf727a486a8f3feb280e19c111a15c5dda5a3cca4e8c7dc5b051168fef`, the
older selected-parameter file with SHA-256
`a9186c93759f2e2c02a6c913350ad06a244fff3f82503820c9962b3df8dd40d9`, and an
older evaluator with SHA-256
`6bc94e6c628aa212ccc4a6cce32226eed42aadaca6d06692e6c9be6984b6e32d`. Those
copied files remain untouched because the main application checkout remains
read-only. A future replay must use and record the current identities above, or
explicitly state that it is reproducing the older draft snapshot.

The pre-adapter evaluator was not runnable unchanged against the current
wheel: it called the retired
`equilibrium.general_reactive_equilibrium_problem_from_mapping` and
`equilibrium.solve(..., active_parameters=...)` surfaces. The worktree adapter
now maps the retained
requests to current `Problem`/`Phase`/`Amounts`/`Reaction(correlation)`,
call `solve_equilibrium`, and call `solved_state_actions` for the supported
state/EOS actions. The adapter must preserve current result statuses and
failure diagnostics. For heat, map the current phase
`TotalEnthalpy` observable (J/mol) times phase amount (mol) to extensive
endpoint `H` (J). The adapter emits the current native neutral and
reaction-reference declarations, including each source basis and pressure.
`reference_basis_unavailable` is reserved for an absent or malformed native
record; the first bounded physical replay and its limits are recorded below.

## Application target and declared topology

The target operating range for MEA and the absorber is the full **315--360 K**
range. Retained calibration inputs extend below and above that range and are
useful for source and continuation diagnosis, but a result outside 315--360 K
must be labelled as supporting or extrapolative. A published fit interval is
an applicability input to assess, not an automatic rejection gate. The
application must disclose extrapolation and its effect on each consumed
prediction; it must not call extrapolated results source-validated.

The first consumer specification keeps the existing nine liquid species, five reactions and
neutral-only vapor support. Phase discovery is deferred. The selected
parameter file is the owner-adopted working input for this sprint; it remains
unqualified for predictive process use and its measured prediction error is
reported separately from numerical convergence.

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
conventions and any provider transfer must remain in the reaction result record;
#84 owns the exact thermodynamically consistent conversion.

The current adapter constructs the native neutral reference from the declared
source ion-pair direction and scales every non-water ratio by `0.125`:
`[CO2, MEA, MEAH+, MEACOO-, HCO3-, CO3--, H3O+, OH-] =
[0.125, 0.125, 0.625, 0.25, 0.125, 0.125, 0.125, 0.125]`. The scale preserves the
positive, charge-neutral dilution direction and keeps the native
`1e-6,1e-8,1e-10,1e-12,1e-14 mol/kg` witness ladder within its `5e-5` terminal
criterion for the adopted nine-species parameter set. A second positive
charge-neutral direction must reproduce the per-reaction terminal contractions
within that same criterion before this reference path is called qualified.

## Reaction and thermal reference requirements

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

The owner adopted the exact selected R2/R4/R5 values in
`selected-current-best-parameters.json` for this working delivery. They are
the incumbent reaction input alongside the selected residual EOS values;
their measured predictive error remains a separate result. The selected
records are:

| reaction | selected correlation coefficients | source-basis handling |
|---|---|---|
| R2 | `a=232.33141533884407`, `b_k=-11105.640030520277`, `c=-36.7816`, `d=0` | already includes the documented `+4.0165349923` common-aqueous-molality offset; do not apply it a second time |
| R4 | `a=1.505015374192114`, `b_k=-1317.0489707842564` | selected analytic shift is carried with the Tong/Aroua source record |
| R5 | `a_k=3037.6399534696106`, `b=-1.0173150837285996`, `c=0.0004277` | selected analytic shift is carried with the Bates/Pinching source record |

R1 and R3 remain the source-record incumbent because the selected document
does not contain fitted records for them. At pivot `T_p=313.15 K`, the
reaction-temperature transformations are `Delta a = Delta h/(R*T_p)` and
`Delta b = -Delta h/R` for R1--R4, and
`Delta a_k = Delta h/(R*ln(10))` and `Delta b = -Delta h/(R*T_p*ln(10))`
for R5. These coordinates are not current Engine EOS active-parameter
actions. #84 still owns the exact source-to-EOS reference conversion; the
adapter must carry the adopted coefficient records to that conversion without
silently changing their basis.

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
background. Mole fractions and aggregate results are dimensionless. A solved
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
chemistry/basis specification case just below the 315 K target boundary. The exact
application-range speciation row is `Bottinger2008_state_058`, source row 58,
333.15 K (60 C), 30 wt% MEA and loading 0.415 mol/mol. Its packet feed is
`[0.4149, 0.99998, 7.910947365207347, 0.00001, 0.00001, 0.00008,
0.00001, 0.00011, 0.00001]` mol, with conserved totals `[2.415, 1.0]` and
fixed 101325 Pa. The retained outputs are MEA+MEAH+ `0.0687`, MEACOO-
`0.0417` and HCO3- `0.0042`, all dimensionless mole fractions, with the same
aggregate coefficient vector `[0,1,0,1,0,0,0,0,0]`. It is a current packet
calibration row and an application-range case; the grouped cross-validation
inventory marks this 333.15 K curve as a non-scoring domain extension pending
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
| Jou 1995 | `vle_obs_0206`, `Jou_1995_VLE.csv` row 35, active row `vle_0097`; 353.15 K, 30 wt%, loading 0.118, source total P 250 kPa | `calibration_derived_partial_pressure`; pCO2 0.0992 kPa from total pressure and calibrated gas composition; current target is 99.2 Pa `true-species-vapor-partial-pressure` | calibration, direct target classification | grouped holdout inventory reserves the Jou w=0.3/T=80 group for validation; the current packet's calibration use is therefore a lineage conflict to disclose, not an identical-state validation claim |
| Hilliard 2008 | `vle_obs_0130`, `Hilliard_2008_VLE.csv` row 24, active row `vle_0029`; 313.15 K, 30 wt%, loading 0.35, source total P 6.75 kPa | `calibration_derived_partial_pressure`; pCO2 0.0721 kPa (72.1 Pa), derived from calibrated FTIR/IR gas composition and measured total pressure | calibration, direct target classification | active grouped training row; source numeric uncertainty and covariance not transcribed |
| Xu 2011 | pressure holdout IDs `vle_obs_0265`--`vle_obs_0272` (source rows 1--8, nominal 100 C) and `vle_obs_0279`--`vle_obs_0288` (source rows 15--24, nominal 120 C), all 30 wt% MEA; source temperatures and loadings remain row-specific | `total_pressure_derived` from measured total pressure corrected by source Eq. (1) for N2 and calculated solvent vapor; pCO2 targets are reported in kPa and converted explicitly | not in the current packet; 18 rows were evaluated in the reaction-selection holdout | reserved validation by source/composition/temperature group; already accessed during candidate selection, so no longer untouched validation |
| Jakobsen 2005 | `Jakobsen2005_state_017`, `Jakobsen_2005_ChEq.csv` row 17; 313.15 K (40 C), 30 wt%, loading 0.11; retained values MEA 0.0985, MEAH+ 0.0065, aggregate 0.105, MEACOO- 0.0103, HCO3- 0.0001, CO3-- 0.0001 | true-species liquid mole fractions plus the MEA+MEAH+ linear aggregate; CO2/H3O+/OH- are balance-inferred; source covariance not reported | not in the current packet | canonical eligible but grouped `reserved_validation`; direct positive species/aggregate observations, held out as a complete source/composition/temperature curve |
| Böttinger 2008 | `Bottinger2008_state_050`, source row 50, 313.15 K/30 wt%/loading 0.487, and exact application-range `Bottinger2008_state_058`, source row 58, 333.15 K/30 wt%/loading 0.415 | true-species liquid mole fractions for MEACOO-/HCO3- and MEA+MEAH+ linear aggregate; CO2, MEA, MEAH+, CO3--, H3O+, OH- balance-inferred; covariance not reported | both are calibration targets in the current packet; state 050 values .0646/.0511/.0052 and state 058 values .0687/.0417/.0042 | state 050 is active grouped training; state 058 is grouped training metadata but marked non-scoring domain extension pending R4/R5 extension |

This inventory is the source/basis/role specification for #60 and #82. It does not
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
retained background only; this preparation did not replay it. The 120 C heat
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

| consumer | physical inputs and coordinates | consumed outputs | consumed action and returned-outcome requirements |
|---|---|---|---|
| reactive VLE | `T` K; solved `P` Pa; finite nine-species feed amounts mol; balance totals; declared phase supports; reaction constants after source-to-provider conversion | total pressure Pa; neutral-vapor mole fractions; CO2 partial pressure Pa; phase composition and evidence | #61 adapter to current `solve_equilibrium`; bounded pressure/root recovery; value rows for packet targets; `solved_state_actions` state-input blocks when requested by an anchor/recovery replay. Keep root/branch status and partial values. |
| liquid speciation | fixed `T` K and `P` Pa; finite feed amounts mol; nine-component molar masses; reaction/balance rows | true liquid mole fractions dimensionless; linear aggregates from stored coefficient vectors | value rows for current packet; no unrecorded finite-difference substitute for a missing native action. Aggregate mapping and source basis stay application-owned. |
| continuation/density | finite phase amounts mol, molar volume m3/mol, balance totals, continuation identity, model/reaction fingerprints | phase pressure Pa, molar density mol/m3, molar volume m3/mol, packing fraction, composition, phase amounts, chemical-potential-over-RT and evidence/status | continuation state and property actions seed bounded recovery and cache identity. Nonpositive, inconsistent or failed density is a failed attempt. Global search remains unestablished if not run. |
| paired heat | fixed endpoint `T/P`, finite composition and amounts, reference/formation enthalpy payload, paired loading endpoints | phase `TotalEnthalpy` (J/mol), phase amount (mol), extensive endpoint `H` (J), paired heat J/mol CO2 | current `solved_state_actions` value/status for the phase observable plus the #61 adapter's amount multiplication and finite pairing. No reaction/reference active-parameter derivative is currently available; do not finite-difference silently. |
| reaction-coordinate fit | candidate reaction coefficient identities and order; application-transformed values; T/P/feed coordinates | fixed-candidate output rows; any future reaction-coefficient Jacobian columns | retained fit receipts use old reaction actions. Current `SolvedStateActionDirection.active_parameters` covers EOS model actives only; #61 owns a conditional reaction-fit design and adoption decision. |

The retained old-wheel application evidence consumes values, recovery evidence,
density and reaction-fit output Jacobians. The current adapter maps the
retained requests to the public `Problem`/`solve_equilibrium` path and records
the available EOS/state action rows through `solved_state_actions`. It does not
invent a derivative tensor for packet rows, second-order actions, or reaction
coefficients. The six built-in fitting observation forms therefore do not by
themselves establish CO2 partial-pressure rows, paired caloric differences, or
reaction-coefficient fitting.

Every promoted active-parameter row must preserve caller parameter order,
output identity, unit and phase. A missing Jacobian block, changed coordinate,
nonfinite row or status mismatch is a hard derivative failure. Retain finite
central outputs when a derivative action fails, but mark the derivative result
unavailable; do not use it as a qualified fit row.

## #61 adapter Design boundary

This section specifies the bounded #61 replacement of the retired evaluator
surface. The owner authorized Engine plus MEA/Lithium implementation on
2026-09-22, excluding IDAES, modular-model and association-development work.
The five findings from the recovered independent review of candidate
`76ed8b824a9b67859f2590233b351631ca2d1a643ec5855ccad8bdb86d077f6a`
are corrected below. The owner-adopted notebook incumbent is the working
parameter input for this sprint. The public native reference chain is delivered
through the current wheel; predictive qualification still depends on its
explicit reference/thermal limits and broader evidence.

### Files, ownership and replacement

The sole production owner is
`analyses/mea_parameter_bundle/scripts/shared_evaluation.py`. The current
implementation uses `corrected_request`, `_problem_from_request`,
`_snapshot_from_result`, `_solve_in_child` and `solve_with_recovery` as one
private request-to-Problem mapping and one result/action-to-snapshot mapping.
Keep packet expansion, cache identity, provenance, forked timeout handling,
bounded recovery and failure receipts in this file. The mapping must use only
the public current interfaces imported from `epcsaft.equilibrium`:
`Problem`, `Phase`, `Free`, `Pinned`, `Amounts`, `Reaction`,
`ReactionLogPolynomial`, `SolvedStateObservable`, `SolvedStateObservableKind`,
`SolvedStateActionDirection`, `SolvedStateActionRequest`, `compile_problem`,
`solve_equilibrium` and `solved_state_actions`, together with top-level
`epcsaft.PropertyObservable`. Do not add a
compatibility shim, restore a retired name, import Engine source or create a
second solver. This import boundary describes the existing EOS-basis path;
R1–R5 construction uses the public reference-path representation delivered by
#84 through the current callables below.

The focused checks belong in
`analyses/mea_parameter_bundle/tests/test_shared_evaluation.py`. Mechanical
metadata readers in `generate_figure_data.py` may call the shared request decoder;
they are not a second adapter owner. `run_best_in_slot_campaign.py` was deleted in the
issue #96 port (below).
`evaluate_direct_absorption_heat.py` and `validate_thermal_references.py`
remain blocked on the #84 reference-basis decision. The direct calls in
`run_reaction_temperature_fit.py` remain a separate optional reaction-fit
extension. None of those three files is part of this adapter Build.

The owner-authorized replacement budget for this delivery is at most **+450
net lines** in the existing shared evaluator after deleting the retired
mapping/result path (gross edit ceiling +700); the focused test delta remains
at most **+100 net lines** (gross edit ceiling +120). This amendment covers the
full retired-adapter replacement, source-basis transport, typed native failure
mapping and retained physical evidence path. There are zero new source files
and zero dependency changes. Exceeding either amended ceiling stops the
implementation and returns the boundary for review; it does not justify hiding
code in another owner.

### Mechanical input mapping

The adapter must validate the fixed nine-component order before constructing a
problem:

`carbon-dioxide`, `monoethanolamine`, `water`,
`protonated-monoethanolamine`, `carbamate-anion`, `bicarbonate-anion`,
`carbonate-anion`, `hydronium-cation`, `hydroxide-anion`.

For each request, map the finite `feed_amounts_mol` by component id to
`Amounts`, map fixed `T` to a float in K, map fixed `P` to a float in Pa, and
map a solved pressure to `Free(initial)` in Pa. Map the finite liquid to
`Phase(..., kind="liquid", amount=Free())` and the incipient vapor to
`Phase(..., kind="vapor", amount=Pinned(0.0))`. Preserve the declared vapor
support exactly as the three neutral ids and the liquid support as all nine
ids. `topology_declared=True` remains explicit; phase discovery is not added.
The old balance matrix, conserved totals, reaction-phase ids and source
standard-state record stay in the application result record. Engine compilation
derives its own balance rows from the five `Reaction` stoichiometries; the
adapter checks the returned total amounts against the retained balance matrix
and charge before publishing a snapshot.

The old continuation object has no current public equivalent. A retained
liquid `Anchor` therefore supplies the liquid `Phase` composition guess; a
retained three-neutral vapor composition or the explicit packet vapor guess
must accompany it. Both phase guesses are required by the current initializer.
Without both, label the attempt as a cold start rather than claiming that an
anchor was consumed. Pressure closure and packing preparation remain with the
Engine; the adapter does not reproduce the packing equation. The anchor's
pressure is the single `Free` pressure guess. The feed remains the source of absolute phase
amounts, so the old hand-built `FinitePhaseStart` and balance correction are
deleted. The outer recovery plan keeps at most four unique starts: nearest
same-temperature anchor, cold packet start, nearest cross-temperature anchor
and one additional cross-temperature anchor. Duplicate signatures are skipped.
The packet's closed `[1, 10000000] Pa` interval is enforced on every pressure
guess and returned pressure. Current `Problem` has no caller-bound field, so
the adapter cannot constrain the internal iterates; it must refuse publication
of a returned out-of-interval state with `pressure_outside_packet`. Boundary
and just-outside numerical pressures falsify the final-state admission rule.

Already accepted EOS-basis polynomial rows may map one-for-one to
`Reaction(stoichiometry=..., correlation=...)`, with products positive and the
declared component order. The actual MEA R1–R5 rows stay on their explicit
source bases and are passed through the native neutral-reference contraction;
their conversion is not approximated as an application-side T-only polynomial.
#84 owns the generic reference implementation, including pressure conventions,
central curvature and the finite-limit witness. Existing infinite-dilution
offsets and historical pressure contractions remain evidence, not a pointwise
callback or scalar `equilibrium_constant` substitute. The following transforms
apply only to the source-form records before native reference evaluation.
`ReactionLogPolynomial` uses
`ln K = a + b/T + c ln(T/Tref) + dT` on the Engine EOS standard state. The
mechanical coordinate transforms are:

- for an input `a_s + b/T + c ln(T/(1 K)) + dT`,
  `a = a_s + c ln(Tref/(1 K))`, with `b`, `c`, `d` unchanged;
- R4's `ln K = a + b_k/T` maps to `(a, b_k, 0, 0)`;
- R5's `-log10 K = a_k/T + b + cT` maps to
  `(-ln(10)b, -ln(10)a_k, 0, -ln(10)c)`.

`Tref`, each reaction's admitted interval and the source standard-state id are
explicit fields in the normalized records; the adapter invents none. It carries
each source correlation and its source standard-state id as request metadata,
and carries the selected R2/R4/R5 coefficient values with
`selected_parameter_role="owner-adopted"`; it performs no source-to-EOS
conversion. The exact selected document therefore remains
`parameter_role="selected"`; an arbitrary candidate reaction vector remains
`parameter_role="candidate"`.

The worktree adapter's source-form normalizer emits the current public
`NeutralReference`/`ReactionReference` records. R1
and R3 retain the raw mole-fraction source basis and system-pressure path;
selected R2 is carried on the common aqueous-molality basis with its fitted
coefficients unchanged; selected R4/R5 use the common molality basis with
their 100 kPa reference pressure. R5's retained negative-log10 polynomial is
converted to the native natural-log polynomial representation only as a
source-form normalization. The native reference owner supplies the EOS
contraction and adds the declared common-molality scale exactly once.

Because current `Reaction` has no phase-id field, the adapter must verify after
compilation that all five reactions participate in the liquid support and no
reaction row is admitted in the neutral-only vapor. A mismatch is typed
`reaction_phase_support_mismatch` and is not repaired by adding application
phase logic.

### Result and action mapping

Call `solve_equilibrium(model, problem)` once per recovery attempt, then compile
the same `model`/`problem` pair and call `solved_state_actions` only for the
declared observables. Current result arrays are full component width per phase;
map them by declared phase ordinal and component id, never by a three-species
vapor slice or a hard-coded offset.

The snapshot preserves these central values and transformations:

| input-specification identity | current source and transformation | unit/status |
|---|---|---|
| `system-pressure` | `result.pressure[0]` | Pa, finite only on a successful state |
| `vapor-y-co2`, `vapor-y-mea`, `vapor-y-water` | neutral vapor `result.mole_fractions` entries | dimensionless |
| `co2-partial-pressure` | `result.pressure[0] * y_CO2` | Pa; never compare with total pressure |
| liquid/species outputs | liquid `result.mole_fractions` entries | dimensionless |
| linear aggregates | stored output coefficient vector dotted with the nine liquid mole fractions | dimensionless |
| phase anchor | `amounts`, `molar_densities`, `packing_fractions`, `1/rho`, composition and solved pressure | mol, mol/m³, dimensionless, m³/mol, Pa |
| phase residual chemical potential | central `PhaseResidualChemicalPotentialOverRt` action value | dimensionless; typed unavailable if unsupported |
| phase reference/residual/total enthalpy | central `PhaseProperty` values for `IdealEnthalpy`, `ResidualEnthalpy` and `TotalEnthalpy` | J/mol; missing thermochemistry stays typed |
| extensive endpoint enthalpy | liquid amount times `TotalEnthalpy` | J |
| paired heat | `[Δn_CO2 h_CO2,feed^ref − (H_b−H_a)]/Δn_CO2` | J/mol CO₂, then kJ/mol CO₂ for the existing report |

The adapter materializes output rows from these selectors with
`identity`, `value`, `status`, `unit` and optional first-order `jacobian`.
`EquilibriumResult.rows` are solver equations and must not be mistaken for
application output rows. `result.success`, `solver_status`, `message`,
`convergence`, `requested_tolerance_met`, raw `residuals`,
`classified_residuals`, their row metadata, topology event, reduced-Hessian diagnostic and
action-batch diagnostics become the evidence/failure record. A failed solve
retains finite diagnostics and no fabricated central values; a successful
central solve retains its values even when an action is unavailable. A finite
solver-success state missing the requested tolerance remains a warned
candidate; it cannot be published as an ordinary accepted result.

Preserve the exact `SolvedStateActionStatus` string for every requested action.
Map native convergence stops to stable failure-record codes (`infeasible`,
`left_domain`, `singular`, `nonfinite`, `stalled`, `budget_exhausted` or
`not_converged`) and keep the native message as the diagnostic. The old
`evaluation_timeout` and `engine_exception` codes remain reserved for the
fork/boundary layer. A phase mechanical class is not exposed by the current
result; record local-check evidence and typed
`mechanical_class_unavailable` rather than infer global stability or phase
discovery.

The base MEA slice consumes central values and **first-order** actions only:
one full-width all-zero A1 direction to obtain the returned enthalpy/chemical-potential
central values (empty direction lists are invalid), any explicitly selected state directions
`(dT [K], dP [Pa], dn_feed[9] [mol])`, and optional EOS active-parameter
directions in the declared `Mixture` active order. Free-intensive components
must be zero: a solved-pressure VLE request has `dP=0`, and a free-temperature
request has `dT=0`. Each A1 Jacobian column is a
separate request containing one direction; two directions in one request mean
an A2 mixed action, not two columns. Assemble the single-direction results in
the declared order and retain each column's availability. Two non-collinear
directions must independently reproduce their numerical A1 references.
There is no MEA requirement
for A2/A3, `PhaseLogActivity` film loading tangents, an outer A2 chain, vapor-Cp
derivatives or absorber process actions. Those belong to the deferred absorber
lane. Current `Mixture` active parameters are EOS families only; a reaction
coefficient identity is typed `reaction_action_unavailable` and is never filled
by a finite difference.

### Finite adapter cases, falsifiers and cost cap

The first adapter trace uses only these input-specification case ids:

1. `Bottinger2008_state_050` and `Bottinger2008_state_058` for the nine-species
   balance, aggregate map and lower/target-range liquid bases;
2. `vle_obs_0130` and `vle_obs_0206` for neutral-vapor support, solved total
   pressure, CO₂ partial pressure and the carrier-transfer/root diagnostic;
3. `kim2007_t80_r1_0.047` and `kim2007_t80_r1_0.090` for the two finite
   enthalpy endpoints.

The pressure-missing Amundsen density observation `AMU-DENS-081` (source
row 81, source-record CSV line 82) remains a separate supporting property datum.
It is not an equilibrium request or a seventh adapter case.

Before any physical claim, the adapter checks finite positive outputs, phase
support, material and charge balances, intensive reaction affinities,
interphase neutral-fugacity equality, unscaled trace-species chemical rows,
the pCO₂ identity,
aggregate dot products, `H = n_liquid h_total`, anchor round trips and the
two independent A1 numerical columns. Independent cold/warm starts
must agree within the existing diagnostic screens of pCO₂ relative spread
`1e-4` and liquid-composition absolute spread `1e-6`; disagreement remains a
typed branch/root result for #89/#90. Physical screens remain the existing
proposals: pCO₂ median absolute log-ratio `≤0.20` dex with 90% within `0.30`
dex, speciation aggregate/minor-ion screens as specified above, density relative
error `≤1.6%` at the supporting case, and paired-heat median absolute error
`≤10 kJ/mol CO₂` for calibration and `≤15 kJ/mol CO₂` for a later comparison.
These are separate from solver residual tolerances; the notebook incumbent's
measured prediction error remains a reported result rather than a convergence
or qualification gate.

The hard execution cap is 60 s per forked child, 900 s per state including all
recovery attempts/cache work, at most four unique starts per state, and
5400 s for the six-case trace. A timeout or cap exhaustion is a typed failure and
stops the trace; it does not trigger a larger campaign. The only allowed Engine
runtime is the non-editable wheel with SHA-256
`c87846663349640ab115cb09f9b880caea71be973dfe685dc9bd0f8bf7b11072`,
runtime source `3f5d9ac87a70aebbefbbecef47fcb8ba39f56e6c` (build fingerprint
`78937d2876bd90feaebbd7c28ae5ad6a7d1c6323fda9d3dab3440338e84dc202`). It is installed from
`/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-greenfield/build/environment-wheel/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl`.
Its affected installed-wheel gate and full native equilibrium/boundary suites
passed. All 444 native transport rows satisfy their existing criteria;
100 neutral-ternary action values moved by small floating-point amounts during
performance integration, recorded in the Engine performance notebook.
This supersedes the preparation wheel `f7902bf…` and the preceding `7a9a133a…`.
The current reference interface is now the declared #84 boundary, and the final
bounded adapter replay is retained below. The earlier `f4bd…` replay remains a
historical baseline; current numerical claims carry the final pinned wheel
identity and achieved raw tolerance status. Verify the identified non-editable
wheel; never import Engine source or sibling source.

### Independent blockers and optional work

The adapter mechanics are independently specified, and the bounded runtime
evidence is retained below. It does not establish predictive or physical
qualification. The native records carry the row-specific source-to-EOS boundary,
including R1--R3 system-`T,P` versus R4/R5 100 kPa conventions, finite
molality, thermal reference identities and gauge. The adapter reports
`reference_basis_unavailable` only when those records are absent or malformed;
it must not replace them with historical offsets, trial-pressure contraction or
a scalar K.

The owner-adopted reaction values are prepared inputs for this delivery.
Reaction-coefficient actions and any new reaction-coordinate fit remain a
separate optional #61 Design. The candidate transformations for an enthalpy
shift at pivot `T_p` remain provenance only:
`Δa=Δh/(R T_p)`, `Δb=-Δh/R` for R1--R4 and
`Δa_k=Δh/(R ln 10)`, `Δb=-Δh/(R T_p ln 10)` for R5. No reaction vector is
relabeled as a reaction action, and no predictive qualification is implied by
the parameter adoption.

### Reaction-coefficient action status

The retained `reaction:R4:correlation:a` and
`reaction:R4:correlation:b_k` values, their R5 pair and the centered
finite-difference agreement are **old-wheel evidence** from the retained
evaluator. They are not current f909/wheel-9f73 reaction-action evidence.
The current `SolvedStateActionDirection.active_parameters` contains only EOS
model actives declared on the `Mixture`; `ReactionLogPolynomial` coefficients
passed through `Reaction(correlation)` have no current reaction-coefficient
action slot. No current R4/R5 or R1--R3 reaction action is therefore available.

A fixed adopted reaction value is carried as a prepared source record until
the adapter maps it through #84's accepted reference path. Any further
reaction-coordinate fit requires a conditional #61 design and adoption
decision. #84's generic
reference chain and #85's EOS-family inventory must not silently absorb that
reaction-fitting extension. Do not substitute finite differences for the
missing consumed action or waive the action requirement.

For provenance, the old record's R4 central perturbation was +/-2.5 kJ/mol,
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

The bounded replay is runnable through the finite #61 adapter and its Stage-A
JSON/CSV/state records are retained below. The fixed nine-species/five-reaction
candidate values and neutral-vapor topology are evaluated through the current
public path. The retained R4 reaction-action record remains old-wheel evidence
and is not a current action check; a current reaction-coefficient action is
reported as the typed `reaction_action_unavailable` result until #61 settles a
separate design and adoption boundary.

The first replay is limited to the following cases: `Bottinger2008_state_058`
for the exact in-range liquid basis, `vle_obs_0130` for Hilliard pCO2,
`vle_obs_0206` for Jou pCO2 and the N2/carrier-transfer diagnostic, the two
endpoints of the Kim/Svendsen 353.15 K pair, and the Amundsen 353.15 K density
row as supporting evidence. The R4 action check is run on the two VLE cases
and the in-range speciation case only **if #61 first provides a current
reaction-action path**; otherwise retain the typed unavailable status and old
record as provenance. This is a bounded consumer trace, not a packet
campaign.

For each equilibrium state, retain at most four unique recovery starts:
nearest same-temperature anchor, cold packet start, nearest cross-temperature
anchor and one additional retained cross-temperature continuation anchor;
duplicate start signatures are skipped. Use the existing hard 60 s child-solver timeout and 900 s per-state
wall budget, including all recovery attempts and cache work. The thermal pair
has two such endpoint budgets. Record each attempt, elapsed time, status and
partial outputs; a budget exhaustion is a typed numerical failure. No broader
parameter or temperature campaign is authorized by this specification.

## Source and input inventory

| class | retained quantities and evidence | present limitation |
|---|---|---|
| measured/direct | Jou/Hilliard pCO2 rows; Böttinger NMR MEA+MEAH aggregate, MEACOO- and HCO3- rows; Matin titration inputs; Kim/Svendsen direct calorimetry; Amundsen density; Hilliard/Weiland solution-Cp observations | pCO2 uncertainty/covariance is unspecified; Böttinger has aggregate/proton-transfer basis; Matin species are derived from measured titration quantities; Amundsen pressure is blank; solution-Cp source values have their own stated mass bases |
| derived | finite molality from `x_i/(x_water*M_water)`; retained R1--R3 infinite-dilution scale offsets; reaction balance totals; aggregate coefficient maps; normalized finite feed and ionic seed vector; calorimetry endpoint pairing; reaction-consistent thermal reference polynomial | finite source-to-provider conversion and reference identities remain a #84 boundary; derived values are not independent measurements |
| assumed | ionic seed floors; fixed 101325 Pa all-liquid sentinel; retained pressure starts and recovery order; neutral-only vapor; zero finite vapor inventory and ideal incoming CO2 reference enthalpy; hydronium gauge; historical trial-pressure provider contraction | source p° and system-`T,P` conventions are source facts; packet assumptions can affect consumed predictions and must be disclosed or falsified separately |
| fitted/candidate | owner-adopted notebook residual EOS, association, Born/Debye-Huckel, packing, solvation, permittivity, interaction and reaction-coordinate values for this delivery | input adoption is explicit; scientific qualification remains `candidate_extrapolation`, with measured predictive error and source extrapolation disclosed as results |
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
RMSE of 0.2366 dex is retained as background, not as a pass gate. The speciation
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
| CO2 vapor partial pressure | median absolute `log10(p_pred/p_obs) <= 0.20` dex; at least 90% of eligible rows within 0.30 dex (about a factor of two); source/temperature group bias within 0.15 dex | retain source pressure conditions and missing uncertainty; do not score rows whose phase/basis definition is unresolved |
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
specification cannot express it.

## Finite Engine handoffs and demonstrated gaps

The following are the smallest concrete handoffs from this application slice:

| owner issue | demonstrated gap or bounded input | stopping condition |
|---|---|---|
| #85 active EOS families | The retained fixed-candidate/old-wheel evidence exercises `SegmentCount`, segment-diameter constant (`SigmaConstant`), `DispersionEnergyOverK`, `Kij`, `AssociationEnergyOverK` and `AssociationVolume`. `Lij` exists as a generic active coordinate but no MEA consumer or candidate slot demonstrates that it is required. The candidate also carries fixed segment-diameter(T), a reciprocal-temperature `k_ij` slope, Born/Debye-Huckel/packing diameters, solvation factors, relative-permittivity law and ion suppression; these are not automatically active fitting coordinates. Reaction-correlation coefficients are not EOS families and remain outside this inventory. | publish the finite EOS family/order actually needed by the first MEA replay; return a reviewed no-code result if existing families suffice |
| #84 source/reference chains | Own the finite molality and infinite-dilution source-to-provider conversion, row-specific system-`T,P` versus source `p°` handling, thermal K(T)/Delta H relation, reference formation enthalpy and hydronium gauge. Do not replace the source record with a scalar K-only input or silently absorb reaction fitting. | source rows, equations, units and reference identities are reviewable and reproducible at the exact target T |
| #87 trace/action accuracy | Trace pCO2 and true-species/aggregate rows, nonunit scales, partial-result retention, returned-outcome/failure meaning, current EOS active-parameter row Jacobians and the missing paired-heat/reference derivative action. | a caller-level trace shows each consumed row/action/returned outcome and a typed failure; no silent finite-difference or dropped failure remains |
| #89 density and pressure roots | Reproduce pressure-root/branch behavior on `vle_obs_0206`, including the solved bounds and retained start, and on any high-loading examples. Distinguish a missed root from a legitimately ambiguous branch. Reuse the existing density owner and retain the Amundsen pressure-missing limitation. | reviewed reproduction classifies each failure/branch and states whether an implementation change is authorized |
| #90 initialization/continuation | Reproduce the known equilibrium-temperature start sensitivity using the evaluator's same-temperature, cold, cross-temperature and continuation anchors. | bounded start/continuation diagnosis identifies a reproducible failure class or establishes that no Engine change is required for the selected cases |
| #61 MEA application adoption | Provide the finite adapter from the retained evaluator to current Engine APIs using the owner-adopted notebook incumbent. Reconcile selected R2/R4/R5 shifts with source-centered correlations and the omitted R1/R3 fit records. Any reaction-coefficient action/fit remains conditional on this design. | explicit adapter/status mapping with calibration, transfer and limitation language; no silent reaction-action promotion |

There is no demonstrated need here for PH/PS/UV, phase discovery, transport,
finite-rate chemistry, a broad optimization-domain campaign, or new physics.
The absorber and MEA can consume the declared neutral-vapor and thermal
contracts without adding those capabilities.

## First replay and dependency boundary

With the finite adapter implemented and the current wheel identified, the first
reviewable evidence block from the native reference path is:

1. `Bottinger2008_state_050` for species order, balance, aggregate map and
   source basis, with `Bottinger2008_state_058` as the exact 333.15 K
   application-range speciation row;
2. `vle_obs_0130` and `vle_obs_0206` for solved pressure, neutral vapor
   support, CO2 partial pressure, source-basis/carrier-transfer assumptions and
   pressure-root diagnostics. Fixed adopted reaction values may be mapped;
   the retained R4 action record is old-wheel provenance, not a current action;
3. the Kim/Svendsen 353.15 K pair for endpoint enthalpy and finite heat
   pairing; and
4. the Amundsen 353.15 K loaded-density row as a supporting property check,
   with pressure explicitly missing.

The record must include exact wheel, packet, parameter, reaction and thermal
hashes; all requested outputs with phase/unit/basis; balances and charge;
root/branch status; partial values and failure diagnostics; and native
derivative identities/statuses. It must not claim numerical or physical
qualification until the proposed physical criteria are reviewed and the
source-basis/carrier assumptions are stated in the result record.

The dependency boundary is deliberately narrow:

- generic #87/#89/#90 diagnosis can proceed with the owner-adopted notebook
  working input;
- #84 consumes the source/reference definitions in this document;
- #85 receives the finite family inventory and may close with no code;
- #61 owns the evaluator adapter, the adopted working-input record and any
  conditional reaction-action design;
- MEA input preparation and qualification are independent of lithium;
- absorber physical qualification consumes accepted MEA thermodynamics, while
  absorber interface preparation can proceed earlier.

## Current status gaps

- The exact finite source-to-provider conversion remains with #84; the
  infinite-dilution R1--R3 offsets and the historical R4/R5 trial-pressure
  contraction are not accepted finite-state mappings.
- The worktree adapter now runs the current status/enthalpy mapping against the
  retained request shape and emits the native reference records; the first
  nine-species replay and its finite-limit diagnostics are recorded below.
- Current solved-state actions expose EOS model actives, not reaction
  correlation coefficients; reaction fitting remains a conditional #61 design
  and adoption decision.
- Zhang's MEA ideal-gas Cp correlation is a source-backed candidate with
  unreported uncertainty; it is not an experiment or adopted thermal input.
- No predictive qualification has been performed; notebook parameter adoption
  and the final bounded replay for this working delivery are complete.

## First bounded MEA replay (historical f4bd baseline)

The first bounded replays used the adopted parameter record
`568f7a5f6379acebacea584d707d5a3222db1022a85a4092b52553248e48524d`, packet
`86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448` after
decompression, and wheel
`f4bdcbb919e169800f9efdf3fc96ee2930924d6e2afd9962f395e503353595e9`. Both
states were fixed-`T,P` cold starts through the current adapter and returned a
finite all-nine liquid state with no material-balance, charge-balance or
pressure-range validation error. These original files retain their recorded
wheel hash; their `engine_commit` field names the preceding checkout rather
than the then-uncommitted runtime and must not be used as an exact source
identity. The final replay below has an exact committed runtime identity.

| state | `T` / `P` | requested outputs `(MEA+MEAH+, MEACOO-, HCO3-)` | liquid density / amount | maximum reference terminal change |
|---|---:|---:|---:|---:|
| `Bottinger2008_state_050` | `313.15 K` / `101325 Pa` | `(0.06771945435, 0.04449868051, 0.005214861586)` | `53402.2745654 mol/m³` / `8.91121565360 mol` | `4.06398024e-5` |
| `Bottinger2008_state_058` | `333.15 K` / `101325 Pa` | `(0.06949829276, 0.04271999906, 0.002420751756)` | `51307.3088194 mol/m³` / `8.91120318997 mol` | `4.23485551e-5` |

All five reaction diagnostics in each state were `Available`. R1--R3 used the
system pressure `101325 Pa`; R4--R5 used their declared `100000 Pa` source
pressure. The native solver reached its available floor (`3.57e-8` classified
residual against the requested `1e-10` row tolerance), so the adapter retains
`requested_tolerance_met=false` as evidence while classifying the state as
evaluated from the finite physical checks. These values are working replay
results; the notebook's measured prediction error remains a result and no
predictive qualification is claimed.

As a finite-reference direction check, the same 050 feed, parameters, source
correlations, `T` and `P` were evaluated with the positive charge-neutral
vector
`[0.03125, 0.03125, 0.15625, 0.0625, 0.03125, 0.03125, 0.03125, 0.03125]`
for `[CO2, MEA, MEAH+, MEACOO-, HCO3-, CO3--, H3O+, OH-]`. Its per-reaction
terminal contractions differed from the adopted `1/8` vector by at most
`2.26e-7`, with every witness below `5e-5` (`R1=1.0160e-5`,
`R2=1.0160e-5`, `R3=2.0320e-5`, `R4=3.75e-12`, `R5=3.87e-12`). This is a
reference-path consistency check only; it does not introduce a second
equilibrium or parameter fallback.

The sequential Stage-A result files also contains the 315--360 K fixed-pressure
sentinel grid at the 050 feed, with empirical-extrapolation labels retained:

| sentinel | status | `(MEA+MEAH+, MEACOO-, HCO3-)` | liquid density / maximum reference change |
|---|---|---:|---:|
| `315 K` | evaluated | `(0.06735473631, 0.04486327385, 0.005306073714)` | `53333.1842869 mol/m³` / `4.07876e-5` |
| `330 K` | evaluated | `(0.06581899338, 0.04639698405, 0.006064820369)` | `52763.3116723 mol/m³` / `4.20638e-5` |
| `345 K` | evaluated | `(0.06557879319, 0.04663106967, 0.006827032189)` | `52155.5969058 mol/m³` / `4.34666e-5` |
| `360 K` | `non_evaluable: budget_exhausted` | unavailable | 200 iterations; failure retained |

The Stage-A result files record the fixed-`T,P` source packet, residual and classified
residual rows, solver attempts, reference diagnostics and physical phase data
once in compact JSON plus homogeneous CSV form:
`results/runs/reaction-temperature-fit/stagea-current-wheel/`
(`stagea-current-wheel-replay.json` and `stagea-current-wheel-rows.csv`).
The exact historical f4bd 050 state record is
`results/runs/reaction-temperature-fit/stagea-current-wheel/states/c8f363da921c24fbfa049cb77b129b7b1de23cf87299a8c4e8c06879c4cde16d.json`
(SHA-256 `d2c8a1359a40c70604174dac7bd54b3515cba5856a4e4d0d7f75b7aebdbbe3b2`).
Pure-water branch checks at 313.15 K returned `Liquid`, `stable_root_count=2`
and `converged` density roots: `55069.7257442 mol/m³` at 101325 Pa and
`55069.7089139 mol/m³` at 100000 Pa. These are source-reference and sentinel
results, not predictive qualification.

## Final current-wheel MEA replay

The final bounded producer used the adopted parameter record
`568f7a5f6379acebacea584d707d5a3222db1022a85a4092b52553248e48524d`, packet
`86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448`, Engine
commit `3f5d9ac87a70aebbefbbecef47fcb8ba39f56e6c`, and wheel
`c87846663349640ab115cb09f9b880caea71be973dfe685dc9bd0f8bf7b11072`. The
replay retained the compiled raw stationarity vector from
`compiled_problem.evaluate(result.coordinates)` for every successful state;
all evaluated rows below have raw maxima below `1e-10` and native requested
tolerance met.

| case | result and raw stationarity maximum | retained values |
|---|---|---|
| `Bottinger2008_state_050` | evaluated; `1.7053025658242404e-13` | `(MEA+MEAH+, MEACOO-, HCO3-) = (0.06771945760549275, 0.04449867725550945, 0.005214865150114531)`; hydronium `2.31334915458689e-10` |
| `Bottinger2008_state_058` | evaluated; `1.7763568394002505e-13` | `(0.06949829335217282, 0.04271999846289983, 0.002420752508060337)` |
| `315 K` sentinel | evaluated; `1.4210854715202004e-13` | `(0.06735473960064955, 0.044863270560672026, 0.0053060772812227805)` |
| `330 K` sentinel | evaluated; `2.2737367544323206e-13` | `(0.06581899676215526, 0.046396980663928215, 0.0060648238778367265)` |
| `345 K` sentinel | evaluated; `1.1368683772161603e-13` | `(0.06557879639989843, 0.046631066446415965, 0.006827035407960529)` |
| `360 K` cold | `non_evaluable: budget_exhausted` | retained as the cold-start failure |
| `360 K` warm from 345 K | evaluated after the retained cold failure; `1.1368683772161603e-13` | `(0.06589580914322377, 0.04629691404387695, 0.007525040310383141)` |

The same final replay solved the free-pressure neutral-vapor cases. The vapor
composition comes from the native pinned zero-amount phase block, and the
partial pressure is the native vapor CO2 mole fraction times the solved system
pressure:

| case | solved pressure (Pa) | vapor `(yCO2, yMEA, yH2O)` | CO2 partial pressure (Pa) | raw maximum |
|---|---:|---:|---:|---:|
| `vle_obs_0130` | `6745.3292512713515` | `(0.004850021209289166, 0.00033854874057571494, 0.9948114300501352)` | `32.71498993230467` | `8.526512829121202e-14` |
| `vle_obs_0206` | `41385.4021244` | `(0.0013610884224680645, 0.002396067635315561, 0.9962428439422164)` | `56.32919169070609` | `1.7053025658242404e-13` |

The complete final producer records are under
`results/runs/reaction-temperature-fit/final-current-wheel/`, with the compact
replay JSON, homogeneous rows CSV, per-state diagnostics, cold failure and
warm recovery retained together. These are bounded working-input replays;
the adopted parameters are authorized working inputs, while predictive
accuracy beyond these comparisons remains to be established.
The packet's direct CO2 partial-pressure targets for 0130 and 0206 are 72.1
and 99.2 Pa, respectively. The converged predictions are therefore about 55%
and 43% lower. This is retained model discrepancy for subsequent comparison
or calibration, not a parameter-adoption or numerical-execution gate.

## Remaining capability and validation work

1. Compare the adopted model against the observable-specific physical screens
   and quantify model discrepancy over the broader retained data.
2. Extend #84's delivered fixed-temperature value/pressure boundary to the
   temperature, parameter and caloric responses consumed by the application.
3. Qualify reaction-correlation and EOS-parameter actions before using them in
   thermal or parameter fitting. Their present unavailability does not block
   the implemented central speciation and VLE calculations.

Matin's direct-to-derived classification is resolved by this handoff as
evidence, not left as an owner question. Missing pCO2 covariance, unspecified
source gauge precision and blank Amundsen pressure remain disclosed limitations
without creating acquisition prerequisites.

No predictive qualification, slow campaign, application transfer or merge was
performed in this preparation slice; the bounded adapter, current-wheel
replays and focused checks are present in the application worktree.


## Current-main replay and handoff — 2026-09-22

The adopted parameter file remains SHA-256
`568f7a5f6379acebacea584d707d5a3222db1022a85a4092b52553248e48524d`.
The bounded replay consumed Engine runtime `892c6687480259a6de6bbc8fa1721a35d06c997f`
and noneditable wheel `dc1d18d02fa560a5b518f4fb20be7e2254e8aa79dd62b3f6dfddf2107005d2b2`.
The new `current-main-adopted-comparison` result directory beside the earlier
`final-current-wheel` result record retains nine requests, eight successful states,
one cold 360 K failure and eight packet-target comparisons. Earlier c878 receipts
are unchanged. Packet calibration labels, selection exposure, source-range
extrapolation and the Böttinger 058 role conflict limit interpretation; this is
not independent predictive validation.

The full replay used evaluator v4 before the final diagnostic-only correction.
The separate `current-main-adopted-comparison-v5-cold-only` result record qualifies the
corrected failure serialization: native raw maximum 6.24741216, classified
maximum 0.00167100625 against 1e-10, requested tolerance false, MAXITER_EXCEEDED,
and no invented state or pressure. The successful 345-to-360 K warm result retains
raw/classified maxima 1.14e-13/2.50e-15. Failed-attempt evidence stays with its
actual attempt; the record-level failure fields all refer to the final attempt.
The current producer is evaluator v5; the corrected cold-only run was fresh.

The verified sum of per-case attempt times is 35.498388 s: VLE 0130 takes 13.919718 s
and VLE 0206 takes 17.273847 s. The earlier chat estimate of 26 s was incomplete waiting
accounting and is not a process benchmark. The separate cold refresh measured
0.524 s. No wheel build occurred and no further numerical process is running.

Resolution (2026-09-22): the adopted coefficients were fitted with the old adapter
under `exclude-same-sign-ion-pairs` (fit wheel `40fba7cf...`; UQ inventory row 102),
which is Figiel's like-charge rule including ion self-pairs. The migration's
`all-ion-pairs` runtime default (commit 8f8e4a2) was never an adoption decision; with
off-diagonal like-charge `k_ij=1` it kept ionic self-dispersion, a hybrid neither source
defines. The parameter record now declares exclusion explicitly and drops the seven
redundant same-sign `k_ij=1` entries (SHA-256 `868a5018...fcb7be`); the adapter injects no
dispersion default. Engine PR #107 (wheel `4368d0f1...`) removed the repeated
fixed-pressure reference work with bit-identical results (VLE medians 13.46->8.47 s and
15.32->8.77 s under the superseded all-pairs model). Under the fitted model, VLE 0206
from a cold packet start ends locally infeasible (residual 0.698 after 53 iterations),
while a start from the old Engine's liquid solution converges (residual 2.3e-13) to
pCO2 84.87 Pa (old Engine 84.93 Pa; observed 99.2 Pa): an initialization failure (#90),
not a missing equilibrium. Engine PR #109 (main `832380ad`, wheel `6cb2c2f0...`) moves the
pinned-vapor pressure seed by one fugacity step; the nine-case replay then evaluates 9/9
(`fitted-exclusion-6cb2`, 31.2 s, VLE 0206 cold at the warm-anchor state). Over all 79
solved-pressure requests from cold (`cold-start-sweep/cold-start-sweep.csv`, producer
`scripts/run_cold_start_sweep.py`), 69 -> 76 evaluate and total time falls 556 -> 380 s;
0128/0145/0227 regress and 0129-0131/0208 slow down because the packet liquid guesses
carry unspeciated molecular CO2 (x_CO2 8.9e-5 to 1.4e-3 against ~1e-6 speciated), so the
seed is the saturation pressure of a wrong liquid. The adapter's recovery plan now adds a
`speciated-liquid-start` after a failed cold packet start for solved-pressure requests: the
liquid alone is speciated at the packet pressure seed and replaces the packet liquid guess.
It recovers 0128, 0145 and 0227 at the baseline states (P and pCO2 within 1e-11 relative),
so all 79 requests evaluate from cold without anchors; earlier attempts are unchanged.

Engine main `c24261a7` (wheel `98b9a4fb...`, 2026-09-23) removes density-closure and
associating pressure-slope work (Engine PRs #111, #113, #114, #116, #118, #119) with
predictions unchanged to <=3e-11. The same 79-request cold sweep (label `main-c242`)
evaluates 79/79 in 121 s total (median 0.48 s per state), against 380 s for `cand-f7cf`.
Against the packet's observed true-species vapor pCO2 (calibration rows, derivable from the
sweep and the state packet), the adopted model gives mean ln(pred/obs) +0.34 / RMS 0.58 for
Hilliard2008 (31 states) and +0.05 / RMS 0.60 for Jou1995 (48 states): a model/reference
discrepancy recorded on Engine #61, not a solver effect.

Engine main `cb163066e683f278ab40fb5cf7069e3602119f96` (wheel
`3a69fd263ba073ea600fa7e45aa866337b11c2e4556329d337bb5e025a0eda9f`, 2026-09-23) is the
current pin after PR #124 merged. Its 79-request cold sweep (`main-cb16`) evaluates 79/79 in
116.662 s total (median 0.55 s); the maximum relative change in `pressure_pa` and
`co2_partial_pressure_pa` against the retained `pr124-d1b4` rows is 0.0 for both. Those
historical rows retain the wheel hash used for that run. The evaluator pins only the
SHA-256 of the wheel file at the recorded install URL (`direct_url.json`); it no longer
hashes the mutable greenfield `build/environment-wheel/` path, which every Engine rebuild
overwrites. The current Engine removed `Parameters.parameter_specs`, `with_values`,
`to_mapping`, `fingerprint` and `Mixture.parameter_fingerprint` and requires explicit Born
`c_shell`/`c_dielectric` and `ionic_dispersion`. Campaign scripts now read coefficient values
from the parameter mapping, obtain the adopted shell-Born constants (1, 1; model
configuration file) through `shared_evaluation.parameter_mapping`, and pass an explicit
mapping fingerprint to the state cache so candidate models cannot reuse selected-model
states. The frozen foundation `data/input/parameters.json` declares no ionic-dispersion rule
and the Born study's `AUTO` variants declare no Born constants; both now fail explicitly
rather than receive an invented default.

Issue #96 port on Engine main `7fa8aaf4` (wheel `e9fb8a47...3e62`, 2026-09-23): the figure,
permittivity and Kiepe CO2-water scripts now call only current Engine callables; retained
results were not regenerated. `generate_figure_data.py` reads temperature, loading and the
source continuation fingerprint from the packet request and takes reaction values from
`parameter_mapping()`; packet state `vle_obs_0186` reproduces the `main-cb16` sweep to
1.3e-12 in pCO2. Its incumbent check now reads the last `candidate_sha256` of
`results/parameter-record-history.csv`, which already records `868a5018...` (2026-09-22,
coefficients unchanged); the earlier check read only the historical permittivity comparison and
adoption record and so rejected the explicit-exclusion file. The Kiepe generator uses
`bubble_point` with a per-isotherm warm-start chain seeded at the first cold-converging
dilute composition; 38/39 rows reproduce the retained pressures to 4.3e-9 relative, and
`kiepe-313.20-13` (retained 22.43 MPa, dense CO2-rich branch) fails without a hand seed.
Born-study variants B and C use permittivity rules the Engine no longer admits.
`run_best_in_slot_campaign.py` is deleted: its optimizer coordinates (reaction coefficients,
ion solvation and Born diameters) and pCO2 observations are not `regression` coordinates or
kinds, and the retained grid campaign superseded it. The thermal chain stops on the missing
reference temperature derivative (Engine #84): `evaluate_direct_absorption_heat.py` and
`validate_thermal_references.py` raise `THERMAL_REFERENCE_UNAVAILABLE` on entry, and
`run_reaction_temperature_fit.py` raises it for the screen, candidate, parity and benchmark
modes and for heat groups of the full replay. Its pressure and speciation full-replay groups,
partial summary, adoption record and self-check remain. `--sensitivity-check` stops on missing
reaction-coefficient actions (Engine #61). The code behind these stops (anchored reference
construction, heat evaluation, thermal validation, screen, candidate, parity, benchmark and
sensitivity drivers) was deleted rather than kept unreachable; the retained results name
their producers, which Git history keeps for the #84 and #61 ports. `shared_evaluation` no
longer accepts a thermochemistry or active-parameter argument, and its records drop the
always-null `thermochemistry` field; as after any evaluator edit, the evaluator source hash
in the cache key sends new evaluations to new state records.

Engine main `83ac1126d8824dd2f1465c194be73c19ebc0cdb5` (wheel
`3eb502abf74c4bb9f48fcafbbe2f271e7bba7a70152ed2d998f10c4606741252`, 2026-09-23, PR #133 neutral-subset
admission fix) is the current pin. Its 79-request cold sweep (`main-83ac`) evaluates 79/79 in
139.7 s total at host load average 15--18 on 12 cores; the maximum relative change against the
retained `main-cb16` rows is 7.3e-13 in `pressure_pa` and 2.3e-11 in `co2_partial_pressure_pa`.
The wall time is not comparable with earlier rows recorded at lower load. The Kiepe CO2-water
generator gives the same 38/39 result on this wheel (`kiepe-313.20-13` infeasible, residual 0.250).
