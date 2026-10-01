"""Issue 140: low-temperature selection/freeze, then ordered assessment only.

Run `select` before `stage 1` through `stage 6`; each assessment has timeout 1800.
The Engine and existing MEA evaluator own every equilibrium calculation.
"""

import copy
import csv
import hashlib
import importlib.util
import json
import math
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[1]
RAW = BUNDLE / "results/runs/temperature-reanchor-140"
STRUCTURES = ("constant-fixed", "slope-fixed", "constant-free", "slope-free")


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path, rows):
    if rows:
        with path.open("w", newline="") as f:
            w = csv.DictWriter(
                f, list(dict.fromkeys(k for r in rows for k in r)), lineterminator="\n"
            )
            w.writeheader()
            w.writerows(rows)


def select():
    assert not (HERE / "freeze.json").exists(), (
        "Already frozen; never replace a frozen selection."
    )
    assert not list(HERE.glob("assessment-stage-*.json")), (
        "Selection precedes all assessments."
    )
    forms, finalists = {}, []
    for structure in STRUCTURES:
        starts = [
            json.loads((HERE / f"{structure}-start-{i}-fit.json").read_text())
            for i in (1, 2)
        ]
        a, b = starts
        assert a["coordinates"] == b["coordinates"]
        cost_gap = (
            abs(a["final_cost"] - b["final_cost"])
            if all(x.get("final_cost") is not None for x in starts)
            else None
        )
        agreement = cost_gap is not None and cost_gap <= 1e-6 * max(
            abs(a["final_cost"]), abs(b["final_cost"])
        )
        differences = {}
        if (
            len(a.get("physical", []))
            == len(b.get("physical", []))
            == len(a["coordinates"])
        ):
            for identity, x, y in zip(
                a["coordinates"], a["physical"], b["physical"], strict=True
            ):
                tolerance = (
                    0.1
                    if identity.endswith("reciprocal_temperature_slope")
                    else 0.01
                    if identity.endswith("dispersion_energy_over_k")
                    else 1e-5
                )
                differences[identity] = {
                    "difference": abs(x - y),
                    "tolerance": tolerance,
                    "met": abs(x - y) <= tolerance,
                }
        else:
            agreement = False
        agreement = agreement and all(v["met"] for v in differences.values())
        eligible = (
            all(x.get("complete") and x["status"] == "converged" for x in starts)
            and agreement
        )
        index = (
            0
            if cost_gap is not None
            and cost_gap <= 1e-6 * max(abs(a["final_cost"]), abs(b["final_cost"]))
            else min(
                range(2),
                key=lambda i: (
                    starts[i]["final_cost"]
                    if starts[i].get("final_cost") is not None
                    else math.inf
                ),
            )
        )
        forms[structure] = {
            "eligible": eligible,
            "two_start_agreement": agreement,
            "cost_difference": cost_gap,
            "coordinate_differences": differences,
            "chosen_start": index + 1 if eligible else None,
            "cost": starts[index]["final_cost"] if eligible else None,
            "starts": [
                {
                    "start": i + 1,
                    "status": x["status"],
                    "complete": x.get("complete", False),
                    "final_cost": x.get("final_cost"),
                    "fit_summary_sha256": digest(
                        HERE / f"{structure}-start-{i + 1}-fit.json"
                    ),
                }
                for i, x in enumerate(starts)
            ],
        }
    for energy in ("fixed", "free"):
        choices = [s for s in STRUCTURES if s.endswith(energy) and forms[s]["eligible"]]
        if not choices:
            continue
        minimum = min(forms[s]["cost"] for s in choices)
        constant = f"constant-{energy}"
        chosen = (
            constant
            if constant in choices and forms[constant]["cost"] <= 1.01 * minimum
            else min(choices, key=lambda s: forms[s]["cost"])
        )
        start = forms[chosen]["chosen_start"]
        result = json.loads((HERE / f"{chosen}-start-{start}-fit.json").read_text())
        finalists.append(
            {
                "structure": chosen,
                "start": start,
                "cost": forms[chosen]["cost"],
                "fitted_coordinates": len(result["coordinates"]),
            }
        )
    finalists.sort(
        key=lambda r: (r["fitted_coordinates"], r["structure"].endswith("free"))
    )
    records = []
    for i, r in enumerate(finalists):
        role = "primary" if i == 0 else "secondary"
        origin = HERE / f"{r['structure']}-start-{r['start']}-parameters.json"
        fit_result = json.loads(
            (HERE / f"{r['structure']}-start-{r['start']}-fit.json").read_text()
        )
        assert digest(origin) == fit_result["parameter_sha256"], (
            "Freeze must use the exact rescored parameter bytes."
        )
        destination = HERE / f"{role}-parameters.json"
        destination.write_bytes(origin.read_bytes())
        import epcsaft

        epcsaft.Parameters.from_mapping(json.loads(destination.read_text()))
        assert digest(destination) == fit_result["parameter_sha256"]
        records.append(
            {
                **r,
                "role": role,
                "record": destination.name,
                "sha256": digest(destination),
            }
        )
    freeze = {
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "forms": forms,
        "records": records,
        "selection": "fewest fitted coordinates; ties fixed source energy; unresolved until temperature folds",
        "preregistration_sha256": digest(HERE / "preregistration.md"),
        "training_targets_sha256": digest(HERE / "training-targets.csv"),
        "assessment_row_ids_sha256": digest(HERE / "assessment-row-ids.json"),
        "never_accessed_admission_sha256": digest(
            HERE / "never-accessed-vle-admission.csv"
        ),
        "high_temperature_model_access_before_freeze": False,
        "selection_code_sha256": digest(Path(__file__)),
    }
    save(HERE / "freeze.json", freeze)
    print(json.dumps(freeze), flush=True)


