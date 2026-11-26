"""Fixed-reference MDEA reported declarations."""

from collections import Counter
import csv
import math
from math import comb
from statistics import fmean

import epcsaft
from epcsaft import equilibrium
from MEA.common.retained_results import read

from .model import CAMPAIGN_ARCHIVE, ELECTROSTATICS, P_REF, REPORTED, ROOT, Route, evaluate

DECLARATION = ROOT / "analyses/mdea_mea_workflow/inputs/bounded-binary-411.json"
BOUNDED_BINARY = ROOT / "analyses/mdea_mea_workflow/results/bounded-binary-411"
UNBOUNDED_BINARY = BOUNDED_BINARY / "fits/unbounded-2"
KURANOV_LOG_SCALE = 0.015


class MDEAWeights(Route):
    def bind(self, point):
        spec = super().bind(point)
        rows = spec.inputs["observations"]["fitted"]
        group_counts = Counter(row["group"] for row in rows)
        assert "measurement_covariance" not in spec.spec
        for row in rows:
            group = row["group"]
            row["weight"] = 1 / group_counts[group]
            if group == "Kuranov":
                assert row["arguments"]["form"] == "log_ratio"
                row["weight"] /= KURANOV_LOG_SCALE**2
        return spec


T_REF = 298.15  # Wangler Eqs. 34-35, T+ = 298.15 K
W, MDEA, CO2 = "water", "methyldiethanolamine", "carbon-dioxide"
MDEAH, HCO3, CO3, H, OH = (
    "protonated-methyldiethanolamine",
    "bicarbonate-anion",
    "carbonate-anion",
    "hydronium-cation",
    "hydroxide-anion",
)
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
    W: (
        (78.41043478578715, -0.36133766233691506, 0.00076555618295),
        "repository water law reused from analyses/mea_parameter_bundle (uyan-2015-permittivity-transfer); Uyan cites "
        "Floriano & Nascimento 2004 (Zotero NBK9T7B7), which tabulates only 273-348 K",
    ),
    MDEA: (
        (22.358, -0.10245714285714318),
        "least-squares line through Hsieh, Chen & Li 2007 pure-MDEA values 303.15-328.15 K "
        "(doi 10.1021/je600515j; NIST ThermoML; data/reference/MDEA/Hsieh_2007_MDEA_relative_permittivity.csv)",
    ),
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
    return {
        "identity": identity,
        "temperature_law": {
            "form": "polynomial-plus-reciprocal-temperature",
            "reference_temperature": _value(T_REF, "kelvin"),
            "terms": [
                {"power": p, "coefficient": {"identity": f"{identity}/a{p}", "value": _value(c, units[p])}}
                for p, c in enumerate(coefficients)
            ],
        },
    }


