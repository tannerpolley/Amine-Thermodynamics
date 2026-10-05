"""Replay the fixed #160 F1-D1 objective on the absorber's pinned Engine wheel."""
from __future__ import annotations

import concurrent.futures
import csv
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import multiprocessing
import os
import sys
import time
import tomllib
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlparse

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / "analyses/mea_parameter_bundle"
D1 = BUNDLE / "results/density-cp-160/D1-evidence"
OUTPUT = BUNDLE / "results/density-cp-160/common-wheel-48a639e7"
ABSORBER = Path("/home/tnnrpolley21/Workspaces/Engineering/MEA-Absorption-Column")
WHEEL = Path("/home/tnnrpolley21/.cache/epcsaft/wheels/8d9d3fcc30f47f36905a90d3f95754e41c4e1712ce160267c2de26e85b16d969/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl")
ENGINE_COMMIT = "464a9897615e513e5cc404ce5b49f46a72466d3d"
ENGINE_WHEEL_SHA256 = "48a639e78d00ef88a2f7e66ed1e3d89831ca0ad5267322330d44f48c34926060"
EXPECTED_COST = 30.0897611888619
COST_TOLERANCE = 1e-8
PROBLEM = "F1-D1-common-wheel"
PHYSICAL_RECORD = D1 / "F1-A/parameters.json"
NATIVE_FIT = D1 / "F1-A/native-fit.json"
CANDIDATE = D1 / "F1-double-prime-candidate-parameters.json"
PACKET = BUNDLE / "results/source-corrections-152/state-packet.json.gz"
STRICT_TARGETS = BUNDLE / "results/source-corrections-152/accepted-wave/strict141-targets.csv"
REQUIRED_IDS = BUNDLE / "results/source-corrections-152/accepted-wave/required-ids.json"
OLD_REPLAY = D1 / "evaluation/F1-replay.json"
OWNER = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def stop(status: str, code: str, detail: str, result: dict[str, object]) -> int:
    result.update(status=status, failure_code=code, failure_diagnostic=detail,
                  wall_s=result.get("wall_s", 0.0))
    write_json(OUTPUT / "qualification.json", result)
    print(json.dumps({"status": status, "failure_code": code, "diagnostic": detail}), flush=True)
    return 2


def verify_wheel() -> dict[str, object]:
    if sha(WHEEL) != ENGINE_WHEEL_SHA256:
        raise RuntimeError(f"wheel SHA-256 mismatch: {WHEEL}")
    dist = importlib.metadata.distribution("epcsaft")
    direct_url = json.loads(dist.read_text("direct_url.json") or "{}")
    installed = Path(unquote(urlparse(direct_url.get("url", "")).path)).resolve()
    if not direct_url.get("url", "").startswith("file://") or installed != WHEEL.resolve():
        raise RuntimeError(f"installed epcsaft wheel path mismatch: {direct_url}")
    site = Path(dist.locate_file("")).resolve()
    module = importlib.util.find_spec("epcsaft")
    module_path = Path(module.origin).resolve() if module and module.origin else None
    package = site / "epcsaft"
    if module_path != (package / "__init__.py").resolve():
        raise RuntimeError(f"epcsaft imports outside installed wheel contents: {module_path}")
    with zipfile.ZipFile(WHEEL) as archive:
        names = sorted(n for n in archive.namelist() if n.startswith("epcsaft/") and not n.endswith("/"))
        actual = sorted(p.relative_to(site).as_posix() for p in package.rglob("*")
                        if p.is_file() and "__pycache__" not in p.parts)
        if names != actual or any((site / n).read_bytes() != archive.read(n) for n in names):
            raise RuntimeError("installed epcsaft package contents differ from wheel")
        tree_hash = hashlib.sha256("\n".join(
            f"{n} {hashlib.sha256(archive.read(n)).hexdigest()}" for n in names
        ).encode()).hexdigest()
    with (ABSORBER / "uv.lock").open("rb") as stream:
        lock = tomllib.load(stream)
    entry = next(p for p in lock["package"] if p["name"] == "epcsaft")
    if (Path(entry["source"]["path"]).resolve() != WHEEL.resolve()
            or f"sha256:{ENGINE_WHEEL_SHA256}" not in {w["hash"] for w in entry["wheels"]}):
        raise RuntimeError("absorber uv.lock does not bind supplied wheel")
    contract_path = ABSORBER / "integration/epcsaft_contract.json"
    identity = json.loads(contract_path.read_text())["final_identity"]
    receipt_path = ABSORBER / "analyses/physical_acceptance_149/results/summary.json"
    receipt = json.loads(receipt_path.read_text())
    if (identity.get("engine_commit"), identity.get("wheel_sha256"), identity.get("wheel_filename")) != (ENGINE_COMMIT, ENGINE_WHEEL_SHA256, WHEEL.name):
        raise RuntimeError("absorber integration contract does not bind supplied wheel")
    if (receipt.get("engine_commit"), receipt.get("engine_wheel_sha256")) != (ENGINE_COMMIT, ENGINE_WHEEL_SHA256):
        raise RuntimeError("absorber physical-acceptance receipt does not bind supplied wheel")
    return {
        "engine_commit": ENGINE_COMMIT, "wheel_path": str(WHEEL), "wheel_sha256": ENGINE_WHEEL_SHA256,
        "distribution_version": dist.version, "installed_module": str(module_path),
        "installed_package_files": len(names), "installed_package_tree_sha256": tree_hash,
        "direct_url": direct_url,
        "uv_lock_sha256": sha(ABSORBER / "uv.lock"),
        "integration_contract_sha256": sha(contract_path), "physical_acceptance_receipt_sha256": sha(receipt_path),
    }


