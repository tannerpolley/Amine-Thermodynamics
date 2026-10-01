"""Issue 140 native low-temperature estimation only; no assessment or selection.

Single-threaded, external timeout 2400: STRUCTURE START
Separate external timeout 1800: rescore STRUCTURE START
No existing fit is resumed or replaced. Both commands reject temperatures >333.15 K.
"""

import copy
import csv
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[1]
sys.path.insert(0, str(BUNDLE / "calibration-misfit"))
import probe  # noqa: E402
import compare  # noqa: E402
import refit  # noqa: E402
from epcsaft import regression  # noqa: E402

s = probe.shared
RAW = BUNDLE / "results/runs/temperature-reanchor-140"
TRAINING = RAW / "training-inputs.json"
SOURCE = HERE / "restored-source-parameters.json"
IDS = [
    "pair/carbamate-anion/water/k_ij",
    "pair/protonated-monoethanolamine/water/k_ij",
    "pair/bicarbonate-anion/water/k_ij",
    "pair/carbamate-anion/protonated-monoethanolamine/k_ij",
]
SLOPE = IDS[1] + "/reciprocal_temperature_slope"
EPSILON = "component/carbon-dioxide/dispersion_energy_over_k"
STRUCTURES = ("constant-fixed", "slope-fixed", "constant-free", "slope-free")


def save(path, value):
    def safe(v):
        v = s._jsonable(v)
        if isinstance(v, dict):
            return {k: safe(x) for k, x in v.items()}
        if isinstance(v, list):
            return [safe(x) for x in v]
        return None if isinstance(v, float) and not math.isfinite(v) else v

    s.write_json(path, safe(value))


def table(path, rows):
    if rows:
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                list(dict.fromkeys(k for r in rows for k in r)),
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)


def design(structure, start):
    assert structure in STRUCTURES and start in ("1", "2")
    ids = (
        IDS
        + ([SLOPE] if structure.startswith("slope") else [])
        + ([EPSILON] if structure.endswith("free") else [])
    )
    bounds = [(-0.5, 0.5)] * 3 + [(-1.0, 1.0)]
    scales = [0.01] * 4
    values = [0.0] * 4 if start == "1" else [0.05, -0.05, 0.05, -0.05]
    if SLOPE in ids:
        bounds.append((-1000.0, 1000.0))
        scales.append(10.0)
        values.append(0.0)
    if EPSILON in ids:
        bounds.append((160.7495, 177.6705))
        scales.append(1.0)
        values.append(169.21 if start == "1" else 172.5942)
    return ids, bounds, scales, values


def verify_inputs():
    hashes = json.loads((HERE / "input-hashes.json").read_text())["hashes"]
    for path in (
        TRAINING,
        SOURCE,
        BUNDLE / "calibration-misfit/refit.py",
        Path(probe.__file__),
        Path(compare.__file__),
        Path(s.__file__),
    ):
        assert s.sha256(path) == hashes[str(path.relative_to(probe.W))], path
    observations = json.loads(TRAINING.read_text())
    assert (
        len(observations) == 84 and sum(len(o["targets"]) for o in observations) == 142
    )
    expected = list(csv.DictReader((HERE / "training-targets.csv").open()))
    assert {(r["identity"], r["target"]) for r in expected} == {
        (o["identity"], t["identity"]) for o in observations for t in o["targets"]
    }
    for o in observations:
        request = o["request"]
        assert request["temperature"]["value"] <= 333.15, o["identity"]
        assert all(compare.in_working_objective(refit._rec(o), t) for t in o["targets"])
        feed = dict(
            zip(
                s.COMPONENT_IDS,
                request["reaction_system"]["feed_amounts_mol"],
                strict=True,
            )
        )
        assert all(math.isfinite(x) and x > 0 for x in feed.values())
        for phase in request["continuation"]["state"]["phases"]:
            support = phase["supported_component_ids"]
            total = math.fsum(feed[i] for i in support)
            assert all(
                abs(x - feed[i] / total) < 1e-15
                for i, x in zip(support, phase["mole_fractions"], strict=True)
            )
        if request["pressure"]["role"] == "solved":
            lo, hi = request["pressure"]["bounds"]
            assert request["pressure"]["initial"] == math.sqrt(lo * hi)
    return observations


