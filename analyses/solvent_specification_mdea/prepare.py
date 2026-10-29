"""Fixed source transformations only; chemistry and observation policy live in TOML."""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / "analyses/mdea_mea_workflow"
OUT = Path(__file__).resolve().parent / "inputs"


sources = {}


def read(path):
    sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text())


loading_path = ROOT / "data/reference/MDEA/Merkley1987_loading_points.csv"
sources[str(loading_path.relative_to(ROOT))] = hashlib.sha256(loading_path.read_bytes()).hexdigest()
loading = {
    (r["temperature_K"], r["MDEA_mass_percent"]): float(r["alpha_LP_mol_CO2_per_mol_MDEA"])
    for r in csv.DictReader(loading_path.open())
}
fitted = read(OLD / "results/stage2-capped/B1/declaration.json")["observations"]
comparisons = read(OLD / "results/stage2-capped/B1/comparisons.json")
groups = {}
for role, records in [("calibration", fitted), ("outside-fit", comparisons)]:
    for i, meta in enumerate(records):
        group, source = meta["group"], meta["row"]
        r = {
            k: float(v)
            for k, v in source.items()
            if isinstance(v, (int, float)) or isinstance(v, str) and v.replace(".", "", 1).replace("-", "", 1).isdigit()
        }
        T = r.get("temperature_K", r.get("temperature_C", 25.0) + 273.15)
        P, water, alpha = 101325.0, 0.0, r.get("loading", 0.0)
        weight = meta.get("weight", 1.0)
        observed, scale = meta["observed"], meta.get("scale", 1.0)
        if group.startswith("Kuranov") or group in ("Ermatchkov", "corrected-Kamps"):
            m = r.get("m_MDEA_mol_per_kg_H2O", r.get("m_MDEA_mol_kg_water"))
            alpha = r.get("m_CO2_mol_per_kg_H2O", r.get("m_CO2_mol_kg_water")) / m
            water = 1 / 0.01801528 / m
            P = (
                r["ten_times_total_pressure_MPa"] * 1e5
                if group.startswith("Kuranov")
                else (max(1e5, r["p_CO2_kPa"] * 1000) if group == "Ermatchkov" else r["total_pressure_MPa"] * 1e6)
            )
        elif group == "Kim":
            P = r["total_pressure_kPa"] * 1000
            x = r["liquid_x_MDEA"]
            water = 1 - x
        else:
            w = r.get(
                "MDEA_mass_fraction",
                r.get(
                    "initial_MDEA_mass_fraction",
                    r.get("unloaded_MDEA_mass_fraction", r.get("MDEA_mass_percent", 23.0) / 100),
                ),
            )
            water = 0.1191622 * (1 - w) / w / 0.01801528
            if group == "Jakobsen":
                alpha = r["loadNMR"]
            if group == "Carson":
                T = 298.15
                alpha = r["x_CO2"] / (1 - r["x_CO2"]) * (1 + water)
            if group.startswith("Merkley"):
                P = r["proposed_pressure_kPa"] * 1000
                alpha = loading[(source["temperature_K"], source["MDEA_mass_percent"])]
                if group == "Merkley-half-loading":
                    alpha /= 2
            if group == "Zheng":
                P, alpha = r["pressure_MPa"] * 1e6, r["alpha_sat_mol_CO2_per_mol_MDEA"]
            if group == "Sedighi":
                P, alpha = r["pressure_kPa"] * 1000, r["alpha_mol_CO2_per_mol_MDEA"]
            if group.startswith("Bottinger"):
                P = r["pressure_Pa"]
            if group == "unloaded-density":
                P = 1e5
        subgroup = source.get("ratio", "") if group == "Jakobsen" else ""
        if group == "Kim":
            subgroup = "binary" if x else "water"
        key = f"{role}-{group}{'-' + subgroup if subgroup else ''}"
        row = dict(
            identity=f"{'fit' if role == 'calibration' else 'comparison'}:{i}",
            source=json.dumps(source, sort_keys=True),
            T=T,
            P=P,
            water=water,
            alpha=alpha,
            amine=x if group == "Kim" else 1.0,
            observed=observed,
            scale=scale,
            weight=weight,
        )
        groups.setdefault(key, []).append(row)
for key, rows in groups.items():
    with (OUT / f"{key}.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
(OUT / "preparation-provenance.json").write_text(
    json.dumps(
        dict(
            sources=sources,
            basis="mol; one analytical MDEA except Kim binary mole-fraction feeds; loading mol CO2/mol MDEA",
            transformations="Pressure Pa; temperature K; Carson loading; Jakobsen ratio and scale from retained declaration; Weiland molar-feed Cp; secant density scales and weights from retained declaration. Source rows preserved verbatim.",
            policy="No chemistry, template, observation constructor, saturation calculation or fit is defined here.",
        ),
        indent=2,
    )
    + "\n"
)
