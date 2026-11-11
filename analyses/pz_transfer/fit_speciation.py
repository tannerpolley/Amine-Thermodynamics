"""NMR-only law-offset calibration; all EOS quantities held at declared starts."""

import csv
import json
import os

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
from run import AN, verify_wheel
from speciation import PZ, PH, PH2, PC, HPC, DC, W, H, document, save


def declarations(q=0.02, tolerance=1e-10):
    par = epcsaft.Parameters.from_mapping(document())
    rr = json.loads((AN / "results/speciation-reactions.json").read_text())
    # Evaluation extensions preserve source domains in the retained source declaration.
    for r in rr:
        r["correlation"]["temperature_min"] = 283.15
        r["correlation"]["temperature_max"] = max(
            333.15, r["correlation"]["temperature_max"]
        )
    coords = [
        reg.reaction_coordinate(
            r["name"],
            "a",
            origin=r["correlation"]["a"],
            scale=1.0,
            bounds=(r["correlation"]["a"] - 3, r["correlation"]["a"] + 3),
        )
        for r in rr[5:]
    ]
    for r in rr:
        r["correlation"] = eq.ReactionLogPolynomial(**r["correlation"])
    rows = list(csv.DictReader((AN / "inputs/ermatchkov-nmr.csv").open()))
    ids = list(par.component_ids)
    obs = []
    blocks = []
    metadata = []
    for r in rows:
        pz = float(r["pz_mol"])
        co2 = float(r["co2_mol"])
        T = float(r["T_K"])
        p = eq.problem_from_mapping(
            dict(
                T=T,
                P=100000.0,
                feed=dict(
                    basis="amounts",
                    values={PZ: pz, W: 1 / 0.0180153, "carbon-dioxide": co2},
                ),
                phases=[dict(name="L", kind="liquid", support=ids)],
                reactions=rr,
                neutral_reference=dict(
                    solvent=W,
                    solute_molality_ratios={
                        i: (4.0 if i == H else 1.0) for i in ids if i != W
                    },
                    standard_molality_mol_per_kg=1.0,
                ),
                row_tolerance=tolerance,
            )
        )
        f0, f1 = float(r["n0_mol"]) / pz, float(r["n1_mol"]) / pz
        f2 = float(r["n2_mol"]) / pz if r["n2_mol"] else None
        values = [f1] if f2 is None else [f1, f2]
        for group, (value, species) in enumerate(
            zip(values, [[PC, HPC], [DC]], strict=False), 1
        ):
            obs.append(
                reg.observation(
                    par,
                    "amount_ratio",
                    p,
                    phase="L",
                    species=species,
                    denominator_phase="L",
                    denominator_species=[PZ, PH, PH2, PC, HPC, DC],
                    observed=value,
                    form="difference",
                    scale=1.0,
                )
            )
            metadata.append(dict(r, group=group, observed_fraction=value))
        if f2 is None:
            blocks.append(np.array([[(q * f1) ** 2]]))
        else:
            areas = np.array([f1 / 2, f0, f2, f1 / 2])
            S = areas.sum()
            # Full normalized-area derivatives; no third independently scored f0.
            select = np.array([[1, 0, 0, 1], [0, 0, 1, 0]])
            J = (select * S - (select @ areas)[:, None]) / S**2
            blocks.append((J * (q * areas) ** 2) @ J.T)
    C = np.zeros((len(obs), len(obs)))
    i = 0
    for b in blocks:
        C[i : i + len(b), i : i + len(b)] = b
        i += len(b)
    uncertainty = reg.MeasurementUncertainty()
    uncertainty.output_sigma = np.sqrt(np.diag(C)).tolist()
    uncertainty.covariance = C.ravel().tolist()
    return par, coords, obs, C, uncertainty, metadata


def info(par, coords, obs, C, x):
    d = reg.differentiate(par, coords, obs, optimizer=list(x))
    J = np.array(d.residual_optimizer_gradient).reshape(len(obs), 3)
    L = np.linalg.cholesky(C)
    J = np.linalg.solve(L, J)
    u, s, vt = np.linalg.svd(J, full_matrices=False)
    cov = (vt.T / s**2) @ vt
    se = np.sqrt(np.diag(cov))
    return dict(
        singular_values=s.tolist(),
        right_vectors=vt.tolist(),
        rank=int(np.linalg.matrix_rank(J)),
        covariance=cov.tolist(),
        se=se.tolist(),
        correlation=(cov / np.outer(se, se)).tolist(),
        jacobian=J.tolist(),
        values=list(d.values) if hasattr(d, "values") else None,
    )


def calculate():
    verify_wheel()
    par, coords, obs, C, uncertainty, metadata = declarations()
    record = dict(
        conditional_representation="A at approved fixed EOS starts; representation selection belongs to stage 4",
        observations=len(obs),
        blank_dicarbamate=10,
    )
    try:
        record["initial_information"] = info(par, coords, obs, C, [0.0, 0.0, 0.0])
        save("nmr-fit.json", record)
        controls = reg.FitControls(
            maximum_iterations=100,
            maximum_elapsed_time_seconds=600,
            function_tolerance=1e-10,
            parameter_tolerance=1e-10,
            gradient_tolerance=1e-8,
            workers=int(os.environ["AGENT_HEAVY_CORES"]),
        )
        fit = reg.fit(
            par,
            coords,
            obs,
            controls=controls,
            uncertainty=uncertainty,
            singular_vectors=True,
        )
        record.update(
            status=fit.status,
            usable=fit.usable,
            message=fit.message,
            optimizer=list(fit.optimizer),
            cost=fit.final_cost,
            active_bounds=list(fit.covariance.active_bounds),
        )
        if fit.usable:
            record["endpoint_information"] = info(par, coords, obs, C, fit.optimizer)
    except Exception as e:
        record.update(exception=type(e).__name__, message=str(e))
    save("nmr-fit.json", record)
    print(
        json.dumps({k: v for k, v in record.items() if "information" not in k}),
        flush=True,
    )


if __name__ == "__main__":
    calculate()
