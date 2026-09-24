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
HISTORICAL_WHEEL = ANALYSIS / "data/input/engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl"
GREENFIELD_3EB_SHA256 = "3eb502abf74c4bb9f48fcafbbe2f271e7bba7a70152ed2d998f10c4606741252"
GREENFIELD_3EB_COMMIT = "83ac1126d8824dd2f1465c194be73c19ebc0cdb5"
GREENFIELD_B66_SHA256 = "b66c7b962541a586f5ec50043a5e8b4e62cf52e24eaec02ef33f43e558762a58"
GREENFIELD_B66_COMMIT = "443a9da492fd5ac7724525945d108c6a2a854d51"
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
        "commit": GREENFIELD_3EB_COMMIT,
        "wheel": None,
        "wheel_sha256": GREENFIELD_3EB_SHA256,
        "parameter": PARAMETERS_G,
        "parameter_sha256": "868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be",
        "evaluator_blob": None,
    },
}


def configure_greenfield(wheel: Path, scenario: str) -> None:
    digest = file_sha256(wheel)
    if scenario == "addendum":
        if digest != GREENFIELD_B66_SHA256:
            raise ValueError(f"addendum requires b66 wheel {GREENFIELD_B66_SHA256}; got {digest}")
        ENGINE["G"].update(
            wheel=wheel, commit=GREENFIELD_B66_COMMIT, wheel_sha256=GREENFIELD_B66_SHA256,
            evaluator_blob=evaluator_blob(),
        )
    else:
        if digest != GREENFIELD_3EB_SHA256:
            raise ValueError(f"standard greenfield runs require wheel {GREENFIELD_3EB_SHA256}; got {digest}")
        ENGINE["G"].update(
            wheel=wheel, commit=GREENFIELD_3EB_COMMIT, wheel_sha256=GREENFIELD_3EB_SHA256,
            evaluator_blob=evaluator_blob(),
        )
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


def evaluator_blob() -> str:
    """Git blob hash of the shared_evaluation.py this checkout imports for G."""
    return subprocess.run(["git", "hash-object", str(SCRIPTS / "shared_evaluation.py")],
                          check=True, capture_output=True, text=True).stdout.strip()


def valid_cold_runs(rows: list[dict[str, str]]) -> tuple[int, ...]:
    """Cold-sweep run indices whose workers started (setup_failure runs excluded)."""
    cold = {int(r["run_index"]) for r in rows if r["scenario"] == "cold_sweep"}
    failed = {int(r["run_index"]) for r in rows if r["scenario"] == "cold_sweep" and r["status"] == "setup_failure"}
    return tuple(sorted(cold - failed))


VALID_RUNS: tuple[int, ...] = ()


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


def legacy_tree(scratch: Path) -> tuple[Path, Path]:
    script_dir = scratch / "historical" / "analyses/mea_parameter_bundle/scripts"
    script_dir.mkdir(parents=True, exist_ok=True)
    (script_dir / "shared_evaluation.py").write_bytes(git_show(EVALUATOR_S_REV))
    parameter_path = scratch / "historical-selected-parameters.json"
    parameter_path.write_bytes(git_show(PARAMETERS_S_REV))
    if file_sha256(parameter_path) != ENGINE["S"]["parameter_sha256"]:
        raise RuntimeError("historical parameter document hash mismatch")
    return script_dir, parameter_path


def import_evaluator(engine: str, scratch: Path, cache_dir: Path):
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
                 wall_s: float, *, state_id: str | None = None, record_timing: bool = True):
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
    if record_timing:
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
                 anchors=None, state_id=None, record_timing=True):
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
    record_state(rec, observation, result, wall_s, state_id=state_id,
                 record_timing=record_timing)
    return result, wall_s


def run_cold_sweep(shared, param_path: Path, rec: Recorder):
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


