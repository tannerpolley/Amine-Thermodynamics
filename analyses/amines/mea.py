"""Fixed-reference MEA declaration and source reaction basis."""

from __future__ import annotations

import copy
from functools import cache
import csv
from dataclasses import dataclass
import gzip
from hashlib import sha256
import json
import math
import tarfile
from pathlib import Path
import warnings

from .fit import compare_rows, retained_endpoint, route_for, save
from .model import (
    CAMPAIGN_ARCHIVE,
    P_REF,
    ROOT,
    Route,
    evaluate,
    parameter_mapping,
    replay,
    parameter_values,
    target_identity,
    with_parameter_values,
)
from MEA.common.mea_source_contracts import (
    EXPECTED_REACTION_CORRELATIONS,
    REACTION_CONTRACT_PATH,
)
from .records import RESULTS, input_path, read
from MEA.solvent_specification import SolventSpecification, deviation_statistics
import epcsaft
import numpy as np
from epcsaft import equilibrium, regression as reg

from .wheel import verify

BUNDLE = ROOT / "analyses/mea_parameter_bundle"
HISTORICAL_SPEC = BUNDLE / "results/adoption-297/historical-spec/MEA.toml"
SALT_FIT = BUNDLE / "results/salt-anchored-435/MEA/F4"
EXPANDED_FIT = ROOT / "analyses/round_7/results/E"
RESTRICTION_FIT = BUNDLE / "results/reduced-refit"
PAPER_EVIDENCE = BUNDLE / "results/paper-evidence-341"
SAME_DATA = BUNDLE / "results/same-data-comparison"
PRESSURE_INPUTS = dict(
    packet=BUNDLE / "results/source-corrections-152/state-packet.json.gz",
    canonical=ROOT / "data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv",
    pressure_rows=PAPER_EVIDENCE / "paper-evidence/canonical-pressure.csv",
)
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
    data = input_path(path).read_bytes()
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
            identity = target_identity(start, family, target) if family == "temperature_law_coefficient" else (
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
    arguments = dict(template["arguments"], observed=observed, phase=problem.phases[1].name)
    source_coordinates = request["reaction_system"]["analytical_feed_contract"]["source_coordinates"]
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
    return round(float(source["temperature_series_C"] or source["temperature_reported_C"]))


def pressure_statistics(rows):
    good = [row for row in rows if row["status"] == "Available" and row["requested_tolerance_met"]]
    error = [row["value"] / row["observed"] - 1 for row in good]
    return dict(
        attempted=len(rows),
        available=len(good),
        bias_percent=100 * math.fsum(error) / len(error) if error else None,
        AARD_percent=100 * math.fsum(map(abs, error)) / len(error) if error else None,
        log_RMSE=math.sqrt(math.fsum(math.log1p(value) ** 2 for value in error) / len(error)) if error else None,
    )


def off_window_statistics(rows):
    pools = {}
    for row in rows:
        group = row["group"]
        pools.setdefault(group, []).append(row)
        if group == "Aronu2011":
            fraction = float(row["row"]["source_coordinates"]["MEA_weight_fraction"])
            pools.setdefault(f"{group} {100 * fraction:g} wt%", []).append(row)
    return {group: pressure_statistics(pool) for group, pool in pools.items()}




def pressure_inputs(declaration):
    templates = {}
    for observation in load_state_packet(declaration["packet"])["observations"]:
        request = observation["request"]
        if request["pressure"]["role"] == "solved":
            series = round(request["temperature"]["value"] - 273.15)
            templates.setdefault(series, []).append((request["reaction_system"]["feed_amounts_mol"][0], request))
    with input_path(declaration["canonical"]).open(newline="") as stream:
        canonical = {row["observation_id"]: row for row in csv.DictReader(stream)}
    with input_path(declaration["pressure_rows"]).open(newline="") as stream:
        population = {
            row["target"]: canonical[row["identity"].removeprefix("canonical:")] for row in csv.DictReader(stream)
        }
    return templates, population


def pressure_additions(spec, templates, population):
    legacy = [
        row
        for row in spec.inputs["observations"]["fitted"]
        if row["group"] == "common149" and row["kind"] == "partial_pressure"
    ]
    old_ids = {row["identity"] for row in legacy}
    added = []
    for identity, source in population.items():
        if identity in old_ids:
            continue
        loading = float(source["CO2_loading"])
        template = min(templates[pressure_series(source)], key=lambda item: abs(item[0] - loading))[1]
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
    return legacy, added


def ablation_pressures(spec):
    templates, population = pressure_inputs(PRESSURE_INPUTS)
    legacy, added = pressure_additions(spec, templates, population)
    return {"legacy-47": evaluate(spec, legacy),
            "Mamun2005": evaluate(spec, [row for row in added
                                        if population[row["identity"]]["source_key"] == "Mamun2005"])}


def wagner_pressure_records(spec, legacy, templates, wagner, *, minimum_temperature=None):
    records = []
    for row in sorted(wagner, key=lambda row: row["subset"]):
        T = float(row["evaluation_temperature_k"])
        if minimum_temperature is not None and T < minimum_temperature:
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
        records.append(
            pressure_record(
                spec,
                legacy,
                identity,
                request,
                float(row["pressure_pa_reported_quantity"]),
                "Wagner2013",
                "Wagner comparison",
            )
        )
    return records


def off_window_pressures(spec, legacy, templates, population, reference):
    first = next(iter(population.values()))
    template = min(templates[pressure_series(first)], key=lambda item: abs(item[0] - float(first["CO2_loading"])))[1]
    rows = []
    for source in reference["source_rows"]:
        identity = f"off-window:{source['observation_id']}"
        observed = float(source["CO2_pressure"]) * 1000
        group = source["source_key"]
        try:
            record = pressure_record(
                spec, legacy, identity, source_feed_request(template, source), observed, group, group
            )
            (row,) = evaluate(spec, [record])
        except (ValueError, RuntimeError) as error:
            row = dict(
                identity=identity,
                observed=observed,
                unit="Pa",
                group=group,
                status="Exception",
                exception=type(error).__name__,
                value=None,
                message=str(error),
            )
        rows.append(dict(row, role="comparison"))
    differences, values = compare_rows(reference["rows"], rows)
    groups = {
        name: pressure_statistics([row for row in rows if row["group"] == name])
        for name in sorted({row["group"] for row in rows})
    }
    return dict(rows=rows, statistics=groups, row_differences=differences, value_differences=values)




def transfer_pressure_records(spec, legacy, templates, canonical, rows):
    for row in rows:
        source = canonical[row["identity"].removeprefix("transfer:canonical:")]
        loading = float(source["CO2_loading"])
        template = min(templates[pressure_series(source)], key=lambda item: abs(item[0] - loading))[1]
        yield pressure_record(
            spec, legacy, row["target"], source_feed_request(template, source),
            float(row["observed"]), row["source"], "transfer",
        )








def comparison_metrics(rows, predicted):
    used = [row for row in rows if row.get(predicted) is not None]
    errors = [row[predicted] - row["observed"] for row in used]
    relative = [abs((row[predicted] - row["observed"]) / row["observed"]) for row in used if row["observed"]]
    return dict(
        n=len(used),
        rmse=math.sqrt(np.mean(np.square(errors))) if errors else None,
        aard_percent=100 * float(np.mean(relative)) if relative else None,
    )








def carbonate_shares(spec, inputs, reference):
    spec.spec["templates"].update(inputs["problems"])
    spec.problems.update({name: spec.problem(name, {}) for name in inputs["problems"]})
    identities = {row["identity"] for row in reference}
    rows = []
    for item in inputs["records"]:
        if item["identity"] not in identities:
            continue
        prediction = spec.prediction(item)
        rows.append(
            dict(
                identity=item["identity"],
                state=item["state_identity"],
                observed=item["arguments"]["observed"],
                value=prediction.get("value"),
                status=prediction["status"],
                convergence=prediction.get("convergence"),
            )
        )
    return rows


def activity_rows(spec, retained, pool=False):
    template = next(o["request"] for o in load_state_packet()["observations"]
                    if o["identity"] == "Bottinger2008_state_046")
    mapping = spec.inputs["endpoint"]
    fixed_reactions = next(problem.reactions for problem in spec.problems.values() if problem.reactions)
    hydrogen, carbonate, bicarbonate = map(
        COMPONENT_IDS.index, ("hydronium-cation", "carbonate-anion", "bicarbonate-anion")
    )
    for prior in retained:
        T, P = prior["T_K"], prior["P_Pa"]
        request = source_feed_request(template, dict(
            source_key="Amundsen2009", CO2_loading=prior["loading"],
            temperature_reported_C=T - 273.15, MEA_weight_fraction=0.30,
        ))
        request["temperature"]["value"] = T
        request["pressure"] = dict(role="fixed", value=P)
        request["phases"] = [phase for phase in request["phases"] if phase["fluid_role"] == "liquid"]
        problem = _problem_from_request(corrected_request(request, mapping))
        problem.feed = equilibrium.Amounts(prior["feed_mol"])
        problem.reactions = fixed_reactions
        solved = equilibrium.solve_equilibrium(spec.model, problem)
        fields = ("identity", "observed") if pool else ("symbol",)
        row = {key: prior[key] for key in ("T_K", "P_Pa", "loading", "feed_mol", *fields)}
        row.update(available=solved.requested_tolerance_met, message=solved.message)
        if row["available"]:
            if pool:
                x = solved.phase_mole_fractions(0)
                row["carbonate_pool_split"] = x[carbonate] / (x[carbonate] + x[bicarbonate])
            else:
                raw, molal, *_ = equilibrium.reaction_activities(spec.model, solved)
                row["pH"] = -molal.species.log_activities[hydrogen] / math.log(10)
                row["raw_R1_pH"] = -raw.species.log_activities[hydrogen] / math.log(10)
                if row["symbol"] is not None:
                    row["model_minus_electrode_pH"] = row["pH"] - row["symbol"]["pH"]
        yield row


def write_reported_property_summary(*, fit_folder=None, output=None):
    wheel = verify()
    declaration = FIT_SETS["reported"]
    if fit_folder is not None:
        declaration = declaration | {"retained": fit_folder}
    point, selection = retained_endpoint(declaration)
    fit_path = declaration["retained"] / f'{selection["selected"]}.json.gz'
    fit = read(fit_path)
    spec = route_for(declaration).bind(point)
    activity_path = SALT_FIT / "q5.json"
    retained = read(activity_path)["result"]
    activities = list(activity_rows(spec, retained["rows"]))
    pool = list(activity_rows(spec, retained["carbonate_pool_comparison"], pool=True))

    rows = fit["replay"]["rows"]
    diagnostic = fit["diagnostics"]
    free_ids = diagnostic["uncertainty"]["free_coordinates"]
    free = [i for i, coord in enumerate(point["coordinates"]) if coord["identity"] in free_ids]
    jacobian = np.array(diagnostic["jacobian_bound_normalized"])[:, free]
    responsive = np.any(jacobian != 0, axis=1)
    ss = math.fsum(row["cost"] for row, use in zip(rows, responsive, strict=True) if use) * 2
    variance = ss / (int(responsive.sum()) - len(free))
    covariance = variance * np.linalg.inv(jacobian.T @ jacobian)
    bands = [
        dict(identity=row["identity"], value_pa=row["value"],
             relative_se_percent=100 * math.sqrt(gradient @ covariance @ gradient / row["row"]["weight"]))
        for row, gradient in zip(rows, jacobian, strict=True)
        if row["group"] == "common149" and row["basis"]["kind"] == "partial_pressure"
    ]
    cai = {
        kind: dict(count=len(group), cost=math.fsum(row["cost"] for row in group))
        for kind in ("temperature", "mole_fraction")
        if (group := [row for row in rows if row["group"] == "Cai" and row["basis"]["kind"] == kind])
    }
    path = output or RESULTS / "mea/reported/properties/uncertainty-and-activities.json.gz"
    save(path, dict(
        wheel=wheel, endpoint_fingerprint=selection["endpoint_fingerprint"],
        inputs=[path.resolve().relative_to(ROOT).as_posix() for path in (fit_path, activity_path)],
        objective=fit["replay"]["cost"], cai=cai, variance=variance,
        raw_row_variance=diagnostic["uncertainty"]["residual_variance"],
        responsive=int(responsive.sum()), fitted_pressure_bands=bands,
        activity_rows=activities, carbonate_pool=pool,
    ))


def absolute_shares(rows):
    ratios = [row["value"] / row["observed"] for row in rows if row["status"] == "Available"]
    return dict(
        n=len(ratios),
        status="available" if ratios else "unavailable",
        geometric_mean=math.exp(math.fsum(map(math.log, ratios)) / len(ratios)) if ratios else None,
        aard_percent=100 * math.fsum(abs(ratio - 1) for ratio in ratios) / len(ratios) if ratios else None,
        minimum=min(ratios, default=None),
        maximum=max(ratios, default=None),
    )




def density_records(spec, rows):
    template = spec.problems[
        next(
            record["problem"] for record in spec.inputs["observations"]["fitted"] if record["group"] == "loaded density"
        )
    ]
    masses = {
        row["component_id"]: row["fixed"]["molar_mass"]["value"]["magnitude"]
        for row in spec.inputs["endpoint"]["components"]
    }
    for row in rows:
        identity, loading, fraction = row["id"], float(row["loading"]), float(row["mea_mass_fraction"])
        feed = {"monoethanolamine": 1.0}
        if fraction < 1:
            feed["water"] = masses["monoethanolamine"] * (1 - fraction) / (fraction * masses["water"])
            if loading:
                feed["carbon-dioxide"] = loading
        support = COMPONENT_IDS if fraction < 1 else tuple(feed)
        spec.problems[identity] = equilibrium.Problem(
            T=float(row["T_K"]),
            P=float(row["P_Pa"]),
            feed=equilibrium.Amounts(feed),
            phases=[equilibrium.Phase("L", kind="liquid", support=support)],
            reactions=template.reactions if fraction < 1 else [],
            neutral_reference=template.neutral_reference if fraction < 1 else None,
            row_tolerance=template.row_tolerance,
        )
        yield dict(
            identity=identity,
            group="density comparison",
            row=row,
            constructor="observation",
            observation_parameters=spec.parameter_sha256,
            kind="phase_density",
            arguments=dict(
                observed=float(row["observed_kg_m3"]),
                scale=float(row.get("s_kg_m3") or row.get("source_uncertainty_value") or 1),
                form="difference",
                phase="L",
                mass_basis=True,
            ),
            weight=1.0,
            problem=identity,
            temperature_domain=[293.15, 393.15],
        )


def heat_capacity_records(spec, rows):
    cp = next(row for row in spec.inputs["observations"]["fitted"] if row["group"] == "Cp")
    template = spec.problems[cp["problem"]]
    masses = {
        row["component_id"]: row["fixed"]["molar_mass"]["value"]["magnitude"]
        for row in spec.inputs["endpoint"]["components"]
    }
    for row in rows:
        if row["role"] == "outside-loading-domain":
            continue
        T, loading = float(row["T_K"]), float(row["loading"])
        if row["MEA_molality"]:
            water = 1 / (float(row["MEA_molality"]) * masses["water"])
        else:
            fraction = float(row["MEA_unloaded_mass_fraction"])
            water = masses["monoethanolamine"] * (1 - fraction) / fraction / masses["water"]
        feed = {"monoethanolamine": 1.0, "water": water, "carbon-dioxide": max(loading, 1e-6)}
        mass = sum(n * masses[species] for species, n in feed.items())
        amount = sum(feed.values())
        name = f"{row['source']}-{T}-{loading}"
        problem = copy.copy(template)
        problem.T, problem.P, problem.feed = T, float(row["calculation_pressure_Pa"]), equilibrium.Amounts(feed)
        spec.problems[name] = problem
        mass_to_mol = 1000 * mass / amount
        observed = float(row["cp_kJ_kg_K"]) * mass_to_mol
        yield dict(
            cp,
            identity=name,
            problem=name,
            row=row,
            temperature_domain=[298.15, 393.15],
            arguments=dict(cp["arguments"], observed=observed, scale=float(row["relative_scale"]) * observed),
            mass_to_mol=mass_to_mol,
        )


def kim_intervals(path, pressure, ceiling):
    with input_path(path).open(newline="") as stream:
        for row in csv.DictReader(stream):
            yield dict(
                identity=row["record_id"],
                T_K=float(row["T_K"]),
                pressure=pressure,
                loading=float(row["loading"]),
                previous_loading=float(row["previous_loading"]),
                observed=float(row["observed"]),
                retained=float(row["predicted"]) if row["predicted"] else None,
                retained_status=row["interval_status"],
                loading_ceiling=ceiling,
                group=f"Kim heat {float(row['T_K']):g} K",
            )


def heat_intervals(spec, mapping, templates, rows):
    packet = load_state_packet()["observations"]
    template = next(item["request"] for item in packet if item["identity"] == "Bottinger2008_state_046")
    request = corrected_request(
        source_feed_request(
            template,
            dict(source_key="Amundsen2009", CO2_loading=0.11, temperature_reported_C=40.0, MEA_weight_fraction=0.30),
        ),
        mapping,
    )
    chemistry = _problem_from_request(request)
    row = next(item for item in spec.inputs["observations"]["fitted"] if item["group"] == "common149")
    references = {reaction.name: reaction.reference for reaction in spec.problems[row["problem"]].reactions}
    for reaction in chemistry.reactions:
        reaction.reference = references[reaction.name]
    masses = {row["component_id"]: row["fixed"]["molar_mass"]["value"]["magnitude"] for row in mapping["components"]}
    water = masses["monoethanolamine"] * 0.7 / (0.3 * masses["water"])
    source_masses = template["reaction_system"]["molar_masses_kg_per_mol"]
    fraction = source_masses[1] / (source_masses[1] + water * source_masses[2])

    @cache
    def liquid(T, P, loading):
        return equilibrium.Problem(
            T=T,
            P=P,
            feed=equilibrium.Amounts({"monoethanolamine": 1.0, "water": water, "carbon-dioxide": loading}),
            phases=[equilibrium.Phase("L", kind="liquid", support=COMPONENT_IDS)],
            reactions=chemistry.reactions,
            neutral_reference=chemistry.neutral_reference,
        )

    @cache
    def bubble(T, loading):
        if loading == 0:
            problem = copy.copy(liquid(T, 1e4, loading))
            problem.phases = [
                problem.phases[0],
                equilibrium.Phase(
                    "V",
                    kind="vapor",
                    support=("monoethanolamine", "water"),
                    amount=equilibrium.Pinned(0.0),
                    composition_guess=(0.01, 0.99),
                ),
            ]
            problem.P = equilibrium.Free(1e4)
        else:
            nominal = min(templates, key=lambda series: abs(series + 273.15 - T))
            template = min(templates[nominal], key=lambda item: abs(item[0] - loading))[1]
            source = dict(
                source_key="model-curve",
                CO2_loading=loading,
                MEA_weight_fraction=fraction,
                temperature_reported_C=T - 273.15,
            )
            problem = _problem_from_request(corrected_request(source_feed_request(template, source), mapping))
        for reaction in problem.reactions:
            reaction.reference = references[reaction.name]
        return equilibrium.solve_equilibrium(spec.model, problem)

    for row in rows:
        T, P, start, end = (row[key] for key in ("T_K", "pressure", "previous_loading", "loading"))
        before, after = liquid(T, P, start), liquid(T, P, end)
        status = "available"
        diagnostic = None
        if row.get("loading_ceiling") is not None:
            if not 0 <= start <= end <= row["loading_ceiling"]:
                status = "above_ceiling"
            else:
                for loading in (start, end):
                    phase = bubble(T, loading)
                    if not phase.requested_tolerance_met:
                        status, diagnostic = "numerical_failure", phase.message
                        break
                    if phase.pressure > P:
                        status, diagnostic = "bubble_pressure_exceeded", phase.pressure
                        break
        value = None
        if status == "available":
            observation = reg.addition_enthalpy(
                spec.parameters,
                before,
                after,
                {"carbon-dioxide": 1.0},
                end - start,
                T,
                P,
                phase="vapor",
                observed=0.0,
                form="difference",
                scale=1000.0,
            )
            prediction = reg.predict(spec.model, observation)
            if prediction.status.name == "Available" and prediction.requested_tolerance_met:
                value = -prediction.value / 1000
            else:
                status, diagnostic = "addition_enthalpy", prediction.message
        yield dict(row, status=status, predicted=value, diagnostic=diagnostic)


def heat_comparison(spec, mapping, templates, retained):
    source = retained["rows"]
    intervals = [
        dict(T_K=row["T_K"], pressure=source["system_pressure_Pa"],
             previous_loading=row["previous_loading"], loading=row["loading"],
             loading_ceiling=source["loading_ceiling"])
        for row in source["rows"]
    ]
    return {"rows": [
        dict(row, predicted_kJ_mol=result["predicted"], status=result["status"],
             diagnostic=result["diagnostic"])
        for row, result in zip(source["rows"], heat_intervals(spec, mapping, templates, intervals), strict=True)
    ], "system_pressure_Pa": source["system_pressure_Pa"], "loading_ceiling": source["loading_ceiling"],
        "sources": source["sources"]}


def refresh_pressure_rows(spec, legacy_template, rows):
    template = next(row["request"] for row in load_state_packet()["observations"]
                    if row["request"]["pressure"]["role"] == "solved")
    records = []
    for row in rows:
        source = row["row"]["source_coordinates"]
        records.append(pressure_record(spec, legacy_template, row["identity"], source_feed_request(template, source),
                                       row["observed"], row["row"]["source"], row["group"]))
    return [dict(old, **new) for old, new in zip(rows, evaluate(spec, records), strict=True)]


def reported_carbonate_shares(spec, references):
    shares = []
    for row in references:
        path = PAPER_EVIDENCE / "paper-evidence/selected-assessment/carbonate-requests" / (row["state"] + ".json")
        problem = _problem_from_request(corrected_request(read(path), spec.inputs["endpoint"]))
        for reaction in problem.reactions:
            reaction.reference = equilibrium.ReactionReference(reaction.reference.source_basis, reference_pressure_pa=P_REF)
        result = equilibrium.solve_equilibrium(spec.model, problem)
        value = None
        if result.requested_tolerance_met:
            x = dict(zip(COMPONENT_IDS, result.phase_mole_fractions(0), strict=True))
            value = x["carbonate-anion"] / sum(x[species] for species in (
                "carbon-dioxide", "carbamate-anion", "bicarbonate-anion", "carbonate-anion"))
        shares.append(dict(row, status="Available" if value is not None else "Unavailable", value=value,
                           cause=None if value is not None else result.message))
    return shares


def display_properties(route, point, fit):
    spec = route.bind(point)
    mapping = point["parameters"]
    template_groups, population = pressure_inputs(PRESSURE_INPUTS)
    legacy, additions = pressure_additions(spec, template_groups, population)
    extra = evaluate(spec, additions)
    held_base = ROOT / "analyses/fixed_reaction_reference/results"
    held_display = held_base / "display-replays"
    retained = read(held_base / "E/MEA/replay.json.gz")
    held_pressures = read(held_display / "wagner.json.gz")
    held_off_window = read(held_base / "MEA/off-window.json.gz")
    hot = refresh_pressure_rows(spec, legacy[0], retained["hot_wagner"])
    wagner = refresh_pressure_rows(spec, legacy[0], held_pressures["rows"])
    off_window = refresh_pressure_rows(spec, legacy[0], held_off_window["rows"])
    fitted_rows = fit["replay"]["rows"]
    legacy_ids = {r["identity"] for r in legacy}
    fitted_pressure = [r for r in fitted_rows if r["identity"] in legacy_ids]
    all_pressure = fitted_pressure + extra
    groups = dict(legacy=fitted_pressure, added=extra, hot_published=hot, all_pressure=all_pressure)
    groups["hot_expanded"] = [q for q in all_pressure if pressure_series(population[q["identity"]]) == 120]
    for row in all_pressure:
        source = population[row["identity"]]
        groups.setdefault(source["source_key"], []).append(row)
        groups.setdefault(f"{pressure_series(source)} C nominal", []).append(row)
    replay = dict(retained, rows=fitted_rows + extra, hot_wagner=hot,
                  summary=dict(retained["summary"], original_cost=fit["replay"]["cost"],
                               pressure={key: pressure_statistics(rows) for key, rows in groups.items()}))

    held = read(held_display / "mea-comparisons.json.gz")
    density = evaluate(spec, list(density_records(spec, [row["row"] for row in held["density"]])))
    records = list(heat_capacity_records(spec, [row["row"] for row in held["heat_capacity"]]))
    capacities = [dict(old, **{**prediction, "predicted_kJ_kg_K": None if prediction["value"] is None
                              else prediction["value"] / record["mass_to_mol"]})
                  for old, prediction, record in zip(held["heat_capacity"], evaluate(spec, records), records, strict=True)]
    shares = reported_carbonate_shares(spec, held["carbonate_share"])

    kim = []
    source = FIT_SETS["published-properties"]
    intervals = kim_intervals(source["kim"], source["heat_pressure"], source["loading_ceiling"])
    updates = {row["identity"]: row for row in heat_intervals(spec, mapping, template_groups, intervals)}
    for row in held["kim_2007"]:
        result = updates[row["record_id"]]
        kim.append(dict(row, predicted=result["predicted"], interval_status=result["status"],
                        diagnostic=result["diagnostic"]))
    identity = dict(wheel=verify(), endpoint_fingerprint=fit["endpoint_fingerprint"], reference_pressure_pa=P_REF)
    caloric = read(held_display / "caloric-and-species.json.gz")
    arcis_measurements = ROOT / "analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/evidence/F4/heat.csv"
    with input_path(arcis_measurements).open(newline="") as stream:
        intervals = [dict(identity=q["id"], T_K=float(q["T_K"]), pressure=float(q["P_Pa"]),
                          previous_loading=0., loading=float(q["loading"]), observed=-float(q["observed_kJ_mol"]))
                     for q in csv.DictReader(stream) if q["source"] == "Arcis2011"]
    arcis = [dict(identity=q["identity"], observed=-q["observed"],
                  predicted=None if q["predicted"] is None else -q["predicted"],
                  status="Available" if q["status"] == "available" else "Unavailable", diagnostic=q["diagnostic"])
             for q in heat_intervals(spec, mapping, template_groups, intervals)]
    targets = {q["identity"]: q for q in caloric["species"]}
    species = {q["identity"]: dict(identity=q["identity"], observed=q["observed"], predicted=q["value"], status=q["status"])
               for q in fitted_rows if q["identity"] in targets}
    for source in load_state_packet()["observations"]:
        request = [q for q in source["targets"] if q["identity"] in targets and q["identity"] not in species]
        if not request:
            continue
        before = [dict(target=q["identity"], kind="packet", quantity="species",
                       observed=targets[q["identity"]]["observed"], predicted=targets[q["identity"]]["predicted"])
                  for q in request]
        for q in retained_state_targets(mapping, spec.model, dict(source, targets=request), before,
                                        reference_pressure_pa=P_REF):
            species[q["identity"]] = q
    if species.keys() != targets.keys():
        raise ValueError("Changed MEA species assessment population")
    from .properties import worked_calorimetry

    return {
        "expanded-pressure": replay | identity,
        "off-window": dict(identity, rows=off_window),
        "wagner": dict(identity, rows=wagner),
        "heat-comparison": dict(identity, rows=heat_comparison(
            spec, mapping, template_groups, read(held_base / "MEA/heat-comparison.json.gz"))),
        "mea-comparisons": dict(identity, density=density, heat_capacity=capacities,
                                carbonate_share=shares, kim_2007=kim),
        "bubble-checks": dict(identity, rows=reference_bubbles(spec, read(held_display / "bubble-checks.json.gz")["rows"])),
        "caloric-and-species": dict(identity, arcis=arcis, species=list(species.values()),
                                    reference_state=worked_calorimetry(spec, caloric["reference_state"])),
    }


def born_sensitivity(route, point):
    """Replay the fitted rows with one fixed Born diameter of 3.0 A changed at a time."""
    base = replay(route.bind(point))
    cases = []
    for ion, diameters in (("bicarbonate-anion", (2.5, 3.5, 4.0)), ("carbonate-anion", (2.5, 4.0))):
        for diameter in diameters:
            changed = dict(point, parameters=with_parameter_values(
                point["parameters"], {f"component/{ion}/born_diameter": diameter}))
            result = replay(route.bind(changed))
            pressures = [abs(row["value"] / reference["value"] - 1)
                         for row, reference in zip(result["rows"], base["rows"], strict=True)
                         if reference["identity"].endswith("-pco2")]
            cases.append(dict(ion=ion, diameter_A=diameter, cost=result["cost"], refused=result["refused"],
                              pressure_count=len(pressures), largest_pressure_change_percent=100 * max(pressures)))
    return dict(reference_cost=base["cost"], cases=cases)


def hajj_permittivity(route, point):
    """Read the bulk relative permittivity of the reported reactive liquid."""
    spec = route.bind(point)
    source = BUNDLE / "results/permittivity-refit/hajj-table-1.csv"
    template = spec.problems["Bottinger2008_state_030::MEA + MEAH+:problem"]
    if not hasattr(epcsaft.State, "bulk_relative_permittivity"):
        raise NotImplementedError("The pinned Engine lacks State.bulk_relative_permittivity")

    rows = []
    with source.open(newline="") as stream:
        for retained in csv.DictReader(stream):
            problem = copy.copy(template)
            problem.T, problem.P = float(retained["T_K"]), float(retained["P"])
            feed = {species: float(retained[column]) for species, column in zip(
                COMPONENT_IDS[:3], ("carbon", "amine", "water"), strict=True)}
            problem.feed = equilibrium.Amounts(feed)
            metadata = json.loads(retained["source"])
            row = dict(identity=retained["identity"], source=metadata, feed_mol=feed,
                       T_K=problem.T, P_Pa=problem.P, loading=float(metadata["loading"]),
                       inferred=float(retained["epsilon"]), row_tolerance=problem.row_tolerance)
            with warnings.catch_warnings(record=True) as observed_warnings:
                warnings.simplefilter("always", epcsaft.DomainWarning)
                result = equilibrium.solve_equilibrium(spec.model, problem)
                row.update(diagnostic=result.message, residual=result.convergence.residual,
                           requested_tolerance_met=result.requested_tolerance_met, predicted=None)
                if result.molar_densities:
                    x, rho = list(result.phase_mole_fractions(0)), result.molar_densities[0]
                    state = spec.model.state(result.temperature, rho=rho, x=x)
                    epsilon = state.bulk_relative_permittivity
                    if epsilon is None:
                        raise NotImplementedError("The pinned Engine does not return bulk relative permittivity for the reactive MEA liquid")
                    row.update(predicted=epsilon, predicted_minus_inferred=epsilon - row["inferred"],
                               liquid_molar_density_mol_m3=rho,
                               pressure_residual_Pa=state.pressure - problem.P,
                               liquid_mole_fractions=dict(zip(COMPONENT_IDS, x, strict=True)))
            row["warnings"] = sorted({str(w.message) for w in observed_warnings})
            rows.append(row)
    isotherms = []
    for T in sorted({r["T_K"] for r in rows}):
        series = sorted((r for r in rows if r["T_K"] == T), key=lambda r: r["loading"])
        first, last = series[0], series[-1]
        inferred_change = last["inferred"] - first["inferred"]
        change = last["predicted"] - first["predicted"] if None not in (first["predicted"], last["predicted"]) else None
        isotherms.append(dict(T_K=T, inferred_change=inferred_change, predicted_change=change,
                              same_sign=None if change is None else bool(np.sign(change) == np.sign(inferred_change))))
    pairs = [(r["inferred"], r["predicted"]) for r in rows if r["requested_tolerance_met"] and r["predicted"] is not None]
    return dict(source=str(source.relative_to(ROOT)), source_sha256=sha256(source.read_bytes()).hexdigest(),
                caveat="Hajj et al. §3.3.1 question whether their microwave-band measurements reach the static limit.",
                rows=rows, isotherms=isotherms, statistics=deviation_statistics(pairs, "dimensionless") if pairs else None)


def reference_bubbles(spec, retained):
    rows = []
    for row in retained:
        group = row["group"]
        source = next(q for q in spec.inputs["observations"]["fitted"] if q["group"] == group)
        problem = copy.copy(spec.problems[source["problem"]])
        problem.T, problem.feed = row["T_K"], equilibrium.Amounts(row["feed"])
        initial = 5e4 if group == "Cai" else problem.P.guess
        answers = []
        for factor in (1, 1.5):
            problem.P = equilibrium.Free(initial * factor)
            result = equilibrium.solve_equilibrium(spec.model, problem)
            if not result.requested_tolerance_met:
                raise ValueError(f"{group}: {result.message}")
            rho = result.molar_densities[0]
            x = list(result.phase_mole_fractions(0))
            state = spec.model.state(result.temperature, rho=rho, x=x)
            fields = ("hard_chain", "dispersion", "association", "debye_huckel", "born",
                      "cation_mixing", "dipolar", "residual_helmholtz")
            obs = reg.observation(spec.parameters, "phase_density", problem, observed=1000., scale=1.,
                                  form="difference", phase=problem.phases[0].name, mass_basis=True)
            density = reg.predict(spec.model, obs)
            if density.status.name != "Available" or not density.requested_tolerance_met:
                raise ValueError(f"{group}: {density.message}")
            answers.append(dict(bubble_pressure_Pa=result.pressure, molar_density_mol_m3=rho,
                                density_kg_m3=density.value, **{k: getattr(state, k) for k in fields},
                                **{"x_" + k: v for k, v in zip(COMPONENT_IDS, x, strict=True)}))
        rows.append(dict(row, answers=answers, printed_digits_agree=all(
            f"{value:.10g}" == f"{answers[1][key]:.10g}" for key, value in answers[0].items())))
    return rows


def reported_curves(route, point):
    from .properties import curve_differences

    spec = route.bind(point)
    mapping = point["parameters"]
    folder = RESULTS / "mea/reported/properties/MEA/curves"
    packet = load_state_packet()["observations"]
    bubble_templates = [item["request"] for item in packet if item["request"]["pressure"]["role"] == "solved"]
    species_templates = [item["request"] for item in packet if item["identity"].startswith("Bottinger")]
    reference = next(item["request"] for item in packet if item["identity"] == "Bottinger2008_state_046")

    def fixed_reference(problem):
        for reaction in problem.reactions:
            reaction.reference = equilibrium.ReactionReference(reaction.reference.source_basis, reference_pressure_pa=P_REF)
        return problem

    def request(template, temperature, loading, fraction, source):
        return corrected_request(source_feed_request(template, dict(source_key=source, CO2_loading=loading,
            MEA_weight_fraction=fraction, temperature_reported_C=temperature - 273.15)), mapping)

    chemistry = fixed_reference(_problem_from_request(request(reference, 313.15, 0.11, 0.30, "Amundsen2009")))
    masses = {row["component_id"]: row["fixed"]["molar_mass"]["value"]["magnitude"] for row in mapping["components"]}
    source_masses = packet[0]["request"]["reaction_system"]["molar_masses_kg_per_mol"]
    species = {"MEA": (1,), "MEAH+": (3,), "MEACOO-": (4,), "HCO3-": (5,), "CO3^2-": (6,),
               "CO2": (0,), "MEA + MEAH+": (1, 3), "HCO3- + CO3^2-": (5, 6)}

    def liquid(T, P, water, loading):
        return equilibrium.Problem(T=T, P=P,
            feed=equilibrium.Amounts({"monoethanolamine": 1.0, "water": water, "carbon-dioxide": loading}),
            phases=[equilibrium.Phase("L", kind="liquid", support=COMPONENT_IDS)],
            reactions=chemistry.reactions, neutral_reference=chemistry.neutral_reference,
            row_tolerance=chemistry.row_tolerance)

    def solve(model, problem):
        result = equilibrium.solve_equilibrium(model, problem)
        if not result.requested_tolerance_met:
            raise ValueError(result.message)
        return result

    def checked(prediction):
        if prediction.status.name != "Available" or not prediction.requested_tolerance_met:
            raise ValueError(prediction.message)
        return prediction.value

    @cache
    def bubble(T, a, w):
        if not a:
            problem = liquid(T, 1e4, source_masses[1] * (1 - w) / (w * source_masses[2]), a)
            problem.phases = [*problem.phases, equilibrium.Phase("V", kind="vapor", support=("monoethanolamine", "water"),
                              amount=equilibrium.Pinned(0.0), composition_guess=(0.01, 0.99))]
            problem.P = equilibrium.Free(1e4)
        else:
            problem = packet_problem(bubble_templates, T, a, w)
        return solve(spec.model, problem)

    def packet_problem(templates, T, a, w):
        template = min(templates, key=lambda q: (abs(round(q["temperature"]["value"] - T)),
                                               abs(q["reaction_system"]["feed_amounts_mol"][0] - a)))
        return fixed_reference(_problem_from_request(request(template, T, a, w, "model-curve")))

    cai = read(folder / "cai-declaration.json")
    neutral = copy.deepcopy(mapping)
    for domain in neutral["domains"]:
        if domain["domain_id"] in cai["neutral_domain_ids"]:
            domain.update(cai["neutral_domain"])
    neutral_model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(neutral), thermochemistry=spec.thermal)

    @cache
    def evaluate(family, T, P, a, w, x):
        if family == "pressure":
            result = bubble(T, a, w)
            return {"CO2 partial pressure": result.pressure * result.phase_mole_fractions(1)[0]}, dict(pressure_Pa=result.pressure)
        if family == "mea-water":
            starts = sorted((r["feed"]["monoethanolamine"], r["T_K"], r["vapor_guess"]["water"])
                            for r in cai["rows"] if r["P_Pa"] == P)
            if not starts:
                raise ValueError(f"Cai isobar is undeclared: {P} Pa")
            composition, temperatures, vapor_water = zip(*starts, strict=True)
            guess, y = float(np.interp(x, composition, temperatures)), float(np.interp(x, composition, vapor_water))
            feed = {"water": 1 - x, "monoethanolamine": x}
            phases = [equilibrium.Phase("L", kind="liquid", support=tuple(feed), composition_guess=feed),
                      equilibrium.Phase("V", kind="vapor", support=tuple(feed), amount=equilibrium.Pinned(0.0),
                                        composition_guess={"water": y, "monoethanolamine": 1 - y})]
            problem = equilibrium.Problem(T=equilibrium.Free(guess), P=P, feed=equilibrium.Amounts(feed),
                                          phases=phases, row_tolerance=chemistry.row_tolerance)
            result = solve(neutral_model, problem)
            return {"bubble temperature": result.temperature, "vapor water mole fraction": result.phase_mole_fractions(1)[2]}, dict(temperature_K=result.temperature)
        if family == "heat":
            water = masses["monoethanolamine"] * 0.7 / (0.3 * masses["water"])
            item = reg.addition_enthalpy(spec.parameters, liquid(T, P, water, 0.0), liquid(T, P, water, a),
                                        {"carbon-dioxide": 1.0}, a, T, P, phase="vapor", observed=0.0,
                                        form="difference", scale=1000.0)
            return {"integral heat of absorption": checked(reg.predict(spec.model, item)) / 1000.0}, {}
        if not a:
            problem = liquid(T, P, source_masses[1] * (1 - w) / (w * source_masses[2]), a)
        elif family == "species":
            problem = packet_problem(species_templates, T, a, w)
        else:
            loaded = request(reference, T, a, w, "Amundsen2009")
            loaded["pressure"] = dict(role="fixed", value=P, bounds=[1.0, 1e7])
            loaded["phases"] = [phase for phase in loaded["phases"] if phase["fluid_role"] == "liquid"]
            problem = fixed_reference(_problem_from_request(loaded))
        if family == "species":
            x = solve(spec.model, problem).phase_mole_fractions(0)
            values = {name: math.fsum(x[i] for i in indices) for name, indices in species.items()}
        else:
            item = reg.observation(spec.parameters, "phase_density", problem, observed=1000.0, form="difference",
                                   scale=1.0, phase=problem.phases[0].name, mass_basis=True)
            values = {"liquid density": checked(reg.predict(spec.model, item))}
        pressure = bubble(T, a, w).pressure
        return values, dict(bubble_pressure_Pa=pressure, below_bubble_pressure=P < pressure)

    fresh, differences = {}, {}
    for path in sorted(folder.glob("*.json.gz")):
        family = path.name.removesuffix(".json.gz")
        retained = read(path)["rows"]
        fields = ("temperature_K", "pressure_Pa", "analytical_loading", "mea_mass_fraction", "liquid_mea_mole_fraction")
        fresh[family] = []
        for row in retained:
            T, P, a, w, x = (row.get(key) for key in fields)
            item = {key: row[key] for key in ("curve", "sampling", "quantity", "unit", *fields) if key in row}
            try:
                values, updates = evaluate(family, None if family == "mea-water" else T,
                                           None if family == "pressure" else P, a, w, x)
                item.update(value=values[row["quantity"]], status="available", requested_tolerance_met=True, **updates)
            except (ValueError, RuntimeError) as error:
                item.update(value=None, status="unavailable", cause=f"{type(error).__name__}: {error}")
            fresh[family].append(item)
        coordinates = tuple(key for key in fields if key != ("temperature_K" if family == "mea-water" else "pressure_Pa"))
        differences[family] = curve_differences(retained, fresh[family],
            lambda row: (row["curve"], row["sampling"], row["quantity"], *(row.get(key) for key in coordinates)))
    return dict(curves=fresh, curve_differences=differences)


