"""Stage 3 source laws and full PZ declaration for issue #308."""

import copy
import csv
import hashlib
import json
import math
import tomllib

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq
from run import AN, SHA, verify_wheel, write_csv

PZ, PH, PH2, PC, HPC, DC = (
    "piperazine",
    "piperazinium",
    "piperazinediium",
    "piperazine-carbamate",
    "protonated-piperazine-carbamate",
    "piperazine-dicarbamate",
)
W, H, HC = "water", "hydronium-cation", "bicarbonate-anion"


def save(name, value):
    (AN / "results" / name).write_text(json.dumps(value, indent=2) + "\n")


def laws():
    rows = list(csv.DictReader((AN / "inputs/hamborg-table16.csv").open()))
    fits, residuals, comparison = {}, [], []
    for name in ["P1", "P2"]:
        data = [r for r in rows if r["law"] == name]
        T = np.array([float(r["T_K"]) for r in data])
        y = np.array([float(r["lnK"]) for r in data])
        X = np.column_stack([1 / T, np.ones(len(T)), np.log(T)])
        # Column normalization changes no physical coordinate or fitted law.
        scale = 1 / np.linalg.norm(X, axis=0)
        J = X * scale / 0.04
        u, s, vt = np.linalg.svd(J, full_matrices=False)
        coef = scale * (vt.T @ ((u.T @ (y / 0.04)) / s))
        cov = ((vt.T / s**2) @ vt) * np.outer(scale, scale)
        se = np.sqrt(np.diag(cov))
        fits[name] = dict(
            parameters_ABC=coef.tolist(),
            se_ABC=se.tolist(),
            covariance=cov.tolist(),
            correlation=(cov / np.outer(se, se)).tolist(),
            column_scales=scale.tolist(),
            singular_values=s.tolist(),
            right_vectors=vt.tolist(),
            rank=int(np.linalg.matrix_rank(J)),
            source_range_K=[float(T.min()), float(T.max())],
            rms_scale=float(np.sqrt(np.mean(((X @ coef - y) / 0.04) ** 2))),
        )
        for r, pred in zip(data, X @ coef, strict=True):
            residuals.append(
                dict(
                    r,
                    calculated_lnK=pred,
                    difference_lnK=pred - float(r["lnK"]),
                    residual_scale=(pred - float(r["lnK"])) / 0.04,
                )
            )
        for t in sorted(
            {
                273.15,
                283.15,
                293.15,
                298.15,
                303.15,
                313.15,
                323.15,
                333.15,
                353.15,
                393.15,
            }
        ):
            x = np.array([1 / t, 1, math.log(t)])
            pk = (
                1656.59 / t + 6.1316 - 0.006556 * t
                if name == "P1"
                else 952.11 / t + 4.3919 - 0.007555 * t
            )
            comparison.append(
                dict(
                    law=name,
                    T_K=t,
                    hamborg_lnK=float(x @ coef),
                    conditional_SE_lnK=float(np.sqrt(x @ cov @ x)),
                    hetzer_lnK=-math.log(10) * pk,
                    difference_lnK=float(x @ coef) + math.log(10) * pk,
                    hamborg_extrapolated=t < T.min() or t > T.max(),
                    hetzer_extrapolated=t < 273.15 or t > 323.15,
                )
            )
    save("protonation-laws.json", fits)
    write_csv("protonation-residuals.csv", residuals)
    write_csv("hetzer-comparison.csv", comparison)
    return fits


def coefficient(cid, family, value, unit):
    return dict(
        identity=f"component/{cid}/{family}",
        family=family,
        value=dict(magnitude=value, unit=unit),
    )


