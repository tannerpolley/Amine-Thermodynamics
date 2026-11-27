"""Fixed-reference MEA declaration and source reaction basis."""

from __future__ import annotations

import copy
from functools import cache
import csv
from dataclasses import dataclass
import gzip
import json
import math
import re
import tarfile
from pathlib import Path

from .fit import compare_rows, retained_endpoint, route_for, save
from .model import (
    CAMPAIGN_ARCHIVE,
    P_REF,
    REPORTED,
    ROOT,
    Route,
    evaluate,
    parameter_mapping,
    parameter_values,
    replay,
    target_identity,
    with_parameter_values,
)
from MEA.common.mea_source_contracts import (
    EXPECTED_REACTION_CORRELATIONS,
    REACTION_CONTRACT_PATH,
)
from .records import RESULTS, archive_paths, input_path, read
from MEA.solvent_specification import SolventSpecification
import epcsaft
import numpy as np
from epcsaft import equilibrium, regression as reg
from scipy.constants import R

from .wheel import verify

BUNDLE = ROOT / "analyses/mea_parameter_bundle"
HISTORICAL_SPEC = BUNDLE / "results/adoption-297/historical-spec/MEA.toml"
SALT_FIT = BUNDLE / "results/salt-anchored-435/MEA/F4"
EXPANDED_FIT = ROOT / "analyses/round_7/results/E"
RESTRICTION_FIT = BUNDLE / "results/reduced-refit"
PAPER_EVIDENCE = BUNDLE / "results/paper-evidence-341"
HONG = BUNDLE / "results/same-data-comparison/hong-2027"
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


def write_expanded_weights_summary():
    wheel = verify()
    results = ROOT / "analyses/amines/results/mea"
    stage = results / "expanded-weights/replay"
    expanded = read(stage / "endpoint.json.gz")
    reported = read(results / "reported/replay/endpoint.json.gz")
    reported_off = read(REPORTED / "MEA/off-window.json.gz")
    if any(record["wheel"] != wheel for record in (expanded, reported, reported_off)):
        raise ValueError("MEA comparison records use another wheel")
    expanded_off = expanded["F4"]["off_window"]["rows"]
    differences, _ = compare_rows(reported_off["rows"], expanded_off)
    if differences:
        raise ValueError(f"Different MEA off-window populations: {differences}")

    heat_file = EXPANDED_FIT.parent / "display-replays/mea-heat-sensitivity.json.gz"
    heat = read(heat_file)["replay"]["rows"]
    hot_heat = {}
    for source in ("Kim2014", "Vinjarapu2024"):
        cohort = [row for row in heat if row["source"] == source and row["T_K"] >= 370]
        values = [row["predicted_kJ_mol"] for row in cohort if row["status"] == "available"]
        hot_heat[source] = dict(available=len(values), attempted=len(cohort),
                               minimum=min(values), maximum=max(values))
    save(stage / "summary.json", dict(
        wheel=wheel,
        hot_heat=hot_heat,
        off_window=dict(
            reported=off_window_statistics(reported_off["rows"]),
            expanded=off_window_statistics(expanded_off),
            incumbent=off_window_statistics(expanded["incumbent"]["off_window"]["rows"]),
            population=len(expanded_off),
        ),
        objective={name: dict(
            count=len(rows),
            expanded_fit=expanded["F4"][name + "_cost"],
        ) for name, rows in (("original", reported["replay"]["rows"]),
                             ("expanded", expanded["F4"]["rows"]))},
    ))


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