def band_statistics(points):
    groups = {}
    for row in points:
        T = row["T_K"]
        band = "absorber" if T <= 353.2 else "stripper" if T >= 370.0 else "intermediate"
        keys = [(row["property"], band, row["role"], cohort) for cohort in ("all", row["cohort"])]
        for key in keys:
            groups.setdefault(key, []).append(row)
    summary = []
    for key, group in sorted(groups.items()):
        available = [row for row in group if row["predicted"] is not None]
        errors = [row["predicted"] - row["observed"] for row in available]
        relative = [error / row["observed"] for error, row in zip(errors, available, strict=True)]
        count = len(available)
        summary.append(
            dict(
                zip(("property", "band", "role", "cohort"), key, strict=True),
                n=len(group),
                available=count,
                AARD_percent=100 * sum(map(abs, relative)) / count if count else None,
                RMSE=math.sqrt(sum(error**2 for error in errors) / count) if count else None,
                bias=sum(errors) / count if count else None,
                mean_signed_relative_percent=100 * sum(relative) / count if count else None,
                T_min_K=min(row["T_K"] for row in group),
                T_max_K=max(row["T_K"] for row in group),
                unit=group[0]["unit"],
                sources=" ".join(sorted({row["source"] for row in group})),
            )
        )
    return summary




