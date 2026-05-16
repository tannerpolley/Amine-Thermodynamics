# Package API Contract

## Boundary

`epcsaft` is a general-purpose EOS/property/equilibrium/regression package.

`MEA-Thermodynamics` is an application/manuscript project.

## Forbidden package public APIs

```python
fit_mea_absorption(...)
fit_co2_capture_column(...)
fit_lithium_extraction_parameters(...)
screen_lithium_extractants(...)
```

## Preferred generic API concepts

```python
ReactionSet(...)
EquilibriumProblem(...)
RegressionProblem(...)
TargetDataset(...)
PhaseSpec(...)
ParameterSet(...)
model.equilibrium(problem)
epcsaft.regress_parameters(problem)
```

## MEA-side wrappers

MEA-Thermodynamics may define internal wrappers to map MEA data and species to generic ePC-SAFT APIs.

Acceptable internal names:

- `build_mea_reaction_set`
- `build_mea_equilibrium_problem`
- `build_mea_regression_dataset`
- `render_mea_pressure_figures`
- `render_mea_speciation_figures`

These wrappers should not be requested as public ePC-SAFT package APIs.
