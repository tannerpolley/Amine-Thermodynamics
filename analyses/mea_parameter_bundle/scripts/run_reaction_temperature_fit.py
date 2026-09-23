"""Bounded R1--R5 reaction-enthalpy screen with exact Engine replay.

The screen, candidate replay, heat endpoints, parity and benchmark consume the
anchored thermal reference, which the pinned Engine cannot construct (see
``evaluate_direct_absorption_heat``); their implementation is in Git history.
The pressure and speciation groups of the full replay, its summary, the
adoption record and the self-check remain.  Every exact solve is cached per
state under the ignored ``results/runs/`` directory.
"""

from __future__ import annotations

import os

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import argparse  # noqa: E402
import copy  # noqa: E402
import csv  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402
from pathlib import Path  # noqa: E402

import epcsaft  # noqa: E402

from evaluate_direct_absorption_heat import THERMAL_REFERENCE_UNAVAILABLE  # noqa: E402
from shared_evaluation import (  # noqa: E402
    ENGINE_WHEEL_SHA256,
    PARAMETERS,
    Anchor,
    attempt_plan,
    corrected_request,
    evaluate_state,
    anchor_from,
    EXPECTED_REACTION_CORRELATIONS,
    load_parameters,
    provenance as shared_provenance,
    sha256,
    _selected_reactions,
    verify_wheel as shared_verify_wheel,
)
from run_direct_parameter_campaign import pressure_catalog, speciation_catalog  # noqa: E402
from refresh_results import bounded_main  # noqa: E402
from result_freshness import FIGURE_DATA, HEAT, require_results  # noqa: E402


ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results/reaction-temperature-fit"
RUNS = ANALYSIS / "results/runs/reaction-temperature-fit"
HEAT_OBSERVATIONS = ANALYSIS / "data/input/calorimetry-observation-partition.csv"
BASELINE_RESIDUALS = ANALYSIS / "results/current-best-fit-residuals.csv"
PIVOT_K = 313.15
R = 8.31446261815324
STEP_KJ_MOL = 2.5
POLICY = "baseline-replay-recovery-v1"
# Independent holdout: Xu 2011 pressure rows never enter the objective.
HOLDOUT_PRESSURE_SOURCES = ("Xu2011",)
# Kim et al. 2014 is model-selection comparison only; fitted heat rows are
# Kim--Svendsen 2007 calibration rows.
PRESSURE_IDS = (
    "vle_obs_0206",
    "vle_obs_0208",
    "vle_obs_0211",
    "vle_obs_0227",
    "vle_obs_0228",
    "vle_obs_0232",
)
HEAT_IDS = (
    "kim2007_t40_r1_0.124",
    "kim2007_t40_r2_0.375",
    "kim2007_t40_r2_0.543",
    "kim2007_t80_r2_0.137",
    "kim2007_t80_r2_0.375",
    "kim2007_t80_r2_0.570",
)
REACTIONS = ("R1", "R2", "R3", "R4", "R5")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = tuple(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def verify_wheel() -> None:
    shared_verify_wheel()


def driver_sha256() -> str:
    return sha256(Path(__file__).with_name("shared_evaluation.py"))


def quarter_cpu_affinity() -> tuple[int, ...]:
    available = sorted(os.sched_getaffinity(0))
    chosen = tuple(available[:1])
    os.sched_setaffinity(0, chosen)
    return chosen


def provenance() -> dict[str, object]:
    return {
        **shared_provenance(),
        "driver_sha256": driver_sha256(),
        "policy": POLICY,
    }


# --- reaction shifts -------------------------------------------------------


def baseline_reactions() -> dict[str, float]:
    values = _selected_reactions()
    for reaction in ("R1", "R3"):
        source = EXPECTED_REACTION_CORRELATIONS[reaction]
        for coefficient in ("a", "b_k", "c", "d_per_k"):
            values[f"reaction:{reaction}:correlation:{coefficient}"] = float(
                source[coefficient]
            )
    return values


def shifted_reactions(shifts_kj_mol: dict[str, float]) -> dict[str, float]:
    values = baseline_reactions()
    for reaction, shift_kj in shifts_kj_mol.items():
        shift = 1000.0 * shift_kj
        if reaction == "R5":
            values["reaction:R5:correlation:a_k"] += shift / (R * math.log(10.0))
            values["reaction:R5:correlation:b"] -= shift / (
                R * PIVOT_K * math.log(10.0)
            )
        else:
            values[f"reaction:{reaction}:correlation:a"] += shift / (R * PIVOT_K)
            values[f"reaction:{reaction}:correlation:b_k"] -= shift / R
    return values


def pivot_check(values: dict[str, float]) -> None:
    request = pressure_catalog(True)[0]["request"]
    base = corrected_request(request, baseline_reactions())
    trial = corrected_request(request, values)
    for old, new in zip(
        base["reaction_system"]["equilibrium_constants"],
        trial["reaction_system"]["equilibrium_constants"],
        strict=True,
    ):
        if not math.isclose(float(old[0]), float(new[0]), rel_tol=0.0, abs_tol=2e-12):
            raise AssertionError(f"pivot changed for {new[6]['reaction_id']}")


# --- catalogs ----------------------------------------------------------------


def require_current_baseline() -> None:
    """Screening and adoption must compare one identified incumbent."""
    selected = sha256(PARAMETERS)
    for receipt in (FIGURE_DATA, HEAT):
        require_results(receipt)
        if json.loads(receipt.read_text()).get("parameter_document_sha256") != selected:
            raise ValueError(
                "Baseline belongs to another selection; refresh before screening or adoption"
            )


def baseline_lookup() -> dict[tuple[str, str], float]:
    require_current_baseline()
    return {
        (row["observation_id"], row["target"]): float(row["predicted"])
        for row in read_csv(BASELINE_RESIDUALS)
        if row["predicted"] != ""
    }


def target_rows(
    state: dict[str, object], record: dict[str, object], extra: dict[str, object]
) -> list[dict[str, object]]:
    rows = []
    for target in state["targets"]:
        predicted = record["predictions"].get(target["prediction_identity"])
        rows.append(
            {
                **extra,
                "family": state["family"],
                "observation_id": state["observation_id"],
                "source": state["source"],
                "temperature_C": round(float(state["temperature_c"])),
                "loading": state["loading"],
                "target": target["identity"],
                "observed": target["observed"],
                "predicted": ""
                if predicted is None
                else predicted * float(target["unit_scale"]),
                "status": record["status"],
                "failure_code": record["failure_code"],
                "failure_diagnostic": record["failure_diagnostic"],
                "attempt_count": record.get("attempt_count", 0),
                "wall_s": record.get("wall_s", 0.0),
                "cache_hit": record.get("cache_hit", False),
            }
        )
    return rows


def pivot_rows(
    state: dict[str, object],
    baseline: dict[tuple[str, str], float],
    extra: dict[str, object],
) -> list[dict[str, object]]:
    """40 C rows: every ln K is pivot-preserved, so the baseline value is exact."""
    rows = []
    for target in state["targets"]:
        key = (state["observation_id"], target["identity"])
        present = key in baseline
        rows.append(
            {
                **extra,
                "family": state["family"],
                "observation_id": state["observation_id"],
                "source": state["source"],
                "temperature_C": 40,
                "loading": state["loading"],
                "target": target["identity"],
                "observed": target["observed"],
                "predicted": baseline[key] if present else "",
                "status": "pivot_reuse" if present else "non_evaluable",
                "failure_code": "" if present else "baseline_non_evaluable",
                "failure_diagnostic": "",
                "attempt_count": 0,
                "wall_s": 0.0,
                "cache_hit": True,
            }
        )
    return rows


def residual(row: dict[str, object]) -> float:
    predicted, observed = float(row["predicted"]), float(row["observed"])
    return (
        predicted - observed
        if row["family"] == "heat"
        else math.log10(predicted / observed)
    )


# --- full replay -----------------------------------------------------------------


def full_group(
    task: tuple[str, str, tuple[int, ...], dict[str, float], float],
) -> tuple[str, list[dict[str, object]]]:
    group, family, temperatures, shifts, budget_s = task
    model = epcsaft.Mixture(load_parameters())
    reactions = shifted_reactions(shifts)
    baseline = baseline_lookup()
    rows: list[dict[str, object]] = []
    extra = {"partition": ""}
    anchors: list[Anchor] = []
    if family in ("pressure", "speciation"):
        catalog = (
            pressure_catalog(True) if family == "pressure" else speciation_catalog()
        )
        states = sorted(
            (
                row
                for row in catalog
                if round(float(row["temperature_c"])) in temperatures
            ),
            key=lambda row: (float(row["temperature_c"]), float(row["loading"])),
        )
        for state in states:
            if round(float(state["temperature_c"])) == 40:
                rows.extend(pivot_rows(state, baseline, extra))
                continue
            record = evaluate_state(
                model,
                state["request"],
                reactions,
                f"full-{state['observation_id']}-candidate",
                anchors if family == "pressure" else [],
                budget_s,
            )
            rows.extend(target_rows(state, record, extra))
            if family == "pressure" and record["status"] == "evaluated":
                anchors.append(anchor_from(record))
        return group, rows
    raise RuntimeError(THERMAL_REFERENCE_UNAVAILABLE)


def run_full(
    workers: int,
    budget_s: float,
    summarize_only: bool = False,
    groups: list[str] | None = None,
) -> None:
    candidate = json.loads(
        (RESULTS / "candidate-receipt.json").read_text(encoding="utf-8")
    )
    shifts = candidate["candidate_shifts_kj_mol"]
    if (
        candidate["parameter_sha256"] != sha256(PARAMETERS)
        or candidate["engine_wheel_sha256"] != ENGINE_WHEEL_SHA256
    ):
        raise ValueError("candidate receipt does not match the selected bundle")
    affinity = quarter_cpu_affinity()
    workers = min(workers, len(affinity), 3)
    # Pressure runs as one ascending-temperature task so cross-temperature
    # anchors exist, exactly as in the retained baseline replay.
    tasks = [
        ("pressure-all", "pressure", (40, 60, 80, 100, 120), shifts, budget_s),
        *(
            (f"speciation-{t}", "speciation", (t,), shifts, budget_s)
            for t in (20, 40, 60, 80)
        ),
        *((f"heat-{t}", "heat", (t,), shifts, budget_s) for t in (40, 80, 120)),
    ]
    selected = (
        [] if summarize_only else [t for t in tasks if groups is None or t[0] in groups]
    )
    rows: list[dict[str, object]] = []
    done: set[str] = set()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(full_group, task): task for task in selected}
        for future in as_completed(futures):
            group, group_rows = future.result()
            rows.extend(group_rows)
            done.add(group)
            write_json(
                RUNS / "groups" / f"{group}.json",
                {"group": group, "rows": group_rows, **provenance()},
            )
            print(f"full: {group} complete", flush=True)
    for task in tasks:
        path = RUNS / "groups" / f"{task[0]}.json"
        if task[0] not in done and path.exists():
            cached = json.loads(path.read_text(encoding="utf-8"))
            if (
                cached["parameter_sha256"] == sha256(PARAMETERS)
                and cached["engine_wheel_sha256"] == ENGINE_WHEEL_SHA256
            ):
                rows.extend(cached["rows"])
                done.add(task[0])
    missing_groups = [task[0] for task in tasks if task[0] not in done]
    rows.sort(
        key=lambda row: (
            str(row["family"]),
            float(row["temperature_C"]),
            str(row["observation_id"]),
            str(row["target"]),
        )
    )
    write_csv(RESULTS / "full-validation-targets.csv", rows)
    summary: dict[str, object] = {}

    def metrics(members: list[dict[str, object]]) -> dict[str, object]:
        evaluated = [row for row in members if row["predicted"] != ""]
        positive = [
            row
            for row in evaluated
            if row["family"] == "heat"
            or (float(row["predicted"]) > 0 and float(row["observed"]) > 0)
        ]
        errors = [residual(row) for row in positive]
        return {
            "attempted": len(members),
            "evaluated": len(evaluated),
            "metric_target_count": len(positive),
            "rmse": math.sqrt(statistics.fmean(v * v for v in errors))
            if errors
            else None,
            "bias": statistics.fmean(errors) if errors else None,
            "median_absolute_error": statistics.median(abs(v) for v in errors)
            if errors
            else None,
        }

    for family in ("pressure", "speciation", "heat"):
        members = [row for row in rows if row["family"] == family]
        if family == "pressure":
            summary["pressure_calibration"] = metrics(
                [r for r in members if r["source"] not in HOLDOUT_PRESSURE_SOURCES]
            )
            summary["pressure_holdout"] = {
                "sources": list(HOLDOUT_PRESSURE_SOURCES),
                **metrics(
                    [r for r in members if r["source"] in HOLDOUT_PRESSURE_SOURCES]
                ),
            }
        elif family == "heat":
            summary["heat_by_partition"] = {
                partition: metrics([r for r in members if r["partition"] == partition])
                for partition in sorted({str(r["partition"]) for r in members})
            }
        else:
            summary[family] = metrics(members)
        summary[f"{family}_by_temperature"] = {
            str(t): metrics([r for r in members if int(r["temperature_C"]) == t])
            for t in sorted({int(r["temperature_C"]) for r in members})
        }
    receipt = {
        "candidate_shifts_kj_mol": shifts,
        "workers": workers,
        "cpu_affinity": affinity,
        **provenance(),
        "validation_complete": not missing_groups,
        "missing_groups": missing_groups,
        "summary": summary,
    }
    write_json(RESULTS / "full-validation-receipt.json", receipt)
    print(json.dumps(receipt, indent=2))


