"""One bounded, cached owner for exact MEA equilibrium evaluations.

The figure, fitting, calorimetry, and thermal-reference scripts all use this
module for request normalization, warm starts, recovery, and cache identity.
It deliberately has no import from those scripts, so a plotting run cannot
silently grow a second solver implementation.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.metadata
import json
import math
import os
import select
import signal
from functools import lru_cache
from dataclasses import dataclass, replace
from pathlib import Path
from time import perf_counter
from urllib.parse import unquote, urlparse

import epcsaft
from epcsaft import equilibrium
from MEA.common.mea_source_contracts import EXPECTED_REACTION_CORRELATIONS


ANALYSIS = Path(__file__).resolve().parents[1]
INPUT = ANALYSIS / "data/input"
PARAMETERS = ANALYSIS / "results/selected-current-best-parameters.json"
ENGINE_WHEEL = INPUT / "engine/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl"
ENGINE_WHEEL_SHA256 = "40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805"
ENGINE_COMMIT = "8438ce5f94a547189c91c4ec180a7782d60879d6"
STATE_PACKET = INPUT / "state-packet.json"
STATE_PACKET_SHA256 = "41017bcf727a486a8f3feb280e19c111a15c5dda5a3cca4e8c7dc5b051168fef"
CANONICAL_SPECIATION = (
    ANALYSIS.parents[1]
    / "data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq.csv"
)
CANONICAL_VLE = (
    ANALYSIS.parents[1]
    / "data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv"
)
R123_SOURCE_TO_COMMON_MOLALITY_OFFSETS = (8.0330699846, 4.0165349923, 4.0165349923)

# Existing cache files remain usable only when their key and record contain
# this evaluator version.  Old keys did not contain this field, so they are
# naturally isolated without deleting anyone's retained results.
EVALUATOR_VERSION = "shared-evaluation-v3"
RUNS = ANALYSIS / "results/runs/reaction-temperature-fit"
SOURCE_CONTRACT = ANALYSIS.parents[1] / "src/MEA/common/mea_source_contracts.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def failure_fields(failure: object | None) -> tuple[str, str]:
    if failure is None:
        return "", ""
    return str(getattr(failure, "code", "unknown")), str(
        getattr(failure, "diagnostic", failure)
    )


def installed_wheel() -> Path:
    direct_url = json.loads(
        importlib.metadata.distribution("epcsaft").read_text("direct_url.json") or "{}"
    ).get("url", "")
    path = Path(unquote(urlparse(direct_url).path))
    if (
        not direct_url.startswith("file://")
        or path.suffix != ".whl"
        or not path.is_file()
    ):
        raise RuntimeError("replay requires epcsaft installed from the retained wheel")
    return path


def verify_wheel() -> None:
    if (
        sha256(ENGINE_WHEEL) != ENGINE_WHEEL_SHA256
        or sha256(installed_wheel()) != ENGINE_WHEEL_SHA256
    ):
        raise RuntimeError("installed and retained Engine wheels must match")


def corrected_request(
    request: dict[str, object], reaction_values: dict[str, float] | None = None
) -> dict[str, object]:
    """Normalize source requests to the installed Engine's current contract."""
    corrected = copy.deepcopy(request)
    for phase in corrected["phases"]:
        phase["model"]["kind"] = "eos"
        phase["model"]["reference_id"] = "installed-eos"
    temperature_k = float(corrected["temperature"]["value"])
    reaction_values = reaction_values or {}
    records = corrected["reaction_system"]["equilibrium_constants"]
    for index, offset in enumerate(R123_SOURCE_TO_COMMON_MOLALITY_OFFSETS):
        reaction_id = f"R{index + 1}"
        source = EXPECTED_REACTION_CORRELATIONS[reaction_id]
        coefficients = (
            float(source["a"]) + offset,
            float(source["b_k"]),
            float(source["c"]),
            float(source["d_per_k"]),
        )
        records[index][1] = "Austgen1991_converted_to_common_molality"
        metadata = {
            "reaction_id": reaction_id,
            "kind": "ln-k-a-plus-b-over-t-plus-c-ln-t-plus-d-t",
            "coefficient_identities": [
                f"reaction:{reaction_id}:correlation:a",
                f"reaction:{reaction_id}:correlation:b_k",
                f"reaction:{reaction_id}:correlation:c",
                f"reaction:{reaction_id}:correlation:d_per_k",
            ],
            "coefficient_values": list(coefficients),
        }
        if len(records[index]) >= 7:
            records[index][6] = metadata
        else:
            records[index].append(metadata)
    for record in records:
        record[4] = "source-standard-state-to-eos-neutral-reference"
        if len(record) < 7 or not record[6]:
            continue
        metadata = record[6]
        identities = metadata.get("coefficient_identities", [])
        coefficients = list(metadata.get("coefficient_values", []))
        for index, identity in enumerate(identities):
            if identity in reaction_values:
                coefficients[index] = reaction_values[identity]
        metadata["coefficient_values"] = coefficients
        if metadata["kind"] == "ln-k-a-plus-b-over-t":
            record[0] = coefficients[0] + coefficients[1] / temperature_k
        elif metadata["kind"] == "ln-k-a-plus-b-over-t-plus-c-ln-t-plus-d-t":
            record[0] = (
                coefficients[0]
                + coefficients[1] / temperature_k
                + coefficients[2] * math.log(temperature_k)
                + coefficients[3] * temperature_k
            )
        elif metadata["kind"] == "negative-log10-temperature-polynomial":
            record[0] = -math.log(10.0) * (
                coefficients[0] / temperature_k
                + coefficients[1]
                + coefficients[2] * temperature_k
            )
    return corrected


