from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from legacy_pcsaft_parameters import get_prop_dict
from plot_all_species_diagnostic import solve_all_species_series
from plot_export import default_output_dir, save_plot


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from pcsaft import flashTQ
except ImportError as exc:
    raise RuntimeError(
        "The legacy all-species pressure diagnostic requires the sibling/local pcsaft package. "
        "Confirm C:\\Users\\Tanner\\Documents\\git\\PC-SAFT exists, then run `uv sync` from this "
        "repository before running `uv run python MEA\\run_plot_exports.py`."
    ) from exc


DATA_ROOT = REPO_ROOT / "data" / "MEA"
PCSAFT_SPECIES = ["CO2", "MEA-2B", "H2O-2B-CC", "MEAH+", "MEACOO-", "HCO3-", "CO32-", "H3O+", "OH-"]
TEMPERATURES_C = (40, 60, 80, 100, 120)


def _load_vle_data(temperature_C: float) -> pd.DataFrame:
    df = pd.read_csv(DATA_ROOT / "VLE" / "Combined_VLE.csv")
    return df[
        (df["temperature"] == temperature_C)
        & (df["MEA_weight_fraction"] == 0.3)
        & (df["CO2_loading"] < 0.6)
    ].sort_values("CO2_loading")


def _pressure_rows_for_temperature(temperature_C: float) -> list[dict[str, object]]:
    df = _load_vle_data(temperature_C)
    if df.empty:
        return []

    loadings = np.linspace(float(df["CO2_loading"].min()), float(df["CO2_loading"].max()), 21)
    chemistry_results = solve_all_species_series(loadings, 0.3, 273.15 + temperature_C)
    params = get_prop_dict(PCSAFT_SPECIES, temperature_C)

    rows: list[dict[str, object]] = []
    for result in chemistry_results:
        observed = float(np.interp(result.loading, df["CO2_loading"].to_numpy(), df["CO2_pressure"].to_numpy()))
        row: dict[str, object] = {
            "temperature_C": temperature_C,
            "MEA_weight_fraction": 0.3,
            "CO2_loading": result.loading,
            "observed_CO2_pressure_kPa": observed,
            "chemistry_success": result.success,
            "chemistry_message": result.message,
            "pressure_success": False,
            "pressure_message": "",
            "pred_CO2_pressure_kPa": np.nan,
            "log10_pred_over_obs": np.nan,
        }
        if not result.success:
            row["pressure_message"] = "skipped because all-species chemistry failed"
            rows.append(row)
            continue

        x = np.asarray(result.x, dtype=float)
        x = x / np.sum(x)
        try:
            pressure_pa, _, y_vapor = flashTQ(273.15 + temperature_C, 0, x, params=params.copy())
            y_vapor = np.asarray(y_vapor, dtype=float)
            pressure_kpa = float(pressure_pa * y_vapor[0] / 1000.0)
            row["pressure_success"] = bool(np.isfinite(pressure_kpa) and pressure_kpa > 0.0)
            row["pressure_message"] = "solved" if row["pressure_success"] else "nonpositive or nonfinite pressure"
            row["pred_CO2_pressure_kPa"] = pressure_kpa
            if row["pressure_success"] and observed > 0.0:
                row["log10_pred_over_obs"] = float(np.log10(pressure_kpa / observed))
        except Exception as exc:
            row["pressure_message"] = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
        rows.append(row)
    return rows


def _json_safe(value):
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def write_pressure_diagnostics(rows: list[dict[str, object]], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "all_species_pcsaft_pressure_diagnostics.csv"
    json_path = output_dir / "all_species_pcsaft_pressure_summary.json"
    frame = pd.DataFrame(rows)
    frame.to_csv(csv_path, index=False)
    success_rows = frame[frame["pressure_success"] == True] if not frame.empty else frame
    payload = {
        "n_points": int(len(frame)),
        "n_pressure_success": int(len(success_rows)),
        "n_chemistry_failed": int((frame["chemistry_success"] == False).sum()) if not frame.empty else 0,
        "n_pressure_failed": int((frame["pressure_success"] == False).sum()) if not frame.empty else 0,
        "median_abs_log10_error": (
            float(success_rows["log10_pred_over_obs"].abs().median())
            if not success_rows.empty
            else None
        ),
        "failures": frame[frame["pressure_success"] == False].to_dict("records") if not frame.empty else [],
    }
    json_path.write_text(json.dumps(_json_safe(payload), indent=2, allow_nan=False), encoding="utf-8")
    return csv_path, json_path


def plot_pressure_diagnostics(rows: list[dict[str, object]]) -> Path:
    frame = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(14, 10))
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:cyan", "tab:purple"]

    for color, temperature_C in zip(colors, TEMPERATURES_C):
        df = _load_vle_data(temperature_C)
        if df.empty:
            continue
        ax.plot(df["CO2_loading"], df["CO2_pressure"], "x", color=color)

        subset = frame[frame["temperature_C"] == temperature_C]
        ok = subset[subset["pressure_success"] == True]
        failed = subset[subset["pressure_success"] == False]
        if not ok.empty:
            ax.plot(
                ok["CO2_loading"],
                ok["pred_CO2_pressure_kPa"],
                "--",
                label=f"all-species diagnostic - T = {temperature_C}",
                color=color,
            )
        if not failed.empty:
            ax.scatter(
                failed["CO2_loading"],
                np.full(len(failed), 1e-4),
                marker="x",
                color=color,
                zorder=5,
            )

    ax.set_xlabel("CO2 loading, mol CO2/mol MEA", fontsize=16)
    ax.set_ylabel("CO2 pressure, kPa", fontsize=16)
    ax.tick_params(labelsize=14)
    ax.set_ylim((1e-4, 5e3))
    ax.set_yscale("log")
    ax.legend()
    fig.tight_layout()
    return save_plot(fig, __file__, "co2_partial_pressure")


def main() -> int:
    rows: list[dict[str, object]] = []
    for temperature_C in TEMPERATURES_C:
        rows.extend(_pressure_rows_for_temperature(temperature_C))

    output_dir = default_output_dir(__file__)
    csv_path, json_path = write_pressure_diagnostics(rows, output_dir)
    plot_path = plot_pressure_diagnostics(rows)
    frame = pd.DataFrame(rows)
    n_success = int((frame["pressure_success"] == True).sum()) if not frame.empty else 0
    n_failed = int((frame["pressure_success"] == False).sum()) if not frame.empty else 0

    print(f"All-species pressure diagnostics: {csv_path}")
    print(f"All-species pressure summary: {json_path}")
    print(f"All-species pressure plot: {plot_path}")
    print(f"All-species pressure points: {n_success}/{len(frame)} successful, {n_failed} skipped/failed")
    return 0 if n_success > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