def retained_state_targets(mapping, model, observation, retained, *, reference_pressure_pa=None):
    request = corrected_request(observation["request"], mapping)
    problem = _problem_from_request(request)
    if reference_pressure_pa is not None:
        for reaction in problem.reactions:
            reaction.reference = equilibrium.ReactionReference(reaction.reference.source_basis,
                                                               reference_pressure_pa=reference_pressure_pa)
    result = equilibrium.solve_equilibrium(model, problem)
    outputs = {output["identity"]: output for output in request["outputs"]}
    phases = {phase.name: i for i, phase in enumerate(problem.phases)}
    for target, reference in zip(observation["targets"], retained, strict=True):
        identity = target["identity"]
        if identity != reference["target"]:
            raise ValueError(f"Different target in the retained state for {identity}")
        value = None
        if result.requested_tolerance_met:
            output = outputs[target["prediction_identity"]]
            index = phases[output["phase_identity"]]
            fractions = dict(zip(COMPONENT_IDS, result.phase_mole_fractions(index), strict=True))
            if (
                identity.startswith(("Matin", "Bottinger"))
                and identity.endswith("::HCO3-")
                and target["basis"] != "true-species-liquid-mole-fraction-linear-aggregate"
            ):
                value = fractions["bicarbonate-anion"] + fractions["carbonate-anion"]
            else:
                coefficient_species = problem.phases[index].support or COMPONENT_IDS
                value = sum(
                    x * fractions[species]
                    for species, x in zip(coefficient_species, output["coefficients"], strict=True)
                )
            if output["selector"] == "phase.partial_pressure":
                value *= result.pressure
        yield dict(
            identity=identity,
            quantity=reference["quantity"],
            group=reference["kind"],
            observed=reference["observed"],
            retained=reference["predicted"],
            predicted=value,
            status="Available" if result.requested_tolerance_met else "Unavailable",
            message=result.message,
        )


