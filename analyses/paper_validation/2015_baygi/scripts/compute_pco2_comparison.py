"""Baygi 2015 model against our C_src model on our 161 canonical 30 wt % pCO2 rows, plus the reproduction check.

Writes to data/processed:
  baygi_pco2_row_comparison.csv       one row per canonical row: observed, Baygi model, our C_src
  baygi_pco2_statistics.csv           n, AARD, mean ln, RMS ln by source / temperature, all rows and 40-80 degC
  baygi_table5_reproduction.csv       Baygi Table 5 AARD against this reproduction and the digitized published curve
  baygi_fig11_recomputed_curves.csv   recomputed Baygi curves on a loading grid next to the digitized Fig. 11 curves

Ours is not recomputed: it is read from calibration-misfit/refit-C-states.csv (variant source-R4-C-f66-v5).

    OMP_NUM_THREADS=1 uv run python analyses/paper_validation/2015_baygi/scripts/compute_pco2_comparison.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from baygi_model import ANALYSIS_DIR, REPO_ROOT, baygi_pco2_kpa

PROCESSED = ANALYSIS_DIR / "data" / "processed"
DIGITIZED = ANALYSIS_DIR / "data" / "digitized"
VLE = REPO_ROOT / "data" / "reference" / "MEA" / "observations" / "vapor_liquid_equilibrium"
STATES = REPO_ROOT / "analyses" / "mea_parameter_bundle" / "calibration-misfit" / "refit-C-states.csv"
C_SRC = "source-R4-C-f66-v5"
MODELS = {"baygi": "Baygi 2015 (ions lumped with water)", "baygi_ions_dropped": "Baygi 2015 (ions dropped)",
          "ours": "ours, refit C_src"}


def safe_pco2(loading: float, temperature_K: float, ions: str) -> float:
    try:
        return baygi_pco2_kpa(loading, temperature_K, 0.3, ions=ions)
    except Exception:  # pcsaft SolutionError / no bubble pressure below 100 MPa
        return float("nan")


def statistics(observed: pd.Series, predicted: pd.Series) -> dict:
    ok = predicted.notna()
    obs, pred = observed[ok], predicted[ok]
    ln = np.log(pred / obs)
    return {"n": int(ok.sum()), "n_rows": len(observed), "aard_percent": float(100 * np.mean(np.abs(pred - obs) / obs)),
            "mean_ln": float(ln.mean()), "rms_ln": float(np.sqrt(np.mean(ln**2)))}


def canonical_rows() -> pd.DataFrame:
    v = pd.read_csv(VLE / "Canonical_VLE_Observations.csv")
    v = v[v.active_view_member == "yes"].copy()
    states = pd.read_csv(STATES)
    states = states[(states.variant == C_SRC) & states.identity.str.startswith("canonical:vle_obs")]
    ours = states.assign(observation_id=states.identity.str.removeprefix("canonical:")).set_index("observation_id")
    assert (ours.status == "evaluated").all() and len(ours) == 161
    rows = pd.DataFrame({
        "observation_id": v.observation_id, "source": v.source_key, "temperature_C": v.temperature_canonical_C,
        "CO2_loading": v.CO2_loading, "observed_pCO2_kPa": v.CO2_pressure})
    rows["ours_C_src_pCO2_kPa"] = rows.observation_id.map(ours.predicted) / 1000.0  # retained states are in Pa
    # the retained observed column must be these rows' pressures
    assert np.allclose(rows.observation_id.map(ours.observed) / 1000.0, rows.observed_pCO2_kPa)
    for key, ions in (("baygi", "water"), ("baygi_ions_dropped", "drop")):
        rows[f"{key}_pCO2_kPa"] = [safe_pco2(a, t + 273.15, ions) for a, t in zip(rows.CO2_loading, rows.temperature_C)]
    return rows.reset_index(drop=True)


def statistics_table(rows: pd.DataFrame) -> pd.DataFrame:
    out = []
    subsets = {"all rows (40-120 degC)": rows, "40-80 degC": rows[rows.temperature_C <= 80]}
    for scope, sub in subsets.items():
        groups = [("overall", "all", sub)]
        groups += [("source", s, g) for s, g in sub.groupby("source")]
        groups += [("temperature_C", f"{t:g}", g) for t, g in sub.groupby("temperature_C")]
        for kind, name, g in groups:
            for key, label in MODELS.items():
                col = "ours_C_src_pCO2_kPa" if key == "ours" else f"{key}_pCO2_kPa"
                out.append({"scope": scope, "group_type": kind, "group": name, "model": label,
                            **statistics(g.observed_pCO2_kPa, g[col])})
    return pd.DataFrame(out)


def digitized_curve(figure: str, series: str) -> pd.DataFrame:
    c = pd.read_csv(DIGITIZED / f"{figure}_model_curves.csv")
    return c[c.series == series].sort_values("CO2_loading")


def published_curve_pco2(curve: pd.DataFrame, loading: np.ndarray) -> np.ndarray:
    """Digitized curve at the given loadings (log-linear); NaN outside the curve's range."""
    x, y = curve.CO2_loading.to_numpy(), np.log(curve.pCO2_kPa.to_numpy())
    return np.where((loading >= x.min()) & (loading <= x.max()), np.exp(np.interp(loading, x, y)), np.nan)


