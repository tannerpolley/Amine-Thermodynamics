"""Fixed-reference MEA declaration and source reaction basis."""

from __future__ import annotations

import copy
import csv
from dataclasses import dataclass
import gzip
import json
import math
from pathlib import Path

from .fit import compare_rows
from .model import (
    CAMPAIGN_ARCHIVE,
    P_REF,
    REPORTED,
    ROOT,
    Route,
    evaluate,
    parameter_values,
    with_parameter_values,
)
from MEA.common.mea_source_contracts import (
    EXPECTED_REACTION_CORRELATIONS,
    REACTION_CONTRACT_PATH,
)
from MEA.common.retained_results import read
from MEA.solvent_specification import SolventSpecification
import epcsaft
from epcsaft import equilibrium, regression as reg

BUNDLE = ROOT / "analyses/mea_parameter_bundle"
HISTORICAL_SPEC = BUNDLE / "results/adoption-297/historical-spec/MEA.toml"
SALT_FIT = BUNDLE / "results/salt-anchored-435/MEA/F4"
EXPANDED_FIT = ROOT / "analyses/round_7/results/E"
STATE_PACKET = BUNDLE / "data/input/state-packet.json.gz"
STATE_PACKET_SCHEMA = "mea-parameter-estimation-observations-compact"
STATE_PACKET_SCHEMA_VERSION = 1
STATE_PACKET_REQUEST_FIELDS = (
    "continuation",
    "feed",
    "identity",
    "intensive_boundaries",
    "outputs",
    "phase_reactions",
    "phases",
    "pressure",
    "reaction_phase_ids",
    "reaction_system",
    "temperature",
)
COMPONENT_IDS = (
    "carbon-dioxide",
    "monoethanolamine",
    "water",
    "protonated-monoethanolamine",
    "carbamate-anion",
    "bicarbonate-anion",
    "carbonate-anion",
    "hydronium-cation",
    "hydroxide-anion",
)
CENSUS_FEED = (9.7292821, 76.9751925)
CENSUS_T = (313.15, 318.15, 333.15, 353.15, 373.15, 393.15)
CENSUS_A = (1e-5, 0.05, 0.1, 0.2, 0.256, 0.3, 0.4, 0.5, 0.6)
# Shell-modified Born constants of the adopted configuration
# (data/reference/MEA/manifests/reactive_vle_model_configurations.json).
REACTION_REFERENCE_PRESSURES = {
    "R1": None,
    "R2": None,
    "R3": None,
    "R4": 1.0e5,
    "R5": 1.0e5,
}
COMMON_SOURCE_STANDARD_STATE_ID = "aqueous-molality-infinite-dilution-water-v1"
RAW_SOURCE_STANDARD_STATE_ID = "aqueous-mole-fraction-infinite-dilution-water-v1"
NEUTRAL_REFERENCE_RATIO_SCALE = 0.125
# The source R1--R3 records use the historical ln(T/(1 K)) convention.  The
# native polynomial requires its reference temperature to lie inside the
# admitted interval, so preserve the source law by shifting ``a`` to this
# source-contract pivot before constructing ReactionLogPolynomial.
REACTION_REFERENCE_TEMPERATURE_K = 313.15


def source_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    return gzip.decompress(data) if path.name.endswith(".json.gz") else data


def load_state_packet(path: Path = STATE_PACKET) -> dict[str, object]:
    """Load and expand the compact retained packet with strict references."""
    return expand_state_packet(json.loads(source_bytes(path)))


