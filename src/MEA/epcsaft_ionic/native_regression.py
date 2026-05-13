from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np

from MEA.epcsaft_ionic.model import (
    ADVANCED_BORN_USER_OPTIONS,
    BOUNDS,
    DEFAULT_INITIAL_GUESS,
    SPECIES,
    SPECIES_INDEX,
    SpeciationTarget,
    VLETarget,
    _base_params,
    apparent_totals,
    load_epcsaft,
    load_speciation_targets,
    load_vle_targets,
    reactive_balances,
    reaction_definitions,
    to_jsonable,
)

PRESSURE_TRAIN_SOURCES = frozenset({"Aronu", "Hilliard", "Idris", "Mamun"})
PRESSURE_VALIDATION_SOURCES = frozenset({"Jou", "Xu"})
SPECIATION_TRAIN_SOURCES = frozenset({"Bottinger", "Matin"})
SPECIATION_VALIDATION_SOURCES = frozenset({"Jakobsen"})
VAPOR_SPECIES = ("CO2", "H2O", "MEA")
NONVOLATILE_SPECIES = ("MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-")
VOLATILE_SPECIES = VAPOR_SPECIES

BASE_FIT_PARAMETERS = (
    "MEAH+__s",
    "MEAH+__e",
    "MEAH+__d_born",
    "MEACOO-__s",
    "MEACOO-__e",
    "MEACOO-__d_born",
    "k_ij__CO2__MEA",
    "k_ij__MEA__H2O",
    "k_ij__MEAH+__MEACOO-",
    "k_ij__MEAH+__HCO3-",
)
CARBONATE_BORN_PARAMETERS = ("HCO3-__d_born", "CO3^2-__d_born")


@dataclass(frozen=True)
class NativeRegressionProblem:
    species: tuple[str, ...]
    rows: tuple[dict[str, Any], ...]
    parameter_specs: tuple[dict[str, Any], ...]
    regularization_terms: tuple[dict[str, Any], ...]
    balances: dict[str, dict[str, float]]
    advanced_born_user_options: dict[str, Any]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(
            {
                "species": list(self.species),
                "rows": list(self.rows),
                "parameter_specs": list(self.parameter_specs),
                "regularization_terms": list(self.regularization_terms),
                "balances": self.balances,
                "advanced_born_user_options": self.advanced_born_user_options,
                "metadata": self.metadata,
            }
        )


def _species_map(x: np.ndarray) -> dict[str, float]:
    return {species: float(x[SPECIES_INDEX[species]]) for species in SPECIES}


def _reaction_payload(temperature_K: float) -> list[dict[str, Any]]:
    return [
        {
            "name": str(reaction.name),
            "stoichiometry": dict(reaction.stoichiometry),
            "log_equilibrium_constant": float(reaction.log_equilibrium_constant),
            "standard_state": str(getattr(reaction, "standard_state", "mole_fraction_activity")),
        }
        for reaction in reaction_definitions(float(temperature_K))
    ]


def _pressure_split(source: str) -> str:
    if source in PRESSURE_VALIDATION_SOURCES:
        return "validation"
    if source in PRESSURE_TRAIN_SOURCES:
        return "train"
    return "unspecified"


def _speciation_split(source: str) -> str:
    if source in SPECIATION_VALIDATION_SOURCES:
        return "validation"
    if source in SPECIATION_TRAIN_SOURCES:
        return "train"
    return "unspecified"


