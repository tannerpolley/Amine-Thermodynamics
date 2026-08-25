# MEA–H₂O–CO₂ evidence library

This directory is the single repository-owned entry point for experimental evidence, parameter provenance, and admission contracts used by the MEA–H₂O–CO₂ analyses.

## Scientific scope

The modeled species are CO₂, MEA, H₂O, MEAH⁺, MEACOO⁻, HCO₃⁻, CO₃²⁻, H₃O⁺, and OH⁻. Possible degradation products or prepared analog compounds remain separately identified; they are never silently folded into the nine-species reaction system.

## Directory map

| Path | Contents | Regression status |
|---|---|---|
| `observations/vapor_liquid_equilibrium/` | Source tables, the 327-row canonical VLE ledger, and the 161-row active view | Governed by the admission and split manifests |
| `observations/liquid_speciation/` | Source-resolved and canonical liquid-speciation evidence | Governed by measurement role and target membership |
| `observations/density_viscosity/` | Direct aqueous-MEA density and viscosity evidence | Qualification evidence; target use is manifest-governed |
| `observations/dielectric/` | Dielectric schema and documented evidence gap | No loaded-solution static dataset is admitted |
| `observations/ionic_activity/` | Direct target-ion activity evidence gap | No MEAH⁺/MEACOO⁻ activity dataset is admitted |
| `observations/ph/` | Equilibrium pH evidence gap | No source-complete loaded-MEA pH matrix is admitted |
| `observations/ionic_analog_volumetrics/` | Ethanolammonium carboxylate density and derived excess-volume evidence | Analog evidence only; not direct MEAH⁺/MEACOO⁻ measurement |
| `parameters/` | ePC-SAFT parameter evidence and source audit | Provenance evidence; not parameter promotion |
| `manifests/` | Admission, provenance, source status, model configuration, fit stages, and observation contracts | Authoritative machine-readable policy |

`manifests/data_library_inventory.csv` inventories every file, its hash, row count when applicable, and its library/admission tier.

## Admission model

Location in `observations/` does not by itself make a row a regression target. Measurement eligibility remains governed by `pco2_metrology_manifest.csv`, `speciation_target_membership.csv`, `vle_row_disposition.csv`, and the related source/provenance contracts.

`grouped_split_manifest.csv` preserves the immutable 147-training/220-reserved Gate-0 history. It is not the selection policy for the new predictive reactive-VLE campaign. The current mixed reactive-observation planning contract is `reactive_vle_cross_validation.csv`. The pressure-first analysis freezes all 121 pCO₂ candidates into a diagnostic-only packet with whole-campaign training, model-selection, reserved, and domain-challenge roles. Its provisional log scales are transparent diagnostic weights, not source uncertainties, and do not admit rows or parameters for promotion. The 198 speciation candidates remain blocked on their same-state pressure and residual contracts. Neutral pure, binary, volumetric, dielectric, and activity families retain their own admission gates and require stage-specific partitions when their source packages close. Cross-validation results and all-data calibration residuals must be reported separately.

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