def document(kij=KIJ):
    components, correlations = [], []
    for cid, (mass, charge, m, sigma, u, locator) in COMPONENTS.items():
        coefficients = [("segment_count", m, "dimensionless"), ("dispersion_energy_over_k", u, "kelvin")]
        if sigma is not None:
            coefficients.append(("segment_diameter", sigma, "angstrom"))
        if charge:
            coefficients += [
                ("packing_diameter", 0.88 * sigma, "angstrom"),
                ("debye_huckel_diameter", sigma, "angstrom"),
            ]
        components.append(
            {
                "component_id": cid,
                "provenance": locator,
                "fixed": {
                    "molar_mass": {"identity": f"component/{cid}/molar_mass", "value": _value(mass, "kilogram / mole")},
                    "charge_number": {
                        "identity": f"component/{cid}/charge_number",
                        "value": _value(charge, "elementary-charge"),
                    },
                },
                "coefficients": [
                    {"family": f, "identity": f"component/{cid}/{f}", "value": _value(v, unit)}
                    for f, v, unit in coefficients
                ],
            }
        )
    prefix = "component/water/segment_diameter"
    correlations.append(
        {
            "component_id": W,
            "correlation_id": prefix,
            "family": "segment_diameter",
            "form": "constant-plus-sum-of-exponentials",
            "constant": {"identity": f"{prefix}/constant", "value": _value(WATER_SIGMA[0], "angstrom")},
            "terms": [
                {
                    "amplitude": {"identity": f"{prefix}/term-{k}/amplitude", "value": _value(a, "angstrom")},
                    "exponent_coefficient": {
                        "identity": f"{prefix}/term-{k}/exponent",
                        "value": _value(b, "1 / kelvin"),
                    },
                }
                for k, (a, b) in enumerate(WATER_SIGMA[1])
            ],
        }
    )
    for cid, (coefficients, locator) in PERMITTIVITY.items():
        prefix = f"component/{cid}/relative_permittivity"
        correlations.append(
            {
                "component_id": cid,
                "correlation_id": prefix,
                "family": "relative_permittivity",
                "provenance": locator,
                "form": "constant-plus-polynomial-in-temperature",
                "reference_temperature": _value(T_REF, "kelvin"),
                "constant": {"identity": f"{prefix}/constant", "value": _value(coefficients[0], "dimensionless")},
                "terms": [
                    {
                        "power": p,
                        "coefficient": {
                            "identity": f"{prefix}/a{p}",
                            "value": _value(c, ["1 / kelvin", "1 / kelvin ** 2"][p - 1]),
                        },
                    }
                    for p, c in enumerate(coefficients)
                    if p
                ],
            }
        )
    zero = ((0.0,), f"zero: {UYAN} section 4.2 applies binary parameters only to water pairs; {WANGLER} Table 6")
    pairs = [
        {
            "component_id_a": a,
            "component_id_b": b,
            "provenance": locator,
            "coefficients": [{"family": "k_ij", **_law(f"pair/{a}/{b}/k_ij", c)}],
        }
        for k, a in enumerate(SPECIES)
        for b in SPECIES[k + 1 :]
        if COMPONENTS[a][1] * COMPONENTS[b][1] <= 0
        for c, locator in [kij.get((a, b), kij.get((b, a), zero))]
    ]
    sites, edges = [], []
    for cid, (n, energy, volume, locator) in SELF_ASSOCIATION.items():
        sites += [
            {"component_id": cid, "site_id": s, "site_role": role, "multiplicity": n}
            for s, role in (("a", "donor"), ("b", "acceptor"))
        ]
        edges.append(
            {
                "endpoint_a": {"component_id": cid, "site_id": "a"},
                "endpoint_b": {"component_id": cid, "site_id": "b"},
                "source": {"kind": "explicit", "provenance": locator},
                "energy_over_k": {"identity": f"association/{cid}/energy_over_k", "value": _value(energy, "kelvin")},
                "volume": {"identity": f"association/{cid}/volume", "value": _value(volume, "dimensionless")},
            }
        )
    for (i, j), (correction, locator) in CROSS_ASSOCIATION.items():
        for donor, acceptor in ((i, j), (j, i)):
            edge = {
                "endpoint_a": {"component_id": donor, "site_id": "a"},
                "endpoint_b": {"component_id": acceptor, "site_id": "b"},
                "source": {
                    "kind": "combining-rule",
                    "rule_id": "wolbach-sandler",
                    "provenance": locator,
                    "inputs": {
                        "energy_over_k": [f"association/{i}/energy_over_k", f"association/{j}/energy_over_k"],
                        "volume": [f"association/{i}/volume", f"association/{j}/volume"],
                    },
                },
            }
            if correction is not None:
                edge["volume_correction"] = _law(f"association/{i}/{j}/volume_correction", correction)
            edges.append(edge)
    families = [
        {"kind": "base", "choice": "pc-saft"},
        {"kind": "association", "choice": "general-site"},
        {
            "kind": "electrolyte",
            "choice": "fully-dissociated-debye-huckel",
            "ionic_dispersion": "exclude-same-sign-ion-pairs",
            "provenance": f"{UYAN} section 2 (Debye-Hueckel, no Born; no like-ion dispersion)",
        },
        {"kind": "permittivity", "choice": "solvent-only", "provenance": f"{UYAN} Eq. 5"},
    ]
    return {
        "schema": "epcsaft.parameters",
        "schema_version": 1,
        "document_id": "mdea-wangler-2018-reproduction",
        "document_version": 1,
        "purpose": "Fixed published Wangler 2018 MDEA-CO2-H2O model (issue #126)",
        "components": components,
        "correlations": correlations,
        "pairs": pairs,
        "model_families": families,
        "topology": {"sites": sites, "edges": edges},
        "reaction_correlations": [
            {"reaction_id": r, "stoichiometry": s, "c1_c2_c3_c4": c, "basis": STANDARD_STATE_ID}
            for r, (s, c) in REACTIONS.items()
        ],
    }


