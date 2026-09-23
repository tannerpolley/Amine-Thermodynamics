"""One bounded, cached owner for exact MEA equilibrium evaluations.

The figure, fitting, calorimetry, and thermal-reference scripts all use this
module for request normalization, warm starts, recovery, and cache identity.
It deliberately has no import from those scripts, so a plotting run cannot
silently grow a second solver implementation.
"""

from __future__ import annotations

import copy
import gzip
import hashlib
import importlib.metadata
import json
import math
import os
import select
import signal
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from urllib.parse import unquote, urlparse

import epcsaft
from epcsaft import equilibrium

from MEA.common.mea_source_contracts import EXPECTED_REACTION_CORRELATIONS


ANALYSIS = Path(__file__).resolve().parents[1]
INPUT = ANALYSIS / "data/input"
PARAMETERS = ANALYSIS / "results/selected-current-best-parameters.json"
ENGINE_WHEEL = Path(
    "/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-greenfield/"
    "build/environment-wheel/epcsaft-0.2.0.dev0-cp313-cp313-linux_x86_64.whl"
)
ENGINE_WHEEL_SHA256 = "6cb2c2f0a513ebccc5b3e3fdc6fd16220b1d59db9959feb2290f20d9f1894041"
ENGINE_COMMIT = "832380ad5e254762dbe5d9dfc44e0659e4b65167"
STATE_PACKET = INPUT / "state-packet.json.gz"
STATE_PACKET_SHA256 = "86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448"
STATE_PACKET_SCHEMA = "mea-parameter-estimation-observations-compact"
STATE_PACKET_SCHEMA_VERSION = 1
STATE_PACKET_REQUEST_FIELDS = (
    "continuation", "feed", "identity", "intensive_boundaries", "outputs",
    "phase_reactions", "phases", "pressure", "reaction_phase_ids",
    "reaction_system", "temperature",
)
CANONICAL_SPECIATION = (
    ANALYSIS.parents[1]
    / "data/reference/MEA/observations/liquid_speciation/Canonical_Combined_ChEq.csv"
)
CANONICAL_VLE = (
    ANALYSIS.parents[1]
    / "data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv"
)
COMPONENT_IDS = (
    "carbon-dioxide", "monoethanolamine", "water", "protonated-monoethanolamine",
    "carbamate-anion", "bicarbonate-anion", "carbonate-anion", "hydronium-cation", "hydroxide-anion",
)
R123_SOURCE_TO_COMMON_MOLALITY_OFFSETS = (8.0330699846, 4.0165349923, 4.0165349923)
NEUTRAL_VAPOR_IDS = COMPONENT_IDS[:3]
MODEL_RUNTIME_DEFAULTS = {"c_shell": 1.0, "c_dielectric": 1.0}
REACTION_REFERENCE_PRESSURES = {"R1": None, "R2": None, "R3": None, "R4": 1.0e5, "R5": 1.0e5}
COMMON_SOURCE_STANDARD_STATE_ID = "aqueous-molality-infinite-dilution-water-v1"
RAW_SOURCE_STANDARD_STATE_ID = "aqueous-mole-fraction-infinite-dilution-water-v1"
NEUTRAL_REFERENCE_RATIO_SCALE = 0.125
# The source R1--R3 records use the historical ln(T/(1 K)) convention.  The
# native polynomial requires its reference temperature to lie inside the
# admitted interval, so preserve the source law by shifting ``a`` to this
# source-contract pivot before constructing ReactionLogPolynomial.
REACTION_REFERENCE_TEMPERATURE_K = 313.15

# Existing cache files remain usable only when their key and record contain
# this evaluator version.  Old keys did not contain this field, so they are
# naturally isolated without deleting anyone's retained results.
EVALUATOR_VERSION = "shared-evaluation-v5"
RUNS = ANALYSIS / "results/runs/reaction-temperature-fit"
SOURCE_CONTRACT = ANALYSIS.parents[1] / "src/MEA/common/mea_source_contracts.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(source_bytes(path)).hexdigest()


def source_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    return gzip.decompress(data) if path.name.endswith(".json.gz") else data


def load_state_packet(path: Path = STATE_PACKET) -> dict[str, object]:
    """Load and expand the compact retained packet with strict references."""
    return expand_state_packet(json.loads(source_bytes(path)))


