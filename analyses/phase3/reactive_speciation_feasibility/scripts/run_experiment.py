from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from MEA.common.analysis_io import file_sha256, repo_relative_path, write_json_file
from MEA.epcsaft_ionic.speciation_feasibility import ActivityState, solve_activity_speciation
from MEA.smith_missen.ideal_speciation import REACTION_IDS, REACTION_MATRIX, SPECIES_9, solve_ideal_speciation

ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_ROOT = ROOT / "analyses" / "phase3" / "reactive_speciation_feasibility"
RESULTS = ANALYSIS_ROOT / "results"
PINNED_RECEIPT = RESULTS / "pinned_reference.json"
FINAL_RECEIPT = RESULTS / "reactive_speciation_feasibility_receipt.json"
PARAMETER_ROOT = ROOT / "data" / "reference" / "epcsaft_datasets" / "MEA_CO2_H2O_phase2"
PURE_CSV = PARAMETER_ROOT / "pure" / "any_solvent.csv"
KIJ_CSV = PARAMETER_ROOT / "mixed" / "binary_interaction" / "k_ij.csv"
TEMPERATURE_K = 313.15
PRESSURE_PA = 101325.0
MEA_WEIGHT_FRACTION = 0.30
LOADINGS = (0.20, 0.40, 0.60)
PERTURBATION_SEED = 20260717

def _pinned_lane() -> dict[str, Any]:
    import epcsaft

    from MEA.epcsaft_ionic.model import solve_activity_speciation as solve_pinned
    from MEA.epcsaft_ionic.model import state_for_x

    states = []
    for loading in LOADINGS:
        seed = solve_ideal_speciation(loading, MEA_WEIGHT_FRACTION, TEMPERATURE_K).mole_fractions
        started = perf_counter()
        prediction = solve_pinned(
            loading,
            TEMPERATURE_K,
            PRESSURE_PA,
            seed,
            {},
            dataset=PARAMETER_ROOT,
        )
        elapsed = perf_counter() - started
        state = state_for_x(seed, TEMPERATURE_K, PRESSURE_PA, {}, dataset=PARAMETER_ROOT)
        gamma_map = state.activity_coefficient()
        ln_phi = np.asarray(state.fugacity_coefficient(natural_log=True), dtype=float)
        log_gamma = np.asarray([math.log(float(gamma_map[name])) for name in SPECIES_9])
        states.append(
            {
                "loading": loading,
                "seed_mole_fractions": dict(zip(SPECIES_9, seed.tolist())),
                "accepted": prediction.accepted,
                "solver_returned_success": prediction.solver_returned_success,
                "rejection_reason": prediction.rejection_reason,
                "message": prediction.message,
                "mole_fractions": dict(zip(SPECIES_9, prediction.x.tolist())),
                "activity_coefficients": prediction.activity_coefficients,
                "reaction_residuals": prediction.reaction_residuals,
                "mass_balance_residuals": prediction.mass_balance_residuals,
                "charge_residual": prediction.charge_residual,
                "state_failure_count": prediction.state_failure_count,
                "elapsed_seconds": elapsed,
                "seed_log_fugacity_coefficients": dict(zip(SPECIES_9, ln_phi.tolist())),
                "seed_log_activity_coefficients": dict(zip(SPECIES_9, log_gamma.tolist())),
                "seed_reference_log_fugacity": dict(zip(SPECIES_9, (ln_phi - log_gamma).tolist())),
            }
        )
    return {
        "lane": "pinned_epcsaft_1_5_2",
        "epcsaft_version": epcsaft.__version__,
        "epcsaft_module_file": Path(epcsaft.__file__).name,
        "temperature_K": TEMPERATURE_K,
        "pressure_Pa": PRESSURE_PA,
        "mea_weight_fraction": MEA_WEIGHT_FRACTION,
        "states": states,
    }


def _build_clean_eos():
    from epcsaft import EPCSAFT

    from MEA.epcsaft_ionic.diagnostic_bundle import (
        COMPONENT_IDS,
        build_mea_diagnostic_bundle,
    )

    bundle = build_mea_diagnostic_bundle(purpose="package-test-fixture")
    selected = bundle.select(COMPONENT_IDS)
    return EPCSAFT(selected), bundle.fingerprint, selected.fingerprint