def prepared_problem(
    problem: object, identity: str, phase: object | None = None
) -> object:
    """Turn a continuation state or Anchor into a finite Engine start."""
    if phase is None:
        continuation = problem.continuation_state
        if continuation is None:
            raise ValueError("state packet request lacks a continuation warm start")
        phase = continuation.phases[0]
    balance = problem.reaction_system.balance_matrix
    targets = problem.reaction_system.conserved_totals
    projected = tuple(
        math.fsum(c * value for c, value in zip(row, phase.mole_fractions, strict=True))
        for row in balance
    )
    total = targets[1] / projected[1]
    amounts = [total * value for value in phase.mole_fractions]
    amounts[0] += targets[0] - math.fsum(
        c * amount for c, amount in zip(balance[0], amounts, strict=True)
    )
    if amounts[0] <= problem.reaction_system.strict_interior_amount_floor_mol:
        amounts = list(problem.reaction_system.feed_amounts_mol)
    if amounts[0] <= problem.reaction_system.strict_interior_amount_floor_mol:
        raise ValueError("continuation warm start cannot satisfy the current feed")
    start = equilibrium.FinitePhaseStart(
        tuple(amounts), math.fsum(amounts) * phase.molar_volume_m3_per_mol
    )
    phases = tuple(
        replace(candidate, start=start if candidate.amount_role == "finite" else None)
        for candidate in problem.phases
    )
    return replace(
        problem,
        phases=phases,
        continuation_identity=identity
        if any(candidate.amount_role == "incipient" for candidate in phases)
        else None,
        continuation_state=None,
    )