def replay_part1(declaration):
    mapping = parameter_mapping(declaration["endpoint"])
    spec = bind_mea(mapping, declaration["specification"], reaction_reference_pressure_pa=None)
    spec.inputs["endpoint"] = mapping
    fitted = spec.inputs["observations"]["fitted"]
    plain = epcsaft.Mixture(spec.parameters)
    template = load_state_packet()["observations"][0]["request"]
    loaded_template = next(
        item["request"] for item in load_state_packet()["observations"] if item["identity"] == "Bottinger2008_state_046"
    )
    masses = {row["component_id"]: row["fixed"]["molar_mass"]["value"]["magnitude"] for row in mapping["components"]}
    frozen_masses = template["reaction_system"]["molar_masses_kg_per_mol"]
    liquid_basis = _problem_from_request(corrected_request(loaded_template, mapping))
    groups = {}
    heat = []
    with tarfile.open(input_path(declaration["assessment"])) as archive:
        for entry in sorted(archive.getmembers(), key=lambda entry: entry.name.startswith("declared-density-rows/")):
            kind = entry.name.split("/", 1)[0]
            if not entry.isfile() or kind not in (
                "states-rows",
                "density-rows",
                "declared-density-rows",
                "cp-rows",
                "calorics-rows",
                "carbonate-rows",
            ):
                continue
            record = json.load(archive.extractfile(entry))
            source, reference = record["input"], record["result"]
            if kind == "states-rows":
                if source["group"] != "packet" or any(row["quantity"] == "species" for row in reference["targets"]):
                    rows = retained_state_targets(mapping, plain, source["observation"], reference["targets"])
                    for row in rows:
                        label = row["group"] if row["quantity"] == "pressure" else "species"
                        if label == "transfer":
                            fraction = source["observation"]["request"]["reaction_system"]["analytical_feed_contract"]
                            label = f"Aronu {100 * float(fraction['source_coordinates']['MEA_weight_fraction']):g} wt% pressures"
                        groups.setdefault(label, []).append(row)
                continue
            if kind == "carbonate-rows":
                request = json.load(archive.extractfile(f"carbonate-requests/{source['id']}.json"))
                state = _problem_from_request(corrected_request(request, mapping))
                result = equilibrium.solve_equilibrium(plain, state)
                value = None
                if result.requested_tolerance_met:
                    fractions = dict(zip(COMPONENT_IDS, result.phase_mole_fractions(0), strict=True))
                    carbon = sum(
                        fractions[species]
                        for species in ("carbon-dioxide", "carbamate-anion", "bicarbonate-anion", "carbonate-anion")
                    )
                    value = fractions["carbonate-anion"] / carbon
                groups.setdefault("Jakobsen carbonate share", []).append(
                    dict(
                        identity=source["id"],
                        observed=reference["observed_share"],
                        retained=reference["predicted_share"],
                        predicted=value,
                        status="Available" if value is not None else "Unavailable",
                        message=result.message,
                    )
                )
                continue
            if kind == "calorics-rows":
                heat.append(
                    dict(
                        identity=source["record_id"],
                        T_K=source["temperature_K"],
                        pressure=source["system_pressure_Pa"],
                        observed=-reference["observed_kJ_mol"],
                        loading=source["alpha_final"],
                        previous_loading=0.0,
                        retained=-reference["predicted_kJ_mol"],
                        group=f"{reference['source']} heats",
                    )
                )
                continue
            T, P = reference["T_K"], reference.get("P_Pa", source.get("P_Pa"))
            observed = reference.get("observed_kg_m3")
            if kind == "cp-rows":
                feed = source["analytical_feed"]
                observed = source["source_observed_kJ_kg_K"]
                state = copy.copy(liquid_basis)
                state.T, state.P, state.feed = T, P, equilibrium.Amounts(feed)
                scale = sum(feed.values()) / sum(n * masses[c] for c, n in feed.items()) / 1000
                item = reg.observation(
                    spec.parameters,
                    "equilibrium_isobaric_heat_capacity",
                    state,
                    phase=state.phases[0].name,
                    observed=observed / scale,
                    form="difference",
                    scale=1.0,
                )
                prediction = reg.predict(spec.model, item)
                label, reference_key = "Four Hilliard heat capacities", "equilibrium_cp_kJ_kg_K"
                value = prediction.value * scale if prediction.status.name == "Available" else None
                status, message = prediction.status.name, prediction.message
            else:
                loading = reference["loading"]
                fraction = reference["mea_mass_fraction"]
                label = reference["source"] + (
                    " all" if reference["source"] == "Han2012" else " loaded" if loading else " CO2-free"
                )
                reference_key = "predicted_kg_m3"
                if fraction == 1 and not loading:
                    model = epcsaft.Pure(epcsaft.Parameters.from_mapping(mapping, components=["monoethanolamine"]))
                    value = model.state(T, P=P, phase="liquid").molar_density * masses["monoethanolamine"]
                    status, message = "Available", None
                else:
                    if kind == "declared-density-rows":
                        feed = reference["declaration"]["analytical_feed"]
                        state = copy.copy(liquid_basis)
                        state.T, state.P, state.feed = T, P, equilibrium.Amounts(feed)
                    elif loading:
                        request = source_feed_request(
                            loaded_template,
                            dict(
                                source_key="Amundsen2009",
                                CO2_loading=loading,
                                temperature_reported_C=T - 273.15,
                                MEA_weight_fraction=fraction,
                            ),
                        )
                        state = _problem_from_request(corrected_request(request, mapping))
                        state.P = P
                    else:
                        water = frozen_masses[1] * (1 - fraction) / (fraction * frozen_masses[2])
                        state = equilibrium.Problem(
                            T=T,
                            P=P,
                            feed=equilibrium.Amounts({"monoethanolamine": 1.0, "water": water}),
                            reactions=liquid_basis.reactions,
                            neutral_reference=liquid_basis.neutral_reference,
                            phases=[equilibrium.Phase("L", kind="liquid", support=COMPONENT_IDS)],
                            row_tolerance=1e-10,
                        )
                    item = reg.observation(
                        spec.parameters,
                        "phase_density",
                        state,
                        phase=state.phases[0].name,
                        observed=observed,
                        form="difference",
                        scale=1.0,
                        mass_basis=True,
                    )
                    prediction = reg.predict(spec.model, item)
                    value = prediction.value if prediction.status.name == "Available" else None
                    status, message = prediction.status.name, prediction.message
            group = groups.setdefault(label, {})
            group[reference["id"]] = dict(
                identity=reference["id"],
                observed=observed,
                retained=reference[reference_key],
                predicted=value,
                status=status,
                message=message,
            )
    groups = {name: list(rows.values()) if isinstance(rows, dict) else rows for name, rows in groups.items()}
    ratios = evaluate(spec, [row for row in fitted if row["group"] == "Jakobsen"])
    retained_ratios = {row["identity"]: row for row in read(declaration["ratios"])}
    groups["Species ratios"] = [
        dict(row, predicted=row["value"], retained=retained_ratios[row["identity"]]["value"]) for row in ratios
    ]
    with input_path(declaration["cp_source"]).open(newline="") as stream:
        records = list(heat_capacity_records(spec, csv.DictReader(stream)))
    retained_cp = {row["identity"]: row for row in read(declaration["broad_cp"])["rows"]}
    for record, result in zip(records, evaluate(spec, records), strict=True):
        identity = record["identity"]
        row = retained_cp[identity]
        groups.setdefault(row["group"], []).append(
            dict(
                identity=identity,
                observed=row["observed_kJ_kg_K"],
                retained=row["predicted_kJ_kg_K"],
                predicted=result["value"] / record["mass_to_mol"] if result["value"] is not None else None,
                status=result["status"],
            )
        )
    templates, _ = pressure_inputs(declaration)
    heat.extend(kim_intervals(declaration["kim"], declaration["heat_pressure"], declaration["loading_ceiling"]))
    for row in heat_intervals(spec, mapping, templates, heat):
        groups.setdefault(row["group"], []).append(row)
    canonical = groups.pop("canonical")
    identities = {row["identity"] for row in fitted}
    groups["Six-source pressures"] = canonical
    groups["47 current-fitted pressures"] = [row for row in canonical if row["identity"] in identities]
    groups["112 current-not-fitted pressures"] = [row for row in canonical if row["identity"] not in identities]
    groups["Wagner pressures"] = groups.pop("wagner")
    groups["Species fractions"] = groups.pop("species")
    summaries = []
    for reference in read(declaration["statistics"]):
        name = reference["group"]
        rows = groups[name]
        metric = "aard_percent" if reference["metric"] == "AARD (%)" else "rmse"
        statistics = comparison_metrics(rows, "predicted")
        summaries.append(
            dict(
                group=name,
                n=statistics["n"],
                retained_rows=reference["n"][0],
                replayed_rows=statistics["n"],
                metric=reference["metric"],
                retained=reference["deviations"][0],
                replayed=statistics[metric],
            )
        )
    return dict(groups=groups, statistics=summaries)


