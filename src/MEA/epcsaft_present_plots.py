from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

from MEA.common.plot_export import save_plot
from MEA.epcsaft_runtime import REPO_ROOT, SPECIES, build_mixture, diagnostic_composition, output_dir


DATA_ROOT = REPO_ROOT / "data" / "reference" / "MEA"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _as_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else np.nan


def load_vle_rows() -> list[dict[str, str]]:
    return _read_csv(DATA_ROOT / "VLE" / "Combined_VLE.csv")


def load_cheq_rows() -> list[dict[str, str]]:
    return _read_csv(DATA_ROOT / "ChEq" / "Combined_ChEq.csv")


def _interp_column(rows: list[dict[str, str]], column: str, loadings: np.ndarray) -> np.ndarray:
    points = [
        (_as_float(row, "CO2_loading"), _as_float(row, column))
        for row in rows
        if np.isfinite(_as_float(row, "CO2_loading")) and np.isfinite(_as_float(row, column))
    ]
    if len(points) < 2:
        return np.full_like(loadings, np.nan, dtype=float)
    points = sorted(points)
    x_data = np.array([point[0] for point in points], dtype=float)
    y_data = np.array([point[1] for point in points], dtype=float)
    return np.interp(loadings, x_data, y_data, left=np.nan, right=np.nan)


def reconcile_speciation_row(row: dict[str, str]) -> np.ndarray:
    loading = _as_float(row, "CO2_loading")
    prior = diagnostic_composition(float(loading))
    measured = {
        "MEA": _as_float(row, "MEA"),
        "MEAH+": _as_float(row, "MEAH^+"),
        "MEACOO-": _as_float(row, "MEACOO^-"),
        "HCO3-": _as_float(row, "HCO3^-"),
        "CO3^2-": _as_float(row, "CO3^2-"),
    }
    species_indices = {
        "CO2": 0,
        "MEA": 1,
        "MEAH+": 3,
        "MEACOO-": 4,
        "HCO3-": 5,
        "CO3^2-": 6,
    }
    names = ["CO2", "MEA", "MEAH+", "MEACOO-", "HCO3-", "CO3^2-"]
    x0 = np.array([prior[species_indices[name]] for name in names], dtype=float)
    for name, value in measured.items():
        if np.isfinite(value):
            x0[names.index(name)] = max(float(value), 1.0e-12)
    x0 = np.clip(x0, 1.0e-12, 0.9)

    def unpack(values: np.ndarray) -> np.ndarray:
        x_co2, x_mea, x_meah, x_meacoo, x_hco3, x_co3 = values
        anion_charge = x_meacoo + x_hco3 + 2.0 * x_co3
        cation_charge = x_meah
        if anion_charge > cation_charge:
            x_h3o = anion_charge - cation_charge
            x_oh = 1.0e-12
        else:
            x_h3o = 1.0e-12
            x_oh = cation_charge - anion_charge
        x_h2o = 1.0 - float(np.sum(values)) - x_h3o - x_oh
        full = np.array([x_co2, x_mea, x_h2o, x_meah, x_meacoo, x_hco3, x_co3, x_h3o, x_oh], dtype=float)
        return full

    def objective(values: np.ndarray) -> float:
        full = unpack(values)
        cost = 0.0
        for name, measured_value in measured.items():
            if np.isfinite(measured_value):
                idx = species_indices[name]
                scale = max(abs(float(measured_value)), 0.002)
                cost += ((full[idx] - float(measured_value)) / scale) ** 2
        total_mea = full[1] + full[3] + full[4]
        total_carbon = full[0] + full[4] + full[5] + full[6]
        balance_scale = max(float(loading) * max(total_mea, 1.0e-8), 0.002)
        cost += 100.0 * ((total_carbon - float(loading) * total_mea) / balance_scale) ** 2
        water_penalty = max(0.0, 0.05 - full[2])
        cost += 1000.0 * water_penalty**2
        cost += 0.01 * float(np.sum(((values - x0) / np.maximum(x0, 0.002)) ** 2))
        return float(cost)

    result = minimize(objective, x0, method="SLSQP", bounds=[(1.0e-12, 0.9)] * len(x0), options={"maxiter": 500, "ftol": 1.0e-12})
    values = result.x if result.success else x0
    full = unpack(np.asarray(values, dtype=float))
    if full[2] <= 0 or not np.all(np.isfinite(full)):
        return prior
    return full / float(np.sum(full))


