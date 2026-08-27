from __future__ import annotations

from pathlib import Path

import pandas as pd

from MEA.common.speciation_figures import write_speciation_plot


FIGURE = Path(__file__).resolve().parents[1]
ANALYSIS = FIGURE.parents[1]
OUTPUT = FIGURE / "output"
CURVES = OUTPUT / "retained_full_speciation_curves.csv"
PREDICTIONS = ANALYSIS / "results/co2_water_kij_anchored_transfer/predictions.csv"
SPECIES = {
    "carbon-dioxide": "CO2",
    "monoethanolamine": "MEA",
    "water": "H2O",
    "protonated-monoethanolamine": "MEAH+",
    "carbamate-anion": "MEACOO-",
    "bicarbonate-anion": "HCO3-",
    "carbonate-anion": "CO3^2-",
    "hydronium-cation": "H3O+",
    "hydroxide-anion": "OH-",
}
ORDER = tuple(SPECIES.values())


def main() -> None:
    curves = pd.read_csv(CURVES)
    curves["species"] = curves["species"].map(SPECIES)
    predictions = pd.read_csv(PREDICTIONS)
    points = predictions.loc[
        (predictions["block"] == "speciation")
        & predictions["temperature_k"].eq(313.15)
        & predictions["observed"].gt(0.0)
    ].copy()
    points["species"] = points["target_identity"].str.rsplit("::", n=1).str[-1]
    points = points.loc[points["species"].isin(ORDER)]
    points = points.rename(
        columns={"loading": "CO2_loading", "observed": "mole_fraction"}
    )[["CO2_loading", "species", "mole_fraction"]]
    points["temperature_C"] = 40.0
    write_speciation_plot(
        curve_frame=curves,
        point_frame=points,
        output_dir=OUTPUT,
        stem="retained_full_speciation_40C",
        title="Retained nine-species ePC-SAFT speciation at 40 °C",
        description=(
            "All nine retained ePC-SAFT liquid species at 30 wt% unloaded MEA and "
            "101.325 kPa. Lines are model states on an even loading grid from zero to one; "
            "markers are available direct-positive 40 °C speciation observations."
        ),
        style_source=str(Path(__file__).relative_to(ANALYSIS.parents[2])),
        temperature_C=40.0,
        plot_order=ORDER,
    )


if __name__ == "__main__":
    main()