def run_representative_states(shared, param_path: Path, rec: Recorder, *, record_timing=True):
    _, rows = load_packet(shared)
    states = {row["identity"]: row for row in rows}
    model, reactions = model_and_reactions(rec.engine, shared, param_path)
    for identity in REPRESENTATIVE_STATES:
        observation = states[identity]
        evaluate_one(shared, model, reactions, observation, rec, state_id=identity,
                     record_timing=record_timing)


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
        b66 = engine == "G" and ENGINE["G"]["wheel_sha256"] == GREENFIELD_B66_SHA256
        greenfield_reason = (
            "No timing taken: the adopted objective includes absorption-heat rows, but the MEA heat scripts have not been rebuilt on Engine #84 reference-temperature actions and #138 record-anchored calorics."
            if b66 else
            "No timing taken on wheel 3eb502ab: the adopted objective includes absorption-heat rows requiring reference-enthalpy actions unavailable on that wheel (Engine #84)."
        )
        rec.add(
            "adopted-fit-objective", "fit_objective_capability",
            "not_measured" if b66 else "not_measurable",
            "not_measured" if b66 else "blocked", unit="", detail=(
                greenfield_reason if engine == "G" else
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
                 reactions: dict[str, float], *, active_identity: str | None = None,
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
    _, _, _, y_plus = solve_output(engine, shared, plus, plus_parameter, reactions, start=start)
    _, _, _, y_minus = solve_output(engine, shared, minus, minus_parameter, reactions, start=start)
    return (y_plus - y_minus) / (2.0 * step)


def finite_difference_pressure(shared, request, param_path: Path, reactions, step: float, start):
    import copy

    plus, minus = copy.deepcopy(request), copy.deepcopy(request)
    plus["pressure"]["value"] += step
    minus["pressure"]["value"] -= step
    _, _, _, y_plus = solve_output("G", shared, plus, param_path, reactions, start=start)
    _, _, _, y_minus = solve_output("G", shared, minus, param_path, reactions, start=start)
    return (y_plus - y_minus) / (2.0 * step)


def finite_difference_temperature(shared, request, param_path: Path, reactions, step: float, start):
    import copy

    plus, minus = copy.deepcopy(request), copy.deepcopy(request)
    plus["temperature"]["value"] += step
    minus["temperature"]["value"] -= step
    _, _, _, y_plus = solve_output("G", shared, plus, param_path, reactions, start=start)
    _, _, _, y_minus = solve_output("G", shared, minus, param_path, reactions, start=start)
    return (y_plus - y_minus) / (2.0 * step)


def run_derivatives(engine: str, shared, param_path: Path, rec: Recorder,
                    scratch: Path, *, record_timing: bool = True):
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
            engine, shared, request, param_path, reactions,
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
                action.unit,
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
            "mole fraction per kij",
        )
        native["temperature"] = ("unavailable", None, "no native solved-state temperature direction")
        native["pressure"] = ("unavailable", None, "no native solved-state pressure direction")

    for direction in ("temperature", "pressure", "kij"):
        native_status, value, detail = native[direction]
        available = value is not None and native_status not in (
            "unavailable", "error", "ReferenceUnavailable"
        )
        rec.add(
            identity, f"derivative:{direction}:availability", native_status,
            "available" if available else "unavailable", unit="status", detail=detail,
        )
        if value is not None:
            rec.add(identity, f"derivative:{direction}:native", value, "available",
                    unit=detail if engine == "S" else native[direction][2], detail=detail)

    finite_differences = {}
    if engine == "G":
        for direction, step, calculate in (
            ("temperature", 0.02, finite_difference_temperature),
            ("pressure", 100.0, finite_difference_pressure),
        ):
            try:
                if direction == "temperature":
                    value = calculate(shared, request, param_path, reactions, step, central)
                    unit = "mole fraction per kelvin"
                else:
                    value = calculate(shared, request, param_path, reactions, step, central)
                    unit = "mole fraction per pascal"
                finite_differences[direction] = value
                rec.add(identity, f"derivative:{direction}:finite_difference", value,
                        "evaluated", unit=unit, detail=f"central step={step:g}")
            except Exception as exc:
                rec.add(identity, f"derivative:{direction}:finite_difference", "",
                        "exception", failure_code=type(exc).__name__,
                        diagnostic=f"{type(exc).__name__}: {exc}", unit="",
                        detail="central difference solve failed")
    try:
        kij_fd = finite_difference(
            engine, shared, request, param_path, reactions, scratch, 1.0e-4,
            start=central if engine == "G" else None,
        )
        finite_differences["kij"] = kij_fd
        rec.add(identity, "derivative:kij:finite_difference", kij_fd, "evaluated",
                unit="mole fraction per kij", detail="central step=0.0001")
    except Exception as exc:
        rec.add(identity, "derivative:kij:finite_difference", "", "exception",
                failure_code=type(exc).__name__, diagnostic=f"{type(exc).__name__}: {exc}",
                unit="mole fraction per kij", detail="central difference solve failed")

    for direction, fd in finite_differences.items():
        native_value = native[direction][1]
        relative_error = (
            "" if native_value is None else
            abs(native_value - fd) / max(abs(fd), 1.0e-14)
        )
        rec.add(
            identity, f"derivative:{direction}:relative_error", relative_error,
            "evaluated" if native_value is not None else "not_applicable",
            unit="relative",
            detail="native-versus-central finite difference" if native_value is not None
            else "native action unavailable; no relative error",
        )

    kij_available = native["kij"][1] is not None and native["kij"][0] not in (
        "unavailable", "error", "ReferenceUnavailable"
    )
    inventory = {
        "temperature": native["temperature"][1] is not None and native["temperature"][0] == "Available",
        "pressure": native["pressure"][1] is not None and native["pressure"][0] == "Available",
        "eos_parameter": kij_available,
        "reaction_coefficient": engine == "S",
    }
    evidence = {
        "temperature": native["temperature"][2],
        "pressure": native["pressure"][2],
        "eos_parameter": native["kij"][2],
        "reaction_coefficient": (
            "retained sensitivity-check.csv includes native R4/R5 coefficient sensitivities on the superseded wheel"
            if engine == "S" else "reaction-coefficient directions unavailable under Engine #61"
        ),
    }
    for family, available in inventory.items():
        rec.add(identity, f"derivative_family:{family}",
                "available" if available else "unavailable",
                "available" if available else "unavailable", unit="status",
                detail=evidence[family])
    if engine == "G":
        reference_temperature_available = (
            ENGINE["G"]["wheel_sha256"] == GREENFIELD_B66_SHA256
            and native["temperature"][0] == "Available"
            and native["temperature"][1] is not None
        )
        rec.add(
            identity, "derivative_family:reaction_reference_temperature",
            "available" if reference_temperature_available else "unavailable",
            "available" if reference_temperature_available else "unavailable",
            unit="status",
            detail=(
                "Engine #84 R1-R5 reference-temperature chain is included in the available source-referenced temperature action"
                if reference_temperature_available else
                "no separate reaction reference-temperature action is exposed by this wheel"
            ),
        )
    if record_timing:
        rec.add(identity, "derivative_measurement_wall_s", perf_counter() - started,
                "complete", unit="s", detail="derivative actions and finite-difference checks")


def record_addendum_value_differences(
    output: Path, rec: Recorder, run_index: int
) -> None:
    raw = read_rows(output)
    previous = defaultdict(list)
    current = []
    for row in raw:
        if (row["engine_label"] == "G" and row["wheel_sha256"] == GREENFIELD_3EB_SHA256
                and row["scenario"] == "representative_states"
                and row["metric"].startswith("prediction:") and row["status"] == "evaluated"):
            value = number(row["value"])
            if value is not None:
                previous[(row["state_id"], row["metric"])].append(value)
        if (row["engine_label"] == "G" and row["wheel_sha256"] == GREENFIELD_B66_SHA256
                and row["scenario"] == "addendum_value_check"
                and int(row["run_index"]) == run_index and row["metric"].startswith("prediction:")
                and row["status"] == "evaluated"):
            current.append(row)

    differences = []
    for row in current:
        key = row["state_id"], row["metric"]
        if not previous[key]:
            rec.add(row["state_id"], f"relative_difference_vs_3eb502ab:{row['metric'].removeprefix('prediction:')}",
                    "", "not_comparable", source_id=row["source_id"],
                    target_identity=row["target_identity"], unit="relative",
                    diagnostic="no evaluated 3eb502ab prediction for this state/output")
            continue
        old_value = statistics.median(previous[key])
        new_value = float(row["value"])
        difference = abs(new_value - old_value) / max(abs(old_value), 1e-300)
        differences.append((difference, row, old_value))
        rec.add(
            row["state_id"], f"relative_difference_vs_3eb502ab:{row['metric'].removeprefix('prediction:')}",
            difference, "evaluated", source_id=row["source_id"],
            target_identity=row["target_identity"], unit="relative", observed=old_value,
            detail="one cache-cold b66 pass versus median of retained 3eb502ab repeats; no timing comparison",
        )
    if differences:
        difference, row, old_value = max(differences, key=lambda item: item[0])
        rec.add(
            row["state_id"], "max_relative_difference_vs_3eb502ab", difference, "evaluated",
            source_id=row["source_id"], target_identity=row["metric"],
            unit="relative", observed=old_value,
            detail=f"maximum over {len(differences)} matched output predictions",
        )


def run_addendum(output: Path, run_index: int, scratch: Path) -> None:
    state_scratch = scratch / "state-value-check"
    state_cache = state_scratch / "state-cache"
    state_cache.mkdir(parents=True)
    shared, param_path, _ = import_evaluator("G", state_scratch, state_cache)
    state_rec = Recorder(output, "G", "addendum_value_check", run_index, uptime())
    try:
        run_representative_states(shared, param_path, state_rec, record_timing=False)
        record_addendum_value_differences(output, state_rec, run_index)
    finally:
        state_rec.close()

    derivative_scratch = scratch / "derivative-check"
    derivative_cache = derivative_scratch / "state-cache"
    derivative_cache.mkdir(parents=True)
    shared, param_path, _ = import_evaluator("G", derivative_scratch, derivative_cache)
    derivative_rec = Recorder(output, "G", "addendum_derivatives", run_index, uptime())
    try:
        run_derivatives("G", shared, param_path, derivative_rec, derivative_scratch,
                       record_timing=False)
    finally:
        derivative_rec.close()

    objective_rec = Recorder(output, "G", "addendum_fit_objective", run_index, uptime())
    try:
        record_fit_objective_capability("G", objective_rec)
    finally:
        objective_rec.close()


def worker(engine: str, scenario: str, run_index: int, output: Path, scratch: Path):
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"
    scratch.mkdir(parents=True, exist_ok=False)
    if scenario == "addendum":
        try:
            run_addendum(output, run_index, scratch)
        except Exception as exc:
            rec = Recorder(output, "G", "addendum", run_index, uptime())
            try:
                rec.add("addendum", "worker_status", "exception", "exception",
                        failure_code=type(exc).__name__, diagnostic=f"{type(exc).__name__}: {exc}")
            finally:
                rec.close()
            print(f"G addendum run {run_index} failed: {type(exc).__name__}: {exc}", flush=True)
            raise
        return

    host_load = uptime()
    rec = Recorder(output, engine, scenario, run_index, host_load)
    started = perf_counter()
    try:
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


def number(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def add_raw_row(path: Path, row: dict[str, object]) -> None:
    with path.open("a", newline="", encoding="utf-8") as stream:
        csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n").writerow(row)


def derive_engine_differences(path: Path) -> list[dict[str, object]]:
    global VALID_RUNS
    VALID_RUNS = valid_cold_runs(read_rows(path))
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
        if run_index not in VALID_RUNS:
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
    global VALID_RUNS
    VALID_RUNS = valid_cold_runs(read_rows(path))
    raw = read_rows(path)
    result = []

    scalar_groups = defaultdict(list)
    for row in raw:
        if row["engine_label"] not in ("S", "G"):
            continue
        value = number(row["value"])
        if value is not None and row["status"] in (
            "evaluated", "complete", "available", "non_evaluable"
        ):
            key = (row["engine_label"], row["scenario"], row["state_id"], row["metric"], row["unit"])
            scalar_groups[key].append(value)
    for (engine, scenario, state, metric, unit), values in sorted(scalar_groups.items()):
        result.append(summary_row(engine, scenario, state, metric, values, unit))

    accuracy = defaultdict(lambda: defaultdict(list))
    for row in raw:
        if row["scenario"] != "cold_sweep" or int(row["run_index"]) not in VALID_RUNS:
            continue
        if row["metric"] not in ("ln_prediction_over_observation", "absolute_relative_error_pct"):
            continue
        if row["status"] == "evaluated" and (value := number(row["value"])) is not None:
            accuracy[(row["engine_label"], row["source_id"], row["state_id"])][row["metric"]].append(value)
    state_accuracy = {
        key: {metric: statistics.median(values) for metric, values in metrics.items()}
        for key, metrics in accuracy.items()
    }
    engine_states = {
        engine: {state for (label, _source, state) in state_accuracy if label == engine}
        for engine in ("S", "G")
    }
    shared_states = engine_states["S"] & engine_states["G"]

    def add_accuracy_summary(scenario: str, selected_states: set[str] | None) -> None:
        grouped = defaultdict(lambda: defaultdict(list))
        for (engine, source, state), metrics in state_accuracy.items():
            if selected_states is not None and state not in selected_states:
                continue
            for metric, value in metrics.items():
                grouped[(engine, source)][metric].append(value)
        for (engine, source), metrics in sorted(grouped.items()):
            logs = metrics["ln_prediction_over_observation"]
            aards = metrics["absolute_relative_error_pct"]
            values = {
                "mean_ln_ratio": statistics.fmean(logs),
                "rms_ln_ratio": math.sqrt(statistics.fmean(value * value for value in logs)),
                "aard_pct": statistics.fmean(aards),
            }
            for metric, value in values.items():
                row = summary_row(
                    engine, scenario, source, metric, [value],
                    "ln ratio" if "ratio" in metric else "%",
                    detail=(
                        f"per-state medians across valid cold runs {VALID_RUNS[0]}–{VALID_RUNS[-1]}"
                        if selected_states is None else
                        f"per-state medians restricted to {len(selected_states)} states evaluated by both Engines"
                    ),
                )
                row["n"] = len(logs)
                result.append(row)

    add_accuracy_summary("accuracy_pco2", None)
    add_accuracy_summary("accuracy_pco2_shared_66", shared_states)

    speciation = defaultdict(list)
    for row in raw:
        if (row["scenario"] != "representative_states"
                or not row["metric"].startswith("absolute_mole_fraction_error:")
                or row["status"] != "evaluated"):
            continue
        if (value := number(row["value"])) is not None:
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

    derivative_families = {}
    for row in raw:
        if not row["metric"].startswith("derivative_family:"):
            continue
        family = row["metric"].split(":", 1)[1]
        if family == "reaction_reference_temperature":
            continue
        derivative_families[(row["engine_label"], row["scenario"], family)] = row
    for (engine, scenario, family), row in sorted(derivative_families.items()):
        result.append({
            "engine_label": engine, "scenario": scenario, "group": family,
            "metric": "native_availability", "n": 1, "summary_value": row["value"],
            "min_value": "", "max_value": "", "unit": "status", "status": row["status"],
            "detail": row["detail"],
        })

    for row in raw:
        if row["metric"] == "fit_objective_capability":
            result.append({
                "engine_label": row["engine_label"], "scenario": row["scenario"],
                "group": row["state_id"], "metric": row["metric"], "n": 1,
                "summary_value": row["value"], "min_value": "", "max_value": "",
                "unit": "", "status": row["status"], "detail": row["detail"],
            })

    cold_status = defaultdict(dict)
    cold_attempts = {}
    cold_walls = {}
    cold_totals = {}
    for row in raw:
        if row["scenario"] != "cold_sweep" or int(row["run_index"]) not in VALID_RUNS:
            continue
        run = int(row["run_index"])
        if row["metric"] == "state_status":
            cold_status[(row["engine_label"], run)][row["state_id"]] = row["status"]
        elif row["metric"] == "attempt_trace":
            try:
                cold_attempts[(row["engine_label"], run, row["state_id"])] = json.loads(row["value"])
            except (TypeError, ValueError):
                cold_attempts[(row["engine_label"], run, row["state_id"])] = []
        elif row["metric"] == "state_wall_s" and (value := number(row["value"])) is not None:
            cold_walls[(row["engine_label"], run, row["state_id"])] = value
        elif row["metric"] == "total_wall_s" and (value := number(row["value"])) is not None:
            cold_totals[(row["engine_label"], run)] = value

    cold_start_counts = defaultdict(list)
    recovered_counts = defaultdict(list)
    for engine in ("S", "G"):
        for run in VALID_RUNS:
            final_statuses = cold_status[(engine, run)]
            first_success = 0
            recovered = 0
            for state, status in final_statuses.items():
                attempts = cold_attempts.get((engine, run, state), [])
                if attempts and attempts[0].get("status") == "evaluated":
                    first_success += 1
                elif status == "evaluated" and attempts:
                    recovered += 1
            cold_start_counts[engine].append(first_success)
            recovered_counts[engine].append(recovered)
    for engine in ("S", "G"):
        result.append(summary_row(
            engine, "cold_sweep", "79-state-cold-sweep",
            "cold_start_only_evaluated_count", cold_start_counts[engine], "states",
            detail="first attempt only; evaluator recovery attempts excluded",
        ))
        result.append(summary_row(
            engine, "cold_sweep", "79-state-cold-sweep",
            "evaluator_recovered_state_count", recovered_counts[engine], "states",
            detail="final evaluated state had a failed first attempt and a successful later evaluator attempt",
        ))

    shared_s_states = set(cold_status[("S", 4)]) & set(cold_status[("S", 5)]) & set(cold_status[("S", 6)])
    shared_s_states = {
        state for state in shared_s_states
        if all(cold_status[("S", run)].get(state) == "evaluated" for run in VALID_RUNS)
    }
    total_ratios, shared_ratios = [], []
    for run in VALID_RUNS:
        s_total, g_total = cold_totals.get(("S", run)), cold_totals.get(("G", run))
        if s_total and g_total:
            total_ratio = s_total / g_total
            total_ratios.append(total_ratio)
            result.append(summary_row(
                "S_vs_G", "engine_pair", f"run-{run}", "s_to_g_total_wall_ratio",
                [total_ratio], "x", detail=f"S={s_total:.17g};G={g_total:.17g}",
            ))
        if shared_s_states:
            s_wall = sum(cold_walls.get(("S", run, state), 0.0) for state in shared_s_states)
            g_wall = sum(cold_walls.get(("G", run, state), 0.0) for state in shared_s_states)
            if s_wall and g_wall:
                ratio = s_wall / g_wall
                shared_ratios.append(ratio)
                result.append(summary_row(
                    "S_vs_G", "engine_pair", f"run-{run}",
                    "s_to_g_shared_states_wall_ratio", [ratio], "x",
                    detail=f"shared_states={len(shared_s_states)};S={s_wall:.17g};G={g_wall:.17g}",
                ))
    for metric, values, detail in (
        ("median_pair_total_wall_ratio", total_ratios, "median of the three per-pair total-wall ratios"),
        ("median_pair_shared_state_wall_ratio", shared_ratios, f"median on {len(shared_s_states)} states evaluated by S in all three runs"),
    ):
        if values:
            result.append(summary_row(
                "S_vs_G", "engine_pair", "valid-pairs", metric, values, "x", detail=detail,
            ))

    pair = [row for row in raw if row["engine_label"] == "S_vs_G" and row["scenario"] == "engine_pair"]
    differences = [
        (float(row["value"]), row["state_id"])
        for row in pair if row["metric"] == "abs_ln_greenfield_over_superseded:pco2"
        and number(row["value"]) is not None
    ]
    if differences:
        vals = [value for value, _ in differences]
        worst = max(differences)
        result.append(summary_row(
            "S_vs_G", "engine_pair", "co2-partial-pressure",
            "max_abs_ln_greenfield_over_superseded", [worst[0]], "absolute ln ratio",
            detail=f"state={worst[1]}; n_common_states={len(differences)}",
        ))
        result.append(summary_row(
            "S_vs_G", "engine_pair", "co2-partial-pressure",
            "median_abs_ln_greenfield_over_superseded", vals, "absolute ln ratio",
            detail=f"n_common_states={len(vals)}",
        ))

    value_differences = [
        float(row["value"]) for row in raw
        if row["scenario"] == "addendum_value_check"
        and row["metric"].startswith("relative_difference_vs_3eb502ab:")
        and row["status"] == "evaluated" and number(row["value"]) is not None
    ]
    value_statuses = [
        row for row in raw
        if row["scenario"] == "addendum_value_check" and row["metric"] == "state_status"
    ]
    if value_statuses:
        evaluated_count = sum(row["status"] == "evaluated" for row in value_statuses)
        result.append({
            "engine_label": "G", "scenario": "addendum_value_check",
            "group": "five-representative-states", "metric": "evaluated_state_count",
            "n": len(value_statuses), "summary_value": evaluated_count,
            "min_value": "", "max_value": "", "unit": "states",
            "status": "summarized", "detail": "retained b66 state_status rows",
        })
    if value_differences:
        worst_row = max(
            (row for row in raw if row["scenario"] == "addendum_value_check"
             and row["metric"] == "max_relative_difference_vs_3eb502ab"
             and number(row["value"]) is not None),
            key=lambda row: float(row["value"]),
            default=None,
        )
        maximum = max(value_differences)
        result.append({
            "engine_label": "G", "scenario": "addendum_value_check",
            "group": "five-representative-states", "metric": "max_relative_difference_vs_3eb502ab",
            "n": len(value_differences), "summary_value": maximum,
            "min_value": min(value_differences), "max_value": maximum,
            "unit": "relative", "status": "equal" if maximum == 0.0 else "summarized",
            "detail": f"n_matched_outputs={len(value_differences)}; state={worst_row['state_id'] if worst_row else 'unknown'}",
        })

    for row in raw:
        if row["scenario"] == "addendum_derivatives" and row["metric"].startswith("derivative:") and row["metric"].endswith(":relative_error"):
            result.append({
                "engine_label": "G", "scenario": "addendum_derivatives",
                "group": row["metric"].split(":", 2)[1],
                "metric": "native_vs_fd_relative_error", "n": 1,
                "summary_value": row["value"], "min_value": "", "max_value": "",
                "unit": row["unit"], "status": row["status"], "detail": row["detail"],
            })
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


def temperature_chain_note(raw: list[dict[str, str]]) -> str:
    chain = next((row for row in raw
                  if row["engine_label"] == "G" and row["wheel_sha256"] == GREENFIELD_B66_SHA256
                  and row["scenario"] == "addendum_derivatives"
                  and row["metric"] == "derivative_family:reaction_reference_temperature"), None)
    relative_error = next((row for row in raw
                           if row["engine_label"] == "G" and row["wheel_sha256"] == GREENFIELD_B66_SHA256
                           and row["scenario"] == "addendum_derivatives"
                           and row["metric"] == "derivative:temperature:relative_error"), None)
    if not chain or chain["value"] != "available":
        return "The retained b66 rows do not record an available reaction reference-temperature chain."
    error = fmt(number(relative_error["value"]), 4) if relative_error else "not measured"
    return (
        "On b66, the measured solved-state temperature action includes the Engine #84 R1–R5 "
        f"reference-temperature chain; its central finite-difference relative error is {error}."
    )


def derivative_failure_note(raw: list[dict[str, str]]) -> str:
    failure = next((row for row in raw
                    if row["engine_label"] == "G" and row["wheel_sha256"] == GREENFIELD_3EB_SHA256
                    and row["scenario"] == "derivatives" and row["metric"] == "worker_status"
                    and "MAXITER_EXCEEDED" in row["diagnostic"]), None)
    if not failure:
        return "No retained 3eb502ab derivative worker row records a MAXITER_EXCEEDED failure."
    _, _, tail = failure["diagnostic"].partition(" after ")
    iterations = tail.split(" ", 1)[0] if tail else "an unrecorded number of"
    return (
        f"The retained G 3eb502ab derivative run {failure['run_index']} failed with "
        f"`MAXITER_EXCEEDED` after {iterations} iterations on the central kij solve. Its failed "
        "worker row remains in `measurements.csv` and is not treated as a derivative value."
    )


def write_readme(path: Path, raw_path: Path, summary: list[dict[str, object]]) -> None:
    global VALID_RUNS
    VALID_RUNS = valid_cold_runs(read_rows(raw_path))
    raw = read_rows(raw_path)

    def pick(engine, scenario, group, metric):
        return next((row for row in summary if row["engine_label"] == engine
                     and row["scenario"] == scenario and row["group"] == group
                     and row["metric"] == metric), None)

    def raw_pick(engine, scenario, metric, *, wheel=None, run=None, state=None):
        return next((row for row in raw
                     if row["engine_label"] == engine and row["scenario"] == scenario
                     and row["metric"] == metric
                     and (wheel is None or row["wheel_sha256"] == wheel)
                     and (run is None or int(row["run_index"]) == run)
                     and (state is None or row["state_id"] == state)), None)

    def value(row):
        return number(row["summary_value"]) if row else None

    def show(row, digits=3):
        return fmt(value(row), digits)

    def code_list(values):
        return ", ".join(f"`{item}`" for item in values) if values else "none"

    identities = defaultdict(set)
    for row in raw:
        if row["engine_label"] in ("S", "G"):
            identities[row["engine_label"], row["engine_commit"], row["wheel_sha256"],
                       row["evaluator_blob_sha"], row["parameter_file_sha256"],
                       row["state_packet_sha256"]].add(row["scenario"])
    provenance = []
    for (engine, commit, wheel, evaluator, parameters, packet), scenarios in sorted(identities.items()):
        if engine == "S":
            label = "S superseded"
        elif wheel == GREENFIELD_3EB_SHA256:
            label = "G 3eb502ab, cold runs 4–5" if evaluator == GREENFIELD_PRE_REBASE_EVALUATOR_BLOB else "G 3eb502ab, cold run 6 and selected checks"
        else:
            label = "G b66 addendum"
        provenance.append(
            f"| {label} | {commit} | {wheel} | {evaluator} | {parameters} | {packet} |"
        )

    setup_failures = sum(row["status"] == "setup_failure" for row in raw)
    s_states = {
        run: {row["state_id"] for row in raw
              if row["engine_label"] == "S" and row["scenario"] == "cold_sweep"
              and int(row["run_index"]) == run and row["metric"] == "state_status"
              and row["status"] == "evaluated"}
        for run in VALID_RUNS
    }
    shared_s = set.intersection(*(s_states[run] for run in VALID_RUNS)) if s_states else set()
    cold_rows = {(row["engine_label"], int(row["run_index"]), row["state_id"], row["metric"]): row
                 for row in raw if row["scenario"] == "cold_sweep"}
    recovered = set()
    attempt_counts = defaultdict(lambda: {"states": 0, "first": 0, "final": 0, "recovered": 0})
    persistent_s_failures = defaultdict(list)
    for state_id in sorted({row["state_id"] for row in raw
                            if row["engine_label"] == "S" and row["scenario"] == "cold_sweep"
                            and int(row["run_index"]) in VALID_RUNS and row["metric"] == "state_status"}):
        statuses = [cold_rows.get(("S", run, state_id, "state_status")) for run in VALID_RUNS]
        if all(row and row["status"] != "evaluated" for row in statuses):
            diagnostic = statuses[0]["diagnostic"]
            persistent_s_failures[diagnostic].append(state_id)
    for row in raw:
        if (row["engine_label"] == "G" and row["scenario"] == "cold_sweep"
                and int(row["run_index"]) in VALID_RUNS and row["metric"] == "attempt_trace"):
            try:
                attempts = json.loads(row["value"])
            except (TypeError, ValueError):
                attempts = []
            counts = attempt_counts[int(row["run_index"])]
            counts["states"] += 1
            if attempts and attempts[0].get("status") == "evaluated":
                counts["first"] += 1
            if attempts and attempts[-1].get("status") == "evaluated":
                counts["final"] += 1
            if (len(attempts) > 1 and attempts[0].get("status") != "evaluated"
                    and attempts[-1].get("status") == "evaluated"):
                recovered.add(row["state_id"])
                counts["recovered"] += 1

    def attempt_count_text(metric):
        counts = [(run, attempt_counts[run][metric], attempt_counts[run]["states"])
                  for run in VALID_RUNS if run in attempt_counts]
        if not counts:
            return "no retained attempt traces"
        if len(counts) == 3 and len({(count, states) for _, count, states in counts}) == 1:
            count, states = counts[0][1:]
            return f"{count}/{states} in every run"
        return ", ".join(f"run {run}: {count}/{states}" for run, count, states in counts)

    def recovered_count_text():
        counts = [(run, attempt_counts[run]["recovered"], attempt_counts[run]["states"])
                  for run in VALID_RUNS if run in attempt_counts]
        if not counts:
            return "no retained attempt traces"
        if len(counts) == 3 and len({count for _, count, _ in counts}) == 1:
            return f"{counts[0][1]} states in every run"
        return ", ".join(f"run {run}: {count} states" for run, count, _ in counts)

    for engine in ("S", "G"):
        total = pick(engine, "cold_sweep", "79-state-cold-sweep", "total_wall_s")
        per = pick(engine, "cold_sweep", "79-state-cold-sweep", "median_per_state_wall_s")
        cold = pick(engine, "cold_sweep", "79-state-cold-sweep", "cold_start_only_evaluated_count")
        final = pick(engine, "cold_sweep", "79-state-cold-sweep", "evaluated_state_count")
        recovery_states = pick(engine, "cold_sweep", "79-state-cold-sweep", "evaluator_recovered_state_count")
        recovery_attempts = pick(engine, "cold_sweep", "79-state-cold-sweep", "recovery_attempts_total")
        label = "S" if engine == "S" else "G (3eb502ab)"
        line = (
            f"| {label} | {round(value(total) or 0):d} | {show(per, 3)} | "
            f"{show(cold, 3)}/79 | {show(final, 3)}/79 | "
            f"{show(recovery_states, 3)} | {show(recovery_attempts, 3)} |"
        )
        if engine == "S":
            s_line = line
        else:
            g_line = line

    pair_lines = []
    for run in VALID_RUNS:
        s_total = raw_pick("S", "cold_sweep", "total_wall_s", run=run, state="79-state-cold-sweep")
        g_total = raw_pick("G", "cold_sweep", "total_wall_s", run=run, state="79-state-cold-sweep")
        total_ratio = pick("S_vs_G", "engine_pair", f"run-{run}", "s_to_g_total_wall_ratio")
        shared_ratio = pick("S_vs_G", "engine_pair", f"run-{run}", "s_to_g_shared_states_wall_ratio")
        pair_lines.append(
            f"| {run} | {round(float(s_total['value']))} | {round(float(g_total['value']))} | "
            f"{show(total_ratio, 3)} | {show(shared_ratio, 3)} |"
        )
    median_total_ratio = pick("S_vs_G", "engine_pair", "valid-pairs", "median_pair_total_wall_ratio")
    median_shared_ratio = pick("S_vs_G", "engine_pair", "valid-pairs", "median_pair_shared_state_wall_ratio")
    accuracy_sources = sorted({row["group"] for row in summary if row["scenario"] == "accuracy_pco2"})
    accuracy_lines = []
    shared_accuracy_lines = []
    for scenario, destination in (
        ("accuracy_pco2", accuracy_lines),
        ("accuracy_pco2_shared_66", shared_accuracy_lines),
    ):
        for engine in ("S", "G"):
            for source in accuracy_sources:
                mean = pick(engine, scenario, source, "mean_ln_ratio")
                rms = pick(engine, scenario, source, "rms_ln_ratio")
                aard = pick(engine, scenario, source, "aard_pct")
                if mean:
                    label = "S" if engine == "S" else ("G, all evaluable states" if scenario == "accuracy_pco2" else "G, shared states")
                    destination.append(
                        f"| {label} | {source} | {mean['n']} | {show(aard, 4)} | "
                        f"{show(mean, 4)} | {show(rms, 4)} |"
                    )

    pair_differences = [
        row for row in raw if row["engine_label"] == "S_vs_G" and row["scenario"] == "engine_pair"
        and row["metric"] == "abs_ln_greenfield_over_superseded:pco2"
        and number(row["value"]) is not None
    ]
    max_pair = max(pair_differences, key=lambda row: float(row["value"])) if pair_differences else None
    median_abs_log = statistics.median(float(row["value"]) for row in pair_differences) if pair_differences else None

    representative_lines = []
    for state_id in REPRESENTATIVE_STATES:
        for engine in ("S", "G"):
            status = pick(engine, "representative_states", state_id, "state_evaluation_status")
            wall = pick(engine, "representative_states", state_id, "state_wall_s")
            iterations = pick(engine, "representative_states", state_id, "iterations")
            label = "S" if engine == "S" else "G (3eb502ab)"
            representative_lines.append(
                f"| `{state_id}` | {label} | `{status and status['status'] or 'missing'}` | "
                f"{show(wall, 3)} | {show(iterations, 3)} |"
            )

    speciation = [row for row in summary if row["scenario"] == "accuracy_speciation"]
    speciation_lines = []
    for engine in ("S", "G"):
        for group in sorted({row["group"] for row in speciation}):
            mean = pick(engine, "accuracy_speciation", group, "mean_absolute_mole_fraction_error")
            rms = pick(engine, "accuracy_speciation", group, "rms_mole_fraction_error")
            if mean:
                label = "S" if engine == "S" else "G (3eb502ab)"
                speciation_lines.append(f"| {label} | {group} | {show(mean, 4)} | {show(rms, 4)} |")

    def family_availability(engine, scenario, family, wheel=None):
        row = raw_pick(engine, scenario, f"derivative_family:{family}", wheel=wheel)
        if row:
            return f"`{row['value']}`"
        row = raw_pick(engine, scenario, f"derivative:{family}:availability", wheel=wheel)
        return f"`{row['status']}`" if row else "not measured"

    derivative_lines = []
    for family in ("temperature", "pressure", "eos_parameter", "reaction_coefficient"):
        derivative_lines.append(
            f"| {family.replace('_', ' ')} | "
            f"{family_availability('S', 'derivatives', family)} | "
            f"{family_availability('G', 'derivatives', family, GREENFIELD_3EB_SHA256)} | "
            f"{family_availability('G', 'addendum_derivatives', family, GREENFIELD_B66_SHA256)} |"
        )

    def derivative_value(engine, scenario, metric, wheel=None):
        row = raw_pick(engine, scenario, metric, wheel=wheel)
        return row["value"] if row and row["value"] not in ("", "None") else "—"

    def derivative_unit(engine, scenario, direction, wheel=None):
        for metric in (f"derivative:{direction}:native", f"derivative:{direction}:finite_difference"):
            row = raw_pick(engine, scenario, metric, wheel=wheel)
            if row and row["unit"]:
                return row["unit"]
        return "—"

    derivative_check_lines = []
    for label, engine, scenario, wheel in (
        ("S", "S", "derivatives", None),
        ("G (3eb502ab)", "G", "derivatives", GREENFIELD_3EB_SHA256),
        ("G (443a9da4)", "G", "addendum_derivatives", GREENFIELD_B66_SHA256),
    ):
        directions = ("kij",) if engine == "S" else (
            ("pressure", "kij") if wheel == GREENFIELD_3EB_SHA256 else
            ("temperature", "pressure", "kij")
        )
        for direction in directions:
            availability = derivative_value(engine, scenario, f"derivative:{direction}:availability", wheel)
            native = derivative_value(engine, scenario, f"derivative:{direction}:native", wheel)
            fd = derivative_value(engine, scenario, f"derivative:{direction}:finite_difference", wheel)
            error = derivative_value(engine, scenario, f"derivative:{direction}:relative_error", wheel)
            if engine == "S" and availability == "evaluated":
                availability = "available"
            derivative_check_lines.append(
                f"| {label} | {direction} | {derivative_unit(engine, scenario, direction, wheel)} | `{availability}` | "
                f"{fmt(native, 5) if native != '—' else '—'} | "
                f"{fmt(fd, 5) if fd != '—' else '—'} | "
                f"{fmt(error, 4) if error not in ('—', '') else '—'} |"
            )

    addendum_statuses = [
        row for row in raw if row["scenario"] == "addendum_value_check" and row["metric"] == "state_status"
    ]
    addendum_predictions = [
        row for row in raw if row["scenario"] == "addendum_value_check"
        and row["metric"].startswith("relative_difference_vs_3eb502ab:")
        and row["status"] == "evaluated" and number(row["value"]) is not None
    ]
    addendum_max = max((float(row["value"]) for row in addendum_predictions), default=None)
    fit_rows = [row for row in raw if row["metric"] == "fit_objective_capability"]
    objective_lines = []
    for row in fit_rows:
        wheel = row["wheel_sha256"]
        label = (
            "S superseded" if row["engine_label"] == "S" else
            "G 3eb502ab" if wheel == GREENFIELD_3EB_SHA256 else "G 443a9da4"
        )
        detail = row["detail"].replace(OBJECTIVE_EVIDENCE.name, f"`{OBJECTIVE_EVIDENCE.name}`")
        detail = detail.replace("file_sha256=", "`file_sha256`=")
        objective_lines.append(f"| {label} | `{row['value']}` | {detail} |")
    if (any(row["wheel_sha256"] == GREENFIELD_B66_SHA256 for row in raw)
            and not any(row["engine_label"] == "G" and row["wheel_sha256"] == GREENFIELD_B66_SHA256
                        for row in fit_rows)):
        objective_lines.append(
            "| G b66 | `not_measured` | The MEA heat scripts have not been rebuilt on Engine #84/#138. |"
        )

    loads = []
    for row in raw:
        if row["scenario"] != "cold_sweep" or row["metric"] != "total_wall_s":
            continue
        try:
            loads.append(float(row["host_load"].split("load average:", 1)[1].split(",", 1)[0]))
        except (IndexError, ValueError):
            pass
    run5_timeout = [
        row for row in raw
        if row["engine_label"] == "S" and row["scenario"] == "cold_sweep"
        and int(row["run_index"]) == 5 and row["metric"] == "state_status"
        and row["failure_code"] == "evaluation_timeout"
    ]
    run5_failures = [
        row for row in raw
        if row["engine_label"] == "S" and row["scenario"] == "cold_sweep"
        and int(row["run_index"]) == 5 and row["metric"] == "state_status"
        and row["status"] != "evaluated"
    ]
    run5_load = (
        run5_timeout[0]["host_load"].split("load average:", 1)[1].split(",", 1)[0].strip()
        if run5_timeout else "not recorded"
    )
    bubble_states = persistent_s_failures.get("bubble Newton iteration limit reached", [])
    reactive_states = persistent_s_failures.get("reactive_finite_phase_certificate_failed", [])
    s_bubble_sums = [
        sum(float(cold_rows[("S", run, state, "state_wall_s")]["value"])
            for state in bubble_states if ("S", run, state, "state_wall_s") in cold_rows)
        for run in VALID_RUNS
    ]
    setup_failures_count = setup_failures
    g_recovery_attempts = pick("G", "cold_sweep", "79-state-cold-sweep", "recovery_attempts_total")
    minimum_shared_ratio = min(
        float(pick("S_vs_G", "engine_pair", f"run-{run}", "s_to_g_shared_states_wall_ratio")["summary_value"])
        for run in VALID_RUNS
    )
    extra_hilliard_states = int(pick("G", "accuracy_pco2", "Hilliard2008", "aard_pct")["n"]) - int(
        pick("S", "accuracy_pco2", "Hilliard2008", "aard_pct")["n"]
    )

    fence = chr(96) * 3
    lines = [
        "# MEA Engine comparison",
        "",
        "Fixed parameters and state packets were used throughout. The measurements describe these Engine and evaluator versions; they do not establish predictive use.",
        f"The original controller setup failures remain as {setup_failures_count} `setup_failure` rows and are excluded from the three valid cold-sweep pairs.",
        "",
        "## Provenance",
        "",
        "| Measurement rows | Engine commit | Wheel SHA-256 | Evaluator git blob | Parameter file SHA-256 | State packet JSON SHA-256 |",
        "|---|---|---|---|---|---|",
        *provenance,
        "",
        f"- State packet JSON SHA-256: {PACKET_SHA256}; compressed file SHA-256: {PACKET_FILE_SHA256}.",
        "- The superseded parameter file from 8f8e4a2^ matches the current adopted file on all 110 shared numeric coefficients. Its seven extra same-sign ion-pair kij=1 entries are omitted by the current file, which explicitly excludes same-sign pairs.",
        "- Each run used OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1, a fresh empty evaluator cache, and sequential workers. The full uptime snapshot is retained in host_load on every measurement row.",
        "- Greenfield rows on wheel 3eb502ab include evaluator recovery attempts. The b66 rows add only the five-state value check and derivative check; no new speed measurements were taken.",
        "",
        "## Summary",
        "",
        "### 79-state solved-pressure replay",
        "",
        "Medians use only valid alternating pairs S4/G4, S5/G5, and S6/G6. Median recovery attempts per sweep is the median of each run's total attempts beyond its first attempt.",
        "",
        "| Engine | Median total wall (s) | Median per-run median state wall (s) | Cold-start-only evaluated / 79 | Final evaluated / 79 | Median states recovered by evaluator | Median recovery attempts per sweep |",
        "|---|---:|---:|---:|---:|---:|---:|",
        s_line,
        g_line,
        "",
        f"Median of per-pair total S/G ratios: {show(median_total_ratio, 3)}x. Per-pair ratios and ratios on the {len(shared_s)} states S evaluated in all three runs:",
        "",
        "| Pair | S total (s) | G total (s) | Total S/G | Shared-state S/G |",
        "|---:|---:|---:|---:|---:|",
        *pair_lines,
        "",
        f"Median shared-state S/G ratio: {show(median_shared_ratio, 3)}x. G was faster in every pair by at least {minimum_shared_ratio:.1f}x on those shared states.",
        f"S totals include about {round(statistics.median(s_bubble_sums)) if s_bubble_sums else 0} s median time on the {len(bubble_states)} bubble-Newton failures. G totals include its {show(g_recovery_attempts, 3)} evaluator recovery attempts per run.",
        f"Cold-sweep start load averages ranged from {fmt(min(loads), 3) if loads else '—'} to {fmt(max(loads), 3) if loads else '—'}; full snapshots remain in `host_load`.",
        "",
        "### Failures and evaluator retries",
        "",
        f"G's `cold-packet-start` failed on {code_list(sorted(recovered))} and evaluated {attempt_count_text('first')}. The newer MEA evaluator then tried `speciated-liquid-start`, recovered {recovered_count_text()}, and evaluated {attempt_count_text('final')}. The S evaluator uses `anchors=[]` and records only the initial attempt, so G's final count reflects both the Engine and newer evaluator.",
        "",
        f"S had {len(reactive_states)} persistent `numerical_convergence_failure` cases with diagnostic `reactive_finite_phase_certificate_failed`: {code_list(reactive_states)}.",
        f"S had {len(bubble_states)} persistent `numerical_convergence_failure` cases with diagnostic `bubble Newton iteration limit reached`: {code_list(bubble_states)}.",
        f"S run 5 had {len(run5_timeout)} additional 60 s `evaluation_timeout` cases: {code_list([row['state_id'] for row in run5_timeout])}; its one-minute load average was {run5_load}. It had {len(run5_failures)} failures total, including {len(reactive_states) + len(bubble_states)} numerical cases.",
        "",
        "### pCO2 accuracy by source, all evaluated states",
        "",
        "Predictions use the per-state median across valid runs. AARD (%) is the mean absolute relative error times 100; mean ln ratio reports bias, and RMS ln ratio reports the log error spread.",
        "",
        "| Engine | Source | States | AARD (%) | Mean ln ratio (bias) | RMS ln ratio |",
        "|---|---|---:|---:|---:|---:|",
        *accuracy_lines,
        "",
        "### pCO2 accuracy on the 66 states evaluated by both Engines",
        "",
        "| Engine | Source | Shared states | AARD (%) | Mean ln ratio (bias) | RMS ln ratio |",
        "|---|---|---:|---:|---:|---:|",
        *shared_accuracy_lines,
        "",
        f"On shared states, G's AARD differs from S by {abs(float(pick('G', 'accuracy_pco2_shared_66', 'Hilliard2008', 'aard_pct')['summary_value']) - float(pick('S', 'accuracy_pco2_shared_66', 'Hilliard2008', 'aard_pct')['summary_value'])):.2f} points for Hilliard2008 and {abs(float(pick('G', 'accuracy_pco2_shared_66', 'Jou1995', 'aard_pct')['summary_value']) - float(pick('S', 'accuracy_pco2_shared_66', 'Jou1995', 'aard_pct')['summary_value'])):.2f} points for Jou1995. The larger all-state Hilliard2008 AARD for G comes from its {extra_hilliard_states} extra evaluable Hilliard states.",
        f"Across {len(pair_differences)} paired pressure states, median |ln(G/S)| is {fmt(median_abs_log, 3)} and maximum is {fmt(max_pair and max_pair['value'], 3)} on `{max_pair['state_id'] if max_pair else '—'}`.",
        "",
        "### Representative states",
        "",
        "Three alternating repeats each on the original 3eb502ab wheel:",
        "",
        "| State | Engine | Evaluation counts | Median wall (s) | Median iterations |",
        "|---|---|---|---:|---:|",
        *representative_lines,
        "",
        "Absolute mole-fraction errors for measured species on the two fixed-pressure states:",
        "",
        "| Engine | Source / species | Mean absolute error | RMS error |",
        "|---|---|---:|---:|",
        *speciation_lines,
        "",
        f"The b66 cache-cold pass evaluated {len(addendum_statuses)} representative states and matched {len(addendum_predictions)} outputs to the median of three 3eb502ab repeats; maximum relative difference: {fmt(addendum_max, 3)}. No timing rows from that pass are retained.",
        "",
        "### Derivatives",
        "",
        "| Direction family | S | G (3eb502ab) | G (443a9da4) |",
        "|---|---|---|---|",
        *derivative_lines,
        "",
        "| Engine / wheel | Direction | Unit | Native status | Native derivative | Central finite difference | Relative error |",
        "|---|---|---|---|---:|---:|---:|",
        *derivative_check_lines,
        "",
        temperature_chain_note(raw),
        derivative_failure_note(raw),
        "The superseded wheel has native R4/R5 coefficient-sensitivity evidence in retained `sensitivity-check.csv`.",
        "",
        "### Adopted fit objective",
        "",
        "| Engine / wheel | Result | Evidence or reason |",
        "|---|---|---|",
        *objective_lines,
        "",
        "No objective timing was taken. Retained `full-validation-targets.csv` contains evaluated heat rows for the superseded 40fba7cf wheel. On wheel 3eb502ab, the adopted objective could not be measured because Engine #84 reference-enthalpy actions were unavailable. On b66, the Engine actions are present, but the MEA heat scripts have not been rebuilt on Engine #84/#138.",
        "",
        "## Reproduction",
        "",
        "Finalization reads `measurements.csv` only; it does not invoke either Engine or modify measurement rows. It deterministically regenerates `summary.csv` and this README:",
        "",
        fence + "bash",
        "python3.13 analyses/mea_parameter_bundle/scripts/compare_engines.py --finalize-only",
        fence,
        "",
        "Set `RUNROOT`, `GREENFIELD_3EB_WHEEL`, and `GREENFIELD_B66_WHEEL` to scratch and pinned wheel paths, then prepare the workers:",
        "",
        fence + "bash",
        'UV_PROJECT_ENVIRONMENT="$RUNROOT/superseded-venv" uv sync --locked --group test --python 3.13',
        'uv pip install --python "$RUNROOT/superseded-venv/bin/python" --reinstall --no-deps analyses/mea_parameter_bundle/data/input/engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl',
        'uv pip install --python "$RUNROOT/superseded-venv/bin/python" pint==0.26.1',
        'UV_PROJECT_ENVIRONMENT="$RUNROOT/greenfield-venv" uv sync --locked --group test --python 3.13',
        'uv pip install --python "$RUNROOT/greenfield-venv/bin/python" --reinstall --no-deps "$GREENFIELD_3EB_WHEEL"',
        'python3.13 analyses/mea_parameter_bundle/scripts/compare_engines.py --superseded-python "$RUNROOT/superseded-venv/bin/python" --greenfield-python "$RUNROOT/greenfield-venv/bin/python" --greenfield-wheel "$GREENFIELD_3EB_WHEEL"',
        'uv pip install --python "$RUNROOT/greenfield-venv/bin/python" --reinstall --no-deps "$GREENFIELD_B66_WHEEL"',
        'python3.13 analyses/mea_parameter_bundle/scripts/compare_engines.py --scenario addendum --append --greenfield-python "$RUNROOT/greenfield-venv/bin/python" --greenfield-wheel "$GREENFIELD_B66_WHEEL"',
        'python3.13 analyses/mea_parameter_bundle/scripts/compare_engines.py --finalize-only',
        fence,
        "",
        "Use wheel 3eb502ab for the original comparison and b66 for the five-state addendum. The addendum records values and derivative checks without timing rows. A fresh comparison refuses to overwrite this folder: run it from a checkout without `results/runs/engine-comparison/`; valid cold runs are taken from the data (cold-sweep runs without `setup_failure` rows), and G rows record the git blob of the `shared_evaluation.py` actually imported.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--append", action="store_true",
                        help="retain existing rows while adding selected states or the b66 addendum")
    parser.add_argument("--selected-only", action="store_true",
                        help="run representative states and derivative/evaluability checks")
    parser.add_argument("--finalize-only", action="store_true",
                        help="regenerate summary.csv and README.md from measurements.csv")
    parser.add_argument("--engine", choices=("S", "G"))
    parser.add_argument("--scenario", choices=(
        "cold_sweep", "representative_states", "derivatives",
        "fit_objective_capability", "addendum",
    ))
    parser.add_argument("--run-index", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--scratch", type=Path)
    parser.add_argument("--superseded-python", type=Path, default=Path("/tmp/mea-engine-comparison-20260923/superseded-venv/bin/python"))
    parser.add_argument("--greenfield-python", type=Path, default=Path("/tmp/mea-engine-comparison-20260923/greenfield-venv/bin/python"))
    parser.add_argument("--greenfield-wheel", type=Path,
                        help="pinned Greenfield wheel for a comparison run or addendum")
    args = parser.parse_args()

    if args.worker:
        if not all((args.engine, args.scenario, args.output, args.scratch)):
            parser.error("--worker requires --engine, --scenario, --output and --scratch")
        if args.scenario == "addendum" and args.engine != "G":
            parser.error("the addendum scenario requires --engine G")
        if args.engine == "G":
            if not args.greenfield_wheel or not args.greenfield_wheel.is_file():
                parser.error("Greenfield workers require an existing --greenfield-wheel")
            try:
                configure_greenfield(args.greenfield_wheel, args.scenario)
            except ValueError as exc:
                parser.error(str(exc))
        worker(args.engine, args.scenario, args.run_index, args.output, args.scratch)
        return

    measurements = OUTPUT / "measurements.csv"
    if args.finalize_only:
        if not measurements.is_file():
            parser.error(f"cannot finalize without {measurements}")
        summary = build_summary(measurements)
        write_summary(OUTPUT / "summary.csv", summary)
        write_readme(OUTPUT / "README.md", measurements, summary)
        print(f"results: {OUTPUT}", flush=True)
        return

    if args.scenario not in (None, "addendum"):
        parser.error("--scenario is only available with --worker, except for addendum runs")
    if args.scenario == "addendum":
        if not args.append or args.selected_only:
            parser.error("--scenario addendum requires --append and cannot use --selected-only")
        if not measurements.is_file():
            parser.error(f"cannot append without {measurements}")
        if not args.greenfield_python.is_file():
            parser.error(f"G Python environment is missing: {args.greenfield_python}")
        if not args.greenfield_wheel or not args.greenfield_wheel.is_file():
            parser.error("--scenario addendum requires an existing --greenfield-wheel")
        try:
            configure_greenfield(args.greenfield_wheel, "addendum")
        except ValueError as exc:
            parser.error(str(exc))
        run_index = max(
            (int(row["run_index"]) for row in read_rows(measurements)
             if row["scenario"].startswith("addendum")),
            default=0,
        ) + 1
        scratch = Path(tempfile.mkdtemp(prefix="mea-engine-comparison-addendum-", dir="/tmp"))
        cmd = [
            str(args.greenfield_python.absolute()), str(Path(__file__).absolute()),
            "--worker", "--engine", "G", "--scenario", "addendum",
            "--run-index", str(run_index), "--output", str(measurements),
            "--scratch", str(scratch / "G-addendum"),
            "--greenfield-wheel", str(args.greenfield_wheel.absolute()),
        ]
        env = os.environ.copy()
        env.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
        completed = subprocess.run(cmd, cwd=ROOT, env=env)
        if completed.returncode:
            parser.error(f"addendum worker exited {completed.returncode}")
        summary = build_summary(measurements)
        write_summary(OUTPUT / "summary.csv", summary)
        write_readme(OUTPUT / "README.md", measurements, summary)
        print(f"results: {OUTPUT}", flush=True)
        return

    if args.selected_only and not args.append:
        parser.error("--selected-only requires --append to preserve existing rows")
    if args.append and not args.selected_only:
        parser.error("--append is reserved for --selected-only")
    if not args.greenfield_wheel or not args.greenfield_wheel.is_file():
        parser.error("comparison runs require an existing --greenfield-wheel")
    try:
        configure_greenfield(args.greenfield_wheel, "comparison")
    except ValueError as exc:
        parser.error(str(exc))
    for label, py in (("S", args.superseded_python), ("G", args.greenfield_python)):
        if not py.is_file():
            parser.error(f"{label} Python environment is missing: {py}")
    if args.append:
        if not measurements.is_file():
            parser.error(f"cannot append without {measurements}")
        existing = read_rows(measurements)
    else:
        if OUTPUT.exists():
            parser.error(f"result directory already exists; refusing to overwrite: {OUTPUT}")
        OUTPUT.mkdir(parents=True)
        with measurements.open("w", newline="", encoding="utf-8") as stream:
            csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n").writeheader()
        existing = []
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
        if engine == "G":
            cmd.extend(("--greenfield-wheel", str(args.greenfield_wheel.absolute())))
        env = os.environ.copy()
        env.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
        print(f"starting {engine} {scenario} run {run_index}: {cmd[0]}", flush=True)
        completed = subprocess.run(cmd, cwd=ROOT, env=env)
        if completed.returncode:
            print(f"worker exited {completed.returncode}: {engine} {scenario} run {run_index}", flush=True)
    derive_engine_differences(measurements)
    summary = build_summary(measurements)
    write_summary(OUTPUT / "summary.csv", summary)
    write_readme(OUTPUT / "README.md", measurements, summary)
    print(f"results: {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
