# Aqueous amine ePC-SAFT evidence and parameterization plan

## 1. Decision

The MEA program now targets one explicit-electrolyte, nine-species model with
CO2-water induced association fixed. Model selection compares only two Born
and relative-permittivity formulations:

| Configuration | Association | Electrostatic formulation |
|---|---|---|
| Shell Born, solvent-only | Schick-Pabsch reciprocal CO2-water 2B topology | Solvent-only relative permittivity |
| Shell Born, ion-suppressed | Same fixed topology | Ion-fraction-suppressed relative permittivity |

Neutral pure and binary parameters are qualified before reactive fitting.
Reactive pressure does not determine neutral binary interactions, Born
diameters, or relative-permittivity coefficients by itself.

## 2. Target system

The liquid species are CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+,
and OH-. The independent reaction set is:

1. water autoprotolysis;
2. MEA protonation;
3. carbamate hydrolysis;
4. CO2 hydration to bicarbonate;
5. bicarbonate dissociation to carbonate.

The incipient vapor contains the declared neutral species. Charged species are
liquid-only. The equilibrium calculation simultaneously enforces reaction
equilibria, elemental balances, electroneutrality, phase normalization,
mechanical equilibrium, and neutral-species chemical-potential equality.

The residual Helmholtz energy contains hard-chain, dispersion, general-site
association, Debye-Huckel, and Born contributions. The relative permittivity is
evaluated from the selected solvent-composition formulation. Reaction
correlations use one declared standard-state convention and remain fixed until
the physical parameter blocks are qualified.

## 3. Fixed induced-association topology

Schick et al. (2023), using the Pabsch et al. (2020) parameterization, assign
CO2 one donor and one acceptor site and retain reciprocal CO2-water cross
edges. The MEA implementation uses:

- one `a` and one `b` site on CO2;
- reciprocal CO2(a)-H2O(b) and CO2(b)-H2O(a) edges;
- cross energy `1212.85 K` from the arithmetic energy rule;
- cross volume `0.04509`;
- zero CO2 self-association.

This interaction represents the physical CO2-water precursor interaction. It
does not replace or duplicate carbamate formation in the explicit reaction
network. A separate CO2-MEA chemical-association edge is not used.

## 4. Literature evidence

| Source | System and useful evidence | Use in this project |
|---|---|---|
| Fakouri Baygi and Pahlavanzadeh (2015) | MEA-H2O-CO2 PC-SAFT, MEA association alternatives, Cai MEA-water VLE | Neutral MEA candidates and a source-faithful baseline reproduction |
| Uyan et al. (2015) | Explicit-ion aqueous MDEA ePC-SAFT with reaction activities and neutral isofugacity | Numerical and formulation comparison for explicit-electrolyte amines |
| Wängler et al. (2018) | Electrolyte amine phase-equilibrium calculations | Independent reactive-electrolyte implementation comparison |
| Cleeton et al. (2020) | Competitive MDEA-H2S-CO2 electrolyte calculations | Multi-acid-gas transfer and residual-trend evidence |
| Bülow et al. (2021) | MDEA, sulfolane, CO2, and H2S with Born solvation and solvent-composition permittivity | Binary-first parameter sequence and high-loading limitation evidence |
| Schick et al. (2023) | CO2 solubility in aqueous and organic electrolyte solutions | Fixed CO2-water induced-association topology and altered-Born comparison |
| Figiel, Yu, and Held (2025) | Solvation-shell-modified Born and nonlinear permittivity for electrolyte properties | Screened-Born equations, ion inputs, and independent evidence targets |

The MDEA sources demonstrate a workable sequence: qualify pure and binary
properties, freeze those values, then evaluate reactive mixtures. Their amine
and ion parameters are not transferred to MEA without matching species,
standard states, and parameter definitions.

## 5. Parameter ownership

