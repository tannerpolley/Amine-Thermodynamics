"""Diagnosis of the failed reproduction gate (issue #126 step 2). Writes results/diagnosis.json.

1. Mass action: the Engine's solved state satisfies Uyan Eqs. 17-23 with independently computed rational activity
   coefficients (pure water; every other species at infinite dilution in water).
2. Activity decomposition: ln gamma* at one Kuranov state under single-input changes to the printed MDEAH+ declaration.
3. Osmotic coefficients of aqueous MDEAH+Cl- (Wangler Tables 8-9, his fit target) with the printed declaration,
   after validating the same routine on NaCl (Held 2014 strategy 2).
4. Wangler section 6.2 speciation (x of H+ and MDEAH+ at 313 K, w_MDEA 0.23, loading 0.02 and 1.4).
5. Box corners of the planned constants k(water-MDEAH+), k(water-HCO3-) in [-0.3, 0.3]: fixed evaluations, not a fit.
"""
import hashlib
import json
import math

import epcsaft
from epcsaft import equilibrium

import model
import score

W, MDEA, MDEAH, HCO3 = model.W, model.MDEA, model.MDEAH, model.HCO3
STATE = 42  # Kuranov Table 2 right block row 1: 313.15 K, m_CO2 2.6729, m_MDEA 3.9707 mol/kg, 0.0735 MPa


def published():
    return model.document()


def spherical():
    return model.spherical_mdeah(model.document())


def set_kij(doc, a, b, value):
    for pair in doc["pairs"]:
        if {pair["component_id_a"], pair["component_id_b"]} == {a, b}:
            pair["coefficients"] = [{"family": "k_ij", "identity": f"pair/{a}/{b}/k_ij",
                                     "value": {"magnitude": value, "unit": "dimensionless"}}]
    return doc


def coefficient(doc, cid, family):
    comp = next(c for c in doc["components"] if c["component_id"] == cid)
    return next(c for c in comp["coefficients"] if c["family"] == family)["value"]


def ln_gamma(mix, T, P, x):
    """Rational ln gamma* (water: pure liquid) at fixed T, P, x; references at 1e-12 charge-balanced solute."""
    lnphi = mix.state(T, P=P, x=x, phase="liquid").log_fugacity_coefficient
    e = 1e-12
    ref = [1.0, e, e, e, e, e / 2, e, e / 2]
    ref = [v / sum(ref) for v in ref]
    lr = mix.state(T, P=P, x=ref, phase="liquid").log_fugacity_coefficient
    lw = mix.state(T, P=P, x=[1.0] + [0.0] * 7, phase="liquid").log_fugacity_coefficient[0]
    return dict(zip(model.SPECIES, [lnphi[0] - lw] + [a - b for a, b in zip(lnphi[1:], lr[1:])]))


def state_checks(row):
    mix = epcsaft.Mixture(epcsaft.Parameters.from_mapping(published()))
    solved = equilibrium.solve_equilibrium(mix, model.bubble_problem(row["T"], row["m_mdea"], row["m_co2"], row["p_exp"]))
    T, P, x = row["T"], solved.pressure[0], solved.phase_mole_fractions(0)
    g = ln_gamma(mix, T, P, x)
    xs = dict(zip(model.SPECIES, x))
    mass_action = {}
    for name, (nu, (c1, c2, c3, c4)) in model.REACTIONS.items():
        lnk = c1 + c2 / T + c3 * math.log(T) + c4 * T
        mass_action[name] = sum(v * (math.log(xs[i]) + g[i]) for i, v in nu.items()) - lnk
    variants = {"published": published(), "MDEAH+ segment number 1": spherical(),
                "k(water-MDEAH+) = 0": set_kij(published(), W, MDEAH, 0.0),
                "MDEAH+ packing diameter = sigma": published()}
    coefficient(variants["MDEAH+ packing diameter = sigma"], MDEAH, "packing_diameter")["magnitude"] = 3.563
    decomposition = {name: ln_gamma(epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc)), T, P, x)
                     for name, doc in variants.items()}
    return {"kuranov_row": row["row"], "T_K": T, "p_exp_Pa": row["p_exp"], "p_calc_Pa": P,
            "liquid_mole_fractions": xs, "mass_action_residual_ln": mass_action,
            "ln_gamma_star_at_published_solution": decomposition,
            "overall_MDEA+CO2+H2O->MDEAH++HCO3-_activity_term": {
                k: v[MDEAH] + v[HCO3] - v[MDEA] - v["carbon-dioxide"] - v[W] for k, v in decomposition.items()}}