class CleanProviderActivityEvaluator:
    def __init__(self, eos: Any, unit_registry: Any) -> None:
        self.eos = eos
        self.u = unit_registry
        self.evaluation_count = 0
        self.eos_evaluation_count = 0

    def _evaluate_log_phi(self, x: np.ndarray) -> tuple[np.ndarray, Any]:
        from scipy.optimize import brentq

        def pressure_residual(molar_density: float) -> float:
            self.eos_evaluation_count += 1
            trial = self.eos.evaluate(
                temperature=TEMPERATURE_K * self.u.kelvin,
                molar_density=molar_density * self.u.mole / self.u.meter**3,
                mole_fractions=tuple(float(value) for value in x),
            )
            return float(trial.pressure.to("pascal").magnitude) - PRESSURE_PA

        density = brentq(pressure_residual, 20000.0, 60000.0, xtol=1.0e-8)
        self.eos_evaluation_count += 1
        result = self.eos.evaluate(
            temperature=TEMPERATURE_K * self.u.kelvin,
            molar_density=density * self.u.mole / self.u.meter**3,
            mole_fractions=tuple(float(value) for value in x),
        )
        if result.log_fugacity_coefficient is None:
            raise ValueError("clean provider did not return log fugacity coefficients")
        values = np.asarray(result.log_fugacity_coefficient, dtype=float)
        if not np.all(np.isfinite(values)):
            raise ValueError("clean provider returned nonfinite log fugacity coefficients")
        return values, result

    def evaluate(
        self,
        temperature_K: float,
        pressure_Pa: float,
        mole_fractions: np.ndarray,
    ) -> ActivityState:
        if temperature_K != TEMPERATURE_K or pressure_Pa != PRESSURE_PA:
            raise ValueError("feasibility evaluator is fixed to the preregistered state conditions")
        self.evaluation_count += 1
        x = np.asarray(mole_fractions, dtype=float)
        ln_phi, result = self._evaluate_log_phi(x)
        reference_x = x.copy()
        reference_x[3:] = 0.0
        reference_x /= float(np.sum(reference_x))
        reference_ln_phi, reference_result = self._evaluate_log_phi(reference_x)
        log_gamma = ln_phi - reference_ln_phi
        return ActivityState(
            log_activities=np.log(np.clip(x, 1.0e-300, None)) + log_gamma,
            convention="mole_fraction_activity",
            diagnostics={
                "mapping": "ln(a_i)=ln(x_i)+ln(phi_i)-ln(phi_i,infinite-dilution-neutral-pool)",
                "density_mol_m3": float(result.molar_density.to("mole / meter ** 3").magnitude),
                "reference_density_mol_m3": float(reference_result.molar_density.to("mole / meter ** 3").magnitude),
                "pressure_residual_Pa": float(result.pressure.to("pascal").magnitude) - PRESSURE_PA,
                "reference_pressure_residual_Pa": float(reference_result.pressure.to("pascal").magnitude) - PRESSURE_PA,
            },
        )

    def convention_probe(self, x: np.ndarray) -> dict[str, dict[str, float]]:
        ln_phi, _ = self._evaluate_log_phi(x)
        reference_x = x.copy()
        reference_x[3:] = 0.0
        reference_x /= float(np.sum(reference_x))
        reference_ln_phi, _ = self._evaluate_log_phi(reference_x)
        return {
            "log_fugacity_coefficients": dict(zip(SPECIES_9, ln_phi.tolist())),
            "reference_log_fugacity": dict(zip(SPECIES_9, reference_ln_phi.tolist())),
            "log_activity_coefficients": dict(zip(SPECIES_9, (ln_phi - reference_ln_phi).tolist())),
        }


