"""#170: heat/density/Cp comparisons using existing #160 declarations."""

import csv
import json
import math
import os
import sys
from pathlib import Path

os.environ["FINAL_HEAT_160"] = "1"
sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[3] / "src")]
import d1_density_cp_160 as d
import heat_160 as h


def summarize_fits():
    choices = {p: d.select(p) for p in [f"F{i}" for i in range(1, 7)]}
    assert all(r["starts_agree"] for r in choices.values()), choices
    choices["F1"]["parameters"] = str(d.BUNDLE / "results/heat-160/A-parameters.json")
    choices["F1"]["rerun_fit"] = choices["F1"]["fit"]
    choices["F1"]["fit"] = str(d.BUNDLE / "results/heat-160/A-native-fit.json")
    d.s.write_json(d.OUT / "fit-summary.json", list(choices.values()))
    uncertainty = {
        p: d.load(h.OUT / "A-summary.json")["conditional_uncertainty"]
        if p == "F1"
        else d.load(r["fit"])["conditional_uncertainty"]
        for p, r in choices.items()
    }
    d.s.write_json(d.OUT / "conditional-uncertainty.json", uncertainty)
    se = []
    corr = []
    rows = []
    old = d.ORIGINAL / "D1-evidence"
    for label in ("no heat", "with heat"):
        for p in choices:
            if label == "no heat":
                choice = next(r for r in d.load(old / "fit-summary.json") if r["problem"] == p)
                raw = d.load(old / f"{p}-{choice['start']}/native-fit.json")
            else:
                raw = d.load(choices[p]["fit"])
            row = dict(problem=p, objective=label, targets=len(raw["targets"]), cost=raw["final_cost"])
            for group, mask in [
                ("pressure", [i for i, t in enumerate(raw["targets"]) if t.endswith("-pco2")]),
                (
                    "species",
                    [
                        i
                        for i, t in enumerate(raw["targets"])
                        if not t.endswith("-pco2") and not t.startswith("vinjarapu")
                    ],
                ),
                ("Bottinger", [i for i, t in enumerate(raw["targets"]) if t.startswith("Bottinger")]),
                ("Matin", [i for i, t in enumerate(raw["targets"]) if t.startswith("Matin")]),
                ("heat", [i for i, t in enumerate(raw["targets"]) if t.startswith("vinjarapu")]),
            ]:
                row[group + "_n"] = len(mask)
                row[group + "_cost"] = math.fsum(0.5 * raw["weighted_residuals"][i] ** 2 for i in mask)
                row[group + "_AARD_percent"] = (
                    100 * math.fsum(abs(raw["predictions"][i] / raw["observed"][i] - 1) for i in mask) / len(mask)
                    if mask
                    else None
                )
            assert abs(row["pressure_cost"] + row["species_cost"] + row["heat_cost"] - row["cost"]) < 1e-8
            row.update(dict(zip(d.IDS, raw["physical"], strict=True)))
            row["active_bounds"] = (
                ";".join(raw["active_bounds"])
                if raw["active_bounds"] and isinstance(raw["active_bounds"][0], str)
                else ";".join(d.IDS[i] for i in raw["active_bounds"])
            )
            rows.append(row)
    for p, value in uncertainty.items():
        for coordinate, error in value["conditional_standard_error"].items():
            se.append(dict(problem=p, coordinate=coordinate, conditional_standard_error=error))
        for i, c1 in enumerate(value["free_coordinates"]):
            for j, c2 in enumerate(value["free_coordinates"]):
                corr.append(
                    dict(
                        problem=p,
                        coordinate1=c1,
                        coordinate2=c2,
                        conditional_correlation=value["conditional_correlation"][i][j],
                    )
                )
    d.table(d.OUT / "fit-comparison.csv", rows)
    d.table(d.OUT / "conditional-standard-errors.csv", se)
    d.table(d.OUT / "conditional-correlations.csv", corr)
    inputs = d.load(d.BUNDLE / "results/heat-160/inputs.json")
    inputs["files"] = {p: d.s.sha256(d.ROOT / p) for p in inputs["files"]}
    inputs.update(
        execution_base="a190141a072a4c7bafba9afb1246e4fbdb0ee6a2",
        issue="https://github.com/tannerpolley/Amine-Thermodynamics/issues/170",
        owner_rule="All six original #160 problems and starts, plus the same eight Vinjarapu heats; F1 start A reproduces reviewed heat-160",
    )
    d.s.write_json(d.OUT / "inputs.json", inputs)
    print("FIT SUMMARY", [(r["problem"], r["cost_A"], r["cost_B"]) for r in choices.values()])