def charged_molecule_ions(doc, *ions):
    """Reading (A), issue #126 D1: keep self dispersion and the neutral diameter (Engine #641)."""
    for comp in doc["components"]:
        if comp["component_id"] in ions:
            comp["fixed"]["charged_molecule_ion"] = {"value": _value(1, "dimensionless")}
            comp["coefficients"] = [c for c in comp["coefficients"] if c["family"] != "packing_diameter"]
    return doc


def reactions(shift=None):
    """`shift` (reaction -> added ln K) is a diagnostic hook for conventions.py; None is the published model."""
    shift = shift or {}
    return [
        equilibrium.Reaction(
            stoichiometry,
            name=name,
            correlation=equilibrium.ReactionLogPolynomial(
                c1 + shift.get(name, 0.0) + c3 * math.log(T_REF), c2, c3, c4, T_REF, 273.15, 423.15, STANDARD_STATE_ID
            ),
            reference=equilibrium.ReactionReference(equilibrium.ReferenceSourceBasis.RawMoleFractionInfiniteDilution),
        )
        for name, (stoichiometry, (c1, c2, c3, c4)) in REACTIONS.items()
    ]


# A positive charge-neutral all-solute dilution path toward infinite dilution in water (scale as in the MEA evaluator).
NEUTRAL_REFERENCE = equilibrium.NeutralReference(
    solvent=W,
    standard_molality_mol_per_kg=1.0,
    solute_molality_ratios={MDEA: 0.125, CO2: 0.125, MDEAH: 0.125, H: 0.125, HCO3: 0.125, OH: 0.0625, CO3: 0.03125},
)


def bubble_problem(
    T, m_mdea, m_co2, p_guess, liquid_guess=None, vapor_guess=None, neutral_reference=NEUTRAL_REFERENCE, shift=None
):
    """Reactive bubble point at T (K) for stoichiometric molalities (mol/kg water); P is solved."""
    n_w = 1.0 / COMPONENTS[W][0]
    if liquid_guess is None:  # ideal-speciation seed: MDEA + CO2 + H2O -> MDEAH+ + HCO3-
        xi = 0.97 * min(m_mdea, m_co2)
        guess = {
            W: n_w - xi,
            MDEA: m_mdea - xi + 1e-6,
            CO2: m_co2 - xi + 1e-4 * m_co2,
            MDEAH: xi,
            HCO3: xi,
            CO3: 1e-3 * xi,
            H: 1e-9,
            OH: 1e-7,
        }
        total = sum(guess.values())
        liquid_guess = {k: v / total for k, v in guess.items()}
    if vapor_guess is None:
        vapor_guess = {W: 0.5, MDEA: 1e-4, CO2: 0.4999}
    return equilibrium.Problem(
        phases=[
            equilibrium.Phase("L", kind="liquid", support=SPECIES, composition_guess=liquid_guess),
            equilibrium.Phase(
                "V", kind="vapor", support=NEUTRAL, amount=equilibrium.Pinned(0.0), composition_guess=vapor_guess
            ),
        ],
        T=T,
        P=equilibrium.Free(p_guess),
        feed=equilibrium.Amounts({W: n_w, MDEA: m_mdea, CO2: m_co2}),
        reactions=reactions(shift),
        neutral_reference=neutral_reference,
    )


def about_298_15(coefficients, t0):
    """Re-express sum a_k (T - t0)^k exactly as a polynomial in T - 298.15 K (the document's reference)."""
    d = T_REF - t0
    return tuple(
        sum(a * comb(k, j) * d ** (k - j) for k, a in enumerate(coefficients) if k >= j)
        for j in range(len(coefficients))
    )


UYAN_EQ26 = about_298_15((-2.2e-2, 4.2e-4, -1.7e-6), 298.0)  # Uyan Eq. 26 (p. 96), k(CO2-water), T+ = 298 K
UYAN_EQ27 = about_298_15((-1.5275e-2, -5.24e-5, 7.9e-6), 298.0)  # Uyan Eq. 27 (p. 96), k(MDEA-water), T+ = 298 K
UYAN_KIJ = {
    (W, MDEA): (UYAN_EQ27, f"{UYAN} Eq. 27, Table 5"),
    (W, CO2): (UYAN_EQ26, f"{UYAN} Eq. 26, Table 5"),
    (W, H): ((0.25,), f"{UYAN} Table 5"),
    (W, OH): ((-0.25,), f"{UYAN} Table 5"),
    (W, CO3): ((-0.25,), f"{UYAN} Table 5"),  # HCO3-/water is '-' in Table 5: zero
    (W, MDEAH): (UYAN_EQ27, f"{UYAN} Table 5 'Eq. (27)'; section 4.3.2 'inherited from MDEA/water'"),
}


