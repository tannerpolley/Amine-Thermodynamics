"""Water–anion laws fitted to Hamer–Wu and Peiper–Pitzer osmotic coefficients."""

import copy
import csv
import os

from .model import ROOT, parameter_mapping
from .wheel import verify
from .records import RESULTS, read
from MEA.solvent_specification import jsonable
import epcsaft
from epcsaft import regression as reg

BUNDLE = ROOT / "analyses/mea_parameter_bundle"
INPUTS = BUNDLE / "results/carbonate-ions-282/inputs"
W, NA, CL = "water", "sodium-cation", "chloride-anion"
HCO3, CO3, OH, MEAH = (
    "bicarbonate-anion",
    "carbonate-anion",
    "hydroxide-anion",
    "protonated-monoethanolamine",
)
P_SALT = 1e5  # Pa; the issue's 0.1 MPa liquid
T_SALT = 298.15  # K, reference temperature of the salt laws
T_RECORD = 313.15  # K, the record's pair-law reference temperature
NA_SLOPE = -0.007981  # 1/K, Held 2014 Table 2 note a, held
HELD = dict(source_id="held-2014", locator="Held 2014 Table 2 (strategy 2), Table 3")
# Held 2014 Table 2, strategy 2: sigma / angstrom, u/k / K; charge; molar mass / kg mol-1
IONS = {NA: (2.8232, 230.0, +1, 0.02298977), CL: (2.7560, 170.0, -1, 0.035453)}
SALT_PAIRS = {
    (NA, CL): 0.317,
    (NA, HCO3): -0.514,
    (NA, CO3): -1.0,
    (NA, OH): 0.649,
    (CL, W): -0.25,
}  # Held 2014 Table 3
LAWS = {
    NA: "pair/sodium-cation/water/k_ij",
    HCO3: "pair/bicarbonate-anion/water/k_ij",
    CO3: "pair/carbonate-anion/water/k_ij",
}
HELD_A0 = {
    NA: 2.37999 + NA_SLOPE * T_SALT,
    HCO3: 0.0,
    CO3: -0.25,
}  # starts: Held's values at 298.15 K
BOUNDS = {0: (-1.0, 1.0), 1: (-0.02, 0.02)}  # a0, a1 / K-1 (design choices)
SCALES = {0: 0.01, 1: 1e-4}

FIT_SETS = {
    "sodium-salts": dict(
        declaration=BUNDLE / "results/selected-current-best-parameters.json",
        retained=RESULTS / "salt/sodium-salts/fit",
        stages=(
            ("1a-sodium", "NaCl", ((NA, 0),)),
            ("1b-bicarbonate", "NaHCO3", ((HCO3, 0), (HCO3, 1))),
            ("1c-carbonate", "Na2CO3", ((CO3, 0), (CO3, 1))),
        ),
    ),
}


def law_node(identity, a0, a1, t_ref, provenance):
    """A pair k_ij as k(T) = a0 + a1 (T - t_ref) (Engine polynomial-plus-reciprocal-temperature form, no 1/T term)."""

    def term(p, v, u):
        return dict(
            power=p,
            coefficient=dict(identity=f"{identity}/a{p}", value=dict(magnitude=v, unit=u)),
        )

    return dict(
        family="k_ij",
        identity=identity,
        provenance=provenance,
        temperature_law=dict(
            form="polynomial-plus-reciprocal-temperature",
            reference_temperature=dict(magnitude=t_ref, unit="kelvin"),
            terms=[term(0, a0, "dimensionless"), term(1, a1, "1 / kelvin")],
        ),
    )


def set_pair(mapping, a, b, node):
    x, y = sorted((a, b))
    pair = next(
        (p for p in mapping["pairs"] if {p["component_id_a"], p["component_id_b"]} == {x, y}),
        None,
    )
    if pair is None:
        pair = dict(component_id_a=x, component_id_b=y, coefficients=[])
        mapping["pairs"].append(pair)
    pair["coefficients"] = [c for c in pair["coefficients"] if not c["identity"].startswith(f"pair/{x}/{y}/k_ij")] + [
        node
    ]