def load_owner(wheel: dict[str, object]):
    sys.path[:0] = [str(BUNDLE / "scripts"), str(BUNDLE / "calibration-misfit"), str(ROOT / "src")]
    import shared_evaluation as shared
    # Bind this driver explicitly; the shared evaluator default remains the old 28181 wheel.
    shared.ENGINE_WHEEL_SHA256 = ENGINE_WHEEL_SHA256
    shared.ENGINE_COMMIT = ENGINE_COMMIT
    shared.verify_wheel()
    import final_evidence as owner
    if owner.s is not shared or owner.probe.shared is not shared:
        raise RuntimeError("fixed-state evaluator lost the explicit wheel binding")
    if Path(shared.epcsaft.__file__).resolve() != Path(str(wheel["installed_module"])):
        raise RuntimeError("loaded Engine module differs from verified installation")
    owner.EVAL = OUTPUT
    return owner


def choose_states(owner):
    fit = json.loads(NATIVE_FIT.read_text())
    record = json.loads(PHYSICAL_RECORD.read_text())
    candidate = json.loads(CANDIDATE.read_text())
    packet = owner.s.load_state_packet(PACKET)
    required = json.loads(REQUIRED_IDS.read_text())
    strict = list(csv.DictReader(STRICT_TARGETS.open(newline="", encoding="utf-8")))
    old = json.loads(OLD_REPLAY.read_text())
    targets = set(fit["targets"])
    if (fit["status"] != "converged" or not fit["usable"] or len(fit["coordinates"]) != 5
            or len(targets) != 141 or fit["final_cost"] != EXPECTED_COST):
        raise RuntimeError("F1-A native fit differs from accepted fixed result")
    if targets != {row["target"] for row in strict} or len(strict) != 141:
        raise RuntimeError("strict141 membership differs from F1-A fit")
    if packet.get("source_corrections") != 152:
        raise RuntimeError("corrected source packet identity is not 152")
    correction = candidate["empirical_density_correction"]
    if correction.get("equilibrium_unchanged") is not True or correction.get("applied_to_chemical_potentials") is not False:
        raise RuntimeError("density correction metadata must remain unapplied to equilibrium")
    for key in ("components", "correlations", "domains", "model_coefficients", "model_families", "pairs", "reaction_correlations", "schema", "schema_version", "sources", "topology"):
        if candidate[key] != record[key]:
            raise RuntimeError(f"candidate/F1-A physical parameter mismatch: {key}")
    if (old.get("parameter_sha256") != sha(PHYSICAL_RECORD) or old.get("targets") != 141 or old.get("passed") is not True
            or abs(old["cost"] - EXPECTED_COST) / EXPECTED_COST > COST_TOLERANCE):
        raise RuntimeError("retained old-wheel replay does not bind F1-A and its 141 targets")
    rows = {row["target"]: row for row in strict}
    if {row["quantity"] for row in strict} != {"pressure", "species"}:
        raise RuntimeError("fit targets contain an unexpected quantity")
    states = []
    for state in packet["observations"]:
        if state["identity"] not in set(required["packet"]):
            continue
        selected = [t for t in state["targets"] if t["identity"] in targets]
        for target in selected:
            source = rows[target["identity"]]
            if (source["identity"] != state["identity"] or target["observed"] != float(source["observed"])
                    or target["basis"] != source["basis"] or target["unit"] != source["unit"]
                    or target["source_identity"] != source["source"] or target["source_hash"] != source["source_sha256"]
                    or state["request"]["temperature"]["value"] != float(source["temperature_K"])):
                raise RuntimeError(f"corrected packet/strict141 input mismatch: {target['identity']}")
        if selected:
            states.append({**state, "targets": selected})
    selected_ids = [t["identity"] for state in states for t in state["targets"]]
    if set(selected_ids) != targets or len(selected_ids) != 141 or len(states) != 83:
        raise RuntimeError(f"selected packet states/targets differ: {len(states)} states, {len(selected_ids)} targets")
    counts = {q: sum(row["quantity"] == q for row in strict) for q in ("pressure", "species", "density")}
    if counts != {"pressure": 47, "species": 94, "density": 0}:
        raise RuntimeError(f"unexpected objective quantities: {counts}")
    return fit, states, rows, packet["source"], counts


