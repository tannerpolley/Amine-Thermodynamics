"""AMP fit declarations and retained pure and binary replays."""

import csv
import math

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
from .records import RESULTS, input_path, read

from .model import CAMPAIGN_ARCHIVE, P_REF, ROOT, Route

AMP, WATER = "aminomethylpropanol", "water"
AMP_TRANSFER = ROOT / "analyses/amp_transfer"


def pure_observation(parameters, row):
    T, value = float(row["T_K"]), float(row["value"])
    if row["kind"] == "density":
        return reg.density(
            parameters,
            T,
            1e5,
            {AMP: 1.0},
            phase="liquid",
            observed=value,
            form="difference",
            mass_basis=True,
            scale=float(row["scale"]),
        )
    return reg.observation(
        parameters,
        "pressure",
        epcsaft.Pure(parameters).saturation(T),
        observed=value,
        form="log_ratio",
    )


def assess_pure(document, rows):
    parameters = epcsaft.Parameters.from_mapping(document)
    model = epcsaft.Pure(parameters)
    values, unavailable = [], []
    for source in rows:
        prediction = reg.predict(model, pure_observation(parameters, source))
        pressure = source["kind"] == "pressure"
        available = (
            prediction.status.name == "Available"
            and prediction.requested_tolerance_met is not False
            and math.isfinite(prediction.value)
            and prediction.value > 0
            and (pressure or prediction.branch.name == "Liquid")
        )
        row = dict(
            campaign=source["campaign"],
            role=source["role"],
            kind=source["kind"],
            T_K=float(source["T_K"]),
            observed=float(source["value"]),
            predicted=prediction.value if available else None,
            status=prediction.status.name,
        )
        if available and pressure:
            roots = [
                model.state(row["T_K"], P=prediction.value, phase=phase)
                for phase in ("liquid", "vapor")
            ]
            row.update(
                relative_error_percent=100 * (prediction.value / row["observed"] - 1),
                liquid_vapor_density_mol_m3=[state.molar_density for state in roots],
                dP_drho=[state.pressure_density_derivative for state in roots],
            )
            available = (
                all(d > 0 for d in row["dP_drho"])
                and roots[0].molar_density > 10 * roots[1].molar_density
            )
        elif available:
            row["error_kg_m3"] = prediction.value - row["observed"]
        values.append(row)
        if not available:
            unavailable.append(row)
    return values, unavailable


def binary_bubble(parameters, row, kind):
    x, y, T = float(row["x_AMP"]), float(row["y_AMP"]), float(row["t_C"]) + 273.15
    pressure_pa = 1000 * float(row["P_kPa"])
    problem = eq.problem_from_mapping(
        dict(
            T=T,
            P=dict(free=True, guess=pressure_pa),
            feed=dict(basis="amounts", values={AMP: x, WATER: 1 - x}),
            phases=[
                dict(
                    name="L",
                    kind="liquid",
                    support=[AMP, WATER],
                    composition_guess={AMP: x, WATER: 1 - x},
                ),
                dict(
                    name="V",
                    kind="vapor",
                    support=[AMP, WATER],
                    amount=dict(status="pinned", value=0.0),
                    composition_guess={AMP: y, WATER: 1 - y},
                ),
            ],
            row_tolerance=1e-10,
        )
    )
    if kind == "pressure":
        return reg.observation(
            parameters, "pressure", problem, observed=pressure_pa, form="log_ratio"
        )
    return reg.observation(
        parameters,
        "mole_fraction",
        problem,
        phase="V",
        species=[AMP],
        observed=y,
        form="difference",
        scale=max(1e-4, 0.05 * y),
    )


def relative_statistics(rows):
    relative = 100 * (
        np.asarray([row["predicted"] for row in rows])
        / [row["observed"] for row in rows]
        - 1
    )
    return dict(
        n=len(rows),
        AARD_percent=float(np.mean(np.abs(relative))),
        signed_relative_bias_percent=float(np.mean(relative)),
    )