def _perturbed_seeds(seed: np.ndarray, rng: np.random.Generator) -> list[tuple[str, np.ndarray]]:
    seeds = [("phase1_nominal", seed)]
    for index, scale in enumerate((0.20, 0.45), start=1):
        perturbed = seed * np.exp(rng.normal(0.0, scale, size=seed.size))
        perturbed /= float(np.sum(perturbed))
        seeds.append((f"lognormal_{index}_scale_{scale:.2f}", perturbed))
    return seeds


def _clean_lane(pinned: dict[str, Any]) -> dict[str, Any]:
    import epcsaft
    from epcsaft import unit_registry as u

    eos, bundle_fingerprint, parameter_fingerprint = _build_clean_eos()
    evaluator = CleanProviderActivityEvaluator(eos, u)
    pinned_by_loading = {float(row["loading"]): row for row in pinned["states"]}
    rng = np.random.default_rng(PERTURBATION_SEED)
    states = []
    all_success = True
    for loading in LOADINGS:
        ideal = solve_ideal_speciation(loading, MEA_WEIGHT_FRACTION, TEMPERATURE_K)
        runs = []
        for seed_label, seed in _perturbed_seeds(ideal.mole_fractions, rng):
            before_activity = evaluator.evaluation_count
            before_eos = evaluator.eos_evaluation_count
            result = solve_activity_speciation(
                loading=loading,
                mea_weight_fraction=MEA_WEIGHT_FRACTION,
                temperature_K=TEMPERATURE_K,
                pressure_Pa=PRESSURE_PA,
                evaluator=evaluator,
                initial_mole_fractions=seed,
            )
            all_success = all_success and result.success
            runs.append(
                {
                    "seed": seed_label,
                    "success": result.success,
                    "message": result.message,
                    "mole_fractions": dict(zip(SPECIES_9, result.mole_fractions.tolist())),
                    "residuals": result.residuals,
                    "max_abs_residual": result.max_abs_residual,
                    "activity_evaluations": result.provider_evaluations,
                    "activity_evaluator_count_delta": evaluator.evaluation_count - before_activity,
                    "public_eos_evaluations": evaluator.eos_evaluation_count - before_eos,
                    "elapsed_seconds": result.elapsed_seconds,
                    "activity_diagnostics": result.activity_diagnostics,
                }
            )
        nominal_x = np.asarray([runs[0]["mole_fractions"][name] for name in SPECIES_9])
        repeat_x = np.asarray([[run["mole_fractions"][name] for name in SPECIES_9] for run in runs])
        pinned_row = pinned_by_loading[loading]
        pinned_x = np.asarray([pinned_row["mole_fractions"][name] for name in SPECIES_9])
        states.append(
            {
                "loading": loading,
                "runs": runs,
                "max_repeat_mole_fraction_spread": float(np.max(np.ptp(repeat_x, axis=0))),
                "nominal_minus_pinned_mole_fractions": dict(zip(SPECIES_9, (nominal_x - pinned_x).tolist())),
                "max_abs_nominal_minus_pinned": float(np.max(np.abs(nominal_x - pinned_x))),
                "pinned_reaction_residuals": pinned_row["reaction_residuals"],
                "pinned_mass_balance_residuals": pinned_row["mass_balance_residuals"],
                "pinned_charge_residual": pinned_row["charge_residual"],
            }
        )

    probe_seed = np.asarray(
        [pinned_by_loading[0.40]["seed_mole_fractions"][name] for name in SPECIES_9],
        dtype=float,
    )
    probe = evaluator.convention_probe(probe_seed)
    pinned_probe = pinned_by_loading[0.40]
    clean_gamma = np.asarray([probe["log_activity_coefficients"][name] for name in SPECIES_9])
    pinned_gamma = np.asarray([pinned_probe["seed_log_activity_coefficients"][name] for name in SPECIES_9])
    clean_reference = np.asarray([probe["reference_log_fugacity"][name] for name in SPECIES_9])
    pinned_reference = np.asarray([pinned_probe["seed_reference_log_fugacity"][name] for name in SPECIES_9])
    reaction_gamma_difference = REACTION_MATRIX @ (clean_gamma - pinned_gamma)
    return {
        "lane": "clean_provider_public_python_api",
        "epcsaft_version": getattr(epcsaft, "__version__", "unknown"),
        "epcsaft_module_file": Path(epcsaft.__file__).name,
        "bundle_fingerprint": bundle_fingerprint,
        "parameter_fingerprint": parameter_fingerprint,
        "activity_convention_probe": {
            **probe,
            "pinned_log_activity_coefficients": pinned_probe["seed_log_activity_coefficients"],
            "pinned_reference_log_fugacity": pinned_probe["seed_reference_log_fugacity"],
            "max_abs_log_gamma_difference": float(np.max(np.abs(clean_gamma - pinned_gamma))),
            "max_abs_reference_log_fugacity_difference": float(np.max(np.abs(clean_reference - pinned_reference))),
            "reaction_log_activity_coefficient_difference": dict(
                zip(REACTION_IDS, reaction_gamma_difference.tolist())
            ),
            "max_abs_reaction_log_activity_coefficient_difference": float(
                np.max(np.abs(reaction_gamma_difference))
            ),
            "standard_state_evidence": "Pinned 1.5.2 defines gamma_i as phi_i divided by the same-pressure infinite-dilution neutral-pool reference; the clean lane evaluates the zero-ion limit through public EPCSAFT.evaluate.",
        },
        "states": states,
        "all_runs_successful": all_success,
    }