def state_job(problem, path, state):
    return OWNER.job(problem, path, "packet", state)


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    base = {
        "question": "Replay the same fixed F1-D1 141-target cost on the identified absorber wheel.",
        "evidence_type": "numerical verification; not physical validation",
        "claim_limit": "This qualifies one fixed 141-target replay on this wheel; it does not claim newest-upstream status, absorber validation, or support for every caloric action.",
    }
    try:
        wheel = verify_wheel()
        owner = load_owner(wheel)
    except Exception as exc:
        base["wall_s"] = time.perf_counter() - start
        return stop("unavailable", "evaluation_capability_unavailable", f"{type(exc).__name__}: {exc}", base)
    try:
        global OWNER
        OWNER = owner
        fit, states, strict, packet_source, counts = choose_states(owner)
    except Exception as exc:
        base["wall_s"] = time.perf_counter() - start
        return stop("unavailable", "input_validation_failed", f"{type(exc).__name__}: {exc}", {**base, "engine": wheel})

    hashes = {
        "candidate_record_sha256": sha(CANDIDATE), "physical_record_sha256": sha(PHYSICAL_RECORD),
        "native_fit_sha256": sha(NATIVE_FIT), "corrected_packet_file_sha256": sha(PACKET),
        "corrected_packet_content_sha256": owner.s.sha256(PACKET), "strict141_sha256": sha(STRICT_TARGETS),
        "required_ids_sha256": sha(REQUIRED_IDS), "previous_wheel_replay_sha256": sha(OLD_REPLAY),
        "driver_sha256": sha(Path(__file__)),
    }
    result = {
        **base, "engine": wheel, "inputs": hashes, "packet_source": packet_source,
        "physical_record": str(PHYSICAL_RECORD), "fixed_coordinates": dict(zip(fit["coordinates"], fit["physical"], strict=True)),
        "expected_cost": EXPECTED_COST, "native_fit_cost": fit["final_cost"], "target_count": 141,
        "target_counts": counts, "state_count": len(states),
    }
    write_json(OUTPUT / "qualification.json", result)

    records, failures = [], []
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=2, mp_context=multiprocessing.get_context("fork"))
    futures = {pool.submit(state_job, PROBLEM, str(PHYSICAL_RECORD), state): state for state in states}
    try:
        for future in concurrent.futures.as_completed(futures):
            state = futures[future]
            try:
                record, _ = future.result()
                records.append(record)
                print(f"evaluated {record['identity']} {record['wall_s']:.3f}s", flush=True)
            except Exception as exc:
                failures.append({"state": state["identity"], "diagnostic": f"{type(exc).__name__}: {exc}"})
                for pending in futures:
                    pending.cancel()
                break
    finally:
        pool.shutdown(wait=True, cancel_futures=bool(failures))
    result["wall_s"] = time.perf_counter() - start
    if failures:
        return stop("non_evaluable", "state_evaluation_failed", json.dumps(failures), result)

    scored = owner.score_rows(PROBLEM, records)
    by_target = {row["target"]: row for row in scored if row["kind"] == "packet"}
    targets = fit["targets"]
    if len(records) != len(states) or len(by_target) != 141 or set(by_target) != set(targets):
        return stop("non_evaluable", "incomplete_target_evaluation", f"{len(records)} states, {len(by_target)} targets", result)
    old = {t: (o, p, r) for t, o, p, r in zip(targets, fit["observed"], fit["predictions"], fit["weighted_residuals"], strict=True)}
    detail = []
    for target in targets:
        row = by_target[target]
        old_obs, old_pred, old_residual = old[target]
        values = [float(row[k]) for k in ("observed", "predicted", "scaled_residual", "cost")]
        if not all(math.isfinite(v) for v in values) or not math.isclose(values[0], old_obs, rel_tol=0, abs_tol=1e-14):
            return stop("non_evaluable", "invalid_target_result", f"{target}: {values}", result)
        detail.append({
            "target": target, "state": row["identity"], "source": row["source"], "quantity": row["quantity"],
            "unit": strict[target]["unit"], "basis": row["basis"], "observed": values[0],
            "native_fit_prediction": old_pred, "common_wheel_prediction": values[1],
            "native_weighted_residual": old_residual, "common_wheel_weighted_residual": values[2],
            "weighted_residual_change": values[2] - old_residual, "cost": values[3],
        })
    with (OUTPUT / "targets.jsonl").open("w", encoding="utf-8") as stream:
        for row in detail:
            stream.write(json.dumps(row, sort_keys=True) + "\n")

    aard = {}
    for quantity in ("pressure", "species"):
        rows = [r for r in scored if r["kind"] == "packet" and r["quantity"] == quantity]
        logs = [float(r["ln_pred_over_obs"]) for r in rows if r["ln_pred_over_obs"] is not None]
        if len(logs) != len(rows):
            return stop("non_evaluable", "aard_unavailable", f"{quantity} has a non-positive prediction", result)
        old_logs = [math.log(float(p) / float(o)) for t, o, p in zip(targets, fit["observed"], fit["predictions"], strict=True)
                    if t.endswith("-pco2") == (quantity == "pressure") and o > 0 and p > 0]
        native_aard = owner.compare.stats(old_logs)["aard_percent"]
        current_aard = owner.compare.stats(logs)["aard_percent"]
        aard[quantity] = {"targets": len(rows), "native_fit_percent": native_aard,
                          "common_wheel_percent": current_aard, "change_percentage_points": current_aard - native_aard,
                          "common_wheel_cost": math.fsum(float(r["cost"]) for r in rows)}
    cost = math.fsum(row["cost"] for row in detail)
    delta = abs(cost - EXPECTED_COST) / abs(EXPECTED_COST)
    result.update(status="evaluated", cost=cost, relative_cost_delta=delta, relative_cost_tolerance=COST_TOLERANCE,
                  equivalence_passed=delta <= COST_TOLERANCE, cost_by_quantity=aard,
                  state_wall_s=math.fsum(float(record["wall_s"]) for record in records))
    write_json(OUTPUT / "qualification.json", result)
    print(json.dumps({k: result[k] for k in ("status", "cost", "relative_cost_delta", "equivalence_passed", "target_count", "state_count", "wall_s")}), flush=True)
    return 0 if result["equivalence_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