def build_pressure_target_rows(targets: Iterable[VLETarget]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target in targets:
        source = str(target.paper)
        rows.append(
            {
                "row_id": target.row_id,
                "mode": "bubble",
                "T": float(target.T),
                "P": float(target.P),
                "P_seed": max(float(target.P), float(target.pressure_kPa) * 1000.0, 1.0e3),
                "loading": float(target.loading),
                "initial_x": _species_map(np.asarray(target.x, dtype=float)),
                "apparent_totals": apparent_totals(float(target.loading)),
                "balances": reactive_balances(),
                "reactions": _reaction_payload(float(target.T)),
                "vapor_species": list(VAPOR_SPECIES),
                "volatile_species": list(VOLATILE_SPECIES),
                "nonvolatile_species": list(NONVOLATILE_SPECIES),
                "targets": {
                    "partial_pressures": {"CO2": float(target.pressure_kPa) * 1000.0},
                },
                "target_partial_pressures": {"CO2": float(target.pressure_kPa) * 1000.0},
                "source": source,
                "split": _pressure_split(source),
                "metadata": {
                    "target_family": "pressure",
                    "pressure_kPa": float(target.pressure_kPa),
                    "co2_loading": float(target.loading),
                    "temperature_C": float(target.T) - 273.15,
                },
            }
        )
    return rows


def build_speciation_target_rows(targets: Iterable[SpeciationTarget]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target in targets:
        source = str(target.source)
        target_speciation = _species_map(np.asarray(target.x, dtype=float))
        rows.append(
            {
                "row_id": target.row_id,
                "mode": "speciation",
                "T": float(target.T),
                "P": float(target.P),
                "P_seed": float(target.P),
                "loading": float(target.loading),
                "initial_x": target_speciation,
                "apparent_totals": apparent_totals(float(target.loading)),
                "balances": reactive_balances(),
                "reactions": _reaction_payload(float(target.T)),
                "vapor_species": list(VAPOR_SPECIES),
                "volatile_species": list(VOLATILE_SPECIES),
                "nonvolatile_species": list(NONVOLATILE_SPECIES),
                "targets": {
                    "speciation": target_speciation,
                },
                "target_speciation": target_speciation,
                "source": source,
                "split": _speciation_split(source),
                "metadata": {
                    "target_family": "speciation",
                    "co2_loading": float(target.loading),
                    "temperature_C": float(target.T) - 273.15,
                },
            }
        )
    return rows


def build_parameter_specs(*, include_carbonate_born: bool = True) -> list[dict[str, Any]]:
    names = BASE_FIT_PARAMETERS + (CARBONATE_BORN_PARAMETERS if include_carbonate_born else ())
    specs: list[dict[str, Any]] = []
    for name in names:
        lower, upper = BOUNDS[name]
        initial = float(DEFAULT_INITIAL_GUESS[name])
        specs.append(
            {
                "name": name,
                "initial": initial,
                "lower": float(lower),
                "upper": float(upper),
                "scale": max(abs(initial), 1.0),
                "regularization_weight": 0.003,
                "provenance": "MEA evidence window",
            }
        )
    return specs


def build_regularization_terms(parameter_specs: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "parameter": str(spec["name"]),
            "target": float(spec["initial"]),
            "weight": float(spec["regularization_weight"]),
            "scale": float(spec["scale"]),
        }
        for spec in parameter_specs
        if float(spec.get("regularization_weight", 0.0)) > 0.0
    ]


def build_native_regression_problem(
    *,
    max_pressure_records: int | None = None,
    max_speciation_records: int | None = None,
    include_carbonate_born: bool = True,
) -> NativeRegressionProblem:
    pressure_targets = load_vle_targets(max_pressure_records)
    speciation_targets = load_speciation_targets(max_speciation_records)
    parameter_specs = build_parameter_specs(include_carbonate_born=include_carbonate_born)
    rows = build_pressure_target_rows(pressure_targets) + build_speciation_target_rows(speciation_targets)
    return NativeRegressionProblem(
        species=tuple(SPECIES),
        rows=tuple(rows),
        parameter_specs=tuple(parameter_specs),
        regularization_terms=tuple(build_regularization_terms(parameter_specs)),
        balances=reactive_balances(),
        advanced_born_user_options=to_jsonable(ADVANCED_BORN_USER_OPTIONS),
        metadata={
            "pressure_row_count": len(pressure_targets),
            "speciation_row_count": len(speciation_targets),
            "pressure_split_rule": {
                "train": sorted(PRESSURE_TRAIN_SOURCES),
                "validation": sorted(PRESSURE_VALIDATION_SOURCES),
            },
            "speciation_split_rule": {
                "train": sorted(SPECIATION_TRAIN_SOURCES),
                "validation": sorted(SPECIATION_VALIDATION_SOURCES),
            },
            "optimizer_owner": "epcsaft",
            "downstream_role": "target_construction_and_result_artifacts",
        },
    )


def to_epcsaft_batch(problem: NativeRegressionProblem):
    epcsaft = load_epcsaft()
    reference_row = problem.rows[0]
    reference_x = np.asarray([reference_row["initial_x"][species] for species in problem.species], dtype=float)
    rows = [
        epcsaft.ReactiveElectrolyteRow(
            row_id=str(row["row_id"]),
            T=float(row["T"]),
            P=float(row.get("P")) if row.get("P") is not None else None,
            P_seed=float(row.get("P_seed")) if row.get("P_seed") is not None else None,
            initial_x=dict(row["initial_x"]),
            balances=dict(row["balances"]),
            totals=dict(row["apparent_totals"]),
            reactions=list(row["reactions"]),
            vapor_species=list(row["vapor_species"]),
            target_partial_pressures=dict(row.get("target_partial_pressures", {})),
            target_speciation=dict(row.get("target_speciation", {})),
            source=str(row.get("source", "")),
            split=str(row.get("split", "")),
            metadata=dict(row.get("metadata", {})),
            mode=str(row["mode"]),
        )
        for row in problem.rows
    ]
    return epcsaft.ReactiveElectrolyteBatch(
        species=problem.species,
        rows=rows,
        balances=problem.balances,
        reactions=problem.rows[0]["reactions"],
        vapor_species=VAPOR_SPECIES,
        volatile_species=VOLATILE_SPECIES,
        nonvolatile_species=NONVOLATILE_SPECIES,
        base_parameters=_base_params(reference_x, float(reference_row["T"])),
        user_options=problem.advanced_born_user_options,
    )


def parameter_maps(problem: NativeRegressionProblem) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    initial = {str(spec["name"]): float(spec["initial"]) for spec in problem.parameter_specs}
    lower = {str(spec["name"]): float(spec["lower"]) for spec in problem.parameter_specs}
    upper = {str(spec["name"]): float(spec["upper"]) for spec in problem.parameter_specs}
    return initial, lower, upper