HISTORY = ANALYSIS / "results/parameter-record-history.csv"
HOLDOUT_LEDGER = ANALYSIS / "results/holdout-evaluations.csv"


def paired_metrics(rows_a: dict, rows_b: dict, keys: list) -> dict[str, float | int]:
    errors_a = [residual(rows_a[k]) for k in keys]
    errors_b = [residual(rows_b[k]) for k in keys]
    rms = lambda v: math.sqrt(statistics.fmean(x * x for x in v)) if v else None  # noqa: E731
    return {
        "count": len(keys),
        "baseline_rmse": rms(errors_a),
        "candidate_rmse": rms(errors_b),
        "baseline_bias": statistics.fmean(errors_a) if errors_a else None,
        "candidate_bias": statistics.fmean(errors_b) if errors_b else None,
    }


def run_adopt() -> None:
    """Compare the replayed candidate with the incumbent on comparable cohorts,
    apply the adoption rules, and on acceptance write the new parameter record."""
    require_current_baseline()
    full = json.loads(
        (RESULTS / "full-validation-receipt.json").read_text(encoding="utf-8")
    )
    if not full["validation_complete"]:
        raise RuntimeError(f"full replay incomplete: {full['missing_groups']}")
    candidate = json.loads(
        (RESULTS / "candidate-receipt.json").read_text(encoding="utf-8")
    )
    shifts = candidate["candidate_shifts_kj_mol"]
    cand = {
        (r["family"], r["observation_id"], r["target"]): r
        for r in read_csv(RESULTS / "full-validation-targets.csv")
    }
    base_rows = {}
    for r in read_csv(BASELINE_RESIDUALS):
        base_rows[(r["family"], r["observation_id"], r["target"])] = {
            "family": r["family"],
            "source": r["source"],
            "observed": r["observed"],
            "predicted": r["predicted"],
        }
    for r in read_csv(
        ANALYSIS / "results/calorimetry/current-selected-direct-enthalpy-comparison.csv"
    ):
        base_rows[("heat", r["record_id"], "heat_release")] = {
            "family": "heat",
            "source": r["source"],
            "observed": r["observed_heat_release_kj_per_mol_CO2"],
            "predicted": r["predicted_heat_release_kj_per_mol_CO2"],
            "partition": r["campaign_partition"],
        }

    def usable(row):
        return (
            row["predicted"] != ""
            and float(row["observed"]) > 0
            and (row["family"] == "heat" or float(row["predicted"]) > 0)
        )

    common = [
        k for k in cand if k in base_rows and usable(cand[k]) and usable(base_rows[k])
    ]
    cohorts = {
        "pressure_calibration": [
            k
            for k in common
            if k[0] == "pressure" and cand[k]["source"] not in HOLDOUT_PRESSURE_SOURCES
        ],
        "pressure_holdout_xu2011": [
            k
            for k in common
            if k[0] == "pressure" and cand[k]["source"] in HOLDOUT_PRESSURE_SOURCES
        ],
        "speciation": [k for k in common if k[0] == "speciation"],
        "heat_calibration_40_80": [
            k
            for k in common
            if k[0] == "heat" and cand[k]["partition"] == "calibration"
        ],
        "heat_holdout_120": [
            k
            for k in common
            if k[0] == "heat" and cand[k]["partition"] == "temperature_holdout"
        ],
        "heat_model_selection_kim2014": [
            k
            for k in common
            if k[0] == "heat" and cand[k]["partition"] == "model_selection_comparison"
        ],
    }
    comparison = {
        name: paired_metrics(base_rows, cand, keys) for name, keys in cohorts.items()
    }
    evaluability = {
        "pressure": {
            "baseline": sum(
                1 for k in base_rows if k[0] == "pressure" and usable(base_rows[k])
            ),
            "candidate": sum(1 for k in cand if k[0] == "pressure" and usable(cand[k])),
        },
        "speciation": {
            "baseline": sum(
                1 for k in base_rows if k[0] == "speciation" and usable(base_rows[k])
            ),
            "candidate": sum(
                1 for k in cand if k[0] == "speciation" and usable(cand[k])
            ),
        },
        "heat": {
            "baseline": sum(
                1 for k in base_rows if k[0] == "heat" and usable(base_rows[k])
            ),
            "candidate": sum(1 for k in cand if k[0] == "heat" and usable(cand[k])),
        },
    }
    held_out = ("pressure_holdout_xu2011", "heat_holdout_120")
    improved_held_out = [
        n
        for n in held_out
        if comparison[n]["count"]
        and comparison[n]["candidate_rmse"] < comparison[n]["baseline_rmse"]
    ]
    degraded = [
        n
        for n, m in comparison.items()
        if m["count"] and m["candidate_rmse"] > m["baseline_rmse"]
    ]
    rules = {
        "evaluability_not_below_incumbent": all(
            v["candidate"] >= v["baseline"] for v in evaluability.values()
        ),
        "held_out_blocks_improved": improved_held_out,
        "no_cohort_degraded": not degraded,
        "degraded_cohorts": degraded,
        "interior_solution": candidate["proposal"] == "unbounded",
    }
    accepted = (
        rules["evaluability_not_below_incumbent"]
        and len(improved_held_out) == len(held_out)
        and rules["no_cohort_degraded"]
        and rules["interior_solution"]
    )
    decision = {
        "decision": "adopted_as_exploratory_incumbent" if accepted else "not_adopted",
        "candidate_shifts_kj_mol": shifts,
        "comparison": comparison,
        "evaluability": evaluability,
        "rules": rules,
        "incumbent_parameter_sha256": sha256(PARAMETERS),
        **provenance(),
    }
    ledger_rows = [
        {
            "date": "2026-09-03",
            "candidate": "reaction-temperature-fit unbounded",
            "holdout_block": n,
            "baseline_rmse": comparison[n]["baseline_rmse"],
            "candidate_rmse": comparison[n]["candidate_rmse"],
            "count": comparison[n]["count"],
            "decision": decision["decision"],
        }
        for n in held_out
    ]
    _append_csv(HOLDOUT_LEDGER, ledger_rows)
    if accepted:
        new_sha = write_adopted_parameters(shifts, candidate)
        decision["adopted_parameter_sha256"] = new_sha
    _append_csv(
        HISTORY,
        [
            {
                "date": "2026-09-03",
                "incumbent_sha256": sha256(PARAMETERS)
                if not accepted
                else decision["incumbent_parameter_sha256"],
                "candidate": "reaction-temperature-fit unbounded R2/R4/R5 enthalpy shifts",
                "candidate_sha256": decision.get("adopted_parameter_sha256", ""),
                "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
                "decision": decision["decision"],
                "reason": "; ".join(
                    f"{n}: {m['baseline_rmse']:.4f}->{m['candidate_rmse']:.4f} (n={m['count']})"
                    for n, m in comparison.items()
                    if m["count"]
                ),
                "evidence": "analyses/mea_parameter_bundle/results/reaction-temperature-fit/adoption-receipt.json",
            }
        ],
    )
    write_json(RESULTS / "adoption-receipt.json", decision)
    print(json.dumps(decision, indent=2))