def document():
    path = (
        AN.parent / "mea_parameter_bundle/results/selected-current-best-parameters.json"
    )
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == "f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97"
    )
    shared = json.loads(path.read_text())
    binary = json.loads((AN / "results/binary-endpoint-0.10.json").read_text())
    remove = {"monoethanolamine", "protonated-monoethanolamine", "carbamate-anion"}
    doc = copy.deepcopy(shared)
    doc["components"] = [
        c for c in shared["components"] if c["component_id"] not in remove
    ]
    doc["pairs"] = [
        p
        for p in shared["pairs"]
        if not ({p["component_id_a"], p["component_id_b"]} & remove)
    ] + binary["pairs"]
    pz = copy.deepcopy(binary["components"][0])
    pz["coefficients"] += [
        coefficient(PZ, f, v, u)
        for f, v, u in [
            ("solvation_factor", 1, "dimensionless"),
            ("dielectric_volume", 0.7309865858310542, "liter / mole"),
            ("dielectric_temperature", 1019.0802597119892, "kelvin"),
        ]
    ]
    doc["components"].append(pz)
    for cid, z, mass in [
        (PH, 1, 0.087146),
        (PH2, 2, 0.088154),
        (PC, -1, 0.129132),
        (DC, -2, 0.172134),
        (HPC, 0, 0.130140),
    ]:
        if z:
            values = [
                ("segment_count", 1, "dimensionless"),
                ("segment_diameter", 5, "angstrom"),
                ("dispersion_energy_over_k", 274.10, "kelvin"),
                ("born_diameter", 5, "angstrom"),
                ("packing_diameter", 4.4, "angstrom"),
                ("debye_huckel_diameter", 5, "angstrom"),
                ("solvation_factor", 1, "dimensionless"),
            ]
        else:
            values = [
                ("segment_count", 2.6519, "dimensionless"),
                ("segment_diameter", 3.7136, "angstrom"),
                ("dispersion_energy_over_k", 274.10, "kelvin"),
                ("solvation_factor", 1, "dimensionless"),
                ("dielectric_volume", 0.7309865858310542, "liter / mole"),
                ("dielectric_temperature", 1019.0802597119892, "kelvin"),
            ]
        doc["components"].append(
            dict(
                component_id=cid,
                name=cid,
                coefficients=[coefficient(cid, *v) for v in values],
                fixed={
                    "charge_number": dict(
                        identity=f"component/{cid}/charge_number",
                        value=dict(magnitude=z, unit="elementary-charge"),
                    ),
                    "molar_mass": dict(
                        identity=f"component/{cid}/molar_mass",
                        value=dict(magnitude=mass, unit="kilogram / mole"),
                    ),
                },
            )
        )
    # Preserve shared topology; remove every edge/site involving retired MEA species.
    for key in ["sites", "presets", "edges", "no_cross_association"]:
        doc["topology"][key] = [
            x
            for x in doc["topology"].get(key, [])
            if not (
                {
                    x.get("component_id"),
                    x.get("component_id_a"),
                    x.get("component_id_b"),
                    x.get("endpoint_a", {}).get("component_id"),
                    x.get("endpoint_b", {}).get("component_id"),
                }
                & remove
            )
        ]
    for key in ["sites", "presets", "edges"]:
        doc["topology"][key] += [
            x for x in binary["topology"].get(key, []) if PZ in json.dumps(x)
        ]
    ids = [c["component_id"] for c in doc["components"]]
    present = {
        frozenset([p["component_id_a"], p["component_id_b"]]) for p in doc["pairs"]
    }
    for i, a in enumerate(ids):
        for b in ids[i + 1 :]:
            if frozenset([a, b]) not in present:
                doc["pairs"].append(
                    dict(
                        component_id_a=a,
                        component_id_b=b,
                        coefficients=[
                            dict(
                                identity=f"pair/{a}/{b}/k_ij",
                                family="k_ij",
                                value=dict(magnitude=0.0, unit="dimensionless"),
                            )
                        ],
                    )
                )
    charges = {
        c["component_id"]: c["fixed"]["charge_number"]["value"]["magnitude"]
        for c in doc["components"]
    }
    doc["pairs"] = [
        p
        for p in doc["pairs"]
        if charges[p["component_id_a"]] * charges[p["component_id_b"]] <= 0
    ]
    doc["topology"]["no_cross_association"].append(
        dict(
            component_id_a="carbon-dioxide",
            component_id_b=PZ,
            provenance=dict(
                source_id="issue-308", locator="design: no CO2 cross association"
            ),
        )
    )
    doc["reaction_correlations"] = []
    return doc


