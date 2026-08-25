from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import statistics
import time

from generate import (
    ANALYSIS,
    _canonical_sha256,
    _configuration,
    _evaluate_configuration,
    _source_states,
    _speciation_rows,
    _write_csv,
)
from MEA.common.analysis_io import read_csv_rows as _read_csv


RESULTS = ANALYSIS / "results" / "ion_coefficient_blocks"
PRIOR_RESULTS = ANALYSIS / "results" / "ion_specific_permittivity"
BASE_ID = "block_baseline"
BASE_NAME = "H+/OH- source values; remaining ions 7.01"
BASE_COEFFICIENTS = {
    "protonated-monoethanolamine": 7.01,
    "carbamate-anion": 7.01,
    "bicarbonate-anion": 7.01,
    "carbonate-anion": 7.01,
    "hydronium-cation": 9.55,
    "hydroxide-anion": 13.96,
}
AMINE_CASES = (
    (
        "amine_meah_generic",
        "MEAH+ = 2.60",
        {**BASE_COEFFICIENTS, "protonated-monoethanolamine": 2.60},
    ),
    (
        "amine_meacoo_generic",
        "MEACOO- = 7.89",
        {**BASE_COEFFICIENTS, "carbamate-anion": 7.89},
    ),
    (
        "amine_both_generic",
        "MEAH+ = 2.60; MEACOO- = 7.89",
        {
            **BASE_COEFFICIENTS,
            "protonated-monoethanolamine": 2.60,
            "carbamate-anion": 7.89,
        },
    ),
)


def _evaluate_case(
    case: tuple[str, str, dict[str, float]],
) -> tuple[str, str, dict[str, float], str, list[dict[str, object]]]:
    configuration_id, name, coefficients = case
    parameters, mapping = _configuration(
        "ion-specific-suppression", 1.0, 1.0, True, coefficients
    )
    return (
        configuration_id,
        name,
        coefficients,
        _canonical_sha256(mapping),
        _evaluate_configuration(
            configuration_id, name, parameters, _source_states()
        ),
    )


def _run_cases(
    cases: tuple[tuple[str, str, dict[str, float]], ...],
) -> list[tuple[str, str, dict[str, float], str, list[dict[str, object]]]]:
    with ProcessPoolExecutor(max_workers=2) as executor:
        return list(executor.map(_evaluate_case, cases))


def _common_loadings(
    state_rows: list[dict[str, object]], configuration_ids: tuple[str, ...]
) -> tuple[float, ...]:
    evaluated = {
        configuration_id: {
            float(row["loading_mol_co2_per_mol_mea"])
            for row in state_rows
            if row["configuration_id"] == configuration_id
            and row["status"] == "evaluated"
        }
        for configuration_id in configuration_ids
    }
    return tuple(sorted(set.intersection(*(evaluated[item] for item in configuration_ids))))


def _typical_factor(
    rows: list[dict[str, object]], configuration_id: str, loadings: tuple[float, ...]
) -> float:
    residuals = [
        abs(float(row["log10_model_over_observed"]))
        for row in rows
        if row["configuration_id"] == configuration_id
        and row["log10_model_over_observed"] not in (None, "")
        and float(row["loading_mol_co2_per_mol_mea"]) in loadings
    ]
    return 10.0 ** statistics.median(residuals)


