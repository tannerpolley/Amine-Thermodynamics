# Ion-dependent permittivity: declaration check

Issue [#388](https://github.com/tannerpolley/Amine-Thermodynamics/issues/388),
2026-11-16. **The probe stopped before observation replay or liquid-split
searches.** The pinned Engine exposes ion suppression as a replacement for
the adopted density–temperature law, but cannot combine the two. The orchestrator
selected the issue's capability stop after inspecting the numerical check
below. This is a declaration limitation, not a negative sensitivity result.

## Pinned Engine and declarations

Engine commit `391dfe5d64ede5036bf160bc6ae037ad5e14af32`, wheel SHA-256
`0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b`.
The wheel hash and every installed `epcsaft/` package file were checked against
the wheel before evaluation; no Engine source was imported or edited.

`epcsaft.Parameters.from_mapping` accepts these declarations:

- `model_families`: `kind: permittivity`, `choice: ion-fraction-suppression`;
  `model_coefficients`: `family: ion_fraction_suppression_coefficient`, with
  `value: {magnitude: alpha, unit: dimensionless}`.
- Alternatively, `choice: ion-specific-suppression` with a component
  coefficient `family: ion_specific_suppression_coefficient` on every ion.
- The adopted choice is `solvent-density-temperature`, consuming component
  `dielectric_volume` and `dielectric_temperature` coefficients.

The first two choices select the same native ion-suppression form, with
salt-free solvent permittivity calculated by solvent mass weighting of
component relative permittivities. They replace the density–temperature form.
Retaining the current choice and adding a scalar suppression coefficient
with identity `probe/alpha` gives exactly:

```text
ParameterError: unconsumed probe/alpha
```

Pinned source locators: `engine/src/epcsaft/parameters.py:457–462, 597–610`
maps the coefficient families; `engine/native/surface/parameter_builder.cpp:230–240,
280–290, 614–620` selects mutually exclusive forms and rejects unused
coefficients; `engine/native/contributions/electrolyte.hpp:157–164, 186–193`
returns the density–temperature and ion-suppression expressions separately.
These line numbers refer to the pinned commit in the read-only historical
clone `upstream/ePC-SAFT` in the main checkout.

## Why point matching does not preserve the adopted law

The direct evaluation used the adopted declaration
`analyses/solvent_specification_mea/inputs/endpoint.json` (SHA-256
`ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed`).
The illustrative, electroneutral composition was water 0.80, MEA 0.18,
MEAH+ 0.01 and carbamate 0.01, on a species mole-fraction basis; other species
were zero. This is a fixed-composition declaration check, not a reactive
equilibrium state or an observation row.

At 353 K, every neutral component's replacement relative permittivity was
set to the adopted model's value at 45,000 mol/m³, and the two original
dielectric coefficient families were removed from the replacement declaration.
The replacement then gives the following dimensionless relative permittivities:

| Form / coefficient | 45,000 mol/m³ | 40,000 mol/m³ |
|---|---:|---:|
| Adopted density–temperature law | 55.15795653250771 | 49.14040580667352 |
| Replacement, α = 0 | 55.157956532507704 | 55.157956532507704 |
| Replacement, α = 7.01 | 48.37568543457964 | 48.37568543457964 |
| Replacement, α = −1 | 56.28362911480378 | 56.28362911480378 |

The α = 0 replacement matches the anchor to floating-point rounding but is
12.246% above the adopted law at the second density. Its density derivative
is zero, whereas that of the current law at fixed temperature and composition
is nonzero. A point match therefore cannot preserve pressure and heat
derivatives or the composition dependence needed for liquid stability.
The α = −1 evaluation checks declaration admission only; it is not a
literature-calibrated coefficient or the requested loading probe.

## Scope and comparison limits

The retained [#265 comparison](../permittivity_temperature_loading/notebook.qmd)
perturbs coefficients within the density–temperature form. Replacing that
form here would mix the ion effect with a change of the solvent law, even
at α = 0. No pressure, speciation, heat, density or tangent-plane response
against #265 was computed, and none of the 54 discarded-fit split states
was searched. Split persistence is unknown for every proposed α.

The wheel-verified direct evaluations ran through `agent-heavy` using
`uv run --project <main-checkout> --no-sync python`; the measured evaluation
block took 0.01366 s, excluding imports, wheel verification and admission wait.
No campaign runtime was projected because the capability stop precedes the
campaign timing gate. No fit, parameter adoption, manuscript change or Engine
issue was made. The combined-law use case is filed as Engine issue tannerpolley/epcsaft#38.
