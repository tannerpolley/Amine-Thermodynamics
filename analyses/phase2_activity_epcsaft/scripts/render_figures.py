from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from MEA.common.plot_style import write_mpl_sidecar  # noqa: E402
from MEA.common.speciation_figures import write_speciation_plot  # noqa: E402

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ANALYSIS_DIR / "data" / "processed"
RESULTS_DIR = ANALYSIS_DIR / "results"
SPECIATION_FIGURE_OUT = ANALYSIS_DIR / "figures" / "speciation" / "output"
STALE_SCAFFOLD_PATTERNS = (
    "phase2_speciation_scaffold_curve.csv",
    "phase2_speciation_scaffold_*C.png",
    "phase2_speciation_scaffold_*C.svg",
    "phase2_speciation_scaffold_*C.mpl.yaml",
    "phase2_speciation_scaffold_*C_plot_data.csv",
)


def require_csv(name: str) -> pd.DataFrame:
    path = PROCESSED_DIR / name
    if not path.exists():
        raise RuntimeError(
            f"Missing {path}. Run `uv run python analyses\\phase2_activity_epcsaft\\scripts\\generate_data.py` first."
        )
    return pd.read_csv(path)


def remove_stale_scaffold_outputs() -> None:
    for root in (RESULTS_DIR, SPECIATION_FIGURE_OUT):
        root.mkdir(parents=True, exist_ok=True)
        for pattern in STALE_SCAFFOLD_PATTERNS:
            for path in root.glob(pattern):
                path.unlink()


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SPECIATION_FIGURE_OUT.mkdir(parents=True, exist_ok=True)
    remove_stale_scaffold_outputs()
    points = require_csv("phase2_speciation_reference_points.csv")
    target_roles = require_csv("phase2_speciation_target_roles.csv")
    curves = require_csv("phase2_speciation_activity_curves.csv")
    points.to_csv(SPECIATION_FIGURE_OUT / "phase2_speciation_reference_points.csv", index=False)
    points.to_csv(RESULTS_DIR / "phase2_speciation_reference_points.csv", index=False)
    target_roles.to_csv(SPECIATION_FIGURE_OUT / "phase2_speciation_target_roles.csv", index=False)
    target_roles.to_csv(RESULTS_DIR / "phase2_speciation_target_roles.csv", index=False)
    curves.to_csv(SPECIATION_FIGURE_OUT / "phase2_speciation_activity_curves.csv", index=False)
    curves.to_csv(RESULTS_DIR / "phase2_speciation_activity_curves.csv", index=False)
    write_speciation_plot(
        curve_frame=curves,
        point_frame=points,
        output_dir=RESULTS_DIR,
        stem="phase2_speciation_activity_plot",
        title="Phase 2 ePC-SAFT activity speciation, 40 C",
        description=(
            "Continuous curves are native ePC-SAFT activity-equilibrium solutions from the Phase 2 "
            "parameter artifact; markers are measured reference points. Residual acceptance is controlled "
            "by phase2_residual_acceptance_audit.csv."
        ),
        style_source="analyses/phase2_activity_epcsaft/scripts/render_figures.py",
        temperature_C=40.0,
    )
    for temperature_C in sorted(curves["temperature_C"].dropna().unique()):
        write_speciation_plot(
            curve_frame=curves,
            point_frame=points,
            output_dir=SPECIATION_FIGURE_OUT,
            stem=f"phase2_speciation_{int(round(float(temperature_C)))}C",
            title=f"Phase 2 ePC-SAFT activity speciation, {float(temperature_C):g} C",
            description=(
                "Continuous curves are native ePC-SAFT activity-equilibrium solutions from the Phase 2 "
                "parameter artifact; markers are measured reference points. Claim status is controlled by "
                "the residual acceptance audit."
            ),
            style_source="analyses/phase2_activity_epcsaft/scripts/render_figures.py",
            temperature_C=float(temperature_C),
        )
    write_mpl_sidecar(
        SPECIATION_FIGURE_OUT / "phase2_speciation_figure_family.mpl.yaml",
        png_name="phase2_speciation_40C.png",
        svg_name="phase2_speciation_40C.svg",
        title="Phase 2 ePC-SAFT activity speciation figure family",
        description="Figure-owned Phase 2 native ePC-SAFT activity-equilibrium speciation outputs; one full-coverage plot is generated per temperature.",
        style_source="analyses/phase2_activity_epcsaft/scripts/render_figures.py",
    )
    print(f"Phase 2 activity-speciation plot artifacts: {SPECIATION_FIGURE_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
