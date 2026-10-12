# MEA-H2O Dielectric Extraction Targets

This folder is reserved for machine-readable relative-permittivity data or correlations for MEA-H2O mixtures.

`agieienko-buchner-2024.csv` admits 14 unloaded compositions at 298.15 K
from Agieienko & Buchner (2024), ESI p. 2, Tables S1 and S2, for
issue #172 dielectric coefficient calibration only. None enters the reactive
pressure, species or heat objectives. Each row preserves composition,
both printed MEA concentrations, water concentration, measured density,
static permittivity, source hash and row locators. The 80.48 wt% sample
prints 13.47 mol/L in S1 and 13.50 mol/L in S2; sample identity joins them.

The ignored publisher PDF has SHA-256
`e928ae3242dc38612f0fbf44e7e1e42c296ca49e3638ac4ef2f08a6c50f0f5c2`.
All values were checked against its Table S1/S2 page. The ESI is not yet a
Zotero attachment; parent key `PUUZWHCS` and main attachment `NTTNUKEX`
identify the paper. S2's water endpoint comes from ESI Ref. 2:
Eiberweiser, Nazet, Hefter & Buchner (2015), J. Phys. Chem. B 119, 5270–5281.

Table S2 footnote a states relative static-permittivity uncertainty generally
better than 1%. Issue #172 uses `0.01 epsilon_s` as a declared fitting scale,
not an independent Gaussian standard deviation. Spectral-fit error is not
permittivity uncertainty. Main article §2.3 reports relative expanded density
uncertainty 0.0005. Measured density is comparison evidence only; the
coefficient reduction uses native EOS density at 101325 Pa, neglecting the
small unloaded protonation. Source and extracted-table hashes are retained
in `analyses/mea_parameter_bundle/results/permittivity-refit-172/inputs/source-admission.json`.

Do not promote MEA `f_solv` from pressure data alone.