def source_context():
    """Every evaluator correction emits these verified laws, including repeated internal corrections."""
    mapping = s.parameter_mapping(SOURCE)
    reactions = s.reaction_values(mapping)
    native = json.loads((HERE / "native-reaction-inputs.json").read_text())
    original = s._engine_reaction_records
    for record in native:
        record["engine_correlation"]["temperature_min"] = 293.15
        record["engine_correlation"]["temperature_max"] = 353.15

    def records(request, values):
        assert values == reactions, "changed fixed source reactions"
        assert request["temperature"]["value"] <= 333.15, (
            "high-temperature input refused"
        )
        assert [r["stoichiometry"] for r in native] == request["reaction_system"][
            "reaction_matrix"
        ]
        return copy.deepcopy(native)

    s._engine_reaction_records = records
    probe.RECORD = SOURCE
    probe._BASE.clear()
    refit.REACTIONS = reactions
    return mapping, reactions, original


def k_ends(mapping):
    values = s.parameter_values(mapping)
    pairs = {
        i: [
            values[i]
            + values.get(i + "/reciprocal_temperature_slope", 0.0)
            * (1 / t - 1 / 313.15)
            for t in (293.15, 333.15)
        ]
        for i in values
        if i.endswith("/k_ij")
    }
    return {
        "temperatures_k": [293.15, 333.15],
        "pairs": pairs,
        "admissible": all(x < 1 for a in pairs.values() for x in a),
    }


def check_state(record, observation):
    check = probe.check(record)
    material, charge = [], None
    if record["status"] == "evaluated":
        system = observation["request"]["reaction_system"]
        amounts = [0.0] * len(s.COMPONENT_IDS)
        for phase in record["phases"]:
            for i, x in zip(phase["support"], phase["mole_fractions"], strict=True):
                amounts[s.COMPONENT_IDS.index(i)] += phase["amount_mol"] * x
        material = [
            math.fsum(c * x for c, x in zip(row, amounts, strict=True)) - target
            for row, target in zip(
                system["balance_matrix"], system["conserved_totals"], strict=True
            )
        ]
        charge = math.fsum(
            c * x for c, x in zip(system["charges"], amounts, strict=True)
        )
        balances = (
            all(
                abs(v) <= 1e-7 * max(1.0, abs(target))
                for v, target in zip(material, system["conserved_totals"], strict=True)
            )
            and abs(charge) <= 1e-7
        )
    else:
        balances = False
    check.update(
        material_residuals_mol=material,
        charge_residual_mol=charge,
        complete=record["status"] == "evaluated"
        and check["tolerance_met"] is True
        and not check["balance_errors"]
        and balances
        and check["max_abs_stationarity"] is not None
        and check["max_abs_stationarity"] <= 1e-10,
    )
    return check


