# Phase 1 Parameter Audit

This audit fixes the Phase 1 baseline choices to explicit local evidence instead of leaving them implicit in older scripts.

## Verified choices

- `verified`: Baygi 2015 screened MEA `2B`, `3B`, and `4C` association schemes against `2B` and `4C` water and selected `MEA 3B / H2O 4C` as the best neutral PC-SAFT baseline for the MEA-H2O system.
- `verified`: Baygi 2015 Table 3 reports `k_ij = -0.0520` for the selected `MEA 3B / H2O 4C` pair.
- `verified`: The retained repo neutral-parity workflow still uses the inherited `MEA 2B / H2O 2B` molecular row and `k_ij = -0.1800` from [src/MEA/epcsaft_neutral/parameters.py](/C:/Users/Tanner/Documents/git/MEA-Thermodynamics/src/MEA/epcsaft_neutral/parameters.py).
- `verified`: The retained six-species Smith-Missen chemistry path and the retained neutral ePC-SAFT parity path already reproduce the baseline pressure/speciation workflow used for continuity checks in this repo.

## Phase 1 decision

Phase 1 now distinguishes two different parameter roles:

- Historical literature choice:
  `MEA 3B / H2O 4C` with `k_ij = -0.0520` from Baygi 2015.
- Retained repo continuity choice:
  the inherited molecular row and neutral-parity `k_ij` in [src/MEA/epcsaft_neutral/parameters.py](/C:/Users/Tanner/Documents/git/MEA-Thermodynamics/src/MEA/epcsaft_neutral/parameters.py).

That split is deliberate. The literature choice answers the provenance question. The retained repo choice answers the reproducibility question for the current checkout.

## Scope boundary

- Phase 1 does not fit ionic parameters.
- Phase 1 does not move `f_solv`.
- Phase 1 does not use pressure-only data to infer ionic quantities.
- Phase 1 does not promote the activity-based ionic route as the baseline.

## Files

- Parameter inventory: [phase1_parameter_provenance.csv](/C:/Users/Tanner/Documents/git/MEA-Thermodynamics/data/reference/MEA/manifests/phase1_parameter_provenance.csv)
- Phase 1 analysis parameter table: [phase1_parameter_table.csv](/C:/Users/Tanner/Documents/git/MEA-Thermodynamics/analyses/phase1_smith_missen_baseline/results/phase1_parameter_table.csv)
