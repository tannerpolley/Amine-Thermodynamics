"""Fixed-reference DEA reported declarations."""

import copy
import csv
import math

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
from MEA.common.retained_results import read

from .fit import save
from .model import CAMPAIGN_ARCHIVE, ELECTROSTATICS, P_REF, REPORTED, ROOT, Route
from .wheel import verify

DEA = ROOT / "analyses/dea_transfer"
DECLARATION = DEA / "inputs/part-ii-346/f2-carbamate-413-route.json"
SHARED_FIT = DEA / "results/refit-413"
FROZEN_BINARY_FIT = DEA / "results/reactive-refit-425/run"
DIETHANOLAMINE, WATER = "diethanolamine", "water"
PRESSURE = {"Lawson", "SeoHong", "Lal"}
PRESSURE_LOG_SCALE = 0.09
LAL_MOLARITY_MOL_M3 = 2000
LAL_FEED_TOLERANCE = 1e-12


def write_salt_anchored_summary():
    wheel = verify()
    stage = ROOT / "analyses/amines/results/dea/system-pressure-salt-anchored/replay"
    campaign = ROOT / "analyses/round_7/results/F"
    endpoint = read(stage / "endpoint.json.gz")
    if endpoint["wheel"] != wheel:
        raise ValueError("DEA salt-anchored replay uses another wheel")
    properties = endpoint["replay"]["properties"]["rows"]
    seohong = [row for row in properties if row["group"] == "SeoHong" and row["status"] == "Available"]
    horstmann = [row for row in properties if row["group"] == "Horstmann" and row["observed"] < 0]
    expanded = read(campaign / "incumbent-expanded.json.gz")["rows"]
    methane = read(campaign / "methane.json.gz")["rows"]
    save(stage / "summary.json", dict(
        wheel=wheel,
        expanded_objective=math.fsum(row["cost"] for row in expanded),
        expanded_groups={group: sum(row["group"] == group for row in expanded)
                         for group in sorted({row["group"] for row in expanded})},
        seohong_aard_percent=100 * math.fsum(abs(row["value"] / row["observed"] - 1)
                                          for row in seohong) / len(seohong),
        horstmann_positive=sum(row["value"] > 0 for row in horstmann if row["status"] == "Available"),
        horstmann_negative_observations=len(horstmann),
        methane_maximum_shift_pa=max(value for row in methane for value in row.get("pCO2_change_Pa", [])),
    ))


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
    with declaration["heat_capacity"].open(newline="") as stream:
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


(CATION_REPLAY,) = ELECTROSTATICS.glob("*/*/diethanolamine")
FIT_SETS = {
    **{
        f"born-{arm}": dict(
            route=Route,
            declaration=DECLARATION,
            reference_pressure_pa=None,
            archive=CAMPAIGN_ARCHIVE,
            endpoint=SHARED_FIT / "selection.json",
            endpoint_keys=("chosen", "parameters"),
            born_diameter=("protonated-diethanolamine", CATION_REPLAY / arm / "replay.json.gz"),
            reference=CATION_REPLAY / arm / "data-rows.json.gz",
            reference_keys=(),
            objective=CATION_REPLAY / arm / "replay.json.gz",
            objective_keys=("cost",),
        )
        for arm in ("control", "volume-equivalent")
    },
    "water-binary": dict(
        replay=replay_water_binary,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=DEA / "inputs/dea-A.json",
        reference=DEA / "results/binary.json",
        mea_endpoint=ROOT
        / "analyses/mea_parameter_bundle/results/stable-refit-255/evidence/candidate-parameters.json",
        heat_capacity=ROOT / "data/reference/DEA/Maham1997_Table1_DEA_cp.csv",
    ),
    **{
        f"mea-fitted-shared-{index}": dict(
            route=Route,
            declaration=DECLARATION,
            reference_pressure_pa=None,
            archive=CAMPAIGN_ARCHIVE,
            endpoint=SHARED_FIT / "selection.json",
            endpoint_keys=("candidates", index, "parameters"),
            reference=SHARED_FIT / "paper-data.csv",
            reference_keys=(),
            **(
                dict(
                    prediction_record=SHARED_FIT / "selection.json",
                    prediction_keys=("candidates", index, "optimizer_report", "predictions"),
                )
                if index != 0 else {}
            ),
            objective=SHARED_FIT / "selection.json",
            objective_keys=("candidates", index, "cost"),
        )
        for index in (0, 1)
    },
    "mea-fitted-shared": dict(
        route=Route,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=FROZEN_BINARY_FIT / "selection.json",
        endpoint_keys=("chosen", "parameters"),
        reference=FROZEN_BINARY_FIT / "data-rows.json",
        reference_keys=(),
        objective=FROZEN_BINARY_FIT / "selection.json",
        objective_keys=("chosen", "cost"),
    ),
    "system-pressure-salt-anchored": dict(
        route=Route,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=ROOT
        / "analyses/dea_transfer/results/salt-anchored-435/campaign/selection.json.gz",
        endpoint_keys=("chosen", "parameters"),
        reference=ROOT
        / "analyses/dea_transfer/results/salt-anchored-435/campaign/data-rows.json.gz",
        reference_keys=(),
        objective=ROOT
        / "analyses/dea_transfer/results/salt-anchored-435/campaign/selection.json.gz",
        objective_keys=("chosen", "cost"),
    ),
    "system-pressure": dict(
        route=ExpandedDEA,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=REPORTED / "DEA/manifest.json.gz",
        endpoint_keys=("prior_declaration",),
        reference=ROOT / "analyses/round_7/results/F/assessment.json.gz",
        reference_keys=("expanded_design",),
        objective=REPORTED / "DEA/reference-control.json.gz",
        objective_keys=("tracking", "cost"),
    ),
    "reported": dict(
        route=ExpandedDEA,
        declaration=DECLARATION,
        retained=REPORTED / "DEA",
        reference_pressure_pa=P_REF,
        maximum_seconds=1620,
        replay_tolerance=1e-8,
    ),
}
