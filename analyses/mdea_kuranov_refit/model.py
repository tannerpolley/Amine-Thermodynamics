"""Wangler 2018 explicit-ion ePC-SAFT for MDEA-CO2-H2O as an Engine parameter document, and its reactive bubble point.

The values below are the published model (issue #126). Each carries its source locator; the Engine evaluates them.
Run `python model.py` to (re)write wangler-2018-parameters.json from these declarations.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import epcsaft
from epcsaft import equilibrium

HERE = Path(__file__).resolve().parent
PARAMETERS = HERE / "wangler-2018-parameters.json"
T_REF = 298.15  # Wangler Eqs. 34-35, T+ = 298.15 K
W, MDEA, CO2 = "water", "methyldiethanolamine", "carbon-dioxide"
MDEAH, HCO3, CO3, H, OH = ("protonated-methyldiethanolamine", "bicarbonate-anion", "carbonate-anion",
                           "hydronium-cation", "hydroxide-anion")
SPECIES = (W, MDEA, CO2, MDEAH, HCO3, CO3, H, OH)
NEUTRAL = (W, MDEA, CO2)
WANGLER, UYAN, HELD = "Wangler2018 (Zotero ZILDPWWE)", "Uyan2015 (Zotero GSLTFVDM)", "Held2014 (Zotero 3DIW87Q5)"

# component: (molar mass kg/mol, charge, m, sigma A, u/k K, locator). Ions: packing 0.88 sigma (Uyan Eq. 10,
# Held2014 Eq. 21) and Debye-Hueckel diameter sigma (Held2008 Eq. 3, a_j = sigma_j); H+ uses the H3O+ set (Uyan p. 4)
# with the H+ molar mass so every reaction conserves mass.
COMPONENTS = {
    W: (0.01801528, 0, 1.2046, None, 353.94, f"{UYAN} Table 3; {WANGLER} Table 4"),
    MDEA: (0.1191622, 0, 3.675, 3.563, 228.711, f"{UYAN} Table 3; {WANGLER} Table 4"),
    CO2: (0.0440095, 0, 2.0729, 2.7852, 169.21, f"{UYAN} Table 3; {WANGLER} Table 4"),
    MDEAH: (0.12017014, 1, 3.675, 3.563, 228.71, f"{UYAN} Table 4 and footnote a; {WANGLER} Table 5 (MDEA values)"),
    HCO3: (0.06101684, -1, 1.0, 2.9296, 70.0, f"{WANGLER} Table 5; {HELD} Table 2 strategy 2"),
    CO3: (0.0600089, -2, 1.0, 2.4422, 249.26, f"{WANGLER} Table 5; {HELD} Table 2 strategy 2"),
    H: (0.00100794, 1, 1.0, 3.4654, 500.0, f"{WANGLER} Table 5; {HELD} Table 2 strategy 2 (H3O+)"),
    OH: (0.01700734, -1, 1.0, 2.0177, 650.0, f"{WANGLER} Table 5; {HELD} Table 2 strategy 2"),
}
WATER_SIGMA = (2.7927, ((10.11, -0.01775), (-1.417, -0.01146)))  # Uyan Table 3 footnote; Wangler Table 4 footnote
# Relative permittivity (Uyan Eq. 5, mass-weighted water/MDEA, ions and CO2 excluded): polynomial in T - 298.15 K.
PERMITTIVITY = {
    W: ((78.41043478578715, -0.36133766233691506, 0.00076555618295),
        "repository water law reused from analyses/mea_parameter_bundle (uyan-2015-permittivity-transfer); Uyan cites "
        "Floriano & Nascimento 2004 (Zotero NBK9T7B7), which tabulates only 273-348 K"),
    MDEA: ((22.358, -0.10245714285714318),
           "least-squares line through Hsieh, Chen & Li 2007 pure-MDEA values 303.15-328.15 K "
           "(doi 10.1021/je600515j; NIST ThermoML; data/reference/MDEA/Hsieh_2007_MDEA_relative_permittivity.csv)"),
}
# Self association (2B water, 4C MDEA as 2 donor + 2 acceptor sites); MDEAH+ carries MDEA's sites with zero energy.
SELF_ASSOCIATION = {
    W: (1, 2425.67, 0.04509, f"{UYAN} Table 3"),
    MDEA: (2, 2046.624, 0.123858, f"{UYAN} Table 3"),
    MDEAH: (2, 0.0, 0.123858, f"{UYAN} Table 4 footnote a; {WANGLER} section 3"),
}
# Wolbach-Sandler cross edges (Uyan Eqs. 8-9, Wangler Eqs. 10-12) with the l_hb correction c(T) of Wangler Table 7.
CROSS_ASSOCIATION = {
    (W, MDEA): ((0.600, -2.57e-3, -1.70e-5), f"{WANGLER} Table 7, Eq. 35"),
    (W, MDEAH): ((0.372, 1.07e-3), f"{WANGLER} Table 7, Eq. 35"),
    (MDEA, MDEAH): (None, f"{WANGLER} section 3 ('cross-associate to water or MDEA'); {UYAN} Table 4 footnote a"),
}
# k_ij: constants or Wangler Eq. 34 polynomials in T - 298.15 K (Table 6). Unlisted pairs are zero (Uyan section 4.2).
KIJ = {
    (W, MDEA): ((-0.184, -1.21e-3, 2.70e-6, 1.53e-7), f"{WANGLER} Table 6"),
    (W, CO2): ((-0.0215, 4.20e-4, -1.70e-6), f"{WANGLER} Table 6"),
    (W, H): ((0.25,), f"{WANGLER} Table 6"),
    (W, OH): ((-0.25,), f"{WANGLER} Table 6"),
    (W, HCO3): ((-0.0765, -6.25e-4, -6.25e-5), f"{WANGLER} Table 6"),
    (W, CO3): ((-0.25,), f"{WANGLER} Table 6"),
    (W, MDEAH): ((-0.184, -1.21e-3, 2.70e-6, 1.53e-7), f"{WANGLER} Table 6"),
}
# ln K = c1 + c2/T + c3 ln T + c4 T on the mole-fraction basis, water pure liquid and every other species at infinite
# dilution in water (Uyan Table 1 and Eqs. 17-23; Wangler Table 2 prints the same constants rounded).
REACTIONS = {
    "R1": ({W: -1, H: 1, OH: 1}, (132.899, -13445.9, -22.477, 0.0)),
    "R2": ({CO2: -1, W: -1, HCO3: 1, H: 1}, (212.739, -11333.8, -33.844, -0.0018149)),
    "R3": ({HCO3: -1, CO3: 1, H: 1}, (287.444, -13648.7, -48.880, 0.030232)),
    "R4": ({MDEAH: -1, MDEA: 1, H: 1}, (-83.491, -819.7, 10.976, 0.0)),
}
STANDARD_STATE_ID = "aqueous-mole-fraction-infinite-dilution-water-v1"


def _value(magnitude, unit):
    return {"magnitude": magnitude, "unit": unit}


def _law(identity, coefficients, unit_prefix="dimensionless"):
    """One value, or a polynomial temperature law in T - 298.15 K (Engine #567 grammar)."""
    if len(coefficients) == 1:
        return {"identity": identity, "value": _value(coefficients[0], unit_prefix)}
    units = ["dimensionless", "1 / kelvin", "1 / kelvin ** 2", "1 / kelvin ** 3"]
    return {"identity": identity, "temperature_law": {
        "form": "polynomial-plus-reciprocal-temperature", "reference_temperature": _value(T_REF, "kelvin"),
        "terms": [{"power": p, "coefficient": {"identity": f"{identity}/a{p}", "value": _value(c, units[p])}}
                  for p, c in enumerate(coefficients)]}}


def document(kij=KIJ):
    components, correlations = [], []
    for cid, (mass, charge, m, sigma, u, locator) in COMPONENTS.items():
        coefficients = [("segment_count", m, "dimensionless"), ("dispersion_energy_over_k", u, "kelvin")]
        if sigma is not None:
            coefficients.append(("segment_diameter", sigma, "angstrom"))
        if charge:
            coefficients += [("packing_diameter", 0.88 * sigma, "angstrom"), ("debye_huckel_diameter", sigma, "angstrom")]
        components.append({"component_id": cid, "provenance": locator, "fixed": {
            "molar_mass": {"identity": f"component/{cid}/molar_mass", "value": _value(mass, "kilogram / mole")},
            "charge_number": {"identity": f"component/{cid}/charge_number", "value": _value(charge, "elementary-charge")}},
            "coefficients": [{"family": f, "identity": f"component/{cid}/{f}", "value": _value(v, unit)}
                             for f, v, unit in coefficients]})
    prefix = "component/water/segment_diameter"
    correlations.append({"component_id": W, "correlation_id": prefix, "family": "segment_diameter",
                         "form": "constant-plus-sum-of-exponentials",
                         "constant": {"identity": f"{prefix}/constant", "value": _value(WATER_SIGMA[0], "angstrom")},
                         "terms": [{"amplitude": {"identity": f"{prefix}/term-{k}/amplitude", "value": _value(a, "angstrom")},
                                    "exponent_coefficient": {"identity": f"{prefix}/term-{k}/exponent",
                                                             "value": _value(b, "1 / kelvin")}}
                                   for k, (a, b) in enumerate(WATER_SIGMA[1])]})
    for cid, (coefficients, locator) in PERMITTIVITY.items():
        prefix = f"component/{cid}/relative_permittivity"
        correlations.append({
            "component_id": cid, "correlation_id": prefix, "family": "relative_permittivity", "provenance": locator,
            "form": "constant-plus-polynomial-in-temperature", "reference_temperature": _value(T_REF, "kelvin"),
            "constant": {"identity": f"{prefix}/constant", "value": _value(coefficients[0], "dimensionless")},
            "terms": [{"power": p, "coefficient": {"identity": f"{prefix}/a{p}", "value": _value(c, ["1 / kelvin", "1 / kelvin ** 2"][p - 1])}}
                      for p, c in enumerate(coefficients) if p]})
    zero = ((0.0,), f"zero: {UYAN} section 4.2 applies binary parameters only to water pairs; {WANGLER} Table 6")
    pairs = [{"component_id_a": a, "component_id_b": b, "provenance": locator,
              "coefficients": [{"family": "k_ij", **_law(f"pair/{a}/{b}/k_ij", c)}]}
             for k, a in enumerate(SPECIES) for b in SPECIES[k + 1:] if COMPONENTS[a][1] * COMPONENTS[b][1] <= 0
             for c, locator in [kij.get((a, b), kij.get((b, a), zero))]]
    sites, edges = [], []
    for cid, (n, energy, volume, locator) in SELF_ASSOCIATION.items():
        sites += [{"component_id": cid, "site_id": s, "site_role": role, "multiplicity": n}
                  for s, role in (("a", "donor"), ("b", "acceptor"))]
        edges.append({"endpoint_a": {"component_id": cid, "site_id": "a"}, "endpoint_b": {"component_id": cid, "site_id": "b"},
                      "source": {"kind": "explicit", "provenance": locator},
                      "energy_over_k": {"identity": f"association/{cid}/energy_over_k", "value": _value(energy, "kelvin")},
                      "volume": {"identity": f"association/{cid}/volume", "value": _value(volume, "dimensionless")}})
    for (i, j), (correction, locator) in CROSS_ASSOCIATION.items():
        for donor, acceptor in ((i, j), (j, i)):
            edge = {"endpoint_a": {"component_id": donor, "site_id": "a"},
                    "endpoint_b": {"component_id": acceptor, "site_id": "b"},
                    "source": {"kind": "combining-rule", "rule_id": "wolbach-sandler", "provenance": locator, "inputs": {
                        "energy_over_k": [f"association/{i}/energy_over_k", f"association/{j}/energy_over_k"],
                        "volume": [f"association/{i}/volume", f"association/{j}/volume"]}}}
            if correction is not None:
                edge["volume_correction"] = _law(f"association/{i}/{j}/volume_correction", correction)
            edges.append(edge)
    families = [{"kind": "base", "choice": "pc-saft"}, {"kind": "association", "choice": "general-site"},
                {"kind": "electrolyte", "choice": "fully-dissociated-debye-huckel", "ionic_dispersion": "exclude-same-sign-ion-pairs",
                 "provenance": f"{UYAN} section 2 (Debye-Hueckel, no Born; no like-ion dispersion)"},
                {"kind": "permittivity", "choice": "solvent-only", "provenance": f"{UYAN} Eq. 5"}]
    return {"schema": "epcsaft.parameters", "schema_version": 1, "document_id": "mdea-wangler-2018-reproduction",
            "document_version": 1, "purpose": "Fixed published Wangler 2018 MDEA-CO2-H2O model (issue #126)",
            "components": components, "correlations": correlations, "pairs": pairs, "model_families": families,
            "topology": {"sites": sites, "edges": edges},
            "reaction_correlations": [{"reaction_id": r, "stoichiometry": s, "c1_c2_c3_c4": c,
                                       "basis": STANDARD_STATE_ID} for r, (s, c) in REACTIONS.items()]}


def charged_molecule_ions(doc, *ions):
    """Reading (A), issue #126 D1: keep self dispersion and the neutral diameter (Engine #641)."""
    for comp in doc["components"]:
        if comp["component_id"] in ions:
            comp["fixed"]["charged_molecule_ion"] = {"value": _value(1, "dimensionless")}
            comp["coefficients"] = [c for c in comp["coefficients"] if c["family"] != "packing_diameter"]
    return doc


def spherical_mdeah(doc):
    """Interpretation (i): MDEAH+ segment number 1 instead of MDEA's 3.675 (README, 'Diagnosis')."""
    comp = next(c for c in doc["components"] if c["component_id"] == MDEAH)
    next(c for c in comp["coefficients"] if c["family"] == "segment_count")["value"]["magnitude"] = 1.0
    return doc


def initial_solvent_permittivity(doc, T, m_mdea):
    """Interpretation (ii) of gap (c): Uyan Eq. 5 on the initial CO2-free water/MDEA solvent, a constant per state.
    Expressed by giving water that constant and removing MDEA's law, so it holds for one (T, m_MDEA) only.
    A local diagnostic recomputation of Uyan Eq. 5: it must not feed adopted results."""
    w = m_mdea * COMPONENTS[MDEA][0] / (1 + m_mdea * COMPONENTS[MDEA][0])
    eps = {cid: sum(c * (T - T_REF) ** p for p, c in enumerate(law)) for cid, (law, _) in PERMITTIVITY.items()}
    water = next(c for c in doc["correlations"] if c["correlation_id"] == "component/water/relative_permittivity")
    water["constant"]["value"]["magnitude"], water["terms"] = (1 - w) * eps[W] + w * eps[MDEA], []
    doc["correlations"] = [c for c in doc["correlations"] if c["correlation_id"] != f"component/{MDEA}/relative_permittivity"]
    return doc


def reactions(shift=None):
    """`shift` (reaction -> added ln K) is a diagnostic hook for conventions.py; None is the published model."""
    shift = shift or {}
    return [equilibrium.Reaction(
        stoichiometry, name=name,
        correlation=equilibrium.ReactionLogPolynomial(c1 + shift.get(name, 0.0) + c3 * math.log(T_REF), c2, c3, c4, T_REF,
                                                      273.15, 423.15, STANDARD_STATE_ID),
        reference=equilibrium.ReactionReference(equilibrium.ReferenceSourceBasis.RawMoleFractionInfiniteDilution))
        for name, (stoichiometry, (c1, c2, c3, c4)) in REACTIONS.items()]


# A positive charge-neutral all-solute dilution path toward infinite dilution in water (scale as in the MEA evaluator).
NEUTRAL_REFERENCE = equilibrium.NeutralReference(
    solvent=W, standard_molality_mol_per_kg=1.0,
    solute_molality_ratios={MDEA: 0.125, CO2: 0.125, MDEAH: 0.125, H: 0.125, HCO3: 0.125, OH: 0.0625, CO3: 0.03125})


def bubble_problem(T, m_mdea, m_co2, p_guess, liquid_guess=None, vapor_guess=None, neutral_reference=NEUTRAL_REFERENCE,
                   shift=None):
    """Reactive bubble point at T (K) for stoichiometric molalities (mol/kg water); P is solved."""
    n_w = 1.0 / COMPONENTS[W][0]
    if liquid_guess is None:  # ideal-speciation seed: MDEA + CO2 + H2O -> MDEAH+ + HCO3-
        xi = 0.97 * min(m_mdea, m_co2)
        guess = {W: n_w - xi, MDEA: m_mdea - xi + 1e-6, CO2: m_co2 - xi + 1e-4 * m_co2, MDEAH: xi, HCO3: xi,
                 CO3: 1e-3 * xi, H: 1e-9, OH: 1e-7}
        total = sum(guess.values())
        liquid_guess = {k: v / total for k, v in guess.items()}
    if vapor_guess is None:
        vapor_guess = {W: 0.5, MDEA: 1e-4, CO2: 0.4999}
    return equilibrium.Problem(
        phases=[equilibrium.Phase("L", kind="liquid", support=SPECIES, composition_guess=liquid_guess),
                equilibrium.Phase("V", kind="vapor", support=NEUTRAL, amount=equilibrium.Pinned(0.0),
                                  composition_guess=vapor_guess)],
        T=T, P=equilibrium.Free(p_guess), feed=equilibrium.Amounts({W: n_w, MDEA: m_mdea, CO2: m_co2}),
        reactions=reactions(shift), neutral_reference=neutral_reference)


if __name__ == "__main__":
    PARAMETERS.write_text(json.dumps(charged_molecule_ions(document(), MDEAH), indent=1) + "\n")
    print(PARAMETERS, epcsaft.Parameters.from_mapping(document()).component_ids)