def expand_state_packet(document: object) -> dict[str, object]:
    """Expand an already decoded compact packet with strict references."""
    if not isinstance(document, dict) or set(document) != {
        "schema",
        "schema_version",
        "source",
        "metadata",
        "request_tables",
        "observations",
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
        if not isinstance(row, dict) or set(row) != {
            "family",
            "identity",
            "multiplier",
            "request",
            "targets",
        }:
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
        if document["metadata"].get("source_corrections") == 152 and any(
            target["source_identity"] in {"Hilliard2008", "Xu2011"} for target in row["targets"]
        ):
            if (request.get("feed") or {}).get(
                "generation"
            ) != "source-corrections-152" or "analytical_feed_contract" not in request["reaction_system"]:
                raise ValueError("Corrected Hilliard/Xu packet lacks the required source-feed contract")
        expanded.append(
            {
                "family": row["family"],
                "identity": row["identity"],
                "multiplier": row["multiplier"],
                "request": request,
                "targets": copy.deepcopy(row["targets"]),
            }
        )
    return {**copy.deepcopy(document["metadata"]), "observations": expanded}


class ReferenceBasisUnavailable(RuntimeError):
    code = "reference_basis_unavailable"


def reaction_values(mapping: dict[str, object]) -> dict[str, float]:
    return {k: v for k, v in parameter_values(mapping).items() if k.startswith("reaction:")}


def source_feed_request(template: dict, source: dict) -> dict:
    """Measured source coordinates on the immutable OLD analytical-feed mass/seed basis."""
    request = copy.deepcopy(template)
    system = request["reaction_system"]
    frozen = load_state_packet()["observations"][0]["request"]["reaction_system"]
    if system["species_ids"] != list(COMPONENT_IDS) or any(
        system[key] != frozen[key] for key in ("molar_masses_kg_per_mol", "reaction_matrix", "balance_matrix")
    ):
        raise ValueError("Frozen analytical-feed basis/order/matrix mismatch")
    masses = dict(zip(COMPONENT_IDS, system["molar_masses_kg_per_mol"], strict=True))
    loading = float(source["CO2_loading"])
    temperature_c = float(source["temperature_reported_C"])
    molality = (
        float(source["source_molality_mol_per_kg_water"])
        if source["source_key"] in {"Hilliard2008", "Xu2011"}
        else None
    )
    if molality is not None:
        if float(source["temperature_measured_C"]) != temperature_c:
            raise ValueError("Nominal-only or inconsistent measured temperature")
        water = 1.0 / (molality * masses["water"])
        basis = "source_molality"
    else:
        fraction = float(source["MEA_weight_fraction"])
        if not 0 < fraction < 1:
            raise ValueError("Invalid verified source mass fraction")
        water = (1 - fraction) * masses["monoethanolamine"] / (fraction * masses["water"])
        basis = "source_mass_fraction"
    if not all(math.isfinite(value) for value in (loading, temperature_c, water)) or loading < 0 or water <= 0:
        raise ValueError("Invalid source analytical amounts/temperature")
    analytical = [loading, 1.0, water, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    extents = [1e-5, 1e-4, 1e-5, -1e-5, -1e-5]
    increment = [
        math.fsum(row[i] * extent for row, extent in zip(system["reaction_matrix"], extents, strict=True))
        for i in range(9)
    ]
    system["feed_amounts_mol"] = [amount + change for amount, change in zip(analytical, increment, strict=True)]
    system["conserved_totals"] = [
        math.fsum(c * amount for c, amount in zip(row, system["feed_amounts_mol"], strict=True))
        for row in system["balance_matrix"]
    ]
    system["analytical_feed_contract"] = {
        "basis": basis,
        "source_coordinates": copy.deepcopy(source),
        "neutral_analytical_amounts_mol": analytical,
        "seed_extents_mol": extents,
        "molar_masses_kg_per_mol": list(system["molar_masses_kg_per_mol"]),
        "temperature_measured_C": temperature_c,
    }
    request["temperature"]["value"] = temperature_c + 273.15
    request["feed"] = {
        "generation": "source-corrections-152",
        "source": "reaction_system.analytical_feed_contract",
    }
    return request


def corrected_request(
    request: dict[str, object],
    mapping: dict,
) -> dict[str, object]:
    """Normalize phase model metadata without inventing source-to-EOS reactions."""
    corrected = copy.deepcopy(request)
    values_by_identity = reaction_values(mapping)
    for phase in corrected.get("phases", ()):
        phase.setdefault("model", {})["kind"] = "eos"
        phase["model"]["reference_id"] = "installed-eos"
    if values_by_identity:
        records = corrected.get("reaction_system", {}).get("equilibrium_constants", ())
        for index, record in enumerate(records):
            reaction_id = f"R{index + 1}"
            metadata = record[6] if len(record) >= 7 and isinstance(record[6], dict) else {}
            reaction_id = str(metadata.get("reaction_id", reaction_id))
            prefix = f"reaction:{reaction_id}:correlation:"
            selected = {
                identity[len(prefix) :]: float(value)
                for identity, value in values_by_identity.items()
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
                metadata["effective_parameter_role"] = "candidate"
                metadata["effective_coefficient_identities"] = [
                    f"reaction:{reaction_id}:correlation:{name}" for name in selected
                ]
                metadata["effective_coefficient_values"] = selected
            identities = metadata.get("coefficient_identities", ())
            values = list(metadata.get("coefficient_values", ()))
            for position, identity in enumerate(identities):
                if identity in values_by_identity and position < len(values):
                    values[position] = values_by_identity[identity]
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
                corrected,
                values_by_identity,
                mapping,
            )
    return corrected


def _reaction_specifications(
    mapping: dict,
) -> dict[str, dict[str, object]]:
    return {str(item["reaction_id"]): item for item in mapping.get("reaction_correlations", ())}


def _parameter_domain(domain_id: object, mapping: dict) -> tuple[float, float] | None:
    for domain in mapping.get("domains", ()):
        if domain.get("domain_id") == domain_id:
            lower = domain.get("temperature_min", {}).get("magnitude")
            upper = domain.get("temperature_max", {}).get("magnitude")
            if lower is not None and upper is not None:
                return float(lower), float(upper)
    return None


def _engine_reaction_records(
    request: dict[str, object],
    reaction_values: dict[str, float],
    mapping: dict,
) -> list[dict[str, object]]:
    """Normalize source forms to native polynomial fields without EOS conversion."""
    selected_specs = _reaction_specifications(mapping)
    records = []
    for index, row in enumerate(request["reaction_system"]["reaction_matrix"]):
        reaction_id = f"R{index + 1}"
        source = dict(EXPECTED_REACTION_CORRELATIONS[reaction_id])
        prefix = f"reaction:{reaction_id}:correlation:"
        effective = {
            identity[len(prefix) :]: float(value)
            for identity, value in reaction_values.items()
            if identity.startswith(prefix)
        }
        selected_spec = selected_specs.get(reaction_id)
        source.update(effective)
        common = reaction_id in {"R4", "R5"} or (reaction_id == "R2" and bool(effective))
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
            correlation["a"] += correlation["c"] * math.log(REACTION_REFERENCE_TEMPERATURE_K)
        selected_domain = (
            _parameter_domain(selected_spec.get("candidate_domain_id"), mapping)
            if selected_spec is not None and effective
            else None
        )
        if selected_domain is not None:
            temperature_min, temperature_max = selected_domain
        elif reaction_id in {"R4", "R5"}:
            temperature_min, temperature_max = (293.15, 323.15) if reaction_id == "R4" else (273.15, 323.15)
        else:
            temperature_min, temperature_max = 273.15, 498.15
        correlation.update(
            {
                "reference_temperature": REACTION_REFERENCE_TEMPERATURE_K,
                "temperature_min": temperature_min,
                "temperature_max": temperature_max,
                "standard_state_id": COMMON_SOURCE_STANDARD_STATE_ID if common else RAW_SOURCE_STANDARD_STATE_ID,
            }
        )
        records.append(
            {
                "reaction_id": reaction_id,
                "stoichiometry": list(row),
                "engine_correlation": correlation,
                "engine_reference": {
                    "source_basis": ("CommonMolalityInfiniteDilution" if common else "RawMoleFractionInfiniteDilution"),
                    "reference_pressure_pa": REACTION_REFERENCE_PRESSURES[reaction_id],
                },
                "parameter_role": "candidate",
            }
        )
    return records


def _reaction_correlation(record: dict[str, object], reaction_id: str) -> object:
    payload = record.get("engine_correlation")
    if not isinstance(payload, dict):
        raise ReferenceBasisUnavailable(f"{reaction_id} has no accepted EOS-standard-state reference correlation")
    required = (
        "a",
        "b",
        "c",
        "d",
        "reference_temperature",
        "temperature_min",
        "temperature_max",
        "standard_state_id",
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
    ratios = {component: 1.0 if charges[component] == 0 else 0.0 for component in COMPONENT_IDS if component != solvent}
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
    return solvent, {component: value * NEUTRAL_REFERENCE_RATIO_SCALE for component, value in ratios.items()}


def _neutral_reference(request: dict[str, object]) -> equilibrium.NeutralReference:
    solvent, ratios = _neutral_reference_data(request)
    return equilibrium.NeutralReference(
        solvent=solvent,
        solute_molality_ratios=ratios,
        standard_molality_mol_per_kg=1.0,
    )


def _reaction_reference(record: dict[str, object], reaction_id: str) -> equilibrium.ReactionReference:
    basis_type = equilibrium.ReferenceSourceBasis
    payload = record.get("engine_reference") or record.get("reference")
    payload = payload if isinstance(payload, dict) else {}
    basis_name = str(
        payload.get(
            "source_basis",
            payload.get(
                "basis",
                record.get("reference_source_basis", "CommonMolalityInfiniteDilution"),
            ),
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
        raise ReferenceBasisUnavailable("current request lacks normalized reaction reference records")
    return engine_records


def _problem_from_request(request: dict[str, object], anchor: Anchor | None = None) -> object:
    system = request["reaction_system"]
    species = tuple(system.get("species_ids", ()))
    if species != COMPONENT_IDS:
        raise ValueError("MEA component order does not match the application contract")
    feed_values = tuple(float(value) for value in system["feed_amounts_mol"])
    if len(feed_values) != len(COMPONENT_IDS) or not all(math.isfinite(v) and v > 0 for v in feed_values):
        raise ValueError("MEA feed amounts must be finite and strictly positive")
    if (request.get("feed") or {}).get(
        "generation"
    ) == "source-corrections-152" or "analytical_feed_contract" in system:
        contract = system["analytical_feed_contract"]
        expected = source_feed_request(request, contract["source_coordinates"])
        if system != expected["reaction_system"] or request["temperature"]["value"] != expected["temperature"]["value"]:
            raise ValueError("Final source-feed/temperature contract mismatch before native construction")
        if contract["basis"] == "source_molality":
            increment = [
                math.fsum(
                    row[i] * extent
                    for row, extent in zip(
                        system["reaction_matrix"],
                        contract["seed_extents_mol"],
                        strict=True,
                    )
                )
                for i in range(9)
            ]
            neutral = [value - change for value, change in zip(feed_values, increment, strict=True)]
            recovered = neutral[1] / (system["molar_masses_kg_per_mol"][2] * neutral[2])
            if abs(recovered / float(contract["source_coordinates"]["source_molality_mol_per_kg_water"]) - 1) > 1e-12:
                raise ValueError("Native analytical-feed molality reversal failed")
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
        phases.append(
            equilibrium.Phase(
                identity,
                support=support,
                kind=declared["fluid_role"],
                amount=amount,
                composition_guess=guess,
            )
        )
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
            if phase.kind == "vapor" and all(
                name in supported for name, value in reaction.stoichiometry.items() if value
            ):
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
        "phases": phases,
        "T": temperature,
        "P": pressure,
        "feed": feed,
        "reactions": reactions,
        "standard_gibbs_j_per_mol": system.get("standard_gibbs_j_per_mol", ()),
        "topology_declared": True,
    }
    problem_kwargs["neutral_reference"] = _neutral_reference(request)
    return equilibrium.Problem(**problem_kwargs)


@dataclass(frozen=True)
class Anchor:
    temperature_c: int
    loading: float
    pressure_pa: float
    mole_fractions: tuple[float, ...]
    molar_volume_m3_per_mol: float


def bind_mea(mapping, specification, *, reaction_reference_pressure_pa):
    spec = SolventSpecification(specification, reaction_reference_pressure_pa=reaction_reference_pressure_pa)
    spec.parameters = epcsaft.Parameters.from_mapping(mapping)
    spec.model = epcsaft.Mixture(spec.parameters, thermochemistry=spec.thermal)
    packet = load_state_packet()["observations"][0]["request"]
    request = corrected_request(packet, mapping)
    laws = {r.name: r.correlation for r in _problem_from_request(request).reactions}
    fields = ("a", "b", "c", "d", "e", "f", "reference_temperature")
    for problem in spec.problems.values():
        for reaction in problem.reactions:
            old = reaction.correlation
            reaction.correlation = equilibrium.ReactionLogPolynomial(
                **{k: getattr(laws[reaction.name], k) for k in fields},
                temperature_min=old.temperature_min,
                temperature_max=old.temperature_max,
                standard_state_id=old.standard_state_id,
            )
    for group in spec.spec["chemistry"]["reactions"].values():
        for reaction in group:
            reaction["correlation"].update({k: getattr(laws[reaction["name"]], k) for k in fields})
    return spec


def mea_endpoint_mapping(start, report, declared):
    """Parameter mapping at a fit's returned optimizer (density_268.finish_fit, all fitted reactions)."""
    updates, index = {}, 0
    for q in declared:
        for family, target, factor in q.get("targets", []):
            identity = (
                f"component/{target}/{family}"
                if isinstance(target, str)
                else f"pair/{'/'.join(sorted(target))}/"
                + ("k_ij/reciprocal_temperature_slope" if family == "k_ij_reciprocal_temperature_slope" else family)
            )
            updates[
                identity.replace(
                    "/ion_suppression_coefficient",
                    "/ion_specific_suppression_coefficient",
                )
            ] = report["physical"][index]
            index += 1
    fitted = {q["name"] for q in declared if q.get("kind") in ("reaction_coordinate", "reaction_enthalpy_shift")}
    for entry in report["reactions"]["aqueous"]:
        name, law = (
            entry["name"],
            equilibrium.ReactionLogPolynomial(**entry["correlation"]),
        )
        if name not in fitted:
            continue
        if name == "R5":
            fields = dict(
                zip(
                    ("a_k", "b", "c_per_k"),
                    reg.reaction_log10_reciprocal(law),
                    strict=True,
                )
            )
        elif name == "R2":
            fields = dict(
                a=law.a - law.c * math.log(law.reference_temperature),
                b_k=law.b,
                c=law.c,
                d_per_k=law.d,
            )
        else:  # R4 is stored as a + b_k/T with no ln T term.
            if any((law.c, law.d, law.e, law.f)):
                raise ValueError("R4 must use a + b/T")
            fields = dict(a=law.a, b_k=law.b)
        updates.update({f"reaction:{name}:correlation:{k}": v for k, v in fields.items()})
    return with_parameter_values(start, updates)


class MEARoute(Route):
    def __init__(self, declaration, *, reference_pressure_pa):
        self.path = declaration
        self.fixed_reference_pressure_pa = reference_pressure_pa
        self.config = {
            "reaction_ranges_K": {
                row["reaction_id"]: row["temperature_range_k"]
                for row in json.loads(REACTION_CONTRACT_PATH.read_text())["reactions"]
            }
        }

    def bind(self, point):
        spec = bind_mea(
            point["parameters"],
            self.path,
            reaction_reference_pressure_pa=self.fixed_reference_pressure_pa,
        )
        spec.inputs["endpoint"] = point["parameters"]
        spec.inputs["coordinates"] = point["coordinates"]
        if self.fixed_reference_pressure_pa is not None:
            assert spec.spec["chemistry"]["reactions"] == point["reactions"]
        return spec

    def endpoint_mapping(self, point, report, declared):
        p = Route.endpoint_mapping(self, point, report, declared)
        p["parameters"] = mea_endpoint_mapping(point["parameters"], report, declared)
        return p

    def phase_states(self):
        dense = [
            dict(block="dense", wt=w, T=round(313.15 + 10 * i, 2), a=a, c=c)
            for w in (0.15, 0.25, 0.35, 0.45)
            for i in range(9)
            for a in [1e-5] + [round(0.025 * k, 4) for k in range(1, 25)]
            for c in (1.05, 3.0)
        ]
        census = [dict(block="census", wt=None, T=T, a=a, c=c) for T in CENSUS_T for a in CENSUS_A for c in (1.05, 3.0)]
        offset = [
            dict(block="offset", wt=w, T=round(318.15 + 10 * i, 2), a=round(0.0125 + 0.025 * k, 4), c=1.5)
            for w in (0.2, 0.3, 0.4)
            for i in range(8)
            for k in range(24)
        ]
        return [dict(row, key="{block}|{wt}|{T}|{a}|{c}".format(**row)) for row in dense + census + offset]

    def stability_row(self, spec, state, scale):
        template = spec.problems[
            next(row["problem"] for row in spec.inputs["observations"]["fitted"] if row["group"] == "loaded density")
        ]
        masses = {
            row["component_id"]: row["fixed"]["molar_mass"]["value"]["magnitude"]
            for row in spec.inputs["endpoint"]["components"]
        }
        amine, water = CENSUS_FEED
        if (wt := state["wt"]) is not None:
            water = amine * masses["monoethanolamine"] * (1 - wt) / (wt * masses["water"])
        feed = equilibrium.Amounts({"monoethanolamine": amine, "water": water, "carbon-dioxide": state["a"] * amine})
        liquid = equilibrium.Phase("L", kind="liquid", support=COMPONENT_IDS)
        common = dict(
            T=state["T"],
            feed=feed,
            reactions=template.reactions,
            neutral_reference=template.neutral_reference,
            row_tolerance=1e-10,
        )
        parent = equilibrium.Problem(P=1e5, phases=[liquid], **common)
        vapor = equilibrium.Phase("V", kind="vapor", support=COMPONENT_IDS[:3], amount=equilibrium.Pinned(0.0))
        bubble = equilibrium.Problem(P=equilibrium.Free(2e4), phases=[liquid, vapor], **common)
        return reg.stability(spec.parameters, parent, scale=scale, pressure_reference=bubble, pressure_ratio=state["c"])


def pressure_record(spec, template, identity, request, observed, source, group):
    problem = _problem_from_request(corrected_request(request, spec.inputs["endpoint"]))
    binding = spec.problems[template["problem"]]
    problem.reactions = binding.reactions
    problem.neutral_reference = binding.neutral_reference
    problem.row_tolerance = binding.row_tolerance
    spec.problems[identity] = problem
    arguments = dict(
        template["arguments"], observed=observed, phase=problem.phases[1].name
    )
    source_coordinates = request["reaction_system"]["analytical_feed_contract"][
        "source_coordinates"
    ]
    row = dict(
        id=identity,
        observed=observed,
        quantity="PartialPressure",
        temperature_K=problem.T,
        feed_mol=problem.feed.values,
        source=source,
        source_coordinates=source_coordinates,
        weight=template["weight"],
        form="LogRatio",
        scale=1.0,
    )
    return dict(
        template,
        identity=identity,
        problem=identity,
        group=group,
        row=row,
        arguments=arguments,
        unit="Pa",
        temperature_domain=[293.15, 393.15],
        basis=dict(template["basis"], arguments=arguments),
    )


def pressure_series(source):
    return round(
        float(source["temperature_series_C"] or source["temperature_reported_C"])
    )


def pressure_statistics(rows):
    good = [
        row
        for row in rows
        if row["status"] == "Available" and row["requested_tolerance_met"]
    ]
    error = [row["value"] / row["observed"] - 1 for row in good]
    return dict(
        attempted=len(rows),
        available=len(good),
        bias_percent=100 * math.fsum(error) / len(error) if error else None,
        AARD_percent=100 * math.fsum(map(abs, error)) / len(error) if error else None,
        log_RMSE=math.sqrt(
            math.fsum(math.log1p(value) ** 2 for value in error) / len(error)
        )
        if error
        else None,
    )


def replay_expanded_weights(declaration):
    templates = {}
    for observation in load_state_packet(declaration["packet"])["observations"]:
        request = observation["request"]
        if request["pressure"]["role"] == "solved":
            series = round(request["temperature"]["value"] - 273.15)
            templates.setdefault(series, []).append(
                (request["reaction_system"]["feed_amounts_mol"][0], request)
            )
    with declaration["canonical"].open(newline="") as stream:
        canonical = {row["observation_id"]: row for row in csv.DictReader(stream)}
    with declaration["pressure_rows"].open(newline="") as stream:
        population = {
            row["target"]: canonical[row["identity"].removeprefix("canonical:")]
            for row in csv.DictReader(stream)
        }
    with declaration["wagner"].open(newline="") as stream:
        wagner = [row for row in csv.DictReader(stream) if row["admitted"] == "yes"]

    cases = {}
    for name, (parameters, reference) in declaration["cases"].items():
        reference = read(reference)
        mapping = read(parameters)
        spec = bind_mea(
            mapping, declaration["specification"], reaction_reference_pressure_pa=None
        )
        spec.inputs["endpoint"] = mapping
        originals = spec.inputs["observations"]["fitted"]
        legacy = [
            row
            for row in originals
            if row["group"] == "common149" and row["kind"] == "partial_pressure"
        ]
        old_ids = {row["identity"] for row in legacy}
        added = []
        for identity, source in population.items():
            if identity in old_ids:
                continue
            loading = float(source["CO2_loading"])
            template = min(
                templates[pressure_series(source)],
                key=lambda item: abs(item[0] - loading),
            )[1]
            added.append(
                pressure_record(
                    spec,
                    legacy[0],
                    identity,
                    source_feed_request(template, source),
                    float(source["CO2_pressure"]) * 1000,
                    source["source_key"],
                    "Table S6 additions",
                )
            )
        hot_wagner = []
        for row in sorted(wagner, key=lambda row: row["subset"]):
            T = float(row["evaluation_temperature_k"])
            if T < 370:
                continue
            loading = float(row["loading_mol_CO2_per_mol_MEA"])
            template = min(
                templates[80 if T < 355 else 120],
                key=lambda item: abs(item[0] - loading),
            )[1]
            request = source_feed_request(
                template,
                dict(
                    source_key="Wagner2013",
                    CO2_loading=loading,
                    MEA_weight_fraction=float(row["MEA_mass_fraction_unloaded"]),
                    temperature_reported_C=T - 273.15,
                ),
            )
            identity = f"Wagner2013:csv-row-{row['csv_data_row_number']}-pco2"
            hot_wagner.append(
                pressure_record(
                    spec,
                    legacy[0],
                    identity,
                    request,
                    float(row["pressure_pa_reported_quantity"]),
                    "Wagner2013",
                    "Wagner comparison",
                )
            )
        rows = evaluate(spec, [*originals, *added])
        held = evaluate(spec, hot_wagner)
        pressure_rows = {
            row["identity"]: row for row in rows if row["identity"] in population
        }
        hot = [
            row
            for identity, row in pressure_rows.items()
            if float(population[identity]["temperature_reported_C"]) + 273.15 >= 370
        ]
        pools = dict(
            legacy=[
                row for identity, row in pressure_rows.items() if identity in old_ids
            ],
            added=[
                row
                for identity, row in pressure_rows.items()
                if identity not in old_ids
            ],
            hot_expanded=hot,
            hot_published=hot + held,
            all_pressure=list(pressure_rows.values()),
        )
        for identity, row in pressure_rows.items():
            source = population[identity]
            pools.setdefault(source["source_key"], []).append(row)
            pools.setdefault(f"{pressure_series(source)} C nominal", []).append(row)
        differences, values = compare_rows(
            reference["rows"] + reference["hot_wagner"], rows + held
        )
        cost = [
            math.fsum(row["cost"] for row in group)
            if all("cost" in row for row in group)
            else None
            for group in (rows[: len(originals)], rows)
        ]
        cases[name] = dict(
            rows=rows,
            hot_wagner=held,
            row_differences=differences,
            value_differences=values,
            original_cost=cost[0],
            expanded_cost=cost[1],
            pressure={name: pressure_statistics(rows) for name, rows in pools.items()},
        )
    return cases


FIT_SETS = {
    "expanded-weights": dict(
        replay=replay_expanded_weights,
        archive=CAMPAIGN_ARCHIVE,
        specification=HISTORICAL_SPEC,
        packet=BUNDLE / "results/source-corrections-152/state-packet.json.gz",
        canonical=ROOT
        / "data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv",
        pressure_rows=BUNDLE
        / "results/paper-evidence-341/paper-evidence/canonical-pressure.csv",
        wagner=BUNDLE
        / "results/temperature-reanchor-140/never-accessed-vle-admission.csv",
        cases={
            "F4": (
                EXPANDED_FIT / "F4/parameters.json",
                EXPANDED_FIT / "F4/replay.json.gz",
            ),
            "F2": (
                EXPANDED_FIT / "F2/parameters.json",
                EXPANDED_FIT / "F2/replay.json.gz",
            ),
            "incumbent": (
                SALT_FIT / "parameters.json",
                EXPANDED_FIT / "incumbent/replay.json.gz",
            ),
        },
    ),
    "system-pressure": dict(
        route=MEARoute,
        declaration=HISTORICAL_SPEC,
        reference_pressure_pa=None,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=REPORTED / "MEA/manifest.json.gz",
        endpoint_keys=("prior_declaration",),
        reference=REPORTED / "MEA/reference-control.json.gz",
        reference_keys=("tracking",),
    ),
    "reported": dict(
        route=MEARoute,
        declaration=HISTORICAL_SPEC,
        retained=REPORTED / "MEA",
        reference_pressure_pa=P_REF,
        maximum_seconds=2700,
        replay_tolerance=1e-10,
        diagnostic_attempts=("A-loose.json.gz",),
    ),
}
