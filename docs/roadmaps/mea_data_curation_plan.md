# MEA Data Curation Plan

## Data status categories

Use these labels:

- `present_machine_readable`
- `present_md_needs_extraction`
- `expected_md_needs_extraction`
- `local_literature_lead`
- `source_pending`
- `not_used`
- `rejected_with_reason`

## Priority source status

| Data family | Current status | Target use | Target folder | Notes |
|---|---|---|---|---|
| Wong 2015 Raman high-pressure MEA speciation | present_md_needs_extraction | validation first; possible Phase 2/3 target | `data/reference/MEA/ChEq/` | Repo-local Markdown exists under `docs/papers/md/`; extract tables/figure data into machine-readable CSV before use. |
| Amundsen 2009 CO2-loaded MEA density/viscosity | present_md_needs_extraction | validation/regularization | `data/reference/MEA/density_viscosity/` | Repo-local Markdown exists under `docs/papers/md/`; extract density/viscosity tables into machine-readable CSV before use. |
| MEA-H2O dielectric constants | local_literature_lead | `f_solv` evidence and dielectric mixing | `data/reference/MEA/dielectric/` | Uyan/Cleeton/Schick digests give dielectric-convention leads; no promoted MEA-H2O table exists yet. |
| loaded-MEA pH/electrochemical data | source_pending | H3O+/OH- validation only if scale is clear | `data/reference/MEA/pH/` | Requires source search and user-supplied/downloaded articles. |
| direct MEAH+ salt or carbamate salt osmotic/activity data | source_pending | independent ionic activity evidence | `data/reference/MEA/ionic_activity/` | Do not misuse ethanolammonium acetate/hexanoate as MEACOO- evidence. |

## Required extraction columns

### Wong Raman speciation

- source
- DOI
- temperature_K
- pressure_bar or pressure_kPa
- MEA_weight_fraction
- CO2_loading_molCO2_per_molMEA
- species
- value
- value_basis
- uncertainty
- extraction_method
- notes

### Amundsen density/viscosity

- source
- DOI
- temperature_K
- pressure
- MEA_weight_fraction
- CO2_loading_molCO2_per_molMEA
- density
- density_units
- viscosity
- viscosity_units
- uncertainty
- extraction_method
- notes

### MEA–H2O dielectric

- source
- DOI
- temperature_K
- pressure
- MEA_mole_fraction
- MEA_weight_fraction
- water_mole_fraction
- relative_permittivity
- uncertainty
- correlation_or_table
- notes

### pH/electrochemical

- source
- DOI
- method
- pH_scale
- temperature_K
- pressure
- MEA_weight_fraction
- CO2_loading_molCO2_per_molMEA
- pH
- calibration_notes
- usability_flag

### ionic activity/osmotic

- source
- DOI
- salt_identity
- solvent
- temperature_K
- molality
- osmotic_coefficient
- mean_ionic_activity_coefficient
- density
- uncertainty
- constrains_species
- usability_flag

## Current extraction tasks

### Wong 2015

Source Markdown:

`docs/papers/md/Wong et al. - 2015 - Chemical speciation of CO2 absorption in aqueous monoethanolamine investigated by in situ Raman spec.md`

Target files:

- `data/reference/MEA/ChEq/Wong_2015_Raman_speciation.csv`
- `data/reference/MEA/ChEq/Wong_2015_Raman_metadata.csv`

Required use boundary:

- Use as validation first after extraction and QA.
- Do not fold into the MEAH+/MEACOO- fit until extracted rows, pressure/loading metadata, and uncertainty/conversion assumptions are explicit.

### Amundsen 2009

Source Markdown:

`docs/papers/md/Amundsen et al. - 2009 - Density and viscosity of monoethanolamine + water + carbon dioxide from (25 to 80) °C.md`

Target files:

- `data/reference/MEA/density_viscosity/Amundsen_2009_density.csv`
- `data/reference/MEA/density_viscosity/Amundsen_2009_viscosity.csv`
- `data/reference/MEA/density_viscosity/Amundsen_2009_metadata.csv`

Required use boundary:

- Use as validation or regularization only after the coupled speciation state used for each density/viscosity row is documented.
- Do not infer ion parameters directly from density/viscosity rows without an explicit model state.

### MEA-H2O dielectric

Target files:

- `data/reference/MEA/dielectric/MEA_H2O_dielectric_sources.csv`
- `data/reference/MEA/dielectric/MEA_H2O_dielectric_values.csv`

Required use boundary:

- Keep MEA `f_solv` fixed until direct MEA-H2O dielectric/activity evidence is extracted.
- Treat water-only Floriano/Nascimento and MDEA-water Hsieh-style correlations as convention leads, not direct MEA-H2O data.

## Pending source categories

Loaded-MEA pH/electrochemical data and direct MEAH+ salt or carbamate salt osmotic/activity data remain `source_pending`. Use `docs/prompts/MEA_ePCSAFT/WEB_SOURCE_SEARCH_PROMPT_AFTER_APPROVAL.md` only after user approval.
