#!/usr/bin/env python3
"""Cold, paired MEA comparison of the superseded and greenfield Engine wheels."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import math
import os
import statistics
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter


ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "analyses/mea_parameter_bundle"
SCRIPTS = ANALYSIS / "scripts"
OUTPUT = ANALYSIS / "results/runs/engine-comparison"
STATE_PACKET = ANALYSIS / "data/input/state-packet.json.gz"
PARAMETERS_G = ANALYSIS / "results/selected-current-best-parameters.json"
PARAMETERS_S_REV = "8f8e4a2^:analyses/mea_parameter_bundle/results/selected-current-best-parameters.json"
EVALUATOR_S_REV = "8f8e4a2^:analyses/mea_parameter_bundle/scripts/shared_evaluation.py"
LEGACY_FILES = ("shared_evaluation.py",)
HISTORICAL_WHEEL = ANALYSIS / "data/input/engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl"
GREENFIELD_WHEEL = Path(
    "/home/tnnrpolley21/.cache/epcsaft/wheels/"
    "3eb502abf74c4bb9f48fcafbbe2f271e7bba7a70152ed2d998f10c4606741252/"
    "epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl"
)
ENGINE = {
    "S": {
        "name": "SUPERSEDED",
        "commit": "8438ce5f94a547189c91c4ec180a7782d60879d6",
        "wheel": HISTORICAL_WHEEL,
        "wheel_sha256": "40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805",
        "parameter": None,
        "parameter_sha256": "568f7a5f6379acebacea584d707d5a3222db1022a85a4092b52553248e48524d",
        "evaluator_blob": "25a270bc94c5306dc19b2a2e542891d3357483f9",
    },
    "G": {
        "name": "GREENFIELD",
        "commit": "83ac1126d8824dd2f1465c194be73c19ebc0cdb5",
        "wheel": GREENFIELD_WHEEL,
        "wheel_sha256": "3eb502abf74c4bb9f48fcafbbe2f271e7bba7a70152ed2d998f10c4606741252",
        "parameter": PARAMETERS_G,
        "parameter_sha256": "868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be",
        "evaluator_blob": "ac6298f85a33f0a4d09dd71f17a3a343195392b2",
    },
}
PACKET_SHA256 = "86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448"
PACKET_FILE_SHA256 = "e9d3ea9903fec9b5239dddcfe5bb8449e9f1a1aff488f0900cc9a91479ba48ba"
CSV_FIELDS = (
    "engine_label", "engine_name", "engine_commit", "wheel_sha256",
    "evaluator_blob_sha", "parameter_file_sha256", "state_packet_sha256",
    "scenario", "run_index", "state_id", "source_id", "target_identity",
    "metric", "value", "unit", "observed", "status", "failure_code",
    "diagnostic", "host_load", "timestamp_utc", "detail",
)
SUMMARY_FIELDS = (
    "engine_label", "scenario", "group", "metric", "n", "summary_value",
    "min_value", "max_value", "unit", "status", "detail",
)
TARGET_COMPONENT = "carbamate-anion"
TARGET_KIJ_IDENTITY = "pair/carbon-dioxide/water/k_ij"
OBJECTIVE_EVIDENCE = ANALYSIS / "results/reaction-temperature-fit/full-validation-targets.csv"
GREENFIELD_PRE_REBASE_EVALUATOR_BLOB = "69104fcc0fd67977f67773611eae9e9574fdb28e"
REPRESENTATIVE_STATES = (
    "Bottinger2008_state_050", "Bottinger2008_state_058",
    "vle_obs_0130", "vle_obs_0206", "vle_obs_0232",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_show(revision: str) -> bytes:
    return subprocess.run(
        ["git", "show", revision], cwd=ROOT, check=True, stdout=subprocess.PIPE
    ).stdout


def uptime() -> str:
    try:
        return subprocess.run(
            ["uptime"], check=True, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.strip()
    except Exception as exc:
        return f"uptime unavailable: {type(exc).__name__}: {exc}"


class Recorder:
    def __init__(self, path: Path, engine: str, scenario: str, run_index: int, host_load: str):
        self.path = path
        self.engine = engine
        self.scenario = scenario
        self.run_index = run_index
        self.host_load = host_load
        self.meta = ENGINE[engine]
        self.handle = path.open("a", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.handle, fieldnames=CSV_FIELDS, lineterminator="\n")

    def add(self, state_id: str, metric: str, value: object = "", status: str = "",
            *, source_id: str = "", target_identity: str = "", unit: str = "",
            observed: object = "", failure_code: str = "", diagnostic: str = "",
            detail: str = "", engine_label: str | None = None, run_index: int | None = None,
            scenario: str | None = None, wheel_sha256: str | None = None,
            engine_commit: str | None = None, evaluator_blob_sha: str | None = None,
            parameter_file_sha256: str | None = None):
        self.writer.writerow({
            "engine_label": engine_label or self.engine,
            "engine_name": self.meta["name"],
            "engine_commit": engine_commit or self.meta["commit"],
            "wheel_sha256": wheel_sha256 or self.meta["wheel_sha256"],
            "evaluator_blob_sha": evaluator_blob_sha or self.meta["evaluator_blob"],
            "parameter_file_sha256": parameter_file_sha256 or self.meta["parameter_sha256"],
            "state_packet_sha256": PACKET_SHA256,
            "scenario": scenario or self.scenario,
            "run_index": self.run_index if run_index is None else run_index,
            "state_id": state_id, "source_id": source_id,
            "target_identity": target_identity, "metric": metric, "value": value,
            "unit": unit, "observed": observed, "status": status,
            "failure_code": failure_code, "diagnostic": diagnostic,
            "host_load": self.host_load, "timestamp_utc": utc_now(), "detail": detail,
        })
        self.handle.flush()

    def close(self) -> None:
        self.handle.close()


def assert_row_shape() -> None:
    assert len(CSV_FIELDS) == len(set(CSV_FIELDS))
    assert len(SUMMARY_FIELDS) == len(set(SUMMARY_FIELDS))
    assert math.isclose(math.log(2.0), 0.6931471805599453, rel_tol=1e-14)
    assert math.isclose(abs(100.0 * abs(1.1 - 1.0)), 10.0)


def legacy_tree(scratch: Path) -> tuple[Path, Path]:
    script_dir = scratch / "historical" / "analyses/mea_parameter_bundle/scripts"
    script_dir.mkdir(parents=True, exist_ok=True)
    for name in LEGACY_FILES:
        revision = f"8f8e4a2^:analyses/mea_parameter_bundle/scripts/{name}"
        (script_dir / name).write_bytes(git_show(revision))
    parameter_path = scratch / "historical-selected-parameters.json"
    parameter_path.write_bytes(git_show(PARAMETERS_S_REV))
    if file_sha256(parameter_path) != ENGINE["S"]["parameter_sha256"]:
        raise RuntimeError("historical parameter document hash mismatch")
    return script_dir, parameter_path


def import_evaluator(engine: str, scratch: Path, cache_dir: Path):
    import importlib

    sys.path.insert(0, str(ROOT / "src"))
    if engine == "S":
        scripts, param_path = legacy_tree(scratch)
        sys.path.insert(0, str(scripts))
    else:
        scripts, param_path = SCRIPTS, PARAMETERS_G
        sys.path.insert(0, str(scripts))
    sys.modules.pop("shared_evaluation", None)
    shared = importlib.import_module("shared_evaluation")
    shared.ANALYSIS = ANALYSIS
    shared.INPUT = ANALYSIS / "data/input"
    shared.PARAMETERS = param_path
    shared.STATE_PACKET = STATE_PACKET
    shared.RUNS = cache_dir
    shared.SOURCE_CONTRACT = ROOT / "src/MEA/common/mea_source_contracts.py"
    shared.CANONICAL_SPECIATION = ROOT / "data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq.csv"
    shared.CANONICAL_VLE = ROOT / "data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv"
    if engine == "S":
        shared.ENGINE_WHEEL = HISTORICAL_WHEEL
    else:
        shared.ENGINE_WHEEL_SHA256 = ENGINE["G"]["wheel_sha256"]
        shared.ENGINE_COMMIT = ENGINE["G"]["commit"]
    if file_sha256(shared.PARAMETERS) != ENGINE[engine]["parameter_sha256"]:
        raise RuntimeError("parameter document hash mismatch")
    if file_sha256(STATE_PACKET) != PACKET_FILE_SHA256:
        raise RuntimeError("compressed state-packet hash mismatch")
    if file_sha256(ENGINE[engine]["wheel"]) != ENGINE[engine]["wheel_sha256"]:
        raise RuntimeError("Engine wheel hash mismatch")
    shared.verify_wheel()
    return shared, param_path, scripts


def load_packet(shared):
    packet = shared.load_state_packet(STATE_PACKET)
    rows = packet["observations"]
    if hashlib.sha256(shared.source_bytes(STATE_PACKET)).hexdigest() != PACKET_SHA256:
        raise RuntimeError("decompressed state-packet hash mismatch")
    return packet, rows


def parameter_object(engine: str, param_path: Path):
    import epcsaft

    if engine == "G":
        import shared_evaluation as shared
        return shared.load_parameters(param_path)
    return epcsaft.Parameters.from_json(param_path)


def model_and_reactions(engine: str, shared, param_path: Path):
    import epcsaft

    params = parameter_object(engine, param_path)
    return epcsaft.Mixture(params), shared._selected_reactions()


def record_state(rec: Recorder, observation: dict[str, object], result: dict[str, object],
                 wall_s: float, *, state_id: str | None = None):
    identity = state_id or str(observation["identity"])
    status = str(result.get("status", "exception"))
    code = str(result.get("failure_code", ""))
    diagnostic = str(result.get("failure_diagnostic", ""))
    attempts = list(result.get("attempts") or [])
    evidence = dict(result.get("evidence") or [])
    work = evidence.get("iterations/evaluations/hessian_calls") or [None, None, None]
    if len(work) < 3:
        work = [*work, *([None] * (3 - len(work)))]
    rec.add(identity, "state_status", status, status, failure_code=code, diagnostic=diagnostic)
    rec.add(identity, "state_wall_s", wall_s, status, unit="s", failure_code=code, diagnostic=diagnostic)
    rec.add(identity, "solver_attempt_wall_s", result.get("wall_s", ""), status, unit="s", failure_code=code)
    rec.add(identity, "iterations", work[0], status, failure_code=code)
    rec.add(identity, "evaluations", work[1], status, failure_code=code)
    rec.add(identity, "hessian_calls", work[2], status, failure_code=code)
    attempt_count = int(result.get("attempt_count", len(attempts)))
    rec.add(identity, "attempt_count", attempt_count, status, failure_code=code)
    rec.add(identity, "recovery_attempts", max(0, attempt_count - 1), status, failure_code=code)
    rec.add(identity, "attempt_trace", json.dumps([
        {"kind": a.get("kind"), "status": a.get("status"), "failure_code": a.get("failure_code")}
        for a in attempts
    ], separators=(",", ":")), status, failure_code=code)
    rec.add(identity, "cache_hit", result.get("cache_hit", ""), status, failure_code=code)
    prediction = dict(result.get("predictions") or {})
    targets = list(observation.get("targets") or [])
    target_by_prediction = {str(t["prediction_identity"]): t for t in targets}
    output_by_identity = {
        str(o["identity"]): o for o in observation["request"].get("outputs", [])
    }
    identities = set(prediction) | set(target_by_prediction) | set(output_by_identity)
    for output_id in sorted(identities):
        target = target_by_prediction.get(output_id, {})
        output = output_by_identity.get(output_id, {})
        value = prediction.get(output_id, "")
        output_status = status if value != "" else ("unavailable" if status == "evaluated" else status)
        rec.add(
            identity, f"prediction:{output_id}", value, output_status,
            source_id=str(target.get("source_identity", "")),
            target_identity=str(target.get("identity", output_id)),
            unit=str(target.get("unit", output.get("unit", ""))),
            observed=target.get("observed", ""), failure_code=code,
            diagnostic=diagnostic,
        )
        observed = target.get("observed")
        if output_id == "co2-partial-pressure" and value != "" and observed:
            ratio = float(value) / float(observed)
            if ratio > 0.0:
                rec.add(identity, "ln_prediction_over_observation", math.log(ratio), output_status,
                        source_id=str(target.get("source_identity", "")),
                        target_identity=str(target.get("identity", output_id)),
                        unit="ln ratio", observed=observed)
                rec.add(identity, "absolute_relative_error_pct", abs(ratio - 1.0) * 100.0,
                        output_status, source_id=str(target.get("source_identity", "")),
                        target_identity=str(target.get("identity", output_id)),
                        unit="%", observed=observed)
        elif target and value != "" and str(target.get("unit")) == "dimensionless":
            species = str(target.get("identity", output_id)).split("::")[-1]
            rec.add(identity, f"absolute_mole_fraction_error:{species}",
                    abs(float(value) - float(observed)), output_status,
                    source_id=str(target.get("source_identity", "")),
                    target_identity=str(target.get("identity", output_id)),
                    unit="mole fraction", observed=observed)


def evaluate_one(shared, model, reactions, observation, rec, *, budget_s=60.0,
                 anchors=None, state_id=None):
    start = perf_counter()
    try:
        result = shared.evaluate_state(
            model, observation["request"], reactions,
            state_id or observation["identity"], anchors or [], budget_s=budget_s,
        )
    except Exception as exc:
        result = {
            "status": "exception", "failure_code": type(exc).__name__,
            "failure_diagnostic": str(exc), "attempts": [], "predictions": {},
        }
    wall_s = perf_counter() - start
    record_state(rec, observation, result, wall_s, state_id=state_id)
    return result, wall_s


def run_cold_sweep(shared, param_path: Path, rec: Recorder):
    import epcsaft

    _, rows = load_packet(shared)
    states = [row for row in rows if row["request"]["pressure"]["role"] == "solved"]
    model, reactions = model_and_reactions(rec.engine, shared, param_path)
    started = perf_counter()
    solve_total = 0.0
    evaluated = 0
    iterations = attempts = recovery = 0
    for index, observation in enumerate(states, start=1):
        record, wall = evaluate_one(shared, model, reactions, observation, rec)
        solve_total += wall
        evaluated += record.get("status") == "evaluated"
        evidence = dict(record.get("evidence") or [])
        work = evidence.get("iterations/evaluations/hessian_calls") or [0, 0, 0]
        iterations += int(work[0] or 0)
        attempts_count = int(record.get("attempt_count", len(record.get("attempts") or [])))
        attempts += attempts_count
        recovery += max(0, attempts_count - 1)
        if index % 10 == 0 or index == len(states):
            print(f"{rec.engine} cold {index}/{len(states)}", flush=True)
    non_evaluable = len(states) - evaluated
    rec.add("79-state-cold-sweep", "state_count", len(states), "complete", unit="states")
    rec.add("79-state-cold-sweep", "evaluated_state_count", evaluated, "complete", unit="states")
    rec.add("79-state-cold-sweep", "non_evaluable_state_count", non_evaluable, "complete", unit="states")
    rec.add("79-state-cold-sweep", "total_wall_s", solve_total, "complete", unit="s")
    rec.add("79-state-cold-sweep", "median_per_state_wall_s",
            statistics.median(float(r["value"]) for r in read_numeric_rows(rec.path, rec.engine, rec.scenario, rec.run_index, "state_wall_s")),
            "complete", unit="s")
    rec.add("79-state-cold-sweep", "iterations_total", iterations, "complete", unit="iterations")
    rec.add("79-state-cold-sweep", "attempts_total", attempts, "complete", unit="attempts")
    rec.add("79-state-cold-sweep", "recovery_attempts_total", recovery, "complete", unit="attempts")
    rec.add("79-state-cold-sweep", "process_wall_s", perf_counter() - started, "complete", unit="s")
    print(f"{rec.engine} cold done {evaluated}/{len(states)} in {solve_total:.3f}s", flush=True)


def read_numeric_rows(path: Path, engine: str, scenario: str, run_index: int, metric: str):
    with path.open(newline="", encoding="utf-8") as stream:
        return [
            row for row in csv.DictReader(stream)
            if row["engine_label"] == engine and row["scenario"] == scenario
            and int(row["run_index"]) == run_index and row["metric"] == metric
            and row["value"] not in ("", "None")
        ]


def run_representative_states(shared, param_path: Path, rec: Recorder):
    _, rows = load_packet(shared)
    states = {row["identity"]: row for row in rows}
    model, reactions = model_and_reactions(rec.engine, shared, param_path)
    for identity in REPRESENTATIVE_STATES:
        observation = states[identity]
        evaluate_one(shared, model, reactions, observation, rec, state_id=identity)


def record_fit_objective_capability(engine: str, rec: Recorder):
    if engine == "S" and OBJECTIVE_EVIDENCE.is_file():
        with OBJECTIVE_EVIDENCE.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        heat = [row for row in rows if row.get("family") == "heat" and row.get("status") == "evaluated"]
        rec.add(
            "adopted-fit-objective", "fit_objective_capability", "could_evaluate",
            "retained_evidence", unit="", detail=(
                f"No timing taken. {OBJECTIVE_EVIDENCE.name} retains {len(heat)} evaluated heat rows "
                f"from the superseded wheel {ENGINE['S']['wheel_sha256']}; "
                f"file_sha256={file_sha256(OBJECTIVE_EVIDENCE)}."
            ),
        )
    else:
        rec.add(
            "adopted-fit-objective", "fit_objective_capability", "not_measurable",
            "blocked", unit="", detail=(
                "No timing taken: the adopted objective includes absorption-heat rows, "
                "and the current Greenfield path lacks the required reference-enthalpy actions (Engine #84)."
                if engine == "G" else
                "No retained full-validation target table was available to establish prior superseded capability."
            ),
        )


def find_coefficient(mapping: dict[str, object], identity: str):
    if isinstance(mapping, dict):
        if mapping.get("identity") == identity and isinstance(mapping.get("value"), dict):
            return mapping["value"]
        for value in mapping.values():
            found = find_coefficient(value, identity)
            if found is not None:
                return found
    elif isinstance(mapping, list):
        for value in mapping:
            found = find_coefficient(value, identity)
            if found is not None:
                return found
    return None


def solve_output(engine: str, shared, request: dict[str, object], param_path: Path,
                 reactions: dict[str, float], scratch: Path, *, active_identity: str | None = None,
                 start=None):
    import epcsaft
    from epcsaft import equilibrium

    corrected = shared.corrected_request(request, reactions)
    if engine == "G":
        params = shared.load_parameters(param_path)
        active = []
        if active_identity == TARGET_KIJ_IDENTITY:
            model_ids = params.component_ids
            size = len(model_ids)
            i, j = model_ids.index("carbon-dioxide"), model_ids.index("water")
            active = [epcsaft.ActiveParameter(epcsaft.ParameterFamily.Kij, (i * size + j, j * size + i))]
        model = epcsaft.Mixture(params, active_parameters=active)
        problem = shared._problem_from_request(corrected, None)
        result = equilibrium.solve_equilibrium(model, problem, start)
        if not result.success:
            raise RuntimeError(f"central solve failed: {result.solver_status} {result.message}")
        phase_index = next(
            index for index, phase in enumerate(problem.phases) if phase.kind == "liquid"
        )
        width = len(model.component_ids)
        flat = result.mole_fractions[phase_index * width:(phase_index + 1) * width]
        component_index = shared.COMPONENT_IDS.index(TARGET_COMPONENT)
        value = float(flat[component_index])
        return model, problem, result, value
    params = epcsaft.Parameters.from_json(param_path)
    model = epcsaft.Mixture(params)
    problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(corrected)
    problem = shared.prepared_problem(problem, "engine-comparison-derivative")
    active = None
    if active_identity:
        active = epcsaft.ActiveParameterSet(params, [active_identity])
    result = equilibrium.solve(model, problem, active_parameters=active)
    if result.status != "evaluated":
        raise RuntimeError(f"central solve failed: {result.status} {result.solver_status}")
    liquid = next(phase for phase in result.phases if phase.role == "liquid")
    value = float(liquid.mole_fractions[model.component_ids.index(TARGET_COMPONENT)])
    return model, problem, result, value


def finite_difference(engine: str, shared, request: dict[str, object], param_path: Path,
                      reactions: dict[str, float], scratch: Path, step: float, start=None):
    import copy

    mapping_plus = json.loads(param_path.read_text(encoding="utf-8"))
    mapping_minus = json.loads(param_path.read_text(encoding="utf-8"))
    find_coefficient(mapping_plus, TARGET_KIJ_IDENTITY)["magnitude"] += step
    find_coefficient(mapping_minus, TARGET_KIJ_IDENTITY)["magnitude"] -= step
    plus_parameter, minus_parameter = scratch / "kij-plus.json", scratch / "kij-minus.json"
    plus_parameter.write_text(json.dumps(mapping_plus), encoding="utf-8")
    minus_parameter.write_text(json.dumps(mapping_minus), encoding="utf-8")
    plus, minus = copy.deepcopy(request), copy.deepcopy(request)
    _, _, _, y_plus = solve_output(engine, shared, plus, plus_parameter, reactions, scratch, start=start)
    _, _, _, y_minus = solve_output(engine, shared, minus, minus_parameter, reactions, scratch, start=start)
    return (y_plus - y_minus) / (2.0 * step)


def finite_difference_pressure(shared, request, param_path: Path, reactions, scratch: Path,
                               step: float, start):
    import copy

    plus, minus = copy.deepcopy(request), copy.deepcopy(request)
    plus["pressure"]["value"] += step
    minus["pressure"]["value"] -= step
    _, _, _, y_plus = solve_output("G", shared, plus, param_path, reactions, scratch, start=start)
    _, _, _, y_minus = solve_output("G", shared, minus, param_path, reactions, scratch, start=start)
    return (y_plus - y_minus) / (2.0 * step)


def run_derivatives(engine: str, shared, param_path: Path, rec: Recorder, scratch: Path):
    from epcsaft import equilibrium
    import epcsaft

    _, rows = load_packet(shared)
    base = next(row for row in rows if row["identity"] == "Bottinger2008_state_050")
    request = base["request"]
    reactions = shared._selected_reactions()
    identity = base["identity"]
    started = perf_counter()
    native = {}
    if engine == "G":
        model, problem, central, _ = solve_output(
            engine, shared, request, param_path, reactions, scratch,
            active_identity=TARGET_KIJ_IDENTITY,
        )
        compiled = equilibrium.compile_problem(model, problem)
        component = model.component_ids.index(TARGET_COMPONENT)
        observable = equilibrium.SolvedStateObservable(
            equilibrium.SolvedStateObservableKind.PhaseMoleFraction, 0, component
        )
        n = len(model.component_ids)
        moves = {
            "temperature": (1.0, 0.0, [0.0] * n, [0.0]),
            "pressure": (0.0, 1.0, [0.0] * n, [0.0]),
            "kij": (0.0, 0.0, [0.0] * n, [1.0]),
        }
        for direction, move in moves.items():
            action = equilibrium.solved_state_actions(
                compiled, central,
                equilibrium.SolvedStateActionRequest(
                    [observable], [equilibrium.SolvedStateActionDirection(*move)]
                ),
            ).results[0]
            native[direction] = (
                action.status.name,
                None if action.action is None else float(action.action),
                "solved_state_actions",
            )
    else:
        params = epcsaft.Parameters.from_json(param_path)
        active = epcsaft.ActiveParameterSet(params, [TARGET_KIJ_IDENTITY])
        model = epcsaft.Mixture(params)
        problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
            shared.corrected_request(request, reactions)
        )
        problem = shared.prepared_problem(problem, "engine-comparison-derivative")
        central = equilibrium.solve(model, problem, active_parameters=active)
        if central.status != "evaluated":
            raise RuntimeError(f"central derivative solve failed: {central.status}")
        output_id = next(
            target["prediction_identity"]
            for target in base["targets"]
            if "meacoo" in target["prediction_identity"].lower()
        )
        output_row = next(row for row in central.rows if str(row.identity) == output_id)
        jacobian = list(output_row.jacobian or [])
        native["kij"] = (
            str(output_row.status), None if not jacobian else float(jacobian[0]),
            "equilibrium.solve(active_parameters=ActiveParameterSet)",
        )
        native["temperature"] = ("unavailable", None, "old solve result has no solved-state temperature direction")
        native["pressure"] = ("unavailable", None, "old solve result has no solved-state pressure direction")

    native_available = {}
    for direction in ("temperature", "pressure", "kij"):
        native_status, value, detail = native[direction]
        available = value is not None and native_status not in ("unavailable", "error")
        native_available[direction] = available
        rec.add(identity, f"derivative:{direction}:availability", native_status,
                "available" if available else "unavailable", unit="status", detail=detail)
        if value is not None:
            rec.add(identity, f"derivative:{direction}:native", value, "available",
                    unit="mole fraction per coordinate", detail=detail)
    step = 1.0e-4
    fd = None
    try:
        fd = finite_difference(engine, shared, request, param_path, reactions, scratch, step,
                               start=central if engine == "G" else None)
        rec.add(identity, "derivative:kij:finite_difference", fd, "evaluated",
                unit="mole fraction per kij", detail=f"central step={step:g}")
    except Exception as exc:
        rec.add(identity, "derivative:kij:finite_difference", "", "exception",
                failure_code=type(exc).__name__, diagnostic=f"{type(exc).__name__}: {exc}",
                unit="mole fraction per kij", detail="central difference solve failed")
    native_kij = native["kij"][1]
    rec.add(identity, "derivative:kij:relative_error",
            "" if native_kij is None or fd is None else abs(native_kij - fd) / max(abs(fd), 1e-14),
            "not_applicable" if native_kij is None or fd is None else "evaluated", unit="relative",
            detail="native-versus-central finite difference")
    if engine == "G":
        native_pressure = native["pressure"][1]
        try:
            pressure_fd = finite_difference_pressure(shared, request, param_path, reactions,
                                                     scratch, 100.0, central)
            rec.add(identity, "derivative:pressure:finite_difference", pressure_fd, "evaluated",
                    unit="mole fraction per pascal", detail="central step=100 Pa")
            rec.add(identity, "derivative:pressure:relative_error",
                    "" if native_pressure is None else abs(native_pressure - pressure_fd) / max(abs(pressure_fd), 1e-14),
                    "not_applicable" if native_pressure is None else "evaluated", unit="relative",
                    detail="native pressure action versus central finite difference")
        except Exception as exc:
            rec.add(identity, "derivative:pressure:finite_difference", "", "exception",
                    failure_code=type(exc).__name__, diagnostic=f"{type(exc).__name__}: {exc}",
                    unit="mole fraction per pascal", detail="central difference solve failed")
            rec.add(identity, "derivative:pressure:relative_error", "", "not_applicable",
                    unit="relative", detail="finite-difference pressure solve failed")

    inventory = {
        "temperature": native_available["temperature"],
        "pressure": native_available["pressure"],
        "eos_parameter": native_kij is not None,
        "reaction_coefficient": engine == "S",
        "reaction_reference_temperature": False,
    }
    evidence = {
        "temperature": native["temperature"][2],
        "pressure": native["pressure"][2],
        "eos_parameter": native["kij"][2],
        "reaction_coefficient": (
            "retained sensitivity-check.csv includes native R4/R5 coefficient sensitivities on the superseded wheel"
            if engine == "S" else "no reaction-coefficient direction in current Engine #61"
        ),
        "reaction_reference_temperature": (
            "not exposed as a native active coordinate in the superseded result path"
            if engine == "S" else "no reaction-reference temperature direction in current Engine #84"
        ),
    }
    for family, available in inventory.items():
        rec.add(identity, f"derivative_family:{family}",
                "available" if available else "unavailable",
                "available" if available else "unavailable", unit="status", detail=evidence[family])
    rec.add(identity, "derivative_measurement_wall_s", perf_counter() - started,
            "complete", unit="s", detail="central EOS kij action and finite-difference check")


def worker(engine: str, scenario: str, run_index: int, output: Path, scratch: Path):
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"
    host_load = uptime()
    rec = Recorder(output, engine, scenario, run_index, host_load)
    started = perf_counter()
    try:
        scratch.mkdir(parents=True, exist_ok=False)
        cache_dir = scratch / "state-cache"
        cache_dir.mkdir()
        shared, param_path, _ = import_evaluator(engine, scratch, cache_dir)
        if scenario == "cold_sweep":
            run_cold_sweep(shared, param_path, rec)
        elif scenario == "representative_states":
            run_representative_states(shared, param_path, rec)
        elif scenario == "derivatives":
            run_derivatives(engine, shared, param_path, rec, scratch)
        elif scenario == "fit_objective_capability":
            record_fit_objective_capability(engine, rec)
        else:
            raise ValueError(f"unknown scenario: {scenario}")
        if scenario != "fit_objective_capability":
            rec.add(scenario, "worker_process_wall_s", perf_counter() - started, "complete", unit="s")
    except Exception as exc:
        rec.add(scenario, "worker_status", "exception", "exception",
                failure_code=type(exc).__name__, diagnostic=f"{type(exc).__name__}: {exc}")
        print(f"{engine} {scenario} run {run_index} failed: {type(exc).__name__}: {exc}", flush=True)
        raise
    finally:
        rec.close()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def label_setup_failures(path: Path) -> None:
    rows = read_rows(path)
    changed = False
    for row in rows:
        if (row["metric"] == "worker_status" and row["failure_code"] == "ModuleNotFoundError"
                and "No module named 'epcsaft'" in row["diagnostic"]):
            row["value"] = row["status"] = "setup_failure"
            row["failure_code"] = "venv_interpreter_symlink_resolved_to_base"
            row["diagnostic"] += "; startup failure, no Engine calculation ran"
            row["detail"] = "setup failure; excluded from measured run medians"
            changed = True
    if changed:
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)


def trim_to_selected_scope(path: Path) -> None:
    rows = read_rows(path)
    kept = []
    for row in rows:
        if row["scenario"] == "fit_objective_capability":
            if row["metric"] == "fit_objective_capability":
                kept.append(row)
        elif row["scenario"] in ("cold_sweep", "representative_states", "derivatives"):
            kept.append(row)
        elif (row["scenario"] == "engine_pair"
              and row["metric"] == "abs_ln_greenfield_over_superseded:pco2"):
            kept.append(row)
        elif row["metric"] == "worker_status":
            kept.append(row)
    if len(kept) != len(rows):
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(kept)


def number(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def add_raw_row(path: Path, row: dict[str, object]) -> None:
    with path.open("a", newline="", encoding="utf-8") as stream:
        csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n").writerow(row)


def derive_engine_differences(path: Path) -> list[dict[str, object]]:
    raw = read_rows(path)
    predictions = defaultdict(lambda: {"S": [], "G": []})
    statuses = defaultdict(dict)
    blobs = defaultdict(set)
    loads = defaultdict(set)
    sources = {}
    for row in raw:
        engine = row["engine_label"]
        if engine not in ("S", "G") or row["scenario"] != "cold_sweep":
            continue
        run_index = int(row["run_index"])
        if run_index not in (4, 5, 6):
            continue
        blobs[engine].add(row["evaluator_blob_sha"])
        if row["host_load"]:
            loads[engine].add(row["host_load"])
        if row["metric"] == "state_status":
            statuses[(run_index, row["state_id"])][engine] = row["status"]
        if row["metric"] == "prediction:co2-partial-pressure" and row["status"] == "evaluated":
            value = number(row["value"])
            if value is not None and value > 0.0:
                predictions[row["state_id"]][engine].append(value)
                sources[row["state_id"]] = row["source_id"]
    existing = {
        (row["metric"], row["state_id"], row["run_index"])
        for row in raw if row["engine_label"] == "S_vs_G" and row["scenario"] == "engine_pair"
    }
    now = utc_now()
    pair_rows = []
    for state_id, values in sorted(predictions.items()):
        if not values["S"] or not values["G"]:
            continue
        s_value = statistics.median(values["S"])
        g_value = statistics.median(values["G"])
        log_ratio = math.log(g_value / s_value)
        metric = "abs_ln_greenfield_over_superseded:pco2"
        if (metric, state_id, "0") in existing:
            continue
        pair_rows.append({
            "engine_label": "S_vs_G", "engine_name": "SUPERSEDED_vs_GREENFIELD",
            "engine_commit": f"S:{ENGINE['S']['commit']};G:{ENGINE['G']['commit']}",
            "wheel_sha256": f"S:{ENGINE['S']['wheel_sha256']};G:{ENGINE['G']['wheel_sha256']}",
            "evaluator_blob_sha": f"S:{';'.join(sorted(blobs['S']))};G:{';'.join(sorted(blobs['G']))}",
            "parameter_file_sha256": f"S:{ENGINE['S']['parameter_sha256']};G:{ENGINE['G']['parameter_sha256']}",
            "state_packet_sha256": PACKET_SHA256, "scenario": "engine_pair",
            "run_index": 0, "state_id": state_id, "source_id": sources.get(state_id, ""),
            "target_identity": "co2-partial-pressure", "metric": metric,
            "value": abs(log_ratio), "unit": "absolute ln ratio", "observed": "",
            "status": "evaluated", "failure_code": "", "diagnostic": "",
            "host_load": f"S={' | '.join(sorted(loads['S']))}; G={' | '.join(sorted(loads['G']))}",
            "timestamp_utc": now,
            "detail": f"signed_ln_G_over_S={log_ratio:.17g};S={s_value:.17g};G={g_value:.17g}",
        })
    for (run_index, state_id), by_engine in sorted(statuses.items()):
        if (by_engine.get("S") and by_engine.get("G")
                and by_engine["S"] != by_engine["G"]
                and ("status_mismatch", state_id, str(run_index)) not in existing):
            pair_rows.append({
                "engine_label": "S_vs_G", "engine_name": "SUPERSEDED_vs_GREENFIELD",
                "engine_commit": f"S:{ENGINE['S']['commit']};G:{ENGINE['G']['commit']}",
                "wheel_sha256": f"S:{ENGINE['S']['wheel_sha256']};G:{ENGINE['G']['wheel_sha256']}",
                "evaluator_blob_sha": f"S:{';'.join(sorted(blobs['S']))};G:{';'.join(sorted(blobs['G']))}",
                "parameter_file_sha256": f"S:{ENGINE['S']['parameter_sha256']};G:{ENGINE['G']['parameter_sha256']}",
                "state_packet_sha256": PACKET_SHA256, "scenario": "engine_pair",
                "run_index": run_index, "state_id": state_id, "source_id": "",
                "target_identity": "", "metric": "status_mismatch", "value": "",
                "unit": "", "observed": "", "status": "mismatch",
                "failure_code": "", "diagnostic": "",
                "host_load": f"S={' | '.join(sorted(loads['S']))}; G={' | '.join(sorted(loads['G']))}",
                "timestamp_utc": now,
                "detail": f"S={by_engine['S']};G={by_engine['G']}",
            })
    for row in pair_rows:
        add_raw_row(path, row)
    return pair_rows


def summary_row(engine: str, scenario: str, group: str, metric: str, values: list[float],
                unit: str, detail: str = ""):
    return {
        "engine_label": engine, "scenario": scenario, "group": group,
        "metric": metric, "n": len(values),
        "summary_value": statistics.median(values) if values else "",
        "min_value": min(values) if values else "",
        "max_value": max(values) if values else "",
        "unit": unit, "status": "summarized" if values else "no_evaluable_values",
        "detail": detail,
    }


def build_summary(path: Path) -> list[dict[str, object]]:
    raw = read_rows(path)
    result = []
    scalar_groups = defaultdict(list)
    for row in raw:
        if row["engine_label"] not in ("S", "G"):
            continue
        value = number(row["value"])
        if value is None or row["status"] not in (
            "evaluated", "complete", "available", "non_evaluable"
        ):
            continue
        key = (row["engine_label"], row["scenario"], row["state_id"], row["metric"], row["unit"])
        scalar_groups[key].append(value)
    for (engine, scenario, state, metric, unit), values in sorted(scalar_groups.items()):
        result.append(summary_row(engine, scenario, state, metric, values, unit))

    accuracy = defaultdict(lambda: defaultdict(list))
    for row in raw:
        if row["scenario"] != "cold_sweep" or int(row["run_index"]) not in (4, 5, 6):
            continue
        metric = row["metric"]
        if metric not in ("ln_prediction_over_observation", "absolute_relative_error_pct"):
            continue
        if row["status"] != "evaluated":
            continue
        value = number(row["value"])
        if value is not None:
            accuracy[(row["engine_label"], row["source_id"], row["state_id"])][metric].append(value)
    grouped_accuracy = defaultdict(lambda: defaultdict(list))
    for (engine, source, _state), metrics in accuracy.items():
        for metric, values in metrics.items():
            grouped_accuracy[(engine, source)][metric].append(statistics.median(values))
    for (engine, source), metrics in sorted(grouped_accuracy.items()):
        logs = metrics["ln_prediction_over_observation"]
        aards = metrics["absolute_relative_error_pct"]
        stats = {
            "mean_ln_ratio": statistics.fmean(logs),
            "rms_ln_ratio": math.sqrt(statistics.fmean(value * value for value in logs)),
            "aard_pct": statistics.fmean(aards),
        }
        for metric, value in stats.items():
            unit = "ln ratio" if "ratio" in metric else "%"
            row = summary_row(engine, "accuracy_pco2", source, metric, [value], unit,
                              detail="computed across per-state medians from valid cold runs 4–6")
            row["n"] = len(logs)
            result.append(row)

    speciation = defaultdict(list)
    for row in raw:
        if (row["scenario"] != "representative_states"
                or not row["metric"].startswith("absolute_mole_fraction_error:")
                or row["status"] != "evaluated"):
            continue
        value = number(row["value"])
        if value is not None:
            species = row["metric"].split(":", 1)[1]
            key = (row["engine_label"], row["source_id"], species, row["target_identity"])
            speciation[key].append(value)
    spec_groups = defaultdict(list)
    for (engine, source, species, _target), values in speciation.items():
        spec_groups[(engine, source, species)].append(statistics.median(values))
    for (engine, source, species), values in sorted(spec_groups.items()):
        for metric, statistic in (
            ("mean_absolute_mole_fraction_error", statistics.fmean(values)),
            ("rms_mole_fraction_error", math.sqrt(statistics.fmean(value * value for value in values))),
        ):
            row = summary_row(engine, "accuracy_speciation", f"{source}/{species}",
                              metric, [statistic], "mole fraction",
                              detail="per-target medians across representative repeats")
            row["n"] = len(values)
            result.append(row)

    representative_status = defaultdict(list)
    for row in raw:
        if row["scenario"] == "representative_states" and row["metric"] == "state_status":
            representative_status[(row["engine_label"], row["state_id"])].append(row["status"])
    for (engine, state_id), values in sorted(representative_status.items()):
        counts = Counter(values)
        result.append({
            "engine_label": engine, "scenario": "representative_states", "group": state_id,
            "metric": "state_evaluation_status", "n": len(values), "summary_value": "",
            "min_value": "", "max_value": "", "unit": "status",
            "status": ", ".join(f"{name}:{count}" for name, count in sorted(counts.items())),
            "detail": "three alternating repeats requested",
        })

    for row in raw:
        if row["metric"] == "derivative_family:temperature" or row["metric"].startswith("derivative_family:"):
            family = row["metric"].split(":", 1)[1]
            result.append({
                "engine_label": row["engine_label"], "scenario": "derivatives", "group": family,
                "metric": "native_availability", "n": 1, "summary_value": row["value"],
                "min_value": "", "max_value": "", "unit": "status", "status": row["status"],
                "detail": row["detail"],
            })
        elif row["metric"] == "fit_objective_capability":
            result.append({
                "engine_label": row["engine_label"], "scenario": row["scenario"],
                "group": row["state_id"], "metric": row["metric"], "n": 1,
                "summary_value": row["value"], "min_value": "", "max_value": "",
                "unit": "", "status": row["status"], "detail": row["detail"],
            })

    pair = [row for row in raw if row["engine_label"] == "S_vs_G" and row["scenario"] == "engine_pair"]
    differences = [(float(row["value"]), row["state_id"]) for row in pair
                   if row["metric"] == "abs_ln_greenfield_over_superseded:pco2"
                   and number(row["value"]) is not None]
    if differences:
        worst = max(differences)
        result.append(summary_row(
            "S_vs_G", "engine_pair", "co2-partial-pressure",
            "max_abs_ln_greenfield_over_superseded", [worst[0]], "absolute ln ratio",
            detail=f"state={worst[1]}; n_common_states={len(differences)}",
        ))
    return result


def write_summary(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object, digits: int = 4) -> str:
    try:
        return f"{float(value):.{digits}g}"
    except (ValueError, TypeError):
        return "—"


def write_readme(path: Path, raw_path: Path, summary: list[dict[str, object]], command: str,
                 python_paths: dict[str, str], scratch_root: Path):
    raw = read_rows(raw_path)

    def pick(engine, scenario, group, metric):
        return next((row for row in summary if row["engine_label"] == engine
                     and row["scenario"] == scenario and row["group"] == group
                     and row["metric"] == metric), None)

    cold_runs = sorted({int(row["run_index"]) for row in raw
                        if row["scenario"] == "cold_sweep" and row["metric"] == "state_count"
                        and row["engine_label"] == "S"})
    setup_failures = sum(row["status"] == "setup_failure" for row in raw)
    start_loads = []
    for row in raw:
        if row["scenario"] != "cold_sweep" or row["metric"] != "state_count":
            continue
        try:
            start_loads.append(float(row["host_load"].split("load average:", 1)[1].split(",", 1)[0]))
        except (IndexError, ValueError):
            pass
    lines = [
        "# MEA Engine comparison",
        "",
        "This fixed-input comparison reports elapsed time, states evaluated, prediction errors, and derivative values. It does not qualify predictive use.",
        "The first controller attempt failed before any Engine calculation because Python resolved each venv symlink to the base interpreter. Those rows remain labeled `setup_failure` and are excluded from all medians.",
        "",
        "## Provenance",
        "",
        "| Engine rows | Engine commit | Wheel SHA-256 | Evaluator git blob | Parameter file SHA-256 |",
        "|---|---|---|---|---|",
        f"| S | `{ENGINE['S']['commit']}` | `{ENGINE['S']['wheel_sha256']}` | `{ENGINE['S']['evaluator_blob']}` | `{ENGINE['S']['parameter_sha256']}` |",
        f"| G cold runs 4–5 | `{ENGINE['G']['commit']}` | `{ENGINE['G']['wheel_sha256']}` | `{GREENFIELD_PRE_REBASE_EVALUATOR_BLOB}` | `{ENGINE['G']['parameter_sha256']}` |",
        f"| G cold run 6 and selected states | `{ENGINE['G']['commit']}` | `{ENGINE['G']['wheel_sha256']}` | `{ENGINE['G']['evaluator_blob']}` | `{ENGINE['G']['parameter_sha256']}` |",
        "",
        f"- The Greenfield evaluator’s only difference across those rows is its stored pin constants; the producer set the wheel SHA and Engine commit in memory to `{ENGINE['G']['wheel_sha256']}` and `{ENGINE['G']['commit']}` for every G run.",
        f"- State packet JSON SHA-256: `{PACKET_SHA256}`; compressed file SHA-256: `{PACKET_FILE_SHA256}`.",
        "- The old parameter file is from `8f8e4a2^` and matches the adopted current file on all 110 common coefficients. It retains seven same-sign ion-pair `kij=1` entries that the current file omits while explicitly excluding same-sign pairs; this preserves the fitted model’s exclusion rule.",
        "- Python 3.13.14; each scratch venv used `uv sync --locked --group test`. The superseded wheel also needed Pint 0.26.1. Both venvs and every evaluator cache were under `/tmp`.",
        "- Each run used `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`. Workers ran sequentially. The raw `uptime` text is retained in `host_load` on every measurement row.",
        "- Each Engine/run used a new empty state cache. Valid cold runs were `S4,G4,S5,G5,S6,G6`; representative-state runs alternate S and G three times per state.",
        f"- Valid cold run indices retained: `{','.join(map(str, cold_runs))}`. Setup-failure rows retained: `{setup_failures}`.",
        "",
        "## Summary",
        "",
        "### 79-state solved-pressure replay",
        "",
        "Medians use only valid cold run indices 4–6. Non-evaluable states count as failures; their attempt and solver diagnostics remain in `measurements.csv`.",
        "",
        "| Engine | Median total wall (s) | Median per-state median (s) | Evaluated states / 79 | Non-evaluable / 79 | Median recovery attempts | S/G wall ratio |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    totals = {}
    for label in ("S", "G"):
        total = pick(label, "cold_sweep", "79-state-cold-sweep", "total_wall_s")
        per = pick(label, "cold_sweep", "79-state-cold-sweep", "median_per_state_wall_s")
        ok = pick(label, "cold_sweep", "79-state-cold-sweep", "evaluated_state_count")
        bad = pick(label, "cold_sweep", "79-state-cold-sweep", "non_evaluable_state_count")
        recovery = pick(label, "cold_sweep", "79-state-cold-sweep", "recovery_attempts_total")
        totals[label] = number(str(total["summary_value"])) if total else None
        ratio = (totals.get("S") / totals.get("G") if label == "G" and totals.get("G") else None)
        lines.append(
            f"| {label} | {fmt(total and total['summary_value'])} | {fmt(per and per['summary_value'])} | "
            f"{fmt(ok and ok['summary_value'], 3)}/79 | {fmt(bad and bad['summary_value'], 3)}/79 | "
            f"{fmt(recovery and recovery['summary_value'], 4)} | {fmt(ratio) if label == 'G' else '—'} |"
        )
    lines.extend([
        "",
        "### pCO₂ accuracy by source",
        "",
        "The table uses per-state median predictions from valid cold runs. Mean and RMS are over `ln(predicted/observed)`; AARD is `100 × mean(|predicted/observed − 1|)`.",
        "",
        "| Engine | Source | Evaluated states | Mean ln ratio | RMS ln ratio | AARD (%) |",
        "|---|---|---:|---:|---:|---:|",
    ])
    sources = sorted({row["group"] for row in summary if row["scenario"] == "accuracy_pco2"})
    for label in ("S", "G"):
        for source in sources:
            mean = pick(label, "accuracy_pco2", source, "mean_ln_ratio")
            rms = pick(label, "accuracy_pco2", source, "rms_ln_ratio")
            aard = pick(label, "accuracy_pco2", source, "aard_pct")
            n = mean["n"] if mean else 0
            lines.append(f"| {label} | {source} | {n} | {fmt(mean and mean['summary_value'])} | "
                         f"{fmt(rms and rms['summary_value'])} | {fmt(aard and aard['summary_value'])} |")
    paired = pick("S_vs_G", "engine_pair", "co2-partial-pressure", "max_abs_ln_greenfield_over_superseded")
    lines.extend([
        "",
        f"Maximum paired `|ln(G/S)|` for pCO₂: **{fmt(paired and paired['summary_value'])}** "
        f"on `{paired['detail'].split(';')[0].removeprefix('state=') if paired else '—'}` "
        f"across {paired['detail'].split('n_common_states=')[-1] if paired else '0'} commonly evaluated states.",
        "",
        "### Representative states",
        "",
        "Three alternating repeats each: Böttinger 050 and 058 at fixed pressure; VLE 0130, 0206, and 0232 at 40, 80, and 120 °C.",
        "",
        "| State | Engine | Evaluated status counts | Median wall (s) | Median iterations |",
        "|---|---|---|---:|---:|",
    ])
    for state_id in REPRESENTATIVE_STATES:
        for label in ("S", "G"):
            status = pick(label, "representative_states", state_id, "state_evaluation_status")
            wall = pick(label, "representative_states", state_id, "state_wall_s")
            iterations = pick(label, "representative_states", state_id, "iterations")
            lines.append(f"| {state_id} | {label} | {status and status['status'] or 'missing'} | "
                         f"{fmt(wall and wall['summary_value'])} | {fmt(iterations and iterations['summary_value'], 3)} |")
    spec = [row for row in summary if row["scenario"] == "accuracy_speciation"]
    if spec:
        lines.extend(["", "Absolute mole-fraction errors for measured species on the two fixed-pressure states:", "",
                      "| Engine | Source / species | Mean absolute error | RMS error |",
                      "|---|---|---:|---:|"])
        groups = sorted({row["group"] for row in spec})
        for label in ("S", "G"):
            for group in groups:
                mean = pick(label, "accuracy_speciation", group, "mean_absolute_mole_fraction_error")
                rms = pick(label, "accuracy_speciation", group, "rms_mole_fraction_error")
                lines.append(f"| {label} | {group} | {fmt(mean and mean['summary_value'])} | {fmt(rms and rms['summary_value'])} |")
    lines.extend([
        "",
        "### Derivatives",
        "",
        "| Derivative family | S | G |",
        "|---|---|---|",
    ])
    for family in ("temperature", "pressure", "eos_parameter", "reaction_coefficient", "reaction_reference_temperature"):
        old = pick("S", "derivatives", family, "native_availability")
        new = pick("G", "derivatives", family, "native_availability")
        lines.append(f"| {family.replace('_', ' ')} | {old and old['summary_value'] or 'not measured'} | {new and new['summary_value'] or 'not measured'} |")
    for title, metric in (("Native CO₂–H₂O kij action", "derivative:kij:native"),
                          ("Central finite difference", "derivative:kij:finite_difference"),
                          ("Relative error", "derivative:kij:relative_error")):
        lines.append("")
        lines.append(f"{title} on `Bottinger2008_state_050`:")
        lines.append("")
        lines.append("| Engine | Value |")
        lines.append("|---|---:|")
        for label in ("S", "G"):
            row = pick(label, "derivatives", "Bottinger2008_state_050", metric)
            lines.append(f"| {label} | {fmt(row and row['summary_value'])} |")
    lines.extend([
        "",
        "The G CO₂–H₂O kij action returned `ReferenceUnavailable` on this source-reference MEA problem, so it has no native-versus-finite-difference error. The old Engine’s kij action was available and its finite-difference relative error is shown above.",
        "",
        "Greenfield pressure direction on the same state:",
        "",
        "| Engine | Native pressure derivative | Central finite difference | Relative error |",
        "|---|---:|---:|---:|",
    ])
    for label in ("S", "G"):
        native = pick(label, "derivatives", "Bottinger2008_state_050", "derivative:pressure:native")
        fd = pick(label, "derivatives", "Bottinger2008_state_050", "derivative:pressure:finite_difference")
        error = pick(label, "derivatives", "Bottinger2008_state_050", "derivative:pressure:relative_error")
        lines.append(f"| {label} | {fmt(native and native['summary_value'])} | "
                     f"{fmt(fd and fd['summary_value'])} | {fmt(error and error['summary_value'])} |")
    lines.extend([
        "",
        "On this MEA source-reference problem, Greenfield reported temperature and EOS-parameter directions as `ReferenceUnavailable` and pressure as available. Reaction-coefficient actions remain unavailable under Engine #61; reaction-reference temperature derivatives remain unavailable under Engine #84. The superseded wheel has native R4/R5 coefficient sensitivity evidence in the retained `sensitivity-check.csv`.",
        "",
        "### Adopted fit objective",
        "",
        "No new objective timing was taken. The superseded side could evaluate the pressure/speciation/heat target families: retained `full-validation-targets.csv` contains evaluated heat rows for the 40fba7cf wheel. This is prior capability evidence, not a timing for this comparison. Greenfield is recorded as not measurable because its adopted objective includes absorption-heat rows blocked by Engine #84.",
        "",
        "## Reproduction and limits",
        "",
        "Worker Python paths: " + ", ".join(f"`{label}={python_paths[label]}`" for label in ("S", "G")) + ".",
        "",
        "```bash",
        command,
        "```",
        "",
        f"Scratch root: `{scratch_root}`. The long-format measurements are in `measurements.csv`; medians and aggregate statistics are in `summary.csv`.",
        "- The setup failures came from resolving the venv `bin/python` symlink before launching workers; the corrected commands preserve the venv path.",
        "- Superseded runs 4–6 had numerical-convergence failures; those states were excluded only from prediction accuracy and evaluated-state counts. All per-attempt outcomes remain in the long-format table.",
        f"- Cold-run start load averages (1 min) ranged from {fmt(min(start_loads)) if start_loads else '—'} to {fmt(max(start_loads)) if start_loads else '—'}. Result timings vary with the host load snapshots retained in `host_load`; only three valid alternating cold pairs were requested.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--append", action="store_true",
                        help="retain existing rows while adding selected states")
    parser.add_argument("--selected-only", action="store_true",
                        help="run representative states and derivative/evaluability checks")
    parser.add_argument("--finalize-only", action="store_true",
                        help="rebuild pair rows, summary.csv and README.md without Engine runs")
    parser.add_argument("--engine", choices=("S", "G"))
    parser.add_argument("--scenario", choices=("cold_sweep", "representative_states", "derivatives", "fit_objective_capability"))
    parser.add_argument("--run-index", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--scratch", type=Path)
    parser.add_argument("--superseded-python", type=Path, default=Path("/tmp/mea-engine-comparison-20260923/superseded-venv/bin/python"))
    parser.add_argument("--greenfield-python", type=Path, default=Path("/tmp/mea-engine-comparison-20260923/greenfield-venv/bin/python"))
    args = parser.parse_args()
    if args.self_check:
        assert_row_shape()
        print("comparison producer self-check passed")
        return
    if args.worker:
        if not all((args.engine, args.scenario, args.output, args.scratch)):
            parser.error("--worker requires --engine, --scenario, --output and --scratch")
        worker(args.engine, args.scenario, args.run_index, args.output, args.scratch)
        return
    measurements = OUTPUT / "measurements.csv"
    if args.finalize_only:
        if not measurements.is_file():
            parser.error(f"cannot finalize without {measurements}")
        for label, py in (("S", args.superseded_python), ("G", args.greenfield_python)):
            if not py.is_file():
                parser.error(f"{label} Python environment is missing: {py}")
        python_paths = {"S": str(args.superseded_python.absolute()), "G": str(args.greenfield_python.absolute())}
        trim_to_selected_scope(measurements)
        label_setup_failures(measurements)
        derive_engine_differences(measurements)
        summary = build_summary(measurements)
        write_summary(OUTPUT / "summary.csv", summary)
        fresh_command = (
            f"python3.13 {SCRIPTS.relative_to(ROOT) / 'compare_engines.py'} "
            f"--superseded-python {python_paths['S']} --greenfield-python {python_paths['G']}"
        )
        write_readme(OUTPUT / "README.md", measurements, summary, fresh_command, python_paths, Path("/tmp"))
        print(f"results: {OUTPUT}", flush=True)
        return
    if args.selected_only and not args.append:
        parser.error("--selected-only requires --append to preserve existing rows")
    if args.append and not args.selected_only:
        parser.error("--append is reserved for --selected-only")
    if args.append:
        if not measurements.is_file():
            parser.error(f"cannot append without {measurements}")
        if not args.selected_only:
            parser.error("--append requires --selected-only")
        trim_to_selected_scope(measurements)
        label_setup_failures(measurements)
        existing = read_rows(measurements)
    else:
        if OUTPUT.exists():
            parser.error(f"result directory already exists; refusing to overwrite: {OUTPUT}")
        OUTPUT.mkdir(parents=True)
        with measurements.open("w", newline="", encoding="utf-8") as stream:
            csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n").writeheader()
        existing = []
    for label, py in (("S", args.superseded_python), ("G", args.greenfield_python)):
        if not py.is_file():
            parser.error(f"{label} Python environment is missing: {py}")
    scratch_root = Path(tempfile.mkdtemp(prefix="mea-engine-comparison-", dir="/tmp"))
    python_paths = {"S": str(args.superseded_python.absolute()), "G": str(args.greenfield_python.absolute())}
    plan = []
    cold_start = max(
        (int(row["run_index"]) for row in existing if row["scenario"] == "cold_sweep"),
        default=0,
    ) + 1
    if not args.selected_only:
        for run_index in range(cold_start, cold_start + 3):
            plan.extend((("S", "cold_sweep", run_index), ("G", "cold_sweep", run_index)))
    representative_start = max(
        (int(row["run_index"]) for row in existing if row["scenario"] == "representative_states"),
        default=0,
    ) + 1
    for run_index in range(representative_start, representative_start + 3):
        plan.extend((("S", "representative_states", run_index), ("G", "representative_states", run_index)))
    for engine in ("S", "G"):
        derivative_complete = any(
            row["engine_label"] == engine and row["scenario"] == "derivatives"
            and row["metric"] == "derivative_family:eos_parameter"
            and row["value"] == "available"
            for row in existing
        )
        if not derivative_complete:
            derivative_run = max(
                (int(row["run_index"]) for row in existing
                 if row["scenario"] == "derivatives" and row["engine_label"] == engine),
                default=0,
            ) + 1
            plan.append((engine, "derivatives", derivative_run))
    objective_run = max(
        (int(row["run_index"]) for row in existing if row["scenario"] == "fit_objective_capability"),
        default=0,
    ) + 1
    plan.extend((("S", "fit_objective_capability", objective_run), ("G", "fit_objective_capability", objective_run)))
    for engine, scenario, run_index in plan:
        scratch = scratch_root / f"{engine}-{scenario}-{run_index}"
        cmd = [
            python_paths[engine], str(Path(__file__).absolute()), "--worker",
            "--engine", engine, "--scenario", scenario, "--run-index", str(run_index),
            "--output", str(measurements), "--scratch", str(scratch),
        ]
        env = os.environ.copy()
        env.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
        print(f"starting {engine} {scenario} run {run_index}: {cmd[0]}", flush=True)
        completed = subprocess.run(cmd, cwd=ROOT, env=env)
        if completed.returncode:
            print(f"worker exited {completed.returncode}: {engine} {scenario} run {run_index}", flush=True)
    trim_to_selected_scope(measurements)
    label_setup_failures(measurements)
    derive_engine_differences(measurements)
    summary = build_summary(measurements)
    write_summary(OUTPUT / "summary.csv", summary)
    fresh_command = (
        f"python3.13 {SCRIPTS.relative_to(ROOT) / 'compare_engines.py'} "
        f"--superseded-python {python_paths['S']} --greenfield-python {python_paths['G']}"
    )
    write_readme(OUTPUT / "README.md", measurements, summary, fresh_command, python_paths, scratch_root)
    print(f"results: {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
