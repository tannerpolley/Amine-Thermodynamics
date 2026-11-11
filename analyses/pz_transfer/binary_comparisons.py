"""Frozen trial endpoint comparisons; no parameter adoption or adjustment."""

import json

import epcsaft
from epcsaft import equilibrium as eq
from binary import AN, PZ, W, document, load_rows, problem
from binary_evidence import parameters, phase_report, predictions
from run import verify_wheel, write_csv


def calculate():
    verify_wheel()
    calibration = json.loads((AN / "results/binary-calibration.json").read_text())
    checked = json.loads((AN / "results/binary-calibration-phases.json").read_text())
    assert len(checked) == 23 and all(p["passed"] for p in checked), (
        "Return phase failure to owner before comparison"
    )
    assert all(
        not r["active_bounds"] and r["status"] == "converged"
        for r in calibration["starts"]
    ), "Return bound or convergence problem to owner"
    values = calibration["starts"][0]["values"]
    par = parameters(values)
    model = epcsaft.Mixture(par)
    phases = []
    hill = []
    for r in load_rows("hilliard-d2.csv"):
        m = float(r["m_PZ"])
        x = m / (m + 1 / 0.01801528)
        rr = dict(
            r,
            x=x,
            y=float(r["pPZ_Pa"]) / (float(r["pPZ_Pa"]) + float(r["pH2O_Pa"])),
            P_kPa=(float(r["pPZ_Pa"]) + float(r["pH2O_Pa"])) / 1000,
        )
        pred, _ = predictions(par, [rr])
        P, y = pred
        p = P * y
        observed = float(r["pPZ_Pa"])
        hill.append(
            dict(
                r,
                x=x,
                predicted_pPZ_Pa=p,
                difference_Pa=p - observed,
                relative_percent=100 * (p / observed - 1),
                below_2Pa=observed < 2,
                below_313K=float(r["T_K"]) < 313.15,
            )
        )
        phases.append(dict(source="HilliardD2", **phase_report(par, problem(rr), rr)))
    write_csv("binary-hilliard.csv", hill)
    baseline_doc = document()
    original = json.loads((AN / "inputs/razavi.json").read_text())
    baseline_doc["components"][0] = original["components"][0]
    baseline_doc["topology"]["edges"][0] = original["topology"]["edges"][0]
    for term, value in zip(
        baseline_doc["pairs"][0]["coefficients"][0]["temperature_law"]["terms"],
        values,
        strict=True,
    ):
        term["coefficient"]["value"]["magnitude"] = float(value)
    baseline_model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(baseline_doc))
    densities = []
    for i, r in enumerate(load_rows("aqueous-density.csv")):
        if r["phase"] == "excluded precipitate":
            continue
        w = float(r["w_PZ"])
        x = (w / 0.08613) / (w / 0.08613 + (1 - w) / 0.01801528)
        T = float(r["T_K"])
        P = float(r["P_Pa"])
        state = model.state(T, P=P, x={PZ: x, W: 1 - x}, phase="liquid")
        mass = x * 0.08613 + (1 - x) * 0.01801528
        rho = state.molar_density * mass
        delta = rho - float(r["rho_kg_m3"])
        rr = dict(
            r,
            row=i + 1,
            x=x,
            predicted_kg_m3=rho,
            difference_kg_m3=delta,
            relative_percent=100 * delta / float(r["rho_kg_m3"]),
            source_units=delta / float(r["source_scale_kg_m3"]),
            dP_drho=state.pressure_density_derivative,
        )
        old = (
            baseline_model.state(
                T, P=P, x={PZ: x, W: 1 - x}, phase="liquid"
            ).molar_density
            * mass
        )
        rr["razavi_at_same_k_kg_m3"] = old
        rr["stage1b_density_shift_kg_m3"] = rho - old
        if r["source"] == "Concepcion2020":
            shifted = 0.1001 + 0.0001
            sx = (shifted / 0.08613) / (shifted / 0.08613 + (1 - shifted) / 0.01801528)
            srho = model.state(
                T, P=P, x={PZ: sx, W: 1 - sx}, phase="liquid"
            ).molar_density * (sx * 0.08613 + (1 - sx) * 0.01801528)
            rr["mass_fraction_1e-4_sensitivity_kg_m3"] = srho - rho
        else:
            rr["mass_fraction_1e-4_sensitivity_kg_m3"] = "not specified"
        densities.append(rr)
        prob = eq.Problem(
            T=T,
            P=P,
            feed=eq.Amounts({PZ: x, W: 1 - x}),
            phases=[eq.Phase("L", kind="liquid", support=[PZ, W])],
            row_tolerance=1e-10,
        )
        phase = phase_report(par, prob, rr)
        rr["fluid_phase_passed"] = phase["passed"]
        phases.append(dict(source=r["source"], **phase))
    write_csv("binary-density.csv", densities)
    # Explicit downward fluid extrapolation at source-comparison molalities, not new calibration data.
    low = []
    for m in [0.9, 1.8, 2.5, 3.6, 5.0]:
        x = m / (m + 1 / 0.01801528)
        for T in [283.0, 293.15, 298.15, 303.15, 313.15]:
            r = dict(row=f"{m}:{T}", T_K=T, x=x, y=0.001, P_kPa=10.0)
            pred, _ = predictions(par, [r])
            P, y = pred
            low.append(
                dict(
                    T_K=T,
                    m_PZ=m,
                    x=x,
                    predicted_P_Pa=P,
                    predicted_pPZ_Pa=P * y,
                    below_313K=T < 313.15,
                    classification="fluid-only extrapolation; solid stability unqualified",
                )
            )
            phases.append(
                dict(
                    source="low-temperature-extrapolation",
                    **phase_report(par, problem(r), r),
                )
            )
    write_csv("binary-low-temperature.csv", low)
    (AN / "results/binary-comparison-phases.json").write_text(
        json.dumps(phases, indent=2) + "\n"
    )
    print(
        json.dumps(
            dict(phase_states=len(phases), passed=sum(p["passed"] for p in phases))
        ),
        flush=True,
    )


if __name__ == "__main__":
    calculate()