def _summary(
    state_rows: list[dict[str, object]],
    speciation_rows: list[dict[str, object]],
    configuration_id: str,
    name: str,
    common_loadings: tuple[float, ...],
) -> dict[str, object]:
    states = [row for row in state_rows if row["configuration_id"] == configuration_id]
    evaluated = [row for row in states if row["status"] == "evaluated"]
    return {
        "configuration_id": configuration_id,
        "configuration_name": name,
        "evaluated_state_count": len(evaluated),
        "failed_state_count": len(states) - len(evaluated),
        "common_state_typical_speciation_factor": _typical_factor(
            speciation_rows, configuration_id, common_loadings
        ),
        "minimum_bulk_relative_permittivity": min(
            (float(row["bulk_relative_permittivity"]) for row in evaluated),
            default=None,
        ),
        "maximum_bulk_relative_permittivity": max(
            (float(row["bulk_relative_permittivity"]) for row in evaluated),
            default=None,
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
    wheel_path = Path(os.environ["EPCSAFT_ENGINE_WHEEL"]).resolve()
    wheel_sha256 = hashlib.sha256(wheel_path.read_bytes()).hexdigest()
    prior_summary = json.loads((PRIOR_RESULTS / "summary.json").read_text())
    if prior_summary["engine_wheel_sha256"] != wheel_sha256:
        raise RuntimeError("prior baseline was generated with a different Engine wheel")
    baseline_rows = [
        {
            **row,
            "configuration_id": BASE_ID,
            "configuration_name": BASE_NAME,
        }
        for row in _read_csv(PRIOR_RESULTS / "state_results.csv")
        if row["configuration_id"] == "zuber_known_universal_fallback"
    ]
    _, baseline_mapping = _configuration(
        "ion-specific-suppression", 1.0, 1.0, True, BASE_COEFFICIENTS
    )
    state_rows: list[dict[str, object]] = list(baseline_rows)
    configurations = [(BASE_ID, BASE_NAME, BASE_COEFFICIENTS, _canonical_sha256(baseline_mapping))]
    amine_results = _run_cases(AMINE_CASES)
    for configuration_id, name, coefficients, mapping_sha, rows in amine_results:
        configurations.append((configuration_id, name, coefficients, mapping_sha))
        state_rows.extend(rows)
    amine_ids = tuple(configuration_id for configuration_id, *_ in configurations)
    amine_speciation = _speciation_rows(
        state_rows,
        _source_states(),
        configurations=tuple((item[0], item[1]) for item in configurations),
    )
    amine_common = _common_loadings(state_rows, amine_ids)
    maximum_coverage = max(
        sum(
            row["configuration_id"] == configuration_id and row["status"] == "evaluated"
            for row in state_rows
        )
        for configuration_id in amine_ids
    )
    eligible = [
        item
        for item in configurations
        if sum(
            row["configuration_id"] == item[0] and row["status"] == "evaluated"
            for row in state_rows
        )
        == maximum_coverage
    ]
    selected = min(
        eligible,
        key=lambda item: _typical_factor(amine_speciation, item[0], amine_common),
    )
    selected_id, selected_name, selected_coefficients, _ = selected
    carbonate_cases = (
        (
            "carbonate_hco3_generic",
            f"{selected_name}; HCO3- = 7.89",
            {**selected_coefficients, "bicarbonate-anion": 7.89},
        ),
        (
            "carbonate_co3_generic",
            f"{selected_name}; CO3^2- = 7.89",
            {**selected_coefficients, "carbonate-anion": 7.89},
        ),
        (
            "carbonate_both_generic",
            f"{selected_name}; HCO3-/CO3^2- = 7.89",
            {
                **selected_coefficients,
                "bicarbonate-anion": 7.89,
                "carbonate-anion": 7.89,
            },
        ),
    )
    for configuration_id, name, coefficients, mapping_sha, rows in _run_cases(
        carbonate_cases
    ):
        configurations.append((configuration_id, name, coefficients, mapping_sha))
        state_rows.extend(rows)
    configuration_pairs = tuple((item[0], item[1]) for item in configurations)
    speciation_rows = _speciation_rows(
        state_rows, _source_states(), configurations=configuration_pairs
    )
    carbonate_ids = (selected_id,) + tuple(item[0] for item in carbonate_cases)
    carbonate_common = _common_loadings(state_rows, carbonate_ids)
    parameter_rows = []
    coefficient_rows = []
    for configuration_id, name, coefficients, mapping_sha in configurations:
        blocks = ["amine" if configuration_id in amine_ids else "carbonate"]
        if configuration_id == selected_id:
            blocks.append("carbonate_base")
        parameter_rows.append(
            {
                "configuration_id": configuration_id,
                "configuration_name": name,
                "analysis_block": ";".join(blocks),
                "parameter_mapping_sha256": mapping_sha,
            }
        )
        coefficient_rows.extend(
            {
                "configuration_id": configuration_id,
                "component_id": component_id,
                "alpha_i": value,
            }
            for component_id, value in coefficients.items()
        )
    RESULTS.mkdir(parents=True, exist_ok=True)
    _write_csv(RESULTS / "state_results.csv", state_rows)
    _write_csv(RESULTS / "speciation_comparison.csv", speciation_rows)
    _write_csv(RESULTS / "parameter_table.csv", parameter_rows)
    _write_csv(RESULTS / "ion_specific_coefficients.csv", coefficient_rows)
    summaries = [
        _summary(
            state_rows,
            speciation_rows,
            configuration_id,
            name,
            amine_common if configuration_id in amine_ids else carbonate_common,
        )
        for configuration_id, name in configuration_pairs
    ]
    summary = {
        "schema": "mea.ion-coefficient-block-sensitivity.v1",
        "status": "completed",
        "engine_wheel_sha256": wheel_sha256,
        "engine_wheel_path": str(wheel_path),
        "runtime_seconds": time.monotonic() - started,
        "worker_count": 2,
        "amine_common_loadings": list(amine_common),
        "selected_amine_configuration_id": selected_id,
        "carbonate_common_loadings": list(carbonate_common),
        "configurations": summaries,
    }
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