def expand_state_packet(document: object) -> dict[str, object]:
    """Expand an already decoded compact packet with strict references."""
    if not isinstance(document, dict) or set(document) != {
        "schema", "schema_version", "source", "metadata", "request_tables", "observations"
    }:
        raise ValueError("invalid compact state packet fields")
    if document["schema"] != STATE_PACKET_SCHEMA or document["schema_version"] != STATE_PACKET_SCHEMA_VERSION:
        raise ValueError("unsupported compact state packet schema")
    tables = document["request_tables"]
    if not isinstance(tables, dict) or set(tables) != set(STATE_PACKET_REQUEST_FIELDS):
        raise ValueError("invalid compact state packet request tables")
    if not isinstance(document["metadata"], dict) or not isinstance(document["source"], dict):
        raise ValueError("invalid compact state packet metadata")
    observations = document["observations"]
    if not isinstance(observations, list):
        raise ValueError("invalid compact state packet observations")
    expanded = []
    for row in observations:
        if not isinstance(row, dict) or set(row) != {"family", "identity", "multiplier", "request", "targets"}:
            raise ValueError("invalid compact state packet observation")
        refs = row["request"]
        if not isinstance(refs, dict) or set(refs) != set(STATE_PACKET_REQUEST_FIELDS):
            raise ValueError("invalid compact state packet references")
        request = {}
        for field in STATE_PACKET_REQUEST_FIELDS:
            ref = refs[field]
            if isinstance(ref, bool) or not isinstance(ref, int):
                raise ValueError(f"invalid {field} reference")
            table = tables[field]
            if not isinstance(table, list) or ref < 0 or ref >= len(table):
                raise ValueError(f"out-of-range {field} reference")
            request[field] = copy.deepcopy(table[ref])
        expanded.append({
            "family": row["family"], "identity": row["identity"],
            "multiplier": row["multiplier"], "request": request,
            "targets": copy.deepcopy(row["targets"]),
        })
    return {**copy.deepcopy(document["metadata"]), "observations": expanded}


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def _jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    diagnostic_fields = (
        "reaction_index", "terminal_contraction", "observed_terminal_change",
        "reference_pressure_pa", "status", "message",
    )
    if all(hasattr(value, field) for field in diagnostic_fields):
        result = {field: _jsonable(getattr(value, field)) for field in diagnostic_fields}
        for field in (
            "terminal_contraction_pressure_derivative",
            "terminal_contraction_pressure_second_derivative",
        ):
            if hasattr(value, field):
                result[field] = _jsonable(getattr(value, field))
        return result
    value = getattr(value, "name", value)
    return value if value is None or isinstance(value, (bool, int, float, str)) else str(value)


def installed_wheel() -> Path:
    direct_metadata = json.loads(
        importlib.metadata.distribution("epcsaft").read_text("direct_url.json") or "{}"
    )
    direct_url = direct_metadata.get("url", "")
    archive_info = direct_metadata.get("archive_info", {})
    archive_hash = archive_info.get("hashes", {}).get("sha256") or archive_info.get("hash")
    path = Path(unquote(urlparse(direct_url).path))
    if (
        not direct_url.startswith("file://")
        or path.suffix != ".whl"
        or not path.is_file()
    ):
        raise RuntimeError("replay requires epcsaft installed from the retained wheel")
    if archive_hash is not None and archive_hash != ENGINE_WHEEL_SHA256:
        raise RuntimeError("installed wheel metadata does not match the retained wheel")
    return path


def verify_wheel() -> None:
    if (
        sha256(ENGINE_WHEEL) != ENGINE_WHEEL_SHA256
        or sha256(installed_wheel()) != ENGINE_WHEEL_SHA256
    ):
        raise RuntimeError("installed and retained Engine wheels must match")


class ReferenceBasisUnavailable(RuntimeError):
    code = "reference_basis_unavailable"


def parameter_mapping(path: Path = PARAMETERS) -> dict[str, object]:
    mapping = json.loads(path.read_text(encoding="utf-8"))
    for family in mapping.get("model_families", ()):
        if family.get("kind") == "electrolyte" and family.get("choice") == "born":
            for key, value in MODEL_RUNTIME_DEFAULTS.items():
                family.setdefault(key, value)
    return mapping


def load_parameters(path: Path = PARAMETERS) -> epcsaft.Parameters:
    return epcsaft.Parameters.from_mapping(parameter_mapping(path))


def corrected_request(
    request: dict[str, object], reaction_values: dict[str, float] | None = None
) -> dict[str, object]:
    """Normalize phase model metadata without inventing source-to-EOS reactions."""
    corrected = copy.deepcopy(request)
    if reaction_values is None:
        reaction_values = _selected_reactions()
    for phase in corrected.get("phases", ()):
        phase.setdefault("model", {})["kind"] = "eos"
        phase["model"]["reference_id"] = "installed-eos"
    if reaction_values:
        selected_specs = {
            str(item.get("reaction_id")): item
            for item in parameter_mapping().get("reaction_correlations", ())
        }
        adopted = reaction_values == _selected_reactions()
        records = corrected.get("reaction_system", {}).get("equilibrium_constants", ())
        for index, record in enumerate(records):
            reaction_id = f"R{index + 1}"
            metadata = record[6] if len(record) >= 7 and isinstance(record[6], dict) else {}
            reaction_id = str(metadata.get("reaction_id", reaction_id))
            prefix = f"reaction:{reaction_id}:correlation:"
            selected = {
                identity[len(prefix):]: float(value)
                for identity, value in reaction_values.items()
                if identity.startswith(prefix)
            }
            if not selected and reaction_id not in EXPECTED_REACTION_CORRELATIONS:
                continue
            metadata = copy.deepcopy(metadata)
            metadata["reaction_id"] = reaction_id
            source = EXPECTED_REACTION_CORRELATIONS.get(reaction_id)
            if source is not None:
                metadata["source_correlation"] = copy.deepcopy(source)
                if len(record) > 2:
                    metadata["source_standard_state_id"] = record[2]
            if selected:
                metadata["effective_parameter_role"] = "selected" if adopted else "candidate"
                metadata["effective_coefficient_identities"] = [
                    f"reaction:{reaction_id}:correlation:{name}" for name in selected
                ]
                metadata["effective_coefficient_values"] = selected
                if adopted:
                    metadata["selected_parameter_role"] = "owner-adopted"
                    metadata["selected_coefficient_values"] = selected
                    selected_spec = selected_specs.get(reaction_id)
                    if selected_spec is not None:
                        metadata["selected_correlation_kind"] = selected_spec.get("kind")
                        metadata["selected_correlation_source"] = copy.deepcopy(
                            selected_spec.get("source", {})
                        )
            identities = metadata.get("coefficient_identities", ())
            values = list(metadata.get("coefficient_values", ()))
            for position, identity in enumerate(identities):
                if identity in reaction_values and position < len(values):
                    values[position] = reaction_values[identity]
            if identities:
                metadata["coefficient_values"] = values
            if len(record) >= 7:
                record[6] = metadata
            else:
                record.append(metadata)
        # The adapter targets the current native reference API.  Source records
        # are deliberately emitted here, before Problem construction, so the
        # Engine owns the only source-to-EOS conversion and reference
        # contraction.
        if "reaction_matrix" in corrected.get("reaction_system", {}):
            corrected["reaction_system"]["engine_reactions"] = _engine_reaction_records(
                corrected, reaction_values
            )
    return corrected