def _source_hashes() -> dict[str, str]:
    paths = (
        PURE_CSV,
        KIJ_CSV,
        PARAMETER_ROOT / "mixed" / "binary_interaction" / "k_hb_ij.csv",
        PARAMETER_ROOT / "user_options.json",
        ROOT / "src" / "MEA" / "epcsaft_ionic" / "diagnostic_bundle.py",
        ROOT / "src" / "MEA" / "epcsaft_ionic" / "speciation_feasibility.py",
        Path(__file__).resolve(),
    )
    return {repo_relative_path(path): file_sha256(path) for path in paths}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", required=True, choices=("pinned", "clean"))
    args = parser.parse_args()
    if args.lane == "pinned":
        payload = _pinned_lane()
        write_json_file(PINNED_RECEIPT, payload)
        print(PINNED_RECEIPT)
        return

    if not PINNED_RECEIPT.is_file():
        raise FileNotFoundError(f"run --lane pinned first: {PINNED_RECEIPT}")
    pinned = json.loads(PINNED_RECEIPT.read_text(encoding="utf-8"))
    clean = _clean_lane(pinned)
    wheel_text = os.environ.get("CLEAN_PROVIDER_WHEEL")
    wheel = Path(wheel_text) if wheel_text else None
    conclusion = "feasible" if clean["all_runs_successful"] else "blocked"
    receipt = {
        "schema_version": 2,
        "experiment": "lightweight_mea_reactive_speciation_over_clean_provider",
        "conclusion": conclusion,
        "claim_boundary": "diagnostic_reference_oracle_and_seed_generator_only",
        "regression_execution_admitted": False,
        "parameter_promotion_allowed": False,
        "conditions": {
            "temperature_K": TEMPERATURE_K,
            "pressure_Pa": PRESSURE_PA,
            "mea_weight_fraction": MEA_WEIGHT_FRACTION,
            "loadings": LOADINGS,
        },
        "source_hashes": _source_hashes(),
        "clean_provider_wheel": (
            {"filename": wheel.name, "sha256": file_sha256(wheel)}
            if wheel is not None and wheel.is_file()
            else None
        ),
        "pinned_lane": {
            "path": repo_relative_path(PINNED_RECEIPT),
            "sha256": file_sha256(PINNED_RECEIPT),
        },
        "clean_lane": clean,
        "tasks": {
            "1_public_parameter_construction": "completed",
            "2_finite_convention_correct_activities": "completed",
            "3_three_state_solve_from_phase1_seed": "completed" if clean["all_runs_successful"] else "blocked",
            "4_composition_and_residual_comparison": "completed",
            "5_perturbed_seed_cost_measurement": "completed",
        },
    }
    write_json_file(FINAL_RECEIPT, receipt)
    print(FINAL_RECEIPT)


if __name__ == "__main__":
    main()