def data_informed_compositions(
    cheq_rows: list[dict[str, str]],
    loadings: np.ndarray,
) -> list[np.ndarray]:
    filtered = [
        row
        for row in cheq_rows
        if abs(_as_float(row, "MEA_weight_fraction") - 0.30) < 1e-9
        and abs(_as_float(row, "temperature") - 40.0) < 1e-9
    ]
    reconciled = [
        (float(_as_float(row, "CO2_loading")), reconcile_speciation_row(row))
        for row in filtered
        if np.isfinite(_as_float(row, "CO2_loading"))
    ]
    reconciled = sorted(reconciled, key=lambda item: item[0])
    if len(reconciled) < 2:
        return [diagnostic_composition(float(loading)) for loading in loadings]

    measured_loading = np.array([item[0] for item in reconciled], dtype=float)
    measured_x = np.array([item[1] for item in reconciled], dtype=float)

    compositions: list[np.ndarray] = []
    for loading in loadings:
        x = np.array([np.interp(float(loading), measured_loading, measured_x[:, idx]) for idx in range(measured_x.shape[1])], dtype=float)
        if not np.all(np.isfinite(x)):
            x = diagnostic_composition(float(loading))
        compositions.append(x / float(np.sum(x)))
    return compositions


def diagnostic_series(
    *,
    temperature_K: float = 313.15,
    mea_weight_fraction: float = 0.30,
    loadings: np.ndarray | None = None,
    pressure_Pa: float = 101325.0,
    compositions: list[np.ndarray] | None = None,
) -> list[dict[str, float]]:
    loadings = np.linspace(0.05, 0.75, 18) if loadings is None else np.asarray(loadings, dtype=float)
    compositions = compositions or [
        diagnostic_composition(loading=float(loading), mea_weight_fraction=mea_weight_fraction)
        for loading in loadings
    ]
    rows: list[dict[str, float]] = []
    for loading, x in zip(loadings, compositions):
        try:
            mixture = build_mixture(temperature_K, x)
            state = mixture.state(temperature_K, x, P=pressure_Pa, phase="liq")
            fugacity = state.fugacity_coefficient(natural_log=True, return_contribution_terms=True)
            ares = state.residual_helmholtz(return_contribution_terms=True)
            liquid_fugacity_kPa = float(x[0] * np.exp(fugacity["total"][0]) * pressure_Pa / 1000.0)
            rows.append(
                {
                    "loading": float(loading),
                    "pressure_Pa": state.pressure(),
                    "density_kg_m3": state.mass_density(),
                    "ln_phi_CO2": float(np.asarray(fugacity["total"], dtype=float)[0]),
                    "liquid_fugacity_CO2_kPa": liquid_fugacity_kPa,
                    "ares_total": float(ares["total"]),
                    "ares_ion": float(ares["terms"].get("ion", np.nan)),
                    "ares_born": float(ares["terms"].get("born", np.nan)),
                    "x_CO2": float(x[0]),
                    "x_MEA": float(x[1]),
                    "x_H2O": float(x[2]),
                    "x_MEACOO": float(x[4]),
                    "x_HCO3": float(x[5]),
                }
            )
        except Exception as exc:
            rows.append({"loading": float(loading), "error": str(exc)})
    return rows