FIT_SETS = {
    "published-properties": dict(
        replay=replay_part1,
        archive=CAMPAIGN_ARCHIVE,
        specification=HISTORICAL_SPEC,
        endpoint=SAME_DATA / "polley-2026-explicit-defaults.json",
        assessment=SAME_DATA / "part1/published/selected-assessment/assessment-rows.tar.gz",
        ratios=SAME_DATA / "part1/published/ratios.json",
        broad_cp=SAME_DATA / "part1/published/heat-capacity-264.json",
        cp_source=BUNDLE / "heat-capacity-264/sources.csv",
        kim=SAME_DATA / "part1/published/kim2007-heat-pathways/kim-heat.csv",
        heat_pressure=1734000.0,
        loading_ceiling=0.6,
        statistics=SAME_DATA / "part1-scores.json",
        **PRESSURE_INPUTS,
    ),
    "water-bicarbonate-ablation": dict(
        route=MEARoute,
        declaration=HISTORICAL_SPEC,
        reference_pressure_pa=P_REF,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=RESULTS / "mea/water-bicarbonate-ablation/fit/A.json.gz",
        endpoint_keys=("endpoint",),
        reference=RESULTS / "mea/water-bicarbonate-ablation/fit/A.json.gz",
        reference_keys=("replay",),
        retained=RESULTS / "move/mea/water-bicarbonate-ablation/fit",
    ),
    "reported": dict(
        route=MEARoute,
        declaration=HISTORICAL_SPEC,
        retained=RESULTS / "move/mea/reported/fit",
        preserved=RESULTS / "mea/reported/fit",
        reference_pressure_pa=P_REF,
        maximum_seconds=2700,
        replay_tolerance=1e-10,
    ),
}

FIT_SETS["water-anion-control"] = FIT_SETS["reported"] | dict(
    retained=RESULTS / "move/mea/water-anion-control/fit",
    water_anion_intercepts=True,
)

FIT_SETS["common-pressure-weight"] = FIT_SETS["reported"] | dict(
    retained=RESULTS / "move/mea/common-pressure-weight/fit",
    pressure_log_scale=0.05,
    held_pressure_groups=("Kiepe",),  # CO₂–water, with no amine.
)