def table5(rows: pd.DataFrame) -> pd.DataFrame:
    jou = pd.read_csv(VLE / "Jou_1995_VLE.csv")
    jou = jou[jou.MEA_weight_fraction == 0.3].rename(columns={"CO2_loading": "loading", "CO2_pressure": "obs", "temperature": "T_C"})
    mamun = rows[rows.source == "Mamun2005"].rename(columns={"CO2_loading": "loading", "observed_pCO2_kPa": "obs", "temperature_C": "T_C"})
    fig11 = {40: digitized_curve("baygi2015_fig11", "313 K"), 120: digitized_curve("baygi2015_fig11", "393 K")}
    out = []
    cases = [
        ("Ma'mun 2005", "19 rows, 393 K (our file: 120 degC), same 19 rows as Baygi", 21.03, 19, mamun),
        ("Jou 1995", "all 74 Jou rows we hold (0-150 degC, loading 0.003-0.689); Baygi used 100 of 124 rows to loading 1.324, "
                     "so the row sets differ", 43.16, 100, jou),
        ("Jou 1995, 40 and 120 degC rows", "the 313 K and 393 K Jou rows we hold (Fig. 11 temperatures)", None, None,
         jou[jou.T_C.isin([40, 120])]),
    ]
    for source, note, published, n_published, d in cases:
        d = d.reset_index(drop=True)
        d["baygi"] = [safe_pco2(a, t + 273.15, "water") for a, t in zip(d.loading, d.T_C)]
        d["baygi_ions_dropped"] = [safe_pco2(a, t + 273.15, "drop") for a, t in zip(d.loading, d.T_C)]
        d["curve"] = np.nan
        for t, curve in fig11.items():
            m = d.T_C == t
            d.loc[m, "curve"] = published_curve_pco2(curve, d.loc[m, "loading"].to_numpy())
        for label, col in (("this reproduction (ions lumped with water)", "baygi"),
                           ("this reproduction (ions dropped)", "baygi_ions_dropped"),
                           ("Baygi Fig. 11 digitized curve", "curve")):
            s = statistics(d.obs, d[col])
            out.append({"source": source, "rows": note, "model": label, "n": s["n"], "n_rows": s["n_rows"],
                        "aard_percent": s["aard_percent"], "mean_ln": s["mean_ln"], "rms_ln": s["rms_ln"],
                        "baygi_table5_aard_percent": published, "baygi_table5_n": n_published})
    return pd.DataFrame(out)


def recomputed_curves() -> pd.DataFrame:
    out = []
    for series, t_K in (("313 K", 313.15), ("393 K", 393.15)):
        pub = digitized_curve("baygi2015_fig11", series)
        for a in np.round(np.arange(0.02, 1.0001, 0.02), 3):
            mine = {key: safe_pco2(a, t_K, ions) for key, ions in (("baygi", "water"), ("baygi_ions_dropped", "drop"))}
            out.append({"series": series, "temperature_K": t_K, "CO2_loading": a, "baygi_pCO2_kPa": mine["baygi"],
                        "baygi_ions_dropped_pCO2_kPa": mine["baygi_ions_dropped"],
                        "digitized_fig11_pCO2_kPa": float(published_curve_pco2(pub, np.array([a]))[0])})
    c = pd.DataFrame(out)
    c["ln_recomputed_over_digitized"] = np.log(c.baygi_pCO2_kPa / c.digitized_fig11_pCO2_kPa)
    c["ln_ions_dropped_over_digitized"] = np.log(c.baygi_ions_dropped_pCO2_kPa / c.digitized_fig11_pCO2_kPa)
    return c


def main() -> int:
    rows = canonical_rows()
    rows.to_csv(PROCESSED / "baygi_pco2_row_comparison.csv", index=False, float_format="%.6g")
    stats = statistics_table(rows)
    stats.to_csv(PROCESSED / "baygi_pco2_statistics.csv", index=False, float_format="%.6g")
    t5 = table5(rows)
    t5.to_csv(PROCESSED / "baygi_table5_reproduction.csv", index=False, float_format="%.6g")
    curves = recomputed_curves()
    curves.to_csv(PROCESSED / "baygi_fig11_recomputed_curves.csv", index=False, float_format="%.6g")
    pd.set_option("display.width", 220, "display.max_columns", 20)
    print(t5.drop(columns="rows").round(3).to_string())
    print(stats[stats.group_type.isin(["overall", "source"])].round(3).to_string())
    print(rows[rows.baygi_pCO2_kPa.isna()])
    for lim in (0.6, 1.0):
        c = curves[curves.CO2_loading <= lim]
        print(f"loading <= {lim}: median |ln recomputed/digitized| {c.ln_recomputed_over_digitized.abs().median():.3f}, "
              f"max {c.ln_recomputed_over_digitized.abs().max():.3f}; ions dropped median "
              f"{c.ln_ions_dropped_over_digitized.abs().median():.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