def replay_expanded_weights(declaration):
    templates, population = pressure_inputs(declaration)
    with input_path(declaration["wagner"]).open(newline="") as stream:
        wagner = [row for row in csv.DictReader(stream) if row["admitted"] == "yes"]

    cases = {}
    for name, (parameters, reference) in declaration["cases"].items():
        reference = read(reference)
        mapping = read(parameters)
        spec = bind_mea(mapping, declaration["specification"], reaction_reference_pressure_pa=None)
        spec.inputs["endpoint"] = mapping
        originals = spec.inputs["observations"]["fitted"]
        legacy, added = pressure_additions(spec, templates, population)
        old_ids = {row["identity"] for row in legacy}
        hot_wagner = wagner_pressure_records(spec, legacy[0], templates, wagner, minimum_temperature=370)
        rows = evaluate(spec, [*originals, *added])
        held = evaluate(spec, hot_wagner)
        pressure_rows = {row["identity"]: row for row in rows if row["identity"] in population}
        hot = [
            row
            for identity, row in pressure_rows.items()
            if float(population[identity]["temperature_reported_C"]) + 273.15 >= 370
        ]
        pools = dict(
            legacy=[row for identity, row in pressure_rows.items() if identity in old_ids],
            added=[row for identity, row in pressure_rows.items() if identity not in old_ids],
            hot_expanded=hot,
            hot_published=hot + held,
            all_pressure=list(pressure_rows.values()),
        )
        for identity, row in pressure_rows.items():
            source = population[identity]
            pools.setdefault(source["source_key"], []).append(row)
            pools.setdefault(f"{pressure_series(source)} C nominal", []).append(row)
        differences, values = compare_rows(reference["rows"] + reference["hot_wagner"], rows + held)
        cost = [
            math.fsum(row["cost"] for row in group) if all("cost" in row for row in group) else None
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
        if name in declaration["off_window"]:
            cases[name]["off_window"] = off_window_pressures(
                spec, legacy[0], templates, population, read(declaration["off_window"][name])
            )
    return cases


def transfer_pressure_records(spec, legacy, templates, canonical, rows):
    for row in rows:
        source = canonical[row["identity"].removeprefix("transfer:canonical:")]
        loading = float(source["CO2_loading"])
        template = min(templates[pressure_series(source)], key=lambda item: abs(item[0] - loading))[1]
        yield pressure_record(
            spec, legacy, row["target"], source_feed_request(template, source),
            float(row["observed"]), row["source"], "transfer",
        )


def replay_restrictions(declaration):
    templates, population = pressure_inputs(declaration)
    with input_path(declaration["statistics"]).open(newline="") as stream:
        agreement = {(row["fit"], row["dataset"]): row for row in csv.DictReader(stream)}
    cases = {}
    for name in declaration["cases"]:
        folder = declaration["reference"] / name
        mapping = parameter_mapping(folder / "parameters.json")
        spec = bind_mea(mapping, declaration["specification"], reaction_reference_pressure_pa=None)
        spec.inputs["endpoint"] = mapping
        result = replay(spec)
        retained = read(folder / "replay.json")
        differences, values = compare_rows(retained["rows"], result["rows"])
        legacy, additional = pressure_additions(spec, templates, population)
        additional = evaluate(spec, additional)
        original_ids = {row["identity"] for row in legacy}
        selected = {row["identity"] for row in additional}
        with input_path(declaration["assessment"][name]).open(newline="") as stream:
            assessment = list(csv.DictReader(stream))
        prior = [row for row in assessment if row["target"] in selected]
        held = additional
        if name == declaration["transfer_case"]:
            with input_path(declaration["wagner"]).open(newline="") as stream:
                wagner = [row for row in csv.DictReader(stream) if row["admitted"] == "yes"]
            with input_path(declaration["canonical"]).open(newline="") as stream:
                canonical = {row["observation_id"]: row for row in csv.DictReader(stream)}
            transfers = [row for row in assessment if row["kind"] == "transfer"]
            extra = wagner_pressure_records(spec, legacy[0], templates, wagner) + list(
                transfer_pressure_records(spec, legacy[0], templates, canonical, transfers)
            )
            held = additional + evaluate(spec, extra)
            prior.extend(row for row in assessment if row["kind"] in ("wagner", "transfer"))
        held = [dict(row, role="not fitted") for row in held]
        held_differences, held_values = compare_rows(
            [
                dict(
                    identity=row["target"],
                    value=float(row["predicted"]) if row["predicted"] else None,
                    status=row["status"],
                    requested_tolerance_met=row["status"] == "Available",
                    role="not fitted",
                )
                for row in prior
            ],
            held,
        )
        pools = {
            "fitted: fitted CO2 partial pressure": [row for row in result["rows"] if row["identity"] in original_ids],
            "fitted: loaded density": [row for row in result["rows"] if row["group"] == "loaded density"],
            "not fitted: six-source pressures": additional,
        }
        aard = {
            key: dict(
                retained=float(agreement[name, key]["aard_percent"]), replayed=pressure_statistics(rows)["AARD_percent"]
            )
            for key, rows in pools.items()
        }
        cases[name] = dict(
            result,
            rows=[dict(row, role="fitted") for row in result["rows"]],
            retained_cost=retained["cost"],
            row_differences=differences + held_differences,
            value_differences=values + held_values,
            comparisons=held,
            aard_percent=aard,
            parameter_source=(folder / "parameters.json").relative_to(ROOT).as_posix(),
        )
    return dict(cases=cases)


def replay_bound_profiles(declaration):
    mapping = parameter_mapping(declaration["endpoint"])
    folder = declaration["profile"]
    coordinates = read(folder / "inputs.json")["coordinates"]
    indices = {coordinate["identity"]: index for index, coordinate in enumerate(coordinates)}
    baseline = bind_mea(mapping, declaration["specification"], reaction_reference_pressure_pa=None)
    retained_predictions = read(folder / "predictions.json")
    results = []
    baseline_rows = {row["identity"]: row for row in baseline.inputs["observations"]["fitted"]}
    records = []
    for row in retained_predictions["records"]:
        identity = row["identity"]
        source = baseline_rows[identity.removesuffix(":bicarbonate-only")]
        records.append(dict(source, arguments=row["arguments"], identity=identity, group=row["group"]))
    baseline_values = {row["identity"]: row["value"] for row in evaluate(baseline, records)}
    base_cost = replay(baseline)["cost"]
    for profile in read(folder / "profiles.json"):
        index = indices[profile["parameter"]]
        name = f"profile-{index}-{profile['fraction']}"
        fit = read(folder / name / "fit.json")
        physical = iter(fit["physical"])
        updates = {}
        for i, coordinate in enumerate(coordinates):
            for family, species, factor in coordinate["targets"]:
                identity = target_identity(mapping, family, species)
                updates[identity] = next(physical) if i in fit["indices"] else factor * profile["fixed_value"]
        if next(physical, None) is not None:
            raise ValueError(f"{name}: unexpected profile coefficient")
        point = with_parameter_values(mapping, updates)
        spec = bind_mea(point, declaration["specification"], reaction_reference_pressure_pa=None)
        result = replay(spec)
        predicted = evaluate(spec, records)
        retained = read(folder / name / "predictions.json")["values"]
        # The retained derivative report provides finite predictions for each requested row.
        before = [
            dict(identity=row["identity"], value=value, status="Available", requested_tolerance_met=True)
            for row, value in zip(records, retained, strict=True)
        ]
        differences, values = compare_rows(before, predicted)
        changes = {}
        for row in predicted:
            if row["status"] == "Available" and row["requested_tolerance_met"]:
                change = abs(row["value"] / baseline_values[row["identity"]] - 1)
                changes[row["group"]] = max(changes.get(row["group"], 0.0), change)
        results.append(
            dict(
                result,
                profile=name,
                retained=profile,
                comparisons=predicted,
                row_differences=differences,
                value_differences=values,
                delta_cost=result["cost"] - base_cost,
                group_changes=changes,
            )
        )
    return dict(profiles=results)


class Hong:
    def __init__(self, parameters):
        self.input = read(parameters)
        self.masses = {
            row["component_id"]: row["fixed"]["molar_mass"]["value"]["magnitude"]
            for row in self.input["parameters"]["components"]
        }
        self.species = tuple(self.masses)
        self.temperatures = np.arange(9) * 10 + 313.15
        self.loadings = np.arange(1, 11) / 10
        self.weights = np.asarray(self.input["weights"])

    def weight(self, a, T):
        return float(np.interp(T, self.temperatures, [np.interp(a, self.loadings, row) for row in self.weights]))

    def coefficient(self, name, magnitude, unit="dimensionless"):
        return dict(identity=name, value=dict(magnitude=magnitude, unit=unit))

    def model(self, w):
        doc = copy.deepcopy(self.input["parameters"])
        topology = doc["topology"]
        neutral = self.input["neutral_association"]
        (km, kw), (em, ew) = (
            [e[k]["value"]["magnitude"] for e in neutral["edges"][:2]] for k in ("volume", "energy_over_k")
        )
        cross_volume = ((km ** (1 / 3) + kw ** (1 / 3)) / 2) ** 3
        cross_energy = self.input["mea_water_alpha_HB"] * math.sqrt(em * ew)
        intercept = -800 if w == 0 else 800 if w == 1 else math.log(w / (1 - w))
        doc["pathway_weight"]["coefficients"][0]["value"]["magnitude"] = intercept
        reactive_sites, topology["sites"] = topology["sites"], []
        for site in reactive_sites:
            suffix = site["site_id"][1:]
            for q in neutral["sites"]:
                topology["sites"].append(dict(q, site_id=q["site_id"] + suffix, pathway=site["pathway"]))
            topology["sites"].append(site)
            for i, q in enumerate(copy.deepcopy(neutral["edges"])):
                for end in ("endpoint_a", "endpoint_b"):
                    q[end]["site_id"] += suffix
                if i >= 2:
                    q.update(
                        energy_over_k=self.coefficient(f"cross-{i}", cross_energy, "kelvin"),
                        volume=self.coefficient(f"cross-{i}/volume", cross_volume),
                    )
                for k in ("energy_over_k", "volume"):
                    q[k]["identity"] += suffix
                topology["edges"].append(q)
        return epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc))

    def composition(self, a, water):
        n = np.array([1.0, water, a])
        return n / n.sum()

    def phase_solve(self, mix, a, T, water, pinned=0.0):
        x = self.composition(a, water)
        problem = equilibrium.bubble_point(
            liquid=equilibrium.Phase("L", kind="liquid", composition_guess=dict(zip(self.species, x))),
            T=T,
            feed=equilibrium.Amounts(dict(zip(self.species, (1.0, water, a)))),
        )
        if pinned:
            # Seed the same fixed-amount solve with the liquid's 1 bar fugacities.
            state = mix.state(T, P=1e5, x=x, phase="liquid")
            fugacity = x * np.exp(state.log_fugacity_coefficient) * 1e5
            guess = float(fugacity.sum())
            problem.P = equilibrium.Free(guess)
            problem.phases[1].composition_guess = dict(zip(self.species, fugacity / guess))
            problem.phases[1].amount = equilibrium.Pinned(pinned)
        return equilibrium.solve_equilibrium(mix, problem)

    @cache
    def pressure(self, a, T, water, w):
        mix = self.model(w)
        result = self.phase_solve(mix, a, T, water)
        eigenvalue, stability = None, "stable"
        if not result.success:
            match = re.search(r"lowest eigenvalue (-?[\d.eE+-]+)", result.message)
            if match is None or "local phase instability:" not in result.message or float(match[1]) >= 0:
                raise RuntimeError((a, T, water, w, result.message))
            eigenvalue, stability = float(match[1]), "locally unstable"
            result = self.phase_solve(mix, a, T, water, 1e-9)
            if not result.success:
                raise RuntimeError((a, T, water, w, eigenvalue, result.message))
        x, y = np.asarray(result.mole_fractions).reshape(2, 3)
        predicted = float(result.pressure * y[2])
        return dict(
            predicted=predicted,
            stability=stability,
            minimum_eigenvalue=eigenvalue,
            w=w,
            pressure_Pa=result.pressure,
            liquid_density_mol_m3=result.molar_densities[0],
            max_solver_residual=max(map(abs, result.classified_residuals)),
            liquid=x.tolist(),
            vapor=y.tolist(),
        )

    def heat(self, row):
        a, b, T, w = (row[k] for k in ("previous_loading", "loading", "T_K", "water_per_mea"))
        points = [a, a + (b - a) / 4, a + (b - a) / 2, a + 3 * (b - a) / 4, b]
        output, states = {}, []
        for side in (1,) if T == 313.15 else (-1,) if T == 393.15 else (-1, 1):
            label = "warm" if side == 1 else "cool"
            for step in (0.1, 0.01):
                Ta = T + side * step
                p = [
                    (self.pressure(x, T, w, self.weight(x, T)), self.pressure(x, Ta, w, self.weight(x, Ta)))
                    for x in points
                ]
                states.extend(q for pair in p for q in pair)
                g = [-R * math.log(v["predicted"] / u["predicted"]) / (1 / Ta - 1 / T) / 1000 for u, v in p]
                output.update(
                    {
                        f"{label}_{step}_simpson": (g[0] + 4 * g[2] + g[4]) / 6,
                        f"{label}_{step}_halved": (g[0] + 4 * g[1] + 2 * g[2] + 4 * g[3] + g[4]) / 12,
                        f"{label}_{step}_endpoint": g[4],
                    }
                )
        unstable = [r for r in states if r["stability"] == "locally unstable"]
        return dict(
            output,
            stability="locally unstable" if unstable else "stable",
            minimum_eigenvalue=min((q["minimum_eigenvalue"] for q in unstable), default=None),
            max_solver_residual=max(q["max_solver_residual"] for q in states),
            w=self.weight(b, T),
            pressure_states=len(states),
            unstable_pressure_states=len(unstable),
            min_w=min(q["w"] for q in states),
            max_w=max(q["w"] for q in states),
        )

    def predict(self, row):
        T, a, water = (row[k] for k in ("T_K", "analytical_loading", "water_per_mea"))
        if row["block"].startswith("Kim "):
            return self.heat(row)
        w = self.weight(a, 313.15 if row["hilliard_edge"] else T)
        if not row["pressure_Pa"]:
            return self.pressure(a, T, water, w)
        x = self.composition(a, water)
        P = float(row["pressure_Pa"])
        state = self.model(w).state(T, P=P, x=x, phase="liquid")
        return dict(
            predicted=float(state.molar_density * (x @ list(self.masses.values()))),
            w=w,
            liquid_density_mol_m3=state.molar_density,
            pressure_residual_Pa=state.pressure - P,
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


def hong_scores(rows):

    output = []
    for block in dict.fromkeys(r["block"] for r in rows):
        selected = [r for r in rows if r["block"] == block and r["three_model_eligible"]]
        groups = [("all", selected)]
        unmatched = [r for r in rows if r["block"] == block and not r["three_model_eligible"]]
        if unmatched:
            groups.append(("above 0.60, Hong only", unmatched))
        if block == "canonical":
            for domain, base in [("all", selected), ("strict grid", [r for r in selected if r["inside_hong_grid"]])]:
                if domain != "all":
                    groups.append((domain, base))
                for field, labels in [
                    ("adopted_role", ("fitted", "not fitted")),
                    ("stability", ("stable", "locally unstable")),
                ]:
                    groups.extend((f"{domain}, {label}", [r for r in base if r[field] == label]) for label in labels)
        kim_block = block.startswith("Kim ")
        sides = (
            ("cool", "warm")
            if block == "Kim 353.15 K"
            else ("cool",)
            if block == "Kim 393.15 K"
            else ("warm",)
            if kim_block
            else ("",)
        )
        metric = "aard_percent" if block in ("canonical", "wagner") else "rmse"
        for group, data in groups:
            for side in sides:
                key = f"{side}_0.01_halved" if side else "predicted"
                models = [("hong", key), ("adopted", "adopted"), ("polley_hedengren_2026", "polley_hedengren_2026")]
                if data is unmatched:
                    models = models[:1]
                assert len({r["record_id"] for r in data}) == len(data)
                # Every model is scored on the same rows; a row any model cannot predict is listed, not dropped silently.
                unavailable = [r["record_id"] for r in data if any(r.get(k) is None for _, k in models)]
                scored = [r for r in data if r["record_id"] not in unavailable]
                n = len(scored)
                values = {m: comparison_metrics(scored, predicted=k) for m, k in models} if n else {}
                role_2026 = (
                    "fitted / not fitted" if block in ("canonical", "Kim 313.15 K", "Kim 353.15 K") else "not fitted"
                )
                output.append(
                    dict(
                        block=block,
                        subset=group,
                        side=side,
                        n=n,
                        unavailable=unavailable,
                        metric=metric,
                        adopted_fitted=sum(r["adopted_role"] == "fitted" for r in scored),
                        polley_hedengren_2026_role=role_2026 if data is not unmatched else "above_ceiling",
                        hong_role="not fitted",
                        stable=sum(r.get("stability") == "stable" for r in scored),
                        locally_unstable=sum(r.get("stability") == "locally unstable" for r in scored),
                        **{m: values[m][metric] if values else None for m, _ in models},
                    )
                )
    return output


def replay_published_pressures(declaration):
    templates, population = pressure_inputs(declaration)
    with input_path(declaration["wagner"]).open(newline="") as stream:
        wagner = [row for row in csv.DictReader(stream) if row["admitted"] == "yes"]
    results = {}
    for label, (endpoint, path) in declaration["pressure_cases"].items():
        mapping = parameter_mapping(endpoint)
        spec = bind_mea(mapping, declaration["specification"], reaction_reference_pressure_pa=None)
        spec.inputs["endpoint"] = mapping
        legacy, added = pressure_additions(spec, templates, population)
        rows = evaluate(spec, legacy + added + wagner_pressure_records(spec, legacy[0], templates, wagner))
        with input_path(path).open(newline="") as stream:
            prior = [
                dict(
                    identity=row["target"],
                    value=float(row["predicted"]) if row["predicted"] else None,
                    status=row["status"],
                    requested_tolerance_met=row["status"] == "Available",
                )
                for row in csv.DictReader(stream)
                if row["kind"] in ("canonical", "wagner")
            ]
        differences, values = compare_rows(prior, rows)
        canonical = [row for row in rows if row["identity"] in population]
        results[label] = dict(
            rows=rows, row_differences=differences, value_differences=values, canonical=pressure_statistics(canonical)
        )
    baygi = read(declaration["baygi"])
    comparison_ids = {row["target"] for row in baygi["rows"]}
    matched = {
        label: pressure_statistics([row for row in record["rows"] if row["identity"] in comparison_ids])
        for label, record in results.items()
    }
    return dict(results=results, baygi_matched=matched, baygi_literature_input=baygi["reference"])


def replay_hong(declaration):
    model = Hong(declaration["endpoint"])
    with input_path(declaration["admission"]).open(newline="") as stream:
        pressures = {row["record_id"]: row["pressure_Pa"] for row in csv.DictReader(stream)}
    rows = []
    for path in declaration["blocks"]:
        with input_path(path).open(newline="") as stream:
            for record in csv.DictReader(stream):
                row = {field: record[field] for field in ("record_id", "block", "adopted_role")}
                for field in ("hilliard_edge", "three_model_eligible", "inside_hong_grid"):
                    row[field] = record[field] == "True"
                for field in (
                    "T_K",
                    "analytical_loading",
                    "water_per_mea",
                    "observed",
                    "loading",
                    "previous_loading",
                    "adopted",
                    "polley_hedengren_2026",
                ):
                    row[field] = float(record[field]) if record[field] else None
                row["pressure_Pa"] = (
                    float(pressures[row["record_id"]]) if pressures[row["record_id"]] else None
                )
                try:
                    row.update(model.predict(row), failure="")
                except (RuntimeError, ValueError) as error:
                    row["failure"] = str(error)
                row["retained_failure"] = record["failure"]
                rows.append(row)
    comparisons = replay_published_pressures(declaration)
    templates, _ = pressure_inputs(declaration)
    identities = {row["record_id"] for row in rows}
    for column, (name, density, kim) in declaration["comparison_cases"].items():
        endpoint, _ = declaration["pressure_cases"][name]
        mapping = parameter_mapping(endpoint)
        spec = bind_mea(mapping, declaration["specification"], reaction_reference_pressure_pa=None)
        spec.inputs["endpoint"] = mapping
        with input_path(density).open(newline="") as stream:
            records = [row for row in csv.DictReader(stream) if row["id"] in identities]
        predicted = {row["identity"]: row["value"] for row in evaluate(spec, list(density_records(spec, records)))}
        predicted.update({row["identity"]: row["value"] for row in comparisons["results"][name]["rows"]})
        intervals = [
            row for row in kim_intervals(kim, declaration["heat_pressure"], declaration["loading_ceiling"])
            if row["identity"] in identities
        ]
        predicted.update({row["identity"]: row["predicted"] for row in heat_intervals(spec, mapping, templates, intervals)})
        for row in rows:
            row[f"retained_{column}"] = row[column]
            row[column] = predicted[row["record_id"]]
    return dict(rows=rows, statistics=hong_scores(rows), pressure_comparisons=comparisons)


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


def write_reported_property_summary():
    wheel = verify()
    declaration = FIT_SETS["reported"]
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
    save(ROOT / "analyses/amines/results/mea/reported/properties/uncertainty-and-activities.json.gz", dict(
        wheel=wheel, endpoint_fingerprint=selection["endpoint_fingerprint"],
        inputs=[path.relative_to(ROOT).as_posix() for path in (fit_path, activity_path)],
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


def replay_sensitivities(declaration):
    specification = declaration["specification"]
    shared_inputs = read(declaration["share_inputs"])
    prefix = declaration["shared_root"].relative_to(ROOT).as_posix() + "/"
    (control,) = (ROOT / path for path in archive_paths()
                  if path.startswith(prefix) and path.endswith("/arm-replay-costs.json"))
    shared = {}
    for name in declaration["arms"]:
        folder = control.parent / name
        mapping = read(folder / "parameters.json.gz")
        spec = bind_mea(mapping, specification, reaction_reference_pressure_pa=None)
        result = replay(spec)
        retained = read(folder / "replay.json.gz")
        difference, values = compare_rows(retained["rows"], result["rows"])
        share = read(folder / "carbonate-share.json")
        shares = carbonate_shares(spec, shared_inputs, share["rows"])
        share_difference, share_values = compare_rows(share["rows"], shares)
        shared[name] = dict(
            result,
            retained_cost=retained["cost"],
            row_differences=difference + share_difference,
            value_differences=values + share_values,
            shares=shares,
            retained_shares=share["summary"],
        )
    baseline = {row["state"]: row for row in shared["P0"]["shares"]}
    for arm in shared.values():
        rows = arm["shares"]
        for label, subset in (
            ("all", rows),
            ("without 018", [row for row in rows if not row["state"].endswith("_018")]),
        ):
            matched = [row for row in subset if row["status"] == baseline[row["state"]]["status"] == "Available"]
            old = absolute_shares([baseline[row["state"]] for row in matched])["geometric_mean"]
            current = absolute_shares(matched)["geometric_mean"]
            arm.setdefault("summary", {})[label] = dict(
                absolute_shares(subset),
                matched_n=len(matched),
                F2_matched_geometric_mean=old,
                matched_change=current - old if matched else None,
                matched_factor=current / old if matched else None,
            )

    profile = read(declaration["profile_mapping"])
    prior = read(declaration["profile_replay"])
    records = []
    for point, retained in zip([profile["center"], *profile["points"].values()], prior["rows"], strict=True):
        if point["k"] != retained["k"]:
            raise ValueError(f"Bicarbonate profile key differs at {point['k']}")
        spec = bind_mea(point["mapping"], specification, reaction_reference_pressure_pa=None)
        result = replay(spec)
        differences, values = compare_rows(retained["rows"], result["rows"])
        stage = [row for row in result["rows"] if row["group"] != "Kiepe"]
        rss = 2 * math.fsum(row["cost"] for row in stage) if all("cost" in row for row in stage) else None
        records.append(
            dict(
                result,
                k=point["k"],
                retained_cost=retained["replay_cost"],
                stage_rss=rss,
                stage_n=len(stage),
                row_differences=differences,
                value_differences=values,
            )
        )
    center = records[0]
    rank = read(declaration["information"])["result"]["p"]
    variance = center["stage_rss"] / (center["stage_n"] - rank) if center["stage_rss"] is not None else None
    cutoff = 0.5 * variance * declaration["profile_chi_square"] if variance is not None else None
    for point in records:
        point["increase_from_center"] = point["cost"] - center["cost"] if point["cost"] is not None else None

    mapping = parameter_mapping(declaration["endpoint"])
    retained = read(declaration["born"])
    born = {}
    for case in [*retained["cases"], dict(retained["bicarbonate_interior"], ion="bicarbonate-anion")]:
        ion = case["ion"]
        name = f"{ion}-{case['diameter_A']:g}" if ion else "baseline"
        parameters = (
            with_parameter_values(mapping, {f"component/{ion}/born_diameter": case["diameter_A"]}) if ion else mapping
        )
        spec = bind_mea(parameters, specification, reaction_reference_pressure_pa=None)
        result = replay(spec)
        born[name] = dict(result, retained_cost=case["cost"])
        if ion and "jou_pressure" in case:
            target = case["jou_pressure"]
            row = next(row for row in result["rows"] if row["identity"] == target["identity"])
            born[name]["jou_pressure"] = dict(retained=target["perturbed"], replayed=row["value"])
    base = {row["identity"]: row for row in born["baseline"]["rows"]}
    for case in retained["cases"][1:]:
        name = f"{case['ion']}-{case['diameter_A']:g}"
        rows = born[name]["rows"]
        shifts = [
            dict(identity=row["identity"], change_percent=100 * (row["value"] / base[row["identity"]]["value"] - 1))
            for row in rows
            if row["row"].get("quantity") == "PartialPressure"
            and row.get("value") is not None
            and base[row["identity"]].get("value")
        ]
        born[name]["largest_pressure_change"] = max(shifts, key=lambda row: abs(row["change_percent"]))
    largest_objective_change_percent = (
        100 * max(abs(case["cost"] - born["baseline"]["cost"]) for case in born.values()) / retained["reference_cost"]
    )
    return dict(
        shared=shared,
        bicarbonate=dict(
            rows=records, stage_variance=variance, delta_cutoff=cutoff, retained_delta_cutoff=prior["delta_cutoff"]
        ),
        born=born,
        largest_born_objective_change_percent=largest_objective_change_percent,
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


def replay_temperature_bands(declaration):
    endpoint, evidence = declaration["endpoint"], declaration["reference"]
    mapping = parameter_mapping(endpoint)
    spec = bind_mea(mapping, declaration["specification"], reaction_reference_pressure_pa=None)
    spec.inputs["endpoint"] = mapping
    fitted = {row["identity"]: row for row in replay(spec)["rows"]}
    templates, population = pressure_inputs(declaration)
    with input_path(declaration["wagner"]).open(newline="") as stream:
        wagner = [row for row in csv.DictReader(stream) if row["admitted"] == "yes"]
    with input_path(declaration["canonical"]).open(newline="") as stream:
        canonical = {row["observation_id"]: row for row in csv.DictReader(stream)}
    legacy, added = pressure_additions(spec, templates, population)
    pressure = {
        row["identity"]: row
        for row in evaluate(spec, added + wagner_pressure_records(spec, legacy[0], templates, wagner))
    }
    points = []
    with input_path((evidence / "state-targets.csv")).open(newline="") as stream:
        for row in csv.DictReader(stream):
            kind, identity = row["kind"], row["target"]
            if row["quantity"] != "pressure" or kind not in ("canonical", "wagner", "transfer"):
                continue
            if kind == "transfer":
                (record,) = transfer_pressure_records(spec, legacy[0], templates, canonical, [row])
                pressure[identity] = spec.prediction(record)
            prediction = fitted.get(identity, pressure.get(identity))
            role = "fitted" if identity in fitted else "not fitted, 15/45 wt%" if kind == "transfer" else "not fitted"
            cohort = (
                "Hilliard 2008 + Jou 1995 (common149)"
                if role == "fitted"
                else {"canonical": "six-source 30 wt%", "wagner": "Wagner 2013", "transfer": "Aronu 2011 15/45 wt%"}[
                    kind
                ]
            )
            points.append(
                dict(
                    property="CO2 partial pressure",
                    role=role,
                    cohort=cohort,
                    source=row["source"],
                    T_K=float(row["temperature_K"]),
                    observed=float(row["observed"]),
                    predicted=prediction["value"],
                    unit="Pa",
                    identity=identity,
                    status=prediction["status"],
                )
            )

    retained_density = read(evidence / "density-268/density.json")["result"]
    fitted_density = {
        identity.replace("AMU-DENS-", "Amundsen2009_state_"): row
        for identity, row in fitted.items()
        if "density" in row["group"]
    }
    density = evaluate(spec, list(density_records(spec, (row["row"] for row in retained_density))))
    density_differences, density_values = compare_rows(retained_density, density)
    for prediction in density:
        identity, row = prediction["identity"], prediction["row"]
        use_fit = identity in fitted_density
        prediction = fitted_density[identity] if use_fit else prediction
        source, loaded = row["source"], float(row["loading"]) > 0
        points.append(
            dict(
                property="density",
                role="fitted" if use_fit else "not fitted",
                cohort=f"{source} {'loaded' if loaded else 'CO2-free'}",
                source=source,
                T_K=float(row["T_K"]),
                observed=float(row["observed_kg_m3"]),
                predicted=prediction.get("value"),
                unit="kg/m3",
                identity=identity,
                status=prediction["status"],
            )
        )

    with input_path((evidence / "cp.csv")).open(newline="") as stream:
        direct_cp = list(csv.DictReader(stream))
    with input_path(declaration["cp_source"]).open(newline="") as stream:
        cp = list(heat_capacity_records(spec, csv.DictReader(stream)))
    direct_cp_coordinates = {(float(row["T_K"]), float(row["loading"])) for row in direct_cp}
    for source, prediction in zip(cp, evaluate(spec, cp), strict=True):
        row = source["row"]
        T, loading = float(row["T_K"]), float(row["loading"])
        if (T, loading) not in direct_cp_coordinates:
            value = prediction["value"] / source["mass_to_mol"] if prediction["value"] is not None else None
            name = row["source"]
            points.append(
                dict(
                    property="heat capacity",
                    role="not fitted",
                    cohort=f"{name} {'loaded' if loading > 0 else 'CO2-free'}",
                    source=name,
                    T_K=T,
                    observed=float(row["cp_kJ_kg_K"]),
                    predicted=value,
                    unit="kJ/(kg K)",
                    identity=source["identity"],
                    status=prediction["status"],
                )
            )
    for row in direct_cp:
        record = next(record for record in spec.inputs["observations"]["fitted"] if record["identity"] == row["id"])
        problem = spec.problems[record["problem"]]
        masses = {c["component_id"]: c["fixed"]["molar_mass"]["value"]["magnitude"] for c in mapping["components"]}
        factor = sum(problem.feed.values.values()) / sum(n * masses[c] for c, n in problem.feed.values.items()) / 1000
        prediction = fitted[record["identity"]]
        points.append(
            dict(
                property="heat capacity",
                role="fitted",
                cohort="Hilliard 2008 (fitted states)",
                source="Hilliard2008",
                T_K=float(row["T_K"]),
                observed=float(row["observed_kJ_kg_K"]),
                predicted=prediction["value"] * factor,
                unit="kJ/(kg K)",
                identity=record["identity"],
                status=prediction["status"],
            )
        )

    heat = []
    with input_path((evidence / "heat.csv")).open(newline="") as stream:
        for row in csv.DictReader(stream):
            role = "fitted" if row["role"] == "fitted" else "not fitted"
            heat.append(
                dict(
                    identity=row["id"],
                    T_K=float(row["T_K"]),
                    loading=float(row["loading"]),
                    previous_loading=0.0,
                    pressure=float(row["P_Pa"]),
                    observed=-float(row["observed_kJ_mol"]),
                    retained=-float(row["predicted_kJ_mol"]),
                    retained_status="available",
                    cohort=row["source"],
                    role=role,
                    source=row["source"],
                )
            )
    heat_reference = read(declaration["heat_reference"])
    with input_path((evidence / "kim2007-heat-pathways/kim-heat.csv")).open(newline="") as stream:
        for row in csv.DictReader(stream):
            flagged = row["source_inconsistent"] == "True" or row["first_120"] == "True"
            heat.append(
                dict(
                    identity=row["record_id"],
                    T_K=float(row["T_K"]),
                    loading=float(row["loading"]),
                    previous_loading=float(row["previous_loading"]),
                    pressure=heat_reference["system_pressure_Pa"],
                    loading_ceiling=heat_reference["loading_ceiling"],
                    observed=float(row["observed"]),
                    retained=float(row["predicted"]) if row["predicted"] else None,
                    retained_status=row["interval_status"],
                    cohort="Kim and Svendsen 2007",
                    role="not fitted, source-flagged" if flagged else "not fitted",
                    source="Kim2007",
                )
            )
    for row in heat_reference["rows"]:
        cohort = "Kim et al. 2014 (replayed)" if row["source"] == "Kim2014" else "Vinjarapu 2024 Table 5 (replayed)"
        heat.append(
            dict(
                identity=row["record_id"],
                T_K=row["T_K"],
                loading=row["loading"],
                previous_loading=row["previous_loading"],
                pressure=heat_reference["system_pressure_Pa"],
                loading_ceiling=heat_reference["loading_ceiling"],
                observed=row["observed_kJ_mol"],
                retained=row["predicted_kJ_mol"],
                retained_status=row["status"],
                cohort=cohort,
                role="not fitted",
                source=row["source"],
            )
        )
    heat = list(heat_intervals(spec, mapping, templates, heat))
    points += [
        dict(row, property="heat of absorption", unit="kJ/mol CO2")
        for row in heat
        if row["retained_status"] == "available"
    ]
    return dict(
        points=points,
        statistics=band_statistics(points),
        heat=heat,
        density_row_differences=density_differences,
        density_value_differences=density_values,
    )


def retained_state_targets(mapping, model, observation, retained):
    request = corrected_request(observation["request"], mapping)
    problem = _problem_from_request(request)
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
    "temperature-bands": dict(
        replay=replay_temperature_bands,
        archive=CAMPAIGN_ARCHIVE,
        specification=HISTORICAL_SPEC,
        endpoint=RESTRICTION_FIT / "F2/parameters.json",
        reference=RESTRICTION_FIT / "evidence/F2",
        wagner=BUNDLE / "results/temperature-reanchor-140/never-accessed-vle-admission.csv",
        cp_source=BUNDLE / "heat-capacity-264/sources.csv",
        heat_reference=BUNDLE / "results/stripper-temperature-409/heat-replay.json",
        statistics=BUNDLE / "results/stripper-temperature-409/band-table.csv",
        **PRESSURE_INPUTS,
    ),
    "sensitivities": dict(
        replay=replay_sensitivities,
        archive=CAMPAIGN_ARCHIVE,
        specification=HISTORICAL_SPEC,
        endpoint=RESTRICTION_FIT / "F2/parameters.json",
        shared_root=BUNDLE / "results/shared-ion-electrostatics-423",
        share_inputs=BUNDLE / "results/bicarbonate-carbonate-266/inputs.json",
        arms=(
            "P0",
            "M1",
            "M3",
            "M3-refit",
            "P1",
            "P1-refit",
            "bicarbonate-anion-2.5",
            "bicarbonate-anion-3.5",
            "bicarbonate-anion-4",
            "carbonate-anion-2.5",
            "carbonate-anion-4",
            "carbonate-anion-4.953",
            "permittivity-+5pct",
            "permittivity--5pct",
        ),
        profile_mapping=ROOT / "analyses/mdea_mea_workflow/results/shared-bicarbonate-417/profile.json.gz",
        profile_replay=ROOT / "analyses/round_5/results/C/MEA-k-profile.json.gz",
        profile_chi_square=3.84146,
        information=BUNDLE / "results/objective-weights-420/MEA/information.json.gz",
        born=BUNDLE / "results/born-diameter-sensitivity-405/summary.json",
    ),
    "published-properties": dict(
        replay=replay_part1,
        archive=CAMPAIGN_ARCHIVE,
        specification=HISTORICAL_SPEC,
        endpoint=HONG.parent / "polley-2026-explicit-defaults.json",
        assessment=HONG.parent / "part1/published/selected-assessment/assessment-rows.tar.gz",
        ratios=HONG.parent / "part1/published/ratios.json",
        broad_cp=HONG.parent / "part1/published/heat-capacity-264.json",
        cp_source=BUNDLE / "heat-capacity-264/sources.csv",
        kim=HONG.parent / "part1/published/kim2007-heat-pathways/kim-heat.csv",
        heat_pressure=1734000.0,
        loading_ceiling=0.6,
        statistics=HONG.parent / "part1-scores.json",
        **PRESSURE_INPUTS,
    ),
    "published": dict(
        replay=replay_hong,
        archive=CAMPAIGN_ARCHIVE,
        endpoint=HONG / "parameters.json",
        specification=HISTORICAL_SPEC,
        **PRESSURE_INPUTS,
        wagner=BUNDLE / "results/temperature-reanchor-140/never-accessed-vle-admission.csv",
        pressure_cases={
            "Polley and Hedengren": (
                BUNDLE / "results/same-data-comparison/polley-2026-explicit-defaults.json",
                BUNDLE / "results/same-data-comparison/part1/published/selected-assessment/state-targets.csv",
            ),
            "16-parameter calibration": (
                RESTRICTION_FIT / "F0/parameters.json",
                BUNDLE / "results/adoption-297/paper-evidence/state-targets.csv",
            ),
            "prior F2": (RESTRICTION_FIT / "F2/parameters.json", PAPER_EVIDENCE / "paper-evidence/state-targets.csv"),
            "salt-anchored": (
                SALT_FIT / "parameters.json",
                SALT_FIT.parent / "evidence/F4/state-targets.csv",
            ),
        },
        comparison_cases={
            "adopted": (
                "prior F2",
                PAPER_EVIDENCE / "paper-evidence/density.csv",
                PAPER_EVIDENCE / "paper-evidence/kim2007-heat-pathways/kim-heat.csv",
            ),
            "polley_hedengren_2026": (
                "Polley and Hedengren",
                HONG.parent / "part1/published/selected-assessment/density.csv",
                HONG.parent / "part1/published/kim2007-heat-pathways/kim-heat.csv",
            ),
        },
        heat_pressure=1734000.0,
        loading_ceiling=0.6,
        baygi=SALT_FIT.parent / "baygi-matched-pressure.json",
        admission=HONG / "admission.csv",
        statistics=HONG / "scores.csv",
        blocks=tuple(
            HONG / f"{name}.csv"
            for name in (
                "canonical",
                "wagner",
                "Amundsen2009",
                "Hartono2014",
                "Han2012",
                "Kim 313.15 K",
                "Kim 353.15 K",
                "Kim 393.15 K",
            )
        ),
    ),
    "restrictions": dict(
        replay=replay_restrictions,
        archive=CAMPAIGN_ARCHIVE,
        specification=HISTORICAL_SPEC,
        reference=RESTRICTION_FIT,
        statistics=RESTRICTION_FIT / "agreement.csv",
        **PRESSURE_INPUTS,
        cases=("F0", "F1", "F2", "F3", "F4", "F4-0", "F5"),
        transfer_case="F2",
        wagner=BUNDLE / "results/temperature-reanchor-140/never-accessed-vle-admission.csv",
        assessment={
            "F0": BUNDLE / "results/adoption-297/paper-evidence/state-targets.csv",
            **{
                name: RESTRICTION_FIT / f"evidence/{name}/state-targets.csv"
                for name in ("F1", "F2", "F3", "F4", "F4-0", "F5")
            },
        },
    ),
    "restrictions-bound-profiles": dict(
        replay=replay_bound_profiles,
        archive=CAMPAIGN_ARCHIVE,
        specification=HISTORICAL_SPEC,
        endpoint=RESTRICTION_FIT / "F2/parameters.json",
        profile=PAPER_EVIDENCE / "uncertainty",
    ),
    "system-pressure-bound-profiles": dict(
        replay=replay_bound_profiles,
        archive=CAMPAIGN_ARCHIVE,
        specification=HISTORICAL_SPEC,
        endpoint=SALT_FIT / "parameters.json",
        profile=SALT_FIT / "uncertainty",
    ),
    "expanded-weights": dict(
        replay=replay_expanded_weights,
        archive=CAMPAIGN_ARCHIVE,
        specification=HISTORICAL_SPEC,
        **PRESSURE_INPUTS,
        wagner=BUNDLE / "results/temperature-reanchor-140/never-accessed-vle-admission.csv",
        off_window={name: EXPANDED_FIT / f"{name}/off-window.json.gz" for name in ("F4", "incumbent")},
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
        retained=RESULTS / "mea/reported/fit",
        reference_pressure_pa=P_REF,
        maximum_seconds=2700,
        replay_tolerance=1e-10,
        diagnostic_attempts=("A-loose.json.gz",),
    ),
}