def main():
    choices = {r["problem"]: r for r in d.load(d.OUT / "fit-summary.json")}
    current = d.s.parameter_mapping(d.BUNDLE / "results/selected-current-best-parameters.json")
    original = d.s.parameter_mapping(d.ORIGINAL / "D1-evidence/F1-double-prime-candidate-parameters.json")
    assert current["empirical_density_correction"] == original["empirical_density_correction"]
    c = current["empirical_density_correction"]["c_cm3_mol"]
    sources = [
        r
        for r in csv.DictReader(
            (d.ROOT / "data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv").open()
        )
        if r["property"] == "density" and r["co2_loading_mol_per_mol_mea"]
    ]
    values = [d.density_job(current, r) for r in sources]
    d.s.write_json(d.OUT / "density-states.json", values)
    d.table(d.OUT / "corrected-densities.csv", d.corrected(values, c))
    cp = [
        dict(record=label, **d.m.cp_check(mapping, T, a, observed))
        for label, mapping in [("heat F1", current), ("no-heat F1", original)]
        for T, a, observed in d.m.HILLIARD
    ]
    d.table(d.OUT / "heat-capacity-comparison.csv", cp)
    rows = []
    for label, mapping in [("heat F1", current), ("no-heat F1", original)]:
        params = h.epcsaft.Parameters.from_mapping(mapping)
        for source, sources in [("Vinjarapu2024", h.VINJARAPU), ("Arcis2011", h.ARCIS)]:
            predictions = h.predict(mapping, h.heat_items(mapping, params, sources))
            for r, y in zip(sources, predictions, strict=True):
                rows.append(
                    dict(
                        record=label,
                        source=source,
                        record_id=r["record_id"],
                        temperature_K=r["temperature_K"],
                        pressure_Pa=r["system_pressure_Pa"],
                        loading=r["alpha_final"],
                        observed_J_mol=r["observed_addition_enthalpy_J_per_mol_CO2"],
                        predicted_J_mol=y,
                        scale_J_mol=r["uH_J_per_mol_CO2"],
                        residual_J_mol=y - r["observed_addition_enthalpy_J_per_mol_CO2"],
                        role="fitted" if source == "Vinjarapu2024" and label == "heat F1" else "predicted",
                        parameter_sha256=d.s.sha256(
                            d.BUNDLE / "results/selected-current-best-parameters.json"
                            if label == "heat F1"
                            else d.ORIGINAL / "D1-evidence/F1-double-prime-candidate-parameters.json"
                        ),
                    )
                )
    d.table(d.OUT / "figure-data/heat.csv", rows)
    heatstats = []
    for label in ["heat F1", "no-heat F1"]:
        for source, pressure in [
            ("Vinjarapu2024", None),
            ("Arcis2011", None),
            ("Arcis2011", 510000),
            ("Arcis2011", 1030000),
        ]:
            part = [
                r
                for r in rows
                if r["record"] == label and r["source"] == source and (pressure is None or r["pressure_Pa"] == pressure)
            ]
            heatstats.append(
                dict(
                    record=label,
                    source=source,
                    pressure_Pa=pressure,
                    n=len(part),
                    RMSE_kJ_mol=math.sqrt(math.fsum(r["residual_J_mol"] ** 2 for r in part) / len(part)) / 1000,
                    bias_kJ_mol=math.fsum(r["residual_J_mol"] for r in part) / len(part) / 1000,
                    minimum_predicted_kJ_mol=min(r["predicted_J_mol"] for r in part) / 1000,
                    maximum_predicted_kJ_mol=max(r["predicted_J_mol"] for r in part) / 1000,
                    heat_cost=math.fsum(0.5 * (r["residual_J_mol"] / r["scale_J_mol"]) ** 2 for r in part),
                )
            )
    d.table(d.OUT / "heat-comparison.csv", heatstats)
    new = list(csv.DictReader((d.OUT / "evaluation/targets.csv").open()))
    old = [dict(r, problem="F1") for r in new if r["problem"] == "F1-no-heat"]
    comparisons = []
    for kind, label in [("packet", "Hilliard/Jou packet pressures"), ("canonical", "canonical pressures")]:
        for T in [40, 60, 80, 100, 120, None]:
            part = {
                name: [
                    r
                    for r in data
                    if r["problem"] == "F1"
                    and r["kind"] == kind
                    and r["quantity"] == "pressure"
                    and (
                        T is None
                        or min([40, 60, 80, 100, 120], key=lambda t: abs(float(r["temperature_K"]) - 273.15 - t)) == T
                    )
                ]
                for name, data in [("no heat", old), ("with heat", new)]
            }
            assert {(r["identity"], r["target"]) for r in part["no heat"]} == {
                (r["identity"], r["target"]) for r in part["with heat"]
            }
            if not part["no heat"]:
                continue
            comparisons.append(
                dict(
                    cohort=label,
                    nominal_temperature_C=T,
                    n=len(part["no heat"]),
                    **{
                        name.replace(" ", "_") + "_AARD_percent": 100
                        * math.fsum(abs(float(r["predicted"]) / float(r["observed"]) - 1) for r in values)
                        / len(values)
                        for name, values in part.items()
                    },
                )
            )
    d.table(d.OUT / "high-temperature-comparison.csv", comparisons)
    # Preserve model-generation tables for the current notebook; no added fitting.
    for filename, mask in [
        ("pressure-figure-data.csv", lambda r: r["kind"] == "packet" and r["quantity"] == "pressure"),
        ("species-figure-data.csv", lambda r: r["kind"] == "packet" and r["quantity"] == "species"),
        ("pool-figure-data.csv", lambda r: r["kind"] == "packet" and r["problem"] in ("F1", "F2", "F4", "F5")),
    ]:
        d.table(d.OUT / filename, [r for r in new if mask(r)])
    d.decomposition(choices)
    figures = d.OUT / "figure-data"
    d.s.write_json(
        figures / "input-hashes.json", {str(p.relative_to(d.OUT)): d.s.sha256(p) for p in figures.glob("*.csv")}
    )
    print("POST EVIDENCE", len(values), "density states", len(rows), "heat values", flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["summarize"]:
        summarize_fits()
    else:
        main()