def fit(structure, start):
    observations = verify_inputs()
    mapping, reactions, original = source_context()
    name = f"{structure}-start-{start}"
    summary_path = HERE / f"{name}-fit.json"
    assert not summary_path.exists(), "no unregistered continuation or extra fit"
    cache = RAW / name
    cache.mkdir(parents=True, exist_ok=False)
    s.RUNS = cache / "anchor-cache"
    ids, bounds, scales, values = design(structure, start)
    mapping = s.with_parameter_values(mapping, dict(zip(ids, values, strict=True)))
    params = probe.epcsaft.Parameters.from_mapping(mapping)
    model = probe.epcsaft.Mixture(params)
    fingerprint = s.parameter_fingerprint(mapping)
    controls = regression.FitControls()
    controls.maximum_iterations = 40
    controls.maximum_elapsed_time_seconds = 2250
    tolerances = {
        k: getattr(controls, k)
        for k in ("function_tolerance", "gradient_tolerance", "parameter_tolerance")
    }
    assert set(tolerances.values()) == {0.0}
    output = {
        "structure": structure,
        "start_name": start,
        "coordinates": ids,
        "start": values,
        "bounds": bounds,
        "scales": scales,
        "status": "preparing",
        "native_complete": False,
        "complete": False,
        "checks": [],
        "provenance": {
            "training_sha256": s.sha256(TRAINING),
            "source_sha256": s.sha256(SOURCE),
            "native_reaction_inputs_sha256": s.sha256(
                HERE / "native-reaction-inputs.json"
            ),
            "wheel_sha256": s.ENGINE_WHEEL_SHA256,
            "producer_sha256": s.sha256(Path(__file__)),
            "native_tolerances": tolerances,
            "maximum_iterations": 40,
            "maximum_elapsed_time_seconds": 2250,
            "state_timeout_s": 180,
            "thermochemistry": "native reaction-source derivatives; no inherited reaction calorics",
        },
    }
    save(summary_path, output)
    clock = time.perf_counter()
    try:
        assert k_ends(mapping)["admissible"]
        calibration = []
        with (cache / "anchors.jsonl").open("w") as handle:
            for observation in observations:
                rec = s.evaluate_state(
                    model,
                    observation["request"],
                    reactions,
                    observation["identity"],
                    [],
                    budget_s=180,
                    limits=s.EvaluationLimits(
                        state_timeout_s=180, overall_timeout_s=180
                    ),
                    model_fingerprint=fingerprint,
                )
                handle.write(json.dumps(rec) + "\n")
                handle.flush()
                check = check_state(rec, observation)
                output["checks"].append({"identity": observation["identity"], **check})
                save(summary_path, output)
                print(
                    "anchor", name, observation["identity"], rec["status"], flush=True
                )
                assert check["complete"], (observation["identity"], check)
                calibration.append(
                    (
                        observation,
                        s._problem_from_request(
                            s.corrected_request(observation["request"], reactions),
                            s.anchor_from(rec),
                        ),
                    )
                )
        rows = [
            r
            for observation, problem in calibration
            for r in refit.observations(params, observation, problem, 60)
        ]
        assert len(rows) == 142 and len(calibration) == 84
        coordinates = []
        for identity, value, scale, bound in zip(
            ids, values, scales, bounds, strict=True
        ):
            family = (
                "dispersion_energy_over_k"
                if identity == EPSILON
                else "k_ij_reciprocal_temperature_slope"
                if identity == SLOPE
                else "k_ij"
            )
            target = (
                "carbon-dioxide"
                if identity == EPSILON
                else tuple(identity.split("/")[1:3])
            )
            coordinates.append(
                regression.coordinate(
                    params, family, target, origin=value, scale=scale, bounds=bound
                )
            )
        output["status"] = "fitting"
        output["setup_s"] = time.perf_counter() - clock
        save(summary_path, output)
        fit_clock = time.perf_counter()
        result = regression.fit(
            params,
            coordinates,
            [r[1] for r in rows],
            weights=[r[2] for r in rows],
            controls=controls,
        )
        output.update(
            {
                k: s._jsonable(getattr(result, k))
                for k in (
                    "status",
                    "message",
                    "usable",
                    "physical",
                    "predictions",
                    "weighted_residuals",
                    "initial_cost",
                    "final_cost",
                    "iterations",
                    "residual_evaluations",
                    "jacobian_evaluations",
                    "trial_failures",
                    "iteration_costs",
                    "iteration_seconds",
                )
            }
        )
        output.update(
            targets=[r[0] for r in rows],
            fit_s=time.perf_counter() - fit_clock,
            observation_statuses=[x.name for x in result.statuses],
            failures=[
                {
                    "trial": f.trial,
                    "observation": rows[f.observation][0],
                    "status": f.status.name,
                    "message": f.message,
                    "jacobian": f.jacobian,
                }
                for f in result.failures
            ],
            active_bounds=[ids[k] for k in result.covariance.active_bounds],
            engine_covariance={
                k: getattr(result.covariance, k)
                for k in (
                    "status",
                    "assumption",
                    "rank",
                    "singular_values",
                    "variance_factor",
                )
            },
        )
        raw = {
            **output,
            "optimizer_jacobian": list(result.optimizer_jacobian),
            "physical_jacobian": list(result.physical_jacobian),
        }
        save(cache / "native-fit.json", raw)
        finite = all(
            len(v) == 142 and np.isfinite(v).all()
            for v in (result.predictions, result.weighted_residuals)
        )
        finite = (
            finite
            and len(result.physical) == len(ids)
            and np.isfinite(result.physical).all()
            and math.isfinite(result.final_cost)
        )
        jacobian_ok = (
            len(result.optimizer_jacobian) == 142 * len(ids)
            and np.isfinite(result.optimizer_jacobian).all()
        )
        output["native_complete"] = (
            result.status == "converged"
            and result.usable
            and finite
            and jacobian_ok
            and len(result.statuses) == 142
            and all(x.name == "Available" for x in result.statuses)
        )
        if jacobian_ok:
            jacobian = np.array(result.optimizer_jacobian).reshape(
                142, len(ids)
            ) / np.array(scales)
            norms = np.linalg.norm(jacobian, axis=0)
            output["weighted_physical_jacobian_singular_values"] = np.linalg.svd(
                jacobian, compute_uv=False
            ).tolist()
            output["weighted_scaled_jacobian_singular_values"] = np.linalg.svd(
                jacobian * np.array(scales), compute_uv=False
            ).tolist()
            output["column_norms"] = dict(zip(ids, norms.tolist(), strict=True))
            output["column_normalized_singular_values"] = (
                np.linalg.svd(jacobian / norms, compute_uv=False).tolist()
                if np.all(norms > 0)
                else None
            )
            output["jacobian_column_correlations"] = np.corrcoef(
                jacobian, rowvar=False
            ).tolist()
            table(
                HERE / f"{name}-jacobian.csv",
                [
                    {
                        "target": r[0],
                        "weight": r[2],
                        "prediction": p,
                        "weighted_residual": residual,
                        **{
                            f"d/d[{i}]": float(v) for i, v in zip(ids, row, strict=True)
                        },
                    }
                    for r, p, residual, row in zip(
                        rows,
                        result.predictions,
                        result.weighted_residuals,
                        jacobian,
                        strict=True,
                    )
                ],
            )
        table(
            HERE / f"{name}-iterations.csv",
            [
                {"iteration": i, "cost": cost, "seconds": sec}
                for i, (cost, sec) in enumerate(
                    zip(result.iteration_costs, result.iteration_seconds, strict=True)
                )
            ],
        )
        if len(result.physical) == len(ids) and np.isfinite(result.physical).all():
            final = s.with_parameter_values(
                mapping, dict(zip(ids, result.physical, strict=True))
            )
            for node in s._identified(final):
                if node["identity"] in ids:
                    node["provenance"] = {
                        "source_id": "issue-140-low-temperature-loaded-solution-fit",
                        "locator": f"{name}-fit.json; 142 targets at <=333.15 K",
                    }
                    node.pop("source_sha256", None)
            final["purpose"] = (
                "Issue 140 low-temperature source-constant comparison; not adopted or physically validated."
            )
            final["document_id"] = "mea-temperature-reanchor-140-" + name
            assert s.reaction_values(final) == reactions
            output["k_at_domain_ends"] = k_ends(final)
            output["native_complete"] = (
                output["native_complete"] and output["k_at_domain_ends"]["admissible"]
            )
            path = HERE / f"{name}-parameters.json"
            save(path, final)
            probe.epcsaft.Parameters.from_mapping(json.loads(path.read_text()))
            output["parameter_sha256"] = s.sha256(path)
            output["parameters_path"] = str(path.relative_to(probe.W))
    except Exception as exc:
        output.update(
            status="incomplete",
            failure_stage=output["status"],
            diagnostic=f"{type(exc).__name__}: {exc}",
            native_complete=False,
            complete=False,
        )
    finally:
        s._engine_reaction_records = original
        output["wall_s"] = time.perf_counter() - clock
        save(summary_path, output)
    print(
        json.dumps(
            {
                "name": name,
                "status": output["status"],
                "native_complete": output["native_complete"],
                "final_cost": output.get("final_cost"),
            }
        ),
        flush=True,
    )


