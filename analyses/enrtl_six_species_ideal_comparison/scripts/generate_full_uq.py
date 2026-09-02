"""Run the current nine-species ePC-SAFT all-parameter screening study.

This is a diagnostic screening-prior UQ, not a posterior parameter estimate.
The Engine supplies EOS states and source-reference transfers; the temporary
SciPy/Newton layer solves the closed reactive liquid composition.
"""

from __future__ import annotations

import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import qmc, rankdata


ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "analyses" / "enrtl_six_species_ideal_comparison"
RESULTS = ANALYSIS / "results"
PACKET = Path(
    os.environ.get(
        "EPCSAFT_PARAMETER_PACKET",
        "/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/analyses/2026-mea-parameter-estimation/inputs/candidate-3-parameters.json",
    )
)
REACTION_INPUT = Path(
    os.environ.get(
        "EPCSAFT_REACTION_INPUT",
        "/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/analyses/2026-mea-parameter-estimation/inputs/candidate-3-mixed-n8-input.json",
    )
)

PRESSURE_PA = 100_000.0
SEED = 20260901
SAMPLE_COUNT = int(os.environ.get("MEA_UQ_SAMPLE_COUNT", "256"))
GRID_COUNT = int(os.environ.get("MEA_UQ_GRID_COUNT", "16"))
LOCAL_GRID_TOP = int(os.environ.get("MEA_UQ_GRID_TOP", "12"))
SMOKE = os.environ.get("MEA_UQ_SMOKE", "").lower() in {"1", "true", "yes"}
WORKERS = max(1, int(os.environ.get("MEA_UQ_WORKERS", "4")))
SHORT_NAMES = {
    "carbon-dioxide": "co2",
    "monoethanolamine": "mea",
    "water": "h2o",
    "protonated-monoethanolamine": "meah",
    "carbamate-anion": "meacoo",
    "bicarbonate-anion": "hco3",
    "carbonate-anion": "co3",
    "hydronium-cation": "h3o",
    "hydroxide-anion": "oh",
}
SPECIES = tuple(SHORT_NAMES)
ANALYSIS_OUTPUTS = (
    "log10_fugacity_co2_kpa",
    "density_mol_m3",
    "log10_amount_meah",
    "log10_amount_meacoo",
    "log10_amount_co3",
)
NEWTON_MAX_ITERATIONS = int(os.environ.get("MEA_UQ_NEWTON_MAX_ITERATIONS", "64"))
CONTINUATION_STEPS = int(os.environ.get("MEA_UQ_CONTINUATION_STEPS", "4"))
EQUILIBRIUM_TOLERANCE = 1.0e-6


@dataclass(frozen=True)
class Group:
    key: str
    family: str
    identities: tuple[str, ...]
    value: float
    unit: str
    lower: float | None
    upper: float | None
    status: str
    reason: str


@dataclass(frozen=True)
class StateSpec:
    temperature_k: float
    loading: float
    feed: tuple[float, ...]
    source_state: str


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_engine():
    import epcsaft  # type: ignore[import-not-found]

    return epcsaft


def numeric(value: Any, unit: str | None = None) -> float:
    if hasattr(value, "to") and unit is not None:
        return float(value.to(unit).magnitude)
    return float(value)


def charge_map(raw: dict[str, Any]) -> dict[str, int]:
    return {
        component["component_id"]: int(component["fixed"]["charge_number"]["value"]["magnitude"])
        for component in raw["components"]
    }


def source_declaration(epcsaft: Any, standard: dict[str, Any]) -> Any:
    pairs = tuple(
        epcsaft.SourceReferenceIonPair(tuple(pair[0]), tuple(pair[1]))
        for pair in standard["ion_pairs"]
    )
    return epcsaft.SourceReferenceDeclaration(
        reference_state_id=standard["id"],
        component_ids=tuple(standard["component_ids"]),
        solvent_mole_fractions=tuple(standard["solvent_composition"]),
        ion_pairs=pairs,
        phase=standard["phase"],
        reference_convention=standard["reference_convention"],
        activity_convention_id=standard["activity_convention_id"],
        standard_molality_mol_per_kg=standard["standard_molality_mol_per_kg"],
        reference_pressure_pa=standard["reference_pressure_pa"],
        required_derivatives=(),
        pure_components=(),
    )


def canonical_association(identity: str) -> str:
    parts = identity.split("/")
    if len(parts) != 6 or parts[0] != "association":
        return identity
    left = tuple(parts[1:3])
    right = tuple(parts[3:5])
    return "/".join(("association", *min(left, right), *max(left, right), parts[5]))


def prior(family: str, value: float) -> tuple[float | None, float | None, str]:
    if family == "k_ij":
        half = max(0.01, 0.25 * abs(value))
        return max(-0.95, value - half), min(0.95, value + half), "screening_additive_kij"
    if family == "k_ij_reciprocal_temperature_slope":
        return -1000.0, 1000.0, "candidate_optimizer_domain"
    if family == "reaction_correlation":
        half = max(0.20 * abs(value), 0.20)
        return value - half, value + half, "screening_relative_reaction"
    factors = {
        "segment_count": 0.05,
        "segment_diameter": 0.08,
        "dispersion_energy_over_k": 0.12,
        "association_energy_over_k": 0.12,
        "association_volume": 0.12,
        "born_diameter": 0.10,
        "debye_huckel_diameter": 0.10,
        "packing_diameter": 0.10,
        "ion_specific_suppression_coefficient": 0.20,
        "relative_permittivity": 0.10,
        "ionic_region_relative_permittivity": 0.12,
        "solvation_factor": 0.12,
        "temperature_polynomial_coefficient_1": 0.12,
        "temperature_polynomial_coefficient_2": 0.12,
        "exponential_temperature_coefficient": 0.12,
    }
    half = factors.get(family, 0.10)
    if value == 0.0:
        return -half, half, "screening_symmetric_zero"
    return max(1.0e-12, value * (1.0 - half)), value * (1.0 + half), "screening_relative"