def calculation():
    spec = importlib.util.spec_from_file_location("phase_a", HERE / "phase-a.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.verify()
    return module


def feed_start(request, s):
    request = copy.deepcopy(request)
    feed = dict(
        zip(
            s.COMPONENT_IDS, request["reaction_system"]["feed_amounts_mol"], strict=True
        )
    )
    phases = []
    for phase in request["phases"]:
        support = (
            s.COMPONENT_IDS
            if phase["support"]["kind"] == "all_components"
            else phase["support"]["component_ids"]
        )
        total = math.fsum(feed[i] for i in support)
        phases.append(
            {
                "role": phase["fluid_role"],
                "supported_component_ids": list(support),
                "mole_fractions": [feed[i] / total for i in support],
            }
        )
    request["continuation"] = {"state": {"phases": phases}}
    if request["pressure"]["role"] == "solved":
        request["pressure"]["initial"] = math.sqrt(
            math.prod(request["pressure"]["bounds"])
        )
    return request


def wagner(pa, subset):
    rows = [
        r
        for r in csv.DictReader((HERE / "never-accessed-vle-admission.csv").open())
        if r["admitted"] == "yes" and r["subset"] == subset
    ]
    out = []
    for row in rows:
        T, loading, w = (
            float(row[k])
            for k in (
                "evaluation_temperature_k",
                "loading_mol_CO2_per_mol_MEA",
                "MEA_mass_fraction_unloaded",
            )
        )
        candidates = [
            o
            for o in pa.probe.OBSERVATIONS
            if o["request"]["pressure"]["role"] == "solved"
            and round(o["request"]["temperature"]["value"] - 273.15)
            == (80 if T < 355 else 120)
        ]
        request = copy.deepcopy(
            min(
                candidates,
                key=lambda o: abs(
                    o["request"]["reaction_system"]["feed_amounts_mol"][0] - loading
                ),
            )["request"]
        )
        system = request["reaction_system"]
        carbon, mea = system["conserved_totals"]
        system["feed_amounts_mol"][0] += loading * mea - (carbon - 2 * mea)
        system["feed_amounts_mol"][2] *= (1 - w) / w / (0.7 / 0.3)
        system["conserved_totals"] = [
            math.fsum(c * n for c, n in zip(b, system["feed_amounts_mol"], strict=True))
            for b in system["balance_matrix"]
        ]
        assert (
            abs(
                (system["conserved_totals"][0] - 2 * system["conserved_totals"][1])
                / system["conserved_totals"][1]
                - loading
            )
            < 1e-12
        )
        request["temperature"]["value"] = T
        identity = f"Wagner2013:csv-row-{row['csv_data_row_number']}"
        out.append(
            {
                "identity": identity,
                "request": request,
                "mass_fraction": w,
                "targets": [
                    {
                        "identity": identity + "-pco2",
                        "observed": float(row["pressure_pa_reported_quantity"]),
                        "prediction_identity": "co2-partial-pressure",
                        "source_identity": "Wagner2013",
                        "basis": "true-species-vapor-partial-pressure",
                        "scale": None,
                    }
                ],
            }
        )
    return out


def metrics(rows):
    complete = all(r["numerically_complete"] for r in rows)
    out = {
        "rows": len(rows),
        "available": sum(r["predicted"] is not None for r in rows),
        "complete": complete,
    }
    if complete:
        logs = [r["ln_pred_over_obs"] for r in rows]
        out.update(
            aard_percent=100
            * math.fsum(abs(r["relative_error"]) for r in rows)
            / len(rows),
            rms_ln=math.sqrt(math.fsum(v * v for v in logs) / len(rows)),
            mean_ln=math.fsum(logs) / len(rows),
            mean_relative_error_percent=100
            * math.fsum(r["relative_error"] for r in rows)
            / len(rows),
        )
        if rows[0]["quantity"] == "species":
            errors = [r["predicted"] - r["observed"] for r in rows]
            out.update(
                mean_absolute_error=math.fsum(map(abs, errors)) / len(rows),
                rms_absolute_error=math.sqrt(
                    math.fsum(e * e for e in errors) / len(rows)
                ),
                mean_absolute_signed_error=math.fsum(errors) / len(rows),
                cost=math.fsum(0.5 * r["scaled_residual"] ** 2 for r in rows),
            )
    return out


def check():
    """Analytic metric reference and selection counterexample: better cost cannot override simplicity."""
    global HERE
    original = HERE
    parameter_bytes = (original / "restored-source-parameters.json").read_bytes()
    with tempfile.TemporaryDirectory() as tmp:
        HERE = Path(tmp)
        for name in (
            "preregistration.md",
            "training-targets.csv",
            "assessment-row-ids.json",
            "never-accessed-vle-admission.csv",
        ):
            (HERE / name).write_text("check-only\n")
        for structure, cost in zip(STRUCTURES, (100.0, 99.5, 90.0, 89.2), strict=True):
            coords = (
                ["k1", "k2", "k3", "k4"]
                + (
                    ["reciprocal_temperature_slope"]
                    if structure.startswith("slope")
                    else []
                )
                + (["dispersion_energy_over_k"] if structure.endswith("free") else [])
            )
            for start in (1, 2):
                name = f"{structure}-start-{start}"
                (HERE / f"{name}-parameters.json").write_bytes(parameter_bytes)
                save(
                    HERE / f"{name}-fit.json",
                    {
                        "coordinates": coords,
                        "physical": [0.0] * len(coords),
                        "final_cost": cost,
                        "complete": True,
                        "status": "converged",
                        "parameter_sha256": digest(HERE / f"{name}-parameters.json"),
                    },
                )
        select()
        frozen = json.loads((HERE / "freeze.json").read_text())
        assert [r["structure"] for r in frozen["records"]] == [
            "constant-fixed",
            "constant-free",
        ]
        assert frozen["records"][0]["cost"] > frozen["records"][1]["cost"]
        (HERE / "freeze.json").unlink()
        for structure in ("constant-fixed", "slope-fixed"):
            p = HERE / f"{structure}-start-2-fit.json"
            r = json.loads(p.read_text())
            r["complete"] = False
            save(p, r)
        select()
        frozen = json.loads((HERE / "freeze.json").read_text())
        assert [r["structure"] for r in frozen["records"]] == ["constant-free"]
    HERE = original
    rows = [
        {
            "numerically_complete": True,
            "predicted": p,
            "observed": 10.0,
            "ln_pred_over_obs": math.log(p / 10.0),
            "relative_error": p / 10.0 - 1,
            "quantity": "pressure",
        }
        for p in (20.0, 5.0)
    ]
    m = metrics(rows)
    assert (
        m["aard_percent"] == 75.0
        and m["mean_ln"] == 0.0
        and abs(m["rms_ln"] - math.log(2)) < 1e-12
    )
    rows[0]["numerically_complete"] = False
    assert "aard_percent" not in metrics(rows)
    print("Analytic metric and simplicity/incomplete-branch selection checks passed.")


def heat_comparison(pa, freeze, deadline):
    """Prespecified outside-objective two-endpoint comparison; never an estimation target."""
    import evaluate_direct_absorption_heat as heat

    s = pa.s
    observations = [
        r
        for r in heat.read_rows(heat.OBSERVATIONS)
        if r["regression_eligible"] == "true"
    ]
    identities = json.loads((HERE / "assessment-row-ids.json").read_text())[
        "outside_objective_heat"
    ]
    assert {r["record_id"] for r in observations} == {
        r["record_id"] for r in identities
    }
    original_builder = s._engine_reaction_records
    original_evaluate = heat.evaluate_state
    original_request = heat.heat_request

    def heat_request(templates, temperature_c, loading):
        request = original_request(templates, temperature_c, loading)
        system = request["reaction_system"]
        carbon, mea = system["conserved_totals"]
        system["feed_amounts_mol"][0] += loading * mea - (carbon - 2 * mea)
        system["conserved_totals"] = [
            math.fsum(
                c * n for c, n in zip(row, system["feed_amounts_mol"], strict=True)
            )
            for row in system["balance_matrix"]
        ]
        assert (
            abs(
                (system["conserved_totals"][0] - 2 * system["conserved_totals"][1])
                / system["conserved_totals"][1]
                - loading
            )
            < 1e-12
        )
        return request

    heat.heat_request = heat_request
    records = freeze["records"] + [
        {"role": "adopted", "record": str(pa.ADOPTED), "sha256": digest(pa.ADOPTED)}
    ]
    comparisons, diagnostics, summaries = [], [], {}
    for record in records:
        path = HERE / record["record"]
        assert digest(path) == record["sha256"]
        mapping = s.parameter_mapping(path)
        reactions = s.reaction_values(mapping)

        def engine_records(request, values):
            native = original_builder(request, values)
            if record["role"] != "adopted":
                for r in native:
                    r["engine_correlation"]["temperature_min"] = 293.15
                    r["engine_correlation"]["temperature_max"] = 393.15
            return native

        s._engine_reaction_records = engine_records
        model = pa.probe.epcsaft.Mixture(
            pa.probe.epcsaft.Parameters.from_mapping(mapping),
            thermochemistry=heat.vrc.record(),
        )
        fingerprint = s.parameter_fingerprint(
            {
                "parameters": mapping,
                "thermal_sha256": s.sha256(heat.vrc.PHYSICAL_CALORICS),
            }
        )
        s.RUNS = RAW / f"heat-{record['role']}-cache"
        checks = []

        def evaluate(*args, **kwargs):
            result = original_evaluate(*args, **kwargs)
            checks.append(
                {
                    "record_role": record["role"],
                    "identity": args[3],
                    **pa.probe.check(result),
                }
            )
            with (RAW / f"heat-{record['role']}-states.jsonl").open("a") as f:
                f.write(json.dumps(result) + "\n")
            return result

        heat.evaluate_state = evaluate
        try:
            states, attempts, scored = heat.score(
                reactions,
                model,
                fingerprint,
                observations,
                s.EvaluationLimits(180, 1780, deadline),
                f"heat-{record['role']}",
            )
        except s.EvaluationTimeout as exc:
            summaries[record["role"]] = {
                "complete": False,
                "diagnostic": str(exc),
                "planned_intervals": len(observations),
            }
            diagnostics.extend(checks)
            continue
        diagnostics.extend(checks)
        valid = all(
            c["tolerance_met"] is True
            and not c["balance_errors"]
            and c["max_abs_stationarity"] is not None
            and c["max_abs_stationarity"] <= 1e-10
            for c in checks
        )
        source_rows = {r["record_id"]: r for r in observations}
        for r in scored:
            source = source_rows[r["record_id"]]
            r.update(
                record_role=record["role"],
                record_sha256=record["sha256"],
                run=source["run"],
                source_notes=source["notes"],
                first_row_source_typo_sensitivity=source[
                    "first_row_source_typo_sensitivity"
                ],
                previous_endpoint_basis=source["previous_endpoint_basis"],
            )
        comparisons.extend(scored)
        groups = {"pooled": scored}
        groups.update(
            {
                f"source={source}/T={T}C": [
                    r
                    for r in scored
                    if r["source"] == source and r["temperature_C"] == T
                ]
                for source, T in {(r["source"], r["temperature_C"]) for r in scored}
            }
        )
        groups.update(
            {
                f"source={source}/T={T}C/run={run}": [
                    r
                    for r in scored
                    if r["source"] == source
                    and r["temperature_C"] == T
                    and r["run"] == run
                ]
                for source, T, run in {
                    (r["source"], r["temperature_C"], r["run"]) for r in scored
                }
            }
        )
        groups["first-dose-excluded-sensitivity"] = [
            r for r in scored if r["previous_endpoint_basis"] != "assumed_start_loading"
        ]
        summaries[record["role"]] = {}
        for key, rows in groups.items():
            complete = valid and all(r["status"] == "evaluated" for r in rows)
            values = [
                r["residual_kj_per_mol_CO2"] for r in rows if r["status"] == "evaluated"
            ]
            summaries[record["role"]][key] = {
                "rows": len(rows),
                "available": len(values),
                "complete": complete,
                **(
                    {
                        "rmse_kj_per_mol_CO2": math.sqrt(
                            math.fsum(v * v for v in values) / len(values)
                        ),
                        "mean_bias_kj_per_mol_CO2": math.fsum(values) / len(values),
                    }
                    if complete
                    else {}
                ),
            }
        table(HERE / f"heat-{record['role']}-endpoints.csv", states)
        table(HERE / f"heat-{record['role']}-attempts.csv", attempts)
    s._engine_reaction_records = original_builder
    heat.evaluate_state = original_evaluate
    heat.heat_request = original_request
    table(HERE / "heat-comparison.csv", comparisons)
    save(
        HERE / "heat-comparison.json",
        {
            "metrics": summaries,
            "checks": diagnostics,
            "thermal_records_sha256": s.sha256(heat.vrc.PHYSICAL_CALORICS),
            "freeze_sha256": digest(HERE / "freeze.json"),
            "conditions": "Existing two-endpoint method, positive release kJ/mol CO2; zero vapor inventory; ideal-gas CO2 feed; comparison only, no uncertainty-based caloric pass.",
        },
    )


def stage(number):
    freeze = json.loads((HERE / "freeze.json").read_text())
    assert freeze["records"], (
        "No complete finalist; high-temperature assessment is not authorized."
    )
    assert digest(HERE / "preregistration.md") == freeze["preregistration_sha256"]
    assert (
        digest(HERE / "assessment-row-ids.json") == freeze["assessment_row_ids_sha256"]
    )
    assert (
        digest(HERE / "never-accessed-vle-admission.csv")
        == freeze["never_accessed_admission_sha256"]
    )
    for i in range(1, number):
        assert (HERE / f"assessment-stage-{i}.json").exists(), (
            "Prespecified assessment order"
        )
    assert not (HERE / f"assessment-stage-{number}.json").exists(), (
        "Assess once; no automatic repeat."
    )
    pa = calculation()
    s, probe, compare = pa.s, pa.probe, pa.compare
    ids = json.loads((HERE / "assessment-row-ids.json").read_text())
    canonical = {r["observation_id"]: r for r in csv.DictReader(s.CANONICAL_VLE.open())}
    subsets = {
        r["subset"]
        for r in csv.DictReader((HERE / "never-accessed-vle-admission.csv").open())
        if r["admitted"] == "yes"
    }
    near = next(x for x in subsets if "80" in x)
    outside = next(x for x in subsets if x != near)

    def canonical_set(key):
        wanted = set(ids[key])
        return probe.pressure_observations(lambda r: r["observation_id"] in wanted)

    if number == 1:
        groups = [("canonical-80C-21", canonical_set("primary_80c_pressure"))]
    elif number == 2:
        wanted = {r["target"] for r in ids["packet_80c_species"]}
        observations = []
        for o in probe.OBSERVATIONS:
            o = copy.deepcopy(o)
            o["targets"] = [t for t in o["targets"] if t["identity"] in wanted]
            if o["targets"]:
                observations.append(o)
        groups = [("species-80C", observations)]
    elif number == 3:
        groups = [("never-accessed-80C", wagner(pa, near))]
    elif number == 4:
        groups = [
            ("canonical-100-120C", canonical_set("outside_100_120c_pressure")),
            ("never-accessed-100-120C", wagner(pa, outside)),
        ]
    elif number == 5:
        groups = [
            ("transfer-15wt", canonical_set("outside_15wt_pressure")),
            ("transfer-45wt", canonical_set("outside_45wt_pressure")),
        ]
    elif number == 6:
        groups = [
            ("never-accessed-80C", wagner(pa, near)),
            ("never-accessed-100-120C", wagner(pa, outside)),
        ]
    else:
        raise ValueError("stage 1..6")
    records = (
        freeze["records"]
        if number != 6
        else [
            {"role": "adopted", "record": str(pa.ADOPTED), "sha256": digest(pa.ADOPTED)}
        ]
    )
    native_builder = s._engine_reaction_records
    deadline = time.perf_counter() + 1780
    rows, checks, summary, interaction_checks = [], [], {}, {}
    for record in records:
        path = HERE / record["record"]
        assert digest(path) == record["sha256"]
        mapping = s.parameter_mapping(path)
        reactions = s.reaction_values(mapping)
        values = s.parameter_values(mapping)
        ends = {
            i: [
                values[i]
                + values.get(i + "/reciprocal_temperature_slope", 0.0)
                * (1 / T - 1 / 313.15)
                for T in (353.15, 393.15)
            ]
            for i in values
            if i.endswith("/k_ij")
        }
        interaction_checks[record["role"]] = {
            "temperatures_k": [353.15, 393.15],
            "pairs": ends,
            "admissible_at_353_15_k": all(v[0] < 1 for v in ends.values()),
            "admissible_at_393_15_k": all(v[1] < 1 for v in ends.values()),
        }
        model = probe.epcsaft.Mixture(probe.epcsaft.Parameters.from_mapping(mapping))
        fingerprint = s.parameter_fingerprint(mapping)

        def engine_records(request, values):
            native = native_builder(request, values)
            if record["role"] != "adopted":
                for r in native:
                    r["engine_correlation"]["temperature_min"] = 293.15
                    r["engine_correlation"]["temperature_max"] = (
                        393.15 if number in (4, 5, 6) else 353.15
                    )
            return native

        s._engine_reaction_records = engine_records
        s.RUNS = RAW / f"assessment-{record['role']}-stage-{number}-cache"
        limits = s.EvaluationLimits(180, 1780, deadline)
        for group, observations in groups:
            for o in observations:
                request = feed_start(o["request"], s)
                try:
                    result = s.evaluate_state(
                        model,
                        request,
                        reactions,
                        o["identity"],
                        [],
                        budget_s=180,
                        limits=limits,
                        model_fingerprint=fingerprint,
                    )
                except s.EvaluationTimeout as exc:
                    result = {
                        "status": "non_evaluable",
                        "failure_code": "assessment_deadline_exhausted",
                        "failure_diagnostic": str(exc),
                        "predictions": {},
                        "identity": o["identity"],
                    }
                with (RAW / f"assessment-{record['role']}-stage-{number}.jsonl").open(
                    "a"
                ) as f:
                    f.write(json.dumps(result) + "\n")
                check = probe.check(result)
                ok = (
                    result["status"] == "evaluated"
                    and check["tolerance_met"]
                    and not check["balance_errors"]
                    and check["max_abs_stationarity"] is not None
                    and check["max_abs_stationarity"] <= 1e-10
                )
                checks.append(
                    {
                        "record_role": record["role"],
                        "group": group,
                        "identity": o["identity"],
                        **check,
                    }
                )
                liq = next(
                    (p for p in result.get("phases", []) if p["role"] == "liquid"), None
                )
                system = request["reaction_system"]
                carbon, mea = system["conserved_totals"]
                for t in o["targets"]:
                    pressure = t["prediction_identity"] == "co2-partial-pressure"
                    rec = {**result, "liquid": liq}
                    predicted = (
                        compare.predicted(rec, t)
                        if result["status"] == "evaluated"
                        else None
                    )
                    ln = (
                        math.log(predicted / t["observed"])
                        if predicted is not None and predicted > 0 and t["observed"] > 0
                        else None
                    )
                    row = {
                        "record_role": record["role"],
                        "record_sha256": record["sha256"],
                        "group": group,
                        "identity": o["identity"],
                        "target": t["identity"],
                        "source": t["source_identity"],
                        "temperature_k": request["temperature"]["value"],
                        "mea_mass_fraction": o.get(
                            "mass_fraction",
                            float(
                                canonical[o["identity"].removeprefix("canonical:")][
                                    "MEA_weight_fraction"
                                ]
                            )
                            if o["identity"].startswith("canonical:")
                            else 0.3,
                        ),
                        "loading_mol_CO2_per_mol_MEA": (carbon - 2 * mea) / mea,
                        "quantity": "pressure" if pressure else "species",
                        "unit": "Pa" if pressure else "mol/mol true species",
                        "observed": t["observed"],
                        "predicted": predicted,
                        "ln_pred_over_obs": ln,
                        "relative_error": predicted / t["observed"] - 1
                        if ln is not None
                        else None,
                        "scaled_residual": ln / 0.3
                        if pressure and ln is not None
                        else (predicted - t["observed"]) / (0.1 * t["observed"] + 0.001)
                        if predicted is not None
                        else None,
                        "status": result["status"],
                        "numerically_complete": bool(ok and ln is not None),
                        **check,
                    }
                    rows.append(row)
                print(
                    record["role"],
                    group,
                    o["identity"],
                    result["status"],
                    check,
                    flush=True,
                )
    for role in {r["record_role"] for r in rows}:
        for group in {r["group"] for r in rows}:
            base = [r for r in rows if r["record_role"] == role and r["group"] == group]
            if not base:
                continue
            sets = {"pooled": base}
            sets.update(
                {
                    f"source={source}": [r for r in base if r["source"] == source]
                    for source in {r["source"] for r in base}
                }
            )
            sets.update(
                {
                    f"T={T}K": [r for r in base if r["temperature_k"] == T]
                    for T in {r["temperature_k"] for r in base}
                }
            )
            sets.update(
                {
                    f"source={source}/T={T}K": [
                        r
                        for r in base
                        if r["source"] == source and r["temperature_k"] == T
                    ]
                    for source, T in {(r["source"], r["temperature_k"]) for r in base}
                }
            )
            if group.startswith("transfer"):
                for label, low, high in (
                    ("<0.3", 0.0, 0.3),
                    ("0.3-0.5", 0.3, 0.5),
                    (">=0.5", 0.5, math.inf),
                ):
                    band = [
                        r
                        for r in base
                        if low <= r["loading_mol_CO2_per_mol_MEA"] < high
                    ]
                    if band:
                        sets["loading=" + label] = band
            if group == "canonical-80C-21":
                sets["canonical-80C-19"] = [
                    r
                    for r in base
                    if r["identity"].removeprefix("canonical:")
                    in ids["secondary_80c_pressure_19"]
                ]
            summary[f"{role}/{group}"] = {
                key: metrics(values) for key, values in sets.items()
            }
    table(HERE / f"assessment-stage-{number}-rows.csv", rows)
    save(
        HERE / f"assessment-stage-{number}.json",
        {
            "stage": number,
            "metrics": summary,
            "checks": checks,
            "freeze_sha256": digest(HERE / "freeze.json"),
            "records": records,
            "interaction_checks": interaction_checks,
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "all_required_states_complete": all(
                r["numerically_complete"] for r in rows
            ),
        },
    )
    s._engine_reaction_records = native_builder
    if number == 6:
        heat_comparison(pa, freeze, deadline)


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    if sys.argv[1:] == ["select"]:
        select()
    elif sys.argv[1:] == ["check"]:
        check()
    elif len(sys.argv) == 3 and sys.argv[1] == "stage":
        stage(int(sys.argv[2]))
    else:
        raise SystemExit("check | select | stage 1..6")
