"""Reproduce the bounded final-wheel MEA replay and retain its diagnostics."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path

import shared_evaluation as shared


ANALYSIS = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS / "results/runs/reaction-temperature-fit/strict-current-wheel"
SENTINELS = (315.0, 330.0, 345.0)
VLE_IDS = ("vle_obs_0130", "vle_obs_0206")


def _request_map(packet: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(observation["identity"]): observation["request"]
        for observation in packet["observations"]
    }


def _request_at_temperature(request: dict[str, object], temperature_k: float) -> dict[str, object]:
    result = copy.deepcopy(request)
    result["temperature"]["value"] = temperature_k
    return result


def _evidence(record: dict[str, object]) -> dict[str, object]:
    return {str(key): value for key, value in record.get("evidence", ())}


def _max_abs(values: object) -> float | None:
    if not isinstance(values, list) or not values:
        return None
    return max(abs(float(value)) for value in values)


def _row_payload(
    case: str, role: str, request: dict[str, object], record: dict[str, object]
) -> list[dict[str, object]]:
    evidence = _evidence(record)
    phases = record.get("phases", ())
    pressure = None
    if phases:
        pressure = phases[0].get("pressure_pa")
    compiled = evidence.get("compiled_point_evaluation", {})
    raw_max = (
        compiled.get("raw_stationarity_max_abs")
        if isinstance(compiled, dict)
        else None
    )
    common = {
        "case": case,
        "role": role,
        "temperature_k": request["temperature"]["value"],
        "pressure_pa": pressure,
        "status": record.get("status", ""),
        "failure_code": record.get("failure_code", ""),
        "solver_status": record.get("solver_status", ""),
        "requested_tolerance_met": evidence.get("requested_tolerance_met"),
        "raw_stationarity_max_abs": raw_max,
        "classified_residual_max_abs": _max_abs(evidence.get("classified_residuals")),
        "attempt_count": record.get("attempt_count", 0),
    }
    rows = []
    for row in record.get("rows", ()):
        if row.get("identity") == "action-batch-diagnostics":
            continue
        rows.append({
            **common,
            "prediction_identity": row.get("identity", ""),
            "predicted": row.get("value"),
        })
    if not rows:
        rows.append({**common, "prediction_identity": "", "predicted": None})
    return rows


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = (
        "case", "role", "temperature_k", "pressure_pa", "prediction_identity",
        "predicted", "status", "failure_code", "solver_status",
        "requested_tolerance_met", "raw_stationarity_max_abs",
        "classified_residual_max_abs", "attempt_count",
    )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _state_reference(output: Path, case: str) -> dict[str, str] | None:
    matches = []
    for path in (output / "states").glob("*.json"):
        try:
            if json.loads(path.read_text(encoding="utf-8")).get("identity") == case:
                matches.append(path)
        except (OSError, ValueError):
            continue
    if not matches:
        return None
    path = matches[-1]
    return {
        "path": str(path.relative_to(output)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _record_summary(
    output: Path, case: str, role: str, request_sha256: str, record: dict[str, object]
) -> dict[str, object]:
    evidence = _evidence(record)
    compiled = evidence.get("compiled_point_evaluation", {})
    summary: dict[str, object] = {
        "case": case,
        "role": role,
        "request_sha256": request_sha256,
        "status": record.get("status", ""),
        "failure_code": record.get("failure_code", ""),
        "failure_diagnostic": record.get("failure_diagnostic", ""),
        "solver_status": record.get("solver_status", ""),
        "requested_tolerance_met": evidence.get("requested_tolerance_met"),
        "raw_stationarity_max_abs": (
            compiled.get("raw_stationarity_max_abs")
            if isinstance(compiled, dict)
            else None
        ),
        "classified_residual_max_abs": _max_abs(evidence.get("classified_residuals")),
        "state": None if role == "cold-failure" else _state_reference(output, case),
    }
    if role == "cold-failure":
        summary["failure"] = {
            "status": record.get("status", ""),
            "failure_code": record.get("failure_code", ""),
            "failure_diagnostic": record.get("failure_diagnostic", ""),
            "attempts": record.get("attempts", ()),
        }
    if role == "warm-recovery":
        summary["cold_failure"] = next(
            (
                attempt
                for attempt in record.get("attempts", ())
                if attempt.get("status") != "evaluated"
            ),
            None,
        )
    return summary


def run(output: Path, budget_s: float, include_vle: bool) -> None:
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"refusing to mix an existing replay directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    shared.RUNS = output
    shared.verify_wheel()
    packet = shared.load_state_packet()
    requests = _request_map(packet)
    model = shared.epcsaft.Mixture(shared.load_parameters())
    reactions = shared._selected_reactions()
    cases: list[dict[str, object]] = []
    csv_rows: list[dict[str, object]] = []

    def evaluate(case: str, request: dict[str, object], role: str, anchors: list[shared.Anchor]) -> dict[str, object]:
        record = shared.evaluate_state(
            model, request, reactions, case, anchors, budget_s=budget_s
        )
        request_sha256 = hashlib.sha256(
            json.dumps(request, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        cases.append(_record_summary(output, case, role, request_sha256, record))
        csv_rows.extend(_row_payload(case, role, request, record))
        return record

    base = requests["Bottinger2008_state_050"]
    evaluate("Bottinger2008_state_050", base, "speciation", [])
    evaluate("Bottinger2008_state_058", requests["Bottinger2008_state_058"], "speciation", [])
    sentinel_records: dict[float, dict[str, object]] = {}
    for temperature_k in SENTINELS:
        case = f"MEA_fixedP_sentinel_{temperature_k:g}K"
        sentinel_records[temperature_k] = evaluate(
            case, _request_at_temperature(base, temperature_k), "sentinel", []
        )

    cold_request = _request_at_temperature(base, 360.0)
    evaluate("MEA_fixedP_sentinel_360K_cold", cold_request, "cold-failure", [])
    warm_anchor = shared.anchor_from(sentinel_records[345.0])
    if warm_anchor is None:
        warm_record = {
            "identity": "MEA_fixedP_sentinel_360K_warm345",
            "case": "MEA_fixedP_sentinel_360K_warm345",
            "status": "non_evaluable",
            "failure_code": "warm_anchor_unavailable",
            "failure_diagnostic": "345 K sentinel did not produce a liquid anchor",
            "attempt_count": 0,
        }
        cases.append(
            _record_summary(
                output,
                warm_record["case"],
                "warm-recovery",
                hashlib.sha256(
                    json.dumps(cold_request, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
                warm_record,
            )
        )
        csv_rows.extend(_row_payload(warm_record["case"], "warm-recovery", cold_request, warm_record))
    else:
        evaluate(
            "MEA_fixedP_sentinel_360K_warm345",
            cold_request,
            "warm-recovery",
            [warm_anchor],
        )
    if include_vle:
        for identity in VLE_IDS:
            evaluate(identity, requests[identity], "reactive-vle", [])

    archive_sha256 = hashlib.sha256(shared.STATE_PACKET.read_bytes()).hexdigest()
    shared.write_json(
        output / "strict-current-wheel-replay.json",
        {
            "schema": "mea-strict-current-wheel-replay",
            "schema_version": 1,
            "engine_wheel_sha256": shared.ENGINE_WHEEL_SHA256,
            "engine_commit": shared.ENGINE_COMMIT,
            "evaluator_sha256": shared.sha256(Path(shared.__file__)),
            "parameter_sha256": shared.sha256(shared.PARAMETERS),
            "state_packet_archive_sha256": archive_sha256,
            "state_packet_decompressed_sha256": shared.sha256(shared.STATE_PACKET),
            "records": cases,
        },
    )
    _write_csv(output / "strict-current-wheel-rows.csv", csv_rows)
    heartbeat = output / "heartbeat.json"
    if heartbeat.exists():
        heartbeat.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--budget-s", type=float, default=60.0)
    parser.add_argument("--skip-vle", action="store_true")
    args = parser.parse_args()
    run(args.output, args.budget_s, not args.skip_vle)


if __name__ == "__main__":
    main()