def _reaction_identity(reactions: dict[str, float]) -> str:
    return hashlib.sha256(
        json.dumps(reactions, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _selected_reactions() -> dict[str, float]:
    return {
        spec.identity: float(spec.value.magnitude)
        for spec in epcsaft.Parameters.from_json(PARAMETERS).parameter_specs
        if spec.identity.startswith("reaction:")
    }


def provenance(
    thermochemistry: object | None = None, reactions: dict[str, float] | None = None
) -> dict[str, object]:
    values = _selected_reactions() if reactions is None else reactions
    selected = _reaction_identity(_selected_reactions())
    effective = _reaction_identity(values)
    return {
        "evaluator_version": EVALUATOR_VERSION,
        "parameter_sha256": sha256(PARAMETERS),
        "parameter_role": "selected" if effective == selected else "candidate",
        "effective_reaction_values_sha256": effective,
        "engine_commit": ENGINE_COMMIT,
        "engine_wheel_sha256": ENGINE_WHEEL_SHA256,
        "source_contract_sha256": sha256(SOURCE_CONTRACT),
        "evaluator_source_sha256": sha256(Path(__file__)),
        "thermochemistry": None
        if thermochemistry is None
        else thermochemistry.scientific_fingerprint,
    }


@dataclass(frozen=True)
class Anchor:
    temperature_c: int
    loading: float
    pressure_pa: float
    mole_fractions: tuple[float, ...]
    molar_volume_m3_per_mol: float

    @property
    def phase(self) -> object:
        return self


@dataclass(frozen=True)
class EvaluationLimits:
    """Hard per-state limit plus optional invocation deadline.

    A forked child owns each native solve, so the parent can terminate a stuck
    call without leaving a solver thread behind.
    """

    state_timeout_s: float = 60.0
    overall_timeout_s: float = math.inf
    deadline_monotonic: float | None = None


class EvaluationTimeout(TimeoutError):
    pass


@dataclass(frozen=True)
class SolveSnapshot:
    """JSON-safe result returned by the short-lived solver child."""

    status: str
    failure_code: str = ""
    failure_diagnostic: str = ""
    predictions: dict[str, float] = None  # type: ignore[assignment]
    evidence: list[list[object]] = None  # type: ignore[assignment]
    phases: list[dict[str, object]] = None  # type: ignore[assignment]
    total_enthalpy_j: float | None = None
    amount_mol: float | None = None
    molar_density_mol_m3: float | None = None
    physical_status: str = ""
    eos_domain_status: str = ""
    solver_status: str = ""
    rows: list[dict[str, object]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.predictions is None:
            object.__setattr__(self, "predictions", {})
        if self.evidence is None:
            object.__setattr__(self, "evidence", [])
        if self.phases is None:
            object.__setattr__(self, "phases", [])
        if self.rows is None:
            object.__setattr__(self, "rows", [])


def _phase_payload(phase: object) -> dict[str, object]:
    return {
        "role": str(phase.role),
        "pressure_pa": float(phase.pressure_pa),
        "molar_density_mol_m3": float(phase.molar_density_mol_m3),
        "packing_fraction": float(phase.packing_fraction),
        "mechanical_class": str(phase.mechanical_class),
        "mole_fractions": [float(value) for value in phase.mole_fractions],
        "molar_volume_m3_per_mol": float(phase.molar_volume_m3_per_mol),
    }


def _snapshot_from_result(result: object) -> dict[str, object]:
    failure = getattr(result, "failure", None)
    code, diagnostic = failure_fields(failure)
    total = getattr(result, "total_enthalpy", None)
    total_value = None
    amount = None
    density = None
    phases = [_phase_payload(phase) for phase in result.phases]
    if isinstance(total, epcsaft.EquilibriumEnthalpy):
        total_value = float(total.value.to("joule").magnitude)
        amount = float(total.phases[0].amount_mol)
        liquid = next(
            (phase for phase in result.phases if phase.role == "liquid"), None
        )
        density = None if liquid is None else float(liquid.molar_density_mol_m3)
        enthalpies = {phase.phase_identity: phase for phase in total.phases}
        for phase, declared in zip(phases, result.problem.phases, strict=True):
            if declared.identity in enthalpies:
                thermal = enthalpies[declared.identity]
                phase["reference_molar_enthalpy_j_per_mol"] = (
                    thermal.reference_molar_enthalpy_j_per_mol
                )
                phase["residual_molar_enthalpy_j_per_mol"] = (
                    thermal.residual_molar_enthalpy_j_per_mol
                )
    elif total is not None:
        code, diagnostic = failure_fields(total)
    return {
        "status": str(result.status),
        "failure_code": code,
        "failure_diagnostic": diagnostic,
        "predictions": {
            str(row.identity): float(row.value)
            for row in result.rows
            if row.value is not None
        },
        "rows": [
            {
                "identity": str(row.identity),
                "value": None if row.value is None else float(row.value),
                "status": str(row.status),
                "jacobian": None
                if row.jacobian is None
                else [float(value) for value in row.jacobian],
            }
            for row in result.rows
        ],
        "evidence": [[str(name), value] for name, value in result.evidence],
        "phases": phases,
        "solver_status": str(getattr(result, "solver_status", "")),
        "physical_status": str(getattr(result, "physical_status", "")),
        "eos_domain_status": str(getattr(result, "eos_domain_status", "")),
        "total_enthalpy_j": total_value,
        "amount_mol": amount,
        "molar_density_mol_m3": density,
    }


def _snapshot_from_payload(payload: dict[str, object]) -> SolveSnapshot:
    return SolveSnapshot(
        status=str(payload.get("status", "exception")),
        failure_code=str(payload.get("failure_code", "")),
        failure_diagnostic=str(payload.get("failure_diagnostic", "")),
        predictions={
            str(k): float(v) for k, v in dict(payload.get("predictions", {})).items()
        },
        evidence=list(payload.get("evidence", [])),
        phases=list(payload.get("phases", [])),
        total_enthalpy_j=None
        if payload.get("total_enthalpy_j") is None
        else float(payload["total_enthalpy_j"]),
        amount_mol=None
        if payload.get("amount_mol") is None
        else float(payload["amount_mol"]),
        molar_density_mol_m3=None
        if payload.get("molar_density_mol_m3") is None
        else float(payload["molar_density_mol_m3"]),
        physical_status=str(payload.get("physical_status", "")),
        eos_domain_status=str(payload.get("eos_domain_status", "")),
        solver_status=str(payload.get("solver_status", "")),
        rows=list(payload.get("rows", [])),
    )


def _solve_in_child(
    model: object,
    problem: object,
    timeout_s: float,
    active_parameters: object | None = None,
) -> SolveSnapshot:
    """Run one Engine call in a forked child so timeout can kill native code."""
    if not hasattr(os, "fork"):
        raise RuntimeError("hard solver timeout requires POSIX fork support")
    read_fd, write_fd = os.pipe()
    child = os.fork()
    if child == 0:
        os.close(read_fd)
        try:
            try:
                result = equilibrium.solve(
                    model, problem, active_parameters=active_parameters
                )
                payload = {"ok": True, "result": _snapshot_from_result(result)}
            except BaseException as exc:
                payload = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            with os.fdopen(write_fd, "wb") as pipe:
                pipe.write(json.dumps(payload, separators=(",", ":")).encode())
        finally:
            os._exit(0)
    os.close(write_fd)
    deadline = perf_counter() + timeout_s
    chunks: list[bytes] = []
    try:
        while True:
            remaining = deadline - perf_counter()
            if remaining <= 0:
                raise EvaluationTimeout(f"state solve exceeded {timeout_s:g} s")
            ready, _, _ = select.select([read_fd], [], [], remaining)
            if ready:
                data = os.read(read_fd, 1 << 20)
                if data:
                    chunks.append(data)
                else:
                    break
    finally:
        os.close(read_fd)
        try:
            waited, status = os.waitpid(child, os.WNOHANG)
            if waited == 0:
                os.kill(child, signal.SIGKILL)
                os.waitpid(child, 0)
        except ChildProcessError:
            pass
    if not chunks:
        raise RuntimeError("solver child exited without a result")
    payload = json.loads(b"".join(chunks))
    if not payload.get("ok"):
        raise RuntimeError(str(payload.get("error", "solver child failed")))
    return _snapshot_from_payload(payload["result"])


@lru_cache(maxsize=None)
def attempt_success_rates(temperature_c: int) -> dict[str, float]:
    # ponytail: freeze prior-cache rankings per invocation; clear for live re-ranking.
    counts: dict[str, list[int]] = {}
    for path in (RUNS / "states").glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (
            record.get("evaluator_version") != EVALUATOR_VERSION
            or record.get("temperature_c") != temperature_c
        ):
            continue
        for attempt in record.get("attempts", ()):
            tally = counts.setdefault(str(attempt.get("kind")), [0, 0])
            tally[1] += 1
            tally[0] += attempt.get("status") == "evaluated"
    return {kind: ok / total for kind, (ok, total) in counts.items() if total >= 3}


def attempt_plan(
    temperature_c: int, loading: float, anchors: list[Anchor]
) -> list[tuple[str, Anchor | None]]:
    same = sorted(
        (a for a in anchors if a.temperature_c == temperature_c),
        key=lambda a: abs(a.loading - loading),
    )
    cross = sorted(
        (a for a in anchors if a.temperature_c != temperature_c),
        key=lambda a: (abs(a.temperature_c - temperature_c), abs(a.loading - loading)),
    )
    plan: list[tuple[str, Anchor | None]] = []
    if same:
        plan.append(("same-temperature-anchor", same[0]))
    plan.append(("cold-packet-start", None))
    plan.extend(("cross-temperature-anchor", a) for a in cross)
    plan.extend(("same-temperature-anchor", a) for a in same[1:])
    rates = attempt_success_rates(temperature_c)
    plan.sort(key=lambda item: -rates.get(item[0], 0.0))
    return plan


def solve_with_recovery(
    model: epcsaft.Mixture,
    request: dict[str, object],
    reactions: dict[str, float],
    identity: str,
    anchors: list[Anchor],
    thermochemistry: object | None = None,
    budget_s: float = math.inf,
    limits: EvaluationLimits | None = None,
) -> tuple[object | None, list[dict[str, object]]]:
    limits = limits or EvaluationLimits(
        state_timeout_s=60.0, overall_timeout_s=budget_s
    )
    started = perf_counter()
    deadline = min(
        started + limits.state_timeout_s,
        started + budget_s,
        started + limits.overall_timeout_s,
    )
    if limits.deadline_monotonic is not None:
        deadline = min(deadline, limits.deadline_monotonic)
    base = corrected_request(request, reactions)
    temperature_c = round(float(base["temperature"]["value"]) - 273.15)
    seen: set[tuple[object, ...]] = set()
    attempts: list[dict[str, object]] = []
    for kind, anchor in attempt_plan(
        temperature_c, float(base["reaction_system"]["feed_amounts_mol"][0]), anchors
    ):
        if perf_counter() >= deadline:
            attempts.append(
                {
                    "kind": "budget-exhausted",
                    "wall_s": 0.0,
                    "status": "timeout",
                    "failure_code": "evaluation_timeout",
                    "failure_diagnostic": "state budget exhausted before next recovery attempt",
                }
            )
            break
        candidate = copy.deepcopy(base)
        if anchor is not None and candidate["pressure"]["role"] != "fixed":
            candidate["pressure"]["initial"] = anchor.pressure_pa
            candidate["pressure"]["starts"] = [anchor.pressure_pa]
        problem = equilibrium.general_reactive_equilibrium_problem_from_mapping(
            candidate
        )
        problem = prepared_problem(problem, identity, anchor)
        start = next(phase.start for phase in problem.phases if phase.start is not None)
        signature = (
            tuple(round(value, 12) for value in start.amounts_mol),
            round(start.molar_volume_m3_per_mol, 15),
            round(
                float(
                    candidate["pressure"].get(
                        "initial", candidate["pressure"].get("value", 0.0)
                    )
                ),
                6,
            ),
        )
        if signature in seen:
            continue
        seen.add(signature)
        if thermochemistry is not None:
            problem = replace(problem, thermochemistry=thermochemistry)
        clock = perf_counter()
        try:
            result = _solve_in_child(model, problem, max(0.01, deadline - clock))
            status = result.status
            code, diagnostic = result.failure_code, result.failure_diagnostic
        except EvaluationTimeout as exc:
            result = None
            status, code, diagnostic = "timeout", "evaluation_timeout", str(exc)
        except Exception as exc:
            result = None
            status, code, diagnostic = (
                "exception",
                "engine_exception",
                f"{type(exc).__name__}: {exc}",
            )
        evaluated = (
            result is not None
            and status == "evaluated"
            and (thermochemistry is None or result.total_enthalpy_j is not None)
        )
        attempts.append(
            {
                "kind": kind,
                "anchor": None
                if anchor is None
                else [anchor.temperature_c, anchor.loading],
                "wall_s": perf_counter() - clock,
                "status": "evaluated" if evaluated else status,
                "failure_code": "" if evaluated else code,
                "failure_diagnostic": "" if evaluated else diagnostic,
            }
        )
        if evaluated:
            return result, attempts
    return None, attempts


def liquid_anchor(result: object, temperature_c: int, loading: float) -> Anchor:
    liquid = next(phase for phase in result.phases if phase["role"] == "liquid")
    return Anchor(
        temperature_c,
        loading,
        float(liquid["pressure_pa"]),
        tuple(float(x) for x in liquid["mole_fractions"]),
        float(liquid["molar_volume_m3_per_mol"]),
    )


def anchor_from(record: dict[str, object]) -> Anchor | None:
    if record.get("anchor") is None:
        return None
    payload = dict(record["anchor"])
    payload["mole_fractions"] = tuple(payload["mole_fractions"])
    return Anchor(**payload)


def cached_anchors(temperatures: set[int]) -> list[Anchor]:
    anchors = []
    for path in (RUNS / "states").glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (
            record.get("evaluator_version") == EVALUATOR_VERSION
            and record.get("status") == "evaluated"
            and record.get("temperature_c") in temperatures
        ):
            anchor = anchor_from(record)
            if anchor is not None:
                anchors.append(anchor)
    return anchors


def evaluate_state(
    model: epcsaft.Mixture,
    request: dict[str, object],
    reactions: dict[str, float],
    identity: str,
    anchors: list[Anchor],
    thermochemistry: object | None = None,
    budget_s: float = math.inf,
    limits: EvaluationLimits | None = None,
) -> dict[str, object]:
    """Evaluate one state with identity-complete cache and bounded recovery."""
    provenance_data = provenance(thermochemistry, reactions)
    model_fingerprint = model.parameter_fingerprint
    corrected = corrected_request(request, reactions)
    selected_request = corrected_request(request, _selected_reactions())
    provenance_data["parameter_role"] = (
        "selected"
        if (
            model_fingerprint == epcsaft.Parameters.from_json(PARAMETERS).fingerprint
            and corrected["reaction_system"]["equilibrium_constants"]
            == selected_request["reaction_system"]["equilibrium_constants"]
        )
        else "candidate"
    )
    key_parts = {
        **provenance_data,
        "model_parameters_fingerprint": model_fingerprint,
        "request": corrected,
    }
    key = hashlib.sha256(
        json.dumps(
            key_parts, sort_keys=True, default=str, separators=(",", ":")
        ).encode()
    ).hexdigest()
    path = RUNS / "states" / f"{key}.json"
    anchor_ids = sorted(
        hashlib.sha256(json.dumps(a.__dict__, sort_keys=True).encode()).hexdigest()
        for a in anchors
    )
    if path.exists():
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("evaluator_version") == EVALUATOR_VERSION and (
            record.get("status") == "evaluated"
            or (
                record.get("anchor_ids") == anchor_ids
                and record.get("failure_code")
                not in ("evaluation_timeout", "engine_exception")
            )
        ):
            record["cache_hit"] = True
            return record
    write_json(
        RUNS / "heartbeat.json",
        {"state": identity, "pid": os.getpid(), **provenance_data},
    )
    if (
        limits
        and limits.deadline_monotonic is not None
        and perf_counter() >= limits.deadline_monotonic
    ):
        raise EvaluationTimeout(
            "Invocation deadline exhausted; outputs were not published"
        )
    result, attempts = solve_with_recovery(
        model,
        corrected,
        reactions,
        identity,
        anchors,
        thermochemistry,
        budget_s,
        limits,
    )
    if (
        limits
        and limits.deadline_monotonic is not None
        and perf_counter() >= limits.deadline_monotonic
    ):
        raise EvaluationTimeout(
            "Invocation deadline exhausted; outputs were not published"
        )
    temperature_c = round(float(corrected["temperature"]["value"]) - 273.15)
    loading = float(corrected["reaction_system"]["feed_amounts_mol"][0])
    evaluated = result is not None
    record: dict[str, object] = {
        **provenance_data,
        "model_parameters_fingerprint": model_fingerprint,
        "identity": identity,
        "temperature_c": temperature_c,
        "loading": loading,
        "status": "evaluated" if evaluated else "non_evaluable",
        "failure_code": "" if evaluated else attempts[-1].get("failure_code", ""),
        "failure_diagnostic": ""
        if evaluated
        else attempts[-1].get("failure_diagnostic", ""),
        "attempts": attempts,
        "anchor_ids": anchor_ids,
        "attempt_count": len(attempts),
        "wall_s": math.fsum(float(a.get("wall_s", 0.0)) for a in attempts),
        "predictions": {},
        "anchor": None,
        "total_enthalpy_j": None,
        "amount_mol": None,
        "cache_hit": False,
    }
    if evaluated:
        record["predictions"] = result.predictions
        record["solver_status"] = result.solver_status
        record["physical_status"] = result.physical_status
        record["eos_domain_status"] = result.eos_domain_status
        record["phases"] = result.phases
        anchor = liquid_anchor(result, temperature_c, loading)
        record["anchor"] = anchor.__dict__
        record["evidence"] = result.evidence
        if thermochemistry is not None:
            record["total_enthalpy_j"] = result.total_enthalpy_j
            record["amount_mol"] = result.amount_mol
            record["molar_density_mol_m3"] = result.molar_density_mol_m3
    write_json(path, record)
    return record
