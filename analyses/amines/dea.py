"""Fixed-reference DEA reported declarations."""

import copy
import csv
import math

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
from .records import RESULTS, input_path, read

from .model import CAMPAIGN_ARCHIVE, P_REF, ROOT, Route, with_parameter_values

DEA = ROOT / "analyses/dea_transfer"
DECLARATION = DEA / "inputs/part-ii-346/f2-carbamate-413-route.json"
FROZEN_BINARY_FIT = DEA / "results/reactive-refit-425/run"
DIETHANOLAMINE, WATER = "diethanolamine", "water"
PRESSURE = {"Lawson", "SeoHong", "Lal"}
PRESSURE_LOG_SCALE = 0.09
LAL_MOLARITY_MOL_M3 = 2000
LAL_FEED_TOLERANCE = 1e-12


class ExpandedDEA(Route):
    def bind(self, point):
        spec = super().bind(point)
        observations = spec.inputs["observations"]
        fitted, comparisons = (observations[k] for k in ("fitted", "comparisons"))
        promoted = [row for row in comparisons if row["group"] in ("SeoHong", "Lal")]
        pressures = [row for row in fitted + promoted if row["group"] in PRESSURE]
        for row in pressures:
            assert row["kind"] == "partial_pressure" and row["arguments"]["form"] == "log_ratio"
            row.update(
                role="fitted",
                weight=1 / (len(pressures) * PRESSURE_LOG_SCALE**2),
            )
            if row["group"] == "Lal":
                p = spec.problems[row["problem"]]
                amounts = p.feed.values
                masses = {
                    c["component_id"]: c["fixed"]["molar_mass"]["value"]["magnitude"]
                    for c in point["parameters"]["components"]
                }
                w = (
                    masses["diethanolamine"]
                    * amounts["diethanolamine"]
                    / (masses["diethanolamine"] * amounts["diethanolamine"] + masses["water"] * amounts["water"])
                )
                rho = 1021 + (w - 0.20) * (1035 - 1021) / 0.10
                assert math.isclose(
                    w * rho,
                    LAL_MOLARITY_MOL_M3 * masses["diethanolamine"],
                    rel_tol=LAL_FEED_TOLERANCE,
                )
                assert row["arguments"]["observed"] == float(row["row"]["p_CO2_kPa"]) * 1000
        observations["fitted"].extend(promoted)
        observations["comparisons"] = [row for row in comparisons if row not in promoted]
        return spec


class RepairedDEA(ExpandedDEA):
    def bind(self, point):
        spec = super().bind(point)
        observations = spec.inputs["observations"]
        rows = sorted(observations["fitted"] + observations["comparisons"], key=lambda r: r["observation_order"])
        fitted, comparisons = [], []
        for row in rows:
            if row["group"] in ("Lawson", "Carson") or (
                row["group"] == "Lal" and row["arguments"]["observed"] >= 50.0
            ):
                row["role"] = "fitted"
                fitted.append(row)
            else:
                if row["role"] == "fitted":
                    row["role"] = "not fitted"
                comparisons.append(row)
        pressures = [row for row in fitted if row["group"] in PRESSURE]
        for row in pressures:
            row["weight"] = 1 / (len(pressures) * PRESSURE_LOG_SCALE**2)
        observations.update(fitted=fitted, comparisons=comparisons)
        return spec


def repaired_point(point):
    binary = read(RESULTS / "dea/binary-temperature-dependent/fit-inputs/inputs.json")["binary"]
    water_pair = "pair/diethanolamine/water/k_ij"
    point["parameters"] = with_parameter_values(point["parameters"], {
        water_pair: binary["a"] + binary["b_K"] * (1 / 313.15 - 1 / binary["reference_K"]),
        water_pair + "/reciprocal_temperature_slope": binary["b_K"],
    })
    cation = "protonated-diethanolamine"
    for identity, family, other, scale, bound in (
        ("k-DEAH-water-slope", "k_ij_reciprocal_temperature_slope", "water", 50.0, 1000.0),
        ("k-DEAH-CO2", "k_ij", "carbon-dioxide", 0.05, 1.0),
    ):
        point["coordinates"].append(dict(identity=identity, targets=[[family, [cation, other], 1.0]],
                                         origin=0.0, scale=scale, bounds=[-bound, bound]))
    return point