def uyan(mdeah_kij=True):
    """Uyan 2015 as printed: Tables 1, 3-5, Eqs. 26-27, k_hb(water-MDEA) = 0.015 (Table 5 footnote a), no correction on
    the water-MDEAH+ and MDEA-MDEAH+ edges.  mdeah_kij=False takes section 4.2.1 ('set to zero') instead of Table 5."""
    kij = dict(UYAN_KIJ)
    if not mdeah_kij:
        kij.pop((W, MDEAH))
    doc = document(kij)
    for edge in doc["topology"]["edges"]:
        identity = edge.get("volume_correction", {}).get("identity", "")
        if identity == f"association/{W}/{MDEA}/volume_correction":
            edge["volume_correction"] = _law(identity, (0.015,))
        elif identity:
            del edge["volume_correction"]
    doc["document_id"], doc["purpose"] = "mdea-uyan-2015-reproduction", "Fixed published Uyan 2015 model (issue #126)"
    return doc


def kuranov_rows(path):
    with path.open(newline="") as handle:
        return [
            {
                "row": int(r["source_row"]),
                "series": r["source_series"],
                "T": float(r["temperature_K"]),
                "m_mdea": float(r["m_MDEA_mol_per_kg_H2O"]),
                "m_co2": float(r["m_CO2_mol_per_kg_H2O"]),
                "p_exp": float(r["ten_times_total_pressure_MPa"]) * 1e5,
            }
            for r in csv.DictReader(handle)
        ]


def solve_rows(doc, rows):
    """Bubble pressure of every row; within an isotherm series each solve starts from the previous solution.
    Rows are grouped by their retained pressure series."""
    mix = epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc))
    out, previous = {}, {}
    for r in sorted(rows, key=lambda r: (r["series"], r["m_co2"])):
        start = previous.get(r["series"])
        result = None
        for guess in ([start] if start else []) + [None]:  # warm start, then the ideal-speciation seed
            problem = bubble_problem(r["T"], r["m_mdea"], r["m_co2"], r["p_exp"], *(guess if guess else (None, None)))
            result = equilibrium.solve_equilibrium(mix, problem)
            if result.success:
                break
        ok = result.success
        if ok:
            previous[r["series"]] = (
                dict(zip(SPECIES, result.phase_mole_fractions(0))),
                dict(zip(NEUTRAL, result.phase_mole_fractions(1)[:3])),
            )
        out[r["row"]] = {
            "success": ok,
            "message": result.message,
            "linear_solver": result.linear_solver,
            "p_calc": result.pressure if ok else None,
            "x_liquid": result.phase_mole_fractions(0) if ok else [],
            "y_vapor": result.phase_mole_fractions(1)[:3] if ok else [],
        }
    return out


def replay_records(spec, row):
    records = [
        r
        for role in ("fitted", "comparisons")
        for r in spec.inputs["observations"][role]
        if r["group"].startswith("Kuranov")
    ]
    comparison = next(r for r in records if r["group"] == "Kuranov-413K")
    dataset = next(d for d in spec.spec["datasets"] if d["name"] == "outside-fit-Kuranov-413K")
    key = f"kuranov:{row['row']}"
    state = dict(
        T=row["T"],
        P=row["p_exp"],
        water=1 / 0.01801528 / row["m_mdea"],
        alpha=row["alpha"],
        observed=row["p_exp"],
        scale=1.0,
    )
    spec.problems[key] = spec.problem(dataset["template"], state)
    args = spec.bind(dataset["arguments"], state)
    basis = dict(comparison["basis"], arguments=args, template=dataset["template"])
    return records + [
        dict(
            comparison,
            identity=key,
            problem=key,
            row={"source_row": str(row["row"])},
            arguments=args,
            basis=basis,
            group="Kuranov-393K",
            role="not fitted",
        )
    ]