def _reaction_specifications() -> dict[str, dict[str, object]]:
    return {
        str(item["reaction_id"]): item
        for item in parameter_mapping().get("reaction_correlations", ())
    }


def _parameter_domain(domain_id: object) -> tuple[float, float] | None:
    for domain in parameter_mapping().get("domains", ()):
        if domain.get("domain_id") == domain_id:
            lower = domain.get("temperature_min", {}).get("magnitude")
            upper = domain.get("temperature_max", {}).get("magnitude")
            if lower is not None and upper is not None:
                return float(lower), float(upper)
    return None


def _engine_reaction_records(
    request: dict[str, object], reaction_values: dict[str, float]
) -> list[dict[str, object]]:
    """Normalize source forms to native polynomial fields without EOS conversion."""
    selected_specs = _reaction_specifications()
    selected_values = _selected_reactions()
    adopted = reaction_values == selected_values
    records = []
    for index, row in enumerate(request["reaction_system"]["reaction_matrix"]):
        reaction_id = f"R{index + 1}"
        source = dict(EXPECTED_REACTION_CORRELATIONS[reaction_id])
        prefix = f"reaction:{reaction_id}:correlation:"
        effective = {
            identity[len(prefix):]: float(value)
            for identity, value in reaction_values.items()
            if identity.startswith(prefix)
        }
        selected_spec = selected_specs.get(reaction_id)
        if adopted and selected_spec is not None:
            effective = {
                str(coefficient["name"]): float(coefficient["value"]["magnitude"])
                for coefficient in selected_spec.get("coefficients", ())
            }
        source.update(effective)
        common = reaction_id in {"R4", "R5"} or (
            reaction_id == "R2" and bool(effective)
        )
        if reaction_id == "R5":
            correlation = {
                "a": -math.log(10.0) * source["b" if "b" in source else "b_k"],
                "b": -math.log(10.0) * source["a_k"],
                "c": 0.0,
                "d": -math.log(10.0) * source["c_per_k"],
            }
        else:
            correlation = {
                "a": source["a"],
                "b": source["b_k"],
                "c": source.get("c", 0.0),
                "d": source.get("d_per_k", 0.0),
            }
        if correlation["c"]:
            correlation["a"] += correlation["c"] * math.log(
                REACTION_REFERENCE_TEMPERATURE_K
            )
        selected_domain = (
            _parameter_domain(selected_spec.get("candidate_domain_id"))
            if selected_spec is not None and (adopted or effective)
            else None
        )
        if selected_domain is not None:
            temperature_min, temperature_max = selected_domain
        elif reaction_id in {"R4", "R5"}:
            temperature_min, temperature_max = (293.15, 323.15) if reaction_id == "R4" else (273.15, 323.15)
        else:
            temperature_min, temperature_max = 273.15, 498.15
        correlation.update({
            "reference_temperature": REACTION_REFERENCE_TEMPERATURE_K,
            "temperature_min": temperature_min,
            "temperature_max": temperature_max,
            "standard_state_id": COMMON_SOURCE_STANDARD_STATE_ID if common else RAW_SOURCE_STANDARD_STATE_ID,
        })
        records.append({
            "reaction_id": reaction_id,
            "stoichiometry": list(row),
            "engine_correlation": correlation,
            "engine_reference": {
                "source_basis": (
                    "CommonMolalityInfiniteDilution" if common
                    else "RawMoleFractionInfiniteDilution"
                ),
                "reference_pressure_pa": REACTION_REFERENCE_PRESSURES[reaction_id],
            },
            "parameter_role": "selected" if adopted and selected_spec is not None else "candidate",
        })
    return records