def k_node(mapping, identity, value, provenance):
    template = copy.deepcopy(
        next(c for p in mapping["pairs"] for c in p["coefficients"] if c["family"] == "k_ij" and "value" in c)
    )
    template.update(identity=identity, value=dict(magnitude=value, unit="dimensionless"))
    template["provenance"] = {**template["provenance"], **provenance}
    return template


def law_value(law, T):
    return law["a0"] + law["a1"] * (T - law["t_ref"])


def salt_document(laws, base, *, reactive=False):
    """The selected record reduced to water, Na+, Cl-, HCO3-, CO3^2- and OH-; Na+/Cl- in the record's ion conventions.

    ``laws``: {ion: (a0, a1)} about 298.15 K for the three water-ion laws."""
    mapping = parameter_mapping(base)
    template = next(c for c in mapping["components"] if c["component_id"] == HCO3)
    for ion, (sigma, u, z, molar_mass) in IONS.items():
        c = copy.deepcopy(template)
        c.update(component_id=ion, name=ion, aliases=[ion])
        c["fixed"]["charge_number"]["value"]["magnitude"] = z
        c["fixed"]["molar_mass"]["value"]["magnitude"] = molar_mass
        for field in c["fixed"].values():
            field["provenance"] = {**field["provenance"], **HELD}
        values = dict(
            segment_count=1.0,
            segment_diameter=sigma,
            dispersion_energy_over_k=u,
            packing_diameter=0.88 * sigma,
            debye_huckel_diameter=sigma,
            born_diameter=sigma,
            solvation_factor=1.0,
        )  # Born diameter sigma: design choice
        for node in c["coefficients"]:
            node["identity"] = f"component/{ion}/{node['family']}"
            node["value"] = {**node["value"], "magnitude": values[node["family"]]}
            node["provenance"] = {**node["provenance"], **HELD}
        mapping["components"].append(c)
    keep = {W, NA, HCO3, CO3, OH} | ({"carbon-dioxide", "hydronium-cation"} if reactive else {CL})
    mapping["components"] = [c for c in mapping["components"] if c["component_id"] in keep]
    mapping["pairs"] = [p for p in mapping["pairs"] if {p["component_id_a"], p["component_id_b"]} <= keep]
    mapping["correlations"] = [c for c in mapping["correlations"] if c["component_id"] in keep]
    mapping["reaction_correlations"] = [
        c for c in mapping["reaction_correlations"] if reactive and c["reaction_id"] in ("R1", "R2", "R3")
    ]
    topology = mapping["topology"]
    topology["sites"] = [x for x in topology["sites"] if x["component_id"] in keep]
    topology["edges"] = [
        e for e in topology["edges"] if {e["endpoint_a"]["component_id"], e["endpoint_b"]["component_id"]} <= keep
    ]
    for key in ("no_cross_association",):
        for owner in (mapping, topology):
            if key in owner:
                owner[key] = [
                    x for x in owner[key] if {v for k, v in x.items() if k.startswith("component_id")} <= keep
                ]
    for (a, b), k in SALT_PAIRS.items():
        if {a, b} <= keep:
            set_pair(
                mapping,
                a,
                b,
                k_node(mapping, f"pair/{min(a, b)}/{max(a, b)}/k_ij", k, HELD),
            )
    own = dict(
        source_id="carbonate-ions-282",
        locator="analyses/mea_parameter_bundle/scripts/carbonate_ions_282.py",
    )
    for ion, (a0, a1) in laws.items():
        set_pair(mapping, ion, W, law_node(LAWS[ion], a0, a1, T_SALT, own))
    return mapping


def water_molar_mass(base):
    return next(c for c in parameter_mapping(base)["components"] if c["component_id"] == W)["fixed"]["molar_mass"][
        "value"
    ]["magnitude"]