def _append_csv(path: Path, rows: list[dict[str, object]]) -> None:
    existing = read_csv(path) if path.exists() else []
    write_csv(path, existing + rows)


def write_adopted_parameters(
    shifts: dict[str, float], candidate: dict[str, object]
) -> str:
    """Write the shifted R2/R4/R5 correlations into a new parameter document."""
    document = json.loads(PARAMETERS.read_text(encoding="utf-8"))
    values = shifted_reactions(shifts)
    receipt_sha = "sha256:" + sha256(RESULTS / "candidate-receipt.json")
    source = {
        "domain_id": "mea-diagnostic-293-15-to-393-15-k",
        "locator": "analyses/mea_parameter_bundle/results/reaction-temperature-fit/candidate-receipt.json:proposal=unbounded; constant reaction-enthalpy shift preserving ln K at 313.15 K",
        "source_id": "mea-reaction-temperature-fit-2026-09-03",
    }
    units = {
        "a": "dimensionless",
        "b_k": "kelvin",
        "c": "dimensionless",
        "d_per_k": "1 / kelvin",
        "a_k": "kelvin",
        "b": "dimensionless",
        "c_per_k": "1 / kelvin",
    }
    template = next(
        r for r in document["reaction_correlations"] if r["reaction_id"] == "R4"
    )
    kept = [
        r
        for r in document["reaction_correlations"]
        if r["reaction_id"] not in ("R2", "R4", "R5")
    ]
    for reaction_id, names, kind in (
        (
            "R2",
            ("a", "b_k", "c", "d_per_k"),
            "ln-k-a-plus-b-over-t-plus-c-ln-t-plus-d-t",
        ),
        ("R4", ("a", "b_k"), "ln-k-a-plus-b-over-t"),
        ("R5", ("a_k", "b", "c_per_k"), "negative-log10-temperature-polynomial"),
    ):
        old = next(
            (
                r
                for r in document["reaction_correlations"]
                if r["reaction_id"] == reaction_id
            ),
            None,
        )
        entry = copy.deepcopy(old or template)
        entry.update(
            {
                "reaction_id": reaction_id,
                "kind": kind,
                "source": source,
                "source_sha256": receipt_sha,
                "qualification": "candidate_extrapolation",
            }
        )
        domains = {
            c["name"]: c.get("optimizer_domain", {"lower": -1.0e6, "upper": 1.0e6})
            for c in (old or {}).get("coefficients", [])
        }
        entry["coefficients"] = [
            {
                "identity": f"reaction:{reaction_id}:correlation:{n}",
                "name": n,
                "optimizer_domain": domains.get(n, {"lower": -1.0e6, "upper": 1.0e6}),
                "value": {
                    "magnitude": values[f"reaction:{reaction_id}:correlation:{n}"],
                    "unit": units[n],
                },
            }
            for n in names
        ]
        if reaction_id == "R2":
            entry["source"] = {
                **source,
                "locator": source["locator"]
                + "; R2 base: Austgen 1991 converted to the common aqueous-molality standard state (ln K offset +4.0165349923); supersedes the source-contract R2 for this record",
            }
        kept.append(entry)
    document["reaction_correlations"] = sorted(kept, key=lambda r: r["reaction_id"])
    if all(item["source_id"] != source["source_id"] for item in document["sources"]):
        document["sources"].append(
            {
                "citation": "MEA-Thermodynamics reaction-temperature fit, 2026-09-03 (analyses/mea_parameter_bundle/results/reaction-temperature-fit)",
                "source_id": source["source_id"],
                "use_basis": "constant R2/R4/R5 reaction-enthalpy shifts fitted to pressure, speciation, and 40/80 C calorimetry with Xu 2011 pressure and 120 C calorimetry held out; ln K preserved at 313.15 K",
            }
        )
    document["document_version"] = int(document.get("document_version", 1)) + 1
    PARAMETERS.write_text(
        json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    for identity, value in _selected_reactions().items():
        assert math.isclose(value, values[identity], rel_tol=0, abs_tol=1e-12), identity
    return sha256(PARAMETERS)


def self_check() -> None:
    base = baseline_reactions()
    assert all(base[identity] == value for identity, value in _selected_reactions().items())
    for reaction in REACTIONS:
        trial = shifted_reactions({reaction: STEP_KJ_MOL})
        pivot_check(trial)
        assert trial != base
        for temperature_k in (293.15, 313.15, 353.15, 393.15):
            request = copy.deepcopy(pressure_catalog(True)[0]["request"])
            request["temperature"]["value"] = temperature_k
            old = corrected_request(request, base)["reaction_system"]["engine_reactions"]
            new = corrected_request(request, trial)["reaction_system"]["engine_reactions"]
            for index, (before, after) in enumerate(
                zip(old, new, strict=True), start=1
            ):
                expected = 1000.0 * STEP_KJ_MOL if reaction == f"R{index}" else 0.0
                before_correlation = before["engine_correlation"]
                after_correlation = after["engine_correlation"]
                actual = (
                    R
                    * temperature_k**2
                    * (
                        -after_correlation["b"] / temperature_k**2
                        + after_correlation["c"] / temperature_k
                        + after_correlation["d"]
                        + before_correlation["b"] / temperature_k**2
                        - before_correlation["c"] / temperature_k
                        - before_correlation["d"]
                    )
                )
                assert math.isclose(actual, expected, rel_tol=2e-12, abs_tol=2e-8)
    # Cohort roles.
    heat = {row["record_id"]: row for row in read_csv(HEAT_OBSERVATIONS)}
    assert all(heat[k]["campaign_partition"] == "calibration" for k in HEAT_IDS)
    pressure = {row["observation_id"]: row for row in pressure_catalog(True)}
    assert all(
        pressure[k]["source"] not in HOLDOUT_PRESSURE_SOURCES for k in PRESSURE_IDS
    )
    # Status can never be "evaluated" without a prediction.
    fake_state = {
        "family": "pressure",
        "observation_id": "x",
        "source": "s",
        "temperature_c": 40,
        "loading": 0.1,
        "targets": [
            {
                "identity": "pCO2",
                "prediction_identity": "co2-partial-pressure",
                "observed": 1.0,
                "unit_scale": 1.0,
            }
        ],
    }
    assert pivot_rows(fake_state, {}, {})[0]["status"] == "non_evaluable"
    # Duplicate starts collapse in the attempt plan.
    a = Anchor(120, 0.1, 1.0e5, (0.5, 0.5), 1e-5)
    kinds = [k for k, _ in attempt_plan(120, 0.12, [a, a])]
    assert sorted(kinds) == [
        "cold-packet-start",
        "same-temperature-anchor",
    ]
    print("self-check passed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--parity", action="store_true")
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--sensitivity-check", action="store_true")
    parser.add_argument("--adopt", action="store_true")
    parser.add_argument("--candidate", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--summarize-partial", action="store_true")
    parser.add_argument("--groups", nargs="+")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--budget-s",
        type=float,
        default=900.0,
        help="per-state wall budget across attempts",
    )
    args = parser.parse_args()
    quarter_cpu_affinity()
    verify_wheel()
    if args.self_check:
        self_check()
    elif args.adopt:
        run_adopt()
    elif args.sensitivity_check:
        raise RuntimeError(
            "reaction-coefficient equilibrium actions are unavailable in the pinned "
            "Engine (active parameters address EOS families only; "
            "tannerpolley/ePC-SAFT#61); the retained sensitivity-check results are "
            "left unchanged"
        )
    elif args.summarize_partial:
        run_full(args.workers, args.budget_s, summarize_only=True)
    elif args.full:
        run_full(args.workers, args.budget_s, groups=args.groups)
    else:
        # Screen, candidate, parity and benchmark all consume the anchored
        # thermal reference.
        raise RuntimeError(THERMAL_REFERENCE_UNAVAILABLE)


if __name__ == "__main__":
    bounded_main(main)
