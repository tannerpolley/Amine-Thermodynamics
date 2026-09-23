"""Check actual ionic source-reference pressure jets against held-coordinate perturbations."""
from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path

import shared_evaluation as shared
from epcsaft import equilibrium


def main() -> None:
    shared.verify_wheel()
    model = shared.epcsaft.Mixture(shared.load_parameters())
    request = next(item["request"] for item in shared.load_state_packet()["observations"]
                   if item["identity"] == "vle_obs_0130")
    problem = shared._problem_from_request(shared.corrected_request(request, shared._selected_reactions()))
    result = equilibrium.solve_equilibrium(model, problem)
    if not result.success or max(map(abs, result.residuals)) > 1e-10:
        raise RuntimeError(f"central reactive bubble failed: {result.message}")
    compiled = equilibrium.compile_problem(model, problem)
    point = list(result.coordinates)
    width, pressure_column = len(point), compiled.primal_size - 1
    chemical_rows = {row.index: index for index, row in enumerate(compiled.rows)
                     if row.phase == 0 and row.kind.name == "Chemical"}
    rows, fixed = [], []
    for step in (100.0, 300.0, 1000.0):
        lower, upper = point.copy(), point.copy()
        lower[pressure_column] -= step
        upper[pressure_column] += step
        lower_values, upper_values = compiled.evaluate(lower).values, compiled.evaluate(upper).values
        lower_jacobian, upper_jacobian = compiled.jacobian(lower), compiled.jacobian(upper)
        for index, reaction in enumerate(problem.reactions):
            diagnostic = result.neutral_reference_diagnostics[index]
            first = diagnostic.terminal_contraction_pressure_derivative
            second = diagnostic.terminal_contraction_pressure_second_derivative
            if reaction.reference.reference_pressure_pa is not None:
                if step == 100.0:
                    fixed.append({"reaction": reaction.name, "first": first, "second": second})
                if first != 0.0 or second != 0.0:
                    raise RuntimeError("fixed-source pressure derivative changed")
                continue
            nu = [reaction.stoichiometry.get(name, 0.0) for name in model.component_ids]
            first_fd = -sum(nu[i] * (upper_values[row] - lower_values[row])
                            for i, row in chemical_rows.items()) / (2 * step)
            second_fd = -sum(nu[i] * (upper_jacobian[row * width + pressure_column]
                                      - lower_jacobian[row * width + pressure_column])
                             for i, row in chemical_rows.items()) / (2 * step)
            passed = (first is not None and second is not None
                      and math.isclose(first, first_fd, rel_tol=1e-5, abs_tol=0.0)
                      and math.isclose(second, second_fd, rel_tol=1e-5, abs_tol=0.0))
            rows.append({"reaction": reaction.name, "step_pa": step, "first_per_pa": first,
                         "first_fd_per_pa": first_fd, "second_per_pa2": second,
                         "second_fd_per_pa2": second_fd, "passed": passed})
    output = Path(__file__).resolve().parents[1] / "results"
    path = output / "reference-pressure-jets.csv"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    shared.write_json(output / "reference-pressure-jets.json", {
        "engine_commit": shared.ENGINE_COMMIT, "wheel_sha256": shared.ENGINE_WHEEL_SHA256,
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "parameter_sha256": shared.sha256(shared.PARAMETERS), "case": "vle_obs_0130",
        "pressure_pa": result.pressure[0], "raw_residual_max": max(map(abs, result.residuals)),
        "csv_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "rows": len(rows),
        "criterion": "relative agreement <= 1e-5, no absolute floor", "fixed_sources": fixed,
        "claim_limit": "One actual ionic reference; held-coordinate pressure perturbations, not global stability.",
    })
    if not all(row["passed"] for row in rows):
        raise RuntimeError("pressure-jet discrepancy retained in the CSV")


if __name__ == "__main__":
    main()