def alternate_start(point):
    trial = {"k-DEAH-water": -0.25, "k-DEACOO-water": -0.10, "hydrolysis-a": 6.264,
             "hydrolysis-enthalpy-shift": 5000.0, "k-DEAH-water-slope": -50.0, "k-DEAH-CO2": 0.2}
    return [(trial[q["identity"]] - q["origin"]) / q["scale"] for q in point["coordinates"]]


def bubble(parameters, row):
    x = float(row["x_water"])
    feed = {
        c: amount for c, amount in ((DIETHANOLAMINE, 1 - x), (WATER, x)) if amount > 0
    }
    pressure = 1e3 * float(row["P_kPa"])
    problem = eq.problem_from_mapping(
        dict(
            T=float(row["T_K"]),
            P=dict(free=True, guess=pressure),
            feed=dict(basis="amounts", values=feed),
            phases=[
                dict(name="L", kind="liquid", support=list(feed)),
                dict(
                    name="V",
                    kind="vapor",
                    support=list(feed),
                    amount=dict(status="pinned", value=0.0),
                ),
            ],
            row_tolerance=1e-10,
        )
    )
    return reg.observation(
        parameters, "pressure", problem, observed=pressure, form="log_ratio"
    )


def replay_water_binary(declaration):
    retained = read(declaration["reference"])
    document = read(declaration["endpoint"])
    fitted_parameters = epcsaft.Parameters.from_mapping(document)
    fitted = epcsaft.Mixture(fitted_parameters)
    pre_dielectric = copy.deepcopy(document)
    dea = next(
        c for c in pre_dielectric["components"] if c["component_id"] == DIETHANOLAMINE
    )
    mea = next(
        c
        for c in read(declaration["mea_endpoint"])["components"]
        if c["component_id"] == "monoethanolamine"
    )
    inherited = {row["family"]: row["value"] for row in mea["coefficients"]}
    for coefficient in dea["coefficients"]:
        if coefficient["family"] in ("dielectric_volume", "dielectric_temperature"):
            coefficient["value"] = inherited[coefficient["family"]]
    parameters = epcsaft.Parameters.from_mapping(pre_dielectric)
    model = epcsaft.Mixture(parameters)
    topology = pre_dielectric["topology"]
    pure = dict(
        pre_dielectric,
        components=[dea],
        pairs=[],
        correlations=[],
        reaction_correlations=[],
        topology=dict(
            topology,
            no_cross_association=[],
            sites=[
                site
                for site in topology["sites"]
                if site["component_id"] == DIETHANOLAMINE
            ],
            edges=[
                edge
                for edge in topology["edges"]
                if edge["endpoint_a"]["component_id"]
                == edge["endpoint_b"]["component_id"]
                == DIETHANOLAMINE
            ],
        ),
    )
    pure = epcsaft.Pure(epcsaft.Parameters.from_mapping(pure))
    pure_rows = []
    for row in retained["pure"]["rows"]:
        solution = eq.solve_equilibrium(pure, pure.saturation(row["T_K"]))
        observed = row["P_kPa"]
        value = (
            solution.pressure / 1e3
            if solution.requested_tolerance_met and solution.pressure
            else None
        )
        pure_rows.append(
            dict(
                source=row["source"],
                T_K=row["T_K"],
                P_kPa=observed,
                model_kPa=value,
                relative_percent=100 * (value / observed - 1)
                if value is not None
                else None,
                requested_tolerance_met=solution.requested_tolerance_met,
            )
        )
    binary_rows = []
    residuals = []
    for row in retained["binary"]["rows"]:
        predicted = reg.predict(model, bubble(parameters, row))
        available = (
            predicted.status.name == "Available"
            and predicted.requested_tolerance_met is not False
        )
        binary_rows.append(
            dict(
                row,
                predicted_kPa=predicted.value / 1e3 if available else None,
                status=predicted.status.name,
                requested_tolerance_met=predicted.requested_tolerance_met,
            )
        )
        if available:
            residuals.append(predicted.residual)
    dielectric_rows = []
    for row in retained["hsieh_rows"]:
        x, T, observed = (float(row[name]) for name in ("x_DEA", "T_K", "epsilon"))
        composition = {DIETHANOLAMINE: x, WATER: 1 - x}
        observation = reg.electrolyte(
            fitted_parameters,
            "bulk_relative_permittivity",
            T,
            101325.0,
            composition,
            ions=("hydronium-cation", "hydroxide-anion"),
            stoichiometry=(1, 1),
            molality=0.0,
            observed=observed,
            form="difference",
            scale=0.01 * observed,
        )
        prediction = reg.predict(fitted, observation)
        dielectric_rows.append(
            dict(row, predicted=prediction.value, status=prediction.status.name)
        )
    with input_path(declaration["heat_capacity"]).open(newline="") as stream:
        maham = list(csv.DictReader(stream))
    T = np.array([float(row["T_K"]) for row in maham])
    residual_cp = np.array(
        [
            model.state(
                t, P=1e5, x={DIETHANOLAMINE: 1.0}, phase="liquid"
            ).residual_isobaric_heat_capacity
            for t in T
        ]
    )
    ideal = np.array([float(row["cp_J_per_mol_K"]) for row in maham]) - residual_cp
    slope, intercept = np.polyfit(T - 313.15, ideal, 1)
    dielectric_errors = [
        100 * abs(row["predicted"] / float(row["epsilon"]) - 1)
        for row in dielectric_rows
        if row["status"] == "Available"
    ]
    return dict(
        pure=dict(
            rows=pure_rows,
            model_MARE_percent=float(
                np.mean(
                    [
                        abs(row["relative_percent"])
                        for row in pure_rows
                        if row["relative_percent"] is not None
                    ]
                )
            ),
        ),
        binary=dict(
            rows=binary_rows,
            cost=math.fsum(value**2 for value in residuals) / (2 * len(binary_rows))
            if len(residuals) == len(binary_rows)
            else None,
            MARE_percent=float(
                np.mean(
                    [
                        100 * abs(row["predicted_kPa"] / float(row["P_kPa"]) - 1)
                        for row in binary_rows
                        if row["predicted_kPa"] is not None
                    ]
                )
            ),
        ),
        dielectric=dict(
            rows=dielectric_rows, MARE_percent=float(np.mean(dielectric_errors))
        ),
        caloric=dict(
            T_K=T.tolist(),
            residual_cp=residual_cp.tolist(),
            ideal_cp=ideal.tolist(),
            line=[float(intercept), float(slope)],
            line_residuals=(ideal - (intercept + slope * (T - 313.15))).tolist(),
        ),
    )


FIT_SETS = {
    "water-binary": dict(
        replay=replay_water_binary,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=DEA / "inputs/dea-A.json",
        reference=DEA / "results/binary.json",
        mea_endpoint=ROOT
        / "analyses/mea_parameter_bundle/results/stable-refit-255/evidence/candidate-parameters.json",
        heat_capacity=ROOT / "data/reference/DEA/Maham1997_Table1_DEA_cp.csv",
    ),
    "reported": dict(
        route=RepairedDEA,
        declaration=DECLARATION,
        retained=RESULTS / "dea/reported/fit",
        reference_pressure_pa=P_REF,
        maximum_seconds=1620,
        replay_tolerance=1e-8,
    ),
}