def pressure_deviation(rows, name):
    unsolved = [r["row"] for r in rows if r[name]["pressure_Pa"] is None]
    errors = {r["row"]: 100 * (r[name]["pressure_Pa"] / r["p_exp"] - 1) for r in rows if r["row"] not in unsolved}
    aard = fmean(map(abs, errors.values())) if errors else None
    worst = max(errors, key=lambda i: abs(errors[i])) if errors else None
    return dict(
        n=len(rows),
        solved=len(errors),
        unsolved_rows=unsolved,
        AARD_percent=None if unsolved else aard,
        solved_AARD_percent=aard,
        bias_percent=fmean(errors.values()) if errors else None,
        max_abs_percent=abs(errors[worst]) if errors else None,
        worst_row=worst,
    )


def replay_published(declaration):
    rows = [dict(row, alpha=row["m_co2"] / row["m_mdea"]) for row in kuranov_rows(declaration["observations"])]
    route = Route(declaration["specification"], reference_pressure_pa=None)
    spec = route.bind(read(declaration["endpoint"]))
    restore = next(row for row in rows if row["row"] == declaration["restored_row"])
    predictions = evaluate(spec, replay_records(spec, restore))
    for row, predicted in zip(rows, sorted(predictions, key=lambda p: int(p["row"]["source_row"])), strict=True):
        if row["row"] != int(predicted["row"]["source_row"]):
            raise ValueError(f"Mismatched Kuranov row {row['row']}")
        row["present"] = dict(pressure_Pa=predicted["value"], status=predicted["status"])
    references = {name: read(path) for name, path in declaration["reference"].items()}
    own = [dict(row, row=row["source_row"]) for row in references["wangler"]]
    documents = dict(
        Uyan=uyan(), Uyan_k0=uyan(False), Wangler=document(), Wangler_charged=charged_molecule_ions(document(), MDEAH)
    )
    for name, point in documents.items():
        for campaign in (rows, own) if name.startswith("Wangler") else (rows,):
            solved = solve_rows(point, campaign)
            for row in campaign:
                result = solved[row["row"]]
                row[name] = dict(
                    pressure_Pa=result["p_calc"],
                    status="solved" if result["success"] else "unsolved",
                    linear_solver=result["linear_solver"],
                    message=result["message"],
                )
    selected = {row["row"]: row for row in rows}
    stats = references["statistics"]
    subsets = {name: [selected[i] for i in ids] for name, ids in stats["sets"].items() if name != "Wangler Table 10"}
    subsets["Wangler Table 10"] = own
    present = {name: pressure_deviation(subsets[name], "present") for name in stats["present"]}
    reconstruction = [
        dict(
            reading=r["reading"],
            subset=r["subset"],
            printed=r["printed"],
            **pressure_deviation(subsets[r["subset"]], r["reading"]),
        )
        for r in stats["reconstruction"]
    ]
    return dict(kuranov=rows, wangler=own, statistics=dict(present=present, reconstruction=reconstruction))