def nacl_rows(parameters):
    out = []
    for row in csv.DictReader((INPUTS / "hamer-wu-1972-nacl.csv").open()):
        m, phi = float(row["molality"]), float(row["phi"])
        item = reg.electrolyte(
            parameters,
            "osmotic_coefficient",
            float(row["temperature_K"]),
            P_SALT,
            {W: 1.0},
            ions=(NA, CL),
            stoichiometry=(1, 1),
            molality=m,
            observed=phi,
            form="difference",
            scale=0.003,
        )
        out.append(dict(salt="NaCl", T=float(row["temperature_K"]), m=m, observed=phi, item=item))
    return out


def carbonate_rows(parameters, salts, *, base):
    """Peiper & Pitzer Table 6 rows at the printed equilibrium ionic composition (charge-closed), observed on the ionic basis."""
    mw, out = water_molar_mass(base), []
    for row in csv.DictReader((INPUTS / "peiper-pitzer-1982-table6.csv").open()):
        if row["salt"] not in salts:
            continue
        m = float(row["nominal_molality"])
        printed = {k: float(row[k]) for k in ("X2", "Y", "H2X", "Z")}
        na = {"NaHCO3": m, "Na2CO3": 2 * m, "mixed": 3 * m}[row["salt"]]
        ions = {NA: na, CO3: printed["X2"], HCO3: printed["Y"], OH: printed["Z"]}
        minor = CO3 if row["salt"] == "NaHCO3" else OH  # charge closure (issue: Na+ nominal, minor anion by balance)
        ions[minor] = (na - ions[HCO3] - (2 * ions[CO3] if minor == OH else ions[OH])) / (2 if minor == CO3 else 1)
        adjustment = ions[minor] - (printed["X2"] if minor == CO3 else printed["Z"])
        if ions[minor] < 0:
            out.append(
                dict(
                    salt=row["salt"],
                    T=float(row["temperature_K"]),
                    m=m,
                    unavailable="charge closure gives a negative minor anion",
                )
            )
            continue
        total_printed = na + sum(printed.values())
        ionic = sum(ions.values())
        phi_ion = (float(row["phi"]) * total_printed - printed["H2X"]) / ionic  # dissolved CO2 ideal
        n_water = 1 / mw
        x = {
            W: n_water / (n_water + ionic),
            **{k: v / (n_water + ionic) for k, v in ions.items()},
        }
        item = reg.mixture_osmotic_coefficient(
            parameters,
            float(row["temperature_K"]),
            P_SALT,
            x,
            observed=phi_ion,
            scale=0.01,
        )
        out.append(
            dict(
                salt=row["salt"],
                T=float(row["temperature_K"]),
                m=m,
                observed=phi_ion,
                phi_printed=float(row["phi"]),
                water_activity=float(row["water_activity"]),
                charge_adjustment=adjustment,
                h2x_share=printed["H2X"] / total_printed,
                composition_mol_per_kg=ions,
                item=item,
            )
        )
    return out


def predict(mapping, rows):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
    out = []
    for x in rows:
        if "item" not in x:
            out.append({k: v for k, v in x.items() if k != "item"})
            continue
        p = reg.predict(model, x["item"])
        out.append(
            dict(
                {k: v for k, v in x.items() if k != "item"},
                status=p.status.name,
                value=p.value,
                relative_error=p.value / x["observed"] - 1 if p.status.name == "Available" else None,
            )
        )
    return out


def aard(rows):
    e = [abs(x["relative_error"]) for x in rows if x.get("relative_error") is not None]
    return dict(n=len(e), aard_percent=100 * sum(e) / len(e), max_percent=100 * max(e))


