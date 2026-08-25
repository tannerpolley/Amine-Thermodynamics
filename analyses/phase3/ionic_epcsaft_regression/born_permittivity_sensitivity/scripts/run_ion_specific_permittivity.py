from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import statistics
import time

import epcsaft

from generate import (
    ANALYSIS,
    _canonical_sha256,
    _configuration,
    _evaluate_configuration,
    _source_states,
    _speciation_rows,
    _write_csv,
)


RESULTS = ANALYSIS / "results" / "ion_specific_permittivity"
BASE_ID = "shell_born_ion_suppressed"
COEFFICIENTS = {
    "zuber_exact_generic": {
        "protonated-monoethanolamine": 2.60,
        "carbamate-anion": 7.89,
        "bicarbonate-anion": 7.89,
        "carbonate-anion": 7.89,
        "hydronium-cation": 9.55,
        "hydroxide-anion": 13.96,
    },
    "zuber_charge_class": {
        "protonated-monoethanolamine": 2.60,
        "carbamate-anion": 7.89,
        "bicarbonate-anion": 7.89,
        "carbonate-anion": 7.89,
        "hydronium-cation": 2.60,
        "hydroxide-anion": 7.89,
    },
    "zuber_known_universal_fallback": {
        "protonated-monoethanolamine": 7.01,
        "carbamate-anion": 7.01,
        "bicarbonate-anion": 7.01,
        "carbonate-anion": 7.01,
        "hydronium-cation": 9.55,
        "hydroxide-anion": 13.96,
    },
}
NAMES = {
    BASE_ID: "Universal suppression (7.01)",
    "zuber_exact_generic": "Zuber known ions + generic organic-ion classes",
    "zuber_charge_class": "Zuber generic charge classes",
    "zuber_known_universal_fallback": "Zuber H+/OH- + 7.01 organic-ion fallback",
}
CASES = (
    (BASE_ID, NAMES[BASE_ID], "ion-fraction-suppression", None),
) + tuple(
    (
        configuration_id,
        NAMES[configuration_id],
        "ion-specific-suppression",
        coefficients,
    )
    for configuration_id, coefficients in COEFFICIENTS.items()
)
ALL_CONFIGURATIONS = tuple(
    (configuration_id, name) for configuration_id, name, *_ in CASES
)


def _summary(
    configuration_id: str,
    name: str,
    states: list[dict[str, object]],
    speciation: list[dict[str, object]],
) -> dict[str, object]:
    selected = [row for row in states if row["configuration_id"] == configuration_id]
    evaluated = [row for row in selected if row["status"] == "evaluated"]
    residuals = [
        abs(float(row["log10_model_over_observed"]))
        for row in speciation
        if row["configuration_id"] == configuration_id
        and row["log10_model_over_observed"] not in (None, "")
    ]
    common_residuals = [
        abs(float(row["log10_model_over_observed"]))
        for row in speciation
        if row["configuration_id"] == configuration_id
        and row["log10_model_over_observed"] not in (None, "")
        and float(row["loading_mol_co2_per_mol_mea"]) != 0.78
    ]
    median = statistics.median(residuals) if residuals else None
    return {
        "configuration_id": configuration_id,
        "configuration_name": name,
        "state_count": len(selected),
        "evaluated_state_count": len(evaluated),
        "failed_state_count": len(selected) - len(evaluated),
        "typical_speciation_factor": 10.0**median if median is not None else None,
        "common_five_state_typical_speciation_factor": 10.0
        ** statistics.median(common_residuals),
        "minimum_bulk_relative_permittivity": min(
            (float(row["bulk_relative_permittivity"]) for row in evaluated),
            default=None,
        ),
        "maximum_bulk_relative_permittivity": max(
            (float(row["bulk_relative_permittivity"]) for row in evaluated),
            default=None,
        ),
        "minimum_mass_density_kg_m3": min(
            (float(row["mass_density_kg_m3"]) for row in evaluated), default=None
        ),
        "maximum_mass_density_kg_m3": max(
            (float(row["mass_density_kg_m3"]) for row in evaluated), default=None
        ),
        "maximum_balance_inf_norm": max(
            (float(row["balance_inf_norm"]) for row in evaluated), default=None
        ),
        "maximum_reaction_affinity_inf_norm": max(
            (float(row["reaction_affinity_inf_norm"]) for row in evaluated),
            default=None,
        ),
    }


def main() -> None:
    started = time.monotonic()
    source_states = _source_states()
    state_rows: list[dict[str, object]] = []
    parameter_rows: list[dict[str, object]] = []
    coefficient_rows: list[dict[str, object]] = []
    for configuration_id, name, formulation, coefficients in CASES:
        parameters, mapping = _configuration(
            formulation, 1.0, 1.0, True, coefficients
        )
        state_rows.extend(
            _evaluate_configuration(configuration_id, name, parameters, source_states)
        )
        parameter_rows.append(
            {
                "configuration_id": configuration_id,
                "configuration_name": name,
                "relative_permittivity_formulation": formulation,
                "co2_water_induced_association": True,
                "coefficient_assignment": configuration_id,
                "coefficient_source": (
                    "Figiel et al. (2025), Eq. 11"
                    if coefficients is None
                    else "Zuber et al. (2014), Eqs. 8-9 and Tables 2/9"
                ),
                "parameter_mapping_sha256": _canonical_sha256(mapping),
            }
        )
        assigned = coefficients or {
            component_id: 7.01
            for component_id in (
                "protonated-monoethanolamine",
                "carbamate-anion",
                "bicarbonate-anion",
                "carbonate-anion",
                "hydronium-cation",
                "hydroxide-anion",
            )
        }
        coefficient_rows.extend(
            {
                "configuration_id": configuration_id,
                "component_id": component_id,
                "alpha_i": value,
                "assignment": (
                    "source ion" if component_id in {"hydronium-cation", "hydroxide-anion"}
                    and configuration_id
                    in {"zuber_exact_generic", "zuber_known_universal_fallback"}
                    else "transferred class/fallback"
                ),
            }
            for component_id, value in assigned.items()
        )
    speciation_rows = _speciation_rows(
        state_rows, source_states, configurations=ALL_CONFIGURATIONS
    )
    RESULTS.mkdir(parents=True, exist_ok=True)
    _write_csv(RESULTS / "state_results.csv", state_rows)
    _write_csv(RESULTS / "speciation_comparison.csv", speciation_rows)
    _write_csv(RESULTS / "parameter_table.csv", parameter_rows)
    _write_csv(RESULTS / "ion_specific_coefficients.csv", coefficient_rows)
    module_path = Path(epcsaft.__file__).resolve()
    wheel_path = Path(os.environ["EPCSAFT_ENGINE_WHEEL"]).resolve()
    summary = {
        "schema": "mea.ion-specific-permittivity-sensitivity.v1",
        "status": "completed",
        "runtime_seconds": time.monotonic() - started,
        "installed_epcsaft_module_sha256": hashlib.sha256(
            module_path.read_bytes()
        ).hexdigest(),
        "engine_wheel_path": str(wheel_path),
        "engine_wheel_sha256": hashlib.sha256(wheel_path.read_bytes()).hexdigest(),
        "configurations": [
            _summary(configuration_id, name, state_rows, speciation_rows)
            for configuration_id, name in ALL_CONFIGURATIONS
        ],
        "interpretation_scope": (
            "Zuber aqueous coefficients transferred into the existing MEA salt-free "
            "solvent-mixture rule; organic MEA-ion values are sensitivity assignments"
        ),
    }
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