def add_ion(doc, cid, mass, z, sigma, u, kij):
    """Append a Held 2014 strategy-2 ion (packing 0.88 sigma, Debye-Hueckel sigma) with its k_ij to every unlike-sign partner."""
    doc["components"].append({"component_id": cid, "fixed": {
        "molar_mass": {"identity": f"component/{cid}/molar_mass", "value": {"magnitude": mass, "unit": "kilogram / mole"}},
        "charge_number": {"identity": f"component/{cid}/charge_number", "value": {"magnitude": z, "unit": "elementary-charge"}}},
        "coefficients": [{"family": f, "identity": f"component/{cid}/{f}", "value": {"magnitude": v, "unit": unit}} for f, v, unit in (
            ("segment_count", 1.0, "dimensionless"), ("dispersion_energy_over_k", u, "kelvin"), ("segment_diameter", sigma, "angstrom"),
            ("packing_diameter", 0.88 * sigma, "angstrom"), ("debye_huckel_diameter", sigma, "angstrom"))]})
    for other in doc["components"][:-1]:
        if other["fixed"]["charge_number"]["value"]["magnitude"] * z <= 0:
            doc["pairs"].append({"component_id_a": other["component_id"], "component_id_b": cid, "coefficients": [{
                "family": "k_ij", "identity": f"pair/{other['component_id']}/{cid}/k_ij",
                "value": {"magnitude": kij.get(other["component_id"], 0.0), "unit": "dimensionless"}}]})
    return doc


def osmotic(doc, cation, anion, T, m):
    mix = epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc, components=[W, cation, anion]))
    n = [1 / model.COMPONENTS[W][0], m, m]
    x = [v / sum(n) for v in n]
    lw = mix.state(T, P=101325.0, x=x, phase="liquid").log_fugacity_coefficient[0]
    lw0 = mix.state(T, P=101325.0, x=[1.0, 0.0, 0.0], phase="liquid").log_fugacity_coefficient[0]
    return -(math.log(x[0]) + lw - lw0) / (model.COMPONENTS[W][0] * 2 * m)


MDEAHCL = [(273.15, 0.411, 0.835), (273.15, 0.546, 0.845), (273.15, 0.676, 0.838), (273.15, 0.784, 0.839),
           (273.15, 0.957, 0.854), (273.15, 1.023, 0.860), (273.15, 1.093, 0.861),  # Wangler Table 8
           (313.15, 0.403, 0.869), (313.15, 0.677, 0.861), (313.15, 1.141, 0.874)]  # Wangler Table 9
NACL_298 = [(0.5, 0.921), (1.0, 0.936), (2.0, 0.983), (4.0, 1.116)]  # Robinson & Stokes NaCl osmotic coefficients


def osmotic_checks():
    T = 298.15
    nacl = add_ion(add_ion(published(), "sodium-cation", 0.02298977, 1, 2.8232, 230.0, {W: -0.007981 * T + 2.37999}),
                   "chloride-anion", 0.035453, -1, 2.7560, 170.0, {W: -0.25, "sodium-cation": 0.317})
    out = {"NaCl_298K_validation": [{"m": m, "phi_ref": p, "phi_calc": osmotic(nacl, "sodium-cation", "chloride-anion", T, m)}
                                    for m, p in NACL_298]}
    for name, base in (("published", published()), ("MDEAH+ segment number 1", spherical())):
        doc = add_ion(base, "chloride-anion", 0.035453, -1, 2.7560, 170.0, {W: -0.25})  # MDEAH+-Cl- 0 (Wangler)
        calc = [osmotic(doc, MDEAH, "chloride-anion", T, m) for T, m, _ in MDEAHCL]
        out[f"MDEAH+Cl- {name}"] = {"rows": [{"T": T, "m": m, "phi_exp": p, "phi_calc": c} for (T, m, p), c in zip(MDEAHCL, calc)],
                                    "ARD_percent": 100 * sum(abs(1 - c / p) for c, (_, _, p) in zip(calc, MDEAHCL)) / len(calc)}
    out["Wangler_Fig10_ARD_percent"] = 5.05
    return out