def build_groups(epcsaft: Any, parameters: Any, raw: dict[str, Any]) -> tuple[list[Group], dict[str, dict[str, Any]]]:
    charges = charge_map(raw)
    specs = parameters.parameter_specs
    by_group: dict[str, list[Any]] = {}
    for spec in specs:
        key = canonical_association(spec.identity)
        by_group.setdefault(key, []).append(spec)
    groups: list[Group] = []
    inventory: dict[str, dict[str, Any]] = {}
    for spec in specs:
        value = numeric(spec.value, spec.unit)
        key = canonical_association(spec.identity)
        members = by_group.get(key, [])
        if not spec.continuous:
            status, reason, lower, upper, prior_kind = (
                "excluded_derived",
                "non-continuous combining-rule cross association record",
                None,
                None,
                "not_admissible",
            )
        elif spec.family == "k_ij":
            parts = spec.identity.split("/")
            charge_a = charges.get(parts[1], 0)
            charge_b = charges.get(parts[2], 0)
            if charge_a and charge_b and charge_a * charge_b > 0:
                status, reason, lower, upper, prior_kind = (
                    "excluded_structural",
                    "current ionic-dispersion model excludes same-sign ion pairs",
                    0.0,
                    0.0,
                    "structural_zero_by_model",
                )
            else:
                lower, upper, prior_kind = prior(spec.family, value)
                status, reason = "included_lhc", "continuous packet coordinate; fixed disposition does not remove it from screening"
        else:
            lower, upper, prior_kind = prior(spec.family, value)
            if spec.family == "reaction_correlation":
                floor = {"dimensionless": 0.20, "kelvin": 250.0, "1 / kelvin": 1.0e-4}.get(spec.unit, 0.20)
                half = max(0.20 * abs(value), floor)
                lower, upper, prior_kind = value - half, value + half, "screening_relative_reaction"
            status, reason = "included_lhc", "continuous packet coordinate; fixed disposition does not remove it from screening"
        inventory[spec.identity] = {
            "identity": spec.identity,
            "family": spec.family,
            "value": value,
            "unit": spec.unit,
            "continuous": bool(spec.continuous),
            "tie_group": key,
            "status": status,
            "reason": reason,
            "lower": lower,
            "upper": upper,
            "prior_kind": prior_kind,
            "source_id": spec.source_id,
            "domain_id": spec.domain_id,
            "qualification": spec.qualification,
        }
        if status == "included_lhc" and not any(group.key == key for group in groups):
            groups.append(
                Group(key, spec.family, tuple(member.identity for member in members), value, spec.unit, lower, upper, status, reason)
            )
    for component in raw["components"]:
        identity = component["component_id"]
        for fixed_name in ("charge_number", "molar_mass"):
            record = component["fixed"][fixed_name]
            fixed_identity = f"component/{identity}/{fixed_name}"
            inventory[fixed_identity] = {
                "identity": fixed_identity,
                "family": fixed_name,
                "value": float(record["value"]["magnitude"]),
                "unit": record["value"]["unit"],
                "continuous": False,
                "tie_group": fixed_identity,
                "status": "excluded_identity",
                "reason": "chemical identity invariant, not a thermodynamic UQ coordinate",
                "lower": None,
                "upper": None,
                "prior_kind": "not_admissible",
                "source_id": record["provenance"]["source_id"],
                "domain_id": record["provenance"]["domain_id"],
                "qualification": record["qualification"],
            }
    inventory["model/topology/ionic_dispersion"] = {
        "identity": "model/topology/ionic_dispersion",
        "family": "discrete_model_choice",
        "value": "exclude-same-sign-ion-pairs",
        "unit": "categorical",
        "continuous": False,
        "tie_group": "model/topology/ionic_dispersion",
        "status": "excluded_identity",
        "reason": "discrete model-family choice; requires scenario analysis rather than continuous LHC",
        "lower": None,
        "upper": None,
        "prior_kind": "scenario_only",
        "source_id": "installed-provider-bundle",
        "domain_id": "mea-candidate-293-15-to-393-15-k",
        "qualification": "diagnostic",
    }
    return groups, inventory


