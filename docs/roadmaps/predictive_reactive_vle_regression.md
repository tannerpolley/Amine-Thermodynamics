# Predictive reactive VLE regression roadmap

The endpoint is one nine-species MEA-H2O-CO2 parameterization that predicts
CO2 partial pressure and liquid speciation on source-separated observations.
The Engine already supplies the generic homogeneous and reactive-bubble
equilibrium calculations. The remaining work is parameter qualification and
efficient multi-observation regression.

## Retained model

The liquid contains CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, and
OH-. The incipient vapor contains the declared neutral species. The calculation
uses PC-SAFT hard-chain, dispersion, general-site association, Debye-Huckel,
Born solvation, and a composition-dependent relative-permittivity model.

CO2-water induced association is fixed throughout the remaining program. It
uses the Schick-Pabsch reciprocal 2B topology, a cross energy of 1212.85 K,
and a cross volume of 0.04509. The only retained structural comparison is
direct Born with solvent-only permittivity versus screened Born with
ion-fraction suppression.

## Data and residuals

The reusable pressure collection contains 121 CO2 partial-pressure rows; the
speciation collection contains 198 direct-positive or declared aggregate
observations. Training, model-selection, and reserved campaigns remain grouped
by source. Each residual stays in its reported basis and uses source-backed
uncertainty where available. A missing uncertainty is resolved from the source
or measurement method before a row enters parameter selection.

## Parameter sequence

1. Freeze source rows, campaign groups, reaction definitions, and the immutable
   Engine wheel identity.
2. Qualify the retained H2O and MEA pure-component and ordinary-association
   parameters.
3. Fit `k_MEA,H2O`, `k_CO2,H2O(T)`, and `k_CO2,MEA` on their physical binary
   observations, one pair at a time, with induced association fixed.
4. Compare the two retained Born and permittivity formulations using independent
   dielectric, solvation, and activity evidence.
5. Constrain MEAH+ and MEACOO- size and dispersion directions with direct or
   aggregate speciation and volumetric observations.
6. Fit the smallest identifiable reactive parameter block to coupled pressure
   and same-state speciation observations.
7. Reopen reaction-correlation coefficients only when systematic
   multi-temperature residuals remain after EOS and ion qualification.
8. Select by source-blocked validation, refit on all admitted observations,
   quantify uncertainty, and retain one complete parameter table.

The immediate calculation is the Cai MEA-water binary qualification under the
retained neutral family. It is followed by physical CO2-water qualification,
then the two Born formulations. Reactive pressure fitting does not determine
neutral binary, Born, or relative-permittivity parameters by itself.
