from __future__ import annotations

from time import perf_counter

from MEA.epcsaft_runtime import (
    SPECIES,
    build_mixture,
    dataset_label,
    diagnostic_composition,
    is_finite_payload,
)


def _safe_call(name: str, func, errors: list[dict[str, str]]):
    try:
        return func()
    except Exception as exc:
        errors.append({"diagnostic": name, "error": repr(exc)})
        return None


def run_smoke_case(
    *,
    mea_weight_fraction: float = 0.30,
    temperature_K: float = 313.15,
    loading: float = 0.30,
    pressure_Pa: float = 101325.0,
) -> dict:
    x = diagnostic_composition(loading=loading, mea_weight_fraction=mea_weight_fraction)
    started = perf_counter()
    mixture = build_mixture(temperature_K, x)
    state = mixture.state(temperature_K, x, P=pressure_Pa, phase="liq")
    elapsed_ms = 1000.0 * (perf_counter() - started)

    errors: list[dict[str, str]] = []
    fugacity = _safe_call(
        "fugacity_coefficient_terms",
        lambda: state.fugacity_coefficient(natural_log=True, return_contribution_terms=True),
        errors,
    )
    ares = _safe_call(
        "residual_helmholtz_terms",
        lambda: state.residual_helmholtz(return_contribution_terms=True),
        errors,
    )
    diagnostics = _safe_call("state_diagnostics", state.state_diagnostics, errors)
    rel_perm = _safe_call("relative_permittivity", state.relative_permittivity, errors)
    activity = _safe_call("activity_coefficient", state.activity_coefficient, errors)

    required = {
        "pressure_Pa": state.pressure(),
        "molar_density_mol_m3": state.molar_density(),
        "mass_density_kg_m3": state.mass_density(),
        "residual_enthalpy": state.residual_enthalpy(),
        "residual_gibbs": state.residual_gibbs(),
        "compressibility_factor": state.compressibility_factor(),
    }
    if not is_finite_payload(required):
        raise RuntimeError(f"Required ePC-SAFT diagnostics were not finite: {required}")

    return {
        "dataset": dataset_label(),
        "species": list(SPECIES),
        "case": {
            "MEA_weight_fraction": mea_weight_fraction,
            "temperature_K": temperature_K,
            "temperature_C": temperature_K - 273.15,
            "CO2_loading_mol_CO2_per_mol_MEA": loading,
            "pressure_Pa": pressure_Pa,
        },
        "x": {name: float(value) for name, value in zip(SPECIES, x)},
        "required": required,
        "optional": {
            "fugacity_coefficient_ln": fugacity,
            "residual_helmholtz": ares,
            "state_diagnostics": diagnostics,
            "relative_permittivity": rel_perm,
            "activity_coefficient": activity,
        },
        "diagnostic_errors": errors,
        "runtime_ms": elapsed_ms,
    }