def write_vle_comparison(vle_rows: list[dict[str, str]], series_rows: list[dict[str, float]]) -> Path:
    valid_series = [row for row in series_rows if "error" not in row]
    loadings = np.array([row["loading"] for row in valid_series], dtype=float)
    fugacity = np.array([row["liquid_fugacity_CO2_kPa"] for row in valid_series], dtype=float)
    filtered = [
        row
        for row in vle_rows
        if abs(_as_float(row, "MEA_weight_fraction") - 0.30) < 1e-9
        and abs(_as_float(row, "temperature") - 40.0) < 1e-9
    ]
    out = output_dir("diagnostics") / "vle_surrogate_comparison_30wt_40C.csv"
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "CO2_loading",
                "CO2_pressure_data_kPa",
                "liquid_fugacity_CO2_surrogate_kPa",
                "log10_surrogate_over_data",
                "paper",
            ],
        )
        writer.writeheader()
        for row in filtered:
            loading = _as_float(row, "CO2_loading")
            pressure = _as_float(row, "CO2_pressure")
            if not np.isfinite(loading) or not np.isfinite(pressure) or pressure <= 0:
                continue
            surrogate = float(np.interp(loading, loadings, fugacity))
            writer.writerow(
                {
                    "CO2_loading": loading,
                    "CO2_pressure_data_kPa": pressure,
                    "liquid_fugacity_CO2_surrogate_kPa": surrogate,
                    "log10_surrogate_over_data": float(np.log10(surrogate / pressure)) if surrogate > 0 else np.nan,
                    "paper": row.get("paper", ""),
                }
            )
    return out


def write_diagnostic_series(rows: list[dict[str, float]]) -> Path:
    out = output_dir("diagnostics") / "diagnostic_series.csv"
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    return out


def plot_vle_overview(vle_rows: list[dict[str, str]], series_rows: list[dict[str, float]]) -> Path:
    fig, ax = plt.subplots(figsize=(8.0, 5.5))
    filtered = [
        row
        for row in vle_rows
        if abs(_as_float(row, "MEA_weight_fraction") - 0.30) < 1e-9
    ]
    temperatures = sorted({round(_as_float(row, "temperature")) for row in filtered if np.isfinite(_as_float(row, "temperature"))})
    cmap = plt.get_cmap("viridis", max(len(temperatures), 1))
    for idx, temperature in enumerate(temperatures):
        subset = [row for row in filtered if round(_as_float(row, "temperature")) == temperature]
        subset = sorted(subset, key=lambda row: _as_float(row, "CO2_loading"))
        ax.semilogy(
            [_as_float(row, "CO2_loading") for row in subset],
            [_as_float(row, "CO2_pressure") for row in subset],
            "o",
            ms=4,
            color=cmap(idx),
            label=f"{temperature:g} C",
        )
    valid_series = [row for row in series_rows if "error" not in row]
    ax.semilogy(
        [row["loading"] for row in valid_series],
        [row["liquid_fugacity_CO2_kPa"] for row in valid_series],
        "-",
        color="black",
        lw=1.8,
        label="unregressed ePC-SAFT fugacity surrogate, 40 C",
    )
    ax.set_xlabel("CO2 loading, mol CO2 / mol MEA")
    ax.set_ylabel("CO2 partial pressure, kPa")
    ax.set_title("MEA-CO2-H2O VLE data and unregressed ePC-SAFT surrogate")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(title="30 wt% MEA", ncols=2, fontsize=8)
    return save_plot(fig, __file__, "epcsaft_vle_data_overview")