def rescore(structure, start):
    observations = verify_inputs()
    _, reactions, original = source_context()
    name = f"{structure}-start-{start}"
    summary_path = HERE / f"{name}-fit.json"
    output = json.loads(summary_path.read_text())
    assert output["native_complete"], "incomplete native fit is not ranked or rescored"
    assert "rescore" not in output, "no unregistered repeated rescore"
    design(structure, start)
    path = HERE / f"{name}-parameters.json"
    assert s.sha256(path) == output["parameter_sha256"]
    mapping = json.loads(path.read_text())
    assert s.reaction_values(mapping) == reactions
    model = probe.epcsaft.Mixture(probe.epcsaft.Parameters.from_mapping(mapping))
    fingerprint = s.parameter_fingerprint(mapping)
    s.RUNS = RAW / name / "rescore-cache"
    assert not s.RUNS.exists(), "rescore must start with a fresh cache"
    anchors = {
        r["identity"]: s.anchor_from(r)
        for r in map(
            json.loads, (RAW / name / "anchors.jsonl").read_text().splitlines()
        )
    }
    rows, checks, groups = [], [], {}
    deadline = time.perf_counter() + 1790
    try:
        with (RAW / name / "rescore-states.jsonl").open("w") as handle:
            for observation in observations:
                rec = s.evaluate_state(
                    model,
                    observation["request"],
                    reactions,
                    observation["identity"],
                    [anchors[observation["identity"]]],
                    budget_s=180,
                    limits=s.EvaluationLimits(
                        state_timeout_s=180,
                        overall_timeout_s=180,
                        deadline_monotonic=deadline,
                    ),
                    model_fingerprint=fingerprint,
                )
                handle.write(json.dumps(rec) + "\n")
                handle.flush()
                check = check_state(rec, observation)
                checks.append({"identity": observation["identity"], **check})
                liquid = next(
                    (p for p in rec.get("phases", []) if p["role"] == "liquid"), None
                )
                view = {
                    "status": rec["status"],
                    "predictions": rec["predictions"],
                    "liquid": liquid,
                }
                for target in observation["targets"]:
                    family = (
                        "pressure"
                        if target["prediction_identity"] == "co2-partial-pressure"
                        else "species"
                    )
                    predicted = (
                        compare.predicted(view, target)
                        if rec["status"] == "evaluated"
                        else None
                    )
                    available = (
                        predicted is not None
                        and math.isfinite(predicted)
                        and (predicted > 0 or family == "species")
                    )
                    ln = (
                        math.log(predicted / target["observed"])
                        if available and predicted > 0 and target["observed"] > 0
                        else None
                    )
                    residual = (
                        (
                            ln / 0.3
                            if family == "pressure"
                            else (predicted - target["observed"])
                            / (0.1 * target["observed"] + 0.001)
                        )
                        if available
                        else None
                    )
                    row = {
                        "identity": observation["identity"],
                        "target": target["identity"],
                        "source": target["source_identity"],
                        "temperature_k": observation["request"]["temperature"]["value"],
                        "quantity": family,
                        "observed": target["observed"],
                        "predicted": predicted,
                        "ln_pred_over_obs": ln,
                        "scaled_residual": residual,
                        "cost": 0.5 * residual**2 if residual is not None else None,
                        "status": rec["status"],
                        "numerically_complete": check["complete"],
                        "parameter_sha256": s.sha256(path),
                    }
                    rows.append(row)
                    for key in (
                        family,
                        target["source_identity"],
                        f"T={row['temperature_k']}",
                        f"{family}:T={row['temperature_k']}",
                        f"{target['source_identity']}:{row['temperature_k']}",
                    ):
                        groups.setdefault(key, []).append(row)
                print(
                    "rescore", name, observation["identity"], rec["status"], flush=True
                )
        complete = (
            len(checks) == 84
            and len(rows) == 142
            and all(c["complete"] for c in checks)
            and all(
                r["scaled_residual"] is not None and math.isfinite(r["scaled_residual"])
                for r in rows
            )
        )
        cost = math.fsum(r["cost"] for r in rows) if complete else None
        output["rescore"] = {
            "cost": cost,
            "difference_from_native": cost - output["final_cost"] if complete else None,
            "states": len(checks),
            "targets": len(rows),
            "complete": complete,
            "checks": checks,
            "max_abs_stationarity": max(
                (
                    c["max_abs_stationarity"]
                    for c in checks
                    if c["max_abs_stationarity"] is not None
                ),
                default=None,
            ),
            "tolerance_met": all(c["tolerance_met"] is True for c in checks),
            "balance_errors": sum(bool(c["balance_errors"]) for c in checks),
            "family_costs": {
                k: math.fsum(r["cost"] for r in groups[k])
                if all(r["cost"] is not None for r in groups[k])
                else None
                for k in ("pressure", "species")
            },
            "source_temperature_costs": {
                k: math.fsum(r["cost"] for r in v)
                if all(r["cost"] is not None for r in v)
                else None
                for k, v in groups.items()
                if k not in ("pressure", "species")
            },
        }
        output["complete"] = complete
    except Exception as exc:
        output["complete"] = False
        output["rescore"] = {
            "complete": False,
            "states": len(checks),
            "targets": len(rows),
            "checks": checks,
            "diagnostic": f"{type(exc).__name__}: {exc}",
        }
    finally:
        table(HERE / f"{name}-rescore-targets.csv", rows)
        save(summary_path, output)
        s._engine_reaction_records = original
    print(
        json.dumps(
            {
                "name": name,
                "complete": output["complete"],
                "rescore": output["rescore"].get("cost"),
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["rescore"] and len(args) == 3:
        assert args[1] in STRUCTURES and args[2] in ("1", "2")
        rescore(*args[1:])
    elif len(args) == 2:
        design(*args)
        fit(*args)
    else:
        raise SystemExit("STRUCTURE START | rescore STRUCTURE START")