def _reaction_correlation(record: dict[str, object], reaction_id: str) -> object:
    payload = record.get("engine_correlation")
    if not isinstance(payload, dict):
        raise ReferenceBasisUnavailable(
            f"{reaction_id} has no accepted EOS-standard-state reference correlation"
        )
    required = (
        "a", "b", "c", "d", "reference_temperature", "temperature_min",
        "temperature_max", "standard_state_id",
    )
    if any(key not in payload for key in required):
        raise ReferenceBasisUnavailable(f"{reaction_id} reference correlation is incomplete")
    standard_state_id = payload["standard_state_id"]
    if not isinstance(standard_state_id, str) or not standard_state_id:
        raise ReferenceBasisUnavailable(f"{reaction_id} reference basis does not match the Engine")
    return equilibrium.ReactionLogPolynomial(
        *(float(payload[key]) for key in required[:-1]),
        standard_state_id,
    )


def _neutral_reference_data(request: dict[str, object]) -> tuple[str, dict[str, float]]:
    system = request["reaction_system"]
    source = system.get("source_standard_state", {})
    solvent_composition = source.get("solvent_composition", ())
    solvent = "water"
    if len(solvent_composition) == len(COMPONENT_IDS):
        solvent = COMPONENT_IDS[max(range(len(COMPONENT_IDS)), key=solvent_composition.__getitem__)]
    charges = dict(zip(COMPONENT_IDS, system.get("charges", ()), strict=True))
    ratios = {
        component: 1.0 if charges[component] == 0 else 0.0
        for component in COMPONENT_IDS
        if component != solvent
    }
    for pair in source.get("ion_pairs", ()):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ReferenceBasisUnavailable("source ion-pair reference rows are malformed")
        components, stoichiometry = pair
        if len(components) != 2 or len(stoichiometry) != 2:
            raise ReferenceBasisUnavailable("source ion-pair reference rows are incomplete")
        for component, coefficient in zip(components, stoichiometry, strict=True):
            if component == solvent or component not in ratios:
                raise ReferenceBasisUnavailable("source ion-pair reference component is invalid")
            coefficient = float(coefficient)
            if not math.isfinite(coefficient) or coefficient <= 0.0:
                raise ReferenceBasisUnavailable("source ion-pair stoichiometry is invalid")
            ratios[component] += coefficient
    if any(value <= 0.0 or not math.isfinite(value) for value in ratios.values()):
        raise ReferenceBasisUnavailable("neutral source reference ratios must be positive")
    if abs(math.fsum(charges[component] * value for component, value in ratios.items())) > 1.0e-12:
        raise ReferenceBasisUnavailable("neutral source reference ratios are not charge balanced")
    # The dilution vector is a direction in the neutral solute subspace.  A
    # one-eighth-scale source ion-pair vector keeps the native 1e-6..1e-14
    # witness ladder inside its finite-limit tolerance for this nine-species
    # parameter set while preserving positivity and charge balance exactly.
    return solvent, {
        component: value * NEUTRAL_REFERENCE_RATIO_SCALE
        for component, value in ratios.items()
    }


def _neutral_reference(request: dict[str, object]) -> equilibrium.NeutralReference:
    solvent, ratios = _neutral_reference_data(request)
    return equilibrium.NeutralReference(
        solvent=solvent,
        solute_molality_ratios=ratios,
        standard_molality_mol_per_kg=1.0,
    )


def _reaction_reference(
    record: dict[str, object], reaction_id: str
) -> equilibrium.ReactionReference:
    basis_type = equilibrium.ReferenceSourceBasis
    payload = record.get("engine_reference") or record.get("reference")
    payload = payload if isinstance(payload, dict) else {}
    basis_name = str(
        payload.get(
            "source_basis",
            payload.get("basis", record.get("reference_source_basis", "CommonMolalityInfiniteDilution")),
        )
    )
    basis = getattr(basis_type, basis_name.rsplit(".", 1)[-1], None)
    if basis is None:
        raise ReferenceBasisUnavailable(f"{reaction_id} source basis {basis_name!r} is unavailable")
    pressure = payload.get(
        "reference_pressure_pa",
        record.get("reference_pressure_pa", REACTION_REFERENCE_PRESSURES.get(reaction_id)),
    )
    if pressure is not None:
        pressure = float(pressure)
        if not math.isfinite(pressure) or pressure <= 0.0:
            raise ReferenceBasisUnavailable(f"{reaction_id} reference pressure is invalid")
    return equilibrium.ReactionReference(basis, reference_pressure_pa=pressure)


def _reaction_records(request: dict[str, object]) -> list[dict[str, object]]:
    system = request["reaction_system"]
    engine_records = system.get("engine_reactions")
    if not isinstance(engine_records, list):
        raise ReferenceBasisUnavailable(
            "current request lacks normalized reaction reference records"
        )
    return engine_records