def replay_pure_and_binary(declaration):
    reference = read(declaration["reference"])
    with input_path(declaration["pure_rows"]).open(newline="") as stream:
        pure, unavailable = assess_pure(
            read(declaration["pure_endpoint"]), list(csv.DictReader(stream))
        )
    pure_groups = {}
    for group in dict.fromkeys(row["campaign"] for row in pure):
        rows = [
            row for row in pure if row["campaign"] == group and row not in unavailable
        ]
        if not rows:
            continue
        pure_groups[group] = (
            relative_statistics(rows)
            if rows[0]["kind"] == "pressure"
            else dict(n=len(rows), errors_kg_m3=[row["error_kg_m3"] for row in rows])
        )
    with input_path(declaration["binary_rows"]).open(newline="") as stream:
        binary_rows = list(csv.DictReader(stream))
    binary = {}
    for name, (path, keys) in declaration["binary_endpoints"].items():
        document = read(path)
        for key in keys:
            document = document[key]
        parameters = epcsaft.Parameters.from_mapping(document)
        model = epcsaft.Mixture(parameters)
        binary[name] = {}
        for kind in ("pressure", "vapor_composition"):
            rows = []
            for row in binary_rows:
                prediction = reg.predict(model, binary_bubble(parameters, row, kind))
                observed = (
                    1000 * float(row["P_kPa"])
                    if kind == "pressure"
                    else float(row["y_AMP"])
                )
                rows.append(
                    dict(
                        row=row["row"],
                        observed=observed,
                        predicted=prediction.value,
                        status=prediction.status.name,
                        tolerance=prediction.requested_tolerance_met,
                    )
                )
            available = [
                row
                for row in rows
                if row["status"] == "Available" and row["tolerance"] is not False
            ]
            binary[name][kind] = dict(
                rows=rows, **(relative_statistics(available) if available else {})
            )
    return dict(
        pure=dict(rows=pure, groups=pure_groups, unavailable=unavailable),
        binary=binary,
        reference=declaration["reference"].relative_to(ROOT).as_posix(),
        retained_pure_available=len(reference["pure"]["rows"])
        - len(reference["pure"]["unavailable"]),
    )


DECLARATION = (
    ROOT / "analyses/amp_transfer/inputs/retransfer-344/phase-2/AMP-05e94210.json"
)
ADDED = {"tong", "hartono-2021-supplemental"}
LOADED = "loaded-pressure"


class ExpandedPressure(Route):
    def bind(self, point):
        spec = super().bind(point)
        observations = spec.inputs["observations"]
        fitted, outside = (observations[role] for role in ("fitted", "comparisons"))
        added = [r for r in outside if r["group"] in ADDED]
        original = [r for r in fitted if r["group"] == LOADED]
        assert all(r["arguments"]["form"] == "log_ratio" and r["unit"] == "Pa" for r in original + added)
        (coefficient,) = {r["weight"] for r in original}
        for r in original + added:
            r.update(
                weight=coefficient * len(original) / (len(original) + len(added)),
                role="fitted",
            )
        fitted.extend(added)
        observations["comparisons"] = [r for r in outside if r["group"] not in ADDED]
        return spec


FIT_SETS = {
    "pure-and-binary": dict(
        replay=replay_pure_and_binary,
        archive=CAMPAIGN_ARCHIVE,
        reference=AMP_TRANSFER
        / "results/retransfer-344-05e94210/pure-binary-on-05e94210.json",
        pure_endpoint=AMP_TRANSFER / "inputs/amp-pure-endpoint.json",
        pure_rows=AMP_TRANSFER / "inputs/pure-amp.csv",
        binary_rows=AMP_TRANSFER / "inputs/hartono-2013-table-3.csv",
        binary_endpoints={
            "earlier_binary_fit": (AMP_TRANSFER / "inputs/amp-document.json", ()),
            "reported_part_ii_fit_start_0_unpenalized": (
                AMP_TRANSFER
                / "results/retransfer-344-05e94210/campaign/start-0/unpenalized/stage-0/parameters.json",
                ("parameters",),
            ),
        },
    ),
    "first-data": dict(
        route=Route,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=ROOT
        / "analyses/amp_transfer/results/retransfer-412-f2-05e94210/main/parameters.json",
        endpoint_keys=(),
        reference=ROOT / "analyses/round_5/results/A/original-main.json.gz",
        reference_keys=("original", "rows"),
        objective=ROOT / "analyses/round_5/results/A/original-main.json.gz",
        objective_keys=("cost",),
    ),
    "first-data-hot-pressures": dict(
        route=ExpandedPressure,
        declaration=DECLARATION,
        reference_pressure_pa=None,
        retained=RESULTS / "move/amp/first-data-hot-pressures/fit",
        fit_from="first-data",
        maximum_seconds=900,
        replay_tolerance=1e-8,
    ),
    "reported": dict(
        route=ExpandedPressure,
        declaration=DECLARATION,
        retained=RESULTS / "move/amp/reported/fit",
        preserved=RESULTS / "amp/reported/fit",
        reference_pressure_pa=P_REF,
        maximum_seconds=6750,
        replay_tolerance=1e-8,
    ),
}

FIT_SETS["water-anion-control"] = FIT_SETS["reported"] | dict(
    retained=RESULTS / "move/amp/water-anion-control/fit",
    water_anion_intercepts=True,
)

FIT_SETS["without-hot-pressures"] = FIT_SETS["reported"] | dict(
    route=Route,
    retained=RESULTS / "move/amp/without-hot-pressures/fit",
)

FIT_SETS["common-pressure-weight"] = FIT_SETS["reported"] | dict(
    retained=RESULTS / "move/amp/common-pressure-weight/fit",
    pressure_log_scale=0.05,
)

FIT_SETS["fixed-r4"] = FIT_SETS["reported"] | dict(
    retained=RESULTS / "move/amp/fixed-r4/fit",
    fixed_r4=AMP_TRANSFER / "inputs/retransfer-344/phase-2/declarations.toml",
)
