from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from MEA.six_species.plot_pressure import legacy_pcsaft_params  # noqa: E402

try:
    from pcsaft import flashTQ
except ImportError as exc:
    raise RuntimeError("The retained neutral pressure reference requires the locked pcsaft dependency") from exc


ANALYSIS_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ANALYSIS_DIR / "results"
STATES_PATH = RESULTS_DIR / "state_species_results.csv"
VLE_PATH = REPO_ROOT / "data/reference/MEA/observations/vapor_liquid_equilibrium/Combined_VLE.csv"

MODELS = ("ideal_9_species", "ideal_6_species")
TOTALS = {
    "CO2": ("CO2", "MEACOO-", "HCO3-", "CO3^2-"),
    "MEA": ("MEA", "MEAH+", "MEACOO-"),
    "H2O": ("H2O", "HCO3-", "CO3^2-", "H3O+", "OH-"),
}


def _apparent_rows(states: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for keys, group in states[states["state_family"] == "vle"].groupby(
        ["source", "temperature_C", "CO2_loading", "model"], sort=True
    ):
        source, temperature_C, loading, model = keys
        values = group.set_index("species")["amount_per_mol_initial_MEA"]
        totals = {parent: float(values.reindex(species, fill_value=0.0).sum()) for parent, species in TOTALS.items()}
        denominator = sum(totals.values())
        rows.append(
            {
                "source": source,
                "temperature_C": temperature_C,
                "CO2_loading": loading,
                "model": model,
                **{f"apparent_x_{parent}": value / denominator for parent, value in totals.items()},
            }
        )
    return pd.DataFrame(rows)


def _metrics(results: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (model, temperature_C), group in results.groupby(["model", "temperature_C"], sort=True):
        rows.append({"model": model, "temperature_C": temperature_C, **_metric_values(group)})
    for model, group in results.groupby("model", sort=True):
        rows.append({"model": model, "temperature_C": "overall", **_metric_values(group)})
    return pd.DataFrame(rows)


def _metric_values(group: pd.DataFrame) -> dict[str, object]:
    valid = group[group["status"] == "success"]
    log_error = valid["log10_predicted_over_observed"].to_numpy(dtype=float)
    pressure_error = (valid["predicted_CO2_pressure_kPa"] - valid["observed_CO2_pressure_kPa"]).to_numpy(dtype=float)
    return {
        "attempted_count": len(group),
        "success_count": len(valid),
        "coverage_fraction": len(valid) / len(group) if len(group) else np.nan,
        "median_abs_log10_error": np.median(np.abs(log_error)) if len(log_error) else np.nan,
        "median_log10_predicted_over_observed": np.median(log_error) if len(log_error) else np.nan,
        "rmse_log10_error": np.sqrt(np.mean(log_error**2)) if len(log_error) else np.nan,
        "mae_pressure_kPa": np.mean(np.abs(pressure_error)) if len(pressure_error) else np.nan,
        "rmse_pressure_kPa": np.sqrt(np.mean(pressure_error**2)) if len(pressure_error) else np.nan,
    }


def main() -> int:
    states = pd.read_csv(STATES_PATH)
    apparent = _apparent_rows(states)
    wide = apparent.pivot(index=["source", "temperature_C", "CO2_loading"], columns="model")
    projection = wide.loc[:, [column for column in wide.columns if column[1] in MODELS]].copy()
    projection.columns = [f"{model}_{quantity}" for quantity, model in projection.columns]
    for parent in TOTALS:
        projection[f"max_abs_{parent}_projection_delta"] = (
            projection[f"ideal_9_species_apparent_x_{parent}"]
            - projection[f"ideal_6_species_apparent_x_{parent}"]
        ).abs()
    projection = projection.reset_index()
    projection["max_abs_projection_delta"] = projection[
        [f"max_abs_{parent}_projection_delta" for parent in TOTALS]
    ].max(axis=1)

    observations = pd.read_csv(VLE_PATH).rename(
        columns={"source_key": "source", "temperature": "temperature_C"}
    )[["source", "temperature_C", "CO2_loading", "CO2_pressure"]].rename(
        columns={"CO2_pressure": "observed_CO2_pressure_kPa"}
    )
    # Multiple papers can report the same coordinate with different measured pressures;
    # reuse the one model state while retaining every observation row.
    projection = projection.merge(observations, on=["source", "temperature_C", "CO2_loading"], validate="one_to_many")
    if float(projection["max_abs_projection_delta"].max()) > 1.0e-10:
        raise RuntimeError("Corrected six/nine apparent projections are not equal within the run contract")

    rows: list[dict[str, object]] = []
    for record in projection.to_dict("records"):
        try:
            apparent_x = np.array(
                [record[f"ideal_9_species_apparent_x_{parent}"] for parent in TOTALS], dtype=float
            )
            pressure_pa, _, y_vapor = flashTQ(
                float(record["temperature_C"]) + 273.15, 0, apparent_x, params=legacy_pcsaft_params()
            )
            predicted = float(pressure_pa * np.asarray(y_vapor, dtype=float)[0] / 1000.0)
            status = "success"
            error = float(np.log10(predicted / record["observed_CO2_pressure_kPa"])) if predicted > 0 else np.nan
            message = ""
        except Exception as exc:  # preserve row-level failures in the retained result
            predicted = np.nan
            status = "failed"
            error = np.nan
            message = f"{type(exc).__name__}: {exc}"
        for model in MODELS:
            rows.append(
                {
                    "source": record["source"],
                    "temperature_C": record["temperature_C"],
                    "CO2_loading": record["CO2_loading"],
                    "model": model,
                    **{f"apparent_x_{parent}": record[f"ideal_{9 if model == 'ideal_9_species' else 6}_species_apparent_x_{parent}"] for parent in TOTALS},
                    "observed_CO2_pressure_kPa": record["observed_CO2_pressure_kPa"],
                    "predicted_CO2_pressure_kPa": predicted,
                    "log10_predicted_over_observed": error,
                    "status": status,
                    "error_message": message,
                    "pressure_evaluation": "shared_after_projection_check",
                }
            )

    results = pd.DataFrame(rows)
    projection.to_csv(RESULTS_DIR / "corrected_apparent_projection_diagnostics.csv", index=False, lineterminator="\n")
    results.to_csv(RESULTS_DIR / "corrected_apparent_pressure_comparison.csv", index=False, lineterminator="\n")
    _metrics(results).to_csv(RESULTS_DIR / "corrected_apparent_pressure_metrics.csv", index=False, lineterminator="\n")
    pd.DataFrame([
        {"artifact": "corrected_apparent_pressure_comparison.csv", "role": "full canonical VLE comparison"},
        {"artifact": "corrected_apparent_projection_diagnostics.csv", "role": "six/nine conserved-total projection check"},
    ]).to_csv(RESULTS_DIR / "corrected_apparent_pressure_manifest.csv", index=False, lineterminator="\n")
    with open(RESULTS_DIR / "corrected_apparent_pressure_summary.md", "w", encoding="utf-8") as handle:
        metrics = _metrics(results)
        overall = metrics[metrics["temperature_C"] == "overall"].iloc[0]
        handle.write(
            "# Corrected apparent-projection pressure comparison\n\n"
            "The apparent liquid composition is formed from conserved carbon, amine, and water totals. "
            "The six- and nine-species projections agree before the neutral EOS call; one pressure evaluation "
            "is therefore shared by both labels after the projection check.\n\n"
            f"maximum absolute projected-composition difference: {float(projection['max_abs_projection_delta'].max()):.6e}\n"
            f"pressure rows: {int(overall['attempted_count'])}\n"
            f"coverage: {float(overall['coverage_fraction']):.6f}\n"
            f"median absolute log10 pressure error: {float(overall['median_abs_log10_error']):.6f}\n"
            f"RMSE log10 pressure error: {float(overall['rmse_log10_error']):.6f}\n\n"
            "This neutral apparent-EOS lane cannot distinguish six from nine species or identify reaction/ionic "
            "parameters: those parameters change internal species allocation, while the conserved apparent feed "
            "is fixed by loading and feed composition. The result is diagnostic, not a reactive ePC-SAFT VLE claim.\n"
        )
    print(f"Generated corrected apparent-projection pressure results under {RESULTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