def _problem_from_request(request: dict[str, object], anchor: Anchor | None = None) -> object:
    system = request["reaction_system"]
    species = tuple(system.get("species_ids", ()))
    if species != COMPONENT_IDS:
        raise ValueError("MEA component order does not match the application contract")
    feed_values = tuple(float(value) for value in system["feed_amounts_mol"])
    if len(feed_values) != len(COMPONENT_IDS) or not all(math.isfinite(v) and v > 0 for v in feed_values):
        raise ValueError("MEA feed amounts must be finite and strictly positive")
    feed = equilibrium.Amounts(dict(zip(COMPONENT_IDS, feed_values, strict=True)))
    continuation = request.get("continuation") or {}
    state = continuation.get("state") or {}
    states = {item.get("role"): item for item in state.get("phases", ())}
    phases = []
    for declared in request["phases"]:
        identity = declared["identity"]
        state_phase = states.get(declared["fluid_role"], {})
        support = tuple(declared.get("support", {}).get("component_ids", ()))
        if declared.get("support", {}).get("kind") == "all_components":
            support = COMPONENT_IDS
        if not support:
            support = tuple(state_phase.get("supported_component_ids", ()))
        guess = list(state_phase.get("mole_fractions", ()))
        if anchor is not None and declared["fluid_role"] == "liquid":
            guess = list(anchor.mole_fractions)
        if not support or len(guess) != len(support):
            raise ValueError(f"phase {identity} lacks a complete composition guess")
        amount = equilibrium.Pinned(0.0) if declared["amount_role"] == "incipient" else equilibrium.Free()
        phases.append(equilibrium.Phase(
            identity, support=support, kind=declared["fluid_role"], amount=amount,
            composition_guess=guess,
        ))
    reactions = []
    matrix = system.get("reaction_matrix", ())
    records = _reaction_records(request)
    if len(matrix) != len(records):
        raise ReferenceBasisUnavailable("reaction reference rows are incomplete")
    for index, (row, record) in enumerate(zip(matrix, records, strict=True)):
        reaction_id = str(record.get("reaction_id", f"R{index + 1}"))
        stoichiometry = dict(zip(COMPONENT_IDS, map(float, row), strict=True))
        correlation = _reaction_correlation(record, reaction_id)
        reference = _reaction_reference(record, reaction_id)
        reactions.append(
            equilibrium.Reaction(
                stoichiometry,
                name=reaction_id,
                correlation=correlation,
                reference=reference,
            )
        )
    for reaction in reactions:
        for phase in phases:
            supported = set(phase.support or ())
            if phase.kind == "vapor" and all(name in supported for name, value in reaction.stoichiometry.items() if value):
                raise ValueError("reaction_phase_support_mismatch")
    temperature = float(request["temperature"]["value"])
    pressure_data = request["pressure"]
    lower, upper = map(float, pressure_data.get("bounds", (1.0, 1.0e7)))
    if pressure_data["role"] == "fixed":
        pressure_value = float(pressure_data["value"])
        pressure = pressure_value
    else:
        pressure_value = anchor.pressure_pa if anchor is not None else float(pressure_data.get("initial", 0.0))
        pressure = equilibrium.Free(pressure_value)
    if not lower <= pressure_value <= upper:
        raise ValueError("pressure_outside_packet")
    problem_kwargs = {
        "phases": phases, "T": temperature, "P": pressure, "feed": feed,
        "reactions": reactions,
        "standard_gibbs_j_per_mol": system.get("standard_gibbs_j_per_mol", ()),
        "topology_declared": True,
    }
    problem_kwargs["neutral_reference"] = _neutral_reference(request)
    return equilibrium.Problem(**problem_kwargs)


