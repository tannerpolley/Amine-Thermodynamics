# MEAH+/MEACOO- Volumetric Evidence and Identification Path

## Scope and claim boundary

This package prepares a falsifiable, future native regression for the
provisional one-segment `MEAH+` and `MEACOO-` ePC-SAFT parameters. It does not
execute a fit, assign a unique experimental volume to either ion, promote the
historical seeds, or establish predictive/source-complete parameters. The
current disposition is **additional-data-required** and execution remains
fail-closed.

## Measurement boundary

Marcus, *Biophysical Chemistry* 124 (2006) 200–207,
[DOI 10.1016/j.bpc.2006.04.013](https://doi.org/10.1016/j.bpc.2006.04.013),
establishes the governing boundary: density yields a volume for an
electroneutral salt solution. Partitioning that result between individual ions
requires an extra-thermodynamic convention. This package therefore admits
electroneutral solutions and never an isolated-ion density.

Shamshina et al.,
[DOI 10.1016/j.gce.2021.07.001](https://doi.org/10.1016/j.gce.2021.07.001),
report preparation and precipitation of the exact neutral salt,
2-hydroxyethylammonium (2-hydroxyethyl)carbamate. This establishes experimental
feasibility but supplies no volumetric oracle. The bounded search recorded on
2026-07-23 found no numerical liquid, aqueous partial-molar, crystal, or solid
density for that exact salt. This is an unresolved search result, not proof
that no measurement exists.

## Acquired numerical evidence

### Exact-cation carboxylate analogs

Augusto et al.,
[DOI 10.1021/acs.jced.1c00687](https://doi.org/10.1021/acs.jced.1c00687),
Table 2, pp. 1314–1315, supplies 84 direct density observations for aqueous
2-hydroxyethylammonium acetate and hexanoate: seven ionic-liquid mole fractions
at each of six temperatures from 298.15 to 363.15 K and ambient pressure
81.5 ± 0.5 kPa. Density is normalized to g/cm³ while the reported dry
ionic-liquid mole-fraction basis is preserved. The open primary PDF has SHA-256
`7d1589ab1cd9423af357568815ca1aa6dd4a7fc3620b00c7739418daae3749c8`.

Dhage et al.,
[DOI 10.1021/acsomega.5c13309](https://doi.org/10.1021/acsomega.5c13309),
Table 3, p. 18171, supplies 44 direct densities at 298 K for aqueous
ethanolammonium acetate, propionate, butanoate, and pentanoate. Its reported
excess molar volumes are retained separately as derived observations and are
independently reproducible to 0.01 cm³/mol from the rounded table inputs. They
must not be counted as independent residuals beside the parent densities. The
open primary PDF has SHA-256
`9185359f823c75cd63a0e2d1d7895242505fe630c952cdb8ba546e0f612ede2f`.

Amirchand and Singh,
[DOI 10.1016/j.molliq.2022.118845](https://doi.org/10.1016/j.molliq.2022.118845),
identify relevant acetate, butanoate, and hexanoate tables from 298.15 to
313.15 K. The numeric primary tables were not lawfully accessible during this
pass. No values were copied from snippets, inferred, or substituted; the source
remains an explicit acquisition gap.

All source identities, licenses, artifact hashes, table locators, and admission
limits are in
`data/reference/MEA/volumetric/volumetric_source_manifest.csv`. The 128 direct
analog densities and 44 reported-derived volumes are retained in separate raw
and derived CSVs under `data/reference/MEA/volumetric/`.

### Bulk reactive-MEA evidence

The repository's Amundsen table contains exactly 103 direct density rows: 35
unloaded and 68 CO2-loaded aqueous-MEA observations from 25 to 80 °C. Stored
absolute uncertainty is 0.0005 g/cm³ for unloaded rows and 0.002 g/cm³ for
loaded rows. Loaded density is a bulk reactive-state observable; it depends on
speciation, reaction constants, every mixture parameter, and the EOS reference
basis.

The 2011 Maiti, Bourcier, and Aines paper,
[DOI 10.1016/j.cplett.2011.04.080](https://doi.org/10.1016/j.cplett.2011.04.080),
reports **2.8 Å³ per absorbed CO2 for MEA**, not 3.5 Å³. A later LLNL report
(`LLNL-JRNL-643475`) separately reports approximately 3.5 Å³ per CO2 and a
modeled 4–6 Å³ local carbamate contraction. These bulk/atomistic quantities are
plausibility context, not independent single-ion volumes and not standalone
regression targets. Their manuscript hashes and exact admission limits are in
the source manifest.

Canonical Matin, Jakobsen, Böttinger, and Wong records provide population
information. The combined row contract retains measurement role separately
from lifecycle and objective role, including direct positives, reported
zeros/upper bounds, aggregates, balance-inferred rows, ambiguous calibration
records, contextual rows, and held-out rows. Only explicitly eligible direct,
aggregate, or upper-bound observations may enter the corresponding future
objective.

## Evidence matrix

| Evidence | Status | Information supplied | Limit |
| --- | --- | --- | --- |
| Individual `MEAH+` or `MEACOO-` density | physically non-unique | none without a convention | macroscopic electroneutrality |
| Exact salt isolation | verified | material identity and feasibility | no density value |
| Augusto exact-cation analog density | 84 direct rows | shared-cation packing and temperature response | cation and anion remain coupled |
| Dhage exact-cation analog density | 44 direct rows | multi-anion shared-cation leverage | one temperature; counterions remain coupled |
| Dhage excess molar volume | 44 reported-derived rows | contraction diagnostic | derived from the same densities |
| Amirchand analog tables | primary identity verified; numeric extraction blocked | potentially useful temperature and infinite-dilution leverage | closed numeric tables |
| Amundsen unloaded/loaded density | 35 + 68 direct rows | bulk mixture and carbamation response | coupled to speciation and all mixture terms |
| Canonical speciation roles | 1,070 row memberships | species and aggregate population constraints | inferred and ambiguous roles are not independent targets |
| Maiti 2011 / later LLNL report | verified context | bulk carbamation direction and scale | not an isolated-ion or direct fit target |
| Exact aqueous salt density | unresolved | highest-value missing discriminator | requires simultaneous chemical assay |

## Parameter identifiability

A single salt cannot separate cation and anion terms. Multiple carboxylates
supply common-cation leverage only after their anion parameters and covariance
are independently sourced or jointly regularized. Density is most informative
about packing/size but also responds to dispersion and interactions. Reactive
density additionally couples to reaction constants and species populations;
speciation constrains populations but cannot uniquely identify all size,
dispersion, Born, and interaction terms.

The machine-readable map in
`data/reference/MEA/manifests/ionic_parameter_observable_map.csv` therefore
freezes the initial model to `MEAH+` sigma and epsilon plus one regularized
`MEACOO-` sigma correction. Both one-segment conventions and Born diameters
remain fixed. `k_ij(MEAH+,MEACOO-)` remains fixed unless a recorded pre-fit
amendment shows structured residuals and independent sensitivity; it may
replace, not simply enlarge, the active correction block.

## Frozen staged plan

1. **Shared-cation analog stage.** Fit common `MEAH+` size and dispersion to
   direct analog densities with every counterion term fixed to an immutable
   source-bound prior or included in declared joint regularization. Do not
   double-count derived excess volumes.
2. **Carbamate correction.** Apply one regularized `MEACOO-` size correction
   through an electroneutral reactive state. Maiti evidence adjudicates
   plausibility but cannot supply the missing prior uncertainty.
3. **Reactive-MEA refinement.** When installed native Regression and
   Equilibrium derivatives are admitted, evaluate Amundsen density and eligible
   speciation residuals from the same constrained state. Reaction constants,
   Born terms, trace ions, and all other interactions remain fixed.
4. **Independent validation.** The volumetric split freezes 153 future-training
   and 78 validation observations by complete source/salt/temperature or
   MEA-fraction/temperature/loading groups. The existing 147-training/
   220-validation pressure/speciation split remains immutable and separate.
5. **Fail closed.** Reject a candidate that fails constraints, matches density
   but not speciation, depends materially on a start/prior/bound, has an
   ill-conditioned active block, or omits a failed state.

The complete objectives, scaling, bounds and their limited status, deterministic
multistart policy, diagnostics, receipts, and stop conditions are frozen in
`analyses/phase3/ionic_epcsaft_regression/ionic_volumetric_fit_preregistration.json`.

## Direct measurement path

The highest-value experiment is a 298.15 K vibrating-tube density series for
purified aqueous exact salt over six concentrations, paired with quantitative
speciation, water content, and CO2 inventory. The bounded request in
`docs/ePC-SAFT/meah-meacoo-direct-density-request.md` preserves raw instrument
and assay evidence and treats solid pycnometer or crystal density as secondary
packing evidence.

## Current disposition

The MEA-side evidence package and preregistration are complete enough to expose
the blockers honestly, but not to run or promote a fit. The disposition is
`additional-data-required`: counterion priors/regularization, installed native
density/regression derivatives, and ideally direct exact-salt aqueous density
with simultaneous speciation are still required.