def salt_fit(name, laws, active, rows_of, *, base):
    """One cascade fit: ``active`` = [(ion, power), ...] law coefficients; other laws held at ``laws``."""
    mapping = salt_document(laws, base)
    parameters = epcsaft.Parameters.from_mapping(mapping)
    rows = rows_of(parameters)
    coordinates = [
        reg.coordinate(
            parameters,
            [("temperature_law_coefficient", f"{LAWS[ion]}/a{p}", 1.0)],
            origin=laws[ion][p],
            scale=SCALES[p],
            bounds=BOUNDS[p],
        )
        for ion, p in active
    ]
    controls = reg.FitControls(
        maximum_iterations=200,
        maximum_elapsed_time_seconds=3600.0,
        function_tolerance=1e-12,
        parameter_tolerance=1e-12,
        gradient_tolerance=1e-10,
        workers=int(os.environ["AGENT_HEAVY_CORES"]),
    )
    fit = reg.fit(parameters, coordinates, [x["item"] for x in rows], controls=controls)
    fitted = copy.deepcopy(laws)
    for (ion, p), value in zip(active, fit.physical, strict=True):
        fitted[ion] = tuple(value if i == p else fitted[ion][i] for i in (0, 1))
    on_bound = [
        dict(coefficient=f"{LAWS[ion]}/a{p}", value=v, bounds=BOUNDS[p])
        for (ion, p), v in zip(active, fit.physical, strict=True)
        if min(abs(v - BOUNDS[p][0]), abs(v - BOUNDS[p][1])) <= 1e-8 * max(1.0, abs(v))
    ]
    replay = predict(salt_document(fitted, base), rows)
    difference = max(abs(x["value"] - pv) for x, pv in zip(replay, fit.predictions, strict=True))
    report = dict(
        name=name,
        status=fit.status,
        message=fit.message,
        usable=fit.usable,
        iterations=len(fit.iteration_costs or []),
        initial_cost=fit.initial_cost,
        final_cost=fit.final_cost,
        active=[f"{LAWS[i]}/a{p}" for i, p in active],
        start={f"{LAWS[i]}/a{p}": laws[i][p] for i, p in active},
        endpoint={f"{LAWS[i]}/a{p}": v for (i, p), v in zip(active, fit.physical, strict=True)},
        on_bound=on_bound,
        covariance_active_bounds=jsonable(fit.covariance.active_bounds),
        replay_maximum_difference=difference,
        laws={ion: dict(a0=v[0], a1=v[1], t_ref=T_SALT) for ion, v in fitted.items()},
        rows=replay,
    )
    return fitted, report


def salt_rows(document, base):
    parameters = epcsaft.Parameters.from_mapping(document)
    return {
        "NaCl": predict(document, nacl_rows(parameters)),
        **{
            name: predict(document, carbonate_rows(parameters, {name}, base=base))
            for name in ("NaHCO3", "Na2CO3", "mixed")
        },
    }


def replay(fit_set):
    wheel = verify()
    record = read(fit_set["retained"] / "summary.json")
    if record["wheel_sha256"] != wheel:
        raise ValueError("The retained salt cascade belongs to a different wheel")
    return dict(
        wheel=wheel,
        rows=salt_rows(record["result"]["document"], fit_set["declaration"]),
    )


def rows(fit_set):
    base = fit_set["declaration"]
    laws = {ion: (a0, NA_SLOPE if ion == NA else 0.0) for ion, a0 in HELD_A0.items()}
    parameters = epcsaft.Parameters.from_mapping(salt_document(laws, base))
    groups = {"NaCl": nacl_rows(parameters)}
    groups.update((name, carbonate_rows(parameters, {name}, base=base))
                  for name in ("NaHCO3", "Na2CO3", "mixed"))
    return dict(wheel=verify(), rows={name: [{k: v for k, v in row.items() if k != "item"}
                                           for row in data] for name, data in groups.items()})


def fit(fit_set):
    wheel = verify()
    base = fit_set["declaration"]
    laws = {ion: (a0, NA_SLOPE if ion == NA else 0.0) for ion, a0 in HELD_A0.items()}
    stages = {}
    for name, group, active in fit_set["stages"]:
        rows_of = nacl_rows if group == "NaCl" else lambda p: carbonate_rows(p, {group}, base=base)
        laws, stages[name] = salt_fit(name, laws, active, rows_of, base=base)
    document = salt_document(laws, base)
    rows = salt_rows(document, base)
    return dict(
        wheel=wheel,
        stages=stages,
        document=document,
        rows=rows,
        scores={group: aard(values) for group, values in rows.items()},
        laws_at_record_reference={
            ion: dict(a0=a0 + a1 * (T_RECORD - T_SALT), a1=a1, t_ref=T_RECORD) for ion, (a0, a1) in laws.items()
        },
    )