def load_states(raw_input: dict[str, Any], ideal_path: Path) -> tuple[list[StateSpec], dict[float, dict[str, float]]]:
    with ideal_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    candidates: dict[tuple[float, float], dict[str, float]] = {}
    for row in rows:
        if row["model"] != "ideal_9_species" or row["state_family"] != "speciation":
            continue
        key = (float(row["temperature_C"]), float(row["CO2_loading"]))
        candidates.setdefault(key, {})[row["species"]] = float(row["amount_per_mol_initial_MEA"])
    temperatures = sorted({float(item["request"]["temperature"]["value"]) for item in raw_input["observations"]})
    targets = (0.10, 0.30, 0.50, 0.70)
    states: list[StateSpec] = []
    for temperature_k in temperatures:
        temperature_c = temperature_k - 273.15
        for target in targets:
            available = [key for key in candidates if abs(key[0] - temperature_c) < 1.0e-8]
            if not available:
                continue
            key = min(available, key=lambda item: abs(item[1] - target))
            values = candidates[key]
            if set(values) != {"CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-"}:
                continue
            feed = tuple(values[short] for short in ("CO2", "MEA", "H2O", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-"))
            states.append(StateSpec(temperature_k, key[1], feed, f"ideal_speciation_{temperature_c:g}C_{key[1]:g}"))
    if not states:
        raise RuntimeError(f"No ideal state templates found in {ideal_path}")
    source_by_temperature = {}
    for item in raw_input["observations"]:
        temperature_k = float(item["request"]["temperature"]["value"])
        source_by_temperature.setdefault(temperature_k, item["request"]["reaction_system"])
    return states, source_by_temperature


def build_lnks(epcsaft: Any, model: Any, system: dict[str, Any], temperature_k: float, values: dict[str, float]) -> np.ndarray:
    standard = system["source_standard_state"]
    declaration = source_declaration(epcsaft, standard)
    transfer = epcsaft.source_reference_transfer(
        model,
        declaration,
        T=temperature_k * epcsaft.unit_registry.kelvin,
        P=PRESSURE_PA * epcsaft.unit_registry.pascal,
    )
    basis = np.asarray(transfer.neutral_basis, dtype=float)
    contractions = np.asarray(transfer.transfer_log_contractions, dtype=float)
    result = []
    for reaction, raw_constant in zip(system["reaction_matrix"], system["equilibrium_constants"], strict=True):
        stoich = np.asarray(reaction, dtype=float)
        coordinates = np.linalg.lstsq(basis.T, stoich, rcond=None)[0]
        if np.max(np.abs(coordinates @ basis - stoich)) > 1.0e-8:
            raise RuntimeError("reaction is outside the Engine neutral-reference span")
        source_ln_k = float(raw_constant[0])
        if len(raw_constant) == 7 and raw_constant[6]["reaction_id"] == "R4":
            source_ln_k = values["reaction:R4:correlation:a"] + values["reaction:R4:correlation:b_k"] / temperature_k
        if len(raw_constant) == 7 and raw_constant[6]["reaction_id"] == "R5":
            source_ln_k = -math.log(10.0) * (
                values["reaction:R5:correlation:a_k"] / temperature_k
                + values["reaction:R5:correlation:b"]
                + values["reaction:R5:correlation:c_per_k"] * temperature_k
            )
        offset = float(
            coordinates @ contractions
            + stoich.sum() * math.log(PRESSURE_PA / (8.31446261815324 * temperature_k))
        )
        result.append(source_ln_k + offset)
    return np.asarray(result, dtype=float)


def solve_state(epcsaft: Any, model: Any, system: dict[str, Any], state: StateSpec, values: dict[str, float], initial_extents: np.ndarray | None = None) -> dict[str, Any]:
    reaction_matrix = np.asarray(system["reaction_matrix"], dtype=float)
    feed = np.asarray(state.feed, dtype=float)
    extents = np.zeros(reaction_matrix.shape[0]) if initial_extents is None else np.asarray(initial_extents, dtype=float).copy()
    lnks = build_lnks(epcsaft, model, system, state.temperature_k, values)
    coordinate_ids = None
    started = None
    for iteration in range(NEWTON_MAX_ITERATIONS):
        amounts = feed + reaction_matrix.T @ extents
        if np.any(amounts <= 1.0e-15):
            return {"status": "failed", "failure": "negative_amount_during_newton", "iterations": iteration}
        total = float(amounts.sum())
        x = amounts / total
        try:
            eos_state = model.state(
                T=state.temperature_k * epcsaft.unit_registry.kelvin,
                P=PRESSURE_PA * epcsaft.unit_registry.pascal,
                x=tuple(x),
                phase="liquid",
            )
        except Exception as exc:
            return {"status": "failed", "failure": f"eos_state:{type(exc).__name__}:{exc}", "iterations": iteration}
        log_fugacity = np.log(x) + math.log(PRESSURE_PA / (8.31446261815324 * state.temperature_k)) + np.asarray(eos_state.fugacity.ln_coefficient, dtype=float)
        residual = reaction_matrix @ log_fugacity - lnks
        norm = float(np.max(np.abs(residual)))
        if started is None:
            started = norm
        if norm < EQUILIBRIUM_TOLERANCE:
            coordinate_ids = tuple(eos_state.fixed_pressure_composition_derivatives["coordinate_component_ids"])
            break
        derivatives = eos_state.fixed_pressure_composition_derivatives
        if derivatives["status"] != "available":
            return {"status": "failed", "failure": "composition_derivatives_unavailable", "iterations": iteration, "max_affinity_residual": norm}
        coordinate_ids = tuple(derivatives["coordinate_component_ids"])
        coordinate_index = [SPECIES.index(identity) for identity in coordinate_ids]
        chemical_derivatives = np.asarray(derivatives["chemical_potential_derivatives_over_rt"], dtype=float)
        da = reaction_matrix.T
        dx = (da * total - amounts[:, None] * da.sum(axis=0)) / total**2
        dq = dx[coordinate_index, :] / x[coordinate_index, None]
        jacobian = reaction_matrix @ chemical_derivatives @ dq
        try:
            step = np.linalg.solve(jacobian, -residual)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(jacobian, -residual, rcond=None)[0]
        base = norm
        accepted = False
        alpha = 1.0
        while alpha >= 1.0e-5:
            trial = extents + alpha * step
            trial_amounts = feed + reaction_matrix.T @ trial
            if np.any(trial_amounts <= 1.0e-15):
                alpha *= 0.5
                continue
            trial_x = trial_amounts / trial_amounts.sum()
            try:
                trial_state = model.state(
                    T=state.temperature_k * epcsaft.unit_registry.kelvin,
                    P=PRESSURE_PA * epcsaft.unit_registry.pascal,
                    x=tuple(trial_x),
                    phase="liquid",
                )
                trial_residual = reaction_matrix @ (
                    np.log(trial_x)
                    + math.log(PRESSURE_PA / (8.31446261815324 * state.temperature_k))
                    + np.asarray(trial_state.fugacity.ln_coefficient, dtype=float)
                ) - lnks
            except Exception:
                alpha *= 0.5
                continue
            if float(np.max(np.abs(trial_residual))) < base:
                extents = trial
                accepted = True
                break
            alpha *= 0.5
        if not accepted:
            return {"status": "failed", "failure": "newton_line_search_failed", "iterations": iteration, "max_affinity_residual": norm}
    else:
        return {"status": "failed", "failure": "newton_max_iterations", "iterations": NEWTON_MAX_ITERATIONS, "max_affinity_residual": norm}
    amounts = feed + reaction_matrix.T @ extents
    if coordinate_ids is None or norm >= EQUILIBRIUM_TOLERANCE:
        return {"status": "failed", "failure": "equilibrium_gate_failed", "iterations": iteration + 1, "max_affinity_residual": norm}
    state_result: dict[str, Any] = {
        "status": "success",
        "failure": "",
        "iterations": iteration + 1,
        "max_affinity_residual": norm,
        "initial_affinity_residual": started,
        "temperature_k": state.temperature_k,
        "loading": state.loading,
        "source_state": state.source_state,
        "density_mol_m3": float(eos_state.molar_density.to("mole / meter**3").magnitude),
        "fugacity_co2_kpa": float(math.exp(log_fugacity[0]) / 1000.0),
        "_extents": extents.tolist(),
    }
    for identity, amount in zip(SPECIES, amounts, strict=True):
        state_result[f"amount_{SHORT_NAMES[identity]}"] = float(amount)
        state_result[f"log10_amount_{SHORT_NAMES[identity]}"] = math.log10(max(float(amount), 1.0e-300))
    state_result["log10_fugacity_co2_kpa"] = math.log10(max(state_result["fugacity_co2_kpa"], 1.0e-300))
    return state_result


def values_for(groups: list[Group], vector: np.ndarray | None = None) -> dict[str, float]:
    result = {}
    for index, group in enumerate(groups):
        value = group.value if vector is None else float(group.lower + vector[index] * (group.upper - group.lower))
        for identity in group.identities:
            result[identity] = value
    return result


def replace_values(parameters: Any, values: dict[str, float], epcsaft: Any) -> Any:
    """Replace values without adding schema-invalid synthetic provenance records."""
    mapping = parameters.to_mapping()
    expected = set(values)
    found: set[str] = set()

    def replace(item: object) -> None:
        if isinstance(item, list):
            for child in item:
                replace(child)
        elif isinstance(item, dict):
            identity = item.get("identity")
            if identity in values:
                quantity = item.get("value")
                if not isinstance(quantity, dict) or "magnitude" not in quantity:
                    raise ValueError(f"parameter record has no magnitude: {identity}")
                quantity["magnitude"] = float(values[identity])
                found.add(str(identity))
            for child in tuple(item.values()):
                replace(child)

    replace(mapping)
    if found != expected:
        missing = ", ".join(sorted(expected - found))
        raise ValueError(f"parameter identities not found in packet: {missing}")
    return epcsaft.Parameters.from_mapping(mapping, components=parameters.component_ids)


def evaluate_model(epcsaft: Any, parameters: Any, system_by_temperature: dict[float, dict[str, Any]], states: list[StateSpec], values: dict[str, float], selected: list[StateSpec], initial_extents_by_state: dict[str, list[float]] | None = None, reference_values: dict[str, float] | None = None) -> list[dict[str, Any]]:
    try:
        model = replace_values(parameters, values, epcsaft)
        model = epcsaft.Mixture(model)
    except Exception as exc:
        return [
            {
                "status": "failed",
                "failure": f"model:{type(exc).__name__}:{exc}",
                "temperature_k": state.temperature_k,
                "loading": state.loading,
                "source_state": state.source_state,
            }
            for state in selected
        ]
    rows = []
    for state in selected:
        system = system_by_temperature[state.temperature_k]
        try:
            initial = None if initial_extents_by_state is None else initial_extents_by_state.get(state.source_state)
            stage_values = [values]
            if initial is not None and reference_values is not None and any(values[key] != reference_values[key] for key in values):
                continuation_values = []
                for alpha in np.linspace(1.0 / CONTINUATION_STEPS, 1.0, CONTINUATION_STEPS):
                    continuation_values.append({key: reference_values[key] + alpha * (values[key] - reference_values[key]) for key in values})
                stage_values.extend(continuation_values)
            result = None
            stage_initial = None if initial is None else np.asarray(initial)
            for stage_index, stage in enumerate(stage_values):
                result = solve_state(epcsaft, model, system, state, stage, stage_initial)
                if result.get("status") != "success":
                    if stage_index == 0 and len(stage_values) > 1:
                        stage_initial = None if initial is None else np.asarray(initial)
                        continue
                    break
                stage_initial = np.asarray(result["_extents"])
            assert result is not None
            rows.append(result)
        except Exception as exc:
            rows.append(
                {
                    "status": "failed",
                    "failure": f"state:{type(exc).__name__}:{exc}",
                    "temperature_k": state.temperature_k,
                    "loading": state.loading,
                    "source_state": state.source_state,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def inventory_rows(inventory: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [inventory[key] for key in sorted(inventory)]


def output_value(row: dict[str, Any], name: str) -> float:
    return float(row[name])


def rank_statistics(sample_rows: list[dict[str, Any]], groups: list[Group], output: str) -> list[dict[str, Any]]:
    valid = [row for row in sample_rows if row.get("status") == "success" and math.isfinite(float(row.get(output, "nan")))]
    if len(valid) < max(32, len(groups) // 2):
        return []
    x = np.asarray([[float(row[f"parameter__{group.key}"]) for group in groups] for row in valid])
    y = np.asarray([output_value(row, output) for row in valid])
    xr = np.asarray([rankdata(x[:, j]) for j in range(x.shape[1])], dtype=float).T
    yr = rankdata(y).astype(float)
    xz = (xr - xr.mean(axis=0)) / np.where(xr.std(axis=0) > 0, xr.std(axis=0), 1.0)
    yz = (yr - yr.mean()) / max(float(yr.std()), 1.0)
    beta = np.linalg.lstsq(np.column_stack([np.ones(len(yz)), xz]), yz, rcond=None)[0][1:]
    corr = np.corrcoef(np.column_stack([xz, yz]), rowvar=False)
    precision = np.linalg.pinv(corr + 1.0e-8 * np.eye(corr.shape[0]), rcond=1.0e-10)
    prcc = np.asarray([
        -precision[j, -1] / math.sqrt(max(precision[j, j] * precision[-1, -1], 1.0e-30))
        for j in range(len(groups))
    ])
    spearman = np.asarray([np.corrcoef(xr[:, j], yr)[0, 1] for j in range(len(groups))])
    rng = np.random.default_rng(SEED + len(output))
    boot = np.empty((200, len(groups)))
    for index in range(200):
        selected = rng.integers(0, len(y), len(y))
        boot[index] = [np.corrcoef(xr[selected, j], yr[selected])[0, 1] for j in range(len(groups))]
    rows = []
    for j, group in enumerate(groups):
        rows.append({
            "output": output,
            "parameter_group": group.key,
            "parameter_identities": "|".join(group.identities),
            "family": group.family,
            "spearman_rho": float(spearman[j]),
            "spearman_ci_low": float(np.nanpercentile(boot[:, j], 2.5)),
            "spearman_ci_high": float(np.nanpercentile(boot[:, j], 97.5)),
            "rank_src_beta": float(beta[j]),
            "prcc_ridge": float(prcc[j]),
            "absolute_importance": float(abs(prcc[j])),
            "valid_sample_count": len(valid),
            "sample_count": len(sample_rows),
        })
    return rows


def context(epcsaft: Any) -> tuple[Any, Any, list[Group], dict[str, dict[str, Any]], list[StateSpec], dict[float, dict[str, Any]], StateSpec, dict[str, float], dict[str, list[float]]]:
    raw_packet = json.loads(PACKET.read_text(encoding="utf-8"))
    raw_input = json.loads(REACTION_INPUT.read_text(encoding="utf-8"))
    parameters = epcsaft.Parameters.from_json(PACKET)
    groups, inventory = build_groups(epcsaft, parameters, raw_packet)
    states, systems = load_states(raw_input, RESULTS / "state_species_results.csv")
    central = min(states, key=lambda item: abs(item.temperature_k - 313.15) + 100.0 * abs(item.loading - 0.3))
    center_values = values_for(groups)
    if os.environ.get("MEA_UQ_WRITE_INVENTORY", "1") != "0":
        write_csv(RESULTS / "uq_parameter_inventory.csv", inventory_rows(inventory))
    central_result = evaluate_model(epcsaft, parameters, systems, states, center_values, [central])[0]
    if central_result.get("status") != "success":
        raise RuntimeError(f"Central baseline state failed: {central_result.get('failure', 'unknown failure')}")
    return parameters, raw_input, groups, inventory, states, systems, central, center_values, {central.source_state: central_result["_extents"]}


def lhc_row(epcsaft: Any, parameters: Any, groups: list[Group], systems: dict[float, dict[str, Any]], states: list[StateSpec], central: StateSpec, center_values: dict[str, float], baseline_extents: dict[str, list[float]], sample_id: int, vector: np.ndarray) -> dict[str, Any]:
    values = values_for(groups, vector)
    state_result = evaluate_model(epcsaft, parameters, systems, states, values, [central], baseline_extents, center_values)[0]
    row: dict[str, Any] = {"sample_id": sample_id, "status": state_result.get("status", "failed"), "failure": state_result.get("failure", "")}
    for group in groups:
        row[f"parameter__{group.key}"] = float(values[group.identities[0]])
    row.update({key: value for key, value in state_result.items() if key not in {"status", "failure"} and not key.startswith("_")})
    return row


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def part_rows(pattern: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(RESULTS.glob(pattern)):
        rows.extend(read_csv_rows(path))
    return rows


def run_lhc_batch(epcsaft: Any, start: int, stop: int) -> int:
    parameters, _, groups, _, states, systems, central, center_values, baseline_extents = context(epcsaft)
    design = qmc.LatinHypercube(len(groups), scramble=True, optimization="random-cd", seed=SEED)
    unit_design = design.random(SAMPLE_COUNT)
    stop = min(stop, SAMPLE_COUNT)
    if start < 0 or start >= stop:
        raise ValueError(f"invalid LHC batch [{start}, {stop})")
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(lhc_row, epcsaft, parameters, groups, systems, states, central, center_values, baseline_extents, sample_id, unit_design[sample_id]) for sample_id in range(start, stop)]
        rows = [future.result() for future in futures]
    path = RESULTS / f"uq_lhc_part_{start:04d}_{stop:04d}.csv"
    write_csv(path, rows)
    print(json.dumps({"phase": "lhc", "path": str(path), "sample_start": start, "sample_stop": stop, "rows": len(rows), "valid": sum(row.get("status") == "success" for row in rows)}, indent=2))
    return 0


def aggregate_lhc(epcsaft: Any) -> int:
    parameters, _, groups, _, _, _, _, _, _ = context(epcsaft)
    rows = sorted(part_rows("uq_lhc_part_*.csv"), key=lambda row: int(row["sample_id"]))
    if len(rows) != SAMPLE_COUNT or {int(row["sample_id"]) for row in rows} != set(range(SAMPLE_COUNT)):
        raise RuntimeError(f"LHC parts are incomplete: found {len(rows)} rows for {SAMPLE_COUNT} requested samples")
    write_csv(RESULTS / "uq_lhc_samples.csv", rows)
    sensitivity_rows = [row for output in ANALYSIS_OUTPUTS for row in rank_statistics(rows, groups, output)]
    write_csv(RESULTS / "uq_global_sensitivity.csv", sensitivity_rows)
    print(json.dumps({"phase": "aggregate-lhc", "rows": len(rows), "valid": sum(row.get("status") == "success" for row in rows), "sensitivity_rows": len(sensitivity_rows)}, indent=2))
    return 0


def run_local_batch(epcsaft: Any, start: int, stop: int) -> int:
    parameters, _, groups, _, states, systems, central, center_values, baseline_extents = context(epcsaft)
    baseline = evaluate_model(epcsaft, parameters, systems, states, center_values, [central], baseline_extents)[0]
    local_groups = groups[start:min(stop, len(groups))]
    def endpoint_row(group: Group) -> dict[str, Any]:
        low_values = dict(center_values)
        high_values = dict(center_values)
        for identity in group.identities:
            low_values[identity] = group.lower
            high_values[identity] = group.upper
        low = evaluate_model(epcsaft, parameters, systems, states, low_values, [central], baseline_extents, center_values)[0]
        high = evaluate_model(epcsaft, parameters, systems, states, high_values, [central], baseline_extents, center_values)[0]
        row = {"parameter_group": group.key, "parameter_identities": "|".join(group.identities), "family": group.family, "center_value": group.value, "lower_value": group.lower, "upper_value": group.upper, "lower_status": low.get("status"), "upper_status": high.get("status")}
        for output in ANALYSIS_OUTPUTS:
            center_value = float(baseline[output])
            low_value = float(low[output]) if low.get("status") == "success" else math.nan
            high_value = float(high[output]) if high.get("status") == "success" else math.nan
            row[f"{output}_lower"] = low_value
            row[f"{output}_upper"] = high_value
            row[f"{output}_relative_span"] = abs(high_value - low_value) / max(abs(center_value), 1.0e-30) if math.isfinite(low_value) and math.isfinite(high_value) else math.nan
        return row
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        rows = [future.result() for future in [pool.submit(endpoint_row, group) for group in local_groups]]
    path = RESULTS / f"uq_local_part_{start:04d}_{min(stop, len(groups)):04d}.csv"
    write_csv(path, rows)
    print(json.dumps({"phase": "local", "path": str(path), "rows": len(rows)}, indent=2))
    return 0


def baseline_grid(epcsaft: Any, parameters: Any, systems: dict[float, dict[str, Any]], states: list[StateSpec], center_values: dict[str, float], baseline_extents: dict[str, list[float]]) -> tuple[list[dict[str, Any]], dict[str, list[float]]]:
    rows = evaluate_model(epcsaft, parameters, systems, states, center_values, states, baseline_extents)
    baseline_extents.update({row["source_state"]: row["_extents"] for row in rows if row.get("status") == "success" and "_extents" in row})
    return [{key: value for key, value in row.items() if not key.startswith("_")} for row in rows], baseline_extents


def finalize_uq(epcsaft: Any) -> int:
    parameters, _, groups, _, states, systems, central, center_values, baseline_extents = context(epcsaft)
    sample_rows = sorted(part_rows("uq_lhc_part_*.csv"), key=lambda row: int(row["sample_id"]))
    if len(sample_rows) != SAMPLE_COUNT:
        raise RuntimeError(f"Cannot finalize incomplete LHC: found {len(sample_rows)} rows for {SAMPLE_COUNT}")
    write_csv(RESULTS / "uq_lhc_samples.csv", sample_rows)
    sensitivity_rows = [row for output in ANALYSIS_OUTPUTS for row in rank_statistics(sample_rows, groups, output)]
    write_csv(RESULTS / "uq_global_sensitivity.csv", sensitivity_rows)
    skip_endpoints = os.environ.get("MEA_UQ_SKIP_ENDPOINTS", "").lower() in {"1", "true", "yes"}
    if skip_endpoints:
        central_result = evaluate_model(epcsaft, parameters, systems, states, center_values, [central], baseline_extents)[0]
        grid_result = [{key: value for key, value in central_result.items() if not key.startswith("_")}]
    else:
        grid_result, baseline_extents = baseline_grid(epcsaft, parameters, systems, states, center_values, baseline_extents)
    write_csv(RESULTS / "uq_state_grid_baseline.csv", grid_result)
    center_state = next(row for row in grid_result if abs(float(row.get("temperature_k", 0)) - central.temperature_k) < 1.0e-8 and abs(float(row.get("loading", 0)) - central.loading) < 1.0e-8)
    local_rows = sorted(part_rows("uq_local_part_*.csv"), key=lambda row: row["parameter_group"])
    if skip_endpoints:
        local_rows = []
    elif len(local_rows) != len(groups):
        raise RuntimeError(f"Cannot finalize incomplete local screen: found {len(local_rows)} rows for {len(groups)} groups")
    write_csv(RESULTS / "uq_local_sensitivity.csv", local_rows)
    ranked = sorted([row for row in sensitivity_rows if row["output"] == "log10_fugacity_co2_kpa"], key=lambda row: float(row["absolute_importance"]), reverse=True)
    top_keys = {row["parameter_group"] for row in ranked[:LOCAL_GRID_TOP]}
    grid_rows = sorted(part_rows("uq_grid_part_*.csv"), key=lambda row: (row["parameter_group"], float(row["temperature_k"]), float(row["loading"])) )
    if skip_endpoints:
        grid_rows = []
    elif top_keys and len(grid_rows) != len(top_keys) * len(states):
        raise RuntimeError(f"Cannot finalize incomplete grid screen: found {len(grid_rows)} rows for {len(top_keys) * len(states)}")
    write_csv(RESULTS / "uq_grid_top_parameter_sensitivity.csv", grid_rows)
    write_csv(
        RESULTS / "uq_endpoint_status.csv",
        [{
            "endpoint_confirmation": "not_run" if skip_endpoints else "complete",
            "local_groups_requested": len(groups),
            "local_groups_retained": len(local_rows),
            "grid_top_groups_requested": len(top_keys) if not skip_endpoints else 0,
            "grid_rows_retained": len(grid_rows),
            "reason": "primary global LHC/UQ finalized; endpoint and top-parameter grid phases were not run in this execution" if skip_endpoints else "complete",
        }],
    )
    valid_samples = [row for row in sample_rows if row.get("status") == "success"]
    uq_rows = []
    for output in ANALYSIS_OUTPUTS:
        values = np.asarray([float(row[output]) for row in valid_samples])
        center_value = float(center_state[output])
        uq_rows.append({"output": output, "baseline": center_value, "q_0_025": float(np.percentile(values, 2.5)) if len(values) else math.nan, "q_0_500": float(np.percentile(values, 50.0)) if len(values) else math.nan, "q_0_975": float(np.percentile(values, 97.5)) if len(values) else math.nan, "mean": float(values.mean()) if len(values) else math.nan, "std": float(values.std(ddof=1)) if len(values) > 1 else math.nan, "valid_count": len(values), "attempted_count": len(sample_rows), "failure_fraction": 1.0 - len(values) / len(sample_rows)})
    write_csv(RESULTS / "uq_uncertainty_summary.csv", uq_rows)
    design = qmc.LatinHypercube(len(groups), scramble=True, optimization="random-cd", seed=SEED).random(SAMPLE_COUNT)
    design_corr = np.corrcoef(design, rowvar=False)
    receipt = {"study_id": "mea-nine-species-all-parameter-smart-lhc-v1", "packet_path": str(PACKET), "packet_sha256": f"sha256:{sha256(PACKET)}", "reaction_input_path": str(REACTION_INPUT), "reaction_input_sha256": f"sha256:{sha256(REACTION_INPUT)}", "engine_wheel_path": os.environ.get("EPCSAFT_ENGINE_WHEEL", "explicit wheel supplied by caller"), "engine_wheel_sha256": f"sha256:{sha256(Path(os.environ['EPCSAFT_ENGINE_WHEEL']))}" if os.environ.get("EPCSAFT_ENGINE_WHEEL") and Path(os.environ["EPCSAFT_ENGINE_WHEEL"]).is_file() else "unresolved", "sample_count": SAMPLE_COUNT, "valid_sample_count": len(valid_samples), "parameter_group_count": len(groups), "parameter_identity_count": len(read_csv_rows(RESULTS / "uq_parameter_inventory.csv")), "lhc_seed": SEED, "lhc_max_abs_dimension_correlation": float(np.max(np.abs(design_corr - np.eye(design_corr.shape[0])))), "central_state": {"temperature_k": central.temperature_k, "loading": central.loading, "source_state": central.source_state}, "grid_state_count": len(states) if not skip_endpoints else 1, "grid_top_parameter_count": len(top_keys) if not skip_endpoints else 0, "endpoint_confirmation": "not_run" if skip_endpoints else "complete", "workers": WORKERS, "continuation_fallback_steps": CONTINUATION_STEPS, "equilibrium_solver": "temporary SciPy Newton reaction-extents bridge with Engine EOS fixed-pressure composition derivatives", "uq_status": "screening-prior-input-uncertainty; not measurement-backed posterior covariance"}
    (RESULTS / "uq_run_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    manifest_items = [("uq_parameter_inventory.csv", "all packet coordinates, fixed/derived exclusions, and screening priors"), ("uq_lhc_samples.csv", "scrambled maximin Latin-hypercube central-state samples"), ("uq_global_sensitivity.csv", "Spearman, rank-SRC, ridge-PRCC, and bootstrap rank intervals"), ("uq_uncertainty_summary.csv", "screening-prior output quantiles and failure fraction"), ("uq_endpoint_status.csv", "completion status for optional endpoint and state-grid confirmation phases"), ("uq_run_receipt.json", "engine, packet, seed, sample, and claim-boundary receipt")]
    if not skip_endpoints:
        manifest_items.extend([("uq_local_sensitivity.csv", "all included parameter lower/upper central-state responses"), ("uq_state_grid_baseline.csv", "central candidate baseline over temperature/loading grid"), ("uq_grid_top_parameter_sensitivity.csv", "top pCO2-ranked parameters over full state grid")])
    manifest = [{"artifact": name, "role": role} for name, role in manifest_items]
    write_csv(RESULTS / "uq_manifest.csv", manifest)
    print(json.dumps(receipt, indent=2))
    return 0


def run_grid_batch(epcsaft: Any, start: int, stop: int) -> int:
    parameters, _, groups, _, states, systems, central, center_values, baseline_extents = context(epcsaft)
    sensitivity_rows = read_csv_rows(RESULTS / "uq_global_sensitivity.csv")
    ranked = sorted([row for row in sensitivity_rows if row["output"] == "log10_fugacity_co2_kpa"], key=lambda row: float(row["absolute_importance"]), reverse=True)
    selected = [group for group in groups if group.key in {row["parameter_group"] for row in ranked[:LOCAL_GRID_TOP]}]
    selected = selected[start:min(stop, len(selected))]
    grid_states = states
    def grid_row(group: Group) -> list[dict[str, Any]]:
        low_values = dict(center_values)
        high_values = dict(center_values)
        for identity in group.identities:
            low_values[identity] = group.lower
            high_values[identity] = group.upper
        low_results = evaluate_model(epcsaft, parameters, systems, states, low_values, grid_states, baseline_extents, center_values)
        high_results = evaluate_model(epcsaft, parameters, systems, states, high_values, grid_states, baseline_extents, center_values)
        rows = []
        for state, low, high in zip(grid_states, low_results, high_results, strict=True):
            row = {"parameter_group": group.key, "parameter_identities": "|".join(group.identities), "temperature_k": state.temperature_k, "loading": state.loading, "lower_status": low.get("status"), "upper_status": high.get("status")}
            for output in ANALYSIS_OUTPUTS:
                lo = float(low[output]) if low.get("status") == "success" else math.nan
                hi = float(high[output]) if high.get("status") == "success" else math.nan
                row[f"{output}_lower"] = lo
                row[f"{output}_upper"] = hi
                row[f"{output}_span"] = abs(hi - lo) if math.isfinite(lo) and math.isfinite(hi) else math.nan
            rows.append(row)
        return rows
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        rows = [row for future in [pool.submit(grid_row, group) for group in selected] for row in future.result()]
    path = RESULTS / f"uq_grid_part_{start:04d}_{min(stop, len(selected) + start):04d}.csv"
    write_csv(path, rows)
    print(json.dumps({"phase": "grid", "path": str(path), "groups": len(selected), "rows": len(rows)}, indent=2))
    return 0


def run_phase(epcsaft: Any, phase: str) -> int:
    if phase == "lhc":
        return run_lhc_batch(epcsaft, int(os.environ.get("MEA_UQ_BATCH_START", "0")), int(os.environ.get("MEA_UQ_BATCH_STOP", "16")))
    if phase == "aggregate-lhc":
        return aggregate_lhc(epcsaft)
    if phase == "local":
        return run_local_batch(epcsaft, int(os.environ.get("MEA_UQ_BATCH_START", "0")), int(os.environ.get("MEA_UQ_BATCH_STOP", "16")))
    if phase == "grid":
        return run_grid_batch(epcsaft, int(os.environ.get("MEA_UQ_BATCH_START", "0")), int(os.environ.get("MEA_UQ_BATCH_STOP", "4")))
    if phase == "finalize":
        return finalize_uq(epcsaft)
    raise ValueError(f"unknown MEA_UQ_PHASE={phase}")


def main() -> int:
    if not PACKET.is_file() or not REACTION_INPUT.is_file():
        raise RuntimeError(f"Missing explicit Engine inputs: {PACKET} or {REACTION_INPUT}")
    epcsaft = load_engine()
    phase = os.environ.get("MEA_UQ_PHASE", "full")
    if phase != "full":
        return run_phase(epcsaft, phase)
    raw_packet = json.loads(PACKET.read_text(encoding="utf-8"))
    raw_input = json.loads(REACTION_INPUT.read_text(encoding="utf-8"))
    parameters = epcsaft.Parameters.from_json(PACKET)
    groups, inventory = build_groups(epcsaft, parameters, raw_packet)
    states, systems = load_states(raw_input, RESULTS / "state_species_results.csv")
    central = min(states, key=lambda item: abs(item.temperature_k - 313.15) + 100.0 * abs(item.loading - 0.3))
    system_by_temperature = systems
    center_values = values_for(groups)
    write_csv(RESULTS / "uq_parameter_inventory.csv", inventory_rows(inventory))

    central_result = evaluate_model(epcsaft, parameters, system_by_temperature, states, center_values, [central])[0]
    if central_result.get("status") != "success":
        raise RuntimeError(f"Central baseline state failed: {central_result.get('failure', 'unknown failure')}")
    baseline_extents = {central.source_state: central_result["_extents"]}

    design = qmc.LatinHypercube(len(groups), scramble=True, optimization="random-cd", seed=SEED)
    unit_design = design.random(SAMPLE_COUNT)
    def lhc_row(sample_id: int, vector: np.ndarray) -> dict[str, Any]:
        values = values_for(groups, vector)
        state_result = evaluate_model(epcsaft, parameters, system_by_temperature, states, values, [central], baseline_extents, center_values)[0]
        row: dict[str, Any] = {"sample_id": sample_id, "status": state_result.get("status", "failed"), "failure": state_result.get("failure", "")}
        for index, group in enumerate(groups):
            row[f"parameter__{group.key}"] = float(values[group.identities[0]])
        row.update({key: value for key, value in state_result.items() if key not in {"status", "failure"} and not key.startswith("_")})
        return row

    sample_rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(lhc_row, sample_id, vector) for sample_id, vector in enumerate(unit_design)]
        for completed, future in enumerate(as_completed(futures), start=1):
            sample_rows.append(future.result())
            if completed % 16 == 0 or completed == SAMPLE_COUNT:
                print(f"LHC {completed}/{SAMPLE_COUNT}", flush=True)
    sample_rows.sort(key=lambda row: row["sample_id"])
    write_csv(RESULTS / "uq_lhc_samples.csv", sample_rows)

    sensitivity_rows: list[dict[str, Any]] = []
    for output in ANALYSIS_OUTPUTS:
        sensitivity_rows.extend(rank_statistics(sample_rows, groups, output))
    write_csv(RESULTS / "uq_global_sensitivity.csv", sensitivity_rows)

    baseline_result = evaluate_model(epcsaft, parameters, system_by_temperature, states, center_values, states, baseline_extents)
    baseline_extents.update({row["source_state"]: row["_extents"] for row in baseline_result if row.get("status") == "success" and "_extents" in row})
    baseline_result = [{key: value for key, value in row.items() if not key.startswith("_")} for row in baseline_result]
    write_csv(RESULTS / "uq_state_grid_baseline.csv", baseline_result)

    center_state = next(row for row in baseline_result if abs(float(row.get("temperature_k", 0)) - central.temperature_k) < 1.0e-8 and abs(float(row.get("loading", 0)) - central.loading) < 1.0e-8)
    if center_state.get("status") != "success":
        raise RuntimeError(f"Central baseline state failed: {center_state.get('failure', 'unknown failure')}")
    local_rows: list[dict[str, Any]] = []
    local_groups = groups[:4] if SMOKE else groups
    def endpoint_row(group: Group) -> tuple[Group, dict[str, Any], dict[str, Any]]:
        if group.lower is None or group.upper is None:
            raise ValueError(f"missing endpoint for included group {group.key}")
        low_values = dict(center_values)
        high_values = dict(center_values)
        for identity in group.identities:
            low_values[identity] = group.lower
            high_values[identity] = group.upper
        low = evaluate_model(epcsaft, parameters, system_by_temperature, states, low_values, [central], baseline_extents, center_values)[0]
        high = evaluate_model(epcsaft, parameters, system_by_temperature, states, high_values, [central], baseline_extents, center_values)[0]
        return group, low, high

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        endpoint_futures = [pool.submit(endpoint_row, group) for group in local_groups]
        for index, future in enumerate(as_completed(endpoint_futures)):
            group, low, high = future.result()

            row = {"parameter_group": group.key, "parameter_identities": "|".join(group.identities), "family": group.family, "center_value": group.value, "lower_value": group.lower, "upper_value": group.upper, "lower_status": low.get("status"), "upper_status": high.get("status")}
            for output in ANALYSIS_OUTPUTS:
                center_value = float(center_state[output])
                low_value = float(low[output]) if low.get("status") == "success" else math.nan
                high_value = float(high[output]) if high.get("status") == "success" else math.nan
                row[f"{output}_lower"] = low_value
                row[f"{output}_upper"] = high_value
                row[f"{output}_relative_span"] = abs(high_value - low_value) / max(abs(center_value), 1.0e-30) if math.isfinite(low_value) and math.isfinite(high_value) else math.nan
            local_rows.append(row)
            if (index + 1) % 16 == 0 or index + 1 == len(local_groups):
                print(f"local endpoints {index + 1}/{len(local_groups)}", flush=True)
    write_csv(RESULTS / "uq_local_sensitivity.csv", local_rows)

    ranked = sorted(
        [row for row in sensitivity_rows if row["output"] == "log10_fugacity_co2_kpa"],
        key=lambda row: row["absolute_importance"],
        reverse=True,
    )
    top_keys = {row["parameter_group"] for row in ranked[:LOCAL_GRID_TOP]}
    grid_rows: list[dict[str, Any]] = []
    grid_states = [central] if SMOKE else states
    def grid_endpoints(group: Group) -> tuple[Group, list[dict[str, Any]], list[dict[str, Any]]]:
        if group.key not in top_keys:
            raise ValueError("not selected")
        low_values = dict(center_values)
        high_values = dict(center_values)
        for identity in group.identities:
            low_values[identity] = group.lower
            high_values[identity] = group.upper
        low_results = evaluate_model(epcsaft, parameters, system_by_temperature, states, low_values, grid_states, baseline_extents, center_values)
        high_results = evaluate_model(epcsaft, parameters, system_by_temperature, states, high_values, grid_states, baseline_extents, center_values)
        return group, low_results, high_results

    selected_grid_groups = [group for group in groups if group.key in top_keys]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        grid_futures = [pool.submit(grid_endpoints, group) for group in selected_grid_groups]
        for future in as_completed(grid_futures):
            group, low_results, high_results = future.result()
            for state, low, high in zip(grid_states, low_results, high_results, strict=True):
                row = {"parameter_group": group.key, "parameter_identities": "|".join(group.identities), "temperature_k": state.temperature_k, "loading": state.loading, "lower_status": low.get("status"), "upper_status": high.get("status")}
                for output in ANALYSIS_OUTPUTS:
                    lo = float(low[output]) if low.get("status") == "success" else math.nan
                    hi = float(high[output]) if high.get("status") == "success" else math.nan
                    row[f"{output}_lower"] = lo
                    row[f"{output}_upper"] = hi
                    row[f"{output}_span"] = abs(hi - lo) if math.isfinite(lo) and math.isfinite(hi) else math.nan
                grid_rows.append(row)
    write_csv(RESULTS / "uq_grid_top_parameter_sensitivity.csv", grid_rows)

    uq_rows: list[dict[str, Any]] = []
    valid_samples = [row for row in sample_rows if row.get("status") == "success"]
    for output in ANALYSIS_OUTPUTS:
        values = np.asarray([float(row[output]) for row in valid_samples])
        center_value = float(center_state[output])
        if not len(values):
            uq_rows.append({
                "output": output,
                "baseline": center_value,
                "q_0_025": math.nan,
                "q_0_500": math.nan,
                "q_0_975": math.nan,
                "mean": math.nan,
                "std": math.nan,
                "valid_count": 0,
                "attempted_count": len(sample_rows),
                "failure_fraction": 1.0,
            })
            continue
        uq_rows.append({
            "output": output,
            "baseline": center_value,
            "q_0_025": float(np.percentile(values, 2.5)),
            "q_0_500": float(np.percentile(values, 50.0)),
            "q_0_975": float(np.percentile(values, 97.5)),
            "mean": float(values.mean()),
            "std": float(values.std(ddof=1)),
            "valid_count": len(values),
            "attempted_count": len(sample_rows),
            "failure_fraction": 1.0 - len(values) / len(sample_rows),
        })
    write_csv(RESULTS / "uq_uncertainty_summary.csv", uq_rows)

    design_corr = np.corrcoef(unit_design, rowvar=False)
    receipt = {
        "study_id": "mea-nine-species-all-parameter-smart-lhc-v1",
        "packet_path": str(PACKET),
        "packet_sha256": f"sha256:{sha256(PACKET)}",
        "reaction_input_path": str(REACTION_INPUT),
        "reaction_input_sha256": f"sha256:{sha256(REACTION_INPUT)}",
        "engine_wheel_path": os.environ.get("EPCSAFT_ENGINE_WHEEL", "explicit wheel supplied by caller"),
        "engine_wheel_sha256": f"sha256:{sha256(Path(os.environ['EPCSAFT_ENGINE_WHEEL']))}" if os.environ.get("EPCSAFT_ENGINE_WHEEL") and Path(os.environ["EPCSAFT_ENGINE_WHEEL"]).is_file() else "unresolved",
        "sample_count": SAMPLE_COUNT,
        "valid_sample_count": len(valid_samples),
        "parameter_group_count": len(groups),
        "parameter_identity_count": len(inventory),
        "lhc_seed": SEED,
        "lhc_max_abs_dimension_correlation": float(np.max(np.abs(design_corr - np.eye(design_corr.shape[0])))),
        "central_state": {"temperature_k": central.temperature_k, "loading": central.loading, "source_state": central.source_state},
        "grid_state_count": len(states),
        "grid_top_parameter_count": len(top_keys),
        "smoke": SMOKE,
        "equilibrium_solver": "temporary SciPy Newton reaction-extents bridge with Engine EOS fixed-pressure composition derivatives",
        "uq_status": "screening-prior-input-uncertainty; not measurement-backed posterior covariance",
    }
    (RESULTS / "uq_run_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    manifest = [
        {"artifact": "uq_parameter_inventory.csv", "role": "all packet coordinates, fixed/derived exclusions, and screening priors"},
        {"artifact": "uq_lhc_samples.csv", "role": "scrambled maximin Latin-hypercube central-state samples"},
        {"artifact": "uq_global_sensitivity.csv", "role": "Spearman, rank-SRC, ridge-PRCC, and bootstrap rank intervals"},
        {"artifact": "uq_uncertainty_summary.csv", "role": "screening-prior output quantiles and failure fraction"},
        {"artifact": "uq_local_sensitivity.csv", "role": "all included parameter lower/upper central-state responses"},
        {"artifact": "uq_state_grid_baseline.csv", "role": "central candidate baseline over temperature/loading grid"},
        {"artifact": "uq_grid_top_parameter_sensitivity.csv", "role": "top pCO2-ranked parameters over full state grid"},
        {"artifact": "uq_run_receipt.json", "role": "engine, packet, seed, sample, and claim-boundary receipt"},
    ]
    write_csv(RESULTS / "uq_manifest.csv", manifest)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
