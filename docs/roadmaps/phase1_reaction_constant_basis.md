# Phase 1 Reaction Constant Basis

Phase 1 uses the Smith-Missen-style ideal/apparent chemistry convention. Activities are set equal to mole fractions for the literature baseline.

## Verified basis

- `verified`: Baygi 2015 lists five explicit reactions for the apparent-speciation baseline:
  water autoprotolysis, CO2 hydration to bicarbonate, bicarbonate dissociation to carbonate, carbamate hydrolysis, and protonated-amine dissociation.
- `verified`: Baygi 2015 uses Edwards et al. (1978) for `R1-R3`, Tong et al. (2012) for `R4`, and Bates and Pinching (1951) for `R5`.
- `verified`: Baygi 2015 states that the `R4` carbamate-hydrolysis constant was reported on a molality basis and converted to a mole-fraction basis for the ideal-speciation workflow.

## Solver note

The Phase 1 speciation workflow now solves the explicit five-reaction, nine-species ideal Smith-Missen system in `src/MEA/smith_missen/ideal_speciation.py`. The older six-species code in `src/MEA/six_species/chemistry.py` remains only as the retained legacy pressure/parity path.

## Phase 1 rule

Do not mix these Phase 1 mole-fraction or apparent constants with later activity-based `K_a` expressions without an explicit conversion and a stated reference-state convention.

## Files

- Reaction manifest: [reaction_constant_manifest.csv](data/reference/MEA/manifests/reaction_constant_manifest.csv)
- Phase 1 analysis reaction table: [phase1_reaction_constant_table.csv](analyses/phase1_smith_missen_baseline/results/phase1_reaction_constant_table.csv)