def plot_speciation_overlay(cheq_rows: list[dict[str, str]], series_rows: list[dict[str, float]]) -> Path:
    fig, ax = plt.subplots(figsize=(8.0, 5.5))
    species_columns = {
        "MEA": "tab:blue",
        "MEAH^+": "tab:orange",
        "MEACOO^-": "tab:green",
        "HCO3^-": "tab:red",
        "CO3^2-": "tab:purple",
    }
    filtered = [
        row
        for row in cheq_rows
        if abs(_as_float(row, "MEA_weight_fraction") - 0.30) < 1e-9
        and abs(_as_float(row, "temperature") - 40.0) < 1e-9
    ]
    for species, color in species_columns.items():
        points = [(row, _as_float(row, species)) for row in filtered if np.isfinite(_as_float(row, species))]
        if points:
            ax.semilogy(
                [_as_float(row, "CO2_loading") for row, _ in points],
                [value for _, value in points],
                "o",
                ms=4,
                alpha=0.8,
                color=color,
            label=f"{species} data",
            )

    model_map = {
        "x_MEACOO": ("MEACOO- data-informed path", "tab:green"),
        "x_HCO3": ("HCO3- data-informed path", "tab:red"),
        "x_MEA": ("MEA data-informed path", "tab:blue"),
    }
    valid = [row for row in series_rows if "error" not in row]
    for key, (label, color) in model_map.items():
        ax.semilogy(
            [row["loading"] for row in valid],
            [row[key] for row in valid],
            "-",
            color=color,
            lw=1.5,
            label=label,
        )
    ax.set_xlabel("CO2 loading, mol CO2 / mol MEA")
    ax.set_ylabel("True-species mole fraction")
    ax.set_title("Speciation data with data-informed ePC-SAFT state path")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8, ncols=2)
    return save_plot(fig, __file__, "epcsaft_speciation_diagnostic_overlay")


def plot_epcsaft_diagnostics(series_rows: list[dict[str, float]]) -> Path:
    valid = [row for row in series_rows if "error" not in row]
    if not valid:
        raise RuntimeError("No finite ePC-SAFT diagnostic states were available for plotting.")
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.0), sharex=True)
    loading = [row["loading"] for row in valid]

    axes[0, 0].plot(loading, [row["density_kg_m3"] for row in valid], "o-", color="tab:blue")
    axes[0, 0].set_ylabel("Density, kg/m3")

    axes[0, 1].plot(loading, [row["pressure_Pa"] / 1e5 for row in valid], "o-", color="tab:orange")
    axes[0, 1].set_ylabel("State pressure, bar")

    axes[1, 0].plot(loading, [row["ln_phi_CO2"] for row in valid], "o-", color="tab:green")
    axes[1, 0].set_ylabel("ln phi CO2")
    axes[1, 0].set_xlabel("CO2 loading, mol/mol")

    axes[1, 1].plot(loading, [row["ares_ion"] for row in valid], "o-", label="ion", color="tab:red")
    axes[1, 1].plot(loading, [row["ares_born"] for row in valid], "s-", label="born", color="tab:purple")
    axes[1, 1].set_ylabel("Ares contribution")
    axes[1, 1].set_xlabel("CO2 loading, mol/mol")
    axes[1, 1].legend(fontsize=8)

    for ax in axes.ravel():
        ax.grid(True, alpha=0.25)
    fig.suptitle("ePC-SAFT diagnostics on 30 wt% MEA, 40 C data-informed states")
    fig.tight_layout()
    return save_plot(fig, __file__, "epcsaft_liquid_diagnostics")


def main() -> int:
    vle_rows = load_vle_rows()
    cheq_rows = load_cheq_rows()
    loadings = np.linspace(0.11, 0.74, 18)
    compositions = data_informed_compositions(cheq_rows, loadings)
    series = diagnostic_series(loadings=loadings, compositions=compositions)
    series_path = write_diagnostic_series(series)
    comparison_path = write_vle_comparison(vle_rows, series)
    paths = [
        plot_vle_overview(vle_rows, series),
        plot_speciation_overlay(cheq_rows, series),
        plot_epcsaft_diagnostics(series),
    ]
    print(f"Wrote diagnostic series: {series_path}")
    print(f"Wrote VLE surrogate comparison: {comparison_path}")
    comparison_rows = _read_csv(comparison_path)
    residuals = np.array([_as_float(row, "log10_surrogate_over_data") for row in comparison_rows], dtype=float)
    residuals = residuals[np.isfinite(residuals)]
    if residuals.size:
        print(
            "VLE surrogate log10(model/data): "
            f"median={np.median(residuals):.3g}, min={np.min(residuals):.3g}, max={np.max(residuals):.3g}"
        )
    for path in paths:
        print(f"Plot artifact: {path}")
    failures = [row for row in series if "error" in row]
    if failures:
        print(f"Diagnostic state failures: {len(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