| Parameter family | Evidence used | Current treatment |
|---|---|---|
| H2O and CO2 pure parameters | Held/Schick/Pabsch source family | Fixed during MEA-water qualification |
| MEA `m`, `sigma`, `epsilon/k`, association topology | Pure MEA vapor pressure and density plus independent MEA-water evidence | Compare source-backed candidate families |
| `k_MEA,H2O` | Cai and additional MEA-water VLE, density, and caloric observations | Fit only after the pure family is fixed |
| `k_CO2,H2O(T)` | Physical CO2-water solubility | Fit with induced association fixed |
| `k_CO2,MEA` | Physical neutral evidence when available | Start at zero; do not infer from reactive pressure alone |
| Trace carbonate and water ions | Reviewed electrolyte sources with matched definitions | Fixed during principal-ion estimation |
| MEAH+ and MEACOO- size/dispersion | Direct and aggregate speciation, volumetric evidence, and source-backed priors | Estimate only identifiable directions |
| Born diameters and solvation factors | Solvation, transfer, and activity evidence | Fixed or independently constrained before reactive fitting |
| Relative-permittivity parameters | Unloaded and loaded solution measurements | Compare direct and screened formulations independently of pressure fitting |
| Reaction correlations | Source correlations with declared temperature domains | Fixed initially; reopen only after EOS qualification |

## 6. Neutral qualification

### 6.1 Pure components

The retained water family uses the Held 2B parameters and its
temperature-dependent segment diameter. Candidate MEA families must be
evaluated with their own source association topology. A binary interaction
value fitted with another water or MEA family is only an initial value.

### 6.2 MEA-water

Cai et al. (1996) provide 29 isobaric VLE rows at 101.33 and 66.66 kPa. The
101.33 kPa series trains `k_MEA,H2O`; the 66.66 kPa series independently tests
pressure-level transfer. Each measured state contributes component
log-fugacity equalities. The exact Engine derivative with respect to the active
binary coordinate is checked against centered finite differences.

The existing Baygi 3B-MEA/2B-water and 3B-MEA/4C-water reproductions are
diagnostics because their fixed-state residuals retain strong composition
trends. The next pass evaluates source-backed MEA association candidates under
the fixed Held water family and retains the smallest candidate that improves
both pressure levels.

### 6.3 CO2-water

Physical CO2-water data identify the temperature-dependent binary interaction
under the fixed induced-association topology. Fit and challenge pressure ranges
remain separate. The resulting `k_CO2,H2O(T)` is frozen before any reactive MEA
fit.

## 7. Electrostatic comparison

Both retained configurations use solvation-shell-modified Born. The practical
MEA candidate uses the Figiel-style ion-fraction suppression law and its
source-fixed discrete choices. A fixed-parameter sensitivity at 313.15 K
rejected original-Born and shell-Born solvent-only controls because they found
vapor-scale rather than liquid-scale roots under the current parameter set.
Direct dielectric, solvation, transfer, and activity observations are still
needed to constrain the retained electrostatic parameters independently.

Missing MEAH+ or MEACOO- solvation evidence does not create another freely
fitted pressure coordinate. It yields a source-centered prior or a retained
uncertainty interval whose effect is reported explicitly.

## 8. Regression sequence

1. Freeze observation identities, source groups, reaction definitions, and the
   immutable Engine wheel.
2. Select the neutral MEA pure and ordinary-association family.
3. Fit `k_MEA,H2O`, `k_CO2,H2O(T)`, and `k_CO2,MEA` on physical binary data.
4. Constrain the retained shell-Born ion-suppressed formulation on independent evidence.
5. Estimate the smallest full-rank MEAH+/MEACOO- block using speciation and
   volumetric observations.
6. Fit coupled reactive pressure and same-state speciation with shared global
   parameters and local equilibrium states.
7. Inspect rank, conditioning, active bounds, source-group residuals,
   temperature trends, and start sensitivity.
8. Reopen only physically named reaction-correlation coefficients supported by
   remaining multi-temperature structure.
9. Select by source-blocked validation, refit on all admitted observations,
   quantify uncertainty, and retain one complete parameter set.

## 9. Numerical method

The current reduced-space calculation solves each equilibrium state inside the
parameter objective. It is scientifically valid but expensive. The mature
formulation should also support one sparse simultaneous NLP: experiment-local
phase compositions, densities, and reaction coordinates; shared global model
parameters; and one summed pressure/speciation/caloric objective. Scientific
parameter staging stays the same under either numerical formulation.

Fast development uses cached compiled states, exact total derivatives, one or
two workers, and representative rows. Full source collections run only for a
retained candidate. Solver residual and balance tolerances are not weakened to
improve fit statistics.

## 10. Manuscript claim boundary

The manuscript may claim a selected predictive MEA parameterization only after
the complete parameter table, source-separated validation, all-row accounting,
pressure and speciation results, uncertainty analysis, and immutable-wheel
replay are available. Until then, the calculations establish formulation and
parameter sensitivities rather than predictive completion.
