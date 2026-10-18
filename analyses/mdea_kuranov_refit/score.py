"""Issue #126 step 2: score Kuranov 1996 Table 2 total pressures with the fixed Wangler 2018 model (nothing fitted).

ARD = (100/N) sum |1 - p_calc/p_exp| over all rows; a row that does not solve is reported, never dropped.
Diagnostic variants (not Wangler's printed model) isolate the causes found in README.md.
Usage: python score.py   (writes results/reproduction-rows.csv and results/reproduction-summary.json)
"""
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import epcsaft
from epcsaft import equilibrium

import model

ROOT = model.HERE.parents[1]
KURANOV = ROOT / "data/reference/MDEA/Kuranov_1996_CO2_MDEA_total_pressure.csv"
RESULTS = model.HERE / "results"
WHEEL_SHA256 = "d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357"


def kuranov_rows():
    with KURANOV.open() as handle:
        return [{"row": int(r["source_row"]), "series": r["source_series"], "T": float(r["temperature_K"]),
                 "m_mdea": float(r["m_MDEA_mol_per_kg_H2O"]), "m_co2": float(r["m_CO2_mol_per_kg_H2O"]),
                 "p_exp": float(r["ten_times_total_pressure_MPa"]) * 1e5} for r in csv.DictReader(handle)]


def solve_rows(doc, rows):
    """Bubble pressure of every row; within an isotherm series each solve starts from the previous solution.
    `doc` is one parameter document, or a function of the row returning that row's document."""
    shared = None if callable(doc) else epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc))
    out, previous = {}, {}
    for r in sorted(rows, key=lambda r: (r["series"], r["m_co2"])):
        mix = shared or epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc(r)))
        start = previous.get(r["series"])
        result = None
        for guess in ([start] if start else []) + [None]:  # warm start, then the ideal-speciation seed
            problem = model.bubble_problem(r["T"], r["m_mdea"], r["m_co2"], r["p_exp"],
                                           *(guess if guess else (None, None)))
            result = equilibrium.solve_equilibrium(mix, problem)
            if result.success:
                break
        ok = result.success
        if ok:
            previous[r["series"]] = (dict(zip(model.SPECIES, result.phase_mole_fractions(0))),
                                     dict(zip(model.NEUTRAL, result.phase_mole_fractions(1)[:3])))
        out[r["row"]] = {"success": ok, "message": result.message, "p_calc": result.pressure[0] if ok else math.nan,
                         "x_liquid": result.phase_mole_fractions(0) if ok else []}
    return out


def summary(rows, solved):
    dev = [abs(1 - solved[r["row"]]["p_calc"] / r["p_exp"]) for r in rows if solved[r["row"]]["success"]]
    by_series = {}
    for r in rows:
        s = solved[r["row"]]
        if s["success"]:
            by_series.setdefault(r["series"], []).append(abs(1 - s["p_calc"] / r["p_exp"]))
    return {"rows": len(rows), "solved": len(dev), "unsolved_rows": [r["row"] for r in rows if not solved[r["row"]]["success"]],
            "ARD_percent_solved_rows": 100 * sum(dev) / len(dev) if dev else math.nan,
            "mean_ln_ratio": sum(math.log(solved[r["row"]]["p_calc"] / r["p_exp"]) for r in rows if solved[r["row"]]["success"]) / max(len(dev), 1),
            "ARD_percent_by_series": {k: 100 * sum(v) / len(v) for k, v in sorted(by_series.items())},
            "ARD_percent_by_MDEA_molality": {m: 100 * sum(a) / len(a) for m in ("about 2 mol/kg (19 mass %)", "3.9707 mol/kg (32 mass %)")
                                             for a in [[abs(1 - solved[r["row"]]["p_calc"] / r["p_exp"]) for r in rows
                                                        if solved[r["row"]]["success"] and (r["m_mdea"] > 3) == m.startswith("3.97")]]}}