def wangler_speciation():
    """Wangler section 6.2: at 313 K, w_MDEA = 0.23, x(H+) 3.80e-11 -> 3.32e-9 and x(MDEAH+) 9.80e-4 -> 3.37e-2 for alpha 0.02 -> 1.4."""
    T, m = 313.15, 0.23 / (0.77 * model.COMPONENTS[MDEA][0])
    out = {"reported": {"alpha=0.02": {"H+": 3.80e-11, "MDEAH+": 9.80e-4}, "alpha=1.4": {"H+": 3.32e-9, "MDEAH+": 3.37e-2}}}
    for name, doc in (("as-printed", published()),
                      ("spherical MDEAH+, initial-solvent permittivity", model.initial_solvent_permittivity(spherical(), T, m))):
        mix = epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc))
        out[name], guess = {}, (None, None)
        for alpha in (0.02, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4):  # warm-started loading sweep
            for p0 in (1e4, 1e5, 1e6, 1e7, 5e7):
                r = equilibrium.solve_equilibrium(mix, model.bubble_problem(T, m, alpha * m, p0, *guess))
                if r.success:
                    break
            x = dict(zip(model.SPECIES, r.phase_mole_fractions(0))) if r.success else {}
            if r.success:
                guess = (x, dict(zip(model.NEUTRAL, r.phase_mole_fractions(1)[:3])))
            out[name][f"alpha={alpha}"] = {"success": r.success, "H+": x.get(model.H), "MDEAH+": x.get(MDEAH),
                                           "P_Pa": r.pressure[0] if r.success else None}
    return out


def main():
    rows = score.kuranov_rows()
    report = {"state": state_checks(next(r for r in rows if r["row"] == STATE)), "osmotic": osmotic_checks(),
              "wangler_section_6_2_speciation": wangler_speciation()}
    corners = {}
    for name, base in (("as-printed", published), ("spherical MDEAH+, initial-solvent permittivity", spherical)):
        for k_mdeah in (-0.3, 0.3):
            for k_hco3 in (-0.3, 0.3):
                def doc(r, base=base, k_mdeah=k_mdeah, k_hco3=k_hco3, initial=name != "as-printed"):
                    d = set_kij(set_kij(base(), W, MDEAH, k_mdeah), W, HCO3, k_hco3)
                    return model.initial_solvent_permittivity(d, r["T"], r["m_mdea"]) if initial else d
                corners[f"{name}: k(w-MDEAH+)={k_mdeah}, k(w-HCO3-)={k_hco3}"] = score.summary(rows, score.solve_rows(doc, rows))
    report["box_corners_constant_kij"] = corners
    assert epcsaft.provenance()[1] == score.WHEEL_SHA256, "installed Engine wheel is not the pinned 21e761c3 wheel"
    report["provenance"] = {"engine_wheel_sha256": score.WHEEL_SHA256,
                            "kuranov_csv_sha256": hashlib.sha256(score.KURANOV.read_bytes()).hexdigest(),
                            "scripts_sha256": {p: hashlib.sha256((model.HERE / p).read_bytes()).hexdigest()
                                               for p in ("model.py", "score.py", "diagnose.py")}}
    (score.RESULTS / "diagnosis.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({"mass_action": report["state"]["mass_action_residual_ln"],
                      "overall_activity_term": report["state"]["overall_MDEA+CO2+H2O->MDEAH++HCO3-_activity_term"],
                      "osmotic_ARD": {k: v["ARD_percent"] for k, v in report["osmotic"].items() if isinstance(v, dict)},
                      "corners": {k: (v["solved"], round(v["ARD_percent_solved_rows"], 1)) for k, v in corners.items()}}, indent=1))


if __name__ == "__main__":
    main()
