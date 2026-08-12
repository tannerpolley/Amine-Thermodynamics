# Predictive reactive VLE regression roadmap

MEA execution issue: [MEA-Thermodynamics #53](https://github.com/tannerpolley/MEA-Thermodynamics/issues/53), child of the coupled-regression workstream issue #13.

## Decision

The planned endpoint is one predictive, coupled reactive-VLE parameterization for MEA–H₂O–CO₂. The current unified Engine can evaluate the required polar, dielectric, and Born physics, but it cannot yet regress the coupled reactive observations. Its public Regression interface currently admits only pure-saturation and fixed-state-pressure observations. Engine issues [#30](https://github.com/tannerpolley/ePC-SAFT/issues/30) and [#31](https://github.com/tannerpolley/ePC-SAFT/issues/31) own the missing general observation families.

No current MEA result establishes a predictive M5 parameterization. The retained M0–M5 calculations are diagnostics. The current planning identifiers in `reactive_vle_model_configurations.json` replace those informal labels with explicit physics factors.

## Scientific model

The final calculation solves the five-reaction, nine-species liquid together with a vapor containing neutral CO₂, H₂O, and MEA. Ions remain liquid-only. Vapor fugacities come from the EOS; ideal vapor is allowed only as an explicitly compared low-pressure approximation.

The physics comparison is factorized:

- neutral polarity: no explicit multipoles, CO₂ quadrupole only, H₂O/MEA dipoles only, and full DD+QQ+DQ;
- association: current fixed topology versus a source-fixed CO₂ induced-association topology;
- electrostatics: the retained diagnostic basis versus corrected SSM+DS Born with a qualified relative-permittivity model.

DD, QQ, and DQ are not three independent fit switches. With all physical moments present, DQ follows automatically. Molecular moments stay fixed to source values. The neutral segment and association parameters must be refitted for each polar formulation so dispersion does not continue to hide the polarity that the explicit term now represents.

SSM+DS is a fixed model choice, not a continuous fit coordinate. MEA Born and relative-permittivity parameters cannot be promoted from the current pressure and speciation rows: the library still lacks qualified loaded static-permittivity and direct MEAH⁺/MEACOO⁻ activity evidence. The inherited MEA relative-permittivity value of 32 is therefore provisional and cannot qualify the corrected electrostatic configuration.

## Data use

The current mixed-observation candidate set contains 121 pCO₂ rows and 198 direct-positive or explicit aggregate speciation observations. `reactive_vle_cross_validation.csv` assigns every candidate to one of five whole-campaign folds, but does not yet admit any row for scoring because source-backed residual scales and an immutable Data-packet identity remain open. After those gates close, model form and active coordinates are chosen using campaign-blocked cross-validation. The final estimation then uses every admissible in-domain row.

The planned first joint qualification domain is 313.15–353.15 K because it contains both admitted pCO₂ and speciation evidence. It is not all executable under the present reaction sources: R4 and R5 currently end at 323.15 K. The 333.15 K and 353.15 K rows therefore remain assigned to campaign folds but cannot enter the joint fit until S5 qualifies new R4/R5 coefficients over that domain. Lower-temperature speciation is support evidence. Pressure data above 353.15 K are a later domain-extension challenge. Cross-validation metrics support transfer claims; residuals after the all-data refit support calibration claims only.

Residuals retain each observable's reported basis and use source uncertainty where available. A missing uncertainty does not authorize an arbitrary tuning weight: the source or measurement method must support a preregistered scale before execution. Promotion is decided separately for pCO₂, speciation, volumetric, dielectric, and activity evidence rather than by one aggregate objective that can hide a failed family. Rank and conditioning are checked before profile likelihoods and campaign-blocked bootstrap uncertainty.

## Parameter order

The executable order is frozen in `reactive_vle_parameter_stages.json`:

1. freeze source rows, campaign blocks, and immutable Data/Engine identities;
2. refit neutral pure parameters separately for each polar formulation;
3. fit neutral binary interactions, then test induced association only after its source topology is complete;
4. certify a fixed-T,P homogeneous reactive tracer through Engine issue #30;
5. constrain the MEAH⁺/MEACOO⁻ segment block while Born and reaction terms remain fixed;
6. reconsider physically named R4/R5 A/B/C/D coefficients only after the EOS and ion blocks are qualified;
7. fit true bubble/VLE observations through Engine issue #31;
8. select by campaign-blocked evidence, refit on all admissible in-domain data, quantify uncertainty, and promote one parameter set.

Fitting every table entry simultaneously is excluded. It would let neutral dispersion, polar attraction, association, ionic solvation, binary interactions, and reaction constants compensate for one another while matching the same pCO₂ curve.

## Immediate work

The next executable scientific task is source closure for S1 and S2: complete the pure-MEA property package, bind source-valued molecular moments, and finish primary binary MEA–H₂O and physical CO₂-solubility tables. These inputs can qualify neutral parameters without waiting for reactive regression. In parallel, the upstream Engine issues can admit the two generic observation families. No application-owned optimizer or copied thermodynamic equation should be added here.

The manuscript remains unchanged until the coupled fit, cross-validation, uncertainty, immutable-artifact replay, and predictive gates pass.