def check_temperature_laws(T=373.15):
    """Self-check: the declared polynomial laws equal hand-evaluated constants at one temperature."""
    dt = T - model.T_REF
    constants = {pair: ((sum(c * dt**p for p, c in enumerate(coefficients)),), locator)
                 for pair, (coefficients, locator) in model.KIJ.items()}
    laws, fixed = model.document(), model.document(constants)
    for (i, j), (correction, _) in model.CROSS_ASSOCIATION.items():
        if correction:
            value = sum(c * dt**p for p, c in enumerate(correction))
            for edge in fixed["topology"]["edges"]:
                if edge.get("volume_correction", {}).get("identity") == f"association/{i}/{j}/volume_correction":
                    edge["volume_correction"] = {"identity": edge["volume_correction"]["identity"],
                                                 "value": {"magnitude": value, "unit": "dimensionless"}}
    x = [0.86, 0.06, 0.01, 0.03, 0.028, 0.001, 1e-9, 1e-9]
    x = [v / sum(x) for v in x]
    a, b = (epcsaft.Mixture(epcsaft.Parameters.from_mapping(d)).state(T, P=2e5, x=x, phase="liquid").log_fugacity_coefficient
            for d in (laws, fixed))
    assert max(abs(u - v) for u, v in zip(a, b)) < 1e-10, (a, b)


def printed():
    return model.document()


def initial_solvent(base):
    return lambda r: model.initial_solvent_permittivity(base(), r["T"], r["m_mdea"])


def spherical():
    return model.spherical_mdeah(model.document())


VARIANTS = {  # name: (document or per-row document function, role)
    "as-printed": (printed(), "the gate: Wangler Tables 2, 4-7 and Uyan Tables 1, 3-4 as printed; Engine speciated permittivity"),
    "as-printed, initial-solvent permittivity": (initial_solvent(printed), "gap (c) reading (ii) alone"),
    "spherical MDEAH+": (spherical(), "reading (i) alone: MDEAH+ segment number 1"),
    "spherical MDEAH+, initial-solvent permittivity": (initial_solvent(spherical), "readings (i) and (ii): candidate reproduction"),
}


def main():
    check_temperature_laws()
    if epcsaft.provenance()[1] != WHEEL_SHA256:
        sys.exit("installed Engine wheel is not the pinned 21e761c3 wheel")
    rows = kuranov_rows()
    RESULTS.mkdir(exist_ok=True)
    report, table = {}, {r["row"]: dict(r) for r in rows}
    for name, (doc, role) in VARIANTS.items():
        solved = solve_rows(doc, rows)
        report[name] = {"role": role, **summary(rows, solved)}
        for r in rows:
            table[r["row"]][f"p_calc_Pa[{name}]"] = solved[r["row"]]["p_calc"]
        print(name, json.dumps({k: v for k, v in report[name].items() if k != "ARD_percent_by_series"}), flush=True)
    model_doc = model.PARAMETERS.read_bytes()
    assert json.loads(model_doc) == json.loads(json.dumps(model.document())), "wangler-2018-parameters.json is stale: run model.py"
    report["provenance"] = {
        "engine_wheel_sha256": WHEEL_SHA256, "kuranov_csv_sha256": hashlib.sha256(KURANOV.read_bytes()).hexdigest(),
        "parameters_sha256": hashlib.sha256(model_doc).hexdigest(),
        "scripts_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (model.HERE / "model.py", Path(__file__))},
        "benchmark": "Wangler 2018 Table 11: 19.7 % ARD on 82 Kuranov rows; working gate 16.7-22.7 %"}
    (RESULTS / "reproduction-summary.json").write_text(json.dumps(report, indent=1) + "\n")
    with (RESULTS / "reproduction-rows.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, list(next(iter(table.values()))), lineterminator="\n")
        writer.writeheader()
        writer.writerows(table[k] for k in sorted(table))


if __name__ == "__main__":
    main()