def _reaction_identity(reactions: dict[str, float]) -> str:
    return hashlib.sha256(
        json.dumps(reactions, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _selected_reactions() -> dict[str, float]:
    values: dict[str, float] = {}
    for reaction in parameter_mapping().get("reaction_correlations", ()):
        for coefficient in reaction.get("coefficients", ()):
            identity = coefficient.get("identity")
            if isinstance(identity, str) and identity.startswith("reaction:"):
                values[identity] = float(coefficient["value"]["magnitude"])
    return values


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
        "parameter_runtime_defaults": MODEL_RUNTIME_DEFAULTS,
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


def _phase_payload(problem: object, result: object, index: int, width: int) -> dict[str, object]:
    declared = problem.phases[index]
    support = tuple(declared.support or COMPONENT_IDS)
    flat = result.mole_fractions[index * width:(index + 1) * width]
    positions = {name: COMPONENT_IDS.index(name) for name in support}
    if (
        len(flat) != width
        or index >= len(result.amounts)
        or index >= len(result.molar_densities)
        or index >= len(result.packing_fractions)
        or not result.pressure
    ):
        return {
            "identity": declared.name, "role": declared.kind, "support": list(support),
            "pressure_pa": None, "amount_mol": None, "molar_density_mol_m3": None,
            "packing_fraction": None, "mechanical_class": "mechanical_class_unavailable",
            "mole_fractions": [], "molar_volume_m3_per_mol": None,
        }
    mole_fractions = [float(flat[positions[name]]) for name in support]
    rho = float(result.molar_densities[index])
    pressure = result.pressure[index] if index < len(result.pressure) else result.pressure[0]
    return {
        "identity": declared.name,
        "role": declared.kind,
        "support": list(support),
        "pressure_pa": float(pressure),
        "amount_mol": float(result.amounts[index]),
        "molar_density_mol_m3": rho,
        "packing_fraction": float(result.packing_fractions[index]),
        "mechanical_class": "mechanical_class_unavailable",
        "mole_fractions": mole_fractions,
        "molar_volume_m3_per_mol": 1.0 / rho,
    }


def _stop_code(result: object) -> tuple[str, str]:
    if getattr(result, "success", False):
        return "", ""
    convergence = getattr(result, "convergence", None)
    stop = getattr(getattr(convergence, "stop", None), "name", "not_converged").lower()
    code = stop if stop in {"infeasible", "left_domain", "singular", "nonfinite", "stalled", "budget_exhausted"} else "not_converged"
    return code, str(getattr(result, "message", "equilibrium solve failed"))


def _output_value(output: dict[str, object], problem: object, result: object, phases: list[dict[str, object]]) -> float | None:
    selector = output.get("selector")
    if selector == "system.pressure":
        return float(result.pressure[0])
    phase_name = output.get("phase_identity")
    if not isinstance(phase_name, str):
        raise ValueError(f"output {output.get('identity')} lacks phase identity")
    index = next(i for i, phase in enumerate(problem.phases) if phase.name == phase_name)
    phase = phases[index]
    values = phase["mole_fractions"]
    coefficients = output.get("coefficients", ())
    value = math.fsum(float(c) * float(v) for c, v in zip(coefficients, values, strict=True))
    if selector == "phase.partial_pressure":
        value *= float(phase["pressure_pa"])
    elif selector != "phase.mole_fraction":
        raise ValueError(f"unsupported output selector {selector}")
    return value


def _central_action_rows(model: object, problem: object, result: object, phases: list[dict[str, object]]) -> list[dict[str, object]]:
    observables = []
    identities = []
    for phase_index, phase in enumerate(problem.phases):
        support = tuple(phase.support or COMPONENT_IDS)
        for component in support:
            observables.append(equilibrium.SolvedStateObservable(
                equilibrium.SolvedStateObservableKind.PhaseResidualChemicalPotentialOverRt,
                phase_index, COMPONENT_IDS.index(component),
            ))
            identities.append(f"phase:{phase.name}:residual-chemical-potential-over-rt:{component}")
        observables.append(equilibrium.SolvedStateObservable(
            equilibrium.SolvedStateObservableKind.PhaseProperty,
            phase_index, property=epcsaft.PropertyObservable.TotalEnthalpy,
        ))
        identities.append(f"phase:{phase.name}:total-enthalpy")
    direction = equilibrium.SolvedStateActionDirection(
        0.0, 0.0, [0.0] * len(model.component_ids), []
    )
    batch = equilibrium.solved_state_actions(
        equilibrium.compile_problem(model, problem), result,
        equilibrium.SolvedStateActionRequest(observables, [direction]),
    )
    rows = []
    for identity, item in zip(identities, batch.results, strict=True):
        status = item.status.name
        value = None if item.value is None else float(item.value)
        row = {
            "identity": identity, "value": value, "status": status, "unit": item.unit,
            "action": None if item.action is None else float(item.action), "jacobian": None,
        }
        rows.append(row)
        if identity.endswith(":total-enthalpy") and value is not None:
            phase_name = identity.split(":", 2)[1]
            phase = next(item for item in phases if item["identity"] == phase_name)
            phase["total_molar_enthalpy_j_per_mol"] = value
    diagnostics = {}
    for name in (
        "equation_count", "state_dimension", "maximum_energy_order", "state_factorizations",
        "linear_solves", "rank", "condition_estimate", "maximum_linear_residual",
        "central_residual", "central_floor",
    ):
        value = getattr(batch.diagnostics, name)
        diagnostics[name] = getattr(value, "name", value)
    rows.append({
        "identity": "action-batch-diagnostics", "value": None, "status": "diagnostic",
        "unit": "", "diagnostics": diagnostics,
    })
    return rows


def _snapshot_from_result(model: object, problem: object, request: dict[str, object], result: object) -> dict[str, object]:
    width = len(model.component_ids)
    phases = [_phase_payload(problem, result, i, width) for i in range(result.phase_count)]
    code, diagnostic = _stop_code(result)
    predictions: dict[str, float] = {}
    rows: list[dict[str, object]] = []
    for output in request.get("outputs", ()):
        identity = str(output["identity"])
        try:
            value = _output_value(output, problem, result, phases) if result.success else None
            status = "available" if value is not None and math.isfinite(value) else "unavailable"
            if status == "available":
                predictions[identity] = value
        except Exception as exc:
            value, status = None, f"unavailable:{type(exc).__name__}"
        rows.append({"identity": identity, "value": value, "status": status, "unit": output.get("unit", "")})
    action_diagnostic = ""
    compiled_point_evaluation: dict[str, object] | None = None
    validation_errors: list[str] = []
    if result.success:
        balance = request.get("reaction_system", {}).get("balance_matrix", ())
        targets = request.get("reaction_system", {}).get("conserved_totals", ())
        charges = request.get("reaction_system", {}).get("charges", ())
        def full_composition(phase: dict[str, object]) -> list[float]:
            values = [0.0] * len(COMPONENT_IDS)
            for component, value in zip(phase["support"], phase["mole_fractions"], strict=True):
                values[COMPONENT_IDS.index(component)] = float(value)
            return values
        if balance and targets:
            for row, target in zip(balance, targets, strict=True):
                actual = math.fsum(
                    float(phase["amount_mol"]) * sum(
                        float(coefficient) * float(value)
                        for coefficient, value in zip(row, full_composition(phase), strict=True)
                    ) for phase in phases if phase["amount_mol"] is not None
                )
                if abs(actual - float(target)) > 1e-7 * max(1.0, abs(float(target))):
                    validation_errors.append("material_balance")
        if charges:
            actual_charge = math.fsum(
                float(phase["amount_mol"]) * sum(
                    float(charge) * float(value)
                    for charge, value in zip(charges, full_composition(phase), strict=True)
                ) for phase in phases if phase["amount_mol"] is not None
            )
            if abs(actual_charge) > 1e-7:
                validation_errors.append("charge_balance")
        lower, upper = map(float, request.get("pressure", {}).get("bounds", (1.0, 1.0e7)))
        if any(not lower <= float(value) <= upper for value in result.pressure):
            validation_errors.append("pressure_outside_packet")
        try:
            rows.extend(_central_action_rows(model, problem, result, phases))
        except Exception as exc:
            action_diagnostic = f"{type(exc).__name__}: {exc}"
        try:
            point = equilibrium.compile_problem(model, problem).evaluate(result.coordinates)
            raw_values = [float(value) for value in point.values]
            compiled_point_evaluation = {
                "raw_stationarity": raw_values,
                "raw_stationarity_max_abs": max(map(abs, raw_values), default=0.0),
                "objective": float(point.objective),
                "floor": float(point.floor),
            }
        except Exception as exc:
            compiled_point_evaluation = {
                "status": "unavailable",
                "diagnostic": f"{type(exc).__name__}: {exc}",
            }
    evidence = [
        ["success", bool(result.success)], ["message", str(result.message)],
        ["solver_status", str(result.solver_status)],
        ["requested_tolerance_met", result.requested_tolerance_met],
        ["residuals", [float(value) for value in result.residuals]],
        ["classified_residuals", [float(value) for value in result.classified_residuals]],
        ["iterations/evaluations/hessian_calls", [int(result.iterations), int(result.evaluations), int(result.hessian_calls)]],
        ["jacobian_rank/generic_nullity", [int(result.jacobian_rank), int(result.generic_nullity)]],
        ["reduced_hessian_minimum", float(result.reduced_hessian_minimum)],
        ["topology_event", getattr(result.topology_event, "name", str(result.topology_event))],
    ]
    reference_diagnostics = getattr(result, "neutral_reference_diagnostics", None)
    if reference_diagnostics is not None:
        evidence.append(["neutral_reference_diagnostics", _jsonable(reference_diagnostics)])
    if action_diagnostic:
        evidence.append(["action_batch", action_diagnostic])
    if compiled_point_evaluation is not None:
        evidence.append(["compiled_point_evaluation", compiled_point_evaluation])
    if validation_errors:
        evidence.append(["validation_errors", validation_errors])
    total_molar = next(
        (phase.get("total_molar_enthalpy_j_per_mol") for phase in phases if phase["role"] == "liquid"),
        None,
    )
    liquid_amount = next((phase["amount_mol"] for phase in phases if phase["role"] == "liquid"), None)
    return {
        "status": "evaluated" if result.success and not validation_errors else "non_evaluable",
        "failure_code": validation_errors[0] if validation_errors else code,
        "failure_diagnostic": diagnostic,
        "predictions": predictions,
        "rows": rows,
        "evidence": evidence,
        "phases": phases,
        "solver_status": str(result.solver_status),
        "physical_status": "",
        "eos_domain_status": "",
        "total_enthalpy_j": None if total_molar is None or liquid_amount is None else total_molar * liquid_amount,
        "amount_mol": liquid_amount,
        "molar_density_mol_m3": next((p["molar_density_mol_m3"] for p in phases if p["role"] == "liquid"), None),
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
    request: dict[str, object] | None = None,
) -> SolveSnapshot:
    """Run one Engine call in a forked child so timeout can kill native code."""
    if active_parameters is not None:
        return SolveSnapshot(
            status="unavailable",
            failure_code="reaction_action_unavailable",
            failure_diagnostic=(
                "the current Engine exposes EOS active parameters only; "
                "reaction-correlation actions are unavailable"
            ),
        )
    if not hasattr(os, "fork"):
        raise RuntimeError("hard solver timeout requires POSIX fork support")
    read_fd, write_fd = os.pipe()
    child = os.fork()
    if child == 0:
        os.close(read_fd)
        try:
            try:
                result = equilibrium.solve_equilibrium(model, problem)
                payload = {"ok": True, "result": _snapshot_from_result(model, problem, request or {}, result)}
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
            waited, _status = os.waitpid(child, os.WNOHANG)
            if waited == 0:
                os.kill(child, signal.SIGKILL)
                os.waitpid(child, 0)
        except ChildProcessError:
            pass
    if not chunks:
        raise RuntimeError("solver child exited without a result")
    payload = json.loads(b"".join(chunks))
    if not payload.get("ok"):
        error = str(payload.get("error", "solver child failed"))
        if "reference_unavailable" in error:
            raise ReferenceBasisUnavailable(error)
        raise RuntimeError(error)
    return _snapshot_from_payload(payload["result"])


def attempt_plan(
    temperature_c: int, loading: float, anchors: list[Anchor], solved_pressure: bool = False
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
    if solved_pressure:
        plan.append(("speciated-liquid-start", None))
    plan.extend(("cross-temperature-anchor", a) for a in cross[:2])
    return plan[:4]


def _speciated_liquid_anchor(
    model: epcsaft.Mixture, request: dict[str, object], temperature_c: int, loading: float,
    timeout_s: float,
) -> tuple[Anchor | None, str, str]:
    """Speciate the liquid alone at the packet pressure seed to replace an unspeciated guess.

    Packet liquid guesses can carry molecular CO2 far above its speciated value, which puts
    the Engine's pinned-vapor pressure seed at the saturation pressure of the wrong liquid.
    """
    liquid = copy.deepcopy(request)
    liquid["phases"] = [p for p in liquid["phases"] if p["fluid_role"] == "liquid"]
    liquid["pressure"] = {
        **liquid["pressure"], "role": "fixed", "value": float(liquid["pressure"].get("initial", 0.0))
    }
    try:
        snapshot = _solve_in_child(model, _problem_from_request(liquid), timeout_s)
    except Exception as exc:
        return None, "speciation_failed", f"{type(exc).__name__}: {exc}"
    if snapshot.status != "evaluated":
        return None, snapshot.failure_code or "speciation_failed", snapshot.failure_diagnostic
    return liquid_anchor(snapshot, temperature_c, loading), "", ""


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
        temperature_c, float(base["reaction_system"]["feed_amounts_mol"][0]), anchors,
        base["pressure"]["role"] != "fixed",
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
        if kind == "speciated-liquid-start":
            clock = perf_counter()
            anchor, code, diagnostic = _speciated_liquid_anchor(
                model, base, temperature_c, float(base["reaction_system"]["feed_amounts_mol"][0]),
                max(0.01, deadline - clock),
            )
            if anchor is None:
                attempts.append({
                    "kind": kind, "anchor": None, "wall_s": perf_counter() - clock,
                    "status": "non_evaluable", "failure_code": code, "failure_diagnostic": diagnostic,
                })
                continue
        candidate = copy.deepcopy(base)
        try:
            problem = _problem_from_request(candidate, anchor)
        except ReferenceBasisUnavailable as exc:
            attempts.append({
                "kind": kind, "anchor": None if anchor is None else [anchor.temperature_c, anchor.loading],
                "wall_s": 0.0, "status": "unavailable", "failure_code": exc.code,
                "failure_diagnostic": str(exc),
            })
            break
        except ValueError as exc:
            message = str(exc)
            attempts.append({
                "kind": kind, "anchor": None if anchor is None else [anchor.temperature_c, anchor.loading],
                "wall_s": 0.0, "status": "unavailable",
                "failure_code": message if message in {"pressure_outside_packet", "reaction_phase_support_mismatch"} else "input_error",
                "failure_diagnostic": message,
            })
            break
        signature = (
            None if anchor is None else tuple(round(value, 12) for value in anchor.mole_fractions),
            None if anchor is None else round(anchor.molar_volume_m3_per_mol, 15),
            None if anchor is None else round(anchor.pressure_pa, 6),
        )
        if signature in seen:
            continue
        seen.add(signature)
        clock = perf_counter()
        try:
            result = _solve_in_child(model, problem, max(0.01, deadline - clock), request=base)
            status = result.status
            code, diagnostic = result.failure_code, result.failure_diagnostic
        except EvaluationTimeout as exc:
            result = None
            status, code, diagnostic = "timeout", "evaluation_timeout", str(exc)
        except ReferenceBasisUnavailable as exc:
            result = None
            status, code, diagnostic = "unavailable", exc.code, str(exc)
        except Exception as exc:
            result = None
            status, code, diagnostic = (
                "exception",
                "engine_exception",
                f"{type(exc).__name__}: {exc}",
            )
        evaluated = result is not None and status == "evaluated"
        attempt = {
            "kind": kind,
            "anchor": None
            if anchor is None
            else [anchor.temperature_c, anchor.loading],
            "wall_s": perf_counter() - clock,
            "status": "evaluated" if evaluated else status,
            "failure_code": "" if evaluated else code,
            "failure_diagnostic": "" if evaluated else diagnostic,
        }
        if result is not None:
            attempt["solver_status"] = result.solver_status
            attempt["evidence"] = result.evidence
        attempts.append(attempt)
        if evaluated:
            return result, attempts
        if code == "reference_basis_unavailable":
            break
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
    model_fingerprint = str(
        getattr(model, "parameter_fingerprint", f"sha256:{sha256(PARAMETERS)}")
    )
    corrected = corrected_request(request, reactions)
    provenance_data["parameter_role"] = (
        "selected"
        if reactions == _selected_reactions()
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
        "rows": [],
        "anchor": None,
        "total_enthalpy_j": None,
        "amount_mol": None,
        "cache_hit": False,
    }
    if not evaluated and attempts:
        failed_attempt = attempts[-1]
        if "solver_status" in failed_attempt:
            record["solver_status"] = failed_attempt["solver_status"]
        if "evidence" in failed_attempt:
            record["evidence"] = failed_attempt["evidence"]
    if evaluated:
        record["predictions"] = result.predictions
        record["solver_status"] = result.solver_status
        record["physical_status"] = result.physical_status
        record["eos_domain_status"] = result.eos_domain_status
        record["phases"] = result.phases
        record["rows"] = result.rows
        anchor = liquid_anchor(result, temperature_c, loading)
        record["anchor"] = anchor.__dict__
        record["evidence"] = result.evidence
        record["total_enthalpy_j"] = result.total_enthalpy_j
        record["amount_mol"] = result.amount_mol
        record["molar_density_mol_m3"] = result.molar_density_mol_m3
    write_json(path, record)
    return record
