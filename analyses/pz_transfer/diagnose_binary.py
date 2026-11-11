"""Bounded #308 phase probes; trial k values are diagnostics, never adopted fits."""

import copy
import json

import epcsaft
from epcsaft import equilibrium as eq
from binary import document, load_rows, problem
from run import AN, verify_wheel, write_csv


def calculate():
    verify_wheel()
    doc = document()
    (AN / "results/binary-start-parameters.json").write_text(
        json.dumps(doc, indent=2) + "\n"
    )
    rows = []
    for k in [0.0, -0.05, -0.1]:
        trial = copy.deepcopy(doc)
        trial["pairs"][0]["coefficients"][0]["temperature_law"]["terms"][0][
            "coefficient"
        ]["value"]["magnitude"] = k
        par = epcsaft.Parameters.from_mapping(trial)
        model = epcsaft.Mixture(par)
        for r in load_rows("hartono-table6.csv"):
            if r["role"] != "calibration":
                continue
            for tolerance in [1e-10, 1e-12] if k == 0 else [1e-10]:
                sol = eq.solve_equilibrium(model, problem(r, tolerance))
                x = float(r["x"])
                st = model.state(
                    float(r["T_K"]),
                    P=float(r["P_kPa"]) * 1000,
                    x={"piperazine": x, "water": 1 - x},
                    phase="liquid",
                )
                rows.append(
                    dict(
                        row=r["row"],
                        T_K=r["T_K"],
                        x=x,
                        k0_trial=k,
                        k1_trial=0.0,
                        row_tolerance=tolerance,
                        solver_status=sol.solver_status,
                        requested_tolerance_met=sol.requested_tolerance_met,
                        message=sol.message,
                        returned_pressure_Pa=sol.pressure,
                        max_equation_residual=max(map(abs, sol.residuals))
                        if sol.residuals
                        else None,
                        observed_P_liquid_mol_m3=st.molar_density,
                        observed_P_dP_drho=st.pressure_density_derivative,
                    )
                )
    write_csv("binary-phase-diagnosis.csv", rows)
    print(
        json.dumps(
            {
                str(k): sum(
                    r["returned_pressure_Pa"] is not None
                    for r in rows
                    if r["k0_trial"] == k and r["row_tolerance"] == 1e-10
                )
                for k in [0.0, -0.05, -0.1]
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    calculate()
