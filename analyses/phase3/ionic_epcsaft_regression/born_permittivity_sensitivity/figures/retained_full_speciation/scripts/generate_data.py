from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json
import math
import os
from pathlib import Path

import epcsaft


FIGURE = Path(__file__).resolve().parents[1]
ANALYSIS = FIGURE.parents[1]
ANALYSIS_SCRIPTS = ANALYSIS / "scripts"
os.sys.path.insert(0, str(ANALYSIS_SCRIPTS))

from evaluate_anchored_co2_water_kij import PARAMETERS, _mapping  # noqa: E402
from generate import COMPONENT_IDS  # noqa: E402
from run_full_predictive_refinement import _liquid  # noqa: E402
from MEA.common.analysis_io import write_csv_rows as _write  # noqa: E402
from MEA.epcsaft_ionic.parameter_document import (  # noqa: E402
    materialize_parameter_candidate,
    set_parameter_values,
)


OUTPUT = FIGURE / "output"
CURVES = OUTPUT / "retained_full_speciation_curves.csv"
DIAGNOSTICS = OUTPUT / "retained_full_speciation_diagnostics.csv"
SETTINGS = ANALYSIS / "results/retained_predictive_parameter_settings.json"
TEMPERATURE_K = 313.15
PRESSURE_PA = 101_325.0
LOADINGS = tuple(index / 40 for index in range(41))


def _evaluate(payload: tuple[dict[str, object], float]) -> dict[str, object]:
    mapping, loading = payload
    effective_loading = max(loading, 1.0e-3)
    try:
        parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
        problem = _liquid(
            parameters,
            identity=f"retained-full-speciation-{loading:.6f}",
            temperature_k=TEMPERATURE_K,
            pressure_pa=PRESSURE_PA,
            loading=effective_loading,
        )
        reference = problem.continuation_reference
        return {
            "status": "evaluated",
            "temperature_k": TEMPERATURE_K,
            "pressure_pa": PRESSURE_PA,
            "loading": loading,
            "effective_loading": effective_loading,
            "molar_volume_m3_per_mol": reference.molar_volume_m3_per_mol,
            "minimum_mole_fraction": min(reference.mole_fractions),
            "mole_fraction_sum": math.fsum(reference.mole_fractions),
            "mole_fractions": reference.mole_fractions,
        }
    except Exception as error:
        return {
            "status": "failed",
            "temperature_k": TEMPERATURE_K,
            "pressure_pa": PRESSURE_PA,
            "loading": loading,
            "effective_loading": effective_loading,
            "reason": f"{type(error).__name__}: {error}",
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    args = parser.parse_args()
    retained = json.loads(SETTINGS.read_text(encoding="utf-8"))
    mapping = _mapping(materialize_parameter_candidate(PARAMETERS), TEMPERATURE_K)
    shared = retained["shared_parameters"]
    set_parameter_values(
        mapping,
        {
            "pair/carbon-dioxide/monoethanolamine/k_ij": shared[
                "pair/carbon-dioxide/monoethanolamine/k_ij"
            ],
            "component/protonated-monoethanolamine/segment_diameter": shared[
                "component/protonated-monoethanolamine/segment_diameter_angstrom"
            ],
            "component/carbamate-anion/segment_diameter": shared[
                "component/carbamate-anion/segment_diameter_angstrom"
            ],
        },
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(_evaluate, ((deepcopy(mapping), loading) for loading in LOADINGS)))

    curve_rows = [
        {
            "temperature_C": TEMPERATURE_K - 273.15,
            "pressure_pa": PRESSURE_PA,
            "CO2_loading": result["loading"],
            "species": component_id,
            "mole_fraction": value,
        }
        for result in results
        if result["status"] == "evaluated"
        for component_id, value in zip(COMPONENT_IDS, result["mole_fractions"], strict=True)
    ]
    diagnostics = [
        {key: value for key, value in result.items() if key != "mole_fractions"}
        for result in results
    ]
    _write(CURVES, curve_rows)
    _write(DIAGNOSTICS, diagnostics)
    failures = [row for row in diagnostics if row["status"] != "evaluated"]
    print(f"evaluated={len(results) - len(failures)}/{len(results)}")
    print(CURVES)
    print(DIAGNOSTICS)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
