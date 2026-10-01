# MEA–H₂O–CO₂ evidence library

This directory is the single repository-owned entry point for experimental evidence, parameter provenance, and admission contracts used by the MEA–H₂O–CO₂ analyses.

## Scientific scope

The modeled species are CO₂, MEA, H₂O, MEAH⁺, MEACOO⁻, HCO₃⁻, CO₃²⁻, H₃O⁺, and OH⁻. Possible degradation products or prepared analog compounds remain separately identified; they are never silently folded into the nine-species reaction system.

## Directory map

| Path | Contents | Parameter regression status |
|---|---|---|
| `observations/vapor_liquid_equilibrium/` | Source tables, the 327-row canonical VLE ledger, and the 161-row active view | Governed by the admission and split manifests |
| `observations/reaction_constants/` | Reported dilute-MEA dissociation and carbamate constants, retaining finite-ionic-strength and infinite-dilution roles | Source extraction only; no target admission |
| `observations/liquid_speciation/` | Source-resolved and canonical liquid-speciation evidence | Governed by measurement role and target membership |
| `observations/calorimetry/` | Reported absorption and protonation heats with their sign and dose definitions | Existing admission files govern target use; new source tables alone admit no rows |
| `observations/density_viscosity/` | Direct aqueous-MEA density and viscosity evidence | Qualification evidence; target use is governed by the admission files |
| `observations/dielectric/` | Dielectric fields and documented evidence gap | No loaded-solution static dataset is admitted |
| `observations/ionic_activity/` | Direct target-ion activity evidence gap | No MEAH⁺/MEACOO⁻ activity dataset is admitted |
| `observations/ph/` | Equilibrium pH evidence gap | No source-complete loaded-MEA pH matrix is admitted |
| `observations/ionic_analog_volumetrics/` | Ethanolammonium carboxylate density and derived excess-volume evidence | Analog evidence only; not direct MEAH⁺/MEACOO⁻ measurement |
| `parameters/` | ePC-SAFT parameter evidence and source audit | Provenance evidence; not parameter promotion |
| `manifests/` | Admission, provenance, source status, model configuration, fit stages, and observation contracts | Authoritative machine-readable policy |

`manifests/data_library_inventory.csv` inventories every file, its hash, row count when applicable, and its library/admission tier.

## Near 30 wt% MEA literature inventory

The 2026-09-30 discovery pass is retained in `manifests/source_status_manifest.csv`;
queries and source-reading routes are recorded in `manifests/source_search_log.csv`.
`manifests/source_status_manifest.csv` owns publication identity, concentration and measurement basis,
temperature coverage, observation counts, access, extraction status and source caveats.
The file inventory continues to own file hashes and row counts.
`repo_extraction_status` owns the publication extraction fact. The legacy `status`
column duplicates that fact for the nine reconciled retained-extraction entries;
read `repo_extraction_status` for extraction coverage, including partial and diagnostic roles.
The remaining legacy `status` values also describe source workflow and are not a
second extraction authority.

The search includes 25–35 wt% aqueous MEA and reported 7 mol/kg water, 5 mol/L
or 5-normal solutions. These concentration bases remain distinct. A molarity or
normality requires the preparation temperature and density before conversion to mass
fraction. Dilute protonation and carbamate measurements are marked as supporting
reaction evidence; they are not concentrated loaded-solution pH measurements.

`scope_assessment` and `evidence_level` distinguish inspected primary passages,
publisher or database metadata, secondary literature tables and unresolved discovery
candidates. A blank count or range means unverified, never zero. Counts identify
their scope: equilibrium states, per-species values, derived constants or an entire
multiconcentration campaign. Retained counts are separate from published counts;
they must not be summed across reused experiments or repeated literature columns.
Mixed solvents, reference salts and degradation studies retain their composition
caveats. PDF attachment keys and SHA-256 hashes identify inspected local companions.

The discovery pass inventoried sources without extracting observation tables or changing
target membership. Subsequent authorized table extractions are recorded by publication in
`manifests/source_status_manifest.csv`; the source tables alone do not change admission.
The discovery pass does not establish exhaustive worldwide coverage. New Zotero
items remain pending because the configured Companion has no item-add or PDF
acquisition operation; duplicate checks used 546 live top-level items. Existing
items were left unchanged. The proposed tag is `mea-30wt-data-2026-09`.

## Admission model

Location in `observations/` does not by itself make a row a regression target. Measurement eligibility remains governed by `pco2_metrology_manifest.csv`, `speciation_target_membership.csv`, `vle_row_disposition.csv`, and the related source/provenance contracts.

`grouped_split_manifest.csv` preserves the immutable 147-training/220-reserved Gate-0 history. It is not the selection policy for the new predictive reactive-VLE campaign. The current mixed reactive-observation planning file is `reactive_vle_cross_validation.csv`. The pressure-first analysis freezes all 121 pCO₂ candidates into a diagnostic-only packet with whole-campaign training, model-selection, reserved, and domain-challenge roles. Its provisional log scales are transparent diagnostic weights, not source uncertainties, and do not admit rows or parameters for promotion. The 198 speciation candidates remain blocked on their same-state pressure and residual requirements. Neutral pure, binary, volumetric, dielectric, and activity families retain their own admission gates and require stage-specific partitions when their source packages close. Cross-validation results and all-data calibration residuals must be reported separately.

`reactive_vle_model_configurations.json` defines the factorized polar, association, and electrostatic comparisons. `reactive_vle_parameter_stages.json` defines the fit order and fail-closed upstream gates. These are planning and data contracts, not evidence that reactive fitting is currently executable.

## Basis and provenance rules

- Preserve reported temperature, pressure, composition, loading, molality, standard-state, and sign-convention bases.
- Record conversions as derived values with their rule; never overwrite the reported value.
- Keep direct, aggregate, balance-inferred, calibration-derived, model-derived, and fitted quantities distinct.
- Keep replicate, stock-solution, apparatus, source, and calibration groups together when assigning training or validation roles.
- Treat below-detection observations as censored evidence, not numeric zero.
- Treat microwave dielectric measurements and fitted dispersion limits according to their actual frequency basis.
- Treat analog salts and prepared byproduct mixtures as analog or byproduct evidence, not target-ion measurements.

Run `uv run python scripts/validate_mea_data_library.py` after changing this library.