def reactions(fits):
    decl = tomllib.loads(
        (AN.parent / "solvent_specification_mea/declarations.toml").read_text()
    )
    rows = copy.deepcopy(decl["chemistry"]["reactions"]["aqueous"][:3])
    for r in rows:
        r["stoichiometry"] = {k: v for k, v in r["stoichiometry"].items() if v}
    stoich = [
        {PH: -1, W: -1, PZ: 1, H: 1},
        {PH2: -1, W: -1, PH: 1, H: 1},
        {PC: -1, W: -1, PZ: 1, HC: 1},
        {HPC: -1, W: -1, PC: 1, H: 1},
        {DC: -1, W: -1, PC: 1, HC: 1},
    ]
    for i, st in enumerate(stoich, 1):
        if i <= 2:
            A, B, C = fits[f"P{i}"]["parameters_ABC"]
            a, b, c = B + C * math.log(313.15), A, C
            domain = [293, 353]
        else:
            A, B = {3: (-3.750, 1570.4), 4: (4.354, 1517.0), 5: (-1.587, 574.2)}[i]
            a, b, c = -math.log(10) * A, -math.log(10) * B, 0.0
            domain = [283, 333]
        rows.append(
            dict(
                name=f"P{i}",
                stoichiometry=st,
                correlation=dict(
                    a=a,
                    b=b,
                    c=c,
                    d=0.0,
                    e=0.0,
                    f=0.0,
                    reference_temperature=313.15,
                    standard_state_id="aqueous-molality-infinite-dilution-water-v1",
                    temperature_min=domain[0],
                    temperature_max=domain[1],
                ),
                reference=dict(
                    source_basis="CommonMolalityInfiniteDilution",
                    reference_pressure_pa=100000.0,
                ),
            )
        )
    return rows


def problem(rows, T=313.15):
    rr = copy.deepcopy(rows)
    for r in rr:
        r["correlation"] = eq.ReactionLogPolynomial(**r["correlation"])
    ids = [c["component_id"] for c in document()["components"]]
    return eq.problem_from_mapping(
        dict(
            T=T,
            P=100000.0,
            feed=dict(
                basis="amounts", values={PZ: 1.0, W: 55.5084, "carbon-dioxide": 0.5}
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
            row_tolerance=1e-10,
        )
    )


def calculate():
    verify_wheel()
    fits = laws()
    doc = document()
    rr = reactions(fits)
    formulas = {
        PZ: dict(C=4, H=10, N=2),
        PH: dict(C=4, H=11, N=2, charge=1),
        PH2: dict(C=4, H=12, N=2, charge=2),
        PC: dict(C=5, H=9, N=2, O=2, charge=-1),
        HPC: dict(C=5, H=10, N=2, O=2),
        DC: dict(C=6, H=8, N=2, O=4, charge=-2),
        W: dict(H=2, O=1),
        "carbon-dioxide": dict(C=1, O=2),
        HC: dict(H=1, C=1, O=3, charge=-1),
        "carbonate-anion": dict(C=1, O=3, charge=-2),
        H: dict(H=3, O=1, charge=1),
        "hydroxide-anion": dict(H=1, O=1, charge=-1),
    }
    for r in rr:
        for element in ["C", "H", "N", "O", "charge"]:
            assert (
                sum(
                    n * formulas[c].get(element, 0)
                    for c, n in r["stoichiometry"].items()
                )
                == 0
            ), (r["name"], element)
    anchors = []
    for r in rr[3:]:
        c = r["correlation"]
        T = 298.15
        value = c["a"] + c["b"] / T + c["c"] * math.log(T / c["reference_temperature"])
        expected = {
            "P1": -22.37,
            "P2": -12.45,
            "P3": -math.log(10) * 1.517,
            "P4": -math.log(10) * 9.442,
            "P5": -math.log(10) * 0.339,
        }[r["name"]]
        assert abs(value - expected) < (0.04 if r["name"] in ["P1", "P2"] else 0.005)
        anchors.append(
            dict(
                reaction=r["name"],
                T_K=T,
                source_basis_lnK=value,
                rounded_source_lnK=expected,
                difference=value - expected,
                delta_nu_solutes=sum(
                    n for k, n in r["stoichiometry"].items() if k != W
                ),
            )
        )
    save("speciation-source-anchors.json", anchors)
    save("speciation-start-parameters.json", doc)
    save("speciation-reactions.json", rr)
    admission = dict(
        wheel_sha256=SHA,
        species_count=len(doc["components"]),
        reaction_count=len(rr),
        charges={
            c["component_id"]: c["fixed"]["charge_number"]["value"]["magnitude"]
            for c in doc["components"]
        },
    )
    try:
        par = epcsaft.Parameters.from_mapping(doc)
        model = epcsaft.Mixture(par)
        p = problem(rr)
        admission.update(parameters_admitted=True, problem_admitted=True)
        result = eq.solve_equilibrium(model, p)
        admission.update(
            message=result.message,
            success=result.success,
            requested_tolerance_met=result.requested_tolerance_met,
            residuals=list(result.residuals),
            mole_fractions=list(result.mole_fractions),
        )
    except Exception as e:
        admission.update(exception=type(e).__name__, message=str(e))
    save("speciation-admission.json", admission)
    print(json.dumps(admission), flush=True)


if __name__ == "__main__":
    calculate()
