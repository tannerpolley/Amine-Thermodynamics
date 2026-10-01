"""Issue 140 diagnostic source constants and reuse of its frozen loaded-fit method."""

import csv
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent
OUT = BASE / "stage-2"
OUT.mkdir(exist_ok=True)


def load(filename):
    spec = importlib.util.spec_from_file_location(filename.replace("-", "_"), BASE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fit = load("low-temperature-fit.py")
assessment = load("assessment.py")
pa = load("phase-a.py")
s = fit.s
R = pa.probe.epcsaft.GAS_CONSTANT_J_PER_MOL_K
fit.HERE = assessment.HERE = OUT
fit.RAW = assessment.RAW = pa.RAW / "stage-2"
fit.SOURCE = OUT / "restored-source-parameters.json"
fit.RAW.mkdir(exist_ok=True)
# The original module stays the only wheel, packet and reference-verification owner.
assessment.calculation = lambda: pa


def source_constants():
    assert not (OUT / "source-fit.json").exists(), "source fits run once"
    environment = pa.verify()
    inputs = json.loads((BASE / "stage-2-inputs.json").read_text())["inputs"]
    sys.path.insert(0, str(pa.BUNDLE / "scripts"))
    from verify_temperature_reference import water_reference

    results, residuals, heat_rows = {}, [], []
    change = {}
    for rid, item in (("R4", inputs[2]), ("R5", inputs[0])):
        rows = item["selected_rows"]
        T = np.array([float(r["temperature_K"]) for r in rows])
        assert len(T) == 4 and np.all(T <= 333.15)
        density = np.array([water_reference(t)[1] * .01801528 / 1000 for t in T])
        y = (
            -np.log([float(r["constant_reported_dm3_per_mol"]) for r in rows]) - np.log(density)
            if rid == "R4" else np.array([float(r["ln_Ka"]) for r in rows])
        )
        X = np.column_stack((np.ones(len(T)), 1 / T - 1 / 313.15))
        theta, _, rank, singular = np.linalg.lstsq(X, y, rcond=None)
        assert rank == 2
        error = X @ theta - y
        variance = float(error @ error / (len(T) - 2))
        cov = variance * np.linalg.inv(X.T @ X)
        transform = np.array([[1., -1 / 313.15], [0., 1.]])
        A, B = transform @ theta
        ab_cov = transform @ cov @ transform.T
        results[rid] = {
            "A": float(A), "B_K": float(B), "C": 0., "D_per_K": 0.,
            "L0": float(theta[0]), "T0_K": 313.15, "covariance_L0_B": cov.tolist(),
            "covariance_A_B": ab_cov.tolist(), "residual_variance_ln_K": variance,
            "degrees_of_freedom": 2, "rank": int(rank), "singular_values": singular.tolist(),
            "coefficient_correlation_A_B": float(ab_cov[0, 1] / np.sqrt(ab_cov[0, 0] * ab_cov[1, 1])),
            "enthalpy_dissociation_or_hydrolysis_kJ_per_mol": float(-R * B / 1000),
            "enthalpy_residual_based_SE_kJ_per_mol": float(R * np.sqrt(cov[1, 1]) / 1000),
            "source_path": item["path"], "source_file_sha256": item["sha256"],
            "source_temperature_range_K": [float(min(T)), float(max(T))],
        }
        for row, t, observed, delta, rho in zip(rows, T, y, error, density, strict=True):
            residuals.append({
                "reaction": rid, "source_row": row["source_row"], "temperature_K": float(t),
                "observed_converted_ln_K": float(observed), "fitted_ln_K": float(observed + delta),
                "residual_ln_K": float(delta), "density_kg_per_L": float(rho) if rid == "R4" else None,
                "temperature_uncertainty_K": row["temperature_uncertainty_K"],
                "temperature_effect_ln_K_scale": float(abs(B / t**2) * float(row["temperature_uncertainty_K"] or .5)),
            })
        change.update(
            {"reaction:R4:correlation:a": float(A), "reaction:R4:correlation:b_k": float(B)}
            if rid == "R4" else {
                "reaction:R5:correlation:a_k": float(-B / math.log(10)),
                "reaction:R5:correlation:b": float(-A / math.log(10)),
                "reaction:R5:correlation:c_per_k": 0.,
            }
        )
    for row in inputs[1]["selected_rows"]:
        measured = float(row["enthalpy_protonation_reported_kJ_per_mol"])
        predicted = results["R5"]["enthalpy_dissociation_or_hydrolysis_kJ_per_mol"]
        heat_rows.append({
            "source_row": row["source_row"], "temperature_K": float(row["temperature_K"]),
            "measured_positive_release_kJ_per_mol": measured,
            "fitted_positive_release_kJ_per_mol": predicted,
            "fitted_protonation_enthalpy_kJ_per_mol": -predicted,
            "difference_release_kJ_per_mol": predicted - measured,
            "source_stated_heat_uncertainty_scale_kJ_per_mol": .025 * measured,
            "fitted_enthalpy_residual_based_SE_kJ_per_mol": results["R5"]["enthalpy_residual_based_SE_kJ_per_mol"],
            "chemical_consistency": "UNRESOLVED: source measurement uncertainty unavailable",
        })
    scatter = []
    finite = inputs[2]["empirical_finite_I_rows"]
    for t, salt in sorted({(r["temperature_K"], r["NaClO4_mol_per_dm3"]) for r in finite}):
        group = [r for r in finite if r["temperature_K"] == t and r["NaClO4_mol_per_dm3"] == salt]
        values = [float(r["constant_reported_dm3_per_mol"]) for r in group]
        assert len(values) == 3
        scatter.append({
            "temperature_K": t, "added_NaClO4_mol_per_dm3": salt, "loading_conditions": 3,
            "Kc_min_L_per_mol": min(values), "Kc_max_L_per_mol": max(values),
            "Kc_range_L_per_mol": max(values) - min(values), "Kc_mean_L_per_mol": float(np.mean(values)),
            "Kc_sample_SD_across_loadings_L_per_mol": float(np.std(values, ddof=1)),
            "meaning": "finite-I loading scatter, not replicate or zero-I uncertainty",
            "zero_I_scatter": "unavailable: reliable total ionic strengths not tabulated",
        })
    mapping = s.with_parameter_values(s.parameter_mapping(BASE / "restored-source-parameters.json"), change)
    for reaction in mapping["reaction_correlations"]:
        rid = reaction["reaction_id"]
        if rid in results:
            reaction["source"] = {"source_id": "Aroua1999" if rid == "R4" else "KimProtonation2011", "locator": "source-fit.json; source-only diagnostic A+B/T"}
            reaction["source_sha256"] = "sha256:" + results[rid]["source_file_sha256"]
            reaction["source_temperature_range_k"] = results[rid]["source_temperature_range_K"]
    mapping["purpose"] = "Issue 140 diagnostic: source measurement uncertainty unavailable; not adopted"
    fit.save(fit.SOURCE, mapping)
    pa.probe.epcsaft.Parameters.from_mapping(mapping)
    native = s._engine_reaction_records(json.loads(fit.TRAINING.read_text())[0]["request"], s.reaction_values(mapping))
    for reaction in native:
        reaction["engine_correlation"]["temperature_min"] = 293.15
        reaction["engine_correlation"]["temperature_max"] = 353.15
    checks = []
    for row in residuals:
        rid, t = row["reaction"], row["temperature_K"]
        c = native[int(rid[1:]) - 1]["engine_correlation"]
        value = c["a"] + c["b"] / t + c["c"] * math.log(t / c["reference_temperature"]) + c["d"] * t
        difference = value - row["fitted_ln_K"]
        assert abs(difference) <= 5e-13
        checks.append({"reaction": rid, "temperature_K": t, "native_ln_K": value, "difference_ln_K": difference})
    fit.save(OUT / "native-reaction-inputs.json", native)
    for filename in ("training-targets.csv", "assessment-row-ids.json", "never-accessed-vle-admission.csv"):
        (OUT / filename).symlink_to(Path("..") / filename)
    (OUT / "preregistration.md").symlink_to(Path("..") / "stage-2-preregistration.md")
    hashes = json.loads((BASE / "input-hashes.json").read_text())
    hashes["hashes"][str(fit.SOURCE.relative_to(pa.probe.W))] = s.sha256(fit.SOURCE)
    fit.save(OUT / "input-hashes.json", hashes)
    fit.table(OUT / "source-residuals.csv", residuals)
    fit.table(OUT / "protonation-enthalpy-comparison.csv", heat_rows)
    fit.table(OUT / "finite-I-loading-scatter.csv", scatter)
    fit.table(OUT / "native-coefficient-checks.csv", checks)
    fit.save(OUT / "source-fit.json", {
        "label": "diagnostic: source measurement uncertainty unavailable", "chemical_consistency": "UNRESOLVED",
        "coefficients": results, "environment": environment,
        "covariance_meaning": "OLS residual covariance, independent equal-variance assumption; no measured covariance",
        "density_meaning": "Wagner-Pruss saturated-liquid water approximation, not exact ambient reference",
        "input_snapshot_sha256": s.sha256(BASE / "stage-2-inputs.json"),
        "preregistration_sha256": s.sha256(BASE / "stage-2-preregistration.md"),
        "producer_sha256": s.sha256(Path(__file__)),
    })
    print(json.dumps(results), flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["source"]:
        source_constants()
    elif args[0] == "fit":
        fit.fit(*args[1:])
    elif args[0] == "rescore":
        fit.rescore(*args[1:])
    elif args == ["select"]:
        assessment.select()
    elif args[0] == "stage":
        assessment.stage(int(args[1]))
    elif args == ["heat"]:
        freeze = json.loads((OUT / "freeze.json").read_text())
        assert freeze["records"] and (OUT / "assessment-stage-5.json").exists()
        assert not (OUT / "heat-comparison.json").exists(), "heat assessed once"
        assessment.heat_comparison(pa, freeze, time.perf_counter() + 1780, adopted_baseline=BASE)
    else:
        raise SystemExit("source | fit STRUCTURE START | rescore STRUCTURE START | select | stage 1..5 | heat")