(CATION_REPLAY,) = ELECTROSTATICS.glob("*/*/methyldiethanolamine")
FIT_SETS = {
    **{
        f"born-{arm}": dict(
            route=Route,
            declaration=DECLARATION,
            reference_pressure_pa=None,
            archive=CAMPAIGN_ARCHIVE,
            endpoint=BOUNDED_BINARY / "endpoint.json",
            endpoint_keys=(),
            born_diameter=("protonated-methyldiethanolamine", CATION_REPLAY / arm / "replay.json.gz"),
            reference=CATION_REPLAY / arm / "data-rows.json.gz",
            reference_keys=(),
            objective=CATION_REPLAY / arm / "replay.json.gz",
            objective_keys=("cost",),
        )
        for arm in ("control", "volume-equivalent")
    },
    "published": dict(
        replay=replay_published,
        archive=CAMPAIGN_ARCHIVE,
        specification=DECLARATION,
        endpoint=BOUNDED_BINARY / "endpoint.json",
        observations=ROOT / "data/reference/MDEA/Kuranov_1996_CO2_MDEA_total_pressure.csv",
        restored_row=72,
        reference={
            "kuranov": BOUNDED_BINARY.parent / "kuranov-published-422/kuranov-rows.json",
            "wangler": BOUNDED_BINARY.parent / "kuranov-published-422/wangler-table-10-rows.json",
            "statistics": BOUNDED_BINARY.parent / "kuranov-published-422/statistics.json",
        },
    ),
    "system-pressure-first-weights": dict(
        route=Route,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=ROOT / "analyses/mdea_mea_workflow/results/salt-anchored-435/campaign/selection.json.gz",
        endpoint_keys=("point",),
        reference=ROOT / "analyses/mdea_mea_workflow/results/salt-anchored-435/campaign/data-rows.json.gz",
        reference_keys=(),
        objective=ROOT / "analyses/mdea_mea_workflow/results/salt-anchored-435/campaign/selection.json.gz",
        objective_keys=("cost",),
    ),
    "bicarbonate-0.765": dict(
        route=Route,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=BOUNDED_BINARY / "endpoint.json",
        endpoint_keys=(),
        reference=BOUNDED_BINARY / "data-rows.json",
        reference_keys=(),
        objective=BOUNDED_BINARY / "summary-row.json",
        objective_keys=("data_cost",),
    ),
    "bicarbonate-0.765-unbounded": dict(
        route=Route,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=UNBOUNDED_BINARY / "endpoint.json",
        endpoint_keys=(),
        reference=BOUNDED_BINARY / "data-rows.json",
        reference_keys=(),
        prediction_record=UNBOUNDED_BINARY / "stage-1-fit.json",
        prediction_keys=("predictions",),
        objective=UNBOUNDED_BINARY / "stage-1-fit.json",
        objective_keys=("endpoint_replay_cost",),
    ),
    "bicarbonate-0.1325": dict(
        route=Route,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=ROOT
        / "analyses/mdea_mea_workflow/results/shared-bicarbonate-417/mdea/mdea-low-0.1325000116847309-8b91ef8cebc9f6abd2fa1af7fa05e0939b6b6e1d61c6293c8f84c05da5491c3f/endpoint.json.gz",
        endpoint_keys=(),
        reference=ROOT
        / "analyses/mdea_mea_workflow/results/shared-bicarbonate-417/mdea/mdea-low-0.1325000116847309-8b91ef8cebc9f6abd2fa1af7fa05e0939b6b6e1d61c6293c8f84c05da5491c3f/data-rows.json.gz",
        reference_keys=(),
        objective=ROOT
        / "analyses/mdea_mea_workflow/results/shared-bicarbonate-417/mdea/mdea-low-0.1325000116847309-8b91ef8cebc9f6abd2fa1af7fa05e0939b6b6e1d61c6293c8f84c05da5491c3f/selection.json.gz",
        objective_keys=("cost",),
    ),
    "bicarbonate-1.0": dict(
        route=Route,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=ROOT
        / "analyses/mdea_mea_workflow/results/shared-bicarbonate-417/mdea/mdea-high-1.0-8b91ef8cebc9f6abd2fa1af7fa05e0939b6b6e1d61c6293c8f84c05da5491c3f/endpoint.json.gz",
        endpoint_keys=(),
        reference=ROOT
        / "analyses/mdea_mea_workflow/results/shared-bicarbonate-417/mdea/mdea-high-1.0-8b91ef8cebc9f6abd2fa1af7fa05e0939b6b6e1d61c6293c8f84c05da5491c3f/data-rows.json.gz",
        reference_keys=(),
        objective=ROOT
        / "analyses/mdea_mea_workflow/results/shared-bicarbonate-417/mdea/mdea-high-1.0-8b91ef8cebc9f6abd2fa1af7fa05e0939b6b6e1d61c6293c8f84c05da5491c3f/selection.json.gz",
        objective_keys=("cost",),
    ),
    "system-pressure": dict(
        route=MDEAWeights,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=REPORTED / "MDEA/manifest.json.gz",
        endpoint_keys=("prior_declaration",),
        reference=REPORTED / "MDEA/reference-control.json.gz",
        reference_keys=("tracking",),
    ),
    "reported": dict(
        route=MDEAWeights,
        declaration=DECLARATION,
        retained=REPORTED / "MDEA",
        reference_pressure_pa=P_REF,
        maximum_seconds=10980,
        replay_tolerance=1e-8,
    ),
    "slope-bound": dict(
        route=MDEAWeights,
        declaration=DECLARATION,
        retained=REPORTED / "MDEA_slope_bound",
        reference_pressure_pa=P_REF,
        bound_rule="k_bound",
    ),
}

REPORTED_SET = "reported"
